"""Prompt-gap localization and editing agents for the selector workflow."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from llm import LLMClient
from prompt_ops import extract_json_object, parse_prompt_sections
from utils.io import read_prompt_file, write_text


PROMPT_GAP_LOCALIZATION_SCHEMA = "prompt-gap-localization-v1"
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
}
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


def _validate_prompt_gap_localization(
    payload: dict[str, Any], *, current_prompt: str
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
    }, []


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
    members = [
        item for item in selected_group.get("members", []) if isinstance(item, dict)
    ]
    agent_payload = {
        "schema_version": "prompt-gap-localization-input-v1",
        "current_prompt_sections": parse_prompt_sections(current_prompt),
        "selected_error_group": {
            "group_id": selected_group.get("group_id"),
            "group_summary": selected_group.get("group_summary"),
            "shared_cause": selected_group.get("shared_cause"),
            "finding_count": len(members),
            "anchor_kinds": sorted(
                {str(item.get("anchor_kind") or "") for item in members}
            ),
            "representative_errors": selected_group.get("representative_errors", []),
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
                "schema_version": "prompt-gap-localization-repair-v1",
                "original_localization_input": agent_payload,
                "previous_output": previous_output,
                "validation_errors": validation_errors,
                "repair_instruction": (
                    "Return one complete corrected prompt-gap-localization-v1 object. "
                    "Repair only the reported schema, length, status, section, operation, and exact-quote violations."
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
            parsed, current_prompt=current_prompt
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
                    "Repair only the reported schema, length, or retrospective-language violations."
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
