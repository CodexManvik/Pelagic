## PRD: Project Leviathan - FloatChat AI V2 Rewrite

## 1. Product overview

### 1.1 Document title and version

- PRD: Project Leviathan - FloatChat AI V2 Rewrite
- Version: 1.0
- Date: 2026-04-24
- Authoring context: Senior Technical Product Manager + Staff Engineer perspective

### 1.2 Product summary

Project Leviathan is a full V2 rewrite of FloatChat AI from a hackathon prototype into a cloud-native, event-driven, enterprise-grade SaaS platform for ocean intelligence. The current prototype demonstrates core value through ARGO float exploration, profile visualization, and NL-to-SQL querying, but it is constrained by localhost deployment, static/simulated data, monolithic interaction patterns, and limited production controls.

V2 will establish a modern reference architecture that proves production-level thinking under strict free-tier constraints. The platform will ingest live ARGO feeds through a serverless streaming pipeline, provide resilient API and AI orchestration layers, and deliver high-fidelity 3D geospatial analytics through a Next.js web application.

The product vision is to become the best public portfolio demonstration of end-to-end distributed systems, event-driven data engineering, and enterprise AI orchestration in the ocean-climate domain, with interview-ready technical depth across product, architecture, security, and operations.

### 1.3 Executive summary and product vision

- Build an enterprise-style ocean data platform using only free-tier services.
- Replace regex-centric query logic with a LangGraph multi-agent system that is observable, testable, and self-correcting.
- Shift from static/local processing to live global ARGO ingestion with replayable events and resilient consumers.
- Deliver a modern 3D exploratory UX that can support scientific workflows and executive storytelling.
- Demonstrate measurable engineering excellence: secure-by-default CI/CD, infrastructure as code, and production-grade telemetry.

## 2. Goals

### 2.1 Business goals

- Position FloatChat AI as a flagship internship portfolio artifact competitive for top-tier technology companies.
- Demonstrate applied competence in distributed systems, cloud architecture, and LLM engineering.
- Build a reusable platform foundation that can extend beyond ARGO into broader ocean and climate datasets.
- Establish a credible public demo with clear architecture narrative and operational metrics.

### 2.2 User goals

- Enable oceanographers to discover float behavior, water-mass patterns, and BGC trends faster than manual workflows.
- Enable climate data scientists to ask natural language questions and receive validated analytical outputs with provenance.
- Enable technical reviewers (hiring managers, mentors) to inspect architecture quality, security posture, and engineering maturity.

### 2.3 Non-goals

- Not targeting commercial monetization or enterprise procurement in V2.
- Not replacing specialized desktop scientific suites for advanced publication-grade modeling.
- Not implementing paid cloud managed services.
- Not supporting offline-first desktop operation.

## 3. User personas

### 3.1 Key user types

- Oceanographer
- Climate data scientist
- Data engineer
- Hiring manager and technical interviewer
- Platform administrator

### 3.2 Basic persona details

- **Oceanographer**: Needs rapid visualization of profiles, trajectories, water-mass signatures, and BGC context with scientific plausibility.
- **Climate data scientist**: Needs trustworthy query workflows, reproducible outputs, and ability to inspect assumptions and data lineage.
- **Data engineer**: Needs robust ingestion, schema consistency, replayability, and low-maintenance operations under free-tier constraints.
- **Hiring manager and technical interviewer**: Needs evidence of systems thinking, tradeoff analysis, security awareness, and delivery rigor.
- **Platform administrator**: Needs clear controls for roles, secrets, deployment health, and incident triage.

### 3.3 Role-based access

- **Viewer**: Explore global map, run predefined analyses, view dashboards, export bounded datasets.
- **Researcher**: Execute advanced NL queries, compare cohorts, create saved views, access deeper diagnostics.
- **Admin**: Manage ingestion schedules, role assignments, guardrail policies, and operational configuration.

## 4. Functional requirements

### 4.1 System architecture and data flow

- **Live ingestion source**: Cron-triggered Python producer fetches ARGO updates from global FTP sources.
- **Event transport**: Producer publishes normalized events to Upstash Kafka topics.
- **Ingestion service**: FastAPI consumer subscribes, validates, deduplicates, and upserts records into Neon Postgres.
- **Storage model**: Neon stores canonical relational measurements and pgvector embeddings for semantic retrieval.
- **API layer**: FastAPI exposes versioned endpoints for map tiles/data slices, profile analytics, query execution, exports, and admin operations.
- **AI orchestration**: LangGraph coordinates Router Agent -> SQL Data Engineer Agent -> Oceanographer Agent, with self-correction loop and policy checks.
- **Frontend layer**: Next.js 14 application consumes APIs for real-time map and analytical interaction.
- **Observability feedback loop**: Langfuse traces LLM flow; Prometheus metrics and Grafana dashboards drive SLO monitoring and tuning.
```mermaid
graph TD
    %% External Sources
    ARGO[Global ARGO FTP] -->|Cron Fetch| Prod[Python Producer]
    
    %% Event Streaming
    Prod -->|Batch JSON| Kafka[(Upstash Kafka)]
    
    %% Backend & Data
    Kafka -->|Consume/Validate| Fast[FastAPI Consumer]
    Fast -->|Upsert/TTL| DB[(Neon Postgres + pgvector)]
    
    %% AI Agent Flow
    User((User)) -->|NL Query| Next[Next.js Frontend]
    Next -->|API Call| FastAPI[FastAPI Gateway]
    FastAPI -->|Orchestrate| LangGraph{LangGraph Agents}
    LangGraph -->|1. Route| Router[Router Agent]
    LangGraph -->|2. Generate| SQL[SQL Data Engineer]
    LangGraph -->|3. Explain| Ocean[Oceanographer Agent]
    SQL <-->|Execute/Self-Correct| DB
    LangGraph <-->|LLM API| Groq[Groq API Llama-3]
    
    %% Telemetry
    FastAPI -.->|Traces| Langfuse[Langfuse]
    FastAPI -.->|Metrics| Grafana[Prometheus/Grafana]

### 4.2 End-to-end flow details

1. ARGO poller runs on schedule and fetches incremental source files.
2. Parser normalizes measurements and emits immutable events keyed by float/profile identifiers.
3. Kafka buffers and decouples producer/consumer workloads, enabling replay and back-pressure resilience.
4. FastAPI consumer validates schema and quality flags, then performs idempotent writes to Neon.
5. Embedding job updates pgvector representations for queryable semantic context.
6. User opens Next.js app and interacts with Deck.gl globe/map and analytical panels.
7. Natural language query is sent to LangGraph orchestration endpoint.
8. Router Agent classifies intent and required tools.
9. SQL Data Engineer Agent generates/validates SQLAlchemy-safe SQL against schema constraints.
10. Oceanographer Agent enforces domain plausibility checks and crafts scientific interpretation.
11. API returns structured result + explanation + confidence metadata to frontend.
12. Full execution traces, latency, token usage, and failure reasons are captured for quality control.

### 4.3 Detailed tech stack (free-tier constrained)

- **Frontend**
  - Next.js 14 App Router
  - TypeScript
  - TailwindCSS
  - Zustand state management
  - Deck.gl for 3D WebGL globe and ocean mapping
  - Hosting: Vercel Free or Cloudflare Pages Free
- **Backend**
  - Python 3.11+
  - FastAPI
  - SQLAlchemy 2.0
  - Docker containers
  - Hosting: Google Cloud Run free tier or Render free tier
- **AI and orchestration**
  - LangGraph multi-agent workflows
  - Groq API with Llama-3 model family
  - Guardrails for SQL safety and domain validation
- **Data and messaging**
  - Neon serverless Postgres
  - pgvector extension in Neon
  - Upstash Kafka serverless topics
  - Scheduled producer job (cron)
- **DevSecOps**
  - Terraform for infrastructure as code
  - GitHub Actions for CI/CD
  - Trivy for container and dependency scanning
  - SonarCloud for SAST and code quality gates
- **Observability**
  - Langfuse for LLM traces, token/cost, and latency
  - Prometheus metrics exporter
  - Grafana Cloud dashboards and alerting
- **Testing Engineering**
  - Backend: `pytest` with `pytest-asyncio` for API and Kafka consumer unit/integration tests.
  - Frontend: `Vitest` for component logic and `Playwright` for critical E2E (End-to-End) user flows.
  - Mocking: `testcontainers` or SQLite memory DBs for isolated database testing in CI.

### 4.4 Core feature set

- **Live global ARGO ingestion pipeline** (Priority: P0)
  - Incremental fetch, normalization, quality handling, idempotent writes.
  - Retry and dead-letter strategies under transient failures.
- **Enterprise-grade query and reasoning engine** (Priority: P0)
  - Multi-agent query planning, SQL generation, validation, and scientific interpretation.
  - Structured response envelopes with confidence and provenance.
- **3D geospatial exploration interface** (Priority: P0)
  - Globe/map exploration, trajectory rendering, depth/time slicing, parameter overlays.
- **Scientific profile analytics** (Priority: P1)
  - T-S profiles, BGC trends, vertical sections, temporal comparisons.
- **Secure tenant-lite access model** (Priority: P1)
  - GitHub OAuth and RBAC with role-aware feature gating.
- **Auditability and exportability** (Priority: P1)
  - Bounded exports with metadata, run history, and trace links.

## 5. User experience

### 5.1 Entry points and first-time user flow

- Landing page introduces live ingest status and global ocean activity snapshot.
- User authenticates via GitHub OAuth and is assigned default Viewer role.
- Guided onboarding showcases map layers, query panel, and profile explorer.
- User executes first natural language question with transparent reasoning trail.

### 5.2 Core experience

- **Explore globe**: User discovers float trajectories and hotspots through Deck.gl layers.
  - This enables immediate geospatial context and reduces query ambiguity.
- **Inspect profile**: User selects a float/profile and drills into T-S and BGC depth behavior.
  - This preserves scientific workflow fidelity and improves trust.
- **Ask analysis question**: User submits NL request and receives validated SQL-backed answer.
  - This reduces analyst cycle time while keeping output explainable.
- **Operational confidence**: User/admin inspects trace and quality metadata for each answer.
  - This supports reliability and interview-ready transparency.

### 5.3 Advanced features and edge cases

- Graceful degradation when Groq API or Kafka is temporarily unavailable.
- Query safety fallback to curated templates for ambiguous or risky requests.
- Time-windowed replay for ingestion correction and post-incident recovery.
- High-cardinality map data handling with progressive loading and level-of-detail.
- Regional data sparsity handling with confidence signaling.

### 5.4 UI and UX highlights

- 3D globe-first narrative for geospatial storytelling.
- Unified query + evidence panel with SQL and domain rationale visibility.
- Performance-aware rendering for smooth interaction under free-tier constraints.
- Clear trust indicators: data freshness, trace availability, quality confidence.

## 6. Narrative

A climate scientist opens the platform and immediately sees a live, global view of ARGO activity. They narrow to a basin, inspect a trajectory, and ask a nuanced question about temperature-salinity structure and oxygen changes across depth bands. Behind the scenes, a multi-agent AI workflow routes intent, generates validated SQL, and applies domain plausibility checks before presenting a result with lineage and confidence. The scientist gains insight quickly, while the engineering stack demonstrates production-grade architecture, observability, and security discipline.

## 7. Success metrics

### 7.1 User-centric metrics

- Median time-to-first-insight under 120 seconds for new users.
- Query success satisfaction score of at least 4.3/5 from evaluators.
- At least 70% of user sessions complete a map-to-query-to-profile workflow.

### 7.2 Business metrics

- Portfolio interview conversion improvement target: 3x over current baseline.
- Minimum 5 strong technical review endorsements referencing architecture depth.
- Public demo completion rate of at least 80% without operator intervention.

### 7.3 Technical metrics

- API p95 latency under 800 ms for non-LLM endpoints.
- End-to-end NL query p95 under 4.5 s under aggressive showcase load.
- Ingestion pipeline successful event processing rate above 99.0% daily.
- Data freshness lag under 15 minutes from ARGO source to query availability.
- Error budget: monthly platform availability target 99.5%.
- LLM structured output validity above 97%.
- Map interaction frame rate target: 45+ FPS on mid-tier laptop GPU for standard workloads.
- **Target Scale**: Optimized for 500,000 daily ingested ARGO records and up to 200 concurrent user sessions.
- API p95 latency under 800 ms for non-LLM endpoints.
- End-to-end NL query p95 under 4.5 s under peak load.
- Ingestion pipeline successful event processing rate above 99.0% daily.
- Data freshness lag under 15 minutes from ARGO source to query availability.

## 8. Technical considerations

### 8.1 Integration points

- ARGO FTP endpoints with resilient polling and incremental checkpoints.
- Upstash Kafka topic schema governance and replay strategy.
- Neon schema migration and indexing strategy for analytical and vector workloads.
- LangGraph orchestration service integration with Groq model endpoints.
- Frontend API contract versioning between Next.js and FastAPI.

### 8.2 Data storage and privacy

- Canonical measurement storage in Neon with strict schema versioning.
- pgvector embedding storage for semantic query assist and retrieval.
- Minimal personal data storage (OAuth identifiers only) with encryption in transit.
- Audit logs for privileged actions and model outputs used in decisions.

### 8.3 Scalability and performance

- Event-driven decoupling via Kafka to absorb burst ingestion patterns.
- Idempotent consumers and partitioning strategy by float or region.
- Caching strategy for hot geospatial tiles and frequent analytical aggregates.
- Progressive data fetch patterns in frontend to avoid over-fetching.
- Back-pressure aware consumers with bounded memory and retry windows.
- **Data Retention & TTL (Time-To-Live)**: To strictly adhere to Neon.tech's 500MB free-tier storage limit, raw ARGO measurement data will have a rolling 7-day TTL. A cron job will drop raw measurements older than 7 days, while preserving aggregated daily summaries, float metadata, and vector embeddings indefinitely.
- **Message Batching**: To avoid hitting Upstash Kafka's daily message limits, the Python producer will batch up to 500 float records into a single JSON payload before publishing to the topic.
- **API Rate Limiting**: The FastAPI backend will implement IP-based and Role-based rate limiting (e.g., using `fastapi-limiter` with in-memory storage) to prevent abuse of the free Groq LLM API and Neon connection pool.
- **Connection Pooling**: Neon's PgBouncer will be utilized to multiplex database connections, ensuring the system remains stable under the target load of 200 concurrent users without exhausting Postgres connection limits.

### 8.4 Security and compliance baseline

- GitHub OAuth with RBAC enforcement at API and UI levels.
- OWASP-aligned input validation and output encoding.
- SQL safety controls: strict allowlist patterns and parameterized execution.
- Secrets management through environment isolation and GitHub Actions secrets.
- Trivy and SonarCloud quality gates must pass before deploy.
- SOC2-aligned control mapping for access, change management, and logging.

### 8.5 Potential challenges

- Free-tier quota variability across hosting and third-party services.
- API rate limits (Groq, Kafka, hosting providers) during demo spikes.
- Data quality inconsistencies in upstream ARGO feeds.
- Balancing scientific depth with UX simplicity for mixed audiences.

## 9. Milestones and sequencing

### 9.1 Project estimate

- Size: Large
- Time estimate: 14 to 18 weeks (single lead developer with part-time mentorship)

### 9.2 Team size and composition

- Team size: 1 to 3
- Roles involved: Product/Platform Lead, Full-stack Engineer, Optional Data Science Reviewer

### 9.3 Suggested phases (5 epics)

- **Epic 1: Infrastructure and DevSecOps foundation** (2 to 3 weeks)
  - Key deliverables: Terraform baseline, CI/CD pipeline, container hardening, security gates, environment strategy.
- **Epic 2: Real-time data pipeline** (3 to 4 weeks)
  - Key deliverables: ARGO producer, Kafka topics, FastAPI consumer, idempotent ingestion, replay and DLQ strategy.
- **Epic 3: FastAPI and multi-agent AI core** (3 to 4 weeks)
  - Key deliverables: versioned API, LangGraph agents, SQL validation framework, domain plausibility checks.
- **Epic 4: 3D geospatial frontend** (3 to 4 weeks)
  - Key deliverables: Next.js app shell, Deck.gl globe, profile analytics UI, auth and role-aware workflows.
- **Epic 5: Observability, reliability, and launch** (2 to 3 weeks)
  - Key deliverables: Langfuse tracing, Prometheus metrics, Grafana dashboards, load tests, demo runbook.

## 10. User stories

### 10.1 Live ingestion reliability

- **ID**: GH-001
- **Description**: As a data engineer, I want the ARGO ingestion pipeline to process incremental updates reliably so that the dataset remains fresh and replayable.
- **Acceptance criteria**:
  - Producer records checkpoint state for each source pull.
  - Consumer performs idempotent upsert using deterministic keys.
  - Failed batches are retried and then routed to dead-letter topic after threshold.
  - Daily processing success rate and lag metrics are visible in Grafana.

### 10.2 Geospatial ocean exploration

- **ID**: GH-002
- **Description**: As an oceanographer, I want a 3D globe map with float trajectories and parameter overlays so that I can identify spatial patterns rapidly.
- **Acceptance criteria**:
  - User can filter by time window, basin, and parameter type.
  - Deck.gl layers render trajectories and selected points with legend and units.
  - Map interactions remain responsive with progressive loading enabled.
  - Selected map object links directly to profile analytics panel.

### 10.3 Scientific profile analytics

- **ID**: GH-003
- **Description**: As a climate data scientist, I want to inspect T-S and BGC profiles by depth so that I can validate water-mass and biogeochemical behavior.
- **Acceptance criteria**:
  - User can compare at least two profiles side-by-side.
  - T-S and depth charts include axis units and quality-flag-aware filtering.
  - Missing or sparse BGC values are explicitly labeled.
  - Exported chart metadata includes profile identifiers and timestamp.

### 10.4 Multi-agent natural language analytics

- **ID**: GH-004
- **Description**: As a researcher, I want to ask complex natural language questions so that I can get accurate, explainable, SQL-backed insights.
- **Acceptance criteria**:
  - Router Agent classifies query intent with confidence score.
  - SQL Data Engineer Agent returns validated, non-destructive SQL only.
  - Oceanographer Agent appends domain plausibility assessment.
  - Response includes answer, SQL summary, and trace link.

### 10.5 Query safety and guardrails

- **ID**: GH-005
- **Description**: As an administrator, I want strict query guardrails so that unsafe execution paths are blocked by default.
- **Acceptance criteria**:
  - Only allowlisted operations are executed for analytical queries.
  - Parameterized execution is mandatory for user-provided values.
  - Blocked queries return actionable explanation and safe fallback.
  - Guardrail decisions are logged for audit.

### 10.6 Authentication and authorization

- **ID**: GH-006
- **Description**: As a platform administrator, I want GitHub OAuth with role-based access control so that sensitive capabilities are limited to authorized users.
- **Acceptance criteria**:
  - OAuth login flow is functional for all supported environments.
  - Viewer, Researcher, and Admin roles enforce endpoint-level permissions.
  - Unauthorized action attempts are denied and logged.
  - Role changes take effect without service redeploy.

### 10.7 Observability and SLO governance

- **ID**: GH-007
- **Description**: As an engineer, I want comprehensive telemetry so that I can detect regressions, optimize latency, and communicate system health.
- **Acceptance criteria**:
  - Prometheus exports API, ingestion, and worker metrics.
  - Grafana dashboards include latency, throughput, error budget, and freshness lag.
  - Langfuse traces include agent path, token usage, latency, and failure causes.
  - Alert thresholds trigger notifications for SLO violations.

### 10.8 DevSecOps quality gates

- **ID**: GH-008
- **Description**: As a hiring manager reviewer, I want reproducible secure delivery practices so that the project demonstrates enterprise engineering maturity.
- **Acceptance criteria**:
  - Pull requests run tests, linting, Trivy scan, and SonarCloud analysis.
  - Deployment only proceeds when required quality gates pass.
  - Infrastructure changes are codified in Terraform with peer review.
  - Build artifacts and release notes are versioned and traceable.

### 10.9 Interview-mode demonstration workflow

- **ID**: GH-009
- **Description**: As a candidate, I want a reliable scripted demo path so that I can consistently showcase architecture depth in interviews.
- **Acceptance criteria**:
  - A guided scenario demonstrates ingestion, query orchestration, and map analytics in one flow.
  - Demo mode has preflight checks for dependencies and quotas.
  - Failure fallbacks are documented in a runbook.
  - Demo output includes architecture callouts tied to real telemetry.

### 10.10 Data export and reproducibility

- **ID**: GH-010
- **Description**: As a researcher, I want exportable and reproducible outputs so that analysis can be shared and independently verified.
- **Acceptance criteria**:
  - Exports include result data, query metadata, and timestamp.
  - Export format options include CSV and JSON in MVP.
  - Each export references originating trace and profile identifiers.
  - Export size and rate limits are enforced per role.
