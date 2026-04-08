from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

import pandas as pd
from datasets import load_dataset

from .schema import PipelineConfig


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_raw_dataset(config: PipelineConfig) -> Tuple[pd.DataFrame, Path]:
    dataset = load_dataset(config.dataset_id, split=config.split)
    df = dataset.to_pandas()

    raw_dir = Path(config.raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=True)

    stamp = _utc_stamp()
    raw_file = raw_dir / f"zomato_raw_{stamp}.jsonl"
    with raw_file.open("w", encoding="utf-8") as handle:
        for record in df.to_dict(orient="records"):
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    return df, raw_file

