"""LATO dataset loading and sampling."""

from __future__ import annotations

import dataclasses
import json
import random
from collections import Counter
from pathlib import Path

from utils.io import write_text


@dataclasses.dataclass
class Case:
    dataset: str
    case_id: str
    content: str
    gold_plantuml: str


def load_cases(datasets_dir: Path) -> dict[str, list[Case]]:
    datasets: dict[str, list[Case]] = {}
    for path in sorted(datasets_dir.glob("*.jsonl")):
        name = path.stem.lower()
        cases: list[Case] = []
        with path.open(encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                payload = json.loads(line)
                content = str(payload.get("content") or "").strip()
                plantuml = str(payload.get("plantuml") or "").strip()
                if not content or not plantuml:
                    continue
                cases.append(Case(dataset=name, case_id=f"{name}-{idx:04d}", content=content, gold_plantuml=plantuml))
        datasets[name] = cases
    if not datasets:
        raise FileNotFoundError(f"No .jsonl datasets found under {datasets_dir}")
    return datasets


def grouped_cases(cases: list[Case]) -> dict[str, list[Case]]:
    groups: dict[str, list[Case]] = {}
    for case in cases:
        groups.setdefault(case.dataset, []).append(case)
    return groups


def select_cases_with_strategy(
    cases: list[Case],
    *,
    limit: int | None,
    strategy: str,
    seed: int,
) -> list[Case]:
    if limit is None or limit <= 0 or limit >= len(cases):
        return list(cases)

    strategy = strategy.lower()
    if strategy == "prefix":
        return cases[:limit]

    rng = random.Random(seed)
    if strategy == "random":
        selected = list(cases)
        rng.shuffle(selected)
        return selected[:limit]

    if strategy != "stratified":
        raise ValueError(f"Unknown sample strategy {strategy!r}")

    groups = grouped_cases(cases)
    dataset_names = sorted(groups)
    if limit < len(dataset_names):
        dataset_names = rng.sample(dataset_names, limit)
    selected_by_dataset: dict[str, list[Case]] = {name: [] for name in dataset_names}
    remaining = limit

    base_quota = max(1, limit // max(1, len(dataset_names)))
    for name in dataset_names:
        pool = list(groups[name])
        rng.shuffle(pool)
        take = min(base_quota, len(pool), remaining)
        selected_by_dataset[name].extend(pool[:take])
        remaining -= take
        groups[name] = pool[take:]
        if remaining <= 0:
            break

    while remaining > 0:
        available = [name for name in dataset_names if groups[name]]
        if not available:
            break
        for name in available:
            selected_by_dataset[name].append(groups[name].pop(0))
            remaining -= 1
            if remaining <= 0:
                break

    selected: list[Case] = []
    max_len = max((len(items) for items in selected_by_dataset.values()), default=0)
    for idx in range(max_len):
        for name in dataset_names:
            items = selected_by_dataset[name]
            if idx < len(items):
                selected.append(items[idx])
    return selected[:limit]


def describe_case_distribution(cases: list[Case]) -> str:
    counts = Counter(case.dataset for case in cases)
    return ", ".join(f"{name}={counts[name]}" for name in sorted(counts)) or "empty"


def write_case_manifest(path: Path, cases: list[Case]) -> None:
    payload = [
        {
            "dataset": case.dataset,
            "case_id": case.case_id,
        }
        for case in cases
    ]
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2))
