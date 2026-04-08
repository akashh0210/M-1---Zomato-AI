from __future__ import annotations

import json
from typing import Dict, List

from phase2.schemas import RecommendationItem, RecommendationRequest

from .config import get_groq_api_key, get_groq_model
from .groq_client import GroqClient
from .prompting import SYSTEM_PROMPT, build_user_prompt


def _truncate(text: str, limit: int) -> str:
    clean = text.strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def _parse_and_validate_llm_output(
    raw_text: str,
    candidate_map: Dict[str, RecommendationItem],
) -> List[dict]:
    parsed = json.loads(raw_text)
    recs = parsed.get("recommendations")
    if not isinstance(recs, list) or not recs:
        raise ValueError("LLM output missing recommendations list")

    valid_rows: List[dict] = []
    seen_names = set()
    for row in recs:
        if not isinstance(row, dict):
            continue
        name = str(row.get("restaurant_name", "")).strip()
        if name not in candidate_map or name in seen_names:
            continue
        confidence = row.get("confidence", 0.5)
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.5
        confidence = max(0.0, min(1.0, confidence))
        rationale = _truncate(str(row.get("rationale", "")), 220)
        tradeoffs = _truncate(str(row.get("tradeoffs", "")), 160)
        if not rationale:
            continue
        seen_names.add(name)
        valid_rows.append(
            {
                "restaurant_name": name,
                "rationale": rationale,
                "tradeoffs": tradeoffs,
                "confidence": confidence,
            }
        )

    if not valid_rows:
        raise ValueError("No valid LLM rows after validation")
    return valid_rows


def apply_llm_reranking(
    request: RecommendationRequest,
    deterministic_recommendations: List[RecommendationItem],
) -> List[RecommendationItem]:
    if len(deterministic_recommendations) <= 1:
        return deterministic_recommendations

    api_key = get_groq_api_key()
    if not api_key:
        return deterministic_recommendations

    model = get_groq_model()
    candidate_map = {item.restaurant_name: item for item in deterministic_recommendations}
    try:
        client = GroqClient(api_key=api_key, model=model)
        user_prompt = build_user_prompt(request, deterministic_recommendations)
        raw_output = client.complete_json(SYSTEM_PROMPT, user_prompt)
        rows = _parse_and_validate_llm_output(raw_output, candidate_map)
    except Exception:
        # Guardrail fallback: deterministic phase 3 ranking remains source of truth.
        return deterministic_recommendations[:5]

    reranked: List[RecommendationItem] = []
    for idx, row in enumerate(rows, start=1):
        base = candidate_map[row["restaurant_name"]]
        explanation = row["rationale"]
        if row["tradeoffs"]:
            explanation = f"{row['rationale']} Tradeoff: {row['tradeoffs']}"
        reranked.append(
            RecommendationItem(
                rank=idx,
                restaurant_name=base.restaurant_name,
                location_city=base.location_city,
                cuisines=base.cuisines,
                rating=base.rating,
                estimated_cost_for_two=base.estimated_cost_for_two,
                explanation=explanation,
                confidence=round(row["confidence"], 2),
            )
        )

    existing = {item.restaurant_name for item in reranked}
    for item in deterministic_recommendations:
        if item.restaurant_name in existing:
            continue
        reranked.append(
            RecommendationItem(
                rank=len(reranked) + 1,
                restaurant_name=item.restaurant_name,
                location_city=item.location_city,
                cuisines=item.cuisines,
                rating=item.rating,
                estimated_cost_for_two=item.estimated_cost_for_two,
                explanation=item.explanation,
                confidence=item.confidence,
            )
        )
    return reranked[:5]

