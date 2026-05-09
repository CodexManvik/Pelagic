# Debug Map (Internal)

## Request and Event Flows

### API Request Flow
1. Client -> FastAPI router -> request-id middleware.
2. Route handler -> service layer -> DB session.
3. Optional: LangGraph pipeline -> SQL guard -> DB execution.
4. Response -> request-id in headers.

### Ingestion Flow
1. Producer fetches ARGO updates.
2. Batch publish to QStash webhook target.
3. Webhook validates + Redis dedupe + upserts.
4. TTL cleanup and daily summaries run on schedule.

## Log Correlation
- Request id header: `X-Request-ID`.
- Log field: `request_id`.
- Query pipeline logs: `trace_id`, `agent_step`, `sql_hash`.

## Metrics
- `/metrics` endpoint exposes:
  - `http_requests_total` (by method, status).
  - `argo_ingest_events_total`.
  - `argo_ingest_lag_seconds`.
  - `nl_query_latency_seconds`.

## Common Failure Modes
- 401 on webhook: missing or invalid QStash signature.
- 500 on ingestion: database upsert failure or schema mismatch.
- Query guard failure: SQL uses non-allowlisted tables or non-SELECT verbs.
- Empty map: ingestion not yet run or TTL cleanup ran with no summaries.

## Quick Checks
- `GET /health` returns `ok` and database `ok`.
- `POST /api/webhooks/argo-ingest` with sample payload returns `ok`.
- `POST /api/v1/query` returns `answer` and `sql`.
- `GET /api/v1/floats?limit=10` returns data.

## Environment Matrix
- Local dev: `.env` + local DB or Neon.
- Demo: Neon + QStash + Upstash Redis + Groq + Langfuse.
- CI: SQLite (unit) + mocked LLM.
