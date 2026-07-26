"""
Shared pytest fixtures and factories for the EduSense AI 360 test suite.

These let the engines and pipelines be tested without the heavy CV stack
(MediaPipe / FER) by supplying synthetic signals and a mock perception result.
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pytest

# Ensure the project root is importable when pytest is run from anywhere.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.config_manager import ConfigManager  # noqa: E402
from backend.contracts.models import (  # noqa: E402
    FaceBox, EyeSignals, EmotionResult, EmotionLabel,
)
from backend.pipeline.frame_pipeline import PerceptionResult, PerceptionFace  # noqa: E402


@pytest.fixture
def config() -> ConfigManager:
    """A fresh, validated configuration manager."""
    return ConfigManager()


@pytest.fixture
def rgb_frame() -> np.ndarray:
    """A synthetic RGB frame with texture (passes the quality gate)."""
    return np.random.default_rng(0).integers(60, 200, size=(120, 160, 3), dtype=np.uint8)


@pytest.fixture
def make_eye():
    def _f(attention: float, confidence: float = 0.9) -> EyeSignals:
        return EyeSignals(eyes_open=attention > 0.3, attention=attention, confidence=confidence)
    return _f


@pytest.fixture
def make_emotion():
    def _f(label: EmotionLabel, contribution: float, confidence: float = 0.8) -> EmotionResult:
        return EmotionResult(dominant=label, engagement_contribution=contribution,
                             confidence=confidence, available=True)
    return _f


@pytest.fixture
def perception_factory(make_eye, make_emotion):
    """Returns a builder producing a PerceptionResult with N students."""
    def _build(students):
        faces = []
        for i, (att, label, contrib) in enumerate(students):
            faces.append(PerceptionFace(
                i, FaceBox(10 + i * 60, 10, 40, 40, 0.9, face_id=i),
                make_eye(att), make_emotion(label, contrib)))
        dominant = students[0][1] if students else EmotionLabel.NEUTRAL
        return PerceptionResult(
            faces=faces, faces_present=len(faces), dominant_emotion=dominant,
            annotated_frame=np.zeros((40, 40, 3), dtype=np.uint8))
    return _build
