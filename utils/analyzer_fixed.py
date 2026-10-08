# utils/analyzer.py

"""
Lab test risk analysis with pattern detection and intelligent recommendations.
"""

from utils.reference_ranges import get_reference_range, get_critical_limits


def assess_risk(test_name: str, value: float, unit: str = "", 
                gender: str = "default", age_group: str = "adult"):
    """
    Assess risk level for a single lab value.
    
    Args:
        test_name: Name of the test
        value: Numeric value
        unit: Unit of measurement
        gender: Patient gender
        age_group: Patient age group
    
    Returns:
        dict: Risk assessment with status, range, message, bar percentage
    """
    
    # Get reference range
    ref_range = get_reference_range(test_name, gender, age_group)
    
    if not ref_range:
        return {
            "status": "yellow",
            "range": "Reference range not available",
            "message": f"Unable to find reference range for {test_name}.",
            "bar_pct": 50
        }
    
    min_val = ref_range.get("min", 0)
    max_val = ref_range.get("max", 100)
    
    # Check critical limits first
    critical = get_critical_limits(test_name)
    if critical:
        if value < critical.get("low", -float('inf')):
            return {
                "status": "red",
                "range": f"{min_val} – {max_val}",
                "message": f"CRITICALLY LOW: {test_name} is dangerously below normal range. Seek immediate medical attention.",
                "bar_pct": 10
            }
        if value > critical.get("high", float('inf')):
            return {
                "status": "red",
                "range": f"{min_val} – {max_val}",
                "message": f"CRITICALLY HIGH: {test_name} is dangerously above normal range. Seek immediate medical attention.",
                "bar_pct": 90
            }
    
    # Calculate percentage for visual bar
    if value < min_val:
        # Below range
        pct = max(10, (value / min_val) * 30)
        bar_pct = min(30, pct)
    elif value > max_val:
        # Above range
        ratio = value / max_val
        pct = min(90, 70 + (ratio * 20))
        bar_pct = min(90, pct)
    else:
        # Within range - map to 30-70% range
        bar_pct = 30 + ((value - min_val) / (max_val - min_val) * 40)
    
    # Risk assessment logic
    if min_val <= value <= max_val:
        # Normal range
        return {
            "status": "green",
            "range": f"{min_val} – {max_val}",
            "message": f"Your {test_name} is within the normal range.",
            "bar_pct": int(bar_pct)
        }
    
    elif value < min_val:
        # Below normal
        deviation_pct = ((min_val - value) / min_val) * 100
        
        if deviation_pct < 10:
            status = "yellow"
            message = f"Your {test_name} is slightly below normal. Consider monitoring."
        else:
            status = "red"
            message = f"Your {test_name} is significantly below normal. Please consult your doctor."
        
        return {
            "status": status,
            "range": f"{min_val} – {max_val}",
            "message": message,
            "bar_pct": int(bar_pct)
        }
    
    else:  # value > max_val
        # Above normal
        deviation_pct = ((value - max_val) / max_val) * 100
        
        if deviation_pct < 10:
            status = "yellow"
            message = f"Your {test_name} is slightly above normal. Lifestyle modifications may help."
        else:
            status = "red"
            message = f"Your {test_name} is significantly above normal. Please consult your doctor."
        
        return {
            "status": status,
            "range": f"{min_val} – {max_val}",
            "message": message,
            "bar_pct": int(bar_pct)
        }


def detect_patterns(results: list) -> list:
    """
    Detect medical patterns across multiple lab values.
    
    Args:
        results: List of result dictionaries with name, value, status
    
    Returns:
        list: List of detected pattern strings
    """
    patterns = []
    
    # Helper to find results by name
    def find_test(name_substring):
        return [r for r in results if name_substring.lower() in r["name"].lower()]
    
    # Pattern 1: Anemia indicators
    hb_tests = find_test("hemoglobin")
    if hb_tests and hb_tests[0]["status"] in ["red", "yellow"]:
        if hb_tests[0]["value"] < 12:
            patterns.append("Possible anemia detected (low hemoglobin). Consider iron studies, B12, and folate levels.")
    
    # Pattern 2: Diabetes indicators
    glucose_tests = find_test("glucose")
    if glucose_tests and glucose_tests[0]["value"] > 100:
        if glucose_tests[0]["value"] >= 126:
            patterns.append("Fasting glucose in diabetic range. HbA1c testing recommended.")
        elif glucose_tests[0]["value"] > 100:
            patterns.append("Fasting glucose elevated. Pre-diabetic range - lifestyle modifications recommended.")
    
    # Pattern 3: Kidney function
    creatinine_tests = find_test("creatinine")
    if creatinine_tests and creatinine_tests[0]["status"] == "red":
        patterns.append("Elevated creatinine may indicate reduced kidney function. Additional kidney function tests recommended.")
    
    # Pattern 4: Liver function
    alt_tests = find_test("alt")
    ast_tests = find_test("ast")
    if (alt_tests and alt_tests[0]["status"] in ["red", "yellow"]) or \
       (ast_tests and ast_tests[0]["status"] in ["red", "yellow"]):
        patterns.append("Liver enzyme elevation detected. Avoid alcohol and hepatotoxic medications. Consult physician.")
    
    # Pattern 5: Lipid profile issues
    chol_tests = find_test("cholesterol")
    if chol_tests and chol_tests[0]["value"] > 200:
        patterns.append("Elevated cholesterol. Dietary modifications (low saturated fat) and exercise recommended.")
    
    # Pattern 6: Infection/inflammation indicators
    wbc_tests = find_test("wbc")
    if wbc_tests and wbc_tests[0]["value"] > 11000:
        patterns.append("Elevated WBC count may indicate infection or inflammation.")
    
    # Pattern 7: Clotting risk
    platelet_tests = find_test("platelet")
    if platelet_tests:
        if platelet_tests[0]["value"] < 100000:
            patterns.append("Low platelet count increases bleeding risk. Avoid NSAIDs and contact sports.")
        elif platelet_tests[0]["value"] > 500000:
            patterns.append("Elevated platelet count may increase clotting risk.")
    
    return patterns


def generate_summary(results: list, patterns: list) -> str:
    """
    Generate intelligent summary based on actual results and patterns.
    
    Args:
        results: List of result dictionaries
        patterns: List of detected pattern strings
    
    Returns:
        str: Natural language summary
    """
    if not results:
        return "No lab values were successfully extracted for analysis. Please check your input format."
    
    # Count by status
    counts = {"green": 0, "yellow": 0, "red": 0}
    for r in results:
        counts[r["status"]] += 1
    
    total = len(results)
    
    # Build summary
    summary_parts = []
    
    # Overall assessment
    if counts["red"] > 0:
        summary_parts.append(f"⚠️ {counts['red']} parameter(s) are outside normal range and require medical attention.")
    if counts["yellow"] > 0:
        summary_parts.append(f"{counts['yellow']} parameter(s) are borderline and should be monitored.")
    if counts["green"] > 0:
        summary_parts.append(f"✅ {counts['green']} parameter(s) are within normal range.")
    
    # Specific abnormal findings
    abnormal = [r for r in results if r["status"] in ["red", "yellow"]]
    if abnormal:
        summary_parts.append("\n\n**Key Findings:**")
        for r in abnormal[:3]:  # Top 3 abnormal results
            value_str = f"{r['value']:,.1f}" if isinstance(r['value'], float) else str(r['value'])
            summary_parts.append(f"• {r['name']}: {value_str} {r.get('unit', '')} ({r['status'].upper()})")
    
    # Add patterns
    if patterns:
        summary_parts.append("\n\n**Detected Patterns:**")
        for pattern in patterns[:3]:  # Top 3 patterns
            summary_parts.append(f"• {pattern}")
    
    # Medical disclaimer
    summary_parts.append("\n\n⚕️ **Important:** This analysis is for educational purposes only. Always consult a qualified healthcare provider for medical advice.")
    
    return " ".join(summary_parts)


def generate_next_steps(results: list, patterns: list) -> list:
    """
    Generate personalized next steps based on actual abnormal values.
    
    Args:
        results: List of result dictionaries
        patterns: List of detected pattern strings
    
    Returns:
        list: List of next step dictionaries with tag, icon, text
    """
    next_steps = []
    
    # Prioritize by severity
    critical = [r for r in results if r["status"] == "red"]
    borderline = [r for r in results if r["status"] == "yellow"]
    
    # Critical findings - urgent action needed
    for r in critical[:2]:  # Top 2 critical
        next_steps.append({
            "tag": "urgent",
            "icon": "🚨",
            "text": f"Consult a physician urgently about your {r['name']} level. This requires medical evaluation."
        })
    
    # Borderline findings - consult recommended
    for r in borderline[:2]:  # Top 2 borderline
        next_steps.append({
            "tag": "consult",
            "icon": "⚠️",
            "text": f"Schedule a follow-up for {r['name']}. Your doctor may recommend lifestyle changes or further testing."
        })
    
    # Pattern-based recommendations
    for pattern in patterns[:2]:  # Top 2 patterns
        next_steps.append({
            "tag": "monitor",
            "icon": "✅",
            "text": pattern
        })
    
    # If no abnormal findings, general advice
    if not next_steps:
        next_steps.append({
            "tag": "monitor",
            "icon": "✅",
            "text": "All values are within normal range. Maintain healthy lifestyle and routine check-ups."
        })
    
    # Limit to 5 next steps max
    return next_steps[:5]


def process_lab_results(extracted_data: dict, patient_context: dict = None):
    """
    Process multiple lab results from extraction.
    
    Complete pipeline:
    1. Assess risk for each value
    2. Detect patterns across values
    3. Generate intelligent summary
    4. Generate personalized next steps
    
    Args:
        extracted_data: Dictionary of {test_name: {"value": float, "unit": str}}
        patient_context: Optional dict with gender, age, etc.
    
    Returns:
        dict: Complete analysis with results, summary, next_steps, patterns
    """
    if patient_context is None:
        patient_context = {"gender": "default", "age_group": "adult"}
    
    results = []
    
    # Process each lab value
    for test_name, test_data in extracted_data.items():
        try:
            # Extract value and unit
            if isinstance(test_data, dict):
                value = test_data.get("value")
                unit = test_data.get("unit", "")
            else:
                # Fallback for old format
                value = test_data
                unit = ""
            
            # Validate value
            if value is None or not isinstance(value, (int, float)):
                continue
            
            value = float(value)
            
            # Assess risk
            risk_info = assess_risk(
                test_name, 
                value, 
                unit,
                patient_context.get("gender", "default"),
                patient_context.get("age_group", "adult")
            )
            
            # Build result record
            results.append({
                "name": test_name.title().replace("_", " "),
                "value": value,
                "unit": unit,
                "reference": risk_info["range"],
                "status": risk_info["status"],
                "bar_pct": risk_info["bar_pct"],
                "explanation": risk_info["message"]
            })
        
        except Exception as e:
            print(f"⚠️ Error processing {test_name}: {str(e)}")
            continue
    
    # Detect patterns
    patterns = detect_patterns(results)
    
    # Generate summary
    summary = generate_summary(results, patterns)
    
    # Generate next steps
    next_steps = generate_next_steps(results, patterns)
    
    return {
        "results": results,
        "summary": summary,
        "next_steps": next_steps,
        "patterns": patterns,
        "counts": {
            "green": sum(1 for r in results if r["status"] == "green"),
            "yellow": sum(1 for r in results if r["status"] == "yellow"),
            "red": sum(1 for r in results if r["status"] == "red")
        }
    }
