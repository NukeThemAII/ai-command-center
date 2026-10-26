# Upwork Portfolio Item — Polyglot AI Stack

**Title:** Polyglot AI Automation Stack — RAG, Stateful LLM Agents & Deterministic Risk Gating

**Role:** Sole engineer — architecture, backend (Python + TypeScript), data layer, orchestration, infra, observability

**Skills:** Python, TypeScript, FastAPI, LangGraph, Pydantic AI, PostgreSQL, pgvector, Redis, Docker, n8n, RAG, LLM integration, API design, monitoring

---

## Summary (~150 words)

Designed and shipped a production-grade AI automation platform in a polyglot
architecture: a Python FastAPI + LangGraph service running stateful LLM agents
with persistent conversation memory, a pgvector RAG pipeline that turns any
website into a cited, grounded knowledge base, and a TypeScript decision engine
that enforces deterministic risk and policy gates — with an optional TypeSafe
"System One" probabilistic decision-model overlay under strict validation.
Workflow automation (n8n) fans out inbound webhooks through the full chain into
an immutable audit store. Everything runs as six memory-capped Docker containers
on an isolated bridge network, with live telemetry dashboards, rate-limited and
token-guarded public endpoints, and provider-resilient LLM routing. Built live
end-to-end in one session, verified with real traffic — measured, not mocked.

## Metrics (real, measured live)

- **548 ms** decision-model latency (3-question fan-out, TypeSafe Jev 1.13)
- **$0.0000213** per model decision (provider-billed `usage.cost`)
- **1536-dim** embeddings, HNSW cosine index in pgvector
- **< 25 ms** deterministic risk gate (in-network, zero external calls)
- **6-container** Docker topology: n8n · FastAPI/LangGraph · TypeScript gate ·
  Postgres/pgvector · Redis (AOF) · crawl4ai
- **5 req/s** edge rate limiting on AI endpoints; loopback-only databases
- Live public status page + interactive demo dashboard with per-hop latency
  animation of the real pipeline

## Highlights for proposals

- Explainable risk decisions: documented additive risk model → score, per-gate
  pass/fail, machine-readable reason codes — no black-box gating.
- Fail-open engineering: model overlay can never block or fabricate; the
  deterministic layer stays the authority.
- Cost discipline: sub-cent-per-call decision modeling; free-tier-friendly stack.
- Security posture: single root-restricted secrets file, Bearer + basic auth,
  rate limiting, sanitized public surfaces.

**Live demo available on request** (interactive dashboard + public case-study page).
