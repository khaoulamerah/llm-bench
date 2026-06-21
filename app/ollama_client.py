import json
import re
import time
import requests

from config import OLLAMA_CHAT_URL, OLLAMA_TAGS_URL, REQUEST_TIMEOUT_SECONDS


class OllamaError(Exception):
    pass


def is_model_available(model_name: str) -> bool:
    try:
        resp = requests.get(OLLAMA_TAGS_URL, timeout=10)
        resp.raise_for_status()
        available = [m["name"] for m in resp.json().get("models", [])]
        return model_name in available
    except requests.RequestException as e:
        raise OllamaError(f"Impossible de contacter Ollama : {e}")


def _extract_json(raw_text: str) -> dict:
    raw_text = raw_text.strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError(f"Reponse non-JSON du modele : {raw_text[:300]}")


def call_model(model_name: str, system_prompt: str, user_prompt: str,
                temperature: float = 0.1) -> dict:
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "format": "json",
        "stream": False,
        "options": {"temperature": temperature},
    }

    start = time.perf_counter()
    try:
        resp = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise OllamaError(f"Appel a {model_name} echoue : {e}")
    elapsed = time.perf_counter() - start

    body = resp.json()
    raw_content = body.get("message", {}).get("content", "")

    try:
        parsed = _extract_json(raw_content)
    except ValueError as e:
        raise OllamaError(str(e))

    return {
        "parsed": parsed,
        "latency_seconds": round(elapsed, 2),
        "raw_response": raw_content,
        "eval_count": body.get("eval_count"),
        "eval_duration_ns": body.get("eval_duration"),
    }
