# ============================================================
# DASHBOARD PERAMALAN GANGGUAN KABEL SR - PLN UP3 SERPONG
# Desain: Cyber-Futuristik (Neon Glass + HUD + Grafik Beranimasi)
# Logika model (ARIMA / SARIMAX) TIDAK diubah.
# ============================================================
import re
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import base64, os
import holidays as hol
from datetime import datetime
from statsmodels.tsa.statespace.sarimax import SARIMAX

_VER_ST = tuple(int(p) for p in re.findall(r"\d+", st.__version__)[:2])

# ============================================================
# 1. KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Dashboard Gangguan Kabel SR",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 2. PALET WARNA
# ============================================================
TEXT_MAIN = "#F1F5F9"
TEXT_GRAY = "#94A3B8"
VIOLET = "#8B5CF6"
INDIGO = "#6366F1"
CYAN = "#22D3EE"
PINK = "#F472B6"
ORANGE = "#FB923C"
HIJAU = "#34D399"
MERAH = "#F87171"
FONT_PLOT = "Plus Jakarta Sans, Segoe UI, sans-serif"

# ============================================================
# 3. CSS KUSTOM
# ============================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,400,0,0');

:root { --violet:#8B5CF6; --indigo:#6366F1; --cyan:#22D3EE; --pink:#F472B6; --text:#F1F5F9; --muted:#94A3B8; }

html, body, [class*="css"] { font-family:'Plus Jakarta Sans', sans-serif; }

@property --ang { syntax:'<angle>'; initial-value:0deg; inherits:false; }

/* ---------- Latar futuristik: aurora neon + grid + scanline ---------- */
.stApp {
    background:
        linear-gradient(rgba(34,211,238,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(34,211,238,.035) 1px, transparent 1px),
        radial-gradient(900px 600px at 12% -10%, rgba(139,92,246,.34), transparent 60%),
        radial-gradient(800px 560px at 100% 0%, rgba(34,211,238,.20), transparent 55%),
        radial-gradient(700px 500px at 62% 112%, rgba(244,114,182,.16), transparent 60%),
        #040716;
    background-size: 46px 46px, 46px 46px, auto, auto, auto, auto;
    background-attachment: fixed;
    color: #E2E8F0;
}
/* aurora yang bergerak pelan */
.stApp::before {
    content:""; position:fixed; inset:-20%; pointer-events:none; z-index:0; opacity:.55;
    background:
        radial-gradient(420px 320px at 25% 30%, rgba(139,92,246,.22), transparent 70%),
        radial-gradient(380px 300px at 75% 65%, rgba(34,211,238,.16), transparent 70%);
    animation: aurora 18s ease-in-out infinite alternate;
}
/* garis pemindai (scanline) halus */
.stApp::after {
    content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.5;
    background: repeating-linear-gradient(0deg, rgba(255,255,255,.018) 0, rgba(255,255,255,.018) 1px, transparent 1px, transparent 3px);
}
[data-testid="stMain"], [data-testid="stAppViewContainer"] > section { position:relative; z-index:1; }

#MainMenu, footer { visibility:hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"],
[data-testid="stSidebarNav"] { display:none !important; }
[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarCollapsedControl"] button,
[data-testid="collapsedControl"] button { color:#67E8F9 !important; }

.block-container { padding: 1.6rem 2.4rem 2.5rem 2.4rem !important; max-width: 1500px; }

h1, h2, h3, h4 { color: var(--text) !important; }
.stMarkdown, .stMarkdown p, .stMarkdown li, [data-testid="stCaptionContainer"],
[data-testid="stWidgetLabel"] p, label { color: #CBD5E1 !important; }

@keyframes fadeUp { from { opacity:0; transform: translateY(18px); } to { opacity:1; transform:none; } }
@keyframes sweep { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
@keyframes growX { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes pulse { 0% { box-shadow:0 0 0 0 rgba(52,211,153,.7); } 70% { box-shadow:0 0 0 9px rgba(52,211,153,0); } 100% { box-shadow:0 0 0 0 rgba(52,211,153,0); } }
@keyframes glowmove { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }
@keyframes aurora { 0% { transform: translate3d(-3%, -2%, 0) scale(1); } 100% { transform: translate3d(4%, 3%, 0) scale(1.12); } }
@keyframes spin { to { --ang: 360deg; } }
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:.25; } }
@keyframes flicker { 0%,100% { text-shadow:0 0 18px rgba(34,211,238,.55); } 50% { text-shadow:0 0 30px rgba(139,92,246,.85); } }

/* ══════════ SIDEBAR KARTU ══════════ */
section[data-testid="stSidebar"] {
    width: 300px !important; min-width: 300px !important;
    background: transparent !important; border-right: none !important;
}
section[data-testid="stSidebar"] > div:first-child {
    background: linear-gradient(180deg, rgba(18,24,54,.86), rgba(8,12,30,.9));
    backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
    margin: 14px 0 14px 14px; width: calc(100% - 14px) !important;
    height: calc(100vh - 28px) !important;
    border-radius: 26px; border: 1px solid rgba(34,211,238,.16);
    box-shadow: 0 30px 60px -20px rgba(0,0,0,.75), 0 0 46px -14px rgba(34,211,238,.38), inset 0 1px 0 rgba(255,255,255,.07);
    padding-top: 0 !important; position: relative;
}
/* header bawaan: tidak makan tinggi, tombol collapse di pojok kanan atas */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    position:absolute !important; top:10px; right:10px; z-index:10;
    height:auto !important; min-height:0 !important; padding:0 !important; margin:0 !important;
    background:transparent !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] { overflow-x:hidden; padding-top:0 !important; }
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] { padding: 3.2rem 1rem 1.4rem 1rem !important; }
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 6px; }
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] {
    background: none !important; border: none !important; box-shadow: none !important;
    padding: 0 !important; animation: none !important; backdrop-filter: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"]::before { display:none !important; }

.brand-wide { position:relative; border-radius:18px; padding:14px 18px; display:flex; align-items:center;
              justify-content:center;
              background: linear-gradient(135deg, #FFFFFF 0%, #EAF6FF 55%, #DDEBFF 100%);
              border:1.5px solid rgba(34,211,238,.9);
              box-shadow: 0 0 0 4px rgba(34,211,238,.10), 0 14px 34px -10px rgba(34,211,238,.75), 0 0 28px -6px rgba(139,92,246,.55); }
.brand-wide img { height:52px; object-fit:contain; max-width:100%;
                  filter: saturate(1.45) contrast(1.18) drop-shadow(0 1px 1px rgba(15,23,42,.25)); }
.brand-text { display:flex; align-items:center; gap:12px; padding:2px 4px; }
.brand-logo { width:44px; height:44px; border-radius:14px; flex-shrink:0; font-size:22px;
              background:linear-gradient(135deg,#8B5CF6,#22D3EE); display:flex; align-items:center; justify-content:center;
              box-shadow:0 10px 24px -8px rgba(34,211,238,.9); }
.brand-title { font-family:'Orbitron',sans-serif; font-weight:700; font-size:14.5px; color:#F8FAFC; letter-spacing:.4px;
               margin:16px 4px 0 4px; line-height:1.3; text-transform:uppercase; }
.brand-sub { font-family:'JetBrains Mono',monospace; font-size:10.5px; color:#67E8F9; font-weight:500;
             margin:4px 4px 14px 4px; letter-spacing:.6px; }

section[data-testid="stSidebar"] [data-baseweb="input"],
section[data-testid="stSidebar"] [data-baseweb="base-input"] {
    background: rgba(255,255,255,.05) !important; border: 1px solid rgba(34,211,238,.18) !important;
    border-radius: 14px !important;
}
section[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    font-size:13px !important; font-weight:600 !important; color:#E2E8F0 !important;
    padding:10px 12px !important; height:42px;
}
section[data-testid="stSidebar"] [data-testid="stTextInput"] { margin-bottom: 4px; }
.menu-label { display:block; font-family:'JetBrains Mono',monospace; font-size:10.5px; font-weight:700; color:#475569;
              letter-spacing:1.6px; text-transform:uppercase; margin:16px 6px 8px 6px; line-height:1.2; }

section[data-testid="stSidebar"] .stButton { width:100%; }
section[data-testid="stSidebar"] .stButton > button {
    width:100% !important; height:44px !important; min-height:44px !important;
    justify-content:flex-start !important; text-align:left; gap:12px; padding:0 14px !important;
    border:1px solid transparent !important; border-radius:14px !important; white-space:nowrap;
    background:transparent !important; color:#94A3B8 !important; box-shadow:none !important;
    transition: all .25s ease;
}
section[data-testid="stSidebar"] .stButton > button > div { justify-content:flex-start !important; gap:12px; width:100%; }
section[data-testid="stSidebar"] .stButton > button p {
    font-size:13.5px !important; font-weight:600 !important; color:inherit !important; margin:0; text-align:left;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}
section[data-testid="stSidebar"] .stButton > button [data-testid="stIconMaterial"] { font-size:21px !important; color:inherit !important; }
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(34,211,238,.09) !important; color:#CFFAFE !important; transform: translateX(3px);
    border-color: rgba(34,211,238,.22) !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {
    background: linear-gradient(135deg, rgba(139,92,246,.95), rgba(99,102,241,.95)) !important; color:#FFFFFF !important;
    border-color: rgba(255,255,255,.18) !important;
    box-shadow: 0 12px 28px -10px rgba(139,92,246,.95), 0 0 22px -4px rgba(34,211,238,.45), 0 0 0 1px rgba(255,255,255,.1) inset !important;
}

.status { margin:20px 0 10px 0; padding:14px; border-radius:16px; background:rgba(255,255,255,.04);
          border:1px solid rgba(34,211,238,.18); position:relative; overflow:hidden; }
.status::before { content:""; position:absolute; left:0; top:0; height:100%; width:3px;
                  background:linear-gradient(180deg,#22D3EE,#8B5CF6); }
.status .row { display:flex; align-items:center; gap:8px; }
.pulse { width:9px; height:9px; border-radius:50%; background:#34D399; display:inline-block; animation:pulse 2s infinite; }
.status .lbl { font-family:'JetBrains Mono',monospace; font-size:10.5px; font-weight:700; color:#94A3B8; text-transform:uppercase; letter-spacing:1px; }
.status .val { font-family:'Orbitron',sans-serif; font-size:16px; font-weight:700; color:#F8FAFC; margin-top:8px; letter-spacing:.5px; }
.status .sub { font-family:'JetBrains Mono',monospace; font-size:10.5px; color:#64748B; font-weight:500; margin-top:4px; }

section[data-testid="stSidebar"] .st-key-reload button {
    justify-content:center !important; border:1px solid rgba(255,255,255,.10) !important;
    background:rgba(255,255,255,.04) !important;
}

/* ══════════ KARTU KACA + BORDER NEON BERPUTAR ══════════ */
div[data-testid="stVerticalBlockBorderWrapper"] {
    position: relative;
    background: linear-gradient(180deg, rgba(255,255,255,.065), rgba(255,255,255,.022)) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 24px !important;
    padding: 1.1rem 1.3rem !important;
    backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    box-shadow: 0 20px 50px -24px rgba(0,0,0,.8), inset 0 1px 0 rgba(255,255,255,.06) !important;
    animation: fadeUp .7s cubic-bezier(.2,.8,.2,1) both;
    transition: box-shadow .3s ease;
}
div[data-testid="stVerticalBlockBorderWrapper"]::before {
    content:""; position:absolute; inset:0; border-radius:24px; padding:1.2px; pointer-events:none; opacity:.8;
    background: conic-gradient(from var(--ang), transparent 0%, transparent 52%, rgba(34,211,238,.95) 72%, rgba(139,92,246,.95) 86%, transparent 100%);
    -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite: xor; mask-composite: exclude;
    animation: spin 7s linear infinite;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 20px 50px -24px rgba(0,0,0,.8), 0 0 40px -8px rgba(34,211,238,.4) !important;
}
.glass {
    position:relative;
    background: linear-gradient(180deg, rgba(255,255,255,.065), rgba(255,255,255,.025));
    border: 1px solid rgba(255,255,255,.09); border-radius: 22px; padding: 22px 24px;
    backdrop-filter: blur(18px); animation: fadeUp .7s cubic-bezier(.2,.8,.2,1) both;
    box-shadow: 0 20px 50px -24px rgba(0,0,0,.75), inset 0 1px 0 rgba(255,255,255,.06);
}
/* sudut HUD */
.glass::before, .glass::after { content:""; position:absolute; width:14px; height:14px; pointer-events:none; opacity:.85; }
.glass::before { top:9px; left:9px; border-top:2px solid #22D3EE; border-left:2px solid #22D3EE; border-top-left-radius:6px; }
.glass::after { bottom:9px; right:9px; border-bottom:2px solid #8B5CF6; border-right:2px solid #8B5CF6; border-bottom-right-radius:6px; }
.glass-title { color:#F8FAFC; font-family:'Orbitron',sans-serif; font-size:13px; font-weight:700; margin-bottom:10px;
               letter-spacing:.8px; text-transform:uppercase; }
.glass-text { color:#94A3B8; font-size:12.5px; line-height:1.8; font-weight:500; }
.note { border-radius:16px; padding:16px 20px; }
.note.green { background:rgba(52,211,153,.10); border:1px solid rgba(52,211,153,.30); }
.note.green .t { color:#6EE7B7; font-size:13px; font-weight:700; }
.note.green .d { color:#A7F3D0; font-size:11.5px; line-height:1.6; margin-top:4px; font-weight:500; }
.note.amber { background:rgba(251,146,60,.10); border:1px solid rgba(251,146,60,.30); }
.note.amber .t { color:#FDBA74; font-size:12px; font-weight:700; }
.note.amber .d { color:#FED7AA; font-size:11.5px; line-height:1.6; margin-top:4px; font-weight:500; }

/* ══════════ KPI ══════════ */
[data-testid="stMetric"] {
    background: linear-gradient(160deg, rgba(255,255,255,.08), rgba(255,255,255,.025));
    border: 1px solid rgba(255,255,255,.09); border-radius: 22px; padding: 22px 22px 18px 22px;
    position: relative; overflow: hidden; backdrop-filter: blur(16px);
    box-shadow: 0 20px 50px -24px rgba(0,0,0,.8);
    animation: fadeUp .7s cubic-bezier(.2,.8,.2,1) both;
    transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
}
[data-testid="stMetric"]:hover {
    transform: translateY(-5px); border-color: rgba(34,211,238,.55);
    box-shadow: 0 24px 50px -20px rgba(0,0,0,.85), 0 0 38px -8px rgba(34,211,238,.6);
}
[data-testid="stMetric"]::before {
    content:""; position:absolute; left:0; top:0; width:100%; height:2px; opacity:.95;
    background: linear-gradient(90deg, transparent, #8B5CF6, #22D3EE, transparent);
    background-size: 200% 100%; animation: sweep 4s linear infinite;
}
[data-testid="stMetric"]::after {
    content:'insights'; font-family:'Material Symbols Rounded'; position:absolute; top:20px; right:20px;
    font-size:21px; color:#A78BFA; background:rgba(139,92,246,.16); padding:9px; border-radius:50%;
    box-shadow: 0 0 20px -4px rgba(139,92,246,.7);
}
[data-testid="column"]:nth-of-type(2) [data-testid="stMetric"]::after,
[data-testid="stColumn"]:nth-of-type(2) [data-testid="stMetric"]::after { content:'trending_up'; color:#22D3EE; background:rgba(34,211,238,.14); box-shadow:0 0 20px -4px rgba(34,211,238,.7); }
[data-testid="column"]:nth-of-type(3) [data-testid="stMetric"]::after,
[data-testid="stColumn"]:nth-of-type(3) [data-testid="stMetric"]::after { content:'check_circle'; color:#34D399; background:rgba(52,211,153,.14); box-shadow:0 0 20px -4px rgba(52,211,153,.7); }
[data-testid="column"]:nth-of-type(4) [data-testid="stMetric"]::after,
[data-testid="stColumn"]:nth-of-type(4) [data-testid="stMetric"]::after { content:'calendar_month'; color:#F472B6; background:rgba(244,114,182,.14); box-shadow:0 0 20px -4px rgba(244,114,182,.7); }

[data-testid="stMetricLabel"] p { font-family:'JetBrains Mono',monospace; font-size:11px !important; font-weight:700 !important; color:#94A3B8 !important; letter-spacing:1.4px; }
[data-testid="stMetricValue"] {
    font-family:'Orbitron',sans-serif; font-size: 32px !important; font-weight: 700 !important; letter-spacing: 0px; margin: 12px 0 4px 0;
    background: linear-gradient(90deg, #FFFFFF, #67E8F9 60%, #C4B5FD); -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent !important;
    filter: drop-shadow(0 0 14px rgba(34,211,238,.35));
}
[data-testid="stMetricDelta"] { margin-top: 10px; }
[data-testid="stMetricDelta"] * {
    color:#A5F3FC !important; font-size:12px !important; font-weight:600;
    background:rgba(34,211,238,.10) !important; padding:5px 12px; border-radius:99px; display:inline-block;
    border:1px solid rgba(34,211,238,.18);
}
[data-testid="stMetricDelta"] svg { display:none; }

/* ══════════ JUDUL ══════════ */
.hero-title {
    font-family:'Orbitron',sans-serif;
    font-size: 27px; font-weight: 800; letter-spacing: .5px; line-height: 1.25; margin-top: 6px; text-transform: uppercase;
    background: linear-gradient(90deg, #FFFFFF 0%, #67E8F9 40%, #C4B5FD 80%, #FFFFFF 100%); background-size: 200% 100%;
    -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
    animation: glowmove 8s linear infinite;
    filter: drop-shadow(0 0 16px rgba(34,211,238,.35));
}
.hero-sub { color:#94A3B8; font-size:12.5px; margin-top:8px; font-weight:500; display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.chip { display:inline-flex; align-items:center; gap:6px; background:rgba(52,211,153,.12); color:#6EE7B7;
        border:1px solid rgba(52,211,153,.3); border-radius:99px; padding:3px 10px; font-size:10.5px; font-weight:700;
        letter-spacing:.8px; font-family:'JetBrains Mono',monospace; }
.chip.cyan { background:rgba(34,211,238,.10); color:#67E8F9; border-color:rgba(34,211,238,.3); }
.chip .blink { animation: blink 1.4s infinite; }
.judul-seksi { font-family:'Orbitron',sans-serif; font-size:14px; font-weight:700; color:#F8FAFC; margin-bottom:3px;
               letter-spacing:.8px; text-transform:uppercase; display:flex; align-items:center; gap:10px; }
.judul-seksi::before { content:""; width:6px; height:16px; border-radius:3px; background:linear-gradient(180deg,#22D3EE,#8B5CF6);
                       box-shadow:0 0 12px rgba(34,211,238,.7); }
.sub-seksi { font-family:'JetBrains Mono',monospace; font-size:11px; color:#64748B; font-weight:500; margin:0 0 10px 16px; }

/* ══════════ TABEL ══════════ */
.tbl-wrap { border-radius:18px; overflow:auto; border:1px solid rgba(34,211,238,.14); background:rgba(255,255,255,.025); }
.tbl { width:100%; border-collapse:collapse; font-size:12.5px; }
.tbl th { position:sticky; top:0; background:#0A1030; color:#67E8F9; text-transform:uppercase; font-size:10.5px;
          letter-spacing:1px; font-weight:700; text-align:left; padding:12px 16px; font-family:'JetBrains Mono',monospace;
          border-bottom:1px solid rgba(34,211,238,.25); }
.tbl td { padding:11px 16px; color:#E2E8F0; border-top:1px solid rgba(255,255,255,.05); font-weight:500; }
.tbl tbody tr:hover { background:rgba(34,211,238,.07); }
.tbl td.good { background:rgba(52,211,153,.15); color:#6EE7B7; font-weight:800; }
.tbl td.bad { color:#F87171; font-weight:700; }

/* ══════════ BAR SUMBER (animasi) ══════════ */
.src-track { background:rgba(255,255,255,.07); border-radius:8px; height:8px; overflow:hidden; }
.src-fill { height:8px; border-radius:8px; background:linear-gradient(90deg,#8B5CF6,#22D3EE);
            box-shadow:0 0 14px rgba(34,211,238,.6); transform-origin:left;
            animation: growX 1.2s cubic-bezier(.2,.8,.2,1) both; }

/* ══════════ KONTROL ══════════ */
[data-testid="stMain"] .stButton > button, [data-testid="stMain"] .stDownloadButton > button,
section.main .stButton > button, section.main .stDownloadButton > button {
    width:100%; height:42px; border-radius:999px; font-weight:700; font-size:13px;
    border:1px solid rgba(255,255,255,.13); background:rgba(255,255,255,.05); color:#E2E8F0; transition:all .25s ease;
}
[data-testid="stMain"] .stButton > button:hover, [data-testid="stMain"] .stDownloadButton > button:hover,
section.main .stButton > button:hover, section.main .stDownloadButton > button:hover {
    border-color:rgba(34,211,238,.75); color:#FFFFFF; box-shadow:0 0 26px -6px rgba(34,211,238,.85);
}
[data-testid="stMain"] .stButton > button[kind="primary"], [data-testid="stMain"] .stButton > button[data-testid="stBaseButton-primary"],
section.main .stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#8B5CF6,#6366F1); border:none; color:#FFFFFF;
    box-shadow:0 12px 28px -10px rgba(139,92,246,.95), 0 0 20px -4px rgba(34,211,238,.4);
}
[data-baseweb="select"] > div {
    background: rgba(255,255,255,.05) !important; border:1px solid rgba(34,211,238,.2) !important;
    border-radius: 14px !important; min-height: 42px;
}
[data-baseweb="select"] span, [data-baseweb="select"] div, [data-baseweb="select"] input { color:#E2E8F0 !important; font-size:13px; font-weight:600; }
[data-baseweb="select"] svg { fill:#67E8F9 !important; }
div[data-baseweb="popover"] ul, div[data-baseweb="menu"] { background:#0A1030 !important; border-radius:14px; }
li[role="option"] { color:#E2E8F0 !important; font-size:13px; }
li[role="option"]:hover { background:rgba(34,211,238,.18) !important; }
[data-testid="stFileUploaderDropzone"] { background:rgba(255,255,255,.03); border:1.5px dashed rgba(34,211,238,.45); border-radius:18px; }
[data-testid="stFileUploaderDropzone"] * { color:#CBD5E1 !important; }
[data-testid="stExpander"] { background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.08); border-radius:16px; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p { color:#E2E8F0 !important; }
[data-testid="stAlert"] { background:rgba(255,255,255,.05) !important; border:1px solid rgba(255,255,255,.1); border-radius:16px; }
[data-testid="stAlert"] * { color:#E2E8F0 !important; }
[data-testid="stSlider"] *, [data-testid="stSelectSlider"] * { color:#CBD5E1 !important; }
div[data-baseweb="slider"] div[role="slider"] { background:#22D3EE !important; box-shadow:0 0 16px rgba(34,211,238,.95); }
iframe { border:none; background:transparent; }

/* ══════════ PERBAIKAN SIDEBAR v2 ══════════ */
/* tombol collapse: strip sendiri di atas, tidak menimpa logo */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { top:8px !important; right:12px !important; }

/* tanpa scrollbar di dalam sidebar (tetap bisa di-scroll) */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] { scrollbar-width:none; -ms-overflow-style:none; }
section[data-testid="stSidebar"] *::-webkit-scrollbar { display:none !important; width:0 !important; height:0 !important; }

/* jarak lebih rapat agar semua muat */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap:4px; }
section[data-testid="stSidebar"] .stButton > button { height:42px !important; min-height:42px !important; }
/* pakai padding (bukan margin) supaya ikut dihitung dalam tinggi kotak markdown Streamlit */
.brand-title { margin:0 !important; padding:24px 4px 0 4px; }
.brand-sub { margin:0 !important; padding:6px 4px 18px 4px; }
.menu-label { color:#7C8BA5; margin:0 !important; padding:16px 6px 12px 6px; line-height:1.3; }
.status { margin:14px 0 8px 0; padding:12px 14px; }

/* kolom cari: seragam gelap-neon (hilangkan warna cokelat bawaan) */
section[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"] {
    background: rgba(8,14,38,.9) !important; border:1px solid rgba(34,211,238,.30) !important; border-radius:14px !important;
}
section[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="base-input"],
section[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background:transparent !important; background-color:transparent !important; box-shadow:none !important;
}
section[data-testid="stSidebar"] [data-testid="stTextInput"] input::placeholder { color:#64748B !important; opacity:1; }
section[data-testid="stSidebar"] [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
    border-color:#22D3EE !important; box-shadow:0 0 0 3px rgba(34,211,238,.18) !important;
}

/* scrollbar neon */
::-webkit-scrollbar { width:8px; height:8px; }
::-webkit-scrollbar-thumb { background:linear-gradient(180deg,#22D3EE,#8B5CF6); border-radius:8px; }
::-webkit-scrollbar-track { background:rgba(255,255,255,.03); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================
# 4. PEMUATAN DATA
# ============================================================
@st.cache_data
def load_data():
    xl = pd.ExcelFile('ARIMA_PLN_PowerBI.xlsx')
    return (
        pd.read_excel(xl, sheet_name='Historis'),
        pd.read_excel(xl, sheet_name='Metrik'),
        pd.read_excel(xl, sheet_name='Peramalan'),
        pd.read_excel(xl, sheet_name='Penyebab'),
        pd.read_excel(xl, sheet_name='Sumber'),
    )

hist, metrik, peramalan, penyebab, sumber = load_data()

def _cari_kolom(df, kandidat):
    def normal(s):
        return (str(s).lower().replace('²', '2').replace('^', '')
                .replace(' ', '').replace('_', '').replace('-', '')
                .replace('(', '').replace(')', '').replace('%', ''))
    peta = {normal(c): c for c in df.columns}
    for k in kandidat:
        if normal(k) in peta: return peta[normal(k)]
    return None

def _alias(df, kandidat, label=None):
    if label is None: label = kandidat[0]
    if label in df.columns: return
    asli = _cari_kolom(df, kandidat)
    if asli is not None: df[label] = df[asli]

_alias(metrik, ['R2', 'R²', 'R^2', 'R-Squared', 'RSquared', 'R2 (%)'], 'R2')
_alias(metrik, ['sMAPE(%)', 'sMAPE', 'sMAPE (%)', 'SMAPE'], 'sMAPE(%)')
_alias(metrik, ['MAE'], 'MAE')
_alias(metrik, ['RMSE'], 'RMSE')
_alias(metrik, ['MASE'], 'MASE')

# ============================================================
# 5. SESSION STATE
# ============================================================
if 'halaman' not in st.session_state: st.session_state.halaman = 'Ringkasan'
if 'model_terpilih' not in st.session_state: st.session_state.model_terpilih = 'ARIMA Dasar'
if 'hasil_ramalan_baru' not in st.session_state: st.session_state.hasil_ramalan_baru = None
if 'ts_baru_terakhir' not in st.session_state: st.session_state.ts_baru_terakhir = None
if 'info_model_baru' not in st.session_state: st.session_state.info_model_baru = None

# ============================================================
# 6. SIDEBAR KARTU
# ============================================================
MENU = ["Ringkasan", "Tren Harian", "Peramalan", "Perbarui & Ramalkan",
        "Analisis Penyebab", "Perbandingan Model", "Akurasi Model"]
IKON_MATERIAL = {"Ringkasan": ":material/dashboard:", "Tren Harian": ":material/show_chart:",
                 "Peramalan": ":material/query_stats:", "Perbarui & Ramalkan": ":material/published_with_changes:",
                 "Analisis Penyebab": ":material/pie_chart:", "Perbandingan Model": ":material/compare_arrows:",
                 "Akurasi Model": ":material/verified:"}
IKON_EMOJI = {"Ringkasan": "🏠", "Tren Harian": "📈", "Peramalan": "🔮", "Perbarui & Ramalkan": "🔄",
              "Analisis Penyebab": "🥧", "Perbandingan Model": "⚖️", "Akurasi Model": "✅"}

def _pindah_halaman(nama):
    st.session_state.halaman = nama

def _muat_ulang():
    st.cache_data.clear()

def render_sidebar():
    pakai_material = _VER_ST >= (1, 37)
    aktif = st.session_state.halaman
    with st.sidebar:
        if os.path.exists('logo_haleyora.png'):
            with open('logo_haleyora.png', 'rb') as f:
                b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<div class="brand-wide"><img src="data:image/png;base64,{b64}"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="brand-text"><div class="brand-logo">⚡</div>'
                        '<div style="color:#F8FAFC;font-size:19px;font-weight:800;letter-spacing:-.5px;">'
                        'haleyora<span style="color:#FB923C;">power</span></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-title">Forecast Gangguan Kabel SR</div>'
                    '<div class="brand-sub">&#9656; PLN UP3 SERPONG</div>', unsafe_allow_html=True)

        kata = st.text_input("Cari", key="cari_menu", placeholder="Cari menu...", label_visibility="collapsed")
        st.markdown('<div class="menu-label">// Menu</div>', unsafe_allow_html=True)

        tampil_menu = [m for m in MENU if kata.strip().lower() in m.lower()] if kata.strip() else MENU
        for nama in tampil_menu:
            ikon = IKON_MATERIAL[nama] if pakai_material else IKON_EMOJI[nama]
            st.button(nama, icon=ikon, key=f"nav_{nama}",
                      type="primary" if nama == aktif else "secondary",
                      on_click=_pindah_halaman, args=(nama,))
        if not tampil_menu:
            st.caption("Menu tidak ditemukan.")

        jumlah_hari_hist = f"{len(hist):,}".replace(",", ".")
        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.markdown(f'<div class="status"><div class="row"><span class="pulse"></span>'
                    f'<span class="lbl">Model aktif</span></div><div class="val">ARIMA(1,1,1)</div>'
                    f'<div class="sub">{jumlah_hari_hist} hari data historis</div></div>',
                    unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        st.button("Muat Ulang Data", icon=(":material/refresh:" if pakai_material else "🔄"),
                  key="reload", on_click=_muat_ulang)

render_sidebar()

# ============================================================
# 7. HEADER & FILTER
# ============================================================
kiri, k_filter, kanan = st.columns([6, 2.2, 2.2])
with kiri:
    st.markdown(
        '<div class="hero-title">Dashboard Peramalan Gangguan Kabel SR</div>'
        '<div class="hero-sub">PT. Haleyora Power Serpong &nbsp;·&nbsp; Metode ARIMA &amp; SARIMAX '
        '<span class="chip"><span class="pulse"></span>LIVE</span>'
        f'<span class="chip cyan"><span class="blink">●</span>SYS ONLINE · {datetime.now():%d %b %Y}</span></div>',
        unsafe_allow_html=True)
with k_filter:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    opsi = ['Semua'] + list(pd.to_datetime(hist.iloc[:, 0]).dt.strftime('%b %Y').unique())
    pilih_bulan = st.selectbox("p", opsi, label_visibility="collapsed")

hist_f = hist.copy()
hist_f.iloc[:, 0] = pd.to_datetime(hist_f.iloc[:, 0])
if pilih_bulan != 'Semua':
    hist_f = hist_f[hist_f.iloc[:, 0].dt.strftime('%b %Y') == pilih_bulan]
kol_tgl, kol_val = hist_f.columns[0], hist_f.columns[1]

with kanan:
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.download_button(
        "⬇ Unduh Data CSV", key="unduh",
        data=hist_f.to_csv(index=False).encode('utf-8'),
        file_name=f"gangguan_SR_{datetime.now():%Y%m%d}.csv",
        mime="text/csv")

st.markdown("<div style='height: 22px;'></div>", unsafe_allow_html=True)

# ============================================================
# 8. HELPER: TATA LETAK, ANIMASI, TABEL
# ============================================================
TRANSPARAN = 'rgba(0,0,0,0)'

def tata(t=280):
    return dict(
        template='plotly_dark',
        plot_bgcolor=TRANSPARAN, paper_bgcolor=TRANSPARAN,
        font=dict(color=TEXT_GRAY, size=11, family=FONT_PLOT),
        height=t, margin=dict(l=10, r=10, t=10, b=30),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color=TEXT_GRAY), showline=False, zeroline=False),
        yaxis=dict(gridcolor='rgba(34,211,238,0.07)', tickfont=dict(size=11, color=TEXT_GRAY), zeroline=False),
        legend=dict(orientation='h', yanchor='bottom', y=1.05, x=0, font=dict(size=11, color=TEXT_GRAY)),
        hoverlabel=dict(bgcolor='#070C22', bordercolor=CYAN, font=dict(color='#F8FAFC', size=12))
    )

def judul(teks, sub=""):
    st.markdown(f'<div class="judul-seksi">{teks}</div><div class="sub-seksi">{sub}</div>', unsafe_allow_html=True)

def spasi(px=24):
    st.markdown(f"<div style='height:{px}px'></div>", unsafe_allow_html=True)

def tampil(fig, durasi=28, redraw=False):
    """Menampilkan grafik Plotly beranimasi (auto-play saat dimuat)."""
    tinggi = int(fig.layout.height or 300)
    html = fig.to_html(
        include_plotlyjs='cdn', full_html=True, auto_play=True,
        config={'displayModeBar': False, 'responsive': True},
        animation_opts={'frame': {'duration': durasi, 'redraw': redraw},
                        'transition': {'duration': 0}, 'mode': 'immediate', 'fromcurrent': True})
    html = html.replace(
        '<head>',
        '<head><link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">'
        '<style>html,body{margin:0;padding:0;background:transparent;overflow:hidden}</style>', 1)
    components.html(html, height=tinggi + 6)

def anim_garis(fig, groups, n_frames=46):
    """Garis 'tergambar' bertahap. groups = urutan grup trace yang digambar bergantian."""
    # Sumbu X dikunci bertipe tanggal. Tanpa ini, data awal yang dikosongkan membuat
    # Plotly menebak sumbu sebagai angka (linear) sehingga grafik tidak tampil.
    fig.update_xaxes(type='date')
    lens = [len(fig.data[g[0]].x) for g in groups]
    total = float(sum(lens)) or 1.0
    xs = [fig.data[i].x for i in range(len(fig.data))]
    ys = [fig.data[i].y for i in range(len(fig.data))]
    frames = []
    for s in range(1, n_frames + 1):
        pos = total * s / n_frames
        used, idx, dat = 0.0, [], []
        for g, L in zip(groups, lens):
            k = int(round(min(max(pos - used, 0), L)))
            used += L
            for i in g:
                idx.append(i)
                dat.append(go.Scatter(x=xs[i][:k], y=ys[i][:k]))
        frames.append(go.Frame(data=dat, traces=idx, name=str(s)))
    for i in range(len(fig.data)):
        fig.data[i].x = xs[i][:0]
        fig.data[i].y = ys[i][:0]
    fig.frames = frames
    return fig

def anim_bar(fig, n_frames=26):
    """Batang 'tumbuh' dari nol dengan easing."""
    yf = [float(v) for v in fig.data[0].y]
    frames = [go.Frame(data=[go.Bar(y=[v * (1 - (1 - s / n_frames) ** 3) for v in yf])],
                       traces=[0], name=str(s)) for s in range(1, n_frames + 1)]
    fig.data[0].y = [0] * len(yf)
    fig.frames = frames
    return fig

def anim_donat(fig, nilai, per_slice=7):
    """Irisan donat muncul satu per satu."""
    k = len(nilai)
    frames = []
    for s in range(1, k * per_slice + 1):
        vals = [v * min(max((s - j * per_slice) / per_slice, 0), 1) for j, v in enumerate(nilai)]
        frames.append(go.Frame(data=[go.Pie(values=vals)], traces=[0], name=str(s)))
    fig.data[0].values = [0] * k
    fig.frames = frames
    return fig

def tabel_html(df, fmt=None, tinggi=None, sorot=None):
    """Tabel bertema gelap (menggantikan st.dataframe). sorot(kolom, nilai) -> kelas CSS."""
    fmt = fmt or {}
    th = ''.join(f'<th>{c}</th>' for c in df.columns)
    baris = ''
    for _, r in df.iterrows():
        td = ''
        for c in df.columns:
            v = r[c]
            if isinstance(v, (float, np.floating)) and pd.isna(v):
                s = '-'
            else:
                try: s = fmt[c].format(v) if c in fmt else str(v)
                except Exception: s = str(v)
            kls = sorot(c, v) if sorot else ''
            td += f'<td class="{kls}">{s}</td>'
        baris += f'<tr>{td}</tr>'
    gaya = f'max-height:{tinggi}px;' if tinggi else ''
    st.markdown(f'<div class="tbl-wrap" style="{gaya}"><table class="tbl"><thead><tr>{th}</tr></thead>'
                f'<tbody>{baris}</tbody></table></div>', unsafe_allow_html=True)

# ============================================================
# 9. KPI CARDS
# ============================================================
def kpi():
    k1, k2, k3, k4 = st.columns(4)
    total = f"{int(hist_f[kol_val].sum()):,}".replace(",", ".")
    baris_terbaik = metrik.loc[metrik['MASE'].idxmin()]
    mase = float(baris_terbaik['MASE'])
    with k1: st.metric("TOTAL GANGGUAN", total, "kasus tercatat ↗")
    with k2: st.metric("RATA-RATA HARIAN", f"{hist_f[kol_val].mean():.2f}".replace(".", ","), "gangguan / hari ↗")
    with k3: st.metric("AKURASI MASE", f"{mase:.3f}".replace(".", ","), "belum unggul dari naive")
    with k4: st.metric("PROYEKSI 30 HARI", f"{peramalan['Prediksi'].mean():.2f}".replace(".", ","), "kategori sedang ↗")

# ============================================================
# 10. FUNGSI GRAFIK (BERANIMASI)
# ============================================================
def g_tren(t=320):
    f = go.Figure()
    # lapisan "glow" (di bawah) lalu garis utama
    f.add_trace(go.Scatter(
        x=hist_f[kol_tgl], y=hist_f[kol_val], showlegend=False, hoverinfo='skip',
        line=dict(color='rgba(34,211,238,0.20)', width=11, shape='spline')))
    f.add_trace(go.Scatter(
        x=peramalan['Tanggal'], y=peramalan['Prediksi'], showlegend=False, hoverinfo='skip',
        line=dict(color='rgba(251,146,60,0.20)', width=11, shape='spline')))
    f.add_trace(go.Scatter(
        x=hist_f[kol_tgl], y=hist_f[kol_val], name='Aktual',
        line=dict(color=CYAN, width=3, shape='spline'),
        fill='tozeroy', fillcolor='rgba(34, 211, 238, 0.10)'))
    f.add_trace(go.Scatter(
        x=peramalan['Tanggal'], y=peramalan['Prediksi'], name='Prediksi',
        line=dict(color=ORANGE, width=3, dash='dot', shape='spline')))
    L = tata(t)
    try:
        xmin = min(pd.to_datetime(hist_f[kol_tgl]).min(), pd.to_datetime(peramalan['Tanggal']).min())
        xmax = max(pd.to_datetime(hist_f[kol_tgl]).max(), pd.to_datetime(peramalan['Tanggal']).max())
        L['xaxis']['range'] = [str(xmin), str(xmax)]
    except Exception:
        pass
    ymax = max(float(hist_f[kol_val].max()), float(peramalan['Prediksi'].max()))
    L['yaxis']['range'] = [0, ymax * 1.15]
    f.update_layout(**L)
    return anim_garis(f, [[0, 2], [1, 3]])

def g_penyebab(t=320):
    d = penyebab.head(5).copy()
    d['Lengkap'] = d['Penyebab'].astype(str)
    d['Penyebab'] = d['Lengkap'].apply(lambda x: x if len(x) <= 22 else x[:20] + '…')
    nilai = [float(v) for v in d['Jumlah']]
    tot = sum(nilai) or 1.0
    teks = [f"{v / tot * 100:.0f}%" for v in nilai]
    warna = [VIOLET, CYAN, PINK, ORANGE, HIJAU]
    f = go.Figure(go.Pie(
        labels=list(d['Penyebab']), values=nilai, hole=.68, sort=False,
        text=teks, textinfo='text', textposition='inside',
        textfont=dict(size=11, color='white', family=FONT_PLOT),
        marker=dict(colors=warna, line=dict(color='#050818', width=3)),
        customdata=list(d['Lengkap']),
        hovertemplate='<b>%{customdata}</b><br>%{value} kasus<extra></extra>'))
    f.update_layout(template='plotly_dark', paper_bgcolor=TRANSPARAN, plot_bgcolor=TRANSPARAN, height=t,
                    margin=dict(l=10, r=10, t=10, b=10),
                    font=dict(color=TEXT_GRAY, family=FONT_PLOT),
                    hoverlabel=dict(bgcolor='#070C22', bordercolor=CYAN, font=dict(color='#F8FAFC', size=12)),
                    legend=dict(orientation='h', yanchor='top', y=-0.02, xanchor='center', x=0.5,
                                font=dict(size=11, color=TEXT_GRAY)))
    return anim_donat(f, nilai)

def g_ramal(t=250):
    f = go.Figure()
    f.add_trace(go.Scatter(x=peramalan['Tanggal'], y=peramalan['CI_Atas'], mode='lines',
                           line=dict(color='rgba(0,0,0,0)'), showlegend=False))
    f.add_trace(go.Scatter(x=peramalan['Tanggal'], y=peramalan['CI_Bawah'], fill='tonexty', mode='lines',
                           fillcolor='rgba(139, 92, 246, 0.22)', line=dict(color='rgba(0,0,0,0)'), name='Interval 95%'))
    f.add_trace(go.Scatter(x=peramalan['Tanggal'], y=peramalan['Prediksi'], name='Prediksi',
                           line=dict(color='#A78BFA', width=3, shape='spline')))
    L = tata(t); L['yaxis']['range'] = [0, 55]; f.update_layout(**L)
    return anim_garis(f, [[0, 1, 2]])

def g_bulan(t=300):
    h = hist.copy(); h.iloc[:, 0] = pd.to_datetime(h.iloc[:, 0]); h['Bulan'] = h.iloc[:, 0].dt.strftime('%b %Y')
    b = h.groupby('Bulan', sort=False)[h.columns[1]].sum().reset_index(); b.columns = ['Bulan', 'Jumlah']
    mx = b['Jumlah'].max()
    warna = [CYAN if i == len(b['Jumlah']) - 1 else '#7C6AF0' for i in range(len(b['Jumlah']))]
    teks = [f"{v:,}".replace(",", ".") for v in b['Jumlah']]
    kw = dict(x=list(b['Bulan']), y=[float(v) for v in b['Jumlah']], text=teks, textposition='outside',
              textfont=dict(size=10, color=TEXT_MAIN), cliponaxis=False)
    try: f = go.Figure(go.Bar(**kw, marker=dict(color=warna, cornerradius=6)))
    except Exception: f = go.Figure(go.Bar(**kw, marker=dict(color=warna)))
    L = tata(t); L['xaxis'].update(tickangle=0); L['yaxis'].update(range=[0, mx * 1.2]); f.update_layout(**L)
    return anim_bar(f)

def b_sumber():
    total_s = sumber['Jumlah'].sum(); html = ""
    for i, (_, r) in enumerate(sumber.head(6).iterrows()):
        pct = r['Jumlah'] / total_s * 100; jml = f"{r['Jumlah']:,}".replace(",", "."); nama = str(r['Sumber_Lapor'])[:22]
        html += (
            f'<div style="margin-bottom:18px;"><div style="display:flex;justify-content:space-between;margin-bottom:7px;">'
            f'<span style="color:{TEXT_MAIN};font-size:12px;font-weight:600;">{nama}</span>'
            f'<span style="color:{TEXT_GRAY};font-size:11px;font-weight:700;">{jml} <span style="font-weight:500;">({pct:.1f}%)</span></span></div>'
            f'<div class="src-track"><div class="src-fill" style="width:{min(pct, 100):.1f}%;animation-delay:{i * 0.12:.2f}s;"></div></div></div>')
    return html

def t_metrik():
    kolom_mase = metrik['MASE']
    def sorot(c, v):
        if c != 'MASE': return ''
        if v == kolom_mase.min(): return 'good'
        if v == kolom_mase.max(): return 'bad'
        return ''
    tabel_html(metrik, fmt={'MAE': '{:.2f}', 'RMSE': '{:.2f}', 'sMAPE(%)': '{:.2f}%', 'R2': '{:.4f}', 'MASE': '{:.3f}'}, sorot=sorot)

def catatan():
    spasi(16)
    st.markdown(
        f'<div class="glass"><div class="glass-title">Interpretasi Hasil</div>'
        f'<div class="glass-text">'
        f'Model ARIMA(1,1,1) menghasilkan MASE 1,548. Nilai ini belum mengungguli baseline naive (1,527) maupun mean (1,528), dengan selisih sangat tipis hanya 0,021 pada skala MASE. '
        f'Penambahan variabel eksogen kalender pada SARIMAX tidak memperbaiki akurasi; MASE justru meningkat menjadi 1,653 (kalender dasar) dan 1,670 (kalender lengkap). '
        f'Residual model tetap white noise (p &gt; 0,05 pada lag 7, 14, dan 21), sehingga keterbatasan akurasi berasal dari sifat data yang overdispersed (rasio 4,60) dan dipengaruhi faktor eksogen fisik di luar dataset seperti kondisi cuaca.</div></div>',
        unsafe_allow_html=True)

# ============================================================
# 11. SIMULASI SKENARIO
# ============================================================
def simulasi_skenario():
    spasi(16)
    judul("Simulasi Skenario Faktor Eksternal", "Ilustrasi dampak faktor eksogen tambahan di luar model")
    st.markdown('<div class="glass" style="padding:16px 20px;margin-bottom:20px;"><div class="glass-text" style="margin:0;">'
                'Model ARIMA sudah menangkap pola historis murni dari data. Simulasi ini menggeser hasil prediksi secara proporsional untuk mengilustrasikan potensi dampak faktor cuaca yang belum dimodelkan.</div></div>',
                unsafe_allow_html=True)

    skenario = st.select_slider("Skenario Faktor Eksternal", options=["Musim Kering (-30%)", "Normal (0%)", "Musim Hujan (+20%)", "Cuaca Ekstrem (+50%)"], value="Normal (0%)")
    faktor = {"Musim Kering (-30%)": -0.30, "Normal (0%)": 0.0, "Musim Hujan (+20%)": 0.20, "Cuaca Ekstrem (+50%)": 0.50}[skenario]
    df_sim = peramalan.copy(); df_sim['Prediksi_Sim'] = (df_sim['Prediksi'] * (1 + faktor)).clip(lower=0)

    f = go.Figure()
    f.add_trace(go.Scatter(x=df_sim['Tanggal'], y=df_sim['Prediksi'], name='Prediksi ARIMA (asli)', line=dict(color=TEXT_GRAY, width=2, dash='dot', shape='spline')))
    f.add_trace(go.Scatter(x=df_sim['Tanggal'], y=df_sim['Prediksi_Sim'], name=f'Simulasi: {skenario}', line=dict(color=CYAN, width=3, shape='spline'), fill='tonexty', fillcolor='rgba(34, 211, 238, 0.12)'))
    L = tata(300)
    ymax = float(max(df_sim['Prediksi'].max(), df_sim['Prediksi_Sim'].max()))
    L['yaxis']['range'] = [0, ymax * 1.2]
    f.update_layout(**L)
    f = anim_garis(f, [[0, 1]])
    with st.container(border=True):
        tampil(f)

    selisih = df_sim['Prediksi_Sim'].mean() - df_sim['Prediksi'].mean()
    c1, c2 = st.columns(2)
    with c1: st.metric("Rata-rata Prediksi Asli", f"{df_sim['Prediksi'].mean():.1f}", "gangguan/hari")
    with c2: st.metric("Rata-rata Skenario", f"{df_sim['Prediksi_Sim'].mean():.1f}", f"{'+' if selisih >= 0 else ''}{selisih:.1f} vs asli ↗")

# ============================================================
# 12. GRAFIK PROGRES
# ============================================================
def g_progres_optimasi():
    df_prog = metrik[~metrik['Model'].str.contains('baseline', case=False, na=False)].copy()
    warna_bar = ['#7C6AF0'] * (len(df_prog) - 1) + [CYAN]
    f = go.Figure(go.Bar(x=list(df_prog['Model']), y=[float(v) for v in df_prog['MASE']], marker_color=warna_bar,
                         text=list(df_prog['MASE'].round(3)), textposition='outside',
                         textfont=dict(color=TEXT_MAIN, size=11), cliponaxis=False))
    f.add_hline(y=1.0, line_dash='dot', line_color=MERAH, annotation_text='Ambang naive', annotation_font_size=10, annotation_font_color=MERAH)
    L = tata(320); L['yaxis']['title'] = 'MASE'; L['yaxis']['range'] = [0, float(df_prog['MASE'].max()) * 1.25]
    f.update_layout(**L)
    return anim_bar(f)

def g_progres_r2():
    df_prog = metrik[~metrik['Model'].str.contains('baseline', case=False, na=False)].copy()
    warna_bar = [VIOLET if v >= 0 else '#F87171' for v in df_prog['R2']]
    f = go.Figure(go.Bar(x=list(df_prog['Model']), y=[float(v) for v in df_prog['R2']], marker_color=warna_bar,
                         text=list(df_prog['R2'].round(4)), textposition='outside',
                         textfont=dict(color=TEXT_MAIN, size=11), cliponaxis=False))
    f.add_hline(y=0, line_dash='dot', line_color=TEXT_GRAY)
    lo, hi = min(0.0, float(df_prog['R2'].min())), max(0.0, float(df_prog['R2'].max()))
    rng = (hi - lo) or 1.0
    L = tata(320); L['yaxis']['title'] = 'R2'; L['yaxis']['range'] = [lo - 0.2 * rng, hi + 0.25 * rng]
    f.update_layout(**L)
    return anim_bar(f)

# ============================================================
# 13. TOGGLE MODEL
# ============================================================
def kartu_model_toggle():
    opsi_model = {
        'ARIMA Dasar': {'nama_metrik': 'ARIMA(1, 1, 1)', 'deskripsi': 'Model univariat terbaik berdasarkan AIC. Residual white noise, tetapi MASE masih di atas 1,0 sehingga belum mengungguli baseline naive.', 'warna': CYAN},
        'SARIMAX Kalender Dasar': {'nama_metrik': 'SARIMAX(1, 1, 1) + kalender dasar', 'deskripsi': 'Penambahan variabel kalender (akhir pekan, awal/akhir bulan). Tidak meningkatkan akurasi; MASE justru lebih tinggi dari ARIMA.', 'warna': VIOLET},
        'SARIMAX Kalender Lengkap': {'nama_metrik': 'SARIMAX(1, 1, 2) + kalender lengkap', 'deskripsi': 'Order dioptimasi ulang + fitur hari libur nasional. Hasil terburuk; indikasi overfitting terhadap pola kalender.', 'warna': ORANGE}
    }
    cols = st.columns(3)
    for i, nama_opsi in enumerate(opsi_model.keys()):
        aktif = st.session_state.model_terpilih == nama_opsi
        with cols[i]:
            if st.button(nama_opsi, key=f"toggle_{nama_opsi}", type="primary" if aktif else "secondary"):
                st.session_state.model_terpilih = nama_opsi; st.rerun()

    spasi(14)
    pilihan = opsi_model[st.session_state.model_terpilih]
    baris = metrik[metrik['Model'] == pilihan['nama_metrik']]
    if baris.empty:
        st.warning(f"Data untuk model '{pilihan['nama_metrik']}' belum ditemukan pada sheet Metrik."); return

    m = baris.iloc[0]
    st.markdown(
        f'<div class="glass" style="border-left:3px solid {pilihan["warna"]};box-shadow:0 0 40px -14px {pilihan["warna"]};">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px;">'
        f'<span style="color:{TEXT_MAIN};font-family:Orbitron,sans-serif;font-size:15px;font-weight:700;letter-spacing:.6px;">{st.session_state.model_terpilih}</span>'
        f'<span style="background:rgba(255,255,255,0.08);color:{TEXT_MAIN};padding:6px 14px;border-radius:20px;font-size:11px;font-weight:700;border:1px solid rgba(255,255,255,.12);">{pilihan["nama_metrik"]}</span></div>'
        f'<div class="glass-text" style="margin:0;font-size:13px;">{pilihan["deskripsi"]}</div></div>', unsafe_allow_html=True)

    spasi(16)
    k1, k2, k3, k4, k5 = st.columns(5)
    def _nil(series, key, fmt):
        try: return f"{series[key]:{fmt}}".replace(".", ",")
        except Exception: return "-"
    with k1: st.metric("MAE", _nil(m, 'MAE', '.2f'))
    with k2: st.metric("RMSE", _nil(m, 'RMSE', '.2f'))
    with k3: st.metric("sMAPE", _nil(m, 'sMAPE(%)', '.2f') + ("%" if _nil(m, 'sMAPE(%)', '.2f') != "-" else ""))
    with k4: st.metric("R2", _nil(m, 'R2', '.4f'))
    with k5: st.metric("MASE", _nil(m, 'MASE', '.3f'))

# ============================================================
# 14. PERAMALAN BERGULIR
# ============================================================
def proses_data_upload(df_baru, kol_tgl_baru, kol_val_baru, jumlah_hari=30, order_model=(1, 1, 1)):
    kerja = df_baru.copy(); kerja[kol_tgl_baru] = pd.to_datetime(kerja[kol_tgl_baru], errors='coerce'); kerja = kerja.dropna(subset=[kol_tgl_baru])
    if kerja[kol_val_baru].dtype == object:
        agregasi = kerja.groupby(kerja[kol_tgl_baru].dt.normalize()).size(); ts_baru = agregasi.rename('jumlah')
    else:
        ts_baru = kerja.set_index(kol_tgl_baru)[kol_val_baru]
    ts_baru = ts_baru.asfreq('D').interpolate(method='linear').round()

    def buat_exog(index_tanggal):
        exog = pd.DataFrame(index=index_tanggal)
        exog['is_weekend'] = (index_tanggal.dayofweek >= 5).astype(int)
        exog['is_month_start'] = (index_tanggal.day <= 3).astype(int)
        exog['is_month_end'] = (index_tanggal.day >= 28).astype(int)
        exog['day_of_week'] = index_tanggal.dayofweek
        id_hol = hol.Indonesia(years=sorted(set(index_tanggal.year)))
        exog['is_holiday'] = [1 if d in id_hol else 0 for d in index_tanggal.date]
        return exog

    exog_baru = buat_exog(ts_baru.index)
    model_baru = SARIMAX(ts_baru, exog=exog_baru, order=order_model, enforce_stationarity=False, enforce_invertibility=False).fit(disp=False, maxiter=1000, method='powell')
    idx_depan = pd.date_range(ts_baru.index[-1] + pd.Timedelta(days=1), periods=jumlah_hari, freq='D')
    exog_depan = buat_exog(idx_depan)
    fc_baru = model_baru.get_forecast(steps=jumlah_hari, exog=exog_depan); ci = fc_baru.conf_int()

    hasil_baru = pd.DataFrame({
        'Tanggal': idx_depan, 'Prediksi': fc_baru.predicted_mean.clip(lower=0).round(2).values,
        'CI_Bawah': ci.iloc[:, 0].clip(lower=0).round(2).values, 'CI_Atas': ci.iloc[:, 1].clip(lower=0).round(2).values,
    })
    return {'ts_baru': ts_baru, 'hasil': hasil_baru, 'order': order_model, 'aic': model_baru.aic}

def halaman_perbarui_ramalkan():
    st.markdown('<div class="glass" style="margin-bottom:20px;"><div class="glass-title">Peramalan Bergulir (Rolling Forecast)</div>'
                '<div class="glass-text">Fitur ini memungkinkan sistem melatih ulang model SARIMAX secara otomatis menggunakan data gangguan terbaru yang diunggah, kemudian menghasilkan peramalan dari titik data paling akhir.</div></div>',
                unsafe_allow_html=True)
    st.markdown('<div class="glass" style="margin-bottom:24px;"><div class="glass-title" style="margin-bottom:12px;">Panduan Rentang Peramalan</div>'
                '<div style="display:flex;gap:16px;flex-wrap:wrap;">'
                '<div class="note green" style="flex:1;min-width:220px;"><div class="t">7-42 HARI — DISARANKAN</div><div class="d">Interval kepercayaan masih wajar.</div></div>'
                '<div class="note amber" style="flex:1;min-width:220px;"><div class="t">43-120 HARI — HANYA ILUSTRASI</div><div class="d">Interval melebar signifikan.</div></div>'
                '</div></div>', unsafe_allow_html=True)

    file_baru = st.file_uploader("Unggah berkas data gangguan (XLSX / CSV)", type=['xlsx', 'csv'], key="upload_ramalan")
    if file_baru is not None:
        try:
            if file_baru.name.lower().endswith('.csv'): df_baru = pd.read_csv(file_baru)
            else: df_baru = pd.read_excel(file_baru)
            st.success(f"Berkas berhasil dimuat - {len(df_baru):,} baris")
            with st.expander("Pratinjau data", expanded=False): tabel_html(df_baru.head(10), tinggi=320)

            c1, c2 = st.columns(2)
            with c1: kol_tgl_baru = st.selectbox("Kolom tanggal", df_baru.columns, key="pilih_kol_tgl")
            with c2: kol_val_baru = st.selectbox("Kolom jumlah gangguan", df_baru.columns, key="pilih_kol_val")
            jumlah_hari = st.slider("Jumlah hari ke depan", min_value=7, max_value=120, value=30, step=7)
            jalankan = st.button("🔄 Latih Ulang Model", type="primary")

            if jalankan:
                with st.spinner("Melatih ulang..."):
                    try:
                        out = proses_data_upload(df_baru, kol_tgl_baru, kol_val_baru, jumlah_hari=jumlah_hari)
                        st.session_state.hasil_ramalan_baru = out['hasil']; st.session_state.ts_baru_terakhir = out['ts_baru']; st.session_state.info_model_baru = out
                    except Exception as e: st.error(f"Gagal: {e}"); st.session_state.hasil_ramalan_baru = None
        except Exception as e: st.error(f"Error: {e}")

    if st.session_state.hasil_ramalan_baru is not None:
        hasil_baru = st.session_state.hasil_ramalan_baru; ts_baru = st.session_state.ts_baru_terakhir; info = st.session_state.info_model_baru
        st.markdown(f'<div class="note green" style="margin:20px 0;"><div class="t">Model berhasil dilatih ulang dari {len(ts_baru)} hari data.</div></div>', unsafe_allow_html=True)

        n_hari = len(hasil_baru)
        k1, k2, k3 = st.columns(3)
        with k1: st.metric("Order Model", f"SARIMAX{info['order']}", "otomatis ↗")
        with k2: st.metric("Proyeksi Rata-rata", f"{hasil_baru['Prediksi'].mean():.2f}".replace(".", ","), "gangguan / hari ↗")
        with k3: st.metric("Periode", f"{n_hari} hari", "ke depan")

        spasi(20)
        with st.container(border=True):
            judul("Grafik Peramalan Baru", "Data aktual dan hasil peramalan bergulir")
            f = go.Figure()
            f.add_trace(go.Scatter(x=ts_baru.index[-60:], y=ts_baru.values[-60:], name="Aktual", line=dict(color=CYAN, width=3, shape='spline'), fill="tozeroy", fillcolor="rgba(34, 211, 238, 0.10)"))
            f.add_trace(go.Scatter(x=hasil_baru['Tanggal'], y=hasil_baru['CI_Atas'], mode="lines", line=dict(color="rgba(0,0,0,0)"), showlegend=False))
            f.add_trace(go.Scatter(x=hasil_baru['Tanggal'], y=hasil_baru['CI_Bawah'], fill="tonexty", mode="lines", fillcolor="rgba(139, 92, 246, 0.22)", line=dict(color="rgba(0,0,0,0)"), name="Interval 95%"))
            f.add_trace(go.Scatter(x=hasil_baru['Tanggal'], y=hasil_baru['Prediksi'], name="Prediksi", line=dict(color=ORANGE, width=3, dash="dot", shape='spline')))
            L = tata(380)
            ymax = float(max(np.max(ts_baru.values[-60:]), hasil_baru['CI_Atas'].max()))
            L['yaxis']['range'] = [0, ymax * 1.1]
            f.update_layout(**L)
            tampil(anim_garis(f, [[0], [1, 2, 3]]))

        spasi(16)
        tabel_html(hasil_baru.assign(Tanggal=pd.to_datetime(hasil_baru['Tanggal']).dt.strftime('%d %b %Y')),
                   fmt={'Prediksi': '{:.2f}', 'CI_Bawah': '{:.2f}', 'CI_Atas': '{:.2f}'}, tinggi=360)
        spasi(12)
        st.download_button("⬇ Unduh CSV", data=hasil_baru.to_csv(index=False).encode('utf-8'), file_name="peramalan.csv", mime="text/csv")
    else:
        st.info("Unggah berkas data gangguan untuk memulai peramalan bergulir.")

# ============================================================
# 15. ROUTING
# ============================================================
halaman = st.session_state.halaman

if halaman == 'Ringkasan':
    kpi()
    spasi(24)
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.container(border=True):
            judul("Tren Gangguan Harian", "Aktual vs prediksi"); tampil(g_tren())
    with c2:
        with st.container(border=True):
            judul("Penyebab Gangguan", "Lima kategori"); tampil(g_penyebab(), 30, True)
    spasi(24)
    c3, c4, c5 = st.columns(3)
    with c3:
        with st.container(border=True):
            judul("Peramalan 30 Hari", "Interval 95%"); tampil(g_ramal())
    with c4:
        with st.container(border=True):
            judul("Distribusi Bulanan", "Volume per bulan"); tampil(g_bulan(), 28, True)
    with c5:
        with st.container(border=True):
            judul("Kanal Pelaporan", "Sumber laporan"); st.markdown(f'<div style="padding-top:8px;">{b_sumber()}</div>', unsafe_allow_html=True)
    spasi(24)
    judul("Perbandingan Model vs Baseline", "Evaluasi pada data testing"); t_metrik(); catatan()

elif halaman == 'Tren Harian':
    kpi(); spasi(24)
    with st.container(border=True):
        judul("Tren Gangguan Harian", "Data aktual dan prediksi"); tampil(g_tren(420))
    spasi(24)
    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            judul("Distribusi Bulanan", "Volume per bulan"); tampil(g_bulan(320), 28, True)
    with b:
        with st.container(border=True):
            judul("Statistik Deskriptif", "Ringkasan periode")
            s = hist_f[kol_val]; total = f"{int(s.sum()):,}".replace(",", ".")
            st.markdown(
                f'<table style="width:100%;font-size:13px;font-weight:500;border-collapse:collapse;">'
                f'<tr style="border-bottom:1px solid rgba(255,255,255,0.07);"><td style="padding:14px 0;color:{TEXT_GRAY};">Total</td><td style="padding:14px 0;text-align:right;color:{TEXT_MAIN};font-weight:700;">{total}</td></tr>'
                f'<tr style="border-bottom:1px solid rgba(255,255,255,0.07);"><td style="padding:14px 0;color:{TEXT_GRAY};">Rata-rata</td><td style="padding:14px 0;text-align:right;color:{TEXT_MAIN};font-weight:700;">{s.mean():.2f}</td></tr>'
                f'<tr><td style="padding:14px 0;color:{TEXT_GRAY};">Maksimum</td><td style="padding:14px 0;text-align:right;color:{MERAH};font-weight:700;">{int(s.max())}</td></tr></table>',
                unsafe_allow_html=True)

elif halaman == 'Peramalan':
    k1, k2, k3 = st.columns(3)
    with k1: st.metric("PROYEKSI", f"{peramalan['Prediksi'].mean():.2f}".replace(".", ","), "gangguan / hari ↗")
    with k2: st.metric("BATAS BAWAH", f"{peramalan['CI_Bawah'].min():.1f}".replace(".", ","), "interval 95%")
    with k3: st.metric("BATAS ATAS", f"{peramalan['CI_Atas'].max():.1f}".replace(".", ","), "interval 95%")
    spasi(24)
    with st.container(border=True):
        judul("Peramalan 30 Hari ke Depan", "Prediksi beserta interval 95%"); tampil(g_ramal(400))
    spasi(20)
    judul("Tabel Hasil Peramalan", "Rincian prediksi harian")
    tp = peramalan.copy(); tp['Tanggal'] = pd.to_datetime(tp['Tanggal']).dt.strftime('%d %b %Y')
    tabel_html(tp, fmt={'Prediksi': '{:.2f}', 'CI_Bawah': '{:.2f}', 'CI_Atas': '{:.2f}'}, tinggi=320)
    simulasi_skenario()

elif halaman == 'Perbarui & Ramalkan':
    judul("Perbarui Data dan Ramalkan Ulang", "Unggah data terbaru"); halaman_perbarui_ramalkan()

elif halaman == 'Analisis Penyebab':
    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            judul("Distribusi Penyebab", "Kategori terbanyak"); tampil(g_penyebab(340), 30, True)
    with b:
        with st.container(border=True):
            judul("Kanal Pelaporan", "Sumber laporan"); st.markdown(f'<div style="padding-top:8px;">{b_sumber()}</div>', unsafe_allow_html=True)
    spasi(20)
    judul("Rincian Penyebab", "Seluruh kategori")
    p = penyebab.copy(); p['Proporsi (%)'] = (p['Jumlah'] / p['Jumlah'].sum() * 100).round(2)
    tabel_html(p.head(15), tinggi=380)

elif halaman == 'Perbandingan Model':
    st.markdown('<div class="glass" style="margin-bottom:24px;"><div class="glass-title">Bandingkan Model</div>'
                '<div class="glass-text" style="margin:0;">Klik salah satu tombol untuk melihat performa.</div></div>', unsafe_allow_html=True)
    kartu_model_toggle()
    spasi(24)
    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            judul("MASE Seluruh Model", "Semakin rendah semakin baik"); tampil(g_progres_optimasi(), 28, True)
    with b:
        with st.container(border=True):
            judul("R² Seluruh Model", "Semakin tinggi semakin baik"); tampil(g_progres_r2(), 28, True)
    spasi(20)
    judul("Tabel Lengkap", "ARIMA, SARIMAX, dan baseline"); t_metrik()
    st.markdown('<div class="note green" style="margin-top:20px;padding:20px 24px;"><div class="t" style="font-size:14px;margin-bottom:8px;">Kesimpulan</div>'
                '<div class="d" style="font-size:12.5px;line-height:1.8;">Model final yang digunakan adalah ARIMA(1,1,1). Penambahan eksogen tidak meningkatkan akurasi.</div></div>',
                unsafe_allow_html=True)

elif halaman == 'Akurasi Model':
    baris_terbaik = metrik.loc[metrik['MASE'].idxmin()]; ar = baris_terbaik
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.metric("MAE", f"{ar['MAE']:.2f}".replace(".", ","), "absolute error")
    with k2: st.metric("RMSE", f"{ar['RMSE']:.2f}".replace(".", ","), "root mean sq.")
    with k3: st.metric("sMAPE", f"{ar['sMAPE(%)']:.2f}%".replace(".", ","), "symmetric MAPE")
    with k4: st.metric("MASE", f"{ar['MASE']:.3f}".replace(".", ","), "model terbaik")
    spasi(24)
    judul("Perbandingan Model vs Baseline", "Evaluasi pada data testing"); t_metrik(); catatan()
    spasi(20)
    judul("Validasi Model", "Uji diagnostik residual")
    v1, v2, v3 = st.columns(3)
    for kol, (label, nilai) in zip([v1, v2, v3], [("Ljung-Box Lag 7", "0,609"), ("Ljung-Box Lag 14", "0,713"), ("Ljung-Box Lag 21", "0,671")]):
        with kol:
            st.markdown(
                f'<div class="glass" style="text-align:center;"><div style="color:{TEXT_GRAY};font-family:JetBrains Mono,monospace;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">{label}</div>'
                f'<div style="color:{HIJAU};font-family:Orbitron,sans-serif;font-size:36px;font-weight:700;margin:10px 0 6px;animation:flicker 3s infinite;text-shadow:0 0 24px rgba(52,211,153,.5);">{nilai}</div>'
                f'<div style="color:{TEXT_GRAY};font-size:11px;font-weight:500;">p &gt; 0,05 · white noise</div></div>', unsafe_allow_html=True)

# ============================================================
# 16. FOOTER
# ============================================================
st.markdown(f'<div style="text-align:center;color:{TEXT_GRAY};font-family:JetBrains Mono,monospace;font-size:11px;font-weight:500;padding:30px 0 10px;border-top:1px solid rgba(34,211,238,0.15);margin-top:30px;letter-spacing:.5px;">Dashboard Peramalan Gangguan Kabel Sambungan Rumah &nbsp;·&nbsp; PT. Haleyora Power Serpong &nbsp;·&nbsp; ARIMA(1,1,1) &nbsp;·&nbsp; CRISP-DM Framework</div>', unsafe_allow_html=True)
