"""
EduSense AI 360 - Demo Source
=============================

A synthetic perception source for **Demo Mode** - a reliable, camera-free and
model-free way to show the full system at a science exhibition where the laptop
camera or AI models may be unavailable.

It produces a deterministic, realistic classroom: five students with distinct
"personas" (a star, a steady learner, one who recovers, one who drifts off, and one
who is distracted), and a class-wide engagement arc that starts high, dips during a
long stretch of lecture, then recovers. The output is an ordinary
:class:`PerceptionResult`, so it flows through the *real* analysis pipeline,
analytics, remarks, graphs, and reports - nothing is faked downstream.

Being deterministic (no randomness), every demo run looks the same, which is exactly
what you want when presenting.
"""

from __future__ import annotations

import math
from typing import Any

from backend.contracts.models import FaceBox, EyeSignals, EmotionResult, EmotionLabel
from backend.pipeline.frame_pipeline import PerceptionResult, PerceptionFace

# Box border colours (BGR) by engagement band.
_GREEN = (120, 220, 80)
_AMBER = (40, 180, 250)
_RED = (90, 90, 250)

# Persona attention-arc parameters.
_PERSONAS = [
    {"base": 0.86, "amp": 0.05, "phase": 0.0, "trend": 0.000},   # star
    {"base": 0.70, "amp": 0.08, "phase": 1.0, "trend": 0.000},   # steady
    {"base": 0.54, "amp": 0.10, "phase": 2.0, "trend": 0.005},   # recovers
    {"base": 0.70, "amp": 0.08, "phase": 1.5, "trend": -0.006},  # drifts off
    {"base": 0.30, "amp": 0.12, "phase": 0.5, "trend": 0.000},   # distracted
]

# Relative face positions (x, y, w, h) in [0, 1].
_BOX_POS = [
    (0.10, 0.20, 0.16, 0.30), (0.39, 0.16, 0.15, 0.30), (0.65, 0.22, 0.15, 0.29),
    (0.21, 0.55, 0.15, 0.28), (0.58, 0.56, 0.15, 0.27),
]


def _draw_box(img: Any, x: int, y: int, w: int, h: int, color, th: int = 2) -> None:
    """Draw a rectangle border on a BGR image using NumPy slicing (no OpenCV needed)."""
    H, W = img.shape[:2]
    x = max(0, x); y = max(0, y)
    x2 = min(W - 1, x + w); y2 = min(H - 1, y + h)
    img[y:y + th, x:x2] = color
    img[max(0, y2 - th):y2, x:x2] = color
    img[y:y2, x:x + th] = color
    img[y:y2, max(0, x2 - th):x2] = color


class DemoSource:
    """Deterministic synthetic perception for Demo Mode."""

    def __init__(self, dip_center: int = 18, dip_width: float = 6.0) -> None:
        self.i = 0
        self._dip_center = dip_center
        self._dip_width = dip_width

    def reset(self) -> None:
        self.i = 0

    # -- arcs ---------------------------------------------------------------
    def _class_dip(self) -> float:
        """A gentle Gaussian dip in class-wide attention around the mid-session."""
        x = self.i
        return -0.30 * math.exp(-((x - self._dip_center) ** 2) / (2 * self._dip_width ** 2))

    def _attention_for(self, p: dict) -> float:
        wobble = p["amp"] * math.sin(self.i * 0.5 + p["phase"])
        att = p["base"] + wobble + p["trend"] * self.i + self._class_dip()
        return max(0.05, min(0.99, att))

    @staticmethod
    def _emotion_for(att: float) -> tuple[EmotionLabel, float]:
        if att >= 0.78:
            return EmotionLabel.HAPPY, 0.9
        if att >= 0.50:
            return EmotionLabel.NEUTRAL, 0.2
        if att >= 0.32:
            return EmotionLabel.SAD, -0.4
        return EmotionLabel.SAD, -0.55

    # -- perception ---------------------------------------------------------
    def process(self, processed: Any) -> PerceptionResult:
        """Return a synthetic PerceptionResult for the current demo frame."""
        self.i += 1
        canvas = processed.bgr.copy() if hasattr(processed.bgr, "copy") else processed.bgr
        H, W = canvas.shape[:2]

        faces: list[PerceptionFace] = []
        emotions: list[EmotionLabel] = []
        for idx, persona in enumerate(_PERSONAS):
            att = self._attention_for(persona)
            label, contribution = self._emotion_for(att)
            emotions.append(label)

            rx, ry, rw, rh = _BOX_POS[idx]
            x, y, w, h = int(rx * W), int(ry * H), int(rw * W), int(rh * H)
            color = _GREEN if att >= 0.60 else (_AMBER if att >= 0.40 else _RED)
            _draw_box(canvas, x, y, w, h, color)

            faces.append(PerceptionFace(
                idx,
                FaceBox(x, y, w, h, 0.9, face_id=idx),
                EyeSignals(eyes_open=att > 0.3, attention=att, confidence=0.85),
                EmotionResult(dominant=label, engagement_contribution=contribution,
                              confidence=0.8, available=True),
            ))

        dominant = max(set(emotions), key=emotions.count) if emotions else EmotionLabel.NEUTRAL
        return PerceptionResult(
            faces=faces, faces_present=len(faces), dominant_emotion=dominant,
            annotated_frame=canvas, quality_confidence=1.0,
        )
