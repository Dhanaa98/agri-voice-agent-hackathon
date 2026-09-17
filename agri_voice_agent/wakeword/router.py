"""Multi-wakeword routing layer.

Two ONNX wakeword models: "Hey Field" (covers both Weather and Crop --
main.py resolves which one via intent.py's resolve_field_domain() once the
transcript comes back, same deterministic keyword approach the farmer
dashboard's chat uses) and "Hey Plant" (kept separate -- disease diagnosis
is a different conversation shape, multi-turn and symptom-driven rather
than a one-shot question). Originally three wakewords, one per domain
(Weather/Crop/Plant); Weather and Crop were merged because in practice
they're both short, single-shot informational questions a farmer asks
without first deciding which specialist they want ("how's it looking out
there" could be either), and "Hey Crop" specifically was acoustically weak
on its own -- short, hard-stop ending, too close to "Hey Plant".

First detector to cross its confidence threshold wins for a given frame.

Drop your trained .onnx models into agri_voice_agent/wakeword/models/ named
field.onnx, plant.onnx (or pass explicit paths to WakewordRouter) and this
becomes live. Until then, `detect()` accepts a manually-supplied domain
name so the rest of the pipeline (ASR + domain agents) can be built and
tested independently of the wakeword models.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import onnxruntime as ort

from .. import config

DOMAINS = ("field", "plant")

DEFAULT_THRESHOLDS = {
    "field": 0.5,
    "plant": 0.5,
}


@dataclass
class WakewordDetection:
    domain: str
    confidence: float


class WakewordModel:
    """Wraps a single ONNX wakeword model for one domain."""

    def __init__(self, domain: str, model_path: Path, threshold: float = 0.5):
        self.domain = domain
        self.threshold = threshold
        self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])
        self._input_name = self.session.get_inputs()[0].name

    def score(self, audio_frame: np.ndarray) -> float:
        """Run inference on one audio frame, return confidence in [0, 1]."""
        outputs = self.session.run(None, {self._input_name: audio_frame})
        return float(outputs[0].squeeze())


class WakewordRouter:
    """Loads both wakeword models ("field", "plant") and routes incoming audio.

    Instantiation is lazy per-model: if a model file is missing, that
    domain is simply unavailable for detection (logged, not fatal), so the
    router can run in a partially-configured state during development.
    """

    def __init__(
        self,
        model_paths: dict[str, Path] | None = None,
        thresholds: dict[str, float] | None = None,
    ):
        self.thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
        model_paths = model_paths or {
            domain: config.WAKEWORD_MODELS_DIR / f"{domain}.onnx" for domain in DOMAINS
        }
        self.models: dict[str, WakewordModel] = {}
        for domain, path in model_paths.items():
            if Path(path).exists():
                self.models[domain] = WakewordModel(domain, Path(path), self.thresholds[domain])
            else:
                print(f"[wakeword] no model found for '{domain}' at {path} -- domain disabled until provided")

    def process_frame(self, audio_frame: np.ndarray) -> WakewordDetection | None:
        """Score one audio frame against every loaded model.

        Returns the highest-confidence detector that crossed its threshold,
        or None if nothing triggered. If multiple detectors cross threshold
        on the same frame, the highest-confidence one wins (helps reduce
        cross-triggering between the two wakeword phrases).
        """
        best: WakewordDetection | None = None
        for domain, model in self.models.items():
            confidence = model.score(audio_frame)
            if confidence >= model.threshold and (best is None or confidence > best.confidence):
                best = WakewordDetection(domain=domain, confidence=confidence)
        return best
