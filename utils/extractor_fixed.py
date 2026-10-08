# utils/extractor.py

"""
Lab report text extraction and cleaning module.
Extracts lab test values from pasted text using LLM and cleans them for analysis.
"""

import json
import re
from typing import Dict, Tuple
import streamlit as st
from groq import Groq


def call_llm(prompt: str) -> str:
    """
    Call Groq LLM API to extract structured data from text.
    
    Uses Groq's fast inference with Mixtral model for JSON extraction.
    Falls back to empty JSON if API call fails.
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        str: LLM response (should be valid JSON)
    """
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets.get("GROQ_API_KEY", "")
        
        if not api_key:
            # No API key - return empty JSON
            print("⚠️ No GROQ_API_KEY found in secrets - using regex fallback")
            return "{}"
        
        print(f"✅ API key found, calling Groq...")
        
        # Initialize Groq client
        client = Groq(api_key=api_key)
        
        # Call Groq API
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Fast, accurate model
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for consistent JSON output
            max_tokens=2000
        )
        
        result = response.choices[0].message.content
        print(f"✅ LLM response received ({len(result)} chars)")
        return result
        
    except Exception as e:
        # API call failed - return empty JSON safely
        print(f"❌ LLM call failed: {str(e)}")
        return "{}"


def extract_json_from_llm(text: str) -> dict:
    """
    Extract lab values from raw report text using LLM.
    
    Args:
        text: Raw lab report text from user input
        
    Returns:
        dict: Extracted lab values with format {"test": {"value": float, "unit": str}}
    """
    # Build prompt for LLM
    prompt = f"""Extract all lab test names, their numeric values AND units from the following lab report.

Return ONLY valid JSON in this EXACT format:
{{
  "Hemoglobin": {{"value": 11.2, "unit": "g/dL"}},
  "WBC Count": {{"value": 7800, "unit": "/μL"}},
  "Glucose": {{"value": 108, "unit": "mg/dL"}}
}}

CRITICAL RULES:
- Include BOTH value and unit for each test
- Use standard medical test names (Hemoglobin not Hb, WBC Count not WBC)
- Extract numeric value WITHOUT units in the "value" field
- Put the ORIGINAL unit in the "unit" field
- Do NOT include explanations, markdown, or extra text
- Return ONLY the JSON object

Lab Report Text:
{text}

JSON Output:"""

    try:
        # Call LLM
        llm_response = call_llm(prompt)
        cleaned = llm_response.strip()
        
        # Remove markdown code blocks if present
        if "```" in cleaned:
            # Extract content between first { and last }
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start:end+1]
        
        # Parse JSON
        data = json.loads(cleaned)
        
        # Ensure it's a dict
        return data if isinstance(data, dict) else {}
        
    except:
        # Any error - return empty dict safely
        return {}


def clean_lab_values(data: dict) -> dict:
    """
    Clean extracted lab values to ensure consistent format.
    
    Converts all values to proper structure with float value and string unit.
    Skips any value that cannot be converted to float.
    
    Args:
        data: Dictionary from LLM or regex (may contain various formats)
        
    Returns:
        dict: Clean dictionary with format {test_name: {"value": float, "unit": str}}
              GUARANTEED: All values are dicts with "value" (float) and "unit" (str)
    """
    cleaned = {}
    
    for key, val in data.items():
        try:
            # Skip None or empty
            if val is None or val == "":
                continue
            
            # Handle different input formats
            value = None
            unit = ""
            
            # Format 1: Already structured {"value": X, "unit": Y}
            if isinstance(val, dict):
                value = val.get("value")
                unit = val.get("unit", "")
            
            # Format 2: Just a number
            elif isinstance(val, (int, float)):
                value = val
                unit = ""
            
            # Format 3: String that might contain number + unit
            else:
                val_str = str(val)
                # Remove symbols
                val_str = val_str.replace("<", "").replace(">", "").replace(",", "")
                
                # Try to extract number and unit separately
                # Pattern: number (optional decimal) followed by optional whitespace and unit
                match = re.match(r'(-?\d+\.?\d*)\s*(.*)', val_str.strip())
                
                if match:
                    value = float(match.group(1))
                    unit = match.group(2).strip()
                else:
                    continue  # Can't parse, skip
            
            # Validate value is actually a number
            if value is not None:
                value = float(value)
                
                # Sanity check: reject obviously wrong values
                if value < 0:
                    continue  # Negative lab values don't make sense (except temperature)
                if value > 1_000_000:
                    continue  # Suspiciously high - likely extraction error
                
                cleaned[key] = {
                    "value": value,
                    "unit": str(unit) if unit else ""
                }
        
        except:
            # Skip any value that fails conversion
            continue
    
    return cleaned


def regex_fallback_extraction(text: str) -> dict:
    """
    Simple regex-based fallback extraction when LLM fails.
    
    Extracts patterns like:
    - Hemoglobin: 9.8 g/dL
    - WBC Count 12000 /μL
    - MCV - 70 fL
    
    Args:
        text: Raw lab report text
        
    Returns:
        dict: Extracted values {test_name: "value unit string"}
    """
    results = {}
    
    try:
        # Split into lines
        lines = text.strip().split('\n')
        
        for line in lines:
            # Pattern: Word(s) followed by separator (:, -, or space) then number (optional unit)
            match = re.match(
                r'([A-Za-z][A-Za-z\s]+?)[\s:=-]+([\d,.<>]+(?:\.\d+)?)\s*([A-Za-z/μ°%]*)',
                line.strip()
            )
            
            if match:
                test_name = match.group(1).strip()
                value_str = match.group(2).strip()
                unit = match.group(3).strip()
                
                # Only keep if test name looks reasonable (2-30 chars, contains letter)
                if 2 <= len(test_name) <= 30 and any(c.isalpha() for c in test_name):
                    # Store as string, will be cleaned by clean_lab_values
                    if unit:
                        results[test_name] = f"{value_str} {unit}"
                    else:
                        results[test_name] = value_str
    
    except:
        pass
    
    return results


def process_lab_report(text: str) -> dict:
    """
    Main function to process raw lab report text into clean lab values.
    
    Pipeline:
    1. Extract values using LLM (with units)
    2. Fallback to regex if LLM fails
    3. Clean and normalize to standard format
    4. Return result ready for risk analysis
    
    Args:
        text: Raw lab report text pasted by user or extracted from PDF
        
    Returns:
        dict: Clean dictionary {test_name: {"value": float, "unit": str}}
              Empty dict if processing fails
              GUARANTEED: All values have "value" (float) and "unit" (str)
              
    Example Output:
        {
            "Hemoglobin": {"value": 9.8, "unit": "g/dL"},
            "WBC Count": {"value": 12000.0, "unit": "/μL"},
            "MCV": {"value": 70.0, "unit": "fL"}
        }
    """
    # Validate input
    if not text or not isinstance(text, str) or not text.strip():
        print("❌ No valid text provided")
        return {}
    
    try:
        text = text.strip()
        print(f"📝 Processing {len(text)} characters of text...")
        
        # Step 1: Try LLM extraction first
        extracted_data = extract_json_from_llm(text)
        cleaned_data = clean_lab_values(extracted_data)
        
        if cleaned_data:
            print(f"✅ LLM extraction successful: {len(cleaned_data)} values")
        else:
            print("⚠️ LLM extraction returned empty, trying regex fallback...")
            # Step 2: If LLM failed, try regex fallback
            fallback_data = regex_fallback_extraction(text)
            cleaned_data = clean_lab_values(fallback_data)
            if cleaned_data:
                print(f"✅ Regex fallback successful: {len(cleaned_data)} values")
            else:
                print("❌ Both LLM and regex extraction failed")
        
        # Step 3: Final validation
        valid_data = {}
        for test, data in cleaned_data.items():
            if isinstance(data, dict) and "value" in data and isinstance(data["value"], float):
                valid_data[test] = data
        
        print(f"📊 Final result: {len(valid_data)} valid lab values")
        return valid_data
        
    except Exception as e:
        # Never crash the app
        print(f"❌ Exception in process_lab_report: {str(e)}")
        return {}
