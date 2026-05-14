import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, ContextualRecallMetric
from deepeval.test_case import LLMTestCase

from src.extensions.rag.service import ask, _get_retriever
from src.extensions.rag.models import AskRequest

QUESTIONS = [
    # (question, expected_output_hint)
    ("What is the break-cost cap specified in clause 4.3(b) of the Lending Policy?",
     "3 times the most recent monthly interest charge"),
    ("What is the establishment fee for an Acme loan product?",
     "$499"),
    ("What action must be taken on day 7 of a hardship case per the Hardship Policy and SLA Handbook?",
     "second reminder"),
    ("What is the AFCA referral procedure for complaints per the Complaints Policy?",
     "AFCA"),
    ("What exact words does Gandalf say in the Silmaril Charter?",
     None),
    ("Where was the One Ring forged according to the Silmaril Charter, and in what year?",
     "Eregion"),
    ("What is the minimum NPS threshold for broker accreditation?",
     None),
    ("What are Acme's business hours and how do they relate to SLA calculations?",
     "08:00"),
    ("What is the cooling-off period for Acme loan agreements?",
     "14 business days"),
    ("What does the NCCP Act s.117 require of credit licensees?",
     None),
]

def _make_test_case(question: str, expected: str | None) -> LLMTestCase:
    chunks, _ = _get_retriever().query(question)
    context = [c["text"] for c in chunks]
    response = ask(AskRequest(question=question))
    return LLMTestCase(
        input=question,
        actual_output=response.answer,
        expected_output=expected or response.answer,
        retrieval_context=context,
    )


@pytest.mark.parametrize("question,expected", QUESTIONS)
def test_rag_question(question: str, expected: str | None):
    test_case = _make_test_case(question, expected)
    assert_test(test_case, [
        AnswerRelevancyMetric(threshold=0.7),
        FaithfulnessMetric(threshold=0.7),
        ContextualRecallMetric(threshold=0.5),
    ])
