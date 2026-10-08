# utils/analyzer.py

from utils.reference_ranges import get_reference_range, get_critical_limits
from utils.knowledge_base import MEDICAL_KNOWLEDGE
import streamlit as st
from groq import Groq
import json

def get_explanation_rag(test_name: str, value: float, status: str, ref_range_str: str):
    """
    FEATURE 1: Grounded Clinical Intelligence Engine
    Generates a patient-friendly explanation grounded in clinical context.
    """
    kb_entry = MEDICAL_KNOWLEDGE.get(test_name.lower().replace(" ", "_"), {})
    definition = kb_entry.get("definition", "No specific definition available.")
    
    prompt = f"""
    You are a helpful medical assistant focusing on lab report explanations.
    
    Test: {test_name}
    Value: {value}
    Status: {status}
    Reference Range: {ref_range_str}
    Medical Definition: {definition}
    
    Instruction:
    1. Generate a grounded, simple, one-sentence explanation for this result.
    2. Use the provided medical definition.
    3. NO diagnosis. NO medication advice.
    4. MUST end with: "Please consult your physician for clinical interpretation."
    5. Be encouraging but medically safe.
    """
    
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return f"Your {test_name} is {status} ({ref_range_str}). {definition} Please consult your physician for clinical interpretation."
            
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except:
        return f"Your {test_name} is {status} ({ref_range_str}). {definition} Please consult your physician for clinical interpretation."

def detect_clinical_patterns(data: dict):
    """
    FEATURE 2: Multi-Parameter Clinical Pattern Detection
    - Grounded Clinical Intelligence Engine: Explain parameters using a clinical corpus.
    Rule-based reasoning for combined results.
    """
    patterns = []
    
    # 1. Anemia Pattern: Low Hb + Low MCV
    hb = data.get("Hemoglobin") or data.get("Hb")
    mcv = data.get("MCV")
    if hb and mcv and hb < 12 and mcv < 80:
        patterns.append({
            "title": "Possible Iron Deficiency Pattern",
            "evidence": f"Low Hemoglobin ({hb}) and Low MCV ({mcv})",
            "insight": "This combination often suggests iron deficiency anemia, though other causes are possible.",
            "severity": "medium"
        })
    elif hb and hb < 12:
         patterns.append({
            "title": "Low Hemoglobin Detected",
            "evidence": f"Hb ({hb}) is below normal range",
            "insight": "Anemia involves lower-than-normal red blood cell levels or oxygen-carrying capacity.",
            "severity": "medium"
        })

    # 2. Infection Pattern: High WBC
    wbc = data.get("WBC Count") or data.get("WBC") or data.get("White Blood Cells")
    if wbc and wbc > 11000:
        patterns.append({
            "title": "Elevated White Blood Cell Count",
            "evidence": f"WBC count ({wbc}) is high",
            "insight": "This may indicate the body's response to infection, inflammation, or stress.",
            "severity": "medium"
        })
        
    # 3. Kidney Function: High Creatinine + High Urea
    creatinine = data.get("Creatinine")
    urea = data.get("Urea") or data.get("BUN")
    if creatinine and creatinine > 1.3:
        severity = "high" if creatinine > 2.0 else "medium"
        patterns.append({
            "title": "Kidney Function Insight",
            "evidence": f"Creatinine ({creatinine}) is above the normal range",
            "insight": "Elevated creatinine levels can reflect how well your kidneys are filtering waste.",
            "severity": severity
        })

    return patterns

def assess_risk(test_name: str, value: float, unit: str = None, 
                gender: str = "default", age_group: str = "adult"):
    """
    Inner function for individual parameter assessment.
    """
    ref_range = get_reference_range(test_name, gender, age_group)
    if not ref_range:
        return {
            "status": "yellow",
            "range": "Reference range not available",
            "message": f"Unable to find reference range for {test_name}",
            "bar_pct": 50
        }
    
    min_val = ref_range.get("min", 0)
    max_val = ref_range.get("max", 100)
    critical = get_critical_limits(test_name)
    
    status = "green"
    if value < min_val:
        deviation = ((min_val - value) / min_val) * 100
        status = "red" if deviation > 10 else "yellow"
    elif value > max_val:
        deviation = ((value - max_val) / max_val) * 100
        status = "red" if deviation > 10 else "yellow"

    if critical:
        if value < critical.get("low", -float('inf')) or value > critical.get("high", float('inf')):
            status = "red"

    # Bar percentage calculation
    if value < min_val:
        bar_pct = max(10, (value / min_val) * 30)
    elif value > max_val:
        ratio = value / max_val
        bar_pct = min(90, 70 + (ratio * 15))
    else:
        bar_pct = 30 + ((value - min_val) / (max_val - min_val) * 40)

    range_str = f"{min_val} – {max_val} {unit if unit else ''}".strip()
    
    # Feature 1: Get RAG explanation
    explanation = get_explanation_rag(test_name, value, status, range_str)

    return {
        "status": status,
        "range": range_str,
        "message": explanation,
        "bar_pct": int(bar_pct)
    }

def generate_health_coach_plan(results: list, patterns: list, profile: dict):
    """
    FEATURE 3: Personalized Health Coach
    Generates a lifestyle plan based on profile and results.
    """
    if not profile:
        profile = {"age": 30, "activity": "Moderate", "goal": "General Wellness"}
        
    abnormal_tests = [r["name"] for r in results if r["status"] == "red"]
    
    prompt = f"""
    You are a Certified Health Coach. Generate a personalized wellness plan.
    
    User Profile:
    - Age: {profile.get('age')}
    - Activity Level: {profile.get('activity')}
    - Health Goal: {profile.get('goal')}
    
    Lab Concerns:
    - Abnormal Values: {", ".join(abnormal_tests) if abnormal_tests else "None"}
    - Patterns: {", ".join([p['title'] for p in patterns])}
    
    Structure your response in Markdown with these sections:
    1. **🎯 Actionable Steps**: 2-3 specific lifestyle changes.
    2. **🥗 Nutrition Strategy**: Focused on the abnormal values or gaps.
    3. **💪 Activity Plan**: Tailored to their current level and goals.
    
    Rules:
    - Be optimistic and practical.
    - NO diagnosis. NO prescriptions.
    - Mention: "Consult your doctor before starting a new exercise or diet regimen."
    """
    
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return "Fill out your profile to receive a personalized health plan."
            
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except:
        return "Unable to generate health plan. Please consult your physician."

def generate_summary_ai(results: list, patterns: list, language: str = "English"):
    """
    FEATURE 3: AI-Generated Patient Summary
    Uses structured data to generate a cohesive summary.
    """
    abnormal_count = len([r for r in results if r["status"] == "red"])
    borderline_count = len([r for r in results if r["status"] == "yellow"])
    
    prompt = f"""
    You are a clinical summary assistant. Generate a patient-friendly summary in {language}.
    
    Metrics:
    - Abnormal: {abnormal_count}
    - Borderline: {borderline_count}
    - Total Parameters: {len(results)}
    
    Detected Patterns:
    {json.dumps(patterns, indent=2)}
    
    Rules:
    - BE CLEAR and patient-friendly.
    - DO NOT diagnose. Use words like "suggests", "may indicate", "consider discussing".
    - DO NOT prescribe.
    - RECOMMEND next steps (monitoring, consulting physician).
    - Provide the response in {language}.
    - Keep it under 100 words.
    """
    
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return "Unable to generate AI summary at this time. Please review individual results and consult your doctor."
            
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except:
        return "An error occurred generating summary. Please consult your physician for interpretation."

def calculate_confidence_score(extraction_metadata: dict, results_count: int):
    """
    FEATURE 4: Confidence Score
    """
    method = extraction_metadata.get("extraction_method", "failed")
    if method == "llm" and results_count > 3:
        return "High"
    if method == "regex" or results_count > 0:
        return "Medium"
    return "Low"

def process_lab_results(extraction_package: dict, patient_context: dict = None):
    """
    Main entry point for analysis.
    """
    data = extraction_package.get("data", {})
    metadata = extraction_package.get("metadata", {})
    user_profile = st.session_state.get("user_profile", {})
    
    if patient_context is None:
        patient_context = {"gender": "default", "age_group": "adult"}
    
    results = []
    for test_name, value in data.items():
        risk_info = assess_risk(test_name, value, "", 
                               patient_context.get("gender", "default"),
                               patient_context.get("age_group", "adult"))
        
        results.append({
            "name": test_name.title().replace("_", " "),
            "value": value,
            "unit": "",
            "reference": risk_info["range"],
            "status": risk_info["status"],
            "bar_pct": risk_info["bar_pct"],
            "explanation": risk_info["message"]
        })
    
    # Feature 2: Patterns
    patterns = detect_clinical_patterns(data)
    
    # Feature 3: Summary
    language = user_profile.get("language", "English")
    ai_summary = generate_summary_ai(results, patterns, language)
    
    # Feature 4: Confidence
    confidence = calculate_confidence_score(metadata, len(results))
    
    # Phase 2 - Feature 3: Health Coach
    health_plan = generate_health_coach_plan(results, patterns, user_profile)
    
    return {
        "results": results,
        "patterns": patterns,
        "summary": ai_summary,
        "confidence": confidence,
        "health_plan": health_plan
    }
