"""
EduSense AI 360 - Frame Buffer
==============================

A thread-safe, latest-wins buffer that decouples the camera capture thread from
the analysis consumer (Architecture Part 3 §5.2). The capture thread *puts* frames
as fast as the device delivers them; the analysis side *gets the latest* at its own
sustainable rate. When the consumer is slower than capture, older frames are simply
dropped (counted), which bounds latency and prevents backlog growth.

This module is pure Python (no OpenCV/NumPy import) so it is fully unit-testable
without the computer-vision stack.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class BufferedFrame:
    """A captured frame with its sequence number and capture timestamp."""
    frame: Any
    sequence: int
    timestamp: float


class FrameBuffer:
    """Single-slot, latest-wins frame buffer with drop accounting."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._latest: Optional[BufferedFrame] = None
        self._sequence: int = 0
        self._dropped: int = 0
        self._consumed_sequence: int = 0

    def put(self, frame: Any) -> int:
        """Store a frame as the new latest, returning its sequence number.

        If a previous, never-consumed frame is overwritten, the drop counter is
        incremented (latest-wins).
        """
        with self._condition:
            if self._latest is not None and self._latest.sequence > self._consumed_sequence:
                self._dropped += 1
            self._sequence += 1
            self._latest = BufferedFrame(frame=frame, sequence=self._sequence, timestamp=time.time())
            self._condition.notify_all()
            return self._sequence

    def get_latest(self) -> Optional[BufferedFrame]:
        """Return the most recent BufferedFrame (marking it consumed), or None."""
        with self._lock:
            if self._latest is None:
                return None
            self._consumed_sequence = self._latest.sequence
            return self._latest

    def get_latest_frame(self) -> Optional[Any]:
        """Convenience: return just the latest frame image, or None."""
        buffered = self.get_latest()
        return buffered.frame if buffered is not None else None

    def wait_for_frame(self, timeout: float = 1.0) -> Optional[BufferedFrame]:
        """Block until a frame newer than the last consumed one is available.

        Returns the new frame, or None if the timeout elapses first.
        """
        deadline = time.time() + timeout
        with self._condition:
            while True:
                if self._latest is not None and self._latest.sequence > self._consumed_sequence:
                    self._consumed_sequence = self._latest.sequence
                    return self._latest
                remaining = deadline - time.time()
                if remaining <= 0:
                    return None
                self._condition.wait(timeout=remaining)

    def clear(self) -> None:
        """Discard the buffered frame (e.g. on camera stop)."""
        with self._lock:
            self._latest = None

    @property
    def dropped(self) -> int:
        """Number of frames overwritten before being consumed."""
        with self._lock:
            return self._dropped

    @property
    def sequence(self) -> int:
        """Total number of frames put into the buffer."""
        with self._lock:
            return self._sequence

    def reset_stats(self) -> None:
        with self._lock:
            self._dropped = 0
