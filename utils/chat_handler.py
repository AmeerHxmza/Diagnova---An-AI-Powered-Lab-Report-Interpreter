# utils/chat_handler.py

"""
Chat assistant handler for patient questions about their lab results.
Powered by OpenAI gpt-4o-mini for cost and token efficiency.
"""

from utils.openai_client import get_openai_client, OPENAI_MODEL


def get_chat_response(messages: list, context: dict):
    """
    Handle AI Chat Assistant Q&A.
    Grounds the conversation in the current analysis context.
    """
    results_summary = []
    for r in context.get("results", []):
        results_summary.append(f"{r['name']}: {r['value']} {r.get('unit', '')} ({r['status']})")
    
    patterns_summary = [p["title"] for p in context.get("patterns", [])]
    
    system_prompt = f"""
You are Diagnova AI, a friendly and professional medical report assistant.
The user is asking questions about their specific lab results.

CURRENT RESULTS:
{", ".join(results_summary) if results_summary else "No specific test results available."}

DETECTED PATTERNS:
{", ".join(patterns_summary) if patterns_summary else "None detected."}

INSTRUCTIONS:
1. Base your answers ONLY on the provided results and general medical knowledge.
2. Be empathetic and clear.
3. NEVER give a definitive diagnosis or prescribe medication.
4. If asked about something not in the report, clearly state that.
5. Always remind the user: "This information is for educational purposes. Please consult your doctor for a formal diagnosis."
6. Keep answers concise (under 3 sentences unless complex) to save tokens and maintain readability.
"""
    
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    
    try:
        client = get_openai_client()
        if not client:
            return "I apologize, but I cannot answer questions right now (OpenAI API key missing). Please consult your physician."
            
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=full_messages,
            temperature=0.5,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"I'm sorry, I'm having trouble processing your question. Error: {str(e)}"
