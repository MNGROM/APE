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


def validate_prompt_revision_plan(payload: dict[str, Any], *, max_sections: int | None) -> tuple[bool, list[str]]:
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
        if section not in SECTION_NAMES:
            errors.append(f"Revision plan item {idx} has invalid section: {section!r}")
        if operation not in REVISION_OPERATIONS:
            errors.append(f"Revision plan item {idx} has invalid operation: {operation!r}")
        if operation != "append_new" and (not isinstance(text_to_modify, str) or not text_to_modify.strip()):
            errors.append(f"Revision plan item {idx} must provide non-empty string text_to_modify for operation {operation!r}")
        if section in planned_sections:
            errors.append(f"Section {section!r} is planned more than once")
        planned_sections.add(section)
        if not isinstance(intent, str) or not intent.strip():
            errors.append(f"Revision plan item {idx} must provide non-empty string intent")
        if not isinstance(change_instruction, str) or not change_instruction.strip():
            errors.append(f"Revision plan item {idx} must provide non-empty string change_instruction")
    return not errors, errors


def validate_error_localization_payload(payload: dict[str, Any], *, max_sections: int) -> tuple[bool, list[str]]:
    errors: list[str] = []
    section_diagnoses = payload.get("section_diagnoses")
    if not isinstance(section_diagnoses, list) or not section_diagnoses:
        errors.append("Payload must contain a non-empty section_diagnoses list")
        return False, errors

    for idx, diagnosis in enumerate(section_diagnoses, start=1):
        if not isinstance(diagnosis, dict):
            errors.append(f"Section diagnosis {idx} must be an object")
            continue
        section = str(diagnosis.get("section") or "").strip().lower()
        if section not in SECTION_NAMES:
            errors.append(f"Section diagnosis {idx} has invalid section: {section!r}")
    return not errors, errors


def validate_prompt_candidate(candidate: str) -> tuple[bool, list[str]]:
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
    return not errors, errors


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
