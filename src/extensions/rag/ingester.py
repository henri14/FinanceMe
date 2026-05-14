import re
from pathlib import Path

import lancedb
import pyarrow as pa
from sentence_transformers import SentenceTransformer

CORPUS_DIR = Path(__file__).resolve().parents[3] / "corpus"
DB_PATH = str(Path(__file__).resolve().parents[3] / "data" / "lancedb")
TABLE_NAME = "chunks"
MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64
MIN_CHUNK_CHARS = 50
MAX_CHUNK_CHARS = 500


def _parse_frontmatter(lines: list[str]) -> dict:
    meta = {"doc_id": "", "title": ""}
    for line in lines[:10]:
        if line.startswith("# "):
            meta["title"] = line[2:].strip()
        m = re.match(r"\*\*Document ID:\*\*\s*(.+)", line)
        if m:
            meta["doc_id"] = m.group(1).strip()
    return meta


def _chunk_document(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    meta = _parse_frontmatter(lines)

    chunks = []
    current_h2 = ""
    current_h3 = ""
    current_lines: list[str] = []

    def flush(h2: str, h3: str, body_lines: list[str]):
        body = "\n".join(body_lines).strip()[:MAX_CHUNK_CHARS]
        if len(body) >= MIN_CHUNK_CHARS:
            heading = " > ".join(filter(None, [meta["title"], h2, h3]))
            text = f"{heading}\n\n{body}" if heading else body
            chunks.append({
                "doc_id": meta["doc_id"],
                "title": meta["title"],
                "section": h2,
                "subsection": h3,
                "text": text,
                "source_file": path.name,
            })

    for line in lines:
        if line.startswith("## "):
            flush(current_h2, current_h3, current_lines)
            current_h2 = line[3:].strip()
            current_h3 = ""
            current_lines = []
        elif line.startswith("### "):
            flush(current_h2, current_h3, current_lines)
            current_h3 = line[4:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    flush(current_h2, current_h3, current_lines)
    return chunks


def ingest(corpus_dir: Path = CORPUS_DIR, db_path: str = DB_PATH, reset: bool = False):
    model = SentenceTransformer(MODEL_NAME)

    all_chunks: list[dict] = []
    for md_file in sorted(corpus_dir.glob("*.md")):
        all_chunks.extend(_chunk_document(md_file))

    print(f"Parsed {len(all_chunks)} chunks from {corpus_dir}")

    texts = [c["text"] for c in all_chunks]
    vectors = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        vectors.extend(model.encode(batch, normalize_embeddings=True).tolist())
        print(f"  Embedded {min(i + BATCH_SIZE, len(texts))}/{len(texts)}")

    schema = pa.schema([
        pa.field("doc_id", pa.string()),
        pa.field("title", pa.string()),
        pa.field("section", pa.string()),
        pa.field("subsection", pa.string()),
        pa.field("text", pa.string()),
        pa.field("source_file", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 384)),
    ])

    db = lancedb.connect(db_path)
    if reset and TABLE_NAME in db.table_names():
        db.drop_table(TABLE_NAME)

    rows = [{**c, "vector": v} for c, v in zip(all_chunks, vectors)]

    if TABLE_NAME in db.table_names():
        db.open_table(TABLE_NAME).add(rows)
    else:
        db.create_table(TABLE_NAME, data=rows, schema=schema)

    print(f"Ingested {len(rows)} chunks into LanceDB at {db_path}")
