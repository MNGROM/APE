"""Failure-analysis agent and human-readable evaluation report."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from analysis.error_selector import (
    FAILURE_ERRORS_SCHEMA,
    FINDING_BUDGET,
    FailureAnalysisValidationResult,
    build_failure_analysis_input,
    validate_failure_errors,
)
from llm import LLMClient
from metrics import EvaluationRecord, relation_text
from prompt_ops import extract_json_object
from utils.io import read_prompt_file, write_text


def build_analysis(
    records: list[EvaluationRecord],
    summary: dict[str, float],
    max_cases: int | None = None,
) -> str:
    failure_counter = Counter(ft for record in records for ft in record.failure_types)
    failed_records = [
        record
        for record in records
        if record.failure_types and "infrastructure_error" not in record.failure_types
    ]
    infrastructure_records = [
        record for record in records if "infrastructure_error" in record.failure_types
    ]
    limit = max_cases if max_cases is not None and max_cases > 0 else len(failed_records)
    infrastructure_limit = (
        max_cases
        if max_cases is not None and max_cases > 0
        else len(infrastructure_records)
    )
    representative = sorted(
        failed_records,
        key=lambda record: (
            1 if record.syntax.passed else 0,
            record.llm_element_metrics.node_metrics.f1
            if record.llm_element_metrics.status == "success"
            else 0.0,
            record.llm_element_metrics.relation_metrics.f1
            if record.llm_element_metrics.status == "success"
            else 0.0,
        ),
    )[:limit]

    lines = ["# Prompt Evaluation Analysis", "", "## Summary"]
    for key, value in summary.items():
        lines.append(f"- {key}: {int(value)}" if key == "count" else f"- {key}: {value:.4f}")
    lines.extend(["", "## Failure Types"])
    if failure_counter:
        lines.extend(f"- {failure}: {count}" for failure, count in failure_counter.most_common())
    else:
        lines.append("- none")

    if infrastructure_records:
        lines.extend(
            [
                "",
                "## Infrastructure Errors",
                f"- count: {len(infrastructure_records)}",
                "- These cases failed before a model output was available. Do not modify the prompt based only on infrastructure errors.",
            ]
        )
        for record in infrastructure_records[:infrastructure_limit]:
            error = " | ".join(record.syntax.errors[:3]) if record.syntax.errors else "unknown"
            lines.append(f"- {record.case_id}: {error}")

    lines.extend(["", "## Representative Failure Cases"])
    if not representative:
        lines.extend(["- none", ""])
    for record in representative:
        lines.extend(
            [
                f"### {record.case_id}",
                f"- dataset: {record.dataset}",
                f"- failure_types: {', '.join(record.failure_types) if record.failure_types else 'none'}",
                f"- syntax_passed: {record.syntax.passed}",
            ]
        )
        if record.syntax.errors:
            lines.append(f"- syntax_errors: {' | '.join(record.syntax.errors[:5])}")
        lines.append(f"- plantuml_compiles: {record.plantuml_compilation.passed}")
        if record.plantuml_compilation.errors:
            lines.append(
                f"- plantuml_compile_errors: {' | '.join(record.plantuml_compilation.errors[:5])}"
            )
        if record.llm_element_metrics.enabled:
            lines.append(f"- llm_element_status: {record.llm_element_metrics.status}")
            if record.llm_element_metrics.status == "success":
                lines.extend(
                    [
                        f"- llm_node_f1: {record.llm_element_metrics.node_metrics.f1:.4f}",
                        f"- llm_relation_f1: {record.llm_element_metrics.relation_metrics.f1:.4f}",
                    ]
                )
            elif record.llm_element_metrics.error:
                lines.append(f"- llm_element_error: {record.llm_element_metrics.error[:300]}")
        else:
            lines.append("- llm_element_status: disabled")

        matching = record.llm_element_metrics.matching
        nodes = matching.get("nodes", {}) if isinstance(matching.get("nodes"), dict) else {}
        relations = (
            matching.get("relations", {})
            if isinstance(matching.get("relations"), dict)
            else {}
        )
        for label, values in (
            ("llm_missing_nodes", nodes.get("fn") or []),
            ("llm_extra_nodes", nodes.get("fp") or []),
        ):
            if values:
                lines.append(f"- {label}:")
                lines.extend(f"  - {item}" for item in values[:8])
        for label, values in (
            ("llm_missing_relations", relations.get("fn") or []),
            ("llm_extra_relations", relations.get("fp") or []),
        ):
            if values:
                lines.append(f"- {label}:")
                lines.extend(f"  - {relation_text(item)}" for item in values[:8])
        if record.node_metrics.matcher != "disabled":
            lines.extend(
                [
                    f"- embedding_node_f1: {record.node_metrics.f1:.4f}",
                    f"- embedding_relation_f1: {record.relation_metrics.f1:.4f}",
                ]
            )
        lines.extend(
            [
                "- input_excerpt:",
                "  " + record.input_requirement[:700].replace("\n", " "),
                "- generated_excerpt:",
                "  " + record.generated_plantuml[:700].replace("\n", " "),
            ]
        )

    lines.extend(["", "## Prompt Improvement Guidance"])
    if records and len(infrastructure_records) == len(records):
        lines.append(
            "- All evaluated cases failed due to infrastructure errors. Do not change the prompt for this iteration."
        )
    lines.extend(
        [
            "- Modify only the run-local `work.md` prompt.",
            "- Preserve the required markdown sections.",
            "- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.",
            "- Target the most frequent failure types first and avoid overfitting to a single case.",
            "",
        ]
    )
    return "\n".join(lines)


def analyze_failures(
    *,
    current_prompt: str,
    records: list[EvaluationRecord],
    summary: dict[str, float],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    raw_output_path: Path,
    rejected_patterns_path: Path,
    state_dir: Path | None,
    iteration: int,
    batch_id: int = 0,
    generation_run: str = "run",
) -> FailureAnalysisValidationResult:
    del current_prompt, summary
    payload = build_failure_analysis_input(
        records,
        generation_run=generation_run,
        iteration=iteration,
        batch_id=batch_id,
        finding_budget=FINDING_BUDGET,
    )
    agent_payload = {
        "schema_version": payload["schema_version"],
        "cases": [
            {
                **{key: value for key, value in case.items() if key != "findings"},
                "findings": [
                    {key: value for key, value in finding.items() if key != "finding_key"}
                    for finding in case.get("findings", [])
                ],
            }
            for case in payload.get("cases", [])
        ],
    }
    write_text(output_input_path, json.dumps(agent_payload, ensure_ascii=False, indent=2))

    if not agent_payload["cases"]:
        automatic_errors = [
            item for item in payload.get("_automatic_errors", []) if isinstance(item, dict)
        ]
        if automatic_errors:
            normalized = {
                "schema_version": FAILURE_ERRORS_SCHEMA,
                "errors": automatic_errors,
            }
            write_text(raw_output_path, "No LLM findings; Python recorded generic diagnostics.\n")
            write_text(rejected_patterns_path, "[]\n")
            write_text(output_path, json.dumps(normalized, ensure_ascii=False, indent=2))
            return FailureAnalysisValidationResult(normalized, [], [])
        result = FailureAnalysisValidationResult(
            None,
            [],
            ["No eligible findings for failure analysis"],
        )
        write_text(raw_output_path, "No eligible findings for failure analysis.\n")
        write_text(rejected_patterns_path, "[]\n")
        return result

    raw = llm_client.chat(
        [
            {
                "role": "system",
                "content": read_prompt_file(
                    args.failure_analysis_prompt_path, label="failure analysis"
                ),
            },
            {
                "role": "user",
                "content": json.dumps(agent_payload, ensure_ascii=False, indent=2),
            },
        ],
        temperature=args.analysis_temperature,
        max_tokens=args.analysis_max_tokens,
        thinking=args.analysis_thinking,
        state_dir=state_dir,
        retry_phase="failure_analysis",
        retry_context={"iteration": iteration, "output_path": str(output_path)},
    )
    write_text(raw_output_path, raw)
    parsed = extract_json_object(raw)
    if parsed is None:
        result = FailureAnalysisValidationResult(
            None,
            [],
            ["Failure analysis did not return a JSON object"],
        )
        write_text(rejected_patterns_path, "[]\n")
        write_text(output_path.with_suffix(".rejected.txt"), result.fatal_errors[0] + "\n")
        return result

    result = validate_failure_errors(parsed, input_payload=payload)
    write_text(
        rejected_patterns_path,
        json.dumps(result.rejected_patterns, ensure_ascii=False, indent=2),
    )
    if result.normalized_payload is None:
        errors = [
            *result.fatal_errors,
            *[
                error
                for rejected in result.rejected_patterns
                for error in rejected.get("errors", [])
            ],
        ]
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected failure analysis: {'; '.join(errors)}", flush=True)
        return result

    write_text(
        output_path,
        json.dumps(result.normalized_payload, ensure_ascii=False, indent=2),
    )
    return result
