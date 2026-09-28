"""Main orchestration loop: wakeword -> ASR -> domain routing -> response.

One wakeword, "Hey Green", covers all three domains (Weather, Crop, and
Plant) -- see wakeword/router.py's module docstring for the two-then-one
history. "field" is the internal WAKEWORD/domain-key name, not an agent or
the spoken phrase -- there is no FieldAgent, and the phrase itself has
changed twice ("Hey Field" then "Hey Green") while this internal name
stayed stable. Once "Hey Green" fires and ASR returns a transcript,
`resolve_field_domain()` (intent.py) uses the same deterministic keyword
routing the farmer dashboard's single chat uses to decide weather/crop/
plant BEFORE any agent.handle() call -- so `self.active_domain` briefly
holds "field" only while listening, and is rewritten to the real domain
the moment speech comes back.

State machine per audio frame:
  IDLE    -- every frame is scored by the wakeword router. A detection
             crossing threshold switches to ACTIVE for that wakeword and
             opens an ASR session.
  ACTIVE  -- frames are streamed to ASR instead of the wakeword router,
             until ASR reports a final transcript for one utterance. The
             transcript first resolves "field" to weather/crop/plant; the
             matching domain agent then handles it against the shared
             farm_state, the response is printed (stand-in for TTS), and
             the loop returns to IDLE (or stays active for Plant's
             multi-turn follow-ups -- see MULTI_TURN_DOMAINS below).

Requires a wakeword .onnx model to be present under
agri_voice_agent/wakeword/models/ to actually trigger domains by voice.
Until it exists, run individual domain agents directly (see
tests/test_weather_manual.py, tests/test_crop_manual.py) or use
`--domain` to skip wakeword detection and go straight into ACTIVE mode for
one domain, for testing the ASR/domain wiring independently.
"""

from __future__ import annotations

import argparse
import sys
import threading

from . import config
from .asr import StreamingASR
from .audio_input import MicrophoneStream
from .domains.crop import CropAgent
from .domains.plant import PlantAgent
from .domains.weather import WeatherAgent
from .events import EventBus
from .farm_state import FarmStore

# Fixed farmer_id for this single-operator local CLI/demo pipeline -- see
# VoiceAgentLoop.__init__'s comment on why this differs from the web
# dashboard's real per-browser farmer identity.
LOCAL_DEMO_FARMER_ID = "local-demo"
from .intent import resolve_field_domain
from .wakeword.router import WakewordRouter

DOMAIN_AGENTS = {
    "weather": WeatherAgent,
    "crop": CropAgent,
    "plant": PlantAgent,
}

# Domains whose agent.handle() takes the ASR transcript and may need
# several turns before it's done (e.g. Plant's follow-up questions).
# Domains not listed here are single-shot: one utterance, one response,
# turn ends immediately (agent.handle(farm_state) with no transcript).
MULTI_TURN_DOMAINS = {"plant"}


class VoiceAgentLoop:
    def __init__(self, forced_domain: str | None = None, events: EventBus | None = None):
        # This technical/demo pipeline doesn't do multi-farm selection by
        # voice (that's the farmer dashboard's job, see farmer_server.py's
        # module docstring) -- it just always operates on the first farm on
        # file, auto-creating one so the loop works with zero setup. It
        # shares the same FARM_STATE_PATH file and a fixed, well-known
        # farmer_id (this is a single-operator local CLI demo, not a
        # multi-tenant server -- see farmer_server.py's FarmStore for why
        # the web dashboard needs real per-farmer identity and this
        # doesn't), so a farm added through the farmer dashboard under
        # that SAME farmer_id shows up here too. A farm created by some
        # other farmer on the deployed web dashboard will NOT show up here
        # -- that's the point of this change, not a regression. Keep the
        # whole store, not just this farmer's FarmState, so saving never
        # clobbers other farmers' data written to the same file.
        self._farm_store = FarmStore.load(config.FARM_STATE_PATH)
        self.farm_state = self._farm_store.get(LOCAL_DEMO_FARMER_ID)
        if not self.farm_state.farms:
            self.farm_state.add_farm("Farm 1")
        else:
            self.farm_state.set_active(0)
        self.wakeword_router = WakewordRouter() if forced_domain is None else None
        self.forced_domain = forced_domain
        self.active_domain: str | None = forced_domain
        self._asr: StreamingASR | None = None
        self.events = events or EventBus()

        self._agents = {}
        for name, agent_cls in DOMAIN_AGENTS.items():
            try:
                self._agents[name] = agent_cls()
            except RuntimeError as exc:
                print(f"[main] '{name}' domain agent unavailable: {exc}")

        self.events.emit("farm_state", farm_state=self.farm_state.to_dict())

    def _on_final_transcript(self, transcript: str) -> None:
        domain = self.active_domain
        # "field" is the wakeword that was heard, not an agent -- resolve
        # it to weather/crop/plant now that we actually have words to
        # route on, same deterministic keyword logic the farmer
        # dashboard's chat uses. self.active_domain is updated too so the rest of this turn
        # (events, _end_turn's idle-domain reset) reflects the REAL domain,
        # not the wakeword name.
        if domain == "field":
            domain = resolve_field_domain(transcript)
            self.active_domain = domain
        print(f"[{domain}] heard: {transcript}")
        self.events.emit("transcript", domain=domain, text=transcript)

        agent = self._agents.get(domain)
        if agent is None:
            message = f"no agent configured for domain '{domain}'"
            print(f"[main] {message}")
            self.events.emit("error", domain=domain, message=message)
            self._end_turn()
            return

        farm = self.farm_state.active_farm
        try:
            if domain in MULTI_TURN_DOMAINS:
                response = agent.handle(farm, transcript)
            elif domain == "weather":
                response = agent.handle(farm, question=transcript)
            else:
                response = agent.handle(farm)
        except Exception as exc:  # noqa: BLE001 -- surface any domain failure without killing the loop
            response = f"(error handling request: {exc})"
            self.events.emit("error", domain=domain, message=str(exc))

        print(f"[{domain}] response: {response}")
        self.events.emit("response", domain=domain, text=response)
        self._farm_store.save(config.FARM_STATE_PATH)
        self.events.emit("farm_state", farm_state=self.farm_state.to_dict())

        if domain in MULTI_TURN_DOMAINS and not self._domain_conversation_done(domain):
            # Stay in this domain -- ASR session remains open for the next
            # follow-up answer instead of returning to wakeword listening.
            return

        self._end_turn()

    def _domain_conversation_done(self, domain: str) -> bool:
        """True if a multi-turn domain has finished its current exchange.

        PlantAgent tracks this per its internal session (session_id
        "default" for the single active conversation a voice agent has at
        once); other multi-turn domains would need their own check here.
        """
        agent = self._agents.get(domain)
        if isinstance(agent, PlantAgent):
            return agent.is_done()
        return True

    def _start_turn(self, domain: str) -> None:
        print(f"[main] wakeword detected -> entering '{domain}' domain")
        self.active_domain = domain
        self.events.emit("state", status="active", domain=domain)
        self._asr = StreamingASR(on_final_transcript=self._on_final_transcript)
        self._asr.connect()

    def _end_turn(self) -> None:
        if self._asr is not None:
            self._asr.disconnect()
            self._asr = None
        if self.forced_domain is None:
            self.active_domain = None
            print("[main] back to listening for wakewords...")
            self.events.emit("state", status="idle", domain=None)

    def on_frame(self, samples, pcm_bytes: bytes) -> None:
        if self.active_domain is not None:
            if self._asr is not None:
                self._asr.send_audio(pcm_bytes)
            return

        if self.wakeword_router is None:
            return

        detection = self.wakeword_router.process_frame(samples)
        if detection is not None:
            self._start_turn(detection.domain)

    def run(self) -> None:
        if self.forced_domain is not None:
            print(f"[main] forced domain '{self.forced_domain}' -- skipping wakeword detection")
            self._start_turn(self.forced_domain)
        else:
            self.events.emit("state", status="idle", domain=None)

        print("[main] listening... (Ctrl+C to stop)")
        stop_event = threading.Event()
        with MicrophoneStream(on_frame=self.on_frame):
            try:
                stop_event.wait()
            except KeyboardInterrupt:
                print("\n[main] stopping")
        if self._asr is not None:
            self._asr.disconnect()


def main() -> None:
    parser = argparse.ArgumentParser(description="Agricultural voice agent")
    parser.add_argument(
        "--domain",
        choices=sorted(DOMAIN_AGENTS.keys()),
        default=None,
        help="Skip wakeword detection and go straight into this domain (for testing ASR wiring without .onnx models)",
    )
    args = parser.parse_args()

    loop = VoiceAgentLoop(forced_domain=args.domain)
    loop.run()


if __name__ == "__main__":
    sys.exit(main() or 0)
