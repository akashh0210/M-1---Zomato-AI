from __future__ import annotations

from fastapi import FastAPI, HTTPException

from phase2.schemas import RecommendationRequest, RecommendationResponse
from phase3.service import load_processed_data, recommend, get_all_locations, get_all_cuisines
from phase4.orchestrator import apply_llm_reranking
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="Restaurant Recommendation API", version="0.1.0")

ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
os.makedirs(ui_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=ui_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(ui_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "UI not built yet."}

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/locations")
def locations() -> dict[str, list[str]]:
    try:
        df = load_processed_data()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"locations": get_all_locations(df)}


@app.get("/cuisines")
def cuisines() -> dict[str, list[str]]:
    try:
        df = load_processed_data()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"cuisines": get_all_cuisines(df)}


@app.post("/recommendations", response_model=RecommendationResponse)
def recommendations(payload: RecommendationRequest) -> RecommendationResponse:
    try:
        df = load_processed_data()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    recommendations_list, suggestions, message = recommend(payload, df)
    if recommendations_list:
        recommendations_list = apply_llm_reranking(payload, recommendations_list)
        for idx, item in enumerate(recommendations_list, start=1):
            item.rank = idx
            
        cuisine_str = ", ".join(payload.cuisine) if isinstance(payload.cuisine, list) else payload.cuisine
        message = f"Best fit based on your budget ({payload.budget}) and cuisine preference ({cuisine_str})."
    return RecommendationResponse(
        query=payload,
        recommendations=recommendations_list,
        suggestions=suggestions,
        message=message,
    )

