# SOFTWARE REQUIREMENT SPECIFICATION (SRS)
# EduSense AI 360
## AI-Powered Smart Classroom Engagement & Teaching Quality Monitoring System

---

## PART 4 — DEVELOPMENT INSTRUCTIONS, PROJECT STRUCTURE & IMPLEMENTATION GUIDELINES

| Field | Value |
|---|---|
| Document Part | Part 4 — Development Blueprint |
| Continues From | Parts 1A, 1B, 2, 3 |
| Version | 1.0 |
| Audience | Engineering, Tech Lead, DevOps, QA, future contributors |
| Backend | Python 3.12+ · Frontend: Gradio |

### Preface

This part is the **definitive development blueprint** for EduSense AI 360. It specifies
*how* the software is to be built: the folder structure, file organisation, module
communication, configuration, coding standards, object-oriented design, error-handling
and performance practice, model and data management, logging, testing, documentation,
installation, version control, deployment, maintainability, and the final packaging
requirements. It assumes the product will mature into a commercial offering and must
therefore meet professional engineering standards from the outset.

This part contains development instructions only — no source code and no
implementation technique.

### Relationship to the Existing Scaffold

A working modular scaffold already exists (core AI/analytics/reporting modules, a
single orchestration pipeline, central configuration, and the SRS document set). This
blueprint defines the **target commercial structure** the project grows into; Section 1
states explicitly how today's scaffold maps onto it, so growth is additive and no
existing work is discarded.

---

# 1. PROJECT STRUCTURE

## 1.1 Target Directory Tree
```
edusense_ai_360/                      # repository root
├── main.py                           # application entry point (launches the app)
├── README.md                         # project overview & quick start
├── requirements.txt                  # pinned dependencies
├── LICENSE                           # license text
├── CHANGELOG.md                      # version history
├── VERSION                           # single source of the version number
├── .gitignore
├── pyproject.toml                    # packaging / tooling metadata
│
├── frontend/                         # PRESENTATION LAYER (Gradio UI only)
│   ├── __init__.py
│   ├── app_ui.py                     # assembles the Gradio shell (sidebar, tabs)
│   ├── views/                        # one module per screen
│   │   ├── dashboard_view.py
│   │   ├── live_monitor_view.py
│   │   ├── student_insights_view.py
│   │   ├── teacher_insights_view.py
│   │   ├── analytics_view.py
│   │   ├── reports_view.py
│   │   └── settings_view.py
│   ├── components/                   # reusable UI pieces (kpi_card, status_bar…)
│   ├── callbacks/                    # event handlers that call the backend façade
│   └── theme/                        # Gradio theme + custom CSS, design tokens
│
├── backend/                          # BUSINESS + AI + ANALYTICS + REPORTING
│   ├── __init__.py
│   ├── pipeline/
│   │   └── frame_pipeline.py         # single orchestration point
│   ├── camera/
│   │   ├── camera_manager.py         # device lifecycle, capture, recovery
│   │   ├── frame_buffer.py           # bounded latest-wins buffer/queue
│   │   └── frame_processor.py        # colour convert, normalise, quality gate
│   ├── ai_models/
│   │   ├── face_detection.py
│   │   ├── eye_tracking.py
│   │   ├── emotion_detection.py
│   │   └── model_registry.py         # loading, reuse, versioning, health
│   ├── analytics/
│   │   ├── engagement_engine.py
│   │   ├── attention_engine.py
│   │   ├── student_analytics.py
│   │   └── teacher_analytics.py
│   ├── remarks/
│   │   ├── remarks_engine.py         # rule arbitration & prioritisation
│   │   ├── student_remarks.py
│   │   └── teacher_remarks.py
│   ├── session/
│   │   └── session_manager.py        # lifecycle, timer, persistence, cleanup
│   ├── reporting/
│   │   ├── graph_engine.py
│   │   ├── report_engine.py
│   │   └── export_engine.py          # PDF / Excel / CSV + history & naming
│   ├── contracts/
│   │   └── models.py                 # shared typed data objects (contracts)
│   └── services/
│       ├── notification_manager.py
│       ├── health_monitor.py
│       └── performance_monitor.py
│
├── config/
│   ├── default_config.yaml           # shipped defaults (read-only baseline)
│   ├── user_config.yaml              # user overrides (created at runtime)
│   ├── config_manager.py             # holds & serves validated runtime config
│   └── settings_manager.py           # load/validate/save/reset/import/export
│
├── core/                             # CROSS-CUTTING FOUNDATIONS
│   ├── logger.py                     # categorised logging setup
│   ├── error_handler.py              # central fault containment & recovery
│   └── exceptions.py                 # application exception hierarchy
│
├── utilities/
│   ├── __init__.py
│   └── helpers.py                    # math, smoothing, validation, IO helpers
│
├── assets/
│   ├── icons/                        # outline icon set (per Part 2)
│   ├── fonts/                        # Sora, Inter, mono
│   ├── themes/                       # theme token files (dark/light)
│   └── images/                       # logo, splash, screenshots
│
├── models/                           # downloaded / cached AI model weights
│
├── data/
│   ├── sessions/                     # persisted session JSON (SQLite-ready)
│   ├── analytics/                    # cached analytics artefacts
│   └── temp/                         # transient working data
│
├── exports/                          # generated user-facing report files
│   └── reports/
│
├── logs/
│   ├── application/
│   ├── sessions/
│   ├── camera/
│   ├── ai/
│   ├── errors/
│   ├── performance/
│   └── debug/
│
├── documentation/                    # all project documents (SRS + guides)
│   ├── srs/                          # Parts 1A–4 (this document set)
│   ├── INSTALLATION.md
│   ├── USER_MANUAL.md
│   ├── DEVELOPER_GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── TROUBLESHOOTING.md
│   ├── FAQ.md
│   └── CREDITS.md
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── system/
│   ├── performance/
│   ├── fixtures/                     # sample frames, mock signals, configs
│   └── conftest.py
│
├── scripts/
│   ├── install.sh / install.bat      # environment setup
│   ├── run.sh / run.bat              # launch the app
│   └── package.sh / package.bat      # build distributable
│
└── samples/
    ├── reports/                      # sample generated reports
    ├── exports/                      # sample exports
    └── screenshots/                  # product screenshots
```

## 1.2 Folder Purposes (summary)
- **frontend/** — the Gradio presentation layer only; views, reusable components,
  callbacks, and theme. Contains no AI/analytics logic.
- **backend/** — all domain logic, grouped by concern: pipeline, camera, AI models,
  analytics, remarks, session, reporting, shared contracts, and services.
- **config/** — defaults, user overrides, and the managers that load, validate, and
  serve configuration.
- **core/** — cross-cutting foundations (logging, error handling, exception hierarchy).
- **utilities/** — domain-agnostic reusable helpers.
- **assets/** — icons, fonts, themes, images.
- **models/** — cached model weights (gitignored; populated on first run).
- **data/** — runtime persistence (sessions, analytics cache, temp).
- **exports/** — user-facing generated reports.
- **logs/** — categorised log output, one subfolder per category.
- **documentation/** — the SRS set and all guides.
- **tests/** — the full test suite by level, plus fixtures.
- **scripts/** — install, run, and packaging helpers.
- **samples/** — example outputs and screenshots for demos and onboarding.

## 1.3 Mapping From the Existing Scaffold
| Today | Target |
|---|---|
| `app.py` | `main.py` (entry) + `frontend/app_ui.py` (UI assembly) |
| `modules/face_detection.py`, `eye_tracking.py`, `emotion_detection.py` | `backend/ai_models/` |
| `modules/engagement.py` | `backend/analytics/engagement_engine.py` |
| `modules/analytics.py` | `backend/analytics/student_analytics.py` (+ session split) |
| `modules/remarks.py` | `backend/remarks/` |
| `modules/reports.py` | `backend/reporting/report_engine.py` + `export_engine.py` |
| `modules/pipeline.py` | `backend/pipeline/frame_pipeline.py` |
| dataclasses inside modules | consolidated into `backend/contracts/models.py` |
| `config.py` | `config/` (manager + default/user files) |
| `utils/helpers.py` | `utilities/helpers.py` |
| `docs/` | `documentation/srs/` |

This is a mechanical reorganisation; behaviour and contracts are preserved.

---

# 2. FILE ORGANIZATION

## 2.1 Naming Conventions
- **Modules/files:** `snake_case.py`, descriptive and singular by responsibility
  (`engagement_engine.py`, not `utils2.py`).
- **Packages/folders:** `lower_snake_case`, each with an `__init__.py`.
- **Classes:** `PascalCase` (`EngagementEngine`, `CameraManager`).
- **Functions/methods:** `snake_case`, verb-led (`compute_score`, `load_config`).
- **Variables:** `snake_case`, intention-revealing; no single letters except loop
  indices/maths.
- **Constants:** `UPPER_SNAKE_CASE`, grouped in config or a constants module.
- **Private members:** leading underscore (`_internal_state`).
- **Test files:** `test_<unit>.py`; test functions `test_<behaviour>`.

## 2.2 Module Separation
One responsibility per module; one primary class or cohesive function group per file.
UI code never contains domain logic; domain logic never imports UI. Contracts live in
one place (`backend/contracts/`) and are imported by producers and consumers alike.

## 2.3 Package Organization & Import Hierarchy
Imports flow **downward** through the layering (Part 3 §1):
`frontend → backend → (analytics/ai/reporting) → config/core/utilities/contracts`.
A lower layer must never import an upper layer. Cross-cutting `core` and `utilities`
may be imported by any layer but import nothing domain-specific themselves.

## 2.4 Dependency Rules
- **No circular dependencies.** If two modules need each other, extract the shared
  concept into a contract or utility they both depend on.
- **No duplicated logic.** Shared computation lives once (utilities, engines, graph
  engine) and is reused; copy-paste is prohibited.
- **Depend on abstractions/contracts,** not on concrete sibling internals.
- Third-party libraries are wrapped behind module interfaces so they can be swapped.

---

# 3. MODULE COMMUNICATION

## 3.1 Mechanism
Modules communicate exclusively through **explicit inputs and outputs expressed as
typed contracts** (Part 3 §3). A module receives contract objects, returns contract
objects, and shares nothing else.

| Pathway | Input | Output |
|---|---|---|
| Camera → Pipeline | capture request | validated frame |
| Pipeline → Face Detection | frame | `FaceBox[]` |
| Pipeline → Eye Tracking | frame, faces | `EyeSignals[]` |
| Pipeline → Emotion | face crop | `EmotionResult` |
| Pipeline → Engagement Engine | eye + emotion + presence | `EngagementResult` |
| Pipeline → Remarks | engagement | remark text |
| Pipeline → Frontend | `FrameResult` (+ annotated frame) | rendered UI |
| Analytics → Report Engine | `SessionSummary`, time-series | report artefact |

## 3.2 Interfaces & Shared Objects
- **Interfaces:** each engine/module exposes a small, stable public method set (e.g.
  `process(frame) -> FrameResult`, `score_face(...) -> EngagementResult`). Internals are
  private.
- **Shared objects:** only the contracts in `backend/contracts/`. No shared mutable
  globals.

## 3.3 State Management
- **AI Processing modules are stateless per frame** (except small smoothing buffers
  internal to a module).
- **Session/analytics state** is owned solely by the Session Manager and analytics
  engines and is never reached into directly by other modules.
- **Configuration state** is owned by the Configuration Manager and read-only to
  consumers.

## 3.4 Dependency Direction, Coupling, Cohesion
Dependencies point inward/downward (Clean Architecture). Coupling is loose (contracts +
config only); cohesion is high (each module does one thing). The **Frame Pipeline** is
the only component aware of the full module composition.

---

# 4. CONFIGURATION MANAGEMENT

## 4.1 Configuration Sources (precedence: later overrides earlier)
1. **Default Configuration** — shipped `config/default_config.yaml`, the read-only
   baseline.
2. **User Configuration** — `config/user_config.yaml`, created from the Settings page,
   overriding defaults.
3. **Environment Variables** — optional overrides for deployment-specific values (e.g.
   paths, verbosity), highest precedence.

## 4.2 Configuration Domains
Camera (device, resolution, FPS), Dashboard (visible cards, refresh, density, theme),
Analytics (weights, band boundaries, smoothing window), AI Thresholds (detection
confidence, EAR, gaze tolerance, distraction, prolonged-inattention), Logging (level,
retention, rotation), and Report (default format, export location).

## 4.3 Loading & Validation
- On startup the **Configuration Manager** loads defaults, merges user config, applies
  environment overrides, **validates every value** against its permitted range/set, and
  exposes a single immutable runtime configuration.
- Invalid values are rejected with a clear message; the prior valid (or default) value
  is retained and the event logged.
- A corrupt/missing user config falls back to defaults without failing startup.
- Runtime-applicable changes take effect immediately; others indicate a restart.

---

# 5. CODING STANDARDS

## 5.1 Style Guide
Follow **PEP 8** layout and **PEP 257** docstrings; format with an automatic formatter
(e.g. Black) and lint (e.g. Ruff/flake8). Maximum line length and import ordering are
enforced by tooling so style is never debated in review.

## 5.2 Naming
As in §2.1 — PascalCase classes, snake_case functions/variables, UPPER_SNAKE constants.

## 5.3 File Headers & Module Documentation
Every module begins with a header docstring stating its purpose, its place in the
architecture, and its key inputs/outputs. Public classes and functions carry docstrings
describing behaviour, parameters, returns, and raised exceptions.

## 5.4 Comments & Docstrings
- **Docstrings** explain *what* and *why* (intent, contracts, edge cases).
- **Inline comments** are reserved for non-obvious reasoning, not narration of obvious
  code.
- Comments are kept current with the code they describe.

## 5.5 Type Hints
All public functions, methods, and contracts are fully **type-hinted**. Hints are
treated as part of the interface and are checked (e.g. mypy/pyright) in CI when adopted.

## 5.6 Readability & Maintainability
Small functions, single level of abstraction per function, early returns over deep
nesting, intention-revealing names, and no magic numbers (use named config/constants).
Code is optimised for the next reader, not for cleverness.

---

# 6. OBJECT-ORIENTED DESIGN

## 6.1 Classes & Responsibilities
Each engine/manager is a class with one clear responsibility and a small public
surface. Data is modelled as immutable contract objects (dataclasses).

## 6.2 Inheritance vs Composition
**Favour composition over inheritance.** Inheritance is used only for genuine
"is-a" relationships (e.g. a base detector interface with concrete backends). Engines
*compose* collaborators (the Pipeline composes detectors and the engagement engine)
rather than inheriting them.

## 6.3 Interfaces & Abstraction
Pluggable concerns (emotion backend, storage backend, export format) sit behind small
abstract interfaces so implementations are interchangeable. Consumers depend on the
interface, not the concrete class.

## 6.4 Encapsulation
Internal state is private; access is via methods/properties. Modules expose intent, not
internals.

## 6.5 Single Responsibility & Dependency Injection
Each class changes for one reason only. Collaborators (config, logger, backends) are
**injected** (passed in) where it aids testability and decoupling, rather than
hard-constructed deep inside a class. This lets tests substitute fakes easily.

---

# 7. ERROR-HANDLING STRATEGY

## 7.1 Exception Hierarchy
A single application base exception (e.g. `EduSenseError`) with specific subclasses:
`CameraError`, `FrameError`, `ModelError`, `AnalyticsError`, `ReportError`,
`ConfigError`. Modules raise specific exceptions; the central Error Handler catches and
classifies them.

## 7.2 Practices
- **Recovery mechanisms** and **fallback behaviour** per condition (Part 3 §20).
- **Graceful degradation:** neutral defaults over failure.
- **Retry mechanisms:** bounded retries with backoff (camera reconnect).
- **Safe shutdown:** release camera/models, flush logs, persist session data on exit
  (including unexpected termination).
- **Logging:** every handled error logged with context and severity.
- **User notifications:** faults surface as clear, non-technical messages while details
  go to logs.
- Exceptions are caught at **module and pipeline boundaries**, never swallowed
  silently.

---

# 8. PERFORMANCE GUIDELINES

- **Efficient memory:** reuse buffers, avoid per-frame allocations where possible,
  bound queues, release large objects promptly; no unbounded growth.
- **Efficient CPU:** analyse at a sensible resolution; skip frames under load;
  short-circuit when no face is present.
- **Frame & processing optimisation:** downscale for detection, latest-wins buffering,
  avoid redundant colour conversions.
- **Caching:** cache loaded models and reusable computations; cache analytics artefacts
  where valid.
- **Lazy loading:** load models and heavy resources on first use, not at import.
- **Parallel execution where appropriate:** decouple capture, analysis, and UI; run
  independent per-face analyses concurrently when beneficial.
- **Thread safety:** protect shared structures (frame buffer, session state) with
  appropriate synchronisation; keep shared mutable state minimal.
- **Resource cleanup:** deterministic release of camera, models, file handles, and
  threads on stop/shutdown.

---

# 9. AI MODEL MANAGEMENT

A dedicated **Model Registry** (`backend/ai_models/model_registry.py`) governs models:
- **Model Loading & Initialization:** lazy, once, cached for reuse across frames and
  sessions.
- **Model Reuse:** a single loaded instance per backend serves all requests.
- **Prediction Pipeline:** uniform preprocess → infer → postprocess path per model.
- **Confidence Thresholds:** sourced from configuration; low-confidence handling per
  Part 3.
- **Model Health Checking:** verify a model loaded and responds; expose health to the
  Health Monitor.
- **Model Failure Recovery:** degrade the affected capability to a safe default; keep
  the rest of the pipeline running.
- **Future Model Replacement:** new backends drop in behind the existing interface with
  no downstream change.
- **Model Versioning:** record model identity/version in session metadata and logs for
  reproducibility.

---

# 10. DATA MANAGEMENT

- **Temporary Data:** scratch artefacts in `data/temp/`, cleared on session end/startup.
- **Session Data:** authored by the Session Manager; persisted to `data/sessions/`
  (JSON; SQLite-ready) as summary + time-series.
- **Historical Data:** retained sessions enabling cross-session analytics later.
- **Analytics Data:** cached aggregates in `data/analytics/`.
- **Export Data:** finished reports in `exports/`.
- **Cleanup Rules:** temp cleared routinely; configurable pruning of old
  sessions/exports.
- **Retention:** configurable retention windows per data class.
- **Data Validation:** validate on read and write; reject malformed records and log;
  never corrupt the running session on a bad record.

---

# 11. GRAPH MANAGEMENT

- **Graph Architecture:** a single **Graph Engine** produces figure data consumed by
  both dashboard and reports (no duplicate charting).
- **Graph Updates & Real-time Refresh:** live charts append points smoothly at the
  configured refresh cadence without full redraws.
- **Performance Optimisation:** cap retained live points, downsample long series for
  display, throttle redraws.
- **Chart Components:** reusable definitions per chart type with the Part 2 styling
  (colours, legends, axes, tooltips, animation).
- **History Management:** completed-session series available for historical views.
- **Export Support:** charts exportable as images/data and embeddable in reports.

---

# 12. REPORT MANAGEMENT

- **Report Templates:** consistent layouts for PDF/Excel/CSV defined once and reused.
- **Report Storage:** `exports/reports/`.
- **Naming Rules:** deterministic, collision-resistant (`<session_id>_<type>_<timestamp>`).
- **Export Locations:** default under `exports/`; user-configurable and validated as
  writable.
- **History:** track generated files (name, date, format, size) for the Reports panel.
- **File Validation:** verify a report was written and is well-formed; report failures
  clearly.
- **Cleanup & Versioning:** configurable pruning; regenerated reports versioned by
  timestamp rather than overwriting.

---

# 13. LOGGING ARCHITECTURE

## 13.1 Log Folders & Categories
`logs/` contains: `application/`, `sessions/`, `camera/`, `ai/`, `errors/`,
`performance/`, `debug/`. Warnings are recorded within the relevant category at WARNING
level.

## 13.2 Behaviour
- Each entry is timestamped and severity-tagged (DEBUG/INFO/WARNING/ERROR/CRITICAL).
- Logging is **non-blocking** and must never crash or stall analysis.
- Verbosity is configuration-driven.

## 13.3 Retention & Rotation
- **Rotation:** size- and/or time-based per log file to bound disk usage.
- **Retention Policy:** keep a configurable number of rotated files per category; prune
  the rest.
- Logs are structured to permit future remote aggregation.

---

# 14. TESTING STRATEGY

## 14.1 Levels
- **Unit Testing:** each engine/utility in isolation with mock contracts (e.g.
  engagement scoring, EAR/gaze maths, remark rule selection, analytics aggregation,
  config validation). No camera/model needed.
- **Integration Testing:** module groups together (pipeline + engines; analytics +
  reporting) using fixture frames and mock detector outputs.
- **System Testing:** the full application against recorded/synthetic input.
- **UI Testing:** dashboard flows — start/stop, navigation, export, settings.
- **Camera Testing:** initialisation, switching, disconnect/recovery (with a real or
  virtual camera).
- **Performance Testing:** FPS, per-frame time, memory/CPU against Part 3 budgets.
- **Stress Testing:** many faces, prolonged sessions, rapid start/stop, low resources.
- **Regression Testing:** a maintained suite re-run on every change to prevent
  re-breakage.
- **Acceptance Testing:** validate against the Part 1B functional requirements
  (traceable via `FR-XX-NNN`).
- **Manual Testing:** exploratory checks of real classroom feel and edge cases.
- **Future Automated Testing:** CI runs unit/integration/regression on every commit;
  coverage gates enforced.

## 14.2 Success Criteria
- Unit + integration pass on every commit; defined **coverage threshold** met for core
  engines.
- Performance tests within Part 3 budgets on reference hardware.
- All Part 1B acceptance requirements demonstrably satisfied.
- No known critical/major defects open at release.

## 14.3 Fixtures
`tests/fixtures/` holds sample frames, mock signal sets, and test configurations so the
non-CV logic is fully testable without hardware (as already demonstrated by the
scaffold's smoke test of the engine → analytics → reports path).

---

# 15. PROJECT DOCUMENTATION

| Document | Purpose |
|---|---|
| **README** | Overview, features, quick start, structure map. |
| **Installation Guide** | Step-by-step environment setup and run instructions. |
| **User Manual** | How to operate the app: sessions, dashboard, reports, settings. |
| **Developer Guide** | Architecture orientation, conventions, how to add a module. |
| **Architecture Guide** | The layered/modular design and contracts (links to SRS Part 3). |
| **API Documentation** | Public interfaces of backend modules/engines (and any future REST API). |
| **Troubleshooting Guide** | Common problems (camera, lighting, performance) and fixes. |
| **FAQ** | Frequent questions for users and evaluators. |
| **Changelog** | Versioned record of changes (Keep a Changelog style). |
| **License** | Legal terms of use. |
| **Credits** | Acknowledgements of libraries, models, and contributors. |

The full SRS (Parts 1A–4) lives under `documentation/srs/` as the authoritative
specification.

---

# 16. INSTALLATION REQUIREMENTS

- **Python Version:** 3.12 or later.
- **Package Manager:** `pip` (within a virtual environment); `requirements.txt` pins
  versions.
- **Required Libraries:** Gradio (UI); OpenCV (vision); MediaPipe (face/landmarks/iris);
  FER or DeepFace (emotion); NumPy, Pandas (data); Plotly (graphs); ReportLab, OpenPyXL
  (reports). CSV via the standard library.
- **Installation Order:** create and activate a virtual environment → upgrade pip →
  install from `requirements.txt`. First run may download model weights into `models/`.
- **Dependency Validation:** on startup the app checks for required libraries and clearly
  reports any that are missing, disabling only the affected features.
- **Environment Setup:** `scripts/install.*` automates venv creation and installation;
  `scripts/run.*` launches the app.
- **Operating System Support:** Windows (primary); macOS and Linux supported where the
  dependencies are available.
- **Hardware Compatibility:** a standard laptop with an external USB webcam; CPU-first,
  no GPU required (GPU optional for acceleration).

---

# 17. VERSION CONTROL

- **Repository:** Git, with the structure of §1 and a comprehensive `.gitignore`
  (exclude `models/` weights, `logs/`, `data/`, `exports/`, virtual env, caches).
- **Branch Strategy:** `main` (stable/released), `develop` (integration),
  `feature/<name>`, `release/<version>`, `hotfix/<name>`.
- **Commit Standards:** **Conventional Commits** (`feat:`, `fix:`, `docs:`, `refactor:`,
  `test:`, `chore:`), imperative, scoped, small and focused.
- **Version Numbers:** **Semantic Versioning** `MAJOR.MINOR.PATCH`, sourced from the
  `VERSION` file and surfaced in the UI/About.
- **Release Notes:** summarised per release in `CHANGELOG.md`.
- **Tags:** annotated tags per release (`v1.0.0`).
- **Milestones:** track scope per release (e.g. v1.1 attendance, v1.2 database).
- **Future Releases:** the roadmap (§19) maps to milestones.

---

# 18. DEPLOYMENT

- **Local Installation:** clone/extract → install dependencies → run (`scripts/run.*`).
- **Executable Packaging:** a single-file/folder build (e.g. PyInstaller) so non-technical
  users can run without a Python setup; bundles assets and pins the model strategy.
- **Portable Version:** a self-contained folder runnable without installation, with
  config/data kept relative to the app.
- **Future Cloud Deployment:** the backend/business layers, being UI-agnostic, can be
  served behind an API for browser/cloud use.
- **Future School Deployment:** multi-machine/classroom rollout with centralised config
  and reporting.
- **Automatic Updates:** a future updater checks the version, fetches releases, and
  applies them safely with rollback.

---

# 19. MAINTAINABILITY & FUTURE EXPANSION

## 19.1 Maintainability
Readable layered architecture, reusable modules, clear documentation, simple
file-based configuration, modular expansion at defined seams, low technical debt
(enforced by linting/formatting/tests), and a professional, predictable folder layout
mean a new developer can orient quickly and contribute safely.

## 19.2 Future Expansion (attach at defined seams)
Attendance · Multiple Cameras · Voice Recognition / Speech Analysis · Classroom
Heatmaps · Database (SQLite→server) · Cloud Storage · Student Login · Teacher Login ·
School Administrator Portal · AI Recommendations · Mobile App · REST API. Each attaches
via a new module/contract, a new Data Layer backend, an auth layer, or an API façade —
without rewriting existing modules (see Part 3 §23).

---

# 20. DEVELOPMENT PRINCIPLES

The project upholds: Professional Enterprise Standards · Clean Code · **SOLID** ·
**DRY** (no duplicated logic) · **KISS** (simplest solution that works) · **YAGNI**
(build what the spec needs, leave clean seams for the rest) · Separation of Concerns ·
Scalable Design · Reusable Components · Maintainable Code · Production-Level Quality.

---

# 21. FINAL SOFTWARE PACKAGE REQUIREMENTS

The completed deliverable shall include: the complete project folder; all Python source
(frontend + backend); configuration files; assets, icons, fonts, themes; documentation
(SRS + all guides); `requirements.txt`; `README`; `LICENSE`; test files; installation,
user, and developer guides; sample reports and exports; project screenshots; and
version information — all professionally packaged.

**Acceptance:** the project shall be organised so that a user only needs to **install
dependencies and run the application** (`scripts/install.*` then `scripts/run.*`, or
`pip install -r requirements.txt` then `python main.py`). Defaults shall be sensible,
first-run shall be smooth, and the application shall start, monitor, analyse, and export
without further configuration.

---

## END OF PART 4 — DEVELOPMENT INSTRUCTIONS, PROJECT STRUCTURE & IMPLEMENTATION GUIDELINES

This part defines the definitive development blueprint — structure, conventions,
communication, configuration, standards, OOP, error handling, performance, model/data
management, logging, testing, documentation, installation, version control, deployment,
maintainability, principles, and final packaging — sufficient to generate the complete,
professional EduSense AI 360 software package.
