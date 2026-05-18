# Acme FinanceMe — AI Demo

A hands-on demonstration of three progressively more capable AI related tasks.
- a plain chat client
- a Retrieval-Augmented Generation (RAG) service grounded in real policy documents
- an autonomous Operations Copilot agent.

These use the OpenAI API. All three run together via Docker Compose and are accessible
through a single interactive menu.

---

## The Three Missions

### Mission 1 — Simple Chat Client
An interactive terminal chat session backed by `gpt-4o-mini`.
Conversation history is persisted to SQLite and each turn is augmented with policy context
retrieved from the Vault RAG service. Token usage, cost (USD), and latency are logged on
every turn.

### Mission 2 — RAG Evaluation
Runs policy questions through the vanilla LLM and the RAG enabled LLM and scores each answer 1 (pass) or 0 (fail):

| Path | What it does |
|---|---|
| **Raw LLM** | Sends the question directly to the model with no context |
| **RAG** | Retrieves relevant chunks from the Vault and passes them to the model |

A summary table is printed at the end showing how many questions each path answered correctly,
demonstrating the accuracy uplift from retrieval.

### Mission 3 — Operations Agent Tests
Runs loan-application scenarios through the Operations Copilot — an agentic loop that calls
three tools (CRM lookup, policy search via the Vault, calendar slot booking) and produces a
structured action plan. Each scenario is checked for the expected outcome (plan generated or
requires human intervention) and reported as PASS / FAIL.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| **Docker** | Docker Engine 24+ or Docker Desktop |
| **Docker Compose** | Included with Docker Desktop; v2.20+ for standalone installs |
| **OpenAI API key** | Must have access to `gpt-4o-mini` |

### Providing your OpenAI API key

Either export it in your shell before running any `docker compose` command:

```bash
export OPENAI_API_KEY=sk-...
```

Or create a `.env` file in the project root:

```
OPENAI_API_KEY=sk-...
```

Docker Compose will pick up the `.env` file automatically.

---

## Running the demo

### 1. Build the images

```bash
docker compose build
```

This step downloads dependencies and pre-caches the embedding model (~500 MB on first run).
Subsequent builds are fast thanks to Docker layer caching.

### 2. Start the platform services

```bash
docker compose up vault prometheus -d
```

The `vault` service ingests the policy corpus into a local vector store on first start
(this takes about a minute). It becomes healthy once the `/metrics` endpoint responds.
Prometheus begins scraping RAG metrics automatically once the vault is healthy.

### 3. Launch the menu

```bash
docker compose run --rm menu
```

The interactive menu appears in your terminal:

```
╔══════════════════════════════════════════╗
║      Acme FinanceMe — AI Demo  v1        ║
╚══════════════════════════════════════════╝

  Prometheus metrics: http://localhost:9090

  0)  Check prerequisites
  1)  Mission 1 — Simple chat client
  2)  Mission 2 — RAG evaluation
  3)  Mission 3 — Operations Agent tests
  q)  Quit
```

Select **0** first to confirm your API key is recognised and the Vault is reachable,
then work through the missions in order.

### Stopping everything

```bash
docker compose down
```

The vector store is persisted in `./data/lancedb` so ingestion does not repeat on the next run.

---

## Observability

Prometheus scrapes the Vault's `/metrics` endpoint every 15 seconds.
Open **http://localhost:9090** in a browser while the platform is running to query metrics such as
`rag_requests_total`, `rag_retrieval_latency_ms`, and `rag_response_chars_total`.


---

## Project structure

```
.
├── corpus/                          # Policy & regulatory source documents (RAG input)
├── config/
│   └── config.yaml                  # Model name, RAG toggle, conversation window size
├── data/                            # Runtime data — created automatically, git-ignored
│   ├── lancedb/                     # Vector store (populated on first vault start)
│   ├── chat_history.db              # SQLite conversation history
│   ├── metrics.jsonl                # Per-turn token / cost / latency log
│   └── copilot_traces.jsonl         # Copilot agent step-by-step reasoning traces
├── eval/
│   └── run.py                       # Mission 2: LLM-vs-RAG comparison runner
├── scripts/
│   ├── ingest_corpus.py             # Chunks and embeds corpus into LanceDB
│   └── vault_entrypoint.sh          # Docker entrypoint: ingest if needed, then serve
├── src/
│   ├── cli.py                       # Typer CLI — exposes `chat` and `copilot` commands
│   ├── core/
│   │   ├── client.py                # Chat loop: RAG context injection, copilot routing
│   │   ├── config.py                # Pydantic settings loaded from config.yaml
│   │   └── metrics.py               # Token / cost / latency collector
│   ├── extensions/
│   │   ├── rag/
│   │   │   ├── service.py           # FastAPI vault service — /ask and /metrics endpoints
│   │   │   ├── retriever.py         # LanceDB cosine-similarity search
│   │   │   ├── ingester.py          # Markdown chunker and sentence-transformer embedder
│   │   │   ├── evaluator.py         # RAGAS-based pytest evaluator
│   │   │   └── eval_questions.json  # Evaluation question bank (category, expected answer)
│   │   └── tools/
│   │       ├── agent.py             # CopilotAgent — agentic loop and structured output
│   │       ├── models.py            # AgentPlan output schema
│   │       └── tool_schemas.py      # OpenAI function-calling tool definitions
│   ├── storage/
│   │   └── db.py                    # SQLite conversation store
│   └── tools/
│       ├── crm.py                   # Mock CRM with sample loan applications
│       └── calendar_tool.py         # Mock calendar — next available business slot
├── Dockerfile
├── docker-compose.yml               # vault · prometheus · chat · copilot · menu services
├── menu.sh                          # Interactive mission launcher (runs inside container)
├── prometheus.yml
└── pyproject.toml
```
