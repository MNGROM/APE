"""Prompt rewrite agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from llm import LLMClient
from prompt_ops import extract_json_object, validate_prompt_candidate
from utils.io import read_prompt_file, write_text


def rewrite_prompt(
    *,
    current_prompt: str,
    revision_plan: dict[str, Any],
    candidate_constraints: dict[str, Any] | None = None,
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> str | None:
    payload = {
        "current_prompt": current_prompt,
        "revision_plan": revision_plan,
    }
    if candidate_constraints is not None:
        payload["candidate_constraints"] = candidate_constraints
    write_text(output_input_path, json.dumps(payload, ensure_ascii=False, indent=2))
    messages = [
        {
            "role": "system",
            "content": read_prompt_file(args.prompt_rewriter_prompt_path, label="prompt rewriter"),
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
        retry_phase="prompt_rewrite",
        retry_context={"iteration": iteration, "output_path": str(output_path)},
    )
    write_text(output_path, raw)
    parsed = extract_json_object(raw)
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "Prompt rewriter did not return a JSON object.\n")
        return None
    candidate = parsed.get("candidate_prompt")
    if not isinstance(candidate, str) or not candidate.strip():
        write_text(output_path.with_suffix(".rejected.txt"), "Prompt rewriter output must contain a non-empty candidate_prompt string.\n")
        return None
    ok, errors = validate_prompt_candidate(candidate)
    if not ok:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected prompt rewrite: {'; '.join(errors)}", flush=True)
        return None
    return candidate.strip() + "\n"
