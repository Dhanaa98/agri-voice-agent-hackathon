"""Microphone audio capture, shared by the wakeword router and ASR.

Both consumers need the same continuous 16kHz mono PCM stream: the
wakeword router scores it frame-by-frame looking for "Hey Green" /
"Hey Doc", and once triggered, ASR consumes it to transcribe
the following speech. `MicrophoneStream` exposes raw frames via a callback
so `main.py` can fan them out to whichever consumer is currently active.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16_000
FRAME_MS = 30
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)

FrameHandler = Callable[[np.ndarray, bytes], None]


class MicrophoneStream:
    """Opens the default input device and delivers fixed-size frames.

    Each frame is delivered both as an int16 numpy array (for wakeword
    scoring, which expects numeric samples) and as raw little-endian PCM
    bytes (for AssemblyAI streaming, which expects a byte stream).
    """

    def __init__(self, on_frame: FrameHandler, sample_rate: int = SAMPLE_RATE, frame_samples: int = FRAME_SAMPLES):
        self.sample_rate = sample_rate
        self.frame_samples = frame_samples
        self._on_frame = on_frame
        self._stream: sd.InputStream | None = None

    def _callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        if status:
            print(f"[audio] input stream status: {status}")
        samples = indata[:, 0].astype(np.int16)
        self._on_frame(samples, samples.tobytes())

    def start(self) -> None:
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            blocksize=self.frame_samples,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def __enter__(self) -> "MicrophoneStream":
        self.start()
        return self

    def __exit__(self, *exc_info) -> None:
        self.stop()
