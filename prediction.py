"""PlantUML generation helpers."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ape_datasets.lato import Case
from llm import LLMClient


def strip_code_fence(text: str) -> str:
    match = re.search(r"```(?:plantuml|puml|uml)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def extract_plantuml(text: str, *, wrap_if_needed: bool = True) -> str:
    raw = strip_code_fence(text)
    start = raw.find("@startuml")
    end = raw.find("@enduml", start + len("@startuml")) if start != -1 else -1
    if start != -1 and end != -1:
        return raw[start : end + len("@enduml")].strip()
    if not wrap_if_needed:
        return raw
    if "@startuml" not in raw and "@enduml" not in raw:
        return "@startuml\n" + raw.strip() + "\n@enduml"
    return raw


def generate_plantuml_for_case(
    *,
    prompt: str,
    case: Case,
    llm_client: LLMClient,
    mock_with_gold: bool,
    thinking: str | None,
    state_dir: Path | None,
    retry_phase: str,
) -> str:
    if mock_with_gold:
        return extract_plantuml(case.gold_plantuml, wrap_if_needed=True)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Input:\n{case.content}\n\nOutput:"},
    ]
    return llm_client.chat(
        messages,
        thinking=thinking,
        state_dir=state_dir,
        retry_phase=retry_phase,
        retry_context={"dataset": case.dataset, "case_id": case.case_id},
    )


def generated_from_args(
    *,
    prompt: str,
    case: Case,
    args: Any,
    llm_client: LLMClient,
    state_dir: Path | None,
    retry_phase: str,
) -> str:
    prediction_client = llm_client.for_model(
        getattr(args, "generation_model", llm_client.model),
    )
    return generate_plantuml_for_case(
        prompt=prompt,
        case=case,
        llm_client=prediction_client,
        mock_with_gold=args.mock_with_gold,
        thinking=args.generation_thinking,
        state_dir=state_dir,
        retry_phase=retry_phase,
    )
