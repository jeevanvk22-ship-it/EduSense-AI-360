"""
EduSense AI 360 - Emotion Detection
===================================

Classifies per-student facial emotion and maps it to an engagement contribution
(Functional Requirements Part 1B §4; AI Decision Logic Part 6 §3).

Key behaviours
--------------
* Pluggable backend ("fer" default, "deepface" optional), imported lazily.
* **Temporal smoothing** per face id: scores are averaged over a rolling window so
  the reported emotion is stable, not the latest raw prediction (transient vs
  sustained distinction, Part 6 §3.4).
* **Confidence floor:** weak predictions default toward Neutral rather than
  asserting an uncertain emotion.
* Maps the stabilised distribution to an engagement contribution in [-1, 1] using
  configured per-emotion weights.

The model call is isolated in :meth:`_predict`, so smoothing/mapping logic is
testable with a scripted backend.
"""

from __future__ import annotations

from collections import deque
from typing import Any, Optional

from config.config_manager import ConfigManager
from backend.contracts.models import EmotionResult, EmotionLabel
from core.exceptions import EmotionError
from core.error_handler import handle
from core.logger import get_logger
from utilities.helpers import clamp

log = get_logger("ai")

_FER_EMOTIONS = ("angry", "disgust", "fear", "happy", "sad", "surprise", "neutral")


class EmotionDetector:
    """Detects and stabilises facial emotion per tracked face."""

    def __init__(self, config: ConfigManager) -> None:
        em = config.section("emotion")
        self._backend_name = str(em.get("backend", "fer"))
        self._confidence_floor = float(em.get("confidence_threshold", 0.35))
        self._window = int(em.get("smoothing_window", 8))
        self._weights = dict(em.get("engagement_weights", {}))

        self._engine: Any = None
        self._available: Optional[bool] = None
        self._history: dict[int, deque] = {}

    # -- model lifecycle ----------------------------------------------------
    def _ensure_loaded(self) -> bool:
        if self._available is not None:
            return self._available
        try:
            if self._backend_name == "fer":
                from fer import FER
                self._engine = FER(mtcnn=False)
            elif self._backend_name == "deepface":
                from deepface import DeepFace
                self._engine = DeepFace
            else:
                raise EmotionError(f"Unknown emotion backend: {self._backend_name}")
            self._available = True
            log.info("Emotion detector loaded (backend=%s).", self._backend_name)
        except Exception as exc:  # noqa: BLE001
            self._available = False
            handle(EmotionError(f"Emotion backend unavailable: {exc}"),
                   context="emotion load", category="ai")
        return self._available

    @property
    def available(self) -> bool:
        return bool(self._ensure_loaded())

    def reset(self) -> None:
        self._history.clear()

    # -- mapping ------------------------------------------------------------
    def _to_contribution(self, scores: dict[str, float]) -> float:
        total = 0.0
        for emotion, prob in scores.items():
            total += self._weights.get(emotion, 0.0) * prob
        return clamp(total, -1.0, 1.0)

    def _smooth(self, face_id: int, scores: dict[str, float]) -> dict[str, float]:
        """Average the score distribution over the rolling window for this face."""
        buf = self._history.setdefault(face_id, deque(maxlen=self._window))
        buf.append(scores)
        keys = set().union(*buf)
        return {k: sum(s.get(k, 0.0) for s in buf) / len(buf) for k in keys}

    # -- model seam (mockable) ---------------------------------------------
    def _predict(self, face_bgr: Any) -> Optional[dict[str, float]]:
        """Run the backend and return a normalised score distribution, or None."""
        if self._backend_name == "fer":
            detections = self._engine.detect_emotions(face_bgr)
            if not detections:
                return None
            return dict(detections[0]["emotions"])
        # deepface
        res = self._engine.analyze(face_bgr, actions=["emotion"],
                                   enforce_detection=False, silent=True)
        res = res[0] if isinstance(res, list) else res
        raw = res["emotion"]
        total = sum(raw.values()) or 1.0
        return {k: v / total for k, v in raw.items()}

    # -- public api ---------------------------------------------------------
    def analyze(self, face_bgr: Any, face_id: int = 0,
                quality_confidence: float = 1.0) -> EmotionResult:
        """Classify a face crop, smoothing and mapping the result."""
        if not self._ensure_loaded():
            return EmotionResult(available=False)
        if face_bgr is None or getattr(face_bgr, "size", 0) == 0:
            return EmotionResult()

        try:
            raw = self._predict(face_bgr)
        except Exception as exc:  # noqa: BLE001 - per-face fault must not break stream
            handle(EmotionError(f"Emotion prediction failed: {exc}"),
                   context="emotion prediction", category="ai")
            return EmotionResult()

        if not raw:
            return EmotionResult()

        # Normalise then smooth over time.
        total = sum(raw.values()) or 1.0
        norm = {k: v / total for k, v in raw.items()}
        smoothed = self._smooth(face_id, norm)

        dominant_key = max(smoothed, key=smoothed.get)
        dominant_prob = smoothed[dominant_key]
        confidence = clamp(dominant_prob * quality_confidence, 0.0, 1.0)

        # Confidence floor: weak predictions default toward Neutral.
        if confidence < self._confidence_floor:
            dominant = EmotionLabel.NEUTRAL
        else:
            dominant = self._to_label(dominant_key)

        return EmotionResult(
            dominant=dominant,
            scores={k: round(float(v), 3) for k, v in smoothed.items()},
            confidence=round(confidence, 3),
            engagement_contribution=round(self._to_contribution(smoothed), 3),
            available=True,
        )

    @staticmethod
    def _to_label(key: str) -> EmotionLabel:
        try:
            return EmotionLabel(key)
        except ValueError:
            return EmotionLabel.NEUTRAL
