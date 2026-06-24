# LLM Bench — Local Model Testing with Docker & Ollama

This project is a **local benchmarking environment** built to test and compare
open-weight LLM models (Qwen2.5, Llama3.1, Mistral...) before integrating
one of them into the **RSS Intelligence Pipeline** — a real production project
developed for **Djezzy**, Algeria's leading telecom operator.

 This bench helps answer:

- Which local model best replicates Gemini's domain-aware reasoning
  ("good news for Ooredoo = bad news for Djezzy") in French, Arabic, and English?
- What is the real inference speed on modest hardware (CPU, no dedicated GPU)?

This project also served as a **hands-on practice** for Docker, Docker Compose,
containerized services, and local LLM deployment patterns used in professional environments.

---

## Project Structure

```
llm-bench/
├── docker-compose.yml        # defines the 2 containers (ollama + app)
├── .env                      # Docker Compose project name
├── .gitignore
├── README.md
├── app/
│   ├── Dockerfile            # builds the Python app container
│   ├── requirements.txt      # requests, pandas, tabulate
│   ├── config.py             # models list, Ollama URL, paths
│   ├── prompts.py            # system prompts (sentiment + summarize)
│   ├── ollama_client.py      # HTTP client for Ollama API
│   ├── bench.py              # main script: runs all models x articles x tasks
│   ├── results_report.py     # reads CSV and prints comparison tables
│   └── tasks/
│       ├── sentiment.py      # sentiment task logic
│       └── summarize.py      # summarization task logic
├── data/
│   └── articles/
│       ├── articles_fr.json  # 5 French test articles with expected labels
│       ├── articles_ar.json  # 5 Arabic test articles with expected labels
│       └── articles_en.json  # 5 English test articles with expected labels
└── results/
    └── raw_results_*.csv     # auto-generated after each benchmark run
```

---

## Architecture: 2 Containers

| Container          | Image                       | Role                                                           |
| ------------------ | --------------------------- | -------------------------------------------------------------- |
| `llm-bench-ollama` | `ollama/ollama:latest`      | Loads LLM models into memory, exposes a REST API on port 11434 |
| `llm-bench-app`    | built from `app/Dockerfile` | Python scripts that send prompts to Ollama and save results    |

---

## Essential Docker Commands

### Start everything

````bash
docker compose up -d --build

### Check containers are running
```bash
docker compose ps
````

### Download models into Ollama container
```bash
chmod +x scripts/pull_models.sh
./scripts/pull_models.sh
``` 

### Download a model into the Ollama container

```bash
docker compose exec ollama ollama pull qwen2.5:7b
docker compose exec ollama ollama pull llama3.1:8b
docker compose exec ollama ollama pull mistral:7b
```

### List downloaded models

```bash
docker compose exec ollama ollama list
```

### Run the benchmark

```bash
# Full benchmark (all models x all languages x both tasks)
docker compose exec app python bench.py

# One model only
docker compose exec app python bench.py --models qwen2.5:7b

# One task only
docker compose exec app python bench.py --task sentiment

# One language only
docker compose exec app python bench.py --langs fr
```

### Generate the comparison report

```bash
docker compose exec app python results_report.py raw_results_XXXXXXXX.csv
```

### Stop containers (keeps downloaded models)

```bash
docker compose down
```

### Stop and delete everything including models

```bash
docker compose down -v
```

### View logs

```bash
docker compose logs ollama
docker compose logs app
```

---
