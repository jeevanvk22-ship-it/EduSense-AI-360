"""
EduSense AI 360 - Health Monitor
================================

Tracks the health of each subsystem (camera, AI models, pipeline, reporting, …) so
the application can make degraded-mode decisions and surface honest status to the
user (Architecture Part 3 §1.9, §20). Modules report their state here; the dashboard
and error handling read the aggregate.

This is a lightweight in-memory registry — no persistence — refreshed continuously
as the application runs.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from enum import Enum

from core.logger import get_logger

log = get_logger("application")


class HealthStatus(str, Enum):
    HEALTHY = "Healthy"
    DEGRADED = "Degraded"
    DOWN = "Down"
    UNKNOWN = "Unknown"


# Ranking for aggregation: the worst component status wins.
_SEVERITY = {
    HealthStatus.HEALTHY: 0,
    HealthStatus.UNKNOWN: 1,
    HealthStatus.DEGRADED: 2,
    HealthStatus.DOWN: 3,
}


@dataclass
class ComponentHealth:
    """Health record for a single subsystem."""
    name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    detail: str = ""
    updated_at: float = field(default_factory=time.time)


class HealthMonitor:
    """Registry of component health with an aggregate view."""

    def __init__(self) -> None:
        self._components: dict[str, ComponentHealth] = {}
        self._lock = threading.Lock()

    def report(self, component: str, status: HealthStatus, detail: str = "") -> None:
        """Record (or update) the health of a component."""
        with self._lock:
            previous = self._components.get(component)
            self._components[component] = ComponentHealth(
                name=component, status=status, detail=detail, updated_at=time.time()
            )
        if previous is None or previous.status != status:
            level = "warning" if status in (HealthStatus.DEGRADED, HealthStatus.DOWN) else "info"
            getattr(log, level)("Health [%s] -> %s%s", component, status.value,
                                f" ({detail})" if detail else "")

    # -- typed helpers ------------------------------------------------------
    def healthy(self, component: str, detail: str = "") -> None:
        self.report(component, HealthStatus.HEALTHY, detail)

    def degraded(self, component: str, detail: str = "") -> None:
        self.report(component, HealthStatus.DEGRADED, detail)

    def down(self, component: str, detail: str = "") -> None:
        self.report(component, HealthStatus.DOWN, detail)

    # -- queries ------------------------------------------------------------
    def status_of(self, component: str) -> HealthStatus:
        with self._lock:
            record = self._components.get(component)
        return record.status if record else HealthStatus.UNKNOWN

    def overall(self) -> HealthStatus:
        """Aggregate health: the worst (most severe) component status."""
        with self._lock:
            statuses = [c.status for c in self._components.values()]
        if not statuses:
            return HealthStatus.UNKNOWN
        return max(statuses, key=lambda s: _SEVERITY[s])

    def is_degraded(self) -> bool:
        """True if any component is degraded or down."""
        return self.overall() in (HealthStatus.DEGRADED, HealthStatus.DOWN)

    def snapshot(self) -> dict[str, ComponentHealth]:
        """Return a copy of all current component health records."""
        with self._lock:
            return dict(self._components)
