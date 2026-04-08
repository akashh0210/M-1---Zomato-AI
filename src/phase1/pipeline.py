from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .ingest import load_raw_dataset
from .schema import PipelineConfig
from .transform import normalize_restaurant_df
from .validate import build_quality_report, report_as_dict


def run_phase1_pipeline(config: PipelineConfig | None = None) -> Dict[str, str]:
    cfg = config or PipelineConfig()

    processed_dir = Path(cfg.processed_dir)
    reports_dir = Path(cfg.reports_dir)
    processed_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    raw_df, raw_file = load_raw_dataset(cfg)
    normalized_df = normalize_restaurant_df(raw_df)
    quality_report = build_quality_report(normalized_df)

    parquet_path = processed_dir / cfg.output_parquet
    report_path = reports_dir / cfg.output_quality_report

    normalized_df.to_parquet(parquet_path, index=False)
    report_path.write_text(
        json.dumps(report_as_dict(quality_report), indent=2),
        encoding="utf-8",
    )

    return {
        "raw_file": str(raw_file),
        "processed_file": str(parquet_path),
        "quality_report": str(report_path),
        "rows_after_cleaning": str(len(normalized_df)),
    }

