"""utils/openai_client.py

Centralized OpenAI client and configuration for Diagnova.
Handles API key resolution across st.secrets, .env, and environment variables.
Configured with OpenAI's cost-effective and token-efficient 'gpt-4o-mini' model.
"""

import os
from typing import Optional
from dotenv import load_dotenv

try:
    import streamlit as st
except ImportError:
    st = None

from openai import OpenAI

# Load local environment variables from .env
load_dotenv()

OPENAI_MODEL = "gpt-4o-mini"


def get_openai_api_key() -> str:
    """
    Retrieve OpenAI API key with multiple fallback sources:
    1. Streamlit secrets (st.secrets["OPENAI_API_KEY"] or st.secrets.get("OPENAI_API_KEY"))
    2. Environment variables: OPENAI_API_KEY, OPEN_AI_API_KEY, or 'open ai api key'
    3. Direct .env file parsing as a fallback
    """
    # 1. Check Streamlit secrets
    try:
        if hasattr(st, "secrets"):
            if "OPENAI_API_KEY" in st.secrets:
                key = str(st.secrets["OPENAI_API_KEY"]).strip()
                if key:
                    return key
            if "openai_api_key" in st.secrets:
                key = str(st.secrets["openai_api_key"]).strip()
                if key:
                    return key
    except Exception:
        pass

    # 2. Check standard environment variables
    for var_name in ["OPENAI_API_KEY", "OPEN_AI_API_KEY", "open ai api key"]:
        env_val = os.getenv(var_name)
        if env_val and env_val.strip():
            return env_val.strip()

    # 3. Direct inspection of .env if dotenv didn't pick up non-standard formatting
    try:
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line and not line.startswith("#"):
                        key, val = line.split("=", 1)
                        norm_key = key.strip().lower().replace(" ", "_")
                        if norm_key in ["openai_api_key", "open_ai_api_key"]:
                            val = val.strip().strip('"').strip("'")
                            if val:
                                return val
    except Exception:
        pass

    return ""


def get_openai_client() -> Optional[OpenAI]:
    """
    Get an initialized OpenAI client or None if API key is not configured.
    """
    api_key = get_openai_api_key()
    if not api_key:
        return None
    return OpenAI(api_key=api_key)
