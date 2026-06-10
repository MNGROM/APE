"""HiGenModel-style auxiliary metrics for PlantUML activity diagrams."""

from __future__ import annotations

import json
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class CompilationResult:
    passed: bool
    errors: list[str]


@dataclass
class PRF:
    precision: float
    recall: float
    f1: float


@dataclass
class LLMElementMetrics:
    enabled: bool
    status: str
    node_metrics: PRF
    relation_metrics: PRF
    gt_elements: dict[str, Any]
    pred_elements: dict[str, Any]
    matching: dict[str, Any]
    counts: dict[str, int]
    error: str | None = None


EXTRACTION_SYSTEM_PROMPT = (
    "You are an expert in analyzing behavioral modeling code. "
    "Your task is to extract behavioral elements, nodes and relations, from the given code.\n\n"
    "A node is an atomic activity, action, state, start/stop marker, or named decision point.\n"
    "A relation is a control-flow connection between nodes, including sequential flow, "
    "conditional branch, loop, fork/parallel, merge/join, and transition.\n\n"
    "You must output valid JSON and nothing else."
)

EXTRACTION_USER_PLANTUML = (
    "Analyze the following PlantUML activity diagram code and extract all behavioral elements.\n\n"
    "Code:\n{code}\n\n"
    "Extract two categories:\n"
    "1. nodes: each atomic activity/action, start/stop marker, and any named decision point.\n"
    "2. relations: each control-flow relationship between nodes. For each relation, identify:\n"
    '- "from": the source node name\n'
    '- "to": the target node name\n'
    '- "type": one of "sequential", "conditional", "loop", "fork", "merge"\n'
    '- "condition": the condition label if applicable, otherwise null\n\n'
    "Output ONLY a JSON object in this exact format:\n"
    "{{\n"
    '  "nodes": ["node1", "node2"],\n'
    '  "relations": [\n'
    '    {{"from": "node1", "to": "node2", "type": "sequential", "condition": null}}\n'
    "  ]\n"
    "}}"
)

MATCHING_SYSTEM_PROMPT = (
    "You are an expert in comparing behavioral model elements. "
    "Compare extracted elements from a prediction against a ground truth reference and classify "
    "each element as true positive, false positive, or false negative.\n\n"
    "Two nodes match if they refer to the same activity/action/state, even if worded differently. "
    "Two relations match if they connect semantically equivalent node pairs with the same relationship type.\n\n"
    "You must output valid JSON and nothing else."
)

MATCHING_USER_PROMPT = (
    "Compare the following extracted behavioral elements from a prediction against the ground truth.\n\n"
    "Ground Truth Elements:\n{gt_json}\n\n"
    "Prediction Elements:\n{pred_json}\n\n"
    "For nodes, determine TP, FP, and FN.\n"
    "For relations, determine TP, FP, and FN.\n\n"
    "Output ONLY a JSON object in this exact format:\n"
    "{{\n"
    '  "nodes": {{\n'
    '    "tp": [{{"pred": "pred_node", "gt": "gt_node"}}],\n'
    '    "fp": ["pred_node_with_no_match"],\n'
    '    "fn": ["gt_node_with_no_match"]\n'
    "  }},\n"
    '  "relations": {{\n'
    '    "tp": [{{"pred": {{"from": "a", "to": "b", "type": "t"}}, "gt": {{"from": "c", "to": "d", "type": "t"}}}}],\n'
    '    "fp": [{{"from": "a", "to": "b", "type": "t"}}],\n'
    '    "fn": [{{"from": "c", "to": "d", "type": "t"}}]\n'
    "  }}\n"
    "}}"
)


def strip_markdown_fences(code: str) -> str:
    stripped = code.strip()
    match = re.match(r"^```(?:\w+)?\s*\n?(.*?)\n?```\s*$", stripped, flags=re.DOTALL)
    if match:
        return match.group(1).strip()
    return stripped


def ensure_plantuml_wrappers(code: str) -> str:
    full_code = strip_markdown_fences(code)
    if not full_code.startswith("@startuml"):
        full_code = "@startuml\n" + full_code
    if not full_code.rstrip().endswith("@enduml"):
        full_code = full_code + "\n@enduml"
    return full_code


def check_plantuml_compilation(code: str, plantuml_jar: Path, timeout: int = 30) -> CompilationResult:
    if not plantuml_jar.exists():
        return CompilationResult(False, [f"PlantUML jar not found: {plantuml_jar}"])
    if not strip_markdown_fences(code).strip():
        return CompilationResult(False, ["No PlantUML content to compile."])

    full_code = ensure_plantuml_wrappers(code)
    try:
        proc = subprocess.run(
            ["java", "-Djava.awt.headless=true", "-jar", str(plantuml_jar), "-syntax"],
            input=full_code,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return CompilationResult(False, ["Java executable not found."])
    except subprocess.TimeoutExpired:
        return CompilationResult(False, ["PlantUML syntax check timed out."])

    errors: list[str] = []
    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    for line in output.splitlines():
        stripped = line.strip()
        if re.match(r"^(ERROR|SyntaxError|Exception)", stripped, re.IGNORECASE):
            errors.append(stripped)
        elif " line " in stripped and " :" in stripped:
            errors.append(stripped)
    if proc.returncode != 0 and not errors:
        errors.append(f"PlantUML exited with return code {proc.returncode}")
    return CompilationResult(not errors, errors)


def normalize_base_url(base_url: str) -> str:
    value = (base_url or "https://open.bigmodel.cn/api/paas/v4/").strip().rstrip("/")
    suffix = "/chat/completions"
    if value.endswith(suffix):
        value = value[: -len(suffix)]
    return value + "/"


def parse_json_response(text: str) -> Any | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            pass
    return None


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
        raise RuntimeError(f"LLM judge HTTP {exc.code}: {error_body[:1000]}") from exc

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected LLM judge response: {json.dumps(payload, ensure_ascii=False)[:1000]}") from exc
    return str(content or "").strip()


def judge_chat(
    *,
    messages: list[dict[str, str]],
    model: str,
    api_key: str,
    base_url: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
    thinking: str,
) -> str:
    if not api_key:
        raise RuntimeError("LLM judge API key is required when HiGen LLM metrics are enabled")

    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if thinking:
        body["thinking"] = {"type": thinking}
    endpoint = normalize_base_url(base_url) + "chat/completions"
    try:
        return post_chat_completion(endpoint=endpoint, body=body, api_key=api_key, timeout=timeout)
    except RuntimeError as exc:
        if "thinking" not in body or "thinking" not in str(exc).lower():
            raise
        retry_body = {key: value for key, value in body.items() if key != "thinking"}
        return post_chat_completion(endpoint=endpoint, body=retry_body, api_key=api_key, timeout=timeout)


def extract_elements(
    *,
    code: str,
    model: str,
    api_key: str,
    base_url: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
    thinking: str,
    max_retries: int,
) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": EXTRACTION_USER_PLANTUML.format(code=code)},
    ]
    for _ in range(max_retries):
        raw = judge_chat(
            messages=messages,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            thinking=thinking,
        )
        result = parse_json_response(raw)
        if isinstance(result, dict) and isinstance(result.get("nodes"), list) and isinstance(result.get("relations"), list):
            return result
    return {"nodes": [], "relations": []}


def match_elements(
    *,
    gt_elements: dict[str, Any],
    pred_elements: dict[str, Any],
    model: str,
    api_key: str,
    base_url: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
    thinking: str,
    max_retries: int,
) -> dict[str, Any]:
    empty = {
        "nodes": {"tp": [], "fp": pred_elements.get("nodes", []), "fn": gt_elements.get("nodes", [])},
        "relations": {"tp": [], "fp": pred_elements.get("relations", []), "fn": gt_elements.get("relations", [])},
    }
    messages = [
        {"role": "system", "content": MATCHING_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": MATCHING_USER_PROMPT.format(
                gt_json=json.dumps(gt_elements, ensure_ascii=False, indent=2),
                pred_json=json.dumps(pred_elements, ensure_ascii=False, indent=2),
            ),
        },
    ]
    for _ in range(max_retries):
        raw = judge_chat(
            messages=messages,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            thinking=thinking,
        )
        result = parse_json_response(raw)
        if isinstance(result, dict) and isinstance(result.get("nodes"), dict) and isinstance(result.get("relations"), dict):
            return result
    return empty


def compute_prf(tp: int, fp: int, fn: int) -> PRF:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall > 0 else 0.0
    return PRF(round(precision, 4), round(recall, 4), round(f1, 4))


def disabled_llm_metrics() -> LLMElementMetrics:
    zero = PRF(0.0, 0.0, 0.0)
    return LLMElementMetrics(
        enabled=False,
        status="disabled",
        node_metrics=zero,
        relation_metrics=zero,
        gt_elements={},
        pred_elements={},
        matching={},
        counts={},
    )


def evaluate_llm_elements(
    *,
    ground_truth: str,
    prediction: str,
    enabled: bool,
    model: str,
    api_key: str,
    base_url: str,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    timeout: int = 300,
    thinking: str = "disabled",
    max_retries: int = 3,
) -> LLMElementMetrics:
    if not enabled:
        return disabled_llm_metrics()

    try:
        gt_elements = extract_elements(
            code=ground_truth,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            thinking=thinking,
            max_retries=max_retries,
        )
        pred_elements = extract_elements(
            code=prediction,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            thinking=thinking,
            max_retries=max_retries,
        )
        matching = match_elements(
            gt_elements=gt_elements,
            pred_elements=pred_elements,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            thinking=thinking,
            max_retries=max_retries,
        )

        node_tp = len(matching.get("nodes", {}).get("tp", []))
        node_fp = len(matching.get("nodes", {}).get("fp", []))
        node_fn = len(matching.get("nodes", {}).get("fn", []))
        relation_tp = len(matching.get("relations", {}).get("tp", []))
        relation_fp = len(matching.get("relations", {}).get("fp", []))
        relation_fn = len(matching.get("relations", {}).get("fn", []))
        return LLMElementMetrics(
            enabled=True,
            status="success",
            node_metrics=compute_prf(node_tp, node_fp, node_fn),
            relation_metrics=compute_prf(relation_tp, relation_fp, relation_fn),
            gt_elements=gt_elements,
            pred_elements=pred_elements,
            matching=matching,
            counts={
                "node_tp": node_tp,
                "node_fp": node_fp,
                "node_fn": node_fn,
                "relation_tp": relation_tp,
                "relation_fp": relation_fp,
                "relation_fn": relation_fn,
            },
        )
    except Exception as exc:
        zero = PRF(0.0, 0.0, 0.0)
        return LLMElementMetrics(
            enabled=True,
            status="error",
            node_metrics=zero,
            relation_metrics=zero,
            gt_elements={},
            pred_elements={},
            matching={},
            counts={},
            error=str(exc),
        )
