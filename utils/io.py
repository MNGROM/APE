"""Small filesystem helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_prompt_file(path: Path, *, label: str) -> str:
    if not path.exists():
        raise FileNotFoundError(f"{label} prompt file not found: {path}")
    text = read_text(path).strip()
    if not text:
        raise ValueError(f"{label} prompt file is empty: {path}")
    return text


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")
