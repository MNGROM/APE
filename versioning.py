"""Run directory and prompt-version file management."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from utils.io import read_text, write_text


def make_run_dir(runs_dir: Path, label: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    base_name = f"{timestamp}__{label}"
    for suffix in ["", *[f"__{idx}" for idx in range(2, 100)]]:
        run_dir = runs_dir / f"{base_name}{suffix}"
        try:
            run_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            continue
        return run_dir
    raise FileExistsError(f"Could not create a unique run directory for {base_name!r}")


def initialize_run_prompt(seed_prompt_path: Path, run_dir: Path) -> Path:
    work_prompt_path = run_dir / "work.md"
    seed_prompt = read_text(seed_prompt_path)
    write_text(work_prompt_path, seed_prompt)
    write_text(run_dir / "prompt_initial.md", seed_prompt)
    print(f"[prompt] copied seed prompt to run-local work file: {work_prompt_path}")
    return work_prompt_path


def write_run_args(args: argparse.Namespace, run_dir: Path) -> None:
    public_args: dict[str, Any] = {}
    for key, value in sorted(vars(args).items()):
        if key in {"api_key", "llm_judge_api_key"}:
            public_args[f"{key}_present"] = bool(value)
        elif isinstance(value, Path):
            public_args[key] = str(value)
        else:
            public_args[key] = value
    write_text(run_dir / "run_args.json", json.dumps(public_args, ensure_ascii=False, indent=2))
