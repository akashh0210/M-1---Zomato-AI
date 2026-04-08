from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from phase2.schemas import RecommendationItem, RecommendationRequest
from phase4.orchestrator import apply_llm_reranking


def _baseline_items() -> list[RecommendationItem]:
    return [
        RecommendationItem(
            rank=1,
            restaurant_name="Alpha Spice",
            location_city="bangalore",
            cuisines=["north indian", "chinese"],
            rating=4.5,
            estimated_cost_for_two=1200.0,
            explanation="Baseline A",
            confidence=0.9,
        ),
        RecommendationItem(
            rank=2,
            restaurant_name="Budget Bites",
            location_city="bangalore",
            cuisines=["north indian"],
            rating=4.4,
            estimated_cost_for_two=1100.0,
            explanation="Baseline B",
            confidence=0.88,
        ),
    ]


def _request() -> RecommendationRequest:
    return RecommendationRequest(
        location="bangalore",
        budget=1500.0,
        cuisine=["north indian"],
        min_rating=4.0,
        additional_preferences=["family-friendly"],
    )


def test_phase4_fallback_without_api_key(monkeypatch) -> None:
    monkeypatch.setattr("phase4.orchestrator.get_groq_api_key", lambda: None)
    original = _baseline_items()
    reranked = apply_llm_reranking(_request(), original)
    assert [x.restaurant_name for x in reranked] == [x.restaurant_name for x in original]
    assert [x.explanation for x in reranked] == [x.explanation for x in original]


def test_phase4_uses_llm_when_available(monkeypatch) -> None:
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    class FakeClient:
        def __init__(self, api_key: str, model: str) -> None:
            self.api_key = api_key
            self.model = model

        def complete_json(self, system_prompt: str, user_prompt: str) -> str:
            return (
                '{"recommendations":['
                '{"rank":1,"restaurant_name":"Budget Bites","rationale":"Better budget fit.","tradeoffs":"Slightly fewer cuisines.","confidence":0.82},'
                '{"rank":2,"restaurant_name":"Alpha Spice","rationale":"Great overall quality.","tradeoffs":"Higher average cost.","confidence":0.78}'
                "]} "
            )

    monkeypatch.setattr("phase4.orchestrator.GroqClient", FakeClient)

    reranked = apply_llm_reranking(_request(), _baseline_items())
    assert reranked[0].restaurant_name == "Budget Bites"
    assert "Tradeoff:" in reranked[0].explanation
    assert reranked[0].confidence == 0.82

