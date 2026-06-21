from ollama_client import call_model, OllamaError
from prompts import SUMMARY_SYSTEM_PROMPT, build_summary_user_prompt


def run_summary(model_name: str, article: dict) -> dict:
    user_prompt = build_summary_user_prompt(article["title"], article["text"])

    base_row = {
        "task": "summarize",
        "model": model_name,
        "lang": article.get("lang"),
        "article_id": article.get("id"),
    }

    try:
        result = call_model(model_name, SUMMARY_SYSTEM_PROMPT, user_prompt)
    except OllamaError as e:
        return {**base_row, "status": "error", "error": str(e)}

    summary_text = result["parsed"].get("summary", "")
    key_points = result["parsed"].get("key_points", [])

    return {
        **base_row,
        "status": "ok",
        "summary": summary_text,
        "summary_length_chars": len(summary_text),
        "key_points_count": len(key_points),
        "latency_seconds": result["latency_seconds"],
        "eval_count": result["eval_count"],
    }
