#!/usr/bin/env python3
"""Entry point for APE prompt evolution."""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import dataclasses
import hashlib
import json
import math
import os
import statistics
from pathlib import Path
from typing import Any

from analysis.error_selector import (
    build_error_observations,
    failure_analysis_item_count,
    representative_errors,
    select_error_group,
    selected_group_evidence_family,
    selected_group_required_metrics,
    validate_selected_group_eligibility,
)
from analysis.selector_agents import (
    build_rewriter_plan,
    localize_selector_group,
    propose_selector_edit,
)
from analysis.failure_analysis import analyze_failures, build_analysis
from analysis.candidate_registry import (
    evaluated_candidate_ids,
    group_attempt_history,
    group_attempt_signature,
    load_candidate_registry,
    prompt_fingerprint,
    record_evaluated_candidate,
    record_group_attempt,
    save_candidate_registry,
)
from analysis.prompt_rewriter import rewrite_prompt
from prompt_ops import extract_json_object
from config import (
    DEFAULT_BASE_URL,
    DEFAULT_DATASETS_DIR,
    DEFAULT_ERROR_LOCALIZATION_PROMPT_PATH,
    DEFAULT_ERROR_SELECTOR_PROMPT_PATH,
    DEFAULT_FAILURE_ANALYSIS_PROMPT_PATH,
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_MODEL,
    DEFAULT_PLANTUML_JAR,
    DEFAULT_PROMPT_EDITOR_PROMPT_PATH,
    DEFAULT_PROMPT_REWRITER_PROMPT_PATH,
    DEFAULT_PROMPT_PATH,
    DEFAULT_RUNS_DIR,
    DEFAULT_THINKING_TYPE,
    get_llm_provider_settings,
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
    if args.candidate_application_mode not in {
        "isolated",
        "cumulative",
        "diagnostic-apply",
    }:
        raise ValueError(
            "--candidate-application-mode must resolve to isolated, cumulative, or diagnostic-apply"
        )
    thinking_fields = (
        "thinking",
        "generation_thinking",
        "analysis_thinking",
        "selector_thinking",
        "localization_thinking",
        "editor_thinking",
        "judge_thinking",
        "element_extraction_thinking",
    )
    for field in thinking_fields:
        value = getattr(args, field)
        if value == "inherit":
            value = args.thinking
            setattr(args, field, value)
        if value not in {"enabled", "disabled"}:
            raise ValueError(
                f"--{field.replace('_', '-')} must resolve to enabled or disabled"
            )
    temperature_fields = (
        "temperature",
        "analysis_temperature",
        "selector_temperature",
        "localization_temperature",
        "editor_temperature",
        "llm_judge_temperature",
        "element_extraction_temperature",
    )
    nonzero_temperatures = [
        f"--{field.replace('_', '-')}={getattr(args, field)}"
        for field in temperature_fields
        if float(getattr(args, field)) != 0.0
    ]
    if nonzero_temperatures:
        raise ValueError(
            "All model temperatures must be 0; rejected "
            + ", ".join(nonzero_temperatures)
        )
    if args.max_tokens < 1:
        raise ValueError("--max-tokens must be positive")
    if args.top_p is not None and not 0.01 <= args.top_p <= 0.99:
        raise ValueError("--top-p must be between 0.01 and 0.99, or omit")
    if args.top_p is not None:
        print(
            "[config] Both temperature and top_p are set; provider docs recommend adjusting only one.",
            flush=True,
        )
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
    if args.heldout_repeats < 1:
        raise ValueError("--heldout-repeats must be positive")
    if args.gate_concurrency < 1:
        raise ValueError("--gate-concurrency must be positive")
    if args.gate1_size < 0:
        raise ValueError("--gate1-size must be non-negative")
    if args.gate1_seed < 0:
        raise ValueError("--gate1-seed must be non-negative")
    if args.gate2_size < 0:
        raise ValueError("--gate2-size must be non-negative")
    if args.gate2_seed < 0:
        raise ValueError("--gate2-seed must be non-negative")
    if args.validation_repeats < 1:
        raise ValueError("--validation-repeats must be positive")
    if args.max_candidate_attempts_per_epoch < 1:
        raise ValueError("--max-candidate-attempts-per-epoch must be positive")
    if not args.no_evolve and (
        not args.gate1 or args.gate1_size == 0
    ):
        raise ValueError(
            "Selector workflow requires an enabled non-empty Gate1"
        )
    if not args.no_evolve and args.gate2 and args.gate2_size == 0:
        raise ValueError(
            "Enabled Gate2 requires a non-empty Gate2 split"
        )
    if (
        not args.no_evolve
        and args.gate2
        and args.candidate_application_mode == "diagnostic-apply"
    ):
        raise ValueError(
            "--candidate-application-mode diagnostic-apply cannot bypass Gate2; "
            "use cumulative/isolated or explicitly --no-gate2"
        )
    if (
        args.candidate_application_mode in {"isolated", "diagnostic-apply"}
        and not args.no_evolve
        and args.validation_repeats < 3
    ):
        raise ValueError(
            "Isolated and diagnostic-apply modes require --validation-repeats >= 3"
        )
    if (
        args.candidate_application_mode == "isolated"
        and not args.no_evolve
        and args.eval_initial_test
    ):
        raise ValueError(
            "Isolated candidate mode does not evaluate heldout during candidate search; "
            "remove --eval-initial-test"
        )
    if args.validation_calibration_repeats < 2:
        raise ValueError("--validation-calibration-repeats must be at least 2")
    if any(
        value < 1
        for value in (
            args.analysis_max_tokens,
            args.selector_max_tokens,
            args.localization_max_tokens,
            args.editor_max_tokens,
        )
    ):
        raise ValueError(
            "Agent-specific max-token values must all be positive"
        )
    if args.llm_judge_max_tokens < 1:
        raise ValueError("--llm-judge-max-tokens must be positive")
    if args.llm_judge_max_retries < 1:
        raise ValueError("--llm-judge-max-retries must be positive")
    if args.element_extraction_max_tokens < 1:
        raise ValueError("--element-extraction-max-tokens must be positive")
    if args.element_extraction_max_retries < 1:
        raise ValueError("--element-extraction-max-retries must be positive")
    if not args.llm_element_metrics and not args.no_evolve:
        raise ValueError(
            "--no-llm-element-metrics is only supported with --no-evolve because "
            "training and validation use LLM judge metrics"
        )
    if args.llm_element_metrics and not args.api_key:
        raise ValueError(
            "LLM semantic element metrics require the active provider API key or --api-key"
        )
    if (
        args.embedding_element_metrics
        and args.element_extractor == "llm"
        and not args.api_key
    ):
        raise ValueError(
            "LLM element extraction requires the active provider API key or --api-key"
        )
    if getattr(args, "llm_provider", "zhipu") == "deepseek" and args.do_sample is not None:
        raise ValueError(
            "DeepSeek does not define do_sample; omit it with --do-sample omit"
        )


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
    """Resolve role-specific model IDs with the shared --model fallback."""
    for field in ("generation_model", "agent_model", "judge_model"):
        value = str(getattr(args, field, "") or args.model).strip()
        if not value:
            raise ValueError(f"--{field.replace('_', '-')} must resolve to a non-empty model ID")
        setattr(args, field, value)
    args.llm_judge_model = args.judge_model
    return args


def resolve_pipeline_defaults(args: argparse.Namespace) -> argparse.Namespace:
    mode = str(getattr(args, "candidate_application_mode", "auto") or "auto")
    if mode == "auto":
        # Formal runs must always apply only after the enabled Gate's metric decision.
        # The legacy diagnostic path remains available only when explicitly requested.
        args.candidate_application_mode = "cumulative"
    return args


def resolve_agent_thinking(value: str | None, fallback: str) -> str:
    if value is None or value == "inherit":
        return fallback
    return value


def iteration_paths(iter_dir: Path) -> dict[str, Path]:
    return {
        "manifest": iter_dir / "manifest.json",
        "prompt_before": iter_dir / "prompts" / "before.md",
        "prompt_candidate": iter_dir / "prompts" / "candidate.md",
        "prompt_after": iter_dir / "prompts" / "after.md",
        "analysis_cases": iter_dir / "batches" / "analysis_cases.json",
        "validation_cases": iter_dir / "gate1" / "cases.json",
        "validation_baseline_records": iter_dir / "gate1" / "baseline_records.jsonl",
        "validation_baseline_summary": iter_dir / "gate1" / "baseline_summary.json",
        "validation_candidate_records": iter_dir / "gate1" / "candidate_records.jsonl",
        "validation_candidate_summary": iter_dir / "gate1" / "candidate_summary.json",
        "validation_aggregate_summary": iter_dir / "gate1" / "aggregate_summary.json",
        "validation_analysis": iter_dir / "gate1" / "analysis.md",
        "validation_impact_summary": iter_dir / "gate1" / "impact_summary.json",
        "validation_impact_report": iter_dir / "gate1" / "impact_report.md",
        "confirmation_cases": iter_dir / "gate2" / "cases.json",
        "confirmation_baseline_records": iter_dir / "gate2" / "baseline_records.jsonl",
        "confirmation_baseline_summary": iter_dir / "gate2" / "baseline_summary.json",
        "confirmation_candidate_records": iter_dir / "gate2" / "candidate_records.jsonl",
        "confirmation_candidate_summary": iter_dir / "gate2" / "candidate_summary.json",
        "confirmation_aggregate_summary": iter_dir / "gate2" / "aggregate_summary.json",
        "confirmation_analysis": iter_dir / "gate2" / "analysis.md",
        "confirmation_impact_summary": iter_dir / "gate2" / "impact_summary.json",
        "confirmation_impact_report": iter_dir / "gate2" / "impact_report.md",
        "analysis_records": iter_dir / "evaluation" / "analysis_records.jsonl",
        "analysis_summary": iter_dir / "evaluation" / "analysis_summary.json",
        "analysis_overview": iter_dir / "evaluation" / "analysis_overview.md",
        "failure_analysis_input": iter_dir / "agents" / "failure_analysis.input.json",
        "failure_analysis_output": iter_dir / "agents" / "failure_analysis.output.json",
        "failure_analysis_raw_output": iter_dir / "agents" / "failure_analysis.output.raw.txt",
        "failure_analysis_rejected_patterns": iter_dir / "agents" / "failure_analysis.rejected_patterns.json",
        "error_selector_input": iter_dir / "agents" / "error_selector.input.json",
        "error_selector_output": iter_dir / "agents" / "error_selector.output.json",
        "error_localization_input": iter_dir / "agents" / "error_localization.input.json",
        "error_localization_output": iter_dir / "agents" / "error_localization.output.json",
        "prompt_editor_input": iter_dir / "agents" / "prompt_editor.input.json",
        "prompt_editor_output": iter_dir / "agents" / "prompt_editor.output.json",
        "selected_error_group": iter_dir / "mechanisms" / "selected_error_group.json",
        "mechanism_evidence": iter_dir / "mechanisms" / "evidence.json",
        "mechanism_evidence_inventory": iter_dir / "mechanisms" / "evidence_inventory.json",
        "mechanism_lineage": iter_dir / "mechanisms" / "attribution_lineage.json",
        "prompt_rewriter_input": iter_dir / "agents" / "prompt_rewriter.input.json",
        "prompt_rewriter_output": iter_dir / "agents" / "prompt_rewriter.output.json",
        "acceptance": iter_dir / "decision" / "acceptance.json",
        "candidate_attempts": iter_dir / "decision" / "candidate_attempts.json",
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
            "gate1": {
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
            "gate2": {
                "cases": rel_to_iter(iter_dir, paths["confirmation_cases"]),
                "baseline_records": rel_to_iter(iter_dir, paths["confirmation_baseline_records"]),
                "baseline_summary": rel_to_iter(iter_dir, paths["confirmation_baseline_summary"]),
                "candidate_records": rel_to_iter(iter_dir, paths["confirmation_candidate_records"]),
                "candidate_summary": rel_to_iter(iter_dir, paths["confirmation_candidate_summary"]),
                "aggregate_summary": rel_to_iter(iter_dir, paths["confirmation_aggregate_summary"]),
                "analysis": rel_to_iter(iter_dir, paths["confirmation_analysis"]),
                "impact_summary": rel_to_iter(iter_dir, paths["confirmation_impact_summary"]),
                "impact_report": rel_to_iter(iter_dir, paths["confirmation_impact_report"]),
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
                "error_selector": {
                    "input": rel_to_iter(iter_dir, paths["error_selector_input"]),
                    "output": rel_to_iter(iter_dir, paths["error_selector_output"]),
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
            "mechanisms": {
                "evidence": rel_to_iter(iter_dir, paths["mechanism_evidence"]),
                "evidence_inventory": rel_to_iter(iter_dir, paths["mechanism_evidence_inventory"]),
                "selected_error_group": rel_to_iter(iter_dir, paths["selected_error_group"]),
                "attribution_lineage": rel_to_iter(iter_dir, paths["mechanism_lineage"]),
            },
            "decision": {
                "acceptance": rel_to_iter(iter_dir, paths["acceptance"]),
                "candidate_attempts": rel_to_iter(iter_dir, paths["candidate_attempts"]),
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


def split_gate1_cases(cases: list[Case], args: argparse.Namespace) -> tuple[list[Case], list[Case]]:
    if not args.gate1 or args.gate1_size <= 0 or len(cases) < 2:
        return list(cases), []

    max_gate_size_for_pool = max(1, len(cases) // 3)
    gate_size = min(args.gate1_size, max_gate_size_for_pool, len(cases) - 1)
    validation_cases = select_cases_with_strategy(
        cases,
        limit=gate_size,
        strategy=args.gate1_strategy,
        seed=args.gate1_seed,
    )
    validation_ids = {(case.dataset, case.case_id) for case in validation_cases}
    optimize_cases = [case for case in cases if (case.dataset, case.case_id) not in validation_ids]
    return optimize_cases, validation_cases


def split_gate_cases(
    cases: list[Case], args: argparse.Namespace
) -> tuple[list[Case], list[Case], list[Case]]:
    optimize_cases, validation_cases = split_gate1_cases(cases, args)
    if (
        args.no_evolve
        or not args.gate2
        or args.gate2_size <= 0
        or len(optimize_cases) < 2
    ):
        return optimize_cases, validation_cases, []

    max_gate_size_for_pool = max(1, len(optimize_cases) // 3)
    gate_size = min(
        args.gate2_size,
        max_gate_size_for_pool,
        len(optimize_cases) - 1,
    )
    confirmation_cases = select_cases_with_strategy(
        optimize_cases,
        limit=gate_size,
        strategy=args.gate2_strategy,
        seed=args.gate2_seed,
    )
    confirmation_ids = {
        (case.dataset, case.case_id) for case in confirmation_cases
    }
    train_cases = [
        case
        for case in optimize_cases
        if (case.dataset, case.case_id) not in confirmation_ids
    ]
    return train_cases, validation_cases, confirmation_cases


def case_split_fingerprint(cases: list[Case]) -> str:
    canonical = "".join(
        f"{case.dataset}\t{case.case_id}\n"
        for case in sorted(cases, key=lambda item: (item.dataset, item.case_id))
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def case_dataset_counts(cases: list[Case]) -> dict[str, int]:
    return {
        dataset: len(items)
        for dataset, items in sorted(grouped_cases(cases).items())
    }


def write_data_split_summary(
    *,
    run_dir: Path,
    args: argparse.Namespace,
    source_cases: list[Case],
    train_pool_cases: list[Case],
    train_cases: list[Case],
    validation_cases: list[Case],
    confirmation_cases: list[Case],
    test_cases: list[Case] | None = None,
) -> dict[str, Any]:
    summary = {
        "source_count": len(source_cases),
        "train_pool_count": len(train_pool_cases),
        "train_count": len(train_cases),
        "requested_gate1_count": args.gate1_size,
        "actual_gate1_count": len(validation_cases),
        "requested_gate2_count": args.gate2_size,
        "actual_gate2_count": len(confirmation_cases),
        "gate2_enabled": bool(args.gate2),
        "gate_sequence_policy": gate_sequence_policy(bool(args.gate2)),
        "test_count": len(test_cases or []),
        "source_dataset_counts": case_dataset_counts(source_cases),
        "train_pool_dataset_counts": case_dataset_counts(train_pool_cases),
        "train_dataset_counts": case_dataset_counts(train_cases),
        "gate1_dataset_counts": case_dataset_counts(validation_cases),
        "gate2_dataset_counts": case_dataset_counts(confirmation_cases),
        "test_dataset_counts": case_dataset_counts(test_cases or []),
        "gate1_split_fingerprint": case_split_fingerprint(validation_cases),
        "gate2_split_fingerprint": case_split_fingerprint(confirmation_cases),
    }
    write_text(run_dir / "data_split_summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    if args.gate1 and len(validation_cases) != args.gate1_size:
        print(
            f"[split] requested gate1 cases={args.gate1_size}, "
            f"actual={len(validation_cases)} after the one-third training-pool cap",
            flush=True,
        )
    if (
        args.gate2
        and not args.no_evolve
        and len(confirmation_cases) != args.gate2_size
    ):
        print(
            f"[split] requested gate2 cases={args.gate2_size}, "
            f"actual={len(confirmation_cases)} after the one-third remaining-pool cap",
            flush=True,
        )
    return summary


def write_evaluation_records(path: Path, records: list[Any]) -> None:
    lines = [json.dumps(dataclasses.asdict(record), ensure_ascii=False) for record in records]
    write_text(path, ("\n".join(lines) + "\n") if lines else "")




@dataclasses.dataclass
class EpochBatchResult:
    batch_index: int
    global_update_step: int
    records: list[Any]
    summary: dict[str, float]
    batch_summary: dict[str, Any]
    failure_analysis: dict[str, Any] | None = None
    error_observations: list[dict[str, Any]] = dataclasses.field(default_factory=list)
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

    observations = build_error_observations(failure_analysis, batch_id=batch_index)
    evidence_for_log = [
        {key: value for key, value in observation.items() if key != "patterns"}
        for observation in observations
    ]
    write_text(paths["mechanism_evidence"], json.dumps(evidence_for_log, ensure_ascii=False, indent=2))
    classification_counts = {
        "candidate": sum(1 for item in observations if item.get("status") == "actionable"),
        "dataset_convention": sum(1 for item in observations if item.get("status") == "gold_only"),
        "record_only": sum(
            1 for item in observations if item.get("status") in {"secondary", "uncertain"}
        ),
    }
    candidate_count = classification_counts["candidate"]
    record_stage(
        manifest,
        "failure_error_filter",
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
    print(
        f"{log_prefix} collected {candidate_count} "
        "actionable failure error(s)"
    )
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
        error_observations=observations,
        valid_pattern_count=failure_analysis_item_count(failure_analysis),
        rejected_pattern_count=len(failure_result.rejected_patterns),
        skipped_count=0 if candidate_count else 1,
    )




SEMANTIC_ACCEPTANCE_METRICS = (
    "llm_node_f1",
    "llm_relation_f1",
)

DIRECT_ACCEPTANCE_METRIC_BY_FAMILY = {
    "compile": "plantuml_compilation_pass_rate",
}

REQUIRED_METRIC_ACCEPTANCE_POLICY = (
    "all-required-positive-pooled-balanced-and-source-weighted-mean-delta"
)
SINGLE_GATE_SEQUENCE_POLICY = "single-gate1"
DUAL_GATE_SEQUENCE_POLICY = "gate1-then-fresh-gate2"


def gate_sequence_policy(gate2_required: bool) -> str:
    """Return the recorded gate sequence without changing acceptance semantics."""
    return (
        DUAL_GATE_SEQUENCE_POLICY
        if gate2_required
        else SINGLE_GATE_SEQUENCE_POLICY
    )

VALIDATION_CALIBRATION_METRICS = (
    *SEMANTIC_ACCEPTANCE_METRICS,
    "plantuml_compilation_pass_rate",
)


def calibration_statistics(values: list[float]) -> dict[str, float]:
    samples = [float(value) for value in values]
    if not samples:
        raise ValueError("Calibration requires at least one value")
    sample_std = statistics.stdev(samples) if len(samples) >= 2 else 0.0
    return {
        "count": float(len(samples)),
        "mean": statistics.fmean(samples),
        "sample_std": sample_std,
        "min": min(samples),
        "max": max(samples),
        "range": max(samples) - min(samples),
    }


def aggregate_repeat_summaries(summaries: list[dict[str, float]]) -> dict[str, float]:
    if not summaries:
        return {}
    keys = sorted(set().union(*(summary.keys() for summary in summaries)))
    return {
        key: statistics.fmean(float(summary.get(key, 0.0)) for summary in summaries)
        for key in keys
    }


PER_DATASET_DECOMPOSITION_METRICS = (
    "llm_node_precision",
    "llm_node_recall",
    "llm_node_f1",
    "llm_relation_precision",
    "llm_relation_recall",
    "llm_relation_f1",
    "plantuml_compilation_pass_rate",
)


def per_dataset_metric_decomposition(
    repeat_pairs: list[tuple[int, list[Any], list[Any]]],
) -> dict[str, dict[str, Any]]:
    """Split paired gate repeats by source dataset for audit and Gate aggregation.

    A mixed gate pools every dataset into one mean, so a rule that helps one
    dataset and hurts another is indistinguishable from a rule that changes
    nothing. This decomposition reuses the records already produced by the
    gate repeats; it issues no additional model calls.

    The full decomposition remains an audit artifact. Acceptance receives only
    the compact aggregates produced by ``aggregate_source_dataset_metrics``.
    """

    grouped: dict[str, dict[int, dict[str, dict[str, float] | None]]] = {}
    for repeat, baseline_records, candidate_records in repeat_pairs:
        datasets = sorted(
            {
                str(record.dataset)
                for record in [*baseline_records, *candidate_records]
            }
        )
        for dataset in datasets:
            bucket = grouped.setdefault(dataset, {}).setdefault(
                repeat, {"baseline": None, "candidate": None}
            )
            for role, records in (
                ("baseline", baseline_records),
                ("candidate", candidate_records),
            ):
                dataset_records = [
                    record
                    for record in records
                    if str(record.dataset) == dataset
                ]
                bucket[role] = (
                    summarize_records(dataset_records) if dataset_records else None
                )

    decomposition: dict[str, dict[str, Any]] = {}
    for dataset in sorted(grouped):
        repeats = grouped[dataset]
        metrics: dict[str, dict[str, Any]] = {}
        for metric in PER_DATASET_DECOMPOSITION_METRICS:
            deltas: list[float] = []
            missing_repeats: list[int] = []
            for repeat in sorted(repeats):
                baseline = repeats[repeat]["baseline"]
                candidate = repeats[repeat]["candidate"]
                baseline_value = (
                    baseline.get(metric) if isinstance(baseline, dict) else None
                )
                candidate_value = (
                    candidate.get(metric) if isinstance(candidate, dict) else None
                )
                semantic_metric = metric.startswith("llm_")
                semantic_available = bool(
                    not semantic_metric
                    or (
                        isinstance(baseline, dict)
                        and isinstance(candidate, dict)
                        and float(baseline.get("llm_element_evaluated", 0.0)) > 0.0
                        and float(candidate.get("llm_element_evaluated", 0.0)) > 0.0
                    )
                )
                if (
                    isinstance(baseline_value, (int, float))
                    and not isinstance(baseline_value, bool)
                    and isinstance(candidate_value, (int, float))
                    and not isinstance(candidate_value, bool)
                    and semantic_available
                ):
                    deltas.append(float(candidate_value) - float(baseline_value))
                else:
                    missing_repeats.append(repeat)
            available = bool(repeats) and not missing_repeats
            metrics[metric] = {
                "available": available,
                "repeat_deltas": deltas if available else [],
                "mean_delta": statistics.fmean(deltas) if available else None,
                "wins": (
                    sum(1 for delta in deltas if delta > 0.0)
                    if available
                    else None
                ),
                "missing_repeats": missing_repeats,
            }
        case_counts = [
            int(float(summary.get("count", 0.0)))
            for repeat in repeats.values()
            for summary in (repeat["baseline"], repeat["candidate"])
            if isinstance(summary, dict)
        ]
        decomposition[dataset] = {
            "case_count": max(case_counts) if case_counts else 0,
            "repeat_count": len(repeats),
            "metrics": metrics,
        }
    return decomposition


def aggregate_source_dataset_metrics(
    *,
    per_dataset_results: dict[str, dict[str, Any]],
    source_dataset_counts: dict[str, int],
    metrics: list[str] | tuple[str, ...],
) -> dict[str, dict[str, Any]]:
    """Compute equal-domain and source-population-weighted Gate deltas."""

    valid_counts: dict[str, int] = {}
    invalid_count_datasets: list[str] = []
    for dataset, count in sorted(source_dataset_counts.items()):
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            invalid_count_datasets.append(str(dataset))
        else:
            valid_counts[str(dataset)] = count

    observed_datasets = {str(dataset) for dataset in per_dataset_results}
    expected_datasets = set(valid_counts)
    missing_count_datasets = sorted(
        set(invalid_count_datasets) | (observed_datasets - expected_datasets)
    )
    source_count_missing = bool(
        not valid_counts or missing_count_datasets
    )

    aggregates: dict[str, dict[str, Any]] = {}
    for metric in metrics:
        deltas: dict[str, float] = {}
        missing_datasets: list[str] = []
        for dataset in sorted(expected_datasets):
            dataset_payload = per_dataset_results.get(dataset)
            metric_payload = (
                dataset_payload.get("metrics", {}).get(metric)
                if isinstance(dataset_payload, dict)
                else None
            )
            mean_delta = (
                metric_payload.get("mean_delta")
                if isinstance(metric_payload, dict)
                and metric_payload.get("available") is True
                else None
            )
            if (
                isinstance(mean_delta, bool)
                or not isinstance(mean_delta, (int, float))
                or not math.isfinite(float(mean_delta))
            ):
                missing_datasets.append(dataset)
            else:
                deltas[dataset] = float(mean_delta)

        available = bool(
            expected_datasets
            and not source_count_missing
            and not missing_datasets
            and len(deltas) == len(expected_datasets)
        )
        total_weight = sum(valid_counts.values())
        aggregates[metric] = {
            "available": available,
            "balanced_mean_delta": (
                statistics.fmean(deltas.values()) if available else None
            ),
            "source_weighted_mean_delta": (
                sum(deltas[dataset] * valid_counts[dataset] for dataset in deltas)
                / total_weight
                if available and total_weight > 0
                else None
            ),
            "weight_basis": "source_population",
            "missing_datasets": missing_datasets,
            "source_dataset_count_missing": source_count_missing,
            "missing_count_datasets": missing_count_datasets,
            "dataset_count": len(expected_datasets),
            "source_population_count": total_weight,
        }
    return aggregates


def any_improvement_decision(
    *,
    baseline_summaries: list[dict[str, float]],
    candidate_summaries: list[dict[str, float]],
    validation_case_count: int,
    candidate_prompt: str,
    baseline_prompt: str,
    max_prompt_chars: int,
    candidate_evidence_family: str,
    required_metrics: list[str] | tuple[str, ...],
    cross_dataset_metric_results: dict[str, dict[str, Any]],
) -> tuple[bool, dict[str, Any]]:
    if candidate_evidence_family not in {
        "semantic",
        *DIRECT_ACCEPTANCE_METRIC_BY_FAMILY,
    }:
        raise ValueError(
            f"Unsupported candidate evidence family: {candidate_evidence_family!r}"
        )
    normalized_required_metrics = tuple(required_metrics)
    if not normalized_required_metrics:
        raise ValueError("required_metrics must not be empty")
    if len(set(normalized_required_metrics)) != len(normalized_required_metrics):
        raise ValueError("required_metrics must not contain duplicates")
    allowed_required_metrics = (
        set(SEMANTIC_ACCEPTANCE_METRICS)
        if candidate_evidence_family == "semantic"
        else set(DIRECT_ACCEPTANCE_METRIC_BY_FAMILY.values())
    )
    if not set(normalized_required_metrics) <= allowed_required_metrics:
        raise ValueError(
            "required_metrics are incompatible with candidate evidence family"
        )
    if (
        candidate_evidence_family != "semantic"
        and normalized_required_metrics
        != (DIRECT_ACCEPTANCE_METRIC_BY_FAMILY[candidate_evidence_family],)
    ):
        raise ValueError(
            "compile evidence must require plantuml_compilation_pass_rate"
        )
    repeat_count = len(baseline_summaries)
    invalid_reasons: list[str] = []
    if repeat_count == 0 or repeat_count != len(candidate_summaries):
        invalid_reasons.append("repeat_count_mismatch")
    prompt_size_ok = len(candidate_prompt) <= max_prompt_chars
    if not prompt_size_ok:
        invalid_reasons.append("prompt_too_long")
    def finite_metric_value(
        summary: dict[str, float], metric: str
    ) -> float | None:
        value = summary.get(metric)
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            return None
        return float(value)

    if any(
        (finite_metric_value(summary, "infrastructure_error_rate") or 0.0) > 0
        for summary in [*baseline_summaries, *candidate_summaries]
    ):
        invalid_reasons.append("infrastructure_error")

    def metric_result(*, metric: str, available: bool) -> dict[str, Any]:
        measurement_complete = bool(
            available
            and repeat_count == len(candidate_summaries)
            and all(
                finite_metric_value(summary, metric) is not None
                for summary in [*baseline_summaries, *candidate_summaries]
            )
        )
        deltas = (
            [
                float(candidate[metric]) - float(baseline[metric])
                for baseline, candidate in zip(
                    baseline_summaries, candidate_summaries
                )
            ]
            if measurement_complete
            else []
        )
        mean_delta = statistics.fmean(deltas) if deltas else None
        return {
            "available": measurement_complete,
            "repeat_deltas": deltas,
            "mean_delta": mean_delta,
            "median_delta": statistics.median(deltas) if deltas else None,
            "wins": sum(1 for delta in deltas if delta > 0.0),
            "repeat_count": repeat_count,
            "positive_mean_delta": bool(
                measurement_complete
                and mean_delta is not None
                and mean_delta > 0.0
            ),
        }

    semantic_metrics_available = bool(repeat_count) and all(
        finite_metric_value(summary, "llm_element_evaluated")
        == float(validation_case_count)
        and finite_metric_value(summary, "llm_element_failed") == 0.0
        for summary in [*baseline_summaries, *candidate_summaries]
    )
    metric_results: dict[str, dict[str, Any]] = {}
    for metric in SEMANTIC_ACCEPTANCE_METRICS:
        result = metric_result(metric=metric, available=semantic_metrics_available)
        metric_results[metric] = result

    compile_metric = "plantuml_compilation_pass_rate"
    compile_metric_available = bool(repeat_count) and all(
        finite_metric_value(summary, "count") == float(validation_case_count)
        and compile_metric in summary
        for summary in [*baseline_summaries, *candidate_summaries]
    )
    compile_result = metric_result(
        metric=compile_metric,
        available=compile_metric_available,
    )
    metric_results[compile_metric] = compile_result

    required_metric_results = {
        metric: dict(metric_results[metric])
        for metric in normalized_required_metrics
    }
    pooled_incomplete_required_metrics = [
        metric
        for metric, result in required_metric_results.items()
        if not result["available"]
    ]
    def finite_cross_dataset_delta(metric: str, key: str) -> float | None:
        aggregate = cross_dataset_metric_results.get(metric)
        value = aggregate.get(key) if isinstance(aggregate, dict) else None
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(float(value))
        ):
            return None
        return float(value)

    cross_dataset_incomplete_required_metrics: list[str] = []
    source_count_missing_metrics: list[str] = []
    for metric in normalized_required_metrics:
        aggregate = cross_dataset_metric_results.get(metric)
        if not isinstance(aggregate, dict):
            cross_dataset_incomplete_required_metrics.append(metric)
            continue
        if aggregate.get("source_dataset_count_missing"):
            source_count_missing_metrics.append(metric)
            continue
        if (
            aggregate.get("available") is not True
            or aggregate.get("missing_datasets")
            or finite_cross_dataset_delta(metric, "balanced_mean_delta") is None
            or finite_cross_dataset_delta(
                metric, "source_weighted_mean_delta"
            ) is None
        ):
            cross_dataset_incomplete_required_metrics.append(metric)

    incomplete_required_metrics = sorted(
        set(pooled_incomplete_required_metrics)
        | set(cross_dataset_incomplete_required_metrics)
    )
    if source_count_missing_metrics:
        invalid_reasons.append("source_dataset_count_missing")
    if incomplete_required_metrics:
        invalid_reasons.append("required_metric_incomplete")
    non_improving_pooled_required_metrics = [
        metric
        for metric, result in required_metric_results.items()
        if result["available"] and not result["positive_mean_delta"]
    ]
    non_improving_balanced_required_metrics = [
        metric
        for metric in normalized_required_metrics
        if isinstance(cross_dataset_metric_results.get(metric), dict)
        and cross_dataset_metric_results[metric].get("available") is True
        and finite_cross_dataset_delta(metric, "balanced_mean_delta") is not None
        and finite_cross_dataset_delta(metric, "balanced_mean_delta") <= 0.0
    ]
    non_improving_source_weighted_required_metrics = [
        metric
        for metric in normalized_required_metrics
        if isinstance(cross_dataset_metric_results.get(metric), dict)
        and cross_dataset_metric_results[metric].get("available") is True
        and finite_cross_dataset_delta(
            metric, "source_weighted_mean_delta"
        ) is not None
        and finite_cross_dataset_delta(
            metric, "source_weighted_mean_delta"
        ) <= 0.0
    ]
    non_improving_required_metrics = sorted(
        set(non_improving_pooled_required_metrics)
        | set(non_improving_balanced_required_metrics)
        | set(non_improving_source_weighted_required_metrics)
    )
    winning_metrics = [
        metric
        for metric in normalized_required_metrics
        if metric not in incomplete_required_metrics
        and metric not in source_count_missing_metrics
        and metric not in non_improving_required_metrics
    ]

    direct_metric = (
        normalized_required_metrics[0]
        if len(normalized_required_metrics) == 1
        else None
    )
    direct_metric_results = (
        {direct_metric: dict(required_metric_results[direct_metric])}
        if direct_metric is not None
        else {}
    )

    evaluation_valid = not invalid_reasons
    accepted = bool(evaluation_valid and not non_improving_required_metrics)
    rejection_reasons = list(invalid_reasons)
    if not invalid_reasons and non_improving_pooled_required_metrics:
        rejection_reasons.append("required_metric_not_improved")
    if not invalid_reasons and non_improving_balanced_required_metrics:
        rejection_reasons.append("required_metric_balanced_not_improved")
    if not invalid_reasons and non_improving_source_weighted_required_metrics:
        rejection_reasons.append(
            "required_metric_source_weighted_not_improved"
        )
    acceptance_policy = REQUIRED_METRIC_ACCEPTANCE_POLICY

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
    return accepted, {
        "accepted": accepted,
        "acceptance_mode": "positive_mean_delta" if accepted else "rejected",
        "acceptance_policy": acceptance_policy,
        "candidate_evidence_family": candidate_evidence_family,
        "required_metrics": list(normalized_required_metrics),
        "required_metric_results": required_metric_results,
        "cross_dataset_metric_results": cross_dataset_metric_results,
        "incomplete_required_metrics": incomplete_required_metrics,
        "source_count_missing_metrics": source_count_missing_metrics,
        "non_improving_pooled_required_metrics": (
            non_improving_pooled_required_metrics
        ),
        "non_improving_balanced_required_metrics": (
            non_improving_balanced_required_metrics
        ),
        "non_improving_source_weighted_required_metrics": (
            non_improving_source_weighted_required_metrics
        ),
        "non_improving_required_metrics": non_improving_required_metrics,
        "direct_metric": direct_metric,
        "direct_metric_results": direct_metric_results,
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


def selector_application_decision(
    *,
    mode: str,
    candidate_valid: bool,
    gate_evaluated: bool,
    acceptance_decision: dict[str, Any] | None,
) -> dict[str, Any]:
    decision = acceptance_decision or {}
    measurement_valid = bool(
        gate_evaluated and decision.get("evaluation_valid")
    )
    metric_decision = bool(measurement_valid and decision.get("accepted"))
    if mode == "diagnostic-apply":
        applied = bool(candidate_valid and measurement_valid)
        acceptance_mode = "diagnostic_apply"
    elif mode == "cumulative":
        applied = bool(candidate_valid and metric_decision)
        acceptance_mode = "cumulative_gate"
    elif mode == "isolated":
        applied = False
        acceptance_mode = "isolated_diagnostic"
    else:
        raise ValueError(f"Unsupported selector application mode: {mode!r}")
    return {
        "candidate_valid": bool(candidate_valid),
        "gate_evaluated": bool(gate_evaluated),
        "measurement_valid": measurement_valid,
        "applied": applied,
        # `accepted` describes the gate decision; `applied` describes the
        # selected application mode. Diagnostic apply may intentionally have
        # applied=True while accepted remains False.
        "accepted": metric_decision,
        "application_mode": mode,
        "acceptance_mode": acceptance_mode,
    }


def two_stage_gate_decision(
    *,
    gate1_decision: dict[str, Any],
    gate2_decision: dict[str, Any] | None,
    gate2_required: bool,
) -> dict[str, Any]:
    gate1_valid = bool(gate1_decision.get("evaluation_valid"))
    gate1_accepted = bool(gate1_valid and gate1_decision.get("accepted"))
    gate2_evaluated = gate2_decision is not None
    gate2_valid = bool(
        gate2_evaluated and gate2_decision.get("evaluation_valid")
    )
    gate2_accepted = bool(
        gate2_valid and gate2_decision.get("accepted")
    )

    if not gate1_accepted:
        rejection_reasons = [
            "gate1_rejected",
            *list(gate1_decision.get("rejection_reasons", [])),
        ]
    elif gate2_required and not gate2_evaluated:
        rejection_reasons = ["gate2_not_evaluated"]
    elif gate2_required and not gate2_accepted:
        rejection_reasons = [
            "gate2_rejected",
            *list((gate2_decision or {}).get("rejection_reasons", [])),
        ]
    else:
        rejection_reasons = []

    if not gate1_valid:
        invalid_reasons = [
            f"gate1:{reason}"
            for reason in gate1_decision.get("invalid_reasons", [])
        ] or ["gate1:measurement_invalid"]
    elif gate1_accepted and gate2_required and not gate2_evaluated:
        invalid_reasons = ["gate2:not_evaluated"]
    elif gate1_accepted and gate2_required and not gate2_valid:
        invalid_reasons = [
            f"gate2:{reason}"
            for reason in (gate2_decision or {}).get("invalid_reasons", [])
        ] or ["gate2:measurement_invalid"]
    else:
        invalid_reasons = []

    final_evidence = gate2_decision or gate1_decision
    accepted = bool(
        gate1_accepted
        and (not gate2_required or gate2_accepted)
    )
    evaluation_valid = bool(
        gate1_valid
        and (
            not gate1_accepted
            or not gate2_required
            or gate2_valid
        )
    )
    return {
        "schema_version": "two-stage-gate-v1",
        "acceptance_policy": REQUIRED_METRIC_ACCEPTANCE_POLICY,
        "gate_sequence_policy": gate_sequence_policy(gate2_required),
        "evaluation_valid": evaluation_valid,
        "invalid_reasons": invalid_reasons,
        "accepted": accepted,
        "gate1_accepted": gate1_accepted,
        "gate2_required": gate2_required,
        "gate2_evaluated": gate2_evaluated,
        "gate2_accepted": gate2_accepted if gate2_evaluated else None,
        "rejection_reasons": rejection_reasons,
        "candidate_evidence_family": final_evidence.get("candidate_evidence_family"),
        "required_metrics": final_evidence.get("required_metrics", []),
        "required_metric_results": final_evidence.get(
            "required_metric_results", {}
        ),
        "cross_dataset_metric_results": final_evidence.get(
            "cross_dataset_metric_results", {}
        ),
        "incomplete_required_metrics": final_evidence.get(
            "incomplete_required_metrics", []
        ),
        "non_improving_required_metrics": final_evidence.get(
            "non_improving_required_metrics", []
        ),
        "non_improving_balanced_required_metrics": final_evidence.get(
            "non_improving_balanced_required_metrics", []
        ),
        "non_improving_source_weighted_required_metrics": final_evidence.get(
            "non_improving_source_weighted_required_metrics", []
        ),
        "direct_metric": final_evidence.get("direct_metric"),
        "direct_metric_results": final_evidence.get("direct_metric_results", {}),
        "winning_metrics": final_evidence.get("winning_metrics", []),
        "metric_results": final_evidence.get("metric_results", {}),
        "per_dataset_metric_results": final_evidence.get(
            "per_dataset_metric_results", {}
        ),
        "diagnostic_repeat_deltas": final_evidence.get(
            "diagnostic_repeat_deltas", {}
        ),
        "baseline_summary": final_evidence.get("baseline_summary", {}),
        "candidate_summary": final_evidence.get("candidate_summary", {}),
        "gate1_decision": gate1_decision,
        "gate2_decision": gate2_decision,
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
    repeats_path = test_dir / "repeats.json"
    repeat_count = args.heldout_repeats
    split_fingerprint = case_split_fingerprint(test_cases)
    manifest = {
        "dataset": test_dataset,
        "iteration": iteration,
        "status": "running",
        "diagnostic_only": True,
        "repeat_count": repeat_count,
        "test_case_count": len(test_cases),
        "test_split_fingerprint": split_fingerprint,
        "inputs": {
            "prompt": "prompts/after.md",
            "cases": "../test_cases.json",
        },
        "outputs": {
            "records": "test/records.jsonl",
            "summary": "test/summary.json",
            "repeats": "test/repeats.json",
            "analysis": "test/analysis.md",
        },
    }
    write_text(test_dir / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    first_records: list[Any] = []
    repeat_summaries: list[dict[str, float]] = []
    for repeat in range(1, repeat_count + 1):
        repeat_dir = test_dir / f"repeat_{repeat:03d}"
        repeat_records_path = repeat_dir / "records.jsonl"
        records, summary = evaluate_cases(
            prompt=prompt,
            cases=test_cases,
            args=args,
            llm_client=llm_client,
            output_path=repeat_records_path,
            state_dir=run_dir,
            phase=(
                f"iteration_{iteration:03d}:held_out_test_"
                f"repeat_{repeat:03d}_of_{repeat_count:03d}"
            ),
            case_concurrency=args.heldout_test_concurrency,
        )
        if repeat == 1:
            first_records = records
        repeat_summaries.append(summary)
        write_text(
            repeat_dir / "summary.json",
            json.dumps(summary, ensure_ascii=False, indent=2),
        )
        write_text(repeat_dir / "analysis.md", build_analysis(records, summary))
        write_text(
            repeat_dir / "manifest.json",
            json.dumps(
                {
                    "dataset": test_dataset,
                    "iteration": iteration,
                    "repeat": repeat,
                    "repeat_count": repeat_count,
                    "diagnostic_only": True,
                    "test_case_count": len(test_cases),
                    "test_split_fingerprint": split_fingerprint,
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
        print(
            f"[iteration {iteration}] held-out repeat {repeat}/{repeat_count} "
            f"{format_summary(summary)}"
        )

    aggregate_summary = aggregate_repeat_summaries(repeat_summaries)
    repeats_payload = {
        "schema_version": "heldout-repeats-v1",
        "diagnostic_only": True,
        "repeat_count": repeat_count,
        "test_case_count": len(test_cases),
        "test_split_fingerprint": split_fingerprint,
        "repeat_summaries": repeat_summaries,
        "aggregate_summary": aggregate_summary,
    }
    write_evaluation_records(records_path, first_records)
    write_text(
        summary_path,
        json.dumps(aggregate_summary, ensure_ascii=False, indent=2),
    )
    write_text(repeats_path, json.dumps(repeats_payload, ensure_ascii=False, indent=2))
    if repeat_count == 1:
        top_level_analysis = build_analysis(first_records, aggregate_summary)
    else:
        repeat_lines = [
            "# Repeated Heldout Audit",
            "",
            f"- repeats: {repeat_count}",
            f"- test cases: {len(test_cases)}",
            f"- split fingerprint: `{split_fingerprint}`",
            "- diagnostic only: true",
            "",
            f"Aggregate: {format_summary(aggregate_summary)}",
            "",
            "See `repeats.json` and `repeat_NNN/` for every retained measurement.",
        ]
        top_level_analysis = "\n".join(repeat_lines).rstrip() + "\n"
    write_text(analysis_path, top_level_analysis)
    manifest["status"] = "success"
    write_text(test_dir / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    print(
        f"[iteration {iteration}] held-out aggregate repeats={repeat_count} "
        f"{format_summary(aggregate_summary)}"
    )
    return aggregate_summary


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
        outputs={
            "test_summary": "test/summary.json",
            "test_repeats": "test/repeats.json",
        },
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
        outputs={
            "test_summary": "test/summary.json",
            "test_repeats": "test/repeats.json",
        },
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


def evaluate_gate(
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
    phase_prefix: str,
    baseline_cache: dict[str, Any] | None = None,
    candidate_evidence_family: str,
    required_metrics: list[str] | tuple[str, ...],
    source_dataset_counts: dict[str, int],
    gate_name: str = "gate1",
) -> tuple[list[Any], list[Any], dict[str, float], dict[str, float], dict[str, Any]]:
    if gate_name not in {"gate1", "gate2"}:
        raise ValueError(f"Unsupported gate name: {gate_name!r}")
    gate_dir_name = gate_name
    path_prefix = "validation" if gate_name == "gate1" else "confirmation"
    baseline_cache = baseline_cache if baseline_cache is not None else {}
    write_case_manifest(paths[f"{path_prefix}_cases"], validation_cases)

    cached_records = baseline_cache.get("repeat_records")
    cached_summaries = baseline_cache.get("repeat_summaries")
    reuse_baseline = bool(
        isinstance(cached_records, list)
        and isinstance(cached_summaries, list)
        and len(cached_records) == args.validation_repeats
        and len(cached_summaries) == args.validation_repeats
    )
    baseline_repeat_records: list[list[Any]] = (
        list(cached_records) if reuse_baseline else []
    )
    baseline_repeat_summaries: list[dict[str, float]] = (
        list(cached_summaries) if reuse_baseline else []
    )
    candidate_repeat_summaries: list[dict[str, float]] = []
    first_baseline_records: list[Any] = []
    first_candidate_records: list[Any] = []
    repeat_pairs: list[tuple[int, list[Any], list[Any]]] = []

    def evaluate_repeat(prompt: str, *, repeat: int, role: str) -> tuple[list[Any], dict[str, float]]:
        role_dir = iter_dir / gate_dir_name / f"repeat_{repeat:03d}" / role
        records, summary = evaluate_cases(
            prompt=prompt,
            cases=validation_cases,
            args=args,
            llm_client=llm_client,
            output_path=role_dir / "records.jsonl",
            state_dir=run_dir,
            phase=f"{phase_prefix}:{gate_name}_repeat_{repeat:03d}:{role}",
            case_concurrency=args.gate_concurrency,
        )
        write_text(role_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
        return records, summary

    for repeat in range(1, args.validation_repeats + 1):
        if reuse_baseline:
            baseline_records = baseline_repeat_records[repeat - 1]
            baseline_summary = baseline_repeat_summaries[repeat - 1]
            baseline_dir = iter_dir / gate_dir_name / f"repeat_{repeat:03d}" / "baseline"
            write_evaluation_records(baseline_dir / "records.jsonl", baseline_records)
            write_text(
                baseline_dir / "summary.json",
                json.dumps(baseline_summary, ensure_ascii=False, indent=2),
            )
            candidate_records, candidate_summary = evaluate_repeat(
                candidate_prompt, repeat=repeat, role="candidate"
            )
        elif repeat % 2 == 1:
            baseline_records, baseline_summary = evaluate_repeat(baseline_prompt, repeat=repeat, role="baseline")
            candidate_records, candidate_summary = evaluate_repeat(candidate_prompt, repeat=repeat, role="candidate")
        else:
            candidate_records, candidate_summary = evaluate_repeat(candidate_prompt, repeat=repeat, role="candidate")
            baseline_records, baseline_summary = evaluate_repeat(baseline_prompt, repeat=repeat, role="baseline")
        if not reuse_baseline:
            baseline_repeat_records.append(baseline_records)
            baseline_repeat_summaries.append(baseline_summary)
        if repeat == 1:
            first_baseline_records = baseline_records
            first_candidate_records = candidate_records
        repeat_pairs.append((repeat, baseline_records, candidate_records))
        candidate_repeat_summaries.append(candidate_summary)

    if not reuse_baseline:
        baseline_cache["repeat_records"] = baseline_repeat_records
        baseline_cache["repeat_summaries"] = baseline_repeat_summaries

    baseline_summary = aggregate_repeat_summaries(baseline_repeat_summaries)
    candidate_summary = aggregate_repeat_summaries(candidate_repeat_summaries)
    write_text(paths[f"{path_prefix}_baseline_summary"], json.dumps(baseline_summary, ensure_ascii=False, indent=2))
    write_text(paths[f"{path_prefix}_candidate_summary"], json.dumps(candidate_summary, ensure_ascii=False, indent=2))
    write_evaluation_records(paths[f"{path_prefix}_baseline_records"], first_baseline_records)
    write_evaluation_records(paths[f"{path_prefix}_candidate_records"], first_candidate_records)
    per_dataset_results = per_dataset_metric_decomposition(repeat_pairs)
    cross_dataset_metric_results = aggregate_source_dataset_metrics(
        per_dataset_results=per_dataset_results,
        source_dataset_counts=source_dataset_counts,
        metrics=required_metrics,
    )
    accepted, decision = any_improvement_decision(
        baseline_summaries=baseline_repeat_summaries,
        candidate_summaries=candidate_repeat_summaries,
        validation_case_count=len(validation_cases),
        candidate_prompt=candidate_prompt,
        baseline_prompt=baseline_prompt,
        max_prompt_chars=args.max_prompt_chars,
        candidate_evidence_family=candidate_evidence_family,
        required_metrics=required_metrics,
        cross_dataset_metric_results=cross_dataset_metric_results,
    )
    aggregate_payload = {
        "baseline_summary": baseline_summary,
        "candidate_summary": candidate_summary,
        "per_dataset_metric_results": per_dataset_results,
        "baseline_repeat_summaries": baseline_repeat_summaries,
        "candidate_repeat_summaries": candidate_repeat_summaries,
        "metric_results": decision["metric_results"],
        "accepted": decision["accepted"],
        "evaluation_valid": decision["evaluation_valid"],
        "invalid_reasons": decision["invalid_reasons"],
        "rejection_reasons": decision["rejection_reasons"],
        "candidate_evidence_family": decision["candidate_evidence_family"],
        "required_metrics": decision["required_metrics"],
        "required_metric_results": decision["required_metric_results"],
        "cross_dataset_metric_results": decision[
            "cross_dataset_metric_results"
        ],
        "incomplete_required_metrics": decision["incomplete_required_metrics"],
        "non_improving_required_metrics": decision[
            "non_improving_required_metrics"
        ],
        "non_improving_balanced_required_metrics": decision[
            "non_improving_balanced_required_metrics"
        ],
        "non_improving_source_weighted_required_metrics": decision[
            "non_improving_source_weighted_required_metrics"
        ],
        "direct_metric": decision["direct_metric"],
        "direct_metric_results": decision["direct_metric_results"],
        "diagnostic_repeat_deltas": decision["diagnostic_repeat_deltas"],
        "winning_metrics": decision["winning_metrics"],
        "gate_case_count": len(validation_cases),
        f"{gate_name}_case_count": len(validation_cases),
        f"{gate_name}_split_fingerprint": case_split_fingerprint(validation_cases),
    }
    aggregate_payload["gate_name"] = gate_name
    write_text(paths[f"{path_prefix}_aggregate_summary"], json.dumps(aggregate_payload, ensure_ascii=False, indent=2))
    write_text(
        paths[f"{path_prefix}_analysis"],
        f"# Repeated {gate_name.title()} Evaluation\n\n"
        f"- repeats: {args.validation_repeats}\n"
        f"- candidate evidence family: {decision['candidate_evidence_family']}\n"
        f"- required metrics: {', '.join(decision['required_metrics'])}\n"
        f"- direct metric: {decision['direct_metric'] or 'none'}\n"
        f"- winning metrics: {', '.join(decision['winning_metrics']) or 'none'}\n"
        f"- balanced/source-weighted required metrics: "
        f"{json.dumps(decision['cross_dataset_metric_results'], ensure_ascii=False)}\n"
        f"- rejection reasons: {', '.join(decision['rejection_reasons']) or 'none'}\n"
        f"- accepted: {str(accepted).lower()}\n\n"
        "See `aggregate_summary.json` for paired repeat deltas and diagnostic metrics.\n",
    )
    impact_summary = build_validation_impact_summary(repeat_pairs)
    write_validation_impact_report(
        summary=impact_summary,
        json_path=paths[f"{path_prefix}_impact_summary"],
        report_path=paths[f"{path_prefix}_impact_report"],
    )
    decision["accepted"] = accepted
    decision["per_dataset_metric_results"] = per_dataset_results
    decision["gate_name"] = gate_name
    decision["evaluation_source"] = gate_name
    decision[f"{gate_name}_case_count"] = len(validation_cases)
    decision[f"{gate_name}_split_fingerprint"] = case_split_fingerprint(validation_cases)
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


def selected_group_finding_keys(group: dict[str, Any]) -> list[str]:
    return sorted(
        {
            str(member.get("finding_key") or "").strip()
            for member in group.get("members", [])
            if isinstance(member, dict)
            and str(member.get("finding_key") or "").strip()
        }
    )


def candidate_attempt_outcome(attempt_acceptance: dict[str, Any]) -> str:
    if attempt_acceptance.get("applied"):
        return "applied"
    if attempt_acceptance.get("accepted"):
        return "accepted"
    rejection_reasons = [
        str(reason)
        for reason in attempt_acceptance.get("rejection_reasons", [])
        if str(reason)
    ]
    if rejection_reasons:
        return rejection_reasons[0]
    if attempt_acceptance.get("gate_evaluated"):
        return "gate_evaluated"
    if attempt_acceptance.get("candidate_generated"):
        return str(attempt_acceptance.get("candidate_status") or "candidate_generated")
    return "not_generated"


def filter_candidate_groups_by_attempt_history(
    candidate_groups: list[dict[str, Any]],
    *,
    registry: dict[str, Any],
    base_prompt_hash: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    eligible: list[dict[str, Any]] = []
    filtered: list[dict[str, Any]] = []
    for group in candidate_groups:
        finding_keys = selected_group_finding_keys(group)
        history = group_attempt_history(
            registry,
            base_prompt_hash=base_prompt_hash,
            finding_keys=finding_keys,
        )
        prior_terminal_outcomes = sorted(
            {
                str(item.get("outcome") or "")
                for item in history
                if item.get("outcome") in {"no_prompt_gap", "group_incoherent"}
            }
        )
        if prior_terminal_outcomes:
            filtered.append(
                {
                    "group_id": str(group.get("group_id") or ""),
                    "group_signature": group_attempt_signature(
                        base_prompt_hash=base_prompt_hash,
                        finding_keys=finding_keys,
                    ),
                    "finding_keys": finding_keys,
                    "prior_attempt_count": len(history),
                    "prior_terminal_outcomes": prior_terminal_outcomes,
                    "reason": "prior_terminal_localization_same_prompt_and_findings",
                }
            )
            continue
        eligible.append(group)
    return eligible, filtered


def exact_already_covered_recurrence(
    prior_group_attempts: list[dict[str, Any]],
) -> dict[str, Any] | None:
    prior_already_covered = [
        item
        for item in prior_group_attempts
        if item.get("outcome") == "already_covered"
    ]
    if not prior_already_covered:
        return None
    return {
        "match_basis": "same_base_prompt_and_exact_finding_keys",
        "same_prompt_occurrences": len(prior_group_attempts) + 1,
        "prior_already_covered_count": len(prior_already_covered),
        "previous_outcomes": [
            str(item.get("outcome") or "") for item in prior_group_attempts
        ],
    }


def run_training_iterations(
    *,
    args: argparse.Namespace,
    llm_client: LLMClient,
    train_cases: list[Case],
    source_dataset_counts: dict[str, int],
    run_dir: Path,
    work_prompt_path: Path,
    label: str,
    validation_cases: list[Case] | None = None,
    confirmation_cases: list[Case] | None = None,
    test_cases: list[Case] | None = None,
    test_dataset: str | None = None,
    initial_test_summary: dict[str, float] | None = None,
) -> tuple[str, dict[str, float]]:
    """Run the selector-v4 bounded-attempt no-taxonomy workflow."""

    validation_cases = list(validation_cases or [])
    confirmation_cases = list(confirmation_cases or [])
    if not args.no_evolve and not validation_cases:
        raise ValueError("taxonomy-v3 selector workflow requires a non-empty Gate1 split")
    if not args.no_evolve and args.gate2 and not confirmation_cases:
        raise ValueError("selector workflow requires a non-empty Gate2 split")
    prompt = read_text(work_prompt_path)
    registry_path = run_dir / "candidate_registry.json"
    registry = load_candidate_registry(registry_path)
    save_candidate_registry(registry_path, registry)
    last_summary: dict[str, float] = {}
    last_test_summary = initial_test_summary
    global_update_step = 0

    print(f"[run] {label}, policy=taxonomy-v3 selector-v4-bounded-attempts, train_cases={len(train_cases)}")
    print(f"[run] train distribution: {describe_case_distribution(train_cases)}")
    print(f"[run] gate1 cases={len(validation_cases)}")
    print(
        f"[run] gate_policy={gate_sequence_policy(bool(args.gate2))}, "
        f"gate2_enabled={bool(args.gate2)}, gate2_cases={len(confirmation_cases)}"
    )
    print(
        "[run] stop_after_first_apply="
        f"{bool(getattr(args, 'stop_after_first_apply', False))}"
    )
    print(f"[run] heldout_repeats={args.heldout_repeats}")
    print(f"[run] output={run_dir}")

    for iteration in range(1, args.iterations + 1):
        iter_dir = run_dir / f"iteration_{iteration:03d}"
        paths = iteration_paths(iter_dir)
        manifest = make_iteration_manifest(iter_dir, iteration, paths)
        manifest.update(
            {
                "mode": "taxonomy-v3-selector-v4-bounded-attempts",
                "candidate_application_mode": args.candidate_application_mode,
                "gate_sequence_policy": gate_sequence_policy(bool(args.gate2)),
                "candidate_registry": "../candidate_registry.json",
                "taxonomy_mapping": "disabled",
                "gate1_split": {
                    "requested_case_count": args.gate1_size,
                    "actual_case_count": len(validation_cases),
                    "fingerprint": case_split_fingerprint(validation_cases),
                },
                "gate2_split": {
                    "enabled": bool(args.gate2),
                    "requested_case_count": args.gate2_size,
                    "actual_case_count": len(confirmation_cases),
                    "fingerprint": case_split_fingerprint(confirmation_cases),
                },
            }
        )
        prompt_before = prompt
        base_prompt_hash = prompt_fingerprint(prompt)
        write_text(paths["prompt_before"], prompt)
        write_case_manifest(paths["analysis_cases"], train_cases)
        write_case_manifest(paths["validation_cases"], validation_cases)
        if confirmation_cases:
            write_case_manifest(paths["confirmation_cases"], confirmation_cases)
        batches = split_training_batches(
            train_cases,
            args.analysis_batch_size,
            strategy=args.training_batch_strategy,
        )
        manifest["train_batch_count"] = len(batches)
        manifest["train_batch_strategy"] = args.training_batch_strategy
        manifest["epoch_batch_concurrency"] = min(
            args.epoch_batch_concurrency, len(batches)
        ) if batches else 1
        write_iteration_manifest(iter_dir, manifest)
        print(f"\n[iteration {iteration}] selector-v4 analysis with {len(batches)} batch(es)")

        jobs = [
            {
                "batch_index": index,
                "analysis_cases": cases,
                "global_update_step": global_update_step + index,
            }
            for index, cases in enumerate(batches, start=1)
        ]
        batch_results: list[EpochBatchResult] = []
        concurrency = min(args.epoch_batch_concurrency, len(jobs)) if jobs else 1
        if concurrency <= 1:
            for job in jobs:
                batch_results.append(
                    process_epoch_batch(
                        args=args,
                        llm_client=llm_client,
                        run_dir=run_dir,
                        iter_dir=iter_dir,
                        iteration=iteration,
                        batch_index=job["batch_index"],
                        batch_count=len(batches),
                        global_update_step=job["global_update_step"],
                        prompt=prompt,
                        analysis_cases=job["analysis_cases"],
                    )
                )
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                futures = [
                    executor.submit(
                        process_epoch_batch,
                        args=args,
                        llm_client=llm_client,
                        run_dir=run_dir,
                        iter_dir=iter_dir,
                        iteration=iteration,
                        batch_index=job["batch_index"],
                        batch_count=len(batches),
                        global_update_step=job["global_update_step"],
                        prompt=prompt,
                        analysis_cases=job["analysis_cases"],
                    )
                    for job in jobs
                ]
                batch_results = [
                    future.result()
                    for future in concurrent.futures.as_completed(futures)
                ]
        global_update_step += len(batches)
        batch_results.sort(key=lambda item: item.batch_index)
        records = [record for result in batch_results for record in result.records]
        all_errors = [
            item
            for result in batch_results
            for item in result.error_observations
            if isinstance(item, dict)
        ]
        actionable_errors = [item for item in all_errors if item.get("status") == "actionable"]
        epoch_summary = summarize_records(records)
        last_summary = epoch_summary
        write_evaluation_records(paths["analysis_records"], records)
        write_text(paths["analysis_summary"], json.dumps(epoch_summary, ensure_ascii=False, indent=2))
        write_text(paths["analysis_overview"], build_analysis(records, epoch_summary))
        write_text(
            paths["mechanism_evidence_inventory"],
            json.dumps(all_errors, ensure_ascii=False, indent=2),
        )
        record_stage(
            manifest,
            "failure_error_collection",
            status="success" if actionable_errors else "skipped",
            outputs={"inventory": rel_to_iter(iter_dir, paths["mechanism_evidence_inventory"])},
            note=f"valid_errors={len(all_errors)}, actionable_errors={len(actionable_errors)}",
        )

        candidate_prompt: str | None = None
        baseline_gate_summary: dict[str, float] | None = None
        candidate_summary: dict[str, float] | None = None
        selected_group: dict[str, Any] | None = None
        localization: dict[str, Any] | None = None
        editor_plan: dict[str, Any] | None = None
        revision_plan: dict[str, Any] | None = None
        acceptance_decision: dict[str, Any] | None = None
        attempt_payloads: list[dict[str, Any]] = []
        attempt_lineage: list[dict[str, Any]] = []
        validation_baseline_cache: dict[str, Any] = {}
        applied_attempt: int | None = None
        acceptance: dict[str, Any] = {
            "pipeline_policy": "taxonomy-v3",
            "schema_version": "selector-v4-bounded-attempts",
            "application_mode": args.candidate_application_mode,
            "acceptance_policy": REQUIRED_METRIC_ACCEPTANCE_POLICY,
            "gate_sequence_policy": gate_sequence_policy(bool(args.gate2)),
            "acceptance_mode": (
                "diagnostic_apply"
                if args.candidate_application_mode == "diagnostic-apply"
                else "cumulative_gate"
                if args.candidate_application_mode == "cumulative"
                else "isolated_diagnostic"
            ),
            "candidate_generated": False,
            "candidate_status": "not_generated",
            "candidate_valid": False,
            "candidate_evidence_family": None,
            "required_metrics": [],
            "required_metric_results": {},
            "incomplete_required_metrics": [],
            "non_improving_required_metrics": [],
            "direct_metric": None,
            "direct_metric_results": {},
            "gate1_evaluated": False,
            "gate1_decision": None,
            "gate2_evaluated": False,
            "gate2_decision": None,
            "gate_evaluated": False,
            "applied": False,
            "accepted": False,
            "rejection_reasons": [],
            "valid_error_count": len(all_errors),
            "actionable_error_count": len(actionable_errors),
            "max_candidate_attempts": args.max_candidate_attempts_per_epoch,
            "attempt_count": 0,
            "applied_attempt": None,
        }

        selector_result: dict[str, Any] | None = None
        candidate_groups: list[dict[str, Any]] = []
        if args.no_evolve:
            acceptance["rejection_reasons"] = ["no_evolve"]
        elif not actionable_errors:
            acceptance["rejection_reasons"] = ["no_actionable_errors"]
        else:
            selector_result = select_error_group(
                errors=all_errors,
                args=args,
                llm_client=llm_client,
                output_input_path=paths["error_selector_input"],
                output_path=paths["error_selector_output"],
                state_dir=run_dir,
                iteration=iteration,
            )
            record_stage(
                manifest,
                "error_selector",
                status=(
                    "success"
                    if selector_result and selector_result.get("selection_status") == "selected"
                    else "skipped"
                    if selector_result
                    else "invalid"
                ),
                inputs={"errors": rel_to_iter(iter_dir, paths["error_selector_input"])},
                outputs={"groups": rel_to_iter(iter_dir, paths["error_selector_output"])},
                note=(
                    f"selection_status={selector_result.get('selection_status')}"
                    if selector_result
                    else "selector_output_invalid"
                ),
            )
            if selector_result is None:
                acceptance["rejection_reasons"] = ["selector_invalid"]
            elif selector_result.get("selection_status") == "abstain":
                acceptance["rejection_reasons"] = ["selector_abstained"]
            else:
                candidate_groups = [
                    dict(group)
                    for group in selector_result.get("error_groups", [])
                    if isinstance(group, dict)
                ]
                if not candidate_groups and isinstance(selector_result.get("selected_group"), dict):
                    candidate_groups = [dict(selector_result["selected_group"])]

        available_group_count = len(candidate_groups)
        eligible_candidate_groups, filtered_candidate_groups = (
            filter_candidate_groups_by_attempt_history(
                candidate_groups,
                registry=registry,
                base_prompt_hash=base_prompt_hash,
            )
        )
        eligible_group_count = len(eligible_candidate_groups)
        candidate_groups = eligible_candidate_groups[
            : args.max_candidate_attempts_per_epoch
        ]
        manifest["max_candidate_attempts_per_epoch"] = args.max_candidate_attempts_per_epoch
        manifest["selector_group_count"] = available_group_count
        manifest["eligible_candidate_group_count"] = eligible_group_count
        manifest["candidate_group_count"] = len(candidate_groups)
        manifest["filtered_candidate_groups"] = filtered_candidate_groups
        if (
            filtered_candidate_groups
            and not candidate_groups
            and not acceptance["rejection_reasons"]
        ):
            acceptance["rejection_reasons"] = [
                "prior_terminal_localization_groups_filtered"
            ]

        for attempt_index, group in enumerate(candidate_groups, start=1):
            attempt_dir = iter_dir / "candidate_attempts" / f"attempt_{attempt_index:03d}"
            attempt_paths = iteration_paths(attempt_dir)
            write_text(attempt_paths["prompt_before"], prompt_before)
            write_case_manifest(attempt_paths["validation_cases"], validation_cases)
            if confirmation_cases:
                write_case_manifest(attempt_paths["confirmation_cases"], confirmation_cases)

            selected_group = dict(group)
            selected_group["representative_errors"] = representative_errors(selected_group)
            candidate_evidence_family: str | None = None
            candidate_required_metrics: tuple[str, ...] | None = None
            finding_keys = selected_group_finding_keys(selected_group)
            prior_group_attempts = group_attempt_history(
                registry,
                base_prompt_hash=base_prompt_hash,
                finding_keys=finding_keys,
            )
            recurrence = exact_already_covered_recurrence(
                prior_group_attempts
            )
            write_text(
                attempt_paths["selected_error_group"],
                json.dumps(selected_group, ensure_ascii=False, indent=2),
            )
            write_text(
                paths["selected_error_group"],
                json.dumps(selected_group, ensure_ascii=False, indent=2),
            )
            attempt_acceptance: dict[str, Any] = {
                "schema_version": "candidate-attempt-v1",
                "attempt": attempt_index,
                "group_id": str(selected_group.get("group_id") or ""),
                "candidate_generated": False,
                "candidate_status": "not_generated",
                "candidate_valid": False,
                "candidate_evidence_family": None,
                "acceptance_policy": REQUIRED_METRIC_ACCEPTANCE_POLICY,
                "gate_sequence_policy": gate_sequence_policy(bool(args.gate2)),
                "required_metrics": [],
                "required_metric_results": {},
                "incomplete_required_metrics": [],
                "non_improving_required_metrics": [],
                "direct_metric": None,
                "direct_metric_results": {},
                "gate1_evaluated": False,
                "gate1_decision": None,
                "gate2_evaluated": False,
                "gate2_decision": None,
                "gate_evaluated": False,
                "applied": False,
                "accepted": False,
                "rejection_reasons": [],
            }
            localization = None
            editor_plan = None
            revision_plan = None
            attempt_candidate_prompt: str | None = None

            group_eligibility_errors = validate_selected_group_eligibility(selected_group)
            if group_eligibility_errors:
                attempt_acceptance["rejection_reasons"] = ["selected_group_ineligible"]
                attempt_acceptance["selected_group_eligibility_errors"] = group_eligibility_errors
            else:
                candidate_evidence_family = selected_group_evidence_family(
                    selected_group
                )
                candidate_required_metrics = selected_group_required_metrics(
                    selected_group
                )
                attempt_acceptance["candidate_evidence_family"] = candidate_evidence_family
                attempt_acceptance["required_metrics"] = list(
                    candidate_required_metrics
                )
                attempt_acceptance["direct_metric"] = (
                    candidate_required_metrics[0]
                    if len(candidate_required_metrics) == 1
                    else None
                )
                localization = localize_selector_group(
                    current_prompt=prompt_before,
                    selected_group=selected_group,
                    args=args,
                    llm_client=llm_client,
                    output_input_path=attempt_paths["error_localization_input"],
                    output_path=attempt_paths["error_localization_output"],
                    state_dir=run_dir,
                    iteration=iteration,
                    recurrence=recurrence,
                )
                if localization is None:
                    attempt_acceptance["rejection_reasons"] = ["localization_invalid"]
                elif localization.get("group_consistency") == "incoherent":
                    attempt_acceptance["candidate_status"] = "group_incoherent"
                    attempt_acceptance["rejection_reasons"] = ["group_incoherent"]
                elif localization["localization_status"] == "no_prompt_gap":
                    attempt_acceptance["rejection_reasons"] = ["no_prompt_gap"]
                elif localization["localization_status"] == "already_covered":
                    attempt_acceptance["rejection_reasons"] = ["already_covered"]
                else:
                    editor_plan = propose_selector_edit(
                        current_prompt=prompt_before,
                        selected_group=selected_group,
                        localization=localization,
                        args=args,
                        llm_client=llm_client,
                        output_input_path=attempt_paths["prompt_editor_input"],
                        output_path=attempt_paths["prompt_editor_output"],
                        state_dir=run_dir,
                        iteration=iteration,
                    )
                    if editor_plan is None:
                        attempt_acceptance["candidate_status"] = "invalid"
                        attempt_acceptance["rejection_reasons"] = ["prompt_editor_invalid"]
                    else:
                        revision_plan = build_rewriter_plan(
                            localization=localization,
                            editor_plan=editor_plan,
                        )
                        attempt_candidate_prompt = rewrite_prompt(
                            current_prompt=prompt_before,
                            revision_plan=revision_plan,
                            args=args,
                            llm_client=llm_client,
                            output_input_path=attempt_paths["prompt_rewriter_input"],
                            output_path=attempt_paths["prompt_rewriter_output"],
                            state_dir=run_dir,
                            iteration=iteration,
                        )
                        attempt_acceptance["candidate_generated"] = attempt_candidate_prompt is not None
                        attempt_acceptance["candidate_valid"] = attempt_candidate_prompt is not None
                        attempt_acceptance["candidate_status"] = (
                            "valid" if attempt_candidate_prompt is not None else "invalid"
                        )
                        if attempt_candidate_prompt is None:
                            attempt_acceptance["rejection_reasons"] = ["prompt_rewriter_invalid"]
                        else:
                            candidate_prompt = attempt_candidate_prompt
                            write_text(attempt_paths["prompt_candidate"], attempt_candidate_prompt)
                            write_text(paths["prompt_candidate"], attempt_candidate_prompt)

            if attempt_candidate_prompt is not None:
                if candidate_evidence_family is None or not candidate_required_metrics:
                    raise RuntimeError(
                        "Valid candidate is missing evidence-bound required metrics"
                    )
                rewriter_payload = extract_json_object(
                    read_text(attempt_paths["prompt_rewriter_output"])
                ) or {}
                rule_text = str(rewriter_payload.get("rule_text") or "")
                group_id = str(selected_group.get("group_id") or "")
                rule_hash = hashlib.sha256(rule_text.encode("utf-8")).hexdigest()
                candidate_id = "cand_" + hashlib.sha256(
                    f"{base_prompt_hash}\n{group_id}\n{rule_hash}".encode("utf-8")
                ).hexdigest()[:20]
                attempt_acceptance["candidate_id"] = candidate_id
                duplicate = candidate_id in evaluated_candidate_ids(
                    registry, base_prompt_hash=base_prompt_hash
                )
                if duplicate:
                    attempt_acceptance["rejection_reasons"] = [
                        "candidate_already_evaluated_for_prompt"
                    ]
                else:
                    (
                        _baseline_records,
                        _candidate_records,
                        baseline_gate_summary,
                        candidate_summary,
                        gate1_decision,
                    ) = evaluate_gate(
                        baseline_prompt=prompt_before,
                        candidate_prompt=attempt_candidate_prompt,
                        validation_cases=validation_cases,
                        args=args,
                        llm_client=llm_client,
                        run_dir=run_dir,
                        iter_dir=attempt_dir,
                        paths=attempt_paths,
                        iteration=iteration,
                        phase_prefix=(
                            f"iteration_{iteration:03d}:selector:attempt_{attempt_index:03d}"
                        ),
                        baseline_cache=validation_baseline_cache,
                        candidate_evidence_family=candidate_evidence_family,
                        required_metrics=candidate_required_metrics,
                        source_dataset_counts=source_dataset_counts,
                        gate_name="gate1",
                    )
                    gate2_decision = None
                    if (
                        args.gate2
                        and gate1_decision.get("evaluation_valid")
                        and gate1_decision.get("accepted")
                    ):
                        (
                            _confirmation_baseline_records,
                            _confirmation_candidate_records,
                            _confirmation_baseline_summary,
                            _confirmation_candidate_summary,
                            gate2_decision,
                        ) = evaluate_gate(
                            baseline_prompt=prompt_before,
                            candidate_prompt=attempt_candidate_prompt,
                            validation_cases=confirmation_cases,
                            args=args,
                            llm_client=llm_client,
                            run_dir=run_dir,
                            iter_dir=attempt_dir,
                            paths=attempt_paths,
                            iteration=iteration,
                            phase_prefix=(
                                f"iteration_{iteration:03d}:selector:attempt_{attempt_index:03d}"
                            ),
                            baseline_cache=None,
                            candidate_evidence_family=candidate_evidence_family,
                            required_metrics=candidate_required_metrics,
                            source_dataset_counts=source_dataset_counts,
                            gate_name="gate2",
                        )
                    acceptance_decision = two_stage_gate_decision(
                        gate1_decision=gate1_decision,
                        gate2_decision=gate2_decision,
                        gate2_required=bool(args.gate2),
                    )
                    application = selector_application_decision(
                        mode=args.candidate_application_mode,
                        candidate_valid=True,
                        gate_evaluated=True,
                        acceptance_decision=acceptance_decision,
                    )
                    gate_decision = application["accepted"]
                    threshold_rejection_reasons = list(
                        acceptance_decision.get("rejection_reasons", [])
                    )
                    attempt_acceptance.update(
                        {
                            **application,
                            "acceptance_decision": acceptance_decision,
                            "gate1_evaluated": True,
                            "gate1_decision": gate1_decision,
                            "gate2_evaluated": gate2_decision is not None,
                            "gate2_decision": gate2_decision,
                            "candidate_evidence_family": acceptance_decision.get(
                                "candidate_evidence_family",
                                candidate_evidence_family,
                            ),
                            "acceptance_policy": acceptance_decision.get(
                                "acceptance_policy",
                                REQUIRED_METRIC_ACCEPTANCE_POLICY,
                            ),
                            "gate_sequence_policy": acceptance_decision.get(
                                "gate_sequence_policy",
                                gate_sequence_policy(bool(args.gate2)),
                            ),
                            "required_metrics": acceptance_decision.get(
                                "required_metrics", list(candidate_required_metrics)
                            ),
                            "required_metric_results": acceptance_decision.get(
                                "required_metric_results", {}
                            ),
                            "incomplete_required_metrics": acceptance_decision.get(
                                "incomplete_required_metrics", []
                            ),
                            "non_improving_required_metrics": acceptance_decision.get(
                                "non_improving_required_metrics", []
                            ),
                            "direct_metric": acceptance_decision.get(
                                "direct_metric",
                                candidate_required_metrics[0]
                                if len(candidate_required_metrics) == 1
                                else None,
                            ),
                            "direct_metric_results": acceptance_decision.get(
                                "direct_metric_results", {}
                            ),
                            "rejection_reasons": (
                                []
                                if gate_decision
                                or args.candidate_application_mode == "isolated"
                                else [
                                    "gate1_rejected_diagnostic_apply",
                                    *threshold_rejection_reasons,
                                ]
                                if application["applied"]
                                and args.candidate_application_mode == "diagnostic-apply"
                                else threshold_rejection_reasons
                                or ["gate1_rejected"]
                            ),
                        }
                    )
                    selected_for_registry = {
                        "candidate_id": candidate_id,
                        "group_id": group_id,
                        "finding_ids": list(selected_group.get("finding_ids", [])),
                        "finding_keys": [
                            str(item.get("finding_key") or "")
                            for item in selected_group.get("members", [])
                            if isinstance(item, dict)
                            and str(item.get("finding_key") or "")
                        ],
                        "positive_trigger": revision_plan["revision_plan"][0][
                            "positive_trigger"
                        ],
                        "negative_boundary": revision_plan["revision_plan"][0][
                            "negative_boundary"
                        ],
                        "candidate_evidence_family": candidate_evidence_family,
                        "acceptance_policy": acceptance_decision.get(
                            "acceptance_policy", REQUIRED_METRIC_ACCEPTANCE_POLICY
                        ),
                        "gate_sequence_policy": acceptance_decision.get(
                            "gate_sequence_policy",
                            gate_sequence_policy(bool(args.gate2)),
                        ),
                        "required_metrics": list(candidate_required_metrics),
                        "required_metric_results": acceptance_decision.get(
                            "required_metric_results", {}
                        ),
                        "incomplete_required_metrics": acceptance_decision.get(
                            "incomplete_required_metrics", []
                        ),
                        "non_improving_required_metrics": acceptance_decision.get(
                            "non_improving_required_metrics", []
                        ),
                        "direct_metric": acceptance_decision.get(
                            "direct_metric",
                            candidate_required_metrics[0]
                            if len(candidate_required_metrics) == 1
                            else None,
                        ),
                        "direct_metric_results": acceptance_decision.get(
                            "direct_metric_results", {}
                        ),
                    }
                    write_text(
                        attempt_paths["acceptance"],
                        json.dumps(attempt_acceptance, ensure_ascii=False, indent=2),
                    )
                    record_evaluated_candidate(
                        registry,
                        iteration=iteration,
                        base_prompt_hash=base_prompt_hash,
                        candidate_prompt=attempt_candidate_prompt,
                        rule_text=rule_text,
                        candidate_metadata=selected_for_registry,
                        validation_diagnostics=attempt_acceptance,
                        artifact_paths={
                            "candidate_prompt": str(
                                attempt_paths["prompt_candidate"].relative_to(run_dir)
                            ).replace("\\", "/"),
                            "acceptance": str(
                                attempt_paths["acceptance"].relative_to(run_dir)
                            ).replace("\\", "/"),
                            "impact_summary": str(
                                attempt_paths["validation_impact_summary"].relative_to(run_dir)
                            ).replace("\\", "/"),
                            **(
                                {
                                    "gate2_impact_summary": str(
                                        attempt_paths["confirmation_impact_summary"].relative_to(run_dir)
                                    ).replace("\\", "/")
                                }
                                if gate2_decision is not None
                                else {}
                            ),
                        },
                    )
                    save_candidate_registry(registry_path, registry)
                    if application["applied"]:
                        prompt = attempt_candidate_prompt
                        applied_attempt = attempt_index
                        write_text(work_prompt_path, prompt)

            write_text(attempt_paths["prompt_after"], prompt if attempt_acceptance["applied"] else prompt_before)
            write_text(
                attempt_paths["acceptance"],
                json.dumps(attempt_acceptance, ensure_ascii=False, indent=2),
            )
            write_text(
                attempt_paths["mechanism_lineage"],
                json.dumps(
                    {
                        "schema_version": "selector-attempt-lineage-v1",
                        "attempt": attempt_index,
                        "selected_group_id": selected_group.get("group_id"),
                        "localization": localization,
                        "editor_plan": editor_plan,
                        "revision_plan": revision_plan,
                        "acceptance": attempt_acceptance,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            )
            record_group_attempt(
                registry,
                iteration=iteration,
                attempt=attempt_index,
                base_prompt_hash=base_prompt_hash,
                group_id=str(selected_group.get("group_id") or ""),
                finding_keys=finding_keys,
                outcome=candidate_attempt_outcome(attempt_acceptance),
                rejection_reasons=list(
                    attempt_acceptance.get("rejection_reasons", [])
                ),
                candidate_id=str(attempt_acceptance.get("candidate_id") or ""),
            )
            save_candidate_registry(registry_path, registry)
            attempt_payloads.append(attempt_acceptance)
            attempt_lineage.append(
                {
                    "attempt": attempt_index,
                    "group_id": selected_group.get("group_id"),
                    "localization": localization,
                    "editor_plan": editor_plan,
                    "revision_plan": revision_plan,
                    "acceptance": attempt_acceptance,
                }
            )
            if attempt_acceptance["applied"]:
                break

        if attempt_payloads:
            applied_payload = next(
                (item for item in attempt_payloads if item.get("applied")), None
            )
            final_attempt = applied_payload or next(
                (
                    item
                    for item in reversed(attempt_payloads)
                    if item.get("gate_evaluated")
                ),
                attempt_payloads[-1],
            )
            acceptance.update(
                {
                    "candidate_generated": any(
                        item.get("candidate_generated") for item in attempt_payloads
                    ),
                    "candidate_valid": any(
                        item.get("candidate_valid") for item in attempt_payloads
                    ),
                    "candidate_status": (
                        "valid"
                        if any(item.get("candidate_valid") for item in attempt_payloads)
                        else "invalid"
                        if any(item.get("candidate_status") == "invalid" for item in attempt_payloads)
                        else "not_generated"
                    ),
                    "gate_evaluated": any(
                        item.get("gate_evaluated") for item in attempt_payloads
                    ),
                    "gate1_evaluated": any(
                        item.get("gate1_evaluated") for item in attempt_payloads
                    ),
                    "gate1_decision": final_attempt.get("gate1_decision"),
                    "gate2_evaluated": any(
                        item.get("gate2_evaluated") for item in attempt_payloads
                    ),
                    "gate2_decision": final_attempt.get(
                        "gate2_decision"
                    ),
                    "applied": applied_payload is not None,
                    "accepted": any(item.get("accepted") for item in attempt_payloads),
                    "attempt_count": len(attempt_payloads),
                    "applied_attempt": applied_attempt,
                    "selected_group_id": final_attempt.get("group_id"),
                    "candidate_id": final_attempt.get("candidate_id"),
                    "candidate_evidence_family": final_attempt.get(
                        "candidate_evidence_family"
                    ),
                    "acceptance_policy": final_attempt.get(
                        "acceptance_policy", REQUIRED_METRIC_ACCEPTANCE_POLICY
                    ),
                    "gate_sequence_policy": final_attempt.get(
                        "gate_sequence_policy",
                        gate_sequence_policy(bool(args.gate2)),
                    ),
                    "required_metrics": final_attempt.get("required_metrics", []),
                    "required_metric_results": final_attempt.get(
                        "required_metric_results", {}
                    ),
                    "incomplete_required_metrics": final_attempt.get(
                        "incomplete_required_metrics", []
                    ),
                    "non_improving_required_metrics": final_attempt.get(
                        "non_improving_required_metrics", []
                    ),
                    "direct_metric": final_attempt.get("direct_metric"),
                    "direct_metric_results": final_attempt.get(
                        "direct_metric_results", {}
                    ),
                    "acceptance_decision": final_attempt.get("acceptance_decision"),
                    "rejection_reasons": (
                        list(applied_payload.get("rejection_reasons", []))
                        if applied_payload is not None
                        else []
                        if args.candidate_application_mode == "isolated"
                        else [
                            "candidate_attempts_exhausted",
                            *list(final_attempt.get("rejection_reasons", [])),
                        ]
                    ),
                }
            )

        attempts_summary = {
            "schema_version": "candidate-attempts-v1",
            "max_attempts": args.max_candidate_attempts_per_epoch,
            "available_group_count": available_group_count,
            "eligible_group_count": eligible_group_count,
            "filtered_groups": filtered_candidate_groups,
            "attempt_count": len(attempt_payloads),
            "applied_attempt": applied_attempt,
            "attempts": attempt_payloads,
        }
        write_text(
            paths["candidate_attempts"],
            json.dumps(attempts_summary, ensure_ascii=False, indent=2),
        )
        record_stage(
            manifest,
            "candidate_attempts",
            status="applied" if applied_attempt is not None else "completed",
            inputs={"groups": rel_to_iter(iter_dir, paths["error_selector_output"])},
            outputs={"summary": rel_to_iter(iter_dir, paths["candidate_attempts"])},
            note=(
                f"attempted={len(attempt_payloads)}, applied_attempt={applied_attempt}"
            ),
        )

        write_text(paths["prompt_after"], prompt)
        write_text(paths["acceptance"], json.dumps(acceptance, ensure_ascii=False, indent=2))
        write_text(
            paths["mechanism_lineage"],
            json.dumps(
                {
                    "schema_version": "selector-lineage-v3",
                    "applied_attempt": applied_attempt,
                    "attempts": attempt_lineage,
                    "acceptance": acceptance,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        record_stage(
            manifest,
            "epoch_training",
            status="success",
            inputs={"prompt_before": rel_to_iter(iter_dir, paths["prompt_before"])},
            outputs={
                "prompt_after": rel_to_iter(iter_dir, paths["prompt_after"]),
                "analysis_summary": rel_to_iter(iter_dir, paths["analysis_summary"]),
                "acceptance": rel_to_iter(iter_dir, paths["acceptance"]),
            },
            note=(
                f"candidate_valid={acceptance['candidate_valid']}, "
                f"gate_evaluated={acceptance['gate_evaluated']}, applied={acceptance['applied']}"
            ),
        )
        write_iteration_manifest(iter_dir, manifest)
        finalize_iteration_reports(
            run_dir=run_dir,
            iter_dir=iter_dir,
            iteration=iteration,
            prompt_before=prompt_before,
            prompt_after=prompt,
            candidate_prompt=candidate_prompt,
            analysis_summary=epoch_summary,
            baseline_gate_summary=baseline_gate_summary,
            candidate_summary=candidate_summary,
            acceptance=acceptance,
        )
        print(
            f"[iteration {iteration}] selector-v4 complete: "
            f"candidate_generated={acceptance['candidate_generated']}, "
            f"candidate_valid={acceptance['candidate_valid']}, applied={acceptance['applied']}"
        )

        if test_cases is not None and test_dataset is not None:
            prompt_before_hash = prompt_fingerprint(prompt_before)
            prompt_after_hash = prompt_fingerprint(prompt)
            if prompt_after_hash == prompt_before_hash:
                write_text(
                    iter_dir / "test" / "manifest.json",
                    json.dumps(
                        {
                            "dataset": test_dataset,
                            "iteration": iteration,
                            "status": "skipped",
                            "reason": "prompt_unchanged",
                            "prompt_before_hash": prompt_before_hash,
                            "prompt_after_hash": prompt_after_hash,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                )
            else:
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

        if (
            bool(getattr(args, "stop_after_first_apply", False))
            and acceptance["applied"]
        ):
            print(
                "[run] stop_after_first_apply reached: "
                f"iteration={iteration}, "
                f"candidate_id={acceptance.get('candidate_id') or 'unknown'}"
            )
            break

    final_prompt = read_text(work_prompt_path)
    write_text(run_dir / "prompt_final.md", final_prompt)
    if test_cases is not None and test_dataset is not None:
        write_iteration_test_metric_plot(run_dir)
    refresh_run_reports(run_dir)
    if test_cases is not None and test_dataset is not None:
        return final_prompt, last_test_summary or {}
    return final_prompt, last_summary




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
            case_concurrency=args.gate_concurrency,
        )
        summaries.append(summary)
        write_text(repeat_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))

    aggregate = aggregate_repeat_summaries(summaries)
    metric_stats = {
        metric: calibration_statistics(
            [summary.get(metric, 0.0) for summary in summaries]
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
        "acceptance_policy": (
            "all required pooled, balanced, and source-weighted metric mean deltas "
            "must be positive; calibration is descriptive and never sets a threshold"
        ),
        "note": "Calibration reports repeat variability only. No threshold or regression floor is derived or applied.",
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
            f"range={stats['range']:.6f}"
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
    source_cases = list(datasets[train_dataset])
    source_dataset_counts = case_dataset_counts(source_cases)
    train_pool_cases = select_cases_with_strategy(
        source_cases,
        limit=args.max_train_cases,
        strategy=args.sample_strategy,
        seed=args.sample_seed,
    )
    train_cases, validation_cases, confirmation_cases = split_gate_cases(
        train_pool_cases, args
    )
    run_dir = make_run_dir(args.runs_dir, f"train-{train_dataset}")
    write_run_args(args, run_dir)
    write_case_manifest(run_dir / "train_pool_cases.json", train_pool_cases)
    write_case_manifest(run_dir / "train_cases.json", train_cases)
    if validation_cases:
        write_case_manifest(run_dir / "gate1_cases.json", validation_cases)
    if confirmation_cases:
        write_case_manifest(run_dir / "gate2_cases.json", confirmation_cases)
    write_data_split_summary(
        run_dir=run_dir,
        args=args,
        source_cases=source_cases,
        train_pool_cases=train_pool_cases,
        train_cases=train_cases,
        validation_cases=validation_cases,
        confirmation_cases=confirmation_cases,
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
        source_dataset_counts=source_dataset_counts,
        run_dir=run_dir,
        work_prompt_path=work_prompt_path,
        label=f"train_only={train_dataset}",
        validation_cases=validation_cases,
        confirmation_cases=confirmation_cases,
    )
    return summary


def run_one_split(args: argparse.Namespace, datasets: dict[str, list[Case]], llm_client: LLMClient, test_dataset: str) -> dict[str, float]:
    test_dataset = test_dataset.lower()
    if test_dataset not in datasets:
        raise ValueError(f"Unknown test dataset {test_dataset!r}. Available: {', '.join(sorted(datasets))}")

    train_cases_all = [case for name, cases in datasets.items() if name != test_dataset for case in cases]
    source_dataset_counts = case_dataset_counts(train_cases_all)
    test_cases_all = datasets[test_dataset]
    train_pool_cases = select_cases_with_strategy(
        train_cases_all,
        limit=args.max_train_cases,
        strategy=args.sample_strategy,
        seed=args.sample_seed,
    )
    train_cases, validation_cases, confirmation_cases = split_gate_cases(
        train_pool_cases, args
    )
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
        write_case_manifest(run_dir / "gate1_cases.json", validation_cases)
    if confirmation_cases:
        write_case_manifest(run_dir / "gate2_cases.json", confirmation_cases)
    write_case_manifest(run_dir / "test_cases.json", test_cases)
    write_data_split_summary(
        run_dir=run_dir,
        args=args,
        source_cases=train_cases_all,
        train_pool_cases=train_pool_cases,
        train_cases=train_cases,
        validation_cases=validation_cases,
        confirmation_cases=confirmation_cases,
        test_cases=test_cases,
    )
    work_prompt_path = initialize_run_prompt(args.prompt_path, run_dir)
    print(
        f"[run] test={test_dataset}, train_pool_cases={len(train_pool_cases)}, "
        f"train_cases={len(train_cases)}, gate1_cases={len(validation_cases)}, "
        f"gate2_cases={len(confirmation_cases)}, "
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
    isolated_candidates = getattr(
        args, "candidate_application_mode", "cumulative"
    ) == "isolated" and not args.no_evolve
    initial_summary: dict[str, float] | None = None
    if args.eval_initial_test and not isolated_candidates:
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
        source_dataset_counts=source_dataset_counts,
        run_dir=run_dir,
        work_prompt_path=work_prompt_path,
        label=f"test={test_dataset}",
        validation_cases=validation_cases,
        confirmation_cases=confirmation_cases,
        test_cases=None if isolated_candidates else test_cases,
        test_dataset=None if isolated_candidates else test_dataset,
        initial_test_summary=initial_summary,
    )
    if not summary and initial_summary is not None:
        summary = initial_summary
    refresh_run_reports(run_dir)
    if isolated_candidates:
        print(
            "[test] isolated candidate search complete; heldout was reserved and not evaluated"
        )
    elif not summary:
        print("[test] heldout skipped because no epoch changed the Prompt")
    else:
        print(f"[test] final iteration held-out {format_summary(summary)}")
    return summary


def looks_like_run_dir(path: Path) -> bool:
    return (
        (path / "run_args.json").exists()
        or (path / "prompt_initial.md").exists()
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
    provider = get_llm_provider_settings()
    parser = argparse.ArgumentParser(
        description="Prompt evolution for UML activity diagram PlantUML generation"
    )
    parser.add_argument("--test-dataset", default=None, help="Held-out dataset name, or all")
    parser.add_argument("--train-dataset", default=None)
    parser.add_argument("--train-only", action="store_true")
    parser.add_argument("--datasets-dir", type=Path, default=DEFAULT_DATASETS_DIR)
    parser.add_argument("--prompt-path", type=Path, default=DEFAULT_PROMPT_PATH)
    parser.add_argument(
        "--failure-analysis-prompt-path",
        type=Path,
        default=DEFAULT_FAILURE_ANALYSIS_PROMPT_PATH,
    )
    parser.add_argument(
        "--error-selector-prompt-path",
        type=Path,
        default=DEFAULT_ERROR_SELECTOR_PROMPT_PATH,
    )
    parser.add_argument(
        "--error-localization-prompt-path",
        type=Path,
        default=DEFAULT_ERROR_LOCALIZATION_PROMPT_PATH,
        help="System prompt for taxonomy-free Prompt-gap localization",
    )
    parser.add_argument(
        "--prompt-editor-prompt-path",
        type=Path,
        default=DEFAULT_PROMPT_EDITOR_PROMPT_PATH,
    )
    parser.add_argument(
        "--prompt-rewriter-prompt-path",
        type=Path,
        default=DEFAULT_PROMPT_REWRITER_PROMPT_PATH,
    )
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    parser.add_argument("--plantuml-jar", type=Path, default=DEFAULT_PLANTUML_JAR)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument(
        "--stop-after-first-apply",
        action="store_true",
        help=(
            "Stop after the first applied candidate finishes its normal heldout "
            "audit; continue all iterations when no candidate is applied"
        ),
    )
    parser.add_argument("--max-train-cases", type=int, default=0)
    parser.add_argument("--max-test-cases", type=int, default=0)
    parser.add_argument("--eval-initial-test", action="store_true")
    parser.add_argument("--analysis-batch-size", type=int, default=10)
    parser.add_argument(
        "--training-batch-strategy",
        choices=["stratified", "chunked"],
        default="stratified",
    )
    parser.add_argument("--epoch-batch-concurrency", type=int, default=1)
    parser.add_argument("--heldout-test-concurrency", type=int, default=1)
    parser.add_argument(
        "--heldout-repeats",
        type=int,
        default=1,
        help=(
            "Repeat each initial or applied heldout audit; audit-only and never "
            "used for candidate acceptance"
        ),
    )
    parser.add_argument(
        "--gate-concurrency",
        "--validation-gate-concurrency",
        dest="gate_concurrency",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--sample-strategy",
        choices=["stratified", "random", "prefix"],
        default="stratified",
    )
    parser.add_argument(
        "--test-sample-strategy",
        choices=["stratified", "random", "prefix"],
        default="prefix",
    )
    parser.add_argument(
        "--gate1",
        "--validation-gate",
        dest="gate1",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--gate1-size", "--validation-gate-size", dest="gate1_size", type=int, default=30)
    parser.add_argument(
        "--gate1-strategy",
        "--validation-gate-strategy",
        dest="gate1_strategy",
        choices=["stratified", "random", "prefix"],
        default="stratified",
    )
    parser.add_argument("--gate1-seed", "--validation-gate-seed", dest="gate1_seed", type=int, default=20260629)
    parser.add_argument(
        "--gate2",
        "--confirmation-gate",
        dest="gate2",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument("--gate2-size", "--confirmation-gate-size", dest="gate2_size", type=int, default=30)
    parser.add_argument(
        "--gate2-strategy",
        "--confirmation-gate-strategy",
        dest="gate2_strategy",
        choices=["stratified", "random", "prefix"],
        default="stratified",
    )
    parser.add_argument("--gate2-seed", "--confirmation-gate-seed", dest="gate2_seed", type=int, default=20260630)
    parser.add_argument("--validation-repeats", type=int, default=3)
    parser.add_argument("--max-candidate-attempts-per-epoch", type=int, default=3)
    parser.add_argument(
        "--candidate-application-mode",
        choices=["auto", "isolated", "cumulative", "diagnostic-apply"],
        default="auto",
        help=(
            "auto resolves to cumulative for the enabled Gate; diagnostic-apply is "
            "legacy and must be explicit with --no-gate2"
        ),
    )
    parser.add_argument("--calibrate-validation-only", action="store_true")
    parser.add_argument("--validation-calibration-repeats", type=int, default=5)
    parser.add_argument("--sample-seed", type=int, default=13)
    parser.add_argument(
        "--model",
        default=provider.model,
        help="Shared fallback model for generation, agents, and judge",
    )
    parser.add_argument(
        "--generation-model",
        default=provider.generation_model,
    )
    parser.add_argument(
        "--agent-model",
        default=provider.agent_model,
    )
    parser.add_argument(
        "--judge-model",
        default=provider.judge_model,
    )
    parser.add_argument("--api-key", default=provider.api_key)
    parser.add_argument(
        "--base-url",
        default=provider.base_url,
    )
    parser.set_defaults(llm_provider=provider.name, api_key_environment=provider.api_key_environment)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--analysis-temperature", type=float, default=0.0)
    parser.add_argument("--selector-temperature", type=float, default=0.0)
    parser.add_argument("--localization-temperature", type=float, default=0.0)
    parser.add_argument("--editor-temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=optional_float, default=None)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--analysis-max-tokens", type=int, default=4096)
    parser.add_argument("--selector-max-tokens", type=int, default=12000)
    parser.add_argument("--localization-max-tokens", type=int, default=4096)
    parser.add_argument("--editor-max-tokens", type=int, default=4096)
    parser.add_argument(
        "--thinking",
        choices=["enabled", "disabled"],
        default=provider.thinking,
    )
    for option, default, help_text in (
        ("generation", provider.generation_thinking, "PlantUML generation"),
        ("analysis", provider.analysis_thinking, "failure analysis"),
        ("selector", provider.selector_thinking, "error selector"),
        ("localization", provider.localization_thinking, "Prompt-gap localization"),
        ("editor", provider.editor_thinking, "Prompt editor and rewriter"),
        ("judge", provider.judge_thinking, "LLM semantic judge"),
        ("element-extraction", provider.element_extraction_thinking, "auxiliary extraction"),
    ):
        parser.add_argument(
            f"--{option}-thinking",
            choices=["inherit", "enabled", "disabled"],
            default=default,
            help=f"Thinking mode for {help_text}",
        )
    parser.add_argument("--do-sample", type=optional_bool, default=provider.do_sample)
    parser.add_argument("--llm-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-max-retries", type=int, default=20)
    parser.add_argument("--llm-rate-limit-initial-wait", type=int, default=30)
    parser.add_argument("--llm-rate-limit-max-wait", type=int, default=600)
    parser.add_argument("--node-match-threshold", type=float, default=0.85)
    parser.add_argument("--relation-match-threshold", type=float, default=0.85)
    parser.add_argument(
        "--semantic-embedding-model",
        default=DEFAULT_EMBEDDING_MODEL,
    )
    parser.add_argument(
        "--embedding-element-metrics",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    parser.add_argument(
        "--metric-matcher",
        choices=["embedding", "difflib"],
        default="embedding",
    )
    parser.add_argument(
        "--element-extractor",
        choices=["rule", "llm", "auto"],
        default=os.environ.get("APE_ELEMENT_EXTRACTOR", "llm"),
    )
    parser.add_argument("--element-extraction-temperature", type=float, default=0.0)
    parser.add_argument("--element-extraction-max-tokens", type=int, default=4096)
    parser.add_argument("--element-extraction-max-retries", type=int, default=3)
    parser.add_argument("--max-prompt-chars", type=int, default=4000)
    parser.add_argument("--plantuml-compile-timeout", type=int, default=30)
    parser.add_argument(
        "--llm-element-metrics",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    parser.add_argument("--llm-judge-temperature", type=float, default=0.0)
    parser.add_argument("--llm-judge-max-tokens", type=int, default=4096)
    parser.add_argument("--llm-judge-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-judge-max-retries", type=int, default=3)
    parser.add_argument("--mock-with-gold", action="store_true")
    parser.add_argument("--no-evolve", action="store_true")
    parser.add_argument(
        "--refresh-reports",
        nargs="?",
        const="__ALL__",
        default=None,
        metavar="RUN_DIR",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.datasets_dir = args.datasets_dir.resolve()
    args.prompt_path = args.prompt_path.resolve()
    args.failure_analysis_prompt_path = args.failure_analysis_prompt_path.resolve()
    args.error_selector_prompt_path = args.error_selector_prompt_path.resolve()
    args.error_localization_prompt_path = args.error_localization_prompt_path.resolve()
    args.prompt_editor_prompt_path = args.prompt_editor_prompt_path.resolve()
    args.prompt_rewriter_prompt_path = args.prompt_rewriter_prompt_path.resolve()
    args.runs_dir = args.runs_dir.resolve()
    args.plantuml_jar = args.plantuml_jar.resolve()

    if args.refresh_reports:
        refresh_requested_reports(args)
        return

    args.generation_thinking = resolve_agent_thinking(
        args.generation_thinking, args.thinking
    )
    args.analysis_thinking = resolve_agent_thinking(
        args.analysis_thinking, args.thinking
    )
    args.selector_thinking = resolve_agent_thinking(
        args.selector_thinking, args.thinking
    )
    args.localization_thinking = resolve_agent_thinking(
        args.localization_thinking, args.thinking
    )
    args.editor_thinking = resolve_agent_thinking(args.editor_thinking, args.thinking)
    args.judge_thinking = resolve_agent_thinking(args.judge_thinking, args.thinking)
    args.element_extraction_thinking = resolve_agent_thinking(
        args.element_extraction_thinking, args.thinking
    )
    resolve_model_roles(args)
    resolve_pipeline_defaults(args)
    args.pipeline_policy = "taxonomy-v3"
    args.llm_judge_api_key = args.api_key
    args.llm_judge_base_url = args.base_url
    args.llm_judge_thinking = args.judge_thinking

    datasets = load_cases(args.datasets_dir)
    validate_glm_args(args)
    if not args.prompt_path.exists():
        raise FileNotFoundError(f"Seed prompt file not found: {args.prompt_path}")
    read_prompt_file(args.failure_analysis_prompt_path, label="failure analysis")
    read_prompt_file(args.error_selector_prompt_path, label="error selector")
    read_prompt_file(args.error_localization_prompt_path, label="prompt-gap localization")
    read_prompt_file(args.prompt_editor_prompt_path, label="prompt editor")
    read_prompt_file(args.prompt_rewriter_prompt_path, label="prompt rewriter")

    llm_client = make_llm_client(args)
    if args.train_only:
        if not args.train_dataset:
            parser.error("--train-only requires --train-dataset")
        run_train_only(args, datasets, llm_client, args.train_dataset)
        return
    if not args.test_dataset:
        parser.error(
            "Specify --test-dataset, or --train-only with --train-dataset"
        )
    if args.test_dataset.lower() == "all":
        summaries = {
            dataset_name: run_one_split(args, datasets, llm_client, dataset_name)
            for dataset_name in sorted(datasets)
        }
        print("\n[all] held-out summaries")
        for dataset_name, summary in summaries.items():
            print(f"- {dataset_name}: {format_summary(summary)}")
        return
    run_one_split(args, datasets, llm_client, args.test_dataset)


if __name__ == "__main__":
    main()
