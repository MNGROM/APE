"""Deterministic source-case behavior contracts for selector candidates."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ape_datasets.lato import Case
from metrics import relation_text


BEHAVIOR_CONTRACT_SCHEMA = "candidate-behavior-contract-v1"
SUPPORTED_ANCHOR_KINDS = {
    "missing_node",
    "extra_node",
    "missing_relation",
    "extra_relation",
    "compile_error",
    "syntax_error",
}
EXPECTED_TRANSITION_BY_ANCHOR_KIND = {
    "missing_node": "fn_to_tp",
    "extra_node": "fp_to_absent",
    "missing_relation": "fn_to_tp",
    "extra_relation": "fp_to_absent",
    "compile_error": "compile_fail_to_pass",
    "syntax_error": "compile_fail_to_pass",
}


def _normalize_identity(value: Any) -> str:
    return " ".join(str(value or "").split()).casefold()


def _anchor_identity(value: Any, *, family: str) -> str:
    rendered = relation_text(value) if family == "relations" else str(value or "")
    return _normalize_identity(rendered)


def _case_key(dataset: Any, case_id: Any) -> tuple[str, str]:
    return str(dataset or "").strip(), str(case_id or "").strip()


def compile_behavior_contract(
    *, selected_group: dict[str, Any], localization: dict[str, Any]
) -> dict[str, Any]:
    """Compile exact Python-owned obligations from validated selected findings."""

    members = [
        member
        for member in selected_group.get("members", [])
        if isinstance(member, dict)
    ]
    if not members:
        raise ValueError("Behavior contract requires selected group members")

    obligations: list[dict[str, Any]] = []
    cases: dict[tuple[str, str], dict[str, str]] = {}
    unsupported_kinds: list[str] = []
    for member in sorted(members, key=lambda item: int(item.get("finding_id") or 0)):
        finding_id = member.get("finding_id")
        anchor_kind = str(member.get("anchor_kind") or "").strip()
        dataset, case_id = _case_key(member.get("dataset"), member.get("case_id"))
        error_anchor = str(member.get("error_anchor") or "").strip()
        requirement = str(member.get("requirement") or "").strip()
        ground_truth = str(member.get("ground_truth") or "").strip()
        if not isinstance(finding_id, int) or isinstance(finding_id, bool) or finding_id <= 0:
            raise ValueError("Behavior contract finding_id must be a positive integer")
        if not dataset or not case_id or not requirement or not ground_truth:
            raise ValueError(
                f"Behavior contract finding {finding_id} is missing source-case evidence"
            )
        if not error_anchor:
            raise ValueError(
                f"Behavior contract finding {finding_id} is missing error_anchor"
            )
        if anchor_kind not in SUPPORTED_ANCHOR_KINDS:
            unsupported_kinds.append(anchor_kind or "missing")
            continue

        key = (dataset, case_id)
        case_payload = {
            "dataset": dataset,
            "case_id": case_id,
            "content": requirement,
            "gold_plantuml": ground_truth,
        }
        previous = cases.get(key)
        if previous is not None and previous != case_payload:
            raise ValueError(
                f"Behavior contract source case {dataset}/{case_id} has conflicting evidence"
            )
        cases[key] = case_payload
        obligations.append(
            {
                "finding_id": finding_id,
                "finding_key": str(member.get("finding_key") or ""),
                "dataset": dataset,
                "case_id": case_id,
                "anchor_kind": anchor_kind,
                "error_anchor": error_anchor,
                "expected_transition": EXPECTED_TRANSITION_BY_ANCHOR_KIND[
                    anchor_kind
                ],
            }
        )

    source_cases = [cases[key] for key in sorted(cases)]
    canonical_cases = json.dumps(
        source_cases, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    fingerprint = hashlib.sha256(canonical_cases.encode("utf-8")).hexdigest()
    shared_repair = localization.get("shared_repair")
    return {
        "schema_version": BEHAVIOR_CONTRACT_SCHEMA,
        "group_id": str(selected_group.get("group_id") or ""),
        "replay_scope": "selected_group_source_cases",
        "shared_repair": dict(shared_repair) if isinstance(shared_repair, dict) else {},
        "obligations": obligations,
        "source_cases": source_cases,
        "source_case_count": len(source_cases),
        "source_case_fingerprint": fingerprint,
        "unsupported_anchor_kinds": sorted(set(unsupported_kinds)),
    }


def behavior_contract_cases(contract: dict[str, Any]) -> list[Case]:
    cases: list[Case] = []
    for payload in contract.get("source_cases", []):
        if not isinstance(payload, dict):
            continue
        cases.append(
            Case(
                dataset=str(payload.get("dataset") or ""),
                case_id=str(payload.get("case_id") or ""),
                content=str(payload.get("content") or ""),
                gold_plantuml=str(payload.get("gold_plantuml") or ""),
            )
        )
    return cases


def _record_index(records: list[Any]) -> tuple[dict[tuple[str, str], Any], list[str]]:
    indexed: dict[tuple[str, str], Any] = {}
    duplicates: list[str] = []
    for record in records:
        key = _case_key(getattr(record, "dataset", ""), getattr(record, "case_id", ""))
        if key in indexed:
            duplicates.append(f"{key[0]}/{key[1]}")
        indexed[key] = record
    return indexed, sorted(set(duplicates))


def _matching_identities(record: Any) -> dict[str, set[str]] | None:
    metrics = getattr(record, "llm_element_metrics", None)
    if (
        metrics is None
        or not bool(getattr(metrics, "enabled", False))
        or str(getattr(metrics, "status", "")) != "success"
    ):
        return None
    matching = getattr(metrics, "matching", None)
    if not isinstance(matching, dict):
        return None

    identities: dict[str, set[str]] = {}
    for family in ("nodes", "relations"):
        group = matching.get(family)
        if not isinstance(group, dict):
            return None
        for bucket in ("fn", "fp"):
            raw_items = group.get(bucket)
            if not isinstance(raw_items, list):
                return None
            identities[f"{family}_{bucket}"] = {
                _anchor_identity(item, family=family) for item in raw_items
            }
        raw_tp = group.get("tp")
        if not isinstance(raw_tp, list):
            return None
        tp_gold: set[str] = set()
        tp_pred: set[str] = set()
        for item in raw_tp:
            if not isinstance(item, dict) or "gt" not in item or "pred" not in item:
                return None
            tp_gold.add(_anchor_identity(item["gt"], family=family))
            tp_pred.add(_anchor_identity(item["pred"], family=family))
        identities[f"{family}_tp_gold"] = tp_gold
        identities[f"{family}_tp_pred"] = tp_pred
    return identities


def _has_infrastructure_error(record: Any) -> bool:
    return "infrastructure_error" in list(getattr(record, "failure_types", []) or [])


def _compilation_passed(record: Any) -> bool | None:
    result = getattr(record, "plantuml_compilation", None)
    passed = getattr(result, "passed", None)
    return passed if isinstance(passed, bool) else None


def _semantic_observation(
    *, anchor_kind: str, error_anchor: str, identities: dict[str, set[str]]
) -> str:
    family = "nodes" if anchor_kind.endswith("node") else "relations"
    anchor = _anchor_identity(error_anchor, family=family)
    if anchor_kind.startswith("missing"):
        if anchor in identities[f"{family}_tp_gold"]:
            return "repaired"
        if anchor in identities[f"{family}_fn"]:
            return "failure"
        return "unobservable"
    if anchor in identities[f"{family}_fp"]:
        return "failure"
    return "repaired"


def _new_semantic_errors(
    baseline: dict[str, set[str]], candidate: dict[str, set[str]]
) -> list[str]:
    errors: list[str] = []
    for family in ("nodes", "relations"):
        for bucket in ("fn", "fp"):
            key = f"{family}_{bucket}"
            errors.extend(
                f"{family}:{bucket}:{identity}"
                for identity in sorted(candidate[key] - baseline[key])
            )
    return errors


def _repeat_obligation_result(
    *, obligation: dict[str, Any], baseline_record: Any, candidate_record: Any
) -> dict[str, Any]:
    result = {
        "finding_id": obligation["finding_id"],
        "dataset": obligation["dataset"],
        "case_id": obligation["case_id"],
        "anchor_kind": obligation["anchor_kind"],
        "error_anchor": obligation["error_anchor"],
        "status": "unobservable",
        "baseline_observation": "unobservable",
        "candidate_observation": "unobservable",
        "new_semantic_errors": [],
    }
    if _has_infrastructure_error(baseline_record) or _has_infrastructure_error(
        candidate_record
    ):
        result["reason"] = "infrastructure_error"
        return result

    anchor_kind = obligation["anchor_kind"]
    if anchor_kind in {"compile_error", "syntax_error"}:
        baseline_passed = _compilation_passed(baseline_record)
        candidate_passed = _compilation_passed(candidate_record)
        if baseline_passed is None or candidate_passed is None:
            result["reason"] = "compilation_measurement_missing"
            return result
        result["baseline_observation"] = (
            "repaired" if baseline_passed else "failure"
        )
        result["candidate_observation"] = (
            "repaired" if candidate_passed else "failure"
        )
        if baseline_passed:
            result["reason"] = "baseline_failure_not_reproduced"
            return result
        result["status"] = "repaired" if candidate_passed else "not_repaired"
        return result

    baseline_matching = _matching_identities(baseline_record)
    candidate_matching = _matching_identities(candidate_record)
    if baseline_matching is None or candidate_matching is None:
        result["reason"] = "semantic_matching_missing"
        return result
    baseline_observation = _semantic_observation(
        anchor_kind=anchor_kind,
        error_anchor=obligation["error_anchor"],
        identities=baseline_matching,
    )
    candidate_observation = _semantic_observation(
        anchor_kind=anchor_kind,
        error_anchor=obligation["error_anchor"],
        identities=candidate_matching,
    )
    new_errors = _new_semantic_errors(baseline_matching, candidate_matching)
    result.update(
        {
            "baseline_observation": baseline_observation,
            "candidate_observation": candidate_observation,
            "new_semantic_errors": new_errors,
        }
    )
    if baseline_observation != "failure":
        result["reason"] = "baseline_failure_not_reproduced"
    elif candidate_observation == "unobservable":
        result["reason"] = "candidate_target_unobservable"
    elif new_errors:
        result["status"] = "boundary_violation"
        result["reason"] = "new_unrelated_semantic_errors"
    elif candidate_observation == "repaired":
        result["status"] = "repaired"
    else:
        result["status"] = "not_repaired"
        result["reason"] = "target_not_repaired"
    return result


def _aggregate_obligation_status(repeat_statuses: list[str]) -> str:
    if repeat_statuses and all(status == "repaired" for status in repeat_statuses):
        return "proven"
    failure_statuses = {"not_repaired", "boundary_violation"}
    if repeat_statuses and all(status in failure_statuses for status in repeat_statuses):
        return "violated"
    return "inconclusive"


def evaluate_behavior_contract(
    *,
    contract: dict[str, Any],
    repeat_pairs: list[tuple[int, list[Any], list[Any]]],
) -> dict[str, Any]:
    """Evaluate target repair and same-case preservation over paired repeats."""

    obligations = [
        item for item in contract.get("obligations", []) if isinstance(item, dict)
    ]
    unsupported = list(contract.get("unsupported_anchor_kinds", []) or [])
    invalid_reasons: list[str] = []
    if contract.get("schema_version") != BEHAVIOR_CONTRACT_SCHEMA:
        invalid_reasons.append("behavior_contract_schema_invalid")
    if not obligations:
        invalid_reasons.append("behavior_contract_obligations_missing")
    if not repeat_pairs:
        invalid_reasons.append("behavior_contract_repeats_missing")

    obligation_repeats: dict[int, list[dict[str, Any]]] = {
        int(item["finding_id"]): [] for item in obligations
    }
    repeat_results: list[dict[str, Any]] = []
    for repeat, baseline_records, candidate_records in repeat_pairs:
        baseline_index, baseline_duplicates = _record_index(baseline_records)
        candidate_index, candidate_duplicates = _record_index(candidate_records)
        if baseline_duplicates or candidate_duplicates:
            invalid_reasons.append("behavior_contract_duplicate_case_records")
        current_results: list[dict[str, Any]] = []
        for obligation in obligations:
            key = _case_key(obligation.get("dataset"), obligation.get("case_id"))
            baseline_record = baseline_index.get(key)
            candidate_record = candidate_index.get(key)
            if baseline_record is None or candidate_record is None:
                item_result = {
                    **obligation,
                    "status": "unobservable",
                    "reason": "paired_case_record_missing",
                    "new_semantic_errors": [],
                }
            else:
                item_result = _repeat_obligation_result(
                    obligation=obligation,
                    baseline_record=baseline_record,
                    candidate_record=candidate_record,
                )
            item_result["repeat"] = int(repeat)
            current_results.append(item_result)
            obligation_repeats[int(obligation["finding_id"])].append(item_result)
        repeat_results.append(
            {
                "repeat": int(repeat),
                "obligations": current_results,
            }
        )

    obligation_results: list[dict[str, Any]] = []
    for obligation in obligations:
        finding_id = int(obligation["finding_id"])
        results = obligation_repeats[finding_id]
        statuses = [str(item.get("status") or "unobservable") for item in results]
        obligation_results.append(
            {
                **obligation,
                "status": _aggregate_obligation_status(statuses),
                "repeat_statuses": statuses,
                "new_semantic_errors": sorted(
                    {
                        error
                        for item in results
                        for error in item.get("new_semantic_errors", [])
                    }
                ),
            }
        )

    if unsupported:
        status = "unsupported"
    elif invalid_reasons:
        status = "inconclusive"
    elif obligation_results and all(
        item["status"] == "proven" for item in obligation_results
    ):
        status = "proven"
    elif any(item["status"] == "violated" for item in obligation_results):
        status = "violated"
    else:
        status = "inconclusive"

    rejection_reasons = [] if status == "proven" else [f"behavior_contract_{status}"]
    return {
        "schema_version": BEHAVIOR_CONTRACT_SCHEMA,
        "status": status,
        "proven": status == "proven",
        "evaluation_valid": status in {"proven", "violated"},
        "invalid_reasons": sorted(set(invalid_reasons)),
        "rejection_reasons": rejection_reasons,
        "replay_scope": contract.get("replay_scope"),
        "source_case_count": contract.get("source_case_count"),
        "source_case_fingerprint": contract.get("source_case_fingerprint"),
        "repeat_count": len(repeat_pairs),
        "unsupported_anchor_kinds": unsupported,
        "obligation_results": obligation_results,
        "repeat_results": repeat_results,
    }
