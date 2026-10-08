# utils/reference_ranges.py

"""
Medical reference ranges for lab tests.
Sources: Standard clinical guidelines
"""

REFERENCE_RANGES = {
    # Complete Blood Count (CBC)
    "hemoglobin": {
        "name": "Hemoglobin",
        "unit": "g/dL",
        "ranges": {
            "male": {"min": 13.5, "max": 17.5},
            "female": {"min": 12.0, "max": 16.0},
            "child": {"min": 11.0, "max": 16.0},
            "default": {"min": 12.0, "max": 16.0}
        },
        "critical": {
            "low": 7.0,  # Below this is critical
            "high": 20.0  # Above this is critical
        }
    },
    
    "wbc_count": {
        "name": "WBC Count",
        "unit": "/μL",
        "ranges": {
            "default": {"min": 4500, "max": 11000}
        },
        "critical": {
            "low": 2000,
            "high": 30000
        }
    },
    
    "platelets": {
        "name": "Platelets",
        "unit": "/μL",
        "ranges": {
            "default": {"min": 150000, "max": 400000}
        },
        "critical": {
            "low": 50000,
            "high": 1000000
        }
    },
    
    # Metabolic Panel
    "fasting_glucose": {
        "name": "Fasting Glucose",
        "unit": "mg/dL",
        "ranges": {
            "default": {"min": 70, "max": 100},
            "prediabetic": {"min": 101, "max": 125},
            "diabetic": {"min": 126, "max": 999}
        },
        "critical": {
            "low": 50,
            "high": 400
        }
    },
    
    "creatinine": {
        "name": "Creatinine",
        "unit": "mg/dL",
        "ranges": {
            "male": {"min": 0.7, "max": 1.3},
            "female": {"min": 0.6, "max": 1.1},
            "default": {"min": 0.7, "max": 1.2}
        }
    },
    
    # Lipid Profile
    "total_cholesterol": {
        "name": "Total Cholesterol",
        "unit": "mg/dL",
        "ranges": {
            "desirable": {"min": 0, "max": 200},
            "borderline": {"min": 201, "max": 239},
            "high": {"min": 240, "max": 999}
        }
    },
    
    # Liver Function
    "alt": {
        "name": "ALT (SGPT)",
        "unit": "U/L",
        "ranges": {
            "male": {"min": 10, "max": 40},
            "female": {"min": 7, "max": 35},
            "default": {"min": 10, "max": 40}
        }
    },
    
    "ast": {
        "name": "AST (SGOT)",
        "unit": "U/L",
        "ranges": {
            "default": {"min": 10, "max": 40}
        }
    },
    
    # Thyroid
    "tsh": {
        "name": "TSH",
        "unit": "mIU/L",
        "ranges": {
            "default": {"min": 0.4, "max": 4.5}
        }
    }
}


def get_reference_range(test_name: str, gender: str = "default", age_group: str = "adult"):
    """
    Get reference range for a specific test considering patient context.
    
    Args:
        test_name: Name of the lab test
        gender: "male", "female", or "default"
        age_group: "adult", "child", etc.
    
    Returns:
        Dictionary with min/max values or None if test not found
    """
    test_key = test_name.lower().replace(" ", "_")
    
    if test_key not in REFERENCE_RANGES:
        return None
    
    test_info = REFERENCE_RANGES[test_key]
    
    # Try gender-specific range first
    if "ranges" in test_info:
        if gender in test_info["ranges"]:
            return test_info["ranges"][gender]
        elif age_group in test_info["ranges"]:
            return test_info["ranges"][age_group]
        else:
            return test_info["ranges"].get("default", test_info["ranges"])
    
    return None


def get_critical_limits(test_name: str):
    """Get critical low/high values for a test."""
    test_key = test_name.lower().replace(" ", "_")
    if test_key in REFERENCE_RANGES:
        return REFERENCE_RANGES[test_key].get("critical", {})
    return {}