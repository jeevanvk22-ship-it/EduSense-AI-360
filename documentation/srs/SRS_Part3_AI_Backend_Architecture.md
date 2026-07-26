# SOFTWARE REQUIREMENT SPECIFICATION (SRS)
# EduSense AI 360
## AI-Powered Smart Classroom Engagement & Teaching Quality Monitoring System

---

## PART 3 — AI & BACKEND ARCHITECTURE SPECIFICATION

| Field | Value |
|---|---|
| Document Part | Part 3 — AI & Backend Architecture |
| Continues From | Part 1A (Overview), Part 1B (Functional Requirements), Part 2 (UI/UX) |
| Version | 1.0 |
| Audience | AI/Backend Architecture, Computer Vision, Engineering, QA |
| Backend | Python 3.12+ |
| Frontend | Gradio |
| Hardware | Laptop + External USB Webcam only (no Arduino, Pi, sensors, IoT) |

### Preface

This part defines the **complete backend and AI architecture** of EduSense AI 360. It
specifies layers, modules, contracts, data flow, pipelines, engines, cross-cutting
concerns, performance budgets, security, scalability, and the engineering principles
the system obeys. It is written so that an implementer (human or AI) can construct the
entire backend with minimal assumptions.

The architecture follows enterprise software-engineering principles: layered and
modular design, loose coupling through explicit contracts, high cohesion within
modules, and a clean separation of concerns. This part contains architecture only —
no source code and no implementation technique.

### Architectural Tenets

- **Contract-first.** Modules communicate through stable, typed data objects
  (contracts), never through shared mutable globals. A module can be replaced if it
  honours its contract.
- **Single orchestration point.** One pipeline composes the AI modules per frame, so
  the rest of the system has exactly one integration surface.
- **Configuration as data.** All tunable behaviour lives in one configuration source;
  no module hard-codes thresholds.
- **Fail soft.** Any module may fail without crashing the system; it degrades to a safe
  neutral output and reports the fault.
- **Separation of capture, compute, and presentation.** These run as decoupled
  concerns so heavy compute never blocks capture or UI.

---

# 1. LAYERED SOFTWARE ARCHITECTURE

The system is organised into eight horizontal layers. A layer may depend only on the
layers conceptually beneath it (toward Utilities/Configuration/Data) and never reaches
upward. This enforces a clean dependency direction.

```
┌──────────────────────────────────────────────────────────────┐
│ 1. PRESENTATION LAYER          (Gradio dashboard, controls)    │
├──────────────────────────────────────────────────────────────┤
│ 2. BUSINESS LOGIC LAYER        (session, orchestration, rules) │
├──────────────────────────────────────────────────────────────┤
│ 3. AI PROCESSING LAYER         (CV + DL: face/eye/emotion)     │
├──────────────────────────────────────────────────────────────┤
│ 4. ANALYTICS LAYER             (engagement, student/teacher)   │
├──────────────────────────────────────────────────────────────┤
│ 5. REPORTING LAYER             (graphs, reports, exports)      │
├──────────────────────────────────────────────────────────────┤
│ 6. CONFIGURATION LAYER         (settings, thresholds, theme)   │
├──────────────────────────────────────────────────────────────┤
│ 7. UTILITY LAYER               (math, smoothing, helpers, IO)  │
├──────────────────────────────────────────────────────────────┤
│ 8. DATA LAYER                  (session store, logs, files)    │
└──────────────────────────────────────────────────────────────┘
        Cross-cutting: Logging · Error Handling · Health/Perf Monitoring
```

## 1.1 Presentation Layer
Renders the dashboard and all views (Part 2), captures user intent (start/stop, switch
camera, refresh, export, settings), and displays live values, graphs, remarks, and
notifications. It contains **no AI or analytics logic** — it only invokes the Business
Logic Layer and renders returned data. This keeps the UI thin and replaceable.

## 1.2 Business Logic Layer
The system's coordinator. Hosts the **Session Manager**, the **Frame Pipeline
orchestrator**, the **Remarks Engine** rule arbitration, and the **Notification
Manager**. It decides *what happens when*: it drives the per-frame sequence, governs
session lifecycle, applies business rules, and routes results to analytics, reporting,
and presentation. It depends on the AI, Analytics, Reporting, Configuration, Utility,
and Data layers but exposes a clean façade upward to Presentation.

## 1.3 AI Processing Layer
The computer-vision and deep-learning core: **Frame Processing**, **Face Detection**,
**Eye Tracking**, and **Emotion Detection**. It transforms raw frames into structured
per-face signals (contracts). Each module loads its model lazily and degrades safely.
This layer is stateless with respect to sessions — it analyses the current frame and
returns results, leaving accumulation to the Analytics Layer.

## 1.4 Analytics Layer
Turns per-frame signals into meaning: the **Engagement Engine**, **Attention Engine**,
**Student Analytics Engine**, and **Teacher Analytics Engine**. It computes scores,
accumulates session statistics, detects trends and patterns, and produces the inputs
the Remarks and Reporting layers consume.

## 1.5 Reporting Layer
Produces visual and document outputs: the **Graph Engine**, **Report Engine**, and
**Export Engine**. It consumes analytics outputs and renders timelines, summaries, and
PDF/Excel/CSV reports.

## 1.6 Configuration Layer
The single source of truth for tunable behaviour: thresholds, weights, band
boundaries, camera defaults, theme, paths, and feature toggles. Hosts the **Settings
Manager** and **Configuration Manager**. Every other layer reads configuration from
here; none hard-codes parameters.

## 1.7 Utility Layer
Reusable, dependency-light helpers: math (normalisation, distance), temporal smoothing
(moving averages), validation primitives, time/format helpers, and safe IO wrappers.
Has no knowledge of domain concepts and is freely reusable everywhere.

## 1.8 Data Layer
Persistence and durable artefacts: session records (JSON, with SQLite as a defined
upgrade path), generated reports, and logs. It abstracts storage so higher layers
persist and retrieve via simple operations without knowing the storage medium.

## 1.9 Cross-Cutting Concerns
**Logging**, **Error Handling**, and **Health/Performance Monitoring** span all layers
and are described in Sections 17–20.

---

# 2. MODULAR ARCHITECTURE

Each feature is an independent module with one responsibility, a defined input/output
contract, and no hidden coupling. Modules are grouped by the layer they belong to.

## 2.1 Module Catalogue & Responsibilities

| Module | Layer | Responsibility |
|---|---|---|
| **Camera Module** | AI/Capture | Acquire frames from the USB webcam; manage device lifecycle, resolution, FPS, and reconnection. |
| **Frame Processing Module** | AI | Normalise, colour-convert, denoise, and prepare frames for analysis; gate poor-quality frames. |
| **Face Detection Module** | AI | Detect and track faces; emit bounding regions, confidence, stable IDs. |
| **Eye Tracking Module** | AI | Derive eye openness, blink, gaze, sleep, and attention signals per face. |
| **Emotion Detection Module** | AI | Classify facial emotion with confidence; stabilise over frames; map to engagement contribution. |
| **Engagement Engine** | Analytics | Fuse attention, emotion, presence, and continuity into engagement %, level, risk, confidence. |
| **Attention Engine** | Analytics | Specialised computation/aggregation of attention state and focus continuity. |
| **Student Analytics** | Analytics | Accumulate per-student session metrics, distributions, trends, patterns. |
| **Teacher Analytics** | Analytics | Analyse classroom-level patterns and produce constructive, non-evaluative insights. |
| **Remarks Generator** | Business | Generate prioritised student/teacher remarks, recommendations, alerts, positive feedback. |
| **Graph Engine** | Reporting | Build live and historical visualisations from time-series data. |
| **Report Engine** | Reporting | Assemble session reports (summary, stats, charts, remarks). |
| **Export Engine** | Reporting | Render reports to PDF/Excel/CSV; manage file naming and history. |
| **Settings Manager** | Configuration | Present, validate, persist, reset, import/export user settings. |
| **Configuration Manager** | Configuration | Hold runtime configuration; provide validated values to all modules. |
| **Logger** | Cross-cutting | Capture categorised, timestamped logs across the system. |
| **Notification Manager** | Business | Raise UI notifications (success/warning/error/info/progress). |
| **Session Manager** | Business | Govern session lifecycle, timing, statistics, storage, cleanup. |
| **Performance Monitor** | Cross-cutting | Measure FPS, frame time, CPU/memory; surface health. |
| **Health Monitor** | Cross-cutting | Track module/pipeline health; drive degraded-mode decisions. |
| **Error Handler** | Cross-cutting | Centralise fault containment, classification, and recovery. |
| **Utility Manager** | Utility | Provide shared math, smoothing, validation, and IO helpers. |

## 2.2 Orchestration
A single **Frame Pipeline** (Business Logic Layer) composes the AI modules in order and
hands results to Analytics, Remarks, and Presentation. It is the only place that knows
the module composition; all other components depend on its outputs, not on individual
AI modules. This is the system's single integration point and the natural seam for
future modules.

---

# 3. DATA CONTRACTS

Modules exchange typed, immutable result objects. These contracts are the backbone of
loose coupling: a module may be reimplemented freely provided it emits the same
contract. The canonical contracts are:

| Contract | Produced by | Key fields |
|---|---|---|
| **FaceBox** | Face Detection | bounding region, confidence, stable id, crop accessor |
| **EyeSignals** | Eye Tracking | eyes_open, ear, gaze direction/offset, head pose, attention, confidence |
| **EmotionResult** | Emotion Detection | dominant emotion, per-emotion scores, confidence, engagement_contribution |
| **EngagementResult** | Engagement Engine | score (0–100), level, attention, emotion_score, presence, distracted, prolonged_inattention, confidence |
| **StudentResult** | Pipeline | student_id, FaceBox, EngagementResult, remark |
| **FrameResult** | Pipeline | per-student results, classroom_engagement, faces_present, distracted_count, dominant_emotion, annotated frame |
| **FrameRecord** | Session/Analytics | timestamped snapshot of classroom metrics for the session time-series |
| **SessionSummary** | Analytics | aggregate session statistics and trend classification |

Contracts carry confidence where applicable so downstream consumers can weight or
discount uncertain inputs.

---

# 4. DATA FLOW

The end-to-end flow transforms light hitting the webcam into insight on screen and in
reports.

```
Webcam ─▶ Frame Capture ─▶ Frame Processing ─▶ Face Detection ─▶ Eye Tracking ─▶
Emotion Detection ─▶ Engagement Calculation ─▶ Analytics Engine ─▶ Remarks Generator ─▶
Dashboard ─▶ Report Generator
```

## 4.1 Stage-by-Stage
1. **Webcam → Frame Capture.** The Camera Module continuously reads frames on a
   dedicated capture path and places the latest valid frame onto a bounded buffer.
2. **Frame Capture → Frame Processing.** A frame is colour-converted, normalised, and
   quality-checked (lighting, validity). Poor frames are flagged and may be skipped.
3. **Frame Processing → Face Detection.** Faces are located; each is tracked to a
   stable ID; weak detections are discarded; bounding regions are clamped to the frame.
4. **Face Detection → Eye Tracking.** For each face, landmark geometry yields eye
   openness, blink, gaze, sleep, and an attention estimate with confidence.
5. **Face Detection → Emotion Detection.** Each face crop is classified into an emotion
   with confidence, stabilised over recent frames, and mapped to an engagement
   contribution. (Eye and emotion analysis are independent and may run in parallel.)
6. **→ Engagement Calculation.** The Engagement Engine fuses attention, emotion,
   presence, and focus continuity into an engagement %, level, risk, and confidence per
   student, and a classroom average.
7. **→ Analytics Engine.** Per-frame results are appended to the session time-series;
   Student and Teacher Analytics accumulate metrics, distributions, trends, and
   patterns.
8. **→ Remarks Generator.** Engagement and analytics drive prioritised, constructive
   student and teacher remarks, alerts, and positive feedback.
9. **→ Dashboard.** The annotated frame, live metrics, graphs, and remarks are rendered
   in real time.
10. **→ Report Generator.** On demand or session end, aggregated data, charts, and
    remarks are assembled and exported.

## 4.2 Flow Properties
- **One-directional per frame** with clear hand-offs; no stage mutates an earlier
  stage's data.
- **Decoupled timing:** capture, analysis, and presentation operate at independent
  cadences (Section 5, 21) so a slow stage never stalls the others.
- **Fault isolation:** a failing stage yields a neutral contract and a logged fault;
  the flow continues.

---

# 5. CAMERA PIPELINE

## 5.1 Stages
- **Camera Initialization.** Enumerate devices, select the configured device, open it,
  and request the configured resolution/FPS, negotiating the nearest supported values.
- **Resolution & FPS.** Driven by configuration; the achieved values are measured and
  exposed, not assumed.
- **Frame Buffer.** A small bounded buffer holds the most recent frame(s); the analysis
  side always consumes the latest, preventing backlog and latency growth.
- **Frame Queue.** A bounded queue decouples the capture cadence from the analysis
  cadence; when full, the oldest frame is dropped (latest-wins) to keep liveness.
- **Frame Synchronization.** Each frame carries a timestamp/sequence so analytics align
  to real time and the session time-series is monotonic.
- **Frame Validation.** Frames are validated as non-empty and correctly dimensioned
  before entering analysis.
- **Camera Failure Recovery.** Disconnects are detected via repeated failed reads;
  analysis pauses, status updates, and a bounded-retry reconnection runs; on success,
  capture and analysis resume without corrupting the in-progress session.

## 5.2 Concurrency Model
Capture runs independently of analysis and UI. The capture path's sole job is to keep
the latest valid frame available; the analysis path pulls frames at its own
sustainable rate (with frame-skipping under load). This separation is what guarantees a
responsive UI and stable liveness.

---

# 6. COMPUTER VISION PIPELINE

Per analysed frame, the CV pipeline performs:

1. **Image Acquisition.** Obtain the latest valid frame from the camera pipeline.
2. **Color Conversion.** Convert to the colour space each model expects.
3. **Image Normalization.** Scale/normalise intensity for consistent model input.
4. **Frame Optimization.** Optionally downscale for detection to bound per-frame cost;
   analyse at a resolution balancing accuracy and throughput.
5. **Noise Reduction.** Light denoising to stabilise landmarks and predictions without
   destroying detail.
6. **Lighting Handling.** Assess brightness/contrast; compensate where feasible and
   flag low-quality frames so confidence is reduced rather than silently trusted.
7. **Face Region Extraction.** Crop validated face regions for per-face analysis.
8. **Preprocessing.** Resize/normalise each crop to the emotion model's input spec.
9. **Model Input.** Present prepared tensors/inputs to the relevant models.
10. **Prediction.** Run face, landmark, and emotion inference.
11. **Post Processing.** Convert raw outputs into contracts; apply thresholds,
    smoothing, and confidence handling.

The pipeline is **idempotent per frame** and side-effect-free except for emitting
contracts, which makes it testable in isolation.

---

# 7. FACE DETECTION ARCHITECTURE

- **Face Detection.** Locate all faces in the (optionally downscaled) frame.
- **Face Bounding Box.** Emit a region per face, clamped to frame bounds.
- **Face Confidence.** Attach a detection confidence; discard sub-threshold detections.
- **Multiple Face Handling.** Support up to a configured maximum; beyond it, retain the
  strongest detections and flag that the limit was reached.
- **Face Tracking.** Associate detections across frames (centroid/overlap) to maintain
  stable per-student identities.
- **Face Quality.** Assess size, sharpness, and pose adequacy; poor-quality faces lower
  downstream confidence.
- **Face Loss.** Mark an identity lost after a configured number of consecutive
  absences.
- **Face Recovery / Reacquisition.** Re-match a face reappearing nearby within a grace
  window to its prior identity where possible.

**Outputs:** a list of `FaceBox` per frame plus a visible-face count.

---

# 8. EYE TRACKING ARCHITECTURE

- **Eye Landmark Detection.** Extract eye and iris landmarks per face.
- **Eye Aspect Ratio (EAR).** Compute openness; classify open/closed against threshold.
- **Blink Detection.** Identify brief open→closed→open transitions, distinct from
  sustained closure.
- **Gaze Direction.** Estimate centre/left/right/up/down from iris position and head
  orientation.
- **Eye Closure / Sleep Detection.** Flag sustained closure beyond a configured
  duration as drowsiness/sleeping.
- **Focus Detection.** Combine eyes-open + gaze-on-target + forward head pose into a
  focus indication.
- **Attention Score.** Blend the focus components into an attention value in [0, 1].
- **Confidence Score.** Reflect landmark completeness and face quality.

Transient landmark noise is smoothed so single-frame glitches do not create spurious
blink/sleep events. **Output:** an `EyeSignals` per face.

---

# 9. EMOTION DETECTION ARCHITECTURE

- **Model Selection.** A pluggable backend (lightweight default; heavier optional)
  chosen via configuration behind a uniform interface.
- **Preprocessing.** Size/normalise each face crop to model spec.
- **Prediction.** Produce per-emotion probabilities over the supported set (Happy,
  Neutral, Sad, Angry, Fear, Surprise; Confused derived where required).
- **Confidence Filtering.** Treat low-confidence predictions as neutral; handle unknown
  gracefully.
- **Temporal Smoothing.** Average predictions across a configured window per student to
  suppress flicker.
- **Emotion Stability.** Require consistency before switching the reported dominant
  emotion.
- **Emotion History / Timeline.** Maintain per-student emotion over time for analytics
  and the emotion timeline graph.
- **Emotion Confidence.** Carry a confidence value with each result.

Emotion maps to an **engagement contribution** in [-1, 1] via configuration. **Output:**
an `EmotionResult` per face.

---

# 10. ENGAGEMENT ENGINE

An independent analytics engine; the system's interpretive heart.

## 10.1 Inputs
Attention (Eye Tracking), Emotion (engagement contribution), Eye-tracking focus
continuity, Face presence, and Session behaviour (duration, continuity history).

## 10.2 Outputs
Engagement % (0–100), Engagement Level (Poor/Average/Good/Excellent per Part 1B), Risk
Level, Confidence, Current Status, and an Overall Session Score.

## 10.3 Conceptual Derivation
Each factor is normalised to a common 0–1 scale, then combined with **configurable
weights summing to one**:
- **Attention** is the primary driver (open eyes, centred gaze, forward head).
- **Emotion** shifts the score up for positive/learning affect, down for
  frustration/confusion.
- **Presence** rewards a reliably visible face and reduces score/confidence when absent.
- **Continuity of focus** rewards sustained attention and penalises repeated
  distraction.
- **Session context** distinguishes a brief dip from a sustained decline.

The weighted blend yields the engagement %, mapped to a level via configured bands.
**Risk Level** rises with persistently low engagement or prolonged inattention.
**Confidence** is derived from input confidences and face quality. **Overall Session
Score** aggregates engagement across the session. Temporal smoothing keeps the live
value stable. Missing inputs default to neutral and lower confidence rather than
failing. **Output:** an `EngagementResult` per student and a classroom average.

---

# 11. ATTENTION ENGINE

A focused sub-engine that consolidates attention semantics so engagement logic stays
clean:
- Aggregates eye-tracking attention and gaze/focus signals into an attention state.
- Tracks **focus continuity** (sustained on-task frames) and **distraction streaks**.
- Maintains per-student attentive vs distracted time for analytics.
- Flags **prolonged inattention** when distraction persists beyond the configured
  duration.
It feeds both the Engagement Engine (as the attention factor) and Student Analytics (as
time accumulations).

---

# 12. STUDENT ANALYTICS ENGINE

Accumulates and summarises per-student data over the session:
- **Attention %** — attentive proportion of tracked time.
- **Emotion Distribution** — time share per emotion.
- **Focus Duration / Distraction Duration** — accumulated from attention state.
- **Average Engagement** and **Peak Engagement**.
- **Low Engagement Periods** — intervals below threshold, with timing.
- **Trend Analysis** — improving/declining/stable across session portions.
- **Behaviour Pattern / Learning Pattern** — qualitative pattern from the engagement
  and emotion time-series.
- **Performance Summary** — overall classification via engagement bands.

Accumulations remain consistent with elapsed session time and tolerate gaps from
missing frames or lost faces. Trends require a minimum data volume before being
reported.

---

# 13. TEACHER ANALYTICS ENGINE

Analyses **classroom-level engagement patterns** and never evaluates or ranks the
teacher (policy reinforced from Parts 1B and 2). It produces:
- **Attention Trend** and **Engagement Trend** over the session.
- **Attention Drop Timeline** — time-anchored dips (e.g. "dip at 20:00").
- **Interaction Suggestions** and **Teaching Suggestions** — constructive, impersonal.
- **Session Insights** — supportive observations correlating engagement with elapsed
  time/segments.
- **Improvement Opportunities** — actionable, non-judgemental guidance.

All output is constructive, unbiased, and impersonal; insights are generated only when
sufficient session data exists.

---

# 14. REMARKS ENGINE

A rule-driven engine producing natural-language outputs: Student Remarks, Teacher
Remarks, Session Summary, Recommendations, Alerts, Warnings, Positive Feedback, and
Constructive Suggestions.

## 14.1 Rule Prioritisation
Rules are evaluated in a defined priority order so the most important message surfaces:
1. **Safety/attention alerts** — prolonged inattention, sustained sleep/closure, or
   strong risk indicators take top priority.
2. **Negative/declining patterns** — persistent low engagement, distraction streaks,
   confusion.
3. **Neutral/steady states.**
4. **Positive reinforcement** — sustained strong engagement.

Per student, exactly one **primary** remark is emitted (highest-priority matching
rule), with optional secondary supportive notes. Teacher remarks map classroom patterns
to constructive suggestions under the same priority discipline.

## 14.2 Tone Policy
All remarks are supportive and non-stigmatising; sensitive states are framed as
possibilities warranting attention, never as diagnoses; teacher remarks are never
personal criticism. The engine is rule-transparent now and may be replaced by an
LLM-backed generator behind the same interface later.

---

# 15. SESSION MANAGER

Governs the session lifecycle:
- **Session Start.** Initialise a session record, reset per-student state, start timing.
- **Pause / Resume.** Suspend and resume analysis while preserving accumulated data and
  the timeline's integrity.
- **Session End.** Finalise timing, compute summaries, persist the session.
- **Session Timer.** Maintain authoritative elapsed time for the UI and analytics.
- **Session Statistics.** Expose live and final aggregates.
- **Session Storage.** Persist the session (summary + time-series) to the Data Layer
  (JSON; SQLite upgrade path).
- **Session Cleanup.** Release models/camera handles and free buffers on end; support
  retention/pruning of old sessions.

The Session Manager is the temporal authority; analytics align to its clock.

---

# 16. GRAPH ENGINE

Builds visualisations from the session/analytics time-series:
- **Live Graphs** — append new points smoothly without full redraw.
- **Historical Graphs** — render a completed session.
- **Timeline Graphs** — engagement, emotion, attention over time.
- **Emotion Graphs** — distribution (donut/stacked) using the fixed emotion palette.
- **Attention / Engagement Graphs** — trends with annotations (e.g. drop points).
- **Trend & Summary Graphs** — aggregate views for reports.

The engine consumes analytics outputs and applies the Part 2 chart styling (colours,
legends, axes, tooltips, animation). It is presentation-agnostic: it produces figure
data/objects the dashboard and Report Engine both consume, avoiding duplicate charting
logic. It handles empty/sparse data gracefully.

---

# 17. REPORT ENGINE & EXPORT ENGINE

## 17.1 Report Engine
- **Data Collection.** Gather the finished session record, analytics summaries, and
  remarks.
- **Data Aggregation.** Compute report-level statistics (averages, peaks, distributions).
- **Summary Generation.** Produce the narrative session summary.
- **Chart Generation.** Request figures from the Graph Engine for embedding.
- **Report Formatting.** Lay out sections: header (date/time/duration), engagement and
  attention statistics, emotion statistics, charts, teacher remarks, student remarks,
  overall summary.

## 17.2 Export Engine
- **PDF Export.** A formatted, professional document with embedded charts.
- **Excel Export.** Summary sheet plus the full per-frame timeline.
- **CSV Export.** Tabular timeline and summary data.
- **File Naming.** Deterministic, collision-resistant names (session id + type +
  timestamp) under the configured export location.
- **History Management.** Track generated files (name, date, format) for the Report
  panel's history.

Export is permitted only when session data exists; the target location is validated as
writable; failures are reported clearly while preserving existing data.

---

# 18. SETTINGS & CONFIGURATION MANAGER

## 18.1 Configuration Manager
Holds the authoritative runtime configuration (thresholds, weights, band boundaries,
camera defaults, theme, paths, toggles) and serves validated values to every module. No
module hard-codes parameters.

## 18.2 Settings Manager
- **Configuration Loading.** Load persisted settings at startup; apply documented
  defaults when absent.
- **Configuration Validation.** Validate every value against its range/set before
  applying; reject invalid values with a clear message and retain the prior value.
- **Configuration Saving.** Persist changes durably.
- **Default Settings / Reset.** Restore documented defaults on confirmed reset.
- **Import / Export.** Exchange configuration as a portable file.

A corrupt/missing store falls back to defaults and logs the event. Runtime-applicable
changes take effect immediately; others indicate a restart is needed.

---

# 19. LOGGING SYSTEM

Enterprise logging spans the system with categorised, timestamped, severity-tagged
records:
- **Application Logs** (lifecycle/events), **Error Logs**, **Warning Logs**,
  **Performance Logs** (FPS, frame time, resource use), **Camera Logs**
  (connect/disconnect/recovery), **AI Logs** (model load, prediction faults), **Export
  Logs**, **Debug Logs**, and **Session Logs** (start/pause/resume/end).

Logging is **non-blocking** and never crashes or stalls the analysis pipeline; if log
storage is unavailable it degrades gracefully. Verbosity is configurable. Logs support
diagnosis, audit, and support, and are structured to allow future rotation and remote
aggregation.

---

# 20. ERROR HANDLING & RECOVERY

A centralised **Error Handler** classifies faults, contains them, logs them with
context, and selects a recovery strategy. The universal rule: **no single fault crashes
the application; degrade safely and inform the user.**

| Condition | Handling / Recovery |
|---|---|
| **Camera Failure** | Pause analysis, update status, bounded-retry reconnect, resume on success. |
| **Frame Failure** | Skip the frame, log, continue with the next. |
| **No Face** | Skip per-student analysis for the frame; surface sustained absence as a warning. |
| **Poor Lighting** | Reduce confidence, warn the user; avoid silently trusting unreliable results. |
| **Emotion Prediction Failure** | Degrade to neutral emotion, continue. |
| **Model Failure** | Disable only the affected capability; degrade gracefully; log. |
| **Missing Libraries** | Detect at startup; clear message naming what's missing; disable only affected features. |
| **Export Failure** | Clear error, preserve data, allow retry. |
| **Dashboard Failure** | Surface a user-friendly message; keep capture/analysis alive; recover the view. |
| **Configuration Failure** | Fall back to defaults; log; prompt re-save. |
| **Unexpected Exceptions** | Catch at module and pipeline boundaries; isolate; log full context; keep the app running. |

**Recovery Mechanisms:** bounded retries with backoff (camera), latest-wins frame
dropping (overload), neutral-default substitution (AI faults), and degraded modes
driven by the Health Monitor.

---

# 21. PERFORMANCE OPTIMIZATION

Targets are specified on a **reference laptop** (modern multi-core CPU, integrated
graphics, no discrete GPU required) and are **configurable**; they define design intent,
not hard guarantees on all hardware.

| Metric | Target (reference hardware) |
|---|---|
| **Startup Time** | Interactive within ~5–8 s (excluding first-run model download). |
| **Maximum Memory Usage** | Typical ≤ ~1.5 GB; ceiling ~2 GB; no unbounded growth over a session. |
| **CPU Usage** | Sustained within a bounded share (≈ ≤ 60% of available cores) during live analysis, keeping the machine responsive. |
| **GPU Usage** | Optional; the system is CPU-first and fully functional without a GPU. GPU, if present, may accelerate inference. |
| **Expected FPS** | Smooth real-time monitoring (effective analysis ≈ 12–20 FPS via frame-skipping; capture preview higher). |
| **Frame Processing Time** | Per analysed frame within a real-time budget (≈ ≤ 60–80 ms). |
| **Dashboard Refresh Time** | Live indicators ≈ 2 Hz; charts ≈ 1 Hz; smooth, not overloading. |
| **Response Time** | User actions (start/stop/switch/export trigger) acknowledged within ≈ ≤ 200 ms. |

## 21.1 Optimisation Strategies
- **Frame-skipping / analysis throttling** under load (latest-wins).
- **Detection downscaling** to bound per-frame cost.
- **Lazy model loading** so startup is fast and unused backends cost nothing.
- **Temporal smoothing** to reduce recomputation jitter and stabilise output.
- **Decoupled capture/analysis/UI** so no stage blocks another.
- **Configurable performance controls** (analysis frequency, resolution) to adapt to
  hardware.

---

# 22. SECURITY

As an offline, single-machine desktop application, the security posture centres on
robustness and safe local handling rather than network defence:
- **Input Validation.** Validate all external inputs — camera selection, settings,
  file paths — against permitted ranges/sets before use.
- **Configuration Protection.** Validate and sanitise configuration on load; reject
  malformed values; fall back to safe defaults.
- **Export Validation.** Verify export targets are writable and within the configured
  location; produce well-formed files.
- **Safe File Handling.** Use safe paths, avoid overwriting unintentionally via
  deterministic naming, and handle IO errors explicitly.
- **Error Isolation.** Contain faults at module/pipeline boundaries so one failure
  cannot corrupt shared state.
- **Crash Recovery.** Persist session data progressively so an unexpected termination
  loses minimal data; recover to a clean state on restart.

Future networked features (cloud, accounts, API) introduce additional security
requirements (authentication, authorisation, encryption in transit/at rest) addressed
when those capabilities are designed.

---

# 23. FUTURE SCALABILITY

The architecture is designed for additive growth: new capabilities attach at defined
seams (the Frame Pipeline, the analytics contracts, the Data Layer) without rewriting
existing modules.

| Future capability | How the architecture accommodates it |
|---|---|
| **Voice Analysis** | A new capture+analysis module emitting its own contract, fused by the Engagement Engine as an additional factor. |
| **Multiple Students (scale)** | Already first-class via stable face IDs; tracking/identity can be strengthened independently. |
| **Attendance** | Derived from presence/identity data via a new analytics module. |
| **Cloud Storage** | A new Data Layer backend behind the existing persistence abstraction. |
| **Database (SQLite→server)** | Defined upgrade path from JSON; Data Layer abstracts the change. |
| **Teacher/Student Login** | An authentication/identity layer above Presentation; analytics scoped per user. |
| **School Analytics** | Cross-session aggregation on persisted records. |
| **AI Model Upgrade** | Swap any AI module's backend behind its contract; no downstream changes. |
| **Mobile Application** | Reuse the backend/business layers behind a new presentation client. |
| **API Integration** | Expose business-layer services through an API façade. |

---

# 24. SOFTWARE DESIGN PRINCIPLES

The backend adheres to:
- **SOLID.** Single-responsibility modules; open for extension via pluggable backends
  and additive modules; substitutable implementations behind contracts; focused
  interfaces; dependence on abstractions (contracts/config), not concretions.
- **Modular Design.** One responsibility per module; independent and testable.
- **Loose Coupling.** Modules interact only through typed contracts and configuration.
- **High Cohesion.** Related logic lives together; unrelated logic does not.
- **Scalable Architecture.** Additive growth at defined seams.
- **Reusable Components.** Shared utilities and the Graph Engine prevent duplication.
- **Professional Naming.** Clear, consistent, intention-revealing names.
- **Clean Architecture.** Strict layering with an inward dependency direction; the UI
  and frameworks are details at the edges.
- **Dependency Separation.** Configuration, utilities, and data access are isolated from
  domain logic.
- **Enterprise Standards.** Centralised logging, error handling, health/performance
  monitoring, validation, and graceful degradation throughout.

---

## END OF PART 3 — AI & BACKEND ARCHITECTURE SPECIFICATION

This part fully specifies the layered and modular backend architecture, data contracts,
data flow, camera and computer-vision pipelines, the AI and analytics engines, the
remarks/session/graph/report/settings subsystems, logging, error handling, performance,
security, scalability, and design principles for EduSense AI 360 — sufficient for an
implementer to construct the entire backend with minimal assumptions.
