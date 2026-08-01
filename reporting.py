"""Human-readable run reports."""

from __future__ import annotations

import difflib
import json
from pathlib import Path
from typing import Any

from utils.io import read_text, write_text


METRIC_KEYS = (
    "plantuml_compilation_pass_rate",
    "syntax_pass_rate",
    "llm_node_f1",
    "llm_relation_f1",
    "llm_node_precision",
    "llm_node_recall",
    "llm_relation_precision",
    "llm_relation_recall",
    "llm_element_evaluated",
    "llm_element_failed",
    "node_f1",
    "relation_f1",
    "node_precision",
    "node_recall",
    "relation_precision",
    "relation_recall",
    "embedding_element_evaluated",
    "infrastructure_error_rate",
)

IMPACT_METRIC_KEYS = (
    "llm_node_precision",
    "llm_node_recall",
    "llm_node_f1",
    "llm_relation_precision",
    "llm_relation_recall",
    "llm_relation_f1",
    "syntax_pass",
    "plantuml_compilation_pass",
)


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    if isinstance(value, int):
        return str(value)
    if value is None:
        return "-"
    return str(value)


def metric_row(label: str, summary: dict[str, float] | None) -> str:
    summary = summary or {}
    cells = [label]
    for key in METRIC_KEYS:
        cells.append(fmt(summary.get(key)))
    return "| " + " | ".join(cells) + " |"


def metric_delta_row(label: str, deltas: dict[str, float] | None) -> str:
    deltas = deltas or {}
    cells = [label]
    for key in METRIC_KEYS:
        cells.append(fmt(deltas.get(key)))
    return "| " + " | ".join(cells) + " |"


def metric_deltas(before: dict[str, float] | None, after: dict[str, float] | None) -> dict[str, float]:
    before = before or {}
    after = after or {}
    deltas: dict[str, float] = {}
    for key in METRIC_KEYS:
        before_value = before.get(key)
        after_value = after.get(key)
        if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)):
            deltas[key] = float(after_value) - float(before_value)
    return deltas


def _impact_case_key(record: Any) -> tuple[str, str]:
    return str(record.dataset), str(record.case_id)


def _record_groups(records: list[Any]) -> dict[tuple[str, str], list[Any]]:
    groups: dict[tuple[str, str], list[Any]] = {}
    for record in records:
        groups.setdefault(_impact_case_key(record), []).append(record)
    return groups


def _semantic_impact_values(record: Any) -> dict[str, float] | None:
    metrics = getattr(record, "llm_element_metrics", None)
    if metrics is None or getattr(metrics, "status", None) != "success":
        return None
    return {
        "llm_node_precision": float(metrics.node_metrics.precision),
        "llm_node_recall": float(metrics.node_metrics.recall),
        "llm_node_f1": float(metrics.node_metrics.f1),
        "llm_relation_precision": float(metrics.relation_metrics.precision),
        "llm_relation_recall": float(metrics.relation_metrics.recall),
        "llm_relation_f1": float(metrics.relation_metrics.f1),
    }


def _paired_case_impact(*, repeat: int, key: tuple[str, str], baseline: Any, candidate: Any) -> dict[str, Any]:
    baseline_semantic = _semantic_impact_values(baseline)
    candidate_semantic = _semantic_impact_values(candidate)
    semantic_valid = baseline_semantic is not None and candidate_semantic is not None
    deltas: dict[str, float | None] = {
        metric: (
            candidate_semantic[metric] - baseline_semantic[metric]
            if semantic_valid and baseline_semantic is not None and candidate_semantic is not None
            else None
        )
        for metric in IMPACT_METRIC_KEYS[:6]
    }
    deltas["syntax_pass"] = float(bool(candidate.syntax.passed)) - float(bool(baseline.syntax.passed))
    deltas["plantuml_compilation_pass"] = float(bool(candidate.plantuml_compilation.passed)) - float(
        bool(baseline.plantuml_compilation.passed)
    )
    return {
        "repeat": repeat,
        "dataset": key[0],
        "case_id": key[1],
        "pairing_status": "paired",
        "semantic_metric_valid": semantic_valid,
        "baseline_llm_status": getattr(baseline.llm_element_metrics, "status", "missing"),
        "candidate_llm_status": getattr(candidate.llm_element_metrics, "status", "missing"),
        "deltas": deltas,
    }


def _aggregate_impact_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    aggregate: dict[str, Any] = {
        "case_count": len(rows),
        "paired_case_count": sum(row.get("pairing_status") == "paired" for row in rows),
        "semantic_valid_case_count": sum(bool(row.get("semantic_metric_valid")) for row in rows),
        "metrics": {},
    }
    for metric in IMPACT_METRIC_KEYS:
        values = [
            float(row["deltas"][metric])
            for row in rows
            if isinstance(row.get("deltas"), dict)
            and isinstance(row["deltas"].get(metric), (int, float))
        ]
        aggregate["metrics"][metric] = {
            "mean_delta": sum(values) / len(values) if values else None,
            "improved_count": sum(value > 0.0 for value in values),
            "unchanged_count": sum(value == 0.0 for value in values),
            "regressed_count": sum(value < 0.0 for value in values),
            "evaluated_count": len(values),
        }
    return aggregate


def build_validation_impact_summary(
    repeat_pairs: list[tuple[int, list[Any], list[Any]]],
) -> dict[str, Any]:
    """Build paired validation diagnostics without influencing acceptance."""

    case_rows: list[dict[str, Any]] = []
    repeat_rows: list[dict[str, Any]] = []
    for repeat, baseline_records, candidate_records in repeat_pairs:
        baseline_groups = _record_groups(baseline_records)
        candidate_groups = _record_groups(candidate_records)
        current_rows: list[dict[str, Any]] = []
        for key in sorted(set(baseline_groups) | set(candidate_groups)):
            baseline_matches = baseline_groups.get(key, [])
            candidate_matches = candidate_groups.get(key, [])
            if len(baseline_matches) == 1 and len(candidate_matches) == 1:
                row = _paired_case_impact(
                    repeat=repeat,
                    key=key,
                    baseline=baseline_matches[0],
                    candidate=candidate_matches[0],
                )
            else:
                if not baseline_matches:
                    status = "missing_baseline"
                elif not candidate_matches:
                    status = "missing_candidate"
                else:
                    status = "duplicate_case_key"
                row = {
                    "repeat": repeat,
                    "dataset": key[0],
                    "case_id": key[1],
                    "pairing_status": status,
                    "semantic_metric_valid": False,
                    "deltas": {metric: None for metric in IMPACT_METRIC_KEYS},
                }
            current_rows.append(row)
            case_rows.append(row)
        repeat_rows.append({"repeat": repeat, **_aggregate_impact_rows(current_rows)})

    dataset_rows = []
    for dataset in sorted({str(row["dataset"]) for row in case_rows}):
        rows = [row for row in case_rows if row["dataset"] == dataset]
        dataset_rows.append({"dataset": dataset, **_aggregate_impact_rows(rows)})
    return {
        "diagnostic_only": True,
        "acceptance_effect": "none",
        "repeat_count": len(repeat_pairs),
        "repeats": repeat_rows,
        "datasets": dataset_rows,
        "cases": case_rows,
    }


def write_validation_impact_report(*, summary: dict[str, Any], json_path: Path, report_path: Path) -> None:
    write_text(json_path, json.dumps(summary, ensure_ascii=False, indent=2))
    lines = [
        "# Validation Impact Report",
        "",
        "This report is diagnostic only and does not participate in acceptance.",
        "",
        "## Dataset Summary",
        "",
        "| dataset | cases | semantic valid | node P | node R | node F1 | relation P | relation R | relation F1 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for dataset in summary.get("datasets", []):
        metrics = dataset.get("metrics", {})
        lines.append(
            "| "
            + " | ".join(
                [
                    str(dataset.get("dataset", "")),
                    str(dataset.get("case_count", 0)),
                    str(dataset.get("semantic_valid_case_count", 0)),
                    fmt(metrics.get("llm_node_precision", {}).get("mean_delta")),
                    fmt(metrics.get("llm_node_recall", {}).get("mean_delta")),
                    fmt(metrics.get("llm_node_f1", {}).get("mean_delta")),
                    fmt(metrics.get("llm_relation_precision", {}).get("mean_delta")),
                    fmt(metrics.get("llm_relation_recall", {}).get("mean_delta")),
                    fmt(metrics.get("llm_relation_f1", {}).get("mean_delta")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Case Deltas",
            "",
            "| repeat | dataset | case | status | node P | node R | node F1 | relation P | relation R | relation F1 |",
            "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in summary.get("cases", []):
        deltas = row.get("deltas", {})
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row.get("repeat", "")),
                    str(row.get("dataset", "")),
                    str(row.get("case_id", "")),
                    str(row.get("pairing_status", "")),
                    fmt(deltas.get("llm_node_precision")),
                    fmt(deltas.get("llm_node_recall")),
                    fmt(deltas.get("llm_node_f1")),
                    fmt(deltas.get("llm_relation_precision")),
                    fmt(deltas.get("llm_relation_recall")),
                    fmt(deltas.get("llm_relation_f1")),
                ]
            )
            + " |"
        )
    write_text(report_path, "\n".join(lines).rstrip() + "\n")


def metrics_table_header() -> list[str]:
    labels = ["item", *METRIC_KEYS]
    return [
        "| " + " | ".join(labels) + " |",
        "| " + " | ".join(["---"] * len(labels)) + " |",
    ]


def prompt_diff(before: str, after: str, *, from_label: str, to_label: str) -> str:
    return "\n".join(
        difflib.unified_diff(
            before.splitlines(),
            after.splitlines(),
            fromfile=from_label,
            tofile=to_label,
            lineterm="",
        )
    )


def read_json_if_exists(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(read_text(path))


def read_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    return read_text(path)


def refresh_iteration_report(iter_dir: Path) -> None:
    if not iter_dir.is_dir():
        return
    suffix = iter_dir.name.rsplit("_", 1)[-1]
    try:
        iteration = int(suffix)
    except ValueError:
        iteration = 0

    prompt_before = read_text_if_exists(iter_dir / "prompts" / "before.md")
    prompt_after = read_text_if_exists(iter_dir / "prompts" / "after.md")
    if prompt_before is None or prompt_after is None:
        return

    candidate_prompt = read_text_if_exists(iter_dir / "prompts" / "candidate.md")
    analysis_summary = read_json_if_exists(
        iter_dir / "evaluation" / "analysis_summary.json"
    ) or {}
    baseline_gate_summary = read_json_if_exists(
        iter_dir / "validation_gate" / "baseline_summary.json"
    )
    candidate_summary = read_json_if_exists(
        iter_dir / "validation_gate" / "candidate_summary.json"
    )
    acceptance = read_json_if_exists(iter_dir / "decision" / "acceptance.json")

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


def write_iteration_reports(
    *,
    iter_dir: Path,
    iteration: int,
    prompt_before: str,
    prompt_after: str,
    candidate_prompt: str | None,
    analysis_summary: dict[str, float],
    baseline_gate_summary: dict[str, float] | None,
    candidate_summary: dict[str, float] | None,
    acceptance: dict[str, Any] | None,
) -> None:
    accepted = bool(acceptance and acceptance.get("accepted"))
    applied = bool(acceptance and acceptance.get("applied"))
    acceptance_mode = acceptance.get("acceptance_mode") if acceptance else "not_evaluated"
    rejection_reasons = acceptance.get("rejection_reasons", []) if acceptance else []
    baseline_label = "validation_baseline"
    candidate_label = "validation_candidate"

    prompt_lines = [
        f"# Iteration {iteration:03d} Prompt Change",
        "",
        f"- accepted: {accepted}",
        f"- applied: {applied}",
        f"- acceptance_mode: {acceptance_mode}",
        f"- rejection_reasons: {', '.join(rejection_reasons) if rejection_reasons else 'none'}",
        f"- chars_before: {len(prompt_before)}",
        f"- chars_after: {len(prompt_after)}",
    ]
    if acceptance and acceptance.get("selected_group_id"):
        prompt_lines.append(f"- selected_group_id: {acceptance['selected_group_id']}")
    if acceptance and acceptance.get("candidate_evidence_family"):
        prompt_lines.append(
            f"- candidate_evidence_family: {acceptance['candidate_evidence_family']}"
        )
    if acceptance and acceptance.get("direct_metric"):
        prompt_lines.append(f"- direct_metric: {acceptance['direct_metric']}")
    if acceptance and acceptance.get("winning_metrics"):
        prompt_lines.append(f"- winning_metrics: {', '.join(acceptance['winning_metrics'])}")
    if candidate_prompt is not None:
        prompt_lines.append(f"- chars_candidate: {len(candidate_prompt)}")
    prompt_lines.extend(["", "## Applied Change", ""])
    applied_diff = prompt_diff(prompt_before, prompt_after, from_label="prompt_before.md", to_label="prompt_after.md")
    prompt_lines.append("```diff")
    prompt_lines.append(applied_diff or "# no applied prompt change")
    prompt_lines.append("```")
    if candidate_prompt is not None and not applied:
        prompt_lines.extend(["", "## Rejected Candidate Diff", "", "```diff"])
        prompt_lines.append(prompt_diff(prompt_before, candidate_prompt, from_label="prompt_before.md", to_label="prompt_candidate.md") or "# no candidate prompt change")
        prompt_lines.append("```")
    write_text(iter_dir / "reports" / "prompt_change.md", "\n".join(prompt_lines).rstrip() + "\n")

    metric_lines = [
        f"# Iteration {iteration:03d} Metrics",
        "",
        f"- accepted: {accepted}",
        f"- applied: {applied}",
        f"- acceptance_mode: {acceptance_mode}",
        f"- rejection_reasons: {', '.join(rejection_reasons) if rejection_reasons else 'none'}",
        "",
        "## Summaries",
        "",
        *metrics_table_header(),
        metric_row("analysis_current", analysis_summary),
        metric_row(baseline_label, baseline_gate_summary),
        metric_row(candidate_label, candidate_summary),
    ]
    if acceptance:
        metric_lines.extend(["", "## Deltas", "", *metrics_table_header()])
        metric_lines.append(metric_delta_row("candidate_minus_baseline", metric_deltas(baseline_gate_summary, candidate_summary)))
        threshold = acceptance.get("threshold_decision") or acceptance
        gate_payload = {
            "acceptance_policy": threshold.get("acceptance_policy"),
            "candidate_evidence_family": threshold.get(
                "candidate_evidence_family"
            ),
            "direct_metric": threshold.get("direct_metric"),
            "direct_metric_results": threshold.get("direct_metric_results", {}),
            "semantic_safety_results": threshold.get(
                "semantic_safety_results", {}
            ),
            "evaluation_valid": threshold.get("evaluation_valid"),
            "winning_metrics": threshold.get("winning_metrics", []),
            "metric_results": threshold.get("metric_results", {}),
        }
        metric_lines.extend(["", "## Gates", "", "```json", json.dumps(gate_payload, ensure_ascii=False, indent=2), "```"])
    write_text(iter_dir / "reports" / "metrics_report.md", "\n".join(metric_lines).rstrip() + "\n")


def refresh_run_reports(run_dir: Path) -> None:
    for iter_dir in sorted(run_dir.glob("iteration_*")):
        refresh_iteration_report(iter_dir)

    prompt_lines = ["# Prompt Evolution", ""]
    metrics_lines = ["# Metrics Overview", ""]
    metrics_lines.extend(metrics_table_header())
    acceptance_rows = [
        "",
        "## Acceptance Decisions",
        "",
        "| iteration | accepted | acceptance_mode | rejection_reasons |",
        "| --- | --- | --- | --- |",
    ]

    initial_path = run_dir / "prompt_initial.md"
    if initial_path.exists():
        prompt_lines.extend(["## Initial Prompt", "", "```markdown", read_text(initial_path).rstrip(), "```", ""])

    has_iteration_test_metrics = False
    for iter_dir in sorted(run_dir.glob("iteration_*")):
        prompt_report = iter_dir / "reports" / "prompt_change.md"
        if prompt_report.exists():
            prompt_lines.extend([f"## {iter_dir.name}", "", f"See `{prompt_report.relative_to(run_dir).as_posix()}`.", ""])
            acceptance_path = iter_dir / "decision" / "acceptance.json"
            if acceptance_path.exists():
                acceptance = json.loads(read_text(acceptance_path))
                acceptance_rows.append(
                    "| "
                    + " | ".join(
                        [
                            iter_dir.name,
                            str(acceptance.get("accepted")),
                            str(acceptance.get("acceptance_mode", "-")),
                            ", ".join(acceptance.get("rejection_reasons", [])) or "none",
                        ]
                    )
                    + " |"
                )
                prompt_lines.extend(
                    [
                        f"- accepted: {acceptance.get('accepted')}",
                        f"- acceptance_mode: {acceptance.get('acceptance_mode', '-')}",
                        f"- candidate_evidence_family: {acceptance.get('candidate_evidence_family') or '-'}",
                        f"- direct_metric: {acceptance.get('direct_metric') or '-'}",
                        f"- rejection_reasons: {', '.join(acceptance.get('rejection_reasons', [])) or 'none'}",
                        "",
                    ]
                )
        test_summary_path = iter_dir / "test" / "summary.json"
        if test_summary_path.exists():
            metrics_lines.append(metric_row(f"{iter_dir.name}:test", json.loads(read_text(test_summary_path))))
            has_iteration_test_metrics = True

    final_path = run_dir / "prompt_final.md"
    if final_path.exists():
        prompt_lines.extend(["## Final Prompt", "", "```markdown", read_text(final_path).rstrip(), "```", ""])

    test_summary_path = run_dir / "test" / "summary.json"
    if test_summary_path.exists() and not has_iteration_test_metrics:
        metrics_lines.append(metric_row("held_out_test", json.loads(read_text(test_summary_path))))

    if len(acceptance_rows) > 5:
        metrics_lines.extend(acceptance_rows)

    write_text(run_dir / "prompt_evolution.md", "\n".join(prompt_lines).rstrip() + "\n")
    write_text(run_dir / "metrics_overview.md", "\n".join(metrics_lines).rstrip() + "\n")
