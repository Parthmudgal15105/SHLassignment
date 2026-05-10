import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def call_llm_for_intent(messages: list[dict[str, str]]) -> dict[str, Any] | None:
    provider = os.getenv("LLM_PROVIDER", "").lower().strip()

    if provider == "gemini":
        return call_gemini_for_intent(messages)

    return None


def call_gemini_for_intent(messages: list[dict[str, str]]) -> dict[str, Any] | None:
    try:
        from google import genai
    except ImportError:
        return None

    api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("LLM_MODEL", "gemini-2.5-flash")

    if not api_key:
        return None

    client = genai.Client(api_key=api_key)

    conversation_text = "\n".join(
        f"{m.get('role', '')}: {m.get('content', '')}" for m in messages
    )

    prompt = f"""
You are an intent extractor for an SHL assessment recommender.

Return ONLY valid JSON with these fields:
{{
  "intent": "clarify | recommend | refine | compare | refuse | finalize",
  "role": "",
  "skills": [],
  "include": [],
  "exclude": [],
  "assessment_types": [],
  "comparison_products": [],
  "is_out_of_scope": false
}}

Rules:
- Only classify intent. Do not recommend products.
- If the user asks legal/compliance/general hiring/non-SHL advice, set intent to "refuse".
- If the user asks difference/compare/vs, set intent to "compare".
- If the user says final/confirmed/lock it in, set intent to "finalize".
- If the request is too vague, set intent to "clarify".

Conversation:
{conversation_text}
"""

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )

        text = response.text.strip()

        if text.startswith("```"):
            text = text.strip("`")
            text = text.replace("json", "", 1).strip()

        return json.loads(text)

    except Exception:
        return None