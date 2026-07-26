"""
EduSense AI 360 - Data Contracts
================================

The typed objects that modules exchange. These contracts are the backbone of the
system's loose coupling (Architecture Part 3 §3): a module may be reimplemented
freely provided it continues to emit the same contract.

Everything here is a plain dataclass or enum with no behaviour beyond simple,
self-contained derivations (e.g. a bounding box knowing its own centre). Contracts
hold *data*, not logic; engines and managers own the logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------
class EmotionLabel(str, Enum):
    """Supported facial emotion categories (Confused is derived where required)."""
    HAPPY = "happy"
    NEUTRAL = "neutral"
    SAD = "sad"
    ANGRY = "angry"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    CONFUSED = "confused"


class EngagementLevel(str, Enum):
    """Engagement bands (Functional Requirements Part 1B §5)."""
    POOR = "Poor"
    AVERAGE = "Average"
    GOOD = "Good"
    EXCELLENT = "Excellent"


class GazeDirection(str, Enum):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


class RiskLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"


class CameraStatus(str, Enum):
    DISCONNECTED = "Disconnected"
    INITIALISING = "Initialising"
    STREAMING = "Streaming"
    RECONNECTING = "Reconnecting"
    ERROR = "Error"


class TrendDirection(str, Enum):
    RISING = "Rising"
    STABLE = "Stable"
    DECLINING = "Declining"
    INSUFFICIENT = "Insufficient data"


# ---------------------------------------------------------------------------
# Vision contracts
# ---------------------------------------------------------------------------
@dataclass
class FrameQuality:
    """Quality assessment of a single frame produced by frame processing.

    Consumed by the AI pipeline to scale confidence: poor frames lower confidence
    rather than being trusted blindly (AI Decision Logic Part 6 §2.5, §14).
    """
    ok: bool = True
    brightness: float = 0.0          # mean luma, 0-255
    is_low_light: bool = False
    is_overexposed: bool = False
    blur_score: float = 0.0          # higher = sharper
    is_blurry: bool = False
    quality_confidence: float = 1.0  # [0, 1] multiplier for downstream confidence
    reason: str = "ok"


@dataclass
class FaceBox:
    """A detected face in pixel coordinates, with a stable tracking id."""
    x: int
    y: int
    w: int
    h: int
    confidence: float
    face_id: int = -1

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.w // 2, self.y + self.h // 2)

    @property
    def area(self) -> int:
        return max(0, self.w) * max(0, self.h)

    def crop(self, frame: Any) -> Any:
        """Return the sub-image for this face, clamped to frame bounds."""
        h, w = frame.shape[:2]
        x1, y1 = max(0, self.x), max(0, self.y)
        x2, y2 = min(w, self.x + self.w), min(h, self.y + self.h)
        return frame[y1:y2, x1:x2]


@dataclass
class EyeSignals:
    """Per-face eye/attention signals from the eye-tracking module."""
    eyes_open: bool = False
    ear: float = 0.0
    blink: bool = False
    gaze_direction: GazeDirection = GazeDirection.CENTER
    gaze_on_target: bool = False
    gaze_offset: float = 1.0
    head_facing: bool = False
    yaw: float = 0.0
    pitch: float = 0.0
    sleeping: bool = False
    attention: float = 0.0          # blended [0, 1]
    confidence: float = 0.0         # [0, 1]


@dataclass
class EmotionResult:
    """Per-face emotion classification and its engagement contribution."""
    dominant: EmotionLabel = EmotionLabel.NEUTRAL
    scores: dict[str, float] = field(default_factory=lambda: {EmotionLabel.NEUTRAL.value: 1.0})
    confidence: float = 0.0
    engagement_contribution: float = 0.0    # [-1, 1]
    available: bool = True


# ---------------------------------------------------------------------------
# Analytics contracts
# ---------------------------------------------------------------------------
@dataclass
class EngagementResult:
    """Per-student engagement outcome for a single frame."""
    score: float = 0.0                       # 0-100
    level: EngagementLevel = EngagementLevel.POOR
    attention: float = 0.0                   # 0-1 sub-signal
    emotion_score: float = 0.0               # 0-1 sub-signal
    presence: float = 0.0                    # 0-1 sub-signal
    confidence: float = 0.0                  # 0-1
    risk_level: RiskLevel = RiskLevel.LOW
    distracted: bool = True
    prolonged_inattention: bool = False
    distracted_seconds: float = 0.0
    dominant_emotion: EmotionLabel = EmotionLabel.NEUTRAL


@dataclass
class StudentResult:
    """Everything known about one student in one frame."""
    student_id: int
    box: FaceBox
    engagement: EngagementResult
    eye: Optional[EyeSignals] = None
    emotion: Optional[EmotionResult] = None
    remark: str = ""


@dataclass
class FrameResult:
    """Aggregate outcome of analysing a single frame."""
    students: list[StudentResult] = field(default_factory=list)
    classroom_engagement: float = 0.0
    faces_present: int = 0
    distracted_count: int = 0
    dominant_emotion: EmotionLabel = EmotionLabel.NEUTRAL
    annotated_frame: Any = None


@dataclass
class FrameRecord:
    """A timestamped snapshot of classroom metrics for the session time-series."""
    t: float                                 # seconds since session start
    timestamp: str                           # ISO local time
    classroom_engagement: float              # smoothed
    raw_engagement: float                    # unsmoothed
    faces_present: int
    distracted_count: int
    dominant_emotion: str


@dataclass
class SessionSummary:
    """Aggregate statistics for a completed (or in-progress) session."""
    session_id: str
    session_name: str
    duration_seconds: float
    frames_recorded: int
    average_engagement: float
    peak_engagement: float
    lowest_engagement: float
    average_attendance: float
    attention_trend: TrendDirection

    def as_dict(self) -> dict[str, Any]:
        """Plain-dict view for persistence and reporting."""
        return {
            "session_id": self.session_id,
            "session_name": self.session_name,
            "duration_seconds": self.duration_seconds,
            "frames_recorded": self.frames_recorded,
            "average_engagement": self.average_engagement,
            "peak_engagement": self.peak_engagement,
            "lowest_engagement": self.lowest_engagement,
            "average_attendance": self.average_attendance,
            "attention_trend": self.attention_trend.value,
        }
