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
    "node_f1",
    "relation_f1",
    "node_precision",
    "node_recall",
    "relation_precision",
    "relation_recall",
    "infrastructure_error_rate",
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


def first_existing(*paths: Path) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def read_json_first(*paths: Path) -> Any | None:
    path = first_existing(*paths)
    if path is None:
        return None
    return read_json_if_exists(path)


def read_text_first(*paths: Path) -> str | None:
    path = first_existing(*paths)
    if path is None:
        return None
    return read_text_if_exists(path)


def refresh_iteration_report(iter_dir: Path) -> None:
    if not iter_dir.is_dir():
        return
    suffix = iter_dir.name.rsplit("_", 1)[-1]
    try:
        iteration = int(suffix)
    except ValueError:
        iteration = 0

    prompt_before = read_text_first(iter_dir / "prompts" / "before.md", iter_dir / "prompt_before.md")
    prompt_after = read_text_first(iter_dir / "prompts" / "after.md", iter_dir / "prompt_after.md")
    if prompt_before is None or prompt_after is None:
        return

    candidate_prompt = read_text_first(iter_dir / "prompts" / "candidate.md", iter_dir / "candidate_prompt.md", iter_dir / "prompt_candidate.md")
    analysis_summary = read_json_first(iter_dir / "evaluation" / "analysis_summary.json", iter_dir / "evaluation_summary.json", iter_dir / "train_summary.json") or {}
    baseline_gate_summary = read_json_first(iter_dir / "evaluation" / "gate_baseline_summary.json", iter_dir / "baseline_gate_summary.json")
    candidate_summary = read_json_first(iter_dir / "evaluation" / "gate_candidate_summary.json", iter_dir / "candidate_summary.json", iter_dir / "gate_summary.json")
    acceptance = read_json_first(iter_dir / "decision" / "acceptance.json", iter_dir / "prompt_acceptance.json")

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
    acceptance_mode = acceptance.get("acceptance_mode") if acceptance else "not_evaluated"
    rejection_reasons = acceptance.get("rejection_reasons", []) if acceptance else []

    prompt_lines = [
        f"# Iteration {iteration:03d} Prompt Change",
        "",
        f"- accepted: {accepted}",
        f"- acceptance_mode: {acceptance_mode}",
        f"- rejection_reasons: {', '.join(rejection_reasons) if rejection_reasons else 'none'}",
        f"- chars_before: {len(prompt_before)}",
        f"- chars_after: {len(prompt_after)}",
    ]
    if candidate_prompt is not None:
        prompt_lines.append(f"- chars_candidate: {len(candidate_prompt)}")
    prompt_lines.extend(["", "## Applied Change", ""])
    applied_diff = prompt_diff(prompt_before, prompt_after, from_label="prompt_before.md", to_label="prompt_after.md")
    prompt_lines.append("```diff")
    prompt_lines.append(applied_diff or "# no applied prompt change")
    prompt_lines.append("```")
    if candidate_prompt is not None and not accepted:
        prompt_lines.extend(["", "## Rejected Candidate Diff", "", "```diff"])
        prompt_lines.append(prompt_diff(prompt_before, candidate_prompt, from_label="prompt_before.md", to_label="prompt_candidate.md") or "# no candidate prompt change")
        prompt_lines.append("```")
    write_text(iter_dir / "reports" / "prompt_change.md", "\n".join(prompt_lines).rstrip() + "\n")

    metric_lines = [
        f"# Iteration {iteration:03d} Metrics",
        "",
        f"- accepted: {accepted}",
        f"- acceptance_mode: {acceptance_mode}",
        f"- rejection_reasons: {', '.join(rejection_reasons) if rejection_reasons else 'none'}",
        "",
        "## Summaries",
        "",
        *metrics_table_header(),
        metric_row("analysis_current", analysis_summary),
        metric_row("gate_baseline", baseline_gate_summary),
        metric_row("gate_candidate", candidate_summary),
    ]
    if acceptance:
        metric_lines.extend(["", "## Deltas", "", *metrics_table_header()])
        metric_lines.append(metric_delta_row("candidate_minus_baseline", metric_deltas(baseline_gate_summary, candidate_summary)))
        metric_lines.extend(
            [
                "",
                "## Gates",
                "",
                "```json",
                json.dumps(
                    {
                        "safety_gate": acceptance.get("safety_gate"),
                        "benefit_gate": acceptance.get("benefit_gate"),
                        "bootstrap_gate": acceptance.get("bootstrap_gate"),
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                "```",
            ]
        )
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

    for iter_dir in sorted(run_dir.glob("iteration_*")):
        prompt_report = first_existing(iter_dir / "reports" / "prompt_change.md", iter_dir / "prompt_change.md")
        metrics_report = first_existing(iter_dir / "reports" / "metrics_report.md", iter_dir / "metrics_report.md")
        if prompt_report and prompt_report.exists():
            prompt_lines.extend([f"## {iter_dir.name}", "", f"See `{prompt_report.relative_to(run_dir).as_posix()}`.", ""])
            acceptance_path = first_existing(iter_dir / "decision" / "acceptance.json", iter_dir / "prompt_acceptance.json")
            if acceptance_path and acceptance_path.exists():
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
                        f"- rejection_reasons: {', '.join(acceptance.get('rejection_reasons', [])) or 'none'}",
                        "",
                    ]
                )
        if metrics_report and metrics_report.exists():
            summary_path = first_existing(iter_dir / "evaluation" / "analysis_summary.json", iter_dir / "evaluation_summary.json")
            if summary_path and summary_path.exists():
                metrics_lines.append(metric_row(f"{iter_dir.name}:analysis_current", json.loads(read_text(summary_path))))
            baseline_path = first_existing(iter_dir / "evaluation" / "gate_baseline_summary.json", iter_dir / "baseline_gate_summary.json")
            if baseline_path and baseline_path.exists():
                metrics_lines.append(metric_row(f"{iter_dir.name}:gate_baseline", json.loads(read_text(baseline_path))))
            candidate_path = first_existing(iter_dir / "evaluation" / "gate_candidate_summary.json", iter_dir / "candidate_summary.json", iter_dir / "gate_summary.json")
            if candidate_path and candidate_path.exists():
                metrics_lines.append(metric_row(f"{iter_dir.name}:gate_candidate", json.loads(read_text(candidate_path))))

    best_path = run_dir / "prompt_best.md"
    final_path = run_dir / "prompt_final.md"
    if best_path.exists():
        prompt_lines.extend(["## Best Prompt", "", "```markdown", read_text(best_path).rstrip(), "```", ""])
    if final_path.exists():
        prompt_lines.extend(["## Final Prompt", "", "```markdown", read_text(final_path).rstrip(), "```", ""])

    test_summary_path = first_existing(run_dir / "test" / "summary.json", run_dir / "test_summary.json")
    if test_summary_path and test_summary_path.exists():
        metrics_lines.append(metric_row("held_out_test", json.loads(read_text(test_summary_path))))

    if len(acceptance_rows) > 5:
        metrics_lines.extend(acceptance_rows)

    write_text(run_dir / "prompt_evolution.md", "\n".join(prompt_lines).rstrip() + "\n")
    write_text(run_dir / "metrics_overview.md", "\n".join(metrics_lines).rstrip() + "\n")
