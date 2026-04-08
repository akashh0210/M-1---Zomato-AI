from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Dict, Iterable, List

import pandas as pd

from .schema import ProcessedColumns, parse_optional_float

COLS = ProcessedColumns()


def _as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _pick_column(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    lower_map: Dict[str, str] = {str(col).strip().lower(): str(col) for col in df.columns}
    for candidate in candidates:
        if candidate in lower_map:
            return lower_map[candidate]
    return None


def _split_csv_like(text: str) -> List[str]:
    if not text:
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def _rating_to_float(value: object) -> float | None:
    parsed = parse_optional_float(value)
    if parsed is None:
        return None
    if parsed < 0 or parsed > 5:
        return None
    return round(parsed, 2)


def _cost_to_float(value: object) -> float | None:
    parsed = parse_optional_float(value)
    if parsed is None:
        return None
    if parsed < 0:
        return None
    return round(parsed, 2)


def _stable_key(name: str, location: str) -> str:
    raw = "|".join([name.lower(), location.lower()])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]


def normalize_restaurant_df(df: pd.DataFrame) -> pd.DataFrame:
    name_col = _pick_column(df, ["name", "restaurant_name", "restaurant name"])
    location_col = _pick_column(df, ["locality", "location", "city", "location_city"])
    cuisine_col = _pick_column(df, ["cuisine", "cuisines"])
    cost_col = _pick_column(
        df,
        ["average_cost_for_two", "cost_for_two", "cost", "approx_cost(for two people)"],
    )
    rating_col = _pick_column(df, ["rating", "aggregate_rating", "rate"])
    tags_col = _pick_column(
        df,
        ["additional_preferences", "tags", "metadata_tags", "rest_type", "listed_in(type)"],
    )

    if not all([name_col, location_col, cuisine_col, cost_col, rating_col]):
        missing = {
            "name": name_col,
            "location": location_col,
            "cuisine": cuisine_col,
            "cost": cost_col,
            "rating": rating_col,
        }
        raise ValueError(f"Could not map required columns from source dataset: {missing}")

    out = pd.DataFrame()
    out[COLS.restaurant_name] = df[name_col].map(_as_text)
    out[COLS.location_city] = df[location_col].map(_as_text)
    out[COLS.cuisines] = df[cuisine_col].map(_as_text).map(_split_csv_like)
    out[COLS.average_cost_for_two] = df[cost_col].map(_cost_to_float)
    out[COLS.rating] = df[rating_col].map(_rating_to_float)
    out[COLS.metadata_tags] = (
        df[tags_col].map(_as_text).map(_split_csv_like) if tags_col else [[] for _ in range(len(df))]
    )

    out = out[
        (out[COLS.restaurant_name] != "")
        & (out[COLS.location_city] != "")
        & (out[COLS.cuisines].map(len) > 0)
        & out[COLS.average_cost_for_two].notna()
        & out[COLS.rating].notna()
    ].copy()

    out[COLS.stable_key] = out.apply(
        lambda row: _stable_key(
            row[COLS.restaurant_name],
            row[COLS.location_city]
        ),
        axis=1,
    )
    out = out.sort_values(by=[COLS.rating], ascending=False)
    out = out.drop_duplicates(subset=[COLS.stable_key]).reset_index(drop=True)
    out[COLS.ingestion_ts_utc] = datetime.now(timezone.utc).isoformat()
    return out

