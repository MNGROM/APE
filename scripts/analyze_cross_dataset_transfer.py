from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.error_selector import selected_group_required_metrics


METRICS = (
    "llm_node_f1",
    "llm_relation_f1",
    "plantuml_compilation_pass_rate",
)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Required artifact not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def numeric(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def per_dataset_delta(
    per_dataset: dict[str, Any], dataset: str, metric: str
) -> float | None:
    dataset_payload = per_dataset.get(dataset)
    if not isinstance(dataset_payload, dict):
        return None
    metrics = dataset_payload.get("metrics")
    if not isinstance(metrics, dict):
        return None
    metric_payload = metrics.get(metric)
    if not isinstance(metric_payload, dict):
        return None
    return numeric(metric_payload.get("mean_delta"))


def weighted_metric_delta(
    *,
    per_dataset: dict[str, Any],
    train_dataset_counts: dict[str, Any],
    metric: str,
) -> dict[str, Any]:
    expected = {
        dataset: int(count)
        for dataset, count in train_dataset_counts.items()
        if isinstance(count, int) and not isinstance(count, bool) and count > 0
    }
    missing: list[str] = []
    numerator = 0.0
    denominator = 0
    for dataset, count in sorted(expected.items()):
        delta = per_dataset_delta(per_dataset, dataset, metric)
        if delta is None:
            missing.append(dataset)
            continue
        numerator += delta * count
        denominator += count
    extra = sorted(set(per_dataset) - set(expected))
    available = bool(expected) and not missing and not extra and denominator > 0
    return {
        "diagnostic_only": True,
        "available": available,
        "mean_delta": numerator / denominator if available else None,
        "weight_count": denominator if available else 0,
        "missing_datasets": missing,
        "unweighted_datasets": extra,
    }


def classify_dataset_effects(
    per_dataset: dict[str, Any], metric: str
) -> dict[str, list[str]]:
    effects = {"improved": [], "unchanged": [], "regressed": [], "missing": []}
    for dataset in sorted(per_dataset):
        delta = per_dataset_delta(per_dataset, dataset, metric)
        if delta is None:
            effects["missing"].append(dataset)
        elif delta > 0:
            effects["improved"].append(dataset)
        elif delta < 0:
            effects["regressed"].append(dataset)
        else:
            effects["unchanged"].append(dataset)
    return effects


def analyze_gate(
    decision: Any,
    *,
    train_dataset_counts: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(decision, dict):
        return {
            "available": False,
            "accepted": None,
            "evaluation_valid": False,
            "metrics": {},
        }
    metric_results = decision.get("metric_results")
    per_dataset = decision.get("per_dataset_metric_results")
    metric_results = metric_results if isinstance(metric_results, dict) else {}
    per_dataset = per_dataset if isinstance(per_dataset, dict) else {}
    metrics: dict[str, Any] = {}
    for metric in METRICS:
        metric_payload = metric_results.get(metric)
        macro_delta = (
            numeric(metric_payload.get("mean_delta"))
            if isinstance(metric_payload, dict)
            else None
        )
        metrics[metric] = {
            "macro_mean_delta": macro_delta,
            "training_pool_weighted": weighted_metric_delta(
                per_dataset=per_dataset,
                train_dataset_counts=train_dataset_counts,
                metric=metric,
            ),
            "dataset_effects": classify_dataset_effects(per_dataset, metric),
        }
    return {
        "available": True,
        "accepted": decision.get("accepted"),
        "evaluation_valid": bool(decision.get("evaluation_valid")),
        "split_fingerprint": decision.get("gate1_split_fingerprint")
        or decision.get("gate2_split_fingerprint"),
        "metrics": metrics,
    }


def selected_group_for_entry(
    run_dir: Path, entry: dict[str, Any], warnings: list[str]
) -> dict[str, Any] | None:
    artifacts = entry.get("artifacts")
    candidate_prompt = (
        artifacts.get("candidate_prompt") if isinstance(artifacts, dict) else None
    )
    if not isinstance(candidate_prompt, str):
        warnings.append(
            f"candidate {entry.get('candidate_id', 'unknown')} has no candidate_prompt artifact"
        )
        return None
    candidate_path = (run_dir / candidate_prompt).resolve()
    if not is_within(candidate_path, run_dir) or len(candidate_path.parents) < 2:
        warnings.append(f"candidate artifact escapes run directory: {candidate_prompt}")
        return None
    selected_group = candidate_path.parent.parent / "mechanisms" / "selected_error_group.json"
    if not selected_group.exists():
        warnings.append(f"selected error group not found: {selected_group}")
        return None
    return read_json(selected_group)


def source_cases_for_group(payload: dict[str, Any] | None) -> list[dict[str, str]]:
    if not isinstance(payload, dict):
        return []
    members = payload.get("members")
    members = members if isinstance(members, list) else []
    sources = {
        (member.get("dataset"), member.get("case_id"))
        for member in members
        if isinstance(member, dict)
        and isinstance(member.get("dataset"), str)
        and isinstance(member.get("case_id"), str)
    }
    return [
        {"dataset": dataset, "case_id": case_id}
        for dataset, case_id in sorted(sources)
    ]


def derive_required_metrics(
    entry: dict[str, Any],
    group: dict[str, Any] | None,
    *,
    candidate_id: Any,
    warnings: list[str],
) -> list[str]:
    recorded = entry.get("required_metrics")
    if (
        isinstance(recorded, list)
        and recorded
        and all(isinstance(metric, str) and metric in METRICS for metric in recorded)
        and len(set(recorded)) == len(recorded)
    ):
        return list(recorded)
    if not isinstance(group, dict):
        return []
    try:
        return list(selected_group_required_metrics(group))
    except ValueError as exc:
        warnings.append(
            f"candidate {candidate_id or 'unknown'} required metrics unavailable: {exc}"
        )
        return []


def required_metric_counterfactual(
    decision: Any,
    required_metrics: list[str],
) -> dict[str, Any]:
    result = {
        "diagnostic_only": True,
        "available": False,
        "accepted": None,
        "recorded_accepted": (
            decision.get("accepted") if isinstance(decision, dict) else None
        ),
        "required_metrics": list(required_metrics),
        "required_metric_results": {},
        "incomplete_required_metrics": [],
        "non_improving_required_metrics": [],
    }
    if not required_metrics:
        return result
    if not isinstance(decision, dict):
        result["incomplete_required_metrics"] = list(required_metrics)
        return result
    metric_results = decision.get("metric_results")
    if not isinstance(metric_results, dict):
        result["incomplete_required_metrics"] = list(required_metrics)
        return result
    required_results: dict[str, Any] = {}
    incomplete: list[str] = []
    non_improving: list[str] = []
    for metric in required_metrics:
        metric_payload = metric_results.get(metric)
        mean_delta = (
            numeric(metric_payload.get("mean_delta"))
            if isinstance(metric_payload, dict)
            else None
        )
        explicitly_unavailable = bool(
            isinstance(metric_payload, dict)
            and metric_payload.get("available") is False
        )
        available = mean_delta is not None and not explicitly_unavailable
        required_results[metric] = {
            "available": available,
            "mean_delta": mean_delta,
            "positive_mean_delta": bool(available and mean_delta > 0.0),
        }
        if not available:
            incomplete.append(metric)
        elif mean_delta <= 0.0:
            non_improving.append(metric)
    evaluation_valid = bool(decision.get("evaluation_valid"))
    result.update(
        {
            "available": bool(evaluation_valid and not incomplete),
            "accepted": bool(evaluation_valid and not incomplete and not non_improving),
            "required_metric_results": required_results,
            "incomplete_required_metrics": incomplete,
            "non_improving_required_metrics": non_improving,
        }
    )
    return result


def distribution_payload(counts: Counter[str] | None) -> dict[str, Any]:
    if counts is None:
        return {
            "available": False,
            "total": None,
            "datasets": {},
        }
    total = sum(counts.values())
    return {
        "available": True,
        "total": total,
        "datasets": {
            dataset: {
                "count": count,
                "share": count / total if total else 0.0,
            }
            for dataset, count in sorted(counts.items())
        },
    }


def artifact_dataset_counts(
    path: Path,
    *,
    status: str | None = None,
    warnings: list[str],
) -> Counter[str] | None:
    if not path.exists():
        warnings.append(f"evidence funnel artifact missing: {path}")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        warnings.append(f"evidence funnel artifact unreadable: {path}: {exc}")
        return None
    if not isinstance(payload, list):
        warnings.append(f"evidence funnel artifact is not a list: {path}")
        return None
    return Counter(
        str(item.get("dataset"))
        for item in payload
        if isinstance(item, dict)
        and isinstance(item.get("dataset"), str)
        and (status is None or item.get("status") == status)
    )


def metric_deltas(
    initial_summary: dict[str, Any], final_summary: dict[str, Any]
) -> dict[str, float | None]:
    deltas: dict[str, float | None] = {}
    for metric in METRICS:
        initial = numeric(initial_summary.get(metric))
        final = numeric(final_summary.get(metric))
        deltas[metric] = final - initial if initial is not None and final is not None else None
    return deltas


def read_retry_summary(run_dir: Path, warnings: list[str]) -> dict[str, Any]:
    path = run_dir / "rate_limit_events.jsonl"
    if not path.exists():
        return {"event_count": 0, "wait_seconds": 0.0}
    count = 0
    wait_seconds = 0.0
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            warnings.append(f"invalid retry JSON at {path}:{line_number}")
            continue
        count += 1
        wait_seconds += numeric(payload.get("wait_seconds")) or 0.0
    return {"event_count": count, "wait_seconds": wait_seconds}


def analyze_run(run_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    warnings: list[str] = []
    run_args = read_json(run_dir / "run_args.json")
    split_summary = read_json(run_dir / "data_split_summary.json")
    registry = read_json(run_dir / "candidate_registry.json")
    train_dataset_counts = split_summary.get("train_dataset_counts")
    if not isinstance(train_dataset_counts, dict):
        raise ValueError(f"Missing train_dataset_counts: {run_dir}")

    entries = registry.get("entries")
    entries = entries if isinstance(entries, list) else []
    group_attempts = registry.get("group_attempts")
    group_attempts = group_attempts if isinstance(group_attempts, list) else []
    attempts_by_candidate_id: dict[str, dict[str, Any]] = {}
    for attempt in group_attempts:
        if not isinstance(attempt, dict):
            continue
        candidate_id = attempt.get("candidate_id")
        if isinstance(candidate_id, str) and candidate_id:
            attempts_by_candidate_id.setdefault(candidate_id, attempt)
    funnel = Counter(
        str(attempt.get("outcome", "unknown"))
        for attempt in group_attempts
        if isinstance(attempt, dict)
    )

    initial_path = run_dir / "iteration_000" / "test" / "summary.json"
    initial_summary = read_json(initial_path) if initial_path.exists() else {}
    if not initial_summary:
        warnings.append("initial heldout summary is missing")

    evaluated_candidates: list[dict[str, Any]] = []
    applied_candidates: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        candidate_id = entry.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            warnings.append("candidate registry entry has no candidate_id")
            continue
        attempt = attempts_by_candidate_id.get(candidate_id, {})
        if not attempt:
            warnings.append(f"evaluated candidate missing group attempt: {candidate_id}")
        diagnostics = entry.get("validation_diagnostics")
        diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
        selected_group = selected_group_for_entry(run_dir, entry, warnings)
        source_cases = source_cases_for_group(selected_group)
        required_metrics = derive_required_metrics(
            entry,
            selected_group,
            candidate_id=candidate_id,
            warnings=warnings,
        )
        iteration = entry.get("iteration")
        if not isinstance(iteration, int):
            iteration = attempt.get("iteration")
        gate1 = analyze_gate(
            diagnostics.get("gate1_decision"),
            train_dataset_counts=train_dataset_counts,
        )
        gate2 = analyze_gate(
            diagnostics.get("gate2_decision"),
            train_dataset_counts=train_dataset_counts,
        )
        gate1["counterfactual"] = required_metric_counterfactual(
            diagnostics.get("gate1_decision"), required_metrics
        )
        gate2["counterfactual"] = required_metric_counterfactual(
            diagnostics.get("gate2_decision"), required_metrics
        )
        candidate_payload = {
            "candidate_id": candidate_id,
            "iteration": iteration,
            "attempt": attempt.get("attempt"),
            "recorded_outcome": attempt.get("outcome"),
            "source_cases": source_cases,
            "source_artifact_available": selected_group is not None,
            "required_metrics": required_metrics,
            "base_prompt_hash": entry.get("base_prompt_hash"),
            "candidate_prompt_hash": entry.get("candidate_prompt_hash"),
            "gate1": gate1,
            "gate2": gate2,
        }
        evaluated_candidates.append(candidate_payload)
        if attempt.get("outcome") != "applied":
            continue
        final_path = (
            run_dir / f"iteration_{iteration:03d}" / "test" / "summary.json"
            if isinstance(iteration, int)
            else Path()
        )
        final_summary = (
            read_json(final_path)
            if isinstance(iteration, int) and final_path.exists()
            else {}
        )
        if not final_summary:
            warnings.append(f"heldout summary missing for candidate {candidate_id}")
        infrastructure_rates = [
            numeric(initial_summary.get("infrastructure_error_rate")),
            numeric(final_summary.get("infrastructure_error_rate")),
        ]
        infrastructure_valid = all(
            rate is None or rate == 0.0 for rate in infrastructure_rates
        )
        analysis_valid = bool(
            gate1.get("evaluation_valid")
            and gate2.get("evaluation_valid")
            and initial_summary
            and final_summary
            and infrastructure_valid
        )
        applied_candidates.append(
            {
                **candidate_payload,
                "heldout": {
                    "initial_summary": initial_summary,
                    "final_summary": final_summary,
                    "metric_deltas": metric_deltas(initial_summary, final_summary),
                },
                "analysis_valid": analysis_valid,
            }
        )

    discovery_counts = artifact_dataset_counts(
        run_dir / "train_cases.json", warnings=warnings
    )
    iteration_dirs = [
        iteration_dir
        for iteration_dir in sorted(run_dir.glob("iteration_*"))
        if iteration_dir.is_dir() and iteration_dir.name != "iteration_000"
    ]
    actionable_counts: Counter[str] | None = Counter()
    if entries and not iteration_dirs:
        warnings.append("evidence funnel has no candidate iteration directories")
        actionable_counts = None
    for iteration_dir in iteration_dirs:
        observed = artifact_dataset_counts(
            iteration_dir / "mechanisms" / "evidence_inventory.json",
            status="actionable",
            warnings=warnings,
        )
        if observed is None:
            actionable_counts = None
            continue
        if actionable_counts is not None:
            actionable_counts.update(observed)
    attempt_source_counts = (
        Counter(
            source["dataset"]
            for candidate in evaluated_candidates
            for source in candidate["source_cases"]
        )
        if all(
            candidate["source_artifact_available"]
            for candidate in evaluated_candidates
        )
        else None
    )

    return {
        "diagnostic_only": True,
        "run_dir": str(run_dir),
        "run_name": run_dir.name,
        "test_dataset": run_args.get("test_dataset"),
        "provider": run_args.get("llm_provider"),
        "generation_model": run_args.get("generation_model"),
        "agent_model": run_args.get("agent_model"),
        "judge_model": run_args.get("judge_model"),
        "train_dataset_counts": train_dataset_counts,
        "candidate_funnel": dict(sorted(funnel.items())),
        "evidence_funnel": {
            "discovery_cases": distribution_payload(discovery_counts),
            "actionable_findings": distribution_payload(actionable_counts),
            "attempt_source_cases": distribution_payload(attempt_source_counts),
        },
        "evaluated_candidates": evaluated_candidates,
        "applied_candidates": applied_candidates,
        "retry_summary": read_retry_summary(run_dir, warnings),
        "warnings": warnings,
    }


def format_delta(value: Any) -> str:
    number = numeric(value)
    return "-" if number is None else f"{number:+.6f}"


def format_datasets(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def render_markdown(analyses: list[dict[str, Any]]) -> str:
    lines = [
        "# Cross-dataset Transfer Audit",
        "",
        "- diagnostic_only: true",
        f"- input_runs: {len(analyses)}",
        "",
        "## Runs",
        "",
        "| run | test | provider | generation | attempts | outcomes | retries | wait_seconds |",
        "| --- | --- | --- | --- | ---: | --- | ---: | ---: |",
    ]
    for analysis in analyses:
        funnel = analysis["candidate_funnel"]
        outcomes = ", ".join(f"{key}={value}" for key, value in funnel.items()) or "none"
        retry = analysis["retry_summary"]
        lines.append(
            "| "
            + " | ".join(
                [
                    str(analysis["run_name"]),
                    str(analysis.get("test_dataset") or "-"),
                    str(analysis.get("provider") or "-"),
                    str(analysis.get("generation_model") or "-"),
                    str(sum(funnel.values())),
                    outcomes,
                    str(retry["event_count"]),
                    f"{retry['wait_seconds']:.1f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Evidence Funnel",
            "",
            "Shares describe artifact frequency and never affect acceptance.",
            "",
            "| run | stage | status | dataset | count | share |",
            "| --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for analysis in analyses:
        for stage, distribution in analysis["evidence_funnel"].items():
            datasets = distribution.get("datasets", {})
            if not datasets:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            analysis["run_name"],
                            stage,
                            "complete" if distribution.get("available") else "unavailable",
                            "-",
                            "0" if distribution.get("available") else "-",
                            "-",
                        ]
                    )
                    + " |"
                )
                continue
            for dataset, payload in datasets.items():
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            analysis["run_name"],
                            stage,
                            "complete",
                            dataset,
                            str(payload["count"]),
                            f"{payload['share']:.4f}",
                        ]
                    )
                    + " |"
                )

    lines.extend(
        [
            "",
            "## Required-metric Counterfactual",
            "",
            "Counterfactual decisions are diagnostic-only and do not rewrite historical acceptance.",
            "",
            "| run | candidate | outcome | source | required | gate | recorded | counterfactual | unavailable | non_improving |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for analysis in analyses:
        for candidate in analysis["evaluated_candidates"]:
            source = format_datasets(
                [
                    f"{item['dataset']}/{item['case_id']}"
                    for item in candidate["source_cases"]
                ]
            )
            required = ", ".join(candidate["required_metrics"]) or "unavailable"
            for gate_name in ("gate1", "gate2"):
                counterfactual = candidate[gate_name].get("counterfactual", {})
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            analysis["run_name"],
                            str(candidate["candidate_id"]),
                            str(candidate.get("recorded_outcome") or "-"),
                            source,
                            required,
                            gate_name,
                            str(counterfactual.get("recorded_accepted")),
                            (
                                str(counterfactual.get("accepted"))
                                if counterfactual.get("available")
                                else "unavailable"
                            ),
                            format_datasets(
                                counterfactual.get(
                                    "incomplete_required_metrics", []
                                )
                            ),
                            format_datasets(
                                counterfactual.get(
                                    "non_improving_required_metrics", []
                                )
                            ),
                        ]
                    )
                    + " |"
                )

    lines.extend(
        [
            "",
            "## Gate Transfer",
            "",
            "Pool-weighted values are diagnostic-only and never replace the recorded acceptance decision.",
            "",
            "| run | candidate | source | valid | gate | metric | macro_mean | pool_weighted | improved | unchanged | regressed |",
            "| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- |",
        ]
    )
    for analysis in analyses:
        for candidate in analysis["evaluated_candidates"]:
            source = format_datasets(
                [
                    f"{item['dataset']}/{item['case_id']}"
                    for item in candidate["source_cases"]
                ]
            )
            for gate_name in ("gate1", "gate2"):
                gate = candidate[gate_name]
                for metric in METRICS:
                    metric_payload = gate.get("metrics", {}).get(metric, {})
                    weighted = metric_payload.get("training_pool_weighted", {})
                    effects = metric_payload.get("dataset_effects", {})
                    lines.append(
                        "| "
                        + " | ".join(
                            [
                                analysis["run_name"],
                                str(candidate["candidate_id"]),
                                source,
                                str(gate.get("evaluation_valid", False)).lower(),
                                gate_name,
                                metric,
                                format_delta(metric_payload.get("macro_mean_delta")),
                                format_delta(weighted.get("mean_delta")),
                                format_datasets(effects.get("improved", [])),
                                format_datasets(effects.get("unchanged", [])),
                                format_datasets(effects.get("regressed", [])),
                            ]
                        )
                        + " |"
                    )

    lines.extend(
        [
            "",
            "## Heldout Audit",
            "",
            "| run | candidate | test | valid | node_delta | relation_delta | compile_delta |",
            "| --- | --- | --- | --- | ---: | ---: | ---: |",
        ]
    )
    for analysis in analyses:
        for candidate in analysis["applied_candidates"]:
            deltas = candidate["heldout"]["metric_deltas"]
            lines.append(
                "| "
                + " | ".join(
                    [
                        analysis["run_name"],
                        str(candidate["candidate_id"]),
                        str(analysis.get("test_dataset") or "-"),
                        str(candidate["analysis_valid"]).lower(),
                        format_delta(deltas.get("llm_node_f1")),
                        format_delta(deltas.get("llm_relation_f1")),
                        format_delta(deltas.get("plantuml_compilation_pass_rate")),
                    ]
                )
                + " |"
            )

    warnings = [
        f"{analysis['run_name']}: {warning}"
        for analysis in analyses
        for warning in analysis["warnings"]
    ]
    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
    return "\n".join(lines).rstrip() + "\n"


def write_output(text: str, output: Path, run_dirs: list[Path]) -> None:
    output = output.resolve()
    for run_dir in run_dirs:
        if is_within(output, run_dir):
            raise ValueError(f"Output must not be written inside an input run: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only cross-dataset transfer audit for APE run artifacts."
    )
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional Markdown output outside all input run directories.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    run_dirs = [path.resolve() for path in args.run_dirs]
    analyses = [analyze_run(path) for path in run_dirs]
    report = render_markdown(analyses)
    if args.output is None:
        print(report, end="")
    else:
        write_output(report, args.output, run_dirs)
        print(f"Wrote cross-dataset transfer audit: {args.output.resolve()}")


if __name__ == "__main__":
    main()
