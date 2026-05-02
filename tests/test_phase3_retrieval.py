from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from phase2.schemas import RecommendationRequest
from phase3.service import recommend


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "restaurant_name": "Alpha Spice",
                "location_city": "bangalore",
                "cuisines": ["north indian", "chinese"],
                "average_cost_for_two": 1200.0,
                "rating": 4.6,
                "metadata_tags": ["family-friendly", "quick service"],
            },
            {
                "restaurant_name": "Budget Bites",
                "location_city": "bangalore",
                "cuisines": ["north indian"],
                "average_cost_for_two": 1800.0,
                "rating": 4.7,
                "metadata_tags": ["casual dining"],
            },
            {
                "restaurant_name": "City Dosa",
                "location_city": "bangalore",
                "cuisines": ["south indian"],
                "average_cost_for_two": 900.0,
                "rating": 4.8,
                "metadata_tags": ["quick service"],
            },
            {
                "restaurant_name": "Delhi Delight",
                "location_city": "delhi",
                "cuisines": ["north indian", "mughlai"],
                "average_cost_for_two": 1300.0,
                "rating": 4.9,
                "metadata_tags": ["family-friendly"],
            },
        ]
    )


def test_hard_filters_exclude_wrong_location_budget_and_rating() -> None:
    request = RecommendationRequest(
        location="bangalore",
        budget=2000.0,
        cuisine=["north indian"],
        min_rating=4.65,
        additional_preferences=["family-friendly"],
    )
    recommendations, suggestions, message = recommend(request, _sample_df())
    assert suggestions == []
    assert message is None
    assert len(recommendations) == 1
    assert recommendations[0].restaurant_name == "Budget Bites"


def test_soft_scoring_prefers_cuisine_cost_and_preference_fit() -> None:
    request = RecommendationRequest(
        location="bangalore",
        budget=2000.0,
        cuisine=["north indian", "chinese"],
        min_rating=4.0,
        additional_preferences=["family-friendly", "quick service"],
    )
    recommendations, suggestions, message = recommend(request, _sample_df())
    assert suggestions == []
    assert message is None
    assert len(recommendations) >= 2
    assert recommendations[0].restaurant_name == "Alpha Spice"
    assert "Composite score:" in recommendations[0].explanation


def test_returns_cuisine_suggestions_when_cuisine_not_found() -> None:
    request = RecommendationRequest(
        location="bangalore",
        budget=2000.0,
        cuisine=["chines"],
        min_rating=3.0,
        additional_preferences=None,
    )
    recommendations, suggestions, message = recommend(request, _sample_df())
    assert recommendations == []
    assert message is not None
    assert any(s.lower() == "chinese" for s in suggestions)

