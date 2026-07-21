#!/usr/bin/env python3
"""Entry point for APE prompt evolution."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import dataclasses
import hashlib
import json
import os
import statistics
from pathlib import Path
from typing import Any

from analysis.error_localization import localize_errors
from analysis.epoch_planner import plan_epoch_revision
from analysis.failure_analysis import analyze_failures, build_analysis
from analysis.mechanism_clustering import (
    build_mechanism_observations,
    calibration_statistics,
    failure_analysis_item_count,
    load_mechanism_taxonomy,
    make_revision_scope,
    revision_scope_key,
    sanitize_selected_failure_analysis,
    select_epoch_mechanism,
)
from analysis.mechanism_memory import (
    load_memory,
    mark_hypothesis_status,
    prompt_fingerprint,
    record_observations,
    save_memory,
)
from analysis.prompt_editor import propose_prompt_revision
from analysis.prompt_rewriter import rewrite_prompt
from config import (
    DEFAULT_BASE_URL,
    DEFAULT_DATASETS_DIR,
    DEFAULT_EPOCH_PLANNER_PROMPT_PATH,
    DEFAULT_ERROR_LOCALIZATION_PROMPT_PATH,
    DEFAULT_FAILURE_ANALYSIS_PROMPT_PATH,
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_MECHANISM_TAXONOMY_PATH,
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
from reporting import (
    build_validation_impact_summary,
    refresh_run_reports,
    write_iteration_reports,
    write_validation_impact_report,
)
from utils.io import read_prompt_file, read_text, write_text
from versioning import initialize_run_prompt, make_run_dir, write_run_args


ITERATION_TEST_METRIC_KEYS = (
    "llm_node_f1",
    "llm_relation_f1",
    "node_f1",
    "relation_f1",
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
    if args.epoch_batch_concurrency < 1:
        raise ValueError("--epoch-batch-concurrency must be positive")
    if args.heldout_test_concurrency < 1:
        raise ValueError("--heldout-test-concurrency must be positive")
    if args.validation_gate_concurrency < 1:
        raise ValueError("--validation-gate-concurrency must be positive")
    if args.validation_gate_size < 0:
        raise ValueError("--validation-gate-size must be non-negative")
    if args.validation_gate_seed < 0:
        raise ValueError("--validation-gate-seed must be non-negative")
    if args.validation_repeats < 1:
        raise ValueError("--validation-repeats must be positive")
    if args.acceptance_policy == "any-improvement" and not (1 <= args.acceptance_min_wins <= args.validation_repeats):
        raise ValueError("--acceptance-min-wins must be between 1 and --validation-repeats")
    if args.validation_calibration_repeats < 2:
        raise ValueError("--validation-calibration-repeats must be at least 2")
    semantic_min_deltas = (
        args.any_improvement_node_min_delta,
        args.any_improvement_relation_min_delta,
    )
    if any(value < 0 for value in (*semantic_min_deltas, args.any_improvement_compile_min_delta)):
        raise ValueError("any-improvement minimum deltas must be non-negative")
    if args.acceptance_policy == "any-improvement" and not args.calibrate_validation_only and any(value == 0 for value in semantic_min_deltas):
        print(
            "[config] Warning: one or more semantic any-improvement min deltas are zero; "
            "calibrate and freeze non-zero Node/Relation thresholds for formal experiments.",
            flush=True,
        )
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
    if not args.llm_element_metrics and not args.no_evolve:
        raise ValueError("--no-llm-element-metrics is only supported with --no-evolve because training and validation gate use LLM judge metrics")
    if args.llm_element_metrics and not args.api_key:
        raise ValueError("LLM semantic element metrics require the main API key via ZHIPU_LLM_API_KEY or --api-key")
    if args.embedding_element_metrics and args.element_extractor == "llm" and not args.api_key:
        raise ValueError("LLM element extraction requires the main API key via ZHIPU_LLM_API_KEY or --api-key")


def make_llm_client(args: argparse.Namespace) -> LLMClient:
    return LLMClient(
        model=getattr(args, "agent_model", args.model),
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


def resolve_model_roles(args: argparse.Namespace) -> argparse.Namespace:
    """Resolve role-specific model IDs with legacy --model fallback."""
    for field in ("generation_model", "agent_model", "judge_model"):
        value = str(getattr(args, field, "") or args.model).strip()
        if not value:
            raise ValueError(f"--{field.replace('_', '-')} must resolve to a non-empty model ID")
        setattr(args, field, value)
    args.llm_judge_model = args.judge_model
    return args


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
    node_precision_delta = candidate_summary.get("llm_node_precision", 0.0) - baseline_summary.get("llm_node_precision", 0.0)
    relation_precision_delta = candidate_summary.get("llm_relation_precision", 0.0) - baseline_summary.get("llm_relation_precision", 0.0)
    node_delta = candidate_summary.get("llm_node_f1", 0.0) - baseline_summary.get("llm_node_f1", 0.0)
    relation_delta = candidate_summary.get("llm_relation_f1", 0.0) - baseline_summary.get("llm_relation_f1", 0.0)
    embedding_node_delta = candidate_summary.get("node_f1", 0.0) - baseline_summary.get("node_f1", 0.0)
    embedding_relation_delta = candidate_summary.get("relation_f1", 0.0) - baseline_summary.get("relation_f1", 0.0)
    embedding_node_precision_delta = candidate_summary.get("node_precision", 0.0) - baseline_summary.get("node_precision", 0.0)
    embedding_relation_precision_delta = candidate_summary.get("relation_precision", 0.0) - baseline_summary.get("relation_precision", 0.0)
    llm_node_delta = candidate_summary.get("llm_node_f1", 0.0) - baseline_summary.get("llm_node_f1", 0.0)
    llm_relation_delta = candidate_summary.get("llm_relation_f1", 0.0) - baseline_summary.get("llm_relation_f1", 0.0)
    llm_failed_delta = candidate_summary.get("llm_element_failed", 0.0) - baseline_summary.get("llm_element_failed", 0.0)
    infrastructure_delta = candidate_summary.get("infrastructure_error_rate", 0.0) - baseline_summary.get("infrastructure_error_rate", 0.0)
    prompt_size_ok = len(candidate_prompt) <= max_prompt_chars
    llm_metrics_available = candidate_summary.get("llm_element_evaluated", 0.0) > 0 and baseline_summary.get("llm_element_evaluated", 0.0) > 0

    safety_gate = {
        "llm_judge_metrics_available": llm_metrics_available,
        "syntax_not_significantly_worse": syntax_delta >= min_syntax_delta,
        "compile_not_significantly_worse": compile_delta >= min_compile_delta,
        "node_not_significantly_worse": node_delta >= min_node_delta,
        "relation_not_significantly_worse": relation_delta >= min_relation_delta,
        "node_precision_not_significantly_worse": node_precision_delta >= min_node_precision_delta,
        "relation_precision_not_significantly_worse": relation_precision_delta >= min_relation_precision_delta,
        "llm_judge_failures_not_increased": llm_failed_delta <= 0,
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
        "llm_judge_metrics_available": llm_metrics_available,
        "syntax_within_bootstrap_tolerance": syntax_delta >= bootstrap_min_syntax_delta,
        "compile_within_bootstrap_tolerance": compile_delta >= bootstrap_min_compile_delta,
        "node_improved": node_delta >= bootstrap_node_accept_delta,
        "relation_improved": relation_delta >= bootstrap_relation_accept_delta,
        "llm_judge_failures_not_increased": llm_failed_delta <= 0,
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
            "primary_node_precision": node_precision_delta,
            "primary_relation_precision": relation_precision_delta,
            "primary_node_f1": node_delta,
            "primary_relation_f1": relation_delta,
            "llm_node_f1": llm_node_delta,
            "llm_relation_f1": llm_relation_delta,
            "llm_element_failed": llm_failed_delta,
            "embedding_node_precision": embedding_node_precision_delta,
            "embedding_relation_precision": embedding_relation_precision_delta,
            "embedding_node_f1": embedding_node_delta,
            "embedding_relation_f1": embedding_relation_delta,
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
        "embedding_node_delta": embedding_node_delta,
        "embedding_relation_delta": embedding_relation_delta,
        "embedding_node_precision_delta": embedding_node_precision_delta,
        "embedding_relation_precision_delta": embedding_relation_precision_delta,
        "llm_node_delta": llm_node_delta,
        "llm_relation_delta": llm_relation_delta,
        "llm_failed_delta": llm_failed_delta,
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
        "primary_metric_source": "llm_judge",
        "acceptance_policy": "standard: accept when every non-regression check passes on LLM-judge node/relation metrics, LLM-judge failures do not increase, and at least one LLM-judge node/relation or compile benefit gate passes; bootstrap before first accepted update: tolerate limited syntax/compile regression only when LLM-judge node and relation F1 both improve strongly, infrastructure is not worse, and prompt size is ok",
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
        "validation_aggregate_summary": iter_dir / "validation_gate" / "aggregate_summary.json",
        "validation_analysis": iter_dir / "validation_gate" / "analysis.md",
        "validation_impact_summary": iter_dir / "validation_gate" / "impact_summary.json",
        "validation_impact_report": iter_dir / "validation_gate" / "impact_report.md",
        "analysis_records": iter_dir / "evaluation" / "analysis_records.jsonl",
        "analysis_summary": iter_dir / "evaluation" / "analysis_summary.json",
        "analysis_overview": iter_dir / "evaluation" / "analysis_overview.md",
        "failure_analysis_input": iter_dir / "agents" / "failure_analysis.input.json",
        "failure_analysis_output": iter_dir / "agents" / "failure_analysis.output.json",
        "failure_analysis_raw_output": iter_dir / "agents" / "failure_analysis.output.raw.txt",
        "failure_analysis_rejected_patterns": iter_dir / "agents" / "failure_analysis.rejected_patterns.json",
        "error_localization_input": iter_dir / "agents" / "error_localization.input.json",
        "error_localization_output": iter_dir / "agents" / "error_localization.output.json",
        "prompt_editor_input": iter_dir / "agents" / "prompt_editor.input.json",
        "prompt_editor_output": iter_dir / "agents" / "prompt_editor.output.json",
        "epoch_planner_input": iter_dir / "agents" / "epoch_planner.input.json",
        "epoch_planner_output": iter_dir / "agents" / "epoch_planner.output.json",
        "mechanism_clusters": iter_dir / "mechanisms" / "clusters.json",
        "mechanism_selected": iter_dir / "mechanisms" / "selected.json",
        "mechanism_evidence": iter_dir / "mechanisms" / "evidence.json",
        "mechanism_evidence_inventory": iter_dir / "mechanisms" / "evidence_inventory.json",
        "mechanism_lineage": iter_dir / "mechanisms" / "attribution_lineage.json",
        "prompt_gap_consensus": iter_dir / "mechanisms" / "prompt_gap_consensus.json",
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
                "aggregate_summary": rel_to_iter(iter_dir, paths["validation_aggregate_summary"]),
                "analysis": rel_to_iter(iter_dir, paths["validation_analysis"]),
                "impact_summary": rel_to_iter(iter_dir, paths["validation_impact_summary"]),
                "impact_report": rel_to_iter(iter_dir, paths["validation_impact_report"]),
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
                    "raw_output": rel_to_iter(iter_dir, paths["failure_analysis_raw_output"]),
                    "rejected_patterns": rel_to_iter(iter_dir, paths["failure_analysis_rejected_patterns"]),
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
            "mechanisms": {
                "evidence": rel_to_iter(iter_dir, paths["mechanism_evidence"]),
                "evidence_inventory": rel_to_iter(iter_dir, paths["mechanism_evidence_inventory"]),
                "clusters": rel_to_iter(iter_dir, paths["mechanism_clusters"]),
                "selected": rel_to_iter(iter_dir, paths["mechanism_selected"]),
                "attribution_lineage": rel_to_iter(iter_dir, paths["mechanism_lineage"]),
                "prompt_gap_consensus": rel_to_iter(iter_dir, paths["prompt_gap_consensus"]),
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
    refresh_reports: bool = True,
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
    if refresh_reports:
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


def case_split_fingerprint(cases: list[Case]) -> str:
    canonical = "".join(
        f"{case.dataset}\t{case.case_id}\n"
        for case in sorted(cases, key=lambda item: (item.dataset, item.case_id))
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def write_data_split_summary(
    *,
    run_dir: Path,
    args: argparse.Namespace,
    train_pool_cases: list[Case],
    train_cases: list[Case],
    validation_cases: list[Case],
    test_cases: list[Case] | None = None,
) -> dict[str, Any]:
    def counts(cases: list[Case]) -> dict[str, int]:
        return {dataset: len(items) for dataset, items in sorted(grouped_cases(cases).items())}

    summary = {
        "train_pool_count": len(train_pool_cases),
        "train_count": len(train_cases),
        "requested_validation_count": args.validation_gate_size,
        "actual_validation_count": len(validation_cases),
        "test_count": len(test_cases or []),
        "train_dataset_counts": counts(train_cases),
        "validation_dataset_counts": counts(validation_cases),
        "test_dataset_counts": counts(test_cases or []),
        "validation_split_fingerprint": case_split_fingerprint(validation_cases),
    }
    write_text(run_dir / "data_split_summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    if args.validation_gate and len(validation_cases) != args.validation_gate_size:
        print(
            f"[split] requested validation cases={args.validation_gate_size}, "
            f"actual={len(validation_cases)} after the one-third training-pool cap",
            flush=True,
        )
    return summary


def write_evaluation_records(path: Path, records: list[Any]) -> None:
    lines = [json.dumps(dataclasses.asdict(record), ensure_ascii=False) for record in records]
    write_text(path, ("\n".join(lines) + "\n") if lines else "")


def write_attribution_lineage(
    *,
    path: Path,
    selected_mechanism: dict[str, Any] | None,
    batch_edit_results: list[dict[str, Any]],
    prompt_gap_audit: dict[str, Any] | None,
    epoch_revision_plan: dict[str, Any] | None,
    prompt_rewriter_output_path: Path,
    acceptance: dict[str, Any],
) -> None:
    """Persist the Python-owned attribution lineage for offline audit."""

    selected = selected_mechanism or {}
    attribution_ids = sorted(
        set(str(value) for value in selected.get("supporting_attribution_ids", []) if str(value))
    )
    local_by_attribution: dict[str, list[dict[str, Any]]] = {
        attribution_id: [] for attribution_id in attribution_ids
    }
    for result in batch_edit_results:
        revision_input = result.get("revision_input")
        if not isinstance(revision_input, dict):
            continue
        for attribution_id in revision_input.get("supporting_attribution_ids", []):
            attribution_id = str(attribution_id)
            if attribution_id in local_by_attribution:
                local_by_attribution[attribution_id].append(
                    {
                        "batch_id": result.get("batch_id"),
                        "prompt_gap": result.get("prompt_gap"),
                        "target_section": result.get("target_section"),
                        "editor_status": result.get("editor_status"),
                        "revision_scope": revision_input.get("revision_scope"),
                    }
                )

    rule_text: str | None = None
    if prompt_rewriter_output_path.exists():
        try:
            payload = json.loads(read_text(prompt_rewriter_output_path))
        except (json.JSONDecodeError, OSError):
            payload = None
        if isinstance(payload, dict) and isinstance(payload.get("rule_text"), str):
            rule_text = payload["rule_text"]
    final_scope = epoch_revision_plan.get("revision_scope") if isinstance(epoch_revision_plan, dict) else None
    lineage = {
        "schema_version": "atomic-lineage-v1",
        "selected_mechanism": {
            "mechanism_id": selected.get("mechanism_id"),
            "hypothesis_id": selected.get("hypothesis_id"),
            "parent_key": selected.get("parent_key", []),
            "child_key": selected.get("child_key", []),
            "mechanism_signature": selected.get("mechanism_signature"),
            "conflict_status": selected.get("conflict_status", "clear"),
            "supporting_attribution_ids": attribution_ids,
            "supporting_evidence_ids": sorted(
                set(str(value) for value in selected.get("supporting_evidence_ids", []) if str(value))
            ),
        },
        "attributions": [
            {
                "attribution_id": attribution_id,
                "cluster_mechanism_id": selected.get("mechanism_id"),
                "hypothesis_id": selected.get("hypothesis_id"),
                "parent_key": selected.get("parent_key", []),
                "child_key": selected.get("child_key", []),
                "evidence_id": next(
                    (
                        str(item.get("evidence_id") or "")
                        for item in selected.get("supporting_attributions", [])
                        if isinstance(item, dict)
                        and str(item.get("attribution_id") or "") == attribution_id
                    ),
                    None,
                ),
                "anchor_kind": next(
                    (
                        str(item.get("anchor_kind") or "")
                        for item in selected.get("supporting_attributions", [])
                        if isinstance(item, dict)
                        and str(item.get("attribution_id") or "") == attribution_id
                    ),
                    None,
                ),
                "local_plans": local_by_attribution[attribution_id],
                "final_revision_scope": final_scope,
                "final_fragment": {
                    "present": rule_text is not None,
                    "rule_text": rule_text,
                },
                "acceptance": {
                    "accepted": bool(acceptance.get("accepted")),
                    "rejection_reasons": acceptance.get("rejection_reasons", []),
                },
            }
            for attribution_id in attribution_ids
        ],
        "prompt_gap_consensus": prompt_gap_audit,
        "epoch_revision_scope": final_scope,
    }
    write_text(path, json.dumps(lineage, ensure_ascii=False, indent=2))


def make_edit_budget(*, has_accepted_update: bool, args: argparse.Namespace, agent: str) -> dict[str, Any]:
    if agent == "epoch_planner":
        max_revision_items = 1
        guidance = [
            "Merge only the plans for Python's selected mechanism into one section revision.",
            "Prefer modifying or tightening existing guidance over adding independent new rules.",
        ]
    else:
        guidance = [
            "Revise only the Python-selected mechanism and its single highest-impact section.",
            "Prefer modifying or tightening existing guidance over adding independent new rules.",
        ]
        return {
            "guidance": guidance,
        }
    return {
        "max_revision_items": max_revision_items,
        "guidance": guidance,
    }


@dataclasses.dataclass
class EpochBatchResult:
    batch_index: int
    global_update_step: int
    records: list[Any]
    summary: dict[str, float]
    batch_summary: dict[str, Any]
    failure_analysis: dict[str, Any] | None = None
    mechanism_observations: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    valid_pattern_count: int = 0
    rejected_pattern_count: int = 0
    skipped_count: int = 0


def process_epoch_batch(
    *,
    args: argparse.Namespace,
    llm_client: LLMClient,
    run_dir: Path,
    iter_dir: Path,
    iteration: int,
    batch_index: int,
    batch_count: int,
    global_update_step: int,
    prompt: str,
    analysis_cases: list[Case],
    has_accepted_update: bool,
) -> EpochBatchResult:
    batch_dir = iter_dir / "train_batches" / f"batch_{batch_index:03d}"
    paths = iteration_paths(batch_dir)
    manifest = make_iteration_manifest(batch_dir, global_update_step, paths)
    manifest["epoch_iteration"] = iteration
    manifest["batch_index"] = batch_index
    manifest["global_update_step"] = global_update_step
    prompt_before = prompt
    phase_prefix = f"iteration_{iteration:03d}:batch_{batch_index:03d}"
    log_prefix = f"[iteration {iteration} batch {batch_index}/{batch_count}]"

    def skipped_result(
        records: list[Any],
        summary: dict[str, float],
        *,
        rejected_pattern_count: int = 0,
    ) -> EpochBatchResult:
        return EpochBatchResult(
            batch_index=batch_index,
            global_update_step=global_update_step,
            records=records,
            summary=summary,
            batch_summary={
                "batch_index": batch_index,
                "global_update_step": global_update_step,
                "case_count": len(analysis_cases),
                "summary": summary,
            },
            rejected_pattern_count=rejected_pattern_count,
            skipped_count=1,
        )

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
            refresh_reports=False,
        )
        print(f"{log_prefix} prompt unchanged")
        return skipped_result(records, summary)

    if has_only_infrastructure_errors(records):
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
            refresh_reports=False,
        )
        print(f"{log_prefix} infrastructure-only failures; prompt unchanged")
        return skipped_result(records, summary)

    failure_result = analyze_failures(
        current_prompt=prompt,
        records=records,
        summary=summary,
        args=args,
        llm_client=llm_client,
        output_input_path=paths["failure_analysis_input"],
        output_path=paths["failure_analysis_output"],
        raw_output_path=paths["failure_analysis_raw_output"],
        rejected_patterns_path=paths["failure_analysis_rejected_patterns"],
        state_dir=run_dir,
        iteration=iteration,
        batch_id=batch_index,
        generation_run=run_dir.name,
    )
    failure_analysis = failure_result.normalized_payload
    if failure_analysis is None:
        write_text(paths["prompt_after"], prompt)
        record_stage(
            manifest,
            "failure_analysis",
            status="invalid",
            inputs={"records": rel_to_iter(batch_dir, paths["analysis_records"])},
            outputs={
                "input": rel_to_iter(batch_dir, paths["failure_analysis_input"]),
                "output": rel_to_iter(batch_dir, paths["failure_analysis_output"]),
                "raw_output": rel_to_iter(batch_dir, paths["failure_analysis_raw_output"]),
                "rejected_patterns": rel_to_iter(batch_dir, paths["failure_analysis_rejected_patterns"]),
                "prompt_after": rel_to_iter(batch_dir, paths["prompt_after"]),
            },
            note="; ".join(failure_result.fatal_errors),
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
            refresh_reports=False,
        )
        print(f"{log_prefix} failure analysis invalid; prompt unchanged")
        return skipped_result(
            records,
            summary,
            rejected_pattern_count=len(failure_result.rejected_patterns),
        )
    record_stage(
        manifest,
        "failure_analysis",
        status="success",
        inputs={"records": rel_to_iter(batch_dir, paths["analysis_records"])},
        outputs={
            "input": rel_to_iter(batch_dir, paths["failure_analysis_input"]),
            "output": rel_to_iter(batch_dir, paths["failure_analysis_output"]),
            "raw_output": rel_to_iter(batch_dir, paths["failure_analysis_raw_output"]),
            "rejected_patterns": rel_to_iter(batch_dir, paths["failure_analysis_rejected_patterns"]),
        },
        note=(
            f"valid_attributions={failure_analysis_item_count(failure_analysis)}, "
            f"rejected_patterns={len(failure_result.rejected_patterns)}"
        ),
    )
    write_iteration_manifest(batch_dir, manifest)

    taxonomy = load_mechanism_taxonomy(args.mechanism_taxonomy_path)
    observations = build_mechanism_observations(
        failure_analysis,
        taxonomy,
        batch_id=batch_index,
        analysis_summary=summary,
    )
    evidence_for_log = [
        {key: value for key, value in observation.items() if key != "patterns"}
        for observation in observations
    ]
    write_text(paths["mechanism_evidence"], json.dumps(evidence_for_log, ensure_ascii=False, indent=2))
    classification_counts = {
        classification: sum(1 for item in observations if item["classification"] == classification)
        for classification in ("candidate", "dataset_convention", "record_only")
    }
    candidate_count = classification_counts["candidate"]
    record_stage(
        manifest,
        "mechanism_filter",
        status="success" if candidate_count else "skipped",
        inputs={"failure_analysis": rel_to_iter(batch_dir, paths["failure_analysis_output"])},
        outputs={"evidence": rel_to_iter(batch_dir, paths["mechanism_evidence"])},
        note=(
            f"candidate={classification_counts['candidate']}, "
            f"dataset_convention={classification_counts['dataset_convention']}, "
            f"record_only={classification_counts['record_only']}"
        ),
    )
    write_text(paths["prompt_after"], prompt)
    write_iteration_manifest(batch_dir, manifest)
    finalize_iteration_reports(
        run_dir=run_dir,
        iter_dir=batch_dir,
        iteration=global_update_step,
        prompt_before=prompt_before,
        prompt_after=prompt,
        candidate_prompt=None,
        analysis_summary=summary,
        refresh_reports=False,
    )
    print(f"{log_prefix} collected {candidate_count} candidate mechanism observation(s)")
    return EpochBatchResult(
        batch_index=batch_index,
        global_update_step=global_update_step,
        records=records,
        summary=summary,
        batch_summary={
            "batch_index": batch_index,
            "global_update_step": global_update_step,
            "case_count": len(analysis_cases),
            "summary": summary,
        },
        failure_analysis=failure_analysis,
        mechanism_observations=observations,
        valid_pattern_count=failure_analysis_item_count(failure_analysis),
        rejected_pattern_count=len(failure_result.rejected_patterns),
        skipped_count=0 if candidate_count else 1,
    )


def record_unselected_batch(
    *, iter_dir: Path, batch_index: int, selected_mechanism_id: str
) -> None:
    batch_dir = iter_dir / "train_batches" / f"batch_{batch_index:03d}"
    manifest = json.loads(read_text(batch_dir / "manifest.json"))
    record_stage(
        manifest,
        "selected_mechanism_editing",
        status="skipped",
        note=f"not_selected_by_epoch_cluster:{selected_mechanism_id}",
    )
    write_iteration_manifest(batch_dir, manifest)


def create_selected_batch_revision(
    *,
    args: argparse.Namespace,
    llm_client: LLMClient,
    run_dir: Path,
    iter_dir: Path,
    prompt: str,
    selected_observation: dict[str, Any],
    has_accepted_update: bool,
    iteration: int,
) -> dict[str, Any]:
    batch_index = int(selected_observation["batch_id"])
    batch_dir = iter_dir / "train_batches" / f"batch_{batch_index:03d}"
    paths = iteration_paths(batch_dir)
    manifest = json.loads(read_text(batch_dir / "manifest.json"))
    supporting_ids = sorted(set(selected_observation["supporting_evidence_ids"]))
    filtered_failure_analysis = sanitize_selected_failure_analysis(selected_observation)
    if failure_analysis_item_count(filtered_failure_analysis) == 0:
        record_stage(
            manifest,
            "selected_mechanism_editing",
            status="invalid",
            note="selected_evidence_empty_after_sanitization",
        )
        write_iteration_manifest(batch_dir, manifest)
        return {
            "batch_id": batch_index,
            "prompt_gap": "invalid",
            "target_section": None,
            "localization_status": "not_run",
            "editor_status": "not_run",
            "revision_input": None,
        }

    error_localization = localize_errors(
        current_prompt=prompt,
        failure_analysis=filtered_failure_analysis,
        selected_mechanism=selected_observation,
        args=args,
        llm_client=llm_client,
        output_input_path=paths["error_localization_input"],
        output_path=paths["error_localization_output"],
        state_dir=run_dir,
        iteration=iteration,
    )
    if error_localization is None:
        record_stage(
            manifest,
            "selected_mechanism_editing",
            status="invalid",
            outputs={"error_localization": rel_to_iter(batch_dir, paths["error_localization_output"])},
            note="error_localization_invalid",
        )
        write_iteration_manifest(batch_dir, manifest)
        return {
            "batch_id": batch_index,
            "prompt_gap": "invalid",
            "target_section": None,
            "localization_status": "invalid",
            "editor_status": "not_run",
            "revision_input": None,
        }

    prompt_gap = str(error_localization["prompt_gap"])
    diagnoses = error_localization["section_diagnoses"]
    target_section = (
        str(diagnoses[0]["section"]).strip().lower()
        if diagnoses
        else None
    )
    repair_type = (
        str(diagnoses[0].get("repair_type") or "")
        if diagnoses and isinstance(diagnoses[0], dict)
        else ""
    )
    revision_scope = (
        make_revision_scope(
            selected_mechanism=selected_observation,
            prompt_gap=prompt_gap,
            section=target_section or "",
            repair_type=repair_type,
            existing_prompt_quote=str(
                error_localization.get("existing_prompt_quote") or ""
            ),
        )
        if prompt_gap in {"missing", "ambiguous"}
        else None
    )
    if prompt_gap == "already_covered":
        record_stage(
            manifest,
            "selected_mechanism_editing",
            status="skipped",
            outputs={"error_localization": rel_to_iter(batch_dir, paths["error_localization_output"])},
            note="prompt_gap_already_covered",
        )
        write_iteration_manifest(batch_dir, manifest)
        return {
            "batch_id": batch_index,
            "prompt_gap": prompt_gap,
            "target_section": None,
            "localization_status": "success",
            "editor_status": "skipped",
            "revision_input": None,
            "revision_scope": None,
        }

    editor_edit_budget = make_edit_budget(
        has_accepted_update=has_accepted_update,
        args=args,
        agent="prompt_editor",
    )
    revision_plan = propose_prompt_revision(
        current_prompt=prompt,
        failure_analysis=filtered_failure_analysis,
        error_localization=error_localization,
        selected_mechanism=selected_observation,
        edit_budget=editor_edit_budget,
        args=args,
        llm_client=llm_client,
        output_input_path=paths["prompt_editor_input"],
        output_path=paths["prompt_editor_output"],
        state_dir=run_dir,
        iteration=iteration,
    )
    if revision_plan is None:
        record_stage(
            manifest,
            "selected_mechanism_editing",
            status="invalid",
            outputs={
                "error_localization": rel_to_iter(batch_dir, paths["error_localization_output"]),
                "prompt_editor": rel_to_iter(batch_dir, paths["prompt_editor_output"]),
            },
            note="prompt_editor_invalid",
        )
        write_iteration_manifest(batch_dir, manifest)
        return {
            "batch_id": batch_index,
            "prompt_gap": prompt_gap,
            "target_section": target_section,
            "localization_status": "success",
            "editor_status": "invalid",
            "revision_input": None,
            "revision_scope": revision_scope,
        }

    record_stage(
        manifest,
        "selected_mechanism_editing",
        status="success",
        outputs={
            "error_localization": rel_to_iter(batch_dir, paths["error_localization_output"]),
            "prompt_editor": rel_to_iter(batch_dir, paths["prompt_editor_output"]),
        },
        note=f"selected_mechanism={selected_observation['mechanism_id']}",
    )
    write_iteration_manifest(batch_dir, manifest)
    revision_input = {
        "batch_id": batch_index,
        "mechanism_id": selected_observation["mechanism_id"],
        "selected_mechanism_signature": selected_observation["mechanism_signature"],
        "supporting_evidence_ids": supporting_ids,
        "supporting_attribution_ids": sorted(
            set(selected_observation.get("supporting_attribution_ids", []))
        ),
        "supporting_evidence": selected_observation.get("supporting_evidence", []),
        "analysis_summary": selected_observation.get("analysis_summary", {}),
        "failure_analysis": filtered_failure_analysis,
        "error_localization": error_localization,
        "revision_plan": revision_plan["revision_plan"],
        "revision_scope": revision_scope,
    }
    return {
        "batch_id": batch_index,
        "prompt_gap": prompt_gap,
        "target_section": target_section,
        "localization_status": "success",
        "editor_status": "success",
        "revision_input": revision_input,
        "revision_scope": revision_scope,
    }


def collect_selected_batch_revisions(
    *,
    args: argparse.Namespace,
    llm_client: LLMClient,
    run_dir: Path,
    iter_dir: Path,
    prompt: str,
    batch_results: list[EpochBatchResult],
    selected_mechanism: dict[str, Any],
    has_accepted_update: bool,
    iteration: int,
) -> list[dict[str, Any]]:
    selected_observations = selected_mechanism["supporting_batch_observations"]
    selected_batch_ids = {int(item["batch_id"]) for item in selected_observations}
    shared_attributions = [
        dict(item)
        for item in selected_mechanism.get("supporting_attributions", [])
        if isinstance(item, dict)
    ]
    shared_evidence = [
        dict(item)
        for item in selected_mechanism.get("supporting_evidence", [])
        if isinstance(item, dict)
    ]
    shared_attribution_ids = sorted(
        set(str(item) for item in selected_mechanism.get("supporting_attribution_ids", []) if str(item))
    )
    shared_evidence_ids = sorted(
        set(str(item) for item in selected_mechanism.get("supporting_evidence_ids", []) if str(item))
    )
    for result in batch_results:
        if result.batch_index not in selected_batch_ids:
            record_unselected_batch(
                iter_dir=iter_dir,
                batch_index=result.batch_index,
                selected_mechanism_id=selected_mechanism["mechanism_id"],
            )

    def create(observation: dict[str, Any]) -> dict[str, Any]:
        scoped_observation = dict(observation)
        scoped_observation["attributions"] = shared_attributions
        scoped_observation["supporting_attribution_ids"] = shared_attribution_ids
        scoped_observation["supporting_evidence_ids"] = shared_evidence_ids
        scoped_observation["supporting_evidence"] = shared_evidence
        scoped_observation["evidence_catalog"] = shared_evidence
        scoped_observation["hypothesis_id"] = selected_mechanism.get("hypothesis_id")
        scoped_observation["parent_key"] = selected_mechanism.get("parent_key", [])
        scoped_observation["child_key"] = selected_mechanism.get("child_key", [])
        result = create_selected_batch_revision(
            args=args,
            llm_client=llm_client,
            run_dir=run_dir,
            iter_dir=iter_dir,
            prompt=prompt,
            selected_observation=scoped_observation,
            has_accepted_update=has_accepted_update,
            iteration=iteration,
        )
        if result is not None:
            return result
        return {
            "batch_id": int(observation["batch_id"]),
            "prompt_gap": "invalid",
            "target_section": None,
            "localization_status": "invalid",
            "editor_status": "not_run",
            "revision_input": None,
        }

    results: list[dict[str, Any]] = []
    concurrency = min(args.epoch_batch_concurrency, len(selected_observations))
    if concurrency <= 1:
        results = [create(item) for item in selected_observations]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(create, item) for item in selected_observations]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
    return sorted(results, key=lambda item: int(item["batch_id"]))


def build_prompt_gap_consensus(
    *,
    selected_mechanism: dict[str, Any],
    batch_edit_results: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any], str | None]:
    supporting_batch_count = int(selected_mechanism["supporting_batch_count"])
    required_votes = supporting_batch_count // 2 + 1
    by_batch = {
        int(item["batch_id"]): item
        for item in batch_edit_results
    }
    expected_batches = sorted(int(item) for item in selected_mechanism["supporting_batches"])
    normalized_results = [
        by_batch.get(
            batch_id,
            {
                "batch_id": batch_id,
                "prompt_gap": "invalid",
                "target_section": None,
                "localization_status": "missing",
                "editor_status": "not_run",
                "revision_input": None,
            },
        )
        for batch_id in expected_batches
    ]

    def item_scope(item: dict[str, Any]) -> dict[str, Any] | None:
        scope = item.get("revision_scope")
        if isinstance(scope, dict):
            return scope
        section = item.get("target_section")
        if section not in SECTION_NAMES or item.get("prompt_gap") not in {"missing", "ambiguous"}:
            return None
        return make_revision_scope(
            selected_mechanism=selected_mechanism,
            prompt_gap=str(item.get("prompt_gap") or ""),
            section=str(section),
            repair_type=str(item.get("repair_type") or ""),
            existing_prompt_quote=str(item.get("existing_prompt_quote") or ""),
        )

    localization_votes: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    plan_votes: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for item in normalized_results:
        scope = item_scope(item)
        if (
            item.get("localization_status") == "success"
            and item.get("prompt_gap") in {"missing", "ambiguous"}
            and scope is not None
        ):
            localization_votes.setdefault(revision_scope_key(scope), []).append(item)
        if (
            item.get("editor_status") == "success"
            and isinstance(item.get("revision_input"), dict)
            and scope is not None
        ):
            plan_scope = item["revision_input"].get("revision_scope")
            if not isinstance(plan_scope, dict):
                plan_scope = scope
            if isinstance(plan_scope, dict) and revision_scope_key(plan_scope) == revision_scope_key(scope):
                plan_votes.setdefault(revision_scope_key(scope), []).append(item)

    consensus_keys = sorted(
        (
            key
            for key, items in localization_votes.items()
            if len(items) >= required_votes
        ),
        key=lambda key: (-len(localization_votes[key]), key),
    )
    consensus_key = consensus_keys[0] if consensus_keys else None
    consensus_scope = (
        item_scope(localization_votes[consensus_key][0])
        if consensus_key is not None
        else None
    )
    localization_consensus_section = (
        str(consensus_scope.get("section") or "") if consensus_scope else None
    )
    actionable_items = (
        plan_votes.get(consensus_key, [])
        if consensus_key is not None
        else []
    )

    all_already_covered = bool(normalized_results) and all(
        item.get("localization_status") == "success"
        and item.get("prompt_gap") == "already_covered"
        for item in normalized_results
    )
    if all_already_covered:
        decision = "already_covered"
        rejection_reason = "selected_mechanism_already_covered"
        actionable_section = None
        revisions: list[dict[str, Any]] = []
    elif consensus_key is None:
        decision = "insufficient_consensus"
        rejection_reason = "insufficient_prompt_gap_consensus"
        actionable_section = None
        revisions = []
    elif len(actionable_items) < required_votes:
        decision = "insufficient_consensus"
        rejection_reason = "no_valid_selected_mechanism_plans"
        actionable_section = None
        revisions = []
    else:
        decision = "proceed"
        rejection_reason = None
        actionable_section = localization_consensus_section
        revisions = sorted(
            (item["revision_input"] for item in actionable_items),
            key=lambda item: int(item["batch_id"]),
        )

    audit_results = []
    for item in normalized_results:
        valid_plan_vote = (
            item.get("editor_status") == "success"
            and isinstance(item.get("revision_input"), dict)
            and consensus_key is not None
            and item_scope(item) is not None
            and revision_scope_key(item_scope(item) or {}) == consensus_key
        )
        audit_results.append(
            {
                "batch_id": int(item["batch_id"]),
                "prompt_gap": item.get("prompt_gap"),
                "target_section": item.get("target_section"),
                "localization_status": item.get("localization_status"),
                "editor_status": item.get("editor_status"),
                "counted_vote": valid_plan_vote,
                "revision_scope": item_scope(item),
            }
        )
    audit = {
        "selected_mechanism_id": selected_mechanism["mechanism_id"],
        "selected_mechanism_signature": selected_mechanism.get("mechanism_signature", {}),
        "supporting_batch_count": supporting_batch_count,
        "required_votes": required_votes,
        "batch_results": audit_results,
        "localization_consensus_section": localization_consensus_section,
        "consensus_scope": consensus_scope,
        "localization_vote_count": (
            len(localization_votes.get(consensus_key, []))
            if consensus_key is not None
            else 0
        ),
        "actionable_section": actionable_section,
        "actionable_plan_count": len(actionable_items),
        "decision": decision,
        "rejection_reason": rejection_reason,
    }
    return revisions, audit, rejection_reason


SEMANTIC_ACCEPTANCE_METRICS = (
    "llm_node_f1",
    "llm_relation_f1",
)

VALIDATION_CALIBRATION_METRICS = (
    *SEMANTIC_ACCEPTANCE_METRICS,
    "plantuml_compilation_pass_rate",
)


def aggregate_repeat_summaries(summaries: list[dict[str, float]]) -> dict[str, float]:
    if not summaries:
        return {}
    keys = sorted(set().union(*(summary.keys() for summary in summaries)))
    return {
        key: statistics.fmean(float(summary.get(key, 0.0)) for summary in summaries)
        for key in keys
    }


def any_improvement_decision(
    *,
    baseline_summaries: list[dict[str, float]],
    candidate_summaries: list[dict[str, float]],
    validation_case_count: int,
    candidate_prompt: str,
    baseline_prompt: str,
    max_prompt_chars: int,
    min_wins: int,
    min_deltas: dict[str, float],
) -> tuple[bool, dict[str, Any]]:
    repeat_count = len(baseline_summaries)
    invalid_reasons: list[str] = []
    if repeat_count == 0 or repeat_count != len(candidate_summaries):
        invalid_reasons.append("repeat_count_mismatch")
    prompt_size_ok = len(candidate_prompt) <= max_prompt_chars
    if not prompt_size_ok:
        invalid_reasons.append("prompt_too_long")
    if any(
        float(summary.get("infrastructure_error_rate", 0.0)) > 0
        for summary in [*baseline_summaries, *candidate_summaries]
    ):
        invalid_reasons.append("infrastructure_error")

    metric_results: dict[str, dict[str, Any]] = {}
    for metric in SEMANTIC_ACCEPTANCE_METRICS:
        available = all(
            int(float(summary.get("llm_element_evaluated", -1))) == validation_case_count
            and int(float(summary.get("llm_element_failed", -1))) == 0
            for summary in [*baseline_summaries, *candidate_summaries]
        )
        deltas = [
            float(candidate.get(metric, 0.0)) - float(baseline.get(metric, 0.0))
            for baseline, candidate in zip(baseline_summaries, candidate_summaries)
        ]
        mean_delta = statistics.fmean(deltas) if deltas else 0.0
        median_delta = statistics.median(deltas) if deltas else 0.0
        wins = sum(1 for delta in deltas if delta > 0.0)
        min_delta = float(min_deltas.get(metric, 0.0))
        stable = available and mean_delta > min_delta and wins >= min_wins
        metric_results[metric] = {
            "available": available,
            "repeat_deltas": deltas,
            "mean_delta": mean_delta,
            "median_delta": median_delta,
            "wins": wins,
            "repeat_count": repeat_count,
            "min_wins": min_wins,
            "min_delta": min_delta,
            "stable_improvement": stable,
        }

    if not any(result["available"] for result in metric_results.values()):
        invalid_reasons.append("no_complete_acceptance_metric")
    winning_metrics = [
        metric
        for metric, result in metric_results.items()
        if result["stable_improvement"]
    ]
    evaluation_valid = not invalid_reasons
    accepted = evaluation_valid and bool(winning_metrics)

    diagnostic_metrics = (
        "plantuml_compilation_pass_rate",
        "syntax_pass_rate",
        "llm_node_precision",
        "llm_node_recall",
        "llm_relation_precision",
        "llm_relation_recall",
        "llm_element_failed",
        "infrastructure_error_rate",
    )
    diagnostic_deltas = {
        metric: [
            float(candidate.get(metric, 0.0)) - float(baseline.get(metric, 0.0))
            for baseline, candidate in zip(baseline_summaries, candidate_summaries)
        ]
        for metric in diagnostic_metrics
    }
    rejection_reasons = invalid_reasons if invalid_reasons else ([] if accepted else ["no_stable_improvement"])
    return accepted, {
        "accepted": accepted,
        "acceptance_mode": "any_improvement" if accepted else "rejected",
        "acceptance_policy": "any-improvement",
        "evaluation_valid": evaluation_valid,
        "invalid_reasons": invalid_reasons,
        "rejection_reasons": rejection_reasons,
        "winning_metrics": winning_metrics,
        "metric_results": metric_results,
        "diagnostic_repeat_deltas": diagnostic_deltas,
        "validation_repeats": repeat_count,
        "validation_case_count": validation_case_count,
        "prompt_growth": {
            "baseline_chars": len(baseline_prompt),
            "candidate_chars": len(candidate_prompt),
            "max_prompt_chars": max_prompt_chars,
            "prompt_size_ok": prompt_size_ok,
        },
        "baseline_summary": aggregate_repeat_summaries(baseline_summaries),
        "candidate_summary": aggregate_repeat_summaries(candidate_summaries),
        "baseline_repeat_summaries": baseline_summaries,
        "candidate_repeat_summaries": candidate_summaries,
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
        case_concurrency=args.heldout_test_concurrency,
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
    if args.acceptance_policy == "legacy":
        baseline_records, baseline_summary = evaluate_cases(
            prompt=baseline_prompt,
            cases=validation_cases,
            args=args,
            llm_client=llm_client,
            output_path=paths["validation_baseline_records"],
            state_dir=run_dir,
            phase=f"{phase_prefix}:validation_baseline",
            case_concurrency=args.validation_gate_concurrency,
        )
        candidate_records, candidate_summary = evaluate_cases(
            prompt=candidate_prompt,
            cases=validation_cases,
            args=args,
            llm_client=llm_client,
            output_path=paths["validation_candidate_records"],
            state_dir=run_dir,
            phase=f"{phase_prefix}:validation_candidate",
            case_concurrency=args.validation_gate_concurrency,
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
        impact_summary = build_validation_impact_summary(
            [(1, baseline_records, candidate_records)]
        )
        write_validation_impact_report(
            summary=impact_summary,
            json_path=paths["validation_impact_summary"],
            report_path=paths["validation_impact_report"],
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
        decision["validation_split_fingerprint"] = case_split_fingerprint(validation_cases)
        return baseline_records, candidate_records, baseline_summary, candidate_summary, decision

    baseline_repeat_summaries: list[dict[str, float]] = []
    candidate_repeat_summaries: list[dict[str, float]] = []
    first_baseline_records: list[Any] = []
    first_candidate_records: list[Any] = []
    repeat_pairs: list[tuple[int, list[Any], list[Any]]] = []

    def evaluate_repeat(prompt: str, *, repeat: int, role: str) -> tuple[list[Any], dict[str, float]]:
        role_dir = iter_dir / "validation_gate" / f"repeat_{repeat:03d}" / role
        records, summary = evaluate_cases(
            prompt=prompt,
            cases=validation_cases,
            args=args,
            llm_client=llm_client,
            output_path=role_dir / "records.jsonl",
            state_dir=run_dir,
            phase=f"{phase_prefix}:validation_repeat_{repeat:03d}:{role}",
            case_concurrency=args.validation_gate_concurrency,
        )
        write_text(role_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
        return records, summary

    for repeat in range(1, args.validation_repeats + 1):
        if repeat % 2 == 1:
            baseline_records, baseline_summary = evaluate_repeat(baseline_prompt, repeat=repeat, role="baseline")
            candidate_records, candidate_summary = evaluate_repeat(candidate_prompt, repeat=repeat, role="candidate")
        else:
            candidate_records, candidate_summary = evaluate_repeat(candidate_prompt, repeat=repeat, role="candidate")
            baseline_records, baseline_summary = evaluate_repeat(baseline_prompt, repeat=repeat, role="baseline")
        if repeat == 1:
            first_baseline_records = baseline_records
            first_candidate_records = candidate_records
        repeat_pairs.append((repeat, baseline_records, candidate_records))
        baseline_repeat_summaries.append(baseline_summary)
        candidate_repeat_summaries.append(candidate_summary)

    baseline_summary = aggregate_repeat_summaries(baseline_repeat_summaries)
    candidate_summary = aggregate_repeat_summaries(candidate_repeat_summaries)
    write_text(paths["validation_baseline_summary"], json.dumps(baseline_summary, ensure_ascii=False, indent=2))
    write_text(paths["validation_candidate_summary"], json.dumps(candidate_summary, ensure_ascii=False, indent=2))
    write_evaluation_records(paths["validation_baseline_records"], first_baseline_records)
    write_evaluation_records(paths["validation_candidate_records"], first_candidate_records)
    accepted, decision = any_improvement_decision(
        baseline_summaries=baseline_repeat_summaries,
        candidate_summaries=candidate_repeat_summaries,
        validation_case_count=len(validation_cases),
        candidate_prompt=candidate_prompt,
        baseline_prompt=baseline_prompt,
        max_prompt_chars=args.max_prompt_chars,
        min_wins=args.acceptance_min_wins,
        min_deltas={
            "llm_node_f1": args.any_improvement_node_min_delta,
            "llm_relation_f1": args.any_improvement_relation_min_delta,
        },
    )
    aggregate_payload = {
        "baseline_summary": baseline_summary,
        "candidate_summary": candidate_summary,
        "baseline_repeat_summaries": baseline_repeat_summaries,
        "candidate_repeat_summaries": candidate_repeat_summaries,
        "metric_results": decision["metric_results"],
        "diagnostic_repeat_deltas": decision["diagnostic_repeat_deltas"],
        "winning_metrics": decision["winning_metrics"],
        "validation_case_count": len(validation_cases),
        "validation_split_fingerprint": case_split_fingerprint(validation_cases),
    }
    write_text(paths["validation_aggregate_summary"], json.dumps(aggregate_payload, ensure_ascii=False, indent=2))
    write_text(
        paths["validation_analysis"],
        "# Repeated Validation Gate\n\n"
        f"- repeats: {args.validation_repeats}\n"
        f"- winning metrics: {', '.join(decision['winning_metrics']) or 'none'}\n"
        f"- accepted: {str(accepted).lower()}\n\n"
        "See `aggregate_summary.json` for paired repeat deltas and diagnostic metrics.\n",
    )
    impact_summary = build_validation_impact_summary(repeat_pairs)
    write_validation_impact_report(
        summary=impact_summary,
        json_path=paths["validation_impact_summary"],
        report_path=paths["validation_impact_report"],
    )
    decision["accepted"] = accepted
    decision["evaluation_source"] = "validation_gate"
    decision["validation_case_count"] = len(validation_cases)
    decision["validation_split_fingerprint"] = case_split_fingerprint(validation_cases)
    return first_baseline_records, first_candidate_records, baseline_summary, candidate_summary, decision


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
    taxonomy = load_mechanism_taxonomy(args.mechanism_taxonomy_path)
    taxonomy_version = str(taxonomy["version"])
    taxonomy_policy_revision = str(taxonomy.get("policy_revision") or "legacy")
    mechanism_memory_path = run_dir / "mechanism_memory.json"
    mechanism_memory = load_memory(mechanism_memory_path)

    for iteration in range(1, args.iterations + 1):
        iter_dir = run_dir / f"iteration_{iteration:03d}"
        epoch_paths = iteration_paths(iter_dir)
        epoch_manifest = make_iteration_manifest(iter_dir, iteration, epoch_paths)
        epoch_manifest["mode"] = "epoch_planner_updates"
        epoch_manifest["mechanism_memory"] = "../mechanism_memory.json"
        epoch_manifest["validation_split"] = {
            "requested_case_count": args.validation_gate_size,
            "actual_case_count": len(validation_cases),
            "fingerprint": case_split_fingerprint(validation_cases),
        }
        epoch_prompt_before = prompt
        epoch_prompt_hash = prompt_fingerprint(prompt)
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
        epoch_valid_pattern_count = 0
        epoch_rejected_pattern_count = 0
        epoch_records = []
        batch_summaries: list[dict[str, Any]] = []
        mechanism_observations: list[dict[str, Any]] = []
        print(f"\n[iteration {iteration}] training epoch with {len(training_batches)} batch(es)")

        step_base = global_update_step
        batch_jobs = [
            {
                "batch_index": batch_index,
                "analysis_cases": analysis_cases,
                "global_update_step": step_base + batch_index,
            }
            for batch_index, analysis_cases in enumerate(training_batches, start=1)
        ]
        batch_results: list[EpochBatchResult] = []
        batch_concurrency = min(args.epoch_batch_concurrency, len(batch_jobs)) if batch_jobs else 1
        epoch_manifest["epoch_batch_concurrency"] = batch_concurrency

        if batch_concurrency <= 1:
            for job in batch_jobs:
                batch_results.append(
                    process_epoch_batch(
                        args=args,
                        llm_client=llm_client,
                        run_dir=run_dir,
                        iter_dir=iter_dir,
                        iteration=iteration,
                        batch_index=job["batch_index"],
                        batch_count=len(training_batches),
                        global_update_step=job["global_update_step"],
                        prompt=prompt,
                        analysis_cases=job["analysis_cases"],
                        has_accepted_update=has_accepted_update,
                    )
                )
        else:
            print(f"[iteration {iteration}] running {len(training_batches)} training batch(es) with concurrency={batch_concurrency}")
            with concurrent.futures.ThreadPoolExecutor(max_workers=batch_concurrency) as executor:
                futures = [
                    executor.submit(
                        process_epoch_batch,
                        args=args,
                        llm_client=llm_client,
                        run_dir=run_dir,
                        iter_dir=iter_dir,
                        iteration=iteration,
                        batch_index=job["batch_index"],
                        batch_count=len(training_batches),
                        global_update_step=job["global_update_step"],
                        prompt=prompt,
                        analysis_cases=job["analysis_cases"],
                        has_accepted_update=has_accepted_update,
                    )
                    for job in batch_jobs
                ]
                for future in concurrent.futures.as_completed(futures):
                    batch_results.append(future.result())

        global_update_step += len(training_batches)
        batch_results.sort(key=lambda result: result.batch_index)
        for result in batch_results:
            last_summary = result.summary
            epoch_records.extend(result.records)
            batch_summaries.append(result.batch_summary)
            epoch_skipped_count += result.skipped_count
            epoch_valid_pattern_count += result.valid_pattern_count
            epoch_rejected_pattern_count += result.rejected_pattern_count
            mechanism_observations.extend(result.mechanism_observations)

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
            "valid_pattern_count": epoch_valid_pattern_count,
            "rejected_pattern_count": epoch_rejected_pattern_count,
            "mechanism_taxonomy_version": taxonomy_version,
            "mechanism_taxonomy_policy_revision": taxonomy_policy_revision,
            "mechanism_memory": "../mechanism_memory.json",
        }

        selected_mechanism = None
        selected_hypothesis_status: str | None = None
        selected_hypothesis_reasons: list[str] = []
        mechanism_report = {"eligible_candidates": [], "rejected_clusters": [], "selected_mechanism_id": None}
        batch_edit_results: list[dict[str, Any]] = []
        epoch_revision_plan: dict[str, Any] | None = None
        inventory_for_log = [
            {key: value for key, value in observation.items() if key != "patterns"}
            for observation in mechanism_observations
        ]
        write_text(
            epoch_paths["mechanism_evidence_inventory"],
            json.dumps(inventory_for_log, ensure_ascii=False, indent=2),
        )
        candidate_observation_count = sum(
            1 for observation in mechanism_observations if observation.get("candidate_eligible")
        )
        mechanism_memory = record_observations(
            mechanism_memory,
            mechanism_observations,
            prompt_hash=epoch_prompt_hash,
            taxonomy_version=taxonomy_version,
            iteration=iteration,
        )
        save_memory(mechanism_memory_path, mechanism_memory)
        if candidate_observation_count:
            selected_mechanism, mechanism_report = select_epoch_mechanism(
                mechanism_observations,
                evidence_memory=mechanism_memory.get("entries", []),
                prompt_hash=epoch_prompt_hash,
                current_iteration=iteration,
            )
        write_text(epoch_paths["mechanism_clusters"], json.dumps(mechanism_report, ensure_ascii=False, indent=2))
        record_stage(
            epoch_manifest,
            "mechanism_clustering",
            status="success" if selected_mechanism is not None else "skipped",
            outputs={
                "evidence_inventory": rel_to_iter(iter_dir, epoch_paths["mechanism_evidence_inventory"]),
                "clusters": rel_to_iter(iter_dir, epoch_paths["mechanism_clusters"]),
            },
            note=(
                f"valid_patterns={epoch_valid_pattern_count}, "
                f"rejected_patterns={epoch_rejected_pattern_count}, "
                f"candidate_observations={candidate_observation_count}"
            ),
        )
        if selected_mechanism is not None:
            selected_for_log = {
                key: value
                for key, value in selected_mechanism.items()
                if key != "supporting_batch_observations"
            }
            write_text(epoch_paths["mechanism_selected"], json.dumps(selected_for_log, ensure_ascii=False, indent=2))
            epoch_acceptance["selected_mechanism_id"] = selected_mechanism["mechanism_id"]
            epoch_acceptance["selected_hypothesis_id"] = selected_mechanism.get("hypothesis_id")

        batch_revision_inputs: list[dict[str, Any]] = []
        prompt_gap_audit: dict[str, Any] | None = None
        prompt_gap_rejection_reason: str | None = None
        if selected_mechanism is not None and not args.no_evolve:
            batch_edit_results = collect_selected_batch_revisions(
                args=args,
                llm_client=llm_client,
                run_dir=run_dir,
                iter_dir=iter_dir,
                prompt=prompt,
                batch_results=batch_results,
                selected_mechanism=selected_mechanism,
                has_accepted_update=has_accepted_update,
                iteration=iteration,
            )
            (
                batch_revision_inputs,
                prompt_gap_audit,
                prompt_gap_rejection_reason,
            ) = build_prompt_gap_consensus(
                selected_mechanism=selected_mechanism,
                batch_edit_results=batch_edit_results,
            )
            write_text(
                epoch_paths["prompt_gap_consensus"],
                json.dumps(prompt_gap_audit, ensure_ascii=False, indent=2),
            )
            record_stage(
                epoch_manifest,
                "prompt_gap_consensus",
                status="success" if prompt_gap_audit["decision"] == "proceed" else "skipped",
                outputs={
                    "audit": rel_to_iter(iter_dir, epoch_paths["prompt_gap_consensus"]),
                },
                note=(
                    f"decision={prompt_gap_audit['decision']}, "
                    f"required_votes={prompt_gap_audit['required_votes']}, "
                    f"actionable_plans={prompt_gap_audit['actionable_plan_count']}"
                ),
            )
            epoch_collected_count = len(batch_revision_inputs)
            epoch_skipped_count += selected_mechanism["supporting_batch_count"] - epoch_collected_count
            epoch_acceptance.update(
                {
                    "collected_batch_count": epoch_collected_count,
                    "skipped_batch_count": epoch_skipped_count,
                    "prompt_gap_consensus": {
                        key: prompt_gap_audit[key]
                        for key in (
                            "required_votes",
                            "selected_mechanism_signature",
                            "consensus_scope",
                            "localization_consensus_section",
                            "localization_vote_count",
                            "actionable_section",
                            "actionable_plan_count",
                            "decision",
                        )
                    },
                }
            )

        if args.no_evolve:
            epoch_acceptance["rejection_reasons"] = ["no_evolve"]
        elif epoch_valid_pattern_count == 0:
            epoch_acceptance["rejection_reasons"] = ["no_valid_failure_patterns"]
        elif candidate_observation_count == 0:
            epoch_acceptance["rejection_reasons"] = ["no_candidate_eligible_patterns"]
        elif selected_mechanism is None:
            epoch_acceptance["rejection_reasons"] = ["no_eligible_mechanism_cluster"]
        elif not batch_revision_inputs:
            epoch_acceptance["rejection_reasons"] = [
                prompt_gap_rejection_reason or "no_valid_selected_mechanism_plans"
            ]
        else:
            print(
                f"[iteration {iteration}] planning one revision for mechanism "
                f"{selected_mechanism['mechanism_id']} from {len(batch_revision_inputs)} batch plan(s)"
            )
            epoch_edit_budget = make_edit_budget(
                has_accepted_update=has_accepted_update,
                args=args,
                agent="epoch_planner",
            )
            epoch_revision_plan = plan_epoch_revision(
                current_prompt=prompt,
                batch_revision_inputs=batch_revision_inputs,
                selected_mechanism=selected_mechanism,
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
                        epoch_acceptance["selected_mechanism_id"] = selected_mechanism["mechanism_id"]
                        epoch_acceptance["mechanism_taxonomy_version"] = taxonomy_version
                        epoch_acceptance["mechanism_taxonomy_policy_revision"] = taxonomy_policy_revision
                        if prompt_gap_audit is not None:
                            epoch_acceptance["prompt_gap_consensus"] = {
                                key: prompt_gap_audit[key]
                                for key in (
                                    "required_votes",
                                    "selected_mechanism_signature",
                                    "consensus_scope",
                                    "localization_consensus_section",
                                    "localization_vote_count",
                                    "actionable_section",
                                    "actionable_plan_count",
                                    "decision",
                                )
                            }
                        epoch_acceptance.update(
                            {
                                "batch_count": len(training_batches),
                                "collected_batch_count": epoch_collected_count,
                                "skipped_batch_count": epoch_skipped_count,
                                "valid_pattern_count": epoch_valid_pattern_count,
                                "rejected_pattern_count": epoch_rejected_pattern_count,
                            }
                        )
                        if not epoch_acceptance["accepted"]:
                            epoch_acceptance["pipeline_rejection_reason"] = "validation_rejected"
                        write_text(epoch_paths["acceptance"], json.dumps(epoch_acceptance, ensure_ascii=False, indent=2))
                        if epoch_acceptance["accepted"]:
                            selected_hypothesis_status = "accepted"
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
                            selected_hypothesis_status = "rejected"
                            selected_hypothesis_reasons = [
                                str(reason)
                                for reason in epoch_acceptance.get("rejection_reasons", [])
                            ]
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
                        selected_hypothesis_status = "accepted"
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
                            "valid_pattern_count": epoch_valid_pattern_count,
                            "rejected_pattern_count": epoch_rejected_pattern_count,
                            "selected_mechanism_id": selected_mechanism["mechanism_id"],
                            "mechanism_taxonomy_version": taxonomy_version,
                            "mechanism_taxonomy_policy_revision": taxonomy_policy_revision,
                            "selected_hypothesis_id": selected_mechanism.get("hypothesis_id"),
                            "mechanism_memory": "../mechanism_memory.json",
                            "prompt_gap_consensus": {
                                key: prompt_gap_audit[key]
                                for key in (
                                    "required_votes",
                                    "selected_mechanism_signature",
                                    "consensus_scope",
                                    "localization_consensus_section",
                                    "localization_vote_count",
                                    "actionable_section",
                                    "actionable_plan_count",
                                    "decision",
                                )
                            }
                            if prompt_gap_audit is not None
                            else None,
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
        if selected_mechanism is not None and selected_hypothesis_status is not None:
            mechanism_memory = mark_hypothesis_status(
                mechanism_memory,
                prompt_hash=epoch_prompt_hash,
                hypothesis_id=str(selected_mechanism.get("hypothesis_id") or ""),
                status=selected_hypothesis_status,
                rejection_reasons=selected_hypothesis_reasons,
            )
            save_memory(mechanism_memory_path, mechanism_memory)
        write_evaluation_records(epoch_paths["analysis_records"], epoch_records)
        write_text(epoch_paths["analysis_summary"], json.dumps(epoch_summary, ensure_ascii=False, indent=2))
        write_text(epoch_paths["analysis_overview"], build_analysis(epoch_records, epoch_summary))
        write_text(iter_dir / "evaluation" / "batch_summaries.json", json.dumps(batch_summaries, ensure_ascii=False, indent=2))
        write_text(epoch_paths["acceptance"], json.dumps(epoch_acceptance, ensure_ascii=False, indent=2))
        write_attribution_lineage(
            path=epoch_paths["mechanism_lineage"],
            selected_mechanism=selected_mechanism,
            batch_edit_results=batch_edit_results,
            prompt_gap_audit=prompt_gap_audit,
            epoch_revision_plan=epoch_revision_plan,
            prompt_rewriter_output_path=epoch_paths["prompt_rewriter_output"],
            acceptance=epoch_acceptance,
        )
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


def run_validation_calibration(
    *,
    prompt: str,
    validation_cases: list[Case],
    args: argparse.Namespace,
    llm_client: LLMClient,
    run_dir: Path,
) -> dict[str, float]:
    if not validation_cases:
        raise ValueError("Validation calibration requires a non-empty fixed validation split")
    root = run_dir / "validation_calibration"
    summaries: list[dict[str, float]] = []
    for repeat in range(1, args.validation_calibration_repeats + 1):
        repeat_dir = root / f"repeat_{repeat:03d}"
        _, summary = evaluate_cases(
            prompt=prompt,
            cases=validation_cases,
            args=args,
            llm_client=llm_client,
            output_path=repeat_dir / "records.jsonl",
            state_dir=run_dir,
            phase=f"validation_calibration:repeat_{repeat:03d}",
            case_concurrency=args.validation_gate_concurrency,
        )
        summaries.append(summary)
        write_text(repeat_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))

    aggregate = aggregate_repeat_summaries(summaries)
    metric_stats = {
        metric: calibration_statistics(
            [summary.get(metric, 0.0) for summary in summaries],
            validation_repeats=args.validation_repeats,
            metric_resolution=(1 / len(validation_cases) if metric == "plantuml_compilation_pass_rate" else 0.0),
        )
        for metric in VALIDATION_CALIBRATION_METRICS
    }
    report = {
        "calibration_repeats": args.validation_calibration_repeats,
        "target_validation_repeats": args.validation_repeats,
        "validation_case_count": len(validation_cases),
        "validation_split_fingerprint": case_split_fingerprint(validation_cases),
        "repeat_summaries": summaries,
        "aggregate_summary": aggregate,
        "metric_statistics": metric_stats,
        "threshold_policy": "1.645 * sqrt(2 / target_validation_repeats) * sample_std; compile is diagnostic and floored at 1 / validation_case_count",
        "note": "Node/Relation recommendations are never applied automatically. Compile calibration is diagnostic only.",
    }
    write_text(root / "aggregate_summary.json", json.dumps(report, ensure_ascii=False, indent=2))
    write_text(
        root / "report.md",
        "# Validation Baseline Calibration\n\n"
        f"- repeats: {args.validation_calibration_repeats}\n"
        f"- validation cases: {len(validation_cases)}\n"
        f"- validation split fingerprint: `{case_split_fingerprint(validation_cases)}`\n\n"
        + "\n".join(
            f"- {metric}: mean={stats['mean']:.6f}, std={stats['sample_std']:.6f}, "
            f"range={stats['range']:.6f}, suggested_min_delta={stats['suggested_min_delta']:.6f}"
            for metric, stats in metric_stats.items()
        )
        + "\n",
    )
    print(f"[calibration] completed {args.validation_calibration_repeats} repeats: {root}")
    return aggregate


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
    write_data_split_summary(
        run_dir=run_dir,
        args=args,
        train_pool_cases=train_pool_cases,
        train_cases=train_cases,
        validation_cases=validation_cases,
    )
    work_prompt_path = initialize_run_prompt(args.prompt_path, run_dir)
    if args.calibrate_validation_only:
        return run_validation_calibration(
            prompt=read_text(work_prompt_path),
            validation_cases=validation_cases,
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
    write_data_split_summary(
        run_dir=run_dir,
        args=args,
        train_pool_cases=train_pool_cases,
        train_cases=train_cases,
        validation_cases=validation_cases,
        test_cases=test_cases,
    )
    work_prompt_path = initialize_run_prompt(args.prompt_path, run_dir)
    print(
        f"[run] test={test_dataset}, train_pool_cases={len(train_pool_cases)}, "
        f"train_cases={len(train_cases)}, validation_gate_cases={len(validation_cases)}, "
        f"test_cases={len(test_cases)}"
    )
    print(f"[run] test distribution: {describe_case_distribution(test_cases)}")
    if args.calibrate_validation_only:
        return run_validation_calibration(
            prompt=read_text(work_prompt_path),
            validation_cases=validation_cases,
            args=args,
            llm_client=llm_client,
            run_dir=run_dir,
        )
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
    parser.add_argument("--mechanism-taxonomy-path", type=Path, default=DEFAULT_MECHANISM_TAXONOMY_PATH, help="Versioned mechanism taxonomy JSON; defaults to atomic v3")
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
    parser.add_argument("--epoch-batch-concurrency", type=int, default=1, help="Number of training batches to process concurrently within each epoch")
    parser.add_argument("--heldout-test-concurrency", type=int, default=1, help="Number of held-out test cases to evaluate concurrently; 1 keeps serial behavior")
    parser.add_argument("--validation-gate-concurrency", type=int, default=1, help="Number of validation cases to evaluate concurrently; 1 keeps serial behavior")
    parser.add_argument("--sample-strategy", choices=["stratified", "random", "prefix"], default="stratified", help="How to select limited training cases")
    parser.add_argument("--test-sample-strategy", choices=["stratified", "random", "prefix"], default="prefix", help="How to select limited held-out test cases")
    parser.add_argument("--validation-gate", action=argparse.BooleanOptionalAction, default=True, help="Reserve a fixed validation gate split from the training pool; use --no-validation-gate to disable")
    parser.add_argument("--validation-gate-size", type=int, default=30, help="Maximum number of training-pool cases reserved for validation gate; capped at about one third of the sampled training pool, 0 disables the split")
    parser.add_argument("--validation-gate-strategy", choices=["stratified", "random", "prefix"], default="stratified", help="How to choose fixed validation gate cases from the sampled training pool")
    parser.add_argument("--validation-gate-seed", type=int, default=20260629, help="Seed used only for selecting fixed validation gate cases")
    parser.add_argument("--validation-repeats", type=int, default=3, help="Paired baseline/candidate repeats for any-improvement validation")
    parser.add_argument("--acceptance-min-wins", type=int, default=2, help="Strictly positive repeat deltas required for a winning metric")
    parser.add_argument("--acceptance-policy", choices=["any-improvement", "legacy"], default="any-improvement", help="Candidate acceptance rule; legacy reproduces the previous single-run gate")
    parser.add_argument("--any-improvement-node-min-delta", type=float, default=0.0, help="Mean LLM node F1 delta required by any-improvement")
    parser.add_argument("--any-improvement-relation-min-delta", type=float, default=0.0, help="Mean LLM relation F1 delta required by any-improvement")
    parser.add_argument("--any-improvement-compile-min-delta", type=float, default=0.0, help="Deprecated compatibility option; compilation is diagnostic and cannot accept a candidate")
    parser.add_argument("--calibrate-validation-only", action="store_true", help="Run repeated seed-prompt validation calibration and exit without training or held-out evaluation")
    parser.add_argument("--validation-calibration-repeats", type=int, default=5, help="Seed-prompt repeats used by --calibrate-validation-only")
    parser.add_argument("--sample-seed", type=int, default=13)
    parser.add_argument("--model", default=os.environ.get("ZHIPU_LLM_MODEL", DEFAULT_MODEL), help="Legacy fallback model for all roles")
    parser.add_argument("--generation-model", default=os.environ.get("ZHIPU_LLM_GENERATION_MODEL"), help="Model used for PlantUML prediction; defaults to --model")
    parser.add_argument("--agent-model", default=os.environ.get("ZHIPU_LLM_AGENT_MODEL"), help="Model used by prompt-evolution agents; defaults to --model")
    parser.add_argument("--judge-model", default=os.environ.get("ZHIPU_LLM_JUDGE_MODEL"), help="Model used for semantic judging and auxiliary extraction; defaults to --model")
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
    parser.add_argument("--judge-thinking", choices=["inherit", "enabled", "disabled"], default=os.environ.get("ZHIPU_JUDGE_THINKING_TYPE", "inherit"), help="Thinking mode for LLM semantic judge calls")
    parser.add_argument(
        "--do-sample",
        type=optional_bool,
        default=False,
        help="GLM sampling mode; defaults to false (greedy decoding), true enables sampling, and 'omit' uses the provider default",
    )
    parser.add_argument("--llm-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-max-retries", type=int, default=20, help="Retries for provider 429/5xx/transient errors before failing")
    parser.add_argument("--llm-rate-limit-initial-wait", type=int, default=30, help="Initial wait seconds for provider rate-limit retries")
    parser.add_argument("--llm-rate-limit-max-wait", type=int, default=600, help="Maximum wait seconds for provider rate-limit retries")
    parser.add_argument("--node-match-threshold", type=float, default=0.85, help="LATO-style node semantic similarity threshold")
    parser.add_argument("--relation-match-threshold", type=float, default=0.85, help="LATO-style relation semantic similarity threshold")
    parser.add_argument("--semantic-embedding-model", default=DEFAULT_EMBEDDING_MODEL, help="Sentence-transformers model used for LATO-style semantic element matching")
    parser.add_argument("--embedding-element-metrics", action=argparse.BooleanOptionalAction, default=False, help="Run auxiliary embedding/difflib element metrics for diagnostics; these metrics do not drive training or acceptance")
    parser.add_argument("--metric-matcher", choices=["embedding", "difflib"], default="embedding", help="Element matcher for auxiliary embedding metrics; only used with --embedding-element-metrics")
    parser.add_argument("--element-extractor", choices=["rule", "llm", "auto"], default=os.environ.get("APE_ELEMENT_EXTRACTOR", "llm"), help="Backend for auxiliary PlantUML-to-node/relation extraction; only used with --embedding-element-metrics")
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
    parser.add_argument("--llm-element-metrics", action=argparse.BooleanOptionalAction, default=True, help="Run LLM judge node/relation P/R/F1 metrics used by training and validation gate; use --no-llm-element-metrics only for cheap local smoke tests")
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
    args.mechanism_taxonomy_path = args.mechanism_taxonomy_path.resolve()
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
    resolve_model_roles(args)
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
    load_mechanism_taxonomy(args.mechanism_taxonomy_path)

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
