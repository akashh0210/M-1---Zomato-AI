from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from phase2.api.main import app
from phase2.api.schemas import RecommendationItem, RecommendationRequest
from phase4.llm.config import get_groq_api_key, get_groq_model
from phase4.llm.groq_client import GroqClient
from phase4.llm.orchestrator import apply_llm_reranking


def test_1_env_key_present() -> bool:
    key = get_groq_api_key()
    ok = bool(key and len(key) > 10)
    print(f"TEST 1 - .env key loaded: {'PASS' if ok else 'FAIL'}")
    return ok


def test_2_direct_groq_connectivity() -> bool:
    key = get_groq_api_key()
    if not key:
        print("TEST 2 - direct Groq call: FAIL (missing GROQ_API_KEY)")
        return False
    client = GroqClient(api_key=key, model=get_groq_model())
    try:
        raw = client.complete_json(
            "Return JSON only.",
            '{"task":"return {\\\"ok\\\":true,\\\"message\\\":\\\"groq connected\\\"} as json"}',
        )
        parsed = json.loads(raw)
        ok = isinstance(parsed, dict)
        print(f"TEST 2 - direct Groq call: {'PASS' if ok else 'FAIL'}")
        return ok
    except Exception as exc:
        print(f"TEST 2 - direct Groq call: FAIL ({exc})")
        return False


def test_3_orchestrator_rerank() -> bool:
    req = RecommendationRequest(
        location="bangalore",
        budget="medium",
        cuisine=["north indian", "chinese"],
        min_rating=3.5,
        additional_preferences=["family-friendly", "quick service"],
        top_n=2,
    )
    base = [
        RecommendationItem(
            rank=1,
            restaurant_name="Alpha Spice",
            location_city="bangalore",
            cuisines=["north indian", "chinese"],
            rating=4.5,
            estimated_cost_for_two=1200.0,
            explanation="Matches your location. Composite score: 0.900.",
            confidence=0.9,
        ),
        RecommendationItem(
            rank=2,
            restaurant_name="Budget Bites",
            location_city="bangalore",
            cuisines=["north indian"],
            rating=4.4,
            estimated_cost_for_two=1000.0,
            explanation="Matches your location. Composite score: 0.860.",
            confidence=0.86,
        ),
    ]
    try:
        out = apply_llm_reranking(req, base)
        ok = len(out) == 2 and all(0 <= item.confidence <= 1 for item in out)
        print(f"TEST 3 - orchestrator rerank call: {'PASS' if ok else 'FAIL'}")
        return ok
    except Exception as exc:
        print(f"TEST 3 - orchestrator rerank call: FAIL ({exc})")
        return False


def test_4_api_recommendations_endpoint() -> bool:
    client = TestClient(app)
    payload = {
        "location": "whitefield",
        "budget": "medium",
        "cuisine": ["north indian", "chinese"],
        "min_rating": 3.8,
        "additional_preferences": ["family-friendly", "quick service"],
        "top_n": 3,
    }
    try:
        response = client.post("/recommendations", json=payload)
        if response.status_code != 200:
            print(f"TEST 4 - /recommendations API call: FAIL (status={response.status_code})")
            return False
        body = response.json()
        recs = body.get("recommendations", [])
        ok = isinstance(recs, list) and len(recs) > 0
        print(f"TEST 4 - /recommendations API call: {'PASS' if ok else 'FAIL'}")
        return ok
    except Exception as exc:
        print(f"TEST 4 - /recommendations API call: FAIL ({exc})")
        return False


if __name__ == "__main__":
    results = [
        test_1_env_key_present(),
        test_2_direct_groq_connectivity(),
        test_3_orchestrator_rerank(),
        test_4_api_recommendations_endpoint(),
    ]
    passed = sum(1 for result in results if result)
    total = len(results)
    print(f"\nRESULT: {passed}/{total} tests passed")
    raise SystemExit(0 if passed == total else 1)

