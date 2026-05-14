# LLM Chat Client Implementation Plan

Based on the instructions in `instructions.md`, I'll outline a comprehensive plan for implementing the LLM chat client. This includes core requirements (OpenAI API integration, configurable model, streaming responses, metrics collection, and modular structure) while incorporating the additional features you mentioned (persistent store for chat interactions, retrieval augmented generation (RAG), tool calling, and evaluation). I'll recommend frameworks/libraries tailored to Python 3.11 compatibility, focusing on simplicity, extensibility, and performance.

## 1. Overview of the Plan
The chat client will be a command-line application (CLI) that interacts with OpenAI's API to generate responses. It will support real-time streaming, collect detailed telemetry (tokens, cost, latency), and store data persistently. Future extensions (RAG, tool calling, evaluation) will be modular, allowing incremental development without disrupting the core.

Key principles:
- **Modularity**: Use a layered architecture (e.g., core logic, storage, extensions) to enable easy additions.
- **Asynchronous**: Leverage async I/O for streaming and non-blocking operations.
- **Configurability**: Model selection, API keys, and settings via a config file.
- **Error Handling**: Robust handling of API errors, rate limits, and timeouts.
- **Testing**: Unit tests for core components, integration tests for API interactions.
- **Deployment**: Containerizable (e.g., Docker) for easy distribution.

Estimated timeline: 4-6 weeks for MVP (core + metrics), plus 2-4 weeks per extension.

## 2. Recommended Frameworks and Libraries
I'll recommend lightweight, well-maintained libraries that align with Python 3.11. These prioritize simplicity for a CLI app while supporting advanced features.

### Core Dependencies
- **openai** (v1.x): Official OpenAI Python client for API interactions, streaming, and tool calling. Handles authentication, retries, and rate limiting out-of-the-box.
- **asyncio** (built-in): For asynchronous streaming and concurrent tasks (e.g., metrics emission while chatting).
- **pydantic** (v2.x): For data validation, configuration management, and type-safe models (e.g., chat messages, metrics).
- **typer** (v0.x): For building the CLI interface (easier than argparse, with auto-completion).
- **loguru** (v0.x): For structured logging and metrics emission (supports JSON and text formats).

### Persistent Store
- **sqlite3** (built-in): Lightweight, file-based database for chat history. No server needed; embeddable.

### Retrieval Augmented Generation (RAG)
- **langchain** (v0.x): High-level framework for RAG pipelines, including vector stores, embeddings, and retrieval. Integrates well with OpenAI.
- **chromadb** (v0.x): Vector database for storing and querying embeddings (fast, local, and scalable).
- **sentence-transformers** (v2.x): For generating embeddings from text (e.g., chat history or documents).

### Tool Calling
- **openai** (built-in support): OpenAI's API natively supports tool calling (e.g., function definitions). We'll define tools as Python functions and integrate them into prompts.

### Evaluation
- **deepeval** (v0.x): For evaluating LLM outputs (e.g., relevance, accuracy, hallucinations). Supports custom metrics and integrates with LangChain.
- **pytest** (built-in ecosystem): For unit testing and evaluation scripts.

### Additional Utilities
- **python-dotenv** (v0.x): For loading API keys from environment variables.
- **aiofiles** (v0.x): For async file I/O (e.g., streaming metrics to JSON files).
- **uvloop** (v0.x): Optional performance boost for asyncio on Linux.

Install via `uv` for dependency management and virtual environment (already activated in your terminal). Use `pyproject.toml` for pinning versions.

## 3. Architecture and Design
- **Layers**:
  - **CLI Layer**: Handles user input/output via Typer.
  - **Core Layer**: Manages OpenAI API calls, streaming, and metrics collection.
  - **Storage Layer**: Persistent store for chats (SQLite).
  - **Extensions Layer**: Pluggable modules for RAG, tool calling, and evaluation.
- **Data Flow**:
  1. User inputs a message via CLI.
  2. Core fetches relevant context (from persistent store or RAG if enabled).
  3. Sends prompt to OpenAI with optional tools.
  4. Streams response, collects metrics, and emits them.
  5. Stores interaction in database.
  6. (Optional) Evaluates response quality.
- **Configuration**: Use a `config.yaml` or Pydantic model for settings (e.g., model name, API key, vector store path).
- **Metrics Handling**: Track in-memory during session; emit to console (text) and file (JSON) asynchronously.

## 4. Implementation Steps
Break into phases for iterative development.

### Phase 1: Core Chat Client (1-2 weeks)
1. Set up project structure (see below).
2. Implement CLI with Typer: Commands for starting chat, configuring model.
3. Integrate OpenAI: Async client for non-streaming calls initially; add streaming later.
4. Add metrics collection: Use OpenAI's usage data for tokens/cost; time requests for latency.
5. Emit metrics: Text to stdout, JSON to file (e.g., `metrics.jsonl`).
6. Add basic persistence to store the last 10 turns in SQLite.
7. Basic error handling and logging.

### Phase 2: Persistence and Streaming (1 week)
1. Add SQLite store: Tables for chats, messages, metrics.
2. Implement async DB operations with SQLAlchemy.
3. Enable response streaming: Update CLI to display chunks in real-time.
4. Store full interactions post-stream.

### Phase 3: RAG Integration (1-2 weeks)
1. Add vector store (ChromaDB) for chat history/documents.
2. Implement embedding generation and retrieval.
3. Modify core to augment prompts with retrieved context.
4. CLI option to enable/disable RAG.

### Phase 4: Tool Calling and Evaluation (1-2 weeks)
1. Define tools as Python functions (e.g., calculator, web search).
2. Integrate with OpenAI API for tool calls in prompts.
3. Add evaluation: Post-response analysis with DeepEval; store scores in DB.
4. CLI commands for running evaluations.

### Phase 5: Testing and Polish (1 week)
1. Write unit/integration tests with pytest.
2. Add Docker support for deployment.
3. Documentation and README.

## 5. Folder Structure
Keep it modular for extensions:

```
ai_chat_client/
├── src/
│   ├── __init__.py
│   ├── cli.py              # Typer CLI entry point
│   ├── core/               # Core logic
│   │   ├── __init__.py
│   │   ├── client.py       # OpenAI client wrapper
│   │   ├── metrics.py      # Metrics collection/emission
│   │   └── streaming.py    # Streaming utilities
│   ├── storage/            # Persistence
│   │   ├── __init__.py
│   │   ├── db.py           # SQLite setup
│   │   └── models.py       # DB models (chats, messages)
│   └── extensions/         # Pluggable features
│       ├── __init__.py
│       ├── rag/            # RAG module
│       │   ├── __init__.py
│       │   ├── vector_store.py
│       │   └── retriever.py
│       ├── tools/          # Tool calling
│       │   ├── __init__.py
│       │   └── tool_registry.py
│       └── evaluation/     # Evaluation
│           ├── __init__.py
│           └── evaluator.py
├── tests/                  # Unit/integration tests
├── config/                 # Config files (e.g., config.yaml)
├── data/                   # DB files, vector stores
├── pyproject.toml          # Dependencies and project metadata
├── Dockerfile              # Containerization
└── README.md               # Usage docs
```

## 6. Future Extensions and Considerations
- **Scalability**: Switch to PostgreSQL for multi-user support.
- **UI**: Add a web interface (e.g., with FastAPI + React) later.
- **Security**: Encrypt API keys; add authentication.
- **Cost Optimization**: Cache embeddings; implement token limits.
- **Evaluation Metrics**: Expand to include user feedback loops.
- **Deployment**: Use GitHub Actions for CI/CD; deploy to cloud (e.g., AWS Lambda for serverless).

This plan ensures a solid foundation while keeping extensions modular. If you proceed, I can help implement specific parts or refine based on feedback. Let me know if you'd like to start with the project setup!