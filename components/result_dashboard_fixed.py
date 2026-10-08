# components/result_dashboard.py - FIXED VERSION

import streamlit as st
import time
import fitz  # PyMuPDF
from PIL import Image
import io
from utils.extractor import process_lab_report
from utils.analyzer import process_lab_results


def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text = ""
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text += page.get_text()
        
        pdf_document.close()
        return text.strip()
    except Exception as e:
        print(f"❌ PDF extraction failed: {str(e)}")
        return ""


def extract_text_from_image(uploaded_file):
    """Extract text from uploaded image file using OCR."""
    st.warning("⚠️ Image OCR not yet implemented. Please use PDF or paste text.")
    return ""


def _status_label(status: str) -> str:
    return {"green": "Normal", "yellow": "Borderline", "red": "Abnormal"}.get(status, "")


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


def render_result_dashboard():
    show      = st.session_state.get("show_results",    False)
    analyzing = st.session_state.get("analyze_clicked", False)

    # Placeholder - shown when no analysis has been run
    if not show:
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    min-height:380px;border:2px dashed var(--border-mid);border-radius:var(--radius-xl);
                    background:var(--bg-white);text-align:center;padding:2.5rem 1.5rem;
                    box-shadow:var(--shadow-sm);">
            <div style="font-size:3rem;margin-bottom:1.2rem;opacity:0.3;">🧪</div>
            <p style="color:var(--text-muted);font-size:0.92rem;max-width:280px;line-height:1.7;margin:0;">
                Your interpreted results will appear here after analysis.<br/><br/>
                Upload a report or paste text, then click
                <strong style="color:var(--blue-700);">Analyze Report</strong>.
            </p>
            <div style="display:flex;gap:0.7rem;margin-top:1.5rem;">
                <div style="width:9px;height:9px;border-radius:50%;background:var(--green);opacity:0.5;"></div>
                <div style="width:9px;height:9px;border-radius:50%;background:var(--yellow);opacity:0.5;"></div>
                <div style="width:9px;height:9px;border-radius:50%;background:var(--red);opacity:0.5;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Processing and Analysis
    if analyzing:
        with st.spinner("Extracting values · Analyzing patterns · Generating insights..."):
            text = ""
            
            # Check for uploaded file first
            uploaded_file = st.session_state.get("uploaded_file", None)
            if uploaded_file is not None:
                file_type = uploaded_file.type
                print(f"📁 Processing uploaded file: {uploaded_file.name} (type: {file_type})")
                
                if file_type == "application/pdf":
                    text = extract_text_from_pdf(uploaded_file)
                    if text:
                        print(f"✅ Extracted {len(text)} characters from PDF")
                    else:
                        st.error("❌ Could not extract text from PDF. Please try pasting text instead.")
                elif file_type in ["image/png", "image/jpeg", "image/jpg"]:
                    text = extract_text_from_image(uploaded_file)
                else:
                    st.error(f"❌ Unsupported file type: {file_type}")
            
            # Fall back to pasted text if no file or extraction failed
            if not text:
                text = st.session_state.get("pasted_text", "")
                if text:
                    print(f"📝 Using pasted text ({len(text)} characters)")
            
            if text:
                try:
                    print(f"\n{'='*60}\nPROCESSING LAB REPORT\n{'='*60}")
                    
                    # Step 1: Extract lab values from text using LLM/regex
                    extracted_data = process_lab_report(text)
                    
                    print(f"\n{'='*60}\nEXTRACTION COMPLETE\n{'='*60}")
                    print(f"Extracted {len(extracted_data)} values")
                    
                    # Step 2: Process with risk analyzer (returns complete analysis)
                    if extracted_data:
                        analysis = process_lab_results(extracted_data)
                        
                        # Store complete analysis in session state
                        st.session_state["analysis_results"] = analysis["results"]
                        st.session_state["analysis_summary"] = analysis["summary"]
                        st.session_state["analysis_next_steps"] = analysis["next_steps"]
                        st.session_state["analysis_patterns"] = analysis["patterns"]
                        st.session_state["analysis_counts"] = analysis["counts"]
                        
                        print(f"✅ Analysis complete: {len(analysis['results'])} results")
                    else:
                        st.warning("⚠️ No lab values could be extracted. Please try:\n\n"
                                 "• Using simple format: `Test Name: Value`\n"
                                 "• Example: `Hemoglobin: 11.2`\n"
                                 "• Ensure text is readable and contains lab values")
                        st.session_state["analysis_results"] = []
                        st.session_state["analysis_summary"] = "No values were extracted for analysis."
                        st.session_state["analysis_next_steps"] = []
                        
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    import traceback
                    print(f"\n{'='*60}\nERROR TRACEBACK\n{'='*60}")
                    traceback.print_exc()
                    st.session_state["analysis_results"] = []
                    st.session_state["analysis_summary"] = "Analysis failed due to an error."
                    st.session_state["analysis_next_steps"] = []
            else:
                st.warning("⚠️ No text found to analyze. Please paste lab report text or upload a PDF file.")
                st.session_state["analysis_results"] = []
                st.session_state["analysis_summary"] = "No input provided."
                st.session_state["analysis_next_steps"] = []
        
        st.session_state["analyze_clicked"] = False

    # Retrieve analysis results from session state
    results = st.session_state.get("analysis_results", [])
    summary = st.session_state.get("analysis_summary", "")
    next_steps = st.session_state.get("analysis_next_steps", [])
    counts = st.session_state.get("analysis_counts", {"green": 0, "yellow": 0, "red": 0})
    
    # If no results at all, show helpful message
    if not results:
        st.warning("⚠️ No analysis results available. Please upload or paste a lab report and click Analyze.")
        return

    # Display Results
    st.markdown('<div class="section-label">📊 Analysis Results</div>', unsafe_allow_html=True)

    # Stats
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-chip green">
            <span class="stat-chip-num">{counts['green']}</span>
            <span class="stat-chip-lbl">✅ Normal</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-chip yellow">
            <span class="stat-chip-num">{counts['yellow']}</span>
            <span class="stat-chip-lbl">⚠️ Borderline</span>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-chip red">
            <span class="stat-chip-num">{counts['red']}</span>
            <span class="stat-chip-lbl">🚨 Abnormal</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # Tabs for filtering by status
    tabs = st.tabs(["🔬 All", "🚨 Abnormal", "⚠️ Borderline", "✅ Normal"])
    with tabs[0]: _render_cards(results)
    with tabs[1]: _render_cards([r for r in results if r["status"] == "red"])
    with tabs[2]: _render_cards([r for r in results if r["status"] == "yellow"])
    with tabs[3]: _render_cards([r for r in results if r["status"] == "green"])

    # AI-Generated Summary
    if summary:
        st.markdown(f"""
        <div class="summary-panel">
            <div class="summary-title">🤖 AI Analysis Summary</div>
            <div class="summary-text">{summary}</div>
        </div>
        """, unsafe_allow_html=True)

    # Personalized Next Steps
    if next_steps:
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">📋 Recommended Next Steps</div>', unsafe_allow_html=True)

        for step in next_steps:
            st.markdown(f"""
            <div class="next-step-item">
                <span style="font-size:1rem;flex-shrink:0;margin-top:2px;">{step['icon']}</span>
                <div>
                    <span class="step-tag tag-{step['tag']}">{step['tag'].upper()}</span>
                    <div class="step-text">{step['text']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Download Report
    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    if summary and next_steps:
        download_content = (
            "=== DIAGNOVA LAB REPORT ANALYSIS ===\n\n"
            f"{summary}\n\n"
            "=== RECOMMENDED NEXT STEPS ===\n"
            + "\n".join(f"[{s['tag'].upper()}] {s['text']}" for s in next_steps)
            + "\n\n=== DISCLAIMER ===\n"
            "This analysis is for educational purposes only and does not replace professional medical advice."
        )
        
        st.download_button(
            label="⬇️ Download Report Summary",
            data=download_content,
            file_name="diagnova_analysis.txt",
            mime="text/plain",
            use_container_width=True,
        )
