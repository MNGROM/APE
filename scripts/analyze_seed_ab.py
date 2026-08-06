"""Analyze a fixed Seed Prompt A/B experiment without model calls."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.prompt_hash import (  # noqa: E402
    PROMPT_HASH_NORMALIZATION_VERSION,
    prompt_file_sha256,
)


DATASETS = ("bp", "fsd", "lmc", "pure", "rac", "us")
CONDITIONS = ("baseline", "candidate-a", "candidate-b")
REPEATS = (1, 2, 3)
METRICS = (
    "llm_node_f1",
    "llm_node_recall",
    "llm_node_precision",
    "llm_relation_f1",
    "plantuml_compilation_pass_rate",
)
DELTA_THRESHOLD = 0.01
TIE_THRESHOLD = 0.005


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_directory(results_root: Path, repeat: int, condition: str) -> Path:
    suffix = re.compile(
        rf"__seed-ab-r{repeat}-{re.escape(condition)}(?:__\d+)?$"
    )
    matches = sorted(
        path
        for path in results_root.iterdir()
        if path.is_dir() and suffix.search(path.name)
    )
    if len(matches) != 1:
        raise ValueError(
            f"Expected one run for repeat={repeat} condition={condition}, "
            f"found {len(matches)} under {results_root}"
        )
    return matches[0]


def validate_run_args(
    run_dir: Path,
    *,
    case_concurrency: int,
    expected_provider: str | None = None,
) -> None:
    args_path = run_dir / "run_args.json"
    args = json.loads(args_path.read_text(encoding="utf-8"))
    if "case_concurrency" not in args:
        raise ValueError(f"Missing case_concurrency in {args_path}")
    actual_concurrency = int(args["case_concurrency"])
    if actual_concurrency != case_concurrency:
        raise ValueError(
            f"Expected case_concurrency={case_concurrency} in {args_path}, "
            f"found {actual_concurrency}"
        )
    if "temperature" not in args or float(args["temperature"]) != 0.0:
        raise ValueError(f"Expected temperature=0 in {args_path}")
    provider = str(args.get("llm_provider", "zhipu") or "zhipu").strip().lower()
    if provider not in {"zhipu", "deepseek"}:
        raise ValueError(f"Unsupported llm_provider={provider!r} in {args_path}")
    if expected_provider and provider != expected_provider:
        raise ValueError(
            f"Provider mismatch in {args_path}: expected={expected_provider} actual={provider}"
        )
    if "do_sample" not in args:
        raise ValueError(f"Missing do_sample in {args_path}")
    do_sample = args["do_sample"]
    if provider == "deepseek" and do_sample is not None:
        raise ValueError(f"DeepSeek run must omit do_sample in {args_path}; found {do_sample!r}")
    if provider == "zhipu" and str(do_sample).lower() != "false":
        raise ValueError(f"Expected do_sample=false for Zhipu run in {args_path}")


def validate_prompt_hash(
    run_dir: Path,
    expected_prompt: Path,
    *,
    condition: str,
    repeat: int,
) -> None:
    expected = prompt_file_sha256(expected_prompt)
    prompt_used = run_dir / "prompt_used.md"
    actual = prompt_file_sha256(prompt_used)
    if actual != expected:
        raise ValueError(
            "Prompt hash mismatch: "
            f"repeat={repeat} condition={condition} run={run_dir} "
            f"expected={expected} actual={actual} "
            f"normalization={PROMPT_HASH_NORMALIZATION_VERSION}"
        )

    manifest_path = run_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        recorded = manifest.get("prompt_sha256")
        if recorded and str(recorded) != actual:
            raise ValueError(
                f"Manifest Prompt hash mismatch in {manifest_path}: "
                f"recorded={recorded} actual={actual}"
            )
        normalization = manifest.get("prompt_hash_normalization")
        if normalization and str(normalization) != PROMPT_HASH_NORMALIZATION_VERSION:
            raise ValueError(
                f"Unsupported Prompt hash normalization in {manifest_path}: "
                f"{normalization}"
            )


def load_rows(run_dir: Path) -> dict[str, dict[str, float]]:
    overview_path = run_dir / "baseline_overview.csv"
    with overview_path.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    if {row.get("dataset") for row in raw_rows} != set(DATASETS):
        raise ValueError(f"Incomplete dataset rows in {overview_path}")

    required = (
        "count",
        *METRICS,
        "infrastructure_error_rate",
        "llm_element_evaluated",
        "llm_element_failed",
    )
    rows: dict[str, dict[str, float]] = {}
    for raw in raw_rows:
        dataset = str(raw["dataset"])
        try:
            rows[dataset] = {key: float(raw[key]) for key in required}
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid semantic measurement for dataset={dataset} "
                f"in {overview_path}"
            ) from exc
    return rows


def validate_case_manifests(
    run_dir: Path,
    expected_hashes: dict[str, str],
    *,
    cases_per_dataset: int,
) -> None:
    for dataset in DATASETS:
        manifest = run_dir / dataset / "test_cases.json"
        cases = json.loads(manifest.read_text(encoding="utf-8"))
        if len(cases) != cases_per_dataset:
            raise ValueError(
                f"Expected {cases_per_dataset} cases in {manifest}, found {len(cases)}"
            )
        digest = sha256(manifest)
        previous = expected_hashes.setdefault(dataset, digest)
        if previous != digest:
            raise ValueError(
                f"Case manifest mismatch for dataset={dataset}: "
                f"expected={previous} actual={digest}"
            )


def weighted_metric(rows: dict[str, dict[str, float]], metric: str) -> float:
    total_count = sum(rows[dataset]["count"] for dataset in DATASETS)
    if total_count <= 0:
        raise ValueError("A/B run has no evaluated cases")
    return sum(
        rows[dataset][metric] * rows[dataset]["count"] for dataset in DATASETS
    ) / total_count


def measurements_complete(rows: dict[str, dict[str, float]], cases_per_dataset: int) -> bool:
    return all(
        row["count"] == float(cases_per_dataset)
        and row["llm_element_evaluated"] == row["count"]
        and row["llm_element_failed"] == 0.0
        and all(math.isfinite(row[metric]) for metric in METRICS)
        for row in rows.values()
    )


def infrastructure_clean(rows: dict[str, dict[str, float]]) -> bool:
    return all(row["infrastructure_error_rate"] == 0.0 for row in rows.values())


def candidate_result(
    condition: str,
    runs: dict[tuple[int, str], dict[str, dict[str, float]]],
    *,
    cases_per_dataset: int,
) -> dict[str, Any]:
    repeat_deltas: dict[str, list[float]] = {metric: [] for metric in METRICS}
    for repeat in REPEATS:
        baseline = runs[(repeat, "baseline")]
        candidate = runs[(repeat, condition)]
        for metric in METRICS:
            repeat_deltas[metric].append(
                weighted_metric(candidate, metric) - weighted_metric(baseline, metric)
            )

    mean_deltas = {
        metric: sum(deltas) / len(deltas)
        for metric, deltas in repeat_deltas.items()
    }
    wins = {
        metric: sum(delta > 0.0 for delta in deltas)
        for metric, deltas in repeat_deltas.items()
    }
    dataset_node_f1_deltas = {
        dataset: sum(
            runs[(repeat, condition)][dataset]["llm_node_f1"]
            - runs[(repeat, "baseline")][dataset]["llm_node_f1"]
            for repeat in REPEATS
        )
        / len(REPEATS)
        for dataset in DATASETS
    }
    positive_dataset_strata = sum(
        delta > 0.0 for delta in dataset_node_f1_deltas.values()
    )
    all_rows = [
        runs[(repeat, condition)] for repeat in REPEATS
    ] + [runs[(repeat, "baseline")] for repeat in REPEATS]
    complete = all(
        measurements_complete(rows, cases_per_dataset) for rows in all_rows
    )
    infra_clean = all(infrastructure_clean(rows) for rows in all_rows)

    criteria = {
        "node_f1_mean_delta_gt_0_01": mean_deltas["llm_node_f1"] > DELTA_THRESHOLD,
        "node_f1_wins_3_of_3": wins["llm_node_f1"] == 3,
        "node_recall_mean_delta_gt_0_01": mean_deltas["llm_node_recall"] > DELTA_THRESHOLD,
        "node_recall_wins_3_of_3": wins["llm_node_recall"] == 3,
        "node_precision_non_regression": mean_deltas["llm_node_precision"] >= -DELTA_THRESHOLD,
        "relation_f1_non_regression": mean_deltas["llm_relation_f1"] >= -DELTA_THRESHOLD,
        "compile_non_regression": mean_deltas["plantuml_compilation_pass_rate"] >= -DELTA_THRESHOLD,
        "node_f1_positive_in_at_least_4_of_6_datasets": positive_dataset_strata >= 4,
        "semantic_measurements_complete": complete,
        "infrastructure_error_rate_zero": infra_clean,
    }
    return {
        "condition": condition,
        "eligible": all(criteria.values()),
        "criteria": criteria,
        "repeat_deltas": repeat_deltas,
        "mean_deltas": mean_deltas,
        "wins": wins,
        "dataset_node_f1_mean_deltas": dataset_node_f1_deltas,
        "positive_dataset_strata": positive_dataset_strata,
        "selection_score": min(
            mean_deltas["llm_node_f1"], mean_deltas["llm_relation_f1"]
        ),
    }


def choose_winner(results: dict[str, dict[str, Any]]) -> tuple[str, str]:
    eligible = [name for name, result in results.items() if result["eligible"]]
    if not eligible:
        return "baseline", "Neither candidate met every admission criterion."
    if len(eligible) == 1:
        winner = eligible[0]
        return winner, f"Only {winner} met every admission criterion."
    score_a = float(results["candidate-a"]["selection_score"])
    score_b = float(results["candidate-b"]["selection_score"])
    if abs(score_a - score_b) < TIE_THRESHOLD:
        return "candidate-a", "Both passed and the score gap was below 0.005."
    winner = "candidate-a" if score_a > score_b else "candidate-b"
    return winner, "Both passed; the higher minimum Node/Relation F1 delta won."


def render_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Seed Prompt A/B Analysis",
        "",
        f"- recommendation: {payload['recommendation']}",
        f"- rationale: {payload['rationale']}",
        "- tracked seed modified: no",
        f"- prompt hash normalization: {payload['prompt_hash_normalization']}",
        "",
        "| candidate | eligible | node_f1_delta | node_f1_wins | node_recall_delta | node_recall_wins | relation_f1_delta | compile_delta | positive_strata | score |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for condition in ("candidate-a", "candidate-b"):
        result = payload["candidate_results"][condition]
        mean = result["mean_deltas"]
        wins = result["wins"]
        lines.append(
            f"| {condition} | {str(result['eligible']).lower()} | "
            f"{mean['llm_node_f1']:.6f} | {wins['llm_node_f1']}/3 | "
            f"{mean['llm_node_recall']:.6f} | {wins['llm_node_recall']}/3 | "
            f"{mean['llm_relation_f1']:.6f} | "
            f"{mean['plantuml_compilation_pass_rate']:.6f} | "
            f"{result['positive_dataset_strata']}/6 | {result['selection_score']:.6f} |"
        )
    lines.extend(["", "## Criteria", ""])
    for condition in ("candidate-a", "candidate-b"):
        lines.extend([f"### {condition}", ""])
        for name, passed in payload["candidate_results"][condition]["criteria"].items():
            lines.append(f"- {name}: {str(passed).lower()}")
        lines.append("")
    lines.extend(
        [
            "The recommendation is an experiment result only. Update",
            "`prompt_workspace/tst.md` separately after review.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a fixed Seed Prompt A/B run without model calls."
    )
    parser.add_argument("--experiment-root", type=Path, required=True)
    parser.add_argument("--inputs-root", type=Path, required=True)
    parser.add_argument("--cases-per-dataset", type=int, default=10)
    parser.add_argument("--case-concurrency", type=int, default=10)
    args = parser.parse_args()
    if args.cases_per_dataset < 1:
        parser.error("--cases-per-dataset must be positive")
    if args.case_concurrency < 1:
        parser.error("--case-concurrency must be positive")

    experiment_root = args.experiment_root.resolve()
    results_root = experiment_root / "results"
    inputs_root = args.inputs_root.resolve()
    prompt_inputs = {
        "baseline": inputs_root / "baseline.md",
        "candidate-a": inputs_root / "candidate_a.md",
        "candidate-b": inputs_root / "candidate_b.md",
    }
    for path in prompt_inputs.values():
        if not path.is_file():
            raise FileNotFoundError(f"Missing Prompt input: {path}")

    design_manifest_path = experiment_root / "design_manifest.json"
    design_manifest = (
        json.loads(design_manifest_path.read_text(encoding="utf-8"))
        if design_manifest_path.exists()
        else {}
    )
    recorded_hashes = design_manifest.get("prompt_sha256", {})
    expected_provider = str(design_manifest.get("provider", "") or "").strip().lower() or None
    if expected_provider is not None and expected_provider not in {"zhipu", "deepseek"}:
        raise ValueError(f"Unsupported provider in {design_manifest_path}: {expected_provider!r}")
    for condition, path in prompt_inputs.items():
        actual = prompt_file_sha256(path)
        recorded = recorded_hashes.get(condition)
        if recorded and str(recorded) != actual:
            raise ValueError(
                f"Design manifest Prompt hash mismatch for {condition}: "
                f"recorded={recorded} actual={actual}"
            )

    runs: dict[tuple[int, str], dict[str, dict[str, float]]] = {}
    run_paths: dict[str, str] = {}
    case_hashes: dict[str, str] = {}
    for repeat in REPEATS:
        for condition in CONDITIONS:
            run_dir = run_directory(results_root, repeat, condition)
            validate_run_args(
                run_dir,
                case_concurrency=args.case_concurrency,
                expected_provider=expected_provider,
            )
            validate_prompt_hash(
                run_dir,
                prompt_inputs[condition],
                condition=condition,
                repeat=repeat,
            )
            runs[(repeat, condition)] = load_rows(run_dir)
            run_paths[f"repeat_{repeat}:{condition}"] = str(run_dir)
            validate_case_manifests(
                run_dir,
                case_hashes,
                cases_per_dataset=args.cases_per_dataset,
            )

    candidate_results = {
        condition: candidate_result(
            condition,
            runs,
            cases_per_dataset=args.cases_per_dataset,
        )
        for condition in ("candidate-a", "candidate-b")
    }
    recommendation, rationale = choose_winner(candidate_results)
    payload = {
        "schema_version": "seed-prompt-ab-analysis-v2",
        "recommendation": recommendation,
        "rationale": rationale,
        "formal_seed_modified": False,
        "prompt_hash_normalization": PROMPT_HASH_NORMALIZATION_VERSION,
        "candidate_results": candidate_results,
        "case_manifest_sha256": case_hashes,
        "run_paths": run_paths,
    }
    (experiment_root / "analysis.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (experiment_root / "analysis.md").write_text(
        render_report(payload), encoding="utf-8"
    )
    print(f"[seed-ab] recommendation: {recommendation}")
    print(f"[seed-ab] analysis: {experiment_root / 'analysis.md'}")


if __name__ == "__main__":
    main()
