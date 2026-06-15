"""Failure analysis agent and human-readable analysis report."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from llm import LLMClient
from metrics import EvaluationRecord
from prompt_ops import extract_json_object
from utils.io import read_prompt_file, write_text


FAILURE_TYPE_GUIDE: dict[str, str] = {
    "syntax_error": "The generated text is not syntactically valid PlantUML or is missing required PlantUML wrappers.",
    "missing_activity": "The prediction omits activities or states that appear in the ground truth; triggered by low node recall.",
    "extra_activity": "The prediction adds unsupported activities or states; triggered by low node precision.",
    "missing_or_wrong_relation": "The prediction omits or misrepresents control-flow relations; triggered by low relation recall.",
    "extra_or_wrong_relation": "The prediction adds unsupported or incorrect control-flow relations; triggered by low relation precision.",
    "wrong_parallel": "The prediction likely mishandles parallel/concurrent behavior.",
    "wrong_loop": "The prediction likely mishandles repeated, periodic, retry, or loop behavior.",
    "generation_error": "The generation call failed before a usable prediction was produced.",
    "infrastructure_error": "The failure is caused by provider, network, timeout, Java, or other infrastructure issues rather than the prompt.",
    "llm_element_judge_error": "The optional LLM element metric failed; this is a diagnostic-metric issue rather than direct PlantUML generation behavior.",
}


def build_analysis(records: list[EvaluationRecord], summary: dict[str, float], max_cases: int) -> str:
    failure_counter = Counter(ft for r in records for ft in r.failure_types)
    failed_records = [r for r in records if r.failure_types and "infrastructure_error" not in r.failure_types]
    infra_records = [r for r in records if "infrastructure_error" in r.failure_types]
    worst = sorted(
        failed_records,
        key=lambda r: (
            1 if r.syntax.passed else 0,
            r.node_metrics.f1,
            r.relation_metrics.f1,
        ),
    )[:max_cases]

    lines: list[str] = []
    lines.append("# Prompt Evaluation Analysis")
    lines.append("")
    lines.append("## Summary")
    for key, value in summary.items():
        if key == "count":
            lines.append(f"- {key}: {int(value)}")
        else:
            lines.append(f"- {key}: {value:.4f}")
    lines.append("")
    lines.append("## Failure Types")
    if failure_counter:
        for failure, count in failure_counter.most_common():
            lines.append(f"- {failure}: {count}")
    else:
        lines.append("- none")
    if infra_records:
        lines.append("")
        lines.append("## Infrastructure Errors")
        lines.append(f"- count: {len(infra_records)}")
        lines.append("- These cases failed before a model output was available. Do not modify the prompt based only on infrastructure errors.")
        for record in infra_records[:max_cases]:
            err = " | ".join(record.syntax.errors[:3]) if record.syntax.errors else "unknown"
            lines.append(f"- {record.case_id}: {err}")
    lines.append("")
    lines.append("## Representative Failure Cases")
    if not worst:
        lines.append("- none")
        lines.append("")
    for record in worst:
        lines.append(f"### {record.case_id}")
        lines.append(f"- dataset: {record.dataset}")
        lines.append(f"- failure_types: {', '.join(record.failure_types) if record.failure_types else 'none'}")
        lines.append(f"- syntax_passed: {record.syntax.passed}")
        if record.syntax.errors:
            lines.append(f"- syntax_errors: {' | '.join(record.syntax.errors[:5])}")
        lines.append(f"- plantuml_compiles: {record.plantuml_compilation.passed}")
        if record.plantuml_compilation.errors:
            lines.append(f"- plantuml_compile_errors: {' | '.join(record.plantuml_compilation.errors[:5])}")
        lines.append(f"- node_f1: {record.node_metrics.f1:.4f}")
        lines.append(f"- relation_f1: {record.relation_metrics.f1:.4f}")
        if record.llm_element_metrics.enabled:
            lines.append(f"- llm_element_status: {record.llm_element_metrics.status}")
            if record.llm_element_metrics.status == "success":
                lines.append(f"- llm_node_f1: {record.llm_element_metrics.node_metrics.f1:.4f}")
                lines.append(f"- llm_relation_f1: {record.llm_element_metrics.relation_metrics.f1:.4f}")
            elif record.llm_element_metrics.error:
                lines.append(f"- llm_element_error: {record.llm_element_metrics.error[:300]}")
        if record.node_metrics.missing:
            lines.append("- missing_nodes:")
            for item in record.node_metrics.missing[:8]:
                lines.append(f"  - {item}")
        if record.node_metrics.extra:
            lines.append("- extra_nodes:")
            for item in record.node_metrics.extra[:8]:
                lines.append(f"  - {item}")
        if record.relation_metrics.missing:
            lines.append("- missing_relations:")
            for item in record.relation_metrics.missing[:8]:
                lines.append(f"  - {item}")
        lines.append("- input_excerpt:")
        lines.append("  " + record.input_requirement[:700].replace("\n", " "))
        lines.append("- generated_excerpt:")
        lines.append("  " + record.generated_plantuml[:700].replace("\n", " "))
    lines.append("")

    lines.append("## Prompt Improvement Guidance")
    if len(infra_records) == len(records):
        lines.append("- All evaluated cases failed due to infrastructure errors. Do not change the prompt for this iteration.")
    lines.append("- Modify only the run-local `work.md` prompt.")
    lines.append("- Preserve the required markdown sections.")
    lines.append("- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.")
    lines.append("- Target the most frequent failure types first and avoid overfitting to a single case.")
    return "\n".join(lines) + "\n"


def failure_analysis_payload(records: list[EvaluationRecord], summary: dict[str, float], max_cases: int) -> dict[str, Any]:
    failed_records = [r for r in records if r.failure_types and "infrastructure_error" not in r.failure_types]
    representative = sorted(
        failed_records,
        key=lambda r: (
            1 if r.syntax.passed else 0,
            r.node_metrics.f1,
            r.relation_metrics.f1,
        ),
    )[:max_cases]
    return {
        "requirements": [r.input_requirement for r in representative],
        "predictions": [r.generated_plantuml for r in representative],
        "ground_truths": [r.gold_plantuml for r in representative],
        "failure_types": {
            "guide": FAILURE_TYPE_GUIDE,
            "by_case": [r.failure_types for r in representative],
        },
    }


def analyze_failures(
    *,
    current_prompt: str,
    records: list[EvaluationRecord],
    summary: dict[str, float],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    payload = failure_analysis_payload(records, summary, args.analysis_cases)
    write_text(output_input_path, json.dumps(payload, ensure_ascii=False, indent=2))
    messages = [
        {
            "role": "system",
            "content": read_prompt_file(args.failure_analysis_prompt_path, label="failure analysis"),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, indent=2),
        },
    ]
    raw = llm_client.chat(
        messages,
        temperature=args.analysis_temperature,
        max_tokens=args.analysis_max_tokens,
        thinking=args.analysis_thinking,
        state_dir=state_dir,
        retry_phase="failure_analysis",
        retry_context={"iteration": iteration, "output_path": str(output_path)},
    )
    write_text(output_path, raw)
    parsed = extract_json_object(raw)
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "Failure analysis did not return a JSON object.\n")
        return None
    return parsed
