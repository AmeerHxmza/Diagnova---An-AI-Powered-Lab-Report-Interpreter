# utils/analyzer.py

"""
Deterministic Clinical Analysis and Laboratory Interpretation Engine.
Evaluates laboratory parameters using hierarchical reference ranges, unit-compatible scaling,
deterministic classification (Normal / Low / High / Unknown), and grounded clinical explanations.
"""

import json
from typing import Dict, List, Any, Optional

try:
    import streamlit as st
except ImportError:
    st = None

from utils.reference_ranges import (
    normalize_test_key,
    get_display_name,
    get_reference_range,
    get_critical_limits,
    parse_reference_range,
    align_value_and_range
)
from utils.knowledge_base import MEDICAL_KNOWLEDGE
from utils.openai_client import get_openai_client, OPENAI_MODEL


def get_explanation_rag(
    test_name: str,
    value: float,
    unit: str,
    status: str,
    label: str,
    ref_range_str: str
) -> str:
    """
    FEATURE 1: Grounded Clinical Intelligence Engine.
    Generates a patient-friendly explanation strictly grounded in the deterministic validated status.
    Fixes Bug 3: Ensures AI explanation NEVER contradicts deterministic classification.
    """
    canonical_key = normalize_test_key(test_name, unit, value)
    kb_entry = MEDICAL_KNOWLEDGE.get(canonical_key, {})
    definition = kb_entry.get("definition", "A standard clinical diagnostic biomarker.")

    # Safe deterministic fallback text if OpenAI call is unavailable or fails
    if status == "green":
        default_fallback = (
            f"Your {test_name} of {value} {unit} is within the normal reference range ({ref_range_str}). "
            f"{definition} Please consult your physician for clinical interpretation."
        )
    elif status == "yellow":
        default_fallback = (
            f"Your {test_name} of {value} {unit} is borderline compared to the standard reference range ({ref_range_str}). "
            f"{definition} Please consult your physician for clinical interpretation."
        )
    elif status == "red":
        default_fallback = (
            f"Your {test_name} of {value} {unit} is {label.lower()} relative to the reference range ({ref_range_str}). "
            f"{definition} Please consult your physician for clinical interpretation."
        )
    else:
        default_fallback = (
            f"Your {test_name} value is {value} {unit}. A specific reference range was not provided for this parameter. "
            f"{definition} Please consult your physician for clinical interpretation."
        )

    try:
        client = get_openai_client()
        if not client:
            return default_fallback

        prompt = f"""You are a clinical laboratory explanation assistant.
The deterministic laboratory classification engine has evaluated this result:
- Test: {test_name}
- Value: {value} {unit}
- Reference Range: {ref_range_str}
- Validated Status: {label} ({status.upper()})
- Medical Definition: {definition}

INSTRUCTIONS:
1. Provide a clear, patient-friendly one-sentence explanation for this result.
2. Ground your explanation in the provided medical definition.
3. You MUST strictly adhere to the Validated Status ({label}).
   - If the Validated Status is Normal, confirm that it is within the healthy reference range.
   - If Low or High, explain what that indicates without diagnosing.
   - If Not Evaluated / Unknown, state that reference values are not established.
4. DO NOT contradict the Validated Status ({label}) under any circumstance.
5. NO medical diagnosis. NO medication advice.
6. MUST end with: "Please consult your physician for clinical interpretation."
"""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=120
        )
        explanation = response.choices[0].message.content.strip()
        return explanation if explanation else default_fallback

    except Exception:
        return default_fallback


def assess_risk(
    test_name: str,
    value: float,
    unit: str = "",
    report_range_str: Optional[str] = None,
    gender: str = "default",
    age_group: str = "adult"
) -> Dict[str, Any]:
    """
    Deterministic parameter risk assessment engine.
    Pipeline:
      1. Canonical alias normalization
      2. Priority reference range resolution (Report printed range -> Clinical catalog -> Unknown)
      3. Unit and magnitude alignment (Thousands vs Absolute cells)
      4. Deterministic classification (Normal / Low / High / Unknown)
      5. Grounded RAG explanation
    """
    canonical_key = normalize_test_key(test_name, unit, value)
    standard_name = get_display_name(canonical_key)

    # ── Step 1: Reference Range Resolution ───────────────────
    # Priority 1: Laboratory's own printed reference range from report
    range_source = None
    raw_min: Optional[float] = None
    raw_max: Optional[float] = None
    resolved_unit = unit

    if report_range_str:
        parsed_rep = parse_reference_range(report_range_str)
        if parsed_rep:
            raw_min = parsed_rep["min"]
            raw_max = parsed_rep["max"]
            range_source = "report"

    # Priority 2: Verified clinical catalog
    if raw_min is None or raw_max is None:
        cat_info = get_reference_range(test_name, gender, age_group, unit, value)
        if cat_info:
            raw_min = cat_info["min"]
            raw_max = cat_info["max"]
            if not resolved_unit:
                resolved_unit = cat_info.get("unit", "")
            range_source = "catalog"

    # Fallback: Neither report range nor catalog range available (Bug 2 Fix)
    if raw_min is None or raw_max is None:
        display_range = "Not Evaluated"
        explanation = (
            f"Reference range for {standard_name} was not available from this laboratory or catalog. "
            "Please consult your physician for clinical interpretation."
        )
        return {
            "name": standard_name,
            "value": value,
            "unit": resolved_unit,
            "range": display_range,
            "status": "gray",
            "label": "Not Evaluated",
            "is_critical": False,
            "is_unknown": True,
            "bar_pct": 50,
            "message": explanation
        }

    # ── Step 2: Unit and Magnitude Alignment (Bug 1 Fix) ──────
    comp_val, comp_min, comp_max, eff_unit = align_value_and_range(
        value, resolved_unit, raw_min, raw_max, canonical_key
    )

    range_str = f"{comp_min:g} – {comp_max:g} {eff_unit}".strip()

    # ── Step 3: Deterministic Classification ─────────────────
    critical_limits = get_critical_limits(canonical_key, eff_unit, comp_val)
    is_critical = False
    status = "green"
    label = "Normal"

    # Check critical life-threatening limits first
    crit_low = critical_limits.get("low", -float("inf"))
    crit_high = critical_limits.get("high", float("inf"))

    if comp_val <= crit_low:
        status = "red"
        label = "Critically Low"
        is_critical = True
    elif comp_val >= crit_high:
        status = "red"
        label = "Critically High"
        is_critical = True
    elif comp_min <= comp_val <= comp_max:
        status = "green"
        label = "Normal"
    elif comp_val < comp_min:
        # Check borderline tolerance (within 10% below minimum)
        deviation = ((comp_min - comp_val) / max(0.001, comp_min)) * 100.0
        if deviation <= 10.0:
            status = "yellow"
            label = "Borderline Low"
        else:
            status = "red"
            label = "Low"
    else:  # comp_val > comp_max
        # Check borderline tolerance (within 10% above maximum)
        deviation = ((comp_val - comp_max) / max(0.001, comp_max)) * 100.0
        if deviation <= 10.0:
            status = "yellow"
            label = "Borderline High"
        else:
            status = "red"
            label = "High"

    # ── Step 4: Visual Bar Percentage ────────────────────────
    if status == "green":
        span = max(0.001, comp_max - comp_min)
        bar_pct = 35 + int(((comp_val - comp_min) / span) * 30)
        bar_pct = max(35, min(65, bar_pct))
    elif comp_val < comp_min:
        bar_pct = max(10, min(30, int((comp_val / max(0.001, comp_min)) * 30)))
    else:  # comp_val > comp_max
        excess = (comp_val - comp_max) / max(0.001, comp_max)
        bar_pct = max(70, min(95, 70 + int(excess * 25)))

    # ── Step 5: Grounded Explanation ─────────────────────────
    explanation = get_explanation_rag(
        standard_name, comp_val, eff_unit, status, label, range_str
    )

    return {
        "name": standard_name,
        "value": comp_val,
        "unit": eff_unit,
        "range": range_str,
        "status": status,
        "label": label,
        "is_critical": is_critical,
        "is_unknown": False,
        "bar_pct": bar_pct,
        "message": explanation
    }


def detect_clinical_patterns(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    FEATURE 2: Multi-Parameter Clinical Pattern Detection.
    Rule-based reasoning evaluating combinations of validated parameters.
    """
    patterns = []
    by_key = {}
    for r in results:
        k = normalize_test_key(r["name"], r.get("unit", ""), r.get("value"))
        by_key[k] = r

    # 1. Microcytic Anemia: Low Hemoglobin + Low MCV
    hb = by_key.get("hemoglobin")
    mcv = by_key.get("mcv")
    if hb and mcv:
        if hb["status"] == "red" and hb["label"] in ("Low", "Critically Low"):
            if mcv["status"] == "red" and mcv["label"] in ("Low", "Critically Low"):
                patterns.append({
                    "title": "Possible Microcytic Anemia Pattern",
                    "evidence": f"Low Hemoglobin ({hb['value']} {hb['unit']}) with Low MCV ({mcv['value']} {mcv['unit']})",
                    "insight": "This combination frequently suggests iron deficiency anemia or thalassemia trait. A ferritin and iron panel may be warranted.",
                    "severity": "medium"
                })
            elif mcv["status"] == "green":
                patterns.append({
                    "title": "Normocytic Anemia Pattern",
                    "evidence": f"Low Hemoglobin ({hb['value']} {hb['unit']}) with normal red cell volume (MCV: {mcv['value']})",
                    "insight": "Often observed in anemia of chronic disease, acute blood loss, or early nutrient deficiency.",
                    "severity": "medium"
                })

    # 2. Infection / Leukocytosis Pattern: High WBC
    wbc = by_key.get("wbc_count")
    if wbc and wbc["status"] == "red" and wbc["label"] in ("High", "Critically High"):
        patterns.append({
            "title": "Elevated White Blood Cell Count (Leukocytosis)",
            "evidence": f"WBC count ({wbc['value']} {wbc['unit']}) is elevated above normal reference range",
            "insight": "May indicate physiological response to bacterial infection, systemic inflammation, or acute physical stress.",
            "severity": "high" if wbc.get("is_critical") else "medium"
        })

    # 3. Thrombocytopenia Pattern: Low Platelets
    plt = by_key.get("platelets")
    if plt and plt["status"] == "red" and plt["label"] in ("Low", "Critically Low"):
        patterns.append({
            "title": "Low Platelet Count (Thrombocytopenia)",
            "evidence": f"Platelet count ({plt['value']} {plt['unit']}) is below reference range",
            "insight": "Reduced platelet count may be associated with viral illness, immune destruction, or medication effects.",
            "severity": "high" if plt.get("is_critical") else "medium"
        })

    # 4. Renal Function: High Creatinine and/or High Urea
    creat = by_key.get("creatinine")
    urea = by_key.get("urea") or by_key.get("bun")
    if creat and creat["status"] in ("red", "yellow") and creat["label"] != "Normal":
        patterns.append({
            "title": "Renal Function Insight",
            "evidence": f"Creatinine ({creat['value']} {creat['unit']}) is elevated",
            "insight": "Elevated serum creatinine reflects altered glomerular filtration rate. Adequate hydration and clinical follow-up are advised.",
            "severity": "high" if creat.get("is_critical") else "medium"
        })

    return patterns


def generate_summary_ai(
    results: List[Dict[str, Any]],
    patterns: List[Dict[str, Any]],
    language: str = "English"
) -> str:
    """
    FEATURE 3: AI-Generated Patient Summary.
    Uses strictly validated parameters to generate a reassuring, clinically aligned summary.
    """
    normal_count = sum(1 for r in results if r["status"] == "green")
    borderline_count = sum(1 for r in results if r["status"] == "yellow")
    abnormal_count = sum(1 for r in results if r["status"] == "red")
    unevaluated_count = sum(1 for r in results if r["status"] == "gray")
    total_count = len(results)

    # Perfect Normal Case: All reported parameters within range
    if normal_count == total_count and total_count > 0:
        return (
            f"All {total_count} evaluated laboratory parameters are within normal physiological reference ranges. "
            "No abnormalities or clinical patterns were identified. "
            "Continue maintaining a healthy lifestyle and attend routine wellness checkups."
        )

    try:
        client = get_openai_client()
        if not client:
            if abnormal_count == 0 and borderline_count == 0:
                return f"All {normal_count} parameters are within normal limits."
            return (
                f"Summary: {normal_count} normal, {borderline_count} borderline, and {abnormal_count} out-of-range "
                f"parameters were identified across {total_count} tests. Consult your physician for detailed interpretation."
            )

        abnormal_names = [f"{r['name']} ({r['label']})" for r in results if r["status"] in ("red", "yellow")]

        prompt = f"""You are a clinical laboratory summary assistant.
Generate a cohesive, patient-friendly laboratory summary in {language}.

Deterministic Metrics:
- Total Parameters: {total_count}
- Normal Parameters: {normal_count}
- Borderline Parameters: {borderline_count}
- Abnormal Parameters: {abnormal_count}
- Not Evaluated: {unevaluated_count}
- Out-of-Range Tests: {", ".join(abnormal_names) if abnormal_names else "None"}

Detected Clinical Patterns:
{json.dumps(patterns, indent=2)}

RULES:
1. Provide a balanced, encouraging summary of these exact findings.
2. If all or most parameters are normal, emphasize that overall findings are reassuring.
3. If specific out-of-range parameters exist, mention them neutrally without diagnosing.
4. NO diagnosis. NO prescriptions.
5. Provide response in {language}.
6. Keep under 100 words.
"""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=250
        )
        return response.choices[0].message.content.strip()

    except Exception:
        return (
            f"Summary: {normal_count} normal, {borderline_count} borderline, and {abnormal_count} out-of-range "
            f"parameters detected. Please review detailed breakdown with your physician."
        )


def generate_health_coach_plan(
    results: List[Dict[str, Any]],
    patterns: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]]
) -> str:
    """
    FEATURE 3: Personalized Health Coach.
    """
    if not profile:
        profile = {"age": 30, "activity": "Moderate", "goal": "General Wellness"}

    abnormal_items = [f"{r['name']} ({r['label']})" for r in results if r["status"] == "red"]

    # If completely normal report:
    if not abnormal_items and not patterns:
        return """### 🎯 Actionable Steps
1. **Maintain Consistency**: Keep up your current daily nutritional balance and hydration habits.
2. **Rest & Recovery**: Ensure 7-8 hours of restful sleep each night to sustain metabolic balance.
3. **Routine Wellness**: Schedule periodic annual health checkups to track your biomarker trends over time.

### 🥗 Nutrition Strategy
- **Whole Foods Focus**: Emphasize fiber-rich vegetables, lean proteins, healthy fats (olive oil, avocados), and whole grains.
- **Hydration**: Drink 2 to 2.5 liters of clean water daily.

### 💪 Activity Plan
- **Cardiovascular Health**: 150 minutes of moderate aerobic activity weekly (brisk walking, cycling, or swimming).
- **Strength Training**: 2 sessions per week targeting major muscle groups for metabolic resilience.

*Consult your doctor before starting any new exercise or diet regimen.*"""

    try:
        client = get_openai_client()
        if not client:
            return "Please consult your healthcare provider to discuss lifestyle recommendations for your results."

        prompt = f"""You are a certified clinical wellness coach. Generate a personalized wellness guidance plan.
User Profile:
- Age: {profile.get('age', 30)}
- Activity Level: {profile.get('activity', 'Moderate')}
- Health Goal: {profile.get('goal', 'General Wellness')}

Findings:
- Out of Range Parameters: {", ".join(abnormal_items) if abnormal_items else "None"}
- Patterns: {", ".join([p['title'] for p in patterns]) if patterns else "None"}

Format in Markdown:
1. **🎯 Actionable Steps**: 2-3 specific lifestyle steps.
2. **🥗 Nutrition Strategy**: Practical dietary focus.
3. **💪 Activity Plan**: Tailored movement recommendations.

Rules:
- Realistic and encouraging.
- NO diagnosis, NO medications.
- Must include: "Consult your doctor before starting a new exercise or diet regimen."
"""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=450
        )
        return response.choices[0].message.content.strip()

    except Exception:
        return "Please consult your healthcare provider to discuss lifestyle recommendations."


def calculate_confidence_score(extraction_metadata: dict, results_count: int) -> str:
    """Calculates overall interpretation confidence based on extraction fidelity."""
    method = extraction_metadata.get("extraction_method", "failed")
    if method == "llm" and results_count >= 3:
        return "High"
    if method in ("llm", "regex") and results_count > 0:
        return "Medium"
    return "Low"


def process_lab_results(
    extraction_package: dict,
    patient_context: Optional[dict] = None
) -> dict:
    """
    Main analysis entry point.
    Processes extraction package containing 'parameters' or 'data'.
    """
    raw_params = extraction_package.get("parameters", [])
    data_dict = extraction_package.get("data", {})
    metadata = extraction_package.get("metadata", {})

    user_profile = {}
    if st and hasattr(st, "session_state"):
        try:
            user_profile = st.session_state.get("user_profile", {})
        except Exception:
            user_profile = {}

    if patient_context is None:
        gender = user_profile.get("gender", "default")
        age_group = user_profile.get("age_group", "adult")
        patient_context = {"gender": gender, "age_group": age_group}

    gender = patient_context.get("gender", "default")
    age_group = patient_context.get("age_group", "adult")

    results = []

    # Priority 1: Use rich parameter objects if available
    if raw_params:
        for p in raw_params:
            t_name = p.get("name", "")
            t_val = p.get("value")
            t_unit = p.get("unit", "")
            t_range = p.get("reference_range", None)

            if t_name and t_val is not None:
                risk_info = assess_risk(
                    test_name=t_name,
                    value=float(t_val),
                    unit=t_unit,
                    report_range_str=t_range,
                    gender=gender,
                    age_group=age_group
                )
                results.append({
                    "name": risk_info["name"],
                    "value": risk_info["value"],
                    "unit": risk_info["unit"],
                    "reference": risk_info["range"],
                    "status": risk_info["status"],
                    "label": risk_info["label"],
                    "is_critical": risk_info.get("is_critical", False),
                    "is_unknown": risk_info.get("is_unknown", False),
                    "bar_pct": risk_info["bar_pct"],
                    "explanation": risk_info["message"]
                })

    # Priority 2: Fallback to flat dictionary data
    elif data_dict:
        for t_name, t_val in data_dict.items():
            if t_name and t_val is not None:
                risk_info = assess_risk(
                    test_name=t_name,
                    value=float(t_val),
                    unit="",
                    report_range_str=None,
                    gender=gender,
                    age_group=age_group
                )
                results.append({
                    "name": risk_info["name"],
                    "value": risk_info["value"],
                    "unit": risk_info["unit"],
                    "reference": risk_info["range"],
                    "status": risk_info["status"],
                    "label": risk_info["label"],
                    "is_critical": risk_info.get("is_critical", False),
                    "is_unknown": risk_info.get("is_unknown", False),
                    "bar_pct": risk_info["bar_pct"],
                    "explanation": risk_info["message"]
                })

    # Clinical Patterns
    patterns = detect_clinical_patterns(results)

    # AI Summary
    language = user_profile.get("language", "English")
    ai_summary = generate_summary_ai(results, patterns, language)

    # Confidence
    confidence = calculate_confidence_score(metadata, len(results))

    # Health Coach Plan
    health_plan = generate_health_coach_plan(results, patterns, user_profile)

    # Check for genuine clinical emergencies
    has_critical = any(r.get("is_critical", False) for r in results)

    return {
        "results": results,
        "patterns": patterns,
        "summary": ai_summary,
        "confidence": confidence,
        "health_plan": health_plan,
        "has_critical": has_critical
    }
