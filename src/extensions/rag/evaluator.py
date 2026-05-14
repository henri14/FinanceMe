import asyncio

import pytest
from ragas.metrics.collections import RougeScore

from src.extensions.rag.models import AskRequest
from src.extensions.rag.service import _get_retriever, ask

QUESTIONS = [
    ("What is the break-cost cap specified in clause 4.3(b) of the Lending Policy?",
     "3 times the most recent monthly interest charge"),
    ("What is the establishment fee for an Acme loan product?",
     "$499"),
    ("What action must be taken on day 7 of a hardship case per the Hardship Policy and SLA Handbook?",
     "second reminder"),
    ("What is the AFCA referral procedure for complaints per the Complaints Policy?",
     "AFCA"),
    ("What exact words does Gandalf say in the Silmaril Charter?", None),
    ("Where was the One Ring forged according to the Silmaril Charter, and in what year?",
     "Eregion"),
    ("What is the minimum NPS threshold for broker accreditation?", None),
    ("What are Acme's business hours and how do they relate to SLA calculations?",
     "08:00"),
    ("What is the cooling-off period for Acme loan agreements?",
     "14 business days"),
    ("What does the NCCP Act s.117 require of credit licensees?", None),
]

_rouge = RougeScore(rouge_type="rougeL", mode="recall")


async def _max_context_rouge(expected: str, contexts: list[str]) -> float:
    results = await asyncio.gather(*[
        _rouge.ascore(reference=expected, response=ctx) for ctx in contexts
    ])
    return max(r.value for r in results)


@pytest.mark.parametrize("question,expected", QUESTIONS)
def test_rag_question(question: str, expected: str | None):
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
