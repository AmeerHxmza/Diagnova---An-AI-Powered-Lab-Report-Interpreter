"""
Test script to verify Groq LLM integration and extraction pipeline
Run this to check if everything is working before running the full Streamlit app
"""

# Mock streamlit secrets for testing
class MockSecrets:
    def get(self, key, default=None):
        # Read from secrets.toml file
        try:
            with open('.streamlit/secrets.toml', 'r') as f:
                for line in f:
                    if line.strip().startswith('GROQ_API_KEY'):
                        return line.split('=')[1].strip().strip('"').strip("'")
        except:
            pass
        return default

# Inject mock before importing
import sys
sys.path.insert(0, '.')

import streamlit as st
st.secrets = MockSecrets()

from utils.extractor import process_lab_report

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
print("Testing Lab Report Extraction")
print("=" * 60)
print("\nInput text:")
print(sample_text)
print("\n" + "=" * 60)
print("Processing...")
print("=" * 60 + "\n")

result = process_lab_report(sample_text)

print("\n" + "=" * 60)
print("RESULTS:")
print("=" * 60)
if result:
    print(f"✅ Successfully extracted {len(result)} values:\n")
    for key, value in result.items():
        print(f"  {key}: {value} (type: {type(value).__name__})")
else:
    print("❌ No values extracted")
    
print("\n" + "=" * 60)
