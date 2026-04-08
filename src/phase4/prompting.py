from __future__ import annotations

import json
from typing import List

from phase2.schemas import RecommendationItem, RecommendationRequest


SYSTEM_PROMPT = (
    "You are a restaurant recommendation analyst. "
    "Use only provided candidates. Do not invent restaurants or fields. "
    "Return strict JSON only."
)


def build_user_prompt(
    request: RecommendationRequest,
    candidates: List[RecommendationItem],
) -> str:
    payload = {
        "user_preferences": {
            "location": request.location,
            "budget": request.budget,
            "cuisine": request.cuisine,
            "min_rating": request.min_rating,
            "additional_preferences": request.additional_preferences,
        },
        "candidates": [
            {
                "restaurant_name": item.restaurant_name,
                "location_city": item.location_city,
                "cuisines": item.cuisines,
                "rating": item.rating,
                "estimated_cost_for_two": item.estimated_cost_for_two,
                "baseline_explanation": item.explanation,
                "baseline_confidence": item.confidence,
            }
            for item in candidates
        ],
        "required_output_schema": {
            "recommendations": [
                {
                    "rank": "integer starting from 1",
                    "restaurant_name": "string, must match provided candidates exactly",
                    "rationale": "string, concise and grounded in candidate fields",
                    "tradeoffs": "string, concise limitation or caveat",
                    "confidence": "number between 0 and 1",
                }
            ]
        },
        "rules": [
            "Return exactly 5 recommendations in your JSON.",
            "Return only JSON. No markdown.",
            "All restaurant_name values must be from candidates.",
            "Do not exceed 220 chars for rationale.",
            "Do not exceed 160 chars for tradeoffs.",
        ],
    }
    return json.dumps(payload, ensure_ascii=True, separators=(",", ":"))

