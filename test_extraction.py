"""test_extraction.py

Test script to verify OpenAI gpt-4o-mini integration and extraction pipeline.
Run this to check if everything is working before running the full Streamlit app.
"""

import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, '.')

from utils.openai_client import get_openai_api_key, OPENAI_MODEL
from utils.extractor import process_lab_report
from utils.analyzer import process_lab_results

# Test sample
sample_text = """
Hemoglobin: 11.2 g/dL
WBC Count: 7,800 /μL
Fasting Glucose: 108 mg/dL
Platelets: 145,000 /μL
Creatinine: 0.9 mg/dL
Total Cholesterol: 215 mg/dL
"""

print("=" * 60)
print(f"Testing Diagnova with OpenAI ({OPENAI_MODEL})")
print("=" * 60)

api_key = get_openai_api_key()
if api_key:
    masked_key = api_key[:7] + "..." + api_key[-4:]
    print(f"✅ OpenAI API Key detected: {masked_key}")
else:
    print("⚠️ No OpenAI API Key found in .env or secrets")

print("\nInput text:")
print(sample_text)
print("=" * 60)
print("Processing extraction...")
print("=" * 60)

extraction_result = process_lab_report(sample_text)
data = extraction_result.get("data", {})
metadata = extraction_result.get("metadata", {})

print("\nEXTRACTION RESULTS:")
print(f"Method: {metadata.get('extraction_method')}")
print(f"Items extracted: {metadata.get('raw_count')}")
for key, value in data.items():
    print(f"  • {key}: {value} (type: {type(value).__name__})")

print("\n" + "=" * 60)
print("Processing analysis...")
print("=" * 60)

analysis_result = process_lab_results(extraction_result)
print(f"Confidence: {analysis_result.get('confidence')}")
print(f"Detected Patterns: {len(analysis_result.get('patterns', []))}")
for p in analysis_result.get("patterns", []):
    print(f"  • [{p['severity'].upper()}] {p['title']}: {p['insight']}")

print(f"\nAI Summary:\n{analysis_result.get('summary')}")
print("\n" + "=" * 60)
print("✅ Test Complete!")
print("=" * 60)
