"""
EduSense AI 360 - Theme & Styling
=================================

Ports the approved dashboard design (`edusense_dashboard_mockup.html`) into the
Gradio application: the dark palette, brand gradients, sidebar, gauge, cards,
typography (Space Grotesk display + Inter body), spacing, and responsive layout.

Strategy: the custom panels (sidebar, gauge, KPI cards, student cards, teacher
panel, status, engagement graph) are rendered as HTML/SVG inside ``gr.HTML`` blocks,
so this stylesheet controls them faithfully. Native Gradio widgets (webcam, buttons,
inputs, plots) are restyled best-effort and the default block chrome is reset for the
elements we drive ourselves.

The CSS is a module constant (imports without Gradio); :func:`build_theme`
constructs the Gradio theme lazily.
"""

from __future__ import annotations

from typing import Any

TOKENS = {
    "brand": "#6366F1", "brand_strong": "#4F46E5", "secondary": "#22D3EE",
    "amber": "#FBBF24", "mint": "#34D399", "rose": "#F87171", "violet": "#A78BFA",
    "ink": "#0B1020", "surface": "#0E1424", "card": "#141A2E", "card_hover": "#1B2236",
    "border": "rgba(255,255,255,.08)", "text": "#F8FAFC", "text_2": "#9AA6BE", "muted": "#5E6A84",
}

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root{
  --ink:#0B1020; --ink-2:#0E1424; --panel:#141A2E; --panel-2:#1B2236;
  --line:rgba(255,255,255,.08); --line-2:rgba(255,255,255,.14);
  --brand:#6366F1; --brand-soft:rgba(99,102,241,.16); --teal:#22D3EE;
  --amber:#FBBF24; --mint:#34D399; --rose:#F87171; --violet:#A78BFA;
  --text:#F8FAFC; --text-2:#9AA6BE; --muted:#5E6A84; --r:16px;
}

/* ---------- Base / Gradio resets ---------- */
.gradio-container{
  max-width:100% !important; padding:0 !important;
  font-family:'Inter',system-ui,sans-serif !important; color:var(--text) !important;
  background:
    radial-gradient(1200px 600px at 80% -10%, rgba(99,102,241,.10), transparent 60%),
    radial-gradient(900px 500px at -10% 110%, rgba(34,211,238,.07), transparent 55%),
    var(--ink) !important;
}
.gradio-container .es-flush, .gradio-container .es-flush > *{
  background:transparent !important; border:none !important; box-shadow:none !important;
  padding:0 !important; margin:0 !important;
}
footer{display:none !important;}
.num{font-family:'Space Grotesk','Inter',sans-serif; font-variant-numeric:tabular-nums; letter-spacing:-.01em;}

/* ---------- App shell ---------- */
.es-app{gap:0 !important; align-items:stretch !important; flex-wrap:nowrap !important;}
.es-side{
  flex:0 0 244px !important; min-width:244px !important; max-width:244px !important;
  background:linear-gradient(180deg,var(--ink-2),var(--ink)); border-right:1px solid var(--line);
  padding:20px 14px !important; gap:4px !important; min-height:100vh;
}
.es-main{padding:20px 26px 34px !important; gap:14px !important; min-width:0 !important; max-width:1340px;}

/* ---------- Sidebar ---------- */
.es-brand{display:flex;align-items:center;gap:11px;padding:2px 8px 16px;}
.es-logo{width:38px;height:38px;border-radius:11px;background:linear-gradient(135deg,var(--brand),var(--teal));
  display:grid;place-items:center;box-shadow:0 6px 18px rgba(99,102,241,.35);flex:none;}
.es-brand h1{font-family:'Space Grotesk';font-size:15.5px;font-weight:700;line-height:1.05;margin:0;}
.es-brand span{font-size:10px;color:var(--muted);letter-spacing:.05em;text-transform:uppercase;}
.es-nav button{
  width:100% !important; display:flex !important; align-items:center; justify-content:flex-start !important;
  gap:11px; padding:10px 12px !important; border-radius:11px !important; color:var(--text-2) !important;
  font-size:13.5px !important; font-weight:500 !important; background:transparent !important;
  border:none !important; box-shadow:none !important; text-align:left !important; min-height:0 !important;
  transition:background .15s,color .15s;
}
.es-nav button:hover{background:rgba(255,255,255,.05) !important; color:var(--text) !important;}
.es-nav.on button{background:var(--brand-soft) !important; color:#fff !important;}
.es-sidefoot{display:flex;align-items:center;gap:10px;padding:12px 8px;border-top:1px solid var(--line);margin-top:8px;}
.es-avatar{width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--violet),var(--brand));
  display:grid;place-items:center;font-size:12px;font-weight:700;flex:none;}
.es-sidefoot small{display:block;color:var(--muted);font-size:10px;}

/* ---------- Topbar ---------- */
.es-topbar{align-items:center !important; justify-content:space-between; gap:14px !important; flex-wrap:wrap;}
.es-ctx{display:flex;align-items:center;gap:12px;flex-wrap:wrap;}
.es-ctx h2{font-family:'Space Grotesk';font-size:20px;font-weight:600;margin:0;}
.es-live{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:600;color:var(--mint);
  background:rgba(52,211,153,.12);padding:5px 11px;border-radius:999px;}
.es-live.idle{color:var(--muted);background:rgba(255,255,255,.05);}
.es-dot{width:8px;height:8px;border-radius:50%;background:var(--mint);animation:espulse 1.8s infinite;}
.es-live.idle .es-dot{background:var(--muted);animation:none;}
@keyframes espulse{0%{box-shadow:0 0 0 0 rgba(52,211,153,.55)}70%{box-shadow:0 0 0 9px rgba(52,211,153,0)}100%{box-shadow:0 0 0 0 rgba(52,211,153,0)}}
.es-chip{font-size:12px;color:var(--text-2);background:var(--panel);border:1px solid var(--line);padding:6px 12px;border-radius:999px;}
.es-chip b{color:var(--text);font-weight:600;}
.es-demobadge{font-size:11px;font-weight:700;letter-spacing:.05em;color:#0B1020;background:var(--amber);padding:5px 10px;border-radius:999px;}

/* ---------- Buttons ---------- */
.es-btn button{
  background:var(--brand) !important; color:#fff !important; border:none !important; border-radius:11px !important;
  font-weight:600 !important; font-size:13px !important; box-shadow:0 4px 14px rgba(99,102,241,.25) !important;
}
.es-btn button:hover{filter:brightness(1.08);}
.es-btn-ghost button{
  background:var(--panel) !important; color:var(--text-2) !important; border:1px solid var(--line-2) !important;
  border-radius:11px !important; font-weight:600 !important; font-size:13px !important; box-shadow:none !important;
}

/* ---------- Cards ---------- */
.es-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);
  box-shadow:0 1px 2px rgba(0,0,0,.3),0 10px 30px rgba(0,0,0,.18);}
.es-card:hover{border-color:var(--line-2);}
.es-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;}

/* hero: gauge + kpis */
.es-hero{gap:14px !important; align-items:stretch !important; flex-wrap:nowrap !important;}
.es-gaugecol{flex:0 0 300px !important; min-width:280px !important;}
.es-kpicol{flex:1 1 auto !important; min-width:0 !important;}
.es-gauge-card{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:20px;
  display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;height:100%;}
.es-gauge{position:relative;width:220px;height:220px;}
.es-gauge svg{transform:rotate(135deg);width:220px;height:220px;}
.es-gtrack{fill:none;stroke:rgba(255,255,255,.07);stroke-width:16;stroke-linecap:round;}
.es-gval{fill:none;stroke:url(#esEng);stroke-width:16;stroke-linecap:round;
  transition:stroke-dasharray .7s cubic-bezier(.22,1,.36,1);}
.es-gcenter{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.es-gbig{font-family:'Space Grotesk';font-size:54px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums;}
.es-gsub{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;margin-top:2px;}
.es-glevel{font-size:13px;font-weight:600;padding:5px 14px;border-radius:999px;margin-top:4px;display:inline-block;}
.es-gcap{font-size:11.5px;color:var(--text-2);text-align:center;max-width:230px;}

.es-kpi{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:15px;}
.es-kpi .top{display:flex;align-items:center;justify-content:space-between;margin-bottom:7px;}
.es-kpi .label{font-size:11px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);}
.es-kpi .iconbox{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;background:rgba(255,255,255,.04);}
.es-kpi .v{font-size:28px;font-weight:700;line-height:1.05;font-family:'Space Grotesk';font-variant-numeric:tabular-nums;}
.es-kpi .d{font-size:11.5px;color:var(--text-2);margin-top:3px;}

/* ---------- Feed / webcam ---------- */
.es-grid2{gap:14px !important; align-items:stretch !important; flex-wrap:wrap !important;}
.es-feedcol{flex:1.55 1 0 !important; min-width:340px !important; gap:8px !important;}
.es-studcol{flex:1 1 0 !important; min-width:300px !important;}
.es-feedbar{display:flex;align-items:center;justify-content:space-between;padding:11px 15px;
  background:var(--panel);border:1px solid var(--line);border-bottom:none;border-radius:16px 16px 0 0;}
.es-feedbar .t{font-size:13px;font-weight:600;}
.es-feedbar .s{font-size:11px;color:var(--muted);}
.es-stage{border:1px solid var(--line) !important; border-radius:0 0 16px 16px !important; overflow:hidden !important;
  background:radial-gradient(120% 120% at 50% 0%, #1d2740, #0c1322 70%) !important; min-height:360px !important;}
.es-stage img{object-fit:contain !important; border-radius:0 0 16px 16px !important;}
.es-stage .image-frame, .es-stage .image-container{border:none !important; background:transparent !important;}
.es-source label{font-size:11px !important; color:var(--muted) !important;}
.es-source{flex:0 0 200px !important;}

/* ---------- Student cards ---------- */
.es-stu{display:flex;gap:11px;align-items:flex-start;padding:11px 12px;border-radius:12px;
  background:var(--ink-2);border-left:3px solid var(--brand);margin-bottom:9px;}
.es-stu.good{border-left-color:var(--mint);} .es-stu.warn{border-left-color:var(--amber);} .es-stu.bad{border-left-color:var(--rose);}
.es-stu .face{width:34px;height:34px;border-radius:9px;flex:none;background:linear-gradient(135deg,#27324d,#1a2236);
  display:grid;place-items:center;font-size:12px;font-weight:700;color:var(--text-2);}
.es-stu .body{flex:1;min-width:0;}
.es-stu .r1{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:3px;}
.es-stu .nm{font-size:13px;font-weight:600;}
.es-score{font-size:12px;font-weight:700;font-family:'Space Grotesk';}
.es-score.good{color:var(--mint);} .es-score.warn{color:var(--amber);} .es-score.bad{color:var(--rose);}
.es-emo{font-size:11px;color:var(--muted);}
.es-stu .rmk{font-size:12px;color:var(--text-2);line-height:1.45;}
.es-panelhead{font-size:13px;font-weight:600;margin-bottom:10px;}

/* ---------- Chart / graph ---------- */
.es-chart{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:16px;}
.es-chart .head{display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;}
.es-chart h3{font-size:13px;font-weight:600;margin:0;}
.es-legend{display:flex;gap:14px;font-size:11px;color:var(--text-2);}
.es-legend i{display:inline-block;width:9px;height:9px;border-radius:3px;margin-right:5px;vertical-align:-1px;}
.es-axis{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin-top:4px;}

/* ---------- Teacher panel ---------- */
.es-teach{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);padding:16px;}
.es-teach h3{font-size:13px;font-weight:600;margin:0 0 4px;display:flex;align-items:center;gap:8px;}
.es-teach .sub{font-size:11px;color:var(--muted);margin-bottom:10px;}
.es-obs{background:var(--ink-2);border-left:3px solid var(--teal);border-radius:9px;padding:9px 12px;
  margin:6px 0;font-size:12.5px;color:var(--text-2);}
.es-sugg{margin:6px 0 0 18px;color:var(--text-2);font-size:12.5px;}
.es-sugg li{margin:3px 0;}

/* ---------- Status indicators ---------- */
.es-status{display:flex;gap:10px;flex-wrap:wrap;}
.es-pill{display:inline-flex;align-items:center;gap:7px;font-size:12px;font-weight:600;padding:6px 12px;border-radius:999px;
  background:var(--panel);border:1px solid var(--line);color:var(--text-2);}
.es-pill .d2{width:7px;height:7px;border-radius:50%;}
.es-pill.ok .d2{background:var(--mint);} .es-pill.warn .d2{background:var(--amber);} .es-pill.bad .d2{background:var(--rose);}

/* ---------- Demo banner ---------- */
.es-demo-banner{background:linear-gradient(90deg, rgba(251,191,36,.16), rgba(99,102,241,.10));
  border:1px solid rgba(251,191,36,.30);border-radius:12px;padding:10px 14px;color:var(--text-2);font-size:13px;}
.es-demo-banner b{color:var(--amber);}

/* ---------- Section headers ---------- */
.es-hero-strip{background:linear-gradient(120deg,#6366F1 0%,#7C5CFC 45%,#22D3EE 100%);
  border-radius:18px;padding:18px 22px;}
.es-hero-strip h1{color:#fff;margin:0;font-family:'Space Grotesk';font-size:22px;font-weight:700;}
.es-hero-strip p{color:rgba(255,255,255,.85);margin:3px 0 0;font-size:12.5px;}

/* native inputs in settings tuned for dark */
.es-section .gr-box, .es-section .block{background:transparent;}

/* ===== Phase: presentation upgrade ===== */
/* Confidence badges */
.es-cbadge{display:inline-block;margin-top:7px;font-size:10.5px;font-weight:600;color:#22D3EE;
  background:rgba(34,211,238,.10);border:1px solid rgba(34,211,238,.22);padding:3px 9px;border-radius:999px;}
.es-cbadge.na{color:#7C89A6;background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.08);}
.es-kpi .u{font-size:15px;color:var(--text-2);}

/* Detection KPI (replaces Students in Frame) */
.es-detect{grid-column:span 2;}
.es-dgrid{display:grid;grid-template-columns:1fr 1fr;gap:9px 16px;margin-top:7px;}
.es-dgrid .dl{display:block;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;}
.es-dgrid .dv{display:block;font-size:20px;font-weight:700;font-family:'Space Grotesk';line-height:1.15;}

/* Student cards: 4-tier status + sub-metrics */
.es-roster{padding:16px;}
.es-stu.exc{border-left-color:var(--mint);} .es-stu.good{border-left-color:#60A5FA;}
.es-stu.mod{border-left-color:var(--amber);} .es-stu.need{border-left-color:var(--rose);}
.es-stat{font-size:11px;font-weight:700;padding:2px 9px;border-radius:999px;}
.es-stat.exc{color:var(--mint);background:rgba(52,211,153,.14);}
.es-stat.good{color:#60A5FA;background:rgba(96,165,250,.14);}
.es-stat.mod{color:var(--amber);background:rgba(251,191,36,.14);}
.es-stat.need{color:var(--rose);background:rgba(248,113,113,.14);}
.es-stu .r2{display:flex;gap:12px;flex-wrap:wrap;margin:2px 0 5px;}
.es-mini{font-size:11px;color:var(--text-2);}
.es-mini b{color:var(--text);font-weight:600;font-family:'Space Grotesk';}

/* Teacher insights + recommendations rows */
.es-ins,.es-rec{display:flex;align-items:flex-start;gap:9px;background:var(--ink-2);border-radius:9px;
  padding:9px 12px;margin:6px 0;font-size:12.5px;color:var(--text-2);border-left:3px solid #60A5FA;}
.es-ins svg,.es-rec svg{flex:none;margin-top:1px;}
.es-ins.ok{border-left-color:var(--mint);} .es-ins.warn{border-left-color:var(--amber);} .es-ins.info{border-left-color:#60A5FA;}
.es-rec{border-left-color:var(--amber);}

/* Global AI confidence card */
.es-aiconf .es-aibig{font-family:'Space Grotesk';font-size:34px;font-weight:700;line-height:1;margin:6px 0 2px;
  display:flex;align-items:baseline;gap:9px;color:var(--mint);font-variant-numeric:tabular-nums;}
.es-aiconf .es-aibig span{font-size:10.5px;color:var(--muted);font-weight:500;text-transform:uppercase;letter-spacing:.06em;}
.es-bar{height:7px;border-radius:999px;background:rgba(255,255,255,.07);overflow:hidden;margin:8px 0 12px;}
.es-bar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--teal),var(--mint));transition:width .5s ease;}
.es-arow{display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-top:1px solid var(--line);font-size:12.5px;}
.es-arow .al{color:var(--text-2);}
.es-arow .av{display:flex;align-items:center;gap:7px;font-weight:600;color:var(--text);}
.es-arow .ad{width:7px;height:7px;border-radius:50%;}
.es-arow .ad.ok{background:var(--mint);} .es-arow .ad.warn{background:var(--amber);} .es-arow .ad.bad{background:var(--rose);}

/* Three-card insight row */
.es-grid3{gap:14px !important;align-items:stretch !important;flex-wrap:wrap !important;}
.es-grid3 > *{flex:1 1 300px !important;min-width:280px !important;}

/* Larger webcam feed (#3) */
.es-stage{min-height:436px !important;}

/* Visual polish (#8): consistent hover lift, softer shadows, smooth transitions */
.es-card,.es-kpi,.es-gauge-card,.es-teach,.es-aiconf,.es-chart,.es-roster{
  transition:border-color .16s ease, transform .16s ease, box-shadow .16s ease;}
.es-card:hover,.es-kpi:hover,.es-gauge-card:hover,.es-teach:hover,.es-aiconf:hover,.es-chart:hover{
  transform:translateY(-2px);box-shadow:0 8px 26px rgba(0,0,0,.30);border-color:var(--line-2);}
.es-kpi .iconbox svg{display:block;}

/* ============================================================
   FINAL POLISH PHASE — premium dashboard components
   ============================================================ */

/* Animated gauge (sweep + glow, only on demo/initial mount) */
@keyframes esSweep { from { stroke-dasharray: 0 565.5; } }
@keyframes esPop   { from { opacity:0; transform:scale(.9); } to { opacity:1; transform:scale(1); } }
@keyframes esGlowPulse { 0%,100%{ filter:drop-shadow(0 0 3px rgba(99,102,241,.35)); } 50%{ filter:drop-shadow(0 0 9px rgba(99,102,241,.6)); } }
.es-animon .es-gval { animation: esSweep 1.15s cubic-bezier(.22,1,.36,1); }
.es-animon .es-gbig { animation: esPop .55s ease both; }
.es-gauge svg { transform:rotate(135deg); width:220px; height:220px; }
.es-gval { will-change: stroke-dasharray; }
.es-gstatus { font-size:11.5px; color:var(--text-2); margin-top:5px; text-align:center; max-width:230px; }

/* Live status ribbon */
.es-ribbon { display:flex; flex-wrap:wrap; gap:8px; padding:2px 0; }
.es-rib { display:inline-flex; align-items:center; gap:7px; font-size:11.5px; font-weight:600;
  padding:6px 12px; border-radius:999px; background:var(--panel); border:1px solid var(--line); color:var(--text-2); }
.es-ribdot { width:7px; height:7px; border-radius:50%; flex:none; }
.es-rib.ok{color:#CFFCE8;} .es-rib.ok .es-ribdot{background:var(--mint); animation:espulse 2s infinite;}
.es-rib.warn{color:#FDEFC7;} .es-rib.warn .es-ribdot{background:var(--amber);}
.es-rib.bad{color:#FED7D7;} .es-rib.bad .es-ribdot{background:var(--rose); animation:espulse 1.4s infinite;}

/* AI processing pipeline */
.es-pipewrap { padding:16px 18px; }
.es-pipehead { font-size:13px; font-weight:600; display:flex; align-items:center; gap:8px; margin-bottom:12px; }
.es-pipesub { color:var(--muted); font-weight:400; font-size:11.5px; margin-left:6px; }
.es-pipe { display:flex; align-items:stretch; gap:4px; overflow-x:auto; padding-bottom:4px; }
.es-pnode { flex:1 1 0; min-width:96px; display:flex; flex-direction:column; align-items:center; gap:5px;
  background:var(--ink-2); border:1px solid var(--line); border-radius:12px; padding:11px 8px; text-align:center; }
.es-pnode .es-pic { width:34px; height:34px; border-radius:10px; display:grid; place-items:center;
  background:rgba(255,255,255,.04); color:var(--muted); }
.es-pnode.on .es-pic { color:#fff; background:linear-gradient(135deg,var(--brand),var(--teal));
  box-shadow:0 0 0 0 rgba(99,102,241,.5); animation:espulse 2.2s infinite; }
.es-pname { font-size:11px; font-weight:600; color:var(--text); line-height:1.2; }
.es-pconf { font-size:10px; color:var(--muted); font-family:'Space Grotesk'; }
.es-pnode.on .es-pconf { color:var(--teal); }
.es-parrow { align-self:center; color:var(--muted); font-size:18px; flex:none; }

/* Webcam feed stats */
.es-feedstats { display:grid; grid-template-columns:repeat(6,1fr); gap:1px; background:var(--line);
  border:1px solid var(--line); border-radius:0 0 14px 14px; overflow:hidden; margin-top:-2px; }
.es-fs { background:var(--panel); padding:8px 10px; display:flex; flex-direction:column; gap:1px; }
.es-fs .fl { font-size:9.5px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; }
.es-fs .fv { font-size:13px; font-weight:700; font-family:'Space Grotesk'; color:var(--text); }
@media (max-width:760px){ .es-feedstats{ grid-template-columns:repeat(3,1fr); } }

/* Sparklines + trend chips */
.es-sparkrow { margin:7px 0 2px; height:30px; }
.es-spark { display:block; }
.es-trend { font-size:11px; font-weight:700; margin-right:5px; }
.es-trend.up{color:var(--mint);} .es-trend.down{color:var(--rose);} .es-trend.flat{color:var(--muted);}
.es-kpi .u{font-size:15px;color:var(--text-2);}

/* Detection KPI */
.es-detect{grid-column:span 2;}
.es-dgrid{display:grid;grid-template-columns:1fr 1fr;gap:9px 16px;margin-top:7px;}
.es-dgrid .dl{display:block;font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;}
.es-dgrid .dv{display:block;font-size:20px;font-weight:700;font-family:'Space Grotesk';line-height:1.15;}

/* Confidence badge */
.es-cbadge{display:inline-block;margin-top:7px;font-size:10.5px;font-weight:600;color:#22D3EE;
  background:rgba(34,211,238,.10);border:1px solid rgba(34,211,238,.22);padding:3px 9px;border-radius:999px;}
.es-cbadge.na{color:#7C89A6;background:rgba(255,255,255,.04);border-color:rgba(255,255,255,.08);}

/* Student cards: status, sub-metrics, progress, tip */
.es-roster{padding:16px;}
.es-stu.exc{border-left-color:var(--mint);} .es-stu.good{border-left-color:#60A5FA;}
.es-stu.mod{border-left-color:var(--amber);} .es-stu.need{border-left-color:var(--rose);}
.es-stat{font-size:11px;font-weight:700;padding:2px 9px;border-radius:999px;}
.es-stat.exc{color:var(--mint);background:rgba(52,211,153,.14);}
.es-stat.good{color:#60A5FA;background:rgba(96,165,250,.14);}
.es-stat.mod{color:var(--amber);background:rgba(251,191,36,.14);}
.es-stat.need{color:var(--rose);background:rgba(248,113,113,.14);}
.es-stu .r2{display:flex;gap:12px;flex-wrap:wrap;margin:2px 0 6px;}
.es-mini{font-size:11px;color:var(--text-2);}
.es-mini b{color:var(--text);font-weight:600;font-family:'Space Grotesk';}
.es-prog{height:6px;border-radius:999px;background:rgba(255,255,255,.07);overflow:hidden;margin:2px 0 7px;}
.es-prog i{display:block;height:100%;border-radius:999px;transition:width .6s ease;}
.es-tip{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--muted);margin-top:6px;}
.es-tip svg{flex:none;}

/* Teacher insights/recommendation rows */
.es-ins,.es-rec{display:flex;align-items:flex-start;gap:9px;background:var(--ink-2);border-radius:9px;
  padding:9px 12px;margin:6px 0;font-size:12.5px;color:var(--text-2);border-left:3px solid #60A5FA;}
.es-ins svg,.es-rec svg{flex:none;margin-top:1px;}
.es-ins.ok{border-left-color:var(--mint);} .es-ins.warn{border-left-color:var(--amber);} .es-ins.info{border-left-color:#60A5FA;}
.es-rec{border-left-color:var(--amber);}

/* Teacher dashboard (page) */
.es-tsummary{background:linear-gradient(120deg,#5b54e6,#7c5cfc 55%,#22d3ee);border:none;color:#fff;
  border-radius:16px;padding:18px 20px;margin-bottom:14px;}
.es-tsummary .es-tsec-h{color:#fff;}
.es-tsum-eng{font-family:'Space Grotesk';font-size:40px;font-weight:700;line-height:1;display:flex;align-items:baseline;gap:9px;margin:4px 0;}
.es-tsum-eng span{font-size:11px;font-weight:500;color:rgba(255,255,255,.8);text-transform:uppercase;letter-spacing:.06em;}
.es-tsum-txt{font-size:12.5px;color:rgba(255,255,255,.92);max-width:640px;}
.es-tgrid{display:grid;grid-template-columns:1fr 1fr;gap:14px;}
.es-tsec{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:15px;}
.es-tsec-h{font-size:12.5px;font-weight:700;display:flex;align-items:center;gap:8px;margin-bottom:9px;color:var(--text);}
.es-tnext{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:15px;margin-top:14px;}
.es-tnext-b{display:flex;align-items:center;gap:10px;font-size:13.5px;color:var(--text);font-weight:500;
  background:var(--ink-2);border-radius:10px;padding:11px 13px;margin-top:4px;}
@media (max-width:900px){ .es-tgrid{grid-template-columns:1fr;} }

/* Global AI confidence card */
.es-aiconf .es-aibig{font-family:'Space Grotesk';font-size:34px;font-weight:700;line-height:1;margin:6px 0 2px;
  display:flex;align-items:baseline;gap:9px;color:var(--mint);font-variant-numeric:tabular-nums;}
.es-aiconf .es-aibig span{font-size:10.5px;color:var(--muted);font-weight:500;text-transform:uppercase;letter-spacing:.06em;}
.es-bar{height:7px;border-radius:999px;background:rgba(255,255,255,.07);overflow:hidden;margin:8px 0 12px;}
.es-bar i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--teal),var(--mint));transition:width .5s ease;}
.es-arow{display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-top:1px solid var(--line);font-size:12.5px;}
.es-arow .al{color:var(--text-2);} .es-arow .av{display:flex;align-items:center;gap:7px;font-weight:600;color:var(--text);}
.es-arow .ad{width:7px;height:7px;border-radius:50%;}
.es-arow .ad.ok{background:var(--mint);} .es-arow .ad.warn{background:var(--amber);} .es-arow .ad.bad{background:var(--rose);}
.es-rstatus{display:flex;align-items:center;gap:8px;font-size:12px;font-weight:600;margin-bottom:8px;}
.es-rstatus .ad{width:7px;height:7px;border-radius:50%;} .es-rstatus.ok{color:var(--mint);} .es-rstatus.warn{color:var(--amber);}

/* Reports: session statistics grid */
.es-rstats{padding:16px;}
.es-rstatgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:8px;}
.es-rstat{display:flex;align-items:center;gap:11px;background:var(--ink-2);border:1px solid var(--line);border-radius:12px;padding:13px;}
.es-rstat .iconbox{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:rgba(255,255,255,.04);flex:none;}
.es-rstat .rv{font-size:20px;font-weight:700;font-family:'Space Grotesk';line-height:1.1;}
.es-rstat .rl{font-size:11px;color:var(--muted);}
@media (max-width:900px){ .es-rstatgrid{grid-template-columns:1fr 1fr;} }

/* Three-card insight row + section grids */
.es-grid3{gap:14px !important;align-items:stretch !important;flex-wrap:wrap !important;}
.es-grid3 > *{flex:1 1 300px !important;min-width:280px !important;}

/* Larger webcam feed */
.es-stage{min-height:444px !important;}

/* Typography hierarchy (#13) */
.es-hero-strip h1{font-size:23px;letter-spacing:-.01em;}
.es-panelhead{font-size:13px;font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:8px;}
.es-ctx h2{font-size:20px;letter-spacing:-.01em;}

/* Micro-animation: gentle section fade-in on mount (#15) */
@keyframes esFade { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:none; } }
.es-card,.es-gauge-card,.es-tsec,.es-tsummary,.es-tnext,.es-pipewrap{animation:esFade .35s ease both;}

/* Consistent hover lift, softer shadows */
.es-card,.es-kpi,.es-gauge-card,.es-teach,.es-aiconf,.es-chart,.es-roster,.es-rstat,.es-pnode{
  transition:border-color .16s ease, transform .16s ease, box-shadow .16s ease;}
.es-card:hover,.es-kpi:hover,.es-gauge-card:hover,.es-teach:hover,.es-aiconf:hover,.es-chart:hover{
  transform:translateY(-2px);box-shadow:0 8px 26px rgba(0,0,0,.30);border-color:var(--line-2);}
.es-rstat:hover,.es-pnode:hover{border-color:var(--line-2);}
.es-kpi .iconbox svg{display:block;}

/* Reports: generated files rows */
.es-filerow{display:flex;align-items:center;gap:11px;background:var(--ink-2);border:1px solid var(--line);
  border-radius:11px;padding:11px 13px;margin:7px 0;}
.es-filerow .iconbox{width:32px;height:32px;border-radius:9px;display:grid;place-items:center;background:rgba(255,255,255,.04);flex:none;}
.es-filerow .fmeta{flex:1;min-width:0;}
.es-filerow .fn{font-size:12.5px;font-weight:600;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.es-filerow .fd{font-size:11px;color:var(--muted);}

/* Settings: grouped cards */
.es-setcard{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px 18px;}
.es-setcard-h{display:flex;align-items:flex-start;gap:11px;margin-bottom:10px;}
.es-setcard-h .st{font-size:14px;font-weight:700;color:var(--text);}
.es-setcard-h .sd{font-size:11.5px;color:var(--muted);margin-top:1px;}
.es-sethint{font-size:11.5px;color:var(--muted);background:var(--ink-2);border-radius:9px;
  padding:9px 11px;margin-top:10px;border-left:3px solid var(--teal);}

/* Reports preview column reads as a card */
.es-reportprev{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px 18px;}
.es-reportprev .prose,.es-reportprev p{font-size:12.5px;color:var(--text-2);}

/* KPI grid (mockup .kpis: 2 columns) + student score/emotion */
.es-kpis{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;height:100%;}
.es-kpis .es-kpi{padding:16px;display:flex;flex-direction:column;}
.es-kpi .v.num{margin-top:0;}
.es-score{font-size:12px;font-weight:700;font-family:'Space Grotesk';font-variant-numeric:tabular-nums;}
.es-score.exc{color:var(--mint);} .es-score.good{color:#60A5FA;}
.es-score.mod{color:var(--amber);} .es-score.need{color:var(--rose);}
.es-emo{font-size:11px;color:var(--muted);}
/* ribbon pills exactly match mockup .pill weight/size */
.es-rib{font-size:12px;padding:6px 12px;}
@media (max-width:680px){ .es-kpis{grid-template-columns:1fr;} }

/* ============================================================
   LOGIN SCREEN (dark glassmorphism)
   ============================================================ */
.es-login{min-height:100vh;display:grid;place-items:center;padding:24px;width:100%;}
.es-logincard{width:100%;max-width:392px;background:rgba(18,24,42,.62);backdrop-filter:blur(20px);
  -webkit-backdrop-filter:blur(20px);border:1px solid var(--line-2);border-radius:22px;
  padding:30px 28px 24px;box-shadow:0 24px 70px rgba(0,0,0,.55),0 2px 0 rgba(255,255,255,.04) inset;
  animation:esLoginIn .5s cubic-bezier(.22,1,.36,1) both;display:flex;flex-direction:column;gap:12px;}
@keyframes esLoginIn{from{opacity:0;transform:translateY(14px) scale(.985);}to{opacity:1;transform:none;}}
.es-login-brand{text-align:center;margin-bottom:6px;}
.es-login-logo{width:64px;height:64px;border-radius:18px;margin:0 auto 14px;position:relative;
  background:linear-gradient(135deg,var(--indigo),var(--teal));display:grid;place-items:center;
  box-shadow:0 12px 30px rgba(99,102,241,.45);animation:esLogoFloat 3.4s ease-in-out infinite;}
@keyframes esLogoFloat{0%,100%{transform:translateY(0);box-shadow:0 12px 30px rgba(99,102,241,.40);}
  50%{transform:translateY(-4px);box-shadow:0 18px 40px rgba(99,102,241,.6);}}
.es-login-ring{position:absolute;inset:-6px;border-radius:22px;border:2px solid rgba(99,102,241,.5);
  animation:esRing 2.4s ease-out infinite;}
@keyframes esRing{0%{transform:scale(.92);opacity:.7;}100%{transform:scale(1.25);opacity:0;}}
.es-login-brand h1{font-family:'Space Grotesk';font-size:22px;font-weight:700;letter-spacing:-.01em;}
.es-login-brand p{font-size:12.5px;color:var(--text-2);margin-top:3px;}
.es-login-sub{font-size:11.5px;color:var(--muted);margin-top:10px;text-transform:uppercase;letter-spacing:.08em;}
.es-loginfield{background:transparent !important;}
.es-loginfield label,.es-loginfield label span{font-size:11.5px !important;font-weight:600 !important;
  color:var(--text-2) !important;text-transform:none !important;}
.es-loginfield input,.es-loginfield textarea{background:rgba(11,16,32,.6) !important;
  border:1px solid var(--line-2) !important;border-radius:11px !important;color:var(--text) !important;
  font-size:13.5px !important;padding:11px 13px !important;transition:border-color .15s, box-shadow .15s;}
.es-loginfield input:focus,.es-loginfield textarea:focus{border-color:var(--indigo) !important;
  box-shadow:0 0 0 3px rgba(99,102,241,.22) !important;outline:none !important;}
.es-loginopts{gap:10px !important;align-items:center !important;}
.es-loginopts label{font-size:12px !important;color:var(--text-2) !important;}
.es-loginbtn{width:100%;}
.es-loginbtn button{width:100% !important;padding:12px !important;font-size:14px !important;}
.es-login-err{font-size:12.5px;font-weight:600;color:#FCA5A5;background:rgba(248,113,113,.12);
  border:1px solid rgba(248,113,113,.3);border-radius:10px;padding:10px 12px;text-align:center;
  animation:esShake .4s;}
@keyframes esShake{0%,100%{transform:translateX(0);}25%{transform:translateX(-5px);}75%{transform:translateX(5px);}}
.es-login-ok{font-size:12.5px;font-weight:600;color:#86EFAC;background:rgba(52,211,153,.12);
  border:1px solid rgba(52,211,153,.3);border-radius:10px;padding:10px 12px;text-align:center;}
.es-login-hint{font-size:11px;color:var(--muted);text-align:center;background:rgba(255,255,255,.03);
  border:1px solid var(--line);border-radius:9px;padding:8px 10px;}
.es-login-hint b{color:var(--text-2);font-weight:600;}

/* ============================================================
   SIDEBAR polish + post-login profile card
   ============================================================ */
.es-navlabel{font-size:10px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;
  color:var(--muted);padding:10px 12px 4px;}
.es-profile{display:flex;gap:11px;align-items:flex-start;margin-top:auto;padding:14px 12px 4px;
  border-top:1px solid var(--line);}
.es-avatar.lg{width:38px;height:38px;border-radius:11px;flex:none;font-size:13px;
  background:linear-gradient(135deg,var(--violet),var(--indigo));}
.es-profmeta{flex:1;min-width:0;}
.es-profmeta .pn{font-size:13px;font-weight:700;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.es-profmeta .pr{font-size:10.5px;color:var(--muted);margin-bottom:6px;}
.es-profrow{display:flex;align-items:center;justify-content:space-between;font-size:11px;
  color:var(--muted);padding:2px 0;}
.es-profrow b{color:var(--text-2);font-weight:600;font-size:11px;max-width:120px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.es-nav button{transition:background .15s,color .15s,transform .1s !important;}
.es-nav button:active{transform:translateX(1px) !important;}

/* Session input always editable + on-brand */
.es-sessioninput input,.es-sessioninput textarea{background:var(--ink-2) !important;
  border:1px solid var(--line-2) !important;border-radius:11px !important;color:var(--text) !important;
  font-size:13px !important;padding:11px 13px !important;pointer-events:auto !important;}
.es-sessioninput input:focus{border-color:var(--indigo) !important;box-shadow:0 0 0 3px rgba(99,102,241,.2) !important;}
.es-controls{gap:10px !important;align-items:center !important;}

/* Gauge: thicker ring + brighter glow + stronger centre type (spec §3/§10) */
.es-gtrack{stroke-width:18 !important;}
.es-gval{stroke-width:18 !important;}
.es-gbig{text-shadow:0 0 18px currentColor;filter:saturate(1.05);}
.es-glevel{font-size:13.5px;}

/* Tighter vertical rhythm to reduce empty space (spec §2/§4) */
.es-main{gap:13px !important;}
.es-hero{margin:0 !important;}
.es-gauge-card{gap:7px;}

/* ---------- Responsive ---------- */
@media (max-width:1000px){
  .es-app{flex-wrap:wrap !important;}
  .es-side{flex-basis:100% !important; max-width:100% !important; min-height:auto; flex-direction:row !important;
    flex-wrap:wrap; overflow-x:auto;}
  .es-hero{flex-wrap:wrap !important;}
  .es-gaugecol{flex-basis:100% !important;}
  .es-feedcol,.es-studcol{flex-basis:100% !important;}
}
@media (prefers-reduced-motion:reduce){*{animation:none !important; transition:none !important;}}
"""


def build_theme() -> Any:
    """Construct the Gradio Soft theme tuned to the brand palette."""
    import gradio as gr
    return gr.themes.Soft(
        primary_hue=gr.themes.colors.indigo,
        secondary_hue=gr.themes.colors.cyan,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
    ).set(
        body_background_fill=TOKENS["ink"],
        block_background_fill=TOKENS["card"],
        block_border_color=TOKENS["border"],
        block_radius="16px",
        block_label_background_fill=TOKENS["card"],
        input_background_fill=TOKENS["surface"],
        button_primary_background_fill=TOKENS["brand"],
        button_primary_background_fill_hover=TOKENS["brand_strong"],
    )
