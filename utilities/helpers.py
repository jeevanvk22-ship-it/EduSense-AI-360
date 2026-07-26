"""
EduSense AI 360 - Shared Utilities
==================================

Domain-agnostic helpers reused across the system: numeric maths, temporal
smoothing, validation primitives, time/format helpers, and safe file IO. This
module depends on nothing domain-specific and may be imported by any layer.
"""

from __future__ import annotations

import json
import math
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional


# ---------------------------------------------------------------------------
# Numeric maths
# ---------------------------------------------------------------------------
def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Constrain ``value`` to the inclusive ``[low, high]`` range."""
    return max(low, min(high, value))


def normalize(value: float, low: float, high: float) -> float:
    """Map ``value`` from ``[low, high]`` to ``[0, 1]`` (clamped)."""
    if high == low:
        return 0.0
    return clamp((value - low) / (high - low), 0.0, 1.0)


def euclidean(p1: Iterable[float], p2: Iterable[float]) -> float:
    """Euclidean distance between two points of equal dimensionality."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def weighted_blend(values: dict[str, float], weights: dict[str, float]) -> float:
    """Weighted sum of ``values`` by matching ``weights`` keys.

    Only keys present in both dicts contribute. Returns 0.0 if no overlap.
    """
    total = 0.0
    for key, weight in weights.items():
        if key in values:
            total += float(weight) * float(values[key])
    return total


def safe_mean(values: Iterable[float], default: float = 0.0) -> float:
    """Arithmetic mean that returns ``default`` for an empty iterable."""
    seq = list(values)
    return sum(seq) / len(seq) if seq else default


# ---------------------------------------------------------------------------
# Temporal smoothing
# ---------------------------------------------------------------------------
class MovingAverage:
    """Fixed-window moving average for smoothing live signals."""

    def __init__(self, window: int = 15) -> None:
        self.window = max(1, int(window))
        self._buf: "deque[float]" = deque(maxlen=self.window)

    def update(self, value: float) -> float:
        self._buf.append(float(value))
        return self.value

    @property
    def value(self) -> float:
        return sum(self._buf) / len(self._buf) if self._buf else 0.0

    def __len__(self) -> int:
        return len(self._buf)

    def reset(self) -> None:
        self._buf.clear()


# ---------------------------------------------------------------------------
# Validation primitives
# ---------------------------------------------------------------------------
def in_range(value: float, low: float, high: float) -> bool:
    """True if ``low <= value <= high``."""
    return low <= value <= high


def coerce_int(value: Any, default: int = 0) -> int:
    """Coerce to int, returning ``default`` on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def coerce_float(value: Any, default: float = 0.0) -> float:
    """Coerce to float, returning ``default`` on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Time & formatting
# ---------------------------------------------------------------------------
def now_iso() -> str:
    """Current local time as an ISO-8601 string (seconds precision)."""
    return datetime.now().isoformat(timespec="seconds")


def timestamp_slug() -> str:
    """Filesystem-safe timestamp for file names, e.g. ``20260627-084512``."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def format_duration(seconds: float) -> str:
    """Human-readable duration, e.g. ``1h 02m 05s`` or ``02m 05s``."""
    seconds = int(max(0, seconds))
    hours, rem = divmod(seconds, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    return f"{minutes:02d}m {secs:02d}s"


# ---------------------------------------------------------------------------
# Safe file IO
# ---------------------------------------------------------------------------
def ensure_dir(path: Path) -> Path:
    """Create a directory (and parents) if needed; return it."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_json_write(path: Path, data: Any, *, indent: int = 2) -> bool:
    """Write JSON atomically (via a temp file + replace). Returns success."""
    path = Path(path)
    try:
        ensure_dir(path.parent)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=indent, default=str)
        tmp.replace(path)
        return True
    except OSError:
        return False


def safe_json_read(path: Path, default: Optional[Any] = None) -> Any:
    """Read JSON, returning ``default`` if missing or malformed."""
    path = Path(path)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default
