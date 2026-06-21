"""Deterministic PlantUML and activity-diagram metrics."""

from __future__ import annotations

import dataclasses
import difflib
import re
import subprocess
from pathlib import Path
from typing import Any

from llm_element_metrics import CompilationResult, LLMElementMetrics
from prediction import extract_plantuml, strip_code_fence

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
Tail = tuple[str, str | None]

_EMBEDDING_MODELS: dict[str, Any] = {}
_EMBEDDING_CACHE: dict[tuple[str, str], list[float]] = {}


@dataclasses.dataclass
class SyntaxResult:
    passed: bool
    errors: list[str]


@dataclasses.dataclass
class MetricBundle:
    precision: float
    recall: float
    f1: float
    missing: list[str]
    extra: list[str]
    correct: int = 0
    gold_count: int = 0
    pred_count: int = 0
    matches: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    matcher: str = "embedding"


@dataclasses.dataclass
class EvaluationRecord:
    dataset: str
    case_id: str
    input_requirement: str
    gold_plantuml: str
    generated_plantuml: str
    syntax: SyntaxResult
    node_metrics: MetricBundle
    relation_metrics: MetricBundle
    plantuml_compilation: CompilationResult
    llm_element_metrics: LLMElementMetrics
    failure_types: list[str]


@dataclasses.dataclass
class ActivityGraph:
    nodes: list[str]
    relations: list[str]


@dataclasses.dataclass(frozen=True)
class RelationParts:
    source: str
    target: str
    kind: str = ""


@dataclasses.dataclass
class IfFrame:
    condition: str
    branch_tails: list[list[Tail]]
    saw_else: bool = False


@dataclasses.dataclass
class WhileFrame:
    condition: str


@dataclasses.dataclass
class ForkFrame:
    source_tails: list[Tail]
    branch_tails: list[list[Tail]]


@dataclasses.dataclass
class RepeatFrame:
    entry_tails: list[Tail]
    first_nodes: list[str] = dataclasses.field(default_factory=list)


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


def normalize_label(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\\n", " ")
    text = re.sub(r"[\u2010-\u2015]", "-", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9_+\-*/=<>()?. ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_condition(line: str, keyword: str) -> str | None:
    pattern = rf"^\s*{keyword}\s*\((.*?)\)"
    match = re.search(pattern, line, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _branch_label(line: str) -> str | None:
    match = re.search(r"(?:then|is)?\s*(?:\(([^()]*)\)|\[([^\[\]]*)\])\s*$", line, flags=re.IGNORECASE)
    if not match:
        return None
    value = match.group(1) or match.group(2) or ""
    return normalize_label(value)


def _format_relation(source: str, target: str, kind: str | None = None) -> str:
    relation = f"{source} -> {target}"
    normalized_kind = normalize_label(kind or "")
    if normalized_kind:
        relation += f" [{normalized_kind}]"
    return relation


def _dedupe_preserving_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _parse_relation(text: str) -> RelationParts | None:
    match = re.match(r"^(.*?)\s+->\s+(.*?)(?:\s+\[([^\[\]]*)\])?$", text)
    if not match:
        return None
    source = normalize_label(match.group(1))
    target = normalize_label(match.group(2))
    kind = normalize_label(match.group(3) or "")
    if not source or not target:
        return None
    return RelationParts(source=source, target=target, kind=kind)


_PLANTUML_ARROW_PATTERN = r"(?:-+(?:\[[^\]]+\]|left|right|up|down|[#A-Za-z0-9_,]+)*-*>)|(?:=+>)"
_TRANSITION_STATEMENT_RE = re.compile(
    rf"^\s*(?P<source>.+?)\s*(?P<arrow>{_PLANTUML_ARROW_PATTERN})\s*(?P<target>.+?)\s*$",
    flags=re.IGNORECASE,
)
_SHORTHAND_ARROW_RE = re.compile(
    rf"^\s*(?P<arrow>{_PLANTUML_ARROW_PATTERN})\s*(?P<label>.*?)\s*;?\s*$",
    flags=re.IGNORECASE,
)


def _strip_statement_suffix(text: str) -> str:
    return text.strip().rstrip(";").strip()


def _split_transition_target_label(text: str) -> tuple[str, str]:
    value = _strip_statement_suffix(text)
    if ":" not in value:
        return value, ""
    target, label = value.split(":", 1)
    return target.strip(), label.strip()


def _parse_transition_statement(line: str) -> RelationParts | None:
    match = _TRANSITION_STATEMENT_RE.match(line)
    if not match:
        return None
    target, label = _split_transition_target_label(match.group("target"))
    source = normalize_label(match.group("source"))
    target = normalize_label(target)
    label = normalize_label(label)
    if not source or not target:
        return None
    return RelationParts(source=source, target=target, kind=label)


def _parse_shorthand_arrow_label(line: str) -> str | None:
    match = _SHORTHAND_ARROW_RE.match(line)
    if not match:
        return None
    label = normalize_label(_strip_statement_suffix(match.group("label")))
    return label or None


def _relation_type(kind: str) -> str:
    normalized = normalize_label(kind)
    if not normalized:
        return "sequential"
    if normalized.startswith("fork") or normalized.startswith("split"):
        return "fork"
    if normalized == "loop":
        return "loop"
    return "conditional"


def _compatible_relation_type(gold_kind: str, pred_kind: str) -> bool:
    return _relation_type(gold_kind) == _relation_type(pred_kind)


def _starts_new_plantuml_statement(line: str) -> bool:
    lower = line.strip().lower()
    if not lower:
        return False
    if lower.startswith(":"):
        return True
    if lower.startswith("@") or lower.startswith("'") or lower.startswith("//"):
        return True
    prefixes = (
        "if",
        "else",
        "elseif",
        "endif",
        "end if",
        "switch",
        "case",
        "endswitch",
        "while",
        "endwhile",
        "repeat",
        "fork",
        "fork again",
        "end fork",
        "fork end",
        "endfork",
        "split",
        "split again",
        "end split",
        "split end",
        "endsplit",
        "partition",
        "group",
        "state",
        "title",
        "skinparam",
        "note",
        "end note",
        "start",
        "stop",
        "end",
        "}",
    )
    return (
        _parse_shorthand_arrow_label(line) is not None
        or any(lower == prefix or lower.startswith(prefix + " ") or lower.startswith(prefix + "(") for prefix in prefixes)
    )


def _logical_plantuml_lines(code: str) -> list[str]:
    logical: list[str] = []
    pending_action: list[str] | None = None

    def flush_pending_action() -> None:
        nonlocal pending_action
        if pending_action is None:
            return
        label = " ".join(part.strip() for part in pending_action if part.strip()).strip()
        if label:
            logical.append(f":{label};")
        pending_action = None

    for raw_line in code.splitlines():
        line = raw_line.strip()
        if pending_action is not None:
            if not line:
                continue
            if _starts_new_plantuml_statement(line):
                flush_pending_action()
            else:
                if ";" in line:
                    pending_action.append(line[: line.rfind(";")])
                    flush_pending_action()
                else:
                    pending_action.append(line)
                continue

        if line.startswith(":"):
            content = line[1:].strip()
            if ";" in content:
                logical.append(f":{content[: content.rfind(';')].strip()};")
            else:
                pending_action = [content]
            continue

        logical.append(line)

    flush_pending_action()
    return logical


def extract_activity_graph(uml_code: str) -> ActivityGraph:
    code = extract_plantuml(uml_code, wrap_if_needed=True)
    nodes: list[str] = []
    relations: list[str] = []
    current_tails: list[Tail] = []
    stack: list[IfFrame | WhileFrame | ForkFrame | RepeatFrame] = []
    in_note = False

    def add_node(label: str) -> str | None:
        nonlocal current_tails
        normalized = normalize_label(label)
        if not normalized:
            return None
        nodes.append(normalized)
        for source, kind in current_tails:
            if source and source != normalized:
                relations.append(_format_relation(source, normalized, kind))
        for frame in reversed(stack):
            if isinstance(frame, RepeatFrame) and not frame.first_nodes:
                frame.first_nodes.append(normalized)
                break
        current_tails = [(normalized, None)]
        return normalized

    def save_current_branch(frame: IfFrame | ForkFrame) -> None:
        frame.branch_tails.append(list(current_tails))

    def flatten_branch_tails(branches: list[list[Tail]]) -> list[Tail]:
        flattened: list[Tail] = []
        for branch in branches:
            flattened.extend(branch)
        return flattened

    def relabel_current_tails(kind: str) -> None:
        nonlocal current_tails
        if not current_tails:
            return
        current_tails = [(source, kind) for source, _ in current_tails]

    for line in _logical_plantuml_lines(code):
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("'") or lower.startswith("//"):
            continue
        if lower.startswith("note "):
            if ":" not in line:
                in_note = True
            continue
        if in_note:
            if lower == "end note" or lower.startswith("end note"):
                in_note = False
            continue
        if lower.startswith("@") or lower == "start":
            continue
        if lower in {"stop", "end"}:
            current_tails = []
            continue
        if lower.startswith("title ") or lower.startswith("skinparam "):
            continue
        if lower.startswith("partition ") or lower.startswith("group ") or lower == "}":
            continue

        shorthand_label = _parse_shorthand_arrow_label(line)
        if shorthand_label:
            relabel_current_tails(shorthand_label)
            continue

        if line.startswith(":") and ";" in line:
            label = line[1 : line.rfind(";")]
            add_node(label)
            continue

        state_match = re.match(r"^state\s+\"?([^\"{}]+?)\"?(?:\s+as\s+\w+)?\s*$", line, flags=re.IGNORECASE)
        if state_match:
            label = normalize_label(state_match.group(1))
            if label and label not in nodes:
                nodes.append(label)
            continue

        transition = _parse_transition_statement(line)
        if transition:
            if transition.source not in nodes:
                nodes.append(transition.source)
            if transition.target not in nodes:
                nodes.append(transition.target)
            if transition.source != transition.target:
                relations.append(_format_relation(transition.source, transition.target, transition.kind or "transition"))
            current_tails = [(transition.target, None)]
            continue

        if_match = re.match(r"^if\s*\((.*?)\)\s*then\b", line, flags=re.IGNORECASE)
        if if_match:
            condition = add_node(if_match.group(1))
            if condition:
                label = _branch_label(line) or "if yes"
                stack.append(IfFrame(condition=condition, branch_tails=[]))
                current_tails = [(condition, label)]
            continue

        elseif_match = re.match(r"^(?:else\s+if|elseif)\s*\((.*?)\)\s*then\b", line, flags=re.IGNORECASE)
        if elseif_match:
            frame = next((item for item in reversed(stack) if isinstance(item, IfFrame)), None)
            if frame:
                save_current_branch(frame)
                current_tails = [(frame.condition, "else if")]
            condition = add_node(elseif_match.group(1))
            if condition:
                current_tails = [(condition, _branch_label(line) or "if yes")]
            continue

        else_match = re.match(r"^else\b", line, flags=re.IGNORECASE)
        if else_match:
            frame = next((item for item in reversed(stack) if isinstance(item, IfFrame)), None)
            if frame:
                save_current_branch(frame)
                frame.saw_else = True
                current_tails = [(frame.condition, _branch_label(line) or "if no")]
            continue

        if lower in {"endif", "end if"}:
            frame = stack.pop() if stack and isinstance(stack[-1], IfFrame) else None
            if frame:
                save_current_branch(frame)
                if not frame.saw_else:
                    frame.branch_tails.append([(frame.condition, "if no")])
                current_tails = flatten_branch_tails(frame.branch_tails)
            continue

        switch_match = re.match(r"^switch\s*\((.*?)\)", line, flags=re.IGNORECASE)
        if switch_match:
            condition = add_node(switch_match.group(1))
            if condition:
                stack.append(IfFrame(condition=condition, branch_tails=[]))
                current_tails = [(condition, "switch")]
            continue

        case_match = re.match(r"^case\s*\((.*?)\)", line, flags=re.IGNORECASE)
        if case_match:
            frame = next((item for item in reversed(stack) if isinstance(item, IfFrame)), None)
            if frame:
                if current_tails != [(frame.condition, "switch")]:
                    save_current_branch(frame)
                current_tails = [(frame.condition, f"case {normalize_label(case_match.group(1))}")]
            continue

        if lower == "endswitch":
            frame = stack.pop() if stack and isinstance(stack[-1], IfFrame) else None
            if frame:
                save_current_branch(frame)
                current_tails = flatten_branch_tails(frame.branch_tails)
            continue

        while_match = re.match(r"^while\s*\((.*?)\)\s*(?:is\b.*)?$", line, flags=re.IGNORECASE)
        if while_match:
            condition = add_node(while_match.group(1))
            if condition:
                stack.append(WhileFrame(condition=condition))
                current_tails = [(condition, _branch_label(line) or "while yes")]
            continue

        endwhile_match = re.match(r"^endwhile\b", line, flags=re.IGNORECASE)
        if endwhile_match:
            frame = stack.pop() if stack and isinstance(stack[-1], WhileFrame) else None
            if frame:
                for source, _ in current_tails:
                    if source and source != frame.condition:
                        relations.append(_format_relation(source, frame.condition, "loop"))
                current_tails = [(frame.condition, _branch_label(line) or "while no")]
            continue

        if lower == "repeat":
            stack.append(RepeatFrame(entry_tails=list(current_tails)))
            continue

        repeat_match = re.match(r"^repeat\s+while\s*\((.*?)\)", line, flags=re.IGNORECASE)
        if repeat_match:
            frame = stack.pop() if stack and isinstance(stack[-1], RepeatFrame) else None
            condition = add_node(repeat_match.group(1))
            if condition and frame:
                for first_node in frame.first_nodes:
                    if first_node != condition:
                        relations.append(_format_relation(condition, first_node, "loop"))
                current_tails = [(condition, _branch_label(line) or "repeat exit")]
            continue

        if lower in {"fork", "split"}:
            source_tails = [(source, kind or "fork") for source, kind in current_tails]
            stack.append(ForkFrame(source_tails=source_tails, branch_tails=[]))
            current_tails = list(source_tails)
            continue

        if lower in {"fork again", "split again"}:
            frame = next((item for item in reversed(stack) if isinstance(item, ForkFrame)), None)
            if frame:
                save_current_branch(frame)
                current_tails = list(frame.source_tails)
            continue

        if lower in {"end fork", "fork end", "endfork", "end split", "split end", "endsplit"}:
            frame = stack.pop() if stack and isinstance(stack[-1], ForkFrame) else None
            if frame:
                save_current_branch(frame)
                current_tails = flatten_branch_tails(frame.branch_tails)
            continue

        condition = extract_condition(line, "if") or extract_condition(line, "while")
        if condition:
            add_node(condition)

    return ActivityGraph(
        nodes=_dedupe_preserving_order(nodes),
        relations=_dedupe_preserving_order(relations),
    )


def iter_semantic_elements(uml_code: str) -> list[str]:
    return extract_activity_graph(uml_code).nodes


def extract_relations(uml_code: str) -> list[str]:
    return extract_activity_graph(uml_code).relations


def _load_embedding_model(model_name: str) -> Any:
    if model_name in _EMBEDDING_MODELS:
        return _EMBEDDING_MODELS[model_name]
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "LATO-style embedding metrics require sentence-transformers. "
            "Install the project dependencies or run with --metric-matcher difflib for a cheap smoke test."
        ) from exc
    model = SentenceTransformer(model_name)
    _EMBEDDING_MODELS[model_name] = model
    return model


def _embedding_vectors(texts: list[str], model_name: str) -> list[list[float]]:
    missing = [text for text in dict.fromkeys(texts) if (model_name, text) not in _EMBEDDING_CACHE]
    if missing:
        model = _load_embedding_model(model_name)
        embeddings = model.encode(missing, normalize_embeddings=True, show_progress_bar=False)
        for text, embedding in zip(missing, embeddings):
            _EMBEDDING_CACHE[(model_name, text)] = [float(value) for value in embedding]
    return [_EMBEDDING_CACHE[(model_name, text)] for text in texts]


def _dot(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def _exact_matches(gold_items: list[str], pred_items: list[str]) -> tuple[set[int], set[int], list[dict[str, Any]]]:
    matched_gold: set[int] = set()
    matched_pred: set[int] = set()
    matches: list[dict[str, Any]] = []
    for gi, gold in enumerate(gold_items):
        for pi, pred in enumerate(pred_items):
            if pi in matched_pred or gold != pred:
                continue
            matched_gold.add(gi)
            matched_pred.add(pi)
            matches.append({"gold": gold, "pred": pred, "score": 1.0, "method": "exact"})
            break
    return matched_gold, matched_pred, matches


def _semantic_match(
    gold_items: list[str],
    pred_items: list[str],
    *,
    threshold: float,
    model_name: str,
) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    matched_gold, matched_pred, matches = _exact_matches(gold_items, pred_items)
    remaining_gold = [(idx, item) for idx, item in enumerate(gold_items) if idx not in matched_gold]
    remaining_pred = [(idx, item) for idx, item in enumerate(pred_items) if idx not in matched_pred]
    if remaining_gold and remaining_pred:
        gold_vectors = _embedding_vectors([item for _, item in remaining_gold], model_name)
        pred_vectors = _embedding_vectors([item for _, item in remaining_pred], model_name)
        candidates: list[tuple[float, int, int, str, str]] = []
        for local_gi, (gold_idx, gold) in enumerate(remaining_gold):
            for local_pi, (pred_idx, pred) in enumerate(remaining_pred):
                score = _dot(gold_vectors[local_gi], pred_vectors[local_pi])
                if score >= threshold:
                    candidates.append((score, gold_idx, pred_idx, gold, pred))
        for score, gold_idx, pred_idx, gold, pred in sorted(candidates, reverse=True):
            if gold_idx in matched_gold or pred_idx in matched_pred:
                continue
            matched_gold.add(gold_idx)
            matched_pred.add(pred_idx)
            matches.append({"gold": gold, "pred": pred, "score": round(score, 4), "method": "embedding"})

    missing = [item for idx, item in enumerate(gold_items) if idx not in matched_gold]
    extra = [item for idx, item in enumerate(pred_items) if idx not in matched_pred]
    return len(matches), missing, extra, matches


def _structured_relation_match(
    gold_items: list[str],
    pred_items: list[str],
    *,
    threshold: float,
    model_name: str,
) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    matched_gold, matched_pred, matches = _exact_matches(gold_items, pred_items)
    parsed_gold = {idx: _parse_relation(item) for idx, item in enumerate(gold_items)}
    parsed_pred = {idx: _parse_relation(item) for idx, item in enumerate(pred_items)}
    remaining_gold = [(idx, item, parsed_gold[idx]) for idx, item in enumerate(gold_items) if idx not in matched_gold and parsed_gold[idx]]
    remaining_pred = [(idx, item, parsed_pred[idx]) for idx, item in enumerate(pred_items) if idx not in matched_pred and parsed_pred[idx]]

    if remaining_gold and remaining_pred:
        gold_text_vectors = _embedding_vectors([item for _, item, _ in remaining_gold], model_name)
        pred_text_vectors = _embedding_vectors([item for _, item, _ in remaining_pred], model_name)
        endpoint_texts = []
        for _, _, relation in remaining_gold:
            endpoint_texts.extend([relation.source, relation.target])
        for _, _, relation in remaining_pred:
            endpoint_texts.extend([relation.source, relation.target])
        _embedding_vectors(endpoint_texts, model_name)

        candidates: list[tuple[float, int, int, str, str, str, float | None, float | None]] = []
        for local_gi, (gold_idx, gold_text, gold_relation) in enumerate(remaining_gold):
            for local_pi, (pred_idx, pred_text, pred_relation) in enumerate(remaining_pred):
                whole_score = _dot(gold_text_vectors[local_gi], pred_text_vectors[local_pi])
                if whole_score >= threshold:
                    candidates.append((whole_score, gold_idx, pred_idx, gold_text, pred_text, "embedding", None, None))

                if not _compatible_relation_type(gold_relation.kind, pred_relation.kind):
                    continue
                source_score = _dot(
                    _embedding_vectors([gold_relation.source], model_name)[0],
                    _embedding_vectors([pred_relation.source], model_name)[0],
                )
                target_score = _dot(
                    _embedding_vectors([gold_relation.target], model_name)[0],
                    _embedding_vectors([pred_relation.target], model_name)[0],
                )
                if source_score >= threshold and target_score >= threshold:
                    score = min(source_score, target_score)
                    candidates.append((score, gold_idx, pred_idx, gold_text, pred_text, "structured_embedding", source_score, target_score))

        for score, gold_idx, pred_idx, gold_text, pred_text, method, source_score, target_score in sorted(candidates, reverse=True):
            if gold_idx in matched_gold or pred_idx in matched_pred:
                continue
            matched_gold.add(gold_idx)
            matched_pred.add(pred_idx)
            match = {
                "gold": gold_text,
                "pred": pred_text,
                "score": round(score, 4),
                "method": method,
            }
            if source_score is not None and target_score is not None:
                match["source_score"] = round(source_score, 4)
                match["target_score"] = round(target_score, 4)
            matches.append(match)

    missing = [item for idx, item in enumerate(gold_items) if idx not in matched_gold]
    extra = [item for idx, item in enumerate(pred_items) if idx not in matched_pred]
    return len(matches), missing, extra, matches


def _difflib_match(
    gold_items: list[str],
    pred_items: list[str],
    *,
    threshold: float,
) -> tuple[int, list[str], list[str], list[dict[str, Any]]]:
    matched_gold, matched_pred, matches = _exact_matches(gold_items, pred_items)
    candidates: list[tuple[float, int, int]] = []
    for gi, gold in enumerate(gold_items):
        if gi in matched_gold:
            continue
        for pi, pred in enumerate(pred_items):
            if pi in matched_pred:
                continue
            score = difflib.SequenceMatcher(None, gold, pred).ratio()
            if score >= threshold:
                candidates.append((score, gi, pi))
    for score, gi, pi in sorted(candidates, reverse=True):
        if gi in matched_gold or pi in matched_pred:
            continue
        matched_gold.add(gi)
        matched_pred.add(pi)
        matches.append({"gold": gold_items[gi], "pred": pred_items[pi], "score": round(score, 4), "method": "difflib"})
    missing = [item for idx, item in enumerate(gold_items) if idx not in matched_gold]
    extra = [item for idx, item in enumerate(pred_items) if idx not in matched_pred]
    return len(matches), missing, extra, matches


def compute_metric(
    gold_items: list[str],
    pred_items: list[str],
    threshold: float,
    *,
    matcher: str = "embedding",
    embedding_model: str = DEFAULT_EMBEDDING_MODEL,
    item_type: str = "node",
) -> MetricBundle:
    if not gold_items and not pred_items:
        return MetricBundle(1.0, 1.0, 1.0, [], [], 0, 0, 0, [], matcher)
    metric_matcher = matcher
    if matcher == "embedding" and item_type == "relation":
        correct, missing, extra, matches = _structured_relation_match(
            gold_items,
            pred_items,
            threshold=threshold,
            model_name=embedding_model,
        )
        metric_matcher = "structured_embedding"
    elif matcher == "embedding":
        correct, missing, extra, matches = _semantic_match(
            gold_items,
            pred_items,
            threshold=threshold,
            model_name=embedding_model,
        )
    elif matcher == "difflib":
        correct, missing, extra, matches = _difflib_match(gold_items, pred_items, threshold=threshold)
    else:
        raise ValueError(f"Unsupported metric matcher: {matcher}")
    precision = correct / len(pred_items) if pred_items else 0.0
    recall = correct / len(gold_items) if gold_items else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return MetricBundle(
        precision=precision,
        recall=recall,
        f1=f1,
        missing=missing[:20],
        extra=extra[:20],
        correct=correct,
        gold_count=len(gold_items),
        pred_count=len(pred_items),
        matches=matches[:20],
        matcher=metric_matcher,
    )


def classify_failures(syntax: SyntaxResult, node_metrics: MetricBundle, relation_metrics: MetricBundle) -> list[str]:
    failures: list[str] = []
    if not syntax.passed:
        failures.append("syntax_error")
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


def avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def harmonic_f1(precision: float, recall: float) -> float:
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def summarize_records(records: list[EvaluationRecord]) -> dict[str, float]:
    llm_records = [r.llm_element_metrics for r in records if r.llm_element_metrics.enabled]
    llm_success = [m for m in llm_records if m.status == "success"]
    node_precision = avg([r.node_metrics.precision for r in records])
    node_recall = avg([r.node_metrics.recall for r in records])
    relation_precision = avg([r.relation_metrics.precision for r in records])
    relation_recall = avg([r.relation_metrics.recall for r in records])
    return {
        "count": float(len(records)),
        "infrastructure_error_rate": avg([1.0 if "infrastructure_error" in r.failure_types else 0.0 for r in records]),
        "node_precision": node_precision,
        "node_recall": node_recall,
        "node_f1": harmonic_f1(node_precision, node_recall),
        "relation_precision": relation_precision,
        "relation_recall": relation_recall,
        "relation_f1": harmonic_f1(relation_precision, relation_recall),
        "plantuml_compilation_pass_rate": avg([1.0 if r.plantuml_compilation.passed else 0.0 for r in records]),
        "llm_element_evaluated": float(len(llm_success)),
        "llm_element_failed": float(len(llm_records) - len(llm_success)),
        "llm_node_precision": avg([m.node_metrics.precision for m in llm_success]),
        "llm_node_recall": avg([m.node_metrics.recall for m in llm_success]),
        "llm_node_f1": avg([m.node_metrics.f1 for m in llm_success]),
        "llm_relation_precision": avg([m.relation_metrics.precision for m in llm_success]),
        "llm_relation_recall": avg([m.relation_metrics.recall for m in llm_success]),
        "llm_relation_f1": avg([m.relation_metrics.f1 for m in llm_success]),
    }


def format_summary(summary: dict[str, float]) -> str:
    text = (
        f"count={int(summary['count'])}, "
        f"plantuml_compile={summary['plantuml_compilation_pass_rate']:.1%}, "
        f"N-F1={summary['node_f1']:.3f}, "
        f"R-F1={summary['relation_f1']:.3f}"
    )
    if summary.get("llm_element_evaluated", 0.0) > 0:
        text += (
            f", LLM-N-F1={summary['llm_node_f1']:.3f}, "
            f"LLM-R-F1={summary['llm_relation_f1']:.3f}"
        )
    return text
