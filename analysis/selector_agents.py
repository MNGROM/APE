"""Prompt-gap localization and editing agents for the selector workflow."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from llm import LLMClient
from prompt_ops import (
    extract_json_object,
    normalized_contract_contains,
    normalized_contract_occurrences,
    parse_prompt_sections,
)
from utils.io import read_prompt_file, write_text


PROMPT_GAP_LOCALIZATION_SCHEMA = "prompt-gap-localization-v2"
PROMPT_GAP_LOCALIZATION_INPUT_SCHEMA = "prompt-gap-localization-input-v2"
PROMPT_EDIT_SCHEMA = "prompt-edit-plan-v2"
LOCALIZATION_SECTIONS = {
    "agent task",
    "input",
    "output",
    "workflow",
    "knowledge",
    "rule",
}
PROMPT_GAP_LOCALIZATION_FIELDS = {
    "schema_version",
    "localization_status",
    "prompt_gap",
    "section",
    "operation",
    "existing_prompt_quote",
    "rationale",
    "group_consistency",
    "member_checks",
    "shared_repair",
}
MEMBER_CHECK_FIELDS = {"finding_id", "compatible", "conflict_reason"}
SHARED_REPAIR_FIELD_ORDER = (
    "input_trigger",
    "structural_operation",
    "preservation_boundary",
)
SHARED_REPAIR_FIELDS = set(SHARED_REPAIR_FIELD_ORDER)
PROMPT_EDIT_FIELDS = {
    "schema_version",
    "intent",
    "positive_trigger",
    "negative_boundary",
    "change_instruction",
}
RETROSPECTIVE_EDIT_CUE = re.compile(
    r"\b(?:prediction|predicted|gold|ground\s+truth|evaluator|metric|f1|"
    r"validation|training\s+case|dataset|missing\s+node|extra\s+node)\b",
    re.IGNORECASE,
)


def _shared_repair_contract_errors(
    localization: dict[str, Any], values: dict[str, str]
) -> list[str]:
    """Require Editor wording to retain the frozen Localization scope."""
    if str(localization.get("localization_status") or "").strip().lower() not in {
        "localized",
        "already_covered",
    }:
        return []
    repair = localization.get("shared_repair")
    if not isinstance(repair, dict):
        return []
    errors: list[str] = []
    bindings = (
        ("positive_trigger", "input_trigger"),
        ("positive_trigger", "structural_operation"),
        ("negative_boundary", "preservation_boundary"),
    )
    for output_field, repair_field in bindings:
        fragment = str(repair.get(repair_field) or "").strip()
        if not fragment:
            errors.append(f"shared_repair.{repair_field} must be non-empty")
            continue
        output = values[output_field]
        if not normalized_contract_contains(output, fragment):
            errors.append(
                f"{output_field} must contain shared_repair.{repair_field} once as one "
                "contiguous canonical token sequence; required fragment: "
                + json.dumps(fragment, ensure_ascii=False)
            )
        elif normalized_contract_occurrences(output, fragment) != 1:
            errors.append(
                f"{output_field} must contain shared_repair.{repair_field} exactly once; "
                "required fragment: "
                + json.dumps(fragment, ensure_ascii=False)
            )
    return errors


def _validate_prompt_gap_localization(
    payload: dict[str, Any], *, current_prompt: str, selected_finding_ids: list[int]
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if set(payload) != PROMPT_GAP_LOCALIZATION_FIELDS:
        errors.append("Prompt-gap localization contains unsupported or missing fields")
    if payload.get("schema_version") != PROMPT_GAP_LOCALIZATION_SCHEMA:
        errors.append(f"schema_version must be {PROMPT_GAP_LOCALIZATION_SCHEMA!r}")
    status = str(payload.get("localization_status") or "").strip().lower()
    prompt_gap = str(payload.get("prompt_gap") or "").strip().lower()
    section = str(payload.get("section") or "").strip().lower()
    operation = str(payload.get("operation") or "").strip().lower()
    quote = str(payload.get("existing_prompt_quote") or "")
    rationale = str(payload.get("rationale") or "").strip()
    consistency = str(payload.get("group_consistency") or "").strip().lower()
    raw_member_checks = payload.get("member_checks")
    raw_shared_repair = payload.get("shared_repair")
    if status not in {"localized", "already_covered", "no_prompt_gap"}:
        errors.append("localization_status must be localized, already_covered, or no_prompt_gap")
    if prompt_gap not in {"missing", "ambiguous", "already_covered", "not_applicable"}:
        errors.append("prompt_gap is invalid")
    if section and section not in LOCALIZATION_SECTIONS:
        errors.append("section is invalid")
    if operation not in {"append_new", "replace_existing", "none"}:
        errors.append("operation is invalid")
    if not rationale or len(rationale) > 500:
        errors.append("rationale must contain 1-500 characters")
    if consistency not in {"coherent", "incoherent"}:
        errors.append("group_consistency must be coherent or incoherent")

    expected_ids = [
        finding_id
        for finding_id in selected_finding_ids
        if isinstance(finding_id, int)
        and not isinstance(finding_id, bool)
        and finding_id > 0
    ]
    if len(expected_ids) != len(selected_finding_ids) or len(set(expected_ids)) != len(
        expected_ids
    ):
        errors.append("selected finding IDs must be unique positive integers")
    member_checks: list[dict[str, Any]] = []
    observed_ids: list[int] = []
    if not isinstance(raw_member_checks, list):
        errors.append("member_checks must be a list")
    else:
        for index, raw_check in enumerate(raw_member_checks):
            if not isinstance(raw_check, dict) or set(raw_check) != MEMBER_CHECK_FIELDS:
                errors.append(
                    f"member_checks[{index}] must contain exactly the member-check fields"
                )
                continue
            finding_id = raw_check.get("finding_id")
            compatible = raw_check.get("compatible")
            conflict_reason = str(raw_check.get("conflict_reason") or "").strip()
            if (
                not isinstance(finding_id, int)
                or isinstance(finding_id, bool)
                or finding_id <= 0
            ):
                errors.append(f"member_checks[{index}].finding_id must be positive")
                continue
            observed_ids.append(finding_id)
            if not isinstance(compatible, bool):
                errors.append(f"member_checks[{index}].compatible must be boolean")
                continue
            if compatible and conflict_reason:
                errors.append(
                    f"member_checks[{index}] compatible=true requires an empty conflict_reason"
                )
            if not compatible and (not conflict_reason or len(conflict_reason) > 500):
                errors.append(
                    f"member_checks[{index}] incompatible members require a 1-500 character conflict_reason"
                )
            member_checks.append(
                {
                    "finding_id": finding_id,
                    "compatible": compatible,
                    "conflict_reason": conflict_reason,
                }
            )
    duplicate_ids = sorted(
        {finding_id for finding_id in observed_ids if observed_ids.count(finding_id) > 1}
    )
    unknown_ids = sorted(set(observed_ids) - set(expected_ids))
    missing_ids = sorted(set(expected_ids) - set(observed_ids))
    if duplicate_ids:
        errors.append(f"member_checks repeats finding IDs: {duplicate_ids}")
    if unknown_ids:
        errors.append(f"member_checks contains unknown finding IDs: {unknown_ids}")
    if missing_ids:
        errors.append(f"member_checks omits finding IDs: {missing_ids}")

    shared_repair: dict[str, str] = {}
    if not isinstance(raw_shared_repair, dict) or set(raw_shared_repair) != SHARED_REPAIR_FIELDS:
        errors.append("shared_repair must contain exactly the shared-repair fields")
    else:
        shared_repair = {
            field: str(raw_shared_repair.get(field) or "").strip()
            for field in SHARED_REPAIR_FIELD_ORDER
        }
        for field, value in shared_repair.items():
            if len(value) > 500:
                errors.append(f"shared_repair.{field} exceeds 500 characters")
    try:
        sections = parse_prompt_sections(current_prompt)
    except ValueError as exc:
        return None, [str(exc)]
    section_text = sections.get(section, "") if section else ""
    if status == "localized":
        if prompt_gap not in {"missing", "ambiguous"}:
            errors.append("localized must use prompt_gap=missing or ambiguous")
        if not section:
            errors.append("localized must declare a target section")
        if operation not in {"append_new", "replace_existing"}:
            errors.append("localized must use append_new or replace_existing")
        if prompt_gap == "ambiguous" and operation != "replace_existing":
            errors.append("ambiguous Prompt guidance must use replace_existing")
        if section_text.strip() == "(None)" and (
            operation != "replace_existing" or quote != "(None)"
        ):
            errors.append("a blank '(None)' section must be replaced exactly")
        if operation == "append_new" and quote:
            errors.append("append_new must use an empty existing_prompt_quote")
        if operation == "replace_existing" and (
            not quote or section_text.count(quote) != 1
        ):
            errors.append("replace_existing quote must occur exactly once in the target section")
    elif status == "already_covered":
        if prompt_gap != "already_covered" or operation != "none" or not section or not quote:
            errors.append(
                "already_covered must declare its section, exact quote, prompt_gap, and operation=none"
            )
        elif section_text.count(quote) != 1:
            errors.append("already_covered quote must occur exactly once in the target section")
    elif status == "no_prompt_gap":
        if prompt_gap != "not_applicable" or section or operation != "none" or quote:
            errors.append("no_prompt_gap must not declare a Prompt edit")
    if status in {"localized", "already_covered"}:
        if consistency != "coherent":
            errors.append(f"{status} requires group_consistency=coherent")
        if member_checks and not all(item["compatible"] for item in member_checks):
            errors.append(f"{status} requires every member to be compatible")
        if shared_repair and any(not value for value in shared_repair.values()):
            errors.append(f"{status} requires every shared_repair field")
    if consistency == "coherent" and member_checks and not all(
        item["compatible"] for item in member_checks
    ):
        errors.append("coherent groups require every member to be compatible")
    if consistency == "incoherent":
        incompatible = [item for item in member_checks if not item["compatible"]]
        if status != "no_prompt_gap":
            errors.append("incoherent groups must use localization_status=no_prompt_gap")
        if not incompatible:
            errors.append("incoherent groups require at least one incompatible member")
        if shared_repair and any(shared_repair.values()):
            errors.append("incoherent groups must not declare a shared repair")
    if errors:
        return None, errors
    return {
        "schema_version": PROMPT_GAP_LOCALIZATION_SCHEMA,
        "localization_status": status,
        "prompt_gap": prompt_gap,
        "section": section,
        "operation": operation,
        "existing_prompt_quote": quote,
        "rationale": rationale,
        "group_consistency": consistency,
        "member_checks": sorted(member_checks, key=lambda item: item["finding_id"]),
        "shared_repair": shared_repair,
    }, []


def localization_member_evidence(selected_group: dict[str, Any]) -> list[dict[str, Any]]:
    members = [
        item for item in selected_group.get("members", []) if isinstance(item, dict)
    ]
    return [
        {
            "finding_id": int(item.get("finding_id") or 0),
            "anchor_kind": str(item.get("anchor_kind") or ""),
            "requirement_quote": str(item.get("requirement_quote") or ""),
            "error_anchor": str(item.get("error_anchor") or ""),
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
        for item in sorted(members, key=lambda item: int(item.get("finding_id") or 0))
    ]


def localize_selector_group(
    *,
    current_prompt: str,
    selected_group: dict[str, Any],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
    recurrence: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    member_evidence = localization_member_evidence(selected_group)
    selected_finding_ids = [item["finding_id"] for item in member_evidence]
    agent_payload = {
        "schema_version": PROMPT_GAP_LOCALIZATION_INPUT_SCHEMA,
        "current_prompt_sections": parse_prompt_sections(current_prompt),
        "selected_error_group": {
            "group_id": selected_group.get("group_id"),
            "group_summary": selected_group.get("group_summary"),
            "shared_cause": selected_group.get("shared_cause"),
            "finding_count": len(member_evidence),
            "anchor_kinds": sorted(
                {str(item.get("anchor_kind") or "") for item in member_evidence}
            ),
            "representative_errors": selected_group.get("representative_errors", []),
            "member_evidence": member_evidence,
        },
    }
    if recurrence:
        agent_payload["exact_recurrence"] = dict(recurrence)
    write_text(output_input_path, json.dumps(agent_payload, ensure_ascii=False, indent=2))
    system_prompt = read_prompt_file(
        args.error_localization_prompt_path, label="prompt-gap localization"
    )
    previous_output: Any = None
    validation_errors: list[str] = []
    for attempt in range(1, 3):
        user_payload: dict[str, Any]
        if attempt == 1:
            user_payload = agent_payload
        else:
            user_payload = {
                "schema_version": "prompt-gap-localization-repair-v2",
                "original_localization_input": agent_payload,
                "previous_output": previous_output,
                "validation_errors": validation_errors,
                "repair_instruction": (
                    "Return one complete corrected prompt-gap-localization-v2 object. "
                    "Repair only the reported schema, member-consistency, shared-repair, "
                    "length, status, section, operation, and exact-quote violations."
                ),
            }
        raw = llm_client.chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, indent=2)},
            ],
            temperature=args.localization_temperature,
            max_tokens=args.localization_max_tokens,
            thinking=args.localization_thinking,
            state_dir=state_dir,
            retry_phase="prompt_gap_localization" if attempt == 1 else "prompt_gap_localization_repair",
            retry_context={
                "iteration": iteration,
                "output_path": str(output_path),
                "schema_attempt": attempt,
            },
        )
        write_text(
            output_path.with_name(f"{output_path.stem}.attempt_{attempt}.raw.txt"),
            raw,
        )
        write_text(output_path, raw)
        parsed = extract_json_object(raw)
        if parsed is None:
            previous_output = raw
            validation_errors = ["Prompt-gap localization did not return JSON"]
            continue
        previous_output = parsed
        normalized, validation_errors = _validate_prompt_gap_localization(
            parsed,
            current_prompt=current_prompt,
            selected_finding_ids=selected_finding_ids,
        )
        if normalized is not None:
            write_text(output_path, json.dumps(normalized, ensure_ascii=False, indent=2))
            return normalized
    write_text(
        output_path.with_suffix(".rejected.txt"),
        "\n".join(validation_errors or ["Prompt-gap localization remained invalid"]) + "\n",
    )
    return None


def propose_selector_edit(
    *,
    current_prompt: str,
    selected_group: dict[str, Any],
    localization: dict[str, Any],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    sections = parse_prompt_sections(current_prompt)
    target_section = str(localization.get("section") or "")
    payload = {
        "schema_version": "prompt-edit-input-v2",
        "selected_error_group": {
            key: selected_group.get(key)
            for key in ("group_id", "group_summary", "shared_cause", "representative_errors")
        },
        "localization": localization,
        "target_section": target_section,
        "target_section_text": sections.get(target_section, ""),
    }
    write_text(output_input_path, json.dumps(payload, ensure_ascii=False, indent=2))
    system_prompt = read_prompt_file(args.prompt_editor_prompt_path, label="prompt editor")
    previous_output: Any = None
    validation_errors: list[str] = []
    for attempt in range(1, 3):
        user_payload: dict[str, Any]
        if attempt == 1:
            user_payload = payload
        else:
            user_payload = {
                "schema_version": "prompt-edit-plan-repair-v1",
                "original_editor_input": payload,
                "previous_output": previous_output,
                "validation_errors": validation_errors,
                "repair_instruction": (
                    "Return one complete corrected prompt-edit-plan-v2 object. "
                    "Repair every reported violation, including canonical preservation or "
                    "occurrence violations. For each required shared_repair fragment, copy all "
                    "words in their original order as one contiguous span exactly once; only "
                    "case, punctuation, and whitespace may change. Do not paraphrase, reorder, "
                    "inflect, delete, or insert words inside a canonical span."
                ),
            }
        raw = llm_client.chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, indent=2)},
            ],
            temperature=args.editor_temperature,
            max_tokens=args.editor_max_tokens,
            thinking=args.editor_thinking,
            state_dir=state_dir,
            retry_phase="prompt_edit" if attempt == 1 else "prompt_edit_repair",
            retry_context={
                "iteration": iteration,
                "output_path": str(output_path),
                "schema_attempt": attempt,
            },
        )
        write_text(
            output_path.with_name(f"{output_path.stem}.attempt_{attempt}.raw.txt"),
            raw,
        )
        write_text(output_path, raw)
        parsed = extract_json_object(raw)
        validation_errors = []
        if parsed is None:
            previous_output = raw
            validation_errors = ["Prompt editor did not return JSON"]
            continue
        previous_output = parsed
        if set(parsed) != PROMPT_EDIT_FIELDS:
            validation_errors.append(
                "Prompt editor output must contain exactly the prompt-edit-plan-v2 fields"
            )
        if parsed.get("schema_version") != PROMPT_EDIT_SCHEMA:
            validation_errors.append(f"schema_version must be {PROMPT_EDIT_SCHEMA!r}")
        values = {
            "intent": str(parsed.get("intent") or "").strip(),
            "positive_trigger": str(parsed.get("positive_trigger") or "").strip(),
            "negative_boundary": str(parsed.get("negative_boundary") or "").strip(),
            "change_instruction": str(parsed.get("change_instruction") or "").strip(),
        }
        limits = {
            "intent": 500,
            "positive_trigger": 500,
            "negative_boundary": 500,
            "change_instruction": 800,
        }
        for field, value in values.items():
            if not value or len(value) > limits[field]:
                validation_errors.append(
                    f"{field} must contain 1-{limits[field]} characters"
                )
        for field in ("positive_trigger", "negative_boundary"):
            if RETROSPECTIVE_EDIT_CUE.search(values[field]):
                validation_errors.append(f"{field} contains retrospective evaluator language")
            if "##" in values[field]:
                validation_errors.append(f"{field} must not contain a Prompt heading")
        if values["positive_trigger"] == values["negative_boundary"]:
            validation_errors.append("positive_trigger and negative_boundary must differ")
        validation_errors.extend(_shared_repair_contract_errors(localization, values))
        if validation_errors:
            continue
        normalized = {"schema_version": PROMPT_EDIT_SCHEMA, **values}
        write_text(output_path, json.dumps(normalized, ensure_ascii=False, indent=2))
        return normalized
    write_text(
        output_path.with_suffix(".rejected.txt"),
        "\n".join(validation_errors or ["Prompt editor output remained invalid"]) + "\n",
    )
    return None


def build_rewriter_plan(
    *, localization: dict[str, Any], editor_plan: dict[str, Any]
) -> dict[str, Any]:
    return {
        "revision_plan": [
            {
                "section": localization["section"],
                "operation": localization["operation"],
                "text_to_modify": localization["existing_prompt_quote"],
                "intent": editor_plan["intent"],
                "change_instruction": editor_plan["change_instruction"],
                "positive_trigger": editor_plan["positive_trigger"],
                "negative_boundary": editor_plan["negative_boundary"],
            }
        ]
    }
