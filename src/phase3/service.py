from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import pandas as pd

from phase2.schemas import RecommendationItem, RecommendationRequest

DATA_FILE = Path("data/processed/restaurants.parquet")


def get_all_locations(df: pd.DataFrame) -> List[str]:
    if "location_city" not in df.columns:
        return []
    return sorted([str(loc).strip() for loc in df["location_city"].dropna().unique() if str(loc).strip()])


def _to_list(value: str | List[str]) -> List[str]:
    return [value] if isinstance(value, str) else value


def get_all_cuisines(df: pd.DataFrame) -> List[str]:
    unique_values = set()
    for items in df["cuisines"].tolist():
        if isinstance(items, list):
            for item in items:
                if item:
                    unique_values.add(str(item).strip().title())
    return sorted(unique_values)


def _normalize_cuisine_list(values: str | Sequence[str]) -> List[str]:
    if isinstance(values, str):
        values = [values]
    out: List[str] = []
    for value in values:
        parts = [part.strip().title() for part in str(value).split(",") if part.strip()]
        out.extend(parts)
    return out


def load_processed_data(path: Path = DATA_FILE) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            "Processed data not found. Run `python scripts/run_phase1.py` first."
        )
    df = pd.read_parquet(path)
    if "cuisines" in df.columns:
        df["cuisines"] = df["cuisines"].apply(
            lambda v: _normalize_cuisine_list(v) if not isinstance(v, list) else _normalize_cuisine_list(v)
        )
    return df


def _contains_any(haystack: Iterable[str], needles: Iterable[str]) -> bool:
    hset = {item.lower() for item in haystack}
    return any(needle.lower() in hset for needle in needles)


def _overlap_ratio(haystack: Iterable[str], needles: Iterable[str]) -> float:
    hset = {item.lower() for item in haystack}
    nset = {item.lower() for item in needles}
    if not nset:
        return 0.0
    return len(hset.intersection(nset)) / len(nset)


def _match_location(df: pd.DataFrame, location: str) -> pd.DataFrame:
    return df[df["location_city"].astype(str).str.lower() == location.strip().lower()].copy()


def _match_budget(df: pd.DataFrame, budget: float) -> pd.DataFrame:
    return df[df["average_cost_for_two"] <= budget * 1.2].copy()


def _build_explanation(row: pd.Series, request: RecommendationRequest) -> str:
    cuisine_text = ", ".join(row["cuisines"][:3])
    return (
        f"Matches your location in {row['location_city']}, fits the {request.budget} budget band, "
        f"offers {cuisine_text}, and has a strong rating of {row['rating']}. "
        f"Composite score: {row['score']:.3f}."
    )


def _preference_to_list(value: str | List[str] | None) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [item.strip().lower() for item in value.split(",") if item.strip()]
    return [str(item).strip().lower() for item in value if str(item).strip()]


def _cost_fit_score(cost: float, target_budget: float) -> float:
    if cost <= target_budget:
        return max(0.0, 1.0 - ((target_budget - cost) / max(target_budget, 1.0)) * 0.5)
    overshoot = cost - target_budget
    penalty = overshoot / max(target_budget * 0.2, 1.0)
    return max(0.0, 1.0 - penalty)


def _preference_match_score(row: pd.Series, preferences: List[str]) -> float:
    if not preferences:
        return 0.0
    tokens = {
        str(row.get("restaurant_name", "")).lower(),
        str(row.get("location_city", "")).lower(),
    }
    for cuisine in row.get("cuisines", []):
        tokens.add(str(cuisine).lower())
    for tag in row.get("metadata_tags", []):
        tokens.add(str(tag).lower())

    matches = 0
    for pref in preferences:
        if any(pref in token for token in tokens):
            matches += 1
    return matches / len(preferences)


def _apply_soft_scoring(
    candidates: pd.DataFrame,
    cuisine_targets: List[str],
    preferences: List[str],
    budget: float,
) -> pd.DataFrame:
    scored = candidates.copy()
    scored["cuisine_similarity"] = scored["cuisines"].apply(
        lambda cuisines: _overlap_ratio(cuisines, cuisine_targets)
    )
    scored["preference_match"] = scored.apply(
        lambda row: _preference_match_score(row, preferences),
        axis=1,
    )
    scored["rating_score"] = (scored["rating"] / 5.0).clip(lower=0.0, upper=1.0)
    scored["cost_fit_score"] = scored["average_cost_for_two"].apply(
        lambda cost: _cost_fit_score(float(cost), budget)
    )
    scored["score"] = (
        (0.45 * scored["rating_score"])
        + (0.25 * scored["cuisine_similarity"])
        + (0.20 * scored["cost_fit_score"])
        + (0.10 * scored["preference_match"])
    )
    return scored.sort_values(
        by=["score", "rating", "average_cost_for_two"],
        ascending=[False, False, True],
    )


def recommend(
    request: RecommendationRequest,
    df: pd.DataFrame,
) -> Tuple[List[RecommendationItem], List[str], str | None]:
    cuisine_targets = _to_list(request.cuisine)
    additional_preferences = _preference_to_list(request.additional_preferences)
    
    location_df = _match_location(df, request.location)
    if location_df.empty:
        top_cities = [str(city) for city in df["location_city"].value_counts().head(5).index]
        return [], top_cities, f"Location '{request.location}' not found. Try one of these popular cities."

    budget_df = _match_budget(location_df, request.budget)
    if budget_df.empty:
        return [], [], f"No restaurants found for budget '{request.budget}' in '{request.location}'. Consider broadening your budget filter."

    rating_df = budget_df[budget_df["rating"] >= request.min_rating].copy()

    if rating_df.empty:
        suggestions: List[str] = []
        known = get_all_cuisines(df)
        for cuisine in cuisine_targets:
            suggestions.extend(get_close_matches(cuisine.lower(), known, n=3, cutoff=0.75))
        deduped_suggestions = sorted(set(suggestions))
        return [], deduped_suggestions, "No exact matches found for current filters."

    filtered = rating_df[
        rating_df["cuisines"].apply(lambda cuisines: _contains_any(cuisines, cuisine_targets))
    ].copy()

    if filtered.empty:
        known = get_all_cuisines(df)
        suggestions = []
        for cuisine in cuisine_targets:
            suggestions.extend(get_close_matches(cuisine.lower(), known, n=5, cutoff=0.6))
        return [], sorted(set(suggestions)), "No cuisine match found; try suggested cuisines."

    ranked = _apply_soft_scoring(
        candidates=filtered,
        cuisine_targets=cuisine_targets,
        preferences=additional_preferences,
        budget=request.budget,
    ).head(50)

    recommendations: List[RecommendationItem] = []
    for idx, (_, row) in enumerate(ranked.iterrows(), start=1):
        confidence = max(0.1, min(1.0, float(row["rating"]) / 5.0))
        recommendations.append(
            RecommendationItem(
                rank=idx,
                restaurant_name=str(row["restaurant_name"]),
                location_city=str(row["location_city"]),
                cuisines=[str(item) for item in row["cuisines"]],
                rating=float(row["rating"]),
                estimated_cost_for_two=float(row["average_cost_for_two"]),
                explanation=_build_explanation(row, request),
                confidence=round(confidence, 2),
            )
        )
    return recommendations, [], None

