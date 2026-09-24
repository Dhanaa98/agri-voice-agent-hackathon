"""Farmer-facing dashboard server: one chat, three agents underneath.

Separate from dashboard_server.py (the technical/judge-facing view over
VoiceAgentLoop's continuous mic + wakeword pipeline, which uses its own
"Hey Green"/"Hey Doc" wakewords -- see wakeword/router.py -- and is left
untouched by this file's own single-chat routing).

This server used to make the farmer click a Weather/Crop/Plant button
before every question (mirroring the wakeword concept in click form). In
practice a farmer chatting naturally forgets to re-click when their topic
shifts mid-conversation -- "do you think we have rain next week" while the
Plant button was still active would silently go to the wrong agent. So the
farmer-facing side is now a SINGLE chat: every message runs through
intent.py's keyword detection to pick the right agent automatically (see
route_message() below), with the previously-active domain kept as the
fallback when a message's wording doesn't clearly point anywhere (e.g. "ok
thanks" or a Plant follow-up answer) rather than guessing wrong.

Two ways a farmer's utterance reaches a domain agent:
  1. POST /chat -- typed text, works everywhere, no API key beyond the
     optional GEMINI_API_KEY for natural phrasing. Fully built and tested.
  2. WS /voice -- browser-captured microphone audio streamed to the
     server, fed into StreamingASR, transcribed text routed the same way
     as typed input. Requires ASSEMBLYAI_API_KEY. Built to the same API
     contract as asr.py, but UNVERIFIED end-to-end: no AssemblyAI key is
     configured in this project yet, so this path has only been exercised
     for construction/import correctness, not a real microphone-to-
     transcript round trip. Test with a real key before relying on it.

Both paths write into the same shared FarmState (loaded/saved at
config.FARM_STATE_PATH) that dashboard_server.py's VoiceAgentLoop also
uses, so a farmer's diagnosis here is visible to the technical dashboard
and vice versa -- one farm list, one state, two front ends.

A farmer can have more than one farm (different fields, can be in
different regions), so farm selection happens on every fresh exchange
(never mid-Plant-diagnosis, same guard as the cross-domain redirect):
  - 0 farms and no location given -- agents still run against an ephemeral,
    unsaved FarmProfile so "what can I grow" works with zero setup; the
    farmer is nudged for a location so it can be saved once given.
  - 0 farms and a location IS given -- that location becomes farm #1
    automatically (default name "Farm 1", renameable later), so the next
    visit doesn't ask again.
  - 1 farm -- used silently, never asked about.
  - 2+ farms -- resolved by an explicit `farm_name` in the request if given
    (e.g. a farmer says "how's the weather on my north field"), otherwise
    the server asks which farm before calling any domain agent.
See resolve_active_farm() below for the actual decision logic.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import requests
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .asr import StreamingASR
from .domains.crop import CropAgent
from .domains.plant import PlantAgent
from .domains.weather import WeatherAgent
from .farm_state import FarmProfile, FarmState
from .intent import detect_domain

STATIC_DIR = Path(__file__).resolve().parent / "static"
WAKEWORD_MODELS_DIR = config.WAKEWORD_MODELS_DIR

DOMAIN_AGENTS = {
    "weather": WeatherAgent,
    "crop": CropAgent,
    "plant": PlantAgent,
}

# Same distinction as main.py: Plant holds a multi-turn session (up to 2
# follow-up questions) via PlantSession; Weather/Crop answer in one shot.
MULTI_TURN_DOMAINS = {"plant"}

app = FastAPI(title="Farmer Dashboard")

# Serves whatever .onnx wakeword models actually exist (dropped in by the
# user, see wakeword/router.py's module docstring -- this project has no
# training pipeline of its own) to the browser for client-side detection
# via onnxruntime-web. The directory is created empty at project scaffold
# time (only a .gitkeep) so this mount never 404s the whole app even
# before any model file is provided -- individual file requests 404
# normally until their .onnx actually exists, which /capabilities'
# wakeword_models field lets the frontend check for up front.
WAKEWORD_MODELS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/wakeword-models", StaticFiles(directory=str(WAKEWORD_MODELS_DIR)), name="wakeword-models")

# Single-chat routing: which domain the last message was routed to, so a
# message whose wording doesn't clearly point anywhere (see route_message)
# stays on-topic instead of falling back to an arbitrary default. Starts on
# "crop" -- picking what to plant is the most common zero-context question
# a farmer opens with, and it needs no location/weather data to answer.
_current_domain = "crop"

_farm_state = FarmState.load(config.FARM_STATE_PATH)
_agents: dict[str, object] = {}
for _name, _cls in DOMAIN_AGENTS.items():
    try:
        _agents[_name] = _cls()
    except RuntimeError as exc:
        print(f"[farmer_server] '{_name}' domain agent unavailable: {exc}")


def _domain_conversation_done(domain: str) -> bool:
    """Mirrors main.py's VoiceAgentLoop._domain_conversation_done -- True
    once a multi-turn domain (Plant) has reached a final diagnosis for its
    current session, so the frontend knows whether to keep prompting for
    another follow-up answer or the exchange is complete."""
    agent = _agents.get(domain)
    if isinstance(agent, PlantAgent):
        return agent.is_done()
    return True


def route_message(text: str) -> tuple[str, bool, bool]:
    """Pick which domain this message belongs to. Returns (domain,
    is_fresh_exchange, switched).

    `is_fresh_exchange` is False only when continuing the currently-active
    multi-turn Plant conversation -- the farmer's answer to a follow-up
    question (e.g. "the whole plant, not just one branch") must never be
    re-routed, since it's a response to a pending question, not a new
    topic, even if its wording happens to overlap another domain's
    keywords. Otherwise, intent.py's keyword match decides; a message with
    no clear match (e.g. "ok thanks", "what about next week") stays on
    whatever domain was already active rather than guessing, since that's
    usually still a continuation of the same topic in natural chat.

    `switched` is True only when this message's own wording caused a
    change from the previously-active domain -- used to show a "switched
    to X" note in the UI without one firing on every single message.
    """
    global _current_domain

    mid_plant_conversation = _current_domain == "plant" and not _domain_conversation_done("plant")
    if mid_plant_conversation:
        return "plant", False, False

    previous = _current_domain
    detected = detect_domain(text)
    if detected is not None:
        _current_domain = detected
    return _current_domain, True, _current_domain != previous


def _find_farm_by_name(name: str) -> int | None:
    lowered = name.strip().lower()
    for i, f in enumerate(_farm_state.farms):
        if f.name.strip().lower() == lowered:
            return i
    return None


# Reused (not recreated) across calls with zero farms / an unresolved
# ambiguous selection, so a multi-turn Plant conversation started before
# any farm exists keeps writing its symptom report onto the SAME object
# PlantSession cached via set_farm() on turn 1 -- a fresh FarmProfile every
# call would make farm.add_symptom_report() on the final turn write onto a
# throwaway object and silently lose the report. Not persisted to disk;
# becomes moot the moment a real farm exists (all other resolve_active_farm
# branches return a `_farm_state.farms[...]` entry instead).
_scratch_farm = FarmProfile(name="", location_confirmed=False)


def resolve_active_farm(
    farm_name: str | None, location: str | None
) -> tuple[FarmProfile, bool, list[str] | None]:
    """Decide which farm this exchange is about, per the module docstring's
    rules. Returns (farm, is_ephemeral, ambiguous_farm_names).

    `is_ephemeral` is True when the returned FarmProfile is a scratch
    object not stored in `_farm_state.farms` -- the zero-farms-yet case, so
    "what can I grow" works before any farm exists. `ambiguous_farm_names`
    is non-None only when there are 2+ farms and neither `farm_name` nor
    the currently active farm disambiguates which one is meant; callers
    must then skip calling any domain agent and ask the farmer to pick.
    """
    if farm_name:
        idx = _find_farm_by_name(farm_name)
        if idx is not None:
            _farm_state.set_active(idx)
            return _farm_state.farms[idx], False, None
        # Named a farm that doesn't exist -- fall through to normal
        # resolution rather than silently ignoring what they said.

    if len(_farm_state.farms) == 0:
        if location:
            # First-ever confirmed location becomes farm #1 automatically,
            # so the farmer is never asked to explicitly "create a farm" --
            # see the module docstring's auto-save rule.
            idx = _farm_state.add_farm("Farm 1", location=location, location_confirmed=True)
            return _farm_state.farms[idx], False, None
        # No farms, no location yet -- still usable anonymously (e.g. crop
        # suitability without weather), via a scratch, unsaved profile.
        return _scratch_farm, True, None

    if len(_farm_state.farms) == 1:
        _farm_state.set_active(0)
        return _farm_state.farms[0], False, None

    # 2+ farms: an already-active selection from a prior turn still counts
    # (so a farmer doesn't get re-asked every single message), but a fresh
    # session with nothing active is genuinely ambiguous.
    active = _farm_state.active_farm
    if active is not None:
        return active, False, None

    return _scratch_farm, True, [f.name for f in _farm_state.farms]


class ChatIn(BaseModel):
    text: str
    crop: str | None = None
    # Only meaningful for the weather domain -- see resolve_active_farm().
    # Lets the farmer set/change where a farm actually is instead of every
    # request silently using config.DEFAULT_LOCATION.
    location: str | None = None
    # Which farm this question is about, when the farmer has more than one
    # (e.g. picked from the farm-disambiguation prompt, or the Farms
    # section's selector). Also accepted as a spoken/typed farm name.
    farm_name: str | None = None


class ChatOut(BaseModel):
    domain: str
    response: str
    done: bool
    farm_state: dict
    # True when this message's own wording caused the chat to switch
    # agents from whatever was active before -- see route_message() in
    # intent.py. The frontend uses this to show a small "switched to X"
    # note so the farmer can see why the topic changed, without having to
    # click anything themselves.
    switched: bool = False
    # True when a weather question was answered using a fallback/default
    # location rather than one the farmer actually gave -- the frontend
    # uses this to prompt for a real location instead of silently reusing
    # config.DEFAULT_LOCATION forever.
    needs_location: bool = False
    # Non-None only when 2+ farms exist and it's unclear which one this
    # question is about -- no domain agent was called this turn; the
    # frontend should ask the farmer to pick one of these names and resend
    # with `farm_name` set.
    ambiguous_farms: list[str] | None = None


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "farmer.html")


@app.get("/wakeword-test")
async def wakeword_test() -> FileResponse:
    """Standalone wakeword-detection test page -- no chat, no ASR, no API
    keys needed. Exists specifically to test the client-side openWakeWord
    pipeline in isolation (does saying "Hey Green" out loud actually cross
    the 0.2 threshold) without ASSEMBLYAI_API_KEY gating the farmer
    dashboard's own wake-toggle button. See static/wakeword_test.html."""
    return FileResponse(STATIC_DIR / "wakeword_test.html")


@app.get("/capabilities")
async def capabilities() -> dict:
    """Tells the frontend what's actually usable right now, so it can show
    the mic button only when a real voice round-trip is possible instead
    of offering a control that would just fail.

    `wakeword_models` reports which wakewords have a COMPLETE, runnable
    detection chain -- not just their own classifier .onnx but also the
    two shared openWakeWord feature-extraction models (melspectrogram.onnx,
    embedding_model.onnx) every classifier depends on (see farmer.html's
    voice module: raw audio -> melspectrogram -> embedding -> classifier,
    each a separate .onnx file). A classifier file alone can't detect
    anything -- its input is a stack of 16 embeddings, not raw audio -- so
    reporting true without the shared models present would let the
    frontend start a wakeword loop that can never actually fire. All three
    files are served to the browser at /wakeword-models/<name>.onnx via
    the StaticFiles mount below. Wakeword listening additionally needs
    mic_available (ASSEMBLYAI_API_KEY) since detecting the wakeword is only
    useful if the follow-up speech can then actually be transcribed.
    """
    shared_models_present = (WAKEWORD_MODELS_DIR / "melspectrogram.onnx").exists() and (
        WAKEWORD_MODELS_DIR / "embedding_model.onnx"
    ).exists()
    return {
        "mic_available": bool(config.ASSEMBLYAI_API_KEY),
        "phrasing_available": bool(config.GEMINI_API_KEY),
        "domains_available": {name: name in _agents for name in DOMAIN_AGENTS},
        "wakeword_models": {
            name: shared_models_present and (WAKEWORD_MODELS_DIR / f"{name}.onnx").exists()
            for name in ("field", "plant")
        },
    }


@app.get("/farm_state")
async def get_farm_state() -> dict:
    return _farm_state.to_dict()


class FarmOut(BaseModel):
    index: int
    name: str
    location: str
    location_confirmed: bool
    active: bool


@app.get("/farms", response_model=list[FarmOut])
async def list_farms() -> list[FarmOut]:
    return [
        FarmOut(
            index=i,
            name=f.name,
            location=f.location,
            location_confirmed=f.location_confirmed,
            active=(i == _farm_state.active_farm_index),
        )
        for i, f in enumerate(_farm_state.farms)
    ]


class AddFarmIn(BaseModel):
    name: str
    location: str | None = None


@app.post("/farms", response_model=FarmOut)
async def add_farm(body: AddFarmIn) -> FarmOut:
    """Explicitly add a farm from the Farms section UI (as opposed to the
    auto-save-as-"Farm 1" path in resolve_active_farm(), which only fires
    for the very first farm)."""
    name = body.name.strip() or f"Farm {len(_farm_state.farms) + 1}"
    idx = _farm_state.add_farm(name, location=body.location or "", location_confirmed=bool(body.location))
    _farm_state.save(config.FARM_STATE_PATH)
    f = _farm_state.farms[idx]
    return FarmOut(index=idx, name=f.name, location=f.location, location_confirmed=f.location_confirmed, active=True)


@app.post("/farms/{index}/select", response_model=FarmOut)
async def select_farm(index: int) -> FarmOut:
    if not (0 <= index < len(_farm_state.farms)):
        raise ValueError(f"No farm at index {index}")
    _farm_state.set_active(index)
    _farm_state.save(config.FARM_STATE_PATH)
    f = _farm_state.farms[index]
    return FarmOut(index=index, name=f.name, location=f.location, location_confirmed=f.location_confirmed, active=True)


class UpdateFarmIn(BaseModel):
    name: str | None = None
    location: str | None = None


@app.patch("/farms/{index}", response_model=FarmOut)
async def update_farm(index: int, body: UpdateFarmIn) -> FarmOut:
    """Rename a farm and/or change its saved location after it's already
    been added -- separate from POST /farms (creates a new one) and
    POST /farms/{index}/select (switches which is active). Either field
    may be omitted to leave it unchanged."""
    if not (0 <= index < len(_farm_state.farms)):
        raise ValueError(f"No farm at index {index}")
    f = _farm_state.farms[index]
    if body.name is not None:
        name = body.name.strip()
        if name:
            f.name = name
    if body.location is not None:
        location = body.location.strip()
        f.location = location
        f.location_confirmed = bool(location)
    _farm_state.save(config.FARM_STATE_PATH)
    return FarmOut(index=index, name=f.name, location=f.location, location_confirmed=f.location_confirmed, active=(index == _farm_state.active_farm_index))


class ResolveLocationIn(BaseModel):
    # GPS fix from the browser's navigator.geolocation, when the farmer
    # granted permission. Omitted (both None) triggers the IP-based
    # fallback below.
    lat: float | None = None
    lon: float | None = None


class ResolveLocationOut(BaseModel):
    location: str | None
    source: str  # "gps" | "ip" | "unavailable"


@app.post("/resolve_location", response_model=ResolveLocationOut)
async def resolve_location(body: ResolveLocationIn, request: Request) -> ResolveLocationOut:
    """Auto-detect a location so a farmer doesn't have to type one for
    their first farm. GPS first (device-accurate, needs the browser's
    permission prompt), then IP-geolocation as a same-page fallback if GPS
    was denied or unsupported -- coarser (city-level, via the request's
    public IP) but needs no permission and never blocks the farmer from
    getting *some* auto-filled location.

    This only *resolves a name*; it does not create or modify any farm --
    the frontend still runs it through /chat (or /farms) with the
    resolved name, so the existing farm-creation/confirmation bookkeeping
    stays in one place.
    """
    weather_agent = _agents.get("weather")
    if isinstance(weather_agent, WeatherAgent) and body.lat is not None and body.lon is not None:
        try:
            name = weather_agent.reverse_geocode(body.lat, body.lon)
            return ResolveLocationOut(location=name, source="gps")
        except Exception:  # noqa: BLE001 -- fall through to IP-based lookup
            pass

    client_ip = request.client.host if request.client else None
    # Loopback/private addresses (local dev) can't be IP-geolocated -- skip
    # straight to "unavailable" rather than sending a useless lookup.
    if client_ip and not client_ip.startswith(("127.", "10.", "192.168.", "::1")):
        try:
            # ip-api.com's free tier only serves plain HTTP (its HTTPS
            # endpoint requires a paid key) -- fine here since the only data
            # in flight is the request's own public IP and a resulting
            # city/country, not anything sensitive.
            resp = requests.get(f"http://ip-api.com/json/{client_ip}", timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") == "success":
                city = data.get("city", "")
                country = data.get("countryCode", "")
                if city and country:
                    return ResolveLocationOut(location=f"{city},{country}", source="ip")
        except Exception:  # noqa: BLE001 -- IP geolocation is best-effort
            pass

    return ResolveLocationOut(location=None, source="unavailable")


@app.post("/chat", response_model=ChatOut)
async def chat(body: ChatIn) -> ChatOut:
    """Single-chat typed-text path -- see module docstring. route_message()
    decides which domain handles this message; the frontend never tells us
    which agent to use."""
    domain, is_fresh_exchange, switched = route_message(body.text)

    agent = _agents.get(domain)
    if agent is None:
        return ChatOut(
            domain=domain,
            response=f"The {domain} agent isn't available right now (missing an API key).",
            done=True,
            farm_state=_farm_state.to_dict(),
        )

    if is_fresh_exchange:
        farm, _, ambiguous = resolve_active_farm(body.farm_name, body.location)
        if ambiguous is not None:
            return ChatOut(
                domain=domain,
                response="You have more than one farm -- which one is this about: " + ", ".join(ambiguous) + "?",
                done=True,
                farm_state=_farm_state.to_dict(),
                ambiguous_farms=ambiguous,
            )
    else:
        # Mid multi-turn conversation (Plant): keep using whichever farm
        # the session already started against, never re-resolve.
        farm, _, _ = resolve_active_farm(None, None)

    needs_location = False

    try:
        if domain in MULTI_TURN_DOMAINS:
            response = agent.handle(farm, body.text, crop=body.crop)
        elif domain == "weather":
            # location=None here still resolves via WeatherAgent.handle()'s
            # own fallback chain (explicit -> farm.location ->
            # config.DEFAULT_LOCATION). needs_location is driven by
            # farm.location_confirmed, which WeatherAgent.handle() only
            # sets True when a real explicit location was given -- falling
            # all the way back to config.DEFAULT_LOCATION does NOT count as
            # confirmed, so the prompt keeps showing on every query until
            # the farmer actually supplies a location, not just the first.
            response = agent.handle(farm, location=body.location, question=body.text)
            needs_location = not farm.location_confirmed
        elif domain == "crop":
            response = agent.handle(farm, crop_name=body.crop)
        else:
            response = agent.handle(farm)
    except Exception as exc:  # noqa: BLE001 -- surface the failure to the farmer, don't crash the server
        response = f"Something went wrong handling that: {exc}"

    farm.add_chat_turn(domain=domain, role="farmer", text=body.text)
    farm.add_chat_turn(domain=domain, role="agent", text=response)
    _farm_state.save(config.FARM_STATE_PATH)
    done = _domain_conversation_done(domain) if domain in MULTI_TURN_DOMAINS else True

    return ChatOut(
        domain=domain,
        response=response,
        done=done,
        farm_state=_farm_state.to_dict(),
        switched=switched,
        needs_location=needs_location,
    )


@app.websocket("/voice")
async def voice_session(websocket: WebSocket) -> None:
    """Real-microphone path: browser streams raw 16-bit PCM audio frames
    over this socket, server feeds them to StreamingASR, and the final
    transcript is routed the same way as a typed /chat message once ASR
    reports end-of-turn -- see module docstring. UNVERIFIED end-to-end, no
    AssemblyAI key configured in this project yet.
    """
    await websocket.accept()

    if not config.ASSEMBLYAI_API_KEY:
        await websocket.send_json({"type": "error", "message": "Voice input needs ASSEMBLYAI_API_KEY to be set."})
        await websocket.close()
        return

    loop = asyncio.get_running_loop()

    def on_final_transcript(transcript: str) -> None:
        asyncio.run_coroutine_threadsafe(_handle_voice_transcript(websocket, transcript), loop)

    try:
        asr = StreamingASR(on_final_transcript=on_final_transcript)
        # StreamingASR.connect() is a BLOCKING call -- it only returns once
        # AssemblyAI's websocket handshake actually succeeds, which includes
        # an internal SDK retry after an initial SSL handshake timeout
        # (~4.6-4.8s observed on this machine, reproducible every time, see
        # docs/build_log.md). Run it in a thread so this coroutine doesn't
        # block the event loop, and explicitly signal "ready" to the browser
        # only once it returns -- the browser must not start streaming PCM
        # before this, or the first several seconds of the farmer's speech
        # never reach AssemblyAI (this was the root cause of transcripts
        # like "what is the weather" coming back as garbled fragments).
        await loop.run_in_executor(None, asr.connect)
    except Exception as exc:  # noqa: BLE001 -- report connection failure, don't crash the endpoint
        await websocket.send_json({"type": "error", "message": f"Could not start voice session: {exc}"})
        await websocket.close()
        return

    await websocket.send_json({"type": "ready"})

    try:
        while True:
            data = await websocket.receive_bytes()
            asr.send_audio(data)
    except WebSocketDisconnect:
        pass
    finally:
        asr.disconnect()


async def _handle_voice_transcript(websocket: WebSocket, transcript: str) -> None:
    domain, is_fresh_exchange, switched = route_message(transcript)

    agent = _agents.get(domain)
    if agent is None:
        await websocket.send_json({"type": "error", "message": f"The {domain} agent isn't available right now."})
        return

    if is_fresh_exchange:
        # Voice input has no separate "location"/"farm_name" fields the way
        # typed input does -- farm disambiguation for speech relies on the
        # same already-active farm (or the single-farm/zero-farm defaults);
        # a multi-farm farmer switching farms by voice says so in their
        # transcript, which is future work once a real ASR key is in use.
        farm, _, ambiguous = resolve_active_farm(None, None)
        if ambiguous is not None:
            await websocket.send_json(
                {
                    "type": "result",
                    "domain": domain,
                    "transcript": transcript,
                    "response": "You have more than one farm -- which one is this about: "
                    + ", ".join(ambiguous)
                    + "?",
                    "done": True,
                    "farm_state": _farm_state.to_dict(),
                    "ambiguous_farms": ambiguous,
                }
            )
            return
    else:
        farm, _, _ = resolve_active_farm(None, None)

    needs_location = False

    try:
        if domain in MULTI_TURN_DOMAINS:
            response = agent.handle(farm, transcript)
        elif domain == "weather":
            response = agent.handle(farm, question=transcript)
            needs_location = not farm.location_confirmed
        else:
            response = agent.handle(farm)
    except Exception as exc:  # noqa: BLE001
        response = f"Something went wrong handling that: {exc}"

    farm.add_chat_turn(domain=domain, role="farmer", text=transcript)
    farm.add_chat_turn(domain=domain, role="agent", text=response)
    _farm_state.save(config.FARM_STATE_PATH)
    done = _domain_conversation_done(domain) if domain in MULTI_TURN_DOMAINS else True

    await websocket.send_json(
        {
            "type": "result",
            "domain": domain,
            "transcript": transcript,
            "response": response,
            "done": done,
            "farm_state": _farm_state.to_dict(),
            "switched": switched,
            "needs_location": needs_location,
        }
    )


def main() -> None:
    import argparse
    import os

    import uvicorn

    # Cloud hosts (Render/Railway/Fly.io) inject the port to bind via $PORT
    # and expect the process to listen on 0.0.0.0, not localhost -- local
    # dev still defaults to 127.0.0.1:8001 same as before when $PORT isn't
    # set, so `python -m agri_voice_agent.farmer_server` with no flags
    # keeps working unchanged.
    parser = argparse.ArgumentParser(description="Farmer-facing dashboard server")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0" if os.getenv("PORT") else "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8001")))
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
