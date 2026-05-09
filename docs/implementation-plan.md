# FloatChat AI V2 Implementation Plan (Internal)

## Goals
- Deliver an end-to-end, free-tier-ready, event-driven ocean intelligence platform.
- Keep local dev friction low: one command per service, with API keys provided via `.env`.
- Preserve production-minded architecture (observability, guardrails, replayable ingestion).

## Assumptions and Constraints
- Free-tier services only (Neon, Upstash, Groq, Vercel/Cloudflare, Grafana Cloud).
- Strict storage budget: raw measurements TTL 7 days; aggregated summaries retained.
- All new modules must be modular, testable, and observable.

## Phased Delivery (Internal)

### Phase 0: Foundation (Days 1-5)
- Backend app structure, settings, logging, and Prometheus metrics.
- Database schema expansion (query audit, embeddings, summary tables).
- API versioning and standard response envelopes.
- Docs: debug map, runbook, and environment variable matrix.

### Phase 1: Ingestion Pipeline (Days 6-14)
- Producer: ARGO poller (index fetch + minimal measurements) with batching.
- Transport: QStash webhook delivery for batch events.
- Consumer: idempotent upserts with Redis-backed dedupe and replay support.
- TTL cleanup job and daily summary rollup job.

### Phase 2: AI Orchestration (Days 15-24)
- LangGraph multi-agent pipeline: Router -> SQL Engineer -> Oceanographer.
- SQL guardrails (parse + allowlist) and execution sandbox.
- Structured outputs and trace logging (Langfuse optional).
- Query audit persistence and replayable results.

### Phase 3: Frontend (Days 25-36)
- Next.js 14 App Router scaffolding with Tailwind and Deck.gl.
- 3D globe view, float filtering, profile panel, and query panel.
- API integration for map layers, profiles, and NL query results.
- UX polish: staged animations, non-default typography, and narrative layout.

### Phase 4: Observability + Quality Gates (Days 37-45)
- Prometheus metrics and Grafana dashboards (latency, ingestion lag, error budget).
- Langfuse traces for LLM flows and SQL validation outcomes.
- CI/CD with unit tests, linting, and security scanning.

## Target Code Map (Planned)

```
backend/
  api/
    router.py
    webhooks.py
    routes/
      health.py
      floats.py
      profiles.py
      query.py
      admin.py
  ai/
    graph.py
    llm.py
    schemas.py
    guards.py
    tools.py
  core/
    config.py
    logging.py
    middleware.py
    prompts.py
    telemetry.py
  db/
    models.py
    session.py
  services/
    ingestion.py
    query.py
    summaries.py
    embeddings.py
  worker/
    cleanup.py
    embedding_worker.py
  prompts/
    router.md
    sql_engineer.md
    oceanographer.md
    repair_sql.md
  schemas/
    floats.py
    query.py
    health.py
    ingestion.py

data-pipeline/
  argo_fetcher.py
  argo_events.py
  producer.py
  requirements.txt

frontend/
  app/
  components/
  styles/
  lib/
```

## Environment Variables (Key)
- `DATABASE_URL`, `APP_NAME`, `ENVIRONMENT`
- `GROQ_API_KEY`, `GROQ_MODEL`
- `QSTASH_TOKEN`, `QSTASH_TARGET_URL`, `QSTASH_CURRENT_SIGNING_KEY`, `QSTASH_NEXT_SIGNING_KEY`
- `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`

## Acceptance Criteria (Internal)
- Ingestion accepts batched events and writes idempotently to Neon.
- Query endpoint returns SQL-backed results with guardrail verdicts.
- Frontend renders globe, profile chart, and query panel without crashing.
- Metrics and traces available for debugging and demo.

## Demo Readiness Checklist
- Fresh ingestion run completes in under 10 minutes.
- Sample NL query returns a result with confidence and trace link.
- Map renders with at least 1,000 points at 45+ FPS on mid-tier GPU.
- Runbook steps validated in a clean environment.
