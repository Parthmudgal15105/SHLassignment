import json
import os
from typing import Any

import requests


def _extract_json(text: str) -> dict[str, Any] | None:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    try:
        data = json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None

    if isinstance(data, dict):
        return data

    return None


def _call_groq(prompt: str, model: str, timeout: float) -> dict[str, Any] | None:
    api_key = os.getenv("LLM_API_KEY", "").strip()

    if not api_key:
        return None

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Return only compact JSON. Do not recommend products. "
                        "Extract user intent for an SHL assessment recommender."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0,
            "max_tokens": 300,
            "response_format": {"type": "json_object"},
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"]
    return _extract_json(content)


def _call_gemini(prompt: str, model: str, timeout: float) -> dict[str, Any] | None:
    api_key = os.getenv("LLM_API_KEY", "").strip()

    if not api_key:
        return None

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        params={"key": api_key},
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "Return only compact JSON. Do not recommend products. "
                                "Extract user intent for an SHL assessment recommender.\n\n"
                                f"{prompt}"
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0,
                "maxOutputTokens": 300,
                "responseMimeType": "application/json",
            },
        },
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["candidates"][0]["content"]["parts"][0]["text"]
    return _extract_json(content)


def extract_intent_with_llm(prompt: str) -> dict[str, Any] | None:
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    timeout = float(os.getenv("LLM_TIMEOUT_SECONDS", "6"))

    if provider == "gemini":
        model = os.getenv("LLM_MODEL", "gemini-1.5-flash").strip()
        caller = _call_gemini
    else:
        model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant").strip()
        caller = _call_groq

    try:
        return caller(prompt, model, timeout)
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None
