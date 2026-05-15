#!/usr/bin/env python
"""Compare RAG vs raw-LLM answer quality across all evaluation questions.

Requires the vault RAG service to be running:
    uv run uvicorn src.extensions.rag.service:app --port 8000
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.extensions.rag.evaluator import run_evaluation

_Q_WIDTH = 60
_SEP = "-" * (_Q_WIDTH + 22)


def _trunc(text: str) -> str:
    return text if len(text) <= _Q_WIDTH else text[: _Q_WIDTH - 3] + "..."


def main() -> None:
    print("Running evaluation (vault must be running on localhost:8000) …")
    results = run_evaluation()

    print()
    print(f"{'Question':<{_Q_WIDTH}}  {'Raw LLM':>7}  {'RAG':>7}")
    print(_SEP)
    for r in results:
        print(f"{_trunc(r['question']):<{_Q_WIDTH}}  {r['llm_score']:>7}  {r['rag_score']:>7}")
    print(_SEP)

    n = len(results)
    llm_total = sum(r["llm_score"] for r in results)
    rag_total = sum(r["rag_score"] for r in results)
    print(f"{'TOTAL':<{_Q_WIDTH}}  {f'{llm_total}/{n}':>7}  {f'{rag_total}/{n}':>7}")


if __name__ == "__main__":
    main()
