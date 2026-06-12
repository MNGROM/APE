"""AHE-compatible evaluator for UML prompt optimization.

This module keeps the AHE outer loop intact while replacing Harbor evaluation
with a prompt-evaluation backend. The editable workspace contains a single
prompt file, and each task is one LATO requirement-to-PlantUML case.
"""

from __future__ import annotations

import dataclasses
import difflib
import json
import os
import random
import re
import subprocess
import time
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from evaluators.llm_element_metrics import (
    CompilationResult,
    LLMElementMetrics,
    check_plantuml_compilation,
    evaluate_llm_elements,
)
from utils.rate_limit import ProviderHTTPError, call_with_provider_retries


PROJECT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
DEFAULT_MODEL = "glm-5.1"
DEFAULT_PLANTUML_JAR = PROJECT_DIR / "tools" / "plantuml" / "plantuml-1.2025.4.jar"


class LLMHTTPError(ProviderHTTPError):
    def __init__(self, status_code: int, body: str, headers: dict[str, str] | None = None) -> None:
        super().__init__("LLM", status_code, body, headers)


@dataclass
class Case:
    dataset: str
    case_id: str
    content: str
    gold_plantuml: str


@dataclass
class SyntaxResult:
    passed: bool
    errors: list[str]


@dataclass
class StructureResult:
    passed: bool
    errors: list[str]
    start_count: int
    terminal_count: int
    node_count: int
    reachable_count: int
    dangling_edges: list[str]


@dataclass
class GraphNode:
    node_id: str
    label: str
    kind: str
    line_no: int


@dataclass
class ActivityGraph:
    nodes: dict[str, GraphNode]
    order: list[str]
    edges: list[tuple[str, str]]
    errors: list[str]
    dangling_edges: list[str]
    start_ids: list[str]
    terminal_ids: list[str]


@dataclass
class MetricBundle:
    precision: float
    recall: float
    f1: float
    missing: list[str]
    extra: list[str]


@dataclass
class EvaluationRecord:
    dataset: str
    case_id: str
    input_requirement: str
    gold_plantuml: str
    generated_plantuml: str
    syntax: SyntaxResult
    structure: StructureResult
    node_metrics: MetricBundle
    relation_metrics: MetricBundle
    plantuml_compilation: CompilationResult
    llm_element_metrics: LLMElementMetrics
    quality_score: float
    reward: float
    failure_types: list[str]


def load_cases(datasets_dir: Path) -> dict[str, list[Case]]:
    datasets: dict[str, list[Case]] = {}
    for path in sorted(datasets_dir.glob("*.jsonl")):
        name = path.stem.lower()
        cases: list[Case] = []
        with path.open(encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                if not line.strip():
                    continue
                payload = json.loads(line)
                content = str(payload.get("content") or "").strip()
                plantuml = str(payload.get("plantuml") or "").strip()
                if content and plantuml:
                    cases.append(Case(name, f"{name}-{idx:04d}", content, plantuml))
        datasets[name] = cases
    if not datasets:
        raise FileNotFoundError(f"No .jsonl datasets found under {datasets_dir}")
    return datasets


def grouped_cases(cases: list[Case]) -> dict[str, list[Case]]:
    groups: dict[str, list[Case]] = {}
    for case in cases:
        groups.setdefault(case.dataset, []).append(case)
    return groups


def select_cases_with_strategy(cases: list[Case], *, max_cases: int, strategy: str, seed: int) -> list[Case]:
    if max_cases <= 0 or max_cases >= len(cases):
        return list(cases)
    strategy = strategy.lower()
    if strategy == "prefix":
        return cases[:max_cases]
    rng = random.Random(seed)
    if strategy == "random":
        selected = list(cases)
        rng.shuffle(selected)
        return selected[:max_cases]
    if strategy != "stratified":
        raise ValueError(f"Unknown prompt_uml sample strategy {strategy!r}")

    groups = grouped_cases(cases)
    names = sorted(groups)
    if max_cases < len(names):
        names = rng.sample(names, max_cases)
    selected_by_dataset: dict[str, list[Case]] = {name: [] for name in names}
    remaining = max_cases
    base_quota = max(1, max_cases // max(1, len(names)))
    for name in names:
        pool = list(groups[name])
        rng.shuffle(pool)
        take = min(base_quota, len(pool), remaining)
        selected_by_dataset[name].extend(pool[:take])
        groups[name] = pool[take:]
        remaining -= take
        if remaining <= 0:
            break
    while remaining > 0:
        available = [name for name in names if groups[name]]
        if not available:
            break
        for name in available:
            selected_by_dataset[name].append(groups[name].pop(0))
            remaining -= 1
            if remaining <= 0:
                break
    selected: list[Case] = []
    max_len = max((len(items) for items in selected_by_dataset.values()), default=0)
    for idx in range(max_len):
        for name in names:
            items = selected_by_dataset[name]
            if idx < len(items):
                selected.append(items[idx])
    return selected[:max_cases]


def describe_case_distribution(cases: list[Case]) -> str:
    counts = Counter(case.dataset for case in cases)
    return ", ".join(f"{name}={counts[name]}" for name in sorted(counts)) or "empty"


def write_case_manifest(path: Path, cases: list[Case]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([{"dataset": case.dataset, "case_id": case.case_id} for case in cases], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def select_split(
    datasets: dict[str, list[Case]],
    *,
    mode: str,
    dataset_name: str | None,
    max_cases: int,
    sample_strategy: str,
    sample_seed: int,
) -> list[Case]:
    mode = mode.lower()
    if mode not in {"train", "test"}:
        raise ValueError(f"Unknown prompt_uml split mode: {mode}")
    if not dataset_name:
        raise ValueError("prompt_uml.test_dataset is required")
    test_name = dataset_name.lower()
    if test_name not in datasets:
        raise ValueError(f"Unknown prompt_uml test dataset {test_name!r}. Available: {', '.join(sorted(datasets))}")
    if mode == "test":
        cases = list(datasets[test_name])
    else:
        cases = [case for name, items in datasets.items() if name != test_name for case in items]
    return select_cases_with_strategy(cases, max_cases=max_cases, strategy=sample_strategy, seed=sample_seed)


def normalize_base_url(base_url: str) -> str:
    value = (base_url or DEFAULT_BASE_URL).strip().rstrip("/")
    suffix = "/chat/completions"
    if value.endswith(suffix):
        value = value[: -len(suffix)]
    return value + "/"


def post_chat_completion(*, endpoint: str, body: dict[str, Any], api_key: str, timeout: int) -> str:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise LLMHTTPError(exc.code, error_body, dict(exc.headers.items())) from exc

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected LLM response: {json.dumps(payload, ensure_ascii=False)[:1000]}") from exc
    return str(content or "").strip()


def chat_completion(
    *,
    messages: list[dict[str, str]],
    model: str,
    api_key: str,
    base_url: str,
    temperature: float,
    top_p: float | None,
    max_tokens: int,
    thinking: str,
    do_sample: bool | None,
    timeout: int,
    state_dir: Path | None = None,
    retry_phase: str = "prompt_uml_llm_request",
    retry_context: dict[str, Any] | None = None,
    max_retries: int = 20,
    retry_initial_wait: int = 30,
    retry_max_wait: int = 600,
) -> str:
    if not api_key:
        raise RuntimeError("ZHIPU_LLM_API_KEY or prompt_uml.api_key is required unless mock_with_gold is enabled")
    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if top_p is not None:
        body["top_p"] = top_p
    if do_sample is not None:
        body["do_sample"] = do_sample
    if thinking:
        body["thinking"] = {"type": thinking}
    endpoint = normalize_base_url(base_url) + "chat/completions"
    try:
        return call_with_provider_retries(
            lambda: post_chat_completion(
                endpoint=endpoint,
                body=body,
                api_key=api_key,
                timeout=timeout,
            ),
            phase=retry_phase,
            state_dir=state_dir,
            context=retry_context,
            max_retries=max_retries,
            initial_wait=retry_initial_wait,
            max_wait=retry_max_wait,
        )
    except LLMHTTPError as exc:
        lowered = exc.body.lower()
        retriable_fields = []
        for field in ("thinking", "do_sample", "max_tokens"):
            if field in body and field in lowered:
                retriable_fields.append(field)
        if exc.status_code not in {400, 422} or not retriable_fields:
            raise

        retry_body = {k: v for k, v in body.items() if k not in set(retriable_fields)}
        print(f"[glm-compat] Retrying without rejected fields: {', '.join(retriable_fields)}")
        return call_with_provider_retries(
            lambda: post_chat_completion(
                endpoint=endpoint,
                body=retry_body,
                api_key=api_key,
                timeout=timeout,
            ),
            phase=f"{retry_phase}:glm_compat",
            state_dir=state_dir,
            context=retry_context,
            max_retries=max_retries,
            initial_wait=retry_initial_wait,
            max_wait=retry_max_wait,
        )


def strip_code_fence(text: str) -> str:
    match = re.search(r"```(?:plantuml|puml|uml)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else text.strip()


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


def has_required_wrappers(text: str) -> bool:
    raw = strip_code_fence(text)
    return "@startuml" in raw and "@enduml" in raw


def validate_plantuml(uml_code: str, plantuml_jar: Path, timeout: int = 30) -> SyntaxResult:
    errors: list[str] = []
    if not plantuml_jar.exists():
        return SyntaxResult(False, [f"PlantUML jar not found: {plantuml_jar}"])
    if not has_required_wrappers(uml_code):
        errors.append("Missing required @startuml/@enduml wrapper")

    normalized = extract_plantuml(uml_code, wrap_if_needed=True)
    try:
        proc = subprocess.run(
            ["java", "-jar", str(plantuml_jar), "-syntax"],
            input=normalized,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return SyntaxResult(False, ["Java executable not found"])
    except subprocess.TimeoutExpired:
        return SyntaxResult(False, ["PlantUML syntax check timed out"])

    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    for line in output.splitlines():
        stripped = line.strip()
        if re.match(r"^(ERROR|SyntaxError|Exception)", stripped, flags=re.IGNORECASE):
            errors.append(stripped)
        elif " line " in stripped and " :" in stripped:
            errors.append(stripped)
    if proc.returncode != 0 and not errors:
        errors.append(f"PlantUML exited with return code {proc.returncode}")
    return SyntaxResult(not errors, errors)


def _is_terminal_line(lower: str) -> bool:
    return lower in {"stop", "end"} or lower.startswith("detach") or lower.startswith("kill")


def _is_activity_line(line: str) -> bool:
    return line.startswith(":") and ";" in line


def _condition_keyword(line: str) -> str | None:
    lower = line.lower()
    for keyword in ("if", "elseif", "else if", "switch", "case", "while"):
        if re.match(rf"^{re.escape(keyword)}\s*\(", lower):
            return keyword
    if re.search(r"^repeat\s+while\s*\(", lower):
        return "repeat while"
    return None


def _label_for_structure_line(line: str) -> str | None:
    if _is_activity_line(line):
        return normalize_label(line[1 : line.rfind(";")])
    keyword = _condition_keyword(line)
    if not keyword:
        return None
    if keyword == "repeat while":
        match = re.search(r"repeat\s+while\s*\((.*?)\)", line, flags=re.IGNORECASE)
        return normalize_label(match.group(1)) if match else None
    if keyword == "elseif":
        return normalize_label(extract_condition(line, "elseif") or "")
    if keyword == "else if":
        return normalize_label(extract_condition(line, "else if") or "")
    return normalize_label(extract_condition(line, keyword) or "")


def _slug_label(label: str) -> str:
    return normalize_label(label)


def _split_arrow_endpoint(endpoint: str) -> str:
    endpoint = endpoint.strip()
    endpoint = re.sub(r"^\[|\]$", "", endpoint).strip()
    endpoint = re.sub(r"^:+|;+$", "", endpoint).strip()
    endpoint = re.sub(r"^\"|\"$", "", endpoint).strip()
    return _slug_label(endpoint)


def _strip_note_lines(code: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    in_note = False
    for line_no, raw_line in enumerate(code.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("note "):
            if ":" in line:
                continue
            in_note = True
            continue
        if in_note:
            if lower == "end note" or lower.startswith("end note"):
                in_note = False
            continue
        if lower.startswith("@"):
            continue
        result.append((line_no, line))
    return result


def _add_graph_node(graph: ActivityGraph, label: str, kind: str, line_no: int) -> str:
    node_id = f"{kind}#{len(graph.order) + 1}"
    graph.nodes[node_id] = GraphNode(node_id=node_id, label=label, kind=kind, line_no=line_no)
    graph.order.append(node_id)
    if kind == "start":
        graph.start_ids.append(node_id)
    if kind == "terminal":
        graph.terminal_ids.append(node_id)
    return node_id


def _add_edges(graph: ActivityGraph, sources: list[str], target: str) -> None:
    for source in sources:
        if source != target:
            graph.edges.append((source, target))


def _is_block_end(line: str, end_tokens: set[str]) -> bool:
    lower = line.lower()
    return any(lower.startswith(token) for token in end_tokens)


def _split_if_branches(lines: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    branches: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    depth = 0
    for line_no, line in lines:
        lower = line.lower()
        if depth == 0 and (lower.startswith("else") or lower.startswith("elseif")):
            branches.append(current)
            current = []
            if lower.startswith("elseif") or lower.startswith("else if"):
                current.append((line_no, line))
            continue
        current.append((line_no, line))
        if re.match(r"^if\s*\(", lower):
            depth += 1
        elif lower.startswith("endif") or lower == "end if":
            depth = max(0, depth - 1)
    branches.append(current)
    return branches


def _split_switch_branches(lines: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    branches: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    depth = 0
    for line_no, line in lines:
        lower = line.lower()
        if depth == 0 and lower.startswith("case"):
            if current:
                branches.append(current)
            current = [(line_no, line)]
            continue
        current.append((line_no, line))
        if re.match(r"^switch\s*\(", lower):
            depth += 1
        elif lower.startswith("endswitch"):
            depth = max(0, depth - 1)
    if current:
        branches.append(current)
    return branches


def _split_fork_branches(lines: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    branches: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    depth = 0
    for line_no, line in lines:
        lower = line.lower()
        if depth == 0 and lower.startswith("fork end"):
            if current:
                branches.append(current)
            current = []
            continue
        if depth == 0 and lower.startswith("fork again"):
            branches.append(current)
            current = []
            continue
        current.append((line_no, line))
        if lower == "fork":
            depth += 1
        elif lower.startswith("end fork"):
            depth = max(0, depth - 1)
    branches.append(current)
    return branches


def _find_matching_block(
    lines: list[tuple[int, str]],
    start: int,
    *,
    opener: str,
    closer: str,
) -> int:
    depth = 0
    for idx in range(start, len(lines)):
        lower = lines[idx][1].lower()
        if opener == "if" and re.match(r"^if\s*\(", lower):
            depth += 1
        elif opener == "switch" and re.match(r"^switch\s*\(", lower):
            depth += 1
        elif opener == "fork" and lower == "fork":
            depth += 1
        elif opener == "repeat" and lower == "repeat":
            depth += 1
        elif opener == "while" and re.match(r"^while\s*\(", lower):
            depth += 1

        if closer == "endif" and (lower.startswith("endif") or lower == "end if"):
            depth -= 1
        elif closer == "endswitch" and lower.startswith("endswitch"):
            depth -= 1
        elif closer == "end fork" and (
            lower.startswith("end fork") or lower.startswith("endfork") or lower.startswith("fork end")
        ):
            depth -= 1
        elif closer == "repeat while" and re.search(r"^repeat\s+while\s*\(", lower):
            depth -= 1
        elif closer == "endwhile" and lower.startswith("endwhile"):
            depth -= 1

        if depth == 0:
            return idx
    return -1


def _parse_activity_block(
    graph: ActivityGraph,
    lines: list[tuple[int, str]],
    entries: list[str],
) -> list[str]:
    pending = list(entries)
    idx = 0
    while idx < len(lines):
        line_no, line = lines[idx]
        lower = line.lower()

        if lower in {"start", "start:"}:
            node_id = _add_graph_node(graph, "start", "start", line_no)
            if pending:
                _add_edges(graph, pending, node_id)
            pending = [node_id]
            idx += 1
            continue

        if _is_terminal_line(lower):
            node_id = _add_graph_node(graph, lower, "terminal", line_no)
            _add_edges(graph, pending, node_id)
            pending = []
            idx += 1
            continue

        if re.match(r"^if\s*\(", lower):
            condition = normalize_label(extract_condition(line, "if") or f"if line {line_no}")
            decision_id = _add_graph_node(graph, condition, "decision", line_no)
            _add_edges(graph, pending, decision_id)
            end_idx = _find_matching_block(lines, idx, opener="if", closer="endif")
            if end_idx == -1:
                end_idx = len(lines)
            body = lines[idx + 1 : end_idx]
            branch_exits: list[str] = []
            for branch in _split_if_branches(body):
                branch_exits.extend(_parse_activity_block(graph, branch, [decision_id]))
            pending = branch_exits or [decision_id]
            idx = end_idx + 1
            continue

        if re.match(r"^switch\s*\(", lower):
            condition = normalize_label(extract_condition(line, "switch") or f"switch line {line_no}")
            switch_id = _add_graph_node(graph, condition, "decision", line_no)
            _add_edges(graph, pending, switch_id)
            end_idx = _find_matching_block(lines, idx, opener="switch", closer="endswitch")
            if end_idx == -1:
                end_idx = len(lines)
            body = lines[idx + 1 : end_idx]
            branch_exits: list[str] = []
            for branch in _split_switch_branches(body):
                branch_exits.extend(_parse_activity_block(graph, branch, [switch_id]))
            pending = branch_exits or [switch_id]
            idx = end_idx + 1
            continue

        if lower == "fork":
            fork_id = _add_graph_node(graph, f"fork line {line_no}", "fork", line_no)
            join_id = _add_graph_node(graph, f"join line {line_no}", "join", line_no)
            _add_edges(graph, pending, fork_id)
            end_idx = _find_matching_block(lines, idx, opener="fork", closer="end fork")
            if end_idx == -1:
                end_idx = len(lines)
            body = lines[idx + 1 : end_idx]
            branch_exits: list[str] = []
            for branch in _split_fork_branches(body):
                branch_exits.extend(_parse_activity_block(graph, branch, [fork_id]))
            _add_edges(graph, branch_exits or [fork_id], join_id)
            pending = [join_id]
            idx = end_idx + 1
            continue

        if lower == "repeat":
            repeat_id = _add_graph_node(graph, f"repeat line {line_no}", "loop", line_no)
            _add_edges(graph, pending, repeat_id)
            end_idx = _find_matching_block(lines, idx, opener="repeat", closer="repeat while")
            if end_idx == -1:
                end_idx = len(lines)
            body = lines[idx + 1 : end_idx]
            exits = _parse_activity_block(graph, body, [repeat_id])
            if end_idx < len(lines):
                condition = _label_for_structure_line(lines[end_idx][1]) or f"repeat while line {lines[end_idx][0]}"
                loop_id = _add_graph_node(graph, condition, "loop_condition", lines[end_idx][0])
                _add_edges(graph, exits or [repeat_id], loop_id)
                graph.edges.append((loop_id, repeat_id))
                pending = [loop_id]
            else:
                pending = exits or [repeat_id]
            idx = end_idx + 1
            continue

        if re.match(r"^while\s*\(", lower):
            condition = normalize_label(extract_condition(line, "while") or f"while line {line_no}")
            loop_id = _add_graph_node(graph, condition, "loop_condition", line_no)
            _add_edges(graph, pending, loop_id)
            end_idx = _find_matching_block(lines, idx, opener="while", closer="endwhile")
            if end_idx == -1:
                end_idx = len(lines)
            body = lines[idx + 1 : end_idx]
            exits = _parse_activity_block(graph, body, [loop_id])
            _add_edges(graph, exits or [loop_id], loop_id)
            pending = [loop_id]
            idx = end_idx + 1
            continue

        label = _label_for_structure_line(line)
        if label:
            node_id = _add_graph_node(graph, label, "activity", line_no)
            _add_edges(graph, pending, node_id)
            pending = [node_id]
        idx += 1

    return pending


def build_activity_graph(uml_code: str, *, check_explicit_arrows: bool = True) -> ActivityGraph:
    code = extract_plantuml(uml_code, wrap_if_needed=True)
    graph = ActivityGraph(nodes={}, order=[], edges=[], errors=[], dangling_edges=[], start_ids=[], terminal_ids=[])
    lines = _strip_note_lines(code)
    _parse_activity_block(graph, lines, [])

    if check_explicit_arrows:
        labels = {
            node.label
            for node in graph.nodes.values()
            if node.kind not in {"start", "terminal", "fork", "join"}
        }
        for line_no, line in lines:
            if _is_activity_line(line):
                continue
            if "-->" not in line and "->" not in line:
                continue
            parts = re.split(r"-+>", line, maxsplit=1)
            if len(parts) != 2:
                continue
            left = _split_arrow_endpoint(parts[0])
            right = _split_arrow_endpoint(parts[1])
            if left and left not in labels and left not in {"start", "stop", "end"}:
                graph.dangling_edges.append(f"line {line_no}: missing source {left}")
            if right and right not in labels and right not in {"start", "stop", "end"}:
                graph.dangling_edges.append(f"line {line_no}: missing target {right}")
    return graph


def validate_activity_structure(uml_code: str, *, check_explicit_arrows: bool = True) -> StructureResult:
    """Check LATO-style structural validity using a PlantUML activity CFG."""
    graph = build_activity_graph(uml_code, check_explicit_arrows=check_explicit_arrows)
    errors: list[str] = list(graph.errors)
    start_count = len(graph.start_ids)
    terminal_count = len(graph.terminal_ids)

    if start_count != 1:
        errors.append(f"Expected exactly one start node, found {start_count}")
    if terminal_count < 1:
        errors.append("Expected at least one stop/end terminal node")

    reachable: set[str] = set()
    adjacency: dict[str, list[str]] = {}
    for source, target in graph.edges:
        if source not in graph.nodes:
            errors.append(f"Dangling edge source id: {source}")
            continue
        if target not in graph.nodes:
            errors.append(f"Dangling edge target id: {target}")
            continue
        adjacency.setdefault(source, []).append(target)
    if graph.start_ids:
        stack = [graph.start_ids[0]]
        while stack:
            node_id = stack.pop()
            if node_id in reachable:
                continue
            reachable.add(node_id)
            stack.extend(adjacency.get(node_id, []))

    semantic_node_ids = [
        node_id
        for node_id, node in graph.nodes.items()
        if node.kind not in {"start", "fork", "join"}
    ]
    unreachable = [node_id for node_id in semantic_node_ids if node_id not in reachable]
    if unreachable:
        errors.append(f"Unreachable nodes: {len(unreachable)}")
    if graph.dangling_edges:
        errors.extend(graph.dangling_edges[:10])

    return StructureResult(
        passed=not errors,
        errors=errors,
        start_count=start_count,
        terminal_count=terminal_count,
        node_count=len(semantic_node_ids),
        reachable_count=sum(1 for node_id in semantic_node_ids if node_id in reachable),
        dangling_edges=graph.dangling_edges[:20],
    )


def cfg_semantic_elements(uml_code: str) -> list[str]:
    graph = build_activity_graph(uml_code, check_explicit_arrows=False)
    return [
        graph.nodes[node_id].label
        for node_id in graph.order
        if graph.nodes[node_id].kind in {"activity", "decision", "loop_condition"}
    ]


def cfg_relations(uml_code: str) -> list[str]:
    graph = build_activity_graph(uml_code, check_explicit_arrows=False)
    semantic_kinds = {"activity", "decision", "loop_condition"}
    adjacency: dict[str, list[str]] = {}
    for source, target in graph.edges:
        adjacency.setdefault(source, []).append(target)

    def semantic_successors(node_id: str) -> list[str]:
        found: list[str] = []
        seen: set[str] = set()
        stack = list(adjacency.get(node_id, []))
        while stack:
            current = stack.pop(0)
            if current in seen:
                continue
            seen.add(current)
            node = graph.nodes.get(current)
            if node is None:
                continue
            if node.kind in semantic_kinds:
                found.append(current)
            elif node.kind != "terminal":
                stack.extend(adjacency.get(current, []))
        return found

    relations: list[str] = []
    for source in graph.order:
        source_node = graph.nodes.get(source)
        if source_node is None or source_node.kind not in semantic_kinds:
            continue
        for target in semantic_successors(source):
            target_node = graph.nodes[target]
            if source_node.label and target_node.label and source_node.label != target_node.label:
                relations.append(f"{source_node.label} -> {target_node.label}")
    return relations


def _legacy_validate_activity_structure(uml_code: str, *, check_explicit_arrows: bool = True) -> StructureResult:
    """Legacy lightweight validator retained for reference during migration."""
    code = extract_plantuml(uml_code, wrap_if_needed=True)
    errors: list[str] = []
    nodes: list[tuple[str, str]] = []
    edges: list[tuple[str, str]] = []
    dangling_edges: list[str] = []
    in_note = False
    start_count = 0
    terminal_count = 0
    last_node_id: str | None = None
    seen_start = False
    semantic_before_start = 0
    control_depth = 0

    for line_no, raw_line in enumerate(code.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("note "):
            if ":" in line:
                continue
            in_note = True
            continue
        if in_note:
            if lower == "end note" or lower.startswith("end note"):
                in_note = False
            continue
        if lower.startswith("@"):
            continue

        if lower in {"start", "start:"}:
            start_count += 1
            node_id = f"start#{start_count}"
            nodes.append((node_id, "start"))
            if last_node_id:
                edges.append((last_node_id, node_id))
            last_node_id = node_id
            seen_start = True
            continue
        if _is_terminal_line(lower):
            terminal_count += 1
            node_id = f"terminal#{terminal_count}"
            nodes.append((node_id, lower))
            if last_node_id:
                edges.append((last_node_id, node_id))
            # Top-level terminals end the current flow. Terminals inside
            # condition/switch/fork/loop blocks may only end that branch.
            if control_depth == 0:
                last_node_id = None
            continue

        if (
            re.match(r"^if\s*\(", lower)
            or re.match(r"^switch\s*\(", lower)
            or re.match(r"^while\s*\(", lower)
            or lower == "fork"
            or lower == "repeat"
        ):
            control_depth += 1
        elif (
            lower.startswith("endif")
            or lower == "end if"
            or lower.startswith("endswitch")
            or lower.startswith("end fork")
            or lower.startswith("endwhile")
            or re.search(r"^repeat\s+while\s*\(", lower)
        ):
            control_depth = max(0, control_depth - 1)

        label = _label_for_structure_line(line)
        if label:
            if not seen_start:
                semantic_before_start += 1
            node_id = f"node#{len(nodes) + 1}"
            nodes.append((node_id, label))
            if last_node_id:
                edges.append((last_node_id, node_id))
            last_node_id = node_id

    labels = {label for _, label in nodes if label not in {"start", "stop", "end", "detach", "kill"}}
    if check_explicit_arrows:
        for line_no, raw_line in enumerate(code.splitlines(), start=1):
            line = raw_line.strip()
            if _is_activity_line(line):
                continue
            if "-->" not in line and "->" not in line:
                continue
            parts = re.split(r"-+>", line, maxsplit=1)
            if len(parts) != 2:
                continue
            left = _split_arrow_endpoint(parts[0])
            right = _split_arrow_endpoint(parts[1])
            if left and left not in labels and left not in {"start", "stop", "end"}:
                dangling_edges.append(f"line {line_no}: missing source {left}")
            if right and right not in labels and right not in {"start", "stop", "end"}:
                dangling_edges.append(f"line {line_no}: missing target {right}")

    if start_count != 1:
        errors.append(f"Expected exactly one start node, found {start_count}")
    if terminal_count < 1:
        errors.append("Expected at least one stop/end terminal node")
    if semantic_before_start:
        errors.append(f"Semantic nodes before start: {semantic_before_start}")

    reachable: set[str] = set()
    adjacency: dict[str, list[str]] = {}
    for source, target in edges:
        adjacency.setdefault(source, []).append(target)
    if nodes:
        start_nodes = [node_id for node_id, label in nodes if label == "start"]
        stack = list(start_nodes[:1])
        while stack:
            node_id = stack.pop()
            if node_id in reachable:
                continue
            reachable.add(node_id)
            stack.extend(adjacency.get(node_id, []))
    semantic_node_ids = [node_id for node_id, label in nodes if label != "start"]
    unreachable = [node_id for node_id in semantic_node_ids if node_id not in reachable]
    if unreachable:
        errors.append(f"Unreachable nodes: {len(unreachable)}")
    if dangling_edges:
        errors.extend(dangling_edges[:10])

    return StructureResult(
        passed=not errors,
        errors=errors,
        start_count=start_count,
        terminal_count=terminal_count,
        node_count=len(semantic_node_ids),
        reachable_count=sum(1 for node_id in semantic_node_ids if node_id in reachable),
        dangling_edges=dangling_edges[:20],
    )


def normalize_label(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\\n", " ")
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9_+\-*/=<>()?. ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_condition(line: str, keyword: str) -> str | None:
    match = re.search(rf"^\s*{keyword}\s*\((.*?)\)", line, flags=re.IGNORECASE)
    return match.group(1).strip() if match else None


def iter_semantic_elements(uml_code: str) -> list[str]:
    return cfg_semantic_elements(uml_code)


def extract_relations(uml_code: str) -> list[str]:
    return cfg_relations(uml_code)


def greedy_match(gold_items: list[str], pred_items: list[str], threshold: float) -> tuple[int, list[str], list[str]]:
    gold_counter = Counter(gold_items)
    pred_counter = Counter(pred_items)
    exact = 0
    for item in list(gold_counter):
        count = min(gold_counter[item], pred_counter.get(item, 0))
        if count:
            exact += count
            gold_counter[item] -= count
            pred_counter[item] -= count

    remaining_gold = list(gold_counter.elements())
    remaining_pred = list(pred_counter.elements())
    matched_gold: set[int] = set()
    matched_pred: set[int] = set()
    fuzzy = 0
    candidates: list[tuple[float, int, int]] = []
    for gi, gold in enumerate(remaining_gold):
        for pi, pred in enumerate(remaining_pred):
            score = difflib.SequenceMatcher(None, gold, pred).ratio()
            if score >= threshold:
                candidates.append((score, gi, pi))
    for _, gi, pi in sorted(candidates, reverse=True):
        if gi in matched_gold or pi in matched_pred:
            continue
        matched_gold.add(gi)
        matched_pred.add(pi)
        fuzzy += 1

    missing = [item for i, item in enumerate(remaining_gold) if i not in matched_gold]
    extra = [item for i, item in enumerate(remaining_pred) if i not in matched_pred]
    return exact + fuzzy, missing, extra


def compute_metric(gold_items: list[str], pred_items: list[str], threshold: float) -> MetricBundle:
    if not gold_items and not pred_items:
        return MetricBundle(1.0, 1.0, 1.0, [], [])
    correct, missing, extra = greedy_match(gold_items, pred_items, threshold)
    precision = correct / len(pred_items) if pred_items else 0.0
    recall = correct / len(gold_items) if gold_items else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return MetricBundle(precision, recall, f1, missing[:20], extra[:20])


def classify_failures(
    syntax: SyntaxResult,
    structure: StructureResult,
    node_metrics: MetricBundle,
    relation_metrics: MetricBundle,
) -> list[str]:
    failures: list[str] = []
    if not syntax.passed:
        failures.append("syntax_error")
    if not structure.passed:
        failures.append("structure_invalid")
    if syntax.passed and structure.start_count != 1:
        failures.append("invalid_start")
    if syntax.passed and structure.terminal_count < 1:
        failures.append("missing_terminal")
    if syntax.passed and structure.reachable_count < structure.node_count:
        failures.append("unreachable_node")
    if syntax.passed and structure.dangling_edges:
        failures.append("dangling_control_flow")
    if node_metrics.recall < 0.85:
        failures.append("missing_activity")
    if node_metrics.precision < 0.85:
        failures.append("extra_activity")
    if relation_metrics.recall < 0.80:
        failures.append("missing_or_wrong_relation")
    if relation_metrics.precision < 0.80:
        failures.append("extra_or_wrong_relation")
    missing_relation_text = " ".join(relation_metrics.missing)
    if any(word in missing_relation_text for word in ("fork", "parallel", "concurrent", "simultaneous")):
        failures.append("wrong_parallel")
    if any(word in missing_relation_text for word in ("repeat", "while", "until", "loop", "periodic")):
        failures.append("wrong_loop")
    return failures


def is_infrastructure_error(message: str) -> bool:
    lowered = message.lower()
    return any(
        marker in lowered
        for marker in (
            "timed out",
            "incompleteread",
            "ssl:",
            "urlopen error",
            "connection reset",
            "remote end closed",
            "temporary failure",
            "llm http 429",
            "llm http 500",
            "llm http 502",
            "llm http 503",
            "llm http 504",
        )
    )


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize_records(records: list[EvaluationRecord]) -> dict[str, float]:
    llm_records = [r.llm_element_metrics for r in records if r.llm_element_metrics.enabled]
    llm_success = [m for m in llm_records if m.status == "success"]
    return {
        "count": float(len(records)),
        "syntax_pass_rate": average([1.0 if r.syntax.passed else 0.0 for r in records]),
        "structure_valid_rate": average([1.0 if r.structure.passed else 0.0 for r in records]),
        "infrastructure_error_rate": average([1.0 if "infrastructure_error" in r.failure_types else 0.0 for r in records]),
        "node_precision": average([r.node_metrics.precision for r in records]),
        "node_recall": average([r.node_metrics.recall for r in records]),
        "node_f1": average([r.node_metrics.f1 for r in records]),
        "relation_precision": average([r.relation_metrics.precision for r in records]),
        "relation_recall": average([r.relation_metrics.recall for r in records]),
        "relation_f1": average([r.relation_metrics.f1 for r in records]),
        "plantuml_compilation_pass_rate": average([1.0 if r.plantuml_compilation.passed else 0.0 for r in records]),
        "llm_element_evaluated": float(len(llm_success)),
        "llm_element_failed": float(len(llm_records) - len(llm_success)),
        "llm_node_precision": average([m.node_metrics.precision for m in llm_success]),
        "llm_node_recall": average([m.node_metrics.recall for m in llm_success]),
        "llm_node_f1": average([m.node_metrics.f1 for m in llm_success]),
        "llm_relation_precision": average([m.relation_metrics.precision for m in llm_success]),
        "llm_relation_recall": average([m.relation_metrics.recall for m in llm_success]),
        "llm_relation_f1": average([m.relation_metrics.f1 for m in llm_success]),
        "quality_score": average([r.quality_score for r in records]),
        "mean_reward": average([r.reward for r in records]),
    }


def calculate_reward(
    syntax: SyntaxResult,
    structure: StructureResult,
    node_metrics: MetricBundle,
    relation_metrics: MetricBundle,
    *,
    node_threshold: float,
    relation_threshold: float,
) -> float:
    if (
        syntax.passed
        and structure.passed
        and node_metrics.f1 >= node_threshold
        and relation_metrics.f1 >= relation_threshold
    ):
        return 1.0
    return 0.0


def calculate_quality_score(
    syntax: SyntaxResult,
    node_metrics: MetricBundle,
    relation_metrics: MetricBundle,
    *,
    node_weight: float,
    relation_weight: float,
) -> float:
    if not syntax.passed:
        return 0.0
    total = node_weight + relation_weight
    if total <= 0:
        node_weight, relation_weight, total = 0.6, 0.4, 1.0
    return (node_weight * node_metrics.f1 + relation_weight * relation_metrics.f1) / total


def generate_plantuml_for_case(
    prompt: str,
    case: Case,
    settings: dict[str, Any],
    *,
    state_dir: Path | None = None,
    retry_phase: str = "prompt_uml_eval",
) -> str:
    if settings.get("mock_with_gold"):
        return extract_plantuml(case.gold_plantuml, wrap_if_needed=True)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Input:\n{case.content}\n\nOutput:"},
    ]
    return chat_completion(
        messages=messages,
        model=settings.get("model", DEFAULT_MODEL),
        api_key=settings.get("api_key", ""),
        base_url=settings.get("base_url", DEFAULT_BASE_URL),
        temperature=float(settings.get("temperature", 0.2)),
        top_p=settings.get("top_p"),
        max_tokens=int(settings.get("max_tokens", 6000)),
        thinking=settings.get("thinking", "disabled"),
        do_sample=settings.get("do_sample"),
        timeout=int(settings.get("llm_timeout", 300)),
        state_dir=state_dir,
        retry_phase=retry_phase,
        retry_context={"dataset": case.dataset, "case_id": case.case_id},
        max_retries=int(settings.get("llm_max_retries", 20)),
        retry_initial_wait=int(settings.get("llm_rate_limit_initial_wait", 30)),
        retry_max_wait=int(settings.get("llm_rate_limit_max_wait", 600)),
    )


def evaluate_case(
    prompt: str,
    case: Case,
    settings: dict[str, Any],
    *,
    state_dir: Path | None = None,
    retry_phase: str = "prompt_uml_eval",
) -> EvaluationRecord:
    try:
        generated = generate_plantuml_for_case(
            prompt,
            case,
            settings,
            state_dir=state_dir,
            retry_phase=retry_phase,
        )
    except Exception as exc:
        generated = ""
        syntax = SyntaxResult(False, [f"LLM generation failed: {exc}"])
        structure = StructureResult(False, ["No generated PlantUML to validate"], 0, 0, 0, 0, [])
        node_metrics = compute_metric(
            iter_semantic_elements(case.gold_plantuml),
            [],
            threshold=float(settings.get("node_match_threshold", 0.82)),
        )
        relation_metrics = compute_metric(
            extract_relations(case.gold_plantuml),
            [],
            threshold=float(settings.get("relation_match_threshold", 0.86)),
        )
        failure_types = ["generation_error"]
        if is_infrastructure_error(str(exc)):
            failure_types.append("infrastructure_error")
        else:
            failure_types.extend(["syntax_error", "missing_activity", "missing_or_wrong_relation"])
    else:
        syntax = validate_plantuml(generated, Path(settings.get("plantuml_jar", DEFAULT_PLANTUML_JAR)))
        structure = validate_activity_structure(
            generated,
            check_explicit_arrows=bool(settings.get("check_explicit_arrows", False)),
        )
        node_metrics = compute_metric(
            iter_semantic_elements(case.gold_plantuml),
            iter_semantic_elements(generated),
            threshold=float(settings.get("node_match_threshold", 0.82)),
        )
        relation_metrics = compute_metric(
            extract_relations(case.gold_plantuml),
            extract_relations(generated),
            threshold=float(settings.get("relation_match_threshold", 0.86)),
        )
        failure_types = classify_failures(syntax, structure, node_metrics, relation_metrics)

    generated_plantuml = extract_plantuml(generated, wrap_if_needed=False)
    plantuml_compilation = check_plantuml_compilation(
        generated_plantuml,
        Path(settings.get("plantuml_jar", DEFAULT_PLANTUML_JAR)),
        timeout=int(settings.get("plantuml_compile_timeout", 30)),
    )
    llm_element_metrics = evaluate_llm_elements(
        ground_truth=case.gold_plantuml,
        prediction=generated_plantuml,
        enabled=bool(settings.get("llm_element_metrics", False)),
        model=str(settings.get("llm_judge_model") or settings.get("model", DEFAULT_MODEL)),
        api_key=str(settings.get("llm_judge_api_key") or settings.get("api_key", "")),
        base_url=str(settings.get("llm_judge_base_url") or settings.get("base_url", DEFAULT_BASE_URL)),
        temperature=float(settings.get("llm_judge_temperature", 0.0)),
        max_tokens=int(settings.get("llm_judge_max_tokens", 4096)),
        timeout=int(settings.get("llm_judge_timeout", settings.get("llm_timeout", 300))),
        thinking=str(settings.get("llm_judge_thinking", "disabled")),
        max_retries=int(settings.get("llm_judge_max_retries", 3)),
        state_dir=state_dir,
        retry_phase=f"{retry_phase}:llm_judge",
        retry_context={"dataset": case.dataset, "case_id": case.case_id},
        provider_max_retries=int(settings.get("llm_max_retries", 20)),
        retry_initial_wait=int(settings.get("llm_rate_limit_initial_wait", 30)),
        retry_max_wait=int(settings.get("llm_rate_limit_max_wait", 600)),
    )
    if llm_element_metrics.status == "error":
        failure_types.append("llm_element_judge_error")

    reward = calculate_reward(
        syntax,
        structure,
        node_metrics,
        relation_metrics,
        node_threshold=float(settings.get("node_f1_pass_threshold", 0.70)),
        relation_threshold=float(settings.get("relation_f1_pass_threshold", 0.55)),
    )
    quality_score = calculate_quality_score(
        syntax,
        node_metrics,
        relation_metrics,
        node_weight=float(settings.get("quality_node_weight", 0.6)),
        relation_weight=float(settings.get("quality_relation_weight", 0.4)),
    )
    return EvaluationRecord(
        dataset=case.dataset,
        case_id=case.case_id,
        input_requirement=case.content,
        gold_plantuml=case.gold_plantuml,
        generated_plantuml=generated_plantuml,
        syntax=syntax,
        structure=structure,
        node_metrics=node_metrics,
        relation_metrics=relation_metrics,
        plantuml_compilation=plantuml_compilation,
        llm_element_metrics=llm_element_metrics,
        quality_score=quality_score,
        reward=reward,
        failure_types=failure_types,
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_trace(task_dir: Path, case: Case, record: EvaluationRecord, prompt_path: Path) -> None:
    trace = {
        "backend": "prompt_uml",
        "task_id": case.case_id,
        "dataset": case.dataset,
        "prompt_path": str(prompt_path),
        "messages": [
            {"role": "system", "content_path": str(prompt_path), "note": "UML generation prompt under evaluation"},
            {"role": "user", "content": f"Input:\n{case.content}\n\nOutput:"},
            {"role": "assistant", "content": record.generated_plantuml},
        ],
        "verifier": {
            "reward": record.reward,
            "quality_score": record.quality_score,
            "syntax": dataclasses.asdict(record.syntax),
            "structure": dataclasses.asdict(record.structure),
            "node_metrics": dataclasses.asdict(record.node_metrics),
            "relation_metrics": dataclasses.asdict(record.relation_metrics),
            "plantuml_compilation": dataclasses.asdict(record.plantuml_compilation),
            "llm_element_metrics": dataclasses.asdict(record.llm_element_metrics),
            "failure_types": record.failure_types,
        },
    }
    write_json(task_dir / "agent" / "nexau_in_memory_tracer.cleaned.json", trace)
    nexau_lines = [
        f"prompt_uml task={case.case_id}",
        f"reward={record.reward}",
        f"quality_score={record.quality_score:.4f}",
        f"syntax_passed={record.syntax.passed}",
        f"structure_passed={record.structure.passed}",
        f"node_f1={record.node_metrics.f1:.4f}",
        f"relation_f1={record.relation_metrics.f1:.4f}",
        f"plantuml_compiles={record.plantuml_compilation.passed}",
        f"llm_element_status={record.llm_element_metrics.status}",
        f"failure_types={','.join(record.failure_types) if record.failure_types else 'none'}",
    ]
    if record.llm_element_metrics.status == "success":
        nexau_lines.extend(
            [
                f"llm_node_f1={record.llm_element_metrics.node_metrics.f1:.4f}",
                f"llm_relation_f1={record.llm_element_metrics.relation_metrics.f1:.4f}",
            ]
        )
    (task_dir / "agent").mkdir(parents=True, exist_ok=True)
    (task_dir / "agent" / "nexau.txt").write_text("\n".join(nexau_lines) + "\n", encoding="utf-8")


def write_task_artifacts(job_dir: Path, case: Case, record: EvaluationRecord, prompt_path: Path) -> None:
    task_dir = job_dir / case.case_id
    write_json(task_dir / "result.json", {"task_id": case.case_id, "finished_at": datetime.now().isoformat()})
    (task_dir / "verifier").mkdir(parents=True, exist_ok=True)
    (task_dir / "verifier" / "reward.txt").write_text(str(record.reward), encoding="utf-8")
    write_json(task_dir / "verifier" / "metrics.json", dataclasses.asdict(record))
    write_trace(task_dir, case, record, prompt_path)
    if "infrastructure_error" in record.failure_types:
        (task_dir / "exception.txt").write_text("\n".join(record.syntax.errors), encoding="utf-8")


def build_analysis(records: list[EvaluationRecord], summary: dict[str, float], max_cases: int) -> str:
    failure_counter = Counter(ft for record in records for ft in record.failure_types)
    failed_records = [record for record in records if record.failure_types and "infrastructure_error" not in record.failure_types]
    infra_records = [record for record in records if "infrastructure_error" in record.failure_types]
    worst = sorted(
        failed_records,
        key=lambda record: (
            1 if record.syntax.passed else 0,
            record.node_metrics.f1,
            record.relation_metrics.f1,
        ),
    )[:max_cases]

    lines = ["# Prompt UML Evaluation Analysis", "", "## Summary"]
    for key, value in summary.items():
        if key == "count":
            lines.append(f"- {key}: {int(value)}")
        else:
            lines.append(f"- {key}: {value:.4f}")
    lines.extend(["", "## Failure Types"])
    if failure_counter:
        for failure, count in failure_counter.most_common():
            lines.append(f"- {failure}: {count}")
    else:
        lines.append("- none")
    if infra_records:
        lines.extend(["", "## Infrastructure Errors", f"- count: {len(infra_records)}"])
        lines.append("- These cases failed before model output was available. Do not optimize the prompt based only on them.")
        for record in infra_records[:max_cases]:
            lines.append(f"- {record.case_id}: {' | '.join(record.syntax.errors[:3])}")

    lines.extend(["", "## Representative Failure Cases"])
    if not worst:
        lines.append("- none")
    for record in worst:
        lines.append(f"### {record.case_id}")
        lines.append(f"- dataset: {record.dataset}")
        lines.append(f"- failure_types: {', '.join(record.failure_types) if record.failure_types else 'none'}")
        lines.append(f"- reward: {record.reward:.1f}")
        lines.append(f"- quality_score: {record.quality_score:.4f}")
        lines.append(f"- syntax_passed: {record.syntax.passed}")
        if record.syntax.errors:
            lines.append(f"- syntax_errors: {' | '.join(record.syntax.errors[:5])}")
        lines.append(f"- plantuml_compiles: {record.plantuml_compilation.passed}")
        if record.plantuml_compilation.errors:
            lines.append(f"- plantuml_compile_errors: {' | '.join(record.plantuml_compilation.errors[:5])}")
        lines.append(f"- structure_passed: {record.structure.passed}")
        if record.structure.errors:
            lines.append(f"- structure_errors: {' | '.join(record.structure.errors[:5])}")
        lines.append(
            "- structure_counts: "
            f"start={record.structure.start_count}, terminal={record.structure.terminal_count}, "
            f"reachable={record.structure.reachable_count}/{record.structure.node_count}"
        )
        lines.append(f"- node_f1: {record.node_metrics.f1:.4f}")
        lines.append(f"- relation_f1: {record.relation_metrics.f1:.4f}")
        if record.llm_element_metrics.enabled:
            lines.append(f"- llm_element_status: {record.llm_element_metrics.status}")
            if record.llm_element_metrics.status == "success":
                lines.append(f"- llm_node_f1: {record.llm_element_metrics.node_metrics.f1:.4f}")
                lines.append(f"- llm_relation_f1: {record.llm_element_metrics.relation_metrics.f1:.4f}")
            elif record.llm_element_metrics.error:
                lines.append(f"- llm_element_error: {record.llm_element_metrics.error[:300]}")
        if record.node_metrics.missing:
            lines.append("- missing_nodes:")
            for item in record.node_metrics.missing[:8]:
                lines.append(f"  - {item}")
        if record.node_metrics.extra:
            lines.append("- extra_nodes:")
            for item in record.node_metrics.extra[:8]:
                lines.append(f"  - {item}")
        if record.relation_metrics.missing:
            lines.append("- missing_relations:")
            for item in record.relation_metrics.missing[:8]:
                lines.append(f"  - {item}")
        lines.append("- input_excerpt:")
        lines.append("  " + record.input_requirement[:700].replace("\n", " "))
        lines.append("- generated_excerpt:")
        lines.append("  " + record.generated_plantuml[:700].replace("\n", " "))

    lines.extend(
        [
            "",
            "## Prompt Optimization Guidance",
            "- The editable component is `workspace/work.md` only.",
            "- The evolve agent is optimizing a prompt document; it must not output PlantUML itself.",
            "- Preserve the prompt's required markdown sections.",
            "- Prefer targeted prompt edits tied to failure evidence and predicted affected cases.",
            "- Treat syntax, structural validity, activity coverage, and relation coverage as separate failure surfaces.",
            "- A case passes only when PlantUML syntax, LATO-style structural validity, node F1, and relation F1 all pass their thresholds.",
            "- Use `quality_score`, `node_f1`, and `relation_f1` to judge incremental progress when binary reward remains 0.",
            "- Do not rollback a prompt change solely because reward stayed 0 if continuous quality metrics improved.",
            "- Numbered steps are sequential by default, but sibling entries inside one instruction may require `fork` to match benchmark style.",
            "- If some cases already pass, protect them. Prefer narrow edits for stable-failing cases over broad style changes.",
            "- Use notes sparingly; broad note-related rules can alter extraction and regress activity/relation matching.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_prompt_uml_evaluation(
    *,
    workspace_dir: Path,
    output_root: Path,
    settings: dict[str, Any],
    split: str = "train",
) -> Path:
    datasets_dir = Path(settings.get("datasets_dir", PROJECT_DIR / "prompt_datasets" / "lato")).resolve()
    prompt_filename = settings.get("prompt_filename", "work.md")
    prompt_path = (workspace_dir / prompt_filename).resolve()
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    prompt = prompt_path.read_text(encoding="utf-8")

    datasets = load_cases(datasets_dir)
    max_cases_key = "max_test_cases" if split == "test" else "max_train_cases"
    cases = select_split(
        datasets,
        mode=split,
        dataset_name=settings.get("test_dataset"),
        max_cases=int(settings.get(max_cases_key, 0) or 0),
        sample_strategy=str(
            settings.get("test_sample_strategy", "prefix")
            if split == "test"
            else settings.get("sample_strategy", "stratified")
        ),
        sample_seed=int(settings.get("sample_seed", 13)) + (20_000 if split == "test" else 0),
    )

    job_dir = output_root / datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    job_dir.mkdir(parents=True, exist_ok=False)
    print(f"[prompt-uml] {split} distribution: {describe_case_distribution(cases)}", flush=True)
    write_case_manifest(job_dir / f"{split}_cases.json", cases)

    records: list[EvaluationRecord] = []
    for idx, case in enumerate(cases, start=1):
        print(f"[prompt-uml] {split} {idx}/{len(cases)} {case.case_id}", flush=True)
        record = evaluate_case(
            prompt,
            case,
            settings,
            state_dir=job_dir,
            retry_phase=f"prompt_uml:{split}",
        )
        records.append(record)
        write_task_artifacts(job_dir, case, record, prompt_path)

    summary = summarize_records(records)
    write_json(job_dir / "result.json", {"finished_at": datetime.now().isoformat(), "summary": summary})
    write_json(job_dir / "prompt_uml_summary.json", summary)
    with (job_dir / "prompt_uml_records.jsonl").open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(dataclasses.asdict(record), ensure_ascii=False) + "\n")

    analysis_dir = output_root.parent / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    (analysis_dir / "overview.md").write_text(
        build_analysis(records, summary, int(settings.get("analysis_cases", 8))),
        encoding="utf-8",
    )
    detail_dir = analysis_dir / "detail"
    detail_dir.mkdir(parents=True, exist_ok=True)
    for record in records:
        (detail_dir / f"{record.case_id}.md").write_text(
            build_analysis([record], summarize_records([record]), 1),
            encoding="utf-8",
        )

    return job_dir

