"""Evaluate the seed prompt on every LATO dataset without training."""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any

from ape_datasets.lato import describe_case_distribution, load_cases, select_cases_with_strategy, write_case_manifest
from config import (
    DEFAULT_BASE_URL,
    DEFAULT_DATASETS_DIR,
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_MODEL,
    DEFAULT_PLANTUML_JAR,
    DEFAULT_PROMPT_PATH,
    DEFAULT_THINKING_TYPE,
    PROJECT_DIR,
    optional_bool,
    optional_float,
)
from analysis.failure_analysis import build_analysis
from evaluation import evaluate_cases
from metrics import DEFAULT_EMBEDDING_MODEL, format_summary
from reporting import refresh_run_reports
from run import make_llm_client, resolve_agent_thinking, resolve_model_roles
from utils.io import read_prompt_file, write_text
from versioning import make_run_dir, write_run_args


DEFAULT_BASELINE_RUNS_DIR = PROJECT_DIR / "seed_prompt_runs"
DEFAULT_DATASETS = ("bp", "fsd", "lmc", "pure", "rac", "us")
OVERVIEW_COLUMNS = (
    "dataset",
    "count",
    "node_precision",
    "node_recall",
    "node_f1",
    "relation_precision",
    "relation_recall",
    "relation_f1",
    "llm_node_precision",
    "llm_node_recall",
    "llm_node_f1",
    "llm_relation_precision",
    "llm_relation_recall",
    "llm_relation_f1",
    "syntax_pass_rate",
    "plantuml_compilation_pass_rate",
    "infrastructure_error_rate",
    "llm_element_evaluated",
    "llm_element_failed",
    "summary_path",
)


def parse_dataset_names(value: str) -> list[str]:
    names = [item.strip().lower() for item in value.split(",") if item.strip()]
    if not names:
        raise argparse.ArgumentTypeError("expected at least one dataset name")
    if names == ["all"]:
        return list(DEFAULT_DATASETS)
    return names


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Evaluate prompt_workspace/tst.md as a fixed iteration_000 baseline on LATO datasets.",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_BASELINE_RUNS_DIR, help="Directory for seed baseline logs")
    parser.add_argument("--run-name", default="seed-tst-baseline", help="Run label appended after the timestamp")
    parser.add_argument("--prompt-path", type=Path, default=DEFAULT_PROMPT_PATH)
    parser.add_argument("--datasets-dir", type=Path, default=DEFAULT_DATASETS_DIR)
    parser.add_argument("--datasets", type=parse_dataset_names, default=list(DEFAULT_DATASETS), help="Comma-separated dataset names, or 'all'")
    parser.add_argument("--max-test-cases", type=int, default=0, help="0 means all cases for each dataset")
    parser.add_argument("--test-sample-strategy", choices=["stratified", "random", "prefix"], default="prefix")
    parser.add_argument("--sample-seed", type=int, default=13)

    parser.add_argument("--model", default=os.environ.get("ZHIPU_LLM_MODEL", DEFAULT_MODEL), help="Legacy fallback model for all roles")
    parser.add_argument("--generation-model", default=os.environ.get("ZHIPU_LLM_GENERATION_MODEL"), help="Model used for PlantUML prediction; defaults to --model")
    parser.add_argument("--agent-model", default=os.environ.get("ZHIPU_LLM_AGENT_MODEL"), help="Compatibility role for the shared APE client; defaults to --model")
    parser.add_argument("--judge-model", default=os.environ.get("ZHIPU_LLM_JUDGE_MODEL"), help="Model used for semantic judging; defaults to --model")
    parser.add_argument("--api-key", default=os.environ.get("ZHIPU_LLM_API_KEY", ""))
    parser.add_argument("--base-url", default=os.environ.get("ZHIPU_LLM_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=optional_float, default=None, help="GLM top_p, or 'omit' to use provider default")
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--thinking", choices=["enabled", "disabled"], default=os.environ.get("ZHIPU_THINKING_TYPE", DEFAULT_THINKING_TYPE))
    parser.add_argument("--generation-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_GENERATION_THINKING_TYPE", "inherit"))
    parser.add_argument("--judge-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_JUDGE_THINKING_TYPE", "inherit"))
    parser.add_argument("--element-extraction-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_ELEMENT_EXTRACTION_THINKING_TYPE", "inherit"))
    parser.add_argument(
        "--do-sample",
        type=optional_bool,
        default=False,
        help="GLM sampling mode; defaults to false, true enables sampling, and 'omit' uses the provider default",
    )
    parser.add_argument("--llm-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-max-retries", type=int, default=20)
    parser.add_argument("--llm-rate-limit-initial-wait", type=int, default=30)
    parser.add_argument("--llm-rate-limit-max-wait", type=int, default=600)

    parser.add_argument("--plantuml-jar", type=Path, default=DEFAULT_PLANTUML_JAR)
    parser.add_argument("--plantuml-compile-timeout", type=int, default=30)
    parser.add_argument("--node-match-threshold", type=float, default=0.85)
    parser.add_argument("--relation-match-threshold", type=float, default=0.85)
    parser.add_argument("--semantic-embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--metric-matcher", choices=["embedding", "difflib"], default="embedding")
    parser.add_argument("--element-extractor", choices=["rule", "llm", "auto"], default=os.environ.get("APE_ELEMENT_EXTRACTOR", "llm"))
    parser.add_argument("--element-extraction-temperature", type=float, default=0.0)
    parser.add_argument("--element-extraction-max-tokens", type=int, default=4096)
    parser.add_argument("--element-extraction-max-retries", type=int, default=3)
    parser.add_argument("--llm-element-metrics", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--llm-judge-temperature", type=float, default=0.0)
    parser.add_argument("--llm-judge-max-tokens", type=int, default=4096)
    parser.add_argument("--llm-judge-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-judge-max-retries", type=int, default=3)
    parser.add_argument("--mock-with-gold", action="store_true", help="Use ground truth PlantUML as predictions for a cheap smoke test")
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if args.max_test_cases < 0:
        raise ValueError("--max-test-cases must be non-negative")
    if args.max_tokens < 1:
        raise ValueError("--max-tokens must be positive")
    if args.top_p is not None and not (0.01 <= args.top_p <= 0.99):
        raise ValueError("--top-p must be between 0.01 and 0.99, or 'omit'")
    if args.llm_max_retries < 0:
        raise ValueError("--llm-max-retries must be non-negative")
    if args.llm_judge_max_tokens < 1:
        raise ValueError("--llm-judge-max-tokens must be positive")
    if args.llm_judge_max_retries < 1:
        raise ValueError("--llm-judge-max-retries must be positive")
    if args.element_extraction_max_tokens < 1:
        raise ValueError("--element-extraction-max-tokens must be positive")
    if args.element_extraction_max_retries < 1:
        raise ValueError("--element-extraction-max-retries must be positive")
    if not args.mock_with_gold and not args.api_key:
        raise ValueError("Seed prompt evaluation requires ZHIPU_LLM_API_KEY or --api-key unless --mock-with-gold is used")
    if args.llm_element_metrics and not args.api_key:
        raise ValueError("LLM semantic element metrics require ZHIPU_LLM_API_KEY or --api-key")
    if args.element_extractor == "llm" and not args.api_key:
        raise ValueError("LLM element extraction requires ZHIPU_LLM_API_KEY or --api-key")


def prepare_args(args: argparse.Namespace) -> None:
    args.output_dir = args.output_dir.resolve()
    args.prompt_path = args.prompt_path.resolve()
    args.datasets_dir = args.datasets_dir.resolve()
    args.plantuml_jar = args.plantuml_jar.resolve()
    args.generation_thinking = resolve_agent_thinking(args.generation_thinking, args.thinking)
    args.judge_thinking = resolve_agent_thinking(args.judge_thinking, args.thinking)
    args.element_extraction_thinking = resolve_agent_thinking(args.element_extraction_thinking, args.thinking)
    resolve_model_roles(args)
    args.llm_judge_api_key = args.api_key
    args.llm_judge_base_url = args.base_url
    args.llm_judge_thinking = args.judge_thinking


def metric_value(summary: dict[str, Any], key: str) -> float:
    value = summary.get(key, 0.0)
    return float(value or 0.0)


def overview_row(dataset: str, dataset_dir: Path, run_dir: Path, summary: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {"dataset": dataset}
    for key in OVERVIEW_COLUMNS:
        if key in {"dataset", "summary_path"}:
            continue
        row[key] = metric_value(summary, key)
    row["summary_path"] = (dataset_dir / "iteration_000" / "test" / "summary.json").relative_to(run_dir).as_posix()
    return row


def write_overview(run_dir: Path, rows: list[dict[str, Any]]) -> None:
    csv_path = run_dir / "baseline_overview.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OVERVIEW_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in OVERVIEW_COLUMNS})

    lines = [
        "# Seed Prompt Baseline Overview",
        "",
        "| dataset | count | node_f1 | relation_f1 | llm_node_f1 | llm_relation_f1 | syntax | compile | summary |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {dataset} | {count:.0f} | {node_f1:.4f} | {relation_f1:.4f} | "
            "{llm_node_f1:.4f} | {llm_relation_f1:.4f} | {syntax_pass_rate:.4f} | "
            "{plantuml_compilation_pass_rate:.4f} | `{summary_path}` |".format(**row)
        )
    write_text(run_dir / "baseline_overview.md", "\n".join(lines) + "\n")


def write_manifest(run_dir: Path, args: argparse.Namespace, rows: list[dict[str, Any]]) -> None:
    payload = {
        "mode": "seed_prompt_baseline",
        "prompt": "prompt_used.md",
        "datasets": [row["dataset"] for row in rows],
        "overview": {
            "csv": "baseline_overview.csv",
            "markdown": "baseline_overview.md",
        },
        "dataset_summaries": {row["dataset"]: row["summary_path"] for row in rows},
        "config": {
            "element_extractor": args.element_extractor,
            "llm_element_metrics": args.llm_element_metrics,
            "metric_matcher": args.metric_matcher,
            "max_test_cases": args.max_test_cases,
            "test_sample_strategy": args.test_sample_strategy,
        },
    }
    write_text(run_dir / "manifest.json", json.dumps(payload, ensure_ascii=False, indent=2))


def evaluate_seed_dataset(
    *,
    prompt: str,
    cases: list[Any],
    dataset: str,
    args: argparse.Namespace,
    llm_client: Any,
    dataset_dir: Path,
) -> dict[str, float]:
    iter_dir = dataset_dir / "iteration_000"
    test_dir = iter_dir / "test"
    write_text(iter_dir / "prompts" / "before.md", prompt)
    write_text(iter_dir / "prompts" / "after.md", prompt)
    write_text(
        iter_dir / "manifest.json",
        json.dumps(
            {
                "iteration": 0,
                "mode": "seed_prompt_baseline",
                "dataset": dataset,
                "inputs": {
                    "prompt": "prompts/after.md",
                    "cases": "../test_cases.json",
                },
                "outputs": {
                    "records": "test/records.jsonl",
                    "summary": "test/summary.json",
                    "analysis": "test/analysis.md",
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    write_text(
        test_dir / "manifest.json",
        json.dumps(
            {
                "dataset": dataset,
                "inputs": {
                    "prompt": "../prompts/after.md",
                    "cases": "../../test_cases.json",
                },
                "outputs": {
                    "records": "records.jsonl",
                    "summary": "summary.json",
                    "analysis": "analysis.md",
                },
            },
            ensure_ascii=False,
            indent=2,
        ),
    )
    records, summary = evaluate_cases(
        prompt=prompt,
        cases=cases,
        args=args,
        llm_client=llm_client,
        output_path=test_dir / "records.jsonl",
        state_dir=dataset_dir,
        phase=f"iteration_000:{dataset}:seed_baseline",
    )
    write_text(test_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    write_text(test_dir / "analysis.md", build_analysis(records, summary))
    refresh_run_reports(dataset_dir)
    return summary


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    prepare_args(args)
    validate_args(args)

    prompt = read_prompt_file(args.prompt_path, label="seed")
    datasets = load_cases(args.datasets_dir)
    missing = [name for name in args.datasets if name not in datasets]
    if missing:
        raise ValueError(f"Unknown dataset(s): {', '.join(missing)}. Available: {', '.join(sorted(datasets))}")

    run_dir = make_run_dir(args.output_dir, args.run_name)
    write_run_args(args, run_dir)
    write_text(run_dir / "prompt_used.md", prompt)
    write_text(run_dir / "prompt_initial.md", prompt)
    write_text(run_dir / "prompt_final.md", prompt)
    print(f"[baseline] output: {run_dir}")
    print(f"[baseline] prompt: {args.prompt_path}")

    llm_client = make_llm_client(args)
    rows: list[dict[str, Any]] = []
    for dataset in args.datasets:
        all_cases = datasets[dataset]
        cases = select_cases_with_strategy(
            all_cases,
            limit=args.max_test_cases,
            strategy=args.test_sample_strategy,
            seed=args.sample_seed + 20_000,
        )
        dataset_dir = run_dir / dataset
        write_run_args(args, dataset_dir)
        write_text(dataset_dir / "prompt_initial.md", prompt)
        write_text(dataset_dir / "prompt_final.md", prompt)
        write_text(dataset_dir / "prompt_used.md", prompt)
        write_case_manifest(dataset_dir / "test_cases.json", cases)
        print(f"\n[baseline:{dataset}] cases={len(cases)} distribution={describe_case_distribution(cases)}")
        summary = evaluate_seed_dataset(
            prompt=prompt,
            cases=cases,
            dataset=dataset,
            args=args,
            llm_client=llm_client,
            dataset_dir=dataset_dir,
        )
        print(f"[baseline:{dataset}] {format_summary(summary)}")
        rows.append(overview_row(dataset, dataset_dir, run_dir, summary))
        write_overview(run_dir, rows)
        write_manifest(run_dir, args, rows)

    write_overview(run_dir, rows)
    write_manifest(run_dir, args, rows)
    print(f"\n[baseline] overview: {run_dir / 'baseline_overview.md'}")


if __name__ == "__main__":
    main()
