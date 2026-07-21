"""Failure analysis agent and human-readable analysis report."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from analysis.mechanism_clustering import (
    ALLOWED_ANCHOR_FIELDS,
    ANCHOR_FIELD_TO_KIND,
    ATOMIC_SCHEMA_VERSION,
    FailureAnalysisValidationResult,
    load_mechanism_taxonomy,
    make_case_evidence_id,
    validate_failure_analysis_payload,
)
from llm import LLMClient
from metrics import EvaluationRecord, relation_text
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
    "llm_element_judge_error": "The LLM-judge element metric failed; this means the primary training signal is unavailable for this case.",
}

ATOMIC_ANCHOR_BUDGET = 12
ATOMIC_ANCHOR_FIELDS = tuple(ANCHOR_FIELD_TO_KIND)
ATOMIC_ANCHOR_FIELD_PRIORITY = {
    "compile_errors": 0,
    "syntax_errors": 1,
    "llm_extra_nodes": 2,
    "llm_missing_nodes": 3,
    "llm_extra_relations": 4,
    "llm_missing_relations": 5,
}
PRIMARY_DIRECTIONS_BY_ANCHOR_FIELD = {
    field: sorted(
        direction
        for direction, allowed_fields in ALLOWED_ANCHOR_FIELDS.items()
        if field in allowed_fields
    )
    for field in ATOMIC_ANCHOR_FIELDS
}
PRIMARY_DIRECTIONS_BY_ANCHOR_FIELD["compile_errors"] = ["syntax_or_format_error"]
PRIMARY_DIRECTIONS_BY_ANCHOR_FIELD["syntax_errors"] = ["syntax_or_format_error"]


def _canonical_match_value(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, dict) else str(value)


def matching_quality(record: EvaluationRecord) -> dict[str, Any]:
    if record.llm_element_metrics.status != "success":
        return {"status": "unavailable", "reasons": [record.llm_element_metrics.status]}
    reasons: list[str] = []
    matching = record.llm_element_metrics.matching
    for family in ("nodes", "relations"):
        group = matching.get(family, {}) if isinstance(matching.get(family), dict) else {}
        pred_values: list[str] = []
        gt_values: list[str] = []
        for item in group.get("tp") or []:
            if not isinstance(item, dict) or "pred" not in item or "gt" not in item:
                reasons.append(f"{family}_tp_malformed")
                continue
            pred_values.append(_canonical_match_value(item["pred"]))
            gt_values.append(_canonical_match_value(item["gt"]))
        if len(pred_values) != len(set(pred_values)):
            reasons.append(f"{family}_prediction_matches_multiple_gold")
        if len(gt_values) != len(set(gt_values)):
            reasons.append(f"{family}_gold_matches_multiple_predictions")
    return {
        "status": "non_bijective" if reasons else "valid",
        "reasons": sorted(set(reasons)),
    }


def _atomic_anchor_scores(record: EvaluationRecord) -> dict[str, float]:
    metrics = record.llm_element_metrics
    node_matching = (
        metrics.matching.get("nodes", {})
        if isinstance(metrics.matching.get("nodes"), dict)
        else {}
    )
    if metrics.status == "success":
        missing_nodes_present = bool(node_matching.get("fn"))
        extra_nodes_present = bool(node_matching.get("fp"))
        scores = {
            "llm_missing_nodes": 1.0 + (1.0 - float(metrics.node_metrics.recall)),
            "llm_extra_nodes": 1.0 + (1.0 - float(metrics.node_metrics.precision)),
            "llm_missing_relations": (
                0.5 if missing_nodes_present else 1.0
            )
            + (1.0 - float(metrics.relation_metrics.recall)),
            "llm_extra_relations": (
                0.5 if extra_nodes_present else 1.0
            )
            + (1.0 - float(metrics.relation_metrics.precision)),
        }
    else:
        scores = {
            "llm_missing_nodes": 0.0,
            "llm_extra_nodes": 0.0,
            "llm_missing_relations": 0.0,
            "llm_extra_relations": 0.0,
        }
    scores["compile_errors"] = 3.0 if not record.plantuml_compilation.passed else 0.0
    scores["syntax_errors"] = 2.9 if not record.syntax.passed else 0.0
    return scores


def _atomic_candidates_for_case(
    record: EvaluationRecord,
    case: dict[str, Any],
) -> list[dict[str, Any]]:
    occurrences: Counter[str] = Counter()
    for field in ATOMIC_ANCHOR_FIELDS:
        occurrences.update(str(value) for value in case.get(field, []))
    scores = _atomic_anchor_scores(record)
    matching_valid = case.get("matching_quality", {}).get("status") == "valid"
    candidates: list[dict[str, Any]] = []
    for field in ATOMIC_ANCHOR_FIELDS:
        for field_index, value in enumerate(case.get(field, [])):
            anchor = str(value)
            if not anchor or occurrences[anchor] != 1:
                continue
            anchor_kind = ANCHOR_FIELD_TO_KIND[field]
            candidates.append(
                {
                    "error_anchor": anchor,
                    "anchor_kind": anchor_kind,
                    "allowed_primary_failure_directions": PRIMARY_DIRECTIONS_BY_ANCHOR_FIELD[field],
                    "primary_allowed_by_matching": matching_valid,
                    "direct_node_anchor": anchor_kind in {"missing_node", "extra_node"},
                    "_source_field": field,
                    "_score": scores[field],
                    "_field_index": field_index,
                }
            )
    candidates.sort(
        key=lambda item: (
            -float(item["_score"]),
            ATOMIC_ANCHOR_FIELD_PRIORITY[item["_source_field"]],
            int(item["_field_index"]),
            str(item["error_anchor"]),
        )
    )
    return candidates


def _apply_atomic_anchor_budget(
    records_and_evidence: list[tuple[EvaluationRecord, dict[str, Any]]],
    *,
    budget: int,
) -> tuple[list[dict[str, Any]], int]:
    per_case = [
        (case, _atomic_candidates_for_case(record, case))
        for record, case in records_and_evidence
    ]
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    depth = 0
    while len(selected) < budget:
        added = False
        for case, candidates in per_case:
            if depth < len(candidates):
                selected.append((case, candidates[depth]))
                added = True
                if len(selected) == budget:
                    break
        if not added:
            break
        depth += 1

    selected_by_evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case, candidate in selected:
        selected_by_evidence[str(case["evidence_id"])].append(candidate)

    narrowed_cases: list[dict[str, Any]] = []
    for _, case in records_and_evidence:
        selected_candidates = selected_by_evidence.get(str(case["evidence_id"]), [])
        if not selected_candidates:
            continue
        narrowed = dict(case)
        selected_by_field: dict[str, list[str]] = defaultdict(list)
        public_candidates: list[dict[str, Any]] = []
        for candidate in selected_candidates:
            selected_by_field[candidate["_source_field"]].append(candidate["error_anchor"])
            public_candidates.append(
                {
                    key: value
                    for key, value in candidate.items()
                    if not key.startswith("_")
                }
            )
        for field in ATOMIC_ANCHOR_FIELDS:
            narrowed[field] = selected_by_field.get(field, [])
        narrowed["attribution_candidates"] = public_candidates
        narrowed_cases.append(narrowed)
    return narrowed_cases, len(selected)


def build_analysis(records: list[EvaluationRecord], summary: dict[str, float], max_cases: int | None = None) -> str:
    failure_counter = Counter(ft for r in records for ft in r.failure_types)
    failed_records = [r for r in records if r.failure_types and "infrastructure_error" not in r.failure_types]
    infra_records = [r for r in records if "infrastructure_error" in r.failure_types]
    representative_limit = max_cases if max_cases is not None and max_cases > 0 else len(failed_records)
    infra_limit = max_cases if max_cases is not None and max_cases > 0 else len(infra_records)
    worst = sorted(
        failed_records,
        key=lambda r: (
            1 if r.syntax.passed else 0,
            r.llm_element_metrics.node_metrics.f1 if r.llm_element_metrics.status == "success" else 0.0,
            r.llm_element_metrics.relation_metrics.f1 if r.llm_element_metrics.status == "success" else 0.0,
        ),
    )[:representative_limit]

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
        for record in infra_records[:infra_limit]:
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
        if record.llm_element_metrics.enabled:
            lines.append(f"- llm_element_status: {record.llm_element_metrics.status}")
            if record.llm_element_metrics.status == "success":
                lines.append(f"- llm_node_f1: {record.llm_element_metrics.node_metrics.f1:.4f}")
                lines.append(f"- llm_relation_f1: {record.llm_element_metrics.relation_metrics.f1:.4f}")
            elif record.llm_element_metrics.error:
                lines.append(f"- llm_element_error: {record.llm_element_metrics.error[:300]}")
        else:
            lines.append("- llm_element_status: disabled")
        node_matching = record.llm_element_metrics.matching.get("nodes", {}) if isinstance(record.llm_element_metrics.matching.get("nodes"), dict) else {}
        relation_matching = record.llm_element_metrics.matching.get("relations", {}) if isinstance(record.llm_element_metrics.matching.get("relations"), dict) else {}
        missing_nodes = node_matching.get("fn") or []
        extra_nodes = node_matching.get("fp") or []
        missing_relations = relation_matching.get("fn") or []
        extra_relations = relation_matching.get("fp") or []
        if missing_nodes:
            lines.append("- llm_missing_nodes:")
            for item in missing_nodes[:8]:
                lines.append(f"  - {item}")
        if extra_nodes:
            lines.append("- llm_extra_nodes:")
            for item in extra_nodes[:8]:
                lines.append(f"  - {item}")
        if missing_relations:
            lines.append("- llm_missing_relations:")
            for item in missing_relations[:8]:
                lines.append(f"  - {relation_text(item)}")
        if extra_relations:
            lines.append("- llm_extra_relations:")
            for item in extra_relations[:8]:
                lines.append(f"  - {relation_text(item)}")
        if record.node_metrics.matcher != "disabled":
            lines.append(f"- embedding_node_f1: {record.node_metrics.f1:.4f}")
            lines.append(f"- embedding_relation_f1: {record.relation_metrics.f1:.4f}")
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


def failure_analysis_payload(
    records: list[EvaluationRecord],
    summary: dict[str, float],
    max_cases: int | None = None,
    *,
    generation_run: str = "run",
    iteration: int = 0,
    batch_id: int = 0,
    atomic_anchor_budget: int | None = None,
) -> dict[str, Any]:
    failed_records = [r for r in records if r.failure_types and "infrastructure_error" not in r.failure_types]
    limit = max_cases if max_cases is not None and max_cases > 0 else len(failed_records)
    representative = sorted(
        failed_records,
        key=lambda r: (
            1 if r.syntax.passed else 0,
            r.llm_element_metrics.node_metrics.f1 if r.llm_element_metrics.status == "success" else 0.0,
            r.llm_element_metrics.relation_metrics.f1 if r.llm_element_metrics.status == "success" else 0.0,
        ),
    )[:limit]
    records_and_evidence: list[tuple[EvaluationRecord, dict[str, Any]]] = []
    for record in representative:
        node_matching = record.llm_element_metrics.matching.get("nodes", {}) if isinstance(record.llm_element_metrics.matching.get("nodes"), dict) else {}
        relation_matching = record.llm_element_metrics.matching.get("relations", {}) if isinstance(record.llm_element_metrics.matching.get("relations"), dict) else {}
        case = {
            "evidence_id": make_case_evidence_id(
                generation_run=generation_run,
                iteration=iteration,
                batch_id=batch_id,
                dataset=record.dataset,
                case_id=record.case_id,
            ),
            "dataset": record.dataset,
            "case_id": record.case_id,
            "failure_types": record.failure_types,
            "syntax_passed": record.syntax.passed,
            "plantuml_compiles": record.plantuml_compilation.passed,
            "llm_element_status": record.llm_element_metrics.status,
            "llm_node_f1": record.llm_element_metrics.node_metrics.f1,
            "llm_relation_f1": record.llm_element_metrics.relation_metrics.f1,
            "llm_counts": record.llm_element_metrics.counts,
            "matching_quality": matching_quality(record),
            "llm_missing_nodes": (node_matching.get("fn") or [])[:12],
            "llm_extra_nodes": (node_matching.get("fp") or [])[:12],
            "llm_missing_relations": [
                relation_text(item) for item in (relation_matching.get("fn") or [])[:12]
            ],
            "llm_extra_relations": [
                relation_text(item) for item in (relation_matching.get("fp") or [])[:12]
            ],
            "syntax_errors": (
                [str(item) for item in record.syntax.errors[:12]]
                if record.syntax.errors
                else (["syntax_failed_without_detail"] if not record.syntax.passed else [])
            ),
            "compile_errors": (
                [str(item) for item in record.plantuml_compilation.errors[:12]]
                if record.plantuml_compilation.errors
                else (
                    ["compile_failed_without_detail"]
                    if not record.plantuml_compilation.passed
                    else []
                )
            ),
            "requirement": record.input_requirement,
            "prediction": record.generated_plantuml,
            "ground_truth": record.gold_plantuml,
        }
        records_and_evidence.append((record, case))
    case_evidence = [case for _, case in records_and_evidence]
    attribution_budget = None
    if atomic_anchor_budget is not None:
        case_evidence, attribution_budget = _apply_atomic_anchor_budget(
            records_and_evidence,
            budget=max(1, int(atomic_anchor_budget)),
        )
    payload = {
        "metric_source": "llm_judge",
        "summary": summary,
        "failure_type_guide": FAILURE_TYPE_GUIDE,
        "case_evidence": case_evidence,
    }
    if attribution_budget is not None:
        payload["attribution_budget"] = attribution_budget
    return payload


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
    taxonomy_path = getattr(args, "mechanism_taxonomy_path", None)
    taxonomy_version = None
    if taxonomy_path is not None:
        taxonomy_version = load_mechanism_taxonomy(Path(taxonomy_path))["version"]
    payload = failure_analysis_payload(
        records,
        summary,
        generation_run=generation_run,
        iteration=iteration,
        batch_id=batch_id,
        atomic_anchor_budget=(
            ATOMIC_ANCHOR_BUDGET if taxonomy_version == "v3" else None
        ),
    )
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
    write_text(raw_output_path, raw)
    parsed = extract_json_object(raw)
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "Failure analysis did not return a JSON object.\n")
        result = FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=[],
            fatal_errors=["Failure analysis did not return a JSON object"],
        )
        write_text(rejected_patterns_path, "[]\n")
        return result
    required_schema_version = None
    if taxonomy_version == "v3":
        required_schema_version = ATOMIC_SCHEMA_VERSION
    result = validate_failure_analysis_payload(
        parsed,
        evidence_catalog=payload["case_evidence"],
        required_schema_version=required_schema_version,
    )
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
    write_text(output_path, json.dumps(result.normalized_payload, ensure_ascii=False, indent=2))
    return result
