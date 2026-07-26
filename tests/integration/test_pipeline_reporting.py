"""Integration tests: analysis pipeline, session manager, reporting."""

from __future__ import annotations

import os

import numpy as np

from backend.contracts.models import EmotionLabel
from backend.ai_models.model_registry import ModelRegistry
from backend.pipeline.analysis_pipeline import AnalysisPipeline
from backend.session.session_manager import SessionManager
from backend.reporting.report_engine import ReportEngine
from backend.reporting.export_engine import ExportEngine
from core.exceptions import ExportError
import pytest


class TestAnalysisPipeline:
    def test_full_frame_result(self, config, perception_factory, rgb_frame):
        from backend.camera.frame_processor import FrameProcessor
        registry = ModelRegistry(config)
        pipe = AnalysisPipeline(config, registry, "s", "Test")
        pipe._perception.process = lambda processed: perception_factory([
            (0.9, EmotionLabel.HAPPY, 0.9), (0.1, EmotionLabel.SAD, -0.5)])
        processed = FrameProcessor(config).process(rgb_frame)
        result = pipe.analyze(processed)
        assert len(result.students) == 2
        assert 0 <= result.classroom_engagement <= 100
        assert result.faces_present == 2
        assert all(s.remark for s in result.students)


class TestSessionManager:
    def test_lifecycle_and_persist(self, config, perception_factory, rgb_frame, tmp_path):
        sm = SessionManager(config)
        sm._pipeline._perception.process = lambda p: perception_factory([(0.8, EmotionLabel.HAPPY, 0.9)])
        sm.start("Test Session")
        assert sm.is_running
        for _ in range(8):
            sm.process_frame(rgb_frame)
        sm.pause(); assert not sm.is_running
        sm.resume(); assert sm.is_running
        payload = sm.stop()
        assert payload["saved"] is True
        assert os.path.exists(payload["path"])


class TestReporting:
    def _session_with_data(self, config, perception_factory, rgb_frame):
        sm = SessionManager(config)
        sm._pipeline._perception.process = lambda p: perception_factory([
            (0.8, EmotionLabel.HAPPY, 0.9), (0.2, EmotionLabel.SAD, -0.4)])
        sm.start("Report Test")
        for _ in range(15):
            sm.process_frame(rgb_frame)
        sm.stop()
        return sm

    def test_pdf_excel_csv(self, config, perception_factory, rgb_frame):
        sm = self._session_with_data(config, perception_factory, rgb_frame)
        data = ReportEngine(config).build(sm.pipeline.classroom,
                                          sm.pipeline.student_summaries(),
                                          sm.pipeline.teacher_insights())
        ee = ExportEngine(config)
        for fmt in ("pdf", "excel", "csv"):
            path = ee.export(data, fmt)
            assert os.path.exists(path)
            assert os.path.getsize(path) > 0

    def test_empty_export_blocked(self, config):
        from backend.reporting.report_engine import ReportData
        from backend.contracts.models import SessionSummary, TrendDirection
        empty = ReportData(SessionSummary("x", "Empty", 0, 0, 0, 0, 0, 0, TrendDirection.INSUFFICIENT),
                           [], {}, [], [], [], "")
        with pytest.raises(ExportError):
            ExportEngine(config).export(empty, "pdf")


class TestDemoMode:
    def test_demo_populates_everything(self, config):
        """Demo Mode runs with no camera and no AI models, filling every screen."""
        from frontend.callbacks.handlers import DashboardController
        ctrl = DashboardController(config)
        annotated, kpis, students, status, msg = ctrl.run_demo(frames=30)
        assert annotated is not None and annotated.shape[2] == 3
        assert "es-gauge" in kpis                 # gauge rendered
        assert students.count("es-stu") == 5      # five student cards
        summary = ctrl._session.pipeline.session_summary()
        assert summary.frames_recorded == 30
        assert len(ctrl._session.pipeline.student_summaries()) == 5
        # Reports work from demo data.
        path, _ = ctrl.generate_report("csv")
        assert path is not None
