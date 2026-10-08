# utils/reference_ranges.py

"""
Comprehensive Laboratory Reference Ranges and Unit Normalization Engine.
Implements canonical alias mapping, unit compatibility scaling, and deterministic clinical thresholds.
Sources: Standard clinical pathology guidelines (CLSI, MedlinePlus, Mayo Clinic Laboratories).
"""

import re
from typing import Dict, Optional, Tuple, Any

# ── Canonical Test Aliases ───────────────────────────────────────────────────
CANONICAL_ALIASES = {
    # WBC
    "wbc": "wbc_count",
    "wbc_count": "wbc_count",
    "wbc count": "wbc_count",
    "white blood cells": "wbc_count",
    "white blood cell count": "wbc_count",
    "total leucocyte count": "wbc_count",
    "total leukocyte count": "wbc_count",
    "total leucocytes": "wbc_count",
    "total leukocytes": "wbc_count",
    "tlc": "wbc_count",
    "leukocytes": "wbc_count",
    "leucocytes": "wbc_count",

    # RBC
    "rbc": "rbc_count",
    "rbc_count": "rbc_count",
    "rbc count": "rbc_count",
    "red blood cells": "rbc_count",
    "red blood cell count": "rbc_count",
    "erythrocytes": "rbc_count",
    "total rbc": "rbc_count",

    # Hemoglobin
    "hb": "hemoglobin",
    "hgb": "hemoglobin",
    "hemoglobin": "hemoglobin",
    "haemoglobin": "hemoglobin",

    # Hematocrit
    "hct": "hematocrit",
    "hematocrit": "hematocrit",
    "haematocrit": "hematocrit",
    "pcv": "hematocrit",
    "packed cell volume": "hematocrit",

    # Indices
    "mcv": "mcv",
    "mean corpuscular volume": "mcv",
    "mean cell volume": "mcv",
    "mch": "mch",
    "mean corpuscular hemoglobin": "mch",
    "mean cell hemoglobin": "mch",
    "mchc": "mchc",
    "mean corpuscular hemoglobin concentration": "mchc",
    "mean cell hemoglobin concentration": "mchc",
    "rdw": "rdw",
    "rdw_cv": "rdw",
    "rdw-cv": "rdw",
    "rdw cv": "rdw",
    "red cell distribution width": "rdw",
    "rdw_sd": "rdw_sd",
    "rdw-sd": "rdw_sd",
    "rdw sd": "rdw_sd",

    # Platelets
    "platelets": "platelets",
    "platelet count": "platelets",
    "plt": "platelets",
    "thrombocytes": "platelets",
    "total platelets": "platelets",
    "mpv": "mpv",
    "mean platelet volume": "mpv",

    # Differential - Neutrophils
    "neutrophils": "neutrophils_pct",
    "neutrophil %": "neutrophils_pct",
    "neutrophils %": "neutrophils_pct",
    "neutrophil percent": "neutrophils_pct",
    "segmented neutrophils": "neutrophils_pct",
    "segs": "neutrophils_pct",
    "polys": "neutrophils_pct",
    "anc": "neutrophils_abs",
    "absolute neutrophils": "neutrophils_abs",
    "absolute neutrophil count": "neutrophils_abs",

    # Differential - Lymphocytes
    "lymphocytes": "lymphocytes_pct",
    "lymphocyte %": "lymphocytes_pct",
    "lymphocytes %": "lymphocytes_pct",
    "lymphocyte percent": "lymphocytes_pct",
    "lymphs": "lymphocytes_pct",
    "alc": "lymphocytes_abs",
    "absolute lymphocytes": "lymphocytes_abs",
    "absolute lymphocyte count": "lymphocytes_abs",

    # Differential - Monocytes
    "monocytes": "monocytes_pct",
    "monocyte %": "monocytes_pct",
    "monocytes %": "monocytes_pct",
    "monocyte percent": "monocytes_pct",
    "monos": "monocytes_pct",
    "amc": "monocytes_abs",
    "absolute monocytes": "monocytes_abs",
    "absolute monocyte count": "monocytes_abs",

    # Differential - Eosinophils
    "eosinophils": "eosinophils_pct",
    "eosinophil %": "eosinophils_pct",
    "eosinophils %": "eosinophils_pct",
    "eosinophil percent": "eosinophils_pct",
    "eos": "eosinophils_pct",
    "aec": "eosinophils_abs",
    "absolute eosinophils": "eosinophils_abs",
    "absolute eosinophil count": "eosinophils_abs",

    # Differential - Basophils
    "basophils": "basophils_pct",
    "basophil %": "basophils_pct",
    "basophils %": "basophils_pct",
    "basophil percent": "basophils_pct",
    "basos": "basophils_pct",
    "abc": "basophils_abs",
    "absolute basophils": "basophils_abs",
    "absolute basophil count": "basophils_abs",

    # Metabolic & Renal
    "fasting glucose": "fasting_glucose",
    "fasting blood sugar": "fasting_glucose",
    "fbs": "fasting_glucose",
    "glucose": "fasting_glucose",
    "blood sugar": "fasting_glucose",
    "creatinine": "creatinine",
    "serum creatinine": "creatinine",
    "urea": "urea",
    "blood urea": "urea",
    "bun": "bun",
    "blood urea nitrogen": "bun",
    "hba1c": "hba1c",
    "glycated hemoglobin": "hba1c",

    # Liver
    "alt": "alt",
    "sgpt": "alt",
    "alt (sgpt)": "alt",
    "ast": "ast",
    "sgot": "ast",
    "ast (sgot)": "ast",
    "alp": "alp",
    "alkaline phosphatase": "alp",
    "total bilirubin": "bilirubin_total",
    "bilirubin": "bilirubin_total",

    # Lipids
    "total cholesterol": "total_cholesterol",
    "cholesterol": "total_cholesterol",
    "triglycerides": "triglycerides",
    "hdl": "hdl",
    "hdl cholesterol": "hdl",
    "ldl": "ldl",
    "ldl cholesterol": "ldl",

    # Thyroid
    "tsh": "tsh",
    "thyroid stimulating hormone": "tsh",
}

# Standard Clinical Display Names
STANDARD_NAMES = {
    "wbc_count": "WBC Count",
    "rbc_count": "RBC Count",
    "hemoglobin": "Hemoglobin",
    "hematocrit": "Hematocrit",
    "mcv": "MCV",
    "mch": "MCH",
    "mchc": "MCHC",
    "rdw": "RDW",
    "rdw_sd": "RDW-SD",
    "platelets": "Platelet Count",
    "mpv": "MPV",
    "neutrophils_pct": "Neutrophils (%)",
    "neutrophils_abs": "Absolute Neutrophils",
    "lymphocytes_pct": "Lymphocytes (%)",
    "lymphocytes_abs": "Absolute Lymphocytes",
    "monocytes_pct": "Monocytes (%)",
    "monocytes_abs": "Absolute Monocytes",
    "eosinophils_pct": "Eosinophils (%)",
    "eosinophils_abs": "Absolute Eosinophils",
    "basophils_pct": "Basophils (%)",
    "basophils_abs": "Absolute Basophils",
    "fasting_glucose": "Fasting Glucose",
    "creatinine": "Creatinine",
    "urea": "Blood Urea",
    "bun": "BUN",
    "hba1c": "HbA1c",
    "alt": "ALT (SGPT)",
    "ast": "AST (SGOT)",
    "alp": "Alkaline Phosphatase",
    "bilirubin_total": "Total Bilirubin",
    "total_cholesterol": "Total Cholesterol",
    "triglycerides": "Triglycerides",
    "hdl": "HDL Cholesterol",
    "ldl": "LDL Cholesterol",
    "tsh": "TSH",
}


# ── Clinical Catalog Reference Ranges ────────────────────────────────────────
REFERENCE_RANGES = {
    # ── Complete Blood Count (CBC) ──────────────────────────
    "wbc_count": {
        "name": "WBC Count",
        "units": {
            "k_uL": "10³/µL",
            "cells_uL": "/µL"
        },
        "ranges": {
            "male":    {"min": 4.5, "max": 11.0, "unit": "10³/µL"},
            "female":  {"min": 4.5, "max": 11.0, "unit": "10³/µL"},
            "child":   {"min": 5.0, "max": 15.0, "unit": "10³/µL"},
            "default": {"min": 4.5, "max": 11.0, "unit": "10³/µL"}
        },
        "critical": {
            "low": 2.0,     # < 2.0 × 10³/µL or < 2000 /µL is severe leukopenia
            "high": 30.0    # > 30.0 × 10³/µL or > 30000 /µL is marked leukocytosis
        }
    },

    "rbc_count": {
        "name": "RBC Count",
        "units": {
            "M_uL": "10⁶/µL"
        },
        "ranges": {
            "male":    {"min": 4.3, "max": 5.9, "unit": "10⁶/µL"},
            "female":  {"min": 3.8, "max": 5.2, "unit": "10⁶/µL"},
            "child":   {"min": 4.0, "max": 5.5, "unit": "10⁶/µL"},
            "default": {"min": 4.2, "max": 5.8, "unit": "10⁶/µL"}
        },
        "critical": {
            "low": 2.0,
            "high": 7.5
        }
    },

    "hemoglobin": {
        "name": "Hemoglobin",
        "units": {
            "g_dL": "g/dL"
        },
        "ranges": {
            "male":    {"min": 13.5, "max": 17.5, "unit": "g/dL"},
            "female":  {"min": 12.0, "max": 16.0, "unit": "g/dL"},
            "child":   {"min": 11.0, "max": 16.0, "unit": "g/dL"},
            "default": {"min": 13.0, "max": 17.0, "unit": "g/dL"}
        },
        "critical": {
            "low": 7.0,
            "high": 20.0
        }
    },

    "hematocrit": {
        "name": "Hematocrit",
        "units": {
            "pct": "%"
        },
        "ranges": {
            "male":    {"min": 41.0, "max": 53.0, "unit": "%"},
            "female":  {"min": 36.0, "max": 46.0, "unit": "%"},
            "child":   {"min": 34.0, "max": 44.0, "unit": "%"},
            "default": {"min": 38.0, "max": 50.0, "unit": "%"}
        },
        "critical": {
            "low": 20.0,
            "high": 60.0
        }
    },

    "mcv": {
        "name": "MCV",
        "units": {
            "fL": "fL"
        },
        "ranges": {
            "default": {"min": 80.0, "max": 100.0, "unit": "fL"}
        },
        "critical": {
            "low": 65.0,
            "high": 120.0
        }
    },

    "mch": {
        "name": "MCH",
        "units": {
            "pg": "pg"
        },
        "ranges": {
            "default": {"min": 27.0, "max": 33.0, "unit": "pg"}
        }
    },

    "mchc": {
        "name": "MCHC",
        "units": {
            "g_dL": "g/dL"
        },
        "ranges": {
            "default": {"min": 32.0, "max": 36.0, "unit": "g/dL"}
        }
    },

    "rdw": {
        "name": "RDW",
        "units": {
            "pct": "%"
        },
        "ranges": {
            "default": {"min": 11.5, "max": 14.5, "unit": "%"}
        }
    },

    "rdw_sd": {
        "name": "RDW-SD",
        "units": {
            "fL": "fL"
        },
        "ranges": {
            "default": {"min": 39.0, "max": 46.0, "unit": "fL"}
        }
    },

    "platelets": {
        "name": "Platelets",
        "units": {
            "k_uL": "10³/µL",
            "cells_uL": "/µL"
        },
        "ranges": {
            "default": {"min": 150.0, "max": 450.0, "unit": "10³/µL"}
        },
        "critical": {
            "low": 50.0,     # < 50 × 10³/µL or < 50,000 /µL (bleeding risk)
            "high": 1000.0   # > 1000 × 10³/µL or > 1,000,000 /µL (thrombosis risk)
        }
    },

    "mpv": {
        "name": "MPV",
        "units": {
            "fL": "fL"
        },
        "ranges": {
            "default": {"min": 7.5, "max": 11.5, "unit": "fL"}
        }
    },

    # ── Differential Leukocytes ─────────────────────────────
    "neutrophils_pct": {
        "name": "Neutrophils (%)",
        "ranges": {
            "default": {"min": 40.0, "max": 75.0, "unit": "%"}
        }
    },
    "neutrophils_abs": {
        "name": "Absolute Neutrophils",
        "ranges": {
            "default": {"min": 1.8, "max": 7.5, "unit": "10³/µL"}
        },
        "critical": {
            "low": 0.5,      # Severe neutropenia
            "high": 25.0
        }
    },

    "lymphocytes_pct": {
        "name": "Lymphocytes (%)",
        "ranges": {
            "default": {"min": 20.0, "max": 45.0, "unit": "%"}
        }
    },
    "lymphocytes_abs": {
        "name": "Absolute Lymphocytes",
        "ranges": {
            "default": {"min": 1.0, "max": 4.0, "unit": "10³/µL"}
        }
    },

    "monocytes_pct": {
        "name": "Monocytes (%)",
        "ranges": {
            "default": {"min": 2.0, "max": 10.0, "unit": "%"}
        }
    },
    "monocytes_abs": {
        "name": "Absolute Monocytes",
        "ranges": {
            "default": {"min": 0.2, "max": 0.8, "unit": "10³/µL"}
        }
    },

    "eosinophils_pct": {
        "name": "Eosinophils (%)",
        "ranges": {
            "default": {"min": 1.0, "max": 6.0, "unit": "%"}
        }
    },
    "eosinophils_abs": {
        "name": "Absolute Eosinophils",
        "ranges": {
            "default": {"min": 0.0, "max": 0.5, "unit": "10³/µL"}
        }
    },

    "basophils_pct": {
        "name": "Basophils (%)",
        "ranges": {
            "default": {"min": 0.0, "max": 2.0, "unit": "%"}
        }
    },
    "basophils_abs": {
        "name": "Absolute Basophils",
        "ranges": {
            "default": {"min": 0.0, "max": 0.2, "unit": "10³/µL"}
        }
    },

    # ── Metabolic & Renal ───────────────────────────────────
    "fasting_glucose": {
        "name": "Fasting Glucose",
        "ranges": {
            "default": {"min": 70.0, "max": 99.0, "unit": "mg/dL"}
        },
        "critical": {
            "low": 50.0,
            "high": 400.0
        }
    },

    "hba1c": {
        "name": "HbA1c",
        "ranges": {
            "default": {"min": 4.0, "max": 5.6, "unit": "%"}
        }
    },

    "creatinine": {
        "name": "Creatinine",
        "ranges": {
            "male":    {"min": 0.7, "max": 1.3, "unit": "mg/dL"},
            "female":  {"min": 0.6, "max": 1.1, "unit": "mg/dL"},
            "default": {"min": 0.7, "max": 1.2, "unit": "mg/dL"}
        },
        "critical": {
            "high": 4.0
        }
    },

    "urea": {
        "name": "Blood Urea",
        "ranges": {
            "default": {"min": 15.0, "max": 45.0, "unit": "mg/dL"}
        }
    },

    "bun": {
        "name": "BUN",
        "ranges": {
            "default": {"min": 7.0, "max": 20.0, "unit": "mg/dL"}
        }
    },

    # ── Liver Function ──────────────────────────────────────
    "alt": {
        "name": "ALT (SGPT)",
        "ranges": {
            "male":    {"min": 10.0, "max": 40.0, "unit": "U/L"},
            "female":  {"min": 7.0,  "max": 35.0, "unit": "U/L"},
            "default": {"min": 10.0, "max": 40.0, "unit": "U/L"}
        }
    },

    "ast": {
        "name": "AST (SGOT)",
        "ranges": {
            "default": {"min": 10.0, "max": 40.0, "unit": "U/L"}
        }
    },

    "alp": {
        "name": "Alkaline Phosphatase",
        "ranges": {
            "default": {"min": 44.0, "max": 147.0, "unit": "U/L"}
        }
    },

    "bilirubin_total": {
        "name": "Total Bilirubin",
        "ranges": {
            "default": {"min": 0.2, "max": 1.2, "unit": "mg/dL"}
        }
    },

    # ── Lipid Profile ───────────────────────────────────────
    "total_cholesterol": {
        "name": "Total Cholesterol",
        "ranges": {
            "default": {"min": 125.0, "max": 200.0, "unit": "mg/dL"}
        }
    },

    "triglycerides": {
        "name": "Triglycerides",
        "ranges": {
            "default": {"min": 50.0, "max": 150.0, "unit": "mg/dL"}
        }
    },

    "hdl": {
        "name": "HDL Cholesterol",
        "ranges": {
            "male":    {"min": 40.0, "max": 90.0, "unit": "mg/dL"},
            "female":  {"min": 50.0, "max": 90.0, "unit": "mg/dL"},
            "default": {"min": 40.0, "max": 90.0, "unit": "mg/dL"}
        }
    },

    "ldl": {
        "name": "LDL Cholesterol",
        "ranges": {
            "default": {"min": 50.0, "max": 100.0, "unit": "mg/dL"}
        }
    },

    # ── Thyroid ─────────────────────────────────────────────
    "tsh": {
        "name": "TSH",
        "ranges": {
            "default": {"min": 0.4, "max": 4.5, "unit": "mIU/L"}
        }
    }
}


# ── Utility: Test Name Normalization ─────────────────────────────────────────
def normalize_test_key(test_name: str, unit: str = "", value: Optional[float] = None) -> str:
    """
    Map raw test name string to its canonical dictionary key.
    Handles variations like TLC, WBC, White Blood Cells, ANC, Segs, etc.
    Ensures compound names (e.g. Mean Corpuscular Hemoglobin) are matched before generic components.
    """
    clean_name = test_name.lower().strip()
    clean_name = re.sub(r'[^a-z0-9% ]+', ' ', clean_name).strip()
    clean_name = re.sub(r'\s+', ' ', clean_name)
    words = clean_name.split()

    # Priority 0: Explicit MCHC / MCH disambiguation from standard Hemoglobin
    if "mchc" in words or "mean corpuscular hemoglobin concentration" in clean_name or "mean cell hemoglobin concentration" in clean_name:
        return "mchc"
    if "mch" in words or "mean corpuscular hemoglobin" in clean_name or "mean cell hemoglobin" in clean_name:
        return "mch"

    # Priority 1: Direct dictionary alias lookup
    if clean_name in CANONICAL_ALIASES:
        key = CANONICAL_ALIASES[clean_name]
    else:
        underscored = clean_name.replace(" ", "_")
        if underscored in CANONICAL_ALIASES:
            key = CANONICAL_ALIASES[underscored]
        elif underscored in REFERENCE_RANGES:
            key = underscored
        else:
            # Match longest multi-word aliases first to avoid greedy substring collisions
            sorted_aliases = sorted(CANONICAL_ALIASES.items(), key=lambda x: len(x[0]), reverse=True)
            key = None
            for alias, target in sorted_aliases:
                if alias == clean_name:
                    key = target
                    break
                if " " in alias and alias in clean_name:
                    key = target
                    break
                if " " not in alias and alias in words:
                    if alias in ("hemoglobin", "hb", "hgb") and any(w in words for w in ["mch", "mchc", "corpuscular"]):
                        continue
                    key = target
                    break
            if not key:
                key = underscored

    # 2. Contextual differentiation: Percent vs Absolute differential
    # If the user reported "Neutrophils" without specifying pct or abs:
    unit_str = (unit or "").lower()
    if key in ("neutrophils_pct", "lymphocytes_pct", "monocytes_pct", "eosinophils_pct", "basophils_pct"):
        # Check if unit indicates absolute (e.g., 10^3/uL, /uL, k/uL)
        if any(u in unit_str for u in ["10^3", "10*3", "10e3", "k/ul", "/ul", "cells", "thou"]):
            abs_key = key.replace("_pct", "_abs")
            return abs_key
        # Check if value is very small (< 10) for neutrophils/lymphocytes and unit is not %
        if "%" not in unit_str and value is not None:
            if key == "neutrophils_pct" and value < 10.0:
                return "neutrophils_abs"
            if key == "lymphocytes_pct" and value < 8.0:
                return "lymphocytes_abs"

    return key or clean_name


def get_display_name(test_key: str) -> str:
    """Return standard clinical display name for a test key."""
    if test_key in STANDARD_NAMES:
        return STANDARD_NAMES[test_key]
    if test_key in REFERENCE_RANGES and "name" in REFERENCE_RANGES[test_key]:
        return REFERENCE_RANGES[test_key]["name"]
    return test_key.replace("_", " ").title()


# ── Utility: Reference Range Parser ──────────────────────────────────────────
def parse_reference_range(range_str: str) -> Optional[Dict[str, float]]:
    """
    Parse a reference range string from a laboratory report.
    Examples:
      - "4.5 - 11.0" -> {"min": 4.5, "max": 11.0}
      - "4,500 – 11,000" -> {"min": 4500.0, "max": 11000.0}
      - "< 200" -> {"min": 0.0, "max": 200.0}
      - "> 60" -> {"min": 60.0, "max": 9999.0}
      - "13.5 to 17.5" -> {"min": 13.5, "max": 17.5}
    """
    if not range_str or not isinstance(range_str, str):
        return None

    clean = range_str.replace(",", "").strip()

    # Pattern: < X or <= X
    m_lt = re.search(r'^[<≤]\s*([0-9]+\.?[0-9]*)', clean)
    if m_lt:
        return {"min": 0.0, "max": float(m_lt.group(1))}

    # Pattern: > X or >= X
    m_gt = re.search(r'^[>≥]\s*([0-9]+\.?[0-9]*)', clean)
    if m_gt:
        return {"min": float(m_gt.group(1)), "max": 999999.0}

    # Pattern: MIN - MAX or MIN to MAX
    m_range = re.search(r'([0-9]+\.?[0-9]*)\s*(?:-|–|—|to)\s*([0-9]+\.?[0-9]*)', clean)
    if m_range:
        v1 = float(m_range.group(1))
        v2 = float(m_range.group(2))
        return {"min": min(v1, v2), "max": max(v1, v2)}

    return None


# ── Utility: Unit & Scale Compatibility Normalizer ───────────────────────────
def align_value_and_range(
    value: float,
    unit: str,
    range_min: float,
    range_max: float,
    test_key: str
) -> Tuple[float, float, float, str]:
    """
    Normalizes magnitude discrepancies between extracted values and reference ranges.
    Fixes Bug 1 (e.g. WBC 7.65 × 10³/µL vs catalog range 4500–11000 /µL).

    Returns:
        Tuple[comp_value, comp_min, comp_max, effective_unit]
    """
    unit_lower = (unit or "").lower()

    # Rule 1: WBC / Platelet scale difference (Thousands vs Absolute cells)
    # If test is WBC, Absolute Leukocytes, or Platelets:
    if test_key in ("wbc_count", "platelets", "neutrophils_abs", "lymphocytes_abs", "monocytes_abs", "eosinophils_abs"):
        # Case A: Value is scaled (< 100 for WBC, < 1000 for Platelets), but range is in absolute (min >= 1000)
        if value < 100.0 and range_min >= 1000.0:
            # Range is in /uL (e.g. 4500 - 11000), while value is in 10^3/uL (7.65)
            # Normalize range to 10^3/uL scale for user-friendly display
            comp_min = range_min / 1000.0
            comp_max = range_max / 1000.0
            eff_unit = "10³/µL" if not unit else unit
            return value, comp_min, comp_max, eff_unit

        # Case B: Value is in absolute cells (>= 1000), but range is in 10^3/uL (<= 50)
        if value >= 500.0 and range_max <= 50.0:
            # Value is 7650, range is 4.5 - 11.0
            comp_val = value / 1000.0
            eff_unit = "10³/µL"
            return comp_val, range_min, range_max, eff_unit

        # Case C: Platelets in thousands vs absolute
        if test_key == "platelets":
            if value < 1000.0 and range_min >= 10000.0:
                comp_min = range_min / 1000.0
                comp_max = range_max / 1000.0
                eff_unit = "10³/µL" if not unit else unit
                return value, comp_min, comp_max, eff_unit
            elif value >= 10000.0 and range_max <= 1000.0:
                comp_val = value / 1000.0
                eff_unit = "10³/µL"
                return comp_val, range_min, range_max, eff_unit

    # Rule 2: Hemoglobin g/L vs g/dL
    if test_key == "hemoglobin":
        if value > 50.0 and range_max <= 25.0:
            # Value in g/L (e.g. 152 g/L -> 15.2 g/dL)
            return value / 10.0, range_min, range_max, "g/dL"
        if "g/l" in unit_lower and "dl" not in unit_lower and range_max <= 25.0:
            return value / 10.0, range_min, range_max, "g/dL"

    # Rule 3: Hematocrit fraction vs percentage
    if test_key == "hematocrit":
        if 0.0 < value <= 1.0 and range_min >= 20.0:
            # Value is 0.45 fraction -> 45.0 %
            return value * 100.0, range_min, range_max, "%"

    # Default: already on same scale
    eff_unit = unit if unit else ""
    return value, range_min, range_max, eff_unit


# ── Main Reference Range Lookup ──────────────────────────────────────────────
def get_reference_range(
    test_name: str,
    gender: str = "default",
    age_group: str = "adult",
    unit: str = "",
    value: Optional[float] = None
) -> Optional[Dict[str, Any]]:
    """
    Get reference range for a specific test considering demographic context,
    unit specification, and value scale.
    """
    test_key = normalize_test_key(test_name, unit, value)
    if test_key not in REFERENCE_RANGES:
        return None

    test_info = REFERENCE_RANGES[test_key]
    ranges = test_info.get("ranges", {})

    # Gender / age resolution
    gender_key = (gender or "default").lower()
    selected_range = None

    if gender_key in ranges:
        selected_range = ranges[gender_key]
    elif age_group in ranges:
        selected_range = ranges[age_group]
    elif "default" in ranges:
        selected_range = ranges["default"]
    elif ranges:
        selected_range = next(iter(ranges.values()))

    if not selected_range:
        return None

    min_val = selected_range.get("min", 0.0)
    max_val = selected_range.get("max", 100.0)
    ref_unit = selected_range.get("unit", unit or "")

    return {
        "key": test_key,
        "name": test_info.get("name", get_display_name(test_key)),
        "min": min_val,
        "max": max_val,
        "unit": ref_unit
    }


def get_critical_limits(test_name: str, unit: str = "", value: Optional[float] = None) -> Dict[str, float]:
    """Get clinical emergency critical limits for a test."""
    test_key = normalize_test_key(test_name, unit, value)
    if test_key in REFERENCE_RANGES:
        return REFERENCE_RANGES[test_key].get("critical", {})
    return {}