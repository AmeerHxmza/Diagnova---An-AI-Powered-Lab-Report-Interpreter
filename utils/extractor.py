# utils/extractor.py

"""
Lab report text extraction and clinical entity parsing module.
Extracts test names, numeric values, measurement units, and laboratory-specific
reference ranges using OpenAI gpt-4o-mini and deterministic regex fallback.
"""

import json
import re
import io
import base64
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image

try:
    import streamlit as st
except ImportError:
    st = None

from utils.openai_client import get_openai_client, OPENAI_MODEL


def extract_text_from_image(uploaded_file) -> str:
    """
    Extract text from uploaded image (PNG, JPG, JPEG) using OpenAI gpt-4o-mini vision.
    Token-optimized: downsizes oversized images and compresses before encoding.
    """
    try:
        client = get_openai_client()
        if not client:
            print("[WARN] No OPENAI_API_KEY available for OCR")
            return ""

        # Read image bytes
        if hasattr(uploaded_file, "read"):
            image_bytes = uploaded_file.read()
            uploaded_file.seek(0)
        else:
            image_bytes = uploaded_file

        if not image_bytes:
            return ""

        # Open and optimize image using PIL to save tokens
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Limit maximum dimension to 1600px to optimize vision token usage
        max_dim = 1600
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

        # Compress to JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        b64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

        prompt = (
            "You are an expert clinical document OCR engine.\n"
            "Transcribe ALL text, lab test names, numeric values, units, and reference ranges "
            "visible in this lab report image verbatim.\n"
            "Do NOT summarize, comment, or omit anything. Output all transcribed text clearly."
        )

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1500,
            temperature=0.0
        )

        extracted_text = response.choices[0].message.content or ""
        print(f"[OK] OCR transcribed {len(extracted_text)} characters from image")
        return extracted_text.strip()

    except Exception as e:
        print(f"[ERROR] OCR Extraction failed: {str(e)}")
        return ""


def call_llm(prompt: str, json_mode: bool = False) -> str:
    """
    Call OpenAI LLM API to extract structured data from text.
    """
    try:
        client = get_openai_client()
        if not client:
            print("[WARN] No OPENAI_API_KEY found")
            return "{}" if json_mode else ""

        kwargs = {
            "model": OPENAI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,  # Zero temperature for deterministic extraction
            "max_tokens": 1500,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        result = response.choices[0].message.content or ""
        return result

    except Exception as e:
        print(f"[ERROR] OpenAI LLM call failed: {str(e)}")
        return "{}" if json_mode else ""


def extract_parameters_from_llm(text: str) -> dict:
    """
    Extract structured lab parameters (name, value, unit, reference range) from raw text.
    """
    prompt = f"""You are a clinical laboratory data extraction engine.
Extract ALL test parameters from the following lab report.

For each parameter, extract:
1. "name": The clean standard medical test name (e.g. "White Blood Cell Count (WBC)", "Hemoglobin", "Platelets", "RBC Count", "Neutrophils").
2. "value": The numeric value as a number (e.g. 7.65, 14.2, 250, 4.8). If formatted with commas (e.g. 7,650), convert to number (7650).
3. "unit": The exact unit of measurement stated on the report line (e.g. "10^3/uL", "10^6/uL", "g/dL", "%", "fL", "pg", "/uL", "mg/dL"). If no unit is provided, use "".
4. "reference_range": The reference or normal range string printed by the lab (e.g. "4.5 - 11.0", "13.5 - 17.5", "< 200", "4,500 - 11,000"). If not provided in the report, use null.

Return ONLY valid JSON in this exact structure:
{{
  "parameters": [
    {{
      "name": "WBC Count",
      "value": 7.65,
      "unit": "10^3/uL",
      "reference_range": "4.5 - 11.0"
    }}
  ]
}}

Lab Report Text:
{text}
"""

    try:
        llm_response = call_llm(prompt, json_mode=True)
        cleaned = llm_response.strip()

        if "```" in cleaned:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and end > start:
                cleaned = cleaned[start:end+1]

        data = json.loads(cleaned)
        return data if isinstance(data, dict) else {}

    except Exception as e:
        print(f"[ERROR] JSON extraction failed: {str(e)}")
        return {}


def clean_and_normalize_extracted(raw_json: dict) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    """
    Cleans raw extraction JSON into:
    1. data: Dict[str, float] for legacy backward compatibility.
    2. parameters: List[Dict[str, Any]] with name, value, unit, reference_range.
    """
    data: Dict[str, float] = {}
    parameters: List[Dict[str, Any]] = []

    # Format 1: {"parameters": [...]}
    if "parameters" in raw_json and isinstance(raw_json["parameters"], list):
        for item in raw_json["parameters"]:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            raw_val = item.get("value")
            unit = str(item.get("unit", "")).strip()
            ref_range = item.get("reference_range")
            if ref_range is not None:
                ref_range = str(ref_range).strip()

            if not name or raw_val is None:
                continue

            # Convert value to float
            num_val = None
            if isinstance(raw_val, (int, float)):
                num_val = float(raw_val)
            else:
                v_str = str(raw_val).replace("<", "").replace(">", "").replace(",", "").strip()
                m = re.search(r'-?\d+\.?\d*', v_str)
                if m:
                    num_val = float(m.group(0))

            if num_val is not None:
                data[name] = num_val
                parameters.append({
                    "name": name,
                    "value": num_val,
                    "unit": unit,
                    "reference_range": ref_range
                })

    # Format 2: Flat dictionary {"Test Name": value}
    elif raw_json and isinstance(raw_json, dict):
        for key, val in raw_json.items():
            if key == "parameters" or val is None:
                continue
            num_val = None
            if isinstance(val, (int, float)):
                num_val = float(val)
            elif isinstance(val, dict):
                raw_v = val.get("value")
                if isinstance(raw_v, (int, float)):
                    num_val = float(raw_v)
                elif raw_v:
                    m = re.search(r'-?\d+\.?\d*', str(raw_v).replace(",", ""))
                    if m:
                        num_val = float(m.group(0))
            elif isinstance(val, str):
                m = re.search(r'-?\d+\.?\d*', val.replace(",", ""))
                if m:
                    num_val = float(m.group(0))

            if num_val is not None:
                data[str(key).strip()] = num_val
                parameters.append({
                    "name": str(key).strip(),
                    "value": num_val,
                    "unit": "",
                    "reference_range": None
                })

    return data, parameters


def regex_fallback_extraction(text: str) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    """
    Robust regex-based fallback extraction when LLM fails or is unavailable.
    Extracts name, numeric value, unit, and optional reference range.
    """
    data: Dict[str, float] = {}
    parameters: List[Dict[str, Any]] = []

    lines = text.strip().split('\n')
    for line in lines:
        line_clean = line.strip()
        if not line_clean or len(line_clean) < 3:
            continue

        # Pattern: Test Name [:=-] Value [Unit] [(Ref: Min-Max)]
        # Example: "WBC Count: 7.65 10^3/uL (Ref: 4.5 - 11.0)"
        pattern = r'^([A-Za-z\s/%()-]+?)[\s:=-]+([0-9,.]+)\s*([A-Za-z/%µ0-9^*\-]*)(?:[\s([<{]*?(?:ref|reference|range|normal)?[\s:=-]*([0-9.,]+\s*(?:-|–|—|to)\s*[0-9.,]+|[<≤>≥]\s*[0-9.,]+))?'
        m = re.match(pattern, line_clean, re.IGNORECASE)
        if m:
            test_name = m.group(1).strip()
            val_str = m.group(2).replace(",", "").strip()
            unit_str = (m.group(3) or "").strip()
            range_str = (m.group(4) or "").strip() or None

            try:
                num_val = float(val_str)
                if 2 <= len(test_name) <= 40:
                    data[test_name] = num_val
                    parameters.append({
                        "name": test_name,
                        "value": num_val,
                        "unit": unit_str,
                        "reference_range": range_str
                    })
            except ValueError:
                continue

    return data, parameters


def process_lab_report(text: str) -> dict:
    """
    Main function to process raw lab report text into structured lab data.

    Returns:
        dict: {
            "data": Dict[str, float],
            "parameters": List[Dict[str, Any]],
            "metadata": {
                "extraction_method": "llm" | "regex" | "failed",
                "raw_count": int
            }
        }
    """
    result_package = {
        "data": {},
        "parameters": [],
        "metadata": {"extraction_method": "failed", "raw_count": 0}
    }

    if not text or not isinstance(text, str) or not text.strip():
        return result_package

    try:
        text = text.strip()

        # Step 1: Try LLM extraction first
        raw_llm = extract_parameters_from_llm(text)
        data, parameters = clean_and_normalize_extracted(raw_llm)

        if parameters:
            result_package["data"] = data
            result_package["parameters"] = parameters
            result_package["metadata"]["extraction_method"] = "llm"
            result_package["metadata"]["raw_count"] = len(parameters)
            print(f"[OK] LLM extracted {len(parameters)} structured parameters")
        else:
            # Step 2: Fallback to Regex extraction
            data, parameters = regex_fallback_extraction(text)
            if parameters:
                result_package["data"] = data
                result_package["parameters"] = parameters
                result_package["metadata"]["extraction_method"] = "regex"
                result_package["metadata"]["raw_count"] = len(parameters)
                print(f"[OK] Regex fallback extracted {len(parameters)} parameters")

        return result_package

    except Exception as e:
        print(f"[ERROR] Exception in process_lab_report: {str(e)}")
        return result_package
