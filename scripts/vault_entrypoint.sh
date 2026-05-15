#!/bin/bash
set -e

if [ ! -d "/app/data/lancedb" ]; then
    echo "LanceDB not found — ingesting corpus..."
    python scripts/ingest_corpus.py
    echo "Ingestion complete."
fi

exec uvicorn src.extensions.rag.service:app --host 0.0.0.0 --port 8000
