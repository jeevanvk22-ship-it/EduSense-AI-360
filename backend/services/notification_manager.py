"""
EduSense AI 360 - Notification Manager
======================================

A small pub/sub service that raises user-facing notifications (Functional
Requirements Part 1B §16; AI Decision Logic Part 6 §10). Other modules call
:meth:`notify` (or a typed helper) and the presentation layer subscribes to render
toasts. Notifications are kept in a bounded history so a freshly-opened view can
show recent items.

Notifications are informative and non-alarming by design; this service only stores
and dispatches them — tone is the caller's responsibility, guided by Part 6 §10.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from core.error_handler import handle
from core.logger import get_logger

log = get_logger("application")


class NotificationType(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    LOADING = "loading"
    PROCESSING = "processing"


@dataclass
class Notification:
    """A single user-facing notification."""
    type: NotificationType
    title: str
    message: str = ""
    timestamp: float = field(default_factory=time.time)
    action: Optional[str] = None
    notification_id: int = 0


Subscriber = Callable[[Notification], None]


class NotificationManager:
    """Stores recent notifications and dispatches them to subscribers."""

    def __init__(self, history: int = 50) -> None:
        self._history: "deque[Notification]" = deque(maxlen=history)
        self._subscribers: list[Subscriber] = []
        self._lock = threading.Lock()
        self._counter = 0

    # -- subscription -------------------------------------------------------
    def subscribe(self, callback: Subscriber) -> None:
        """Register a callback invoked for every new notification."""
        with self._lock:
            if callback not in self._subscribers:
                self._subscribers.append(callback)

    def unsubscribe(self, callback: Subscriber) -> None:
        with self._lock:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

    # -- emit ---------------------------------------------------------------
    def notify(
        self,
        type: NotificationType,
        title: str,
        message: str = "",
        action: Optional[str] = None,
    ) -> Notification:
        """Create, store, and dispatch a notification."""
        with self._lock:
            self._counter += 1
            note = Notification(
                type=type, title=title, message=message, action=action,
                notification_id=self._counter,
            )
            self._history.append(note)
            subscribers = list(self._subscribers)

        log.debug("Notification [%s] %s", type.value, title)
        for sub in subscribers:
            try:
                sub(note)
            except Exception as exc:  # a bad subscriber must not break others
                handle(exc, context="notification subscriber", category="errors")
        return note

    # -- typed helpers ------------------------------------------------------
    def success(self, title: str, message: str = "", action: Optional[str] = None) -> Notification:
        return self.notify(NotificationType.SUCCESS, title, message, action)

    def warning(self, title: str, message: str = "", action: Optional[str] = None) -> Notification:
        return self.notify(NotificationType.WARNING, title, message, action)

    def error(self, title: str, message: str = "", action: Optional[str] = None) -> Notification:
        return self.notify(NotificationType.ERROR, title, message, action)

    def info(self, title: str, message: str = "", action: Optional[str] = None) -> Notification:
        return self.notify(NotificationType.INFO, title, message, action)

    def loading(self, title: str, message: str = "") -> Notification:
        return self.notify(NotificationType.LOADING, title, message)

    def processing(self, title: str, message: str = "") -> Notification:
        return self.notify(NotificationType.PROCESSING, title, message)

    # -- history ------------------------------------------------------------
    def recent(self, limit: int = 10) -> list[Notification]:
        """Return up to ``limit`` most-recent notifications (newest last)."""
        with self._lock:
            items = list(self._history)
        return items[-limit:]

    def clear(self) -> None:
        with self._lock:
            self._history.clear()
