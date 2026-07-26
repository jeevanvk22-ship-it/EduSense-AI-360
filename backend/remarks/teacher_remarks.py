"""
EduSense AI 360 - Teacher Remarks Rules
=======================================

Turns classroom insights into professional, constructive teaching suggestions
(AI Decision Logic Part 6 §8, §9). Never personal, never ranking, never blame -
impersonal guidance tied to the observed classroom pattern.

This module composes on top of :class:`TeacherInsights` (already constructive) and
de-duplicates/prioritises the suggestions into a clean, ordered list.
"""

from __future__ import annotations

from backend.analytics.teacher_analytics import TeacherInsights


def build(insights: TeacherInsights) -> list[str]:
    """Return an ordered, de-duplicated list of constructive teaching suggestions."""
    suggestions: list[str] = []
    seen: set[str] = set()

    # Insight-derived suggestions first (most specific to this session).
    for s in insights.suggestions:
        if s not in seen:
            suggestions.append(s)
            seen.add(s)

    # A baseline of always-constructive options if the session offered few specifics.
    baseline = [
        "Increase opportunities for interaction.",
        "Use more examples to illustrate key points.",
        "Introduce visual explanations where helpful.",
        "Add a short classroom activity to vary the pace.",
        "Increase questioning frequency to invite participation.",
    ]
    for s in baseline:
        if len(suggestions) >= 5:
            break
        if s not in seen:
            suggestions.append(s)
            seen.add(s)

    return suggestions[:5]
