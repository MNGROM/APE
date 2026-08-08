"""Prompt rewrite agent."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from llm import LLMClient
from prompt_ops import (
    apply_prompt_revision_fragment,
    extract_json_object,
    normalized_contract_contains,
    normalized_contract_occurrences,
    parse_prompt_sections,
)
from utils.io import read_prompt_file, write_text


RETROSPECTIVE_RULE_CUE = re.compile(
    r"\b(?:prediction|predicted|gold|ground\s+truth|evaluator|metric|f1|"
    r"validation|training\s+case|dataset|missing\s+node|extra\s+node)\b",
    re.IGNORECASE,
)
NON_TERMINAL_PERIOD = "\x00"
PROSE_ABBREVIATION_RE = re.compile(r"\b(?:e\.g|i\.e)\.", re.IGNORECASE)


def rule_sentence_count(rule_text: str) -> int:
    """Count prose sentences while ignoring non-terminal period sequences."""
    stripped = str(rule_text or "").strip()
    if not stripped:
        return 0
    protected = re.sub(
        r"\.{2,}",
        lambda match: NON_TERMINAL_PERIOD * len(match.group(0)),
        stripped,
    )
    protected = PROSE_ABBREVIATION_RE.sub(
        lambda match: match.group(0).replace(".", NON_TERMINAL_PERIOD),
        protected,
    )
    protected = re.sub(r"(?<=\d)\.(?=\d)", NON_TERMINAL_PERIOD, protected)
    parts = [
        part
        for part in re.split(r"[.!?]+(?:[\"')\]]+)?(?:\s+|$)", protected)
        if part.strip()
    ]
    return len(parts) or 1


def rewrite_prompt(
    *,
    current_prompt: str,
    revision_plan: dict[str, Any],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> str | None:
    revision_item = (revision_plan.get("revision_plan") or [{}])[0]
    section = str(revision_item.get("section") or "")
    sections = parse_prompt_sections(current_prompt)
    payload = {
        "target_section": section,
        "target_section_text": sections.get(section, ""),
        "operation": revision_item.get("operation"),
        "existing_prompt_quote": revision_item.get("text_to_modify", ""),
        "editor_plan": {
            "intent": revision_item.get("intent", ""),
            "change_instruction": revision_item.get("change_instruction", ""),
        },
        "positive_trigger": revision_item.get("positive_trigger", ""),
        "negative_boundary": revision_item.get("negative_boundary", ""),
    }
    write_text(output_input_path, json.dumps(payload, ensure_ascii=False, indent=2))
    system_prompt = read_prompt_file(
        args.prompt_rewriter_prompt_path, label="prompt rewriter"
    )
    positive_trigger = str(revision_item.get("positive_trigger") or "").strip()
    negative_boundary = str(revision_item.get("negative_boundary") or "").strip()
    previous_output: Any = None
    validation_errors: list[str] = []
    for attempt in range(1, 3):
        user_payload: dict[str, Any]
        if attempt == 1:
            user_payload = payload
        else:
            user_payload = {
                "schema_version": "prompt-rewriter-repair-v1",
                "original_rewriter_input": payload,
                "previous_output": previous_output,
                "validation_errors": validation_errors,
                "repair_instruction": (
                    "Return only a complete corrected {\"rule_text\": \"...\"} object. "
                    "Repair every reported violation, including sentence-count and canonical "
                    "preservation or occurrence violations. Copy all words of the supplied "
                    "positive trigger and negative boundary in their original order as one "
                    "contiguous span exactly once; only case, punctuation, and whitespace may "
                    "change. Do not paraphrase, reorder, inflect, delete, or insert words inside "
                    "either canonical span. Keep rule_text to at most two sentences."
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
            retry_phase="prompt_rewrite" if attempt == 1 else "prompt_rewrite_repair",
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
            validation_errors.append("Prompt rewriter did not return a JSON object")
            previous_output = raw
            continue
        previous_output = parsed
        unexpected = sorted(set(parsed) - {"rule_text"})
        if unexpected:
            validation_errors.append(
                "Prompt rewriter output may contain only rule_text: "
                + ", ".join(unexpected)
            )
        rule_text = parsed.get("rule_text")
        if not isinstance(rule_text, str) or not rule_text.strip():
            validation_errors.append(
                "Prompt rewriter output must contain a non-empty rule_text string"
            )
            rule_text = ""
        if RETROSPECTIVE_RULE_CUE.search(rule_text):
            validation_errors.append(
                "Prompt rewriter rule_text contains retrospective evaluator language"
            )
        if rule_sentence_count(rule_text) > 2:
            validation_errors.append(
                "rule_text must contain at most two sentences"
            )
        if positive_trigger and not normalized_contract_contains(
            rule_text, positive_trigger
        ):
            validation_errors.append(
                "rule_text must contain canonical positive_trigger once as one contiguous "
                "canonical token sequence; required fragment: "
                + json.dumps(positive_trigger, ensure_ascii=False)
            )
        if negative_boundary and not normalized_contract_contains(
            rule_text, negative_boundary
        ):
            validation_errors.append(
                "rule_text must contain canonical negative_boundary once as one contiguous "
                "canonical token sequence; required fragment: "
                + json.dumps(negative_boundary, ensure_ascii=False)
            )
        if positive_trigger and normalized_contract_occurrences(
            rule_text, positive_trigger
        ) > 1:
            validation_errors.append(
                "rule_text must contain canonical positive_trigger exactly once; required "
                "fragment: "
                + json.dumps(positive_trigger, ensure_ascii=False)
            )
        if negative_boundary and normalized_contract_occurrences(
            rule_text, negative_boundary
        ) > 1:
            validation_errors.append(
                "rule_text must contain canonical negative_boundary exactly once; required "
                "fragment: "
                + json.dumps(negative_boundary, ensure_ascii=False)
            )
        if validation_errors:
            continue
        candidate, errors = apply_prompt_revision_fragment(
            current_prompt,
            revision_plan,
            rule_text,
        )
        if candidate is None:
            validation_errors.extend(errors)
            continue
        write_text(
            output_path,
            json.dumps({"rule_text": rule_text}, ensure_ascii=False, indent=2),
        )
        return candidate.strip() + "\n"
    write_text(
        output_path.with_suffix(".rejected.txt"),
        "\n".join(validation_errors or ["Prompt rewriter output remained invalid"]) + "\n",
    )
    if validation_errors:
        print(f"[evolve] Rejected prompt rewrite: {'; '.join(validation_errors)}", flush=True)
    return None
