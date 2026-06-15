"""Batch evaluation workflow."""

from __future__ import annotations

import dataclasses
from pathlib import Path
from typing import Any

from ape_datasets.lato import Case
from llm_element_metrics import check_plantuml_compilation, evaluate_llm_elements
from llm import LLMClient
from metrics import (
    EvaluationRecord,
    SyntaxResult,
    classify_failures,
    compute_metric,
    extract_relations,
    iter_semantic_elements,
    summarize_records,
    validate_plantuml,
)
from prediction import extract_plantuml, generated_from_args
from utils.io import append_jsonl, write_text


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


def evaluate_cases(
    *,
    prompt: str,
    cases: list[Case],
    args: Any,
    llm_client: LLMClient,
    output_path: Path,
    state_dir: Path | None = None,
    phase: str = "eval",
) -> tuple[list[EvaluationRecord], dict[str, float]]:
    write_text(output_path, "")

    records: list[EvaluationRecord] = []
    for idx, case in enumerate(cases, start=1):
        print(f"[eval] {idx}/{len(cases)} {case.case_id}", flush=True)
        try:
            generated = generated_from_args(
                prompt=prompt,
                case=case,
                args=args,
                llm_client=llm_client,
                state_dir=state_dir,
                retry_phase=phase,
            )
        except Exception as exc:
            generated = ""
            syntax = SyntaxResult(False, [f"LLM generation failed: {exc}"])
            gold_nodes = iter_semantic_elements(case.gold_plantuml)
            node_metrics = compute_metric(
                gold_nodes,
                [],
                threshold=args.node_match_threshold,
                matcher=args.metric_matcher,
                embedding_model=args.semantic_embedding_model,
            )
            relation_metrics = compute_metric(
                extract_relations(case.gold_plantuml),
                [],
                threshold=args.relation_match_threshold,
                matcher=args.metric_matcher,
                embedding_model=args.semantic_embedding_model,
                item_type="relation",
            )
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
                matcher=args.metric_matcher,
                embedding_model=args.semantic_embedding_model,
            )
            relation_metrics = compute_metric(
                extract_relations(case.gold_plantuml),
                extract_relations(generated),
                threshold=args.relation_match_threshold,
                matcher=args.metric_matcher,
                embedding_model=args.semantic_embedding_model,
                item_type="relation",
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


def has_only_infrastructure_errors(records: list[EvaluationRecord]) -> bool:
    return bool(records) and all("infrastructure_error" in r.failure_types for r in records)
