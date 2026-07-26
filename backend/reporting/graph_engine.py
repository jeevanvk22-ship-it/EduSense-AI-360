"""
EduSense AI 360 - Graph Engine
==============================

Builds the live and session visualisations (Functional Requirements Part 1B §11;
UI/UX Part 2 §11) from the classroom time-series. A single engine produces figures
consumed by both the dashboard and the report layer, so charting logic is not
duplicated.

Plotly is imported lazily so this module is importable without it; figures follow
the Part 2 palette and dark template. Empty/sparse data renders a calm placeholder
rather than failing.
"""

from __future__ import annotations

from typing import Any, Optional

from backend.analytics.student_analytics import ClassroomAnalytics
from core.logger import get_logger

log = get_logger("application")

# Part 2 palette
BRAND = "#6366F1"
CYAN = "#22D3EE"
GREEN = "#34D399"
DANGER = "#F87171"
GRID = "rgba(255,255,255,0.06)"
AXIS = "#6B7693"
PAPER = "rgba(0,0,0,0)"

EMOTION_COLORS = {
    "happy": "#FBBF24", "neutral": "#94A3B8", "sad": "#60A5FA",
    "angry": "#F87171", "fear": "#A78BFA", "surprise": "#22D3EE",
    "disgust": "#FB923C", "confused": "#FB923C",
}


class GraphEngine:
    """Produces Plotly figures from classroom analytics."""

    def __init__(self) -> None:
        self._available: Optional[bool] = None

    def _go(self):
        import plotly.graph_objects as go
        return go

    def _base_layout(self, go, title: str, **kwargs) -> Any:
        layout = dict(
            title=dict(text=title, font=dict(color="#F8FAFC", size=16)),
            template="plotly_dark",
            paper_bgcolor=PAPER, plot_bgcolor=PAPER,
            font=dict(family="Inter, sans-serif", color="#A8B2C7", size=12),
            margin=dict(l=50, r=30, t=50, b=40),
            xaxis=dict(gridcolor=GRID, zeroline=False, color=AXIS),
            yaxis=dict(gridcolor=GRID, zeroline=False, color=AXIS),
            legend=dict(orientation="h", y=1.12, x=0),
            height=380,
        )
        layout.update(kwargs)
        return go.Layout(**layout)

    def _placeholder(self, title: str) -> Any:
        try:
            go = self._go()
        except Exception:  # noqa: BLE001
            return None
        fig = go.Figure(layout=self._base_layout(go, title))
        fig.add_annotation(text="Run a session to see analytics",
                           showarrow=False, font=dict(color=AXIS, size=14))
        return fig

    # -- charts -------------------------------------------------------------
    def engagement_timeline(self, classroom: ClassroomAnalytics) -> Any:
        if not classroom.frames:
            return self._placeholder("Classroom Engagement Over Time")
        go = self._go()
        ts = classroom.timeseries()
        fig = go.Figure(layout=self._base_layout(
            go, "Classroom Engagement Over Time",
            yaxis=dict(title="Engagement (0-100)", range=[0, 100], gridcolor=GRID, color=AXIS),
            yaxis2=dict(title="Distracted", overlaying="y", side="right", showgrid=False, color=AXIS),
        ))
        fig.add_trace(go.Scatter(
            x=ts["t"], y=ts["engagement"], mode="lines", name="Engagement",
            line=dict(color=BRAND, width=2), fill="tozeroy",
            fillcolor="rgba(99,102,241,0.12)"))
        fig.add_trace(go.Scatter(
            x=ts["t"], y=ts["distracted"], mode="lines", name="Distracted",
            line=dict(color=DANGER, width=1, dash="dot"), yaxis="y2"))
        return fig

    def participation_timeline(self, classroom: ClassroomAnalytics) -> Any:
        if not classroom.frames:
            return self._placeholder("Participation Over Time")
        go = self._go()
        ts = classroom.timeseries()
        fig = go.Figure(layout=self._base_layout(
            go, "Participation Over Time",
            yaxis=dict(title="Students in frame", rangemode="tozero", gridcolor=GRID, color=AXIS)))
        fig.add_trace(go.Scatter(
            x=ts["t"], y=ts["faces"], mode="lines", name="Students",
            line=dict(color=CYAN, width=2)))
        return fig

    def emotion_distribution(self, classroom: ClassroomAnalytics) -> Any:
        if not classroom.frames:
            return self._placeholder("Emotion Distribution")
        go = self._go()
        counts: dict[str, int] = {}
        for f in classroom.frames:
            counts[f.dominant_emotion] = counts.get(f.dominant_emotion, 0) + 1
        labels = list(counts.keys())
        values = list(counts.values())
        colors = [EMOTION_COLORS.get(l, "#94A3B8") for l in labels]
        fig = go.Figure(layout=self._base_layout(go, "Emotion Distribution"))
        fig.add_trace(go.Pie(
            labels=[l.title() for l in labels], values=values, hole=0.55,
            marker=dict(colors=colors), textinfo="percent"))
        return fig

    def student_engagement_bars(self, summaries: list) -> Any:
        if not summaries:
            return self._placeholder("Per-Student Engagement")
        go = self._go()
        ids = [f"Student {s.student_id + 1}" for s in summaries]
        avgs = [s.average_engagement for s in summaries]
        colors = [GREEN if a >= 61 else (BRAND if a >= 31 else DANGER) for a in avgs]
        fig = go.Figure(layout=self._base_layout(
            go, "Per-Student Average Engagement",
            yaxis=dict(title="Engagement (0-100)", range=[0, 100], gridcolor=GRID, color=AXIS)))
        fig.add_trace(go.Bar(x=ids, y=avgs, marker=dict(color=colors)))
        return fig
