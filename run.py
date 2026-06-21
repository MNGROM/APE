#!/usr/bin/env python3
"""Entry point for APE prompt evolution."""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import random
from pathlib import Path
from typing import Any

from analysis.error_localization import localize_errors
from analysis.failure_analysis import analyze_failures, build_analysis
from analysis.prompt_editor import propose_prompt_revision
from analysis.prompt_rewriter import rewrite_prompt
from config import (
    DEFAULT_BASE_URL,
    DEFAULT_DATASETS_DIR,
    DEFAULT_ERROR_LOCALIZATION_PROMPT_PATH,
    DEFAULT_FAILURE_ANALYSIS_PROMPT_PATH,
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_MODEL,
    DEFAULT_PLANTUML_JAR,
    DEFAULT_PROMPT_EDITOR_PROMPT_PATH,
    DEFAULT_PROMPT_REWRITER_PROMPT_PATH,
    DEFAULT_PROMPT_PATH,
    DEFAULT_RUNS_DIR,
    DEFAULT_THINKING_TYPE,
    SECTION_NAMES,
    optional_bool,
    optional_float,
)
from ape_datasets.lato import (
    Case,
    describe_case_distribution,
    load_cases,
    select_cases_with_strategy,
    write_case_manifest,
)
from evaluation import evaluate_cases, has_only_infrastructure_errors
from llm import LLMClient
from metrics import DEFAULT_EMBEDDING_MODEL, EvaluationRecord, format_summary, summarize_records
from reporting import refresh_run_reports, write_iteration_reports
from utils.io import read_prompt_file, read_text, write_text
from versioning import initialize_run_prompt, make_run_dir, write_run_args


def validate_glm_args(args: argparse.Namespace) -> None:
    thinking_fields = (
        "thinking",
        "generation_thinking",
        "analysis_thinking",
        "localization_thinking",
        "editor_thinking",
        "judge_thinking",
        "element_extraction_thinking",
    )
    for field in thinking_fields:
        if getattr(args, field) not in {"enabled", "disabled"}:
            raise ValueError(f"--{field.replace('_', '-')} must resolve to 'enabled' or 'disabled' according to the GLM Chat Completions API")
    if args.max_tokens < 1:
        raise ValueError("--max-tokens must be positive")
    if args.top_p is not None and not (0.01 <= args.top_p <= 0.99):
        raise ValueError("--top-p must be between 0.01 and 0.99, or 'omit'")
    if args.top_p is not None:
        print("[config] Both temperature and top_p are set; GLM docs recommend adjusting only one.", flush=True)
    if args.max_prompt_growth_ratio < 0.0:
        raise ValueError("--max-prompt-growth-ratio must be non-negative; 0 disables the growth-ratio gate")
    if args.max_prompt_chars < 1000:
        raise ValueError("--max-prompt-chars is too small for the required prompt sections")
    if args.llm_max_retries < 0:
        raise ValueError("--llm-max-retries must be non-negative")
    if args.analysis_batch_size < 1 or args.gate_batch_size < 1:
        raise ValueError("--analysis-batch-size and --gate-batch-size must be positive")
    if args.max_sections_per_edit < 0 or args.max_sections_per_edit > len(SECTION_NAMES):
        raise ValueError("--max-sections-per-edit must be 0 (unlimited) or between 1 and the number of fixed prompt sections")
    if args.analysis_max_tokens < 1 or args.localization_max_tokens < 1 or args.editor_max_tokens < 1:
        raise ValueError("--analysis-max-tokens, --localization-max-tokens, and --editor-max-tokens must be positive")
    if args.llm_judge_max_tokens < 1:
        raise ValueError("--llm-judge-max-tokens must be positive")
    if args.llm_judge_max_retries < 1:
        raise ValueError("--llm-judge-max-retries must be positive")
    if args.element_extraction_max_tokens < 1:
        raise ValueError("--element-extraction-max-tokens must be positive")
    if args.element_extraction_max_retries < 1:
        raise ValueError("--element-extraction-max-retries must be positive")
    if args.llm_element_metrics and not args.api_key:
        raise ValueError("LLM semantic element metrics require the main API key via ZHIPU_LLM_API_KEY or --api-key")
    if args.acceptance_metric_source == "llm" and not args.llm_element_metrics:
        raise ValueError("--acceptance-metric-source llm requires --llm-element-metrics")
    if args.element_extractor == "llm" and not args.api_key:
        raise ValueError("LLM element extraction requires the main API key via ZHIPU_LLM_API_KEY or --api-key")


def make_llm_client(args: argparse.Namespace) -> LLMClient:
    return LLMClient(
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        thinking=args.thinking,
        do_sample=args.do_sample,
        timeout=args.llm_timeout,
        max_retries=args.llm_max_retries,
        retry_initial_wait=args.llm_rate_limit_initial_wait,
        retry_max_wait=args.llm_rate_limit_max_wait,
    )


def resolve_agent_thinking(value: str | None, fallback: str) -> str:
    if value is None or value == "inherit":
        return fallback
    return value


def choose_iteration_batch(
    train_cases: list[Case],
    *,
    args: argparse.Namespace,
    iteration: int,
    batch_size: int,
    strategy: str,
    seed_offset: int,
) -> list[Case]:
    if batch_size <= 0 or batch_size >= len(train_cases):
        return list(train_cases)
    return select_cases_with_strategy(
        train_cases,
        limit=batch_size,
        strategy=strategy,
        seed=args.sample_seed + seed_offset + iteration,
    )


def order_cases_for_epoch(cases: list[Case], *, strategy: str, seed: int) -> list[Case]:
    strategy = strategy.lower()
    if strategy == "prefix":
        return list(cases)

    rng = random.Random(seed)
    if strategy == "random":
        ordered = list(cases)
        rng.shuffle(ordered)
        return ordered

    if strategy != "stratified":
        raise ValueError(f"Unknown sample strategy {strategy!r}")

    groups: dict[str, list[Case]] = {}
    for case in cases:
        groups.setdefault(case.dataset, []).append(case)
    for group in groups.values():
        rng.shuffle(group)

    ordered: list[Case] = []
    dataset_names = sorted(groups)
    while True:
        added = False
        for name in dataset_names:
            if groups[name]:
                ordered.append(groups[name].pop(0))
                added = True
        if not added:
            break
    return ordered


def make_epoch_batches(
    train_cases: list[Case],
    *,
    args: argparse.Namespace,
    iteration: int,
) -> list[list[Case]]:
    ordered = order_cases_for_epoch(
        train_cases,
        strategy=args.sample_strategy,
        seed=args.sample_seed + 30_000 + iteration,
    )
    batch_size = args.analysis_batch_size
    return [ordered[idx : idx + batch_size] for idx in range(0, len(ordered), batch_size)]


def acceptance_decision(
    *,
    iteration: int,
    bootstrap_allowed: bool,
    baseline_summary: dict[str, float],
    candidate_summary: dict[str, float],
    candidate_prompt: str,
    baseline_prompt: str,
    max_prompt_growth_ratio: float,
    max_prompt_chars: int,
    min_relation_delta: float,
    min_node_delta: float,
    min_compile_delta: float,
    relation_accept_delta: float,
    node_accept_delta: float,
    compile_accept_delta: float,
    metric_source: str,
) -> tuple[bool, dict[str, Any]]:
    compile_delta = candidate_summary.get("plantuml_compilation_pass_rate", 0.0) - baseline_summary.get("plantuml_compilation_pass_rate", 0.0)
    deterministic_node_delta = candidate_summary.get("node_f1", 0.0) - baseline_summary.get("node_f1", 0.0)
    deterministic_relation_delta = candidate_summary.get("relation_f1", 0.0) - baseline_summary.get("relation_f1", 0.0)
    llm_node_delta = candidate_summary.get("llm_node_f1", 0.0) - baseline_summary.get("llm_node_f1", 0.0)
    llm_relation_delta = candidate_summary.get("llm_relation_f1", 0.0) - baseline_summary.get("llm_relation_f1", 0.0)
    node_metric_key, relation_metric_key = acceptance_metric_keys(metric_source, candidate_summary)
    node_delta = candidate_summary.get(node_metric_key, 0.0) - baseline_summary.get(node_metric_key, 0.0)
    relation_delta = candidate_summary.get(relation_metric_key, 0.0) - baseline_summary.get(relation_metric_key, 0.0)
    infrastructure_delta = candidate_summary.get("infrastructure_error_rate", 0.0) - baseline_summary.get("infrastructure_error_rate", 0.0)
    prompt_growth_ratio = len(candidate_prompt) / max(1, len(baseline_prompt))
    prompt_growth_ok = max_prompt_growth_ratio <= 0.0 or prompt_growth_ratio <= max_prompt_growth_ratio
    prompt_size_ok = len(candidate_prompt) <= max_prompt_chars and prompt_growth_ok
    llm_metrics_available = candidate_summary.get("llm_element_evaluated", 0.0) > 0 and baseline_summary.get("llm_element_evaluated", 0.0) > 0
    llm_semantic_guard_ok = True
    if metric_source == "hybrid" and llm_metrics_available:
        llm_semantic_guard_ok = not (
            (llm_node_delta < -node_accept_delta and llm_relation_delta < -relation_accept_delta)
            or llm_relation_delta < -0.10
            or (compile_delta < 0 and (llm_node_delta < 0 or llm_relation_delta < 0))
        )

    safety_gate = {
        "compile_not_significantly_worse": compile_delta >= min_compile_delta,
        "node_not_significantly_worse": node_delta >= min_node_delta,
        "relation_not_significantly_worse": relation_delta >= min_relation_delta,
        "semantic_metrics_not_both_down": not (node_delta < 0 and relation_delta < 0),
        "llm_semantic_guard_ok": llm_semantic_guard_ok,
        "infrastructure_delta_ok": infrastructure_delta <= 0,
        "prompt_size_ok": prompt_size_ok,
    }
    benefit_gate = {
        "relation_improved": relation_delta >= relation_accept_delta,
        "node_improved": node_delta >= node_accept_delta,
        "compile_improved_without_semantic_regression": compile_delta >= compile_accept_delta and node_delta >= 0 and relation_delta >= 0,
    }
    bootstrap_prompt_size_ok = len(candidate_prompt) <= max_prompt_chars
    bootstrap_gate = {
        "allowed": bootstrap_allowed,
        "is_first_iteration": iteration == 1,
        "node_improved": node_delta >= node_accept_delta,
        "relation_improved": relation_delta >= relation_accept_delta,
        "infrastructure_delta_ok": infrastructure_delta <= 0,
        "prompt_chars_ok": bootstrap_prompt_size_ok,
    }
    standard_accept = all(safety_gate.values()) and any(benefit_gate.values())
    bootstrap_accept = all(bootstrap_gate.values())
    accept = standard_accept or bootstrap_accept
    rejection_reasons = [] if accept else [
        name
        for name, ok in {
            "standard_safety_gate": all(safety_gate.values()),
            "has_required_metric_benefit": any(benefit_gate.values()),
            "bootstrap_gate": bootstrap_accept,
        }.items()
        if not ok
    ]
    return accept, {
        "accepted": accept,
        "metric_deltas": {
            "plantuml_compilation_pass_rate": compile_delta,
            "node_f1": deterministic_node_delta,
            "relation_f1": deterministic_relation_delta,
            "llm_node_f1": llm_node_delta,
            "llm_relation_f1": llm_relation_delta,
            "infrastructure_error_rate": infrastructure_delta,
        },
        "acceptance_metric_source": metric_source,
        "acceptance_node_metric": node_metric_key,
        "acceptance_relation_metric": relation_metric_key,
        "compile_delta": compile_delta,
        "node_delta": node_delta,
        "relation_delta": relation_delta,
        "deterministic_node_delta": deterministic_node_delta,
        "deterministic_relation_delta": deterministic_relation_delta,
        "llm_node_delta": llm_node_delta,
        "llm_relation_delta": llm_relation_delta,
        "infrastructure_delta": infrastructure_delta,
        "min_compile_delta": min_compile_delta,
        "min_node_delta": min_node_delta,
        "min_relation_delta": min_relation_delta,
        "relation_accept_delta": relation_accept_delta,
        "node_accept_delta": node_accept_delta,
        "compile_accept_delta": compile_accept_delta,
        "safety_gate": safety_gate,
        "benefit_gate": benefit_gate,
        "bootstrap_gate": bootstrap_gate,
        "standard_accept": standard_accept,
        "bootstrap_accept": bootstrap_accept,
        "acceptance_mode": "standard" if standard_accept else "bootstrap" if bootstrap_accept else "rejected",
        "rejection_reasons": rejection_reasons,
        "acceptance_policy": "standard: accept when every safety gate passes and at least one selected metric benefit gate passes; bootstrap: only before the first accepted prompt update in iteration 1, accept when selected node and relation metrics both improve enough, infrastructure is not worse, and prompt size is ok",
        "prompt_chars_before": len(baseline_prompt),
        "prompt_chars_candidate": len(candidate_prompt),
        "prompt_growth_ratio": prompt_growth_ratio,
        "max_prompt_growth_ratio": max_prompt_growth_ratio,
        "prompt_growth_ratio_ok": prompt_growth_ok,
        "max_prompt_chars": max_prompt_chars,
        "prompt_size_ok": prompt_size_ok,
        "baseline_summary": baseline_summary,
        "candidate_summary": candidate_summary,
    }


def acceptance_metric_keys(metric_source: str, candidate_summary: dict[str, float]) -> tuple[str, str]:
    if metric_source == "deterministic":
        return "node_f1", "relation_f1"
    if metric_source == "llm":
        return "llm_node_f1", "llm_relation_f1"
    if metric_source == "hybrid":
        llm_available = candidate_summary.get("llm_element_evaluated", 0.0) > 0
        return ("llm_node_f1", "llm_relation_f1") if llm_available else ("node_f1", "relation_f1")
    raise ValueError(f"Unsupported acceptance metric source: {metric_source}")


def metric_priority_key(summary: dict[str, float]) -> tuple[float, float, float, float]:
    return (
        -summary.get("infrastructure_error_rate", 0.0),
        summary.get("relation_f1", 0.0),
        summary.get("node_f1", 0.0),
        summary.get("plantuml_compilation_pass_rate", 0.0),
    )


def iteration_paths(iter_dir: Path) -> dict[str, Path]:
    return {
        "manifest": iter_dir / "manifest.json",
        "prompt_before": iter_dir / "prompts" / "before.md",
        "prompt_candidate": iter_dir / "prompts" / "candidate.md",
        "prompt_after": iter_dir / "prompts" / "after.md",
        "analysis_cases": iter_dir / "batches" / "analysis_cases.json",
        "gate_cases": iter_dir / "batches" / "gate_cases.json",
        "analysis_records": iter_dir / "evaluation" / "analysis_records.jsonl",
        "analysis_summary": iter_dir / "evaluation" / "analysis_summary.json",
        "analysis_overview": iter_dir / "evaluation" / "analysis_overview.md",
        "gate_candidate_records": iter_dir / "evaluation" / "gate_candidate_records.jsonl",
        "gate_candidate_summary": iter_dir / "evaluation" / "gate_candidate_summary.json",
        "gate_baseline_records": iter_dir / "evaluation" / "gate_baseline_records.jsonl",
        "gate_baseline_summary": iter_dir / "evaluation" / "gate_baseline_summary.json",
        "acceptance": iter_dir / "decision" / "acceptance.json",
        "rejected_by_gate": iter_dir / "decision" / "rejected_by_gate.json",
        "update_skipped": iter_dir / "decision" / "update_skipped.txt",
    }


def held_out_paths(iter_dir: Path) -> dict[str, Path]:
    test_dir = iter_dir / "held_out_test"
    return {
        "manifest": test_dir / "manifest.json",
        "cases": test_dir / "cases.json",
        "records": test_dir / "records.jsonl",
        "summary": test_dir / "summary.json",
        "analysis": test_dir / "analysis.md",
    }


def epoch_batch_paths(iter_dir: Path, batch_index: int) -> dict[str, Path]:
    batch_dir = iter_dir / "train_batches" / f"batch_{batch_index:03d}"
    return {
        "dir": batch_dir,
        "manifest": batch_dir / "manifest.json",
        "prompt_before": batch_dir / "prompts" / "before.md",
        "prompt_candidate": batch_dir / "prompts" / "candidate.md",
        "prompt_after": batch_dir / "prompts" / "after.md",
        "cases": batch_dir / "cases.json",
        "records": batch_dir / "evaluation" / "analysis_records.jsonl",
        "summary": batch_dir / "evaluation" / "analysis_summary.json",
        "overview": batch_dir / "evaluation" / "analysis_overview.md",
        "failure_analysis_input": batch_dir / "agents" / "failure_analysis.input.json",
        "failure_analysis_output": batch_dir / "agents" / "failure_analysis.output.json",
        "error_localization_input": batch_dir / "agents" / "error_localization.input.json",
        "error_localization_output": batch_dir / "agents" / "error_localization.output.json",
        "prompt_editor_input": batch_dir / "agents" / "prompt_editor.input.json",
        "prompt_editor_output": batch_dir / "agents" / "prompt_editor.output.json",
        "prompt_rewriter_input": batch_dir / "agents" / "prompt_rewriter.input.json",
        "prompt_rewriter_output": batch_dir / "agents" / "prompt_rewriter.output.json",
        "gate_cases": batch_dir / "gate" / "cases.json",
        "gate_baseline_records": batch_dir / "gate" / "baseline_records.jsonl",
        "gate_baseline_summary": batch_dir / "gate" / "baseline_summary.json",
        "gate_candidate_records": batch_dir / "gate" / "candidate_records.jsonl",
        "gate_candidate_summary": batch_dir / "gate" / "candidate_summary.json",
        "acceptance": batch_dir / "decision" / "acceptance.json",
        "rejected_by_gate": batch_dir / "decision" / "rejected_by_gate.json",
        "update_skipped": batch_dir / "decision" / "update_skipped.txt",
    }


def rel_to_iter(iter_dir: Path, path: Path) -> str:
    return path.relative_to(iter_dir).as_posix()


def make_iteration_manifest(iter_dir: Path, iteration: int, paths: dict[str, Path]) -> dict[str, Any]:
    test_paths = held_out_paths(iter_dir)
    return {
        "iteration": iteration,
        "paths": {
            "prompts": {
                "epoch_before": rel_to_iter(iter_dir, paths["prompt_before"]),
                "epoch_candidate": rel_to_iter(iter_dir, paths["prompt_candidate"]),
                "epoch_after": rel_to_iter(iter_dir, paths["prompt_after"]),
            },
            "batches": {
                "ordered_epoch_cases": rel_to_iter(iter_dir, paths["analysis_cases"]),
                "train_batches_dir": "train_batches",
            },
            "evaluation": {
                "epoch_training_records": rel_to_iter(iter_dir, paths["analysis_records"]),
                "epoch_training_summary": rel_to_iter(iter_dir, paths["analysis_summary"]),
                "epoch_training_overview": rel_to_iter(iter_dir, paths["analysis_overview"]),
                "held_out_test_records": rel_to_iter(iter_dir, test_paths["records"]),
                "held_out_test_summary": rel_to_iter(iter_dir, test_paths["summary"]),
                "held_out_test_analysis": rel_to_iter(iter_dir, test_paths["analysis"]),
            },
            "decision": {
                "update_skipped": rel_to_iter(iter_dir, paths["update_skipped"]),
            },
            "reports": {
                "prompt_change": "reports/prompt_change.md",
                "metrics": "reports/metrics_report.md",
            },
        },
        "stages": {},
    }


def record_stage(
    manifest: dict[str, Any],
    stage: str,
    *,
    status: str,
    inputs: dict[str, str] | None = None,
    outputs: dict[str, str] | None = None,
    note: str | None = None,
) -> None:
    entry: dict[str, Any] = {"status": status}
    if inputs:
        entry["inputs"] = inputs
    if outputs:
        entry["outputs"] = outputs
    if note:
        entry["note"] = note
    manifest.setdefault("stages", {})[stage] = entry


def write_iteration_manifest(iter_dir: Path, manifest: dict[str, Any]) -> None:
    write_text(iter_dir / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))


def finalize_iteration_reports(
    *,
    run_dir: Path,
    iter_dir: Path,
    iteration: int,
    prompt_before: str,
    prompt_after: str,
    candidate_prompt: str | None,
    analysis_summary: dict[str, float],
    baseline_gate_summary: dict[str, float] | None = None,
    candidate_summary: dict[str, float] | None = None,
    held_out_test_summary: dict[str, float] | None = None,
    acceptance: dict[str, Any] | None = None,
    batch_summaries: list[dict[str, Any]] | None = None,
) -> None:
    write_iteration_reports(
        iter_dir=iter_dir,
        iteration=iteration,
        prompt_before=prompt_before,
        prompt_after=prompt_after,
        candidate_prompt=candidate_prompt,
        analysis_summary=analysis_summary,
        baseline_gate_summary=baseline_gate_summary,
        candidate_summary=candidate_summary,
        held_out_test_summary=held_out_test_summary,
        acceptance=acceptance,
        batch_summaries=batch_summaries,
    )
    refresh_run_reports(run_dir)


def write_batch_manifest(
    *,
    iter_dir: Path,
    batch_index: int,
    total_batches: int,
    paths: dict[str, Path],
    status: str,
    prompt_changed: bool,
    note: str | None = None,
) -> None:
    payload: dict[str, Any] = {
        "batch_index": batch_index,
        "total_batches": total_batches,
        "status": status,
        "prompt_changed": prompt_changed,
        "paths": {
            "cases": rel_to_iter(iter_dir, paths["cases"]),
            "prompts": {
                "before": rel_to_iter(iter_dir, paths["prompt_before"]),
                "candidate": rel_to_iter(iter_dir, paths["prompt_candidate"]),
                "after": rel_to_iter(iter_dir, paths["prompt_after"]),
            },
            "evaluation": {
                "records": rel_to_iter(iter_dir, paths["records"]),
                "summary": rel_to_iter(iter_dir, paths["summary"]),
                "overview": rel_to_iter(iter_dir, paths["overview"]),
            },
            "agents": {
                "failure_analysis": {
                    "input": rel_to_iter(iter_dir, paths["failure_analysis_input"]),
                    "output": rel_to_iter(iter_dir, paths["failure_analysis_output"]),
                },
                "error_localization": {
                    "input": rel_to_iter(iter_dir, paths["error_localization_input"]),
                    "output": rel_to_iter(iter_dir, paths["error_localization_output"]),
                },
                "prompt_editor": {
                    "input": rel_to_iter(iter_dir, paths["prompt_editor_input"]),
                    "output": rel_to_iter(iter_dir, paths["prompt_editor_output"]),
                },
                "prompt_rewriter": {
                    "input": rel_to_iter(iter_dir, paths["prompt_rewriter_input"]),
                    "output": rel_to_iter(iter_dir, paths["prompt_rewriter_output"]),
                },
            },
            "decision": {
                "acceptance": rel_to_iter(iter_dir, paths["acceptance"]),
                "rejected_by_gate": rel_to_iter(iter_dir, paths["rejected_by_gate"]),
                "update_skipped": rel_to_iter(iter_dir, paths["update_skipped"]),
            },
            "gate": {
                "cases": rel_to_iter(iter_dir, paths["gate_cases"]),
                "baseline_records": rel_to_iter(iter_dir, paths["gate_baseline_records"]),
                "baseline_summary": rel_to_iter(iter_dir, paths["gate_baseline_summary"]),
                "candidate_records": rel_to_iter(iter_dir, paths["gate_candidate_records"]),
                "candidate_summary": rel_to_iter(iter_dir, paths["gate_candidate_summary"]),
            },
        },
    }
    if note:
        payload["note"] = note
    write_text(paths["manifest"], json.dumps(payload, ensure_ascii=False, indent=2))


def write_jsonl_records(path: Path, records: list[EvaluationRecord]) -> None:
    text = "".join(json.dumps(dataclasses.asdict(record), ensure_ascii=False) + "\n" for record in records)
    write_text(path, text)


def write_metric_curves(run_dir: Path) -> None:
    try:
        from scripts.plot_metric_curves import DEFAULT_METRICS, build_rows, plot, write_csv

        metrics = list(DEFAULT_METRICS)
        rows = build_rows(run_dir, metrics)
        if not rows:
            print(f"[plot] skipped; no metric summaries found under {run_dir}")
            return
        csv_path = run_dir / "metric_curves.csv"
        output_path = run_dir / "metric_curves.png"
        write_csv(csv_path, rows, metrics)
        plot(rows, metrics, output_path)
        print(f"[plot] wrote {output_path}")
        print(f"[plot] wrote {csv_path}")
    except Exception as exc:
        print(f"[plot] warning: failed to write metric curves for {run_dir}: {exc}")


def evaluate_iteration_held_out_test(
    *,
    args: argparse.Namespace,
    llm_client: LLMClient,
    test_cases: list[Case] | None,
    test_dataset: str | None,
    run_dir: Path,
    iter_dir: Path,
    iteration: int,
    prompt: str,
    prompt_path: Path,
    manifest: dict[str, Any],
) -> dict[str, float] | None:
    if not test_cases:
        return None

    paths = held_out_paths(iter_dir)
    write_case_manifest(paths["cases"], test_cases)
    test_manifest = {
        "dataset": test_dataset,
        "diagnostic_only": True,
        "used_by_agents": False,
        "used_by_acceptance_gate": False,
        "inputs": {
            "prompt": rel_to_iter(iter_dir, prompt_path),
            "cases": rel_to_iter(iter_dir, paths["cases"]),
        },
        "outputs": {
            "records": rel_to_iter(iter_dir, paths["records"]),
            "summary": rel_to_iter(iter_dir, paths["summary"]),
            "analysis": rel_to_iter(iter_dir, paths["analysis"]),
        },
        "note": "This held-out evaluation is logged after the iteration using the prompt adopted at iteration end. It is not passed to prompt evolution agents or the acceptance gate.",
    }
    write_text(paths["manifest"], json.dumps(test_manifest, ensure_ascii=False, indent=2))

    print(f"[iteration {iteration}] held-out test distribution: {describe_case_distribution(test_cases)}")
    records, summary = evaluate_cases(
        prompt=prompt,
        cases=test_cases,
        args=args,
        llm_client=llm_client,
        output_path=paths["records"],
        state_dir=run_dir,
        phase=f"iteration_{iteration:03d}:held_out_test",
    )
    write_text(paths["summary"], json.dumps(summary, ensure_ascii=False, indent=2))
    write_text(paths["analysis"], build_analysis(records, summary))
    record_stage(
        manifest,
        "held_out_test",
        status="success",
        inputs={
            "prompt": rel_to_iter(iter_dir, prompt_path),
            "cases": rel_to_iter(iter_dir, paths["cases"]),
        },
        outputs={
            "records": rel_to_iter(iter_dir, paths["records"]),
            "summary": rel_to_iter(iter_dir, paths["summary"]),
            "analysis": rel_to_iter(iter_dir, paths["analysis"]),
        },
        note="diagnostic only; not used by prompt evolution agents or the acceptance gate",
    )
    write_iteration_manifest(iter_dir, manifest)
    print(f"[iteration {iteration}] held-out test {format_summary(summary)}")
    return summary


def run_training_iterations(
    *,
    args: argparse.Namespace,
    llm_client: LLMClient,
    train_cases: list[Case],
    test_cases: list[Case] | None = None,
    test_dataset: str | None = None,
    run_dir: Path,
    work_prompt_path: Path,
    label: str,
) -> tuple[str, dict[str, float]]:
    print(f"[run] {label}, train_cases={len(train_cases)}")
    print(f"[run] train distribution: {describe_case_distribution(train_cases)}")
    print(f"[run] output={run_dir}")

    prompt = read_text(work_prompt_path)
    last_summary: dict[str, float] = {}
    best_prompt = prompt
    best_summary: dict[str, float] = {}
    best_metric_key: tuple[float, float, float, float] | None = None

    def consider_best_prompt(prompt_text: str, summary: dict[str, float], *, iteration: int, phase: str) -> None:
        nonlocal best_metric_key, best_prompt, best_summary
        if not summary:
            return
        current_metric_key = metric_priority_key(summary)
        if best_metric_key is None or current_metric_key > best_metric_key:
            best_metric_key = current_metric_key
            best_prompt = prompt_text
            best_summary = summary
            write_text(run_dir / "prompt_best.md", best_prompt)
            write_text(
                run_dir / "best_prompt_summary.json",
                json.dumps(
                    {
                        "iteration": iteration,
                        "phase": phase,
                        "selection_policy": "accepted batch gate summary priority: infrastructure_error_rate, then relation_f1, node_f1, plantuml_compilation_pass_rate",
                        "metric_priority_key": list(best_metric_key),
                        "summary": best_summary,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            )

    for iteration in range(1, args.iterations + 1):
        iter_dir = run_dir / f"iteration_{iteration:03d}"
        paths = iteration_paths(iter_dir)
        manifest = make_iteration_manifest(iter_dir, iteration, paths)
        iteration_start_prompt = prompt
        current_prompt = prompt
        last_candidate_prompt: str | None = None
        last_gate_baseline_summary: dict[str, float] | None = None
        last_gate_candidate_summary: dict[str, float] | None = None
        last_acceptance: dict[str, Any] | None = None
        epoch_batches = make_epoch_batches(train_cases, args=args, iteration=iteration)
        epoch_cases = [case for batch in epoch_batches for case in batch]
        epoch_records: list[EvaluationRecord] = []
        epoch_batch_entries: list[dict[str, Any]] = []
        epoch_report_batch_summaries: list[dict[str, Any]] = []
        has_accepted_prompt_update = False

        write_text(paths["prompt_before"], iteration_start_prompt)
        write_case_manifest(paths["analysis_cases"], epoch_cases)
        record_stage(
            manifest,
            "epoch_batching",
            status="success",
            outputs={
                "ordered_cases": rel_to_iter(iter_dir, paths["analysis_cases"]),
                "train_batches_dir": "train_batches",
            },
            note=f"{len(epoch_cases)} training cases split into {len(epoch_batches)} batch(es) by --analysis-batch-size; each batch candidate is gated immediately",
        )
        write_iteration_manifest(iter_dir, manifest)

        print(f"\n[iteration {iteration}] epoch training over {len(epoch_cases)} cases in {len(epoch_batches)} batch(es)")
        for batch_index, batch_cases in enumerate(epoch_batches, start=1):
            batch_paths = epoch_batch_paths(iter_dir, batch_index)
            batch_prompt_before = current_prompt
            batch_status = "evaluated"
            batch_note: str | None = None
            prompt_changed = False
            batch_acceptance: dict[str, Any] | None = None
            batch_gate_baseline_summary: dict[str, float] | None = None
            batch_gate_candidate_summary: dict[str, float] | None = None

            write_text(batch_paths["prompt_before"], batch_prompt_before)
            write_case_manifest(batch_paths["cases"], batch_cases)
            print(
                f"[iteration {iteration} batch {batch_index}/{len(epoch_batches)}] "
                f"distribution: {describe_case_distribution(batch_cases)}"
            )
            records, summary = evaluate_cases(
                prompt=current_prompt,
                cases=batch_cases,
                args=args,
                llm_client=llm_client,
                output_path=batch_paths["records"],
                state_dir=run_dir,
                phase=f"iteration_{iteration:03d}:batch_{batch_index:03d}:analysis_current",
            )
            epoch_records.extend(records)
            write_text(batch_paths["summary"], json.dumps(summary, ensure_ascii=False, indent=2))
            write_text(batch_paths["overview"], build_analysis(records, summary))
            print(f"[iteration {iteration} batch {batch_index}/{len(epoch_batches)}] train {format_summary(summary)}")

            if args.no_evolve:
                batch_status = "skipped_no_evolve"
                batch_note = "--no-evolve was set; prompt unchanged"
                write_text(batch_paths["prompt_after"], current_prompt)
            elif has_only_infrastructure_errors(records):
                batch_status = "skipped_infrastructure_only"
                batch_note = "all batch records were infrastructure errors"
                write_text(
                    batch_paths["update_skipped"],
                    "Skipped prompt update because every evaluated case failed before a model output was available.\n",
                )
                write_text(batch_paths["prompt_after"], current_prompt)
            else:
                failure_analysis = analyze_failures(
                    current_prompt=current_prompt,
                    records=records,
                    summary=summary,
                    args=args,
                    llm_client=llm_client,
                    output_input_path=batch_paths["failure_analysis_input"],
                    output_path=batch_paths["failure_analysis_output"],
                    state_dir=run_dir,
                    iteration=iteration * 1000 + batch_index,
                )
                if failure_analysis is None:
                    batch_status = "invalid_failure_analysis"
                    batch_note = "failure analysis did not return valid JSON"
                    write_text(batch_paths["prompt_after"], current_prompt)
                else:
                    error_localization = localize_errors(
                        current_prompt=current_prompt,
                        failure_analysis=failure_analysis,
                        args=args,
                        llm_client=llm_client,
                        output_input_path=batch_paths["error_localization_input"],
                        output_path=batch_paths["error_localization_output"],
                        state_dir=run_dir,
                        iteration=iteration * 1000 + batch_index,
                    )
                    if error_localization is None:
                        batch_status = "invalid_error_localization"
                        batch_note = "error localization did not pass validation"
                        write_text(batch_paths["prompt_after"], current_prompt)
                    else:
                        revision_plan = propose_prompt_revision(
                            current_prompt=current_prompt,
                            failure_analysis=failure_analysis,
                            error_localization=error_localization,
                            args=args,
                            llm_client=llm_client,
                            output_input_path=batch_paths["prompt_editor_input"],
                            output_path=batch_paths["prompt_editor_output"],
                            state_dir=run_dir,
                            iteration=iteration * 1000 + batch_index,
                        )
                        if revision_plan is None:
                            batch_status = "invalid_prompt_editor"
                            batch_note = "prompt revision plan did not pass validation"
                            write_text(batch_paths["prompt_after"], current_prompt)
                        else:
                            candidate = rewrite_prompt(
                                current_prompt=current_prompt,
                                revision_plan=revision_plan,
                                args=args,
                                llm_client=llm_client,
                                output_input_path=batch_paths["prompt_rewriter_input"],
                                output_path=batch_paths["prompt_rewriter_output"],
                                state_dir=run_dir,
                                iteration=iteration * 1000 + batch_index,
                            )
                            if candidate is None:
                                batch_status = "invalid_prompt_rewriter"
                                batch_note = "prompt rewriter did not produce a valid candidate prompt"
                                write_text(batch_paths["prompt_after"], current_prompt)
                            elif candidate == current_prompt:
                                write_text(batch_paths["prompt_candidate"], candidate)
                                batch_status = "candidate_same_as_before"
                                batch_note = "prompt rewriter returned the current prompt"
                                write_text(batch_paths["prompt_after"], current_prompt)
                            else:
                                write_text(batch_paths["prompt_candidate"], candidate)
                                last_candidate_prompt = candidate
                                gate_cases = choose_iteration_batch(
                                    train_cases,
                                    args=args,
                                    iteration=iteration,
                                    batch_size=args.gate_batch_size,
                                    strategy=args.candidate_sample_strategy,
                                    seed_offset=40_000 + batch_index * 1000,
                                )
                                write_case_manifest(batch_paths["gate_cases"], gate_cases)
                                print(
                                    f"[iteration {iteration} batch {batch_index}/{len(epoch_batches)}] "
                                    f"gate distribution: {describe_case_distribution(gate_cases)}"
                                )
                                baseline_gate_records, batch_gate_baseline_summary = evaluate_cases(
                                    prompt=current_prompt,
                                    cases=gate_cases,
                                    args=args,
                                    llm_client=llm_client,
                                    output_path=batch_paths["gate_baseline_records"],
                                    state_dir=run_dir,
                                    phase=f"iteration_{iteration:03d}:batch_{batch_index:03d}:gate_baseline",
                                )
                                write_text(batch_paths["gate_baseline_summary"], json.dumps(batch_gate_baseline_summary, ensure_ascii=False, indent=2))
                                candidate_records, batch_gate_candidate_summary = evaluate_cases(
                                    prompt=candidate,
                                    cases=gate_cases,
                                    args=args,
                                    llm_client=llm_client,
                                    output_path=batch_paths["gate_candidate_records"],
                                    state_dir=run_dir,
                                    phase=f"iteration_{iteration:03d}:batch_{batch_index:03d}:gate_candidate",
                                )
                                write_text(batch_paths["gate_candidate_summary"], json.dumps(batch_gate_candidate_summary, ensure_ascii=False, indent=2))
                                last_gate_baseline_summary = batch_gate_baseline_summary
                                last_gate_candidate_summary = batch_gate_candidate_summary

                                if has_only_infrastructure_errors(baseline_gate_records + candidate_records):
                                    batch_status = "gate_skipped_infrastructure_only"
                                    batch_note = "gate baseline and candidate records were all infrastructure errors"
                                    write_text(
                                        batch_paths["update_skipped"],
                                        "Skipped batch acceptance because gate baseline and candidate records were all infrastructure errors.\n",
                                    )
                                    write_text(batch_paths["prompt_after"], current_prompt)
                                else:
                                    accepted, decision = acceptance_decision(
                                        iteration=iteration,
                                        bootstrap_allowed=iteration == 1 and not has_accepted_prompt_update,
                                        baseline_summary=batch_gate_baseline_summary,
                                        candidate_summary=batch_gate_candidate_summary,
                                        candidate_prompt=candidate,
                                        baseline_prompt=current_prompt,
                                        max_prompt_growth_ratio=args.max_prompt_growth_ratio,
                                        max_prompt_chars=args.max_prompt_chars,
                                        min_relation_delta=args.acceptance_min_relation_delta,
                                        min_node_delta=args.acceptance_min_node_delta,
                                        min_compile_delta=args.acceptance_min_compile_delta,
                                        relation_accept_delta=args.relation_accept_delta,
                                        node_accept_delta=args.node_accept_delta,
                                        compile_accept_delta=args.compile_accept_delta,
                                        metric_source=args.acceptance_metric_source,
                                    )
                                    batch_acceptance = decision
                                    last_acceptance = decision
                                    write_text(batch_paths["acceptance"], json.dumps(decision, ensure_ascii=False, indent=2))
                                    consider_best_prompt(current_prompt, batch_gate_baseline_summary, iteration=iteration, phase=f"batch_{batch_index:03d}:gate_baseline")
                                    if accepted:
                                        current_prompt = candidate
                                        has_accepted_prompt_update = True
                                        prompt_changed = True
                                        batch_status = "accepted_batch_prompt"
                                        write_text(batch_paths["prompt_after"], current_prompt)
                                        consider_best_prompt(current_prompt, batch_gate_candidate_summary, iteration=iteration, phase=f"batch_{batch_index:03d}:gate_candidate")
                                        print(f"[iteration {iteration} batch {batch_index}/{len(epoch_batches)}] accepted candidate")
                                    else:
                                        batch_status = "rejected_batch_prompt"
                                        write_text(batch_paths["rejected_by_gate"], json.dumps(decision, ensure_ascii=False, indent=2))
                                        write_text(batch_paths["prompt_after"], current_prompt)
                                        print(
                                            f"[iteration {iteration} batch {batch_index}/{len(epoch_batches)}] rejected candidate "
                                            f"(reasons={', '.join(decision['rejection_reasons'])})"
                                        )

            write_batch_manifest(
                iter_dir=iter_dir,
                batch_index=batch_index,
                total_batches=len(epoch_batches),
                paths=batch_paths,
                status=batch_status,
                prompt_changed=prompt_changed,
                note=batch_note,
            )
            batch_entry = {
                "batch": batch_index,
                "status": batch_status,
                "prompt_changed": prompt_changed,
                "cases": rel_to_iter(iter_dir, batch_paths["cases"]),
                "summary_path": rel_to_iter(iter_dir, batch_paths["summary"]),
                "prompt_before": rel_to_iter(iter_dir, batch_paths["prompt_before"]),
                "prompt_after": rel_to_iter(iter_dir, batch_paths["prompt_after"]),
            }
            if batch_gate_baseline_summary is not None and batch_gate_candidate_summary is not None:
                batch_entry["gate_baseline_summary_path"] = rel_to_iter(iter_dir, batch_paths["gate_baseline_summary"])
                batch_entry["gate_candidate_summary_path"] = rel_to_iter(iter_dir, batch_paths["gate_candidate_summary"])
            if batch_acceptance is not None:
                batch_entry["acceptance_path"] = rel_to_iter(iter_dir, batch_paths["acceptance"])
                batch_entry["accepted"] = bool(batch_acceptance.get("accepted"))
                batch_entry["acceptance_mode"] = batch_acceptance.get("acceptance_mode")
                batch_entry["rejection_reasons"] = batch_acceptance.get("rejection_reasons", [])
            epoch_batch_entries.append(batch_entry)
            epoch_report_batch_summaries.append(
                {
                    "label": f"batch_{batch_index:03d}",
                    "summary": summary,
                    "gate_baseline_summary": batch_gate_baseline_summary,
                    "gate_candidate_summary": batch_gate_candidate_summary,
                    "acceptance": batch_acceptance,
                    "manifest": {
                        "status": batch_status,
                        "prompt_changed": prompt_changed,
                    },
                }
            )
            manifest["epoch_batches"] = epoch_batch_entries
            write_iteration_manifest(iter_dir, manifest)

        epoch_summary = summarize_records(epoch_records)
        last_summary = epoch_summary
        write_jsonl_records(paths["analysis_records"], epoch_records)
        write_text(paths["analysis_summary"], json.dumps(epoch_summary, ensure_ascii=False, indent=2))
        write_text(paths["analysis_overview"], build_analysis(epoch_records, epoch_summary, max_cases=args.analysis_batch_size))
        write_text(paths["prompt_candidate"], last_candidate_prompt or current_prompt)
        prompt_changed_this_iteration = current_prompt != iteration_start_prompt
        write_text(paths["prompt_after"], current_prompt)
        write_text(work_prompt_path, current_prompt)
        prompt = current_prompt

        accepted_batches = sum(1 for entry in epoch_batch_entries if entry.get("accepted") is True)
        rejected_batches = sum(1 for entry in epoch_batch_entries if entry.get("accepted") is False)
        record_stage(
            manifest,
            "epoch_training",
            status="success",
            inputs={
                "prompt_before": rel_to_iter(iter_dir, paths["prompt_before"]),
                "ordered_cases": rel_to_iter(iter_dir, paths["analysis_cases"]),
            },
            outputs={
                "records": rel_to_iter(iter_dir, paths["analysis_records"]),
                "summary": rel_to_iter(iter_dir, paths["analysis_summary"]),
                "analysis": rel_to_iter(iter_dir, paths["analysis_overview"]),
                "prompt_after": rel_to_iter(iter_dir, paths["prompt_after"]),
            },
            note=f"batch-level gate accepted {accepted_batches} candidate(s), rejected {rejected_batches} candidate(s); training summary aggregates epoch-local mini-batches",
        )
        write_iteration_manifest(iter_dir, manifest)
        print(f"[iteration {iteration}] epoch training aggregate {format_summary(epoch_summary)}")

        if prompt_changed_this_iteration:
            record_stage(
                manifest,
                "iteration_prompt",
                status="updated",
                outputs={"prompt_after": rel_to_iter(iter_dir, paths["prompt_after"])},
                note="iteration adopts the last prompt accepted by a batch-level gate",
            )
            print(f"[iteration {iteration}] prompt updated: {work_prompt_path}")
        else:
            record_stage(
                manifest,
                "iteration_prompt",
                status="unchanged",
                outputs={"prompt_after": rel_to_iter(iter_dir, paths["prompt_after"])},
                note="no batch-level gate accepted a prompt change",
            )
            print(f"[iteration {iteration}] prompt unchanged")
        write_iteration_manifest(iter_dir, manifest)

        held_out_test_summary = evaluate_iteration_held_out_test(
            args=args,
            llm_client=llm_client,
            test_cases=test_cases,
            test_dataset=test_dataset,
            run_dir=run_dir,
            iter_dir=iter_dir,
            iteration=iteration,
            prompt=current_prompt,
            prompt_path=paths["prompt_after"],
            manifest=manifest,
        )
        finalize_iteration_reports(
            run_dir=run_dir,
            iter_dir=iter_dir,
            iteration=iteration,
            prompt_before=iteration_start_prompt,
            prompt_after=current_prompt,
            candidate_prompt=last_candidate_prompt,
            analysis_summary=epoch_summary,
            baseline_gate_summary=last_gate_baseline_summary,
            candidate_summary=last_gate_candidate_summary,
            held_out_test_summary=held_out_test_summary,
            acceptance=last_acceptance,
            batch_summaries=epoch_report_batch_summaries,
        )

    final_prompt = read_text(work_prompt_path)
    if args.use_best_prompt_for_test:
        final_prompt = best_prompt
        write_text(work_prompt_path, final_prompt)
    write_text(run_dir / "prompt_final.md", final_prompt)
    refresh_run_reports(run_dir)
    return final_prompt, last_summary

def run_train_only(args: argparse.Namespace, datasets: dict[str, list[Case]], llm_client: LLMClient, train_dataset: str) -> dict[str, float]:
    train_dataset = train_dataset.lower()
    if train_dataset not in datasets:
        raise ValueError(f"Unknown train dataset {train_dataset!r}. Available: {', '.join(sorted(datasets))}")
    train_cases = select_cases_with_strategy(
        datasets[train_dataset],
        limit=args.max_train_cases,
        strategy=args.sample_strategy,
        seed=args.sample_seed,
    )
    run_dir = make_run_dir(args.runs_dir, f"train-{train_dataset}")
    write_run_args(args, run_dir)
    write_case_manifest(run_dir / "train_cases.json", train_cases)
    work_prompt_path = initialize_run_prompt(args.prompt_path, run_dir)
    _, summary = run_training_iterations(
        args=args,
        llm_client=llm_client,
        train_cases=train_cases,
        run_dir=run_dir,
        work_prompt_path=work_prompt_path,
        label=f"train_only={train_dataset}",
    )
    write_metric_curves(run_dir)
    return summary


def run_one_split(args: argparse.Namespace, datasets: dict[str, list[Case]], llm_client: LLMClient, test_dataset: str) -> dict[str, float]:
    test_dataset = test_dataset.lower()
    if test_dataset not in datasets:
        raise ValueError(f"Unknown test dataset {test_dataset!r}. Available: {', '.join(sorted(datasets))}")

    train_cases_all = [case for name, cases in datasets.items() if name != test_dataset for case in cases]
    test_cases_all = datasets[test_dataset]
    train_cases = select_cases_with_strategy(
        train_cases_all,
        limit=args.max_train_cases,
        strategy=args.sample_strategy,
        seed=args.sample_seed,
    )
    test_cases = select_cases_with_strategy(
        test_cases_all,
        limit=args.max_test_cases,
        strategy=args.test_sample_strategy,
        seed=args.sample_seed + 20_000,
    )

    run_dir = make_run_dir(args.runs_dir, f"test-{test_dataset}")
    write_run_args(args, run_dir)
    write_case_manifest(run_dir / "train_cases.json", train_cases)
    write_case_manifest(run_dir / "test_cases.json", test_cases)
    work_prompt_path = initialize_run_prompt(args.prompt_path, run_dir)
    print(f"[run] test={test_dataset}, train_cases={len(train_cases)}, test_cases={len(test_cases)}")
    print(f"[run] test distribution: {describe_case_distribution(test_cases)}")
    final_prompt, _ = run_training_iterations(
        args=args,
        llm_client=llm_client,
        train_cases=train_cases,
        test_cases=test_cases,
        test_dataset=test_dataset,
        run_dir=run_dir,
        work_prompt_path=work_prompt_path,
        label=f"test={test_dataset}",
    )

    print(f"\n[test] evaluating held-out dataset {test_dataset}")
    test_dir = run_dir / "test"
    test_records_path = test_dir / "records.jsonl"
    test_summary_path = test_dir / "summary.json"
    test_analysis_path = test_dir / "analysis.md"
    test_manifest = {
        "dataset": test_dataset,
        "inputs": {
            "prompt": "prompt_final.md",
            "cases": "test_cases.json",
        },
        "outputs": {
            "records": "test/records.jsonl",
            "summary": "test/summary.json",
            "analysis": "test/analysis.md",
        },
    }
    write_text(test_dir / "manifest.json", json.dumps(test_manifest, ensure_ascii=False, indent=2))
    records, summary = evaluate_cases(
        prompt=final_prompt,
        cases=test_cases,
        args=args,
        llm_client=llm_client,
        output_path=test_records_path,
        state_dir=run_dir,
        phase=f"test_eval:{test_dataset}",
    )
    write_text(test_summary_path, json.dumps(summary, ensure_ascii=False, indent=2))
    write_text(test_analysis_path, build_analysis(records, summary))
    write_text(run_dir / "prompt_final.md", final_prompt)
    refresh_run_reports(run_dir)
    write_metric_curves(run_dir)
    print(f"[test] {format_summary(summary)}")
    return summary


def looks_like_run_dir(path: Path) -> bool:
    return (
        (path / "run_args.json").exists()
        or (path / "prompt_initial.md").exists()
        or (path / "test_summary.json").exists()
        or (path / "test" / "summary.json").exists()
        or any(path.glob("iteration_*"))
    )


def refresh_requested_reports(args: argparse.Namespace) -> None:
    target = args.refresh_reports
    if target == "__ALL__":
        if not args.runs_dir.exists():
            raise FileNotFoundError(f"Runs directory not found: {args.runs_dir}")
        run_dirs = [path for path in sorted(args.runs_dir.iterdir()) if path.is_dir() and looks_like_run_dir(path)]
    else:
        target_path = Path(target)
        if not target_path.is_absolute():
            target_path = (Path.cwd() / target_path).resolve()
        if target_path.name.startswith("iteration_"):
            target_path = target_path.parent
        if not target_path.exists():
            raise FileNotFoundError(f"Run directory not found: {target_path}")
        if not looks_like_run_dir(target_path):
            raise ValueError(f"Not a run directory: {target_path}")
        run_dirs = [target_path]

    for run_dir in run_dirs:
        refresh_run_reports(run_dir)
        write_metric_curves(run_dir)
        print(f"[reports] refreshed {run_dir}")
    print(f"[reports] refreshed {len(run_dirs)} run(s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prompt evolution for UML activity diagram PlantUML generation")
    parser.add_argument("--test-dataset", default=None, help="Held-out dataset name, or 'all' for leave-one-dataset-out")
    parser.add_argument("--train-dataset", default=None, help="Dataset to use for train-only mode")
    parser.add_argument("--train-only", action="store_true", help="Run optimization on --train-dataset without held-out testing")
    parser.add_argument("--datasets-dir", type=Path, default=DEFAULT_DATASETS_DIR)
    parser.add_argument("--prompt-path", type=Path, default=DEFAULT_PROMPT_PATH, help="Read-only seed prompt copied to each run's work.md")
    parser.add_argument("--failure-analysis-prompt-path", type=Path, default=DEFAULT_FAILURE_ANALYSIS_PROMPT_PATH, help="System prompt markdown for the failure-analysis model")
    parser.add_argument("--error-localization-prompt-path", type=Path, default=DEFAULT_ERROR_LOCALIZATION_PROMPT_PATH, help="System prompt markdown for the error-localization model")
    parser.add_argument("--prompt-editor-prompt-path", type=Path, default=DEFAULT_PROMPT_EDITOR_PROMPT_PATH, help="System prompt markdown for the prompt-edit model")
    parser.add_argument("--prompt-rewriter-prompt-path", type=Path, default=DEFAULT_PROMPT_REWRITER_PROMPT_PATH, help="System prompt markdown for the prompt-rewrite model")
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    parser.add_argument("--plantuml-jar", type=Path, default=DEFAULT_PLANTUML_JAR)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--max-train-cases", type=int, default=0, help="0 means all training cases")
    parser.add_argument("--max-test-cases", type=int, default=0, help="0 means all test cases")
    parser.add_argument("--analysis-batch-size", type=int, default=10, help="Training batch size used for generation and failure analysis")
    parser.add_argument("--gate-batch-size", type=int, default=10, help="Training batch size used to accept or reject edited prompts")
    parser.add_argument("--sample-strategy", choices=["stratified", "random", "prefix"], default="stratified", help="How to select limited training cases")
    parser.add_argument("--test-sample-strategy", choices=["stratified", "random", "prefix"], default="prefix", help="How to select limited held-out test cases")
    parser.add_argument("--candidate-sample-strategy", choices=["stratified", "random", "prefix"], default="stratified", help="How to select candidate gate cases")
    parser.add_argument("--sample-seed", type=int, default=13)
    parser.add_argument("--model", default=os.environ.get("ZHIPU_LLM_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-key", default=os.environ.get("ZHIPU_LLM_API_KEY", ""))
    parser.add_argument("--base-url", default=os.environ.get("ZHIPU_LLM_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--analysis-temperature", type=float, default=0.2)
    parser.add_argument("--localization-temperature", type=float, default=0.2)
    parser.add_argument("--editor-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=optional_float, default=None, help="GLM top_p, or 'omit' to use provider default")
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--analysis-max-tokens", type=int, default=4096)
    parser.add_argument("--localization-max-tokens", type=int, default=4096)
    parser.add_argument("--editor-max-tokens", type=int, default=4096)
    parser.add_argument("--thinking", choices=["enabled", "disabled"], default=os.environ.get("ZHIPU_THINKING_TYPE", DEFAULT_THINKING_TYPE), help="Default thinking mode for all model calls unless an agent-specific option overrides it")
    parser.add_argument("--generation-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_GENERATION_THINKING_TYPE", "inherit"), help="Thinking mode for PlantUML generation calls")
    parser.add_argument("--analysis-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_ANALYSIS_THINKING_TYPE", "inherit"), help="Thinking mode for failure-analysis calls")
    parser.add_argument("--localization-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_LOCALIZATION_THINKING_TYPE", "inherit"), help="Thinking mode for error-localization calls")
    parser.add_argument("--editor-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_EDITOR_THINKING_TYPE", "inherit"), help="Thinking mode for prompt-editor calls")
    parser.add_argument("--judge-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_JUDGE_THINKING_TYPE", "inherit"), help="Thinking mode for optional LLM semantic judge calls")
    parser.add_argument("--do-sample", type=optional_bool, default=None, help="GLM do_sample, or 'omit' to use provider default")
    parser.add_argument("--llm-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-max-retries", type=int, default=20, help="Retries for provider 429/5xx/transient errors before failing")
    parser.add_argument("--llm-rate-limit-initial-wait", type=int, default=30, help="Initial wait seconds for provider rate-limit retries")
    parser.add_argument("--llm-rate-limit-max-wait", type=int, default=600, help="Maximum wait seconds for provider rate-limit retries")
    parser.add_argument("--node-match-threshold", type=float, default=0.85, help="LATO-style node semantic similarity threshold")
    parser.add_argument("--relation-match-threshold", type=float, default=0.85, help="LATO-style relation semantic similarity threshold")
    parser.add_argument("--semantic-embedding-model", default=DEFAULT_EMBEDDING_MODEL, help="Sentence-transformers model used for LATO-style semantic element matching")
    parser.add_argument("--metric-matcher", choices=["embedding", "difflib"], default="embedding", help="Element matcher for deterministic metrics; embedding follows the LATO paper, difflib is only a cheap fallback")
    parser.add_argument("--element-extractor", choices=["rule", "llm", "auto"], default=os.environ.get("APE_ELEMENT_EXTRACTOR", "llm"), help="Backend for PlantUML-to-node/relation extraction used before metric matching")
    parser.add_argument("--element-extraction-temperature", type=float, default=0.0, help="Temperature for LLM element extraction")
    parser.add_argument("--element-extraction-max-tokens", type=int, default=4096, help="Max tokens for LLM element extraction")
    parser.add_argument("--element-extraction-max-retries", type=int, default=3, help="JSON/schema retries for LLM element extraction")
    parser.add_argument("--element-extraction-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_ELEMENT_EXTRACTION_THINKING_TYPE", "inherit"), help="Thinking mode for LLM element extraction calls")
    parser.add_argument("--acceptance-min-node-delta", type=float, default=-0.15, help="Minimum node F1 delta tolerated by the safety gate")
    parser.add_argument("--acceptance-min-relation-delta", type=float, default=-0.15, help="Minimum relation F1 delta tolerated by the safety gate")
    parser.add_argument("--acceptance-min-compile-delta", type=float, default=-0.10, help="Minimum PlantUML compilation pass-rate delta tolerated by the safety gate")
    parser.add_argument("--relation-accept-delta", type=float, default=0.03, help="Relation F1 delta logged as a positive signal in the acceptance decision")
    parser.add_argument("--node-accept-delta", type=float, default=0.03, help="Node F1 delta logged as a positive signal in the acceptance decision")
    parser.add_argument("--compile-accept-delta", type=float, default=0.10, help="PlantUML compilation pass-rate delta that can accept a candidate when node and relation F1 do not regress")
    parser.add_argument(
        "--acceptance-metric-source",
        choices=["deterministic", "llm", "hybrid"],
        default="deterministic",
        help="Metric source used by the acceptance gate; hybrid uses LLM node/relation metrics when available with a deterministic-compatible safety policy",
    )
    parser.add_argument(
        "--max-sections-per-edit",
        type=int,
        default=0,
        help="Maximum fixed prompt sections a prompt edit may modify; 0 disables the limit",
    )
    parser.add_argument("--max-prompt-growth-ratio", type=float, default=0.0, help="Reject candidate prompts that grow more than this ratio over the current prompt; 0 disables this ratio gate")
    parser.add_argument("--max-prompt-chars", type=int, default=9000, help="Reject candidate prompts longer than this many characters")
    parser.add_argument("--use-best-prompt-for-test", action=argparse.BooleanOptionalAction, default=False, help="Use the best validation prompt for final held-out testing instead of the last adopted prompt")
    parser.add_argument("--plantuml-compile-timeout", type=int, default=30, help="Timeout in seconds for PlantUML compilation checks")
    parser.add_argument("--llm-element-metrics", action=argparse.BooleanOptionalAction, default=True, help="Run LLM semantic node/relation P/R/F1 metrics; use --no-llm-element-metrics for cheap local smoke tests")
    parser.add_argument("--llm-judge-temperature", type=float, default=0.0)
    parser.add_argument("--llm-judge-max-tokens", type=int, default=4096)
    parser.add_argument("--llm-judge-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-judge-max-retries", type=int, default=3)
    parser.add_argument("--mock-with-gold", action="store_true", help="Use gold PlantUML as generated output for pipeline checks")
    parser.add_argument("--no-evolve", action="store_true", help="Evaluate only; do not ask the LLM to update the prompt")
    parser.add_argument(
        "--refresh-reports",
        nargs="?",
        const="__ALL__",
        default=None,
        metavar="RUN_DIR",
        help="Regenerate human-readable prompt and metrics reports for one run directory, or all runs when RUN_DIR is omitted",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.datasets_dir = args.datasets_dir.resolve()
    args.prompt_path = args.prompt_path.resolve()
    args.failure_analysis_prompt_path = args.failure_analysis_prompt_path.resolve()
    args.error_localization_prompt_path = args.error_localization_prompt_path.resolve()
    args.prompt_editor_prompt_path = args.prompt_editor_prompt_path.resolve()
    args.prompt_rewriter_prompt_path = args.prompt_rewriter_prompt_path.resolve()
    args.runs_dir = args.runs_dir.resolve()
    args.plantuml_jar = args.plantuml_jar.resolve()

    if args.refresh_reports:
        refresh_requested_reports(args)
        return

    args.generation_thinking = resolve_agent_thinking(args.generation_thinking, args.thinking)
    args.analysis_thinking = resolve_agent_thinking(args.analysis_thinking, args.thinking)
    args.localization_thinking = resolve_agent_thinking(args.localization_thinking, args.thinking)
    args.editor_thinking = resolve_agent_thinking(args.editor_thinking, args.thinking)
    args.judge_thinking = resolve_agent_thinking(args.judge_thinking, args.thinking)
    args.element_extraction_thinking = resolve_agent_thinking(args.element_extraction_thinking, args.thinking)
    args.llm_judge_model = args.model
    args.llm_judge_api_key = args.api_key
    args.llm_judge_base_url = args.base_url
    args.llm_judge_thinking = args.judge_thinking

    datasets = load_cases(args.datasets_dir)
    validate_glm_args(args)
    if not args.prompt_path.exists():
        raise FileNotFoundError(f"Seed prompt file not found: {args.prompt_path}")
    read_prompt_file(args.failure_analysis_prompt_path, label="failure analysis")
    read_prompt_file(args.error_localization_prompt_path, label="error localization")
    read_prompt_file(args.prompt_editor_prompt_path, label="prompt editor")
    read_prompt_file(args.prompt_rewriter_prompt_path, label="prompt rewriter")

    llm_client = make_llm_client(args)

    if args.train_only:
        if not args.train_dataset:
            parser.error("--train-only requires --train-dataset")
        run_train_only(args, datasets, llm_client, args.train_dataset)
        return

    if not args.test_dataset:
        parser.error("Specify --test-dataset for split testing, or --train-only --train-dataset for training only")

    if args.test_dataset.lower() == "all":
        summaries: dict[str, dict[str, float]] = {}
        for dataset_name in sorted(datasets):
            summaries[dataset_name] = run_one_split(args, datasets, llm_client, dataset_name)
        print("\n[all] held-out summaries")
        for dataset_name, summary in summaries.items():
            print(f"- {dataset_name}: {format_summary(summary)}")
        return

    run_one_split(args, datasets, llm_client, args.test_dataset)


if __name__ == "__main__":
    main()
