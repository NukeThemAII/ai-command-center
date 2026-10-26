# AI Development & Demo Stack — Architecture Overview

*A self-hosted, open-source AI engineering environment for building RAG,
multi-agent, and voice/webhook AI solutions. Public overview — no credentials,
secrets, or internal infrastructure details are included in this document.*

---

## Purpose

A modular, zero-SaaS-cost AI development server used to design, build, and
demonstrate production-grade AI automation:

- **Custom RAG pipelines** — ingest any website into a vector database and
  answer questions grounded in the retrieved content, with cited sources.
- **Stateful multi-agent workflows** — LangGraph-based agents with persistent
  conversation memory, structured outputs, and audit logging.
- **Voice & webhook AI integrations** — token-guarded webhook endpoints
  designed to be triggered by workflow automation (n8n) or voice AI tool-calls.

## Architecture

All services run as Docker containers on a private internal bridge network.
Only loopback-bound ports are published on the host; databases are never
exposed to the internet. All containers run with memory limits and log
rotation (10 MB x 3 files) for predictable resource use.

| Service       | Technology                          | Role                                                |
|---------------|-------------------------------------|-----------------------------------------------------|
| postgres      | PostgreSQL 16 + pgvector            | Vector store (1536-dim embeddings) + audit log DB   |
| redis         | Redis 7 (AOF persistence)           | Agent conversation memory & webhook state           |
| crawl4ai      | Crawl4AI (Playwright-based)         | Website -> clean Markdown extraction for ingestion  |
| agent-api     | Python 3.12, FastAPI, LangGraph, Pydantic AI | Demo API: RAG pipeline + stateful agent webhook |
| n8n           | n8n workflow automation             | Visual orchestration: webhook -> agent -> database  |

## Data flow

**RAG pipeline**

1. `POST /demo/rag-ingest {"url": ...}` — crawl4ai fetches the page as clean
   Markdown; the text is chunked (paragraph-aware, overlapping) and embedded.
2. Embeddings are stored in pgvector (HNSW cosine index).
3. `POST /demo/rag-query` — raw cosine similarity search over stored chunks.
4. `POST /demo/rag-ask` — similarity search, then a chat LLM produces a
   grounded answer citing the retrieved sources by reference number.

**Stateful agent webhook**

1. `POST /demo/agent-webhook {"session_id", "message"}` (Bearer-token guarded).
2. LangGraph graph: load Redis memory -> LLM lead qualification (structured
   output: score, category, urgency, next action, reply) -> persist memory.
3. Each call is audit-logged to Postgres; conversation state persists across
   turns (per `session_id`, 7-day TTL), enabling voice calls or CRM threads.

## LLM provider design

The stack is provider-agnostic and uses **real production LLM calls and real
embeddings exclusively** — there are no mock or fallback modes. Provider keys
(for OpenAI, Anthropic, OpenRouter, or any OpenAI-compatible endpoint) are
supplied via environment configuration; the active chat provider and the
embedding provider are selected independently. Missing or failing credentials
surface as explicit HTTP 503/502 errors — never silent fake data.

Embeddings: 1536-dimension vectors (e.g. `text-embedding-3-small`), matching
the `vector(1536)` schema. The API validates embedding dimensions at write
time and rejects mismatched models with a clear error.

## Security posture

- All service ports bound to `127.0.0.1` on the host; container-to-container
  traffic stays on the private Docker bridge.
- Raw database ports are never published publicly.
- Demo endpoints are guarded by a Bearer API token (401 on missing/invalid).
- The scraper endpoint requires its own API token and refuses unauthenticated
  non-loopback binding by design.
- Credentials live in a single root-restricted environment file (chmod 600),
  never in code or images.

## Operational characteristics

- Idempotent deployment script: build, launch, network attach — re-runnable.
- Live code reload for the agent API (edit -> ~2s hot reload) for fast demo
  iteration; image rebuilds only on dependency changes.
- Verified boot: automated build + readiness verification passes before
  handover.
- Resource caps per container (512 MB – 2 GB RAM) on a modest VPS footprint.
