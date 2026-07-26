# SOFTWARE REQUIREMENT SPECIFICATION (SRS)
# EduSense AI 360
## AI-Powered Smart Classroom Engagement & Teaching Quality Monitoring System

---

## PART 6 — AI DECISION LOGIC, INTELLIGENCE ENGINE & BUSINESS RULE SPECIFICATION

| Field | Value |
|---|---|
| Document Part | Part 6 — AI Decision Logic & Intelligence |
| Continues From | Parts 1A, 1B, 2, 3, 4 (and the Part 5 build mandate) |
| Version | 1.0 |
| Audience | AI/ML Engineering, Computer Vision, Analytics, QA |
| Status | Definitive intelligence specification |

### Preface

This part defines **how the AI reasons**. Where earlier parts described *what* the
system does (1B), *how it looks* (2), *how it is structured* (3), and *how it is
built* (4), this part removes all remaining ambiguity about the **decision logic,
scoring philosophy, business rules, and AI behaviour**.

The intelligence is **explainable, deterministic where appropriate, and consistent**:
identical inputs produce identical outputs, every insight is traceable to observed
behaviour, and no conclusion is drawn from hidden reasoning. All numeric thresholds
referenced here are **configuration-driven** (defined in `config/default_config.json`
and validated by the Configuration Manager); this document specifies *how values are
used to reach a decision*, never hard-coded magic numbers. Default values are cited
only to illustrate behaviour.

This part contains reasoning specification only — no source code.

### Non-Negotiable Constraints (carried from Parts 1B/2/3)

- The system **never diagnoses** medical or psychological conditions; it describes
  **observed classroom behaviour** only.
- The system **never evaluates, ranks, or blames the teacher**; it analyses
  **classroom response**.
- The system performs **no identity recognition** and maintains **no facial-recognition
  database**; face "identities" are transient, per-session tracking handles only.
- All feedback is **constructive, supportive, and non-stigmatising**.

---

# 1. AI PIPELINE OVERVIEW

The reasoning pipeline transforms raw video into explainable insight through ordered,
loosely-coupled stages (Architecture Part 3 §4). Each stage consumes the previous
stage's contract and never reaches backward.

```
Webcam → Frame Processing → Face Detection → Eye Tracking → Emotion Detection →
Attention Estimation → Engagement Calculation → Behaviour Analysis → Trend Analysis →
Remarks Generation → Teacher Insights → Dashboard → Reports
```

## 1.1 Stage Concepts
1. **Frame Processing** — colour-convert, normalise, and quality-gate each frame;
   poor frames lower downstream confidence rather than being trusted blindly.
2. **Face Detection** — locate and *track* faces, assigning a stable per-session id so
   reasoning is continuous per student.
3. **Eye Tracking** — derive eye openness, blink, gaze, and head pose per face.
4. **Emotion Detection** — classify facial emotion with confidence, stabilised over time.
5. **Attention Estimation** — fuse eye/gaze/head signals into an attention state and
   confidence (Section 2).
6. **Engagement Calculation** — blend attention, emotion, and presence with continuity
   and recovery context into a 0–100 score and a level (Section 4).
7. **Behaviour Analysis** — interpret per-student patterns over the session (Section 8).
8. **Trend Analysis** — detect rising/declining/stable engagement and emotion
   transitions over time (Section 12).
9. **Remarks Generation** — produce prioritised, explainable student remarks (Section 10).
10. **Teacher Insights** — translate classroom-level patterns into constructive,
    non-evaluative observations and suggestions (Section 9).
11. **Dashboard / Reports** — present and persist the reasoning outputs.

## 1.2 Universal Reasoning Rules
- **No single-frame decisions.** Every reported state is temporally smoothed
  (Section 15).
- **Confidence travels with every output** and propagates downstream (Section 13).
- **Conflicts resolve by a fixed priority** (Section 14).
- **Every output is explainable** via the observations that produced it (Section 18).

---

# 2. ATTENTION ENGINE

The Attention Engine determines, per student per frame, how focused the student is on
the lesson, expressed as an **attention value in [0, 1]**, an **attention state**, and a
**confidence**.

## 2.1 Contributing Factors
| Factor | Effect on attention |
|---|---|
| **Eye openness** (EAR vs threshold) | Open eyes support attention; closed eyes reduce it. |
| **Eye/gaze direction** | Gaze centred on the board/teacher supports attention; gaze drifting away reduces it. |
| **Blink frequency** | Normal blinking is ignored; abnormally high/low rates slightly reduce confidence, not attention. |
| **Head orientation** (yaw/pitch) | Facing forward supports attention; turned away reduces it. |
| **Face visibility** | A clearly visible, adequately sized face supports confidence. |
| **Continuous focus** | Sustained on-task frames reinforce a stable High state. |
| **Face absence** | No face → attention is **Unknown**, not Low. |
| **Temporary distractions** | Brief look-aways are tolerated by smoothing and recovery rules. |
| **Confidence level** | Poor lighting, small/blurred faces, or incomplete landmarks lower confidence. |

## 2.2 Derivation (conceptual)
Attention is a **weighted blend** of three normalised components — eyes-open,
gaze-on-target (graded by how far the iris drifts from centre), and head-facing-forward
— combined into [0, 1]. The blend weights are fixed and explainable (eyes and gaze
dominate; head orientation supports). The blended value is then **temporally smoothed**
over a short rolling window before a state is assigned.

## 2.3 Attention States
| State | Meaning (derived from the smoothed attention value, thresholds configurable) |
|---|---|
| **High Attention** | Eyes open, gaze on target, head forward, sustained. |
| **Medium Attention** | Mixed signals (e.g. occasional gaze drift) but still on-task overall. |
| **Low Attention** | Eyes closed, gaze persistently away, or head turned away. |
| **Unknown Attention** | Face absent, or confidence too low to assert a state. |

State boundaries are derived from configured thresholds, not fixed in logic.

## 2.4 Stability Rules
- A state change requires the new condition to **persist across the smoothing window**;
  single-frame fluctuations do not flip the state.
- **Recovery rule:** after a brief distraction, attention recovers smoothly as on-task
  frames accumulate — it is not penalised indefinitely for a momentary look-away.
- **Hysteresis:** the threshold to *leave* a favourable state is slightly stricter than
  to *enter* it, preventing rapid oscillation near a boundary.

## 2.5 Confidence Scoring
Attention confidence rises with complete landmarks, good lighting, and an adequately
sized, forward face; it falls with poor lighting, small/blurred/partial faces, missing
landmarks, or extreme head poses. When confidence is below a configured floor, the
state is reported as **Unknown** rather than asserting Low.

---

# 3. EMOTION ENGINE

## 3.1 Emotion Classes
Happy, Neutral, Sad, Angry, Fear, Surprise (the model's native set). **Confused** is a
**derived** state inferred from a sustained combination of low-arousal negative emotion
(e.g. sad/fear) with reduced attention — never asserted from a single frame.

## 3.2 Confidence
Each prediction carries a confidence. Predictions below a configured confidence floor
are treated as **low-confidence** and **default toward Neutral** rather than asserting an
uncertain emotion.

## 3.3 Smoothing, History & Persistence
- **Emotion smoothing:** predictions are averaged across a configured rolling window per
  student, suppressing frame-to-frame flicker.
- **Emotion history:** a per-student timeline is retained for analytics and the emotion
  timeline graph.
- **Emotion persistence:** the reported dominant emotion is the *stabilised* emotion, not
  the latest raw prediction.

## 3.4 Transient vs Sustained Emotions
This distinction is central to honest reasoning:
- A **transient** emotion (present for only a few frames) **does not** change the
  reported emotional state or materially move engagement; it is absorbed by smoothing.
- A **sustained** emotion (consistent across the smoothing window) **does** become the
  reported state and influences engagement and remarks.
- **Emotion changes** are only recognised when the new emotion is sustained, preventing
  spurious "mood swings" in the analytics.

---

# 4. ENGAGEMENT ENGINE

## 4.1 Conceptual Model
Engagement is a **confidence-weighted blend** of normalised factors, contextualised by
behaviour over time, producing a 0–100 score and a level.

| Factor | Role |
|---|---|
| **Attention** | Primary driver (Section 2). |
| **Emotion** | Positive/learning affect raises engagement; frustration/confusion lowers it (mapped via configured per-emotion weights). |
| **Presence / face visibility** | A reliably visible face supports engagement and confidence; absence lowers both. |
| **Consistency / focus duration** | Sustained on-task focus is rewarded; repeated distraction is penalised. |
| **Behaviour history** | Recent pattern contextualises the current frame (a steady learner is not condemned by one dip). |
| **Temporary distractions** | Tolerated; they dampen but do not collapse the score. |
| **Recovery after distraction** | The score rises again as attention returns — recovery is rewarded. |
| **Session duration** | Distinguishes a brief dip from a sustained decline; informs warm-up handling (Section 7). |
| **Confidence** | Low-confidence inputs reduce the engagement confidence and pull contributions toward neutral. |

## 4.2 Derivation
Each factor is normalised to [0, 1]; the primary factors (attention, emotion, presence)
are combined using **configured weights that sum to one** (defaults: attention 0.5,
emotion 0.3, presence 0.2). Continuity and recovery act as **contextual modifiers** that
reward sustained focus and smooth recovery. The result is scaled to **0–100** and then
**temporally smoothed** for a stable live value.

## 4.3 Engagement Levels
The score maps to a **level via configured bands** (the canonical band set is the four
levels defined in Part 1B: **Poor, Average, Good, Excellent**). The engine derives the
level by selecting the band whose lower bound the score meets. Because bands are
configuration data, finer granularity (e.g. an additional *Critical* sub-band for very
low engagement, or *Moderate* labelling) can be introduced by configuration **without
code change**; the derivation logic is unchanged. No level boundary is hard-coded.

## 4.4 Risk Level
A **risk level** (Low / Moderate / High) is derived from persistently low engagement and
prolonged inattention: brief low readings are Low risk; sustained low engagement or
prolonged inattention escalates risk. Risk is observational (a prompt to check in), never
a judgement of the student.

## 4.5 Confidence
Engagement confidence is derived from the confidences of its inputs (attention, emotion)
and face presence. Missing inputs substitute neutral defaults and **reduce confidence**
rather than causing failure.

---

# 5. DISTRACTION ENGINE

## 5.1 Detection
Distraction is recognised when engagement (or attention) falls below the configured
**distraction threshold**, driven by: gaze persistently away, repeated rapid gaze shifts,
prolonged eye closure, or a missing face (handled as Unknown, see below).

## 5.2 Short vs Long Distraction
- **Short distraction** — below threshold briefly; absorbed/recovered, logged but not
  alarmed.
- **Long distraction** — sustained below threshold beyond the configured
  **prolonged-inattention duration** (default ~10s); flagged as **prolonged inattention**
  and surfaced as an alert and a supportive remark.
- **Frequent distraction** — many short distractions across the session is itself a
  behaviour pattern reported by Student Analytics.

## 5.3 Recovery
A distraction is considered ended once the student returns on-task for a sustained run of
frames; the distraction timer resets and engagement recovers smoothly. Recovery is
rewarded, not ignored.

## 5.4 False Positives
- A **missing face** is **Unknown**, not automatically a distraction, unless absence is
  sustained.
- **Blinks** are distinguished from closure by duration (Section 16).
- Momentary lighting dips or motion blur lower confidence rather than asserting
  distraction.

---

# 6. SESSION INTELLIGENCE

The engine interprets the session as having phases:
- **Beginning / warm-up period** — the opening interval is treated as settling time;
  engagement during warm-up is recorded but down-weighted when judging overall session
  quality, so a slow start does not unfairly dominate the summary.
- **Attention stabilization** — after warm-up, readings are considered representative.
- **Middle of session** — the core period for trend detection.
- **End of session** — closing readings inform the final trend and summary.
- **Session summary** — aggregate engagement, attendance, distribution, and trend.
- **Behaviour evolution** — how engagement and emotion evolved across phases.

Session phase context is what lets the engine distinguish "started slow, improved" from
"started strong, declined," which materially changes teacher insights.

---

# 7. STUDENT INSIGHT ENGINE

Identifies **observed classroom-behaviour patterns** per student — strictly descriptive,
never diagnostic.

| Pattern | Observed basis |
|---|---|
| **Consistent learner** | Sustained engagement with low variance across the session. |
| **Highly focused student** | Predominantly High attention / Excellent engagement. |
| **Temporary distraction** | One or few short distractions with full recovery. |
| **Improving engagement** | Upward trend across session portions. |
| **Declining engagement** | Downward trend across session portions. |
| **Needs attention** | Sustained low engagement or prolonged inattention. |
| **Positive improvement** | Recovery from an early low to a sustained higher level. |
| **High participation** | Reliably present and engaged for most of the session. |
| **Low participation** | Frequently absent from frame or persistently disengaged. |
| **Possible learning difficulty** | *Used cautiously*: sustained confusion-like signals (sustained negative low-arousal emotion + low attention) — phrased as an observation warranting attention, **never a diagnosis**. |

Every pattern is reported with the observation that produced it and is bounded by the
ethical constraints (Section 19).

---

# 8. TEACHER INSIGHT ENGINE

Analyses **classroom response** and produces constructive observations and suggestions.
It **never** evaluates, ranks, or blames the teacher.

## 8.1 Observation Types (time-anchored)
- "Students maintained attention throughout."
- "Attention gradually decreased after [time]."
- "Students responded well following interaction."
- "Students appeared more engaged during explanation with examples."
- "Students showed increased engagement during questioning."

## 8.2 Recommendation Types (constructive, impersonal)
Increase interaction · use more examples · introduce visual explanations · add a short
activity or break around an observed dip · increase questioning frequency. Each
recommendation is tied to the classroom pattern that motivated it.

## 8.3 Tone Policy
Impersonal ("students…", not "you…"), supportive, unbiased, and free of ranking or blame.
Insights are produced only when sufficient session data exists.

---

# 9. REMARKS ENGINE

Produces Student Remarks, Teacher Remarks, Session Summary, Recommendations, Warnings,
Positive Feedback, and Improvement Suggestions.

## 9.1 Priority Order
When multiple remark rules match, the **highest-priority** primary remark is emitted:
1. **Safety / attention alerts** — prolonged inattention, sustained closure/sleep, high
   risk.
2. **Negative / declining patterns** — sustained low engagement, frequent distraction,
   sustained confusion.
3. **Neutral / steady states.**
4. **Positive reinforcement** — sustained strong engagement, clear improvement.

Exactly **one primary remark** per student per update (optional secondary supportive
notes allowed). Teacher remarks follow the same discipline at classroom level.

## 9.2 Tone, Consistency, Explainability
- **Tone:** professional, supportive, non-stigmatising.
- **Consistency:** identical states yield identical remarks; remarks change only when the
  underlying state changes (stabilised, not flickering).
- **No contradictions:** the engine never emits conflicting remarks in the same update
  (e.g. "highly engaged" and "distracted"); priority resolution guarantees a single
  coherent message.
- **Explainability:** every remark is traceable to the engagement level, trend, and
  signals that triggered it.

---

# 10. ALERT ENGINE

Alerts are **informative and non-alarming** — calm, factual, and actionable.

| Alert | Trigger |
|---|---|
| **Long distraction** | Prolonged inattention threshold exceeded for a student. |
| **Very low engagement** | Classroom or student engagement sustained at a critical low. |
| **Camera unavailable** | Camera disconnected or failed to initialise. |
| **Poor lighting** | Sustained low-quality frames detected. |
| **No face** | No face present for a sustained interval. |
| **Low confidence** | Analysis confidence sustained below the floor. |
| **System error** | A contained internal fault occurred. |
| **Report export completed** | An export finished successfully. |
| **Session completed** | A session ended and was saved. |

Alerts state the situation and, where useful, a gentle next step; they never use
alarming language or imply blame.

---

# 11. TREND ANALYSIS ENGINE

Detects how the classroom (and each student) evolves over time:
- **Increasing / Decreasing / Stable engagement** — by comparing engagement across
  session portions (e.g. first vs last third) against configured deltas; below a minimum
  data volume the trend is **Insufficient data**.
- **Emotion transitions** — sustained shifts in dominant emotion across the session.
- **Attention trends** — direction of attention over time, with drop points time-anchored.
- **Behaviour patterns** — recurring distraction/recovery cycles.
- **Session comparison** and **weekly improvements** — *future support* via persisted
  historical sessions (Section 17), designed for but not active in Version 1.

---

# 12. AI CONFIDENCE SYSTEM

Every prediction includes confidence, banded for clarity:
| Band | Meaning |
|---|---|
| **High** | Strong, complete signals; good conditions. |
| **Medium** | Usable but imperfect signals. |
| **Low** | Weak/partial signals; outputs treated cautiously and pulled toward neutral. |
| **Unknown** | Insufficient basis to assert a state (e.g. no face). |

**Confidence decreases when:** lighting is poor; the face is small, blurred, partially
occluded, or at an extreme pose; landmarks are incomplete; the emotion prediction is
weak; or frames are dropped/unstable. Low confidence never silently masquerades as a
confident result — it is surfaced and propagated.

---

# 13. DECISION PRIORITY & CONFLICT RESOLUTION

When observations conflict, a **fixed priority** guarantees deterministic, explainable
resolution:

1. **No face present** → state is **Unknown**; downstream attention/emotion are not
   asserted for that student this frame, regardless of any stale prior values.
2. **Low confidence / poor lighting** → outputs are pulled toward neutral/Unknown rather
   than asserting strong states.
3. **Eyes closed (sustained)** → attention is **Low** even if a prior emotion was
   positive; a "happy" reading does not override sustained eye closure.
4. **Attention** outranks **emotion** in driving engagement; emotion modulates, attention
   leads.
5. **Sustained** observations outrank **transient** ones at every level.

Example: a momentary "Happy" emotion with eyes closed and gaze away resolves to **Low
attention / reduced engagement**, because sustained eye/gaze evidence and the priority
order outrank a transient positive emotion.

---

# 14. FALSE-POSITIVE REDUCTION

| Risk | Mitigation |
|---|---|
| **False attention loss** | Temporal smoothing + recovery + hysteresis; brief look-aways tolerated. |
| **False emotion detection** | Confidence floor + smoothing; low-confidence → Neutral. |
| **Temporary lighting issues** | Quality gating lowers confidence rather than asserting state. |
| **Momentary face loss** | Grace period before declaring loss; reacquire by proximity. |
| **Blink confusion** | Blinks classified by short duration; only sustained closure → drowsiness. |
| **Camera shake / motion blur** | Low-quality frames reduce confidence; smoothing absorbs single-frame noise. |

The guiding principle: **uncertainty lowers confidence; it does not manufacture a
confident negative.**

---

# 15. TEMPORAL ANALYSIS

The AI never relies on a single frame:
- **Rolling windows** per signal (attention, emotion, engagement) of configurable length.
- **Moving averages** smooth live values and graphs.
- **Historical observations** within the session contextualise the present.
- **Time smoothing** stabilises reported states.
- **Prediction stability:** a state persists until a *sustained* change is observed.
- **Consistency checks:** outputs are validated against recent history so they do not
  contradict the established pattern without sufficient new evidence.

---

# 16. PERSONALIZATION

**Version 1 is deterministic and global:** every student is assessed with the same
configured thresholds, ensuring transparent, reproducible behaviour and avoiding premature
complexity (KISS/YAGNI). The architecture nonetheless leaves a clean seam for **future
personalization**: per-student or per-classroom **baselines** (learning a student's
typical attention range and assessing relative to it), adaptive thresholds, and
session-history-aware calibration — all introducible without changing the public reasoning
contracts.

---

# 17. EXPLAINABLE AI

Every insight is **explainable and traceable**:
- Each engagement score is decomposable into its attention, emotion, and presence
  contributions plus continuity/recovery context.
- Each state (attention, emotion, distraction) cites the observations that produced it.
- Each remark and alert references the level/trend/signal that triggered it.
- No conclusion is drawn from hidden reasoning; there are no unexplained outputs. This
  supports trust, debugging, and honest communication with educators.

---

# 18. ETHICAL AI

The intelligence engine operates under firm principles:
- **Privacy** — processing is local; no facial-recognition database is built; face
  identities are transient per-session tracking handles only.
- **No identity recognition / no surveillance** — the system measures engagement
  patterns, not *who* a person is, and is not a monitoring or policing tool.
- **No medical or psychological diagnosis** — only observed classroom behaviour is
  described.
- **Transparency & explainability** — outputs are traceable (Section 17).
- **Fairness & bias reduction** — uniform, configurable thresholds; uncertainty handled
  honestly; care taken that lighting/skin-tone/pose do not silently bias results
  (low-confidence handling rather than confident error).
- **Constructive feedback** — all student and teacher outputs are supportive and
  non-stigmatising.
- **Educational use only** — the system exists to support teaching and learning.

---

# 19. FUTURE AI CAPABILITIES

Designed-for extensions (inactive in Version 1): voice analysis and speech clarity,
hand-raising and note-taking detection, richer class-participation metrics, multi-student
analytics at scale, predictive engagement, cloud analytics, a teacher portal and school
administrator dashboard, and large-classroom support. Each attaches as a new analysis
module emitting its own contract, fused by the engagement engine or consumed by analytics
without altering existing reasoning.

---

# 20. AI DESIGN PRINCIPLES (SUMMARY)

Explainability · Consistency · Deterministic decision-making where appropriate ·
Confidence estimation on every output · Scalability · Ethical AI · Educational purpose ·
Professional analytics · Enterprise architecture · Future extensibility.

---

## END OF PART 6 — AI DECISION LOGIC, INTELLIGENCE ENGINE & BUSINESS RULE SPECIFICATION

This part defines the complete, explainable, ethically-bounded reasoning of EduSense
AI 360 — the attention, emotion, engagement, distraction, session, student-insight,
teacher-insight, remarks, alert, trend, and confidence engines, plus decision priority,
false-positive reduction, temporal analysis, personalization, explainability, and ethics
— providing the definitive intelligence specification for implementation.
