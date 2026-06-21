from ollama_client import call_model, OllamaError
from prompts import SENTIMENT_SYSTEM_PROMPT, build_sentiment_user_prompt


def _enforce_score_coherence(label: str, score: float) -> float:
    if label == "positive" and score < 0.5:
        return 0.65
    if label == "negative" and score > 0.5:
        return 0.35
    if label == "neutral":
        return min(max(score, 0.4), 0.6)
    return score


def run_sentiment(model_name: str, article: dict) -> dict:
    user_prompt = build_sentiment_user_prompt(article["title"], article["text"])

    base_row = {
        "task": "sentiment",
        "model": model_name,
        "lang": article.get("lang"),
        "article_id": article.get("id"),
        "expected_label": article.get("expected_label"),
    }

    try:
        result = call_model(model_name, SENTIMENT_SYSTEM_PROMPT, user_prompt)
    except OllamaError as e:
        return {**base_row, "status": "error", "error": str(e)}

    label = result["parsed"].get("label", "?")
    score = result["parsed"].get("score", None)
    if score is not None:
        score = _enforce_score_coherence(label, float(score))

    return {
        **base_row,
        "status": "ok",
        "predicted_label": label,
        "score": score,
        "correct": (label == article.get("expected_label")) if article.get("expected_label") else None,
        "latency_seconds": result["latency_seconds"],
        "eval_count": result["eval_count"],
    }
