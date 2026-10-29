# Upwork portfolio item — Adaptive Systems AI stack

**Title:** AI Receptionist, Support Bot & Lead Scoring — one config-driven, self-hosted engine

**Role:** Sole engineer — architecture, backend (Python + TypeScript), voice agent, data layer,
orchestration, infrastructure, security, testing

**Skills:** Python, TypeScript, FastAPI, LangGraph, Pydantic AI, RAG, pgvector, PostgreSQL, Redis,
n8n, ElevenLabs, Next.js, Docker, nginx, MCP

---

## Summary (~150 words)

A self-hosted AI engine that businesses configure instead of commissioning. Each client is a folder
of config files: hard facts (hours, prices, services), documents, scoring rules and reply templates.
From that, the engine answers customer questions with checkable citations and never invents a price
or opening time, books and cancels real appointments, runs an ElevenLabs voice receptionist built
automatically from the same config, and scores inbound leads with an LLM whose output is checked by a
deterministic TypeScript policy gate. Every decision is audit-logged per client. Three clients run
today from config alone (our intake plus two fictional demo businesses). Security is tested, not
assumed: prompt-injection detectors, tenant-isolation tests between every client pair, SSRF-safe
ingestion, signed webhooks. A real voice call test books and cancels an appointment end to end.

## Measured on the live system

- Lead qualification p50 2.8 s / p95 4.2 s, with a fallback chain and a review route instead of errors
- Deterministic policy gate ≈ 10 ms, no model call
- Voice tools p95 ≈ 25 ms
- Real voice call test 17/17 (docs question, two injection attempts, book + cancel, signed webhook stored)
- 415 static checks, 98 per-client live tests, 21 voice tests, 81 app checks

## Highlights for proposals

- Hard facts come from config, never from the model; out-of-scope questions are refused.
- Explainable decisions: score, per-gate pass/fail and reason codes for every lead.
- Adding a client is configuration, not development.
- Runs on the client's own server or hosted; the client owns its data.

**Live:** telemetry dashboard https://nukethemaii.github.io/ai-command-center/ · status page
https://status.adaptivesystems.dev/status/stack · walkthrough of the private app on request.
