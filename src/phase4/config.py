from __future__ import annotations

import os
from pathlib import Path


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        key = key.strip().lstrip("\ufeff")
        value = value.strip().strip('"').strip("'")
        existing = os.environ.get(key, "").strip()
        if key and not existing:
            os.environ[key] = value


def load_llm_env() -> None:
    _load_env_file(Path(".env"))


def get_groq_api_key() -> str | None:
    load_llm_env()
    key = os.getenv("GROQ_API_KEY")
    if key:
        key = key.strip()
    return key or None


def get_groq_model() -> str:
    load_llm_env()
    return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant").strip()

