# EduSense AI 360 — Architecture Guide

A concise orientation. The authoritative architecture is **SRS Part 3**
(`documentation/srs/SRS_Part3_AI_Backend_Architecture.md`) and the reasoning rules are
**SRS Part 6** (`SRS_Part6_AI_Decision_Logic.md`).

## Layers (inward dependency direction)
```
Presentation (Gradio)  →  Business (session, pipelines, remarks, notifications)
  →  AI Processing (camera, face/eye/emotion)  →  Analytics (engagement, student/teacher)
  →  Reporting (graph/report/export)  →  Configuration  →  Utilities  →  Data
Cross-cutting: Logging · Error Handling · Health & Performance monitoring
```

## Data flow (per frame)
```
Webcam frame → Frame processing (quality + confidence) → Face detection (+tracking)
  → Eye tracking (attention) + Emotion detection → Engagement engine (score/level/risk)
  → Remarks → Student & Classroom analytics → Dashboard → Reports
```

## Contracts (the coupling backbone)
`FaceBox`, `FrameQuality`, `EyeSignals`, `EmotionResult`, `EngagementResult`,
`StudentResult`, `FrameResult`, `FrameRecord`, `SessionSummary` (in
`backend/contracts/`). Modules communicate only through these and configuration.

## Key engines
- **Attention engine** — state (High/Medium/Low/Unknown), focus continuity, time.
- **Engagement engine** — weighted blend (attention/emotion/presence) → 0–100, level,
  risk, prolonged-inattention timer, confidence.
- **Analytics** — per-student trends/patterns + classroom time-series & summary.
- **Remarks engine** — priority-ordered, one primary remark, no contradictions.
- **Graph / Report / Export** — Plotly for the live dashboard; ReportLab/OpenPyXL/CSV
  for downloadable reports (charts drawn natively, no extra image dependency).

## Reliability
Every module degrades safely on fault; capture, analysis, and UI are decoupled so
heavy processing never freezes the interface; confidence is lowered under poor
conditions rather than producing confident errors.
