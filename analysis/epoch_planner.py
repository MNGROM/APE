"""Epoch-level revision planner agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from analysis.mechanism_clustering import (
    bind_revision_to_mechanism,
    make_revision_scope,
    revision_scope_key,
)
from llm import LLMClient
from prompt_ops import extract_json_object, normalize_prompt_revision_plan, parse_prompt_sections, validate_prompt_revision_plan
from utils.io import read_prompt_file, write_text


def plan_epoch_revision(
    *,
    current_prompt: str,
    batch_revision_inputs: list[dict[str, Any]],
    selected_mechanism: dict[str, Any],
    edit_budget: dict[str, Any],
    args: Any,
    llm_client: LLMClient,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    expected_sections: set[str] = set()
    supplied_scopes: list[dict[str, Any]] = []
    plan_count = 0
    for item in batch_revision_inputs:
        plans = item.get("revision_plan") if isinstance(item, dict) else None
        if isinstance(plans, list) and len(plans) == 1 and isinstance(plans[0], dict):
            plan_count += 1
            expected_sections.add(str(plans[0].get("section") or "").strip().lower())
            scope = plans[0].get("revision_scope")
            if isinstance(scope, dict):
                supplied_scopes.append(scope)
    if len(expected_sections) != 1:
        write_text(
            output_path.with_suffix(".rejected.txt"),
            "Epoch planner requires majority batch plans for exactly one target section.\n",
        )
        return None
    expected_section = next(iter(expected_sections))
    if supplied_scopes and len(supplied_scopes) != plan_count:
        write_text(
            output_path.with_suffix(".rejected.txt"),
            "Epoch planner cannot mix scoped and legacy local revision plans.\n",
        )
        return None
    if supplied_scopes and len({revision_scope_key(scope) for scope in supplied_scopes}) != 1:
        write_text(
            output_path.with_suffix(".rejected.txt"),
            "Epoch planner requires one identical atomic revision scope.\n",
        )
        return None
    if supplied_scopes:
        expected_scope = dict(supplied_scopes[0])
        expected_scope["supporting_attribution_ids"] = sorted(
            {
                str(attribution_id)
                for scope in supplied_scopes
                for attribution_id in scope.get("supporting_attribution_ids", [])
                if str(attribution_id)
            }
        )
        selected_attribution_ids = sorted(
            set(selected_mechanism.get("supporting_attribution_ids", []))
        )
        if selected_attribution_ids and (
            expected_scope["supporting_attribution_ids"] != selected_attribution_ids
        ):
            write_text(
                output_path.with_suffix(".rejected.txt"),
                "Epoch planner scope must cover exactly Python-selected attributions.\n",
            )
            return None
    else:
        expected_scope = make_revision_scope(
            selected_mechanism=selected_mechanism,
            prompt_gap="",
            section=expected_section,
            repair_type="",
            existing_prompt_quote="",
        )
    payload = {
        "current_prompt_sections": parse_prompt_sections(current_prompt),
        "batch_revision_inputs": batch_revision_inputs,
        "selected_mechanism": {
            key: value
            for key, value in selected_mechanism.items()
            if key != "supporting_batch_observations"
        },
        "revision_scope": expected_scope,
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
    if not isinstance(parsed.get("revision_plan"), list) or len(parsed["revision_plan"]) != 1:
        write_text(output_path.with_suffix(".rejected.txt"), "Epoch planner must return exactly one revision_plan item.\n")
        return None
    parsed = normalize_prompt_revision_plan(parsed)
    parsed, mechanism_errors = bind_revision_to_mechanism(
        parsed,
        selected_mechanism=selected_mechanism,
        revision_scope=expected_scope,
    )
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(mechanism_errors) + "\n")
        print(f"[evolve] Rejected epoch mechanism selection: {'; '.join(mechanism_errors)}", flush=True)
        return None
    actual_section = str(parsed["revision_plan"][0].get("section") or "").strip().lower()
    if actual_section != expected_section:
        message = (
            "Epoch planner revision section must match the strict-majority section: "
            f"expected={expected_section!r}, actual={actual_section!r}\n"
        )
        write_text(output_path.with_suffix(".rejected.txt"), message)
        return None
    write_text(output_path, json.dumps(parsed, ensure_ascii=False, indent=2))
    ok, errors = validate_prompt_revision_plan(
        parsed,
        max_sections=1,
        current_prompt=current_prompt,
        require_boundaries=True,
        require_scope=True,
    )
    if not ok:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected epoch revision plan: {'; '.join(errors)}", flush=True)
        return None
    return parsed
