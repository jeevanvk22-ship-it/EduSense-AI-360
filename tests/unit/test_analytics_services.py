"""Unit tests: analytics, remarks, services, and frame processing."""

from __future__ import annotations

import numpy as np

from backend.contracts.models import EngagementResult, EngagementLevel, EmotionLabel
from backend.analytics.student_analytics import StudentAnalytics, ClassroomAnalytics
from backend.analytics.teacher_analytics import TeacherAnalytics
from backend.analytics.engagement_engine import EngagementEngine
from backend.remarks.remarks_engine import RemarksEngine
from backend.camera.frame_buffer import FrameBuffer
from backend.camera.frame_processor import FrameProcessor
from backend.services.notification_manager import NotificationManager, NotificationType
from backend.services.health_monitor import HealthMonitor, HealthStatus
from backend.services.performance_monitor import PerformanceMonitor

T0 = 1000.0


class TestStudentAnalytics:
    def test_rising_trend_and_pattern(self, config):
        sa = StudentAnalytics(config)
        for i in range(12):
            sa.record(7, EngagementResult(score=30.0 + i * 5, level=EngagementLevel.AVERAGE,
                                          dominant_emotion=EmotionLabel.NEUTRAL))
        summ = sa.summary(7)
        assert summ.trend.value == "Rising"
        assert summ.frames == 12
        assert summ.peak_engagement >= summ.average_engagement


class TestClassroomAnalytics:
    def test_declining_and_summary(self, config):
        ca = ClassroomAnalytics(config, "s1", "Class")
        for i in range(30):
            ca.record(max(10, 85 - i * 2), faces_present=3, distracted_count=i // 10, now=T0 + i)
        s = ca.summary()
        assert s.attention_trend.value == "Declining"
        assert s.frames_recorded == 30
        assert s.peak_engagement >= s.lowest_engagement


class TestTeacherAnalytics:
    def test_constructive_and_non_judgmental(self, config):
        ca = ClassroomAnalytics(config, "s1", "Class")
        for i in range(30):
            ca.record(max(10, 80 - i * 2), faces_present=3, distracted_count=0, now=T0 + i)
        ins = TeacherAnalytics(config).analyse(ca)
        assert ins.observations
        text = " ".join(ins.observations).lower()
        assert "you " not in text and "teacher" not in text


class TestRemarks:
    def test_priority_alert_over_positive(self, config, make_eye, make_emotion):
        ee = EngagementEngine(config)
        re_ = RemarksEngine(config)
        ee.score_face(5, make_eye(0.0), make_emotion(EmotionLabel.SAD, -0.5), attention_override=0.0, now=T0)
        prolonged = ee.score_face(5, make_eye(0.0), make_emotion(EmotionLabel.SAD, -0.5),
                                  attention_override=0.0, now=T0 + 12)
        remark = re_.student_remark(prolonged)
        assert "disengaged" in remark.lower() or "check" in remark.lower()

    def test_excellent_positive(self, config, make_eye, make_emotion):
        ee = EngagementEngine(config)
        re_ = RemarksEngine(config)
        exc = ee.score_face(0, make_eye(0.95), make_emotion(EmotionLabel.HAPPY, 0.9), attention_override=0.95)
        assert "focused" in re_.student_remark(exc).lower()


class TestFrameBuffer:
    def test_latest_wins(self):
        buf = FrameBuffer()
        for i in range(5):
            buf.put(np.full((2, 2, 3), i, dtype=np.uint8))
        latest = buf.get_latest()
        assert latest.sequence == 5
        assert buf.dropped == 4


class TestFrameProcessor:
    def test_good_vs_dark(self, config):
        fp = FrameProcessor(config)
        good = np.random.default_rng(0).integers(60, 200, (120, 160, 3), dtype=np.uint8)
        dark = np.full((120, 160, 3), 10, dtype=np.uint8)
        assert fp.process(good).quality.ok is True
        assert fp.process(dark).quality.quality_confidence < 0.5
        assert fp.process(None) is None


class TestServices:
    def test_notifications(self):
        nm = NotificationManager()
        received = []
        nm.subscribe(lambda n: received.append(n.type))
        nm.success("ok")
        nm.error("bad")
        assert NotificationType.SUCCESS in received and NotificationType.ERROR in received

    def test_health_aggregation(self):
        hm = HealthMonitor()
        hm.healthy("a")
        assert hm.overall() == HealthStatus.HEALTHY
        hm.degraded("b")
        assert hm.is_degraded() is True

    def test_performance_budget(self, config):
        pm = PerformanceMonitor(config)
        for _ in range(10):
            pm.record_frame(processing_ms=30.0)
        snap = pm.snapshot()
        assert snap.frame_ms_ok is True
