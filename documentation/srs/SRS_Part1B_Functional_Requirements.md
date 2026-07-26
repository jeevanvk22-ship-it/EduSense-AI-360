# SOFTWARE REQUIREMENT SPECIFICATION (SRS)
# EduSense AI 360
## AI-Powered Smart Classroom Engagement & Teaching Quality Monitoring System

---

## PART 1B — FUNCTIONAL REQUIREMENTS SPECIFICATION

| Field | Value |
|---|---|
| Document Part | Part 1B — Functional Requirements |
| Continues From | Part 1A — Project Overview |
| Version | 1.0 |
| Project Type | AI + Deep Learning + Computer Vision + Educational Analytics |
| Platform | Desktop Software |
| Frontend | Gradio |
| Backend | Python 3.12+ |
| Hardware | Laptop + External USB Webcam only |
| Excluded Hardware | Arduino, Raspberry Pi, IoT devices, sensors, wearables |

### Preface to Part 1B

Part 1A established the project vision, scope, stakeholders, technology stack, and
high-level deliverables. Part 1B specifies the **functional requirements** of every
software module in exhaustive detail. Each module is described through a fixed
ten-part template — Purpose, Inputs, Outputs, Processing, User Interaction,
Functional Flow, Validation Rules, Expected Behaviour, Error Handling, and Future
Scalability — so that the specification is unambiguous and directly buildable.

Each functional requirement carries a unique identifier of the form
**FR-XX-NNN** (e.g. `FR-WC-001`) to support traceability between specification,
implementation, and testing. This document contains requirements only; it
contains no source code and prescribes no implementation.

### Conventions

- **Shall** denotes a mandatory requirement.
- **Should** denotes a recommended requirement.
- **May** denotes an optional capability.
- Module identifier prefixes: `WC` Webcam, `FD` Face Detection, `ET` Eye Tracking,
  `EM` Emotion Detection, `EN` Engagement Engine, `SA` Student Analytics,
  `TA` Teacher Analytics, `SR` Student Remarks, `TR` Teacher Remarks,
  `DB` Dashboard, `AN` Analytics, `RP` Reporting, `ST` Settings, `LG` Logging,
  `EH` Error Handling, `PF` Performance.

---

# SECTION 1 — WEBCAM MODULE

**Requirement Prefix:** `FR-WC`

## 1.1 Purpose
The Webcam Module shall acquire a continuous live video stream from an external
USB webcam connected to the host laptop and make individual frames available to
the rest of the system. It is the single source of all visual input and shall
abstract all camera hardware concerns away from downstream modules.

## 1.2 Inputs
- A connected external USB webcam (one or more devices).
- Camera selection index supplied by the Settings Module.
- Desired capture resolution and frame rate from the Settings Module.
- Start, stop, and switch-camera commands from the Dashboard.

## 1.3 Outputs
- A live sequence of image frames in a defined colour space, delivered at the
  configured frame rate.
- A camera status indicator (e.g. *Disconnected, Initialising, Streaming, Error*).
- Measured live frame rate (FPS).
- The active device index and its reported resolution.

## 1.4 Processing
- **FR-WC-001** The module shall enumerate available camera devices and expose a
  selectable list to the Settings Module.
- **FR-WC-002** The module shall initialise the selected device, request the
  configured resolution, and fall back to the nearest supported resolution if the
  request is unsupported.
- **FR-WC-003** The module shall capture frames continuously in a non-blocking
  manner so that the user interface remains responsive.
- **FR-WC-004** The module shall measure and expose the actual achieved FPS over a
  rolling window.
- **FR-WC-005** The module shall support switching to a different camera device at
  runtime without restarting the application.

## 1.5 User Interaction
- The user selects the active camera from a dropdown.
- The user starts and stops the live stream.
- The user observes camera status and live FPS on the dashboard.

## 1.6 Functional Flow
1. On start, enumerate devices and present them for selection.
2. Initialise the selected device with the configured resolution and FPS.
3. Begin continuous frame capture.
4. Publish each frame and the current status to subscribers (Face Detection,
   Dashboard).
5. On stop, release the device cleanly and set status to *Disconnected*.

## 1.7 Validation Rules
- **FR-WC-006** The module shall verify that at least one camera device is present
  before attempting initialisation.
- **FR-WC-007** Requested resolution and FPS shall be validated against device
  capabilities; invalid values shall be replaced by the nearest valid value and a
  warning logged.
- **FR-WC-008** A captured frame shall be validated as non-empty and of the
  expected dimensions before being published.

## 1.8 Expected Behaviour
The stream shall appear smooth and synchronised with real-world events. Status
shall always reflect the true device state. Switching cameras shall take effect
within a short, bounded time and shall not crash the application.

## 1.9 Error Handling
- **FR-WC-009** If no camera is detected, the module shall report *No camera found*
  and prompt the user to connect a device.
- **FR-WC-010** If the camera disconnects mid-session, the module shall detect the
  loss, set status to *Disconnected*, pause analysis, and attempt automatic
  reconnection at a bounded retry interval.
- **FR-WC-011** On successful reconnection, streaming and analysis shall resume
  automatically without data loss to the already-recorded session.
- **FR-WC-012** Repeated failed frame reads beyond a threshold shall trigger a
  graceful error state rather than a crash.

## 1.10 Future Scalability
The module shall be designed to support, in future, multiple simultaneous cameras
(multi-angle classrooms), IP/RTSP camera sources, and configurable hardware
acceleration, without changes to downstream modules.

---

# SECTION 2 — FACE DETECTION MODULE

**Requirement Prefix:** `FR-FD`

## 2.1 Purpose
The Face Detection Module shall locate all student faces present in each incoming
frame using MediaPipe, and shall maintain stable identities for tracked faces so
that per-student analytics remain consistent across frames.

## 2.2 Inputs
- A single video frame from the Webcam Module.
- Minimum detection-confidence threshold from the Settings Module.
- Maximum number of faces to track from the Settings Module.

## 2.3 Outputs
- A list of detected faces, each with a bounding region, a confidence value, and a
  stable tracking identifier.
- A count of currently visible faces.
- A per-face visibility flag.

## 2.4 Processing
- **FR-FD-001** The module shall detect faces using MediaPipe face detection.
- **FR-FD-002** The module shall support multiple faces in a single frame, up to a
  configurable maximum.
- **FR-FD-003** The module shall assign and maintain a stable identifier for each
  face across frames using positional association (centroid/overlap based), so the
  same student retains the same identity for the duration of their visibility.
- **FR-FD-004** The module shall discard detections below the configured confidence
  threshold.
- **FR-FD-005** The module shall detect face loss when a previously tracked face is
  absent for a defined number of consecutive frames.
- **FR-FD-006** The module shall support face reacquisition: a face reappearing in a
  similar position within a grace period shall, where possible, be matched to its
  prior identity.

## 2.5 User Interaction
The user does not interact with this module directly. Detected face overlays
(boxes, identifiers, engagement colour) are rendered on the dashboard video.

## 2.6 Functional Flow
1. Receive a frame.
2. Run face detection.
3. Filter detections by confidence.
4. Associate detections with existing tracked identities.
5. Mark unmatched existing identities as lost; create identities for new faces.
6. Publish the tracked face list to the Eye Tracking, Emotion, and Engagement
   modules.

## 2.7 Validation Rules
- **FR-FD-007** Confidence threshold shall lie within a valid range; out-of-range
  values shall be clamped and logged.
- **FR-FD-008** Bounding regions shall be clamped to frame boundaries before being
  used to crop sub-images.
- **FR-FD-009** The number of tracked faces shall never exceed the configured
  maximum.

## 2.8 Expected Behaviour
Faces shall be detected reliably under normal classroom lighting and framing.
Tracking identifiers shall remain stable while a student is continuously visible.
Brief occlusions shall not permanently reset a student's identity.

## 2.9 Error Handling
- **FR-FD-010** If no face is detected, the module shall report a *No face detected*
  condition and downstream per-student analysis shall be skipped for that frame.
- **FR-FD-011** If the detector fails or raises an internal error, the module shall
  log the error, skip the frame, and continue with the next frame.
- **FR-FD-012** Sustained absence of any face shall be surfaced to the Dashboard and
  Logging modules as a warning.

## 2.10 Future Scalability
The detection backend shall be replaceable (e.g. alternative detectors or models)
behind the same output contract. Future versions may add re-identification across
sessions and seating-position mapping.

---

# SECTION 3 — EYE TRACKING MODULE

**Requirement Prefix:** `FR-ET`

## 3.1 Purpose
The Eye Tracking Module shall analyse each tracked face to estimate eye state, gaze
direction, drowsiness, and an overall per-student attention level, using facial
landmark geometry (MediaPipe FaceMesh with iris refinement).

## 3.2 Inputs
- A video frame and the list of tracked faces from Face Detection.
- Eye-openness, gaze-tolerance, and head-pose thresholds from the Settings Module.

## 3.3 Outputs
For each tracked face:
- Eye-openness state (open / closed).
- Eye Aspect Ratio value.
- Blink event indication.
- Gaze direction classification (centre / left / right / up / down).
- Sleeping / long-eye-closure indication.
- An attention estimate in the range 0–1.
- A confidence score for the attention estimate.

## 3.4 Processing
- **FR-ET-001** The module shall extract eye landmarks for each face.
- **FR-ET-002** The module shall compute eye openness using the Eye Aspect Ratio and
  classify eyes as open or closed against the configured threshold.
- **FR-ET-003** The module shall detect blinks as brief transitions from open to
  closed to open.
- **FR-ET-004** The module shall estimate gaze direction (left, right, up, down,
  centre) from iris position relative to the eye region and from head orientation.
- **FR-ET-005** The module shall detect sleeping behaviour via sustained eye closure
  beyond a configurable duration (long eye-closure detection).
- **FR-ET-006** The module shall combine eye openness, gaze-on-target, and forward
  head orientation into a single attention estimate.
- **FR-ET-007** The module shall produce a confidence score reflecting landmark
  quality and face visibility.

## 3.5 User Interaction
The user does not interact directly. Attention and gaze state may be visualised on
the dashboard per student.

## 3.6 Functional Flow
1. Receive frame and tracked faces.
2. For each face, extract landmarks.
3. Compute eye openness, blink state, gaze direction, and head orientation.
4. Detect long eye closure / sleeping.
5. Compute attention estimate and confidence.
6. Publish per-face eye signals to the Engagement Engine.

## 3.7 Validation Rules
- **FR-ET-008** Landmark sets shall be validated as complete before computation; an
  incomplete set shall yield a low-confidence neutral result rather than an error.
- **FR-ET-009** Thresholds shall be validated and clamped to sensible ranges.
- **FR-ET-010** Attention output shall always lie within 0–1.

## 3.8 Expected Behaviour
Attention shall fall when the student closes their eyes, looks away from the board,
or turns their head away, and shall rise when the student faces forward with open
eyes and centred gaze. Momentary blinks shall not be misclassified as inattention.

## 3.9 Error Handling
- **FR-ET-011** If landmarks cannot be obtained for a face, the module shall return a
  low-confidence neutral attention value and continue.
- **FR-ET-012** Transient landmark noise shall be smoothed so that single-frame
  glitches do not produce spurious sleeping/blink events.

## 3.10 Future Scalability
Future versions may add calibrated per-student gaze mapping, screen/board region
targeting, and fatigue trend analysis over time.

---

# SECTION 4 — EMOTION DETECTION MODULE

**Requirement Prefix:** `FR-EM`

## 4.1 Purpose
The Emotion Detection Module shall classify the facial emotion of each tracked face
and shall provide a stable, confidence-weighted emotion signal to the Engagement
Engine and analytics modules.

## 4.2 Inputs
- A face sub-image (crop) for each tracked face.
- Emotion-confidence threshold and frame-averaging window from the Settings Module.
- Selected emotion backend (default lightweight model; heavier model optional).

## 4.3 Outputs
For each tracked face:
- A dominant emotion label from the supported set.
- Per-emotion probability scores.
- A detection confidence value.
- A derived engagement contribution mapped from the emotion.

### Supported Emotion Categories
Happy, Neutral, Sad, Angry, Fear, Surprise. A **Confused** state may be derived
from combinations of negative low-arousal emotions (e.g. sustained sad/fear with
low attention) where required.

## 4.4 Processing
- **FR-EM-001** The module shall preprocess each face crop (sizing and normalisation)
  prior to prediction.
- **FR-EM-002** The module shall predict emotion probabilities and select the
  dominant emotion.
- **FR-EM-003** The module shall produce a confidence score for each prediction.
- **FR-EM-004** Predictions below the confidence threshold shall be treated as
  low-confidence and shall default toward a neutral classification.
- **FR-EM-005** The module shall handle unknown or undetectable emotion by returning
  a neutral result flagged as low confidence rather than failing.
- **FR-EM-006** The module shall average predictions across a configurable number of
  recent frames per student to produce a stable emotion output and suppress flicker.

## 4.5 User Interaction
The current dominant emotion is displayed on the dashboard. The user does not
interact with prediction directly.

## 4.6 Functional Flow
1. Receive a face crop.
2. Preprocess the crop.
3. Predict emotion probabilities and confidence.
4. Apply low-confidence and unknown handling.
5. Apply multi-frame averaging for stability.
6. Map the stabilised emotion to an engagement contribution and publish.

## 4.7 Validation Rules
- **FR-EM-007** Empty or zero-size crops shall be rejected and yield a neutral
  low-confidence result.
- **FR-EM-008** Probability scores shall be normalised so that they form a valid
  distribution.
- **FR-EM-009** The engagement contribution mapping shall remain within its defined
  bounds.

## 4.8 Expected Behaviour
Emotion output shall be stable under normal conditions and shall not oscillate
rapidly between labels frame to frame. Positive emotions shall raise engagement and
negative emotions shall lower it, per the configured mapping.

## 4.9 Error Handling
- **FR-EM-010** If the emotion backend is unavailable or fails to load, the module
  shall degrade gracefully to a neutral output and log the condition, allowing the
  rest of the pipeline to continue.
- **FR-EM-011** Per-frame prediction errors shall be caught and shall not interrupt
  the stream.

## 4.10 Future Scalability
The backend shall be pluggable. Future versions may add a dedicated confusion
classifier, micro-expression analysis, and culturally calibrated emotion models.

---

# SECTION 5 — STUDENT ENGAGEMENT ENGINE

**Requirement Prefix:** `FR-EN`

## 5.1 Purpose
The Student Engagement Engine shall compute a quantitative engagement measure for
each student per frame by fusing attention, emotion, face visibility, session
duration, and continuity of focus into a single interpretable score and level.

## 5.2 Inputs
Per student, per frame:
- Attention estimate (from Eye Tracking).
- Emotion engagement contribution (from Emotion Detection).
- Face visibility / presence (from Face Detection).
- Session duration and continuous-focus history (from internal state).
- Configurable factor weights and level bands (from Settings).

## 5.3 Outputs
Per student, per frame:
- **Engagement percentage** (0–100).
- **Engagement level** (categorical band).
- **Confidence score** for the engagement estimate.
- Distraction flag and prolonged-inattention flag.

### Engagement Level Bands
| Range | Level |
|---|---|
| 0–30 | Poor |
| 31–60 | Average |
| 61–80 | Good |
| 81–100 | Excellent |

> Band boundaries shall be configurable so institutions may calibrate them.

## 5.4 Processing (Conceptual)
The engagement percentage shall be a weighted combination of contributing factors,
each normalised to a common 0–1 scale before weighting:

- **Eye attention** — the primary driver: open eyes, centred gaze, and forward head
  orientation increase engagement.
- **Emotion** — the emotion contribution shifts the score upward for positive,
  learning-oriented affect and downward for frustration, confusion, or boredom.
- **Face visibility** — a face that is reliably present contributes positively; an
  absent or poorly visible face reduces the score and confidence.
- **Session duration** — used as context to interpret sustained patterns (for
  example, distinguishing a brief dip from prolonged decline).
- **Continuous focus** — sustained attention over consecutive frames is rewarded,
  while repeated distraction reduces the score.

- **FR-EN-001** The engine shall normalise each factor to 0–1 before combining.
- **FR-EN-002** The engine shall combine factors using configurable weights that sum
  to one, producing a 0–100 percentage.
- **FR-EN-003** The engine shall map the percentage to an engagement level using the
  configured bands.
- **FR-EN-004** The engine shall compute a confidence score derived from the
  confidence of its input signals and face visibility.
- **FR-EN-005** The engine shall flag distraction when the score falls below a
  configurable distraction threshold.
- **FR-EN-006** The engine shall flag prolonged inattention when distraction persists
  beyond a configurable duration, per student.
- **FR-EN-007** The engine shall apply temporal smoothing so the live score is stable
  rather than jittery.

## 5.5 User Interaction
The current engagement percentage and level are displayed prominently on the
dashboard. Thresholds and weights are adjustable via Settings.

## 5.6 Functional Flow
1. Gather per-student attention, emotion, and presence signals.
2. Normalise and weight each factor.
3. Compute the engagement percentage.
4. Map to an engagement level and compute confidence.
5. Update distraction and prolonged-inattention state.
6. Apply smoothing and publish to analytics, remarks, and dashboard.

## 5.7 Validation Rules
- **FR-EN-008** Factor weights shall be validated to sum to one; if not, they shall be
  normalised and the condition logged.
- **FR-EN-009** Output percentage shall always lie within 0–100 and level within the
  defined set.
- **FR-EN-010** Band boundaries shall be validated as monotonic and non-overlapping.

## 5.8 Expected Behaviour
The score shall track intuitively with observed behaviour: an attentive, positive,
clearly visible student trends toward Good/Excellent, while a distracted, absent, or
frustrated student trends toward Poor/Average. The score shall not swing wildly
between consecutive frames.

## 5.9 Error Handling
- **FR-EN-011** Missing input signals shall be substituted with neutral defaults and
  shall reduce the confidence score rather than cause failure.
- **FR-EN-012** Division or normalisation edge cases shall be guarded against.

## 5.10 Future Scalability
Future versions may introduce per-student baselines, adaptive weighting learned from
historical data, and subject- or activity-specific engagement profiles.

---

# SECTION 6 — STUDENT ANALYTICS MODULE

**Requirement Prefix:** `FR-SA`

## 6.1 Purpose
The Student Analytics Module shall aggregate per-student engagement data across a
session into meaningful summary metrics and trends.

## 6.2 Inputs
- Per-student per-frame engagement, attention, distraction flags, and emotion labels.
- Session timing information.

## 6.3 Outputs
Per student:
- Total attentive time.
- Total distracted time.
- Emotion distribution (proportion of time per emotion).
- Average engagement.
- Session engagement summary.
- Overall performance classification.
- Identified trends (e.g. improving, declining, stable).

## 6.4 Processing
- **FR-SA-001** The module shall accumulate attentive versus distracted time using the
  distraction flag over the session.
- **FR-SA-002** The module shall compute the distribution of detected emotions over
  the session.
- **FR-SA-003** The module shall compute average and summary engagement statistics.
- **FR-SA-004** The module shall classify overall performance using the engagement
  level bands.
- **FR-SA-005** The module shall identify trends by comparing engagement across
  successive portions of the session.

## 6.5 User Interaction
Students' analytics are shown on the dashboard analytics cards and contribute to the
session report. The user may refresh analytics on demand.

## 6.6 Functional Flow
1. Continuously receive per-student frame results.
2. Update running totals and distributions.
3. On request or session end, compute summaries and trends.
4. Publish to dashboard, remarks generator, and reporting.

## 6.7 Validation Rules
- **FR-SA-006** Time accumulations shall be consistent with elapsed session time.
- **FR-SA-007** Distributions shall sum to a valid total (100% where expressed as a
  proportion).
- **FR-SA-008** Trend classification shall require a minimum amount of data before
  reporting, otherwise it shall report *insufficient data*.

## 6.8 Expected Behaviour
Metrics shall reflect observed behaviour accurately and update consistently as the
session progresses.

## 6.9 Error Handling
- **FR-SA-009** Gaps caused by missing frames or lost faces shall be handled without
  corrupting totals.
- **FR-SA-010** Empty sessions shall yield clearly marked empty analytics, not errors.

## 6.10 Future Scalability
Future versions may persist per-student history across multiple sessions to track
long-term progress and learning patterns.

---

# SECTION 7 — TEACHER ANALYTICS MODULE

**Requirement Prefix:** `FR-TA`

## 7.1 Purpose
The Teacher Analytics Module shall analyse **classroom-level engagement patterns**
and produce constructive, supportive insights. It is explicitly **not** a teacher
evaluation or scoring system and shall never judge teaching ability.

## 7.2 Inputs
- Classroom-aggregate engagement over time.
- Participation (faces present) over time.
- Emotion distribution over time.
- Session timing and activity markers where available.

## 7.3 Outputs
- A set of natural-language classroom insights, for example:
  - "Attention dropped after 20 minutes."
  - "Students responded better during interactive explanation."
  - "Students appeared distracted during continuous lecture."
- Supporting summary statistics for each insight.

## 7.4 Processing
- **FR-TA-001** The module shall analyse the classroom engagement timeline to detect
  notable rises, dips, and plateaus and the times at which they occur.
- **FR-TA-002** The module shall correlate engagement changes with elapsed time to
  produce time-anchored observations.
- **FR-TA-003** The module shall phrase every insight constructively and neutrally.
- **FR-TA-004** The module shall avoid any language that personally evaluates,
  criticises, or rates the teacher.

## 7.5 User Interaction
Insights are presented on the dashboard and included in reports. The teacher reads
them as supportive feedback.

## 7.6 Functional Flow
1. Receive classroom-aggregate timelines.
2. Detect engagement patterns and their timing.
3. Translate detected patterns into constructive natural-language insights.
4. Publish to dashboard and reporting.

## 7.7 Validation Rules
- **FR-TA-005** Insights shall only be generated when sufficient session data exists.
- **FR-TA-006** All generated text shall conform to the constructive, non-judgemental,
  unbiased tone policy.

## 7.8 Expected Behaviour
Insights shall be relevant, time-anchored, supportive, and actionable, helping the
teacher understand classroom engagement without feeling personally judged.

## 7.9 Error Handling
- **FR-TA-007** With insufficient data, the module shall state that more data is needed
  rather than fabricate insights.

## 7.10 Future Scalability
Future versions may incorporate lesson-segment tagging (e.g. lecture, activity, Q&A)
to produce richer correlations between teaching style and engagement.

---

# SECTION 8 — STUDENT REMARKS GENERATOR

**Requirement Prefix:** `FR-SR`

## 8.1 Purpose
The Student Remarks Generator shall produce intelligent, automatic, supportive
remarks for each student based on engagement levels and trends.

## 8.2 Inputs
- Per-student engagement score, level, distraction state, prolonged-inattention flag,
  dominant emotion, and trend.

## 8.3 Outputs
- A concise natural-language remark per student, such as:
  - "Highly engaged."
  - "Good classroom participation."
  - "Appears distracted."
  - "Needs additional attention."
  - "Possible learning difficulty." (used cautiously and supportively)

## 8.4 Processing
- **FR-SR-001** The module shall select remarks based on engagement level, trend, and
  attention state.
- **FR-SR-002** Prolonged inattention or persistently low engagement shall map to
  supportive remarks suggesting additional attention or a check-in.
- **FR-SR-003** Strong, sustained engagement shall map to positive remarks.
- **FR-SR-004** Sensitive remarks (e.g. possible learning difficulty) shall be phrased
  cautiously as possibilities warranting attention, never as diagnoses.

## 8.5 User Interaction
Remarks are displayed per student on the dashboard and included in reports.

## 8.6 Functional Flow
1. Receive per-student state.
2. Evaluate against remark rules and trends.
3. Select the most appropriate supportive remark.
4. Publish to dashboard and reporting.

## 8.7 Validation Rules
- **FR-SR-005** Exactly one primary remark shall be produced per student per update.
- **FR-SR-006** Remark text shall remain supportive and non-stigmatising.

## 8.8 Expected Behaviour
Remarks shall accurately reflect the student's engagement pattern and shall always be
constructive.

## 8.9 Error Handling
- **FR-SR-007** With missing data, a neutral placeholder remark shall be produced.

## 8.10 Future Scalability
Future versions may generate richer, personalised remarks via a language model behind
the same interface, and may track remark history per student.

---

# SECTION 9 — TEACHER REMARKS GENERATOR

**Requirement Prefix:** `FR-TR`

## 9.1 Purpose
The Teacher Remarks Generator shall produce professional, constructive teaching
suggestions derived from classroom engagement patterns. It shall never criticise the
teacher personally.

## 9.2 Inputs
- Classroom-aggregate engagement summary and trend.
- Teacher analytics insights.
- Emotion and participation distributions.

## 9.3 Outputs
- Professional suggestions, such as:
  - "Increase interaction."
  - "Use more examples."
  - "Introduce visual explanations."
  - "Add classroom activities."
  - "Increase questioning frequency."

## 9.4 Processing
- **FR-TR-001** The module shall map detected engagement patterns to constructive
  pedagogical suggestions.
- **FR-TR-002** Declining-attention patterns shall map to suggestions such as breaks,
  interaction, or activity changes.
- **FR-TR-003** Low overall engagement shall map to suggestions involving examples,
  visuals, or questioning.
- **FR-TR-004** All suggestions shall be impersonal, professional, and unbiased.

## 9.5 User Interaction
Suggestions are displayed on the dashboard and included in reports.

## 9.6 Functional Flow
1. Receive classroom analytics and insights.
2. Match patterns to suggestion rules.
3. Generate a prioritised set of constructive suggestions.
4. Publish to dashboard and reporting.

## 9.7 Validation Rules
- **FR-TR-005** Suggestions shall be generated only when supported by session data.
- **FR-TR-006** Suggestion text shall comply with the non-personal, constructive tone
  policy.

## 9.8 Expected Behaviour
Suggestions shall be relevant, actionable, and framed as supportive guidance rather
than criticism.

## 9.9 Error Handling
- **FR-TR-007** With insufficient data, the module shall present general supportive
  guidance and indicate that more data improves specificity.

## 9.10 Future Scalability
Future versions may tailor suggestions to subject, grade level, and lesson type.

---

# SECTION 10 — DASHBOARD MODULE

**Requirement Prefix:** `FR-DB`

## 10.1 Purpose
The Dashboard Module shall provide a professional, modern, responsive Gradio
interface that presents all live and summary information and exposes user controls.

## 10.2 Inputs
- Live annotated video frames.
- Current emotion, attention, and engagement values.
- Student and teacher remarks.
- Status indicators, performance indicators, analytics cards, and graphs.
- Session timer state.

## 10.3 Outputs
- A rendered, interactive dashboard.
- User commands (start, stop, switch camera, refresh analytics, export).

## 10.4 Dashboard Sections
The dashboard shall include, at minimum:
- **Live Webcam** view with engagement overlays.
- **Current Emotion** indicator.
- **Current Attention** indicator.
- **Current Engagement** percentage and level.
- **Student Remark** panel.
- **Teacher Remark** panel.
- **Current Status** (camera/session state).
- **Performance Indicators** (FPS, processing health).
- **Analytics Cards** (key metrics at a glance).
- **Graphs** (engagement, emotion, attention timelines).
- **Session Timer**.
- **Export Buttons** (PDF, Excel, CSV).

## 10.5 Processing
- **FR-DB-001** The dashboard shall refresh live indicators at a defined, smooth
  refresh rate.
- **FR-DB-002** The dashboard shall organise content into clear logical areas
  (live monitoring, analytics, reports, settings).
- **FR-DB-003** The dashboard shall reflect real-time state changes promptly.

## 10.6 User Interaction
- Start/stop a session, switch cameras, name the session.
- Refresh analytics and view graphs.
- Trigger report exports.
- Adjust settings.

## 10.7 Functional Flow
1. Render the layout with all sections.
2. Subscribe to live data streams and update indicators continuously.
3. Route user commands to the relevant modules.
4. Display results, analytics, and remarks as they update.

## 10.8 Validation Rules
- **FR-DB-004** Controls shall be disabled or clearly indicated when not applicable
  (e.g. export before any session data exists).
- **FR-DB-005** Displayed values shall always be within their defined ranges.

## 10.9 Expected Behaviour
The interface shall be clean, modern, responsive, and intuitive, updating smoothly
without freezing during live analysis.

## 10.10 Error Handling
- **FR-DB-006** Module errors shall be surfaced as clear, non-technical user messages
  while detailed errors are logged.
- **FR-DB-007** Loss of the video stream shall be shown clearly with guidance to
  reconnect.

## 10.11 Future Scalability
Future versions may add multi-camera layouts, theme customisation, role-based views
(teacher vs administrator), and localisation.

---

# SECTION 11 — ANALYTICS MODULE (LIVE & SESSION)

**Requirement Prefix:** `FR-AN`

## 11.1 Purpose
The Analytics Module shall provide live and session-level visual analytics, including
timelines and aggregate statistics.

## 11.2 Inputs
- Time-series of classroom engagement, emotion, attention, and participation.

## 11.3 Outputs
- Live graphs and timelines:
  - Engagement timeline.
  - Emotion timeline.
  - Attention timeline.
- Aggregate statistics:
  - Average engagement.
  - Maximum engagement.
  - Minimum engagement.
- Session summary and trend analysis.

## 11.4 Processing
- **FR-AN-001** The module shall maintain time-series buffers for each tracked metric.
- **FR-AN-002** The module shall render live graphs that update as new data arrives.
- **FR-AN-003** The module shall compute average, maximum, and minimum engagement.
- **FR-AN-004** The module shall produce a session summary and a trend classification.

## 11.5 User Interaction
The user views live and summary graphs and may refresh analytics on demand.

## 11.6 Functional Flow
1. Append incoming metrics to time-series buffers.
2. Update graphs at the configured rate.
3. Compute aggregates and trends on request or session end.
4. Provide data to the dashboard and reporting modules.

## 11.7 Validation Rules
- **FR-AN-005** Graphs shall handle empty or sparse data gracefully.
- **FR-AN-006** Aggregates shall be computed only over valid recorded frames.

## 11.8 Expected Behaviour
Graphs shall be readable, correctly scaled, and synchronised with the session
timeline.

## 11.9 Error Handling
- **FR-AN-007** Rendering failures shall be caught and shall not interrupt live
  analysis.

## 11.10 Future Scalability
Future versions may add comparative analytics across sessions and exportable
interactive charts.

---

# SECTION 12 — REPORT GENERATION MODULE

**Requirement Prefix:** `FR-RP`

## 12.1 Purpose
The Report Generation Module shall produce downloadable session reports in multiple
formats containing all key analytics, remarks, and visuals.

## 12.2 Inputs
- The completed session record, analytics summaries, remarks, and graph data.
- Desired export format (PDF, Excel, CSV) and export location from Settings.

## 12.3 Outputs
- A report file in the requested format.

### Report Contents
Each report shall include, where applicable:
- Date and time.
- Session duration.
- Average engagement.
- Emotion statistics.
- Attention statistics.
- Teacher remarks.
- Student remarks.
- Graphs (in formats that support embedded visuals).
- Overall summary.

## 12.4 Processing
- **FR-RP-001** The module shall export reports as PDF.
- **FR-RP-002** The module shall export reports as Excel.
- **FR-RP-003** The module shall export reports as CSV (tabular timeline and
  summaries).
- **FR-RP-004** The module shall assemble all required content sections into the
  report.
- **FR-RP-005** Graphs shall be embedded in formats that support them (PDF, Excel);
  CSV shall contain the underlying tabular data.

## 12.5 User Interaction
The user triggers exports from the dashboard and downloads the resulting file.

## 12.6 Functional Flow
1. Receive an export request and format.
2. Gather session summary, analytics, remarks, and graph data.
3. Render the report in the requested format.
4. Save to the configured location and provide a download link.

## 12.7 Validation Rules
- **FR-RP-006** Export shall be permitted only when a session contains recorded data.
- **FR-RP-007** The export location shall be validated as writable.

## 12.8 Expected Behaviour
Reports shall be complete, well-formatted, professional, and openable in standard
applications.

## 12.9 Error Handling
- **FR-RP-008** If export fails (e.g. unwritable location, missing dependency), the
  module shall report a clear error, log details, and leave existing data intact.

## 12.10 Future Scalability
Future versions may add scheduled/automatic reports, institutional branding, and
multi-session comparative reports.

---

# SECTION 13 — SETTINGS MODULE

**Requirement Prefix:** `FR-ST`

## 13.1 Purpose
The Settings Module shall centralise all configurable parameters and expose them to
the user for adjustment, persisting changes for future sessions.

## 13.2 Inputs
- User-provided configuration values.
- Existing persisted configuration.

## 13.3 Outputs
- Validated, persisted configuration consumed by all modules.

### Configurable Settings
- Camera selection.
- Resolution.
- Frame rate.
- Theme.
- Export location.
- Thresholds (detection confidence, eye openness, gaze tolerance, distraction,
  prolonged-inattention duration, engagement weights and bands).

## 13.4 Processing
- **FR-ST-001** The module shall present configurable settings in an organised
  interface.
- **FR-ST-002** The module shall validate all settings before applying them.
- **FR-ST-003** The module shall persist settings and reload them on startup.
- **FR-ST-004** The module shall apply changes to the relevant modules at runtime where
  feasible, or indicate when a restart is required.

## 13.5 User Interaction
The user views and edits settings and saves changes.

## 13.6 Functional Flow
1. Load persisted settings at startup.
2. Present current values to the user.
3. Validate and apply edited values.
4. Persist changes.

## 13.7 Validation Rules
- **FR-ST-005** Every setting shall be validated against its permitted range or set.
- **FR-ST-006** Invalid values shall be rejected with a clear message and the previous
  valid value retained.

## 13.8 Expected Behaviour
Settings shall behave predictably, persist reliably, and take effect as documented.

## 13.9 Error Handling
- **FR-ST-007** A corrupt or missing settings store shall fall back to documented
  defaults and log the event.

## 13.10 Future Scalability
Future versions may add per-user profiles, import/export of configuration, and
institution-wide policy defaults.

---

# SECTION 14 — LOGGING MODULE

**Requirement Prefix:** `FR-LG`

## 14.1 Purpose
The Logging Module shall record system events, warnings, errors, and session
activity to support debugging, auditing, and support.

## 14.2 Inputs
- Log messages emitted by all modules, each with a severity level.

## 14.3 Outputs
- Persistent log records categorised by severity and time.

### Log Categories
- Errors.
- Warnings.
- Events (e.g. session start/stop, camera switch).
- Session logs.
- Debug logs.

## 14.4 Processing
- **FR-LG-001** The module shall capture log messages at multiple severity levels.
- **FR-LG-002** The module shall timestamp every log entry.
- **FR-LG-003** The module shall persist logs to durable storage.
- **FR-LG-004** The module shall support a configurable verbosity level.

## 14.5 User Interaction
Logging is largely automatic; logs may be surfaced to advanced users or support.

## 14.6 Functional Flow
1. Receive a log message and severity.
2. Timestamp and format the entry.
3. Filter by configured verbosity.
4. Persist and optionally display.

## 14.7 Validation Rules
- **FR-LG-005** Log writing shall never block or crash the main analysis pipeline.

## 14.8 Expected Behaviour
Logs shall be complete, time-ordered, and useful for diagnosing issues.

## 14.9 Error Handling
- **FR-LG-006** If log storage is unavailable, logging shall degrade gracefully without
  affecting the application.

## 14.10 Future Scalability
Future versions may add log rotation, remote log aggregation, and structured logs.

---

# SECTION 15 — ERROR HANDLING (CROSS-CUTTING)

**Requirement Prefix:** `FR-EH`

## 15.1 Purpose
This section specifies system-wide error-handling requirements so that the
application remains stable and informative under fault conditions. Module-specific
handling is defined within each module above; this section defines the unified
policy and the specific conditions enumerated by the project.

## 15.2 General Policy
- **FR-EH-001** No single module fault shall crash the application; faults shall be
  contained, logged, and surfaced as clear user messages.
- **FR-EH-002** The system shall prefer graceful degradation (neutral defaults, paused
  analysis) over termination.
- **FR-EH-003** Every handled error shall be logged with sufficient context.

## 15.3 Specific Conditions
- **FR-EH-004 Camera disconnected** — pause analysis, show a clear status, and attempt
  automatic reconnection (see Webcam Module).
- **FR-EH-005 No face detected** — skip per-student analysis for affected frames and
  indicate the condition; sustained absence is surfaced as a warning.
- **FR-EH-006 Poor lighting** — detect low-quality frames, warn the user, and reduce
  confidence rather than producing unreliable results silently.
- **FR-EH-007 Low FPS** — detect throughput below a threshold, warn the user, and
  optionally reduce processing load (e.g. lower analysis frequency).
- **FR-EH-008 Multiple faces** — handle up to the configured maximum; beyond it, retain
  the strongest detections and indicate that the limit was reached.
- **FR-EH-009 Emotion model failure** — degrade to neutral emotion output and continue.
- **FR-EH-010 Missing dependencies** — detect absent components at startup, present a
  clear message identifying what is missing, and disable only the affected features.
- **FR-EH-011 Report export failure** — report a clear error, preserve session data, and
  allow retry.

## 15.4 Expected Behaviour
Under any of the above conditions the application shall remain usable, communicate
the situation clearly, and recover automatically where possible.

## 15.5 Future Scalability
Future versions may add a centralised health monitor and user-facing diagnostics.

---

# SECTION 16 — PERFORMANCE REQUIREMENTS

**Requirement Prefix:** `FR-PF`

## 16.1 Purpose
This section specifies the non-functional performance targets the software shall meet
on a standard laptop with an external USB webcam.

## 16.2 Targets
- **FR-PF-001 Startup time** — the application shall reach an interactive state within a
  short, bounded time after launch on a standard laptop.
- **FR-PF-002 CPU usage** — sustained CPU usage shall remain within a bounded share of
  available capacity during live analysis, leaving the machine responsive.
- **FR-PF-003 Memory limits** — memory usage shall remain within a bounded footprint for
  a typical session and shall not grow unbounded over time.
- **FR-PF-004 Expected FPS** — live analysis shall maintain a smooth, usable frame rate
  sufficient for real-time monitoring on the target hardware.
- **FR-PF-005 Response time** — user actions (start, stop, switch camera, export) shall
  produce a visible response within a short, bounded time.
- **FR-PF-006 Dashboard refresh rate** — live indicators and graphs shall refresh at a
  smooth, defined rate that conveys real-time state without overloading the system.

## 16.3 Processing Considerations
- **FR-PF-007** The system shall keep video capture, analysis, and UI responsive
  concurrently so that heavy processing does not freeze the interface.
- **FR-PF-008** The system shall provide configurable performance controls (e.g.
  analysis frequency, resolution) to adapt to varying hardware.

## 16.4 Expected Behaviour
On target hardware the application shall run smoothly in real time, remain
responsive, and stay within its resource budgets throughout a full session.

## 16.5 Future Scalability
Future versions may add optional hardware acceleration, model selection by capability,
and automatic performance tuning based on detected hardware.

---

## END OF PART 1B — FUNCTIONAL REQUIREMENTS SPECIFICATION

This part has specified the functional behaviour of all sixteen requirement areas of
EduSense AI 360 in a form suitable for direct implementation. Subsequent parts may
cover detailed data design, interface design, test specifications, and deployment.
