"""Prompt rewrite agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from llm import LLMClient
from prompt_ops import apply_prompt_revision_fragment, extract_json_object
from utils.io import read_prompt_file, write_text


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
    payload = {
        "current_prompt": current_prompt,
        "revision_plan": revision_plan,
    }
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
    unexpected = sorted(set(parsed) - {"rule_text"})
    if unexpected:
        message = "Prompt rewriter output may contain only rule_text: " + ", ".join(unexpected)
        write_text(output_path.with_suffix(".rejected.txt"), message + "\n")
        return None
    rule_text = parsed.get("rule_text")
    if not isinstance(rule_text, str) or not rule_text.strip():
        write_text(output_path.with_suffix(".rejected.txt"), "Prompt rewriter output must contain a non-empty rule_text string.\n")
        return None
    candidate, errors = apply_prompt_revision_fragment(
        current_prompt,
        revision_plan,
        rule_text,
    )
    if candidate is None:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected prompt rewrite: {'; '.join(errors)}", flush=True)
        return None
    write_text(output_path, json.dumps({"rule_text": rule_text.strip()}, ensure_ascii=False, indent=2))
    return candidate.strip() + "\n"
