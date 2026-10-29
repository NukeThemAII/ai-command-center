# Adaptive Systems stack — public architecture overview

*Public overview: no credentials, keys or internal host details.*

## Purpose

One self-hosted engine that a business configures instead of commissioning: support answers from its
own documents and facts, appointment booking, an AI voice receptionist and lead scoring — any subset,
enabled per client.

## Request flow

**Support question** (chat, voice or API)
1. The caller is resolved to exactly one client (per-client key or voice secret, never from a model).
2. The question is split into at most three parts.
3. Each part is answered from the client's profile facts when it asks for a hard fact (hours,
   holidays, prices of a named service, address, contact, policies), otherwise by retrieval over that
   client's active document chunks (minimum similarity, citations).
4. Refused when nothing relevant is found, when the question is an injection attempt, or when the
   drafted answer contains a price, time, phone number or email that is not in the retrieved context.

**Booking** — slots come from the profile's hours, holidays and service durations; a taken slot
returns three alternatives; cancellations are soft (the row is kept, the status changes).

**Voice** — an ElevenLabs agent per client, generated from its config: the prompt, a facts document,
five webhook tools (facts, knowledge base, availability, book, cancel) and a signed post-call webhook
that stores each call per client (and scores it when the client has lead scoring).

**Lead** — webhook → n8n → LLM sub-scores (fit, budget clarity, urgency, authority, scope clarity)
with evidence quotes → deterministic extractors (budget, timeline, spam/injection) → TypeScript policy
gate → route + reply → audit log → alert. If every model misses its deadline the lead still gets the
deterministic checks and goes to human review.

## Services

| Service | Technology | Role |
|---|---|---|
| agent-api | Python 3.12, FastAPI, LangGraph, Pydantic AI | engine: config, support, booking, voice tools, qualification |
| policy gate | TypeScript, Node 22 | deterministic gate + optional TypeSafe Jev overlay |
| n8n | workflow automation | lead orchestration and alerts |
| postgres | PostgreSQL 16 + pgvector | vectors, audit log, bookings, calls (`client_id` on every row) |
| redis | Redis 7 (AOF) | session memory, rate limits |
| crawl4ai | Playwright-based crawler | admin document ingestion |
| app | Next.js 16 | private mission-control UI |
| uptime-kuma | monitoring | public status page |

## Security posture

- Databases and internal services bound to loopback; containers on a private bridge network.
- Per-endpoint routing at the edge: the public API host serves only machine endpoints; the app host
  requires authentication; per-visitor and global rate limits on anything that calls a model.
- Keys are stored as hashes; secrets live in one root-only environment file, never in code or images.
- Public URL ingestion is SSRF-safe (every address and redirect hop checked, connection pinned).
- Public statistics are sanitized: no personal data, no costs, test traffic excluded.

## Operations

- Docker Compose with health checks; every service is set to restart on its own after a reboot.
- Nightly database backups.
- Uptime Kuma monitors every service and the public hosts.
- Static, per-client, voice and app test suites plus a live smoke set run after every change.
