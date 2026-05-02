# AI Restaurant Recommendation System

## Phase 1 Implementation

Phase 1 covers:
- Dataset ingestion from Hugging Face
- Cleaning and normalization
- Deduplication using a stable key
- Schema-oriented quality checks
- Persisting outputs for downstream phases

## Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Library**: React 18
- **Styling**: Vanilla CSS (Custom Design System with Zomato branding)
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (Python)
- **Server**: Uvicorn
- **Deployment**: Render.com

### AI & Data
- **LLM Engine**: Groq Cloud API (LPU Inference)
- **Orchestration**: Custom prompt management & fallback logic
- **Data Processing**: Pandas, PyArrow
- **Dataset**: Hugging Face `ManikaSaini/zomato-restaurant-recommendation`

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Source Organization

- `src/phase1/data_pipeline/` - ingestion, transformation, validation, pipeline runner
- `src/phase2/api/` - request/response schemas and API endpoints
- `src/phase3/api/` - deterministic candidate retrieval and soft-scoring engine
- `src/phase4/llm/` - Groq prompt orchestration, parsing, and fallback logic

## Run Phase 1 Pipeline

```bash
python scripts/run_phase1.py
```

## Phase 2 API

Start API:

```bash
python scripts/run_api.py
```

Set `.env` value before using LLM reranking:

```bash
GROQ_API_KEY=<your_api_key>
```

Then call:

- `POST http://127.0.0.1:8000/recommendations`
- `GET http://127.0.0.1:8000/health`

API contract:

- `docs/api-spec.md`

## Generated Artifacts

- Raw snapshot: `data/raw/zomato_raw_<timestamp>.jsonl`
- Processed dataset: `data/processed/restaurants.parquet`
- Quality report: `data/reports/quality_report.json`

## Phase 5 Frontend (Next.js)

Since the UI has been upgraded to a React/Next.js dashboard, you need Node.js installed to run it.

### Prerequisites
1. Download and install Node.js from [nodejs.org](https://nodejs.org/).
2. Verify installation by running `node -v` and `npm -v` in your terminal.

### Run Frontend
Open a dedicated terminal, navigate into the frontend directory, install dependencies, and start the development server:

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on **http://localhost:3000** and will automatically proxy requests to the backend API (`http://127.0.0.1:8000`).
