from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from openai import OpenAI
from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

from src.core.config import load_config, Config
from src.extensions.rag.models import AskRequest, AskResponse, Citation
from src.extensions.rag.retriever import Retriever

app = FastAPI(title="The Vault — RAG Service")

_registry = CollectorRegistry()
_retrieval_latency = Histogram(
    "rag_retrieval_latency_ms",
    "Retrieval latency in milliseconds",
    buckets=[10, 25, 50, 100, 200, 300, 500, 1000],
    registry=_registry,
)
_requests_total = Counter("rag_requests_total", "Total /ask requests", registry=_registry)
_input_chars_total = Counter("rag_input_chars_total", "Total input characters", registry=_registry)
_response_chars_total = Counter("rag_response_chars_total", "Total response characters", registry=_registry)

_retriever: Retriever | None = None
_openai: OpenAI | None = None
_config: Config | None = None


def _get_config() -> Config:
    global _config
    if _config is None:
        _config = load_config()
    return _config


def _get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def _get_openai() -> OpenAI:
    global _openai
    if _openai is None:
        import os
        _openai = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _openai


@app.on_event("startup")
def _startup():
    _get_config()
    _get_retriever()
    _get_openai()


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    chunks, retrieval_ms = _get_retriever().query(req.question)
    _retrieval_latency.observe(retrieval_ms)
    _requests_total.inc()
    _input_chars_total.inc(len(req.question))

    context_blocks = "\n\n".join(
        f"[{i + 1}] ({c['doc_id']} — {c['section']} / {c['subsection']})\n{c['text']}"
        for i, c in enumerate(chunks)
    )
    system_prompt = (
        "You are a helpful assistant. Answer the question using only the numbered context "
        "blocks below. Cite sources inline as [1], [2], etc. If the answer is not in the "
        "context, say so.\n\n"
        f"{context_blocks}"
    )

    completion = _get_openai().chat.completions.create(
        model=_get_config().model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.question},
        ],
        temperature=0,
    )
    answer = completion.choices[0].message.content.strip()
    _response_chars_total.inc(len(answer))

    citations = [
        Citation(
            doc_id=c["doc_id"],
            section=c["section"],
            subsection=c["subsection"],
            excerpt=c["text"][:200],
        )
        for c in chunks
    ]

    return AskResponse(answer=answer, citations=citations, retrieval_ms=retrieval_ms)


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return PlainTextResponse(
        generate_latest(_registry).decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST,
    )
