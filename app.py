import sys
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ── Design System Tokens ── */
:root {
    --blue-950:     #051336;
    --blue-900:     #0a2472;
    --blue-800:     #0d3b9e;
    --blue-700:     #1a56c4;
    --blue-600:     #1e6be6;
    --blue-500:     #2d8ef5;
    --blue-400:     #4daeff;
    --blue-200:     #bfdbfe;
    --blue-100:     #dbeeff;
    --blue-50:      #f0f7ff;
    --cyan-500:     #00b4d8;
    --cyan-400:     #38bdf8;
    --bg-page:      #f8fafc;
    --bg-white:     #ffffff;
    --border:       #e2e8f0;
    --border-mid:   #cbd5e1;
    --text-dark:    #0f172a; /* Ultra crisp dark slate for 100% legibility */
    --text-body:    #1e293b;
    --text-muted:   #475569;
    --text-light:   #64748b;
    --green:        #059669;
    --green-light:  #ecfdf5;
    --green-border: #a7f3d0;
    --yellow:       #d97706;
    --yellow-light: #fffbeb;
    --yellow-border:#fde68a;
    --red:          #dc2626;
    --red-light:    #fef2f2;
    --red-border:   #fecaca;
    --shadow-xs:    0 1px 2px rgba(15, 23, 42, 0.05);
    --shadow-sm:    0 2px 8px rgba(15, 23, 42, 0.06);
    --shadow-md:    0 6px 20px rgba(15, 23, 42, 0.08);
    --shadow-lg:    0 12px 36px rgba(10, 36, 114, 0.12);
    --radius-sm:    8px;
    --radius-md:    12px;
    --radius-lg:    18px;
    --radius-xl:    24px;
}

/* ── Base Page ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background: var(--bg-page) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: var(--text-dark) !important;
    -webkit-font-smoothing: antialiased;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 70% 50% at 5% 0%, rgba(45,142,245,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 95% 100%, rgba(0,180,216,0.07) 0%, transparent 60%),
        linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    pointer-events: none; z-index: 0;
}

[data-testid="block-container"] {
    padding: 1.2rem 2rem 3.5rem !important;
    position: relative; z-index: 1;
    max-width: 1440px !important;
}

@media (max-width: 768px) {
    [data-testid="block-container"] { padding: 0.6rem 0.8rem 2rem !important; }
}

/* ── Chrome Cleanup ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"], .stDeployButton { display: none; }
[data-testid="stSidebar"] { display: none !important; }
[data-testid="collapsedControl"] { display: none !important; }

/* ── Scrollbars ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-page); }
::-webkit-scrollbar-thumb { background: var(--border-mid); border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: var(--blue-400); }

/* ── Hero Banner ── */
.hero-wrapper {
    background: linear-gradient(135deg, #07173e 0%, #0d3b9e 55%, #0284c7 100%);
    border-radius: var(--radius-xl);
    padding: 2.2rem 2.6rem;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 1.4rem;
    position: relative; overflow: hidden;
    box-shadow: var(--shadow-lg);
    gap: 1.5rem;
    border: 1px solid rgba(255,255,255,0.15);
}
.hero-wrapper::after {
    content: ''; position: absolute; right: -40px; top: -40px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}
.hero-left { position: relative; z-index: 2; flex: 1; }
.hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.25);
    color: #ffffff !important;
    font-size: 0.7rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    padding: 5px 14px; border-radius: 99px; margin-bottom: 0.8rem;
    backdrop-filter: blur(8px);
}
.badge-dot {
    width: 7px; height: 7px; background: #38bdf8;
    border-radius: 50%; box-shadow: 0 0 10px #38bdf8;
    animation: pdot 2s infinite ease-in-out; flex-shrink: 0;
}
@keyframes pdot {
    0%,100% { opacity:1; transform:scale(1); }
    50%      { opacity:0.3; transform:scale(0.7); }
}
.hero-title {
    font-size: clamp(2rem, 3.8vw, 2.9rem);
    font-weight: 800; color: #ffffff !important;
    letter-spacing: -0.03em; line-height: 1.1; margin: 0 0 0.5rem 0;
}
.hero-title span { color: #38bdf8 !important; }
.hero-subtitle {
    font-size: clamp(0.85rem, 1.8vw, 0.98rem);
    color: rgba(255,255,255,0.85) !important;
    font-weight: 400; line-height: 1.6; max-width: 460px; margin: 0;
}
.hero-stats { display: flex; gap: 0.8rem; position: relative; z-index: 2; flex-shrink: 0; }
.hero-stat-box {
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: var(--radius-md);
    padding: 0.85rem 1.2rem; text-align: center;
    backdrop-filter: blur(12px); min-width: 84px;
}
.hero-stat-num {
    display: block; font-size: 1.6rem; font-weight: 800; color: #ffffff !important;
    font-family: 'JetBrains Mono', monospace !important;
    line-height: 1; margin-bottom: 4px;
}
.hero-stat-lbl {
    font-size: 0.62rem; color: rgba(255,255,255,0.7) !important;
    text-transform: uppercase; letter-spacing: 0.1em; font-weight: 600;
}
@media (max-width: 768px) {
    .hero-wrapper { flex-direction: column; align-items: flex-start; padding: 1.5rem; }
    .hero-stats { width: 100%; justify-content: space-between; }
    .hero-stat-box { flex: 1; min-width: unset; }
}

/* ── Section Title Badges ── */
.section-label {
    display: flex; align-items: center; gap: 9px;
    font-size: 0.72rem; font-weight: 800;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--blue-700) !important; margin-bottom: 0.9rem;
}
.section-label::after {
    content: ''; flex: 1; height: 1.5px;
    background: linear-gradient(90deg, var(--border-mid), transparent);
}

/* ══════════════════════════════════════════════════
   GLOBAL FORM CONTROLS — STRICT HIGH CONTRAST & VISIBILITY
   ══════════════════════════════════════════════════ */

/* All Inputs, Textareas, Native Selects */
input, textarea, select {
    color: var(--text-dark) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Streamlit Selectbox (Report Type & all dropdowns) ── */
div[data-testid="stSelectbox"] {
    background: transparent !important;
}

div[data-testid="stSelectbox"] > div {
    background: transparent !important;
}

/* Force crisp white container for BaseWeb select */
div[data-testid="stSelectbox"] [data-baseweb="select"],
div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
div[data-testid="stSelectbox"] [data-baseweb="select"] div,
[data-baseweb="select"],
[data-baseweb="select"] > div,
[data-baseweb="select"] div {
    background-color: #ffffff !important;
    background: #ffffff !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-baseweb="select"] > div {
    border: 1.5px solid #cbd5e1 !important;
    border-radius: var(--radius-md) !important;
    min-height: 44px !important;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}

div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
[data-baseweb="select"] > div:hover {
    border-color: #1e6be6 !important;
    box-shadow: 0 0 0 3px rgba(30, 107, 230, 0.12) !important;
}

/* FORCE ULTRA-DARK LEGIBLE TEXT & ICONS IN SELECTBOX */
div[data-testid="stSelectbox"] *,
div[data-testid="stSelectbox"] span,
div[data-testid="stSelectbox"] p,
div[data-testid="stSelectbox"] div,
[data-baseweb="select"] *,
[data-baseweb="select"] span,
[data-baseweb="select"] div,
[data-baseweb="select"] input {
    color: #0f172a !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
}

div[data-testid="stSelectbox"] svg,
[data-baseweb="select"] svg {
    fill: #0f172a !important;
    color: #0f172a !important;
}

/* BaseWeb Popover & Dropdown Menu */
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
ul[data-baseweb="menu"],
div[data-baseweb="menu"],
[data-baseweb="menu"] ul,
[role="listbox"] {
    background-color: #ffffff !important;
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: var(--radius-md) !important;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.14) !important;
    padding: 6px !important;
}

li[role="option"],
div[role="option"],
[role="option"] {
    background-color: #ffffff !important;
    background: #ffffff !important;
    color: #0f172a !important;
    border-radius: 8px !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    padding: 9px 12px !important;
    margin-bottom: 2px !important;
}

li[role="option"] *,
div[role="option"] *,
[role="option"] * {
    color: #0f172a !important;
}

li[role="option"]:hover,
div[role="option"]:hover,
[role="option"]:hover,
[role="option"][aria-selected="true"] {
    background-color: #eff6ff !important;
    background: #eff6ff !important;
    color: #1d4ed8 !important;
    font-weight: 700 !important;
}

li[role="option"]:hover *,
div[role="option"]:hover *,
[role="option"]:hover *,
[role="option"][aria-selected="true"] * {
    color: #1d4ed8 !important;
    font-weight: 700 !important;
}

/* ── Textarea ── */
.stTextArea textarea {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: var(--radius-md) !important;
    color: #0f172a !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
    padding: 12px !important;
    line-height: 1.5 !important;
    box-shadow: var(--shadow-xs) !important;
}
.stTextArea textarea:focus {
    border-color: #1e6be6 !important;
    box-shadow: 0 0 0 3px rgba(30, 107, 230, 0.15) !important;
}
.stTextArea textarea::placeholder {
    color: #64748b !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── File Uploader ── */
div[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
    background-color: #f8fafc !important;
    border: 2px dashed #93c5fd !important;
    border-radius: var(--radius-md) !important;
    padding: 1.4rem 1.2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #1e6be6 !important;
    background: #eff6ff !important;
}
/* Instruction text inside dropzone */
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] div,
[data-testid="stFileUploaderDropzone"] small {
    color: #334155 !important;
    font-weight: 500 !important;
}
[data-testid="stFileUploaderDropzone"] small {
    color: #64748b !important;
}

/* UPLOAD BUTTON INSIDE DROPZONE — HIGH CONTRAST WHITE TEXT */
[data-testid="stFileUploaderDropzone"] button,
section[data-testid="stFileUploaderDropzone"] button,
button[data-testid="baseButton-secondary"] {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    background-color: #2563eb !important;
    color: #ffffff !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35) !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s ease !important;
}
[data-testid="stFileUploaderDropzone"] button *,
section[data-testid="stFileUploaderDropzone"] button *,
button[data-testid="baseButton-secondary"] * {
    color: #ffffff !important;
    fill: #ffffff !important;
    font-weight: 700 !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
}
[data-testid="stFileUploaderDropzone"] button:hover,
section[data-testid="stFileUploaderDropzone"] button:hover,
button[data-testid="baseButton-secondary"]:hover {
    background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%) !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Radios / Pills ── */
div[data-testid="stRadio"] {
    background: transparent !important;
}
div[data-testid="stRadio"] > div {
    background: #f1f5f9 !important;
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: var(--radius-md) !important;
    padding: 6px 12px !important;
    gap: 12px !important;
    width: fit-content !important;
}
div[data-testid="stRadio"] label {
    cursor: pointer !important;
}
div[data-testid="stRadio"] label *,
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label div {
    color: #0f172a !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
}

/* ── Primary Action Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--blue-800) 0%, var(--blue-600) 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    padding: 0.75rem 1.4rem !important;
    box-shadow: 0 4px 14px rgba(13, 59, 158, 0.25) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
.stButton > button * {
    color: #ffffff !important;
    font-weight: 700 !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(13, 59, 158, 0.35) !important;
    background: linear-gradient(135deg, var(--blue-700) 0%, var(--blue-500) 100%) !important;
}

/* ══════════════════════════════════════════════════
   CHATBOT STYLING — VISIBLE TEXT & CLEAN DESIGN
   ══════════════════════════════════════════════════ */

/* The outer chat input bar */
[data-testid="stChatInput"],
div[data-testid="stChatInput"] {
    background: transparent !important;
    padding: 0.6rem 0 !important;
}

/* The input container frame */
[data-testid="stChatInput"] > div,
div[data-testid="stChatInput"] > div {
    background: #ffffff !important;
    background-color: #ffffff !important;
    border: 2px solid #cbd5e1 !important;
    border-radius: var(--radius-lg) !important;
    box-shadow: 0 4px 18px rgba(15, 23, 42, 0.08) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    padding: 4px 8px !important;
}

[data-testid="stChatInput"] > div:focus-within,
div[data-testid="stChatInput"] > div:focus-within {
    border-color: #1e6be6 !important;
    box-shadow: 0 0 0 4px rgba(30, 107, 230, 0.16) !important;
}

/* THE CHAT TEXTAREA — GUARANTEED HIGH-CONTRAST DARK TEXT */
[data-testid="stChatInput"] textarea,
div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    background-color: transparent !important;
    color: #0f172a !important;            /* CRISP DARK SLATE TEXT */
    caret-color: #1e6be6 !important;       /* VIBRANT BLUE CARET */
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    line-height: 1.5 !important;
    padding: 8px 12px !important;
}

/* Placeholder */
[data-testid="stChatInput"] textarea::placeholder,
div[data-testid="stChatInput"] textarea::placeholder {
    color: #64748b !important;
    font-weight: 400 !important;
    opacity: 1 !important;
}

/* Send Button */
[data-testid="stChatInput"] button,
div[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #0d3b9e 0%, #1e6be6 100%) !important;
    border-radius: var(--radius-sm) !important;
    border: none !important;
    width: 36px !important;
    height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: transform 0.15s ease !important;
    margin-right: 4px !important;
}
[data-testid="stChatInput"] button:hover,
div[data-testid="stChatInput"] button:hover {
    transform: scale(1.06) !important;
}
[data-testid="stChatInput"] button svg,
div[data-testid="stChatInput"] button svg {
    fill: #ffffff !important;
    color: #ffffff !important;
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.1rem 1.3rem !important;
    margin-bottom: 0.8rem !important;
    box-shadow: var(--shadow-sm) !important;
}

/* User Message variant */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #f0f7ff 0%, #e0effe 100%) !important;
    border: 1.5px solid #bfdbfe !important;
}

/* Message Text formatting */
[data-testid="stChatMessage"] *,
[data-testid="stChatMessageContent"],
[data-testid="stChatMessageContent"] * {
    color: #0f172a !important; /* STRICT DARK TEXT */
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    line-height: 1.65 !important;
}
[data-testid="stChatMessageContent"] strong {
    font-weight: 700 !important;
    color: #0a2472 !important;
}

/* Chat Header Widget */
.chat-header-card {
    display: flex; justify-content: space-between; align-items: center;
    background: #ffffff; border: 1.5px solid var(--border);
    border-radius: var(--radius-md); padding: 0.8rem 1.1rem;
    margin-bottom: 0.9rem; box-shadow: var(--shadow-xs);
}
.chat-title-group { display: flex; align-items: center; gap: 10px; }
.chat-bot-avatar {
    width: 36px; height: 36px; border-radius: 10px;
    background: linear-gradient(135deg, var(--blue-700), var(--blue-500));
    color: #ffffff; display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
}
.chat-name { font-size: 0.88rem; font-weight: 700; color: var(--text-dark); }
.chat-subtext { font-size: 0.72rem; color: var(--text-light); }
.chat-status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--green-light); border: 1px solid var(--green-border);
    color: var(--green); font-size: 0.65rem; font-weight: 700;
    padding: 3px 9px; border-radius: 99px; text-transform: uppercase;
}

/* Chat Empty State */
.chat-empty-card {
    text-align: center; padding: 2rem 1.5rem;
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    border: 1.5px dashed var(--border-mid); border-radius: var(--radius-lg);
    margin-bottom: 1rem;
}
.chat-empty-icon { font-size: 2.2rem; margin-bottom: 0.5rem; }
.chat-empty-title { font-size: 1rem; font-weight: 700; color: var(--text-dark); margin-bottom: 0.3rem; }
.chat-empty-desc { font-size: 0.82rem; color: var(--text-light); max-width: 380px; margin: 0 auto; line-height: 1.5; }

/* ── Result Cards ── */
.result-card {
    background: var(--bg-white); border-radius: var(--radius-md);
    padding: 1.25rem; border: 1.5px solid var(--border);
    box-shadow: var(--shadow-sm); position: relative; overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s; margin-bottom: 0.85rem;
}
.result-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.result-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px; }
.result-card.green  { border-color: var(--green-border);  background: linear-gradient(160deg, var(--green-light)  0%, #fff 50%); }
.result-card.yellow { border-color: var(--yellow-border); background: linear-gradient(160deg, var(--yellow-light) 0%, #fff 50%); }
.result-card.red    { border-color: var(--red-border);    background: linear-gradient(160deg, var(--red-light)    0%, #fff 50%); }
.result-card.gray   { border-color: var(--border-mid);    background: linear-gradient(160deg, #f8fafc 0%, #fff 50%); }
.result-card.green::before  { background: linear-gradient(90deg, var(--green), #34d399); }
.result-card.yellow::before { background: linear-gradient(90deg, var(--yellow), #fbbf24); }
.result-card.red::before    { background: linear-gradient(90deg, var(--red), #f87171); }
.result-card.gray::before   { background: linear-gradient(90deg, #94a3b8, #cbd5e1); }

.rc-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem; gap: 0.5rem; }
.rc-name { font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted) !important; }
.rc-badge { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; padding: 2px 8px; border-radius: 99px; }
.badge-green  { background: var(--green-light);  color: var(--green)  !important; border: 1px solid var(--green-border); }
.badge-yellow { background: var(--yellow-light); color: var(--yellow) !important; border: 1px solid var(--yellow-border); }
.badge-red    { background: var(--red-light);    color: var(--red)    !important; border: 1px solid var(--red-border); }
.badge-gray   { background: #f1f5f9;              color: #475569       !important; border: 1px solid var(--border-mid); }
.rc-value { font-size: 1.8rem; font-weight: 800; font-family: 'JetBrains Mono', monospace !important; line-height: 1; margin-bottom: 2px; }
.rc-value.green  { color: var(--green)  !important; }
.rc-value.yellow { color: var(--yellow) !important; }
.rc-value.red    { color: var(--red)    !important; }
.rc-value.gray   { color: #475569       !important; }
.rc-unit  { font-size: 0.7rem; color: var(--text-light) !important; font-family: 'JetBrains Mono', monospace !important; margin-bottom: 0.5rem; }
.rc-range { font-size: 0.72rem; color: var(--text-muted) !important; margin-bottom: 0.6rem; }
.rc-bar-track { height: 5px; background: rgba(15, 23, 42, 0.07); border-radius: 99px; overflow: hidden; margin-bottom: 0.7rem; }
.rc-bar-fill  { height: 100%; border-radius: 99px; }
.rc-bar-fill.green  { background: linear-gradient(90deg, var(--green), #34d399); }
.rc-bar-fill.yellow { background: linear-gradient(90deg, var(--yellow), #fbbf24); }
.rc-bar-fill.red    { background: linear-gradient(90deg, var(--red), #f87171); }
.rc-bar-fill.gray   { background: linear-gradient(90deg, #94a3b8, #cbd5e1); }
.rc-explanation { font-size: 0.82rem; color: var(--text-dark) !important; line-height: 1.6; border-top: 1px solid rgba(15, 23, 42, 0.06); padding-top: 0.65rem; }

/* Stat Chips */
.stat-chip { display: block; width: 100%; padding: 0.9rem 0.5rem; border-radius: var(--radius-md); text-align: center; border: 1.5px solid; background: var(--bg-white); box-shadow: var(--shadow-xs); margin-bottom: 0.5rem; }
.stat-chip.green  { border-color: var(--green-border); }
.stat-chip.yellow { border-color: var(--yellow-border); }
.stat-chip.red    { border-color: var(--red-border); }
.stat-chip.gray   { border-color: var(--border-mid); }
.stat-chip-num { display: block; font-size: 1.7rem; font-weight: 800; font-family: 'JetBrains Mono', monospace !important; line-height: 1; margin-bottom: 3px; }
.stat-chip.green  .stat-chip-num { color: var(--green)  !important; }
.stat-chip.yellow .stat-chip-num { color: var(--yellow) !important; }
.stat-chip.red    .stat-chip-num { color: var(--red)    !important; }
.stat-chip.gray   .stat-chip-num { color: #64748b       !important; }
.stat-chip-lbl { font-size: 0.65rem; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }


/* Summary & Next Steps */
.summary-panel { background: #ffffff; border: 1.5px solid var(--blue-200); border-radius: var(--radius-lg); padding: 1.5rem; margin-top: 1.2rem; box-shadow: var(--shadow-sm); }
.summary-title { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: var(--blue-700) !important; margin-bottom: 0.7rem; }
.summary-text  { font-size: 0.92rem; color: var(--text-dark) !important; line-height: 1.8; }

.next-step-item { display: flex; align-items: flex-start; gap: 0.8rem; padding: 0.9rem 1rem; background: var(--bg-white); border-radius: var(--radius-md); border: 1.5px solid var(--border); margin-bottom: 0.6rem; box-shadow: var(--shadow-xs); }
.step-tag { font-size: 0.62rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; padding: 2px 8px; border-radius: 99px; margin-bottom: 3px; display: inline-block; }
.tag-monitor { background: var(--green-light);  color: var(--green)  !important; border: 1px solid var(--green-border); }
.tag-consult { background: var(--yellow-light); color: var(--yellow) !important; border: 1px solid var(--yellow-border); }
.tag-urgent  { background: var(--red-light);    color: var(--red)    !important; border: 1px solid var(--red-border); }
.step-text   { font-size: 0.85rem; color: var(--text-dark) !important; line-height: 1.55; }

/* Disclaimer */
.disclaimer { background: #fffbeb; border: 1.5px solid #fde68a; border-radius: var(--radius-md); padding: 1rem 1.3rem; margin-top: 1.4rem; display: flex; align-items: flex-start; gap: 0.8rem; }
.disclaimer-text { font-size: 0.8rem; color: #92400e !important; line-height: 1.6; }

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
.animate-in { animation: fadeUp 0.35s ease forwards; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper animate-in">
    <div class="hero-left">
        <div class="hero-badge">
            <span class="badge-dot"></span>
            OpenAI GPT-4o-mini · Vision & Clinical NER
        </div>
        <h1 class="hero-title">Diagno<span>va</span></h1>
        <p class="hero-subtitle">
            Upload your laboratory report or image to receive clear, structured insights — 
            powered by state-of-the-art clinical intelligence.
        </p>
    </div>
    <div class="hero-stats">
        <div class="hero-stat-box">
            <span class="hero-stat-num">50+</span>
            <span class="hero-stat-lbl">Parameters</span>
        </div>
        <div class="hero-stat-box">
            <span class="hero-stat-num">3</span>
            <span class="hero-stat-lbl">Risk Tiers</span>
        </div>
        <div class="hero-stat-box">
            <span class="hero-stat-num">AI</span>
            <span class="hero-stat-lbl">Vision OCR</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Info Expander ─────────────────────────────────────────────────────────────
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
    <span style="font-size:1.1rem;flex-shrink:0;">⚕️</span>
    <span class="disclaimer-text">
        <strong>Medical Disclaimer:</strong> Diagnova is an educational intelligence tool designed to assist patients in 
        understanding clinical lab values. It does not replace professional medical diagnosis, treatment, or advice. 
        Always consult a qualified healthcare provider regarding your laboratory results.
    </span>
</div>
""", unsafe_allow_html=True)
