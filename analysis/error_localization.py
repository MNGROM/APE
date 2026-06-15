"""Error localization agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import SECTION_NAMES
from llm import LLMClient
from prompt_ops import extract_json_object, parse_prompt_sections, validate_error_localization_payload
from utils.io import read_prompt_file, write_text


def localize_errors(
    *,
    current_prompt: str,
    failure_analysis: dict[str, Any],
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
    ok, errors = validate_error_localization_payload(parsed, max_sections=args.max_sections_per_edit)
    if not ok:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected error localization: {'; '.join(errors)}", flush=True)
        return None
    return parsed
