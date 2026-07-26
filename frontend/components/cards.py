"""
EduSense AI 360 - UI Components
===============================

HTML/SVG builders for the dashboard presentation layer. Every numeric value shown
here is read from existing backend contracts (StudentResult.eye/.emotion/.engagement/
.box with their confidence fields, SessionSummary, classroom analytics). Nothing is
invented; where the backend reports a value as unavailable the UI says so. Pure
functions, no Gradio import - trivially testable.
"""

from __future__ import annotations

from typing import Any, Optional

from backend.contracts.models import FrameResult

# ---------------------------------------------------------------------------
# Icons (single consistent line style)
# ---------------------------------------------------------------------------
_IC = {
    "eye": "<path d='M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z'/><circle cx='12' cy='12' r='3'/>",
    "users": "<circle cx='9' cy='7' r='3'/><path d='M2 21v-2a5 5 0 0 1 5-5h4a5 5 0 0 1 5 5v2'/>",
    "smile": "<circle cx='12' cy='12' r='9'/><path d='M8 14s1.5 2 4 2 4-2 4-2'/><circle cx='9' cy='9' r='1'/><circle cx='15' cy='9' r='1'/>",
    "bolt": "<path d='M13 2L3 14h7l-1 8 10-12h-7z'/>",
    "clock": "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/>",
    "board": "<path d='M22 10L12 5 2 10l10 5 10-5z'/><path d='M6 12v5c0 1 3 3 6 3s6-2 6-3v-5'/>",
    "check": "<path d='M20 6L9 17l-5-5'/>",
    "alert": "<path d='M12 9v4'/><path d='M12 17h.01'/><path d='M10.3 3.3 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.3a2 2 0 0 0-3.4 0z'/>",
    "info": "<circle cx='12' cy='12' r='9'/><path d='M12 16v-4'/><path d='M12 8h.01'/>",
    "bulb": "<path d='M9 18h6'/><path d='M10 22h4'/><path d='M12 2a7 7 0 0 0-4 12.7c.6.5 1 1.3 1 2.1h6c0-.8.4-1.6 1-2.1A7 7 0 0 0 12 2z'/>",
    "shield": "<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/>",
    "camera": "<rect x='2' y='6' width='20' height='14' rx='2'/><circle cx='12' cy='13' r='4'/><path d='M8 6l1.5-3h5L16 6'/>",
    "brain": "<path d='M12 5a3 3 0 0 0-5.9-.8A3 3 0 0 0 4 9a3 3 0 0 0 .5 5.5A2.5 2.5 0 0 0 9 18.5V5z'/><path d='M12 5a3 3 0 0 1 5.9-.8A3 3 0 0 1 20 9a3 3 0 0 1-.5 5.5A2.5 2.5 0 0 1 15 18.5V5z'/>",
    "chart": "<path d='M3 3v18h18'/><rect x='7' y='11' width='3' height='7'/><rect x='12' y='7' width='3' height='11'/><rect x='17' y='4' width='3' height='14'/>",
    "file": "<path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><path d='M14 2v6h6'/>",
    "trend": "<path d='M3 17l6-6 4 4 7-7'/><path d='M14 8h6v6'/>",
    "target": "<circle cx='12' cy='12' r='9'/><circle cx='12' cy='12' r='5'/><circle cx='12' cy='12' r='1'/>",
    "spark": "<path d='M12 2v6'/><path d='M12 22v-6'/><path d='M2 12h6'/><path d='M22 12h-6'/>",
}


def _icon(name: str, color: str = "currentColor", size: int = 16) -> str:
    return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' "
            f"stroke='{color}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'>"
            f"{_IC.get(name, '')}</svg>")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def _level_label(score: float) -> str:
    return ("Excellent" if score >= 81 else "Good" if score >= 61
            else "Average" if score >= 31 else "Poor")


def _status5(score: float) -> str:
    return ("Excellent" if score >= 80 else "Good" if score >= 60
            else "Average" if score >= 40 else "Low" if score >= 20 else "Very Low")


def _color(score: float) -> str:
    return ("#34D399" if score >= 60 else "#FBBF24" if score >= 40
            else "#FB923C" if score >= 20 else "#F87171")


def _classroom_status(score: float) -> str:
    return ("Class is highly engaged" if score >= 80 else "Class is attentive" if score >= 60
            else "Mixed engagement" if score >= 40 else "Engagement is low" if score >= 20
            else "Class appears disengaged")


_STATUS = {
    "Excellent": ("exc", "Excellent"), "Good": ("good", "Good"),
    "Average": ("mod", "Moderate"), "Poor": ("need", "Needs Attention"),
}


def _conf_badge(conf: Optional[float]) -> str:
    if conf is None:
        return "<span class='es-cbadge na'>Confidence unavailable</span>"
    return f"<span class='es-cbadge'>Confidence {conf * 100:.0f}%</span>"


def _dot(value: str) -> str:
    v = (value or "").lower()
    if any(k in v for k in ("excellent", "stable", "healthy", "strong", "good", "active", "connected", "live", "recording")):
        return "ok"
    if any(k in v for k in ("low", "error", "poor", "disconnect", "lost", "critical", "off")):
        return "bad"
    return "warn"


def _mean(vals) -> Optional[float]:
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def _sparkline(values: list, color: str = "#22D3EE", w: int = 116, h: int = 30) -> str:
    if not values or len(values) < 2:
        return f"<svg class='es-spark' width='{w}' height='{h}'></svg>"
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1.0
    n = len(values)
    pts = []
    for i, v in enumerate(values):
        x = i / (n - 1) * (w - 2) + 1
        y = (h - 3) - (v - lo) / rng * (h - 6)
        pts.append(f"{x:.1f},{y:.1f}")
    last_x, last_y = pts[-1].split(",")
    return (f"<svg class='es-spark' width='{w}' height='{h}' viewBox='0 0 {w} {h}' preserveAspectRatio='none'>"
            f"<polyline points='{' '.join(pts)}' fill='none' stroke='{color}' stroke-width='2' "
            "stroke-linecap='round' stroke-linejoin='round'/>"
            f"<circle cx='{last_x}' cy='{last_y}' r='2.2' fill='{color}'/></svg>")


def _trend_chip(curr: Optional[float], prev: Optional[float], unit: str = "") -> str:
    if curr is None or prev is None:
        return ""
    d = curr - prev
    if abs(d) < 0.5:
        return "<span class='es-trend flat'>&#9644; steady</span>"
    if d > 0:
        return f"<span class='es-trend up'>&#9650; {abs(d):.0f}{unit}</span>"
    return f"<span class='es-trend down'>&#9660; {abs(d):.0f}{unit}</span>"


# ---------------------------------------------------------------------------
# Legacy primitives (kept for tests / secondary views)
# ---------------------------------------------------------------------------
def hero(title: str, subtitle: str) -> str:
    return f"<div class='es-hero-strip'><h1>{title}</h1><p>{subtitle}</p></div>"


def kpi_card(label: str, value: str, desc: str = "", color: Optional[str] = None) -> str:
    style = f"color:{color};" if color else ""
    return (f"<div class='es-kpi'><div class='top'><span class='label'>{label}</span></div>"
            f"<div class='v' style='{style}'>{value}</div><div class='d'>{desc}</div></div>")


def kpi_row(cards: list) -> str:
    return "<div class='es-row'>" + "".join(cards) + "</div>"


def pill(text: str, kind: str = "info") -> str:
    return f"<span class='es-pill {kind}'>{text}</span>"


def remark(title: str, body: str) -> str:
    return f"<div class='es-obs'><b>{title}</b><br>{body}</div>"


# ---------------------------------------------------------------------------
# Animated engagement gauge
# ---------------------------------------------------------------------------
def engagement_gauge(score: float, level: str, confidence: Optional[float] = None,
                     classroom_status: str = "", animate: bool = True) -> str:
    full = 424.1
    filled = max(0.0, min(1.0, score / 100.0)) * full
    col = _color(score)
    animcls = " es-animon" if animate else ""
    status = classroom_status or _classroom_status(score)
    pill_txt = f"{level} · {status.lower()}" if level and level != "—" else "Waiting for a session"
    return (
        f"<div class='es-gauge-card{animcls}'><div class='es-gauge'>"
        "<svg viewBox='0 0 220 220'><defs>"
        "<linearGradient id='esEng' x1='0' y1='0' x2='1' y2='1'>"
        "<stop offset='0%' stop-color='#F87171'/><stop offset='45%' stop-color='#FBBF24'/>"
        "<stop offset='100%' stop-color='#34D399'/></linearGradient>"
        "<filter id='esGlow' x='-30%' y='-30%' width='160%' height='160%'>"
        "<feGaussianBlur stdDeviation='3.6' result='b'/>"
        "<feMerge><feMergeNode in='b'/><feMergeNode in='b'/><feMergeNode in='SourceGraphic'/></feMerge></filter></defs>"
        "<circle class='es-gtrack' cx='110' cy='110' r='90' stroke-dasharray='424.1 565.5'/>"
        f"<circle class='es-gval' cx='110' cy='110' r='90' filter='url(#esGlow)' "
        f"style='stroke-dasharray:{filled:.1f} 565.5;--esfill:{filled:.1f}'/>"
        f"</svg><div class='es-gcenter'><div class='es-gbig num' style='color:{col}'>{score:.0f}</div>"
        "<div class='es-gsub'>Engagement</div></div></div>"
        f"<div class='es-glevel' style='color:{col};background:{col}22'>{pill_txt}</div>"
        f"{_conf_badge(confidence)}"
        "<div class='es-gcap'>Live classroom engagement, blended from attention, emotion and presence.</div></div>"
    )


# ---------------------------------------------------------------------------
# Live status ribbon
# ---------------------------------------------------------------------------
def status_ribbon(items: list) -> str:
    """items: list of (label, state) where state is 'ok'|'warn'|'bad'."""
    chips = "".join(
        f"<span class='es-rib {state}'><span class='es-ribdot'></span>{label}</span>"
        for label, state in items
    )
    return f"<div class='es-ribbon'>{chips}</div>"


# ---------------------------------------------------------------------------
# AI processing pipeline
# ---------------------------------------------------------------------------
def ai_pipeline(stages: list) -> str:
    """stages: list of (icon, name, conf_label, active_bool)."""
    nodes = []
    for i, (icon, name, conf, active) in enumerate(stages):
        cls = "es-pnode" + (" on" if active else "")
        nodes.append(
            f"<div class='{cls}'><div class='es-pic'>{_icon(icon, 'currentColor', 17)}</div>"
            f"<div class='es-pname'>{name}</div><div class='es-pconf'>{conf}</div></div>"
        )
        if i < len(stages) - 1:
            nodes.append("<div class='es-parrow'>&#8250;</div>")
    return ("<div class='es-card es-pipewrap'><div class='es-pipehead'>"
            + _icon("brain", "#A78BFA", 16) + " AI processing pipeline"
            "<span class='es-pipesub'>how each frame becomes an insight</span></div>"
            f"<div class='es-pipe'>{''.join(nodes)}</div></div>")


# ---------------------------------------------------------------------------
# Webcam feed stats
# ---------------------------------------------------------------------------
def feed_stats(fps: float, resolution: str, conf: Optional[float],
               detection: str, lighting: str, model: str) -> str:
    conf_s = "—" if conf is None else f"{conf * 100:.0f}%"
    cells = [
        ("Tracking FPS", f"{fps:.0f}"), ("Resolution", resolution),
        ("Confidence", conf_s), ("Detection", detection),
        ("Lighting", lighting), ("Models", model),
    ]
    body = "".join(f"<div class='es-fs'><span class='fl'>{l}</span><span class='fv'>{v}</span></div>"
                   for l, v in cells)
    return f"<div class='es-feedstats'>{body}</div>"


# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
def _student_metrics(result: FrameResult) -> dict:
    students = result.students or []
    if not students:
        return dict(att=0.0, att_conf=None, emo_conf=None, eng_conf=None, avg_eng=0.0)
    att = _mean([(s.eye.attention if s.eye else s.engagement.attention) for s in students]) or 0.0
    att_conf = _mean([(s.eye.confidence if s.eye else None) for s in students])
    emo_conf = _mean([(s.emotion.confidence if (s.emotion and s.emotion.available) else None) for s in students])
    eng_conf = _mean([s.engagement.confidence for s in students])
    avg_eng = _mean([s.engagement.score for s in students]) or 0.0
    return dict(att=att * 100, att_conf=att_conf, emo_conf=emo_conf, eng_conf=eng_conf, avg_eng=avg_eng)


def kpi_cards(result: FrameResult, fps: float, elapsed: str, distinct_seen: Optional[int] = None,
              att_hist: Optional[list] = None, eng_hist: Optional[list] = None) -> str:
    m = _student_metrics(result)
    present = result.faces_present
    distracted = result.distracted_count
    mood = result.dominant_emotion.value.title()
    mood_col = "#FBBF24" if result.dominant_emotion.value == "happy" else "#9AA6BE"
    att_hist = att_hist or []
    eng_hist = eng_hist or []
    att_trend = _trend_chip(att_hist[-1] if att_hist else None,
                            att_hist[0] if len(att_hist) > 1 else None, "%")
    eng_trend = _trend_chip(eng_hist[-1] if eng_hist else None,
                            eng_hist[0] if len(eng_hist) > 1 else None)
    dist_txt = f"{distracted} distracted" if distracted else "all engaged"

    attention = (
        "<div class='es-card es-kpi'><div class='top'><span class='label'>Attention</span>"
        f"<span class='iconbox'>{_icon('eye', '#22D3EE')}</span></div>"
        f"<div class='v num' style='color:#22D3EE'>{m['att']:.0f}<span class='u'>%</span></div>"
        f"<div class='d'>{att_trend} looking at the board</div>"
        f"<div class='es-sparkrow'>{_sparkline(att_hist, '#22D3EE')}</div>"
        f"{_conf_badge(m['att_conf'])}</div>"
    )
    students = (
        "<div class='es-card es-kpi'><div class='top'><span class='label'>Students</span>"
        f"<span class='iconbox'>{_icon('users', '#A78BFA')}</span></div>"
        f"<div class='v num'>{present}</div>"
        f"<div class='d'><span class='es-trend flat'>&#9644; in frame</span> · {dist_txt}</div>"
        f"{_conf_badge(m['eng_conf'])}</div>"
    )
    mood_card = (
        "<div class='es-card es-kpi'><div class='top'><span class='label'>Class mood</span>"
        f"<span class='iconbox'>{_icon('smile', '#FBBF24')}</span></div>"
        f"<div class='v num' style='font-size:26px;color:{mood_col}'>{mood}</div>"
        "<div class='d'>dominant emotion right now</div>"
        f"{_conf_badge(m['emo_conf'])}</div>"
    )
    analysis = (
        "<div class='es-card es-kpi'><div class='top'><span class='label'>Analysis rate</span>"
        f"<span class='iconbox'>{_icon('bolt', '#34D399')}</span></div>"
        f"<div class='v num' style='color:#34D399'>{fps:.0f}<span class='u'> fps</span></div>"
        f"<div class='d'>{eng_trend or '<span class=es-trend up>&#9679; healthy</span>'} real-time</div>"
        f"<div class='es-sparkrow'>{_sparkline(eng_hist, '#34D399')}</div></div>"
    )
    return "<div class='es-kpis'>" + attention + students + mood_card + analysis + "</div>"


def live_kpis(result: FrameResult, fps: float, elapsed: str) -> str:
    """Legacy combined gauge+KPIs (kept for back-compat)."""
    eng = result.classroom_engagement
    eng_conf = _mean([s.engagement.confidence for s in (result.students or [])])
    return (f"<div class='es-live'>{engagement_gauge(eng, _level_label(eng), eng_conf, animate=False)}"
            f"{kpi_cards(result, fps, elapsed)}</div>")


# ---------------------------------------------------------------------------
# Student cards (premium analytics card)
# ---------------------------------------------------------------------------
def _student_tip(level_value: str, emotion: str) -> str:
    if level_value == "Poor":
        return "Consider a quick check-in or a direct question."
    if level_value == "Average":
        return "A short interactive prompt could re-engage them."
    if emotion in ("sad", "fear", "confused"):
        return "May benefit from a brief clarification."
    return "On track — keep the current approach."


def student_cards(result: FrameResult) -> str:
    students = result.students or []
    if not students:
        return ("<div class='es-card es-roster'><div class='es-panelhead'>Student remarks</div>"
                "<div class='es-stu'><div class='body'><div class='rmk'>No students detected yet. "
                "Start a session or run the demo.</div></div></div></div>")
    rows = ["<div class='es-card es-roster'><div class='es-panelhead'>" + _icon("users", "#A78BFA", 15)
            + " Student insights</div>"]
    for s in students:
        eng = s.engagement
        score = eng.score
        statclass, statlabel = _STATUS.get(eng.level.value, ("mod", eng.level.value))
        att = (s.eye.attention if s.eye else eng.attention) * 100
        emotion = (s.emotion.dominant.value if s.emotion else eng.dominant_emotion.value)
        conf = eng.confidence
        col = _color(score)
        band = eng.level.value
        tip = _student_tip(eng.level.value, emotion)
        rows.append(
            f"<div class='es-stu {statclass}'><div class='face'>{s.student_id + 1}</div><div class='body'>"
            f"<div class='r1'><span class='nm'>Student {s.student_id + 1}</span>"
            f"<span class='es-score {statclass} num'>{score:.0f} · {band}</span>"
            f"<span class='es-emo'>· {emotion}</span></div>"
            f"<div class='r2'><span class='es-mini'>Attention <b>{att:.0f}%</b></span>"
            f"<span class='es-mini'>Engagement <b>{score:.0f}</b></span>"
            f"<span class='es-mini'>Conf <b>{conf * 100:.0f}%</b></span></div>"
            f"<div class='es-prog'><i style='width:{max(2, min(100, score)):.0f}%;background:{col}'></i></div>"
            f"<div class='rmk'>{s.remark}</div>"
            f"<div class='es-tip'>{_icon('bulb', '#FBBF24', 12)}<span>{tip}</span></div></div></div>"
        )
    rows.append("</div>")
    return "".join(rows)


def students_panel(result: FrameResult) -> str:
    return student_cards(result)


def student_summary_cards(summaries: list) -> str:
    """Premium per-student cards for the Student Insights page (from session summaries)."""
    if not summaries:
        return ("<div class='es-card es-roster'><div class='es-panelhead'>Student insights</div>"
                "<div class='es-stu'><div class='body'><div class='rmk'>No student data yet. "
                "Run a session or the demo first.</div></div></div></div>")
    rows = ["<div class='es-card es-roster'><div class='es-panelhead'>" + _icon("users", "#A78BFA", 15)
            + " Per-student summary</div>"]
    for s in summaries:
        avg = s.average_engagement
        level = ("Excellent" if avg >= 81 else "Good" if avg >= 61 else "Average" if avg >= 31 else "Poor")
        if "Needs attention" in (s.behaviour_pattern or ""):
            level = "Poor"
        statclass, statlabel = _STATUS.get(level, ("mod", level))
        col = _color(avg)
        rows.append(
            f"<div class='es-stu {statclass}'><div class='face'>{s.student_id + 1}</div><div class='body'>"
            f"<div class='r1'><span class='nm'>Student {s.student_id + 1}</span>"
            f"<span class='es-score {statclass} num'>{avg:.0f} · {level}</span></div>"
            f"<div class='r2'><span class='es-mini'>Avg engagement <b>{avg:.0f}</b></span>"
            f"<span class='es-mini'>Trend <b>{s.trend.value}</b></span>"
            f"<span class='es-mini'>Attention <b>{s.attention_ratio:.0f}%</b></span>"
            f"<span class='es-mini'>Low periods <b>{s.low_engagement_periods}</b></span></div>"
            f"<div class='es-prog'><i style='width:{max(2, min(100, avg)):.0f}%;background:{col}'></i></div>"
            f"<div class='rmk'>{s.behaviour_pattern}</div>"
            f"<div class='es-tip'>{_icon('info', '#60A5FA', 12)}<span>Performance: {s.performance}</span></div>"
            "</div></div>"
        )
    rows.append("</div>")
    return "".join(rows)


# ---------------------------------------------------------------------------
# Engagement graph (inline SVG)
# ---------------------------------------------------------------------------
def engagement_graph_svg(timeseries: dict) -> str:
    t = timeseries.get("t") or []
    eng = timeseries.get("engagement") or []
    dis = timeseries.get("distracted") or []
    faces = timeseries.get("faces") or []
    head = (
        "<div class='es-chart'><div class='head'><h3>Engagement over this session</h3>"
        "<div class='es-legend'><span><i style='background:#6366F1'></i>Engagement</span>"
        "<span><i style='background:#F87171'></i>Distracted</span></div></div>"
    )
    if len(t) < 2:
        return head + ("<div style='height:180px;display:grid;place-items:center;color:#5E6A84;font-size:12.5px'>"
                       "Engagement will plot here as the session runs.</div></div>")
    n = len(t)
    step = max(1, n // 160)
    idx = list(range(0, n, step))
    if idx[-1] != n - 1:
        idx.append(n - 1)
    W, top, bot = 980, 12, 178
    tmin, tmax = t[0], (t[-1] if t[-1] != t[0] else t[0] + 1)
    max_faces = max(faces) if faces else 1

    def X(tv):
        return (tv - tmin) / (tmax - tmin) * W

    def Y(ev):
        return bot - max(0.0, min(100.0, ev)) / 100.0 * (bot - top)

    pts = [(X(t[i]), Y(eng[i])) for i in idx]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = (f"M{pts[0][0]:.1f},{bot} " + " ".join(f"L{x:.1f},{y:.1f}" for x, y in pts)
            + f" L{pts[-1][0]:.1f},{bot} Z")
    distracted_path = ""
    if faces and dis and max_faces > 0:
        dpts = [(X(t[i]), bot - (dis[i] / max_faces) * 36.0) for i in idx]
        distracted_path = ("<path d='M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in dpts)
                           + "' fill='none' stroke='#F87171' stroke-width='1.5' stroke-dasharray='3 4' opacity='.8'/>")
    grid = "".join(f"<line x1='0' y1='{y}' x2='980' y2='{y}'/>" for y in (40, 80, 120, 160))
    svg = (
        "<svg viewBox='0 0 980 190' width='100%' height='190' preserveAspectRatio='none'>"
        "<defs><linearGradient id='esFill' x1='0' y1='0' x2='0' y2='1'>"
        "<stop offset='0%' stop-color='rgba(99,102,241,.35)'/>"
        "<stop offset='100%' stop-color='rgba(99,102,241,0)'/></linearGradient></defs>"
        f"<g stroke='rgba(255,255,255,.06)' stroke-width='1'>{grid}</g>"
        f"<path d='{area}' fill='url(#esFill)'/>"
        f"<path d='{line}' fill='none' stroke='#6366F1' stroke-width='2.5'/>"
        f"{distracted_path}</svg>"
    )
    axis = f"<div class='es-axis'><span>start</span><span>{len(t)} samples</span><span>now</span></div>"
    return head + svg + axis + "</div>"


# ---------------------------------------------------------------------------
# Teacher insights / recommendations (live cards)
# ---------------------------------------------------------------------------
def _ins_kind(text: str) -> tuple:
    v = (text or "").lower()
    if any(k in v for k in ("declin", "decreas", "drop", "dip", "lower", "fell", "less", "lost")):
        return "warn", "alert", "#FBBF24"
    if any(k in v for k in ("strong", "positiv", "good", "excellent", "stable", "high",
                            "attentive", "maintain", "engaged", "improv", "recover")):
        return "ok", "check", "#34D399"
    return "info", "info", "#60A5FA"


def teacher_insights_card(observations: list) -> str:
    head = ("<div class='es-card es-teach'><h3>" + _icon("board", "#22D3EE", 16)
            + " Teacher Insights</h3><div class='sub'>Generated from live classroom analytics</div>")
    if not observations:
        return head + "<div class='es-ins info'>Insights appear here as the session gathers data.</div></div>"
    rows = []
    for o in observations[:5]:
        kind, icon, col = _ins_kind(o)
        rows.append(f"<div class='es-ins {kind}'>{_icon(icon, col, 15)}<span>{o}</span></div>")
    return head + "".join(rows) + "</div>"


def recommendations_card(suggestions: list) -> str:
    head = ("<div class='es-card es-teach'><h3>" + _icon("bulb", "#FBBF24", 16)
            + " AI Teaching Recommendations</h3><div class='sub'>Supportive and optional</div>")
    if not suggestions:
        return head + "<div class='es-ins info'>No specific recommendations right now - keep going.</div></div>"
    rows = "".join(f"<div class='es-rec'>{_icon('bulb', '#FBBF24', 15)}<span>{s}</span></div>"
                   for s in suggestions[:3])
    return head + rows + "</div>"


def teacher_panel(observations: list, suggestions: list, overall: str) -> str:
    return teacher_insights_card(observations)


# ---------------------------------------------------------------------------
# Teacher dashboard (full page: sectioned)
# ---------------------------------------------------------------------------
def teacher_dashboard(summary: str, trend: str, observations: list, suggestions: list,
                      alerts: list, avg_engagement: float) -> str:
    positives = [o for o in observations if _ins_kind(o)[0] == "ok"][:4]
    if not positives:
        positives = observations[:3]
    next_action = suggestions[0] if suggestions else "Maintain the current approach and keep monitoring."
    trend_icon = ("trend" if "ris" in trend.lower() else "alert" if "declin" in trend.lower() else "spark")
    trend_col = ("#34D399" if "ris" in trend.lower() else "#FBBF24" if "declin" in trend.lower() else "#60A5FA")

    def block(title, icon, col, inner):
        return (f"<div class='es-tsec'><div class='es-tsec-h'>{_icon(icon, col, 15)}{title}</div>{inner}</div>")

    pos = "".join(f"<div class='es-ins ok'>{_icon('check', '#34D399', 14)}<span>{o}</span></div>"
                  for o in positives) or "<div class='es-ins info'>Gathering observations…</div>"
    acts = "".join(f"<div class='es-rec'>{_icon('bulb', '#FBBF24', 14)}<span>{s}</span></div>"
                   for s in suggestions[:3]) or "<div class='es-ins info'>No actions needed right now.</div>"
    alert_html = ("".join(f"<div class='es-ins warn'>{_icon('alert', '#F87171', 14)}<span>{a}</span></div>"
                          for a in alerts[:3]) if alerts
                  else "<div class='es-ins ok'>" + _icon('check', '#34D399', 14)
                       + "<span>No priority alerts.</span></div>")

    summary_card = (
        "<div class='es-tsec es-tsummary'><div class='es-tsec-h'>" + _icon("board", "#fff", 15)
        + "Class Summary</div>"
        f"<div class='es-tsum-eng'>{avg_engagement:.0f}<span>avg engagement</span></div>"
        f"<div class='es-tsum-txt'>{summary or 'Session analysis in progress.'}</div></div>"
    )
    grid = (
        block("Positive Observations", "check", "#34D399", pos)
        + block("Attention Trends", trend_icon, trend_col,
                f"<div class='es-ins {_dot(trend)}'>{_icon(trend_icon, trend_col, 14)}"
                f"<span>Overall attention is <b>{trend.lower()}</b> this session.</span></div>")
        + block("Recommended Teaching Actions", "bulb", "#FBBF24", acts)
        + block("Priority Alerts", "alert", "#F87171", alert_html)
    )
    nexta = (
        "<div class='es-tnext'><div class='es-tsec-h'>" + _icon("target", "#A78BFA", 15)
        + "Next Suggested Action</div>"
        f"<div class='es-tnext-b'>{_icon('bulb', '#FBBF24', 16)}<span>{next_action}</span></div></div>"
    )
    return (summary_card + "<div class='es-tgrid'>" + grid + "</div>" + nexta)


# ---------------------------------------------------------------------------
# Global AI confidence card
# ---------------------------------------------------------------------------
def ai_confidence_card(overall: Optional[float], tracking: str, lighting: str,
                       detection: str, health: str) -> str:
    pct = "—" if overall is None else f"{overall * 100:.0f}%"
    barw = 0 if overall is None else max(0, min(100, overall * 100))
    rows = [("Tracking", tracking), ("Lighting", lighting),
            ("Face detection", detection), ("Model health", health)]
    body = "".join(
        f"<div class='es-arow'><span class='al'>{label}</span>"
        f"<span class='av'><span class='ad {_dot(val)}'></span>{val}</span></div>"
        for label, val in rows
    )
    return (
        "<div class='es-card es-aiconf'><h3>" + _icon("shield", "#34D399", 16)
        + " AI Confidence</h3><div class='sub'>For judging the reliability of these readings</div>"
        f"<div class='es-aibig'>{pct}<span>overall confidence</span></div>"
        f"<div class='es-bar'><i style='width:{barw:.0f}%'></i></div>{body}</div>"
    )


# ---------------------------------------------------------------------------
# Reports page builders
# ---------------------------------------------------------------------------
def report_stat_cards(summary: dict) -> str:
    items = [
        ("Average engagement", f"{summary.get('average_engagement', 0):.0f}%", "trend", "#6366F1"),
        ("Peak engagement", f"{summary.get('peak_engagement', 0):.0f}%", "spark", "#34D399"),
        ("Lowest engagement", f"{summary.get('lowest_engagement', 0):.0f}%", "alert", "#FB923C"),
        ("Avg students present", f"{summary.get('average_attendance', 0):.1f}", "users", "#A78BFA"),
        ("Frames analysed", f"{summary.get('frames_recorded', 0)}", "bolt", "#22D3EE"),
        ("Attention trend", str(summary.get('attention_trend', '—')), "chart", "#FBBF24"),
    ]
    cells = "".join(
        f"<div class='es-rstat'><span class='iconbox'>{_icon(icon, col)}</span>"
        f"<div><div class='rv'>{val}</div><div class='rl'>{label}</div></div></div>"
        for label, val, icon, col in items
    )
    return ("<div class='es-card es-rstats'><div class='es-panelhead'>" + _icon("chart", "#6366F1", 15)
            + " Session Statistics</div><div class='es-rstatgrid'>" + cells + "</div></div>")


def report_meta_card(summary: dict, duration: str) -> str:
    rows = [
        ("Session", summary.get("session_name", "—")),
        ("Session ID", (summary.get("session_id", "—") or "—")[:12]),
        ("Duration", duration),
        ("Frames", str(summary.get("frames_recorded", 0))),
        ("Formats", "PDF · Excel · CSV"),
    ]
    body = "".join(f"<div class='es-arow'><span class='al'>{l}</span><span class='av'>{v}</span></div>"
                   for l, v in rows)
    status = ("ok", "Ready to export") if summary.get("frames_recorded", 0) else ("warn", "Awaiting session data")
    return ("<div class='es-card es-aiconf'><h3>" + _icon("file", "#22D3EE", 16)
            + " Report Metadata</h3>"
            f"<div class='es-rstatus {status[0]}'><span class='ad {status[0]}'></span>{status[1]}</div>"
            + body + "</div>")


# ---------------------------------------------------------------------------
# Sidebar / topbar / status / banner
# ---------------------------------------------------------------------------
def sidebar_brand(app_name: str) -> str:
    return (
        "<div class='es-brand'><div class='es-logo'>"
        "<svg width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='2' "
        "stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z'/><circle cx='12' cy='12' r='3'/></svg>"
        f"</div><div><h1>{app_name}</h1><span>Engagement Monitor</span></div></div>"
    )


def sidebar_footer(version: str) -> str:
    return (
        "<div class='es-sidefoot'><div class='es-avatar'>RT</div>"
        f"<div><div style='font-size:12.5px;font-weight:600'>Teacher</div><small>Class 8B &middot; v{version}</small></div></div>"
    )


def sidebar_profile(name: str, klass: str, version: str, session: str) -> str:
    initials = "".join(w[0] for w in name.split()[:2]).upper() or "T"
    return (
        "<div class='es-profile'><div class='es-avatar lg'>" + initials + "</div>"
        f"<div class='es-profmeta'><div class='pn'>{name}</div>"
        f"<div class='pr'>Teacher</div>"
        f"<div class='es-profrow'><span>Class</span><b>{klass}</b></div>"
        f"<div class='es-profrow'><span>Version</span><b>v{version}</b></div>"
        f"<div class='es-profrow'><span>Session</span><b>{session}</b></div>"
        "</div></div>"
    )


def login_brand(app_name: str) -> str:
    return (
        "<div class='es-login-brand'><div class='es-login-logo'>"
        "<svg width='34' height='34' viewBox='0 0 24 24' fill='none' stroke='#fff' stroke-width='2' "
        "stroke-linecap='round' stroke-linejoin='round'>"
        "<path d='M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z'/><circle cx='12' cy='12' r='3'/></svg>"
        "<span class='es-login-ring'></span></div>"
        f"<h1>{app_name}</h1><p>AI-Powered Classroom Engagement Monitor</p>"
        "<div class='es-login-sub'>Sign in to your teacher dashboard</div></div>"
    )


def login_hint(email: str, password: str) -> str:
    return (f"<div class='es-login-hint'>Demo access &nbsp;·&nbsp; Email <b>{email}</b>"
            f" &nbsp;·&nbsp; Password <b>{password}</b></div>")


def topbar(title: str, session_name: str, elapsed: str, running: bool, demo: bool) -> str:
    live = ("<span class='es-live'><span class='es-dot'></span>LIVE</span>" if running
            else "<span class='es-live idle'><span class='es-dot'></span>IDLE</span>")
    badge = "<span class='es-demobadge'>DEMO</span>" if demo else ""
    sess = f"<span class='es-chip'>Session <b>{session_name}</b></span>" if session_name else ""
    return (f"<div class='es-ctx'><h2>{title}</h2>{live}{sess}"
            f"<span class='es-chip'>Time <b class='num'>{elapsed}</b></span>{badge}</div>")


def status_line(camera_status: str, health: str, within_budget: bool) -> str:
    return status_indicators(camera_status, health, within_budget, [])


def status_indicators(camera_status: str, health: str, within_budget: bool, alerts: list) -> str:
    cam_ok = camera_status in ("Streaming", "Running")
    pills = [
        f"<span class='es-pill {'ok' if cam_ok else 'warn'}'><span class='d2'></span>Camera: {camera_status}</span>",
        f"<span class='es-pill {'ok' if health == 'Healthy' else 'warn'}'><span class='d2'></span>Models: {health}</span>",
        f"<span class='es-pill {'ok' if within_budget else 'warn'}'><span class='d2'></span>"
        f"Performance: {'OK' if within_budget else 'watch'}</span>",
    ]
    for a in alerts[:2]:
        pills.append(f"<span class='es-pill bad'><span class='d2'></span>{a}</span>")
    return "<div class='es-status'>" + "".join(pills) + "</div>"


def demo_banner() -> str:
    return ("<div class='es-demo-banner'>No camera at your exhibition table? Press "
            "<b>Run demo</b> to play a realistic 36-second class - every panel and report "
            "fills in, no webcam or AI models required.</div>")
