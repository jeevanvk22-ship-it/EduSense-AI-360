"""Unit tests: attention, engagement, emotion, eye temporal, face tracking."""

from __future__ import annotations

import numpy as np

from backend.contracts.models import EmotionLabel, EngagementLevel, RiskLevel, FaceBox, GazeDirection
from backend.analytics.attention_engine import AttentionEngine, AttentionLevel
from backend.analytics.engagement_engine import EngagementEngine
from backend.ai_models.face_detection import FaceTracker, FaceDetector, _RawDetection
from backend.ai_models.eye_tracking import EyeTracker, _Instant
from backend.ai_models.emotion_detection import EmotionDetector

T0 = 1000.0


class TestEngagementEngine:
    def test_excellent(self, config, make_eye, make_emotion):
        ee = EngagementEngine(config)
        r = ee.score_face(0, make_eye(0.95), make_emotion(EmotionLabel.HAPPY, 0.9),
                          present=True, attention_override=0.95)
        assert r.score >= 81
        assert r.level == EngagementLevel.EXCELLENT
        assert r.risk_level == RiskLevel.LOW

    def test_distraction_and_prolonged(self, config, make_eye, make_emotion):
        ee = EngagementEngine(config)
        low = ee.score_face(1, make_eye(0.0), make_emotion(EmotionLabel.ANGRY, -0.6),
                            present=True, attention_override=0.0, now=T0)
        assert low.distracted is True
        assert low.prolonged_inattention is False
        later = ee.score_face(1, make_eye(0.0), make_emotion(EmotionLabel.ANGRY, -0.6),
                              present=True, attention_override=0.0, now=T0 + 11)
        assert later.prolonged_inattention is True
        assert later.risk_level == RiskLevel.HIGH

    def test_classroom_average(self, config, make_eye, make_emotion):
        ee = EngagementEngine(config)
        a = ee.score_face(0, make_eye(0.9), make_emotion(EmotionLabel.HAPPY, 0.9), attention_override=0.9)
        b = ee.score_face(1, make_eye(0.1), make_emotion(EmotionLabel.SAD, -0.5), attention_override=0.1)
        avg = EngagementEngine.classroom_average([a, b])
        assert 0 <= avg <= 100


class TestAttentionEngine:
    def test_levels(self, config, make_eye):
        ae = AttentionEngine(config)
        assert ae.update(0, make_eye(0.9), present=True, now=T0).level == AttentionLevel.HIGH
        assert ae.update(1, make_eye(0.1), present=True, now=T0).level == AttentionLevel.LOW
        assert ae.update(2, None, present=False, now=T0).level == AttentionLevel.UNKNOWN

    def test_time_accumulation(self, config, make_eye):
        ae = AttentionEngine(config)
        ae.update(0, make_eye(0.9), present=True, now=T0)
        r = ae.update(0, make_eye(0.9), present=True, now=T0 + 2)
        assert r.attentive_seconds >= 2.0
        assert r.focus_streak == 2


class TestFaceTracking:
    def test_stable_ids(self):
        tr = FaceTracker(max_lost_frames=3, match_distance=50)
        ids1 = [b.face_id for b in tr.update([FaceBox(100, 100, 40, 40, 0.9),
                                              FaceBox(300, 100, 40, 40, 0.8)])]
        ids2 = [b.face_id for b in tr.update([FaceBox(104, 101, 40, 40, 0.9),
                                              FaceBox(297, 99, 40, 40, 0.8)])]
        assert ids1 == ids2

    def test_detector_filters_and_tracks(self, config):
        fd = FaceDetector(config)
        fd._available = True
        fd._detector = object()
        fd._run_detection = lambda frame: [
            _RawDetection(10, 10, 50, 50, 0.95),
            _RawDetection(0, 0, 30, 30, 0.40),  # below threshold
        ]
        boxes = fd.detect(np.zeros((480, 640, 3), np.uint8))
        assert len(boxes) == 1
        assert boxes[0].face_id == 0


class TestEyeTemporal:
    def _inst(self, open_, gaze=0.1, yaw=5, pitch=5):
        return _Instant(ear=0.25 if open_ else 0.10, gaze_offset=gaze,
                        gaze_direction=GazeDirection.CENTER, yaw=yaw, pitch=pitch,
                        eyes_open=open_, gaze_on_target=gaze <= 0.22,
                        head_facing=abs(yaw) <= 30 and abs(pitch) <= 25, landmarks_ok=True)

    def test_blink(self, config):
        et = EyeTracker(config)
        et._apply_temporal(1, self._inst(True), 1.0, now=T0)
        et._apply_temporal(1, self._inst(False), 1.0, now=T0 + 0.1)
        sig = et._apply_temporal(1, self._inst(True), 1.0, now=T0 + 0.2)
        assert sig.blink is True

    def test_sleep(self, config):
        et = EyeTracker(config)
        et._apply_temporal(2, self._inst(False), 1.0, now=T0)
        sig = et._apply_temporal(2, self._inst(False), 1.0, now=T0 + 4.0)
        assert sig.sleeping is True
        assert sig.eyes_open is False

    def test_quality_lowers_confidence(self, config):
        et = EyeTracker(config)
        full = et._apply_temporal(3, self._inst(True), 1.0, now=T0).confidence
        poor = et._apply_temporal(4, self._inst(True), 0.3, now=T0).confidence
        assert poor < full


class TestEmotion:
    def test_smoothing_and_mapping(self, config):
        ed = EmotionDetector(config)
        ed._available = True
        ed._engine = object()
        ed._predict = lambda crop: {"happy": 0.7, "neutral": 0.2, "sad": 0.1}
        r = ed.analyze(np.zeros((48, 48, 3), np.uint8), face_id=0)
        assert r.dominant == EmotionLabel.HAPPY
        assert r.engagement_contribution > 0

    def test_low_confidence_floors_to_neutral(self, config):
        ed = EmotionDetector(config)
        ed._available = True
        ed._engine = object()
        ed._predict = lambda crop: {"happy": 0.25, "neutral": 0.2, "sad": 0.2, "fear": 0.2, "angry": 0.15}
        r = ed.analyze(np.zeros((48, 48, 3), np.uint8), face_id=9)
        assert r.dominant == EmotionLabel.NEUTRAL
