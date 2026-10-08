import streamlit as st


def render_upload_section():

    st.markdown('<div class="section-label">📂 Input Report</div>', unsafe_allow_html=True)

    input_mode = st.radio(
        "Input method",
        ["📄 Upload File", "✏️ Paste Text"],
        horizontal=True,
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if input_mode == "📄 Upload File":
        st.markdown("""
        <p style="font-size:0.78rem;color:var(--text-muted);margin-bottom:0.5rem;">
            Supported:&nbsp;
            <code style="background:var(--blue-50);color:var(--blue-700);padding:1px 7px;
                border-radius:4px;border:1px solid var(--border);font-size:0.72rem;">PDF</code>&nbsp;
            <code style="background:var(--blue-50);color:var(--blue-700);padding:1px 7px;
                border-radius:4px;border:1px solid var(--border);font-size:0.72rem;">PNG</code>&nbsp;
            <code style="background:var(--blue-50);color:var(--blue-700);padding:1px 7px;
                border-radius:4px;border:1px solid var(--border);font-size:0.72rem;">JPG</code>
        </p>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "lab_report",
            type=["pdf", "png", "jpg", "jpeg"],
            label_visibility="collapsed",
        )

        if uploaded_file:
            st.session_state["uploaded_file"] = uploaded_file
            st.session_state["input_ready"]   = True
            # Clear pasted text when file is uploaded
            st.session_state["pasted_text"] = ""
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin-top:0.7rem;
                        background:var(--green-light);border:1.5px solid var(--green-border);
                        border-radius:var(--radius-md);padding:0.65rem 0.9rem;">
                <span>✅</span>
                <span style="font-size:0.82rem;color:var(--green);font-weight:600;word-break:break-all;">
                    {uploaded_file.name} — ready to analyze
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.session_state["input_ready"] = False
            st.session_state["uploaded_file"] = None

    else:
        pasted_text = st.text_area(
            "Paste lab report text",
            height=190,
            placeholder=(
                "Paste your lab values here, e.g.\n\n"
                "Hemoglobin: 11.2 g/dL\n"
                "WBC Count: 9,800 /μL\n"
                "Fasting Glucose: 108 mg/dL"
            ),
            label_visibility="collapsed",
        )
        if pasted_text.strip():
            st.session_state["pasted_text"] = pasted_text
            st.session_state["input_ready"] = True
            # Clear uploaded file when text is pasted
            st.session_state["uploaded_file"] = None
        else:
            st.session_state["input_ready"] = False

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    st.markdown('<div class="section-label">🔬 Report Type</div>', unsafe_allow_html=True)

    report_type = st.selectbox(
        "Report type",
        [
            "🩸 Complete Blood Count (CBC)",
            "🧪 Comprehensive Metabolic Panel",
            "💛 Liver Function Test (LFT)",
            "🫘 Kidney Function Test (KFT)",
            "🍬 Diabetes Panel (HbA1c / Glucose)",
            "🦋 Thyroid Function Test (TFT)",
            "💊 Lipid Profile",
            "🔎 Urinalysis",
            "📋 General / Mixed Report",
        ],
        label_visibility="collapsed",
    )
    st.session_state["report_type"] = report_type

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Action Buttons ────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("🔍 Analyze Report", use_container_width=True):
            if st.session_state.get("input_ready"):
                st.session_state["analyze_clicked"] = True
                st.session_state["show_results"]    = True
                st.session_state["show_warning"]    = False
            else:
                st.session_state["show_warning"] = True

    with col2:
        if st.button("✨ Try Sample Report", use_container_width=True):
            st.session_state["sample_clicked"] = True
            st.session_state["show_results"]   = True
            st.session_state["analyze_clicked"] = False
            st.session_state["show_warning"]    = False

    # ── Custom styled warning — never white text ───────────────────────────────
    if st.session_state.get("show_warning"):
        st.markdown("""
        <div style="display:flex;align-items:flex-start;gap:0.7rem;margin-top:0.8rem;
                    background:#fff8e1;border:1.5px solid #f5c878;
                    border-radius:var(--radius-md);padding:0.8rem 1rem;">
            <span style="font-size:1rem;flex-shrink:0;">⚠️</span>
            <span style="font-size:0.84rem;color:#7a5c00;font-weight:500;line-height:1.5;">
                Please upload a file or paste report text first before analyzing.
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:1rem 1.1rem;background:var(--blue-50);
                border:1px solid var(--border);border-radius:var(--radius-md);">
        <p style="font-size:0.67rem;font-weight:700;letter-spacing:0.1em;
                  text-transform:uppercase;color:var(--blue-700);margin:0 0 0.6rem 0;">
            💡 Tips for best results
        </p>
        <ul style="margin:0;padding-left:1rem;">
            <li style="font-size:0.78rem;color:var(--text-body);margin-bottom:0.3rem;line-height:1.5;">
                Ensure the report is clear and legible
            </li>
            <li style="font-size:0.78rem;color:var(--text-body);margin-bottom:0.3rem;line-height:1.5;">
                Select the correct report type above
            </li>
            <li style="font-size:0.78rem;color:var(--text-body);line-height:1.5;">
                PDF format gives the most accurate extraction
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
