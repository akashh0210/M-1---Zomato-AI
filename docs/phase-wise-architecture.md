# Phase-wise Architecture: AI-Powered Restaurant Recommendation System

## 1) Goal and Scope

Build an AI-powered restaurant recommendation system (inspired by Zomato) that:
- Accepts user preferences (location, budget, cuisine, rating, optional tags)
- Uses a real restaurant dataset from Hugging Face
- Combines deterministic filtering with LLM-based ranking and explanations
- Returns useful, human-readable recommendations through a clean interface

This architecture is designed to be delivered in phases so each phase is independently testable and production-ready.

---

## 2) Target System Architecture (High Level)

### Core Components
- **Data Layer**
  - Dataset ingestion from Hugging Face
  - Cleaning, normalization, schema validation
  - Storage in a query-friendly database
- **Recommendation API Layer**
  - User input validation
  - Candidate retrieval using strict filters
  - LLM orchestration for ranking + explanation
  - Response formatting
- **Prompt and LLM Layer**
  - Prompt templates and guardrails
  - Context construction from filtered candidates
  - Structured model outputs
- **Application/UI Layer**
  - Preference input form
  - Recommendation cards/table
  - Explanation display
- **Quality and Ops Layer**
  - Logging, metrics, tracing
  - Model quality evaluation
  - CI/CD, versioning, monitoring

### Data Flow
1. Dataset is ingested and normalized.
2. User submits preferences.
3. Backend applies deterministic filters and scoring.
4. Top candidate set is passed to LLM in structured prompt.
5. LLM returns ranked recommendations with reasons.
6. API validates and returns standardized response to UI.

---

## 3) Phase-wise Delivery Plan

## Phase 0: Foundations and Project Setup

### Objective
Set up development standards, repo structure, environments, and baseline tooling.

### Deliverables
- Repository structure:
  - `data/` (raw, processed)
  - `src/api/`, `src/core/`, `src/llm/`, `src/ui/`
  - `tests/`, `docs/`, `configs/`
- Environment management:
  - `.env.example` for secrets and model configuration
  - Separate dev and prod config profiles
- Tooling:
  - Formatter, linter, pre-commit hooks
  - Basic CI workflow (lint + tests)

### Key Design Decisions
- Keep LLM integration behind an abstraction (`LLMClient`) so model providers can be swapped.
- Version every prompt template to track performance changes.

### Exit Criteria
- Project runs locally end-to-end with a placeholder API endpoint.
- CI checks pass on every pull request.

---

## Phase 1: Data Ingestion and Standardization

### Objective
Build a reliable data pipeline to ingest and clean restaurant data from Hugging Face.

### Inputs
- Source dataset: `ManikaSaini/zomato-restaurant-recommendation`

### Processing Architecture
- **Ingestion module**
  - Load dataset snapshot from Hugging Face
  - Persist raw files in `data/raw/` with ingestion timestamp
- **Transformation module**
  - Normalize fields:
    - `restaurant_name`
    - `locality` (instead of exact city if available)
    - `cuisines` (list)
    - `average_cost_for_two`
    - `rating`
    - `metadata_tags` (optional)
  - Handle null values and malformed rows
  - Deduplicate records by stable key (name + locality to keep highest rated branch)
- **Validation module**
  - Schema checks (type, range, mandatory fields)
  - Quality reports (missing rate, duplicates removed, outlier count)

### Storage
- Start: local file-based storage (`data/processed/restaurants.parquet`)
- Next: move to relational DB for query performance (`PostgreSQL` recommended)

### Exit Criteria
- Reproducible ingestion command builds processed dataset.
- Data quality report generated after each ingestion.

---

## Phase 2: Preference Capture and API Contract

### Objective
Define and implement robust user preference input and request/response contracts.

### API Endpoints
- `GET /locations`
  - Output: List of all unique cities/localities available in the processed data.
- `GET /cuisines`
  - Output: List of all known Title Cased cuisines extracted from the processed dataset.
- `POST /recommendations`
  - Input:
    - `location` (string)
    - `budget` (numeric float representing max budget)
    - `cuisine` (string or list)
    - `min_rating` (float)
    - `additional_preferences` (optional string/list)
  - Output:
    - Top N recommendations with explanation and confidence

### Validation Rules
- `location` required and normalized (case-insensitive mapping)
- `min_rating` in valid range (e.g., 0.0-5.0)
- `budget` treated as maximum allowed threshold
- Unknown cuisine terms handled with fallback or suggestion

### UI (MVP)
- Single form for preferences
- Submission status/loading state
- Error messaging for invalid inputs

### Exit Criteria
- API contract documented in `docs/api-spec.md`.
- Input validation test coverage added.

---

## Phase 3: Deterministic Candidate Retrieval Engine

### Objective
Retrieve and pre-rank candidate restaurants efficiently before invoking LLM.

### Retrieval Pipeline
1. Filter by hard constraints:
   - location match
   - cost range by budget band
   - rating threshold
2. Soft scoring:
   - cuisine similarity score
   - preference keyword matching (family-friendly, quick service, etc.)
   - weighted rating and cost-fit score
3. Produce candidate shortlist (e.g., top 15-30 items) for LLM.

### Why This Phase Matters
- Reduces hallucinations by grounding model on real candidates.
- Controls token usage and latency by shrinking prompt context.

### Exit Criteria
- Candidate retrieval deterministic and unit tested.
- p95 retrieval latency under agreed threshold (e.g., <150ms for local data).

---

## Phase 4: LLM Prompt Engineering and Recommendation Reasoning

### Objective
Use the LLM to rank shortlisted options and generate human-like explanations.

### LLM Provider Decision (Updated)
- Use **Groq LLM** in Phase 4 for ranking and explanation generation.
- Store the API key in a local `.env` file as `GROQ_API_KEY`.
- Do not hardcode API keys in source code, config files, or documentation.

### Prompt Architecture
- **System prompt**
  - Role: recommendation analyst
  - Rules: only use provided candidate data, no fabricated fields
- **User prompt**
  - User preferences in structured JSON
  - Candidate table in compact structured format
- **Output format**
  - Enforced JSON schema:
    - rank
    - restaurant_name
    - rationale
    - tradeoffs
    - confidence

### Guardrails
- Reject output items not present in candidate list.
- Enforce max explanation length.
- Fallback to deterministic ranking if LLM call fails.

### Exit Criteria
- Prompt version `v1` created and benchmarked.
- Structured output parser with validation is stable.

---

## Phase 5: Response Assembly and UX Presentation

### Objective
Transform model output into a clear, user-friendly recommendation experience using a modern Next.js frontend.

### Response Composition
- Merge LLM output with canonical record fields:
  - restaurant name
  - cuisine(s)
  - rating
  - estimated cost
  - AI explanation
- Add optional summary:
  - "Best fit based on your budget and cuisine preference"

### UX/UI Requirements (Next.js Application)
- **Framework**: Next.js (App Router) for building a robust, component-based frontend.
- **Design System**: Brand-aligned Zomato AI exact styling.
  - Usage of custom Zomato Red (`#CB202D`) for highlights and CTA buttons.
  - Deep atmospheric mesh-gradient background for the top search hero section.
  - Clean `Outfit` sans-serif layout.
- **Layout Characteristics**:
  - Central **Hero Search Card**: Wide white card containing a visual "natural language" search input (`"I want a spicy ramen place..."`) representing future upgrades, accompanied by keyword suggestion pills.
  - **Structured Filters**: Direct mapped filters (Locality, Cuisine dropdown, Budget, Min Rating) laid out cleanly in a 4-column inline grid to power the current API. Employs a dynamic "Other..." text input fallback for cuisines.
  - **Results Presentation (`Curated for You`)**: Rich photo-based grid mapping the top recommendation to a dominant "Main Feature" card with AI explanations overlayed. All AI Reasoning explicitly prefixes the actual AI Confidence Score formatting (`Confidence 90% | ...`). Restaurant names explicitly render their rank formatting formatting (`#1 Restaurant Name`).

### Exit Criteria
- Frontend Next.js app communicates cleanly with FastAPI backend.
- UI perfectly matches the Zomato AI brand mockups, featuring image placeholders where the dataset lacks imagery.

---

## Phase 6: Evaluation, Testing, and Quality Assurance

### Objective
Measure system quality across retrieval accuracy, explanation relevance, and reliability.

### Test Strategy
- **Unit tests**
  - normalizers, filters, budget mapping, schema checks
- **Integration tests**
  - API + retrieval + LLM mock pipeline
- **E2E tests**
  - realistic user profiles and expected recommendation quality

### Evaluation Metrics
- Retrieval precision@K
- LLM explanation relevance score (human rubric or pairwise rating)
- Hallucination rate (recommendations not in dataset)
- Latency and success rate

### Exit Criteria
- Minimum quality threshold documented and met.
- Regression suite included in CI pipeline.

---

## Phase 7: Productionization and Operations

### Objective
Prepare the solution for stable deployment, observability, and iterative improvement.

### Production Architecture
- **Frontend Deployment**: Vercel (Next.js Application)
- **Backend Deployment**: Render.com
- Managed database for restaurant records
- Secret management for API keys
- Rate limiting and request quotas

### Observability
- Structured logs:
  - request id
  - filter counts
  - model latency
  - fallback usage
- Metrics dashboard:
  - request volume
  - p50/p95 latency
  - model error rate
- Alerting on:
  - elevated LLM failures
  - high latency
  - data ingestion failures

### Continuous Improvement Loop
- Collect anonymized feedback (liked/disliked recommendation)
- Retrain or recalibrate retrieval weights
- A/B test prompt versions

### Exit Criteria
- Stable deployment with monitoring + alerts.
- Defined release process and rollback strategy.

---

## 4) Suggested Tech Stack (Pragmatic)

- **Backend**: Python (`FastAPI`)
- **Data processing**: `pandas` + `pyarrow`
- **Storage**: local Parquet for snapshots (ready for PostgreSQL)
- **LLM**: Groq (LPU Inference)
- **Frontend**: Next.js 14 (App Router) with Vanilla CSS
- **Testing**: `pytest`, integration + E2E suites
- **Observability**: Structured logging + quality reports
- **Deployment**: Backend on Render.com, Frontend on Vercel
---

## 5) Risk Register and Mitigations

- **Risk: Sparse data for some cities/cuisines**
  - Mitigation: fallback to nearest matching city/cuisine cluster
- **Risk: LLM hallucination**
  - Mitigation: strict candidate grounding + output validator
- **Risk: High latency from large prompts**
  - Mitigation: candidate pruning and compact prompt serialization
- **Risk: Cost escalation from model usage**
  - Mitigation: caching, lower-cost model tier for simple queries

---

## 6) Implementation Milestones (Recommended Timeline)

- **Week 1**: Phase 0 + Phase 1
- **Week 2**: Phase 2 + Phase 3
- **Week 3**: Phase 4 + Phase 5
- **Week 4**: Phase 6 + Phase 7 (deployment and monitoring)

---

## 7) Deployment Strategy

The application components will be deployed on the following platforms for production and testing usage:

- **Frontend Deployment**: The Next.js web application will be hosted on **Vercel** to utilize its seamless integration with Next.js, Edge Network delivery, and automatic preview environments.
- **Backend Deployment**: The Python backend API will be deployed using **Render.com** for robust, scalable hosting of the FastAPI microservices.

---

## 8) Definition of Done (Project Level)

The project is complete when:
- Users can submit preferences and get relevant recommendations.
- Every recommendation maps to real dataset entries.
- LLM explanations are coherent, grounded, and useful.
- System has tests, monitoring, and a repeatable deployment process.

