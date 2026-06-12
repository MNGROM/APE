#!/usr/bin/env python3
"""Prompt evolution loop for UML activity-diagram PlantUML generation.

This is a prompt-level adaptation of the AHE loop:

evaluate -> analyze -> improve

Each run copies the seed prompt into its own `work.md` under `prompt_runs/` and
only evolves that run-local file. The seed prompt is never overwritten. The
normal mode uses a leave-one-dataset-out setup, and train-only mode can be used
to quickly optimize on a few rows from a single dataset without testing.
"""

from __future__ import annotations

import argparse
import dataclasses
import difflib
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - python-dotenv is optional for direct script use.
    load_dotenv = None

from evaluators.llm_element_metrics import (
    CompilationResult,
    LLMElementMetrics,
    check_plantuml_compilation,
    evaluate_llm_elements,
)
from utils.rate_limit import ProviderHTTPError, call_with_provider_retries


PROJECT_DIR = Path(__file__).resolve().parent
if load_dotenv is not None:
    load_dotenv(PROJECT_DIR / ".env", override=False)

DEFAULT_DATASETS_DIR = PROJECT_DIR / "prompt_datasets" / "lato"
DEFAULT_PROMPT_PATH = PROJECT_DIR / "prompt_workspace" / "tst.md"
DEFAULT_FAILURE_ANALYSIS_PROMPT_PATH = PROJECT_DIR / "prompt_workspace" / "failure_analysis.md"
DEFAULT_PROMPT_EDITOR_PROMPT_PATH = PROJECT_DIR / "prompt_workspace" / "prompt_editor.md"
DEFAULT_RUNS_DIR = PROJECT_DIR / "prompt_runs"
DEFAULT_PLANTUML_JAR = PROJECT_DIR / "tools" / "plantuml" / "plantuml-1.2025.4.jar"
DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
DEFAULT_MODEL = "glm-5.1"
DEFAULT_LLM_TIMEOUT = 300
DEFAULT_THINKING_TYPE = "disabled"
REQUIRED_PROMPT_HEADINGS = (
    "## agent task",
    "## input",
    "## output",
    "## workflow",
    "## knowledge",
)
SECTION_NAMES = tuple(heading.replace("## ", "") for heading in REQUIRED_PROMPT_HEADINGS)
SECTION_HEADING_BY_NAME = dict(zip(SECTION_NAMES, REQUIRED_PROMPT_HEADINGS))


@dataclasses.dataclass
class Case:
    dataset: str
    case_id: str
    content: str
    gold_plantuml: str


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


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_prompt_file(path: Path, *, label: str) -> str:
    if not path.exists():
        raise FileNotFoundError(f"{label} prompt file not found: {path}")
    text = read_text(path).strip()
    if not text:
        raise ValueError(f"{label} prompt file is empty: {path}")
    return text


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def append_jsonl(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def load_cases(datasets_dir: Path) -> dict[str, list[Case]]:
    datasets: dict[str, list[Case]] = {}
    for path in sorted(datasets_dir.glob("*.jsonl")):
        name = path.stem.lower()
        cases: list[Case] = []
        with path.open(encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                payload = json.loads(line)
                content = str(payload.get("content") or "").strip()
                plantuml = str(payload.get("plantuml") or "").strip()
                if not content or not plantuml:
                    continue
                cases.append(Case(dataset=name, case_id=f"{name}-{idx:04d}", content=content, gold_plantuml=plantuml))
        datasets[name] = cases
    if not datasets:
        raise FileNotFoundError(f"No .jsonl datasets found under {datasets_dir}")
    return datasets


def select_cases(cases: list[Case], limit: int | None) -> list[Case]:
    if limit is None or limit <= 0:
        return cases
    return cases[:limit]


def grouped_cases(cases: list[Case]) -> dict[str, list[Case]]:
    groups: dict[str, list[Case]] = {}
    for case in cases:
        groups.setdefault(case.dataset, []).append(case)
    return groups


def select_cases_with_strategy(
    cases: list[Case],
    *,
    limit: int | None,
    strategy: str,
    seed: int,
) -> list[Case]:
    if limit is None or limit <= 0 or limit >= len(cases):
        return list(cases)

    strategy = strategy.lower()
    if strategy == "prefix":
        return cases[:limit]

    rng = random.Random(seed)
    if strategy == "random":
        selected = list(cases)
        rng.shuffle(selected)
        return selected[:limit]

    if strategy != "stratified":
        raise ValueError(f"Unknown sample strategy {strategy!r}")

    groups = grouped_cases(cases)
    dataset_names = sorted(groups)
    if limit < len(dataset_names):
        dataset_names = rng.sample(dataset_names, limit)
    selected_by_dataset: dict[str, list[Case]] = {name: [] for name in dataset_names}
    remaining = limit

    base_quota = max(1, limit // max(1, len(dataset_names)))
    for name in dataset_names:
        pool = list(groups[name])
        rng.shuffle(pool)
        take = min(base_quota, len(pool), remaining)
        selected_by_dataset[name].extend(pool[:take])
        remaining -= take
        groups[name] = pool[take:]
        if remaining <= 0:
            break

    while remaining > 0:
        available = [name for name in dataset_names if groups[name]]
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
        for name in dataset_names:
            items = selected_by_dataset[name]
            if idx < len(items):
                selected.append(items[idx])
    return selected[:limit]


def describe_case_distribution(cases: list[Case]) -> str:
    counts = Counter(case.dataset for case in cases)
    return ", ".join(f"{name}={counts[name]}" for name in sorted(counts)) or "empty"


def write_case_manifest(path: Path, cases: list[Case]) -> None:
    payload = [
        {
            "dataset": case.dataset,
            "case_id": case.case_id,
        }
        for case in cases
    ]
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2))


def normalize_base_url(base_url: str) -> str:
    value = (base_url or DEFAULT_BASE_URL).strip().rstrip("/")
    suffix = "/chat/completions"
    if value.endswith(suffix):
        value = value[: -len(suffix)]
    return value + "/"


def optional_float(value: str) -> float | None:
    if value.lower() in {"none", "omit", "default", ""}:
        return None
    return float(value)


def optional_bool(value: str) -> bool | None:
    lowered = value.lower()
    if lowered in {"none", "omit", "default", ""}:
        return None
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError("expected true, false, or omit")


def validate_glm_args(args: argparse.Namespace) -> None:
    if args.thinking not in {"enabled", "disabled"}:
        raise ValueError("--thinking must be 'enabled' or 'disabled' according to the GLM Chat Completions API")
    if args.max_tokens < 1 or args.evolve_max_tokens < 1:
        raise ValueError("--max-tokens and --evolve-max-tokens must be positive")
    if args.top_p is not None and not (0.01 <= args.top_p <= 0.99):
        raise ValueError("--top-p must be between 0.01 and 0.99, or 'omit'")
    if args.top_p is not None:
        print("[config] Both temperature and top_p are set; GLM docs recommend adjusting only one.", flush=True)
    if args.max_prompt_growth_ratio < 1.0:
        raise ValueError("--max-prompt-growth-ratio must be at least 1.0")
    if args.max_prompt_chars < 1000:
        raise ValueError("--max-prompt-chars is too small for the required prompt sections")
    if args.llm_max_retries < 0:
        raise ValueError("--llm-max-retries must be non-negative")
    if args.analysis_batch_size < 1 or args.gate_batch_size < 1:
        raise ValueError("--analysis-batch-size and --gate-batch-size must be positive")
    if args.max_sections_per_edit < 1 or args.max_sections_per_edit > len(SECTION_NAMES):
        raise ValueError("--max-sections-per-edit must be between 1 and the number of fixed prompt sections")
    if args.analysis_max_tokens < 1 or args.editor_max_tokens < 1:
        raise ValueError("--analysis-max-tokens and --editor-max-tokens must be positive")
    if args.llm_judge_max_tokens < 1:
        raise ValueError("--llm-judge-max-tokens must be positive")
    if args.llm_judge_max_retries < 1:
        raise ValueError("--llm-judge-max-retries must be positive")
    if args.llm_element_metrics and not args.api_key:
        raise ValueError("LLM semantic element metrics require the main API key via ZHIPU_LLM_API_KEY or --api-key")


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
    retry_phase: str = "llm_request",
    retry_context: dict[str, Any] | None = None,
    max_retries: int = 20,
    retry_initial_wait: int = 30,
    retry_max_wait: int = 600,
) -> str:
    if not api_key:
        raise RuntimeError("ZHIPU_LLM_API_KEY is required unless --mock-with-gold is used.")

    endpoint = normalize_base_url(base_url) + "chat/completions"
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
    return call_with_provider_retries(
        lambda: post_chat_completion(endpoint=endpoint, body=body, api_key=api_key, timeout=timeout),
        phase=retry_phase,
        state_dir=state_dir,
        context=retry_context,
        max_retries=max_retries,
        initial_wait=retry_initial_wait,
        max_wait=retry_max_wait,
    )


def post_chat_completion(*, endpoint: str, body: dict[str, Any], api_key: str, timeout: int) -> str:
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise ProviderHTTPError("LLM", exc.code, error_body, dict(exc.headers.items())) from exc

    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected LLM response: {json.dumps(payload, ensure_ascii=False)[:1000]}") from exc
    return str(content or "").strip()


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


def iter_semantic_elements(uml_code: str) -> list[str]:
    code = extract_plantuml(uml_code, wrap_if_needed=True)
    elements: list[str] = []
    in_note = False
    for raw_line in code.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lower = line.lower()
        if lower.startswith("note "):
            in_note = True
            continue
        if in_note:
            if lower == "end note" or lower.startswith("end note"):
                in_note = False
            continue
        if lower.startswith("@") or lower in {"start", "stop", "end", "endif", "end if", "endswitch", "end fork"}:
            continue

        if line.startswith(":") and ";" in line:
            label = line[1 : line.rfind(";")]
            normalized = normalize_label(label)
            if normalized:
                elements.append(normalized)
            continue

        condition = (
            extract_condition(line, "if")
            or extract_condition(line, "else if")
            or extract_condition(line, "elseif")
            or extract_condition(line, "switch")
            or extract_condition(line, "case")
            or extract_condition(line, "while")
        )
        if condition:
            normalized = normalize_label(condition)
            if normalized:
                elements.append(normalized)
            continue

        repeat_match = re.search(r"repeat\s+while\s*\((.*?)\)", line, flags=re.IGNORECASE)
        if repeat_match:
            normalized = normalize_label(repeat_match.group(1))
            if normalized:
                elements.append(normalized)

    return elements


def extract_relations(uml_code: str) -> list[str]:
    elements = iter_semantic_elements(uml_code)
    relations: list[str] = []
    for left, right in zip(elements, elements[1:]):
        if left and right and left != right:
            relations.append(f"{left} -> {right}")
    return relations


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


def generate_plantuml_for_case(
    *,
    prompt: str,
    case: Case,
    args: argparse.Namespace,
    state_dir: Path | None,
    retry_phase: str,
) -> str:
    if args.mock_with_gold:
        return extract_plantuml(case.gold_plantuml, wrap_if_needed=True)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Input:\n{case.content}\n\nOutput:"},
    ]
    return chat_completion(
        messages=messages,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        thinking=args.thinking,
        do_sample=args.do_sample,
        timeout=args.llm_timeout,
        state_dir=state_dir,
        retry_phase=retry_phase,
        retry_context={"dataset": case.dataset, "case_id": case.case_id},
        max_retries=args.llm_max_retries,
        retry_initial_wait=args.llm_rate_limit_initial_wait,
        retry_max_wait=args.llm_rate_limit_max_wait,
    )


def evaluate_cases(
    *,
    prompt: str,
    cases: list[Case],
    args: argparse.Namespace,
    output_path: Path,
    state_dir: Path | None = None,
    phase: str = "eval",
) -> tuple[list[EvaluationRecord], dict[str, float]]:
    write_text(output_path, "")

    records: list[EvaluationRecord] = []
    for idx, case in enumerate(cases, start=1):
        print(f"[eval] {idx}/{len(cases)} {case.case_id}", flush=True)
        try:
            generated = generate_plantuml_for_case(
                prompt=prompt,
                case=case,
                args=args,
                state_dir=state_dir,
                retry_phase=phase,
            )
        except Exception as exc:
            generated = ""
            syntax = SyntaxResult(False, [f"LLM generation failed: {exc}"])
            gold_nodes = iter_semantic_elements(case.gold_plantuml)
            node_metrics = compute_metric(gold_nodes, [], threshold=args.node_match_threshold)
            relation_metrics = compute_metric(extract_relations(case.gold_plantuml), [], threshold=args.relation_match_threshold)
            failure_types = ["generation_error"]
            if is_infrastructure_error(str(exc)):
                failure_types.append("infrastructure_error")
            else:
                failure_types.extend(["syntax_error", "missing_activity", "missing_or_wrong_relation"])
        else:
            syntax = validate_plantuml(generated, args.plantuml_jar)
            node_metrics = compute_metric(
                iter_semantic_elements(case.gold_plantuml),
                iter_semantic_elements(generated),
                threshold=args.node_match_threshold,
            )
            relation_metrics = compute_metric(
                extract_relations(case.gold_plantuml),
                extract_relations(generated),
                threshold=args.relation_match_threshold,
            )
            failure_types = classify_failures(syntax, node_metrics, relation_metrics)

        generated_plantuml = extract_plantuml(generated, wrap_if_needed=False)
        plantuml_compilation = check_plantuml_compilation(
            generated_plantuml,
            args.plantuml_jar,
            timeout=args.plantuml_compile_timeout,
        )
        llm_element_metrics = evaluate_llm_elements(
            ground_truth=case.gold_plantuml,
            prediction=generated_plantuml,
            enabled=args.llm_element_metrics,
            model=args.llm_judge_model,
            api_key=args.llm_judge_api_key,
            base_url=args.llm_judge_base_url,
            temperature=args.llm_judge_temperature,
            max_tokens=args.llm_judge_max_tokens,
            timeout=args.llm_judge_timeout,
            thinking=args.llm_judge_thinking,
            max_retries=args.llm_judge_max_retries,
            state_dir=state_dir,
            retry_phase=f"{phase}:llm_judge",
            retry_context={"dataset": case.dataset, "case_id": case.case_id},
            provider_max_retries=args.llm_max_retries,
            retry_initial_wait=args.llm_rate_limit_initial_wait,
            retry_max_wait=args.llm_rate_limit_max_wait,
        )
        if llm_element_metrics.status == "error":
            failure_types.append("llm_element_judge_error")

        record = EvaluationRecord(
            dataset=case.dataset,
            case_id=case.case_id,
            input_requirement=case.content,
            gold_plantuml=case.gold_plantuml,
            generated_plantuml=generated_plantuml,
            syntax=syntax,
            node_metrics=node_metrics,
            relation_metrics=relation_metrics,
            plantuml_compilation=plantuml_compilation,
            llm_element_metrics=llm_element_metrics,
            failure_types=failure_types,
        )
        records.append(record)
        append_jsonl(output_path, dataclasses.asdict(record))

    summary = summarize_records(records)
    return records, summary


def avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def summarize_records(records: list[EvaluationRecord]) -> dict[str, float]:
    llm_records = [r.llm_element_metrics for r in records if r.llm_element_metrics.enabled]
    llm_success = [m for m in llm_records if m.status == "success"]
    return {
        "count": float(len(records)),
        "syntax_pass_rate": avg([1.0 if r.syntax.passed else 0.0 for r in records]),
        "infrastructure_error_rate": avg([1.0 if "infrastructure_error" in r.failure_types else 0.0 for r in records]),
        "node_precision": avg([r.node_metrics.precision for r in records]),
        "node_recall": avg([r.node_metrics.recall for r in records]),
        "node_f1": avg([r.node_metrics.f1 for r in records]),
        "relation_precision": avg([r.relation_metrics.precision for r in records]),
        "relation_recall": avg([r.relation_metrics.recall for r in records]),
        "relation_f1": avg([r.relation_metrics.f1 for r in records]),
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
        f"syntax={summary['syntax_pass_rate']:.1%}, "
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


def optimization_score(summary: dict[str, float]) -> float:
    return (
        0.20 * summary.get("syntax_pass_rate", 0.0)
        + 0.40 * summary.get("node_f1", 0.0)
        + 0.40 * summary.get("relation_f1", 0.0)
        - 0.50 * summary.get("infrastructure_error_rate", 0.0)
    )


def choose_candidate_cases(train_cases: list[Case], args: argparse.Namespace, iteration: int) -> list[Case]:
    if args.candidate_max_cases <= 0 or args.candidate_max_cases >= len(train_cases):
        return list(train_cases)
    return select_cases_with_strategy(
        train_cases,
        limit=args.candidate_max_cases,
        strategy=args.candidate_sample_strategy,
        seed=args.sample_seed + 10_000 + iteration,
    )


def choose_iteration_batch(
    train_cases: list[Case],
    *,
    args: argparse.Namespace,
    iteration: int,
    batch_size: int,
    strategy: str,
    seed_offset: int,
) -> list[Case]:
    if batch_size <= 0 or batch_size >= len(train_cases):
        return list(train_cases)
    return select_cases_with_strategy(
        train_cases,
        limit=batch_size,
        strategy=strategy,
        seed=args.sample_seed + seed_offset + iteration,
    )


def acceptance_decision(
    *,
    baseline_summary: dict[str, float],
    candidate_summary: dict[str, float],
    min_delta: float,
    candidate_prompt: str,
    baseline_prompt: str,
    max_prompt_growth_ratio: float,
    max_prompt_chars: int,
    min_relation_delta: float,
    min_node_delta: float,
    min_syntax_delta: float,
    min_structure_delta: float,
    relation_accept_delta: float,
    node_accept_delta: float,
    combined_accept_delta: float,
) -> tuple[bool, dict[str, Any]]:
    baseline_score = optimization_score(baseline_summary)
    candidate_score = optimization_score(candidate_summary)
    delta = candidate_score - baseline_score
    syntax_delta = candidate_summary.get("syntax_pass_rate", 0.0) - baseline_summary.get("syntax_pass_rate", 0.0)
    structure_delta = candidate_summary.get("structure_valid_rate", baseline_summary.get("structure_valid_rate", 0.0)) - baseline_summary.get("structure_valid_rate", candidate_summary.get("structure_valid_rate", 0.0))
    node_delta = candidate_summary.get("node_f1", 0.0) - baseline_summary.get("node_f1", 0.0)
    relation_delta = candidate_summary.get("relation_f1", 0.0) - baseline_summary.get("relation_f1", 0.0)
    infrastructure_delta = candidate_summary.get("infrastructure_error_rate", 0.0) - baseline_summary.get("infrastructure_error_rate", 0.0)
    prompt_growth_ratio = len(candidate_prompt) / max(1, len(baseline_prompt))
    prompt_size_ok = len(candidate_prompt) <= max_prompt_chars and prompt_growth_ratio <= max_prompt_growth_ratio

    hard_constraints = {
        "syntax_delta_ok": syntax_delta >= min_syntax_delta,
        "structure_delta_ok": structure_delta >= min_structure_delta,
        "node_delta_ok": node_delta >= min_node_delta,
        "relation_delta_ok": relation_delta >= min_relation_delta,
        "infrastructure_delta_ok": infrastructure_delta <= 0,
        "prompt_size_ok": prompt_size_ok,
    }
    improvement_conditions = {
        "relation_improved": relation_delta >= relation_accept_delta,
        "node_improved_without_relation_regression": node_delta >= node_accept_delta and relation_delta >= 0,
        "combined_node_relation_improved": (node_delta + relation_delta) >= combined_accept_delta and relation_delta >= 0,
    }
    accept = all(hard_constraints.values()) and any(improvement_conditions.values())
    return accept, {
        "accepted": accept,
        "baseline_score": baseline_score,
        "candidate_score": candidate_score,
        "score_delta": delta,
        "min_delta": min_delta,
        "score_delta_meets_legacy_min_delta": delta >= min_delta,
        "syntax_delta": syntax_delta,
        "structure_delta": structure_delta,
        "node_delta": node_delta,
        "relation_delta": relation_delta,
        "infrastructure_delta": infrastructure_delta,
        "min_syntax_delta": min_syntax_delta,
        "min_structure_delta": min_structure_delta,
        "min_node_delta": min_node_delta,
        "min_relation_delta": min_relation_delta,
        "relation_accept_delta": relation_accept_delta,
        "node_accept_delta": node_accept_delta,
        "combined_accept_delta": combined_accept_delta,
        "hard_constraints": hard_constraints,
        "improvement_conditions": improvement_conditions,
        "prompt_chars_before": len(baseline_prompt),
        "prompt_chars_candidate": len(candidate_prompt),
        "prompt_growth_ratio": prompt_growth_ratio,
        "max_prompt_growth_ratio": max_prompt_growth_ratio,
        "max_prompt_chars": max_prompt_chars,
        "prompt_size_ok": prompt_size_ok,
        "baseline_summary": baseline_summary,
        "candidate_summary": candidate_summary,
        "score_formula": "0.20*syntax_pass_rate + 0.40*node_f1 + 0.40*relation_f1 - 0.50*infrastructure_error_rate",
    }


def has_only_infrastructure_errors(records: list[EvaluationRecord]) -> bool:
    return bool(records) and all("infrastructure_error" in r.failure_types for r in records)


def build_analysis(records: list[EvaluationRecord], summary: dict[str, float], max_cases: int) -> str:
    failure_counter = Counter(ft for r in records for ft in r.failure_types)
    failed_records = [r for r in records if r.failure_types and "infrastructure_error" not in r.failure_types]
    infra_records = [r for r in records if "infrastructure_error" in r.failure_types]
    worst = sorted(
        failed_records,
        key=lambda r: (
            1 if r.syntax.passed else 0,
            r.node_metrics.f1,
            r.relation_metrics.f1,
        ),
    )[:max_cases]

    lines: list[str] = []
    lines.append("# Prompt Evaluation Analysis")
    lines.append("")
    lines.append("## Summary")
    for key, value in summary.items():
        if key == "count":
            lines.append(f"- {key}: {int(value)}")
        else:
            lines.append(f"- {key}: {value:.4f}")
    lines.append("")
    lines.append("## Failure Types")
    if failure_counter:
        for failure, count in failure_counter.most_common():
            lines.append(f"- {failure}: {count}")
    else:
        lines.append("- none")
    if infra_records:
        lines.append("")
        lines.append("## Infrastructure Errors")
        lines.append(f"- count: {len(infra_records)}")
        lines.append("- These cases failed before a model output was available. Do not modify the prompt based only on infrastructure errors.")
        for record in infra_records[:max_cases]:
            err = " | ".join(record.syntax.errors[:3]) if record.syntax.errors else "unknown"
            lines.append(f"- {record.case_id}: {err}")
    lines.append("")
    lines.append("## Representative Failure Cases")
    if not worst:
        lines.append("- none")
        lines.append("")
    for record in worst:
        lines.append(f"### {record.case_id}")
        lines.append(f"- dataset: {record.dataset}")
        lines.append(f"- failure_types: {', '.join(record.failure_types) if record.failure_types else 'none'}")
        lines.append(f"- syntax_passed: {record.syntax.passed}")
        if record.syntax.errors:
            lines.append(f"- syntax_errors: {' | '.join(record.syntax.errors[:5])}")
        lines.append(f"- plantuml_compiles: {record.plantuml_compilation.passed}")
        if record.plantuml_compilation.errors:
            lines.append(f"- plantuml_compile_errors: {' | '.join(record.plantuml_compilation.errors[:5])}")
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
    lines.append("")

    lines.append("## Prompt Improvement Guidance")
    if len(infra_records) == len(records):
        lines.append("- All evaluated cases failed due to infrastructure errors. Do not change the prompt for this iteration.")
    lines.append("- Modify only the run-local `work.md` prompt.")
    lines.append("- Preserve the required markdown sections.")
    lines.append("- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.")
    lines.append("- Target the most frequent failure types first and avoid overfitting to a single case.")
    return "\n".join(lines) + "\n"


def strip_markdown_fence(text: str) -> str:
    match = re.search(r"```(?:markdown|md)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else text.strip()


def normalize_prompt_headings(candidate: str) -> str:
    normalized = candidate.strip()
    heading_names = [heading.replace("## ", "") for heading in REQUIRED_PROMPT_HEADINGS]
    for heading_name in heading_names:
        pattern = rf"(?im)^#{{1,6}}\s*{re.escape(heading_name)}\s*$"
        normalized = re.sub(pattern, f"## {heading_name}", normalized)
    return normalized


def parse_prompt_sections(prompt: str) -> dict[str, str]:
    normalized = normalize_prompt_headings(prompt)
    pattern = re.compile(r"(?im)^##\s+(.+?)\s*$")
    matches = list(pattern.finditer(normalized))
    sections: dict[str, str] = {}
    seen: list[str] = []
    for idx, match in enumerate(matches):
        name = match.group(1).strip().lower()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(normalized)
        if name in SECTION_NAMES:
            if name in sections:
                raise ValueError(f"Duplicate section heading: {name}")
            sections[name] = normalized[start:end].strip()
            seen.append(name)
    missing = [name for name in SECTION_NAMES if name not in sections]
    if missing:
        raise ValueError(f"Missing required prompt sections: {', '.join(missing)}")
    if seen != list(SECTION_NAMES):
        raise ValueError("Prompt sections must keep the required order")
    return sections


def render_prompt_sections(sections: dict[str, str]) -> str:
    parts: list[str] = []
    for name in SECTION_NAMES:
        heading = SECTION_HEADING_BY_NAME[name]
        content = sections.get(name, "").strip()
        parts.append(f"{heading}\n\n{content}".rstrip())
    return "\n\n".join(parts).strip() + "\n"


def extract_json_object(text: str) -> dict[str, Any] | None:
    stripped = strip_markdown_fence(text)
    try:
        payload = json.loads(stripped)
        return payload if isinstance(payload, dict) else None
    except json.JSONDecodeError:
        pass

    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            payload = json.loads(stripped[start : end + 1])
            return payload if isinstance(payload, dict) else None
        except json.JSONDecodeError:
            return None
    return None


def validate_prompt_edit_payload(payload: dict[str, Any], *, max_sections: int) -> tuple[bool, list[str]]:
    errors: list[str] = []
    edits = payload.get("edits")
    if not isinstance(edits, list) or not edits:
        errors.append("Payload must contain a non-empty edits list")
        return False, errors
    if len(edits) > max_sections:
        errors.append(f"At most {max_sections} sections may be modified")

    edited_sections: set[str] = set()
    for idx, edit in enumerate(edits, start=1):
        if not isinstance(edit, dict):
            errors.append(f"Edit {idx} must be an object")
            continue
        section = str(edit.get("section") or "").strip().lower()
        operation = str(edit.get("operation") or "").strip().lower()
        content = edit.get("content")
        if section not in SECTION_NAMES:
            errors.append(f"Edit {idx} has invalid section: {section!r}")
        if section in edited_sections:
            errors.append(f"Section {section!r} is edited more than once")
        edited_sections.add(section)
        if operation not in {"replace", "append"}:
            errors.append(f"Edit {idx} has invalid operation: {operation!r}")
        if not isinstance(content, str) or not content.strip():
            errors.append(f"Edit {idx} must provide non-empty string content")
        if isinstance(content, str) and re.search(r"(?im)^##\s+", content):
            errors.append(f"Edit {idx} content must not contain markdown section headings")
    return not errors, errors


def apply_prompt_edit_payload(prompt: str, payload: dict[str, Any], *, max_sections: int) -> tuple[str | None, list[str]]:
    ok, errors = validate_prompt_edit_payload(payload, max_sections=max_sections)
    if not ok:
        return None, errors
    try:
        sections = parse_prompt_sections(prompt)
    except ValueError as exc:
        return None, [str(exc)]

    for edit in payload["edits"]:
        section = str(edit["section"]).strip().lower()
        operation = str(edit["operation"]).strip().lower()
        content = str(edit["content"]).strip()
        if operation == "replace":
            sections[section] = content
        elif operation == "append":
            existing = sections.get(section, "").strip()
            sections[section] = f"{existing}\n\n{content}".strip() if existing else content

    candidate = render_prompt_sections(sections)
    ok_candidate, candidate_errors = validate_prompt_candidate(candidate)
    if not ok_candidate:
        return None, candidate_errors
    return candidate, []


def validate_prompt_candidate(candidate: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if strip_code_fence(candidate).lstrip().startswith("@startuml"):
        errors.append("Optimizer returned PlantUML instead of a markdown prompt")
    try:
        parse_prompt_sections(candidate)
    except ValueError as exc:
        errors.append(str(exc))
    try:
        output_section = parse_prompt_sections(candidate).get("output", "")
    except ValueError:
        output_section = ""
    if "plantuml" not in output_section.lower():
        errors.append("Output section must require PlantUML code")
    return not errors, errors


def failure_analysis_payload(records: list[EvaluationRecord], summary: dict[str, float], max_cases: int) -> dict[str, Any]:
    failed_records = [r for r in records if r.failure_types and "infrastructure_error" not in r.failure_types]
    representative = sorted(
        failed_records,
        key=lambda r: (
            1 if r.syntax.passed else 0,
            r.node_metrics.f1,
            r.relation_metrics.f1,
        ),
    )[:max_cases]
    return {
        "summary": summary,
        "failure_type_counts": dict(Counter(ft for r in records for ft in r.failure_types)),
        "representative_cases": [
            {
                "dataset": r.dataset,
                "case_id": r.case_id,
                "input_requirement": r.input_requirement,
                "gold_plantuml": r.gold_plantuml,
                "predicted_plantuml": r.generated_plantuml,
                "syntax": dataclasses.asdict(r.syntax),
                "node_metrics": dataclasses.asdict(r.node_metrics),
                "relation_metrics": dataclasses.asdict(r.relation_metrics),
                "failure_types": r.failure_types,
            }
            for r in representative
        ],
    }


def analyze_failures(
    *,
    current_prompt: str,
    records: list[EvaluationRecord],
    summary: dict[str, float],
    args: argparse.Namespace,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    payload = {
        "task": "Analyze batch-level failures for a UML activity diagram prompt. Do not propose a full prompt.",
        "system_prompt_file": str(args.failure_analysis_prompt_path),
        "current_prompt": current_prompt,
        "evaluation": failure_analysis_payload(records, summary, args.analysis_cases),
        "required_output_schema": {
            "summary": "string",
            "error_patterns": [
                {
                    "name": "short snake_case label",
                    "severity": "low|medium|high",
                    "evidence_case_ids": ["case id strings"],
                    "problem": "what went wrong at the batch level",
                    "suggested_prompt_direction": "general prompt-level direction",
                    "target_sections": ["agent task|input|output|workflow|knowledge"],
                }
            ],
            "do_not_optimize_for": ["string"],
        },
    }
    write_text(output_input_path, json.dumps(payload, ensure_ascii=False, indent=2))
    messages = [
        {
            "role": "system",
            "content": read_prompt_file(args.failure_analysis_prompt_path, label="failure analysis"),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, indent=2),
        },
    ]
    raw = chat_completion(
        messages=messages,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        temperature=args.analysis_temperature,
        top_p=args.top_p,
        max_tokens=args.analysis_max_tokens,
        thinking=args.thinking,
        do_sample=args.do_sample,
        timeout=args.llm_timeout,
        state_dir=state_dir,
        retry_phase="failure_analysis",
        retry_context={"iteration": iteration, "output_path": str(output_path)},
        max_retries=args.llm_max_retries,
        retry_initial_wait=args.llm_rate_limit_initial_wait,
        retry_max_wait=args.llm_rate_limit_max_wait,
    )
    write_text(output_path, raw)
    parsed = extract_json_object(raw)
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "Failure analysis did not return a JSON object.\n")
        return None
    return parsed


def propose_prompt_edits(
    *,
    current_prompt: str,
    failure_analysis: dict[str, Any],
    args: argparse.Namespace,
    output_input_path: Path,
    output_path: Path,
    state_dir: Path | None,
    iteration: int,
) -> dict[str, Any] | None:
    if args.no_evolve:
        return None

    payload = {
        "task": "Edit fixed sections of a UML activity diagram generation prompt.",
        "system_prompt_file": str(args.prompt_editor_prompt_path),
        "current_prompt_sections": parse_prompt_sections(current_prompt),
        "failure_analysis": failure_analysis,
        "constraints": {
            "allowed_sections": list(SECTION_NAMES),
            "allowed_operations": ["replace", "append"],
            "max_sections_per_edit": args.max_sections_per_edit,
            "do_not_change_section_structure": True,
            "prefer_general_rules_over_dataset_specific_examples": True,
            "max_prompt_chars": args.max_prompt_chars,
        },
        "required_output_schema": {
            "edits": [
                {
                    "section": "one of agent task, input, output, workflow, knowledge",
                    "operation": "replace|append",
                    "content": "new section content or content to append, without markdown headings",
                }
            ],
            "rationale": "short explanation",
            "expected_effect": {
                "node_f1": "increase|neutral|risk",
                "relation_f1": "increase|neutral|risk",
                "syntax_pass_rate": "increase|neutral|risk",
            },
        },
    }
    write_text(output_input_path, json.dumps(payload, ensure_ascii=False, indent=2))
    messages = [
        {
            "role": "system",
            "content": read_prompt_file(args.prompt_editor_prompt_path, label="prompt editor"),
        },
        {
            "role": "user",
            "content": json.dumps(payload, ensure_ascii=False, indent=2),
        },
    ]
    raw = chat_completion(
        messages=messages,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        temperature=args.editor_temperature,
        top_p=args.top_p,
        max_tokens=args.editor_max_tokens,
        thinking=args.thinking,
        do_sample=args.do_sample,
        timeout=args.llm_timeout,
        state_dir=state_dir,
        retry_phase="prompt_edit",
        retry_context={"iteration": iteration, "output_path": str(output_path)},
        max_retries=args.llm_max_retries,
        retry_initial_wait=args.llm_rate_limit_initial_wait,
        retry_max_wait=args.llm_rate_limit_max_wait,
    )
    write_text(output_path, raw)
    parsed = extract_json_object(raw)
    if parsed is None:
        write_text(output_path.with_suffix(".rejected.txt"), "Prompt editor did not return a JSON object.\n")
        return None
    ok, errors = validate_prompt_edit_payload(parsed, max_sections=args.max_sections_per_edit)
    if not ok:
        write_text(output_path.with_suffix(".rejected.txt"), "\n".join(errors) + "\n")
        print(f"[evolve] Rejected prompt edit: {'; '.join(errors)}", flush=True)
        return None
    return parsed


def make_run_dir(runs_dir: Path, label: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    run_dir = runs_dir / f"{timestamp}__{label}"
    run_dir.mkdir(parents=True, exist_ok=False)
    return run_dir


def initialize_run_prompt(seed_prompt_path: Path, run_dir: Path) -> Path:
    work_prompt_path = run_dir / "work.md"
    seed_prompt = read_text(seed_prompt_path)
    write_text(work_prompt_path, seed_prompt)
    write_text(run_dir / "prompt_initial.md", seed_prompt)
    print(f"[prompt] copied seed prompt to run-local work file: {work_prompt_path}")
    return work_prompt_path


def write_run_args(args: argparse.Namespace, run_dir: Path) -> None:
    public_args: dict[str, Any] = {}
    for key, value in sorted(vars(args).items()):
        if key in {"api_key", "llm_judge_api_key"}:
            public_args[f"{key}_present"] = bool(value)
        elif isinstance(value, Path):
            public_args[key] = str(value)
        else:
            public_args[key] = value
    write_text(run_dir / "run_args.json", json.dumps(public_args, ensure_ascii=False, indent=2))


def run_training_iterations(
    *,
    args: argparse.Namespace,
    train_cases: list[Case],
    run_dir: Path,
    work_prompt_path: Path,
    label: str,
) -> tuple[str, dict[str, float]]:
    print(f"[run] {label}, train_cases={len(train_cases)}")
    print(f"[run] train distribution: {describe_case_distribution(train_cases)}")
    print(f"[run] output={run_dir}")

    prompt = read_text(work_prompt_path)
    last_summary: dict[str, float] = {}
    best_prompt = prompt
    best_summary: dict[str, float] = {}
    best_score = float("-inf")

    for iteration in range(1, args.iterations + 1):
        iter_dir = run_dir / f"iteration_{iteration:03d}"
        write_text(iter_dir / "prompt_before.md", prompt)
        analysis_cases = choose_iteration_batch(
            train_cases,
            args=args,
            iteration=iteration,
            batch_size=args.analysis_batch_size,
            strategy=args.sample_strategy,
            seed_offset=30_000,
        )
        write_case_manifest(iter_dir / "analysis_batch_cases.json", analysis_cases)
        print(f"\n[iteration {iteration}] evaluating analysis batch")
        print(f"[iteration {iteration}] analysis batch distribution: {describe_case_distribution(analysis_cases)}")
        records, summary = evaluate_cases(
            prompt=prompt,
            cases=analysis_cases,
            args=args,
            output_path=iter_dir / "predictions.jsonl",
            state_dir=run_dir,
            phase=f"iteration_{iteration:03d}:analysis_batch",
        )
        last_summary = summary
        write_text(iter_dir / "evaluation_summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
        write_text(iter_dir / "train_summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
        current_score = optimization_score(summary)
        if current_score > best_score:
            best_score = current_score
            best_prompt = prompt
            best_summary = summary
            write_text(run_dir / "prompt_best.md", best_prompt)
            write_text(
                run_dir / "best_prompt_summary.json",
                json.dumps(
                    {
                        "iteration": iteration,
                        "phase": "train_before_evolve",
                        "score": best_score,
                        "summary": best_summary,
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
            )
        analysis = build_analysis(records, summary, args.analysis_cases)
        write_text(iter_dir / "analysis" / "overview.md", analysis)
        print(f"[iteration {iteration}] train {format_summary(summary)}")

        if args.no_evolve:
            write_text(iter_dir / "prompt_after.md", prompt)
            print(f"[iteration {iteration}] prompt unchanged")
            continue

        if has_only_infrastructure_errors(records):
            write_text(
                iter_dir / "prompt_update.skipped.txt",
                "Skipped prompt update because every evaluated case failed before a model output was available.\n",
            )
            write_text(iter_dir / "prompt_after.md", prompt)
            print(f"[iteration {iteration}] infrastructure-only failures; prompt unchanged")
            continue

        failure_analysis = analyze_failures(
            current_prompt=prompt,
            records=records,
            summary=summary,
            args=args,
            output_input_path=iter_dir / "failure_analysis_input.json",
            output_path=iter_dir / "failure_analysis_output.json",
            state_dir=run_dir,
            iteration=iteration,
        )
        if failure_analysis is None:
            write_text(iter_dir / "prompt_after.md", prompt)
            print(f"[iteration {iteration}] failure analysis invalid; prompt unchanged")
            continue

        edit_payload = propose_prompt_edits(
            current_prompt=prompt,
            failure_analysis=failure_analysis,
            args=args,
            output_input_path=iter_dir / "prompt_edit_input.json",
            output_path=iter_dir / "prompt_edit_output.json",
            state_dir=run_dir,
            iteration=iteration,
        )
        if edit_payload is None:
            write_text(iter_dir / "prompt_after.md", prompt)
            print(f"[iteration {iteration}] prompt edit invalid; prompt unchanged")
            continue

        candidate, edit_errors = apply_prompt_edit_payload(
            prompt,
            edit_payload,
            max_sections=args.max_sections_per_edit,
        )
        if candidate is None:
            write_text(iter_dir / "prompt_edit_output.rejected.txt", "\n".join(edit_errors) + "\n")
            write_text(iter_dir / "prompt_after.md", prompt)
            print(f"[iteration {iteration}] prompt edit rejected: {'; '.join(edit_errors)}")
            continue

        write_text(iter_dir / "candidate_prompt.md", candidate)
        write_text(iter_dir / "prompt_candidate.md", candidate)

        gate_cases = choose_iteration_batch(
            train_cases,
            args=args,
            iteration=iteration,
            batch_size=args.gate_batch_size,
            strategy=args.candidate_sample_strategy,
            seed_offset=40_000,
        )
        print(f"[iteration {iteration}] gate distribution: {describe_case_distribution(gate_cases)}")
        write_case_manifest(iter_dir / "gate_cases.json", gate_cases)
        write_case_manifest(iter_dir / "candidate_cases.json", gate_cases)
        candidate_records, candidate_summary = evaluate_cases(
            prompt=candidate,
            cases=gate_cases,
            args=args,
            output_path=iter_dir / "gate_predictions.jsonl",
            state_dir=run_dir,
            phase=f"iteration_{iteration:03d}:gate_candidate",
        )
        write_text(iter_dir / "gate_summary.json", json.dumps(candidate_summary, ensure_ascii=False, indent=2))
        write_text(iter_dir / "candidate_records.jsonl", "\n".join(json.dumps(dataclasses.asdict(r), ensure_ascii=False) for r in candidate_records) + ("\n" if candidate_records else ""))
        write_text(iter_dir / "candidate_summary.json", json.dumps(candidate_summary, ensure_ascii=False, indent=2))

        baseline_for_gate = summary
        if gate_cases != analysis_cases:
            baseline_gate_records, baseline_for_gate = evaluate_cases(
                prompt=prompt,
                cases=gate_cases,
                args=args,
                output_path=iter_dir / "baseline_gate_records.jsonl",
                state_dir=run_dir,
                phase=f"iteration_{iteration:03d}:baseline_gate_eval",
            )
            write_text(iter_dir / "baseline_gate_summary.json", json.dumps(baseline_for_gate, ensure_ascii=False, indent=2))
            if has_only_infrastructure_errors(baseline_gate_records + candidate_records):
                write_text(iter_dir / "prompt_after.md", prompt)
                print(f"[iteration {iteration}] candidate gate had only infrastructure failures; prompt unchanged")
                continue

        accepted, decision = acceptance_decision(
            baseline_summary=baseline_for_gate,
            candidate_summary=candidate_summary,
            min_delta=args.acceptance_min_delta,
            candidate_prompt=candidate,
            baseline_prompt=prompt,
            max_prompt_growth_ratio=args.max_prompt_growth_ratio,
            max_prompt_chars=args.max_prompt_chars,
            min_relation_delta=args.acceptance_min_relation_delta,
            min_node_delta=args.acceptance_min_node_delta,
            min_syntax_delta=args.acceptance_min_syntax_delta,
            min_structure_delta=args.acceptance_min_structure_delta,
            relation_accept_delta=args.relation_accept_delta,
            node_accept_delta=args.node_accept_delta,
            combined_accept_delta=args.combined_accept_delta,
        )
        write_text(iter_dir / "prompt_acceptance.json", json.dumps(decision, ensure_ascii=False, indent=2))

        if accepted:
            prompt = candidate
            write_text(work_prompt_path, prompt)
            write_text(iter_dir / "prompt_after.md", prompt)
            print(f"[iteration {iteration}] prompt updated: {work_prompt_path}")
        else:
            write_text(iter_dir / "candidate_rejected_by_score.json", json.dumps(decision, ensure_ascii=False, indent=2))
            write_text(iter_dir / "prompt_after.md", prompt)
            print(
                f"[iteration {iteration}] candidate rejected by score "
                f"(delta={decision['score_delta']:.4f}, min={args.acceptance_min_delta:.4f}); prompt unchanged"
            )

    final_prompt = best_prompt if args.use_best_prompt_for_test else read_text(work_prompt_path)
    write_text(run_dir / "prompt_final.md", final_prompt)
    if args.use_best_prompt_for_test:
        write_text(work_prompt_path, final_prompt)
    return final_prompt, last_summary


def run_train_only(args: argparse.Namespace, datasets: dict[str, list[Case]], train_dataset: str) -> dict[str, float]:
    train_dataset = train_dataset.lower()
    if train_dataset not in datasets:
        raise ValueError(f"Unknown train dataset {train_dataset!r}. Available: {', '.join(sorted(datasets))}")
    train_cases = select_cases_with_strategy(
        datasets[train_dataset],
        limit=args.max_train_cases,
        strategy=args.sample_strategy,
        seed=args.sample_seed,
    )
    run_dir = make_run_dir(args.runs_dir, f"train-{train_dataset}")
    write_run_args(args, run_dir)
    write_case_manifest(run_dir / "train_cases.json", train_cases)
    work_prompt_path = initialize_run_prompt(args.prompt_path, run_dir)
    _, summary = run_training_iterations(
        args=args,
        train_cases=train_cases,
        run_dir=run_dir,
        work_prompt_path=work_prompt_path,
        label=f"train_only={train_dataset}",
    )
    return summary


def run_one_split(args: argparse.Namespace, datasets: dict[str, list[Case]], test_dataset: str) -> dict[str, float]:
    test_dataset = test_dataset.lower()
    if test_dataset not in datasets:
        raise ValueError(f"Unknown test dataset {test_dataset!r}. Available: {', '.join(sorted(datasets))}")

    train_cases_all = [case for name, cases in datasets.items() if name != test_dataset for case in cases]
    test_cases_all = datasets[test_dataset]
    train_cases = select_cases_with_strategy(
        train_cases_all,
        limit=args.max_train_cases,
        strategy=args.sample_strategy,
        seed=args.sample_seed,
    )
    test_cases = select_cases_with_strategy(
        test_cases_all,
        limit=args.max_test_cases,
        strategy=args.test_sample_strategy,
        seed=args.sample_seed + 20_000,
    )

    run_dir = make_run_dir(args.runs_dir, f"test-{test_dataset}")
    write_run_args(args, run_dir)
    write_case_manifest(run_dir / "train_cases.json", train_cases)
    write_case_manifest(run_dir / "test_cases.json", test_cases)
    work_prompt_path = initialize_run_prompt(args.prompt_path, run_dir)
    print(f"[run] test={test_dataset}, train_cases={len(train_cases)}, test_cases={len(test_cases)}")
    print(f"[run] test distribution: {describe_case_distribution(test_cases)}")
    final_prompt, _ = run_training_iterations(
        args=args,
        train_cases=train_cases,
        run_dir=run_dir,
        work_prompt_path=work_prompt_path,
        label=f"test={test_dataset}",
    )

    print(f"\n[test] evaluating held-out dataset {test_dataset}")
    records, summary = evaluate_cases(
        prompt=final_prompt,
        cases=test_cases,
        args=args,
        output_path=run_dir / "test_records.jsonl",
        state_dir=run_dir,
        phase=f"test_eval:{test_dataset}",
    )
    write_text(run_dir / "test_summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    write_text(run_dir / "test_analysis.md", build_analysis(records, summary, args.analysis_cases))
    write_text(run_dir / "prompt_final.md", final_prompt)
    print(f"[test] {format_summary(summary)}")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prompt evolution for UML activity diagram PlantUML generation")
    parser.add_argument("--test-dataset", default=None, help="Held-out dataset name, or 'all' for leave-one-dataset-out")
    parser.add_argument("--train-dataset", default=None, help="Dataset to use for train-only mode")
    parser.add_argument("--train-only", action="store_true", help="Run optimization on --train-dataset without held-out testing")
    parser.add_argument("--datasets-dir", type=Path, default=DEFAULT_DATASETS_DIR)
    parser.add_argument("--prompt-path", type=Path, default=DEFAULT_PROMPT_PATH, help="Read-only seed prompt copied to each run's work.md")
    parser.add_argument("--failure-analysis-prompt-path", type=Path, default=DEFAULT_FAILURE_ANALYSIS_PROMPT_PATH, help="System prompt markdown for the failure-analysis model")
    parser.add_argument("--prompt-editor-prompt-path", type=Path, default=DEFAULT_PROMPT_EDITOR_PROMPT_PATH, help="System prompt markdown for the prompt-edit model")
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    parser.add_argument("--plantuml-jar", type=Path, default=DEFAULT_PLANTUML_JAR)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--max-train-cases", type=int, default=0, help="0 means all training cases")
    parser.add_argument("--max-test-cases", type=int, default=0, help="0 means all test cases")
    parser.add_argument("--analysis-batch-size", type=int, default=10, help="Training batch size used for generation and failure analysis")
    parser.add_argument("--gate-batch-size", type=int, default=10, help="Training batch size used to accept or reject edited prompts")
    parser.add_argument("--sample-strategy", choices=["stratified", "random", "prefix"], default="stratified", help="How to select limited training cases")
    parser.add_argument("--test-sample-strategy", choices=["stratified", "random", "prefix"], default="prefix", help="How to select limited held-out test cases")
    parser.add_argument("--candidate-sample-strategy", choices=["stratified", "random", "prefix"], default="stratified", help="How to select candidate gate cases")
    parser.add_argument("--sample-seed", type=int, default=13)
    parser.add_argument("--analysis-cases", type=int, default=8)
    parser.add_argument("--model", default=os.environ.get("ZHIPU_LLM_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-key", default=os.environ.get("ZHIPU_LLM_API_KEY", ""))
    parser.add_argument("--base-url", default=os.environ.get("ZHIPU_LLM_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--evolve-temperature", type=float, default=0.4)
    parser.add_argument("--analysis-temperature", type=float, default=0.2)
    parser.add_argument("--editor-temperature", type=float, default=0.2)
    parser.add_argument("--top-p", type=optional_float, default=None, help="GLM top_p, or 'omit' to use provider default")
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--evolve-max-tokens", type=int, default=12000)
    parser.add_argument("--analysis-max-tokens", type=int, default=4096)
    parser.add_argument("--editor-max-tokens", type=int, default=4096)
    parser.add_argument("--thinking", choices=["enabled", "disabled"], default=os.environ.get("ZHIPU_THINKING_TYPE", DEFAULT_THINKING_TYPE))
    parser.add_argument("--do-sample", type=optional_bool, default=None, help="GLM do_sample, or 'omit' to use provider default")
    parser.add_argument("--llm-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-max-retries", type=int, default=20, help="Retries for provider 429/5xx/transient errors before failing")
    parser.add_argument("--llm-rate-limit-initial-wait", type=int, default=30, help="Initial wait seconds for provider rate-limit retries")
    parser.add_argument("--llm-rate-limit-max-wait", type=int, default=600, help="Maximum wait seconds for provider rate-limit retries")
    parser.add_argument("--node-match-threshold", type=float, default=0.82)
    parser.add_argument("--relation-match-threshold", type=float, default=0.86)
    parser.add_argument("--candidate-max-cases", type=int, default=0, help="Legacy alias for --gate-batch-size when set")
    parser.add_argument("--acceptance-min-delta", type=float, default=0.01, help="Minimum aggregate score improvement required before candidate prompt is accepted")
    parser.add_argument("--acceptance-min-node-delta", type=float, default=-0.005, help="Maximum tolerated node F1 regression during candidate acceptance")
    parser.add_argument("--acceptance-min-relation-delta", type=float, default=-0.002, help="Maximum tolerated relation F1 regression during candidate acceptance")
    parser.add_argument("--acceptance-min-syntax-delta", type=float, default=0.0, help="Minimum syntax pass-rate delta during candidate acceptance")
    parser.add_argument("--acceptance-min-structure-delta", type=float, default=0.0, help="Minimum structure-valid-rate delta when that metric is available")
    parser.add_argument("--relation-accept-delta", type=float, default=0.01, help="Accept when relation F1 improves by at least this amount")
    parser.add_argument("--node-accept-delta", type=float, default=0.015, help="Accept when node F1 improves by at least this amount and relation F1 does not regress")
    parser.add_argument("--combined-accept-delta", type=float, default=0.02, help="Accept when node F1 plus relation F1 improves by at least this amount and relation F1 does not regress")
    parser.add_argument("--max-sections-per-edit", type=int, default=2, help="Maximum fixed prompt sections a prompt edit may modify")
    parser.add_argument("--max-prompt-growth-ratio", type=float, default=1.35, help="Reject candidate prompts that grow more than this ratio over the current prompt")
    parser.add_argument("--max-prompt-chars", type=int, default=9000, help="Reject candidate prompts longer than this many characters")
    parser.add_argument("--use-best-prompt-for-test", action=argparse.BooleanOptionalAction, default=True, help="Use the best validation prompt for held-out testing")
    parser.add_argument("--plantuml-compile-timeout", type=int, default=30, help="Timeout in seconds for PlantUML compilation checks")
    parser.add_argument("--llm-element-metrics", action=argparse.BooleanOptionalAction, default=True, help="Run LLM semantic node/relation P/R/F1 metrics; use --no-llm-element-metrics for cheap local smoke tests")
    parser.add_argument("--llm-judge-temperature", type=float, default=0.0)
    parser.add_argument("--llm-judge-max-tokens", type=int, default=4096)
    parser.add_argument("--llm-judge-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-judge-max-retries", type=int, default=3)
    parser.add_argument("--mock-with-gold", action="store_true", help="Use gold PlantUML as generated output for pipeline checks")
    parser.add_argument("--no-evolve", action="store_true", help="Evaluate only; do not ask the LLM to update the prompt")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.datasets_dir = args.datasets_dir.resolve()
    args.prompt_path = args.prompt_path.resolve()
    args.failure_analysis_prompt_path = args.failure_analysis_prompt_path.resolve()
    args.prompt_editor_prompt_path = args.prompt_editor_prompt_path.resolve()
    args.runs_dir = args.runs_dir.resolve()
    args.plantuml_jar = args.plantuml_jar.resolve()
    if args.candidate_max_cases > 0:
        args.gate_batch_size = args.candidate_max_cases
    args.llm_judge_model = args.model
    args.llm_judge_api_key = args.api_key
    args.llm_judge_base_url = args.base_url
    args.llm_judge_thinking = args.thinking

    datasets = load_cases(args.datasets_dir)
    validate_glm_args(args)
    if not args.prompt_path.exists():
        raise FileNotFoundError(f"Seed prompt file not found: {args.prompt_path}")
    read_prompt_file(args.failure_analysis_prompt_path, label="failure analysis")
    read_prompt_file(args.prompt_editor_prompt_path, label="prompt editor")

    if args.train_only:
        if not args.train_dataset:
            parser.error("--train-only requires --train-dataset")
        run_train_only(args, datasets, args.train_dataset)
        return

    if not args.test_dataset:
        parser.error("Specify --test-dataset for split testing, or --train-only --train-dataset for training only")

    if args.test_dataset.lower() == "all":
        summaries: dict[str, dict[str, float]] = {}
        for dataset_name in sorted(datasets):
            summaries[dataset_name] = run_one_split(args, datasets, dataset_name)
        print("\n[all] held-out summaries")
        for dataset_name, summary in summaries.items():
            print(f"- {dataset_name}: {format_summary(summary)}")
    else:
        run_one_split(args, datasets, args.test_dataset)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        sys.exit(130)


