FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install dependencies in a cached layer before copying source
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Make the venv available without the `uv run` prefix
ENV PATH="/app/.venv/bin:$PATH"

# Pre-download the embedding model so ingestion and startup don't hit the network
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

RUN chmod +x scripts/vault_entrypoint.sh
