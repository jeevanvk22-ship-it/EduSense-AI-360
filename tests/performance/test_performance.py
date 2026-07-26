"""Performance smoke test: per-frame analysis stays within a sane budget."""

from __future__ import annotations

import time

import numpy as np

from backend.contracts.models import EmotionLabel
from backend.camera.frame_processor import FrameProcessor
from backend.ai_models.model_registry import ModelRegistry
from backend.pipeline.analysis_pipeline import AnalysisPipeline


class TestPerformance:
    def test_analysis_frame_time(self, config, perception_factory):
        """With perception mocked, the analytics/scoring path is well under budget."""
        registry = ModelRegistry(config)
        pipe = AnalysisPipeline(config, registry, "perf", "Perf")
        pipe._perception.process = lambda p: perception_factory([
            (0.8, EmotionLabel.HAPPY, 0.9), (0.3, EmotionLabel.NEUTRAL, 0.2),
            (0.5, EmotionLabel.SAD, -0.3)])
        fp = FrameProcessor(config)
        frame = np.random.default_rng(0).integers(60, 200, (480, 640, 3), dtype=np.uint8)
        processed = fp.process(frame)

        start = time.time()
        for _ in range(30):
            pipe.analyze(processed)
        avg_ms = (time.time() - start) / 30 * 1000.0
        # The non-CV scoring path must be fast; generous ceiling for CI variance.
        assert avg_ms < 80.0

    def test_frame_processing_speed(self, config):
        fp = FrameProcessor(config)
        frame = np.random.default_rng(0).integers(60, 200, (480, 640, 3), dtype=np.uint8)
        start = time.time()
        for _ in range(30):
            fp.process(frame)
        avg_ms = (time.time() - start) / 30 * 1000.0
        assert avg_ms < 80.0
