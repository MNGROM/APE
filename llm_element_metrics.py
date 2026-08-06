"""APE semantic element metrics for PlantUML activity diagrams.

* compilation pass rate via ``plantuml.jar -syntax``;
* element-level LLM-as-judge node/relation precision, recall, and F1.
"""

from __future__ import annotations

import json
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from llm import should_send_sampling_control
from utils.rate_limit import ProviderHTTPError, call_with_provider_retries


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
    "Your task is to extract behavioral elements (nodes and relations) from the given code.\n\n"
    'A "node" is an atomic activity, action, or state - a named behavioral unit that appears in the model.\n'
    'A "relation" is a control-flow connection between nodes, including: '
    "sequential flow, conditional branch, loop, fork/parallel, merge/join, and transition.\n\n"
    "You must output valid JSON and nothing else."
)

EXTRACTION_USER_PLANTUML = (
    "Analyze the following PlantUML activity diagram code and extract all behavioral elements.\n\n"
    "Code:\n{code}\n\n"
    "Extract two categories:\n"
    '1. **nodes**: Each atomic activity/action (the text inside `:...;` blocks), '
    "start/stop markers, and any named decision points.\n"
    "2. **relations**: Each control-flow relationship between nodes. For each relation, identify:\n"
    '   - "from": the source node name\n'
    '   - "to": the target node name\n'
    '   - "type": one of "sequential", "conditional", "loop", "fork", "merge"\n'
    '   - "condition": the condition label if applicable, otherwise null\n\n'
    "Output ONLY a JSON object in this exact format:\n"
    "{{\n"
    '  "nodes": ["node1", "node2", "..."],\n'
    '  "relations": [\n'
    '    {{"from": "node1", "to": "node2", "type": "sequential", "condition": null}}\n'
    "  ]\n"
    "}}"
)

MATCHING_SYSTEM_PROMPT = (
    "You are an expert in comparing behavioral model elements. "
    "Your task is to compare extracted elements from a prediction against a ground truth reference "
    "and classify each element as a true positive (TP), false positive (FP), or false negative (FN).\n\n"
    "Two nodes match if they refer to the same activity/action/state, even if worded slightly differently "
    '(e.g., "user login" matches "user log in", "Verify account" matches "Account verification").\n\n'
    "Two relations match if they connect semantically equivalent node pairs with the same relationship type, "
    "even if the exact wording differs slightly.\n\n"
    "You must output valid JSON and nothing else."
)

MATCHING_USER_PROMPT = (
    "Compare the following extracted behavioral elements from a prediction against the ground truth.\n\n"
    "Ground Truth Elements:\n{gt_json}\n\n"
    "Prediction Elements:\n{pred_json}\n\n"
    "For NODES, determine:\n"
    "- TP: nodes in prediction that have a semantic match in ground truth\n"
    "- FP: nodes in prediction with NO match in ground truth\n"
    "- FN: nodes in ground truth with NO match in prediction\n\n"
    "For RELATIONS, determine:\n"
    "- TP: relations in prediction that match a ground truth relation (same source-target pair semantically, same type)\n"
    "- FP: relations in prediction with NO match in ground truth\n"
    "- FN: relations in ground truth with NO match in prediction\n\n"
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
    stripped = (code or "").strip()
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
    """Check PlantUML syntax with the local APE compilation metric."""

    if not plantuml_jar.exists():
        return CompilationResult(False, [f"PlantUML jar not found: {plantuml_jar}"])
    if not strip_markdown_fences(code).strip():
        return CompilationResult(False, ["No PlantUML content to compile."])

    try:
        proc = subprocess.run(
            ["java", "-Djava.awt.headless=true", "-jar", str(plantuml_jar), "-syntax"],
            input=ensure_plantuml_wrappers(code),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError:
        return CompilationResult(False, ["Java executable not found."])
    except subprocess.TimeoutExpired:
        return CompilationResult(False, ["PlantUML syntax check timed out."])

    errors: list[str] = []
    for is_stderr, stream in ((False, proc.stdout or ""), (True, proc.stderr or "")):
        for line in stream.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if re.match(r"^(ERROR|SyntaxError|Exception)", stripped, re.IGNORECASE):
                errors.append(stripped)
            elif " line " in stripped and " :" in stripped:
                errors.append(stripped)
            elif is_stderr:
                errors.append(stripped)
    if proc.returncode != 0 and not errors:
        errors.append(f"PlantUML exited with return code {proc.returncode}")
    return CompilationResult(not errors, errors)


def parse_json_response(text: str) -> Any | None:
    """Extract JSON from LLM output, handling markdown fences and surrounding noise."""

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


def normalize_base_url(base_url: str) -> str:
    value = (base_url or "https://open.bigmodel.cn/api/paas/v4/").strip().rstrip("/")
    suffix = "/chat/completions"
    if value.endswith(suffix):
        value = value[: -len(suffix)]
    return value + "/"


def _clean_optional_body_fields(body: dict[str, Any], error: BaseException) -> dict[str, Any] | None:
    lowered = str(error).lower()
    cleaned = dict(body)
    changed = False
    for field in ("thinking", "max_tokens"):
        if field in cleaned and field in lowered:
            cleaned.pop(field, None)
            changed = True
    return cleaned if changed else None


def post_chat_completion(*, endpoint: str, body: dict[str, Any], api_key: str, timeout: int) -> str:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
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
        raise ProviderHTTPError("APE element-level judge", exc.code, error_body, dict(exc.headers.items())) from exc

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
    do_sample: bool | None = False,
    state_dir: Path | None = None,
    retry_phase: str = "llm_element_judge",
    retry_context: dict[str, Any] | None = None,
    provider_max_retries: int = 20,
    retry_initial_wait: int = 30,
    retry_max_wait: int = 600,
) -> str:
    """Call an OpenAI-compatible chat endpoint with APE's provider retry layer."""

    if float(temperature) != 0.0:
        raise ValueError("LLM temperature must be 0")
    if not api_key:
        raise RuntimeError("LLM judge API key is required when semantic element metrics are enabled")

    body: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }
    if should_send_sampling_control(base_url, do_sample):
        body["do_sample"] = do_sample
    if thinking:
        body["thinking"] = {"type": thinking}

    endpoint = normalize_base_url(base_url) + "chat/completions"

    def call(current_body: dict[str, Any], phase: str) -> str:
        return call_with_provider_retries(
            lambda: post_chat_completion(endpoint=endpoint, body=current_body, api_key=api_key, timeout=timeout),
            phase=phase,
            state_dir=state_dir,
            context=retry_context,
            max_retries=provider_max_retries,
            initial_wait=retry_initial_wait,
            max_wait=retry_max_wait,
        )

    try:
        return call(body, retry_phase)
    except RuntimeError as exc:
        cleaned = _clean_optional_body_fields(body, exc)
        if cleaned is None:
            raise
        return call(cleaned, f"{retry_phase}:openai_compat")


def _valid_extraction(result: Any) -> bool:
    return isinstance(result, dict) and isinstance(result.get("nodes"), list) and isinstance(result.get("relations"), list)


def _valid_matching(result: Any) -> bool:
    return isinstance(result, dict) and isinstance(result.get("nodes"), dict) and isinstance(result.get("relations"), dict)


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
    do_sample: bool | None,
    max_retries: int,
    state_dir: Path | None,
    retry_phase: str,
    retry_context: dict[str, Any],
    provider_max_retries: int,
    retry_initial_wait: int,
    retry_max_wait: int,
) -> dict[str, Any]:
    messages = [
        {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
        {"role": "user", "content": EXTRACTION_USER_PLANTUML.format(code=strip_markdown_fences(code))},
    ]
    for attempt in range(1, max(1, max_retries) + 1):
        raw = judge_chat(
            messages=messages,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            thinking=thinking,
            do_sample=do_sample,
            state_dir=state_dir,
            retry_phase=f"{retry_phase}:extract",
            retry_context={**retry_context, "json_retry_attempt": attempt},
            provider_max_retries=provider_max_retries,
            retry_initial_wait=retry_initial_wait,
            retry_max_wait=retry_max_wait,
        )
        result = parse_json_response(raw)
        if _valid_extraction(result):
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
    do_sample: bool | None,
    max_retries: int,
    state_dir: Path | None,
    retry_phase: str,
    retry_context: dict[str, Any],
    provider_max_retries: int,
    retry_initial_wait: int,
    retry_max_wait: int,
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
    for attempt in range(1, max(1, max_retries) + 1):
        raw = judge_chat(
            messages=messages,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            thinking=thinking,
            do_sample=do_sample,
            state_dir=state_dir,
            retry_phase=f"{retry_phase}:match",
            retry_context={**retry_context, "json_retry_attempt": attempt},
            provider_max_retries=provider_max_retries,
            retry_initial_wait=retry_initial_wait,
            retry_max_wait=retry_max_wait,
        )
        result = parse_json_response(raw)
        if _valid_matching(result):
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


def error_llm_metrics(error: str) -> LLMElementMetrics:
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
        error=error,
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
    do_sample: bool | None = False,
    max_retries: int = 3,
    state_dir: Path | None = None,
    retry_phase: str = "llm_element_judge",
    retry_context: dict[str, Any] | None = None,
    provider_max_retries: int = 20,
    retry_initial_wait: int = 30,
    retry_max_wait: int = 600,
) -> LLMElementMetrics:
    """Evaluate one sample using APE's element-level LLM judge."""

    if not enabled:
        return disabled_llm_metrics()

    retry_context = retry_context or {}
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
            do_sample=do_sample,
            max_retries=max_retries,
            state_dir=state_dir,
            retry_phase=retry_phase,
            retry_context={**retry_context, "judge_step": "gt_extract"},
            provider_max_retries=provider_max_retries,
            retry_initial_wait=retry_initial_wait,
            retry_max_wait=retry_max_wait,
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
            do_sample=do_sample,
            max_retries=max_retries,
            state_dir=state_dir,
            retry_phase=retry_phase,
            retry_context={**retry_context, "judge_step": "pred_extract"},
            provider_max_retries=provider_max_retries,
            retry_initial_wait=retry_initial_wait,
            retry_max_wait=retry_max_wait,
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
            do_sample=do_sample,
            max_retries=max_retries,
            state_dir=state_dir,
            retry_phase=retry_phase,
            retry_context={**retry_context, "judge_step": "match"},
            provider_max_retries=provider_max_retries,
            retry_initial_wait=retry_initial_wait,
            retry_max_wait=retry_max_wait,
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
        return error_llm_metrics(str(exc))
