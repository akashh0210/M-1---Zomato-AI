from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from phase1.pipeline import run_phase1_pipeline
from phase1.schema import PipelineConfig


def main() -> None:
    result = run_phase1_pipeline(PipelineConfig())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

