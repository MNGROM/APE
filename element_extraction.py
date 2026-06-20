"""Element extraction backends for PlantUML activity diagrams."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from llm import LLMClient
from llm_element_metrics import parse_json_response, strip_markdown_fences
from metrics import ActivityGraph, _dedupe_preserving_order, _format_relation, extract_activity_graph, normalize_label
from prediction import extract_plantuml


EXTRACTION_SCHEMA_VERSION = "activity-graph-v1"

EXTRACTION_SYSTEM_PROMPT = (
    "You extract activity-graph elements from PlantUML activity diagram code. "
    "Return only valid JSON. Do not explain your answer."
)

EXTRACTION_USER_PROMPT = """Extract only the elements explicitly present in this PlantUML activity diagram.

Rules:
- Ignore @startuml, @enduml, start, stop, end, notes, titles, styles, and comments.
- Treat each PlantUML activity statement `:...;` as one activity node.
- Treat decision conditions from `if`, `elseif`, `switch`, `case`, `while`, and `repeat while` as nodes when they control flow.
- Extract control-flow relations between nodes, including sequential, conditional, loop, fork, and merge/join relations.
- Do not merge distinct nodes just because their text is semantically similar.
- Do not invent activities or relations that are not represented in the PlantUML code.

Output JSON in this exact shape:
{{
  "nodes": [
    {{"id": "n1", "label": "activity or condition label"}}
  ],
  "relations": [
    {{"from": "n1", "to": "n2", "type": "sequential", "condition": null}}
  ]
}}

Allowed relation type values: sequential, conditional, loop, fork, merge.
Use node ids in relation endpoints when possible. Use concise condition labels such as "yes", "no", "case x", "loop", or "fork" when applicable.

PlantUML:
{code}
"""

_CACHE_BY_PATH: dict[Path, dict[str, dict[str, Any]]] = {}


def _cache_path(state_dir: Path | None) -> Path | None:
    if state_dir is None:
        return None
    return state_dir / "element_extraction_cache.jsonl"


def _load_cache(path: Path) -> dict[str, dict[str, Any]]:
    cached = _CACHE_BY_PATH.get(path)
    if cached is not None:
        return cached
    values: dict[str, dict[str, Any]] = {}
    if path.exists():
        with path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                key = payload.get("key")
                graph = payload.get("graph")
                if isinstance(key, str) and isinstance(graph, dict):
                    values[key] = graph
    _CACHE_BY_PATH[path] = values
    return values


def _write_cache(path: Path, key: str, graph: ActivityGraph) -> None:
    cache = _load_cache(path)
    payload = {"nodes": graph.nodes, "relations": graph.relations}
    cache[key] = payload
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"key": key, "graph": payload}, ensure_ascii=False) + "\n")


def _cache_key(
    *,
    code: str,
    model: str,
    thinking: str,
    temperature: float,
    max_tokens: int,
) -> str:
    payload = {
        "schema": EXTRACTION_SCHEMA_VERSION,
        "code": code,
        "model": model,
        "thinking": thinking,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _node_label(node: Any) -> tuple[str | None, str | None]:
    if isinstance(node, str):
        label = normalize_label(node)
        return None, label or None
    if not isinstance(node, dict):
        return None, None
    raw_id = node.get("id") or node.get("name")
    raw_label = node.get("label") or node.get("text") or node.get("name") or raw_id
    label = normalize_label(str(raw_label or ""))
    node_id = str(raw_id).strip() if raw_id is not None else None
    return node_id or None, label or None


def _relation_kind(relation: dict[str, Any]) -> str | None:
    relation_type = normalize_label(str(relation.get("type") or relation.get("kind") or ""))
    condition_value = relation.get("condition")
    condition = normalize_label(str(condition_value)) if condition_value is not None else ""
    if condition and condition not in {"none", "null"}:
        return condition
    if relation_type and relation_type != "sequential":
        return relation_type
    return None


def _normalize_llm_result(result: Any) -> ActivityGraph:
    if not isinstance(result, dict):
        raise ValueError("LLM extraction did not return a JSON object")
    raw_nodes = result.get("nodes")
    raw_relations = result.get("relations")
    if not isinstance(raw_nodes, list) or not isinstance(raw_relations, list):
        raise ValueError("LLM extraction JSON must contain list fields 'nodes' and 'relations'")

    nodes: list[str] = []
    node_id_to_label: dict[str, str] = {}
    for item in raw_nodes:
        node_id, label = _node_label(item)
        if not label:
            continue
        nodes.append(label)
        if node_id:
            node_id_to_label[node_id] = label

    def endpoint(value: Any) -> str | None:
        if value is None:
            return None
        raw = str(value).strip()
        if raw in node_id_to_label:
            return node_id_to_label[raw]
        label = normalize_label(raw)
        return label or None

    relations: list[str] = []
    for item in raw_relations:
        if not isinstance(item, dict):
            continue
        source = endpoint(item.get("from") or item.get("source"))
        target = endpoint(item.get("to") or item.get("target"))
        if not source or not target or source == target:
            continue
        if source not in nodes:
            nodes.append(source)
        if target not in nodes:
            nodes.append(target)
        relations.append(_format_relation(source, target, _relation_kind(item)))

    return ActivityGraph(
        nodes=_dedupe_preserving_order(nodes),
        relations=_dedupe_preserving_order(relations),
    )


def extract_activity_graph_with_llm(
    uml_code: str,
    *,
    llm_client: LLMClient,
    state_dir: Path | None,
    retry_phase: str,
    retry_context: dict[str, Any],
    thinking: str,
    temperature: float,
    max_tokens: int,
    max_retries: int,
) -> ActivityGraph:
    code = extract_plantuml(uml_code, wrap_if_needed=True)
    key = _cache_key(
        code=code,
        model=llm_client.model,
        thinking=thinking,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    cache_path = _cache_path(state_dir)
    if cache_path is not None:
        cached = _load_cache(cache_path).get(key)
        if cached is not None:
            return ActivityGraph(
                nodes=list(cached.get("nodes") or []),
                relations=list(cached.get("relations") or []),
            )

    messages = [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": EXTRACTION_USER_PROMPT.format(code=strip_markdown_fences(code))},
    ]
    last_error: Exception | None = None
    for attempt in range(1, max(1, max_retries) + 1):
        raw = llm_client.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            thinking=thinking,
            state_dir=state_dir,
            retry_phase=retry_phase,
            retry_context={**retry_context, "json_retry_attempt": attempt},
        )
        result = parse_json_response(raw)
        try:
            graph = _normalize_llm_result(result)
        except ValueError as exc:
            last_error = exc
            continue
        if cache_path is not None:
            _write_cache(cache_path, key, graph)
        return graph
    raise ValueError(f"LLM element extraction did not return valid schema: {last_error}")


def extract_graph_for_metrics(
    uml_code: str,
    *,
    args: Any,
    llm_client: LLMClient,
    state_dir: Path | None,
    phase: str,
    role: str,
    retry_context: dict[str, Any],
) -> ActivityGraph:
    extractor = getattr(args, "element_extractor", "rule")
    if extractor == "rule":
        return extract_activity_graph(uml_code)

    try:
        return extract_activity_graph_with_llm(
            uml_code,
            llm_client=llm_client,
            state_dir=state_dir,
            retry_phase=f"{phase}:element_extraction:{role}",
            retry_context={**retry_context, "extract_role": role},
            thinking=getattr(args, "element_extraction_thinking", "disabled"),
            temperature=getattr(args, "element_extraction_temperature", 0.0),
            max_tokens=getattr(args, "element_extraction_max_tokens", 4096),
            max_retries=getattr(args, "element_extraction_max_retries", 3),
        )
    except Exception:
        if extractor == "auto":
            return extract_activity_graph(uml_code)
        raise
