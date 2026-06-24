import os

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_CHAT_URL = f"{OLLAMA_HOST}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_HOST}/api/tags"

MODELS_TO_TEST = [
    {"name": "qwen2.5:7b",  "size_gb": 4.7, "notes": "bon support arabe"},
    {"name": "llama3.1:8b", "size_gb": 4.7, "notes": "solide FR/EN, plus faible en AR"},
    {"name": "mistral:7b",  "size_gb": 4.1, "notes": "rapide, correct en FR"},
]

DATA_DIR = "/app/data/articles"
RESULTS_DIR = "/app/results"
LANGUAGES = ["fr", "ar", "en"]
REQUEST_TIMEOUT_SECONDS = 120