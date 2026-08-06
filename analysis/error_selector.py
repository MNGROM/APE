"""Evidence-bound failure errors and taxonomy-blind epoch selection."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from llm import LLMClient
from metrics import EvaluationRecord, relation_text
from prompt_ops import extract_json_object
from utils.io import read_prompt_file, write_text


FAILURE_ANALYSIS_INPUT_SCHEMA = "failure-analysis-input-v2"
FAILURE_ERRORS_SCHEMA = "failure-errors-v2"
ERROR_SELECTOR_INPUT_SCHEMA = "error-selector-input-v2"
ERROR_SELECTOR_SCHEMA = "error-selector-v2"
FINDING_BUDGET = 12
FINDING_ID_STRIDE = 1000
ERROR_STATUSES = {"actionable", "secondary", "gold_only", "uncertain"}
SEMANTIC_FINDING_KINDS = (
    "missing_node",
    "extra_node",
    "missing_relation",
    "extra_relation",
)
DIAGNOSTIC_FINDING_KINDS = (
    "syntax_error",
    "compile_error",
)
REQUIRED_METRIC_BY_FINDING_KIND = {
    "missing_node": "llm_node_f1",
    "extra_node": "llm_node_f1",
    "missing_relation": "llm_relation_f1",
    "extra_relation": "llm_relation_f1",
    "syntax_error": "plantuml_compilation_pass_rate",
    "compile_error": "plantuml_compilation_pass_rate",
}
REQUIRED_METRIC_ORDER = (
    "llm_node_f1",
    "llm_relation_f1",
    "plantuml_compilation_pass_rate",
)
FINDING_KINDS = {
    "missing_node",
    "extra_node",
    "missing_relation",
    "extra_relation",
    "syntax_error",
    "compile_error",
}
FAILURE_ERROR_FIELDS = {
    "finding_id",
    "status",
    "primary_finding_id",
    "requirement_quote",
    "error_summary",
    "causal_rationale",
}
SELECTOR_FIELDS = {
    "schema_version",
    "error_groups",
    "selection_status",
    "selected_group_id",
    "selection_rationale",
}
SELECTOR_GROUP_FIELDS = {
    "local_group_id",
    "finding_ids",
    "group_summary",
    "shared_cause",
}
GENERIC_COMPILER_CUE = re.compile(
    r"^(?:error|syntaxerror|exception|some diagram description contains errors|compile_failed_without_detail|"
    r"syntax_failed_without_detail|plantuml exited with return code \d+)\.?$",
    re.IGNORECASE,
)


@dataclass
class FailureAnalysisValidationResult:
    normalized_payload: dict[str, Any] | None
    rejected_patterns: list[dict[str, Any]]
    fatal_errors: list[str]


def failure_analysis_item_count(payload: dict[str, Any] | None) -> int:
    errors = payload.get("errors") if isinstance(payload, dict) else None
    return len(errors) if isinstance(errors, list) else 0


def make_case_evidence_id(
    *, generation_run: str, iteration: int, batch_id: int, dataset: str, case_id: str
) -> str:
    safe_run = re.sub(r"[^A-Za-z0-9_.-]+", "_", generation_run.strip())
    return f"{safe_run}:i{iteration:03d}:b{batch_id:03d}:{dataset}:{case_id}"


def make_finding_key(
    *, dataset: str, case_id: str, anchor_kind: str, error_anchor: str
) -> str:
    canonical = f"{dataset}\n{case_id}\n{anchor_kind}\n{error_anchor}"
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]
    return f"finding_key_{digest}"


def _canonical_matching_quality(record: EvaluationRecord) -> str:
    metrics = record.llm_element_metrics
    if metrics.status != "success":
        return "not_available"
    reasons: list[str] = []
    matching = metrics.matching if isinstance(metrics.matching, dict) else {}
    for family in ("nodes", "relations"):
        group = matching.get(family, {}) if isinstance(matching.get(family), dict) else {}
        pred_values: list[str] = []
        gold_values: list[str] = []
        for item in group.get("tp") or []:
            if not isinstance(item, dict) or "pred" not in item or "gt" not in item:
                reasons.append(f"{family}_tp_malformed")
                continue
            pred_values.append(json.dumps(item["pred"], sort_keys=True, ensure_ascii=False))
            gold_values.append(json.dumps(item["gt"], sort_keys=True, ensure_ascii=False))
        if len(pred_values) != len(set(pred_values)):
            reasons.append(f"{family}_prediction_matches_multiple_gold")
        if len(gold_values) != len(set(gold_values)):
            reasons.append(f"{family}_gold_matches_multiple_predictions")
    return "non_bijective" if reasons else "bijective"


def _finding_anchor_quality(
    record: EvaluationRecord, *, anchor_kind: str, error_anchor: str
) -> str:
    if anchor_kind in {"syntax_error", "compile_error"}:
        return "not_applicable"
    metrics = record.llm_element_metrics
    if metrics.status != "success":
        return "unavailable"
    matching = metrics.matching if isinstance(metrics.matching, dict) else {}
    family = "nodes" if anchor_kind.endswith("node") else "relations"
    side = "gt" if anchor_kind.startswith("missing") else "pred"
    group = matching.get(family)
    if not isinstance(group, dict):
        return "unavailable"
    matched_anchors: list[str] = []
    for item in group.get("tp") or []:
        if not isinstance(item, dict) or side not in item:
            continue
        value = item[side]
        matched_anchors.append(
            relation_text(value) if family == "relations" else str(value)
        )
    return "ambiguous" if error_anchor in matched_anchors else "clear"


def _case_findings(
    record: EvaluationRecord,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    metrics = record.llm_element_metrics
    matching = metrics.matching if isinstance(metrics.matching, dict) else {}
    nodes = matching.get("nodes", {}) if isinstance(matching.get("nodes"), dict) else {}
    relations = (
        matching.get("relations", {})
        if isinstance(matching.get("relations"), dict)
        else {}
    )
    sources: list[tuple[str, str, list[str]]] = [
        ("missing_node", "llm_judge", [str(item) for item in nodes.get("fn") or []]),
        ("extra_node", "llm_judge", [str(item) for item in nodes.get("fp") or []]),
        (
            "missing_relation",
            "llm_judge",
            [relation_text(item) for item in relations.get("fn") or []],
        ),
        (
            "extra_relation",
            "llm_judge",
            [relation_text(item) for item in relations.get("fp") or []],
        ),
        ("compile_error", "compiler", [str(item) for item in record.plantuml_compilation.errors]),
        ("syntax_error", "syntax", [str(item) for item in record.syntax.errors]),
    ]
    if not record.plantuml_compilation.passed and not sources[4][2]:
        sources[4][2].append("compile_failed_without_detail")
    if not record.syntax.passed and not sources[5][2]:
        sources[5][2].append("syntax_failed_without_detail")

    findings: list[dict[str, Any]] = []
    automatic_diagnostics: list[dict[str, Any]] = []
    seen_anchors: set[str] = set()
    for anchor_kind, source, values in sources:
        for error_anchor in values:
            if not error_anchor or error_anchor in seen_anchors:
                continue
            seen_anchors.add(error_anchor)
            finding = {
                "finding_key": make_finding_key(
                    dataset=record.dataset,
                    case_id=record.case_id,
                    anchor_kind=anchor_kind,
                    error_anchor=error_anchor,
                ),
                "anchor_kind": anchor_kind,
                "error_anchor": error_anchor,
                "source": source,
                "anchor_quality": _finding_anchor_quality(
                    record,
                    anchor_kind=anchor_kind,
                    error_anchor=error_anchor,
                ),
            }
            if anchor_kind in {"compile_error", "syntax_error"} and GENERIC_COMPILER_CUE.match(
                error_anchor.strip()
            ):
                automatic_diagnostics.append(finding)
            else:
                findings.append(finding)
    return findings, automatic_diagnostics


def _kind_queue(
    cases_with_findings: list[tuple[dict[str, Any], list[dict[str, Any]]]],
    anchor_kind: str,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    per_case = [
        (case, [item for item in findings if item["anchor_kind"] == anchor_kind])
        for case, findings in cases_with_findings
    ]
    queue: list[tuple[dict[str, Any], dict[str, Any]]] = []
    depth = 0
    while True:
        added = False
        for case, findings in per_case:
            if depth < len(findings):
                queue.append((case, findings[depth]))
                added = True
        if not added:
            return queue
        depth += 1


def build_failure_analysis_input(
    records: list[EvaluationRecord],
    *,
    generation_run: str,
    iteration: int,
    batch_id: int,
    finding_budget: int = FINDING_BUDGET,
) -> dict[str, Any]:
    budget = max(1, int(finding_budget))
    if budget >= FINDING_ID_STRIDE:
        raise ValueError("finding_budget must be smaller than FINDING_ID_STRIDE")
    cases_with_findings: list[tuple[dict[str, Any], list[dict[str, Any]]]] = []
    automatic_by_case: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for record in records:
        if "infrastructure_error" in record.failure_types or not record.failure_types:
            continue
        evidence_id = make_case_evidence_id(
            generation_run=generation_run,
            iteration=iteration,
            batch_id=batch_id,
            dataset=record.dataset,
            case_id=record.case_id,
        )
        case = {
            "evidence_id": evidence_id,
            "dataset": record.dataset,
            "case_id": record.case_id,
            "requirement": record.input_requirement,
            "prediction": record.generated_plantuml,
            "ground_truth": record.gold_plantuml,
            "matching_quality": _canonical_matching_quality(record),
        }
        findings, automatic = _case_findings(record)
        if findings:
            cases_with_findings.append((case, findings))
        automatic_by_case.extend((case, item) for item in automatic)

    queues = {
        kind: _kind_queue(cases_with_findings, kind)
        for kind in (*SEMANTIC_FINDING_KINDS, "compile_error", "syntax_error")
    }
    diagnostic_slots = int(bool(queues["compile_error"])) + int(
        bool(queues["syntax_error"])
    )
    semantic_limit = max(0, budget - diagnostic_slots)
    selected: list[tuple[dict[str, Any], dict[str, Any]]] = []
    semantic_offsets = {kind: 0 for kind in SEMANTIC_FINDING_KINDS}
    while len(selected) < semantic_limit:
        added = False
        for kind in SEMANTIC_FINDING_KINDS:
            offset = semantic_offsets[kind]
            if offset < len(queues[kind]):
                selected.append(queues[kind][offset])
                semantic_offsets[kind] += 1
                added = True
                if len(selected) == semantic_limit:
                    break
        if not added:
            break
    if len(selected) < budget and queues["compile_error"]:
        selected.append(queues["compile_error"][0])
    if len(selected) < budget and queues["syntax_error"]:
        selected.append(queues["syntax_error"][0])

    id_base = (max(1, int(batch_id)) - 1) * FINDING_ID_STRIDE
    findings_by_evidence: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for local_slot, (case, finding) in enumerate(selected, start=1):
        findings_by_evidence[str(case["evidence_id"])].append(
            {**finding, "finding_id": id_base + local_slot}
        )
    cases: list[dict[str, Any]] = []
    for case, _ in cases_with_findings:
        findings = findings_by_evidence.get(str(case["evidence_id"]), [])
        if findings:
            cases.append({**case, "findings": findings})
    if budget + len(automatic_by_case) >= FINDING_ID_STRIDE:
        raise ValueError("Too many automatic diagnostics for numeric finding ID stride")
    automatic_errors = []
    for diagnostic_index, (case, finding) in enumerate(automatic_by_case, start=1):
        automatic_errors.append(
            {
                **finding,
                "finding_id": id_base + budget + diagnostic_index,
                "status": "uncertain",
                "primary_finding_id": None,
                "requirement_quote": "",
                "error_summary": "Generic compiler or syntax diagnostic.",
                "causal_rationale": (
                    "The diagnostic has no precise location or requirement-grounded root cause."
                ),
                **case,
            }
        )
    return {
        "schema_version": FAILURE_ANALYSIS_INPUT_SCHEMA,
        "cases": cases,
        "_automatic_errors": automatic_errors,
    }


def _positive_int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.strip().isdigit():
        parsed = int(value.strip())
        return parsed if parsed > 0 else None
    return None


def _finding_catalog(payload: dict[str, Any]) -> dict[int, dict[str, Any]]:
    catalog: dict[int, dict[str, Any]] = {}
    for case in payload.get("cases", []):
        if not isinstance(case, dict):
            continue
        for finding in case.get("findings", []):
            if not isinstance(finding, dict):
                continue
            finding_id = _positive_int(finding.get("finding_id"))
            if finding_id is not None:
                catalog[finding_id] = {**case, **finding}
    return catalog


def validate_failure_errors(
    payload: dict[str, Any], *, input_payload: dict[str, Any]
) -> FailureAnalysisValidationResult:
    if payload.get("schema_version") != FAILURE_ERRORS_SCHEMA:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=[],
            fatal_errors=[f"Failure analysis must declare schema_version={FAILURE_ERRORS_SCHEMA!r}"],
        )
    if set(payload) != {"schema_version", "errors"}:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=[],
            fatal_errors=["Failure analysis output may contain only schema_version and errors"],
        )
    raw_errors = payload.get("errors")
    if not isinstance(raw_errors, list) or not raw_errors:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=[],
            fatal_errors=["Failure analysis must contain a non-empty errors list"],
        )

    findings = _finding_catalog(input_payload)
    validated: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    classified: set[int] = set()
    for index, raw in enumerate(raw_errors):
        errors: list[str] = []
        if not isinstance(raw, dict):
            rejected.append({"error_index": index, "errors": ["error must be an object"]})
            continue
        if set(raw) != FAILURE_ERROR_FIELDS:
            errors.append("error must contain exactly the failure-errors-v2 fields")
        finding_id = _positive_int(raw.get("finding_id"))
        primary_finding_id = (
            None
            if raw.get("primary_finding_id") is None
            else _positive_int(raw.get("primary_finding_id"))
        )
        status = str(raw.get("status") or "").strip().lower()
        quote = str(raw.get("requirement_quote") or "").strip()
        summary = str(raw.get("error_summary") or "").strip()
        rationale = str(raw.get("causal_rationale") or "").strip()
        finding = findings.get(finding_id)
        if finding_id is None or finding is None:
            errors.append("finding_id must be a known positive integer")
        if finding_id is not None and finding_id in classified:
            errors.append("finding_id is classified more than once")
        elif finding_id is not None and finding is not None:
            classified.add(finding_id)
        if status not in ERROR_STATUSES:
            errors.append(f"status must be one of {sorted(ERROR_STATUSES)}")
        if status == "secondary":
            if primary_finding_id is None:
                errors.append("secondary must reference a positive primary_finding_id")
            elif primary_finding_id == finding_id:
                errors.append("secondary cannot reference itself as primary")
        elif raw.get("primary_finding_id") is not None:
            errors.append("non-secondary errors must use primary_finding_id=null")
        if len(quote) > 300:
            errors.append("requirement_quote exceeds 300 characters")
        if not summary or len(summary) > 200:
            errors.append("error_summary must contain 1-200 characters")
        if not rationale or len(rationale) > 400:
            errors.append("causal_rationale must contain 1-400 characters")
        if finding is not None:
            requirement = str(finding.get("requirement") or "")
            anchor_kind = str(finding.get("anchor_kind") or "")
            if anchor_kind not in FINDING_KINDS:
                errors.append("finding anchor_kind is invalid")
            if anchor_kind not in {"syntax_error", "compile_error"}:
                if not quote or quote not in requirement:
                    errors.append("requirement_quote must be an exact non-empty substring")
            elif quote and quote not in requirement:
                errors.append("syntax/compiler requirement_quote must be empty or exact")
            if status == "actionable":
                anchor_quality = str(finding.get("anchor_quality") or "unavailable")
                if anchor_kind not in {"syntax_error", "compile_error"} and anchor_quality != "clear":
                    errors.append("ambiguous or unavailable finding anchor cannot be actionable")
                if anchor_kind not in {"syntax_error", "compile_error"} and str(
                    finding.get("matching_quality") or "not_available"
                ) != "bijective":
                    errors.append("non-bijective finding cannot be actionable")
                if anchor_kind in {"syntax_error", "compile_error"} and GENERIC_COMPILER_CUE.match(
                    str(finding.get("error_anchor") or "").strip()
                ):
                    errors.append("generic compiler/syntax evidence cannot be actionable")
        if errors:
            rejected.append(
                {
                    "error_index": index,
                    "finding_id": finding_id,
                    "errors": errors,
                }
            )
            continue
        validated.append(
            {
                "finding_id": finding_id,
                "finding_key": str(finding.get("finding_key") or ""),
                "status": status,
                "primary_finding_id": primary_finding_id,
                "requirement_quote": quote,
                "error_summary": summary,
                "causal_rationale": rationale,
                "evidence_id": str(finding.get("evidence_id") or ""),
                "dataset": str(finding.get("dataset") or ""),
                "case_id": str(finding.get("case_id") or ""),
                "anchor_kind": str(finding.get("anchor_kind") or ""),
                "error_anchor": str(finding.get("error_anchor") or ""),
                "source": str(finding.get("source") or ""),
                "matching_quality": str(finding.get("matching_quality") or "not_available"),
                "anchor_quality": str(finding.get("anchor_quality") or "unavailable"),
                "requirement": str(finding.get("requirement") or ""),
                "prediction": str(finding.get("prediction") or ""),
                "ground_truth": str(finding.get("ground_truth") or ""),
            }
        )

    actionable_ids = {
        int(item["finding_id"])
        for item in validated
        if item.get("status") == "actionable"
    }
    linked: list[dict[str, Any]] = []
    for item in validated:
        if item.get("status") == "secondary" and item.get("primary_finding_id") not in actionable_ids:
            rejected.append(
                {
                    "finding_id": item["finding_id"],
                    "errors": [
                        "secondary primary_finding_id must reference a validated actionable error"
                    ],
                }
            )
            continue
        linked.append(item)
    validated = linked

    for finding_id in sorted(set(findings) - classified):
        if any(item.get("finding_id") == finding_id for item in rejected):
            continue
        rejected.append(
            {
                "finding_id": finding_id,
                "errors": ["finding was omitted from failure analysis output"],
            }
        )
    validated.extend(
        item
        for item in input_payload.get("_automatic_errors", [])
        if isinstance(item, dict)
    )
    if not validated:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=rejected,
            fatal_errors=["No valid failure errors remain after validation"],
        )
    validated.sort(key=lambda item: item["finding_id"])
    return FailureAnalysisValidationResult(
        normalized_payload={
            "schema_version": FAILURE_ERRORS_SCHEMA,
            "errors": validated,
        },
        rejected_patterns=rejected,
        fatal_errors=[],
    )


def build_error_observations(
    failure_analysis: dict[str, Any], *, batch_id: int
) -> list[dict[str, Any]]:
    return [
        {**item, "batch_id": int(batch_id), "classification": str(item.get("status") or "")}
        for item in failure_analysis.get("errors", [])
        if isinstance(item, dict)
    ]


def _selector_input(errors: list[dict[str, Any]]) -> dict[str, Any]:
    secondary_by_primary: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for item in errors:
        if item.get("status") != "secondary":
            continue
        primary_id = _positive_int(item.get("primary_finding_id"))
        if primary_id is not None:
            secondary_by_primary[primary_id].append(item)

    compact = []
    full_errors = []
    for item in errors:
        if item.get("status") != "actionable":
            continue
        finding_id = _positive_int(item.get("finding_id"))
        if finding_id is None:
            continue
        secondary_items = sorted(
            secondary_by_primary.get(finding_id, []),
            key=lambda value: int(value["finding_id"]),
        )
        compact_secondary = [
            {
                "finding_id": int(value["finding_id"]),
                "anchor_kind": str(value.get("anchor_kind") or ""),
                "error_anchor": str(value.get("error_anchor") or "")[:300],
                "error_summary": str(value.get("error_summary") or ""),
                "causal_rationale": str(value.get("causal_rationale") or ""),
            }
            for value in secondary_items
        ]
        compact.append(
            {
                "finding_id": finding_id,
                "dataset": str(item.get("dataset") or ""),
                "case_id": str(item.get("case_id") or ""),
                "anchor_kind": str(item.get("anchor_kind") or ""),
                "error_anchor": str(item.get("error_anchor") or "")[:300],
                "requirement_quote": str(item.get("requirement_quote") or ""),
                "error_summary": str(item.get("error_summary") or ""),
                "causal_rationale": str(item.get("causal_rationale") or ""),
                "secondary_errors": compact_secondary,
            }
        )
        full_errors.append({**item, "secondary_errors": secondary_items})
    compact.sort(key=lambda item: item["finding_id"])
    full_errors.sort(key=lambda item: int(item["finding_id"]))
    return {
        "schema_version": ERROR_SELECTOR_INPUT_SCHEMA,
        "errors": compact,
        "_full_errors": full_errors,
    }


def _canonical_group_id(finding_keys: list[str]) -> str:
    canonical = "\n".join(sorted(finding_keys))
    return "group_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:20]


def validate_selector_output(
    payload: dict[str, Any], *, input_payload: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if set(payload) != SELECTOR_FIELDS:
        errors.append("Selector output must contain exactly the error-selector-v2 fields")
    if payload.get("schema_version") != ERROR_SELECTOR_SCHEMA:
        errors.append(f"schema_version must be {ERROR_SELECTOR_SCHEMA!r}")
    if input_payload.get("schema_version") != ERROR_SELECTOR_INPUT_SCHEMA:
        errors.append(f"selector input schema_version must be {ERROR_SELECTOR_INPUT_SCHEMA!r}")
    input_errors = {
        int(item["finding_id"]): item
        for item in input_payload.get("errors", [])
        if isinstance(item, dict) and _positive_int(item.get("finding_id")) is not None
    }
    raw_groups = payload.get("error_groups")
    if not isinstance(raw_groups, list) or not raw_groups:
        errors.append("error_groups must be a non-empty list")
        raw_groups = []
    local_ids: set[str] = set()
    assigned: list[int] = []
    normalized_groups: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_groups):
        if not isinstance(raw, dict):
            errors.append(f"error_groups[{index}] must be an object")
            continue
        if set(raw) != SELECTOR_GROUP_FIELDS:
            errors.append(f"error_groups[{index}] has unsupported or missing fields")
        local_id = str(raw.get("local_group_id") or "").strip()
        finding_ids = raw.get("finding_ids")
        summary = str(raw.get("group_summary") or "").strip()
        cause = str(raw.get("shared_cause") or "").strip()
        if not local_id or local_id in local_ids:
            errors.append(f"error_groups[{index}].local_group_id must be unique and non-empty")
        local_ids.add(local_id)
        if not isinstance(finding_ids, list) or not finding_ids:
            errors.append(f"error_groups[{index}].finding_ids must be a non-empty integer list")
            finding_ids = []
        clean_ids = [_positive_int(item) for item in finding_ids]
        if any(item is None for item in clean_ids):
            errors.append(f"error_groups[{index}].finding_ids must contain positive integers")
        clean_ids = [int(item) for item in clean_ids if item is not None]
        unknown = sorted(set(clean_ids) - set(input_errors))
        if unknown:
            errors.append(
                f"error_groups[{index}] references unknown finding IDs: "
                + ", ".join(str(item) for item in unknown)
            )
        if len(clean_ids) != len(set(clean_ids)):
            errors.append(f"error_groups[{index}] repeats a finding ID")
        if not summary or len(summary) > 300:
            errors.append(f"error_groups[{index}].group_summary must contain 1-300 characters")
        if not cause or len(cause) > 500:
            errors.append(f"error_groups[{index}].shared_cause must contain 1-500 characters")
        assigned.extend(clean_ids)
        normalized_groups.append(
            {
                "local_group_id": local_id,
                "finding_ids": sorted(clean_ids),
                "group_summary": summary,
                "shared_cause": cause,
            }
        )
    assigned_counts = Counter(assigned)
    duplicate_ids = sorted(item for item, count in assigned_counts.items() if count > 1)
    if duplicate_ids:
        errors.append(
            "findings appear in more than one group: "
            + ", ".join(str(item) for item in duplicate_ids)
        )
    omitted = sorted(set(input_errors) - set(assigned))
    if omitted:
        errors.append(
            "selector omitted findings: "
            + ", ".join(str(item) for item in omitted)
        )
    selection_status = str(payload.get("selection_status") or "").strip().lower()
    selected_local_id = str(payload.get("selected_group_id") or "").strip()
    rationale = str(payload.get("selection_rationale") or "").strip()
    if selection_status not in {"selected", "abstain"}:
        errors.append("selection_status must be selected or abstain")
    if not rationale or len(rationale) > 500:
        errors.append("selection_rationale must contain 1-500 characters")
    if selection_status == "selected" and selected_local_id not in local_ids:
        errors.append("selected_group_id must reference one returned local_group_id")
    if (
        selection_status == "selected"
        and normalized_groups
        and selected_local_id != normalized_groups[0]["local_group_id"]
    ):
        errors.append("selected_group_id must reference the first priority-ordered group")
    if selection_status == "abstain" and selected_local_id:
        errors.append("abstain must use an empty selected_group_id")
    if errors:
        return None, errors

    error_by_id = {
        int(item["finding_id"]): item
        for item in input_payload.get("_full_errors", input_payload.get("errors", []))
        if isinstance(item, dict) and _positive_int(item.get("finding_id")) is not None
    }
    selected_group: dict[str, Any] | None = None
    for group in normalized_groups:
        members = [error_by_id[item] for item in group["finding_ids"] if item in error_by_id]
        case_keys = {
            (str(item.get("dataset") or ""), str(item.get("case_id") or ""))
            for item in members
        }
        batch_ids = {int(item.get("batch_id", 0)) for item in members}
        finding_keys = [
            str(item.get("finding_key") or f"numeric_finding_{item['finding_id']}")
            for item in members
        ]
        group["group_id"] = _canonical_group_id(finding_keys)
        group["supporting_finding_count"] = len(group["finding_ids"])
        group["supporting_case_count"] = len(case_keys)
        group["supporting_batch_count"] = len(batch_ids)
        group["members"] = members
        if group["local_group_id"] == selected_local_id:
            selected_group = group
    return {
        "schema_version": ERROR_SELECTOR_SCHEMA,
        "error_groups": normalized_groups,
        "selection_status": selection_status,
        "selected_group_id": selected_group["group_id"] if selected_group else "",
        "selection_rationale": rationale,
        "selected_group": selected_group,
    }, []


def validate_selected_group_eligibility(group: dict[str, Any]) -> list[str]:
    """Validate evidence eligibility without consulting a repair taxonomy."""
    members = [item for item in group.get("members", []) if isinstance(item, dict)]
    if not members:
        return ["selected group has no members"]
    errors: list[str] = []
    families: set[str] = set()
    for item in members:
        finding_id = item.get("finding_id")
        anchor_kind = str(item.get("anchor_kind") or "")
        if item.get("status") != "actionable":
            errors.append(f"finding {finding_id} is not a validated actionable error")
        if anchor_kind in DIAGNOSTIC_FINDING_KINDS:
            families.add("compile")
            if GENERIC_COMPILER_CUE.match(str(item.get("error_anchor") or "").strip()):
                errors.append(f"finding {finding_id} is a generic compiler/syntax diagnostic")
        elif anchor_kind in SEMANTIC_FINDING_KINDS:
            families.add("semantic")
            if str(item.get("matching_quality") or "not_available") != "bijective":
                errors.append(f"finding {finding_id} is not bijective")
        else:
            errors.append(
                f"finding {finding_id} has unsupported anchor_kind {anchor_kind!r}"
            )
    if len(families) > 1:
        errors.append("selected group mixes semantic and compiler/syntax findings")
    return errors


def selected_group_evidence_family(group: dict[str, Any]) -> str:
    """Return the one acceptance metric family supported by a selected group."""

    required_metrics = selected_group_required_metrics(group)
    if required_metrics == ("plantuml_compilation_pass_rate",):
        return "compile"
    return "semantic"


def selected_group_required_metrics(group: dict[str, Any]) -> tuple[str, ...]:
    """Derive the acceptance metrics directly supported by group findings."""

    members = [item for item in group.get("members", []) if isinstance(item, dict)]
    anchor_kind_values = [
        str(item.get("anchor_kind") or "").strip() for item in members
    ]
    anchor_kinds = set(anchor_kind_values)
    if (
        not members
        or any(
            anchor_kind not in REQUIRED_METRIC_BY_FINDING_KIND
            for anchor_kind in anchor_kind_values
        )
    ):
        raise ValueError("Selected group must contain supported finding anchor kinds")
    required = {
        REQUIRED_METRIC_BY_FINDING_KIND[anchor_kind]
        for anchor_kind in anchor_kinds
    }
    compile_metric = "plantuml_compilation_pass_rate"
    if compile_metric in required and len(required) > 1:
        raise ValueError(
            "Selected group must not mix semantic and compile required metrics"
        )
    return tuple(metric for metric in REQUIRED_METRIC_ORDER if metric in required)


def select_error_group(
    *,
    errors: list[dict[str, Any]],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    payload = _selector_input(errors)
    if not payload["errors"]:
        return None
    validation_input = payload
    agent_payload = {
        "schema_version": payload["schema_version"],
        "errors": payload["errors"],
    }
    write_text(output_input_path, json.dumps(agent_payload, ensure_ascii=False, indent=2))
    system_prompt = read_prompt_file(args.error_selector_prompt_path, label="error selector")
    previous_output: Any = None
    validation_errors: list[str] = []
    last_raw = ""
    for attempt in range(1, 4):
        user_payload: dict[str, Any]
        if attempt == 1:
            user_payload = agent_payload
        else:
            user_payload = {
                "schema_version": "error-selector-repair-v1",
                "original_selector_input": agent_payload,
                "previous_output": previous_output,
                "validation_errors": validation_errors,
                "repair_instruction": (
                    "Return a complete corrected error-selector-v2 object. "
                    "Repair only schema, ID partition, references, and length violations."
                ),
            }
        last_raw = llm_client.chat(
            [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=False, indent=2),
                },
            ],
            temperature=args.selector_temperature,
            max_tokens=args.selector_max_tokens,
            thinking=args.selector_thinking,
            state_dir=state_dir,
            retry_phase="error_selector" if attempt == 1 else "error_selector_repair",
            retry_context={
                "iteration": iteration,
                "output_path": str(output_path),
                "schema_attempt": attempt,
            },
        )
        attempt_path = output_path.with_name(
            f"{output_path.stem}.attempt_{attempt}.raw.txt"
        )
        write_text(attempt_path, last_raw)
        write_text(output_path, last_raw)
        parsed = extract_json_object(last_raw)
        if parsed is None:
            previous_output = last_raw
            validation_errors = ["Error selector did not return JSON"]
            continue
        previous_output = parsed
        normalized, validation_errors = validate_selector_output(
            parsed, input_payload=validation_input
        )
        if normalized is not None:
            write_text(output_path, json.dumps(normalized, ensure_ascii=False, indent=2))
            return normalized
    write_text(
        output_path.with_suffix(".rejected.txt"),
        "\n".join(validation_errors or ["Error selector output remained invalid"]) + "\n",
    )
    return None


def representative_errors(group: dict[str, Any], *, limit: int = 5) -> list[dict[str, Any]]:
    members = [item for item in group.get("members", []) if isinstance(item, dict)]
    members.sort(
        key=lambda item: (
            str(item.get("dataset") or ""),
            str(item.get("case_id") or ""),
            int(item.get("finding_id") or 0),
        )
    )
    selected: list[dict[str, Any]] = []
    seen_cases: set[tuple[str, str]] = set()
    for item in members:
        case_key = (str(item.get("dataset") or ""), str(item.get("case_id") or ""))
        if case_key in seen_cases:
            continue
        seen_cases.add(case_key)
        selected.append(item)
        if len(selected) == limit:
            break
    return [
        {
            "finding_id": int(item.get("finding_id") or 0),
            "dataset": str(item.get("dataset") or ""),
            "case_id": str(item.get("case_id") or ""),
            "anchor_kind": str(item.get("anchor_kind") or ""),
            "error_anchor": str(item.get("error_anchor") or ""),
            "requirement_quote": str(item.get("requirement_quote") or ""),
            "error_summary": str(item.get("error_summary") or ""),
            "causal_rationale": str(item.get("causal_rationale") or ""),
            "secondary_errors": [
                {
                    "finding_id": int(secondary.get("finding_id") or 0),
                    "anchor_kind": str(secondary.get("anchor_kind") or ""),
                    "error_anchor": str(secondary.get("error_anchor") or ""),
                    "error_summary": str(secondary.get("error_summary") or ""),
                    "causal_rationale": str(
                        secondary.get("causal_rationale") or ""
                    ),
                }
                for secondary in item.get("secondary_errors", [])
                if isinstance(secondary, dict)
            ],
        }
        for item in selected
    ]
