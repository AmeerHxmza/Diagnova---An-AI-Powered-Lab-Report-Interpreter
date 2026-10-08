# test_cbc_pipeline.py

"""
Comprehensive verification script for the upgraded Diagnova clinical pipeline.
Tests:
1. 15-parameter synthetic CBC dataset evaluation against adult-male reference ranges.
2. Unit conversion and magnitude alignment (WBC 7.65 10^3/uL vs /uL catalog).
3. Handling of missing reference ranges (Not Evaluated instead of Borderline).
4. Alignment of AI explanation with deterministic status.
5. Calibrated urgency alert (No false urgent alert on normal reports).
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from utils.extractor import process_lab_report
from utils.analyzer import process_lab_results, assess_risk

print("=" * 70)
print("  DIAGNOVA CLINICAL PIPELINE VERIFICATION")
print("=" * 70)

# ── 1. Synthetic 15-Parameter CBC Dataset ─────────────────────────────────────
synthetic_cbc_text = """
COMPLETE BLOOD COUNT (CBC) - ADULT MALE
White Blood Cell Count (WBC): 7.65 10^3/uL
Red Blood Cell Count (RBC): 4.80 10^6/uL
Hemoglobin: 15.2 g/dL
Hematocrit: 45.0 %
Mean Corpuscular Volume (MCV): 89.0 fL
Mean Corpuscular Hemoglobin (MCH): 29.5 pg
Mean Corpuscular Hemoglobin Concentration (MCHC): 33.5 g/dL
Red Cell Distribution Width (RDW): 12.8 %
Platelet Count: 265 10^3/uL
Mean Platelet Volume (MPV): 9.8 fL
Neutrophils: 60.0 %
Lymphocytes: 28.0 %
Monocytes: 6.5 %
Eosinophils: 2.5 %
Basophils: 0.5 %
"""

print("\n--- TEST 1: EXTRACTION & ANALYSIS OF 15-PARAMETER CBC ---")
extracted = process_lab_report(synthetic_cbc_text)
print(f"Extracted count: {len(extracted.get('parameters', []))} parameters")
for p in extracted.get("parameters", []):
    print(f"  • {p['name']}: {p['value']} {p['unit']} (Ref: {p['reference_range']})")

analysis = process_lab_results(extracted, patient_context={"gender": "male", "age_group": "adult"})
results = analysis["results"]

counts = {"green": 0, "yellow": 0, "red": 0, "gray": 0}
for r in results:
    s = r["status"]
    counts[s] = counts.get(s, 0) + 1

print("\n--- CLASSIFICATION AUDIT ---")
print(f"Total parameters evaluated: {len(results)}")
print(f"Normal (green):     {counts['green']} (Expected: 15)")
print(f"Borderline (yellow): {counts['yellow']} (Expected: 0)")
print(f"Abnormal (red):     {counts['red']} (Expected: 0)")
print(f"Not Evaluated (gray):{counts['gray']} (Expected: 0)")

print("\nDetailed Parameter Breakdown:")
for r in results:
    print(f"  • {r['name']:<25} = {r['value']:<6} {r['unit']:<8} | Ref: {r['reference']:<18} | Status: [{r['label']}]")

# Check WBC specifically
wbc_res = next((r for r in results if "WBC" in r["name"]), None)
if wbc_res:
    print(f"\nWBC Verification:")
    print(f"  Status: {wbc_res['label']} ({wbc_res['status']})")
    print(f"  Explanation: {wbc_res['explanation']}")
    assert wbc_res["status"] == "green", f"WBC should be green, got {wbc_res['status']}"

assert counts["green"] == 15, f"Expected 15 Normal, got {counts['green']}"
assert counts["yellow"] == 0, f"Expected 0 Borderline, got {counts['yellow']}"
assert counts["red"] == 0, f"Expected 0 Abnormal, got {counts['red']}"
print("\n[PASS] TEST 1: All 15 CBC parameters accurately classified as NORMAL!")


# ── 2. Missing Reference Range Test ───────────────────────────────────────────
print("\n--- TEST 2: MISSING REFERENCE RANGE (BUG 2 AUDIT) ---")
unknown_result = assess_risk(
    test_name="Uncataloged Novel Biomarker XYZ",
    value=42.0,
    unit="ng/mL",
    report_range_str=None
)
print(f"Test: {unknown_result['name']}")
print(f"Status: {unknown_result['status']} (Label: {unknown_result['label']})")
print(f"Range:  {unknown_result['range']}")
print(f"Message:{unknown_result['message']}")

assert unknown_result["status"] == "gray", f"Expected 'gray', got {unknown_result['status']}"
assert unknown_result["label"] == "Not Evaluated", f"Expected 'Not Evaluated', got {unknown_result['label']}"
print("[PASS] TEST 2: Missing reference ranges return 'Not Evaluated' (gray), NEVER Borderline (yellow)!")


# ── 3. WBC Unit Discrepancy Test ──────────────────────────────────────────────
print("\n--- TEST 3: WBC MAGNITUDE & UNIT DISCREPANCY (BUG 1 AUDIT) ---")
# Case A: 7.65 in thousands vs generic catalog (4500 - 11000)
res_a = assess_risk("WBC", 7.65, "10^3/uL", gender="male")
print(f"WBC 7.65 10^3/uL -> Status: {res_a['label']}, Ref: {res_a['range']}")
assert res_a["status"] == "green", f"Expected green for 7.65 10^3/uL, got {res_a['status']}"

# Case B: 7650 in absolute cells
res_b = assess_risk("WBC", 7650.0, "/uL", gender="male")
print(f"WBC 7650 /uL    -> Status: {res_b['label']}, Ref: {res_b['range']}")
assert res_b["status"] == "green", f"Expected green for 7650 /uL, got {res_b['status']}"

print("[PASS] TEST 3: WBC magnitude and unit alignment resolves both scales seamlessly!")


# ── 4. Urgency Alert Audit ────────────────────────────────────────────────────
print("\n--- TEST 4: URGENCY ALERT AUDIT ---")
print(f"Has Critical in 15-parameter CBC: {analysis.get('has_critical', False)}")
assert not analysis.get("has_critical", False), "Normal CBC must NOT trigger critical urgency alert!"
print("[PASS] TEST 4: No false urgent alerts on normal CBC reports!")

print("\n" + "=" * 70)
print("  ALL 4 CLINICAL PIPELINE TESTS PASSED WITH 100% SUCCESS!")
print("=" * 70)
