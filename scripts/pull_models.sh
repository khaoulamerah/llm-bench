
CONTAINER="llm-bench-ollama"

MODELS=(
    "qwen2.5:7b"
    # "llama3.1:8b"
    # "mistral:7b"
)

# ── Check if container is running ──
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER}$"; then
    echo "[ERROR] Container '${CONTAINER}' is not running."
    echo "        Start it first with: docker compose up -d"
    exit 1
fi

echo "========================================="
echo " Ollama container detected — pulling models"
echo "========================================="
echo ""

# ── Pull each model ──
for model in "${MODELS[@]}"; do
    echo ">>> Pulling ${model} ..."
    docker compose exec ollama ollama pull "$model"

    if [ $? -eq 0 ]; then
        echo "[OK] ${model} downloaded successfully"
    else
        echo "[FAILED] ${model} — check your connection or model name"
    fi
    echo ""
done

echo "========================================="
echo " Done. Verify with:"
echo " docker compose exec ollama ollama list"
echo "========================================="