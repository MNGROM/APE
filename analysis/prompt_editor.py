"""Prompt edit agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from llm import LLMClient
from prompt_ops import extract_json_object, normalize_prompt_revision_plan, parse_prompt_sections, validate_prompt_revision_plan
from utils.io import read_prompt_file, write_text


def propose_prompt_revision(
    *,
    current_prompt: str,
    failure_analysis: dict[str, Any],
    error_localization: dict[str, Any],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    if args.no_evolve:
        return None

    payload = {
        "current_prompt_sections": parse_prompt_sections(current_prompt),
        "failure_analysis": failure_analysis,
        "error_localization": error_localization,
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
    parsed = normalize_prompt_revision_plan(parsed)
    write_text(output_path, json.dumps(parsed, ensure_ascii=False, indent=2))
    ok, errors = validate_prompt_revision_plan(parsed, max_sections=args.max_sections_per_edit)
    if not ok:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected prompt revision plan: {'; '.join(errors)}", flush=True)
        return None
    return parsed
