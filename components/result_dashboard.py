import streamlit as st
import time
import fitz  # PyMuPDF
from PIL import Image
import io
from utils.extractor import process_lab_report, extract_text_from_image
from utils.analyzer import process_lab_results
from utils.chat_handler import get_chat_response

# ── Sample Data for Demo ──────────────────────────────────────────────────────
SAMPLE_ANALYSIS = {
    "results": [
        {
            "name": "Hemoglobin",
            "value": 11.2,
            "unit": "g/dL",
            "reference": "13.5 – 17.5",
            "status": "red",
            "bar_pct": 55,
            "explanation": "Your hemoglobin is below the normal range, suggesting anemia. This can cause fatigue and weakness. Please consult your physician for clinical interpretation.",
        },
        {
            "name": "MCV",
            "value": 78,
            "unit": "fL",
            "reference": "80 – 100",
            "status": "red",
            "bar_pct": 30,
            "explanation": "MCV is slightly low, meaning red blood cells are smaller than average. Please consult your physician for clinical interpretation.",
        },
        {
            "name": "WBC Count",
            "value": 9800,
            "unit": "/μL",
            "reference": "4,500 – 11,000",
            "status": "green",
            "bar_pct": 65,
            "explanation": "Your WBC Count is within the normal range. Please consult your physician for clinical interpretation.",
        }
    ],
    "patterns": [
        {
            "title": "Possible Iron Deficiency Pattern",
            "evidence": "Low Hemoglobin (11.2) and Low MCV (78)",
            "insight": "This combination often suggests iron deficiency anemia, though other causes are possible.",
            "severity": "medium"
        }
    ],
    "summary": "Your results show mild microcytic anemia with low hemoglobin and MCV. Other parameters like WBC count are normal. Consider discussing these results with a doctor.",
    "confidence": "High",
    "health_plan": """
### 🎯 Actionable Steps
1. **Increase Iron Intake**: Focus on heme-iron sources and iron-fortified foods.
2. **Optimize Absorption**: Pair iron-rich foods with Vitamin C (e.g., orange juice, peppers).
3. **Monitor Fatigue**: Keep a log of energy levels to share with your physician.

### 🥗 Nutrition Strategy
- **Rich Sources**: Lean red meat, lentils, spinach, and pumpkin seeds.
- **Avoid Inhibitors**: Do not drink tea or coffee during meals, as they can block iron absorption.

### 💪 Activity Plan
- **Light Cardio**: Stick to walking or gentle cycling. Avoid high-intensity training until hemoglobin levels stabilize.
- **Consistency**: 20-30 minutes of moderate movement, 3-4 days a week.

*Consult your doctor before starting a new exercise or diet regimen.*
"""
}


def _status_label(status: str) -> str:
    return {"green": "Normal", "yellow": "Borderline", "red": "Abnormal", "gray": "Not Evaluated"}.get(status, "Not Evaluated")


def _render_single_card(r: dict):
    s   = r.get("status", "green")
    lbl = r.get("label") or _status_label(s)
    val = f"{r['value']:,}" if isinstance(r["value"], int) else str(r["value"])
    unit_str = r.get("unit", "")
    ref_str = r.get("reference", "Not Available")
    explanation = r.get("explanation", "")
    bar_pct = r.get("bar_pct", 50)

    st.markdown(f"""
    <div class="result-card {s}">
        <div class="rc-header">
            <span class="rc-name">{r['name']}</span>
            <span class="rc-badge badge-{s}">{lbl}</span>
        </div>
        <div class="rc-value {s}">{val}</div>
        <div class="rc-unit">{unit_str}</div>
        <div class="rc-range">Reference: {ref_str}</div>
        <div class="rc-bar-track">
            <div class="rc-bar-fill {s}" style="width:{bar_pct}%;"></div>
        </div>
        <div class="rc-explanation">{explanation}</div>
    </div>
    """, unsafe_allow_html=True)


def _render_chat_assistant(context: dict):
    """RENDER FEATURE 1: AI Chat Assistant with professional header, chips, and high-contrast messages"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "pending_chat_prompt" not in st.session_state:
        st.session_state.pending_chat_prompt = None

    # Header Card
    col_hdr, col_btn = st.columns([3, 1])
    with col_hdr:
        st.markdown("""
        <div class="chat-header-card">
            <div class="chat-title-group">
                <div class="chat-bot-avatar">🤖</div>
                <div>
                    <div class="chat-name">Diagnova Clinical Assistant</div>
                    <div class="chat-subtext">OpenAI GPT-4o-mini · Grounded in your lab report</div>
                </div>
            </div>
            <div class="chat-status-pill">
                <span>●</span> Online & Ready
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_btn:
        if st.session_state.chat_history:
            if st.button("🔄 Reset Chat", key="reset_chat_btn", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.pending_chat_prompt = None
                st.rerun()

    # Empty State with Suggested Questions
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="chat-empty-card">
            <div class="chat-empty-icon">🩺</div>
            <div class="chat-empty-title">Ask anything about your lab report</div>
            <div class="chat-empty-desc">
                Get clear, patient-friendly explanations for abnormal markers, reference ranges, and lifestyle advice.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size:0.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;'>💡 Suggested Questions</p>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button("🩸 What do my abnormal results mean?", key="chip_abnormal", use_container_width=True):
                st.session_state.pending_chat_prompt = "What do my abnormal and borderline results indicate, and should I be concerned?"
            if st.button("🥗 What diet changes are recommended?", key="chip_diet", use_container_width=True):
                st.session_state.pending_chat_prompt = "Based on my lab results, what dietary changes or nutritional foods should I focus on?"
        with col_c2:
            if st.button("👨‍⚕️ What should I ask my doctor?", key="chip_doctor", use_container_width=True):
                st.session_state.pending_chat_prompt = "What are the most important questions I should ask my physician about these results?"
            if st.button("🔍 Explain my overall health summary", key="chip_summary", use_container_width=True):
                st.session_state.pending_chat_prompt = "Can you give me a simple, reassuring breakdown of my lab report results?"

    # Display Chat History Container
    chat_container = st.container(height=380)
    with chat_container:
        for message in st.session_state.chat_history:
            role = message["role"]
            avatar = "👤" if role == "user" else "🧬"
            with st.chat_message(role, avatar=avatar):
                st.markdown(message["content"])

    # Handle Input from typing or from suggestion chips
    prompt_input = st.chat_input("Type your health question (e.g., 'What does my Hemoglobin mean?')...")
    active_prompt = prompt_input or st.session_state.get("pending_chat_prompt")

    if active_prompt:
        st.session_state.active_tab = "💬 Chat Assistant"
        st.session_state.pending_chat_prompt = None

        with chat_container:
            with st.chat_message("user", avatar="👤"):
                st.markdown(active_prompt)

        st.session_state.chat_history.append({"role": "user", "content": active_prompt})

        with chat_container:
            with st.chat_message("assistant", avatar="🧬"):
                with st.spinner("Analyzing your report context..."):
                    response = get_chat_response(st.session_state.chat_history, context)
                    st.markdown(response)

        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()


def _render_single_card(r: dict):
    s   = r["status"]
    lbl = _status_label(s)
    val = f"{r['value']:,}" if isinstance(r["value"], int) else str(r["value"])
    st.markdown(f"""
    <div class="result-card {s}">
        <div class="rc-header">
            <span class="rc-name">{r['name']}</span>
            <span class="rc-badge badge-{s}">{lbl}</span>
        </div>
        <div class="rc-value {s}">{val}</div>
        <div class="rc-unit">{r['unit']}</div>
        <div class="rc-range">Reference: {r['reference']}</div>
        <div class="rc-bar-track">
            <div class="rc-bar-fill {s}" style="width:{r['bar_pct']}%;"></div>
        </div>
        <div class="rc-explanation">{r['explanation']}</div>
    </div>
    """, unsafe_allow_html=True)


def _render_cards(results: list):
    if not results:
        st.markdown(
            "<p style='color:var(--text-light);font-size:0.83rem;padding:0.8rem 0;'>"
            "No parameters in this category.</p>",
            unsafe_allow_html=True,
        )
        return
    pairs = [results[i:i+2] for i in range(0, len(results), 2)]
    for pair in pairs:
        cols = st.columns(len(pair))
        for col, r in zip(cols, pair):
            with col:
                _render_single_card(r)


def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page_num in range(pdf_document.page_count):
            text += pdf_document[page_num].get_text()
        pdf_document.close()
        return text.strip()
    except:
        return ""




def render_result_dashboard():
    show      = st.session_state.get("show_results",    False)
    analyzing = st.session_state.get("analyze_clicked", False)
    sampling  = st.session_state.get("sample_clicked",  False)

    if not show:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    min-height:380px;border:2px dashed var(--border-mid);border-radius:var(--radius-xl);
                    background:var(--bg-white);text-align:center;padding:2.5rem 1.5rem;
                    box-shadow:var(--shadow-sm);">
            <div style="font-size:3rem;margin-bottom:1.2rem;opacity:0.3;">🧪</div>
            <p style="color:var(--text-muted);font-size:0.92rem;max-width:280px;line-height:1.7;margin:0;">
                Your interpreted results will appear here after analysis.<br/><br/>
                Upload a report or use
                <strong style="color:var(--blue-700);">Sample Report</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Handle Sample Data
    if sampling:
        st.session_state["full_analysis"] = SAMPLE_ANALYSIS
        st.session_state["sample_clicked"] = False
        st.success("✅ Loaded sample report for demonstration.")

    if analyzing:
        with st.spinner("Analyzing with Medical Intelligence..."):
            text = ""
            uploaded_file = st.session_state.get("uploaded_file", None)
            if uploaded_file:
                if uploaded_file.type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                else:
                    text = extract_text_from_image(uploaded_file)
            
            if not text:
                text = st.session_state.get("pasted_text", "")
            
            if text:
                try:
                    extraction_package = process_lab_report(text)
                    analysis_package = process_lab_results(extraction_package)
                    st.session_state["full_analysis"] = analysis_package
                    st.session_state["chat_history"] = []
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.session_state["full_analysis"] = None
            else:
                st.warning("⚠️ No text to analyze.")
        st.session_state["analyze_clicked"] = False

    analysis = st.session_state.get("full_analysis")
    
    # Language Change Trigger: If language changes in sidebar, re-run summary AI
    user_profile = st.session_state.get("user_profile", {})
    current_lang = user_profile.get("language", "English")
    last_lang = st.session_state.get("last_language", "English")

    if analysis and current_lang != last_lang:
        with st.spinner(f"Translating summary to {current_lang}..."):
            from utils.analyzer import generate_summary_ai
            new_summary = generate_summary_ai(analysis["results"], analysis["patterns"], current_lang)
            analysis["summary"] = new_summary
            st.session_state["full_analysis"] = analysis
            st.session_state["last_language"] = current_lang
    elif not analysis:
        st.session_state["last_language"] = current_lang

    if not analysis:
        st.info("No data available.")
        return

    results = analysis["results"]
    patterns = analysis["patterns"]
    summary = analysis["summary"]
    confidence = analysis["confidence"]

    counts = {"green": 0, "yellow": 0, "red": 0, "gray": 0}
    for r in results:
        st_val = r.get("status", "green")
        counts[st_val] = counts.get(st_val, 0) + 1

    # Header with toggle for Persistence
    conf_color = {"High": "#00a67e", "Medium": "#c97800", "Low": "#d93025"}.get(confidence, "#6b8dae")
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <div class="section-label" style="margin-bottom:0;">📊 Analysis Results</div>
        <div style="font-size:0.7rem;font-weight:700;color:{conf_color};
                    background:white;border:1px solid {conf_color};
                    padding:3px 10px;border-radius:100px;">
            CONFIDENCE: {confidence.upper()}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Persistent Tab Management
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "📋 Analysis"

    # Style the radio to look like tabs
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] div[data-testid="stVerticalBlock"] > div:has(div.stRadio) {
        margin-bottom: -1rem;
    }
    div.stRadio > div {
        background: white;
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid #d0e4f7;
    }
    </style>
    """, unsafe_allow_html=True)

    tab_options = ["📋 Analysis", "🥗 Health Plan", "💬 Chat Assistant"]
    active_index = tab_options.index(st.session_state.active_tab) if st.session_state.active_tab in tab_options else 0
    
    st.session_state.active_tab = st.radio(
        "Navigation",
        tab_options,
        index=active_index,
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    if st.session_state.active_tab == "📋 Analysis":
        # Stats Chips
        if counts["gray"] > 0:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="stat-chip green"><span class="stat-chip-num">{counts["green"]}</span><span class="stat-chip-lbl">✅ Normal</span></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="stat-chip yellow"><span class="stat-chip-num">{counts["yellow"]}</span><span class="stat-chip-lbl">⚠️ Borderline</span></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="stat-chip red"><span class="stat-chip-num">{counts["red"]}</span><span class="stat-chip-lbl">🚨 Abnormal</span></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="stat-chip gray"><span class="stat-chip-num">{counts["gray"]}</span><span class="stat-chip-lbl">⚪ Not Evaluated</span></div>', unsafe_allow_html=True)
        else:
            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="stat-chip green"><span class="stat-chip-num">{counts["green"]}</span><span class="stat-chip-lbl">✅ Normal</span></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="stat-chip yellow"><span class="stat-chip-num">{counts["yellow"]}</span><span class="stat-chip-lbl">⚠️ Borderline</span></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="stat-chip red"><span class="stat-chip-num">{counts["red"]}</span><span class="stat-chip-lbl">🚨 Abnormal</span></div>', unsafe_allow_html=True)

        if patterns:
            st.markdown('<div class="section-label" style="margin-top:1.5rem;">🔍 Clinical Patterns</div>', unsafe_allow_html=True)
            for p in patterns:
                bg = {"high": "#fdecea", "medium": "#fff4e0"}.get(p["severity"], "#eef6ff")
                st.markdown(f"""
                <div style="padding:1rem;background:{bg};border-radius:14px;margin-bottom:0.8rem;border:1px solid rgba(0,0,0,0.05);">
                    <div style="font-weight:700;font-size:0.9rem;color:#0a2472;">{p['title']}</div>
                    <div style="font-size:0.75rem;color:#6b8dae;margin-top:2px;">{p['evidence']}</div>
                    <div style="font-size:0.85rem;margin-top:8px;line-height:1.4;">{p['insight']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:1.5rem;">🔬 Parameter Breakdown</div>', unsafe_allow_html=True)
        _render_cards(results)

        st.markdown(f"""
        <div class="summary-panel" style="margin-top:2rem;">
            <div class="summary-title">🤖 AI Patient Summary</div>
            <div class="summary-text">{summary}</div>
        </div>
        """, unsafe_allow_html=True)

    elif st.session_state.active_tab == "🥗 Health Plan":
        st.markdown('<div class="section-label">🥗 Personalized Health Coach</div>', unsafe_allow_html=True)
        if "health_plan" in analysis:
            st.markdown(analysis["health_plan"])
        else:
            st.info("Complete analysis to see your plan.")

    elif st.session_state.active_tab == "💬 Chat Assistant":
        _render_chat_assistant(analysis)

    # Footer Actions
    st.markdown("<hr style='margin:2rem 0;opacity:0.1;'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown('<div class="section-label" style="margin:0;">📋 Next Steps</div>', unsafe_allow_html=True)
        next_steps = []
        has_critical = analysis.get("has_critical", False) or any(r.get("is_critical", False) for r in results)

        if has_critical:
            crit_names = [r["name"] for r in results if r.get("is_critical")]
            next_steps.append({
                "tag": "urgent",
                "icon": "🚨",
                "text": f"CRITICAL CLINICAL ALERT: One or more parameters ({', '.join(crit_names) if crit_names else 'critical tests'}) reached emergency clinical thresholds. Seek immediate physician consultation."
            })
        elif counts["red"] > 0:
            abnormal_names = [r["name"] for r in results if r.get("status") == "red"]
            next_steps.append({
                "tag": "consult",
                "icon": "⚠️",
                "text": f"Follow up with your healthcare provider to discuss out-of-range parameters ({', '.join(abnormal_names[:3])}{'...' if len(abnormal_names) > 3 else ''})."
            })

        if counts["yellow"] > 0:
            borderline_names = [r["name"] for r in results if r.get("status") == "yellow"]
            next_steps.append({
                "tag": "consult",
                "icon": "🔍",
                "text": f"Monitor borderline parameters ({', '.join(borderline_names[:3])}) during routine follow-up."
            })

        if not has_critical and counts["red"] == 0 and counts["yellow"] == 0:
            next_steps.append({
                "tag": "monitor",
                "icon": "✅",
                "text": "All evaluated parameters are within healthy normal reference ranges. Maintain your healthy lifestyle and routine wellness visits."
            })

        for step in next_steps:
            st.markdown(f"""<div class="next-step-item"><span>{step['icon']}</span><div style="margin-left:8px;"><span class="step-tag tag-{step['tag']}">{step['tag'].upper()}</span><div class="step-text" style="font-size:0.8rem;">{step['text']}</div></div></div>""", unsafe_allow_html=True)

    with col2:
        st.download_button(
            label="⬇️ Download Summary",
            data=f"DIAGNOVA REPORT SUMMARY\n\n{summary}\n\nCONFIDENCE: {confidence.upper()}",
            file_name="diagnova_summary.txt",
            mime="text/plain",
            use_container_width=True,
        )
