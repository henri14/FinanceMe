# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

This project uses [uv](https://github.com/astral-sh/uv) for dependency and environment management.

```bash
# Install dependencies
uv sync

# Run the chat client
uv run python src/cli.py chat

# Run all tests
uv run pytest

# Run a single test
uv run pytest tests/path/to/test_file.py::test_name
```

## Architecture

The project is a modular LLM chat client, structured for incremental extension (RAG, tool calling, evaluation).

**Chat flow** (`src/core/client.py`): `ChatClient.start_chat()` reads user input → fetches recent history from SQLite → calls the OpenAI Responses API (`client.responses.create`) → streams the reply → passes `usage` to `MetricsCollector` and saves both turns to the DB.

**OpenAI API**: Uses the Responses API (`client.responses.create`), not the older Chat Completions API. Token fields are `usage.input_tokens` / `usage.output_tokens` (not `prompt_tokens` / `completion_tokens`).

**Persistence** (`src/storage/db.py`): SQLite via `data/chat_history.db`. `get_last_turns(n)` returns the last *n* messages oldest-first, used to build the context window for each request.

**Metrics** (`src/core/metrics.py`): Each turn is logged as a text line (loguru) and appended as a JSON record to `data/metrics.jsonl`.

**Configuration** (`config/config.yaml` + `src/core/config.py`): Pydantic model loaded from YAML; `api_key` is resolved from environment variables via `os.path.expandvars`. The active model is `gpt-4o-mini`.

**Extensions** (`src/extensions/`): Stub packages for `rag/`, `tools/`, and `evaluation/` — the intended home for future features.

**RAG corpus**: Markdown source documents live in `corpus/`. The planned RAG service ("The Vault") will use LanceDB as the vector store, FastAPI for the API (`/ask`, `/metrics`), and DeepEval for evaluation.

**Token cost rates** (`client.py:_estimate_cost`): Hardcoded for `gpt-4o-mini` ($0.00000015/input token, $0.00000060/output token). Must be updated manually if the model changes.
