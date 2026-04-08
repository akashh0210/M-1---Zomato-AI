from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PipelineConfig:
    dataset_id: str = "ManikaSaini/zomato-restaurant-recommendation"
    split: str = "train"
    raw_dir: str = "data/raw"
    processed_dir: str = "data/processed"
    reports_dir: str = "data/reports"
    output_parquet: str = "restaurants.parquet"
    output_quality_report: str = "quality_report.json"


@dataclass(frozen=True)
class ProcessedColumns:
    restaurant_name: str = "restaurant_name"
    location_city: str = "location_city"
    cuisines: str = "cuisines"
    average_cost_for_two: str = "average_cost_for_two"
    rating: str = "rating"
    metadata_tags: str = "metadata_tags"
    stable_key: str = "stable_key"
    ingestion_ts_utc: str = "ingestion_ts_utc"


def parse_optional_float(value: object) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    filtered = "".join(ch for ch in text if ch.isdigit() or ch in ".-")
    if not filtered:
        return None
    try:
        return float(filtered)
    except ValueError:
        return None

