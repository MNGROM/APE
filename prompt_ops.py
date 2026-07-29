"""Prompt parsing, candidate validation, and exact fragment application."""

from __future__ import annotations

import json
import re
from typing import Any

from config import REQUIRED_PROMPT_HEADINGS, SECTION_NAMES
from prediction import strip_code_fence


REVISION_OPERATIONS = {"append_new", "replace_existing"}
LINE_ITEM_PREFIX_RE = re.compile(r"^(?P<prefix>[ \t]*(?:\d+[.)]|[-+*])[ \t]+)")


def normalize_rule_contract_text(text: str) -> str:
    """Normalize contract text for case, punctuation, and whitespace comparisons."""
    tokens = re.findall(r"\w+", str(text or "").casefold(), flags=re.UNICODE)
    return " ".join(tokens)


def normalized_contract_contains(text: str, fragment: str) -> bool:
    haystack = normalize_rule_contract_text(text).split()
    needle = normalize_rule_contract_text(fragment).split()
    if not needle or len(needle) > len(haystack):
        return False
    width = len(needle)
    return any(
        haystack[index : index + width] == needle
        for index in range(len(haystack) - width + 1)
    )


def normalized_contract_occurrences(text: str, fragment: str) -> int:
    haystack = normalize_rule_contract_text(text).split()
    needle = normalize_rule_contract_text(fragment).split()
    if not needle or len(needle) > len(haystack):
        return 0
    width = len(needle)
    return sum(
        haystack[index : index + width] == needle
        for index in range(len(haystack) - width + 1)
    )


def strip_markdown_fence(text: str) -> str:
    match = re.search(
        r"```(?:markdown|md)?\s*(.*?)```",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    return match.group(1).strip() if match else text.strip()


def normalize_prompt_headings(candidate: str) -> str:
    normalized = candidate.strip()
    for heading in REQUIRED_PROMPT_HEADINGS:
        heading_name = heading.replace("## ", "")
        normalized = re.sub(
            rf"(?im)^#{{1,6}}\s*{re.escape(heading_name)}\s*$",
            f"## {heading_name}",
            normalized,
        )
    return normalized


def parse_prompt_sections(prompt: str) -> dict[str, str]:
    normalized = normalize_prompt_headings(prompt)
    matches = list(re.finditer(r"(?im)^##\s+(.+?)\s*$", normalized))
    sections: dict[str, str] = {}
    seen: list[str] = []
    for index, match in enumerate(matches):
        name = match.group(1).strip().lower()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
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


def _prompt_section_content_spans(prompt: str) -> dict[str, tuple[int, int]]:
    matches = list(re.finditer(r"(?im)^#{1,6}[ \t]+(.+?)[ \t]*$", prompt))
    spans: dict[str, tuple[int, int]] = {}
    seen: list[str] = []
    for index, match in enumerate(matches):
        name = match.group(1).strip().lower()
        if name not in SECTION_NAMES:
            continue
        if name in spans:
            raise ValueError(f"Duplicate section heading: {name}")
        end = matches[index + 1].start() if index + 1 < len(matches) else len(prompt)
        spans[name] = (match.end(), end)
        seen.append(name)
    missing = [name for name in SECTION_NAMES if name not in spans]
    if missing:
        raise ValueError(f"Missing required prompt sections: {', '.join(missing)}")
    if seen != list(SECTION_NAMES):
        raise ValueError("Prompt sections must keep the required order")
    return spans


def _replace_prompt_section_content(prompt: str, *, section: str, content: str) -> str:
    spans = _prompt_section_content_spans(prompt)
    start, end = spans[section]
    newline = "\r\n" if "\r\n" in prompt else "\n"
    trailing = newline if end == len(prompt) else newline * 2
    replacement = f"{newline}{newline}{content.strip()}{trailing}"
    return f"{prompt[:start]}{replacement}{prompt[end:]}"


def _preserve_line_item_prefix(target: str, replacement: str) -> str:
    target_match = LINE_ITEM_PREFIX_RE.match(target)
    if not target_match:
        return replacement
    prefix = target_match.group("prefix")
    body = re.sub(
        r"^[ \t]*(?:\d+[.)]|[-+*])[ \t]+",
        "",
        replacement,
        count=1,
    )
    return prefix + body.lstrip()


def extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = strip_markdown_fence(text)
    try:
        payload = json.loads(stripped)
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        payload = json.loads(stripped[start : end + 1])
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


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
        candidate_sections = parse_prompt_sections(candidate)
    except ValueError as exc:
        errors.append(str(exc))
        candidate_sections = {}
    output_section = candidate_sections.get("output", "")
    if "plantuml" not in output_section.lower():
        errors.append("Output section must require PlantUML code")
    if baseline_prompt is not None and target_section is not None:
        try:
            baseline_sections = parse_prompt_sections(baseline_prompt)
        except ValueError:
            baseline_sections = {}
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
            try:
                baseline_start, baseline_end = _prompt_section_content_spans(baseline_prompt)[
                    target_section
                ]
                candidate_start, candidate_end = _prompt_section_content_spans(candidate)[
                    target_section
                ]
            except (KeyError, ValueError):
                baseline_start = baseline_end = candidate_start = candidate_end = None
            if None not in (baseline_start, baseline_end, candidate_start, candidate_end):
                if (
                    baseline_prompt[:baseline_start] != candidate[:candidate_start]
                    or baseline_prompt[baseline_end:] != candidate[candidate_end:]
                ):
                    errors.append(
                        "Candidate must preserve all bytes outside the declared target section"
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
    operation = str(plan.get("operation") or "").strip().lower()
    fragment = str(rule_text or "").strip()
    if section not in SECTION_NAMES:
        return None, [f"Invalid fragment target section: {section!r}"]
    if operation not in REVISION_OPERATIONS:
        return None, [f"Invalid fragment revision operation: {operation!r}"]
    if not fragment:
        return None, ["Prompt rewriter rule_text must be non-empty"]
    if re.search(r"(?im)^##\s+", fragment):
        return None, ["Prompt rewriter rule_text must not contain section headings"]
    try:
        sections = parse_prompt_sections(current_prompt)
    except ValueError as exc:
        return None, [str(exc)]
    current_section = sections[section]
    if operation == "append_new":
        if str(plan.get("text_to_modify") or "").strip():
            return None, ["append_new requires an empty existing_prompt_quote"]
        replacement = fragment
        sections[section] = f"{current_section.rstrip()}\n\n{replacement}".strip()
    else:
        text_to_modify = str(plan.get("text_to_modify") or "").strip()
        if not text_to_modify:
            return None, ["replace_existing requires exact text_to_modify"]
        occurrences = current_section.count(text_to_modify)
        if occurrences != 1:
            return None, [
                "text_to_modify must occur exactly once as one contiguous target-section span; "
                f"found={occurrences}"
            ]
        replacement = _preserve_line_item_prefix(text_to_modify, fragment)
        sections[section] = current_section.replace(text_to_modify, replacement, 1)

    for field in ("positive_trigger", "negative_boundary"):
        boundary = str(plan.get(field) or "").strip()
        if not boundary:
            return None, [f"Revision plan is missing {field}"]
        if not normalized_contract_contains(fragment, boundary):
            return None, [f"Prompt rewriter rule_text must contain canonical {field}"]

    candidate = _replace_prompt_section_content(
        current_prompt,
        section=section,
        content=sections[section],
    )
    ok, errors = validate_prompt_candidate(
        candidate,
        baseline_prompt=current_prompt,
        target_section=section,
    )
    return (candidate if ok else None), errors
