# Changelog

All notable changes to EduSense AI 360 are documented here.
Format follows *Keep a Changelog*; versioning follows *Semantic Versioning*.

## [Unreleased]
### Added
- **Login screen (frontend-only).** A professional dark, glassmorphism sign-in page now
  gates the dashboard: animated EduSense logo, email + password fields, a password
  visibility toggle, "Remember me", a Sign in button, and inline validation. Credentials are
  validated against fixed demo values in the frontend only (no database, no network, no
  backend auth); on success the dashboard is revealed and the sidebar shows the authenticated
  teacher's profile (name, role, class, version, session). Wrong credentials show
  "Invalid email or password." without crashing.
- **Demo Mode** (`backend/pipeline/demo_source.py`) - a deterministic, camera-free and
  model-free synthetic classroom (five distinct student personas, a realistic
  high→dip→recover engagement arc) injected through a clean perception hook on the
  analysis pipeline. A "Run demo" button on the Live Monitor plays a ~36s class that
  populates every screen and report with no webcam or AI models - reliable for science-
  exhibition laptops. Covered by a new integration test (43 tests total).
- **UI: engagement gauge.** A 270° SVG ring gauge is now the live hero element
  (`frontend/components/cards.py`), with matching theme CSS (`frontend/theme/theme.py`)
  and a Live Monitor demo banner.

### Changed
- **Frontend rewritten to the approved dashboard** (`edusense_dashboard_mockup.html`).
  The Gradio app is now a single professional dashboard: a left **sidebar** with section
  navigation, a **topbar** showing live/demo state, the **engagement gauge**, **KPI cards**,
  a **large webcam feed** with engagement overlay, **student remark cards**, a **teacher
  insight panel**, a **live engagement graph** (inline SVG), and **system status indicators**.
  The approved stylesheet (dark theme, gradients, Space Grotesk + Inter, spacing, responsive
  layout) is ported into `frontend/theme/theme.py`; custom panels render as HTML/SVG in
  `frontend/components/cards.py` for fidelity, with native Gradio widgets only for the
  interactive parts (webcam, buttons, inputs). The app launches directly into this dashboard.
  Backend, AI modules, and analytics are unchanged. Validated end-to-end: builds (95
  components) and serves over HTTP under Gradio 6; theme/CSS applied version-robustly across
  Gradio 4 / 5 / 6 (constructor vs. launch()). Replaced the previous tabbed layout
  (`live_monitor_view.py` removed).

### Changed
- **Presentation upgrade (UI only; no backend/AI/analytics changes).** The Live Monitor
  dashboard now surfaces more of the data the backend already computes:
  - **AI confidence on every major reading** - engagement, attention, and class-mood now
    show real confidence badges read from `EngagementResult.confidence`,
    `EyeSignals.confidence`, and `EmotionResult.confidence`; when the backend reports a value
    as unavailable (e.g. emotion model absent) the UI prints "Confidence unavailable" rather
    than inventing a number.
  - **Teacher Insights card** and a separate **AI Teaching Recommendations card** (max 3),
    both populated from the existing teacher analytics (observations / suggestions), with
    status-coloured icons.
  - **Global AI Confidence card** for judges: overall confidence, tracking stability, lighting,
    face-detection quality, and model health - from real per-student detection confidence,
    face-count stability, the health monitor, and a presentation-layer brightness reading of
    the live frame.
  - **Detection card** replacing the plain "Students in frame" KPI: detected / tracked / lost /
    average engagement.
  - **Richer student cards**: attention, emotion, engagement, a 4-tier status
    (Excellent / Good / Moderate / Needs Attention) with green/blue/amber/red coding, and the AI remark.
  - **Enlarged webcam feed** (~19%) and general polish (consistent hover lift, softer shadows,
    smooth transitions, tighter spacing). Heavier panels (graph, teacher analytics) remain
    throttled so latency is unchanged. Validated: builds (98 components) and serves over HTTP
    under Gradio 6; 43 tests pass.

### Changed
- **Final professional UI/UX refinement (presentation layer only; no backend, AI, analytics,
  reports, export, config, or API changes).** The Live Monitor is now a commercial-grade
  analytics dashboard built to the approved mockup, and every secondary screen was elevated:
  - **Animated engagement gauge** - gradient ring with a glow filter that sweeps 0→score on
    the demo and at session start (held static on live ticks to avoid flicker), a large numeric
    score, a five-tier status (Excellent / Good / Average / Low / Very Low), the confidence
    underneath, and an overall classroom-status line.
  - **Live status ribbon** across the top: Camera, AI Models, Tracking, Lighting, Face
    Detection, Recording, and live student count - each colour-coded from real state with a
    subtle pulse.
  - **AI processing pipeline** strip (Camera → Face Detection → Eye Tracking → Emotion →
    Attention → Engagement → Teacher Insights → Reports) that visually explains the system and
    shows the real per-stage confidence beneath each node, animating the active stages.
  - **Webcam feed** enlarged with a six-metric strip beneath it: Tracking FPS, Resolution,
    Confidence, Detection status, Lighting, and Models.
  - **KPI cards** redesigned with icon, value, a mini trend arrow, a sparkline (from the
    real attention/engagement history), a confidence badge, equal heights and hover lift.
  - **Student cards** as premium analytics cards: avatar, number, attention, emotion,
    engagement, confidence, a four-tier status strip, an engagement progress bar, the AI
    remark and a short recommendation.
  - **Teacher Insights** page rebuilt into a sectioned recommendation dashboard: Class Summary,
    Positive Observations, Attention Trends, Recommended Teaching Actions, Priority Alerts and a
    Next Suggested Action.
  - **Reports** page (highest priority) redesigned into enterprise reporting: large preview
    card, export panel with report metadata and status, a session-statistics grid, and a
    generated-files list - same PDF / Excel / CSV functionality.
  - **Analytics** page gains summary-metric cards and grouped, labelled chart sections;
    **Student** page uses the premium summary cards; **Settings** page uses grouped cards with
    section headers and descriptions.
  - **Global polish**: a single consistent line-icon set, tightened typography hierarchy,
    consistent spacing, meaningful-only colour, subtle fade/hover micro-animations, and
    responsive grids. Validated: builds (103 components) and serves over HTTP under Gradio 6
    with no theme/CSS warning; 43 tests pass.

### Changed
- **Pixel alignment to the approved mockup** (`edusense_dashboard_mockup.html`, now treated
  token-for-token as the source of truth; still presentation-only - no backend/analytics/
  reports/API changes). Diffed the running app against the mockup and reconciled the
  remaining gaps:
  - **Design tokens** confirmed identical (ink/panel/line palette, indigo-soft, violet,
    teal/amber/mint/rose, text tiers, `--r` 16px), and the **card shadow** matched exactly
    (`0 1px 2px / 0 10px 30px`).
  - **Engagement gauge** rebuilt to the mockup's exact geometry: 220px ring, 16px stroke,
    54px Space-Grotesk number, the 0/45/100 gradient stops, and a single level-pill
    ("Good · class is attentive") above the descriptive caption - plus the confidence badge.
  - **KPI section** set to the mockup's 2×2 grid with the same four cards (Attention,
    Students, Class mood, Analysis rate), 30px values, 30px icon boxes and uppercase labels,
    keeping the sparkline + trend + confidence enrichments on the numeric cards.
  - **Student cards** now use the mockup's inline "score · band" format (e.g. "88 · Excellent",
    "24 · Poor") with the matching avatar gradient and spacing, retaining the per-student
    metrics row, engagement progress bar, remark and recommendation.
  - **Layout proportions** matched: hero `300px 1fr`, feed/students `1.55fr 1fr`, main padding
    `20px 26px 34px`, and the ribbon pills sized to the mockup's `.pill`.
  Validated: builds (103 components) and serves over HTTP under Gradio 6 with no theme/CSS
  warning; 43 tests pass.

### Changed
- **Session-name box is now reliably editable.** The live webcam stream no longer
  re-renders the dashboard while idle (it returns `gr.skip()` until a session is running), so
  the input keeps focus and can be typed into freely; the field is explicitly interactive with
  the placeholder "e.g. Class 8B – Science".
- **Sidebar** upgraded to a SaaS-style profile card (avatar, teacher name, class, version, live
  session) with a workspace section label and hover/press transitions.
- **Engagement gauge** thickened to an 18px ring with a brighter multi-pass SVG glow and a
  glowing centre number, keeping the smooth eased sweep.
- **Tighter vertical rhythm** across the dashboard to reduce empty space and feel less
  crowded. Validated: builds (117 components) and serves over HTTP under Gradio 6 with no
  theme/CSS warning; 43 tests pass; all functionality (webcam, demo, reports, exports,
  analytics, tracking) preserved.

## [1.0.0] - 2026-06-28
### Added
- **Phase 7 - Testing, packaging & release.** Pytest suite under `tests/`
  (unit/integration/system/performance, 42 tests) covering config, utilities, the AI
  and analytics engines, services, frame processing, the analysis pipeline, session
  lifecycle, reporting/export, an end-to-end controller flow, and performance budgets.
  Install/run/package scripts (`scripts/`, Windows + Unix), `RELEASE_NOTES.md`, and a
  final consistency pass.

### Added
- **Phase 6 - Reports, export, history & documentation.**
  `backend/reporting/report_engine.py` (assembles export-ready `ReportData` from a
  session) and `export_engine.py` (PDF via ReportLab with native engagement line chart
  + emotion pie + tables; Excel via OpenPyXL with Summary/Timeline/Students sheets; CSV
  via stdlib; deterministic file naming, history listing, retention pruning, writable-
  location validation). Reports tab (`frontend/views/reports_view.py`) with preview,
  PDF/Excel/CSV export, download, and history, wired into the app shell and controller.
  Documentation set (`documentation/`): Installation, User Manual, Developer Guide,
  Architecture, Troubleshooting, FAQ, Credits. Sample PDF/Excel/CSV reports in `samples/`.
- **Phase 5 - Dashboard, graphs, navigation & settings.** `backend/session/session_manager.py`
  (lifecycle: start/pause/resume/stop, authoritative timer, browser-frame processing,
  JSON persistence). `backend/reporting/graph_engine.py` (Plotly engagement/participation/
  emotion/per-student figures, Part 2 styling, empty-state placeholders). Frontend
  (`frontend/`): Part 2 theme + design-token CSS, reusable HTML card components, a
  gradio-free `DashboardController`, five views (Live Monitor with webcam streaming,
  Analytics, Student Insights, Teacher Insights, Settings), the `app_ui` assembler, and
  `main.py` entry point. The application is now runnable (`python main.py`).
- **Phase 4 - Analytics & Remarks engines.** `backend/analytics/`: `AttentionEngine`
  (state classification, focus continuity, attentive/distracted time), `EngagementEngine`
  (attention+emotion+presence blend -> 0-100 score, level, risk, prolonged-inattention
  timer, confidence), `StudentAnalytics` + `ClassroomAnalytics` (per-student trends,
  patterns, distributions; classroom time-series -> `FrameRecord`/`SessionSummary`),
  `TeacherAnalytics` (constructive, non-evaluative classroom insights with time-anchored
  drop points). `backend/remarks/`: priority-ordered `student_remarks` + `teacher_remarks`
  rules and the arbitrating `RemarksEngine` (one primary remark, no contradictions).
  `backend/pipeline/analysis_pipeline.py`: composes the perception pipeline with the new
  engines into the full per-frame `FrameResult` (perception `frame_pipeline.py` untouched).
- **Phase 3 - Perception (AI models + pipeline).** `backend/ai_models/`:
  `FaceDetector` + `FaceTracker` (MediaPipe detection with stable per-session ids via
  centroid tracking, loss/reacquisition); `EyeTracker` (FaceMesh EAR/gaze/head-pose,
  per-student temporal blink & sleep detection, attention blend + confidence);
  `EmotionDetector` (pluggable FER/DeepFace, rolling-window smoothing, confidence floor
  to Neutral, engagement-contribution mapping); `ModelRegistry` (lazy load, reuse,
  health reporting, versioning). `backend/pipeline/frame_pipeline.py`: the perception
  orchestrator (detect -> eyes -> emotion -> annotate) producing `PerceptionResult`,
  with analysis-frame downscaling + box rescaling and frame-quality confidence
  propagation. All heavy backends lazy-imported; logic verified via testing seams.
- **Phase 2 - Camera & Services.** Camera subsystem (`backend/camera/`): thread-safe
  latest-wins `FrameBuffer`, `FrameProcessor` (NumPy colour conversion + lighting/blur
  quality gating producing a confidence multiplier), and `CameraManager` (capture
  thread, resolution/FPS negotiation, live FPS, status, bounded-retry reconnection).
  Service scaffolding (`backend/services/`): `NotificationManager` (pub/sub + history),
  `HealthMonitor` (worst-status aggregation), `PerformanceMonitor` (FPS/frame-time +
  optional psutil CPU/memory vs configured budgets). Added `FrameQuality` contract and
  `frame_processing` + `performance` config sections (validated). Optional `psutil`.
- **Phase 1 - Foundation.** Target project structure (frontend/backend/config/core/
  utilities/assets/models/data/exports/logs/documentation/tests/scripts/samples).
- Configuration layer: `default_config.json`, `ConfigManager` (defaults + user +
  env merge, schema validation, weight normalisation), `SettingsManager`
  (validate/save/reset/import/export).
- Base architecture: typed data contracts (`backend/contracts/models.py`),
  exception hierarchy, categorised rotating logging, central error handler.
- Shared utilities (maths, smoothing, validation, safe IO).
- Pinned `requirements.txt`, `VERSION`, `.gitignore`, packaging metadata.

### Documentation
- Added **SRS Part 6 — AI Decision Logic, Intelligence Engine & Business Rules**:
  the definitive, explainable reasoning spec (attention/emotion/engagement/distraction
  engines, session intelligence, student/teacher insights, remarks/alert/trend engines,
  confidence system, decision priority, false-positive reduction, temporal analysis,
  ethics) governing the Phase 3–4 engine implementation.

