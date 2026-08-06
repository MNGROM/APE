#!/usr/bin/env python3
"""Compare APE and LATO baseline prompts under the same APE metrics."""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from ape_datasets.lato import Case, load_cases, select_cases_with_strategy, write_case_manifest
from config import (
    DEFAULT_BASE_URL,
    DEFAULT_DATASETS_DIR,
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_MODEL,
    DEFAULT_PLANTUML_JAR,
    DEFAULT_PROMPT_PATH,
    DEFAULT_RUNS_DIR,
    DEFAULT_THINKING_TYPE,
    get_llm_provider_settings,
    optional_bool,
)
from element_extraction import extract_graph_for_metrics
from llm import LLMClient
from llm_element_metrics import check_plantuml_compilation, disabled_llm_metrics, evaluate_llm_elements
from metrics import (
    ActivityGraph,
    DEFAULT_EMBEDDING_MODEL,
    EvaluationRecord,
    classify_failures,
    compute_metric,
    format_summary,
    extract_activity_graph,
    summarize_records,
    validate_plantuml,
)
from prediction import extract_plantuml
from utils.io import append_jsonl, read_prompt_file, write_text


LATO_ZERO_SHOT_USER_TEMPLATE = (
    "Input:\n{Input}\n\n"
    "Please generate PlantUML code for the activity diagram according to the above requirements. "
    "Output the results directly without explanation\n\n"
    "Output:"
)


def parse_methods(value: str) -> list[str]:
    methods = [item.strip() for item in value.split(",") if item.strip()]
    allowed = {"ape", "lato-zero-shot"}
    unknown = sorted(set(methods) - allowed)
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown method(s): {', '.join(unknown)}")
    return methods


def make_output_dir(base_dir: Path, test_dataset: str) -> Path:
    stamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    out_dir = base_dir / f"{stamp}__compare-lato__test-{test_dataset}"
    out_dir.mkdir(parents=True, exist_ok=False)
    return out_dir


def select_test_cases(args: argparse.Namespace) -> list[Case]:
    datasets = load_cases(args.datasets_dir)
    if args.test_dataset == "all":
        cases = [case for name in sorted(datasets) for case in datasets[name]]
    else:
        if args.test_dataset not in datasets:
            raise ValueError(f"Unknown test dataset {args.test_dataset!r}. Available: {', '.join(sorted(datasets))}")
        cases = datasets[args.test_dataset]
    return select_cases_with_strategy(
        cases,
        limit=args.max_test_cases,
        strategy=args.test_sample_strategy,
        seed=args.sample_seed,
    )


def build_llm_client(args: argparse.Namespace) -> LLMClient:
    return LLMClient(
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        temperature=args.temperature,
        top_p=args.top_p,
        max_tokens=args.max_tokens,
        thinking=args.thinking,
        do_sample=args.do_sample,
        timeout=args.llm_timeout,
        max_retries=args.llm_max_retries,
        retry_initial_wait=args.llm_rate_limit_initial_wait,
        retry_max_wait=args.llm_rate_limit_max_wait,
    )


def generate_with_method(
    *,
    method: str,
    case: Case,
    ape_prompt: str,
    llm_client: LLMClient,
    args: argparse.Namespace,
    method_dir: Path,
) -> str:
    if args.mock_with_gold:
        return extract_plantuml(case.gold_plantuml, wrap_if_needed=True)

    if method == "ape":
        messages = [
            {"role": "system", "content": ape_prompt},
            {"role": "user", "content": f"Input:\n{case.content}\n\nOutput:"},
        ]
    elif method == "lato-zero-shot":
        messages = [
            {"role": "user", "content": LATO_ZERO_SHOT_USER_TEMPLATE.format(Input=case.content)},
        ]
    else:
        raise ValueError(f"Unsupported method: {method}")

    return llm_client.chat(
        messages,
        thinking=args.generation_thinking,
        state_dir=method_dir,
        retry_phase=f"{method}:generate",
        retry_context={"dataset": case.dataset, "case_id": case.case_id},
    )


def evaluate_generated(
    *,
    case: Case,
    generated: str,
    args: argparse.Namespace,
    llm_client: LLMClient,
    method_dir: Path,
    method: str,
) -> EvaluationRecord:
    generated_plantuml = extract_plantuml(generated, wrap_if_needed=False)
    syntax = validate_plantuml(generated, args.plantuml_jar, timeout=args.plantuml_compile_timeout)
    metric_failure_types: list[str] = []
    try:
        gold_graph = extract_graph_for_metrics(
            case.gold_plantuml,
            args=args,
            llm_client=llm_client,
            state_dir=method_dir,
            phase=method,
            role="gold",
            retry_context={"dataset": case.dataset, "case_id": case.case_id},
        )
        pred_graph = extract_graph_for_metrics(
            generated_plantuml,
            args=args,
            llm_client=llm_client,
            state_dir=method_dir,
            phase=method,
            role="prediction",
            retry_context={"dataset": case.dataset, "case_id": case.case_id},
        )
    except Exception:
        gold_graph = extract_activity_graph(case.gold_plantuml)
        pred_graph = ActivityGraph(nodes=[], relations=[])
        metric_failure_types.append("element_extraction_error")
    node_metrics = compute_metric(
        gold_graph.nodes,
        pred_graph.nodes,
        threshold=args.node_match_threshold,
        matcher=args.metric_matcher,
        embedding_model=args.semantic_embedding_model,
    )
    relation_metrics = compute_metric(
        gold_graph.relations,
        pred_graph.relations,
        threshold=args.relation_match_threshold,
        matcher=args.metric_matcher,
        embedding_model=args.semantic_embedding_model,
        item_type="relation",
    )
    plantuml_compilation = check_plantuml_compilation(
        generated_plantuml,
        args.plantuml_jar,
        timeout=args.plantuml_compile_timeout,
    )

    if args.llm_element_metrics:
        llm_element_metrics = evaluate_llm_elements(
            ground_truth=case.gold_plantuml,
            prediction=generated_plantuml,
            enabled=True,
            model=args.llm_judge_model,
            api_key=args.llm_judge_api_key,
            base_url=args.llm_judge_base_url,
            temperature=args.llm_judge_temperature,
            max_tokens=args.llm_judge_max_tokens,
            timeout=args.llm_judge_timeout,
            thinking=args.llm_judge_thinking,
            do_sample=args.do_sample,
            max_retries=args.llm_judge_max_retries,
            state_dir=method_dir,
            retry_phase=f"{method}:llm_judge",
            retry_context={"dataset": case.dataset, "case_id": case.case_id},
            provider_max_retries=args.llm_max_retries,
            retry_initial_wait=args.llm_rate_limit_initial_wait,
            retry_max_wait=args.llm_rate_limit_max_wait,
        )
    else:
        llm_element_metrics = disabled_llm_metrics()

    failure_types = classify_failures(syntax, node_metrics, relation_metrics)
    if llm_element_metrics.status == "error":
        failure_types.append("llm_element_judge_error")
    failure_types.extend(item for item in metric_failure_types if item not in failure_types)

    return EvaluationRecord(
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


def run_method(
    *,
    method: str,
    cases: list[Case],
    ape_prompt: str,
    llm_client: LLMClient,
    args: argparse.Namespace,
    output_dir: Path,
) -> dict[str, float]:
    method_dir = output_dir / method
    method_dir.mkdir(parents=True, exist_ok=True)
    records_path = method_dir / "records.jsonl"
    write_text(records_path, "")

    records: list[EvaluationRecord] = []
    for idx, case in enumerate(cases, start=1):
        print(f"[{method}] {idx}/{len(cases)} {case.case_id}", flush=True)
        try:
            generated = generate_with_method(
                method=method,
                case=case,
                ape_prompt=ape_prompt,
                llm_client=llm_client,
                args=args,
                method_dir=method_dir,
            )
            record = evaluate_generated(
                case=case,
                generated=generated,
                args=args,
                llm_client=llm_client,
                method_dir=method_dir,
                method=method,
            )
        except Exception as exc:
            print(f"[{method}] generation/evaluation failed for {case.case_id}: {exc}", flush=True)
            zero_args = SimpleNamespace(
                llm_element_metrics=False,
            )
            empty = ""
            syntax = validate_plantuml(empty, args.plantuml_jar, timeout=args.plantuml_compile_timeout)
            gold_graph = extract_activity_graph(case.gold_plantuml)
            node_metrics = compute_metric(
                gold_graph.nodes,
                [],
                threshold=args.node_match_threshold,
                matcher=args.metric_matcher,
                embedding_model=args.semantic_embedding_model,
            )
            relation_metrics = compute_metric(
                gold_graph.relations,
                [],
                threshold=args.relation_match_threshold,
                matcher=args.metric_matcher,
                embedding_model=args.semantic_embedding_model,
                item_type="relation",
            )
            record = EvaluationRecord(
                dataset=case.dataset,
                case_id=case.case_id,
                input_requirement=case.content,
                gold_plantuml=case.gold_plantuml,
                generated_plantuml=empty,
                syntax=syntax,
                node_metrics=node_metrics,
                relation_metrics=relation_metrics,
                plantuml_compilation=check_plantuml_compilation(empty, args.plantuml_jar, timeout=args.plantuml_compile_timeout),
                llm_element_metrics=disabled_llm_metrics(),
                failure_types=["generation_error", "syntax_error", "missing_activity", "missing_or_wrong_relation"],
            )
            _ = zero_args
        records.append(record)
        append_jsonl(records_path, dataclasses.asdict(record))

    summary = summarize_records(records)
    write_text(method_dir / "summary.json", json.dumps(summary, ensure_ascii=False, indent=2))
    write_text(method_dir / "summary.txt", format_summary(summary) + "\n")
    return summary


def write_comparison_report(output_dir: Path, summaries: dict[str, dict[str, float]]) -> None:
    keys = [
        "count",
        "syntax_pass_rate",
        "plantuml_compilation_pass_rate",
        "node_precision",
        "node_recall",
        "node_f1",
        "relation_precision",
        "relation_recall",
        "relation_f1",
        "llm_node_f1",
        "llm_relation_f1",
    ]
    lines = ["# LATO Baseline Comparison", ""]
    lines.append("| metric | " + " | ".join(summaries) + " |")
    lines.append("| --- | " + " | ".join("---" for _ in summaries) + " |")
    for key in keys:
        values = []
        for summary in summaries.values():
            value = summary.get(key, 0.0)
            values.append(f"{value:.4f}" if key != "count" else str(int(value)))
        lines.append("| " + key + " | " + " | ".join(values) + " |")
    write_text(output_dir / "comparison.md", "\n".join(lines) + "\n")


def write_run_args(output_dir: Path, args: argparse.Namespace) -> None:
    payload = {}
    for key, value in vars(args).items():
        if key in {"api_key", "llm_judge_api_key"}:
            payload[f"{key}_present"] = bool(value)
        elif isinstance(value, Path):
            payload[key] = str(value)
        else:
            payload[key] = value
    write_text(output_dir / "run_args.json", json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    provider = get_llm_provider_settings()
    parser = argparse.ArgumentParser(description="Evaluate LATO zero-shot and APE prompts with identical APE metrics")
    parser.add_argument("--datasets-dir", type=Path, default=DEFAULT_DATASETS_DIR)
    parser.add_argument("--test-dataset", default="fsd", help="Dataset name, or 'all'")
    parser.add_argument("--max-test-cases", type=int, default=10, help="0 means all selected test cases")
    parser.add_argument("--test-sample-strategy", choices=["prefix", "random", "stratified"], default="prefix")
    parser.add_argument("--sample-seed", type=int, default=13)
    parser.add_argument("--methods", type=parse_methods, default=parse_methods("ape,lato-zero-shot"))
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--runs-dir", type=Path, default=DEFAULT_RUNS_DIR)
    parser.add_argument("--prompt-path", type=Path, default=DEFAULT_PROMPT_PATH)
    parser.add_argument("--plantuml-jar", type=Path, default=DEFAULT_PLANTUML_JAR)
    parser.add_argument("--plantuml-compile-timeout", type=int, default=30)
    parser.add_argument("--model", default=provider.model)
    parser.add_argument("--api-key", default=provider.api_key)
    parser.add_argument("--base-url", default=provider.base_url)
    parser.set_defaults(llm_provider=provider.name, api_key_environment=provider.api_key_environment)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-p", type=float, default=None)
    parser.add_argument("--do-sample", type=optional_bool, default=provider.do_sample)
    parser.add_argument("--max-tokens", type=int, default=12000)
    parser.add_argument("--thinking", choices=["enabled", "disabled"], default=provider.thinking)
    parser.add_argument("--generation-thinking", choices=["inherit", "enabled", "disabled"], default=provider.generation_thinking)
    parser.add_argument("--llm-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-max-retries", type=int, default=20)
    parser.add_argument("--llm-rate-limit-initial-wait", type=int, default=30)
    parser.add_argument("--llm-rate-limit-max-wait", type=int, default=600)
    parser.add_argument("--node-match-threshold", type=float, default=0.85)
    parser.add_argument("--relation-match-threshold", type=float, default=0.85)
    parser.add_argument("--semantic-embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    parser.add_argument("--metric-matcher", choices=["embedding", "difflib"], default="embedding")
    parser.add_argument("--element-extractor", choices=["rule", "llm", "auto"], default=os.environ.get("APE_ELEMENT_EXTRACTOR", "llm"))
    parser.add_argument("--element-extraction-temperature", type=float, default=0.0)
    parser.add_argument("--element-extraction-max-tokens", type=int, default=4096)
    parser.add_argument("--element-extraction-max-retries", type=int, default=3)
    parser.add_argument("--element-extraction-thinking", choices=["inherit", "enabled", "disabled"], default=provider.element_extraction_thinking)
    parser.add_argument("--llm-element-metrics", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--llm-judge-model", default=provider.judge_model or provider.model)
    parser.add_argument("--llm-judge-api-key", default=provider.judge_api_key)
    parser.add_argument("--llm-judge-base-url", default=provider.judge_base_url)
    parser.add_argument("--llm-judge-temperature", type=float, default=0.0)
    parser.add_argument("--llm-judge-max-tokens", type=int, default=4096)
    parser.add_argument("--llm-judge-timeout", type=int, default=DEFAULT_LLM_TIMEOUT)
    parser.add_argument("--llm-judge-max-retries", type=int, default=3)
    parser.add_argument("--llm-judge-thinking", choices=["inherit", "enabled", "disabled"], default=provider.judge_thinking)
    parser.add_argument("--mock-with-gold", action="store_true", help="Use gold PlantUML as generated output to smoke-test the evaluation flow")
    return parser


def normalize_inherited_modes(args: argparse.Namespace) -> None:
    if args.generation_thinking == "inherit":
        args.generation_thinking = args.thinking
    if args.element_extraction_thinking == "inherit":
        args.element_extraction_thinking = args.thinking
    if args.llm_judge_thinking == "inherit":
        args.llm_judge_thinking = args.thinking


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    normalize_inherited_modes(args)

    temperature_fields = (
        "temperature",
        "element_extraction_temperature",
        "llm_judge_temperature",
    )
    nonzero_temperatures = [
        f"--{field.replace('_', '-')}={getattr(args, field)}"
        for field in temperature_fields
        if float(getattr(args, field)) != 0.0
    ]
    if nonzero_temperatures:
        raise RuntimeError(
            "All model temperatures must be 0; rejected "
            + ", ".join(nonzero_temperatures)
        )

    if not args.mock_with_gold and not args.api_key:
        raise RuntimeError("The active provider API key is required unless --mock-with-gold is used.")
    if args.element_extractor == "llm" and not args.api_key:
        raise RuntimeError("The active provider API key is required when --element-extractor llm is used.")
    if args.llm_element_metrics and not args.llm_judge_api_key:
        raise RuntimeError("LLM judge API key is required when --llm-element-metrics is enabled.")
    if getattr(args, "llm_provider", "zhipu") == "deepseek" and args.do_sample is not None:
        raise RuntimeError("DeepSeek does not define do_sample; omit it with --do-sample omit.")

    output_dir = args.output_dir or make_output_dir(args.runs_dir, args.test_dataset)
    output_dir.mkdir(parents=True, exist_ok=True)
    write_run_args(output_dir, args)

    ape_prompt = read_prompt_file(args.prompt_path, label="APE generation")
    write_text(output_dir / "ape_prompt.md", ape_prompt)
    write_text(output_dir / "lato_zero_shot_prompt.txt", LATO_ZERO_SHOT_USER_TEMPLATE)

    cases = select_test_cases(args)
    write_case_manifest(output_dir / "cases.json", cases)
    print(f"[compare] cases={len(cases)}, methods={','.join(args.methods)}, output={output_dir}", flush=True)

    llm_client = build_llm_client(args)
    summaries = {}
    for method in args.methods:
        summaries[method] = run_method(
            method=method,
            cases=cases,
            ape_prompt=ape_prompt,
            llm_client=llm_client,
            args=args,
            output_dir=output_dir,
        )
        print(f"[{method}] {format_summary(summaries[method])}", flush=True)

    write_text(output_dir / "summary.json", json.dumps(summaries, ensure_ascii=False, indent=2))
    write_comparison_report(output_dir, summaries)


if __name__ == "__main__":
    main()
