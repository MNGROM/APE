from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.error_selector import selected_group_required_metrics
from prediction import extract_plantuml


METRICS = (
    "llm_node_precision",
    "llm_node_recall",
    "llm_node_f1",
    "llm_relation_precision",
    "llm_relation_recall",
    "llm_relation_f1",
    "plantuml_compilation_pass_rate",
)
REQUIRED_METRICS = {
    "llm_node_f1",
    "llm_relation_f1",
    "plantuml_compilation_pass_rate",
}
IMPACT_METRIC_ALIASES = {
    "plantuml_compilation_pass_rate": "plantuml_compilation_pass",
}


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
    if metric_payload.get("available") is False:
        return None
    return numeric(metric_payload.get("mean_delta"))


def merge_per_dataset_metrics(
    primary: dict[str, Any], fallback: dict[str, Any]
) -> dict[str, Any]:
    merged = {
        dataset: dict(payload)
        for dataset, payload in primary.items()
        if isinstance(payload, dict)
    }
    for dataset, fallback_payload in fallback.items():
        if not isinstance(fallback_payload, dict):
            continue
        target = merged.setdefault(dataset, {})
        target_metrics = target.get("metrics")
        if not isinstance(target_metrics, dict):
            target_metrics = {}
        else:
            target_metrics = dict(target_metrics)
        target["metrics"] = target_metrics
        fallback_metrics = fallback_payload.get("metrics")
        if not isinstance(fallback_metrics, dict):
            continue
        for metric, metric_payload in fallback_metrics.items():
            if metric not in target_metrics and isinstance(metric_payload, dict):
                target_metrics[metric] = dict(metric_payload)
        for field in ("case_count", "repeat_count"):
            if field not in target and field in fallback_payload:
                target[field] = fallback_payload[field]
    return merged


def impact_summary_decomposition(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = read_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return {}
    datasets = payload.get("datasets")
    if not isinstance(datasets, list):
        return {}
    result: dict[str, Any] = {}
    for item in datasets:
        if not isinstance(item, dict) or not isinstance(item.get("dataset"), str):
            continue
        raw_metrics = item.get("metrics")
        raw_metrics = raw_metrics if isinstance(raw_metrics, dict) else {}
        metrics: dict[str, Any] = {}
        for metric in METRICS:
            source_metric = IMPACT_METRIC_ALIASES.get(metric, metric)
            source = raw_metrics.get(source_metric)
            mean_delta = (
                numeric(source.get("mean_delta"))
                if isinstance(source, dict)
                else None
            )
            metrics[metric] = {
                "available": mean_delta is not None,
                "mean_delta": mean_delta,
                "legacy_source": "impact_summary",
            }
        result[str(item["dataset"])] = {
            "case_count": item.get("case_count"),
            "repeat_count": payload.get("repeat_count"),
            "metrics": metrics,
        }
    return result


def gate_macro_delta(decision: dict[str, Any], metric: str) -> float | None:
    metric_results = decision.get("metric_results")
    metric_payload = (
        metric_results.get(metric) if isinstance(metric_results, dict) else None
    )
    if isinstance(metric_payload, dict) and metric_payload.get("available") is not False:
        mean_delta = numeric(metric_payload.get("mean_delta"))
        if mean_delta is not None:
            return mean_delta
    baseline = decision.get("baseline_summary")
    candidate = decision.get("candidate_summary")
    if not isinstance(baseline, dict) or not isinstance(candidate, dict):
        return None
    baseline_value = numeric(baseline.get(metric))
    candidate_value = numeric(candidate.get(metric))
    if baseline_value is None or candidate_value is None:
        return None
    return candidate_value - baseline_value


def weighted_metric_delta(
    *,
    per_dataset: dict[str, Any],
    dataset_counts: dict[str, Any],
    metric: str,
    weight_basis: str,
) -> dict[str, Any]:
    expected = {
        dataset: int(count)
        for dataset, count in dataset_counts.items()
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
        "weight_basis": weight_basis,
        "available": available,
        "mean_delta": numerator / denominator if available else None,
        "weight_count": denominator if available else 0,
        "missing_datasets": missing,
        "unweighted_datasets": extra,
    }


def balanced_metric_delta(
    per_dataset: dict[str, Any], metric: str, expected_datasets: set[str] | None = None
) -> float | None:
    datasets = expected_datasets or set(per_dataset)
    if not datasets or set(per_dataset) != datasets:
        return None
    deltas = [
        per_dataset_delta(per_dataset, dataset, metric)
        for dataset in sorted(datasets)
    ]
    if any(delta is None for delta in deltas):
        return None
    return statistics.fmean(float(delta) for delta in deltas if delta is not None)


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
    dataset_counts: dict[str, Any],
    weight_basis: str,
    fallback_per_dataset: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not isinstance(decision, dict):
        return {
            "available": False,
            "accepted": None,
            "evaluation_valid": False,
            "metrics": {},
        }
    per_dataset = decision.get("per_dataset_metric_results")
    per_dataset = per_dataset if isinstance(per_dataset, dict) else {}
    per_dataset = merge_per_dataset_metrics(
        per_dataset,
        fallback_per_dataset if isinstance(fallback_per_dataset, dict) else {},
    )
    metrics: dict[str, Any] = {}
    expected_datasets = {
        str(dataset)
        for dataset, count in dataset_counts.items()
        if isinstance(count, int) and not isinstance(count, bool) and count > 0
    }
    for metric in METRICS:
        macro_delta = balanced_metric_delta(
            per_dataset, metric, expected_datasets
        )
        weighted = weighted_metric_delta(
            per_dataset=per_dataset,
            dataset_counts=dataset_counts,
            metric=metric,
            weight_basis=weight_basis,
        )
        metrics[metric] = {
            "macro_mean_delta": macro_delta,
            "source_weighted": weighted,
            # Retain the historical key for consumers of old report artifacts.
            "training_pool_weighted": weighted,
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


def candidate_attempt_dir(
    run_dir: Path, entry: dict[str, Any], warnings: list[str]
) -> Path | None:
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
    return candidate_path.parent.parent


def selected_group_for_entry(
    attempt_dir: Path | None, warnings: list[str]
) -> dict[str, Any] | None:
    if attempt_dir is None:
        return None
    selected_group = attempt_dir / "mechanisms" / "selected_error_group.json"
    if not selected_group.exists():
        warnings.append(f"selected error group not found: {selected_group}")
        return None
    return read_json(selected_group)


def normalize_plantuml_text(value: str) -> str:
    extracted = extract_plantuml(value, wrap_if_needed=False)
    return "\n".join(
        re.sub(r"\s+", " ", line.strip())
        for line in extracted.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        if line.strip()
    )


def read_gate_records(
    path: Path,
    *,
    repeat: int,
    warnings: list[str],
) -> tuple[dict[tuple[int, str, str], str], bool]:
    if not path.exists():
        warnings.append(f"Gate record artifact missing: {path}")
        return {}, False
    indexed: dict[tuple[int, str, str], str] = {}
    valid = True
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        warnings.append(f"Gate record artifact unreadable: {path}: {exc}")
        return {}, False
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            warnings.append(f"invalid Gate record JSON at {path}:{line_number}")
            valid = False
            continue
        dataset = payload.get("dataset") if isinstance(payload, dict) else None
        case_id = payload.get("case_id") if isinstance(payload, dict) else None
        generated = (
            payload.get("generated_plantuml") if isinstance(payload, dict) else None
        )
        if not all(isinstance(value, str) for value in (dataset, case_id, generated)):
            warnings.append(f"incomplete Gate record at {path}:{line_number}")
            valid = False
            continue
        key = (repeat, dataset, case_id)
        if key in indexed:
            warnings.append(
                f"duplicate Gate record key repeat={repeat} dataset={dataset} "
                f"case_id={case_id}: {path}"
            )
            valid = False
            continue
        indexed[key] = normalize_plantuml_text(generated)
    return indexed, valid


def text_change_summary(
    pairs: list[tuple[str, str, str]],
    *,
    comparison: str,
    missing_pairs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    missing_pairs = list(missing_pairs or [])
    unavailable = {
        "diagnostic_only": True,
        "comparison": comparison,
        "available": False,
        "paired_record_count": None,
        "changed_record_count": None,
        "stable_record_count": None,
        "change_rate": None,
        "stable_rate": None,
        "dataset_results": {},
        "missing_pairs": missing_pairs,
    }
    if missing_pairs or not pairs:
        return unavailable
    dataset_totals: Counter[str] = Counter()
    dataset_changes: Counter[str] = Counter()
    changed_count = 0
    for dataset, before, after in pairs:
        changed = before != after
        dataset_totals[dataset] += 1
        if changed:
            changed_count += 1
            dataset_changes[dataset] += 1
    paired_count = len(pairs)
    stable_count = paired_count - changed_count
    return {
        "diagnostic_only": True,
        "comparison": comparison,
        "available": True,
        "paired_record_count": paired_count,
        "changed_record_count": changed_count,
        "stable_record_count": stable_count,
        "change_rate": changed_count / paired_count,
        "stable_rate": stable_count / paired_count,
        "dataset_results": {
            dataset: {
                "paired_record_count": dataset_totals[dataset],
                "changed_record_count": dataset_changes[dataset],
                "stable_record_count": (
                    dataset_totals[dataset] - dataset_changes[dataset]
                ),
                "change_rate": (
                    dataset_changes[dataset] / dataset_totals[dataset]
                ),
                "stable_rate": (
                    (dataset_totals[dataset] - dataset_changes[dataset])
                    / dataset_totals[dataset]
                ),
            }
            for dataset in sorted(dataset_totals)
        },
        "missing_pairs": [],
    }


def repeat_self_change_summary(
    indexed: dict[tuple[int, str, str], str],
    *,
    repeat_count: int,
    comparison: str,
) -> dict[str, Any]:
    if repeat_count < 2:
        return text_change_summary([], comparison=comparison)
    identities_by_repeat = {
        repeat: {
            (dataset, case_id)
            for indexed_repeat, dataset, case_id in indexed
            if indexed_repeat == repeat
        }
        for repeat in range(1, repeat_count + 1)
    }
    all_identities = set().union(*identities_by_repeat.values())
    missing_pairs = [
        {
            "repeat": repeat,
            "dataset": dataset,
            "case_id": case_id,
            "missing": comparison,
        }
        for repeat in range(1, repeat_count + 1)
        for dataset, case_id in sorted(
            all_identities - identities_by_repeat[repeat]
        )
    ]
    pairs = [
        (
            dataset,
            indexed[(left_repeat, dataset, case_id)],
            indexed[(right_repeat, dataset, case_id)],
        )
        for left_repeat in range(1, repeat_count)
        for right_repeat in range(left_repeat + 1, repeat_count + 1)
        for dataset, case_id in sorted(all_identities)
        if not missing_pairs
    ]
    return text_change_summary(
        pairs,
        comparison=comparison,
        missing_pairs=missing_pairs,
    )


def gate_text_change_rate(
    attempt_dir: Path | None,
    gate_name: str,
    decision: Any,
    warnings: list[str],
) -> dict[str, Any]:
    unavailable = text_change_summary(
        [], comparison="baseline-vs-candidate-same-repeat"
    )
    unavailable.update(
        {
            "paired_prompt_change": dict(unavailable),
            "baseline_self_variation": text_change_summary(
                [], comparison="baseline-repeat-self"
            ),
            "candidate_self_variation": text_change_summary(
                [], comparison="candidate-repeat-self"
            ),
        }
    )
    if attempt_dir is None or not isinstance(decision, dict):
        return unavailable
    repeat_count = decision.get("validation_repeats")
    if not isinstance(repeat_count, int) or repeat_count < 1:
        repeat_dirs = sorted((attempt_dir / gate_name).glob("repeat_*"))
        repeat_count = len(repeat_dirs)
    if repeat_count < 1:
        warnings.append(f"Gate record repeats unavailable: {attempt_dir / gate_name}")
        return unavailable

    baseline_index: dict[tuple[int, str, str], str] = {}
    candidate_index: dict[tuple[int, str, str], str] = {}
    records_valid = True
    for repeat in range(1, repeat_count + 1):
        repeat_dir = attempt_dir / gate_name / f"repeat_{repeat:03d}"
        baseline, baseline_valid = read_gate_records(
            repeat_dir / "baseline" / "records.jsonl",
            repeat=repeat,
            warnings=warnings,
        )
        candidate, candidate_valid = read_gate_records(
            repeat_dir / "candidate" / "records.jsonl",
            repeat=repeat,
            warnings=warnings,
        )
        baseline_index.update(baseline)
        candidate_index.update(candidate)
        records_valid = records_valid and baseline_valid and candidate_valid

    missing_pairs = [
        {"repeat": repeat, "dataset": dataset, "case_id": case_id, "missing": role}
        for role, keys in (
            ("candidate", sorted(set(baseline_index) - set(candidate_index))),
            ("baseline", sorted(set(candidate_index) - set(baseline_index))),
        )
        for repeat, dataset, case_id in keys
    ]
    if not records_valid or missing_pairs or not baseline_index:
        unavailable["missing_pairs"] = missing_pairs
        unavailable["paired_prompt_change"]["missing_pairs"] = missing_pairs
        return unavailable

    paired_prompt_change = text_change_summary(
        [
            (dataset, baseline_index[key], candidate_index[key])
            for key in sorted(baseline_index)
            for _repeat, dataset, _case_id in [key]
        ],
        comparison="baseline-vs-candidate-same-repeat",
    )
    return {
        **paired_prompt_change,
        "paired_prompt_change": paired_prompt_change,
        "baseline_self_variation": repeat_self_change_summary(
            baseline_index,
            repeat_count=repeat_count,
            comparison="baseline-repeat-self",
        ),
        "candidate_self_variation": repeat_self_change_summary(
            candidate_index,
            repeat_count=repeat_count,
            comparison="candidate-repeat-self",
        ),
    }


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
        and all(
            isinstance(metric, str) and metric in REQUIRED_METRICS
            for metric in recorded
        )
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


def artifact_status_dataset_counts(
    path: Path,
    *,
    warnings: list[str],
) -> dict[str, Counter[str]] | None:
    """Return the read-only discovery funnel grouped by status and dataset."""
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
    grouped: dict[str, Counter[str]] = {}
    for item in payload:
        if not isinstance(item, dict) or not isinstance(item.get("dataset"), str):
            continue
        status = str(item.get("status") or item.get("classification") or "unknown")
        grouped.setdefault(status, Counter())[item["dataset"]] += 1
    return grouped


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
    train_pool_dataset_counts = split_summary.get("train_pool_dataset_counts")
    source_dataset_counts = split_summary.get("source_dataset_counts")
    if isinstance(source_dataset_counts, dict) and source_dataset_counts:
        weighted_dataset_counts = source_dataset_counts
        weight_basis = "source_population"
    elif "source_dataset_counts" not in split_summary:
        weighted_dataset_counts = train_dataset_counts
        weight_basis = "historical_train_pool"
    else:
        weighted_dataset_counts = {}
        weight_basis = "source_population"

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

    def entry_sort_key(entry: dict[str, Any]) -> tuple[int, int]:
        iteration = entry.get("iteration")
        attempt = attempts_by_candidate_id.get(
            str(entry.get("candidate_id") or ""), {}
        ).get("attempt")
        return (
            iteration if isinstance(iteration, int) else 10**9,
            attempt if isinstance(attempt, int) else 10**9,
        )

    entries = sorted(
        (entry for entry in entries if isinstance(entry, dict)),
        key=entry_sort_key,
    )
    previous_applied_summary = initial_summary
    previous_applied_iteration: int | None = 0 if initial_summary else None
    for entry in entries:
        candidate_id = entry.get("candidate_id")
        if not isinstance(candidate_id, str) or not candidate_id:
            warnings.append("candidate registry entry has no candidate_id")
            continue
        attempt = attempts_by_candidate_id.get(candidate_id, {})
        if not attempt:
            warnings.append(f"evaluated candidate missing group attempt: {candidate_id}")
        diagnostics = entry.get("validation_diagnostics")
        diagnostics = diagnostics if isinstance(diagnostics, dict) else {}
        gate2_required = (
            bool(run_args.get("gate2"))
            if "gate2" in run_args
            else isinstance(diagnostics.get("gate2_decision"), dict)
        )
        attempt_dir = candidate_attempt_dir(run_dir, entry, warnings)
        selected_group = selected_group_for_entry(attempt_dir, warnings)
        source_cases = source_cases_for_group(selected_group)
        source_datasets = sorted({item["dataset"] for item in source_cases})
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
            dataset_counts=weighted_dataset_counts,
            weight_basis=weight_basis,
            fallback_per_dataset=(
                impact_summary_decomposition(attempt_dir / "gate1" / "impact_summary.json")
                if attempt_dir is not None
                else {}
            ),
        )
        gate2 = analyze_gate(
            diagnostics.get("gate2_decision"),
            dataset_counts=weighted_dataset_counts,
            weight_basis=weight_basis,
            fallback_per_dataset=(
                impact_summary_decomposition(attempt_dir / "gate2" / "impact_summary.json")
                if attempt_dir is not None
                else {}
            ),
        )
        for gate_name, decision, gate in (
            ("gate1", diagnostics.get("gate1_decision"), gate1),
            ("gate2", diagnostics.get("gate2_decision"), gate2),
        ):
            if not isinstance(decision, dict):
                continue
            missing_metrics = [
                metric
                for metric in METRICS
                if not (
                    gate["metrics"][metric].get("source_weighted")
                    or gate["metrics"][metric].get("training_pool_weighted")
                ).get(
                    "available"
                )
            ]
            if missing_metrics:
                warnings.append(
                    f"candidate {candidate_id} {gate_name} per-dataset artifacts "
                    f"unavailable for: {', '.join(missing_metrics)}"
                )
        gate1["counterfactual"] = required_metric_counterfactual(
            diagnostics.get("gate1_decision"), required_metrics
        )
        gate2["counterfactual"] = required_metric_counterfactual(
            diagnostics.get("gate2_decision"), required_metrics
        )
        gate1["plantuml_text_change"] = gate_text_change_rate(
            attempt_dir, "gate1", diagnostics.get("gate1_decision"), warnings
        )
        gate2["plantuml_text_change"] = gate_text_change_rate(
            attempt_dir, "gate2", diagnostics.get("gate2_decision"), warnings
        )
        candidate_payload = {
            "candidate_id": candidate_id,
            "iteration": iteration,
            "attempt": attempt.get("attempt"),
            "recorded_outcome": attempt.get("outcome"),
            "source_cases": source_cases,
            "source_datasets": source_datasets,
            "source_interpretation": "discovery_dataset_only",
            "source_artifact_available": selected_group is not None,
            "required_metrics": required_metrics,
            "gate2_required": gate2_required,
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
            and (not gate2_required or gate2.get("evaluation_valid"))
            and initial_summary
            and final_summary
            and infrastructure_valid
        )
        applied_candidates.append(
            {
                **candidate_payload,
                "heldout": {
                    "initial_summary": initial_summary,
                    "previous_applied_iteration": previous_applied_iteration,
                    "previous_applied_summary": previous_applied_summary,
                    "final_summary": final_summary,
                    "metric_deltas": metric_deltas(initial_summary, final_summary),
                    "cumulative_metric_deltas": metric_deltas(
                        initial_summary, final_summary
                    ),
                    "incremental_metric_deltas": metric_deltas(
                        previous_applied_summary, final_summary
                    ),
                },
                "analysis_valid": analysis_valid,
            }
        )
        previous_applied_summary = final_summary
        previous_applied_iteration = iteration if isinstance(iteration, int) else None

    discovery_counts = artifact_dataset_counts(
        run_dir / "train_cases.json", warnings=warnings
    )
    iteration_dirs = [
        iteration_dir
        for iteration_dir in sorted(run_dir.glob("iteration_*"))
        if iteration_dir.is_dir() and iteration_dir.name != "iteration_000"
    ]
    actionable_counts: Counter[str] | None = Counter()
    status_counts: dict[str, Counter[str]] | None = {}
    if entries and not iteration_dirs:
        warnings.append("evidence funnel has no candidate iteration directories")
        actionable_counts = None
        status_counts = None
    for iteration_dir in iteration_dirs:
        evidence_path = iteration_dir / "mechanisms" / "evidence_inventory.json"
        observed_by_status = artifact_status_dataset_counts(
            evidence_path,
            warnings=warnings,
        )
        if observed_by_status is None:
            status_counts = None
            actionable_counts = None
            continue
        if status_counts is not None:
            for status, counts in observed_by_status.items():
                status_counts.setdefault(status, Counter()).update(counts)
        observed = observed_by_status.get("actionable", Counter())
        if actionable_counts is not None:
            actionable_counts.update(observed)
    attempt_source_counts = (
        Counter(
            dataset
            for candidate in evaluated_candidates
            for dataset in candidate["source_datasets"]
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
        "train_pool_dataset_counts": (
            train_pool_dataset_counts
            if isinstance(train_pool_dataset_counts, dict)
            else None
        ),
        "source_dataset_counts": (
            source_dataset_counts
            if isinstance(source_dataset_counts, dict)
            else None
        ),
        "weight_basis": weight_basis,
        "candidate_funnel": dict(sorted(funnel.items())),
        "evidence_funnel": {
            "discovery_cases": distribution_payload(discovery_counts),
            "actionable_findings": distribution_payload(actionable_counts),
            "discovery_findings_by_status": (
                {
                    status: distribution_payload(counts)
                    for status, counts in sorted((status_counts or {}).items())
                }
                if status_counts is not None
                else None
            ),
            "attempt_source_datasets": distribution_payload(attempt_source_counts),
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
            if stage == "discovery_findings_by_status":
                continue
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
            "## Discovery Filtering Reasons",
            "",
            "Statuses explain the discovery funnel by dataset and remain diagnostic-only.",
            "",
            "| run | status | availability | dataset | count | share_within_status |",
            "| --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for analysis in analyses:
        by_status = analysis["evidence_funnel"].get(
            "discovery_findings_by_status"
        )
        if by_status is None:
            lines.append(
                f"| {analysis['run_name']} | - | unavailable | - | - | - |"
            )
            continue
        if not by_status:
            lines.append(
                f"| {analysis['run_name']} | - | complete | - | 0 | - |"
            )
            continue
        for status, distribution in by_status.items():
            datasets = distribution.get("datasets", {})
            if not datasets:
                lines.append(
                    f"| {analysis['run_name']} | {status} | complete | - | 0 | - |"
                )
                continue
            for dataset, payload in datasets.items():
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            analysis["run_name"],
                            status,
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
                candidate.get("source_datasets", [])
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
            "Weighted values use source_population for new runs and historical_train_pool only as an explicit legacy fallback. This cross-run report is diagnostic-only and never rewrites recorded acceptance.",
            "",
            "| run | candidate | source | valid | gate | metric | balanced_mean | weighted_mean | weight_basis | improved | unchanged | regressed |",
            "| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for analysis in analyses:
        for candidate in analysis["evaluated_candidates"]:
            source = format_datasets(
                candidate.get("source_datasets", [])
            )
            for gate_name in ("gate1", "gate2"):
                gate = candidate[gate_name]
                for metric in METRICS:
                    metric_payload = gate.get("metrics", {}).get(metric, {})
                    weighted = metric_payload.get("source_weighted") or metric_payload.get(
                        "training_pool_weighted", {}
                    )
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
                                str(weighted.get("weight_basis") or "unavailable"),
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
            "## PlantUML Text Change",
            "",
            "Prompt-change rates pair baseline and candidate within each repeat. Self-variation rates compare repeats of the same Prompt.",
            "The three rates are reported separately; no subtraction is treated as a causal effect.",
            "Discovery source labels identify datasets only; Gate records do not replay discovery cases.",
            "",
            "| run | candidate | source_dataset | gate | comparison | status | paired | changed | stable_rate | change_rate |",
            "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for analysis in analyses:
        for candidate in analysis["evaluated_candidates"]:
            source = format_datasets(candidate.get("source_datasets", []))
            for gate_name in ("gate1", "gate2"):
                change = candidate[gate_name].get("plantuml_text_change", {})
                comparisons = (
                    ("baseline_vs_candidate", change.get("paired_prompt_change", change)),
                    ("baseline_self", change.get("baseline_self_variation", {})),
                    ("candidate_self", change.get("candidate_self_variation", {})),
                )
                for comparison_name, comparison in comparisons:
                    lines.append(
                        "| "
                        + " | ".join(
                            [
                                analysis["run_name"],
                                str(candidate["candidate_id"]),
                                source,
                                gate_name,
                                comparison_name,
                                (
                                    "complete"
                                    if comparison.get("available")
                                    else "unavailable"
                                ),
                                str(comparison.get("paired_record_count") or "-"),
                                str(comparison.get("changed_record_count") or "-"),
                                format_delta(comparison.get("stable_rate")),
                                format_delta(comparison.get("change_rate")),
                            ]
                        )
                        + " |"
                    )

    lines.extend(
        [
            "",
            "## Heldout Audit",
            "",
            "Cumulative compares the seed to the current Prompt. Incremental compares the previous applied Prompt to the current Prompt.",
            "",
            "| run | candidate | test | valid | metric | cumulative | incremental |",
            "| --- | --- | --- | --- | --- | ---: | ---: |",
        ]
    )
    for analysis in analyses:
        for candidate in analysis["applied_candidates"]:
            cumulative = candidate["heldout"]["cumulative_metric_deltas"]
            incremental = candidate["heldout"]["incremental_metric_deltas"]
            for metric in METRICS:
                lines.append(
                    "| "
                    + " | ".join(
                        [
                            analysis["run_name"],
                            str(candidate["candidate_id"]),
                            str(analysis.get("test_dataset") or "-"),
                            str(candidate["analysis_valid"]).lower(),
                            metric,
                            format_delta(cumulative.get(metric)),
                            format_delta(incremental.get(metric)),
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
