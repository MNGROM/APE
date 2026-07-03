#!/usr/bin/env python3
"""Entry point for APE prompt evolution."""

from __future__ import annotations

import argparse
import csv
import dataclasses
import json
import os
from pathlib import Path
from typing import Any

from analysis.error_localization import localize_errors
from analysis.epoch_planner import plan_epoch_revision
from analysis.failure_analysis import analyze_failures, build_analysis
from analysis.prompt_editor import propose_prompt_revision
from analysis.prompt_rewriter import rewrite_prompt
from config import (
    DEFAULT_BASE_URL,
    DEFAULT_DATASETS_DIR,
    DEFAULT_EPOCH_PLANNER_PROMPT_PATH,
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
    grouped_cases,
    load_cases,
    select_cases_with_strategy,
    write_case_manifest,
)
from evaluation import evaluate_cases, has_only_infrastructure_errors
from llm import LLMClient
from metrics import DEFAULT_EMBEDDING_MODEL, format_summary, summarize_records
from reporting import refresh_run_reports, write_iteration_reports
from utils.io import read_prompt_file, read_text, write_text
from versioning import initialize_run_prompt, make_run_dir, write_run_args


ITERATION_TEST_METRIC_KEYS = (
    "node_f1",
    "relation_f1",
    "llm_node_f1",
    "llm_relation_f1",
    "plantuml_compilation_pass_rate",
)


def validate_glm_args(args: argparse.Namespace) -> None:
    thinking_fields = (
        "thinking",
        "generation_thinking",
        "analysis_thinking",
        "localization_thinking",
        "editor_thinking",
        "epoch_planner_thinking",
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
    if args.max_prompt_chars < 1000:
        raise ValueError("--max-prompt-chars is too small for the required prompt sections")
    if args.llm_max_retries < 0:
        raise ValueError("--llm-max-retries must be non-negative")
    if args.analysis_batch_size < 1:
        raise ValueError("--analysis-batch-size must be positive")
    if args.validation_gate_size < 0:
        raise ValueError("--validation-gate-size must be non-negative")
    if args.validation_gate_seed < 0:
        raise ValueError("--validation-gate-seed must be non-negative")
    if args.initial_max_sections_per_edit < 0 or args.initial_max_sections_per_edit > len(SECTION_NAMES):
        raise ValueError("--initial-max-sections-per-edit must be 0 (unlimited) or between 1 and the number of fixed prompt sections")
    if args.max_sections_per_edit < 0 or args.max_sections_per_edit > len(SECTION_NAMES):
        raise ValueError("--max-sections-per-edit must be 0 (unlimited) or between 1 and the number of fixed prompt sections")
    if args.analysis_max_tokens < 1 or args.localization_max_tokens < 1 or args.editor_max_tokens < 1 or args.epoch_planner_max_tokens < 1:
        raise ValueError("--analysis-max-tokens, --localization-max-tokens, --editor-max-tokens, and --epoch-planner-max-tokens must be positive")
    if args.llm_judge_max_tokens < 1:
        raise ValueError("--llm-judge-max-tokens must be positive")
    if args.llm_judge_max_retries < 1:
        raise ValueError("--llm-judge-max-retries must be positive")
    if args.element_extraction_max_tokens < 1:
        raise ValueError("--element-extraction-max-tokens must be positive")
    if args.element_extraction_max_retries < 1:
        raise ValueError("--element-extraction-max-retries must be positive")
    if args.bootstrap_node_accept_delta < 0 or args.bootstrap_relation_accept_delta < 0:
        raise ValueError("--bootstrap-node-accept-delta and --bootstrap-relation-accept-delta must be non-negative")
    if args.llm_element_metrics and not args.api_key:
        raise ValueError("LLM semantic element metrics require the main API key via ZHIPU_LLM_API_KEY or --api-key")
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


def acceptance_decision(
    *,
    iteration: int,
    allow_bootstrap: bool,
    baseline_summary: dict[str, float],
    candidate_summary: dict[str, float],
    candidate_prompt: str,
    baseline_prompt: str,
    max_prompt_chars: int,
    min_relation_delta: float,
    min_node_delta: float,
    min_compile_delta: float,
    relation_accept_delta: float,
    node_accept_delta: float,
    compile_accept_delta: float,
    min_syntax_delta: float = -0.01,
    min_node_precision_delta: float = -0.02,
    min_relation_precision_delta: float = -0.02,
    bootstrap_min_compile_delta: float = -0.10,
    bootstrap_min_syntax_delta: float = -0.10,
    bootstrap_node_accept_delta: float = 0.05,
    bootstrap_relation_accept_delta: float = 0.05,
) -> tuple[bool, dict[str, Any]]:
    syntax_delta = candidate_summary.get("syntax_pass_rate", 0.0) - baseline_summary.get("syntax_pass_rate", 0.0)
    compile_delta = candidate_summary.get("plantuml_compilation_pass_rate", 0.0) - baseline_summary.get("plantuml_compilation_pass_rate", 0.0)
    node_precision_delta = candidate_summary.get("node_precision", 0.0) - baseline_summary.get("node_precision", 0.0)
    relation_precision_delta = candidate_summary.get("relation_precision", 0.0) - baseline_summary.get("relation_precision", 0.0)
    node_delta = candidate_summary.get("node_f1", 0.0) - baseline_summary.get("node_f1", 0.0)
    relation_delta = candidate_summary.get("relation_f1", 0.0) - baseline_summary.get("relation_f1", 0.0)
    llm_node_delta = candidate_summary.get("llm_node_f1", 0.0) - baseline_summary.get("llm_node_f1", 0.0)
    llm_relation_delta = candidate_summary.get("llm_relation_f1", 0.0) - baseline_summary.get("llm_relation_f1", 0.0)
    infrastructure_delta = candidate_summary.get("infrastructure_error_rate", 0.0) - baseline_summary.get("infrastructure_error_rate", 0.0)
    prompt_size_ok = len(candidate_prompt) <= max_prompt_chars
    llm_metrics_available = candidate_summary.get("llm_element_evaluated", 0.0) > 0 and baseline_summary.get("llm_element_evaluated", 0.0) > 0
    llm_semantic_guard_ok = True
    bootstrap_llm_guard_ok = True
    if llm_metrics_available:
        llm_semantic_guard_ok = llm_node_delta >= -0.01 and llm_relation_delta >= -0.015
        bootstrap_llm_guard_ok = llm_node_delta >= 0.0 and llm_relation_delta >= 0.0

    safety_gate = {
        "syntax_not_significantly_worse": syntax_delta >= min_syntax_delta,
        "compile_not_significantly_worse": compile_delta >= min_compile_delta,
        "node_not_significantly_worse": node_delta >= min_node_delta,
        "relation_not_significantly_worse": relation_delta >= min_relation_delta,
        "node_precision_not_significantly_worse": node_precision_delta >= min_node_precision_delta,
        "relation_precision_not_significantly_worse": relation_precision_delta >= min_relation_precision_delta,
        "llm_semantic_guard_ok": llm_semantic_guard_ok,
        "infrastructure_delta_ok": infrastructure_delta <= 0,
        "prompt_size_ok": prompt_size_ok,
    }
    benefit_gate = {
        "relation_improved": relation_delta >= relation_accept_delta,
        "node_improved": node_delta >= node_accept_delta,
        "compile_improved_without_semantic_regression": compile_delta >= compile_accept_delta and node_delta >= 0 and relation_delta >= 0,
    }
    bootstrap_gate = {
        "bootstrap_allowed": allow_bootstrap,
        "syntax_within_bootstrap_tolerance": syntax_delta >= bootstrap_min_syntax_delta,
        "compile_within_bootstrap_tolerance": compile_delta >= bootstrap_min_compile_delta,
        "node_improved": node_delta >= bootstrap_node_accept_delta,
        "relation_improved": relation_delta >= bootstrap_relation_accept_delta,
        "llm_semantic_guard_ok": bootstrap_llm_guard_ok,
        "infrastructure_delta_ok": infrastructure_delta <= 0,
        "prompt_size_ok": prompt_size_ok,
    }
    standard_accept = all(safety_gate.values()) and any(benefit_gate.values())
    bootstrap_accept = all(bootstrap_gate.values())
    accept = standard_accept or bootstrap_accept
    bootstrap_status = (
        "accepted"
        if bootstrap_accept
        else "available_failed"
        if allow_bootstrap
        else "disabled_after_first_acceptance"
    )
    rejection_checks = {
        "standard_safety_gate": all(safety_gate.values()),
        "has_required_metric_benefit": any(benefit_gate.values()),
    }
    if allow_bootstrap:
        rejection_checks["bootstrap_gate"] = bootstrap_accept
    rejection_reasons = [] if accept else [name for name, ok in rejection_checks.items() if not ok]
    return accept, {
        "accepted": accept,
        "metric_deltas": {
            "syntax_pass_rate": syntax_delta,
            "plantuml_compilation_pass_rate": compile_delta,
            "node_precision": node_precision_delta,
            "relation_precision": relation_precision_delta,
            "node_f1": node_delta,
            "relation_f1": relation_delta,
            "llm_node_f1": llm_node_delta,
            "llm_relation_f1": llm_relation_delta,
            "infrastructure_error_rate": infrastructure_delta,
        },
        "prompt_growth": {
            "baseline_chars": len(baseline_prompt),
            "candidate_chars": len(candidate_prompt),
            "max_prompt_chars": max_prompt_chars,
            "prompt_size_ok": prompt_size_ok,
            "allow_bootstrap": allow_bootstrap,
        },
        "syntax_delta": syntax_delta,
        "compile_delta": compile_delta,
        "node_delta": node_delta,
        "relation_delta": relation_delta,
        "node_precision_delta": node_precision_delta,
        "relation_precision_delta": relation_precision_delta,
        "deterministic_node_delta": node_delta,
        "deterministic_relation_delta": relation_delta,
        "llm_node_delta": llm_node_delta,
        "llm_relation_delta": llm_relation_delta,
        "infrastructure_delta": infrastructure_delta,
        "min_syntax_delta": min_syntax_delta,
        "min_compile_delta": min_compile_delta,
        "min_node_delta": min_node_delta,
        "min_relation_delta": min_relation_delta,
        "min_node_precision_delta": min_node_precision_delta,
        "min_relation_precision_delta": min_relation_precision_delta,
        "relation_accept_delta": relation_accept_delta,
        "node_accept_delta": node_accept_delta,
        "compile_accept_delta": compile_accept_delta,
        "bootstrap_min_compile_delta": bootstrap_min_compile_delta,
        "bootstrap_min_syntax_delta": bootstrap_min_syntax_delta,
        "bootstrap_node_accept_delta": bootstrap_node_accept_delta,
        "bootstrap_relation_accept_delta": bootstrap_relation_accept_delta,
        "safety_gate": safety_gate,
        "benefit_gate": benefit_gate,
        "bootstrap_gate": bootstrap_gate,
        "bootstrap_status": bootstrap_status,
        "standard_accept": standard_accept,
        "bootstrap_accept": bootstrap_accept,
        "acceptance_mode": "standard" if standard_accept else "bootstrap" if bootstrap_accept else "rejected",
        "rejection_reasons": rejection_reasons,
        "acceptance_policy": "standard: accept when every non-regression check passes and at least one deterministic node/relation/compile benefit gate passes; bootstrap before first accepted update: tolerate limited syntax/compile regression only when deterministic node and relation F1 both improve strongly, LLM metrics do not regress when available, infrastructure is not worse, and prompt size is ok",
        "prompt_chars_before": len(baseline_prompt),
        "prompt_chars_candidate": len(candidate_prompt),
        "max_prompt_chars": max_prompt_chars,
        "prompt_size_ok": prompt_size_ok,
        "baseline_summary": baseline_summary,
        "candidate_summary": candidate_summary,
    }


def iteration_paths(iter_dir: Path) -> dict[str, Path]:
    return {
        "manifest": iter_dir / "manifest.json",
        "prompt_before": iter_dir / "prompts" / "before.md",
        "prompt_candidate": iter_dir / "prompts" / "candidate.md",
        "prompt_after": iter_dir / "prompts" / "after.md",
        "analysis_cases": iter_dir / "batches" / "analysis_cases.json",
        "validation_cases": iter_dir / "validation_gate" / "cases.json",
        "validation_baseline_records": iter_dir / "validation_gate" / "baseline_records.jsonl",
        "validation_baseline_summary": iter_dir / "validation_gate" / "baseline_summary.json",
        "validation_candidate_records": iter_dir / "validation_gate" / "candidate_records.jsonl",
        "validation_candidate_summary": iter_dir / "validation_gate" / "candidate_summary.json",
        "validation_analysis": iter_dir / "validation_gate" / "analysis.md",
        "analysis_records": iter_dir / "evaluation" / "analysis_records.jsonl",
        "analysis_summary": iter_dir / "evaluation" / "analysis_summary.json",
        "analysis_overview": iter_dir / "evaluation" / "analysis_overview.md",
        "failure_analysis_input": iter_dir / "agents" / "failure_analysis.input.json",
        "failure_analysis_output": iter_dir / "agents" / "failure_analysis.output.json",
        "error_localization_input": iter_dir / "agents" / "error_localization.input.json",
        "error_localization_output": iter_dir / "agents" / "error_localization.output.json",
        "prompt_editor_input": iter_dir / "agents" / "prompt_editor.input.json",
        "prompt_editor_output": iter_dir / "agents" / "prompt_editor.output.json",
        "epoch_planner_input": iter_dir / "agents" / "epoch_planner.input.json",
        "epoch_planner_output": iter_dir / "agents" / "epoch_planner.output.json",
        "prompt_rewriter_input": iter_dir / "agents" / "prompt_rewriter.input.json",
        "prompt_rewriter_output": iter_dir / "agents" / "prompt_rewriter.output.json",
        "acceptance": iter_dir / "decision" / "acceptance.json",
        "rejected_by_gate": iter_dir / "decision" / "rejected_by_gate.json",
        "update_skipped": iter_dir / "decision" / "update_skipped.txt",
    }


def rel_to_iter(iter_dir: Path, path: Path) -> str:
    return path.relative_to(iter_dir).as_posix()


def make_iteration_manifest(iter_dir: Path, iteration: int, paths: dict[str, Path]) -> dict[str, Any]:
    return {
        "iteration": iteration,
        "paths": {
            "prompts": {
                "before": rel_to_iter(iter_dir, paths["prompt_before"]),
                "candidate": rel_to_iter(iter_dir, paths["prompt_candidate"]),
                "after": rel_to_iter(iter_dir, paths["prompt_after"]),
            },
            "batches": {
                "analysis_cases": rel_to_iter(iter_dir, paths["analysis_cases"]),
            },
            "validation_gate": {
                "cases": rel_to_iter(iter_dir, paths["validation_cases"]),
                "baseline_records": rel_to_iter(iter_dir, paths["validation_baseline_records"]),
                "baseline_summary": rel_to_iter(iter_dir, paths["validation_baseline_summary"]),
                "candidate_records": rel_to_iter(iter_dir, paths["validation_candidate_records"]),
                "candidate_summary": rel_to_iter(iter_dir, paths["validation_candidate_summary"]),
                "analysis": rel_to_iter(iter_dir, paths["validation_analysis"]),
            },
            "evaluation": {
                "analysis_records": rel_to_iter(iter_dir, paths["analysis_records"]),
                "analysis_summary": rel_to_iter(iter_dir, paths["analysis_summary"]),
                "analysis_overview": rel_to_iter(iter_dir, paths["analysis_overview"]),
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
                "epoch_planner": {
                    "input": rel_to_iter(iter_dir, paths["epoch_planner_input"]),
                    "output": rel_to_iter(iter_dir, paths["epoch_planner_output"]),
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
    acceptance: dict[str, Any] | None = None,
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
        acceptance=acceptance,
    )
    refresh_run_reports(run_dir)


def split_training_batches(train_cases: list[Case], batch_size: int, *, strategy: str = "stratified") -> list[list[Case]]:
    if batch_size <= 0 or batch_size >= len(train_cases):
        return [list(train_cases)]
    if strategy == "chunked":
        return [train_cases[start : start + batch_size] for start in range(0, len(train_cases), batch_size)]
    if strategy != "stratified":
        raise ValueError(f"Unknown training batch strategy {strategy!r}")

    batch_count = (len(train_cases) + batch_size - 1) // batch_size
    groups = grouped_cases(train_cases)
    chunks_by_dataset: dict[str, list[list[Case]]] = {}
    for dataset in sorted(groups):
        cases = groups[dataset]
        base_size, extra = divmod(len(cases), batch_count)
        chunks: list[list[Case]] = []
        start = 0
        for batch_index in range(batch_count):
            size = base_size + (1 if batch_index < extra else 0)
            chunks.append(cases[start : start + size])
            start += size
        chunks_by_dataset[dataset] = chunks

    batches: list[list[Case]] = []
    for batch_index in range(batch_count):
        batch: list[Case] = []
        for dataset in sorted(chunks_by_dataset):
            batch.extend(chunks_by_dataset[dataset][batch_index])
        if batch:
            batches.append(batch)
    return batches


def split_validation_gate_cases(cases: list[Case], args: argparse.Namespace) -> tuple[list[Case], list[Case]]:
    if not args.validation_gate or args.validation_gate_size <= 0 or len(cases) < 2:
        return list(cases), []

    max_gate_size_for_pool = max(1, len(cases) // 3)
    gate_size = min(args.validation_gate_size, max_gate_size_for_pool, len(cases) - 1)
    validation_cases = select_cases_with_strategy(
        cases,
        limit=gate_size,
        strategy=args.validation_gate_strategy,
        seed=args.validation_gate_seed,
    )
    validation_ids = {(case.dataset, case.case_id) for case in validation_cases}
    optimize_cases = [case for case in cases if (case.dataset, case.case_id) not in validation_ids]
    return optimize_cases, validation_cases


def write_evaluation_records(path: Path, records: list[Any]) -> None:
    lines = [json.dumps(dataclasses.asdict(record), ensure_ascii=False) for record in records]
    write_text(path, ("\n".join(lines) + "\n") if lines else "")


def make_edit_budget(*, has_accepted_update: bool, args: argparse.Namespace, agent: str) -> dict[str, Any]:
    if agent == "epoch_planner":
        max_revision_items = args.max_sections_per_edit if has_accepted_update else args.initial_max_sections_per_edit
        guidance = [
            "Merge batch-local plans into the smallest revision supported by the strongest repeated evidence.",
            "Prefer modifying or tightening existing guidance over adding independent new rules.",
        ]
    else:
        if has_accepted_update:
            guidance = [
                "Revise only the single highest-impact section.",
                "Prefer modifying or tightening existing guidance over adding independent new rules.",
            ]
        else:
            guidance = [
                "A small multi-section revision is allowed only when the current prompt lacks core generation guidance.",
                "Revise only sections directly supported by failure analysis and error localization.",
            ]
        return {
            "guidance": guidance,
        }
    return {
        "max_revision_items": max_revision_items,
        "guidance": guidance,
    }


def evaluate_iteration_test(
    *,
    prompt: str,
    test_cases: list[Case],
    test_dataset: str,
    args: argparse.Namespace,
    llm_client: LLMClient,
    run_dir: Path,
    iter_dir: Path,
    iteration: int,
) -> dict[str, float]:
    test_dir = iter_dir / "test"
    records_path = test_dir / "records.jsonl"
    summary_path = test_dir / "summary.json"
    analysis_path = test_dir / "analysis.md"
    manifest = {
        "dataset": test_dataset,
        "iteration": iteration,
        "inputs": {
            "prompt": "prompts/after.md",
            "cases": "../test_cases.json",
        },
        "outputs": {
            "records": "test/records.jsonl",
            "summary": "test/summary.json",
            "analysis": "test/analysis.md",
        },
    }
    write_text(test_dir / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    records, summary = evaluate_cases(
        prompt=prompt,
        cases=test_cases,
        args=args,
        llm_client=llm_client,
        output_path=records_path,
        state_dir=run_dir,
        phase=f"iteration_{iteration:03d}:held_out_test",
    )
    write_text(summary_path, json.dumps(summary, ensure_ascii=False, indent=2))
    write_text(analysis_path, build_analysis(records, summary))
    print(f"[iteration {iteration}] held-out test {format_summary(summary)}")
    return summary


def evaluate_initial_iteration_test(
    *,
    prompt: str,
    test_cases: list[Case],
    test_dataset: str,
    args: argparse.Namespace,
    llm_client: LLMClient,
    run_dir: Path,
) -> dict[str, float]:
    iteration = 0
    iter_dir = run_dir / "iteration_000"
    paths = iteration_paths(iter_dir)
    manifest = make_iteration_manifest(iter_dir, iteration, paths)
    manifest["mode"] = "initial_seed_prompt_test"
    write_text(paths["prompt_before"], prompt)
    write_text(paths["prompt_after"], prompt)
    record_stage(
        manifest,
        "initial_held_out_test",
        status="running",
        inputs={"prompt": rel_to_iter(iter_dir, paths["prompt_after"])},
        outputs={"test_summary": "test/summary.json"},
        note="optional baseline evaluation of the original seed prompt before training",
    )
    write_iteration_manifest(iter_dir, manifest)

    summary = evaluate_iteration_test(
        prompt=prompt,
        test_cases=test_cases,
        test_dataset=test_dataset,
        args=args,
        llm_client=llm_client,
        run_dir=run_dir,
        iter_dir=iter_dir,
        iteration=iteration,
    )
    record_stage(
        manifest,
        "initial_held_out_test",
        status="success",
        inputs={"prompt": rel_to_iter(iter_dir, paths["prompt_after"])},
        outputs={"test_summary": "test/summary.json"},
        note="baseline evaluation of the original seed prompt before training",
    )
    write_iteration_manifest(iter_dir, manifest)
    write_iteration_reports(
        iter_dir=iter_dir,
        iteration=iteration,
        prompt_before=prompt,
        prompt_after=prompt,
        candidate_prompt=None,
        analysis_summary={},
        baseline_gate_summary=None,
        candidate_summary=None,
        acceptance=None,
    )
    write_iteration_test_metric_plot(run_dir)
    refresh_run_reports(run_dir)
    return summary


def evaluate_validation_gate(
    *,
    baseline_prompt: str,
    candidate_prompt: str,
    validation_cases: list[Case],
    args: argparse.Namespace,
    llm_client: LLMClient,
    run_dir: Path,
    iter_dir: Path,
    paths: dict[str, Path],
    iteration: int,
    allow_bootstrap: bool,
    phase_prefix: str,
) -> tuple[list[Any], list[Any], dict[str, float], dict[str, float], dict[str, Any]]:
    write_case_manifest(paths["validation_cases"], validation_cases)
    baseline_records, baseline_summary = evaluate_cases(
        prompt=baseline_prompt,
        cases=validation_cases,
        args=args,
        llm_client=llm_client,
        output_path=paths["validation_baseline_records"],
        state_dir=run_dir,
        phase=f"{phase_prefix}:validation_baseline",
    )
    candidate_records, candidate_summary = evaluate_cases(
        prompt=candidate_prompt,
        cases=validation_cases,
        args=args,
        llm_client=llm_client,
        output_path=paths["validation_candidate_records"],
        state_dir=run_dir,
        phase=f"{phase_prefix}:validation_candidate",
    )
    write_text(paths["validation_baseline_summary"], json.dumps(baseline_summary, ensure_ascii=False, indent=2))
    write_text(paths["validation_candidate_summary"], json.dumps(candidate_summary, ensure_ascii=False, indent=2))
    write_text(
        paths["validation_analysis"],
        "# Validation Gate Analysis\n\n"
        "## Baseline\n\n"
        + build_analysis(baseline_records, baseline_summary).strip()
        + "\n\n## Candidate\n\n"
        + build_analysis(candidate_records, candidate_summary).strip()
        + "\n",
    )
    accepted, decision = acceptance_decision(
        iteration=iteration,
        allow_bootstrap=allow_bootstrap,
        baseline_summary=baseline_summary,
        candidate_summary=candidate_summary,
        candidate_prompt=candidate_prompt,
        baseline_prompt=baseline_prompt,
        max_prompt_chars=args.max_prompt_chars,
        min_relation_delta=args.acceptance_min_relation_delta,
        min_node_delta=args.acceptance_min_node_delta,
        min_compile_delta=args.acceptance_min_compile_delta,
        relation_accept_delta=args.relation_accept_delta,
        node_accept_delta=args.node_accept_delta,
        compile_accept_delta=args.compile_accept_delta,
        min_syntax_delta=args.acceptance_min_syntax_delta,
        min_node_precision_delta=args.acceptance_min_node_precision_delta,
        min_relation_precision_delta=args.acceptance_min_relation_precision_delta,
        bootstrap_min_compile_delta=args.bootstrap_min_compile_delta,
        bootstrap_min_syntax_delta=args.bootstrap_min_syntax_delta,
        bootstrap_node_accept_delta=args.bootstrap_node_accept_delta,
        bootstrap_relation_accept_delta=args.bootstrap_relation_accept_delta,
    )
    decision["accepted"] = accepted
    decision["evaluation_source"] = "validation_gate"
    decision["validation_case_count"] = len(validation_cases)
    return baseline_records, candidate_records, baseline_summary, candidate_summary, decision


def write_iteration_test_metric_plot(run_dir: Path) -> None:
    rows: list[dict[str, float | int]] = []
    for iter_dir in sorted(run_dir.glob("iteration_*")):
        try:
            iteration = int(iter_dir.name.rsplit("_", 1)[-1])
        except ValueError:
            continue
        summary_path = iter_dir / "test" / "summary.json"
        if not summary_path.exists():
            continue
        summary = json.loads(read_text(summary_path))
        row: dict[str, float | int] = {"iteration": iteration}
        for key in ITERATION_TEST_METRIC_KEYS:
            row[key] = float(summary.get(key, 0.0))
        rows.append(row)

    csv_path = run_dir / "iteration_test_metrics.csv"
    fieldnames = ["iteration", *ITERATION_TEST_METRIC_KEYS]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    if not rows:
        return

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x_values = [int(row["iteration"]) for row in rows]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for key in ITERATION_TEST_METRIC_KEYS:
        y_values = [float(row[key]) for row in rows]
        ax.plot(x_values, y_values, marker="o", linewidth=2, label=key)
    ax.set_xlabel("Iteration")
    ax.set_ylabel("Metric")
    ax.set_title("Held-out Test Metrics by Iteration")
    ax.set_xticks(x_values)
    ax.set_ylim(0.0, 1.0)
    ax.grid(True, linestyle="--", alpha=0.35)
    ax.legend(loc="best")
    fig.tight_layout()
    fig.savefig(run_dir / "iteration_test_metrics.png", dpi=160)
    plt.close(fig)


def run_training_iterations(
    *,
    args: argparse.Namespace,
    llm_client: LLMClient,
    train_cases: list[Case],
    run_dir: Path,
    work_prompt_path: Path,
    label: str,
    validation_cases: list[Case] | None = None,
    test_cases: list[Case] | None = None,
    test_dataset: str | None = None,
) -> tuple[str, dict[str, float]]:
    print(f"[run] {label}, train_cases={len(train_cases)}")
    print(f"[run] train distribution: {describe_case_distribution(train_cases)}")
    validation_cases = list(validation_cases or [])
    if validation_cases:
        print(f"[run] validation gate cases={len(validation_cases)}")
        print(f"[run] validation gate distribution: {describe_case_distribution(validation_cases)}")
    print(f"[run] output={run_dir}")

    prompt = read_text(work_prompt_path)
    last_summary: dict[str, float] = {}
    last_test_summary: dict[str, float] | None = None
    global_update_step = 0
    has_accepted_update = False

    for iteration in range(1, args.iterations + 1):
        iter_dir = run_dir / f"iteration_{iteration:03d}"
        epoch_paths = iteration_paths(iter_dir)
        epoch_manifest = make_iteration_manifest(iter_dir, iteration, epoch_paths)
        epoch_manifest["mode"] = "epoch_planner_updates"
        epoch_prompt_before = prompt
        write_text(epoch_paths["prompt_before"], prompt)
        write_case_manifest(epoch_paths["analysis_cases"], train_cases)
        if validation_cases:
            write_case_manifest(epoch_paths["validation_cases"], validation_cases)

        training_batches = split_training_batches(train_cases, args.analysis_batch_size, strategy=args.training_batch_strategy)
        epoch_manifest["train_batch_count"] = len(training_batches)
        epoch_manifest["train_batch_strategy"] = args.training_batch_strategy
        record_stage(
            epoch_manifest,
            "epoch_batching",
            status="success",
            outputs={"cases": rel_to_iter(iter_dir, epoch_paths["analysis_cases"])},
            note=(
                f"split train cases into {len(training_batches)} batch(es) "
                f"with analysis_batch_size={args.analysis_batch_size}, strategy={args.training_batch_strategy}"
            ),
        )
        write_iteration_manifest(iter_dir, epoch_manifest)

        epoch_accepted_count = 0
        epoch_rejected_count = 0
        epoch_skipped_count = 0
        epoch_collected_count = 0
        epoch_records = []
        batch_summaries: list[dict[str, Any]] = []
        batch_revision_inputs: list[dict[str, Any]] = []
        print(f"\n[iteration {iteration}] training epoch with {len(training_batches)} batch(es)")

        for batch_index, analysis_cases in enumerate(training_batches, start=1):
            global_update_step += 1
            batch_dir = iter_dir / "train_batches" / f"batch_{batch_index:03d}"
            paths = iteration_paths(batch_dir)
            manifest = make_iteration_manifest(batch_dir, global_update_step, paths)
            manifest["epoch_iteration"] = iteration
            manifest["batch_index"] = batch_index
            manifest["global_update_step"] = global_update_step
            prompt_before = prompt
            phase_prefix = f"iteration_{iteration:03d}:batch_{batch_index:03d}"
            log_prefix = f"[iteration {iteration} batch {batch_index}/{len(training_batches)}]"

            write_text(paths["prompt_before"], prompt)
            write_case_manifest(paths["analysis_cases"], analysis_cases)
            record_stage(
                manifest,
                "analysis_batch_sampling",
                status="success",
                outputs={"cases": rel_to_iter(batch_dir, paths["analysis_cases"])},
            )
            write_iteration_manifest(batch_dir, manifest)

            print(f"{log_prefix} evaluating analysis batch")
            print(f"{log_prefix} analysis batch distribution: {describe_case_distribution(analysis_cases)}")
            records, summary = evaluate_cases(
                prompt=prompt,
                cases=analysis_cases,
                args=args,
                llm_client=llm_client,
                output_path=paths["analysis_records"],
                state_dir=run_dir,
                phase=f"{phase_prefix}:analysis_batch",
            )
            last_summary = summary
            epoch_records.extend(records)
            batch_summaries.append(
                {
                    "batch_index": batch_index,
                    "global_update_step": global_update_step,
                    "case_count": len(analysis_cases),
                    "summary": summary,
                }
            )
            write_text(paths["analysis_summary"], json.dumps(summary, ensure_ascii=False, indent=2))
            record_stage(
                manifest,
                "analysis_evaluation",
                status="success",
                inputs={
                    "prompt": rel_to_iter(batch_dir, paths["prompt_before"]),
                    "cases": rel_to_iter(batch_dir, paths["analysis_cases"]),
                },
                outputs={
                    "records": rel_to_iter(batch_dir, paths["analysis_records"]),
                    "summary": rel_to_iter(batch_dir, paths["analysis_summary"]),
                },
            )
            write_iteration_manifest(batch_dir, manifest)

            analysis = build_analysis(records, summary)
            write_text(paths["analysis_overview"], analysis)
            print(f"{log_prefix} train {format_summary(summary)}")

            if args.no_evolve:
                epoch_skipped_count += 1
                write_text(paths["prompt_after"], prompt)
                record_stage(
                    manifest,
                    "evolution",
                    status="skipped",
                    note="--no-evolve was set; prompt unchanged",
                    outputs={"prompt_after": rel_to_iter(batch_dir, paths["prompt_after"])},
                )
                write_iteration_manifest(batch_dir, manifest)
                finalize_iteration_reports(
                    run_dir=run_dir,
                    iter_dir=batch_dir,
                    iteration=global_update_step,
                    prompt_before=prompt_before,
                    prompt_after=prompt,
                    candidate_prompt=None,
                    analysis_summary=summary,
                )
                print(f"{log_prefix} prompt unchanged")
                continue

            if has_only_infrastructure_errors(records):
                epoch_skipped_count += 1
                write_text(
                    paths["update_skipped"],
                    "Skipped prompt update because every evaluated case failed before a model output was available.\n",
                )
                write_text(paths["prompt_after"], prompt)
                record_stage(
                    manifest,
                    "evolution",
                    status="skipped",
                    note="all analysis records were infrastructure errors",
                    outputs={
                        "skip_note": rel_to_iter(batch_dir, paths["update_skipped"]),
                        "prompt_after": rel_to_iter(batch_dir, paths["prompt_after"]),
                    },
                )
                write_iteration_manifest(batch_dir, manifest)
                finalize_iteration_reports(
                    run_dir=run_dir,
                    iter_dir=batch_dir,
                    iteration=global_update_step,
                    prompt_before=prompt_before,
                    prompt_after=prompt,
                    candidate_prompt=None,
                    analysis_summary=summary,
                )
                print(f"{log_prefix} infrastructure-only failures; prompt unchanged")
                continue

            failure_analysis = analyze_failures(
                current_prompt=prompt,
                records=records,
                summary=summary,
                args=args,
                llm_client=llm_client,
                output_input_path=paths["failure_analysis_input"],
                output_path=paths["failure_analysis_output"],
                state_dir=run_dir,
                iteration=global_update_step,
            )
            if failure_analysis is None:
                epoch_skipped_count += 1
                write_text(paths["prompt_after"], prompt)
                record_stage(
                    manifest,
                    "failure_analysis",
                    status="invalid",
                    inputs={"records": rel_to_iter(batch_dir, paths["analysis_records"])},
                    outputs={
                        "input": rel_to_iter(batch_dir, paths["failure_analysis_input"]),
                        "output": rel_to_iter(batch_dir, paths["failure_analysis_output"]),
                        "prompt_after": rel_to_iter(batch_dir, paths["prompt_after"]),
                    },
                )
                write_iteration_manifest(batch_dir, manifest)
                finalize_iteration_reports(
                    run_dir=run_dir,
                    iter_dir=batch_dir,
                    iteration=global_update_step,
                    prompt_before=prompt_before,
                    prompt_after=prompt,
                    candidate_prompt=None,
                    analysis_summary=summary,
                )
                print(f"{log_prefix} failure analysis invalid; prompt unchanged")
                continue
            record_stage(
                manifest,
                "failure_analysis",
                status="success",
                inputs={"records": rel_to_iter(batch_dir, paths["analysis_records"])},
                outputs={
                    "input": rel_to_iter(batch_dir, paths["failure_analysis_input"]),
                    "output": rel_to_iter(batch_dir, paths["failure_analysis_output"]),
                },
            )
            write_iteration_manifest(batch_dir, manifest)

            error_localization = localize_errors(
                current_prompt=prompt,
                failure_analysis=failure_analysis,
                args=args,
                llm_client=llm_client,
                output_input_path=paths["error_localization_input"],
                output_path=paths["error_localization_output"],
                state_dir=run_dir,
                iteration=global_update_step,
            )
            if error_localization is None:
                epoch_skipped_count += 1
                write_text(paths["prompt_after"], prompt)
                record_stage(
                    manifest,
                    "error_localization",
                    status="invalid",
                    inputs={
                        "prompt_before": rel_to_iter(batch_dir, paths["prompt_before"]),
                        "failure_analysis": rel_to_iter(batch_dir, paths["failure_analysis_output"]),
                    },
                    outputs={
                        "input": rel_to_iter(batch_dir, paths["error_localization_input"]),
                        "output": rel_to_iter(batch_dir, paths["error_localization_output"]),
                        "prompt_after": rel_to_iter(batch_dir, paths["prompt_after"]),
                    },
                )
                write_iteration_manifest(batch_dir, manifest)
                finalize_iteration_reports(
                    run_dir=run_dir,
                    iter_dir=batch_dir,
                    iteration=global_update_step,
                    prompt_before=prompt_before,
                    prompt_after=prompt,
                    candidate_prompt=None,
                    analysis_summary=summary,
                )
                print(f"{log_prefix} error localization invalid; prompt unchanged")
                continue
            record_stage(
                manifest,
                "error_localization",
                status="success",
                inputs={
                    "prompt_before": rel_to_iter(batch_dir, paths["prompt_before"]),
                    "failure_analysis": rel_to_iter(batch_dir, paths["failure_analysis_output"]),
                },
                outputs={
                    "input": rel_to_iter(batch_dir, paths["error_localization_input"]),
                    "output": rel_to_iter(batch_dir, paths["error_localization_output"]),
                },
            )
            write_iteration_manifest(batch_dir, manifest)

            editor_edit_budget = make_edit_budget(
                has_accepted_update=has_accepted_update,
                args=args,
                agent="prompt_editor",
            )
            revision_plan = propose_prompt_revision(
                current_prompt=prompt,
                failure_analysis=failure_analysis,
                error_localization=error_localization,
                edit_budget=editor_edit_budget,
                args=args,
                llm_client=llm_client,
                output_input_path=paths["prompt_editor_input"],
                output_path=paths["prompt_editor_output"],
                state_dir=run_dir,
                iteration=global_update_step,
            )
            if revision_plan is None:
                epoch_skipped_count += 1
                write_text(paths["prompt_after"], prompt)
                record_stage(
                    manifest,
                    "prompt_editor",
                    status="invalid",
                    inputs={
                        "prompt_before": rel_to_iter(batch_dir, paths["prompt_before"]),
                        "failure_analysis": rel_to_iter(batch_dir, paths["failure_analysis_output"]),
                        "error_localization": rel_to_iter(batch_dir, paths["error_localization_output"]),
                    },
                    outputs={
                        "input": rel_to_iter(batch_dir, paths["prompt_editor_input"]),
                        "output": rel_to_iter(batch_dir, paths["prompt_editor_output"]),
                        "prompt_after": rel_to_iter(batch_dir, paths["prompt_after"]),
                    },
                )
                write_iteration_manifest(batch_dir, manifest)
                finalize_iteration_reports(
                    run_dir=run_dir,
                    iter_dir=batch_dir,
                    iteration=global_update_step,
                    prompt_before=prompt_before,
                    prompt_after=prompt,
                    candidate_prompt=None,
                    analysis_summary=summary,
                )
                print(f"{log_prefix} prompt revision plan invalid; prompt unchanged")
                continue
            record_stage(
                manifest,
                "prompt_editor",
                status="success",
                inputs={
                    "prompt_before": rel_to_iter(batch_dir, paths["prompt_before"]),
                    "failure_analysis": rel_to_iter(batch_dir, paths["failure_analysis_output"]),
                    "error_localization": rel_to_iter(batch_dir, paths["error_localization_output"]),
                },
                outputs={
                    "input": rel_to_iter(batch_dir, paths["prompt_editor_input"]),
                    "output": rel_to_iter(batch_dir, paths["prompt_editor_output"]),
                },
            )
            write_iteration_manifest(batch_dir, manifest)

            batch_revision_inputs.append(
                {
                    "analysis_summary": summary,
                    "failure_analysis": failure_analysis,
                    "error_localization": error_localization,
                    "revision_plan": revision_plan.get("revision_plan", []),
                }
            )
            epoch_collected_count += 1
            write_text(paths["prompt_after"], prompt)
            record_stage(
                manifest,
                "epoch_revision_collection",
                status="success",
                inputs={
                    "prompt_before": rel_to_iter(batch_dir, paths["prompt_before"]),
                    "revision_plan": rel_to_iter(batch_dir, paths["prompt_editor_output"]),
                },
                outputs={"prompt_after": rel_to_iter(batch_dir, paths["prompt_after"])},
                note="batch-local revision plan collected for epoch planner; prompt unchanged",
            )
            write_iteration_manifest(batch_dir, manifest)
            finalize_iteration_reports(
                run_dir=run_dir,
                iter_dir=batch_dir,
                iteration=global_update_step,
                prompt_before=prompt_before,
                prompt_after=prompt,
                candidate_prompt=None,
                analysis_summary=summary,
            )
            print(f"{log_prefix} revision plan collected for epoch planner")

        epoch_summary = summarize_records(epoch_records)
        epoch_candidate_prompt: str | None = None
        epoch_baseline_gate_summary: dict[str, float] | None = None
        epoch_candidate_summary: dict[str, float] | None = None
        epoch_acceptance: dict[str, Any] = {
            "accepted": False,
            "acceptance_mode": "epoch_planner",
            "rejection_reasons": [],
            "batch_count": len(training_batches),
            "collected_batch_count": epoch_collected_count,
            "skipped_batch_count": epoch_skipped_count,
        }

        if args.no_evolve:
            epoch_acceptance["rejection_reasons"] = ["no_evolve"]
        elif not batch_revision_inputs:
            epoch_acceptance["rejection_reasons"] = ["no_batch_revision_plans"]
        else:
            print(f"[iteration {iteration}] planning epoch revision from {len(batch_revision_inputs)} batch plan(s)")
            epoch_edit_budget = make_edit_budget(
                has_accepted_update=has_accepted_update,
                args=args,
                agent="epoch_planner",
            )
            epoch_revision_plan = plan_epoch_revision(
                current_prompt=prompt,
                batch_revision_inputs=batch_revision_inputs,
                edit_budget=epoch_edit_budget,
                args=args,
                llm_client=llm_client,
                output_input_path=epoch_paths["epoch_planner_input"],
                output_path=epoch_paths["epoch_planner_output"],
                state_dir=run_dir,
                iteration=iteration,
            )
            if epoch_revision_plan is None:
                epoch_skipped_count += 1
                epoch_acceptance.update(
                    {
                        "rejection_reasons": ["epoch_planner_invalid"],
                        "batch_count": len(training_batches),
                        "collected_batch_count": epoch_collected_count,
                        "skipped_batch_count": epoch_skipped_count,
                    }
                )
                record_stage(
                    epoch_manifest,
                    "epoch_planner",
                    status="invalid",
                    inputs={"batch_revision_inputs": rel_to_iter(iter_dir, epoch_paths["epoch_planner_input"])},
                    outputs={"output": rel_to_iter(iter_dir, epoch_paths["epoch_planner_output"])},
                )
            else:
                record_stage(
                    epoch_manifest,
                    "epoch_planner",
                    status="success",
                    inputs={"batch_revision_inputs": rel_to_iter(iter_dir, epoch_paths["epoch_planner_input"])},
                    outputs={"revision_plan": rel_to_iter(iter_dir, epoch_paths["epoch_planner_output"])},
                )
                allow_bootstrap = not has_accepted_update
                epoch_candidate_prompt = rewrite_prompt(
                    current_prompt=prompt,
                    revision_plan=epoch_revision_plan,
                    args=args,
                    llm_client=llm_client,
                    output_input_path=epoch_paths["prompt_rewriter_input"],
                    output_path=epoch_paths["prompt_rewriter_output"],
                    state_dir=run_dir,
                    iteration=iteration,
                )
                if epoch_candidate_prompt is None:
                    epoch_skipped_count += 1
                    epoch_acceptance.update(
                        {
                            "rejection_reasons": ["prompt_rewriter_invalid"],
                            "batch_count": len(training_batches),
                            "collected_batch_count": epoch_collected_count,
                            "skipped_batch_count": epoch_skipped_count,
                        }
                    )
                    record_stage(
                        epoch_manifest,
                        "prompt_rewriter",
                        status="invalid",
                        inputs={"revision_plan": rel_to_iter(iter_dir, epoch_paths["epoch_planner_output"])},
                        outputs={"output": rel_to_iter(iter_dir, epoch_paths["prompt_rewriter_output"])},
                    )
                else:
                    write_text(epoch_paths["prompt_candidate"], epoch_candidate_prompt)
                    record_stage(
                        epoch_manifest,
                        "prompt_rewriter",
                        status="success",
                        inputs={"revision_plan": rel_to_iter(iter_dir, epoch_paths["epoch_planner_output"])},
                        outputs={
                            "input": rel_to_iter(iter_dir, epoch_paths["prompt_rewriter_input"]),
                            "output": rel_to_iter(iter_dir, epoch_paths["prompt_rewriter_output"]),
                            "candidate_prompt": rel_to_iter(iter_dir, epoch_paths["prompt_candidate"]),
                        },
                    )
                    if validation_cases:
                        print(f"[iteration {iteration}] evaluating epoch candidate on fixed validation gate")
                        (
                            _validation_baseline_records,
                            _validation_candidate_records,
                            epoch_baseline_gate_summary,
                            epoch_candidate_summary,
                            epoch_acceptance,
                        ) = evaluate_validation_gate(
                            baseline_prompt=prompt,
                            candidate_prompt=epoch_candidate_prompt,
                            validation_cases=validation_cases,
                            args=args,
                            llm_client=llm_client,
                            run_dir=run_dir,
                            iter_dir=iter_dir,
                            paths=epoch_paths,
                            iteration=iteration,
                            allow_bootstrap=allow_bootstrap,
                            phase_prefix=f"iteration_{iteration:03d}:epoch",
                        )
                        write_text(epoch_paths["acceptance"], json.dumps(epoch_acceptance, ensure_ascii=False, indent=2))
                        if epoch_acceptance["accepted"]:
                            epoch_accepted_count = 1
                            has_accepted_update = True
                            prompt = epoch_candidate_prompt
                            write_text(work_prompt_path, prompt)
                            write_text(run_dir / "prompt_best.md", prompt)
                            record_stage(
                                epoch_manifest,
                                "validation_gate",
                                status="accepted",
                                inputs={
                                    "baseline_prompt": rel_to_iter(iter_dir, epoch_paths["prompt_before"]),
                                    "candidate_prompt": rel_to_iter(iter_dir, epoch_paths["prompt_candidate"]),
                                    "cases": rel_to_iter(iter_dir, epoch_paths["validation_cases"]),
                                },
                                outputs={
                                    "baseline_summary": rel_to_iter(iter_dir, epoch_paths["validation_baseline_summary"]),
                                    "candidate_summary": rel_to_iter(iter_dir, epoch_paths["validation_candidate_summary"]),
                                    "decision": rel_to_iter(iter_dir, epoch_paths["acceptance"]),
                                },
                            )
                            print(f"[iteration {iteration}] epoch candidate accepted by validation gate: {work_prompt_path}")
                        else:
                            epoch_rejected_count = 1
                            write_text(epoch_paths["rejected_by_gate"], json.dumps(epoch_acceptance, ensure_ascii=False, indent=2))
                            record_stage(
                                epoch_manifest,
                                "validation_gate",
                                status="rejected",
                                inputs={
                                    "baseline_prompt": rel_to_iter(iter_dir, epoch_paths["prompt_before"]),
                                    "candidate_prompt": rel_to_iter(iter_dir, epoch_paths["prompt_candidate"]),
                                    "cases": rel_to_iter(iter_dir, epoch_paths["validation_cases"]),
                                },
                                outputs={
                                    "baseline_summary": rel_to_iter(iter_dir, epoch_paths["validation_baseline_summary"]),
                                    "candidate_summary": rel_to_iter(iter_dir, epoch_paths["validation_candidate_summary"]),
                                    "decision": rel_to_iter(iter_dir, epoch_paths["acceptance"]),
                                    "rejection_copy": rel_to_iter(iter_dir, epoch_paths["rejected_by_gate"]),
                                },
                            )
                            print(
                                f"[iteration {iteration}] epoch candidate rejected by validation gate "
                                f"(reasons={', '.join(epoch_acceptance['rejection_reasons'])}); prompt unchanged"
                            )
                    else:
                        epoch_accepted_count = 1
                        has_accepted_update = True
                        prompt = epoch_candidate_prompt
                        write_text(work_prompt_path, prompt)
                        write_text(run_dir / "prompt_best.md", prompt)
                        epoch_acceptance = {
                            "accepted": True,
                            "acceptance_mode": "epoch_planner",
                            "gate_evaluated": False,
                            "rejection_reasons": [],
                            "batch_count": len(training_batches),
                            "collected_batch_count": epoch_collected_count,
                            "skipped_batch_count": epoch_skipped_count,
                            "note": "Validation gate is disabled; epoch candidate prompt applied directly.",
                        }
                        record_stage(
                            epoch_manifest,
                            "acceptance",
                            status="accepted",
                            inputs={
                                "candidate_prompt": rel_to_iter(iter_dir, epoch_paths["prompt_candidate"]),
                            },
                            outputs={"decision": rel_to_iter(iter_dir, epoch_paths["acceptance"])},
                            note="validation gate disabled; candidate prompt applied directly",
                        )
                        print(f"[iteration {iteration}] epoch candidate applied directly: {work_prompt_path}")
        write_text(epoch_paths["prompt_after"], prompt)
        write_evaluation_records(epoch_paths["analysis_records"], epoch_records)
        write_text(epoch_paths["analysis_summary"], json.dumps(epoch_summary, ensure_ascii=False, indent=2))
        write_text(epoch_paths["analysis_overview"], build_analysis(epoch_records, epoch_summary))
        write_text(iter_dir / "evaluation" / "batch_summaries.json", json.dumps(batch_summaries, ensure_ascii=False, indent=2))
        write_text(epoch_paths["acceptance"], json.dumps(epoch_acceptance, ensure_ascii=False, indent=2))
        record_stage(
            epoch_manifest,
            "epoch_training",
            status="success",
            inputs={"prompt_before": rel_to_iter(iter_dir, epoch_paths["prompt_before"])},
            outputs={
                "prompt_after": rel_to_iter(iter_dir, epoch_paths["prompt_after"]),
                "analysis_records": rel_to_iter(iter_dir, epoch_paths["analysis_records"]),
                "analysis_summary": rel_to_iter(iter_dir, epoch_paths["analysis_summary"]),
                "batch_summaries": "evaluation/batch_summaries.json",
                "acceptance": rel_to_iter(iter_dir, epoch_paths["acceptance"]),
            },
            note=(
                f"accepted={epoch_accepted_count}, rejected={epoch_rejected_count}, "
                f"skipped={epoch_skipped_count}"
            ),
        )
        write_iteration_manifest(iter_dir, epoch_manifest)
        finalize_iteration_reports(
            run_dir=run_dir,
            iter_dir=iter_dir,
            iteration=iteration,
            prompt_before=epoch_prompt_before,
            prompt_after=prompt,
            candidate_prompt=epoch_candidate_prompt,
            analysis_summary=epoch_summary,
            baseline_gate_summary=epoch_baseline_gate_summary,
            candidate_summary=epoch_candidate_summary,
            acceptance=epoch_acceptance,
        )
        last_summary = epoch_summary
        print(
            f"[iteration {iteration}] epoch complete: "
            f"accepted={epoch_accepted_count}, rejected={epoch_rejected_count}, skipped={epoch_skipped_count}"
        )
        if test_cases is not None and test_dataset is not None:
            print(f"\n[iteration {iteration}] evaluating held-out dataset {test_dataset}")
            last_test_summary = evaluate_iteration_test(
                prompt=prompt,
                test_cases=test_cases,
                test_dataset=test_dataset,
                args=args,
                llm_client=llm_client,
                run_dir=run_dir,
                iter_dir=iter_dir,
                iteration=iteration,
            )
            write_iteration_test_metric_plot(run_dir)
            refresh_run_reports(run_dir)

    final_prompt = read_text(work_prompt_path)
    write_text(run_dir / "prompt_final.md", final_prompt)
    if test_cases is not None and test_dataset is not None:
        write_iteration_test_metric_plot(run_dir)
    refresh_run_reports(run_dir)
    return final_prompt, last_test_summary or last_summary


def run_train_only(args: argparse.Namespace, datasets: dict[str, list[Case]], llm_client: LLMClient, train_dataset: str) -> dict[str, float]:
    train_dataset = train_dataset.lower()
    if train_dataset not in datasets:
        raise ValueError(f"Unknown train dataset {train_dataset!r}. Available: {', '.join(sorted(datasets))}")
    train_pool_cases = select_cases_with_strategy(
        datasets[train_dataset],
        limit=args.max_train_cases,
        strategy=args.sample_strategy,
        seed=args.sample_seed,
    )
    train_cases, validation_cases = split_validation_gate_cases(train_pool_cases, args)
    run_dir = make_run_dir(args.runs_dir, f"train-{train_dataset}")
    write_run_args(args, run_dir)
    write_case_manifest(run_dir / "train_pool_cases.json", train_pool_cases)
    write_case_manifest(run_dir / "train_cases.json", train_cases)
    if validation_cases:
        write_case_manifest(run_dir / "validation_gate_cases.json", validation_cases)
    work_prompt_path = initialize_run_prompt(args.prompt_path, run_dir)
    _, summary = run_training_iterations(
        args=args,
        llm_client=llm_client,
        train_cases=train_cases,
        run_dir=run_dir,
        work_prompt_path=work_prompt_path,
        label=f"train_only={train_dataset}",
        validation_cases=validation_cases,
    )
    return summary


def run_one_split(args: argparse.Namespace, datasets: dict[str, list[Case]], llm_client: LLMClient, test_dataset: str) -> dict[str, float]:
    test_dataset = test_dataset.lower()
    if test_dataset not in datasets:
        raise ValueError(f"Unknown test dataset {test_dataset!r}. Available: {', '.join(sorted(datasets))}")

    train_cases_all = [case for name, cases in datasets.items() if name != test_dataset for case in cases]
    test_cases_all = datasets[test_dataset]
    train_pool_cases = select_cases_with_strategy(
        train_cases_all,
        limit=args.max_train_cases,
        strategy=args.sample_strategy,
        seed=args.sample_seed,
    )
    train_cases, validation_cases = split_validation_gate_cases(train_pool_cases, args)
    test_cases = select_cases_with_strategy(
        test_cases_all,
        limit=args.max_test_cases,
        strategy=args.test_sample_strategy,
        seed=args.sample_seed + 20_000,
    )

    run_dir = make_run_dir(args.runs_dir, f"test-{test_dataset}")
    write_run_args(args, run_dir)
    write_case_manifest(run_dir / "train_pool_cases.json", train_pool_cases)
    write_case_manifest(run_dir / "train_cases.json", train_cases)
    if validation_cases:
        write_case_manifest(run_dir / "validation_gate_cases.json", validation_cases)
    write_case_manifest(run_dir / "test_cases.json", test_cases)
    work_prompt_path = initialize_run_prompt(args.prompt_path, run_dir)
    print(
        f"[run] test={test_dataset}, train_pool_cases={len(train_pool_cases)}, "
        f"train_cases={len(train_cases)}, validation_gate_cases={len(validation_cases)}, "
        f"test_cases={len(test_cases)}"
    )
    print(f"[run] test distribution: {describe_case_distribution(test_cases)}")
    initial_summary: dict[str, float] | None = None
    if args.eval_initial_test:
        print(f"\n[iteration 0] evaluating original prompt on held-out dataset {test_dataset}")
        initial_summary = evaluate_initial_iteration_test(
            prompt=read_text(work_prompt_path),
            test_cases=test_cases,
            test_dataset=test_dataset,
            args=args,
            llm_client=llm_client,
            run_dir=run_dir,
        )

    _, summary = run_training_iterations(
        args=args,
        llm_client=llm_client,
        train_cases=train_cases,
        run_dir=run_dir,
        work_prompt_path=work_prompt_path,
        label=f"test={test_dataset}",
        validation_cases=validation_cases,
        test_cases=test_cases,
        test_dataset=test_dataset,
    )
    if not summary and initial_summary is not None:
        summary = initial_summary
    refresh_run_reports(run_dir)
    print(f"[test] final iteration held-out {format_summary(summary)}")
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
    parser.add_argument("--epoch-planner-prompt-path", type=Path, default=DEFAULT_EPOCH_PLANNER_PROMPT_PATH, help="System prompt markdown for the epoch-level revision planner model")
    parser.add_argument("--prompt-rewriter-prompt-path", type=Path, default=DEFAULT_PROMPT_REWRITER_PROMPT_PATH, help="System prompt markdown for the prompt-rewrite model")
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    parser.add_argument("--plantuml-jar", type=Path, default=DEFAULT_PLANTUML_JAR)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--max-train-cases", type=int, default=0, help="0 means all training cases")
    parser.add_argument("--max-test-cases", type=int, default=0, help="0 means all test cases")
    parser.add_argument(
        "--eval-initial-test",
        action="store_true",
        help="Evaluate the original seed prompt as iteration_000/test before training",
    )
    parser.add_argument("--analysis-batch-size", type=int, default=10, help="Training batch size used for generation and failure analysis")
    parser.add_argument("--training-batch-strategy", choices=["stratified", "chunked"], default="stratified", help="How to split training cases into analysis batches")
    parser.add_argument("--sample-strategy", choices=["stratified", "random", "prefix"], default="stratified", help="How to select limited training cases")
    parser.add_argument("--test-sample-strategy", choices=["stratified", "random", "prefix"], default="prefix", help="How to select limited held-out test cases")
    parser.add_argument("--validation-gate", action=argparse.BooleanOptionalAction, default=True, help="Reserve a fixed validation gate split from the training pool; use --no-validation-gate to disable")
    parser.add_argument("--validation-gate-size", type=int, default=30, help="Maximum number of training-pool cases reserved for validation gate; capped at about one third of the sampled training pool, 0 disables the split")
    parser.add_argument("--validation-gate-strategy", choices=["stratified", "random", "prefix"], default="stratified", help="How to choose fixed validation gate cases from the sampled training pool")
    parser.add_argument("--validation-gate-seed", type=int, default=20260629, help="Seed used only for selecting fixed validation gate cases")
    parser.add_argument("--sample-seed", type=int, default=13)
    parser.add_argument("--model", default=os.environ.get("ZHIPU_LLM_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-key", default=os.environ.get("ZHIPU_LLM_API_KEY", ""))
    parser.add_argument("--base-url", default=os.environ.get("ZHIPU_LLM_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--analysis-temperature", type=float, default=0.2)
    parser.add_argument("--localization-temperature", type=float, default=0.2)
    parser.add_argument("--editor-temperature", type=float, default=0.2)
    parser.add_argument("--epoch-planner-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=optional_float, default=None, help="GLM top_p, or 'omit' to use provider default")
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--analysis-max-tokens", type=int, default=4096)
    parser.add_argument("--localization-max-tokens", type=int, default=4096)
    parser.add_argument("--editor-max-tokens", type=int, default=4096)
    parser.add_argument("--epoch-planner-max-tokens", type=int, default=4096)
    parser.add_argument("--thinking", choices=["enabled", "disabled"], default=os.environ.get("ZHIPU_THINKING_TYPE", DEFAULT_THINKING_TYPE), help="Default thinking mode for all model calls unless an agent-specific option overrides it")
    parser.add_argument("--generation-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_GENERATION_THINKING_TYPE", "inherit"), help="Thinking mode for PlantUML generation calls")
    parser.add_argument("--analysis-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_ANALYSIS_THINKING_TYPE", "inherit"), help="Thinking mode for failure-analysis calls")
    parser.add_argument("--localization-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_LOCALIZATION_THINKING_TYPE", "inherit"), help="Thinking mode for error-localization calls")
    parser.add_argument("--editor-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_EDITOR_THINKING_TYPE", "inherit"), help="Thinking mode for prompt-editor calls")
    parser.add_argument("--epoch-planner-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_EPOCH_PLANNER_THINKING_TYPE", "inherit"), help="Thinking mode for epoch-planner calls")
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
    parser.add_argument("--acceptance-min-node-delta", type=float, default=-0.01, help="Minimum node F1 delta tolerated by the standard validation gate")
    parser.add_argument("--acceptance-min-relation-delta", type=float, default=-0.01, help="Minimum relation F1 delta tolerated by the standard validation gate")
    parser.add_argument("--acceptance-min-compile-delta", type=float, default=-0.01, help="Minimum PlantUML compilation pass-rate delta tolerated by the standard validation gate")
    parser.add_argument("--acceptance-min-syntax-delta", type=float, default=-0.01, help="Minimum syntax pass-rate delta tolerated by the standard validation gate")
    parser.add_argument("--acceptance-min-node-precision-delta", type=float, default=-0.02, help="Minimum node precision delta tolerated by the standard validation gate")
    parser.add_argument("--acceptance-min-relation-precision-delta", type=float, default=-0.02, help="Minimum relation precision delta tolerated by the standard validation gate")
    parser.add_argument("--relation-accept-delta", type=float, default=0.02, help="Relation F1 delta required as a positive signal in the standard validation gate")
    parser.add_argument("--node-accept-delta", type=float, default=0.02, help="Node F1 delta required as a positive signal in the standard validation gate")
    parser.add_argument("--compile-accept-delta", type=float, default=0.05, help="PlantUML compilation pass-rate delta that can accept a candidate when node and relation F1 do not regress")
    parser.add_argument("--bootstrap-min-compile-delta", type=float, default=-0.10, help="Minimum PlantUML compilation pass-rate delta tolerated before the first accepted update")
    parser.add_argument("--bootstrap-min-syntax-delta", type=float, default=-0.10, help="Minimum syntax pass-rate delta tolerated before the first accepted update")
    parser.add_argument("--bootstrap-node-accept-delta", type=float, default=0.05, help="Node F1 delta required before the first accepted update")
    parser.add_argument("--bootstrap-relation-accept-delta", type=float, default=0.05, help="Relation F1 delta required before the first accepted update")
    parser.add_argument(
        "--initial-max-sections-per-edit",
        type=int,
        default=3,
        help="Maximum fixed prompt sections a prompt edit may revise before the first accepted update; 0 disables the limit",
    )
    parser.add_argument(
        "--max-sections-per-edit",
        type=int,
        default=1,
        help="Maximum fixed prompt sections a prompt edit may revise after the first accepted update; 0 disables the limit",
    )
    parser.add_argument("--max-prompt-chars", type=int, default=4000, help="Reject candidate prompts longer than this many characters")
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
    args.epoch_planner_prompt_path = args.epoch_planner_prompt_path.resolve()
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
    args.epoch_planner_thinking = resolve_agent_thinking(args.epoch_planner_thinking, args.thinking)
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
    read_prompt_file(args.epoch_planner_prompt_path, label="epoch planner")
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
