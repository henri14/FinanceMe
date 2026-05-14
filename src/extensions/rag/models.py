from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str


class Citation(BaseModel):
    doc_id: str
    section: str
    subsection: str
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    retrieval_ms: float
