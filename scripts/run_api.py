from __future__ import annotations

import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import os
from phase1.pipeline import run_phase1_pipeline
from phase3.service import DATA_FILE

if __name__ == "__main__":
    # Ensure data exists for the API to run
    if not DATA_FILE.exists():
        print(f"Data file {DATA_FILE} not found. Running phase 1 pipeline...")
        run_phase1_pipeline()
    else:
        print(f"Data file {DATA_FILE} found. Starting API.")

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("phase2.main:app", host="0.0.0.0", port=port, reload=False)
