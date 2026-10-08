import streamlit as st
from components.upload_section import render_upload_section
from components.result_dashboard import render_result_dashboard
from components.sidebar import render_sidebar

st.set_page_config(
    page_title="Diagnova · AI-Powered Lab Report Interpreter",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Tokens ── */
:root {
    --blue-900:     #0a2472;
    --blue-800:     #0d3b9e;
    --blue-700:     #1a56c4;
    --blue-600:     #1e6be6;
    --blue-500:     #2d8ef5;
    --blue-400:     #4daeff;
    --blue-100:     #dbeeff;
    --blue-50:      #eef6ff;
    --cyan:         #00b4d8;
    --bg-page:      #f0f6ff;
    --bg-white:     #ffffff;
    --border:       #d0e4f7;
    --border-mid:   #a8ccf0;
    --text-dark:    #0a2472;
    --text-body:    #2c4a6e;
    --text-muted:   #6b8dae;
    --text-light:   #9ab5cc;
    --green:        #00a67e;
    --green-light:  #e6f7f3;
    --green-border: #a3dece;
    --yellow:       #c97800;
    --yellow-light: #fff4e0;
    --yellow-border:#f5c878;
    --red:          #d93025;
    --red-light:    #fdecea;
    --red-border:   #f4a9a5;
    --shadow-sm:    0 1px 4px rgba(10,36,114,0.07);
    --shadow-md:    0 4px 16px rgba(10,36,114,0.10);
    --shadow-lg:    0 8px 32px rgba(10,36,114,0.13);
    --radius-sm:    8px;
    --radius-md:    14px;
    --radius-lg:    20px;
    --radius-xl:    28px;
}

/* ── Base ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background: var(--bg-page) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text-body) !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 10% 0%,  rgba(45,142,245,0.13) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 100%, rgba(0,180,216,0.10) 0%, transparent 60%),
        linear-gradient(180deg, #eef6ff 0%, #f5f9ff 50%, #f0f6ff 100%);
    pointer-events: none; z-index: 0;
}

[data-testid="block-container"] {
    padding: 1rem 1.5rem 3rem !important;
    position: relative; z-index: 1;
    max-width: 1400px !important;
}

@media (max-width: 768px) {
    [data-testid="block-container"] { padding: 0.5rem 0.6rem 2rem !important; }
}

/* ── Hide sidebar entirely ── */
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── Kill ALL dark widget backgrounds ── */
[data-testid="stFileUploader"],
[data-testid="stFileUploader"] > div,
[data-testid="stFileUploaderDropzone"],
[data-baseweb="select"],
[data-baseweb="select"] > div,
[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"],
[role="option"] {
    background: var(--bg-white) !important;
    background-color: var(--bg-white) !important;
    color: var(--text-dark) !important;
    border-color: var(--border) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"], .stDeployButton { display: none; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-page); }
::-webkit-scrollbar-thumb { background: var(--blue-400); border-radius: 10px; }

/* ── Expander (sidebar replacement) ── */
[data-testid="stExpander"] {
    background: var(--bg-white) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: 1.2rem !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] summary {
    background: var(--blue-50) !important;
    color: var(--blue-700) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.8rem 1.2rem !important;
    border-radius: var(--radius-lg) !important;
}
[data-testid="stExpander"] summary:hover {
    background: var(--blue-100) !important;
}
[data-testid="stExpander"] summary span {
    color: var(--blue-700) !important;
}
[data-testid="stExpander"] summary svg {
    fill: var(--blue-700) !important;
    color: var(--blue-700) !important;
}

/* ── Hero ── */
.hero-wrapper {
    background: linear-gradient(135deg, var(--blue-900) 0%, var(--blue-700) 60%, var(--cyan) 100%);
    border-radius: var(--radius-xl);
    padding: 2.2rem 2.5rem;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.2rem;
    position: relative; overflow: hidden;
    box-shadow: var(--shadow-lg);
    gap: 1rem;
}
.hero-wrapper::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 250px; height: 250px;
    background: rgba(255,255,255,0.05); border-radius: 50%;
}
.hero-left { position: relative; z-index: 2; flex: 1; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.25);
    color: #fff !important;
    font-size: 0.65rem; font-weight: 600;
    letter-spacing: 0.13em; text-transform: uppercase;
    padding: 4px 12px; border-radius: 100px; margin-bottom: 0.8rem;
}
.badge-dot {
    width: 6px; height: 6px; background: #7efff5;
    border-radius: 50%; animation: pdot 2s infinite; flex-shrink: 0;
}
@keyframes pdot {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.4; transform:scale(0.7); }
}
.hero-title {
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 800; color: #fff !important;
    letter-spacing: -0.03em; line-height: 1.1; margin: 0 0 0.5rem 0;
}
.hero-title span { color: #7efff5 !important; }
.hero-subtitle {
    font-size: clamp(0.8rem, 2vw, 0.95rem);
    color: rgba(255,255,255,0.78) !important;
    font-weight: 400; line-height: 1.6; max-width: 440px;
}
.hero-stats { display: flex; gap: 0.8rem; position: relative; z-index: 2; flex-shrink: 0; }
.hero-stat-box {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: var(--radius-md);
    padding: 0.8rem 1.1rem; text-align: center;
    backdrop-filter: blur(10px); min-width: 75px;
}
.hero-stat-num {
    display: block; font-size: 1.6rem; font-weight: 800; color: #fff !important;
    font-family: 'JetBrains Mono', monospace !important;
    line-height: 1; margin-bottom: 3px;
}
.hero-stat-lbl {
    font-size: 0.6rem; color: rgba(255,255,255,0.65) !important;
    text-transform: uppercase; letter-spacing: 0.1em;
}
@media (max-width: 768px) {
    .hero-wrapper { flex-direction: column; align-items: flex-start; padding: 1.4rem; }
    .hero-stats { width: 100%; justify-content: space-between; }
    .hero-stat-box { flex: 1; min-width: unset; }
}

/* ── Section Label ── */
.section-label {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--blue-700) !important; margin-bottom: 0.8rem;
}
.section-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, var(--border-mid), transparent);
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    background: var(--bg-white) !important;
    border-radius: var(--radius-md) !important;
    border: none !important; padding: 0 !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: var(--blue-50) !important;
    border: 2px dashed var(--border-mid) !important;
    border-radius: var(--radius-md) !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: var(--blue-500) !important;
    background: #e0f0ff !important;
}
[data-testid="stFileUploaderDropzone"] * { color: var(--text-muted) !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: var(--blue-700) !important;
    color: #fff !important; border: none !important;
    border-radius: var(--radius-sm) !important; font-weight: 600 !important;
}
[data-testid="stFileUploaderDropzone"] svg { fill: var(--blue-400) !important; }
small { color: var(--text-light) !important; }

/* ── Selectbox ── */
[data-baseweb="select"] > div {
    background: var(--bg-white) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-dark) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-baseweb="select"] > div:hover { border-color: var(--blue-500) !important; }
[data-baseweb="select"] span,
[data-baseweb="select"] div { color: var(--text-dark) !important; background: transparent !important; }
[data-baseweb="select"] svg { fill: var(--text-muted) !important; }
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[role="listbox"] {
    background: var(--bg-white) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    box-shadow: var(--shadow-md) !important;
}
[role="option"] { background: var(--bg-white) !important; color: var(--text-dark) !important; font-size: 0.88rem !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background: var(--blue-50) !important; color: var(--blue-700) !important; }

/* ── Radio — force all text dark ── */
[data-testid="stRadio"] > div {
    background: var(--blue-50) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 0.4rem 0.6rem !important;
    flex-wrap: wrap !important;
}
[data-testid="stRadio"] label,
[data-testid="stRadio"] label *,
[data-testid="stRadio"] p,
[data-testid="stRadio"] span,
div[role="radiogroup"] label,
div[role="radiogroup"] label *,
div[role="radiogroup"] p,
div[role="radiogroup"] span {
    color: var(--text-body) !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
}

/* ── Textarea ── */
.stTextArea textarea {
    background: var(--bg-white) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-dark) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.83rem !important;
}
.stTextArea textarea:focus {
    border-color: var(--blue-500) !important;
    box-shadow: 0 0 0 3px rgba(45,142,245,0.12) !important;
}
.stTextArea textarea::placeholder { color: var(--text-light) !important; }
.stTextArea label { display: none !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--blue-800), var(--blue-500)) !important;
    color: #fff !important; border: none !important;
    border-radius: var(--radius-md) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important; font-size: 0.9rem !important;
    padding: 0.7rem 1.5rem !important;
    box-shadow: 0 4px 18px rgba(13,59,158,0.28) !important;
    transition: all 0.25s ease !important; width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(13,59,158,0.38) !important;
}
[data-testid="stDownloadButton"] button {
    background: #fff !important; color: var(--blue-700) !important;
    border: 2px solid var(--blue-500) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important; width: 100% !important;
    transition: all 0.25s !important;
}
[data-testid="stDownloadButton"] button:hover { background: var(--blue-50) !important; }

hr { border-color: var(--border) !important; margin: 1rem 0 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--blue-50) !important;
    border-radius: var(--radius-md) !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    flex-wrap: wrap !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.78rem !important; font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.4rem 0.8rem !important; border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--bg-white) !important;
    color: var(--blue-700) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span {
    color: var(--text-body) !important;
}

/* ── Override ALL st.warning / st.error / st.info colors ── */
[data-testid="stAlert"] {
    background: #fff8e1 !important;
    border: 1.5px solid #f5c878 !important;
    border-radius: var(--radius-md) !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div,
[data-testid="stAlert"] * {
    color: #7a5c00 !important;
}
[data-testid="stAlert"] svg {
    fill: #c97800 !important;
    color: #c97800 !important;
}

/* ── Result Card ── */
.result-card {
    background: var(--bg-white); border-radius: var(--radius-md);
    padding: 1.2rem; border: 1.5px solid var(--border);
    box-shadow: var(--shadow-sm);
    position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
    margin-bottom: 0.8rem; word-break: break-word;
}
.result-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.result-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; }
.result-card.green  { border-color: var(--green-border);  background: linear-gradient(160deg, var(--green-light)  0%, #fff 50%); }
.result-card.yellow { border-color: var(--yellow-border); background: linear-gradient(160deg, var(--yellow-light) 0%, #fff 50%); }
.result-card.red    { border-color: var(--red-border);    background: linear-gradient(160deg, var(--red-light)    0%, #fff 50%); }
.result-card.green::before  { background: linear-gradient(90deg, var(--green),  #69e0ae); }
.result-card.yellow::before { background: linear-gradient(90deg, var(--yellow), #f5c878); }
.result-card.red::before    { background: linear-gradient(90deg, var(--red),    #f4a9a5); }

.rc-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem; gap: 0.5rem; flex-wrap: wrap; }
.rc-name { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted) !important; }
.rc-badge { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; padding: 2px 8px; border-radius: 100px; white-space: nowrap; }
.badge-green  { background: var(--green-light);  color: var(--green)  !important; border: 1px solid var(--green-border); }
.badge-yellow { background: var(--yellow-light); color: var(--yellow) !important; border: 1px solid var(--yellow-border); }
.badge-red    { background: var(--red-light);    color: var(--red)    !important; border: 1px solid var(--red-border); }
.rc-value { font-size: clamp(1.4rem, 4vw, 2rem); font-weight: 800; font-family: 'JetBrains Mono', monospace !important; line-height: 1; margin-bottom: 2px; }
.rc-value.green  { color: var(--green)  !important; }
.rc-value.yellow { color: var(--yellow) !important; }
.rc-value.red    { color: var(--red)    !important; }
.rc-unit  { font-size: 0.68rem; color: var(--text-light) !important; font-family: 'JetBrains Mono', monospace !important; margin-bottom: 0.5rem; }
.rc-range { font-size: 0.7rem; color: var(--text-muted) !important; margin-bottom: 0.6rem; }
.rc-bar-track { height: 4px; background: rgba(10,36,114,0.07); border-radius: 10px; overflow: hidden; margin-bottom: 0.7rem; }
.rc-bar-fill  { height: 100%; border-radius: 10px; }
.rc-bar-fill.green  { background: linear-gradient(90deg, var(--green),  #69e0ae); }
.rc-bar-fill.yellow { background: linear-gradient(90deg, var(--yellow), #f5c878); }
.rc-bar-fill.red    { background: linear-gradient(90deg, var(--red),    #f4a9a5); }
.rc-explanation { font-size: 0.8rem; color: var(--text-body) !important; line-height: 1.6; border-top: 1px solid rgba(10,36,114,0.07); padding-top: 0.6rem; }

/* ── Stat chip ── */
.stat-chip { display: block; width: 100%; padding: 0.9rem 0.5rem; border-radius: var(--radius-md); text-align: center; border: 1.5px solid; background: var(--bg-white); box-shadow: var(--shadow-sm); margin-bottom: 0.5rem; }
.stat-chip.green  { border-color: var(--green-border); }
.stat-chip.yellow { border-color: var(--yellow-border); }
.stat-chip.red    { border-color: var(--red-border); }
.stat-chip-num { display: block; font-size: clamp(1.4rem, 4vw, 2rem); font-weight: 800; font-family: 'JetBrains Mono', monospace !important; line-height: 1; margin-bottom: 3px; }
.stat-chip.green  .stat-chip-num { color: var(--green)  !important; }
.stat-chip.yellow .stat-chip-num { color: var(--yellow) !important; }
.stat-chip.red    .stat-chip-num { color: var(--red)    !important; }
.stat-chip-lbl { font-size: 0.62rem; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; }

/* ── Summary ── */
.summary-panel { background: linear-gradient(135deg, var(--blue-50), #fff); border: 1.5px solid var(--blue-100); border-radius: var(--radius-lg); padding: 1.4rem; margin-top: 1rem; box-shadow: var(--shadow-sm); }
.summary-title { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase; color: var(--blue-700) !important; margin-bottom: 0.7rem; }
.summary-text  { font-size: 0.88rem; color: var(--text-body) !important; line-height: 1.8; }

/* ── Next Steps ── */
.next-step-item { display: flex; align-items: flex-start; gap: 0.8rem; padding: 0.9rem 1rem; background: var(--bg-white); border-radius: var(--radius-md); border: 1.5px solid var(--border); margin-bottom: 0.6rem; box-shadow: var(--shadow-sm); transition: box-shadow 0.2s; }
.next-step-item:hover { box-shadow: var(--shadow-md); }
.step-tag { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 2px 7px; border-radius: 100px; margin-bottom: 3px; display: inline-block; }
.tag-monitor { background: var(--green-light);  color: var(--green)  !important; border: 1px solid var(--green-border); }
.tag-consult { background: var(--yellow-light); color: var(--yellow) !important; border: 1px solid var(--yellow-border); }
.tag-urgent  { background: var(--red-light);    color: var(--red)    !important; border: 1px solid var(--red-border); }
.step-text   { font-size: 0.83rem; color: var(--text-body) !important; line-height: 1.55; }

/* ── Disclaimer ── */
.disclaimer { background: #fffbea; border: 1.5px solid #f5c878; border-radius: var(--radius-md); padding: 0.9rem 1.2rem; margin-top: 1.2rem; display: flex; align-items: flex-start; gap: 0.7rem; }
.disclaimer-text { font-size: 0.78rem; color: #7a5c00 !important; line-height: 1.6; }

/* ── Mobile columns stack ── */
@media (max-width: 768px) {
    [data-testid="stHorizontalBlock"] { flex-direction: column !important; }
    [data-testid="stHorizontalBlock"] > div { width: 100% !important; min-width: 100% !important; flex: none !important; }
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
.animate-in { animation: fadeUp 0.4s ease forwards; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper animate-in">
    <div class="hero-left">
        <div class="hero-badge">
            <span class="badge-dot"></span>
            AI-Powered · Medical Intelligence
        </div>
        <h1 class="hero-title">Diagno<span>va</span></h1>
        <p class="hero-subtitle">
            Upload your diagnostic report and receive clear, structured insights — 
            understanding your health has never been this accessible.
        </p>
    </div>
    <div class="hero-stats">
        <div class="hero-stat-box">
            <span class="hero-stat-num">50+</span>
            <span class="hero-stat-lbl">Parameters</span>
        </div>
        <div class="hero-stat-box">
            <span class="hero-stat-num">3</span>
            <span class="hero-stat-lbl">Risk Levels</span>
        </div>
        <div class="hero-stat-box">
            <span class="hero-stat-num">AI</span>
            <span class="hero-stat-lbl">Powered</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Info Expander (replaces sidebar) ─────────────────────────────────────────
render_sidebar()

# ── Main Layout ───────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.6], gap="medium")

with col_left:
    render_upload_section()

with col_right:
    render_result_dashboard()

# ── Disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer animate-in">
    <span style="font-size:1rem;flex-shrink:0;margin-top:1px;">⚕️</span>
    <span class="disclaimer-text">
        <strong>Medical Disclaimer:</strong> Diagnova is an educational tool designed to help you 
        understand your lab results. It does not replace professional medical advice, diagnosis, or 
        treatment. Always consult a qualified healthcare provider with questions about your health.
    </span>
</div>
""", unsafe_allow_html=True)
