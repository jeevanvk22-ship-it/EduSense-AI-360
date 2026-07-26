"""System test: the dashboard controller drives a full session lifecycle."""

from __future__ import annotations

import numpy as np

from backend.contracts.models import EmotionLabel
from frontend.callbacks.handlers import DashboardController


class TestEndToEnd:
    def test_controller_full_flow(self, config, perception_factory, rgb_frame):
        ctrl = DashboardController(config)
        ctrl._session._pipeline._perception.process = lambda p: perception_factory([
            (0.85, EmotionLabel.HAPPY, 0.9), (0.15, EmotionLabel.SAD, -0.4)])

        assert "running" in ctrl.start_session("E2E").lower()
        annotated, kpis, students, status = ctrl.process_frame(rgb_frame)
        assert "Engagement" in kpis
        assert "Student 1" in students

        for _ in range(12):
            ctrl.process_frame(rgb_frame)

        # Analytics + insights are available mid/post session.
        assert "average" in ctrl.analytics_summary().lower()
        assert "Student 1" in ctrl.student_insights_html()
        assert "observations" in ctrl.teacher_insights_html().lower()

        # Settings validation behaviour through the controller.
        assert "saved" in ctrl.update_settings({"camera.fps": 25}).lower()
        assert "maximum" in ctrl.update_settings({"camera.fps": 999}).lower()

        # Report generation end to end.
        ctrl.stop_session()
        assert "Session Report" in ctrl.report_preview()
        path, msg = ctrl.generate_report("csv")
        assert path is not None and "ready" in msg.lower()
