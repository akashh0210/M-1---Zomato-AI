# AI-Powered Restaurant Recommendation System

## Problem Statement & Goal

Finding the perfect restaurant can be overwhelming due to information overload and generic search results. This project builds an AI-powered restaurant recommendation system—inspired by Zomato—that solves this problem by providing highly personalized, context-aware dining suggestions. 

The system accepts user preferences (location, budget, cuisine, rating, and optional tags) and combines **deterministic filtering** with **LLM-based ranking and reasoning**. Instead of just returning a list of places, the system provides human-readable explanations detailing *why* a specific restaurant is the best fit for the user's current craving.

## System Architecture

The project is built using a modern, decoupled architecture designed for speed, accuracy, and scalability:

- **Data Layer**: Ingests, cleans, and normalizes a real-world restaurant dataset from Hugging Face. Handles deduplication and schema validation, persisting the data in a fast, query-friendly Parquet format.
- **Recommendation API Layer**: A robust Python/FastAPI backend that handles user input validation, applies strict deterministic filters (budget, location, rating), and manages candidate retrieval to minimize LLM hallucinations.
- **Prompt and LLM Layer**: Integrates with the Groq Cloud API to perform soft-scoring and intelligent ranking on the shortlisted candidates. It generates structured JSON outputs containing the final recommendations and personalized rationales.
- **Application/UI Layer**: A sleek, responsive Next.js frontend built with a custom Zomato-branded design system. It presents the user with an intuitive search interface and rich, photo-based recommendation cards.

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
- **Uptime Management**: UptimeRobot (Ping monitoring)

### AI & Data
- **LLM Engine**: Groq Cloud API (LPU Inference)
- **Data Processing**: Pandas, PyArrow
- **Dataset**: Hugging Face (`ManikaSaini/zomato-restaurant-recommendation`)
- **Storage**: Local Parquet (Ready for PostgreSQL migration)

## Repository Structure

- `data/` - Raw datasets, processed Parquet files, and quality reports.
- `docs/` - Architecture documentation and API specifications.
- `frontend/` - Next.js frontend application.
- `scripts/` - Utility scripts for data ingestion and running the API.
- `src/` - Core backend logic organized by implementation phases:
  - `phase1/` - Data pipeline, ingestion, and validation.
  - `phase2/` - API request/response schemas.
  - `phase3/` - Deterministic candidate retrieval and soft-scoring engine.
  - `phase4/` - Groq prompt orchestration and LLM parser logic.
- `tests/` - Unit and integration testing suites.

## Local Setup & Execution

### 1. Backend Setup

Ensure you have Python 3.10+ installed.

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the data ingestion pipeline (Required for first-time setup)
python scripts/run_phase1.py

# Set your Groq API key in the environment
export GROQ_API_KEY="your_api_key_here"  # On Windows use: set GROQ_API_KEY="your_api_key_here"

# Start the FastAPI server
python scripts/run_api.py
```
The backend API will run on `http://127.0.0.1:8000`.

### 2. Frontend Setup

Ensure you have Node.js 18+ installed.

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
The frontend UI will run on `http://localhost:3000` and proxy API requests to the backend automatically.
