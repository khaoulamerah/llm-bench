import argparse
import json
import os
import sys
import time
from datetime import datetime

import pandas as pd

from config import MODELS_TO_TEST, DATA_DIR, RESULTS_DIR, LANGUAGES
from ollama_client import is_model_available, OllamaError
from tasks.sentiment import run_sentiment
from tasks.summarize import run_summary


def load_articles(lang: str) -> list:
    path = os.path.join(DATA_DIR, f"articles_{lang}.json")
    if not os.path.exists(path):
        print(f"[!] Fichier manquant, ignore : {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        articles = json.load(f)
    for a in articles:
        a["lang"] = lang
    return articles


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="*", default=None)
    parser.add_argument("--task", choices=["sentiment", "summarize", "both"], default="both")
    parser.add_argument("--langs", nargs="*", default=LANGUAGES)
    args = parser.parse_args()

    models = MODELS_TO_TEST
    if args.models:
        models = [m for m in MODELS_TO_TEST if m["name"] in args.models]
        if not models:
            print(f"Aucun modele connu parmi {args.models}. Verifie config.py")
            sys.exit(1)

    all_articles = []
    for lang in args.langs:
        all_articles.extend(load_articles(lang))

    if not all_articles:
        print("Aucun article trouve dans data/articles/. Remplis les fichiers JSON d'abord.")
        sys.exit(1)

    print(f"=== Benchmark : {len(models)} modele(s) x {len(all_articles)} article(s) ===\n")

    rows = []
    for model_cfg in models:
        model_name = model_cfg["name"]
        print(f"--- Modele : {model_name} ---")

        try:
            if not is_model_available(model_name):
                print(f"  [!] {model_name} n'est pas telecharge. "
                      f"Lance : docker compose exec ollama ollama pull {model_name}")
                continue
        except OllamaError as e:
            print(f"  [!] Ollama injoignable : {e}")
            sys.exit(1)

        for article in all_articles:
            label = article.get("id", "?")

            if args.task in ("sentiment", "both"):
                t0 = time.perf_counter()
                row = run_sentiment(model_name, article)
                print(f"  [sentiment] {label} ({article['lang']}) "
                      f"-> {row.get('predicted_label', row.get('error'))} "
                      f"({time.perf_counter() - t0:.1f}s)")
                rows.append(row)

            if args.task in ("summarize", "both"):
                t0 = time.perf_counter()
                row = run_summary(model_name, article)
                status = "ok" if row["status"] == "ok" else row.get("error")
                print(f"  [summarize] {label} ({article['lang']}) "
                      f"-> {status} ({time.perf_counter() - t0:.1f}s)")
                rows.append(row)

        print()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(RESULTS_DIR, f"raw_results_{timestamp}.csv")
    pd.DataFrame(rows).to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\nResultats bruts ecrits dans : {out_path}")
    print("Lance ensuite : python results_report.py", os.path.basename(out_path))


if __name__ == "__main__":
    main()
