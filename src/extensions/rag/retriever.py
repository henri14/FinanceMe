import time
from pathlib import Path

import lancedb
from sentence_transformers import SentenceTransformer

DB_PATH = str(Path(__file__).resolve().parents[3] / "data" / "lancedb")
TABLE_NAME = "chunks"
MODEL_NAME = "all-MiniLM-L6-v2"


class Retriever:
    def __init__(self, db_path: str = DB_PATH, top_k: int = 30):
        self.top_k = top_k
        self._model = SentenceTransformer(MODEL_NAME)
        db = lancedb.connect(db_path)
        self._table = db.open_table(TABLE_NAME)

    def query(self, question: str) -> tuple[list[dict], float]:
        start = time.perf_counter()
        vec = self._model.encode(question, normalize_embeddings=True).tolist()
        results = (
            self._table.search(vec)
            .metric("cosine")
            .limit(self.top_k)
            .to_list()
        )
        latency_ms = (time.perf_counter() - start) * 1000
        return results, latency_ms
