"""Error localization agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from llm import LLMClient
from prompt_ops import (
    extract_json_object,
    normalize_error_localization_payload,
    parse_prompt_sections,
    validate_error_localization_payload,
)
from utils.io import read_prompt_file, write_text


def localize_errors(
    *,
    current_prompt: str,
    failure_analysis: dict[str, Any],
    selected_mechanism: dict[str, Any],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    payload = {
        "current_prompt_sections": parse_prompt_sections(current_prompt),
        "failure_analysis": failure_analysis,
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
    }
    write_text(output_input_path, json.dumps(payload, ensure_ascii=False, indent=2))
    messages = [
        {
            "role": "system",
            "content": read_prompt_file(args.error_localization_prompt_path, label="error localization"),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, indent=2),
        },
    ]
    raw = llm_client.chat(
        messages,
        temperature=args.localization_temperature,
        max_tokens=args.localization_max_tokens,
        thinking=args.localization_thinking,
        state_dir=state_dir,
        retry_phase="error_localization",
        retry_context={"iteration": iteration, "output_path": str(output_path)},
    )
    write_text(output_path, raw)
    parsed = extract_json_object(raw)
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "Error localization did not return a JSON object.\n")
        return None
    parsed = normalize_error_localization_payload(parsed)
    ok, errors = validate_error_localization_payload(
        parsed,
        max_sections=args.max_sections_per_edit,
        current_prompt=current_prompt,
    )
    if not ok:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected error localization: {'; '.join(errors)}", flush=True)
        return None
    write_text(output_path, json.dumps(parsed, ensure_ascii=False, indent=2))
    return parsed
