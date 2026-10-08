# utils/chat_handler.py

import streamlit as st
from groq import Groq
import json

def get_chat_response(messages: list, context: dict):
    """
    Handle AI Chat Assistant Q&A.
    Grounds the conversation in the current analysis context.
    """
    results_summary = []
    for r in context.get("results", []):
        results_summary.append(f"{r['name']}: {r['value']} {r['unit']} ({r['status']})")
    
    patterns_summary = [p["title"] for p in context.get("patterns", [])]
    
    system_prompt = f"""
    You are Diagnova AI, a friendly and professional medical report assistant.
    The user is asking questions about their specific lab results.
    
    CURRENT RESULTS:
    {", ".join(results_summary)}
    
    DETECTED PATTERNS:
    {", ".join(patterns_summary)}
    
    INSTRUCTIONS:
    1. Base your answers ONLY on the provided results and general medical knowledge.
    2. Be empathetic and clear.
    3. NEVER give a definitive diagnosis or prescribe medication.
    4. If asked about something not in the report, clearly state that.
    5. Always remind the user: "This information is for educational purposes. Please consult your doctor for a formal diagnosis."
    6. Keep answers concise (under 3 sentences unless complex).
    """
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return "I apologize, but I cannot answer questions right now (API Key missing). Please consult your physician."
            
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_messages,
            temperature=0.6,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I'm sorry, I'm having trouble processing your question. Error: {str(e)}"
