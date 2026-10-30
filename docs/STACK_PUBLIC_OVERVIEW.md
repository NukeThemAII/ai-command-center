# Adaptive Systems stack — public architecture overview

*Public overview: no credentials, keys or internal host details.*

## Purpose

One self-hosted engine that a business configures instead of commissioning: support answers from its
own documents and facts, appointment booking into its own calendar, an AI voice receptionist, a website
chat widget (with a call button), contact-form capture, confirmation emails and lead scoring — any
subset, enabled per client.

## Request flow

**Support question** (chat, voice or API)
1. The caller is resolved to exactly one client (per-client key or voice secret, never from a model).
2. The question is split into at most three parts.
3. Each part is answered from the client's profile facts when it asks for a hard fact (hours,
   holidays, prices of a named service, address, contact, policies), otherwise by retrieval over that
   client's active document chunks (minimum similarity, citations).
4. Refused when nothing relevant is found, when the question is an injection attempt, or when the
   drafted answer contains a price, time, phone number or email that is not in the retrieved context.

**Booking** — slots come from the profile's hours, holidays and service durations, minus busy time in
the business's Google Calendar; each booking is written there as an event; a taken slot returns three
alternatives; cancellations are soft (the row is kept, the status changes). If the calendar can't be
reached nothing is booked and the caller is told so (never "no free times"). Customers get a
confirmation and a cancellation email.

**Website chat** — one script tag. A publishable key plus the page's origin pick the business. Code
handles what it can without a model (injection refusal, yes/no on a booking summary, a time after
times were offered, the contact the bot just asked for); otherwise a router model returns only an
intent and the details it found, and code answers (support module), books (explicit yes on a summary)
or cancels (booking number + the booking's contact). For businesses with lead scoring, a described
project plus a contact becomes one audited lead. Businesses with a voice agent get a call button: the
voice SDK loads only when pressed, the call uses the same tools, and the transcript shows in the chat.

**Contact forms** — the form POSTs to a per-client secret URL; fields are recognised by name and value
(any platform); a retry within 10 minutes is the same submission; a filled honeypot is stored as spam.

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
| website | Next.js 16 static export | company site with live data; no AI on the public site |
| mail | Postfix + OpenDKIM | send-only mail from the engine (SPF / DKIM / DMARC) |
| uptime-kuma | monitoring | public status page |

## Security posture

- Databases and internal services bound to loopback; containers on a private bridge network.
- Per-endpoint routing at the edge: the public API host serves only machine endpoints; the app host
  requires authentication; per-visitor and global rate limits on anything that calls a model.
- Keys are stored as hashes; secrets live in one root-only environment file, never in code or images.
- Public URL ingestion is SSRF-safe (every address and redirect hop checked, connection pinned).
- Public statistics are sanitized: no personal data, no costs, test traffic excluded.
- Browser origins can be forged, so anything that costs money (bookings, calls, messages, emails) is
  capped per visitor and per business; calls are also capped by the voice agent itself.
- The mail server listens only on private addresses, relays only for the engine on its own network and
  only for one sender address; customer emails contain no visitor-supplied text.

## Operations

- Docker Compose with health checks; every service is set to restart on its own after a reboot.
- Nightly local backups (database, workflow and monitoring databases, configuration) with a restore test.
- Versioned release bundle: idempotent installer, upgrades with backup, migrations and automatic rollback;
  pinned dependencies and images.
- Uptime Kuma monitors every service and the public hosts.
- Static, per-client, chat, forms, calendar, voice and app test suites plus a live smoke set run after
  every change; a boot check verifies every service and public host after a restart.
