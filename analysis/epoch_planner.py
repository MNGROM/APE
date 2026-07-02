"""Epoch-level revision planner agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from llm import LLMClient
from prompt_ops import extract_json_object, normalize_prompt_revision_plan, parse_prompt_sections, validate_prompt_revision_plan
from utils.io import read_prompt_file, write_text


def plan_epoch_revision(
    *,
    current_prompt: str,
    batch_revision_inputs: list[dict[str, Any]],
    edit_budget: dict[str, Any],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    payload = {
        "current_prompt_sections": parse_prompt_sections(current_prompt),
        "batch_revision_inputs": batch_revision_inputs,
        "edit_budget": edit_budget,
    }
    write_text(output_input_path, json.dumps(payload, ensure_ascii=False, indent=2))
    messages = [
        {
            "role": "system",
            "content": read_prompt_file(args.epoch_planner_prompt_path, label="epoch planner"),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, indent=2),
        },
    ]
    raw = llm_client.chat(
        messages,
        temperature=args.epoch_planner_temperature,
        max_tokens=args.epoch_planner_max_tokens,
        thinking=args.epoch_planner_thinking,
        state_dir=state_dir,
        retry_phase="epoch_planner",
        retry_context={"iteration": iteration, "output_path": str(output_path)},
    )
    write_text(output_path, raw)
    parsed = extract_json_object(raw)
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "Epoch planner did not return a JSON object.\n")
        return None
    parsed = normalize_prompt_revision_plan(parsed)
    write_text(output_path, json.dumps(parsed, ensure_ascii=False, indent=2))
    ok, errors = validate_prompt_revision_plan(parsed, max_sections=edit_budget.get("max_revision_items"))
    if not ok:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected epoch revision plan: {'; '.join(errors)}", flush=True)
        return None
    return parsed
