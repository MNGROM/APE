"""Prompt parsing and edit application."""

from __future__ import annotations

import json
import re
from typing import Any

from config import REQUIRED_PROMPT_HEADINGS, SECTION_HEADING_BY_NAME, SECTION_NAMES
from prediction import strip_code_fence

REVISION_OPERATIONS = {
    "append_new",
    "replace_existing",
    "qualify_existing",
    "merge_existing",
}

PROMPT_GAP_STATUSES = {"missing", "ambiguous", "already_covered"}
ERROR_LOCALIZATION_REPAIR_TYPES = {
    "activity_extraction",
    "relation_grounding",
    "construct_selection",
    "anti_hallucination",
    "output_format",
    "mixed_or_uncertain",
}


def strip_markdown_fence(text: str) -> str:
    match = re.search(r"```(?:markdown|md)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else text.strip()


def normalize_prompt_headings(candidate: str) -> str:
    normalized = candidate.strip()
    heading_names = [heading.replace("## ", "") for heading in REQUIRED_PROMPT_HEADINGS]
    for heading_name in heading_names:
        pattern = rf"(?im)^#{{1,6}}\s*{re.escape(heading_name)}\s*$"
        normalized = re.sub(pattern, f"## {heading_name}", normalized)
    return normalized


def parse_prompt_sections(prompt: str) -> dict[str, str]:
    normalized = normalize_prompt_headings(prompt)
    pattern = re.compile(r"(?im)^##\s+(.+?)\s*$")
    matches = list(pattern.finditer(normalized))
    sections: dict[str, str] = {}
    seen: list[str] = []
    for idx, match in enumerate(matches):
        name = match.group(1).strip().lower()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(normalized)
        if name in SECTION_NAMES:
            if name in sections:
                raise ValueError(f"Duplicate section heading: {name}")
            sections[name] = normalized[start:end].strip()
            seen.append(name)
    missing = [name for name in SECTION_NAMES if name not in sections]
    if missing:
        raise ValueError(f"Missing required prompt sections: {', '.join(missing)}")
    if seen != list(SECTION_NAMES):
        raise ValueError("Prompt sections must keep the required order")
    return sections


def render_prompt_sections(sections: dict[str, str]) -> str:
    parts: list[str] = []
    for name in SECTION_NAMES:
        heading = SECTION_HEADING_BY_NAME[name]
        content = sections.get(name, "").strip()
        parts.append(f"{heading}\n\n{content}".rstrip())
    return "\n\n".join(parts).strip() + "\n"


def extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = strip_markdown_fence(text)
    try:
        payload = json.loads(stripped)
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        pass

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            payload = json.loads(stripped[start : end + 1])
            return payload if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def validate_prompt_edit_payload(payload: dict[str, Any], *, max_sections: int | None) -> tuple[bool, list[str]]:
    errors: list[str] = []
    edits = payload.get("edits")
    if not isinstance(edits, list) or not edits:
        errors.append("Payload must contain a non-empty edits list")
        return False, errors
    if max_sections is not None and max_sections > 0 and len(edits) > max_sections:
        errors.append(f"At most {max_sections} sections may be modified")

    edited_sections: set[str] = set()
    for idx, edit in enumerate(edits, start=1):
        if not isinstance(edit, dict):
            errors.append(f"Edit {idx} must be an object")
            continue
        section = str(edit.get("section") or "").strip().lower()
        operation = str(edit.get("operation") or "").strip().lower()
        content = edit.get("content")
        if section not in SECTION_NAMES:
            errors.append(f"Edit {idx} has invalid section: {section!r}")
        if section in edited_sections:
            errors.append(f"Section {section!r} is edited more than once")
        edited_sections.add(section)
        if operation not in {"replace", "append"}:
            errors.append(f"Edit {idx} has invalid operation: {operation!r}")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"Edit {idx} must provide non-empty string content")
        if isinstance(content, str) and re.search(r"(?im)^##\s+", content):
            errors.append(f"Edit {idx} content must not contain markdown section headings")
    return not errors, errors


def normalize_prompt_revision_plan(payload: dict[str, Any]) -> dict[str, Any]:
    revision_plan = payload.get("revision_plan")
    if not isinstance(revision_plan, list):
        return payload

    normalized_plan: list[dict[str, Any]] = []
    section_to_item: dict[str, dict[str, Any]] = {}

    for item in revision_plan:
        if not isinstance(item, dict):
            normalized_plan.append(item)
            continue

        section = str(item.get("section") or "").strip().lower()
        if section not in SECTION_NAMES:
            normalized_plan.append(item)
            continue

        intent = item.get("intent")
        change_instruction = item.get("change_instruction")
        operation = str(item.get("operation") or "append_new").strip().lower()
        text_to_modify = item.get("text_to_modify")
        intent_text = str(intent).strip() if isinstance(intent, str) else ""
        instruction_text = str(change_instruction).strip() if isinstance(change_instruction, str) else ""

        if section not in section_to_item:
            merged_item = dict(item)
            merged_item["section"] = section
            merged_item["operation"] = operation
            if isinstance(text_to_modify, str):
                merged_item["text_to_modify"] = text_to_modify.strip()
            section_to_item[section] = merged_item
            normalized_plan.append(merged_item)
            continue

        merged_item = section_to_item[section]
        existing_intent = str(merged_item.get("intent") or "").strip()
        existing_instruction = str(merged_item.get("change_instruction") or "").strip()

        if intent_text:
            merged_item["intent"] = _merge_revision_texts(existing_intent, intent_text, label="Combined intent")
        if instruction_text:
            merged_item["change_instruction"] = _merge_revision_texts(
                existing_instruction,
                instruction_text,
                label="Combine these requested changes into one coherent section revision",
            )
        if operation != "append_new":
            merged_item["operation"] = operation
        if isinstance(text_to_modify, str) and text_to_modify.strip():
            existing_text = str(merged_item.get("text_to_modify") or "").strip()
            merged_item["text_to_modify"] = _merge_revision_texts(
                existing_text,
                text_to_modify.strip(),
                label="Text to modify",
            )

    normalized_payload = dict(payload)
    normalized_payload["revision_plan"] = normalized_plan
    return normalized_payload


def _merge_revision_texts(existing: str, new: str, *, label: str) -> str:
    if not existing:
        return new
    if new in existing:
        return existing
    if existing.startswith(label + ":"):
        return f"{existing}; {new}"
    return f"{label}: {existing}; {new}"


def validate_prompt_revision_plan(
    payload: dict[str, Any],
    *,
    max_sections: int | None,
    current_prompt: str | None = None,
    require_boundaries: bool = False,
    require_scope: bool = False,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    revision_plan = payload.get("revision_plan")
    if not isinstance(revision_plan, list) or not revision_plan:
        errors.append("Payload must contain a non-empty revision_plan list")
        return False, errors
    if max_sections is not None and max_sections > 0 and len(revision_plan) > max_sections:
        errors.append(f"At most {max_sections} sections may be revised")

    planned_sections: set[str] = set()
    for idx, item in enumerate(revision_plan, start=1):
        if not isinstance(item, dict):
            errors.append(f"Revision plan item {idx} must be an object")
            continue
        section = str(item.get("section") or "").strip().lower()
        operation = str(item.get("operation") or "append_new").strip().lower()
        text_to_modify = item.get("text_to_modify")
        intent = item.get("intent")
        change_instruction = item.get("change_instruction")
        positive_trigger = item.get("positive_trigger")
        negative_boundary = item.get("negative_boundary")
        revision_scope = item.get("revision_scope")
        if section not in SECTION_NAMES:
            errors.append(f"Revision plan item {idx} has invalid section: {section!r}")
        if operation not in REVISION_OPERATIONS:
            errors.append(f"Revision plan item {idx} has invalid operation: {operation!r}")
        if operation != "append_new" and (not isinstance(text_to_modify, str) or not text_to_modify.strip()):
            errors.append(f"Revision plan item {idx} must provide non-empty string text_to_modify for operation {operation!r}")
        if operation != "append_new" and isinstance(text_to_modify, str) and text_to_modify.strip() and current_prompt is not None:
            try:
                section_text = parse_prompt_sections(current_prompt).get(section, "")
            except ValueError:
                section_text = ""
            if text_to_modify.strip() not in section_text:
                errors.append(f"Revision plan item {idx} text_to_modify was not found in section {section!r}")
        if section in planned_sections:
            errors.append(f"Section {section!r} is planned more than once")
        planned_sections.add(section)
        if not isinstance(intent, str) or not intent.strip():
            errors.append(f"Revision plan item {idx} must provide non-empty string intent")
        if not isinstance(change_instruction, str) or not change_instruction.strip():
            errors.append(f"Revision plan item {idx} must provide non-empty string change_instruction")
        if require_boundaries:
            if not isinstance(positive_trigger, str) or not positive_trigger.strip():
                errors.append(f"Revision plan item {idx} must provide non-empty string positive_trigger")
            if not isinstance(negative_boundary, str) or not negative_boundary.strip():
                errors.append(f"Revision plan item {idx} must provide non-empty string negative_boundary")
        if require_scope:
            if not isinstance(revision_scope, dict):
                errors.append(f"Revision plan item {idx} must provide Python-owned revision_scope")
            else:
                required_scope_fields = {
                    "mechanism_id",
                    "mechanism_signature",
                    "supporting_attribution_ids",
                    "prompt_gap",
                    "section",
                    "repair_type",
                    "existing_prompt_quote",
                }
                missing_scope_fields = sorted(required_scope_fields - set(revision_scope))
                if missing_scope_fields:
                    errors.append(
                        f"Revision plan item {idx} revision_scope is missing: "
                        + ", ".join(missing_scope_fields)
                    )
                if str(revision_scope.get("section") or "").strip().lower() != section:
                    errors.append(f"Revision plan item {idx} revision_scope section does not match")
                if not isinstance(revision_scope.get("mechanism_signature"), dict):
                    errors.append(f"Revision plan item {idx} revision_scope mechanism_signature must be an object")
                if not isinstance(revision_scope.get("supporting_attribution_ids"), list):
                    errors.append(f"Revision plan item {idx} revision_scope attribution IDs must be a list")
    return not errors, errors


def normalize_error_localization_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    for field in ("prompt_gap", "existing_prompt_quote", "gap_rationale"):
        value = normalized.get(field)
        if isinstance(value, str):
            normalized[field] = value.strip()
    diagnoses = normalized.get("section_diagnoses")
    if isinstance(diagnoses, list):
        normalized["section_diagnoses"] = [
            {
                key: value.strip() if isinstance(value, str) else value
                for key, value in diagnosis.items()
            }
            if isinstance(diagnosis, dict)
            else diagnosis
            for diagnosis in diagnoses
        ]
    return normalized


def validate_error_localization_payload(
    payload: dict[str, Any],
    *,
    max_sections: int,
    current_prompt: str | None = None,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    expected_fields = {
        "prompt_gap",
        "existing_prompt_quote",
        "gap_rationale",
        "section_diagnoses",
    }
    unexpected_fields = sorted(set(payload) - expected_fields)
    if unexpected_fields:
        errors.append(f"Error localization contains unsupported fields: {', '.join(unexpected_fields)}")

    prompt_gap = payload.get("prompt_gap")
    existing_quote = payload.get("existing_prompt_quote")
    gap_rationale = payload.get("gap_rationale")
    if prompt_gap not in PROMPT_GAP_STATUSES:
        errors.append(f"prompt_gap must be one of {sorted(PROMPT_GAP_STATUSES)}")
    if not isinstance(existing_quote, str):
        errors.append("existing_prompt_quote must be a string")
        existing_quote = ""
    if not isinstance(gap_rationale, str) or not gap_rationale.strip():
        errors.append("gap_rationale must be a non-empty string")

    section_diagnoses = payload.get("section_diagnoses")
    if not isinstance(section_diagnoses, list):
        errors.append("Payload must contain a section_diagnoses list")
        return False, errors

    if prompt_gap == "already_covered":
        if section_diagnoses:
            errors.append("already_covered must use an empty section_diagnoses list")
        if not existing_quote:
            errors.append("already_covered must cite a non-empty existing_prompt_quote")
        elif current_prompt is not None and existing_quote not in current_prompt:
            errors.append("already_covered existing_prompt_quote was not found in the current prompt")
    elif prompt_gap == "ambiguous":
        if len(section_diagnoses) != 1:
            errors.append("ambiguous must contain exactly one section diagnosis")
        if not existing_quote:
            errors.append("ambiguous must cite a non-empty existing_prompt_quote")
    elif prompt_gap == "missing":
        if len(section_diagnoses) != 1:
            errors.append("missing must contain exactly one section diagnosis")
        if existing_quote:
            errors.append("missing must use an empty existing_prompt_quote")

    if max_sections > 0 and len(section_diagnoses) > max_sections:
        errors.append(f"At most {max_sections} sections may be diagnosed")

    for idx, diagnosis in enumerate(section_diagnoses, start=1):
        if not isinstance(diagnosis, dict):
            errors.append(f"Section diagnosis {idx} must be an object")
            continue
        diagnosis_fields = {"section", "repair_type", "section_problem", "risk_if_modified"}
        unexpected_diagnosis_fields = sorted(set(diagnosis) - diagnosis_fields)
        if unexpected_diagnosis_fields:
            errors.append(
                f"Section diagnosis {idx} contains unsupported fields: "
                f"{', '.join(unexpected_diagnosis_fields)}"
            )
        section = str(diagnosis.get("section") or "").strip().lower()
        if section not in SECTION_NAMES:
            errors.append(f"Section diagnosis {idx} has invalid section: {section!r}")
        repair_type = str(diagnosis.get("repair_type") or "").strip()
        if repair_type not in ERROR_LOCALIZATION_REPAIR_TYPES:
            errors.append(f"Section diagnosis {idx} has invalid repair_type: {repair_type!r}")
        for field in ("section_problem", "risk_if_modified"):
            if not isinstance(diagnosis.get(field), str) or not diagnosis[field].strip():
                errors.append(f"Section diagnosis {idx} must provide non-empty {field}")

    if (
        prompt_gap == "ambiguous"
        and len(section_diagnoses) == 1
        and isinstance(section_diagnoses[0], dict)
        and existing_quote
        and current_prompt is not None
    ):
        section = str(section_diagnoses[0].get("section") or "").strip().lower()
        try:
            section_text = parse_prompt_sections(current_prompt).get(section, "")
        except ValueError:
            section_text = ""
        if existing_quote not in section_text:
            errors.append("ambiguous existing_prompt_quote was not found in the diagnosed section")
    return not errors, errors


def validate_revision_against_prompt_gap(
    payload: dict[str, Any], error_localization: dict[str, Any]
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    prompt_gap = error_localization.get("prompt_gap")
    diagnoses = error_localization.get("section_diagnoses")
    plans = payload.get("revision_plan")
    if prompt_gap not in {"missing", "ambiguous"}:
        return False, ["Prompt editor may only run for missing or ambiguous prompt gaps"]
    if not isinstance(diagnoses, list) or len(diagnoses) != 1 or not isinstance(diagnoses[0], dict):
        return False, ["Actionable prompt gap must contain exactly one section diagnosis"]
    if not isinstance(plans, list) or len(plans) != 1 or not isinstance(plans[0], dict):
        return False, ["Prompt revision must contain exactly one plan item"]

    target_section = str(diagnoses[0].get("section") or "").strip().lower()
    plan = plans[0]
    plan_section = str(plan.get("section") or "").strip().lower()
    if plan_section != target_section:
        errors.append("Prompt revision section must match the localized prompt-gap section")
    if prompt_gap == "ambiguous":
        quote = str(error_localization.get("existing_prompt_quote") or "")
        operation = str(plan.get("operation") or "append_new").strip().lower()
        text_to_modify = str(plan.get("text_to_modify") or "")
        if operation == "append_new":
            errors.append("Ambiguous prompt gaps must revise existing text, not append a new rule")
        if quote and quote not in text_to_modify:
            errors.append("Ambiguous prompt revision text_to_modify must contain existing_prompt_quote")
    return not errors, errors


def validate_prompt_candidate(
    candidate: str,
    *,
    baseline_prompt: str | None = None,
    target_section: str | None = None,
) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if strip_code_fence(candidate).lstrip().startswith("@startuml"):
        errors.append("Optimizer returned PlantUML instead of a markdown prompt")
    try:
        parse_prompt_sections(candidate)
    except ValueError as exc:
        errors.append(str(exc))
    try:
        output_section = parse_prompt_sections(candidate).get("output", "")
    except ValueError:
        output_section = ""
    if "plantuml" not in output_section.lower():
        errors.append("Output section must require PlantUML code")
    if baseline_prompt is not None and target_section is not None:
        try:
            baseline_sections = parse_prompt_sections(baseline_prompt)
            candidate_sections = parse_prompt_sections(candidate)
        except ValueError:
            baseline_sections = {}
            candidate_sections = {}
        if target_section not in SECTION_NAMES:
            errors.append(f"Invalid target section for candidate diff: {target_section!r}")
        elif baseline_sections and candidate_sections:
            changed = [
                section
                for section in SECTION_NAMES
                if baseline_sections.get(section, "") != candidate_sections.get(section, "")
            ]
            if changed != [target_section]:
                errors.append(
                    "Candidate must change exactly the declared target section; "
                    f"declared={target_section!r}, changed={changed!r}"
                )
    return not errors, errors


def apply_prompt_revision_fragment(
    current_prompt: str,
    revision_plan: dict[str, Any],
    rule_text: str,
) -> tuple[str | None, list[str]]:
    plans = revision_plan.get("revision_plan")
    if not isinstance(plans, list) or len(plans) != 1 or not isinstance(plans[0], dict):
        return None, ["Fragment rewrite requires exactly one revision plan item"]
    plan = plans[0]
    section = str(plan.get("section") or "").strip().lower()
    operation = str(plan.get("operation") or "append_new").strip().lower()
    fragment = str(rule_text or "").strip()
    if section not in SECTION_NAMES:
        return None, [f"Invalid fragment target section: {section!r}"]
    if operation not in REVISION_OPERATIONS:
        return None, [f"Invalid fragment revision operation: {operation!r}"]
    if not fragment:
        return None, ["Prompt rewriter rule_text must be non-empty"]
    if re.search(r"(?im)^##\s+", fragment):
        return None, ["Prompt rewriter rule_text must not contain section headings"]
    for field in ("positive_trigger", "negative_boundary"):
        boundary = str(plan.get(field) or "").strip()
        if not boundary:
            return None, [f"Revision plan is missing {field}"]
        if boundary not in fragment:
            return None, [f"Prompt rewriter rule_text must contain canonical {field}"]

    try:
        sections = parse_prompt_sections(current_prompt)
    except ValueError as exc:
        return None, [str(exc)]
    current_section = sections[section]
    if operation == "append_new":
        sections[section] = f"{current_section.rstrip()}\n\n{fragment}".strip()
    else:
        text_to_modify = str(plan.get("text_to_modify") or "").strip()
        if not text_to_modify:
            return None, [f"Operation {operation!r} requires exact text_to_modify"]
        occurrences = current_section.count(text_to_modify)
        if occurrences != 1:
            return None, [
                "text_to_modify must occur exactly once as one contiguous target-section span; "
                f"found={occurrences}"
            ]
        sections[section] = current_section.replace(text_to_modify, fragment, 1)
    candidate = render_prompt_sections(sections)
    ok, errors = validate_prompt_candidate(
        candidate,
        baseline_prompt=current_prompt,
        target_section=section,
    )
    return (candidate if ok else None), errors


def apply_prompt_edit_payload(prompt: str, payload: dict[str, Any], *, max_sections: int | None) -> tuple[str | None, list[str]]:
    ok, errors = validate_prompt_edit_payload(payload, max_sections=max_sections)
    if not ok:
        return None, errors
    try:
        sections = parse_prompt_sections(prompt)
    except ValueError as exc:
        return None, [str(exc)]

    for edit in payload["edits"]:
        section = str(edit["section"]).strip().lower()
        operation = str(edit["operation"]).strip().lower()
        content = str(edit["content"]).strip()
        if operation == "replace":
            sections[section] = content
        elif operation == "append":
            existing = sections.get(section, "").strip()
            sections[section] = f"{existing}\n\n{content}".strip() if existing else content

    candidate = render_prompt_sections(sections)
    ok_candidate, candidate_errors = validate_prompt_candidate(candidate)
    if not ok_candidate:
        return None, candidate_errors
    return candidate, []
