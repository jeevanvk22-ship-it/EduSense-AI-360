# SOFTWARE REQUIREMENT SPECIFICATION (SRS)
# EduSense AI 360
## AI-Powered Smart Classroom Engagement & Teaching Quality Monitoring System

---

## PART 2 — UI / UX DESIGN SPECIFICATION

| Field | Value |
|---|---|
| Document Part | Part 2 — UI / UX Design Specification |
| Continues From | Part 1A (Overview), Part 1B (Functional Requirements) |
| Version | 1.0 |
| Audience | Product Design, Frontend Architecture, Engineering |
| Frontend Target | Gradio (implementation-agnostic in this document) |
| Scope | Visual language, layout, components, motion, responsiveness, UX |

### Preface

This document defines the complete intended look, feel, and behaviour of EduSense
AI 360. It describes the **ideal interface** independent of implementation. The goal
is unambiguous: the product must present as a **premium commercial AI analytics
platform** — confident, minimal, data-dense yet calm — and must never read as a
student project. Where Gradio later constrains a detail, the design intent defined
here governs the target, and engineering approximates it as closely as the platform
allows.

This part contains design specification only. It contains no code and prescribes no
implementation technique.

---

# 1. DESIGN PHILOSOPHY & GOALS

## 1.1 Product Personality
EduSense AI 360 is an **intelligent observer**: quietly powerful, precise, and
trustworthy. The interface should feel like a high-end command centre for classroom
insight — the kind of tool an institution pays for. Three adjectives anchor every
decision: **Premium, Clear, Intelligent.**

## 1.2 Design Goals
The interface shall feel: Modern · Professional · Premium · Clean · Minimal ·
AI-powered · Enterprise-grade · Analytics-first.

## 1.3 Guiding Principles
- **Clarity over decoration.** Every pixel earns its place; data is the hero.
- **Calm confidence.** Generous whitespace, restrained colour, no visual noise.
- **One focal point per view.** The eye always knows where to land first.
- **Consistency is luxury.** A single, strict design system across every screen.
- **Motion with meaning.** Animation explains change; it never performs for its own sake.
- **Glance-ability.** Key state (engagement, emotion, attention) is readable in under
  two seconds.

---

# 2. DESIGN LANGUAGE & STYLE

## 2.1 Visual Style Summary
A modern **dark-first analytics aesthetic** built on layered surfaces, soft depth,
and a disciplined accent palette. Light mode mirrors the same system on a bright
canvas. The signature elements are: large gradient headers, soft-shadowed cards with
generous rounding, subtle glassmorphism on overlays, crisp data visualisation, and
fluid micro-interactions.

## 2.2 Core Stylistic Devices
- **Modern cards** — the primary content container; self-contained, elevated, padded.
- **Rounded corners** — soft, consistent radii across all surfaces (see §6).
- **Glassmorphism** — reserved for floating layers (top bar on scroll, modals,
  notifications, dropdowns): translucent surface, background blur, hairline border,
  faint inner highlight. Never used on dense data cards, where it would harm legibility.
- **Soft shadows** — diffuse, low-opacity, multi-layer elevation; never harsh.
- **Gradient headers** — page and hero headers use the brand gradient as a quiet wash.
- **Smooth animations** — short, eased transitions on state, hover, and navigation.
- **Professional outline icons** — consistent stroke weight, never playful.
- **Minimal layout** — strong grid, deliberate whitespace, clear hierarchy.

## 2.3 Surface & Depth Model
Depth is communicated through a small set of elevation levels, not arbitrary shadows:

| Elevation | Use | Treatment |
|---|---|---|
| E0 | App background | Flat base colour |
| E1 | Cards, panels | Subtle shadow, 1px border |
| E2 | Hover / active cards, popovers | Increased shadow, slight lift |
| E3 | Modals, dialogs | Strong shadow + backdrop scrim/blur |
| E4 | Toasts / notifications | Glass surface, top-most |

## 2.4 Theme Support
Both **Dark Mode** (default) and **Light Mode** are first-class, fully specified, and
toggleable from the sidebar and Settings. Theme choice persists across sessions. All
tokens below are defined for both themes; components reference tokens, never raw
colours, so a theme switch recolours the entire app coherently.

---

# 3. COLOR SYSTEM

Colours are defined as semantic tokens. Each token has a dark-mode and light-mode
value. Components must reference tokens, never literal hex.

## 3.1 Brand Colours
| Token | Role | Dark | Light |
|---|---|---|---|
| `--brand-primary` | Primary / actions | `#6366F1` (Indigo) | `#5B5BF0` |
| `--brand-primary-strong` | Pressed / emphasis | `#4F46E5` | `#4338CA` |
| `--brand-secondary` | Secondary accent | `#22D3EE` (Cyan) | `#0EA5C4` |
| `--brand-accent` | Highlights / AI cues | `#A78BFA` (Violet) | `#7C3AED` |
| `--brand-gradient` | Headers / hero | `linear-gradient(120deg,#6366F1 0%,#7C5CFC 45%,#22D3EE 100%)` | `linear-gradient(120deg,#5B5BF0 0%,#7C3AED 50%,#0EA5C4 100%)` |

## 3.2 Status / Semantic Colours
| Token | Role | Dark | Light |
|---|---|---|---|
| `--success` | Good / connected / Excellent | `#34D399` | `#16A34A` |
| `--warning` | Caution / Average | `#FBBF24` | `#D97706` |
| `--danger` | Error / Poor / disconnected | `#F87171` | `#DC2626` |
| `--info` | Informational | `#60A5FA` | `#2563EB` |

## 3.3 Neutral / Structural Colours
| Token | Role | Dark | Light |
|---|---|---|---|
| `--bg` | App background (E0) | `#0A0E1A` | `#F5F7FB` |
| `--surface` | Sidebar / bars | `#0F1525` | `#FFFFFF` |
| `--card` | Card surface (E1) | `#151C2E` | `#FFFFFF` |
| `--card-hover` | Card hover (E2) | `#1B2438` | `#F8FAFF` |
| `--border` | Hairline borders | `rgba(255,255,255,0.08)` | `#E6EAF2` |
| `--border-strong` | Emphasised dividers | `rgba(255,255,255,0.14)` | `#D5DBE8` |
| `--overlay-glass` | Glass layers | `rgba(17,24,39,0.72)` + blur | `rgba(255,255,255,0.72)` + blur |
| `--scrim` | Modal backdrop | `rgba(5,8,16,0.6)` | `rgba(15,23,42,0.35)` |

## 3.4 Text Colours
| Token | Role | Dark | Light |
|---|---|---|---|
| `--text-primary` | Headings / key values | `#F8FAFC` | `#0F172A` |
| `--text-secondary` | Body / labels | `#A8B2C7` | `#475569` |
| `--text-muted` | Captions / hints | `#6B7693` | `#7C879B` |
| `--text-on-brand` | Text on brand fills | `#FFFFFF` | `#FFFFFF` |
| `--text-disabled` | Disabled text | `#4A5468` | `#A8B2C0` |

## 3.5 Interactive State Colours
| Token | Role | Dark | Light |
|---|---|---|---|
| `--btn-primary-bg` | Primary button | `#6366F1` | `#5B5BF0` |
| `--btn-primary-hover` | Hover | `#7479F4` | `#4F46E5` |
| `--btn-primary-active` | Pressed | `#4F46E5` | `#4338CA` |
| `--btn-secondary-bg` | Secondary button | `rgba(99,102,241,0.12)` | `#EEF0FE` |
| `--hover-overlay` | Generic hover wash | `rgba(255,255,255,0.04)` | `rgba(15,23,42,0.03)` |
| `--focus-ring` | Keyboard focus | `#22D3EE` @ 2px + soft glow | `#5B5BF0` @ 2px |
| `--disabled-bg` | Disabled control | `#1A2236` | `#EEF1F6` |

## 3.6 Data Visualisation Palette
A categorical palette tuned for dark and light backgrounds, colour-blind aware
(distinct in hue and value):

| Series | Colour |
|---|---|
| Series 1 (Engagement) | `#6366F1` |
| Series 2 (Attention) | `#22D3EE` |
| Series 3 (Focus) | `#34D399` |
| Series 4 | `#A78BFA` |
| Series 5 | `#FBBF24` |
| Series 6 | `#F472B6` |
| Series 7 | `#60A5FA` |
| Series 8 | `#FB923C` |

**Engagement scale (Poor → Excellent):** continuous gradient
`#F87171 → #FBBF24 → #34D399`, so a glance at colour conveys level.

**Emotion colour mapping** (used consistently in every emotion chart, badge, and card):

| Emotion | Colour |
|---|---|
| Happy | `#FBBF24` |
| Neutral | `#94A3B8` |
| Sad | `#60A5FA` |
| Angry | `#F87171` |
| Fear | `#A78BFA` |
| Surprise | `#22D3EE` |
| Confused | `#FB923C` |

## 3.7 Chart Structural Colours
| Token | Role | Dark | Light |
|---|---|---|---|
| `--chart-grid` | Gridlines | `rgba(255,255,255,0.06)` | `#EEF2F8` |
| `--chart-axis` | Axis lines/labels | `#6B7693` | `#64748B` |
| `--chart-tooltip-bg` | Tooltip | `rgba(17,24,39,0.92)` + blur | `#FFFFFF` |
| `--chart-area-fill` | Area gradient under lines | brand @ 18% → 0% | brand @ 14% → 0% |

## 3.8 Notification Colours
Each notification type pairs a semantic colour with a tinted surface and matching
icon: Success → `--success`; Warning → `--warning`; Error → `--danger`;
Information → `--info`; Loading/Processing → `--brand-secondary` with animated accent.

## 3.9 Icon Colours
Icons inherit `--text-secondary` by default, `--text-primary` when active, and the
relevant semantic colour when conveying status (e.g. camera-connected icon uses
`--success`).

---

# 4. TYPOGRAPHY

## 4.1 Font Families
| Role | Family | Rationale |
|---|---|---|
| Display / Headings | **Sora** (or Inter Tight fallback) | Geometric, confident, modern |
| UI / Body | **Inter** | Highly legible, neutral, professional |
| Metrics / Numerals | **Inter** with tabular figures (JetBrains Mono for IDs/logs) | Aligned, stable numbers |

System fallback stack: `Inter, "Segoe UI", Roboto, system-ui, -apple-system, sans-serif`.

## 4.2 Type Scale
| Style | Size / Line height | Weight | Letter spacing | Use |
|---|---|---|---|---|
| Display XL | 48 / 56 | 700 | -0.02em | Splash, hero metric |
| H1 | 34 / 42 | 700 | -0.01em | Page titles, dashboard header |
| H2 | 26 / 34 | 650 | -0.01em | Section titles |
| H3 | 20 / 28 | 600 | 0 | Panel titles |
| Card Title | 16 / 24 | 600 | 0 | KPI card titles |
| Body Large | 16 / 26 | 400 | 0 | Lead paragraphs |
| Body | 14 / 22 | 400 | 0 | Default text |
| Label | 13 / 18 | 600 | 0.02em (UPPERCASE optional) | Field/card labels |
| Caption | 12 / 16 | 500 | 0.01em | Hints, timestamps |
| Metric Value | 40 / 46 | 700, tabular | -0.02em | Big KPI numbers |
| Metric Unit | 16 / 20 | 600 | 0 | %, units beside metrics |
| Button | 14 / 20 | 600 | 0.01em | All buttons |
| Graph Label | 12 / 16 | 500 | 0.01em | Axis / legend |

## 4.3 Text Hierarchy Rules
- One H1 per view, paired with a brief secondary-coloured subtitle.
- Card titles use Card Title style with a small leading icon.
- Metric values dominate their card; labels sit above in `--text-muted`.
- Numerals always use tabular figures so live-updating values don't shift width.
- Body copy never exceeds ~75 characters per line for readability.
- Avoid more than three type sizes within a single card.

---

# 5. SPACING, GRID & RADII

## 5.1 Spacing Scale (4-pt base)
`4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80`. All margins, padding, and gaps use this
scale exclusively.

## 5.2 Layout Grid
- **Desktop:** 12-column fluid grid, 24px gutters, max content width ~1440px, centred.
- Cards snap to column spans (e.g. KPI cards span 3 columns; webcam spans 8; insights
  panel spans 4).
- Page padding: 32px desktop, 24px laptop, 16px tablet.

## 5.3 Corner Radii
| Token | Value | Use |
|---|---|---|
| `--radius-sm` | 8px | Inputs, small chips |
| `--radius-md` | 12px | Buttons, badges |
| `--radius-lg` | 16px | Cards, panels |
| `--radius-xl` | 20px | Hero / webcam frame |
| `--radius-2xl` | 28px | Modals |
| `--radius-pill` | 999px | Pills, toggles, avatars |

## 5.4 Elevation / Shadow Tokens
| Token | Definition (dark) |
|---|---|
| `--shadow-e1` | `0 1px 2px rgba(0,0,0,.30), 0 4px 16px rgba(0,0,0,.20)` |
| `--shadow-e2` | `0 4px 12px rgba(0,0,0,.35), 0 12px 32px rgba(0,0,0,.28)` |
| `--shadow-e3` | `0 16px 48px rgba(0,0,0,.45)` |
| `--glow-brand` | `0 0 0 1px rgba(99,102,241,.4), 0 0 24px rgba(99,102,241,.25)` (AI emphasis) |

Light mode uses the same structure at lower opacity for a soft, airy feel.

---

# 6. APPLICATION LAYOUT

The application uses a persistent **shell**: a left sidebar, a top navigation bar, the
main content area, and a bottom status bar, with notifications floating top-right.

## 6.1 Shell Anatomy
```
┌───────────────────────────────────────────────────────────────┐
│  TOP NAVIGATION BAR (search · session · theme · profile)       │
├──────────┬────────────────────────────────────────────────────┤
│          │  HEADER AREA (page title · gradient · primary CTA)  │
│ LEFT     ├────────────────────────────────────────────────────┤
│ SIDEBAR  │                                                     │
│ (nav)    │  MAIN CONTENT AREA (dashboard / analytics / etc.)   │
│          │                                                     │
│          │  ANALYTICS PANEL (graphs, insights)                 │
├──────────┴────────────────────────────────────────────────────┤
│  BOTTOM STATUS BAR (camera · FPS · AI status · session timer)  │
└───────────────────────────────────────────────────────────────┘
                                   [ NOTIFICATIONS float top-right ]
```

## 6.2 Top Navigation Bar
- Fixed, full width, height ~64px, `--surface` with a hairline bottom border; becomes
  a glass surface on scroll.
- Left: collapse-sidebar control + current breadcrumb/page name.
- Centre (optional): global search field with a leading search icon, pill-shaped.
- Right: **session indicator** (live dot + elapsed time), **theme toggle**
  (sun/moon), **notifications bell** (with unread badge), and **profile/avatar** with
  a dropdown.

## 6.3 Header Area
- Sits at the top of each page's content. Carries the page H1, a one-line secondary
  subtitle, and the page's primary action(s) aligned right (e.g. *Start Session*,
  *Export*).
- A subtle brand-gradient wash bleeds behind the header text for the dashboard's hero.

## 6.4 Main Content Area
- The workspace. Uses the 12-column grid; content is organised into cards and panels
  with consistent 24px gutters and generous whitespace.

## 6.5 Analytics Panel
- A dedicated region (within Dashboard and the Analytics page) hosting live graphs and
  trend summaries. Visually grouped, with section titles and legends.

## 6.6 Bottom Status Bar
- Fixed, slim (~36px), `--surface`. A live operational readout: camera status dot,
  resolution, live FPS, AI pipeline health, and the session timer. Always visible so
  the operator never loses situational awareness.

## 6.7 Notifications Area
- Top-right stack of glass toast cards (E4), newest on top, auto-dismissing, with
  manual dismiss. Never blocks primary content.

## 6.8 Footer
- Minimal, low-emphasis: product name + version, copyright, and links (Help, About,
  Settings). Present on static/settings pages; suppressed on live monitoring to keep
  the dashboard immersive.

---

# 7. SIDEBAR DESIGN

## 7.1 Structure (top → bottom)
1. **Brand block** — project logo mark + wordmark "EduSense AI 360", with the
   product tagline in `--text-muted` beneath when expanded.
2. **Primary navigation** — Dashboard, Live Monitor, Student Insights, Teacher
   Insights, Analytics, Reports, Settings — each a row with an outline icon + label.
3. **Spacer.**
4. **User information area** — avatar, name/role (e.g. "Teacher · Class 8B"),
   pinned to lower section.
5. **Footer row** — Settings shortcut (gear) + software version label.

## 7.2 Behaviour & States
- **Active item:** brand-tinted background pill, brand-coloured icon and label, and a
  3px brand accent bar on the leading edge.
- **Hover:** `--hover-overlay` background, icon brightens, smooth 150ms transition.
- **Collapse:** toggles between expanded (icon + label, ~248px) and rail (icon-only,
  ~76px). Labels fade out; tooltips appear on hover in rail mode. State persists.
- **Logo:** in rail mode, collapses to the logo mark only.
- Sidebar uses `--surface` with a hairline right border; subtle inner top-edge
  highlight for depth.

---

# 8. MAIN DASHBOARD

The dashboard is the product's centrepiece and must look immediately premium.

## 8.1 Layout (desktop, 12-col)
- **Row 0 — Dashboard Header:** large H1 "Classroom Engagement", subtitle with session
  name and live status; right-aligned *Start / Stop Session* primary button and a
  *Switch Camera* secondary control.
- **Row 1 — KPI strip:** a horizontal row of analytics cards (Attention %, Emotion,
  Engagement %, Focus Score, Session Duration, AI Confidence) — each 2–3 columns.
- **Row 2 — Live + Status:**
  - Left (8 cols): **Live Webcam panel** with engagement overlays.
  - Right (4 cols): a stacked column of **Overall Status**, **Current AI Prediction**,
    and **System Health** cards.
- **Row 3 — Insights:** **Student Remark Card** and **Teacher Remark Card** side by
  side, each summarising the latest AI-generated remark with a "view more" affordance.
- **Row 4 — Analytics summary:** compact engagement timeline + emotion distribution
  preview, linking through to the full Analytics page.

## 8.2 Dashboard Header
- Brand-gradient wash behind the title; the live **session timer** and a pulsing live
  dot sit inline with the subtitle. The primary CTA is the most prominent element on
  the page when no session is running.

## 8.3 Design Qualities
- Strong alignment to the grid; consistent card heights within a row.
- Professional whitespace — cards breathe; nothing is cramped.
- A single clear focal hierarchy: Engagement % is the largest, brightest metric.

---

# 9. WEBCAM PANEL

## 9.1 Composition
- A large rounded frame (`--radius-xl`) containing the live feed, with a refined 1px
  inner border and a soft outer shadow. A thin brand-gradient ring may frame the feed
  when a session is **live** to signal active analysis.
- AI overlays render on top of the feed: per-student bounding regions coloured along
  the engagement scale, compact ID + engagement labels, and an alert glyph on
  prolonged inattention.

## 9.2 Status & Indicators (overlaid, top corners)
- **Recording / Live indicator:** a pulsing dot + "LIVE" pill, top-left.
- **Camera status:** connected/disconnected chip with semantic colour.
- **FPS indicator:** small mono-numeral readout, top-right.
- **Resolution:** shown beside FPS (e.g. "1280×720").
- **Connection status:** reflected in the chip and bottom status bar.

## 9.3 Camera Controls
- A slim control bar beneath the feed: Start/Stop, Switch Camera (dropdown),
  Snapshot, and a Settings shortcut. Controls use secondary button styling and reveal
  on hover/focus to keep the feed uncluttered, while remaining keyboard reachable.

## 9.4 Empty / Error States
- No camera: a centred illustration + message + *Connect Camera* action.
- Disconnected mid-session: dimmed last frame with an overlay spinner and
  "Reconnecting…" message.

---

# 10. ANALYTICS / KPI CARDS

## 10.1 Card Anatomy
Each KPI card contains: a leading **icon** in a tinted rounded square, a **label**
(muted, uppercase-ish), a large **value** with unit, a one-line **description**, and a
**trend indicator** (small arrow + delta, coloured by direction). Cards sit on
`--card` with `--shadow-e1` and `--radius-lg`.

## 10.2 Specified KPI Cards
Attention % · Emotion · Engagement % · Focus Score · Session Duration · AI Confidence ·
Current Status · Number of Alerts.

- **Emotion card** shows the current dominant emotion as a coloured badge (per §3.6)
  plus a tiny emoji-free emotion glyph.
- **Engagement %** is the visual anchor — largest value, with the engagement-scale
  colour applied to the value and a thin progress arc/bar beneath.
- **Alerts** card turns to `--warning`/`--danger` accent when alerts are non-zero.

## 10.3 Card Interactions
- **Hover:** lift to E2, background to `--card-hover`, 150ms ease; trend indicator may
  animate.
- **Value updates:** numbers transition via a brief count/cross-fade so live changes
  feel smooth, never jumpy (tabular figures prevent width shift).
- **Trend indicator:** ▲ up in `--success`, ▼ down in `--danger`, ▬ flat in
  `--text-muted`, each with the delta value.

---

# 11. GRAPH / VISUALISATION SECTION

## 11.1 Graphs Provided
Engagement Timeline · Emotion Timeline · Attention Timeline · Focus Trend · Session
Analytics · Emotion Distribution · Average Engagement · Performance Summary.

## 11.2 Chart Styling
- **Lines:** 2px, brand/series colours, smooth curves, rounded caps; subtle area
  gradient fill under primary lines (`--chart-area-fill`).
- **Distribution/bars:** rounded bar tops, series-coloured, slim, with comfortable gaps.
- **Emotion distribution:** donut or stacked bar using the fixed emotion palette.
- **Grid:** faint (`--chart-grid`), horizontal-only where possible for calm.
- **Axes:** thin, muted labels in Graph Label style; minimal tick density.
- **Legends:** chip-style, top or right, with series colour swatches; clickable to
  toggle series.
- **Tooltips:** glass card with the timestamp/category, series colour dot, and value;
  follows the cursor with a soft fade.
- **Animation:** lines draw-in and bars grow on first render (~400–600ms ease-out);
  live charts append smoothly without full redraw.
- **Zoom & pan:** supported on timelines (drag-to-zoom, reset control).
- **Export:** each chart offers an export/download affordance (image/data).

## 11.3 States
- **Empty:** centred hint "Run a session to see analytics" with a faint placeholder grid.
- **Sparse:** renders gracefully; no broken axes.

---

# 12. STUDENT INSIGHTS PANEL

## 12.1 Content
Current Emotion · Current Attention · Engagement Level · Learning Pattern ·
Distraction Level · Personalised Remark · Risk Indicator · Improvement Suggestions.

## 12.2 Layout
- A panel header with a student selector (when multiple students are tracked) showing
  the student's ID/avatar.
- A two-column arrangement of compact stat rows (Emotion, Attention, Engagement Level,
  Distraction) on the left, and a **remark block** on the right with the personalised,
  supportive remark in Body Large.
- A **Risk Indicator** as a coloured pill (Low/Moderate/High) using semantic colours,
  phrased supportively and never stigmatising.
- **Improvement Suggestions** as a short, friendly bulleted list with leading check
  icons.
- A small **learning-pattern sparkline** showing the student's engagement trend.

## 12.3 Tone
All copy is constructive and non-clinical; sensitive states are framed as
"worth attention," never as diagnoses.

---

# 13. TEACHER INSIGHTS PANEL

## 13.1 Content
Class Engagement · Average Attention · Attention Trend · Attention Drop Points ·
AI Suggestions · Teaching Insights · Interaction Suggestions · Overall Session
Analysis.

## 13.2 Layout
- A summary band of class-level metrics (Average Engagement, Average Attention, Trend
  chip).
- An **attention timeline** with **drop points** marked as labelled annotations
  (e.g. "Dip at 20:00"), so observations are time-anchored.
- **AI Suggestions / Interaction Suggestions** as professional suggestion cards, each
  with an icon, a one-line action ("Increase interaction"), and a brief rationale.
- An **Overall Session Analysis** card with a short narrative summary.

## 13.3 Tone & Policy (reinforced from Part 1B)
This panel analyses **classroom engagement patterns**, never the teacher. All language
is constructive, impersonal, and unbiased — supportive guidance, not evaluation.

---

# 14. REPORT PANEL

## 14.1 Layout
- **Left:** a live **report preview** rendered as a document-like card (session header,
  stats, charts, remarks) so the user sees exactly what they'll export.
- **Right:** an **actions column** — *Export PDF*, *Export Excel*, *Export CSV*,
  *Print*, *Download* — as clearly grouped buttons with format icons; primary export is
  emphasised.
- **Below:** **Report History** — a list/table of previously generated files
  (name, date, format, size) with quick re-download and open actions.

## 14.2 Report Contents (visualised in preview)
Date · Time · Session Duration · Average Engagement · Emotion Statistics · Attention
Statistics · Teacher Remarks · Student Remarks · Charts · Summary.

## 14.3 States & Feedback
- Export disabled until session data exists, with an explanatory tooltip.
- On export: inline progress, then a success toast with a download affordance.
- On failure: clear error toast; existing data preserved.

---

# 15. SETTINGS PAGE

## 15.1 Structure
A two-pane layout: a left settings-category list (Appearance, Camera, AI Thresholds,
Graphs, Export, Dashboard, Language, Reset) and a right detail pane of grouped
controls in cards.

## 15.2 Settings Groups
- **Appearance:** Theme selection (Dark/Light/System), accent preference.
- **Camera:** Camera selection, Resolution, Frame Rate.
- **AI Thresholds:** detection confidence, eye-openness, gaze tolerance, distraction
  threshold, prolonged-inattention duration, engagement weights and band boundaries —
  presented with sliders/inputs, sensible ranges, and helper captions.
- **Graph Preferences:** default chart types, smoothing, animation on/off.
- **Export Preferences:** default format, export location.
- **Dashboard Preferences:** visible cards, refresh rate, layout density.
- **Language.**
- **Reset Settings** (with confirm) and **Save Settings**.

## 15.3 Behaviour
- Controls validate inline; invalid values are blocked with a clear message and the
  prior valid value retained.
- A sticky footer shows *Save* / *Discard* when unsaved changes exist.
- Destructive actions (Reset) require confirmation via a modal.

---

# 16. NOTIFICATIONS

## 16.1 Types & Treatment
Success · Warning · Error · Information · Loading · Processing · AI Analysis Complete ·
Export Complete · Camera Connected · Camera Disconnected.

Each toast is a glass card (E4) with: a leading status icon in its semantic colour, a
bold title, an optional one-line description, an optional action link, and a dismiss
control. A thin coloured accent bar on the leading edge encodes type at a glance.

## 16.2 Behaviour
- Appear top-right, slide-in + fade (~200ms), stack newest-on-top.
- Auto-dismiss after a sensible duration (errors persist until dismissed).
- Loading/Processing toasts show an animated indicator and convert to Success/Error on
  completion (e.g. "Generating report…" → "Export complete").
- Non-blocking; never cover the live feed's critical overlays.

---

# 17. LOADING EXPERIENCE

## 17.1 Splash Screen
On launch: a centred brand mark on `--bg` with the brand gradient subtly animating, the
product name, and a slim indeterminate progress bar plus a status line ("Initialising
AI modules…"). Calm, premium, brief.

## 17.2 Loading Patterns
- **AI loading:** a tasteful animated AI glyph (pulsing nodes) with status text while
  models initialise.
- **Camera loading:** webcam frame shows a shimmer placeholder + "Connecting to
  camera…" until the first valid frame arrives.
- **Dashboard / data loading:** **skeleton screens** — cards and charts render as soft
  shimmering placeholders matching their final shape, avoiding layout shift.
- **Progress indicators:** determinate bars for known tasks (exports), indeterminate
  for unknown (model load).

## 17.3 Principles
Loading never shows a blank screen; it always communicates progress and preserves
layout via skeletons.

---

# 18. RESPONSIVENESS

## 18.1 Breakpoints & Layouts
| Target | Width | Layout behaviour |
|---|---|---|
| **Desktop** | ≥1440px | Full shell, expanded sidebar, multi-column dashboard |
| **Laptop** | 1024–1439px | Expanded or rail sidebar, slightly tighter gutters, KPI strip wraps to 2 rows if needed |
| **Tablet** | 768–1023px | Sidebar collapses to rail/drawer, cards stack to 1–2 columns, graphs full-width, webcam above status cards |
| **Small** | <768px | Single-column, sidebar as overlay drawer, condensed status bar |

## 18.2 Adaptive Components
- KPI cards reflow from a row to a wrapped grid then to a single column.
- The webcam panel scales to container width, maintaining aspect ratio.
- Graphs become full-width and reduce label density on smaller screens.
- The bottom status bar condenses to essential indicators on narrow widths.

## 18.3 Scaling & Resolution
- Layout uses fluid units and the spacing scale so it scales cleanly with zoom/DPI.
- **Minimum supported resolution:** 1280×720.
- **Recommended resolution:** 1920×1080 for the full premium experience.

---

# 19. USER EXPERIENCE & INTERACTION

## 19.1 Navigation Flow
Sidebar drives top-level navigation (Dashboard ↔ Live Monitor ↔ Insights ↔ Analytics
↔ Reports ↔ Settings). Transitions between sections are quick cross-fades; the active
section is always clearly indicated. A typical flow: open app → select camera → start
session on Dashboard → monitor live → review Analytics/Insights → export Report.

## 19.2 Interaction & Click Behaviour
- Buttons give immediate visual feedback (hover lift, pressed state, focus ring).
- Primary actions are always the most prominent; destructive actions are visually
  distinct and confirmation-gated.
- Cards that link deeper show a clear affordance (chevron / "view more").

## 19.3 Hover & Transitions
- Hover states are subtle and consistent (overlay wash, slight lift, icon brighten).
- Standard transition timing: 150–200ms for state, 250–300ms for view changes, all on
  gentle ease curves. Motion respects a reduced-motion preference and disables
  non-essential animation when requested.

## 19.4 Loading Feedback
Every asynchronous action provides immediate feedback (button spinner, skeleton, or
toast). The user is never left uncertain whether an action registered.

## 19.5 Accessibility
- Colour contrast meets accessibility guidance for text and essential UI in both themes.
- Status is never conveyed by colour alone — always paired with an icon and/or label.
- Visible, high-contrast focus rings on all interactive elements.
- Respect reduced-motion and theme preferences.
- Meaningful labels for all controls and data regions for assistive technology.

## 19.6 Keyboard Navigation
- Full keyboard operability: logical tab order, Enter/Space to activate, Esc to close
  overlays, arrow keys within menus/sliders.
- Shortcut affordances for frequent actions (e.g. start/stop session, switch tab) where
  the platform allows.

## 19.7 Ease of Use
The product favours recognition over recall: clear labels, consistent placement, and
sensible defaults. A first-time user can start a session and read engagement within
moments, without instruction.

---

# 20. ICONOGRAPHY

## 20.1 Style
A single **professional outline icon set** with consistent stroke weight (~1.75px),
rounded joins, and a uniform optical size. Icons are never decorative-cartoonish.
Default colour `--text-secondary`; active `--text-primary`; status icons take semantic
colours. Icons in KPI cards sit inside tinted rounded squares.

## 20.2 Icon Assignments
| Concept | Icon (outline) |
|---|---|
| Camera | camera / video |
| Eye / Attention | eye |
| Emotion | smile / face |
| Graph / Analytics | line-chart / bar-chart |
| Dashboard | grid / layout |
| Reports | document / file-text |
| Teacher | presenter / mortarboard |
| Student | user / users |
| Settings | gear |
| Notifications | bell |
| Export | download / share |
| AI | sparkle / brain / node-network |
| Status: connected | check-circle |
| Status: disconnected | alert-triangle |
| Live | record dot |
| Timer | clock |

Icons always pair with a text label except where context is unambiguous (e.g. theme
toggle), and never carry meaning by shape alone in critical status contexts.

---

# 21. DESIGN PRINCIPLES (SUMMARY)

EduSense AI 360 must resemble a **premium enterprise AI analytics platform** — elegant,
minimal, modern, and highly professional. It must never resemble a simple student
project. Every screen upholds: strict consistency via tokens, generous whitespace, a
single clear focal point, restrained colour, meaningful motion, and data presented with
clarity and confidence. The result should make the viewer assume the software is an
expensive commercial product.

---

## END OF PART 2 — UI / UX DESIGN SPECIFICATION

This part fully specifies the visual language, design system, layout, components,
motion, responsiveness, and user experience of EduSense AI 360, ready to guide
frontend development. Subsequent parts may cover data design, integration, and test
specifications.
