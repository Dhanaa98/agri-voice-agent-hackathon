"""AssemblyAI streaming ASR wrapper.

Wraps the AssemblyAI Python SDK's v3 streaming client (`RealTimeTranscriber`,
aliased as `StreamingClient` in the SDK) behind a small callback-based
interface: feed it raw PCM audio frames, get back finalized transcript
strings via `on_final_transcript`. Built against assemblyai==1.5.4's actual
`assemblyai.streaming.v3` module (verified by reading the installed
package source, not just docs) -- see the project build log for details on
that.

This module only knows about turning audio into text; it doesn't know
about wakewords or domain routing. The main orchestration loop (main.py)
is what wires ASR transcripts to the wakeword-selected domain agent.
"""

from __future__ import annotations

from typing import Callable

from assemblyai.streaming.v3 import (
    BeginEvent,
    Encoding,
    RealTimeError,
    RealTimeEvents,
    RealTimeParameters,
    RealTimeTranscriber,
    RealTimeTranscriberOptions,
    SpeechModel,
    TerminationEvent,
    TurnEvent,
)

from . import config

SAMPLE_RATE = 16_000

FinalTranscriptHandler = Callable[[str], None]
PartialTranscriptHandler = Callable[[str], None]


class StreamingASR:
    """Thin wrapper around AssemblyAI's streaming client for mic-style use.

    Usage:
        asr = StreamingASR(on_final_transcript=handle_text)
        asr.connect()
        asr.send_audio(pcm_bytes)   # called repeatedly as audio arrives
        asr.disconnect()
    """

    def __init__(
        self,
        on_final_transcript: FinalTranscriptHandler,
        on_partial_transcript: PartialTranscriptHandler | None = None,
        api_key: str | None = None,
        sample_rate: int = SAMPLE_RATE,
    ):
        self.api_key = api_key or config.ASSEMBLYAI_API_KEY
        if not self.api_key:
            raise RuntimeError("ASSEMBLYAI_API_KEY is not set. Copy .env.example to .env and fill it in.")

        self.sample_rate = sample_rate
        self._on_final_transcript = on_final_transcript
        self._on_partial_transcript = on_partial_transcript

        self._client = RealTimeTranscriber(
            RealTimeTranscriberOptions(api_key=self.api_key)
        )
        self._client.on(RealTimeEvents.Begin, self._handle_begin)
        self._client.on(RealTimeEvents.Turn, self._handle_turn)
        self._client.on(RealTimeEvents.Termination, self._handle_termination)
        self._client.on(RealTimeEvents.Error, self._handle_error)

    def connect(self) -> None:
        self._client.connect(
            RealTimeParameters(
                sample_rate=self.sample_rate,
                encoding=Encoding.pcm_s16le,
                speech_model=SpeechModel.universal_streaming_multilingual,
                format_turns=True,
            )
        )

    def send_audio(self, pcm_bytes: bytes) -> None:
        """Feed one chunk of raw 16-bit PCM mono audio to the transcriber."""
        self._client.stream(pcm_bytes)

    def disconnect(self) -> None:
        self._client.disconnect(terminate=True)

    def _handle_begin(self, client, event: BeginEvent) -> None:
        print(f"[asr] session started: {event.id}")

    def _handle_turn(self, client, event: TurnEvent) -> None:
        if event.end_of_turn and event.transcript:
            self._on_final_transcript(event.transcript)
        elif event.transcript and self._on_partial_transcript:
            self._on_partial_transcript(event.transcript)

    def _handle_termination(self, client, event: TerminationEvent) -> None:
        print(f"[asr] session terminated ({event.audio_duration_seconds}s of audio processed)")

    def _handle_error(self, client, error: RealTimeError) -> None:
        print(f"[asr] error (code={error.code}): {error}")
