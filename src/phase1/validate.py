from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict

import pandas as pd

from .schema import ProcessedColumns

COLS = ProcessedColumns()


@dataclass
class QualityReport:
    total_rows: int
    duplicate_stable_keys: int
    missing_rate_by_column: Dict[str, float]
    invalid_rating_count: int
    invalid_cost_count: int
    outlier_cost_count: int
    outlier_rating_count: int


def _missing_rate(df: pd.DataFrame, col: str) -> float:
    if col not in df:
        return 1.0
    return round(float(df[col].isna().mean()), 4)


def build_quality_report(df: pd.DataFrame) -> QualityReport:
    duplicate_keys = int(df.duplicated(subset=[COLS.stable_key]).sum())
    invalid_rating = int(((df[COLS.rating] < 0) | (df[COLS.rating] > 5)).sum())
    invalid_cost = int((df[COLS.average_cost_for_two] < 0).sum())
    outlier_cost = int((df[COLS.average_cost_for_two] > 20000).sum())
    outlier_rating = int((df[COLS.rating] > 5).sum())

    report = QualityReport(
        total_rows=int(len(df)),
        duplicate_stable_keys=duplicate_keys,
        missing_rate_by_column={
            COLS.restaurant_name: _missing_rate(df, COLS.restaurant_name),
            COLS.location_city: _missing_rate(df, COLS.location_city),
            COLS.cuisines: _missing_rate(df, COLS.cuisines),
            COLS.average_cost_for_two: _missing_rate(df, COLS.average_cost_for_two),
            COLS.rating: _missing_rate(df, COLS.rating),
            COLS.metadata_tags: _missing_rate(df, COLS.metadata_tags),
        },
        invalid_rating_count=invalid_rating,
        invalid_cost_count=invalid_cost,
        outlier_cost_count=outlier_cost,
        outlier_rating_count=outlier_rating,
    )
    return report


def report_as_dict(report: QualityReport) -> Dict[str, object]:
    return asdict(report)

