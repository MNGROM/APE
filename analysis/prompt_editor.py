"""Prompt edit agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from analysis.mechanism_clustering import bind_revision_to_mechanism, make_revision_scope
from llm import LLMClient
from prompt_ops import (
    extract_json_object,
    normalize_prompt_revision_plan,
    parse_prompt_sections,
    validate_prompt_revision_plan,
    validate_revision_against_prompt_gap,
)
from utils.io import read_prompt_file, write_text


def propose_prompt_revision(
    *,
    current_prompt: str,
    failure_analysis: dict[str, Any],
    error_localization: dict[str, Any],
    selected_mechanism: dict[str, Any],
    edit_budget: dict[str, Any],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    if args.no_evolve:
        return None

    diagnoses = error_localization.get("section_diagnoses", [])
    diagnosis = diagnoses[0] if len(diagnoses) == 1 and isinstance(diagnoses[0], dict) else {}
    revision_scope = make_revision_scope(
        selected_mechanism=selected_mechanism,
        prompt_gap=str(error_localization.get("prompt_gap") or ""),
        section=str(diagnosis.get("section") or ""),
        repair_type=str(diagnosis.get("repair_type") or ""),
        existing_prompt_quote=str(error_localization.get("existing_prompt_quote") or ""),
    )
    payload = {
        "current_prompt_sections": parse_prompt_sections(current_prompt),
        "failure_analysis": failure_analysis,
        "error_localization": error_localization,
        "selected_mechanism": {
            "mechanism_id": selected_mechanism["mechanism_id"],
            "hypothesis_id": selected_mechanism.get("hypothesis_id"),
            "parent_key": selected_mechanism.get("parent_key", []),
            "child_key": selected_mechanism.get("child_key", []),
            "mechanism_signature": selected_mechanism["mechanism_signature"],
            "current_supporting_attribution_ids": selected_mechanism.get(
                "current_supporting_attribution_ids", []
            ),
            "historical_supporting_attribution_ids": selected_mechanism.get(
                "historical_supporting_attribution_ids", []
            ),
            "supporting_attribution_ids": selected_mechanism.get(
                "supporting_attribution_ids", []
            ),
            "supporting_evidence_ids": selected_mechanism["supporting_evidence_ids"],
            "positive_trigger": selected_mechanism["positive_trigger"],
            "negative_boundary": selected_mechanism["negative_boundary"],
            "matching_quality": selected_mechanism.get("matching_quality", ""),
            "conflict_status": selected_mechanism.get("conflict_status", "clear"),
        },
        "revision_scope": revision_scope,
        "edit_budget": edit_budget,
    }
    write_text(output_input_path, json.dumps(payload, ensure_ascii=False, indent=2))
    messages = [
        {
            "role": "system",
            "content": read_prompt_file(args.prompt_editor_prompt_path, label="prompt editor"),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, indent=2),
        },
    ]
    raw = llm_client.chat(
        messages,
        temperature=args.editor_temperature,
        max_tokens=args.editor_max_tokens,
        thinking=args.editor_thinking,
        state_dir=state_dir,
        retry_phase="prompt_edit",
        retry_context={"iteration": iteration, "output_path": str(output_path)},
    )
    write_text(output_path, raw)
    parsed = extract_json_object(raw)
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "Prompt editor did not return a JSON object.\n")
        return None
    if not isinstance(parsed.get("revision_plan"), list) or len(parsed["revision_plan"]) != 1:
        write_text(output_path.with_suffix(".rejected.txt"), "Prompt editor must return exactly one revision_plan item.\n")
        return None
    parsed = normalize_prompt_revision_plan(parsed)
    parsed, mechanism_errors = bind_revision_to_mechanism(
        parsed,
        selected_mechanism=selected_mechanism,
        supporting_evidence_ids=selected_mechanism["supporting_evidence_ids"],
        revision_scope=revision_scope,
    )
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(mechanism_errors) + "\n")
        print(f"[evolve] Rejected prompt mechanism selection: {'; '.join(mechanism_errors)}", flush=True)
        return None
    write_text(output_path, json.dumps(parsed, ensure_ascii=False, indent=2))
    ok, errors = validate_prompt_revision_plan(
        parsed,
        max_sections=1,
        current_prompt=current_prompt,
        require_boundaries=True,
        require_scope=True,
    )
    gap_ok, gap_errors = validate_revision_against_prompt_gap(parsed, error_localization)
    errors.extend(gap_errors)
    ok = ok and gap_ok
    if not ok:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected prompt revision plan: {'; '.join(errors)}", flush=True)
        return None
    return parsed
