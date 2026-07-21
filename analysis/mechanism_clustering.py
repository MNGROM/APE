"""Validated mechanism evidence, taxonomy matching, and deterministic clustering."""

from __future__ import annotations

import csv
import dataclasses
import hashlib
import json
import math
import re
import statistics
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

from prompt_ops import extract_json_object
from utils.io import append_jsonl, read_text, write_text
from versioning import make_run_dir


FAILURE_DIRECTIONS = {
    "activity_under_decomposition",
    "activity_over_decomposition",
    "missing_required_relation",
    "spurious_relation",
    "wrong_relation_type",
    "missing_required_parallel",
    "spurious_parallel",
    "missing_required_loop",
    "spurious_loop",
    "condition_or_branch_error",
    "syntax_or_format_error",
    "mixed_or_uncertain",
}

CONSTRUCT_STATES = {
    "activity": {"none", "single", "multiple", "merged", "non_activity"},
    "fork": {"present", "absent"},
    "loop": {"present", "absent"},
    "branch": {"none", "if", "switch", "other"},
    "early_exit": {"present", "absent"},
    "syntax": {"valid", "invalid"},
}

REQUIREMENT_TRIGGERS = {
    "activity": {
        "multiple_explicit_actions",
        "single_explicit_action",
        "context_clause",
        "environment_context",
        "initial_state_context",
        "temporal_context",
        "precondition_context",
        "other_context",
        "unstated_implementation_substeps",
        "heading_or_label",
        "ambiguous",
    },
    "fork": {
        "explicit_concurrency",
        "ordinary_enumeration",
        "multiple_objects_same_action",
        "alternatives_or_sequence",
        "ambiguous",
    },
    "loop": {
        "explicit_iteration_with_exit",
        "periodic_descriptor_only",
        "state_transition_description",
        "ambiguous",
    },
    "branch": {
        "explicit_early_exit",
        "exclusive_values",
        "general_condition",
        "ambiguous",
    },
    "early_exit": {"explicit_early_exit", "ambiguous"},
    "syntax": {
        "compiler_confirmed",
        "wrapper_only",
        "conditional_label_syntax",
        "block_balance_syntax",
        "other_compiler_error",
        "ambiguous",
    },
}

NODE_INVENTORY_STATUSES = {"not_applicable", "sufficient", "insufficient", "uncertain"}
EVIDENCE_BASES = {"requirement_and_gold", "requirement_only", "gold_only", "compiler", "ambiguous"}
EVIDENCE_CLAIM_ROLES = {"primary", "secondary"}
MAX_REQUIREMENT_QUOTE_CHARS = 300
ERROR_EVIDENCE_FIELDS = (
    "llm_missing_nodes",
    "llm_extra_nodes",
    "llm_missing_relations",
    "llm_extra_relations",
)
ALLOWED_ANCHOR_FIELDS = {
    "activity_under_decomposition": {"llm_missing_nodes"},
    "activity_over_decomposition": {"llm_extra_nodes"},
    "missing_required_relation": {"llm_missing_relations"},
    "spurious_relation": {"llm_extra_relations"},
    "wrong_relation_type": {"llm_missing_relations", "llm_extra_relations"},
    "missing_required_parallel": {"llm_missing_relations"},
    "spurious_parallel": {"llm_extra_relations"},
    "missing_required_loop": {"llm_missing_relations"},
    "spurious_loop": {"llm_extra_relations"},
    "condition_or_branch_error": set(ERROR_EVIDENCE_FIELDS),
    "mixed_or_uncertain": set(ERROR_EVIDENCE_FIELDS),
}
SIGNATURE_FIELDS = (
    "failure_direction",
    "construct_family",
    "requirement_trigger",
    "gold_state",
    "prediction_state",
    "node_inventory_status",
)
PARENT_SIGNATURE_FIELDS = tuple(
    field for field in SIGNATURE_FIELDS if field != "requirement_trigger"
)
ATOMIC_SCHEMA_VERSION = "atomic-v1"
HYPOTHESIS_SCHEMA_VERSION = "hypothesis-v1"
ATOMIC_ATTRIBUTION_FIELDS = {
    "evidence_id",
    "role",
    "requirement_quote",
    "error_anchor",
    "failure_direction",
    "construct_family",
    "requirement_trigger",
    "gold_state",
    "prediction_state",
    "node_inventory_status",
    "evidence_basis",
    "causal_rationale",
}
ANCHOR_FIELD_TO_KIND = {
    "llm_missing_nodes": "missing_node",
    "llm_extra_nodes": "extra_node",
    "llm_missing_relations": "missing_relation",
    "llm_extra_relations": "extra_relation",
    "compile_errors": "compile_error",
    "syntax_errors": "syntax_error",
}
ANCHOR_KIND_TO_EVIDENCE_FIELD = {value: key for key, value in ANCHOR_FIELD_TO_KIND.items()}

COMPILER_BLOCK_BALANCE_CUE = re.compile(
    r"\b(?:unclosed|unbalanced|unterminated|unexpected\s+end|missing\s+(?:end|endif|endwhile|endfork|endgroup|endswitch)|"
    r"endif|endwhile|endfork|endgroup|endswitch)\b",
    re.IGNORECASE,
)
COMPILER_WRAPPER_CUE = re.compile(
    r"@startuml|@enduml|startuml|enduml|(?:plantuml\s+)?wrapper|markdown\s+fence|code\s+fence",
    re.IGNORECASE,
)
COMPILER_CONDITIONAL_LABEL_CUE = re.compile(
    r"\b(?:conditional|condition|branch|if|elseif|else|then)\b.*\b(?:label|syntax|malformed|invalid|expected)\b|"
    r"\b(?:label|syntax|malformed|invalid|expected)\b.*\b(?:conditional|condition|branch|if|elseif|else|then)\b",
    re.IGNORECASE,
)


@dataclasses.dataclass
class FailureAnalysisValidationResult:
    normalized_payload: dict[str, Any] | None
    rejected_patterns: list[dict[str, Any]]
    fatal_errors: list[str]


def failure_analysis_item_count(payload: dict[str, Any] | None) -> int:
    if not isinstance(payload, dict):
        return 0
    items = payload.get("error_attributions")
    if isinstance(items, list):
        return len(items)
    patterns = payload.get("error_patterns")
    return len(patterns) if isinstance(patterns, list) else 0


def make_case_evidence_id(
    *, generation_run: str, iteration: int, batch_id: int, dataset: str, case_id: str
) -> str:
    """Build an ID whose source can be reconstructed without trusting model output."""
    safe_run = re.sub(r"[^A-Za-z0-9_.-]+", "_", generation_run.strip())
    return f"{safe_run}:i{iteration:03d}:b{batch_id:03d}:{dataset}:{case_id}"


def load_mechanism_taxonomy(path: Path) -> dict[str, Any]:
    payload = json.loads(read_text(path))
    if not isinstance(payload, dict) or payload.get("version") not in {"v1", "v2", "v3"}:
        raise ValueError(f"Unsupported mechanism taxonomy: {path}")
    mechanisms = payload.get("mechanisms")
    if not isinstance(mechanisms, list) or not mechanisms:
        raise ValueError("Mechanism taxonomy must contain a non-empty mechanisms list")
    seen_ids: set[str] = set()
    for mechanism in mechanisms:
        if not isinstance(mechanism, dict):
            raise ValueError("Mechanism taxonomy entries must be objects")
        mechanism_id = str(mechanism.get("mechanism_id") or "")
        if not mechanism_id or mechanism_id in seen_ids:
            raise ValueError(f"Mechanism taxonomy contains invalid or duplicate ID: {mechanism_id!r}")
        seen_ids.add(mechanism_id)
        if mechanism.get("candidate_eligible", False):
            for field in ("positive_trigger", "negative_boundary"):
                if not isinstance(mechanism.get(field), str) or not mechanism[field].strip():
                    raise ValueError(
                        f"Candidate mechanism {mechanism.get('mechanism_id')!r} must define {field}"
                    )
            if payload.get("version") == "v3":
                match = mechanism.get("match")
                if not isinstance(match, dict) or isinstance(match.get("requirement_trigger"), list):
                    raise ValueError(
                        f"v3 candidate mechanism {mechanism_id!r} must match exactly one trigger"
                    )
    if payload.get("version") == "v3" and payload.get("attribution_schema") != ATOMIC_SCHEMA_VERSION:
        raise ValueError("v3 taxonomy must declare attribution_schema='atomic-v1'")
    if payload.get("version") == "v3" and payload.get("policy_revision") == "open-hypothesis-v1":
        templates = payload.get("rule_templates")
        if not isinstance(templates, list) or not templates:
            raise ValueError("Open v3 taxonomy must contain rule_templates")
        template_ids: set[str] = set()
        for template in templates:
            if not isinstance(template, dict):
                raise ValueError("Taxonomy rule templates must be objects")
            template_id = str(template.get("template_id") or "")
            if not template_id or template_id in template_ids:
                raise ValueError(f"Taxonomy contains invalid or duplicate rule template: {template_id!r}")
            template_ids.add(template_id)
            if not isinstance(template.get("match"), dict):
                raise ValueError(f"Taxonomy rule template {template_id!r} must define match")
            for field in ("positive_trigger_template", "negative_boundary_template"):
                if not isinstance(template.get(field), str) or not template[field].strip():
                    raise ValueError(f"Taxonomy rule template {template_id!r} must define {field}")
    return payload


def mechanism_signature(pattern: dict[str, Any]) -> dict[str, str]:
    return {field: str(pattern.get(field) or "").strip() for field in SIGNATURE_FIELDS}


def mechanism_signature_key(signature: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(signature.get(field) or "").strip() for field in SIGNATURE_FIELDS)


def parent_signature(signature: dict[str, Any]) -> dict[str, str]:
    return {
        field: str(signature.get(field) or "").strip()
        for field in PARENT_SIGNATURE_FIELDS
    }


def parent_signature_key(signature: dict[str, Any]) -> tuple[str, ...]:
    normalized = parent_signature(signature)
    return tuple(normalized.get(field, "") for field in PARENT_SIGNATURE_FIELDS)


def child_signature_key(signature: dict[str, Any]) -> tuple[str, ...]:
    return mechanism_signature_key(signature)


def hypothesis_id(signature: dict[str, Any], *, taxonomy: dict[str, Any]) -> str:
    canonical = json.dumps(
        {
            "taxonomy_version": taxonomy.get("version"),
            "policy_revision": taxonomy.get("policy_revision", "legacy"),
            "child_key": list(child_signature_key(signature)),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return "hyp_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def evidence_claim_ids(pattern: dict[str, Any], *, role: str | None = None) -> list[str]:
    claims = pattern.get("evidence_claims", [])
    if not isinstance(claims, list):
        return []
    return sorted(
        {
            str(claim.get("evidence_id") or "").strip()
            for claim in claims
            if isinstance(claim, dict)
            and (role is None or claim.get("role") == role)
            and str(claim.get("evidence_id") or "").strip()
        }
    )


def requirement_quote_matches(quote: str, requirement: str) -> bool:
    if quote in requirement:
        return True

    def compact(value: str) -> str:
        normalized = unicodedata.normalize("NFKC", value).casefold()
        return "".join(character for character in normalized if character.isalnum())

    compact_quote = compact(quote)
    return len(compact_quote) >= 20 and compact_quote in compact(requirement)


def _validate_evidence_claims(
    pattern: dict[str, Any],
    *,
    evidence_by_id: dict[str, dict[str, Any]],
    pattern_index: int,
    direction: str,
    evidence_basis: str,
) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    if "supporting_evidence_ids" in pattern:
        errors.append(
            f"error_patterns[{pattern_index}] must use evidence_claims instead of supporting_evidence_ids"
        )
    claims = pattern.get("evidence_claims")
    if not isinstance(claims, list) or not claims:
        return [], [*errors, f"error_patterns[{pattern_index}].evidence_claims must be a non-empty list"]

    normalized_claims: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for claim_index, raw_claim in enumerate(claims):
        prefix = f"error_patterns[{pattern_index}].evidence_claims[{claim_index}]"
        if not isinstance(raw_claim, dict):
            errors.append(f"{prefix} must be an object")
            continue
        expected_fields = {"evidence_id", "role", "requirement_quote", "error_anchor"}
        unexpected_fields = sorted(set(raw_claim) - expected_fields)
        if unexpected_fields:
            errors.append(f"{prefix} contains unsupported fields: {', '.join(unexpected_fields)}")
        values: dict[str, str] = {}
        for field in ("evidence_id", "role", "requirement_quote", "error_anchor"):
            value = raw_claim.get(field)
            if not isinstance(value, str):
                errors.append(f"{prefix}.{field} must be a string")
                values[field] = ""
            else:
                values[field] = value.strip()

        evidence_id = values["evidence_id"]
        role = values["role"]
        quote = values["requirement_quote"]
        anchor = values["error_anchor"]
        if not evidence_id:
            errors.append(f"{prefix}.evidence_id must be non-empty")
        elif evidence_id in seen_ids:
            errors.append(f"{prefix}.evidence_id duplicates another claim in this pattern")
        seen_ids.add(evidence_id)
        if role not in EVIDENCE_CLAIM_ROLES:
            errors.append(f"{prefix}.role is invalid: {role!r}")
        if not anchor:
            errors.append(f"{prefix}.error_anchor must be non-empty")

        evidence = evidence_by_id.get(evidence_id)
        if evidence is None:
            if evidence_id:
                errors.append(f"{prefix} references unknown evidence ID: {evidence_id}")
            normalized_claims.append(values)
            continue

        requirement = str(evidence.get("requirement") or "")
        if evidence_basis != "compiler" and (
            not quote or not requirement_quote_matches(quote, requirement)
        ):
            errors.append(f"{prefix}.requirement_quote must be an exact non-empty requirement substring")
        elif evidence_basis == "compiler" and quote and not requirement_quote_matches(quote, requirement):
            errors.append(f"{prefix}.requirement_quote must be empty or an exact requirement substring")
        if len(quote) > MAX_REQUIREMENT_QUOTE_CHARS:
            errors.append(
                f"{prefix}.requirement_quote exceeds {MAX_REQUIREMENT_QUOTE_CHARS} characters"
            )

        if evidence_basis == "compiler":
            if anchor != "compile_failed":
                errors.append(f"{prefix}.error_anchor must be 'compile_failed' for compiler evidence")
            if evidence.get("plantuml_compiles", True):
                errors.append(f"{prefix} claims compiler evidence for a case that compiled")
        elif direction == "syntax_or_format_error":
            if anchor != "syntax_failed":
                errors.append(f"{prefix}.error_anchor must be 'syntax_failed' for non-compiler syntax evidence")
            if evidence.get("syntax_passed", True):
                errors.append(f"{prefix} claims syntax evidence for a case that passed syntax validation")
        else:
            matching_fields = [
                field
                for field in ERROR_EVIDENCE_FIELDS
                if anchor in [str(item) for item in evidence.get(field, [])]
            ]
            if not matching_fields:
                errors.append(f"{prefix}.error_anchor is not present in the case evaluator evidence")
            elif len(matching_fields) > 1:
                errors.append(f"{prefix}.error_anchor is ambiguous across evaluator evidence fields")
            elif role == "primary" and matching_fields[0] not in ALLOWED_ANCHOR_FIELDS.get(direction, set()):
                errors.append(
                    f"{prefix}.error_anchor comes from {matching_fields[0]!r}, which is incompatible with {direction!r}"
                )
        normalized_claims.append(values)
    return normalized_claims, errors


def make_attribution_id(*, evidence_id: str, anchor_kind: str, error_anchor: str) -> str:
    digest = hashlib.sha256(
        f"{evidence_id}\n{anchor_kind}\n{error_anchor}".encode("utf-8")
    ).hexdigest()[:16]
    return f"{evidence_id}:a:{anchor_kind}:{digest}"


def classify_compiler_error(error_anchor: str) -> str:
    """Map one concrete compiler error to the narrow v3 syntax trigger."""

    if COMPILER_BLOCK_BALANCE_CUE.search(error_anchor):
        return "block_balance_syntax"
    if COMPILER_WRAPPER_CUE.search(error_anchor):
        return "wrapper_only"
    if COMPILER_CONDITIONAL_LABEL_CUE.search(error_anchor):
        return "conditional_label_syntax"
    return "other_compiler_error"


def _matching_quality_status(evidence: dict[str, Any]) -> str:
    quality = evidence.get("matching_quality")
    if isinstance(quality, dict):
        return str(quality.get("status") or "unknown")
    return str(quality or "unknown")


def canonical_matching_quality(evidence: dict[str, Any]) -> str:
    status = _matching_quality_status(evidence).strip().lower()
    if status in {"valid", "bijective"}:
        return "bijective"
    if status in {"non_bijective", "non-bijective"}:
        return "non_bijective"
    return "not_available"


def _rejection_reason_codes(errors: list[str]) -> list[str]:
    mappings = (
        ("not present in the case evaluator evidence", "invalid_anchor"),
        ("ambiguous across evaluator evidence fields", "ambiguous_anchor"),
        ("non-bijective judge matching", "non_bijective_matching"),
        ("not grounded by requirement_quote", "invalid_trigger_grounding"),
        ("must be an exact", "invalid_requirement_quote"),
        ("ambiguous_attribution_assignment", "ambiguous_attribution"),
        ("duplicate_attribution", "duplicate_attribution"),
        ("compiler error class", "invalid_compiler_class"),
    )
    reasons = {
        code
        for text, code in mappings
        if any(text in error for error in errors)
    }
    return sorted(reasons or {"invalid_attribution"})


def _atomic_anchor_kind(
    *, evidence: dict[str, Any], error_anchor: str
) -> tuple[str | None, list[str]]:
    matching_fields = [
        field
        for field in ANCHOR_FIELD_TO_KIND
        if error_anchor in [str(item) for item in evidence.get(field, [])]
    ]
    if not matching_fields:
        return None, ["error_anchor is not present in the case evaluator evidence"]
    if len(matching_fields) > 1:
        return None, ["error_anchor is ambiguous across evaluator evidence fields"]
    return ANCHOR_FIELD_TO_KIND[matching_fields[0]], []


def _validate_atomic_attribution(
    raw: Any,
    *,
    evidence_by_id: dict[str, dict[str, Any]],
    index: int,
) -> tuple[dict[str, Any] | None, list[str]]:
    prefix = f"error_attributions[{index}]"
    if not isinstance(raw, dict):
        return None, [f"{prefix} must be an object"]

    errors: list[str] = []
    unexpected = sorted(set(raw) - ATOMIC_ATTRIBUTION_FIELDS)
    if unexpected:
        errors.append(f"{prefix} contains unsupported fields: {', '.join(unexpected)}")

    normalized: dict[str, Any] = {}
    for field in sorted(ATOMIC_ATTRIBUTION_FIELDS):
        value = raw.get(field)
        allow_empty = field == "requirement_quote" and raw.get("evidence_basis") == "compiler"
        if not isinstance(value, str) or (not value.strip() and not allow_empty):
            errors.append(f"{prefix}.{field} must be a non-empty string")
            normalized[field] = ""
        else:
            text = value.strip()
            normalized[field] = (
                text.lower()
                if field
                in {
                    "role",
                    "failure_direction",
                    "construct_family",
                    "requirement_trigger",
                    "gold_state",
                    "prediction_state",
                    "node_inventory_status",
                    "evidence_basis",
                }
                else text
            )

    evidence_id = str(normalized.get("evidence_id") or "")
    role = str(normalized.get("role") or "")
    quote = str(normalized.get("requirement_quote") or "")
    anchor = str(normalized.get("error_anchor") or "")
    direction = str(normalized.get("failure_direction") or "")
    family = str(normalized.get("construct_family") or "")
    trigger = str(normalized.get("requirement_trigger") or "")
    gold_state = str(normalized.get("gold_state") or "")
    prediction_state = str(normalized.get("prediction_state") or "")
    node_status = str(normalized.get("node_inventory_status") or "")
    evidence_basis = str(normalized.get("evidence_basis") or "")

    if role not in EVIDENCE_CLAIM_ROLES:
        errors.append(f"{prefix}.role is invalid: {role!r}")
    if direction not in FAILURE_DIRECTIONS:
        errors.append(f"{prefix}.failure_direction is invalid: {direction!r}")
    if family not in CONSTRUCT_STATES:
        errors.append(f"{prefix}.construct_family is invalid: {family!r}")
    elif trigger not in REQUIREMENT_TRIGGERS[family]:
        errors.append(f"{prefix}.requirement_trigger is invalid for {family!r}: {trigger!r}")
    if family in CONSTRUCT_STATES:
        if gold_state not in CONSTRUCT_STATES[family]:
            errors.append(f"{prefix}.gold_state is invalid for {family!r}: {gold_state!r}")
        if prediction_state not in CONSTRUCT_STATES[family]:
            errors.append(
                f"{prefix}.prediction_state is invalid for {family!r}: {prediction_state!r}"
            )
    if node_status not in NODE_INVENTORY_STATUSES:
        errors.append(f"{prefix}.node_inventory_status is invalid: {node_status!r}")
    if family in {"activity", "syntax"} and node_status != "not_applicable":
        errors.append(
            f"{prefix}.node_inventory_status must be 'not_applicable' for {family!r}"
        )
    if family in {"fork", "loop", "branch", "early_exit"} and node_status == "not_applicable":
        errors.append(f"{prefix}.node_inventory_status must describe inventory sufficiency")
    if role == "primary" and family in {"fork", "loop", "branch", "early_exit"} and node_status != "sufficient":
        errors.append(f"{prefix} construct attribution with insufficient inventory cannot be primary")
    if evidence_basis not in EVIDENCE_BASES:
        errors.append(f"{prefix}.evidence_basis is invalid: {evidence_basis!r}")
    if len(quote) > MAX_REQUIREMENT_QUOTE_CHARS:
        errors.append(f"{prefix}.requirement_quote exceeds {MAX_REQUIREMENT_QUOTE_CHARS} characters")
    if len(str(normalized.get("causal_rationale") or "")) > 500:
        errors.append(f"{prefix}.causal_rationale exceeds 500 characters")

    evidence = evidence_by_id.get(evidence_id)
    anchor_kind: str | None = None
    if evidence is None:
        if evidence_id:
            errors.append(f"{prefix} references unknown evidence ID: {evidence_id}")
    else:
        requirement = str(evidence.get("requirement") or "")
        if evidence_basis == "compiler":
            if quote and quote not in requirement:
                errors.append(f"{prefix}.requirement_quote must be empty or exact")
        elif not quote or quote not in requirement:
            errors.append(f"{prefix}.requirement_quote must be an exact non-empty substring")

        anchor_kind, anchor_errors = _atomic_anchor_kind(
            evidence=evidence,
            error_anchor=anchor,
        )
        errors.extend(f"{prefix}.{error}" for error in anchor_errors)
        if anchor_kind is not None:
            source_field = ANCHOR_KIND_TO_EVIDENCE_FIELD[anchor_kind]
            if evidence_basis == "compiler":
                if family != "syntax" or anchor_kind != "compile_error":
                    errors.append(f"{prefix} compiler evidence requires a compile_error syntax anchor")
                expected_trigger = classify_compiler_error(anchor)
                if trigger != expected_trigger:
                    errors.append(
                        f"{prefix}.requirement_trigger must match compiler error class "
                        f"{expected_trigger!r}"
                    )
            elif direction == "syntax_or_format_error":
                if anchor_kind not in {"syntax_error", "compile_error"}:
                    errors.append(f"{prefix} syntax attribution requires a syntax or compile anchor")
            elif role == "primary" and source_field not in ALLOWED_ANCHOR_FIELDS.get(direction, set()):
                errors.append(
                    f"{prefix}.error_anchor comes from {source_field!r}, incompatible with {direction!r}"
                )
        if role == "primary" and _matching_quality_status(evidence) == "non_bijective":
            errors.append(f"{prefix} non-bijective judge matching cannot provide primary support")
        if role == "primary" and quote and not requirement_trigger_is_grounded(trigger, quote):
            errors.append(f"{prefix}.requirement_trigger is not grounded by requirement_quote")

    if errors or anchor_kind is None:
        return None, errors
    normalized["anchor_kind"] = anchor_kind
    normalized["matching_quality"] = canonical_matching_quality(evidence or {})
    normalized["eligibility"] = role
    normalized["rejection_reasons"] = []
    normalized["attribution_id"] = make_attribution_id(
        evidence_id=evidence_id,
        anchor_kind=anchor_kind,
        error_anchor=anchor,
    )
    return normalized, []


def _validate_atomic_payload(
    payload: dict[str, Any], *, evidence_catalog: list[dict[str, Any]]
) -> FailureAnalysisValidationResult:
    if payload.get("schema_version") != ATOMIC_SCHEMA_VERSION:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=[],
            fatal_errors=[f"Atomic payload must declare schema_version={ATOMIC_SCHEMA_VERSION!r}"],
        )
    raw_items = payload.get("error_attributions")
    if not isinstance(raw_items, list) or not raw_items:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=[],
            fatal_errors=["Payload must contain a non-empty error_attributions list"],
        )
    evidence_by_id = {
        str(item.get("evidence_id") or "").strip(): item
        for item in evidence_catalog
        if isinstance(item, dict) and str(item.get("evidence_id") or "").strip()
    }
    validated: list[tuple[int, dict[str, Any]]] = []
    rejected: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_items):
        normalized, errors = _validate_atomic_attribution(
            raw,
            evidence_by_id=evidence_by_id,
            index=index,
        )
        if normalized is None:
            rejected.append(
                {
                    "attribution_index": index,
                    "evidence_id": str(raw.get("evidence_id") or "") if isinstance(raw, dict) else "",
                    "errors": errors,
                    "rejection_reasons": _rejection_reason_codes(errors),
                }
            )
        else:
            validated.append((index, normalized))

    signatures_by_id: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for _, item in validated:
        signatures_by_id[item["attribution_id"]].add(mechanism_signature_key(item))
    ambiguous_ids = {
        attribution_id
        for attribution_id, signatures in signatures_by_id.items()
        if len(signatures) > 1
    }
    normalized_items: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, item in validated:
        attribution_id = item["attribution_id"]
        if attribution_id in ambiguous_ids:
            rejected.append(
                {
                    "attribution_index": index,
                    "attribution_id": attribution_id,
                    "evidence_id": item["evidence_id"],
                    "errors": ["ambiguous_attribution_assignment"],
                    "rejection_reasons": ["ambiguous_attribution"],
                }
            )
        elif attribution_id in seen_ids:
            rejected.append(
                {
                    "attribution_index": index,
                    "attribution_id": attribution_id,
                    "evidence_id": item["evidence_id"],
                    "errors": ["duplicate_attribution"],
                    "rejection_reasons": ["duplicate_attribution"],
                }
            )
        else:
            seen_ids.add(attribution_id)
            normalized_items.append(item)
    normalized_items.sort(
        key=lambda item: (
            item["attribution_id"],
            mechanism_signature_key(item),
        )
    )
    if not normalized_items:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=rejected,
            fatal_errors=["No valid error attributions remain after validation"],
        )
    return FailureAnalysisValidationResult(
        normalized_payload={
            "schema_version": ATOMIC_SCHEMA_VERSION,
            "error_attributions": normalized_items,
            "evidence_catalog": evidence_catalog,
        },
        rejected_patterns=rejected,
        fatal_errors=[],
    )


def _validate_pattern(
    pattern: Any, evidence_by_id: dict[str, dict[str, Any]], index: int
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not isinstance(pattern, dict):
        return None, [f"error_patterns[{index}] must be an object"]

    normalized = dict(pattern)
    for field in ("name", "problem", "failure_direction", "construct_family", "requirement_trigger", "gold_state", "prediction_state", "node_inventory_status", "evidence_basis"):
        value = pattern.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"error_patterns[{index}].{field} must be a non-empty string")
        else:
            normalized[field] = value.strip().lower() if field not in {"name", "problem"} else value.strip()

    direction = normalized.get("failure_direction", "")
    family = normalized.get("construct_family", "")
    trigger = normalized.get("requirement_trigger", "")
    gold_state = normalized.get("gold_state", "")
    prediction_state = normalized.get("prediction_state", "")
    node_status = normalized.get("node_inventory_status", "")
    evidence_basis = normalized.get("evidence_basis", "")
    if direction and direction not in FAILURE_DIRECTIONS:
        errors.append(f"error_patterns[{index}].failure_direction is invalid: {direction!r}")
    if family and family not in CONSTRUCT_STATES:
        errors.append(f"error_patterns[{index}].construct_family is invalid: {family!r}")
    if family in REQUIREMENT_TRIGGERS and trigger not in REQUIREMENT_TRIGGERS[family]:
        errors.append(f"error_patterns[{index}].requirement_trigger is invalid for {family!r}: {trigger!r}")
    if family in CONSTRUCT_STATES:
        if gold_state not in CONSTRUCT_STATES[family]:
            errors.append(f"error_patterns[{index}].gold_state is invalid for {family!r}: {gold_state!r}")
        if prediction_state not in CONSTRUCT_STATES[family]:
            errors.append(f"error_patterns[{index}].prediction_state is invalid for {family!r}: {prediction_state!r}")
    if node_status and node_status not in NODE_INVENTORY_STATUSES:
        errors.append(f"error_patterns[{index}].node_inventory_status is invalid: {node_status!r}")
    if family in {"activity", "syntax"} and node_status and node_status != "not_applicable":
        errors.append(
            f"error_patterns[{index}].node_inventory_status must be 'not_applicable' for {family!r}"
        )
    if family in {"fork", "loop", "branch", "early_exit"} and node_status == "not_applicable":
        errors.append(
            f"error_patterns[{index}].node_inventory_status must describe inventory sufficiency for {family!r}"
        )
    if evidence_basis and evidence_basis not in EVIDENCE_BASES:
        errors.append(f"error_patterns[{index}].evidence_basis is invalid: {evidence_basis!r}")

    coarse_signals = pattern.get("coarse_failure_signals")
    if not isinstance(coarse_signals, list) or any(not isinstance(item, str) for item in coarse_signals):
        errors.append(f"error_patterns[{index}].coarse_failure_signals must be a string list")
    # Kept only for replaying older agent outputs. Recurrence is computed from
    # validated observations by Python instead of trusting this model label.
    evidence_strength = pattern.get("evidence_strength")
    if evidence_strength is not None and evidence_strength not in {
        "repeated_consistent",
        "repeated_mixed",
        "isolated",
        "uncertain",
    }:
        errors.append(f"error_patterns[{index}].evidence_strength is invalid: {evidence_strength!r}")
    downstream_guidance = pattern.get("downstream_guidance")
    if not isinstance(downstream_guidance, str) or not downstream_guidance.strip():
        errors.append(f"error_patterns[{index}].downstream_guidance must be a non-empty string")
    causes = pattern.get("possible_causes")
    if not isinstance(causes, list) or any(not isinstance(item, str) for item in causes):
        errors.append(f"error_patterns[{index}].possible_causes must be a string list")
    normalized_claims, claim_errors = _validate_evidence_claims(
        pattern,
        evidence_by_id=evidence_by_id,
        pattern_index=index,
        direction=direction,
        evidence_basis=evidence_basis,
    )
    normalized["evidence_claims"] = normalized_claims
    errors.extend(claim_errors)
    if evidence_basis == "compiler" and (family != "syntax" or trigger != "compiler_confirmed"):
        errors.append(f"error_patterns[{index}] may use compiler evidence only for compiler-confirmed syntax failures")
    return (normalized if not errors else None), errors


def validate_failure_analysis_payload(
    payload: dict[str, Any],
    *,
    evidence_catalog: list[dict[str, Any]],
    required_schema_version: str | None = None,
) -> FailureAnalysisValidationResult:
    if required_schema_version == ATOMIC_SCHEMA_VERSION and "error_attributions" not in payload:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=[],
            fatal_errors=[
                f"The configured taxonomy requires schema_version={ATOMIC_SCHEMA_VERSION!r} "
                "with error_attributions"
            ],
        )
    if "error_attributions" in payload and "error_patterns" in payload:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=[],
            fatal_errors=["Payload may not contain both error_attributions and error_patterns"],
        )
    if "error_attributions" in payload:
        return _validate_atomic_payload(payload, evidence_catalog=evidence_catalog)
    patterns = payload.get("error_patterns")
    if not isinstance(patterns, list) or not patterns:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=[],
            fatal_errors=["Payload must contain a non-empty error_patterns list"],
        )
    evidence_by_id = {
        str(item.get("evidence_id") or "").strip(): item
        for item in evidence_catalog
        if isinstance(item, dict) and str(item.get("evidence_id") or "").strip()
    }
    normalized_patterns: list[dict[str, Any]] = []
    rejected_patterns: list[dict[str, Any]] = []
    for index, pattern in enumerate(patterns):
        normalized, pattern_errors = _validate_pattern(pattern, evidence_by_id, index)
        if normalized is not None:
            normalized_patterns.append(normalized)
            continue
        raw_pattern = pattern if isinstance(pattern, dict) else {}
        rejected_patterns.append(
            {
                "pattern_index": index,
                "name": str(raw_pattern.get("name") or ""),
                "signature": mechanism_signature(raw_pattern),
                "supporting_evidence_ids": evidence_claim_ids(raw_pattern),
                "errors": pattern_errors,
            }
        )
    if not normalized_patterns:
        return FailureAnalysisValidationResult(
            normalized_payload=None,
            rejected_patterns=rejected_patterns,
            fatal_errors=["No valid error patterns remain after validation"],
        )
    normalized_payload = dict(payload)
    normalized_payload["error_patterns"] = normalized_patterns
    normalized_payload["evidence_catalog"] = evidence_catalog
    return FailureAnalysisValidationResult(
        normalized_payload=normalized_payload,
        rejected_patterns=rejected_patterns,
        fatal_errors=[],
    )


def _matches_rule(pattern: dict[str, Any], rule: dict[str, Any]) -> bool:
    match = rule.get("match")
    if not isinstance(match, dict):
        return False
    for field, expected in match.items():
        actual = pattern.get(field)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def match_mechanism(pattern: dict[str, Any], taxonomy: dict[str, Any]) -> dict[str, Any] | None:
    for rule in taxonomy.get("mechanisms", []):
        if isinstance(rule, dict) and _matches_rule(pattern, rule):
            return rule
    return None


CONCURRENCY_CUE = re.compile(
    r"\b(?:concurr(?:ent|ently|ency)?|parallel(?:ly)?|simultaneous(?:ly)?|overlap(?:ping)?|in tandem)\b|at the same time",
    re.IGNORECASE,
)
ITERATION_CUE = re.compile(r"\b(?:repeat(?:ed|edly)?|retry|retries|iterat(?:e|es|ed|ion|ive)|loop)\b", re.IGNORECASE)
ITERATION_BOUNDARY_CUE = re.compile(
    r"\b(?:until|while|as long as|condition|complete(?:d|ion)?|success|fail(?:ed|ure)?|normaliz(?:e|es|ed|ation)|limit|maximum|times|attempts?)\b",
    re.IGNORECASE,
)
EARLY_EXIT_CUE = re.compile(
    r"\b(?:terminate(?:s|d|ion)?|abort(?:s|ed)?|exit(?:s|ed)?|stop(?:s|ped)?|cancel(?:s|led)?|return immediately)\b|end (?:the )?(?:process|flow|workflow|operation)",
    re.IGNORECASE,
)
ENVIRONMENT_CONTEXT_CUE = re.compile(
    r"\b(?:environment|location|workspace|home page|homepage|page|window|screen|browser|application|portal|dashboard)\b",
    re.IGNORECASE,
)
INITIAL_STATE_CUE = re.compile(
    r"\b(?:initial(?:ly)?|already|currently|starts? with|begins? with|is open|is displayed|is logged in|state)\b",
    re.IGNORECASE,
)
TEMPORAL_CONTEXT_CUE = re.compile(
    r"\b(?:before|after|during|while|once|until|as soon as|at the start|in the meantime)\b",
    re.IGNORECASE,
)
PRECONDITION_CONTEXT_CUE = re.compile(
    r"\b(?:if|provided that|assuming that|only if|unless|on condition that|requires?)\b",
    re.IGNORECASE,
)
PERFORMED_ACTION_CUE = re.compile(
    r"\b(?:open|opens|opened|navigate|navigates|navigated|click|clicks|clicked|select|selects|selected|enter|enters|entered|import|imports|imported|create|creates|created|run|runs|ran|execute|executes|executed|perform|performs|performed)\b",
    re.IGNORECASE,
)


def requirement_trigger_is_grounded(trigger: str, quote: str) -> bool:
    if trigger == "explicit_concurrency":
        return bool(CONCURRENCY_CUE.search(quote))
    if trigger in {"ordinary_enumeration", "multiple_objects_same_action", "alternatives_or_sequence"}:
        return not CONCURRENCY_CUE.search(quote)
    if trigger == "explicit_iteration_with_exit":
        return bool(
            re.search(r"\b(?:until|while|as long as)\b", quote, re.IGNORECASE)
            or (ITERATION_CUE.search(quote) and ITERATION_BOUNDARY_CUE.search(quote))
        )
    if trigger in {"periodic_descriptor_only", "state_transition_description"}:
        return not (
            re.search(r"\b(?:until|while|as long as)\b", quote, re.IGNORECASE)
            or (ITERATION_CUE.search(quote) and ITERATION_BOUNDARY_CUE.search(quote))
        )
    if trigger == "explicit_early_exit":
        return bool(EARLY_EXIT_CUE.search(quote))
    if trigger == "environment_context":
        return bool(ENVIRONMENT_CONTEXT_CUE.search(quote)) and not bool(
            PERFORMED_ACTION_CUE.search(quote)
        )
    if trigger == "initial_state_context":
        return bool(INITIAL_STATE_CUE.search(quote))
    if trigger == "temporal_context":
        return bool(TEMPORAL_CONTEXT_CUE.search(quote))
    if trigger == "precondition_context":
        return bool(PRECONDITION_CONTEXT_CUE.search(quote))
    return True


def _dynamic_rule_template(
    pattern: dict[str, Any], taxonomy: dict[str, Any]
) -> dict[str, Any] | None:
    if taxonomy.get("version") != "v3" or taxonomy.get("policy_revision") != "open-hypothesis-v1":
        return None
    signature = mechanism_signature(pattern)
    for template in taxonomy.get("rule_templates", []):
        if not isinstance(template, dict) or not _matches_rule(pattern, template):
            continue
        try:
            positive = str(template["positive_trigger_template"]).format(**signature)
            negative = str(template["negative_boundary_template"]).format(**signature)
        except (KeyError, ValueError):
            continue
        if not positive.strip() or not negative.strip():
            continue
        return {
            "mechanism_id": hypothesis_id(signature, taxonomy=taxonomy),
            "hypothesis_id": hypothesis_id(signature, taxonomy=taxonomy),
            "candidate_eligible": True,
            "dynamic": True,
            "template_id": str(template.get("template_id") or ""),
            "positive_trigger": positive.strip(),
            "negative_boundary": negative.strip(),
            "match": dict(template.get("match") or {}),
        }
    return None


def resolve_candidate_rule(
    pattern: dict[str, Any], taxonomy: dict[str, Any]
) -> tuple[dict[str, Any] | None, str | None]:
    """Resolve a narrow rule without treating v3 taxonomy as a whitelist."""

    if str(pattern.get("requirement_trigger") or "") == "ambiguous":
        return None, "ambiguous_trigger"
    rule = match_mechanism(pattern, taxonomy)
    if rule is not None:
        if not rule.get("candidate_eligible", False):
            return None, "taxonomy_record_only"
        if pattern.get("evidence_basis") in {"gold_only", "ambiguous"}:
            return None, "evidence_basis_not_candidate_eligible"
        enriched = dict(rule)
        enriched["hypothesis_id"] = hypothesis_id(
            mechanism_signature(pattern), taxonomy=taxonomy
        )
        return enriched, None
    dynamic = _dynamic_rule_template(pattern, taxonomy)
    if dynamic is None:
        return None, "no_safe_rule_template"
    if pattern.get("evidence_basis") in {"gold_only", "ambiguous"}:
        return None, "evidence_basis_not_candidate_eligible"
    return dynamic, None


def _candidate_rule(pattern: dict[str, Any], taxonomy: dict[str, Any]) -> dict[str, Any] | None:
    rule, _ = resolve_candidate_rule(pattern, taxonomy)
    return rule


def _grounded_primary_ids(pattern: dict[str, Any]) -> set[str]:
    trigger = str(pattern.get("requirement_trigger") or "")
    return {
        str(claim.get("evidence_id") or "").strip()
        for claim in pattern.get("evidence_claims", [])
        if isinstance(claim, dict)
        and claim.get("role") == "primary"
        and requirement_trigger_is_grounded(trigger, str(claim.get("requirement_quote") or ""))
        and str(claim.get("evidence_id") or "").strip()
    }


def ambiguous_primary_evidence_ids(
    failure_analysis: dict[str, Any], taxonomy: dict[str, Any]
) -> set[str]:
    signatures_by_id: dict[str, set[tuple[str, ...]]] = defaultdict(set)
    for pattern in failure_analysis.get("error_patterns", []):
        if not isinstance(pattern, dict) or _candidate_rule(pattern, taxonomy) is None:
            continue
        signature = mechanism_signature_key(mechanism_signature(pattern))
        for evidence_id in _grounded_primary_ids(pattern):
            signatures_by_id[evidence_id].add(signature)
    return {
        evidence_id
        for evidence_id, signatures in signatures_by_id.items()
        if len(signatures) > 1
    }


def candidate_evidence_ids(
    pattern: dict[str, Any], *, ambiguous_ids: set[str] | None = None
) -> list[str]:
    excluded = ambiguous_ids or set()
    return sorted(_grounded_primary_ids(pattern) - excluded)


def candidate_exclusion_reasons(
    pattern: dict[str, Any],
    taxonomy: dict[str, Any],
    *,
    ambiguous_ids: set[str],
) -> list[str]:
    rule = match_mechanism(pattern, taxonomy)
    if not rule or not rule.get("candidate_eligible", False):
        return ["taxonomy_record_only"]
    if pattern.get("evidence_basis") in {"gold_only", "ambiguous"}:
        return ["evidence_basis_not_candidate_eligible"]
    reasons: list[str] = []
    primary_ids = set(evidence_claim_ids(pattern, role="primary"))
    if not primary_ids:
        reasons.append("no_primary_evidence")
    grounded_ids = _grounded_primary_ids(pattern)
    if primary_ids and not grounded_ids:
        reasons.append("requirement_trigger_not_grounded")
    if grounded_ids and not (grounded_ids - ambiguous_ids):
        reasons.append("ambiguous_primary_assignment")
    return reasons


def candidate_eligible_patterns(
    failure_analysis: dict[str, Any], taxonomy: dict[str, Any]
) -> list[dict[str, Any]]:
    eligible: list[dict[str, Any]] = []
    ambiguous_ids = ambiguous_primary_evidence_ids(failure_analysis, taxonomy)
    for pattern in failure_analysis.get("error_patterns", []):
        if not isinstance(pattern, dict):
            continue
        rule = _candidate_rule(pattern, taxonomy)
        if not rule or not candidate_evidence_ids(pattern, ambiguous_ids=ambiguous_ids):
            continue
        item = dict(pattern)
        item["mechanism_id"] = rule["mechanism_id"]
        eligible.append(item)
    return eligible


def candidate_eligible_attributions(
    failure_analysis: dict[str, Any], taxonomy: dict[str, Any]
) -> list[dict[str, Any]]:
    eligible: list[dict[str, Any]] = []
    for attribution in failure_analysis.get("error_attributions", []):
        if not isinstance(attribution, dict) or attribution.get("role") != "primary":
            continue
        rule = _candidate_rule(attribution, taxonomy)
        if not rule:
            continue
        raw_matching_quality = attribution.get("matching_quality")
        matching_quality = str(raw_matching_quality or "not_available")
        if raw_matching_quality is not None and matching_quality not in {"bijective", "not_available"}:
            continue
        if raw_matching_quality is not None and matching_quality == "not_available" and attribution.get("construct_family") != "syntax":
            continue
        item = dict(attribution)
        item["mechanism_id"] = rule["mechanism_id"]
        item["hypothesis_id"] = str(rule.get("hypothesis_id") or hypothesis_id(item, taxonomy=taxonomy))
        item["positive_trigger"] = str(rule.get("positive_trigger") or "")
        item["negative_boundary"] = str(rule.get("negative_boundary") or "")
        eligible.append(item)
    return eligible


def _build_atomic_mechanism_observations(
    failure_analysis: dict[str, Any],
    taxonomy: dict[str, Any],
    *,
    batch_id: int,
    analysis_summary: dict[str, float],
) -> list[dict[str, Any]]:
    evidence_by_id = {
        str(item.get("evidence_id") or ""): item
        for item in failure_analysis.get("evidence_catalog", [])
        if isinstance(item, dict) and str(item.get("evidence_id") or "")
    }
    grouped: dict[tuple[Any, ...], dict[str, Any]] = {}
    for attribution in failure_analysis.get("error_attributions", []):
        if not isinstance(attribution, dict):
            continue
        rule, resolution_reason = resolve_candidate_rule(attribution, taxonomy)
        evidence_basis = str(attribution.get("evidence_basis") or "")
        primary = attribution.get("role") == "primary"
        matching_quality = str(attribution.get("matching_quality") or "")
        matching_allowed = (
            not matching_quality
            or matching_quality == "bijective"
            or (matching_quality == "not_available" and attribution.get("construct_family") == "syntax")
        )
        candidate_eligible = bool(
            primary
            and rule
            and rule.get("candidate_eligible", False)
            and evidence_basis not in {"gold_only", "ambiguous"}
            and matching_allowed
        )
        if candidate_eligible:
            classification = "candidate"
        elif (rule and rule.get("classification") == "dataset_convention") or evidence_basis == "gold_only":
            classification = "dataset_convention"
        else:
            classification = "record_only"
        mechanism_id = str(rule.get("mechanism_id") or "") if rule else None
        signature = mechanism_signature(attribution)
        group_key = (
            *mechanism_signature_key(signature),
            mechanism_id,
            classification,
            evidence_basis,
        )
        observation = grouped.setdefault(
            group_key,
            {
                "batch_id": batch_id,
                "pattern_names": [],
                "patterns": [],
                "attributions": [],
                "mechanism_id": mechanism_id,
                "hypothesis_id": (
                    str(rule.get("hypothesis_id") or hypothesis_id(signature, taxonomy=taxonomy))
                    if rule
                    else hypothesis_id(signature, taxonomy=taxonomy)
                ),
                "parent_key": list(parent_signature_key(signature)),
                "child_key": list(child_signature_key(signature)),
                "mechanism_signature": signature,
                "classification": classification,
                "candidate_eligible": candidate_eligible,
                "evidence_basis": evidence_basis,
                "matching_quality": matching_quality or "not_available",
                "supporting_attribution_ids": [],
                "supporting_evidence_ids": [],
                "supporting_evidence": [],
                "evidence_catalog": list(evidence_by_id.values()),
                "analysis_summary": analysis_summary,
                "candidate_exclusion_reasons": [],
                "positive_trigger": str(rule.get("positive_trigger") or "") if rule else "",
                "negative_boundary": str(rule.get("negative_boundary") or "") if rule else "",
                "resolution_reason": resolution_reason,
            },
        )
        observation["attributions"].append(attribution)
        attribution_id = str(attribution.get("attribution_id") or "")
        evidence_id = str(attribution.get("evidence_id") or "")
        if candidate_eligible and attribution_id:
            observation["supporting_attribution_ids"].append(attribution_id)
        if candidate_eligible and evidence_id:
            observation["supporting_evidence_ids"].append(evidence_id)
        if not candidate_eligible:
            if not primary:
                observation["candidate_exclusion_reasons"].append("secondary_attribution")
            elif not rule or not rule.get("candidate_eligible", False):
                observation["candidate_exclusion_reasons"].append(
                    resolution_reason or "no_safe_rule_template"
                )
            elif evidence_basis in {"gold_only", "ambiguous"}:
                observation["candidate_exclusion_reasons"].append(
                    "evidence_basis_not_candidate_eligible"
                )
            elif not matching_allowed:
                observation["candidate_exclusion_reasons"].append("matching_not_candidate_eligible")

    observations: list[dict[str, Any]] = []
    for observation in grouped.values():
        observation["supporting_attribution_ids"] = sorted(
            set(observation["supporting_attribution_ids"])
        )
        observation["supporting_evidence_ids"] = sorted(
            set(observation["supporting_evidence_ids"])
        )
        observation["candidate_exclusion_reasons"] = sorted(
            set(observation["candidate_exclusion_reasons"])
        )
        observation["attributions"] = sorted(
            observation["attributions"],
            key=lambda item: str(item.get("attribution_id") or ""),
        )
        observation["supporting_evidence"] = [
            evidence_by_id[evidence_id]
            for evidence_id in observation["supporting_evidence_ids"]
            if evidence_id in evidence_by_id
        ]
        observation["evidence_catalog"] = [
            evidence_by_id[evidence_id]
            for evidence_id in sorted(evidence_by_id)
        ]
        observations.append(observation)
    observations.sort(
        key=lambda item: (
            int(item["batch_id"]),
            mechanism_signature_key(item["mechanism_signature"]),
            str(item.get("mechanism_id") or ""),
        )
    )
    return observations


def build_mechanism_observations(
    failure_analysis: dict[str, Any],
    taxonomy: dict[str, Any],
    *,
    batch_id: int,
    analysis_summary: dict[str, float],
) -> list[dict[str, Any]]:
    """Map validated patterns to auditable, batch-scoped mechanism observations."""
    if "error_attributions" in failure_analysis:
        return _build_atomic_mechanism_observations(
            failure_analysis,
            taxonomy,
            batch_id=batch_id,
            analysis_summary=analysis_summary,
        )
    evidence_by_id = {
        str(item.get("evidence_id") or ""): item
        for item in failure_analysis.get("evidence_catalog", [])
        if isinstance(item, dict) and str(item.get("evidence_id") or "")
    }
    ambiguous_ids = ambiguous_primary_evidence_ids(failure_analysis, taxonomy)
    grouped: dict[tuple[Any, ...], dict[str, Any]] = {}
    for pattern in failure_analysis.get("error_patterns", []):
        if not isinstance(pattern, dict):
            continue
        rule = match_mechanism(pattern, taxonomy)
        evidence_basis = str(pattern.get("evidence_basis") or "")
        exclusions = candidate_exclusion_reasons(
            pattern,
            taxonomy,
            ambiguous_ids=ambiguous_ids,
        )
        primary_ids = candidate_evidence_ids(pattern, ambiguous_ids=ambiguous_ids)
        if not exclusions and primary_ids:
            classification = "candidate"
            mechanism_id: str | None = str(rule.get("mechanism_id") or "")
            candidate_eligible = True
        elif (rule and rule.get("classification") == "dataset_convention") or evidence_basis == "gold_only":
            classification = "dataset_convention"
            mechanism_id = str(rule.get("mechanism_id") or "") if rule else None
            candidate_eligible = False
        else:
            classification = "record_only"
            mechanism_id = str(rule.get("mechanism_id") or "") if rule else None
            candidate_eligible = False
        signature = mechanism_signature(pattern)
        group_key = (
            *mechanism_signature_key(signature),
            mechanism_id,
            classification,
            evidence_basis,
        )
        observation = grouped.setdefault(
            group_key,
            {
                "batch_id": batch_id,
                "pattern_names": [],
                "patterns": [],
                "mechanism_id": mechanism_id,
                "mechanism_signature": signature,
                "classification": classification,
                "candidate_eligible": candidate_eligible,
                "evidence_basis": evidence_basis,
                "supporting_evidence_ids": [],
                "supporting_evidence": [],
                "analysis_summary": analysis_summary,
                "candidate_exclusion_reasons": exclusions,
                "positive_trigger": str(rule.get("positive_trigger") or "") if rule else "",
                "negative_boundary": str(rule.get("negative_boundary") or "") if rule else "",
            },
        )
        observation["pattern_names"].append(str(pattern.get("name") or ""))
        observation["patterns"].append(pattern)
        observation["candidate_exclusion_reasons"] = sorted(
            set(observation["candidate_exclusion_reasons"]) | set(exclusions)
        )
        observation["supporting_evidence_ids"].extend(
            primary_ids if candidate_eligible else evidence_claim_ids(pattern)
        )

    observations: list[dict[str, Any]] = []
    for observation in grouped.values():
        evidence_ids = sorted(set(observation["supporting_evidence_ids"]))
        observation["pattern_names"] = sorted(set(observation["pattern_names"]))
        observation["supporting_evidence_ids"] = evidence_ids
        observation["supporting_evidence"] = [
            evidence_by_id[evidence_id]
            for evidence_id in evidence_ids
            if evidence_id in evidence_by_id
        ]
        observations.append(observation)
    observations.sort(
        key=lambda item: (
            int(item["batch_id"]),
            mechanism_signature_key(item["mechanism_signature"]),
            str(item.get("mechanism_id") or ""),
        )
    )
    return observations


SELECTED_PATTERN_FIELDS = (
    "name",
    *SIGNATURE_FIELDS,
    "evidence_basis",
)


def sanitize_selected_failure_analysis(
    selected_observation: dict[str, Any],
) -> dict[str, Any]:
    """Keep only Python-counted evidence and verifiable pattern metadata."""
    if selected_observation.get("attributions") is not None:
        supporting_attribution_ids = {
            str(item).strip()
            for item in selected_observation.get("supporting_attribution_ids", [])
            if str(item).strip()
        }
        attributions = [
            dict(item)
            for item in selected_observation.get("attributions", [])
            if isinstance(item, dict)
            and str(item.get("attribution_id") or "") in supporting_attribution_ids
            and item.get("role") == "primary"
        ]
        attributions.sort(key=lambda item: str(item.get("attribution_id") or ""))
        if {
            str(item.get("attribution_id") or "") for item in attributions
        } != supporting_attribution_ids:
            return {
                "schema_version": ATOMIC_SCHEMA_VERSION,
                "error_attributions": [],
                "evidence_catalog": [],
            }
        evidence_ids = {
            str(item.get("evidence_id") or "") for item in attributions
        }
        selected_anchors_by_evidence: dict[str, dict[str, set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )
        for attribution in attributions:
            evidence_id = str(attribution.get("evidence_id") or "")
            anchor_kind = str(attribution.get("anchor_kind") or "")
            error_anchor = str(attribution.get("error_anchor") or "")
            source_field = ANCHOR_KIND_TO_EVIDENCE_FIELD.get(anchor_kind)
            if evidence_id and source_field and error_anchor:
                selected_anchors_by_evidence[evidence_id][source_field].add(
                    error_anchor
                )
        evidence_by_id = {
            str(item.get("evidence_id") or ""): item
            for item in selected_observation.get("supporting_evidence", [])
            if isinstance(item, dict)
            and str(item.get("evidence_id") or "") in evidence_ids
        }
        if set(evidence_by_id) != evidence_ids:
            return {
                "schema_version": ATOMIC_SCHEMA_VERSION,
                "error_attributions": [],
                "evidence_catalog": [],
            }
        narrowed_evidence_by_id: dict[str, dict[str, Any]] = {}
        for evidence_id, evidence in evidence_by_id.items():
            narrowed = dict(evidence)
            selected_fields = selected_anchors_by_evidence[evidence_id]
            for field in ANCHOR_FIELD_TO_KIND:
                narrowed[field] = sorted(selected_fields.get(field, set()))
            candidates = evidence.get("attribution_candidates")
            if isinstance(candidates, list):
                selected_pairs = {
                    (ANCHOR_FIELD_TO_KIND[field], anchor)
                    for field, anchors in selected_fields.items()
                    for anchor in anchors
                }
                narrowed["attribution_candidates"] = [
                    candidate
                    for candidate in candidates
                    if isinstance(candidate, dict)
                    and (
                        str(candidate.get("anchor_kind") or ""),
                        str(candidate.get("error_anchor") or ""),
                    )
                    in selected_pairs
                ]
            narrowed_evidence_by_id[evidence_id] = narrowed
        return {
            "schema_version": ATOMIC_SCHEMA_VERSION,
            "error_attributions": attributions,
            "evidence_catalog": [
                narrowed_evidence_by_id[evidence_id]
                for evidence_id in sorted(narrowed_evidence_by_id)
            ],
        }
    supporting_ids = {
        item.strip()
        for item in selected_observation.get("supporting_evidence_ids", [])
        if isinstance(item, str) and item.strip()
    }
    patterns: list[dict[str, Any]] = []
    for raw_pattern in selected_observation.get("patterns", []):
        if not isinstance(raw_pattern, dict):
            continue
        claims = [
            {
                field: str(raw_claim.get(field) or "").strip()
                for field in ("evidence_id", "role", "requirement_quote", "error_anchor")
            }
            for raw_claim in raw_pattern.get("evidence_claims", [])
            if isinstance(raw_claim, dict)
            and raw_claim.get("role") == "primary"
            and str(raw_claim.get("evidence_id") or "").strip() in supporting_ids
        ]
        claims.sort(key=lambda item: item["evidence_id"])
        if not claims:
            continue
        pattern = {
            field: raw_pattern[field]
            for field in SELECTED_PATTERN_FIELDS
            if field in raw_pattern
        }
        pattern["evidence_claims"] = claims
        patterns.append(pattern)

    patterns.sort(
        key=lambda item: (
            mechanism_signature_key(item),
            str(item.get("name") or ""),
        )
    )
    evidence_by_id = {
        str(item.get("evidence_id") or "").strip(): item
        for item in selected_observation.get("supporting_evidence", [])
        if isinstance(item, dict)
        and str(item.get("evidence_id") or "").strip() in supporting_ids
    }
    claim_ids = {
        claim["evidence_id"]
        for pattern in patterns
        for claim in pattern["evidence_claims"]
    }
    if claim_ids != supporting_ids or set(evidence_by_id) != supporting_ids:
        return {"error_patterns": [], "evidence_catalog": []}
    return {
        "error_patterns": patterns,
        "evidence_catalog": [
            evidence_by_id[evidence_id]
            for evidence_id in sorted(evidence_by_id)
        ],
    }


def validate_selected_revision(
    payload: dict[str, Any], *, failure_analysis: dict[str, Any], taxonomy: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    signature = payload.get("selected_mechanism_signature")
    if not isinstance(signature, dict):
        return None, ["selected_mechanism_signature must be an object"]
    normalized_signature = mechanism_signature(signature)
    atomic = "error_attributions" in failure_analysis
    matching_items = [
        item
        for item in (
            candidate_eligible_attributions(failure_analysis, taxonomy)
            if atomic
            else candidate_eligible_patterns(failure_analysis, taxonomy)
        )
        if mechanism_signature_key(item) == mechanism_signature_key(normalized_signature)
    ]
    if not matching_items:
        errors.append("selected_mechanism_signature does not match candidate-eligible batch evidence")
    rule, _ = resolve_candidate_rule(matching_items[0], taxonomy) if matching_items else (None, None)
    mechanism_id = str(payload.get("mechanism_id") or "").strip()
    if not rule or not rule.get("candidate_eligible", False):
        errors.append("selected_mechanism_signature does not map to an eligible child hypothesis")
    elif mechanism_id != rule.get("mechanism_id"):
        errors.append("mechanism_id does not match the selected mechanism signature")

    supporting_ids = payload.get("supporting_evidence_ids")
    if not isinstance(supporting_ids, list) or not supporting_ids:
        errors.append("supporting_evidence_ids must be a non-empty list")
        normalized_ids: list[str] = []
    else:
        normalized_ids = [str(item).strip() for item in supporting_ids]
        allowed_ids = {
            str(item.get("evidence_id") or "")
            for item in matching_items
            if atomic and str(item.get("evidence_id") or "")
        }
        if not atomic:
            allowed_ids = {
                evidence_id
                for pattern in matching_items
                for evidence_id in evidence_claim_ids(pattern, role="primary")
            }
        unknown = sorted(set(normalized_ids) - allowed_ids)
        if unknown:
            errors.append(f"supporting_evidence_ids are not evidence for the selected mechanism: {', '.join(unknown)}")
        if len(set(normalized_ids)) != len(normalized_ids):
            errors.append("supporting_evidence_ids contains duplicates")
    if errors:
        return None, errors
    normalized = dict(payload)
    normalized["selected_mechanism_signature"] = normalized_signature
    normalized["supporting_evidence_ids"] = normalized_ids
    if rule:
        normalized["hypothesis_id"] = str(
            rule.get("hypothesis_id") or hypothesis_id(normalized_signature, taxonomy=taxonomy)
        )
    if atomic:
        expected_attribution_ids = sorted(
            str(item.get("attribution_id") or "")
            for item in matching_items
            if str(item.get("attribution_id") or "")
        )
        supplied_attribution_ids = payload.get("supporting_attribution_ids")
        if supplied_attribution_ids is not None and (
            not isinstance(supplied_attribution_ids, list)
            or sorted(set(str(item) for item in supplied_attribution_ids))
            != expected_attribution_ids
        ):
            return None, ["supporting_attribution_ids must match selected atomic attributions"]
        normalized["supporting_attribution_ids"] = expected_attribution_ids
    return normalized, []


def validate_epoch_revision_selection(
    payload: dict[str, Any], *, selected_mechanism: dict[str, Any]
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    expected_id = str(selected_mechanism.get("mechanism_id") or "")
    expected_hypothesis_id = str(selected_mechanism.get("hypothesis_id") or "")
    actual_id = str(payload.get("mechanism_id") or "")
    if actual_id != expected_id:
        errors.append("mechanism_id does not match Python's selected mechanism")
    signature = payload.get("selected_mechanism_signature")
    if not isinstance(signature, dict):
        errors.append("selected_mechanism_signature must be an object")
        normalized_signature: dict[str, str] = {}
    else:
        normalized_signature = mechanism_signature(signature)
        if mechanism_signature_key(normalized_signature) != mechanism_signature_key(
            selected_mechanism.get("mechanism_signature", {})
        ):
            errors.append("selected_mechanism_signature does not match Python's selected mechanism")
    expected_ids = sorted(set(selected_mechanism.get("supporting_evidence_ids", [])))
    supporting_ids = payload.get("supporting_evidence_ids")
    if supporting_ids is None:
        normalized_ids = expected_ids
    elif not isinstance(supporting_ids, list):
        errors.append("supporting_evidence_ids must be a list when provided")
        normalized_ids = []
    else:
        normalized_ids = [str(item).strip() for item in supporting_ids]
        if sorted(set(normalized_ids)) != expected_ids or len(normalized_ids) != len(set(normalized_ids)):
            errors.append("supporting_evidence_ids must exactly match Python's selected evidence IDs")
    if errors:
        return None, errors
    normalized = dict(payload)
    normalized["mechanism_id"] = expected_id
    normalized["selected_mechanism_signature"] = normalized_signature
    normalized["supporting_evidence_ids"] = normalized_ids
    return normalized, []


def make_revision_scope(
    *,
    selected_mechanism: dict[str, Any],
    prompt_gap: str,
    section: str,
    repair_type: str,
    existing_prompt_quote: str,
    supporting_attribution_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "mechanism_id": str(selected_mechanism.get("mechanism_id") or ""),
        "mechanism_signature": mechanism_signature(
            selected_mechanism.get("mechanism_signature", {})
        ),
        "supporting_attribution_ids": sorted(
            set(
                str(item)
                for item in (
                    supporting_attribution_ids
                    if supporting_attribution_ids is not None
                    else selected_mechanism.get("supporting_attribution_ids", [])
                )
                if str(item)
            )
        ),
        "prompt_gap": str(prompt_gap or ""),
        "section": str(section or "").strip().lower(),
        "repair_type": str(repair_type or ""),
        "existing_prompt_quote": (
            str(existing_prompt_quote or "") if prompt_gap == "ambiguous" else ""
        ),
    }


def revision_scope_key(scope: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(scope.get("mechanism_id") or ""),
        mechanism_signature_key(scope.get("mechanism_signature", {})),
        str(scope.get("prompt_gap") or ""),
        str(scope.get("section") or ""),
        str(scope.get("repair_type") or ""),
        str(scope.get("existing_prompt_quote") or ""),
    )


def bind_revision_to_mechanism(
    payload: dict[str, Any],
    *,
    selected_mechanism: dict[str, Any],
    supporting_evidence_ids: list[str] | None = None,
    revision_scope: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Attach Python-owned mechanism metadata to one model-authored revision item."""
    errors: list[str] = []
    expected_id = str(selected_mechanism.get("mechanism_id") or "")
    expected_hypothesis_id = str(selected_mechanism.get("hypothesis_id") or "")
    expected_signature = mechanism_signature(selected_mechanism.get("mechanism_signature", {}))
    expected_ids = sorted(
        set(supporting_evidence_ids or selected_mechanism.get("supporting_evidence_ids", []))
    )
    expected_attribution_ids = sorted(
        set(
            str(item)
            for item in selected_mechanism.get("supporting_attribution_ids", [])
            if str(item)
        )
    )
    for field, expected in (
        ("mechanism_id", expected_id),
        ("hypothesis_id", expected_hypothesis_id),
        ("selected_mechanism_signature", expected_signature),
        ("supporting_evidence_ids", expected_ids),
        ("supporting_attribution_ids", expected_attribution_ids),
    ):
        if field not in payload:
            continue
        actual = payload[field]
        if field == "selected_mechanism_signature" and isinstance(actual, dict):
            actual = mechanism_signature(actual)
        elif field == "supporting_evidence_ids" and isinstance(actual, list):
            actual = sorted(set(str(item) for item in actual))
        elif field == "supporting_attribution_ids" and isinstance(actual, list):
            actual = sorted(set(str(item) for item in actual))
        if actual != expected:
            errors.append(f"Model output may not override Python-owned {field}")

    plans = payload.get("revision_plan")
    if not isinstance(plans, list) or len(plans) != 1 or not isinstance(plans[0], dict):
        errors.append("Revision output must contain exactly one revision_plan item")
    if errors:
        return None, errors

    normalized = dict(payload)
    plan = dict(plans[0])
    section = str(plan.get("section") or "").strip().lower()
    expected_scope = dict(
        revision_scope
        or make_revision_scope(
            selected_mechanism=selected_mechanism,
            prompt_gap="",
            section=section,
            repair_type="",
            existing_prompt_quote="",
            supporting_attribution_ids=expected_attribution_ids,
        )
    )
    expected_scope["supporting_attribution_ids"] = sorted(
        set(expected_scope.get("supporting_attribution_ids", expected_attribution_ids))
    )
    if "revision_scope" in plan and plan["revision_scope"] != expected_scope:
        return None, ["Model output may not override Python-owned revision_scope"]
    for field, expected in (
        ("positive_trigger", str(selected_mechanism.get("positive_trigger") or "")),
        ("negative_boundary", str(selected_mechanism.get("negative_boundary") or "")),
    ):
        if field in plan and plan[field] != expected:
            return None, [f"Model output may not override taxonomy-owned {field}"]
        plan[field] = expected
    plan["revision_scope"] = expected_scope
    normalized["mechanism_id"] = expected_id
    if expected_hypothesis_id:
        normalized["hypothesis_id"] = expected_hypothesis_id
    normalized["selected_mechanism_signature"] = expected_signature
    normalized["supporting_evidence_ids"] = expected_ids
    normalized["supporting_attribution_ids"] = expected_scope[
        "supporting_attribution_ids"
    ]
    normalized["revision_plan"] = [plan]
    return normalized, []


def _evidence_impact(mechanism_id: str, evidence: dict[str, Any]) -> float:
    if mechanism_id in {
        "explicit_actions_merged",
        "context_clause_as_activity",
        "environment_context_as_activity",
        "initial_state_context_as_activity",
        "temporal_context_as_activity",
        "precondition_context_as_activity",
        "single_action_split_into_unsupported_substeps",
        "heading_or_label_as_activity",
    }:
        return 1.0 - float(evidence.get("llm_node_f1", 0.0))
    if mechanism_id in {
        "construct_syntax_invalid",
        "wrapper_syntax_invalid",
        "conditional_label_syntax_invalid",
        "block_balance_syntax_invalid",
    }:
        return 0.0 if evidence.get("plantuml_compiles", False) else 1.0
    return 1.0 - float(evidence.get("llm_relation_f1", 0.0))


def select_epoch_mechanism(
    observations: list[dict[str, Any]],
    *,
    evidence_memory: list[dict[str, Any]] | None = None,
    prompt_hash: str | None = None,
    current_iteration: int | None = None,
    min_batches: int = 2,
    min_cases: int = 3,
    min_datasets: int = 2,
    min_consistency: float = 2 / 3,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Select one current child hypothesis without a generality proof gate.

    The legacy threshold arguments remain accepted for replay compatibility but
    are intentionally ignored by the open-hypothesis policy.
    """

    del min_batches, min_cases, min_datasets, min_consistency
    historical_memory = [
        item
        for item in (evidence_memory or [])
        if current_iteration is None or int(item.get("iteration", -1)) != current_iteration
    ]
    groups: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for item in observations:
        signature = item.get("mechanism_signature")
        if item.get("candidate_eligible") and isinstance(signature, dict):
            groups[child_signature_key(signature)].append(item)

    all_active_memory = [
        item
        for item in historical_memory
        if isinstance(item, dict)
        and (prompt_hash is None or str(item.get("prompt_hash") or "") == prompt_hash)
        and str(item.get("status") or "") not in {"historical", "rejected"}
    ]
    memory = [
        item
        for item in all_active_memory
        if item.get("candidate_eligible") is not False
        and str(item.get("role") or "primary") == "primary"
    ]
    rejected_hypotheses = {
        str(item.get("hypothesis_id") or "")
        for item in historical_memory
        if isinstance(item, dict)
        and (prompt_hash is None or str(item.get("prompt_hash") or "") == prompt_hash)
        and str(item.get("status") or "") == "rejected"
    }

    def memory_signature(item: dict[str, Any]) -> dict[str, str]:
        signature = item.get("mechanism_signature")
        if isinstance(signature, dict):
            return mechanism_signature(signature)
        child_key = item.get("child_key")
        if isinstance(child_key, list) and len(child_key) == len(SIGNATURE_FIELDS):
            return dict(zip(SIGNATURE_FIELDS, [str(value) for value in child_key]))
        return {}

    memory_by_child: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for item in memory:
        signature = memory_signature(item)
        if len(child_signature_key(signature)) == len(SIGNATURE_FIELDS):
            memory_by_child[child_signature_key(signature)].append(item)

    candidates: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    parent_report: dict[tuple[str, ...], dict[str, Any]] = {}
    for key, items in groups.items():
        first = items[0]
        mechanism_id = str(first.get("mechanism_id") or "")
        signature = mechanism_signature(first.get("mechanism_signature", {}))
        hypothesis = str(first.get("hypothesis_id") or hypothesis_id(signature, taxonomy={"version": "v3", "policy_revision": "open-hypothesis-v1"}))
        parent_key = parent_signature_key(signature)
        batches = {int(item.get("batch_id", 0)) for item in items}
        evidence_by_case: dict[tuple[str, str], dict[str, Any]] = {}
        evidence_by_id_all: dict[str, dict[str, Any]] = {}
        attributions_by_id_all: dict[str, dict[str, Any]] = {}
        evidence_ids: set[str] = set()
        attribution_ids: set[str] = set()
        current_attribution_ids: set[str] = set()
        current_evidence_ids: set[str] = set()
        for item in items:
            for attribution in item.get("attributions", []):
                if isinstance(attribution, dict) and str(attribution.get("attribution_id") or ""):
                    attributions_by_id_all[str(attribution["attribution_id"])] = dict(attribution)
            attribution_ids.update(
                str(value)
                for value in item.get("supporting_attribution_ids", [])
                if str(value)
            )
            current_attribution_ids.update(
                str(value)
                for value in item.get("supporting_attribution_ids", [])
                if str(value)
            )
            for evidence in item.get("supporting_evidence", []):
                if not isinstance(evidence, dict):
                    continue
                evidence_id = str(evidence.get("evidence_id") or "")
                dataset = str(evidence.get("dataset") or "")
                case_id = str(evidence.get("case_id") or "")
                if evidence_id:
                    evidence_ids.add(evidence_id)
                    current_evidence_ids.add(evidence_id)
                    evidence_by_id_all[evidence_id] = dict(evidence)
                if dataset and case_id:
                    evidence_by_case.setdefault((dataset, case_id), evidence)
        if not current_attribution_ids and all(not item.get("attributions") for item in items):
            # v1/v2 replay observations have no atomic IDs. Keep them auditable
            # without allowing them to masquerade as v3 attribution evidence.
            current_attribution_ids.update(
                f"legacy:{int(item.get('batch_id', 0))}:{mechanism_id}"
                for item in items
            )

        historical_attribution_ids: set[str] = set()
        historical_evidence_ids: set[str] = set()
        for memory_item in memory_by_child.get(key, []):
            attribution_id = str(memory_item.get("attribution_id") or "")
            evidence_id = str(memory_item.get("evidence_id") or "")
            if attribution_id:
                historical_attribution_ids.add(attribution_id)
                attribution_ids.add(attribution_id)
                if isinstance(memory_item.get("attribution"), dict):
                    attributions_by_id_all[attribution_id] = dict(memory_item["attribution"])
            if evidence_id:
                historical_evidence_ids.add(evidence_id)
                evidence_ids.add(evidence_id)
            evidence = memory_item.get("evidence")
            if isinstance(evidence, dict):
                if evidence_id:
                    evidence_by_id_all[evidence_id] = dict(evidence)
                dataset = str(evidence.get("dataset") or "")
                case_id = str(evidence.get("case_id") or "")
                if dataset and case_id:
                    evidence_by_case.setdefault((dataset, case_id), evidence)
        datasets = {dataset for dataset, _ in evidence_by_case}

        observations_by_batch: dict[int, dict[str, Any]] = {}
        for item in items:
            batch_id = int(item.get("batch_id", 0))
            merged = observations_by_batch.setdefault(
                batch_id,
                {
                    **item,
                    "pattern_names": [],
                    "patterns": [],
                    "attributions": [],
                    "supporting_attribution_ids": [],
                    "supporting_evidence_ids": [],
                    "supporting_evidence": [],
                },
            )
            merged["pattern_names"].extend(item.get("pattern_names", []))
            merged["patterns"].extend(item.get("patterns", []))
            merged["attributions"].extend(item.get("attributions", []))
            merged["supporting_attribution_ids"].extend(
                item.get("supporting_attribution_ids", [])
            )
            merged["supporting_evidence_ids"].extend(item.get("supporting_evidence_ids", []))
            merged["supporting_evidence"].extend(item.get("supporting_evidence", []))
        for merged in observations_by_batch.values():
            merged["pattern_names"] = sorted(set(merged["pattern_names"]))
            merged["supporting_attribution_ids"] = sorted(
                set(merged["supporting_attribution_ids"])
            )
            merged["supporting_evidence_ids"] = sorted(set(merged["supporting_evidence_ids"]))
            attributions_by_id = {
                str(attribution.get("attribution_id") or ""): attribution
                for attribution in merged["attributions"]
                if isinstance(attribution, dict)
                and str(attribution.get("attribution_id") or "")
            }
            merged["attributions"] = [
                attributions_by_id[attribution_id]
                for attribution_id in sorted(attributions_by_id)
            ]
            evidence_by_merged_id = {
                str(evidence.get("evidence_id") or ""): evidence
                for evidence in merged["supporting_evidence"]
                if isinstance(evidence, dict) and str(evidence.get("evidence_id") or "")
            }
            merged["supporting_evidence"] = [
                evidence_by_merged_id[evidence_id]
                for evidence_id in sorted(evidence_by_merged_id)
            ]

        opposite_batches: set[int] = set()
        conflict_attribution_ids: set[str] = set()
        for other in observations:
            other_signature = mechanism_signature(other.get("mechanism_signature", {}))
            if (
                signature["gold_state"] != signature["prediction_state"]
                and other_signature["construct_family"] == signature["construct_family"]
                and other_signature["requirement_trigger"] == signature["requirement_trigger"]
                and other_signature["gold_state"] == signature["prediction_state"]
                and other_signature["prediction_state"] == signature["gold_state"]
                and other.get("evidence_basis") in {"requirement_and_gold", "requirement_only"}
                and any(
                    isinstance(attribution, dict) and attribution.get("role") == "primary"
                    for attribution in other.get("attributions", [])
                )
            ):
                opposite_batches.add(int(other.get("batch_id", 0)))
                conflict_attribution_ids.update(
                    str(attribution.get("attribution_id") or "")
                    for attribution in other.get("attributions", [])
                    if isinstance(attribution, dict)
                    and attribution.get("role") == "primary"
                    and str(attribution.get("attribution_id") or "")
                )
        for memory_item in all_active_memory:
            other_signature = memory_signature(memory_item)
            if (
                signature["gold_state"] != signature["prediction_state"]
                and other_signature.get("construct_family") == signature["construct_family"]
                and other_signature.get("requirement_trigger") == signature["requirement_trigger"]
                and other_signature.get("gold_state") == signature["prediction_state"]
                and other_signature.get("prediction_state") == signature["gold_state"]
                and str(memory_item.get("evidence_basis") or "") in {"requirement_and_gold", "requirement_only"}
            ):
                conflict_attribution_ids.add(str(memory_item.get("attribution_id") or ""))
        consistency = len(batches) / (len(batches) + len(opposite_batches)) if batches or opposite_batches else 0.0
        impacts = [_evidence_impact(mechanism_id, evidence) for evidence in evidence_by_case.values()]
        candidate = {
            "mechanism_id": mechanism_id,
            "hypothesis_id": hypothesis,
            "parent_key": list(parent_key),
            "child_key": list(key),
            "mechanism_signature": signature,
            "matching_quality": str(first.get("matching_quality") or "bijective"),
            "supporting_batch_count": len(batches),
            "supporting_batches": sorted(batches),
            "supporting_dataset_count": len(datasets),
            "supporting_datasets": sorted(datasets),
            "supporting_case_count": len(evidence_by_case),
            "supporting_attribution_ids": sorted(attribution_ids),
            "supporting_evidence_ids": sorted(evidence_ids),
            "supporting_evidence": [
                evidence_by_id_all[evidence_id]
                for evidence_id in sorted(evidence_by_id_all)
            ],
            "supporting_attributions": [
                attributions_by_id_all[attribution_id]
                for attribution_id in sorted(attributions_by_id_all)
            ],
            "current_supporting_attribution_ids": sorted(current_attribution_ids),
            "current_supporting_evidence_ids": sorted(current_evidence_ids),
            "historical_supporting_attribution_ids": sorted(historical_attribution_ids),
            "historical_supporting_evidence_ids": sorted(historical_evidence_ids),
            "historical_supporting_evidence": [
                dict(memory_item["evidence"])
                for memory_item in memory_by_child.get(key, [])
                if isinstance(memory_item.get("evidence"), dict)
            ],
            "historical_supporting_attributions": [
                dict(memory_item["attribution"])
                for memory_item in memory_by_child.get(key, [])
                if isinstance(memory_item.get("attribution"), dict)
            ],
            "opposite_batch_count": len(opposite_batches),
            "opposite_batches": sorted(opposite_batches),
            "consistency": consistency,
            "conflict_status": "scope_conflict" if conflict_attribution_ids else "clear",
            "conflict_attribution_ids": sorted(conflict_attribution_ids),
            "estimated_error_impact": statistics.fmean(impacts) if impacts else 0.0,
            "positive_trigger": str(first.get("positive_trigger") or ""),
            "negative_boundary": str(first.get("negative_boundary") or ""),
            "supporting_batch_observations": [
                observations_by_batch[batch_id]
                for batch_id in sorted(observations_by_batch)
            ],
        }
        parent_bucket = parent_report.setdefault(
            parent_key,
            {
                "parent_key": list(parent_key),
                "child_hypotheses": [],
                "supporting_attribution_ids": [],
                "supporting_case_count": 0,
            },
        )
        parent_bucket["child_hypotheses"].append(hypothesis)
        parent_bucket["supporting_attribution_ids"].extend(attribution_ids)
        parent_bucket["supporting_case_count"] = max(
            int(parent_bucket["supporting_case_count"]), len(evidence_by_case)
        )
        reasons = []
        if not current_attribution_ids:
            reasons.append("no_current_epoch_activation")
        if hypothesis in rejected_hypotheses:
            reasons.append("already_rejected_for_prompt")
        if conflict_attribution_ids:
            reasons.append("scope_conflict")
        if not str(first.get("positive_trigger") or "").strip() or not str(first.get("negative_boundary") or "").strip():
            reasons.append("no_safe_rule_template")
        if reasons:
            candidate["rejection_reasons"] = reasons
            rejected.append(candidate)
        else:
            candidates.append(candidate)

    candidates.sort(
        key=lambda item: (
            -item["estimated_error_impact"],
            -len(item["current_supporting_attribution_ids"]),
            -item["supporting_batch_count"],
            -item["supporting_case_count"],
            -len(item["historical_supporting_attribution_ids"]),
            item["hypothesis_id"],
        )
    )
    hidden_key = "supporting_batch_observations"
    for bucket in parent_report.values():
        bucket["child_hypotheses"] = sorted(set(bucket["child_hypotheses"]))
        bucket["supporting_attribution_ids"] = sorted(set(bucket["supporting_attribution_ids"]))
    report = {
        "eligible_candidates": [{key: value for key, value in item.items() if key != hidden_key} for item in candidates],
        "rejected_clusters": [{key: value for key, value in item.items() if key != hidden_key} for item in rejected],
        "parent_clusters": sorted(parent_report.values(), key=lambda item: tuple(item["parent_key"])),
        "selected_mechanism_id": candidates[0]["mechanism_id"] if candidates else None,
        "selected_hypothesis_id": candidates[0]["hypothesis_id"] if candidates else None,
    }
    return (candidates[0] if candidates else None), report


def calibration_statistics(values: Iterable[float], *, validation_repeats: int, metric_resolution: float = 0.0) -> dict[str, float]:
    samples = [float(value) for value in values]
    if not samples:
        raise ValueError("Calibration requires at least one value")
    sample_std = statistics.stdev(samples) if len(samples) >= 2 else 0.0
    suggested = max(metric_resolution, 1.645 * math.sqrt(2 / validation_repeats) * sample_std)
    return {
        "count": float(len(samples)),
        "mean": statistics.fmean(samples),
        "sample_std": sample_std,
        "min": min(samples),
        "max": max(samples),
        "range": max(samples) - min(samples),
        "suggested_min_delta": suggested,
    }


def export_legacy_mechanism_evidence(source_run: Path, runs_dir: Path) -> tuple[Path, dict[str, int]]:
    """Export old index-based pattern support into a new, separate audit run."""
    source_run = source_run.resolve()
    if not source_run.exists():
        raise FileNotFoundError(source_run)
    audit_dir = make_run_dir(runs_dir, f"mechanism-audit-{source_run.name}")
    write_text(audit_dir / "source_run.json", json.dumps({"source_run": str(source_run)}, indent=2))
    evidence_path = audit_dir / "mechanism_evidence.jsonl"
    invalid_path = audit_dir / "invalid_evidence.jsonl"
    write_text(evidence_path, "")
    write_text(invalid_path, "")
    valid_count = 0
    invalid_count = 0
    pattern_count = 0
    audit_rows: list[dict[str, Any]] = []

    output_paths = sorted(source_run.glob("iteration_*/train_batches/batch_*/agents/failure_analysis.output.json"))
    for output_path in output_paths:
        input_path = output_path.with_name("failure_analysis.input.json")
        if not input_path.exists():
            continue
        raw_output = extract_json_object(read_text(output_path))
        input_payload = json.loads(read_text(input_path))
        if raw_output is None:
            append_jsonl(invalid_path, {"output_path": str(output_path), "reason": "invalid_json"})
            invalid_count += 1
            continue
        iteration_match = re.search(r"iteration_(\d+)", str(output_path))
        batch_match = re.search(r"batch_(\d+)", str(output_path))
        iteration = int(iteration_match.group(1)) if iteration_match else 0
        batch_id = int(batch_match.group(1)) if batch_match else 0
        case_evidence = input_payload.get("case_evidence", [])
        atomic_attributions = raw_output.get("error_attributions")
        if isinstance(atomic_attributions, list):
            case_by_evidence_id = {
                str(case.get("evidence_id") or ""): case
                for case in case_evidence
                if isinstance(case, dict) and str(case.get("evidence_id") or "")
            }
            for attribution_index, attribution in enumerate(atomic_attributions, start=1):
                if not isinstance(attribution, dict):
                    continue
                pattern_count += 1
                evidence_id = str(attribution.get("evidence_id") or "")
                case = case_by_evidence_id.get(evidence_id)
                if case is None:
                    append_jsonl(
                        invalid_path,
                        {
                            "output_path": str(output_path),
                            "attribution_index": attribution_index,
                            "evidence_id": evidence_id,
                            "reason": "attribution_evidence_not_found",
                        },
                    )
                    invalid_count += 1
                    continue
                row = {
                    "evidence_id": evidence_id,
                    "generation_run": source_run.name,
                    "iteration": iteration,
                    "batch_id": batch_id,
                    "dataset": case.get("dataset"),
                    "case_id": case.get("case_id"),
                    "legacy_pattern_name": "",
                    "failure_direction": attribution.get("failure_direction"),
                    "evidence_strength": "",
                    "problem": attribution.get("causal_rationale"),
                    "requirement": case.get("requirement"),
                    "prediction": case.get("prediction"),
                    "ground_truth": case.get("ground_truth"),
                }
                append_jsonl(evidence_path, row)
                audit_rows.append(
                    {
                        "evidence_id": evidence_id,
                        "dataset": case.get("dataset"),
                        "case_id": case.get("case_id"),
                        "failure_direction": attribution.get("failure_direction"),
                        "legacy_pattern_name": "",
                        "construct_family": attribution.get("construct_family"),
                        "requirement_trigger": attribution.get("requirement_trigger"),
                        "gold_state": attribution.get("gold_state"),
                        "prediction_state": attribution.get("prediction_state"),
                        "node_inventory_status": attribution.get("node_inventory_status"),
                        "evidence_basis": attribution.get("evidence_basis"),
                        "mechanism_id": "",
                        "audit_status": "atomic_v3",
                        "audit_notes": attribution.get("causal_rationale", ""),
                    }
                )
                valid_count += 1
            continue
        for pattern_index, pattern in enumerate(raw_output.get("error_patterns", []), start=1):
            if not isinstance(pattern, dict):
                continue
            pattern_count += 1
            for legacy_index in pattern.get("supporting_cases", []):
                if not isinstance(legacy_index, int) or legacy_index < 1 or legacy_index > len(case_evidence):
                    append_jsonl(
                        invalid_path,
                        {
                            "output_path": str(output_path),
                            "pattern_index": pattern_index,
                            "pattern_name": pattern.get("name"),
                            "supporting_case": legacy_index,
                            "available_case_count": len(case_evidence),
                            "reason": "supporting_case_out_of_range",
                        },
                    )
                    invalid_count += 1
                    continue
                case = case_evidence[legacy_index - 1]
                evidence_id = make_case_evidence_id(
                    generation_run=source_run.name,
                    iteration=iteration,
                    batch_id=batch_id,
                    dataset=str(case.get("dataset") or ""),
                    case_id=str(case.get("case_id") or ""),
                )
                row = {
                    "evidence_id": evidence_id,
                    "generation_run": source_run.name,
                    "iteration": iteration,
                    "batch_id": batch_id,
                    "dataset": case.get("dataset"),
                    "case_id": case.get("case_id"),
                    "legacy_pattern_name": pattern.get("name"),
                    "failure_direction": pattern.get("failure_direction"),
                    "evidence_strength": pattern.get("evidence_strength"),
                    "problem": pattern.get("problem"),
                    "requirement": case.get("requirement"),
                    "prediction": case.get("prediction"),
                    "ground_truth": case.get("ground_truth"),
                }
                append_jsonl(evidence_path, row)
                audit_rows.append(
                    {
                        "evidence_id": evidence_id,
                        "dataset": case.get("dataset"),
                        "case_id": case.get("case_id"),
                        "failure_direction": pattern.get("failure_direction"),
                        "legacy_pattern_name": pattern.get("name"),
                        "construct_family": "",
                        "requirement_trigger": "",
                        "gold_state": "",
                        "prediction_state": "",
                        "node_inventory_status": "",
                        "evidence_basis": "",
                        "mechanism_id": "",
                        "audit_status": "",
                        "audit_notes": "",
                    }
                )
                valid_count += 1

    with (audit_dir / "mechanism_audit.csv").open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "evidence_id",
            "dataset",
            "case_id",
            "failure_direction",
            "legacy_pattern_name",
            "construct_family",
            "requirement_trigger",
            "gold_state",
            "prediction_state",
            "node_inventory_status",
            "evidence_basis",
            "mechanism_id",
            "audit_status",
            "audit_notes",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(audit_rows)
    summary = {
        "source_pattern_count": pattern_count,
        "valid_reference_count": valid_count,
        "invalid_reference_count": invalid_count,
        "unique_case_count": len({(row["dataset"], row["case_id"]) for row in audit_rows}),
    }
    write_text(audit_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    write_text(
        audit_dir / "mechanism_audit_report.md",
        "# Mechanism Evidence Audit Export\n\n"
        f"- source run: `{source_run}`\n"
        f"- patterns: {pattern_count}\n"
        f"- valid references: {valid_count}\n"
        f"- invalid references: {invalid_count}\n",
    )
    return audit_dir, summary
