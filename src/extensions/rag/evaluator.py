import asyncio
import json
from pathlib import Path

import pytest
from openai import OpenAI
from ragas.metrics.collections import RougeScore

from src.core.config import load_config
from src.extensions.rag.models import AskRequest
from src.extensions.rag.service import _get_retriever, ask

_QUESTIONS_FILE = Path(__file__).parent / "eval_questions.json"
_raw = json.loads(_QUESTIONS_FILE.read_text())
QUESTIONS = [(q["id"], q["question"], q["expected"]) for q in _raw]

_rouge = RougeScore(rouge_type="rougeL", mode="recall")


async def _max_context_rouge(expected: str, contexts: list[str]) -> float:
    results = await asyncio.gather(*[
        _rouge.ascore(reference=expected, response=ctx) for ctx in contexts
    ])
    return max(r.value for r in results)


def _score_answer(answer: str, expected: str | None) -> int:
    """Return 1 (pass) or 0 (fail). Non-empty answer passes when expected is None."""
    if not answer.strip():
        return 0
    if expected is None:
        return 1
    result = asyncio.run(_rouge.ascore(reference=expected, response=answer))
    return 1 if result.value >= 0.5 else 0


def run_evaluation() -> list[dict]:
    """Run each question against both the RAG service and the LLM alone.

    Returns a list of dicts with keys: id, question, llm_score, rag_score.
    """
    config = load_config()
    client = OpenAI(api_key=config.api_key)
    retriever = _get_retriever()
    results = []

    for qid, question, expected in QUESTIONS:
        # RAG path: retrieval + grounded generation via the vault service
        rag_response = ask(AskRequest(question=question))
        rag_score = _score_answer(rag_response.answer, expected)

        # LLM-only path: direct call with no retrieval context
        completion = client.chat.completions.create(
            model=config.model,
            messages=[{"role": "user", "content": question}],
            temperature=0,
        )
        llm_answer = completion.choices[0].message.content.strip()
        llm_score = _score_answer(llm_answer, expected)

        results.append({
            "id": qid,
            "question": question,
            "llm_score": llm_score,
            "rag_score": rag_score,
        })

    return results


@pytest.mark.parametrize("qid,question,expected", QUESTIONS, ids=[str(q["id"]) for q in _raw])
def test_rag_question(qid: int, question: str, expected: str | None):
    chunks, retrieval_ms = _get_retriever().query(question)
    response = ask(AskRequest(question=question))
    contexts = [c["text"] for c in chunks]

    assert contexts, "Retrieval returned no chunks"
    assert response.answer.strip(), "Answer is empty"
    assert retrieval_ms < 300, f"Retrieval exceeded 300ms target: {retrieval_ms:.0f}ms"

    if expected is not None:
        # Retrieval quality: expected info present in at least one retrieved chunk (no LLM)
        ctx_score = asyncio.run(_max_context_rouge(expected, contexts))
        assert ctx_score >= 0.3, (
            f"Expected info not found in retrieved context "
            f"(max ROUGE-L recall={ctx_score:.2f}). Expected: '{expected}'"
        )

        # Answer quality: response contains the expected information (no LLM)
        ans_result = asyncio.run(_rouge.ascore(reference=expected, response=response.answer))
        assert ans_result.value >= 0.5, (
            f"Answer doesn't sufficiently contain expected info "
            f"(ROUGE-L recall={ans_result.value:.2f}). Expected: '{expected}'"
        )
