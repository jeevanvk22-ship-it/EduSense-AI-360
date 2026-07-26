"""
EduSense AI 360 - Student Analytics
===================================

Two cohesive analytics accumulators (Functional Requirements Part 1B §6; AI Decision
Logic Part 6 §7):

* :class:`StudentAnalytics` - per-student session metrics: attentive/distracted time,
  emotion distribution, average/peak engagement, low-engagement periods, trend, and a
  descriptive behaviour pattern and performance summary.
* :class:`ClassroomAnalytics` - the classroom-level time-series recorder producing
  :class:`FrameRecord` snapshots and a :class:`SessionSummary`, consumed by Teacher
  Analytics and the reporting layer.

All trend/threshold parameters are configuration-driven.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from config.config_manager import ConfigManager
from backend.contracts.models import (
    EngagementResult, EmotionLabel, FrameRecord, SessionSummary, TrendDirection, EngagementLevel,
)
from backend.analytics.attention_engine import AttentionReading
from core.logger import get_logger
from utilities.helpers import MovingAverage, safe_mean, now_iso

log = get_logger("application")


# ---------------------------------------------------------------------------
# Per-student
# ---------------------------------------------------------------------------
@dataclass
class _StudentAccumulator:
    frames: int = 0
    engagement_sum: float = 0.0
    peak: float = 0.0
    lowest: float = 100.0
    first_scores: list[float] = field(default_factory=list)
    last_scores: list[float] = field(default_factory=list)
    emotion_counts: dict[str, int] = field(default_factory=dict)
    attentive_seconds: float = 0.0
    distracted_seconds: float = 0.0
    low_periods: int = 0
    _was_low: bool = False
    prolonged_events: int = 0
    _was_prolonged: bool = False


@dataclass
class StudentSummary:
    student_id: int
    frames: int
    average_engagement: float
    peak_engagement: float
    lowest_engagement: float
    performance: str
    attentive_seconds: float
    distracted_seconds: float
    attention_ratio: float
    emotion_distribution: dict[str, float]
    low_engagement_periods: int
    trend: TrendDirection
    behaviour_pattern: str
    remark_basis: str


class StudentAnalytics:
    """Accumulates and summarises per-student behaviour over a session."""

    def __init__(self, config: ConfigManager) -> None:
        self._trend_min = int(config.get("analytics.trend_min_frames", 6))
        self._trend_rise = float(config.get("analytics.trend_rising_delta", 8.0))
        self._trend_decline = float(config.get("analytics.trend_declining_delta", -8.0))
        self._low_threshold = float(config.get("analytics.low_engagement_threshold", 31))
        self._bands = sorted(
            [(int(b["min"]), str(b["label"])) for b in config.get("engagement.bands", [])],
            key=lambda x: x[0], reverse=True,
        ) or [(81, "Excellent"), (61, "Good"), (31, "Average"), (0, "Poor")]
        self._students: dict[int, _StudentAccumulator] = {}

    def reset(self) -> None:
        self._students.clear()

    def record(self, student_id: int, engagement: EngagementResult,
               attention: Optional[AttentionReading] = None) -> None:
        """Fold one frame's outcome for a student into the accumulators."""
        acc = self._students.setdefault(student_id, _StudentAccumulator())
        acc.frames += 1
        acc.engagement_sum += engagement.score
        acc.peak = max(acc.peak, engagement.score)
        acc.lowest = min(acc.lowest, engagement.score)

        if len(acc.first_scores) < self._trend_min:
            acc.first_scores.append(engagement.score)
        acc.last_scores.append(engagement.score)
        if len(acc.last_scores) > self._trend_min:
            acc.last_scores.pop(0)

        emo = engagement.dominant_emotion.value
        acc.emotion_counts[emo] = acc.emotion_counts.get(emo, 0) + 1

        if attention is not None:
            acc.attentive_seconds = attention.attentive_seconds
            acc.distracted_seconds = attention.distracted_seconds

        is_low = engagement.score < self._low_threshold
        if is_low and not acc._was_low:
            acc.low_periods += 1
        acc._was_low = is_low

        if engagement.prolonged_inattention and not acc._was_prolonged:
            acc.prolonged_events += 1
        acc._was_prolonged = engagement.prolonged_inattention

    # -- summary ------------------------------------------------------------
    def _performance(self, avg: float) -> str:
        for lower, label in self._bands:
            if avg >= lower:
                return label
        return self._bands[-1][1]

    def _trend(self, acc: _StudentAccumulator) -> TrendDirection:
        if acc.frames < self._trend_min * 2:
            return TrendDirection.INSUFFICIENT
        start = safe_mean(acc.first_scores)
        end = safe_mean(acc.last_scores)
        delta = end - start
        if delta >= self._trend_rise:
            return TrendDirection.RISING
        if delta <= self._trend_decline:
            return TrendDirection.DECLINING
        return TrendDirection.STABLE

    def _behaviour_pattern(self, acc: _StudentAccumulator, avg: float,
                           trend: TrendDirection) -> str:
        if acc.prolonged_events >= 1:
            return "Needs attention - extended disengagement observed."
        if avg >= 75 and acc.low_periods == 0:
            return "Consistent, highly-focused engagement."
        if trend == TrendDirection.RISING:
            return "Improving engagement over the session."
        if trend == TrendDirection.DECLINING:
            return "Engagement declined over the session."
        if acc.low_periods >= 3:
            return "Frequent short distractions with recovery."
        return "Steady, moderate engagement."

    def summary(self, student_id: int) -> Optional[StudentSummary]:
        acc = self._students.get(student_id)
        if acc is None or acc.frames == 0:
            return None
        avg = round(acc.engagement_sum / acc.frames, 1)
        total_emo = sum(acc.emotion_counts.values()) or 1
        distribution = {k: round(v / total_emo * 100, 1) for k, v in acc.emotion_counts.items()}
        total_time = acc.attentive_seconds + acc.distracted_seconds
        ratio = round(acc.attentive_seconds / total_time * 100, 1) if total_time else 0.0
        trend = self._trend(acc)
        return StudentSummary(
            student_id=student_id,
            frames=acc.frames,
            average_engagement=avg,
            peak_engagement=round(acc.peak, 1),
            lowest_engagement=round(acc.lowest, 1),
            performance=self._performance(avg),
            attentive_seconds=round(acc.attentive_seconds, 1),
            distracted_seconds=round(acc.distracted_seconds, 1),
            attention_ratio=ratio,
            emotion_distribution=distribution,
            low_engagement_periods=acc.low_periods,
            trend=trend,
            behaviour_pattern=self._behaviour_pattern(acc, avg, trend),
            remark_basis=f"avg {avg}, trend {trend.value}, low-periods {acc.low_periods}",
        )

    def all_summaries(self) -> list[StudentSummary]:
        return [s for sid in self._students if (s := self.summary(sid)) is not None]


# ---------------------------------------------------------------------------
# Classroom-level time-series
# ---------------------------------------------------------------------------
class ClassroomAnalytics:
    """Records classroom metrics over time and computes a session summary."""

    def __init__(self, config: ConfigManager, session_id: str = "", session_name: str = "") -> None:
        self._smoothing = int(config.get("engagement.smoothing_window", 15))
        self._trend_min = int(config.get("analytics.trend_min_frames", 6))
        self._trend_rise = float(config.get("analytics.trend_rising_delta", 8.0))
        self._trend_decline = float(config.get("analytics.trend_declining_delta", -8.0))
        self.session_id = session_id
        self.session_name = session_name or f"Session {datetime.now():%Y-%m-%d %H:%M}"
        self.started_at = time.time()
        self._closed_at: Optional[float] = None
        self._smoother = MovingAverage(self._smoothing)
        self.frames: list[FrameRecord] = []

    def reset(self, session_id: str = "", session_name: str = "") -> None:
        self.session_id = session_id or self.session_id
        self.session_name = session_name or self.session_name
        self.started_at = time.time()
        self._closed_at = None
        self._smoother.reset()
        self.frames.clear()

    def record(self, classroom_engagement: float, faces_present: int,
               distracted_count: int, dominant_emotion: str = "neutral",
               now: Optional[float] = None) -> FrameRecord:
        now = time.time() if now is None else now
        t = round(now - self.started_at, 2)
        smoothed = round(self._smoother.update(classroom_engagement), 1)
        rec = FrameRecord(
            t=t, timestamp=now_iso(), classroom_engagement=smoothed,
            raw_engagement=round(classroom_engagement, 1), faces_present=faces_present,
            distracted_count=distracted_count, dominant_emotion=dominant_emotion,
        )
        self.frames.append(rec)
        return rec

    # -- aggregates ---------------------------------------------------------
    @property
    def duration_seconds(self) -> float:
        end = self._closed_at or time.time()
        return round(end - self.started_at, 1)

    def average_engagement(self) -> float:
        return round(safe_mean([f.raw_engagement for f in self.frames]), 1)

    def peak_engagement(self) -> float:
        return round(max((f.raw_engagement for f in self.frames), default=0.0), 1)

    def lowest_engagement(self) -> float:
        return round(min((f.raw_engagement for f in self.frames), default=0.0), 1)

    def average_attendance(self) -> float:
        return round(safe_mean([f.faces_present for f in self.frames]), 1)

    def attention_trend(self) -> TrendDirection:
        if len(self.frames) < self._trend_min:
            return TrendDirection.INSUFFICIENT
        third = max(1, len(self.frames) // 3)
        start = safe_mean([f.raw_engagement for f in self.frames[:third]])
        end = safe_mean([f.raw_engagement for f in self.frames[-third:]])
        delta = end - start
        if delta >= self._trend_rise:
            return TrendDirection.RISING
        if delta <= self._trend_decline:
            return TrendDirection.DECLINING
        return TrendDirection.STABLE

    def timeseries(self) -> dict[str, list]:
        return {
            "t": [f.t for f in self.frames],
            "engagement": [f.classroom_engagement for f in self.frames],
            "faces": [f.faces_present for f in self.frames],
            "distracted": [f.distracted_count for f in self.frames],
        }

    def close(self) -> None:
        self._closed_at = time.time()

    def summary(self) -> SessionSummary:
        return SessionSummary(
            session_id=self.session_id,
            session_name=self.session_name,
            duration_seconds=self.duration_seconds,
            frames_recorded=len(self.frames),
            average_engagement=self.average_engagement(),
            peak_engagement=self.peak_engagement(),
            lowest_engagement=self.lowest_engagement(),
            average_attendance=self.average_attendance(),
            attention_trend=self.attention_trend(),
        )
