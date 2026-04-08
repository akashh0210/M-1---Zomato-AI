from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from phase2.main import app

client = TestClient(app)


def test_recommendations_accepts_valid_payload() -> None:
    payload = {
        "location": "Bangalore",
        "budget": 1500.0,
        "cuisine": "north indian",
        "min_rating": 3.8,
        "additional_preferences": "family-friendly",
    }
    response = client.post("/recommendations", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "query" in data


def test_recommendations_rejects_invalid_budget() -> None:
    payload = {
        "location": "Bangalore",
        "budget": -100.0,
        "cuisine": "north indian",
        "min_rating": 3.8,
    }
    response = client.post("/recommendations", json=payload)
    assert response.status_code == 422


def test_recommendations_rejects_invalid_min_rating() -> None:
    payload = {
        "location": "Bangalore",
        "budget": 1500.0,
        "cuisine": "north indian",
        "min_rating": 8.2,
    }
    response = client.post("/recommendations", json=payload)
    assert response.status_code == 422

