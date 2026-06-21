#!/usr/bin/env python3
"""Fair comparison evaluator for LATO workflow baseline vs another method."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
LATO_REPO_DEFAULT = WORKSPACE_ROOT / "LATO"
LATO_EXAMPLES_DIR_DEFAULT = WORKSPACE_ROOT / "HiGenModel" / "HiGenModel" / "baselines" / "prompts" / "lato"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(LATO_REPO_DEFAULT) not in sys.path:
    sys.path.insert(0, str(LATO_REPO_DEFAULT))

from ape_datasets.lato import Case, load_cases, select_cases_with_strategy, write_case_manifest
from config import DEFAULT_DATASETS_DIR, DEFAULT_MODEL, DEFAULT_PLANTUML_JAR
from llm_element_metrics import check_plantuml_compilation
from metrics import (
    DEFAULT_EMBEDDING_MODEL,
    ActivityGraph,
    EvaluationRecord,
    classify_failures,
    compute_metric,
    extract_activity_graph,
    summarize_records,
    validate_plantuml,
)
from prediction import extract_plantuml


def _import_lato():
    from src.utils.config_loader import setup_llm
    from src.workflow import LATO

    return setup_llm, LATO


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate LATO workflow baseline and another method on the same LATO cases."
    )
    parser.add_argument("--datasets-dir", type=Path, default=DEFAULT_DATASETS_DIR)
    parser.add_argument("--test-dataset", default="fsd", help="Dataset name under prompt_datasets/lato, or 'all'")
    parser.add_argument("--max-test-cases", type=int, default=0, help="0 means all selected cases")
    parser.add_argument("--test-sample-strategy", choices=["prefix", "random", "stratified"], default="prefix")
    parser.add_argument("--sample-seed", type=int, default=13)
    parser.add_argument("--case-manifest", type=Path, default=None, help="Optional JSON file with fixed dataset/case_id pairs")
    parser.add_argument("--method-pred", type=Path, required=True, help="Prediction file for your method")
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for report and records")
    parser.add_argument("--baseline-mode", choices=["run-lato-workflow", "read-file"], default="run-lato-workflow")
    parser.add_argument("--baseline-pred", type=Path, default=None, help="Existing baseline prediction file when --baseline-mode read-file")
    parser.add_argument("--baseline-name", default="lato-workflow")
    parser.add_argument("--method-name", default="my-method")
    parser.add_argument("--lato-repo", type=Path, default=LATO_REPO_DEFAULT)
    parser.add_argument("--lato-config", type=Path, default=LATO_REPO_DEFAULT / "src" / "utils" / "args.yaml")
    parser.add_argument("--lato-model", default="deepseek", help=f"Model entry name in args.yaml; its model field/env override can still point to {DEFAULT_MODEL}")
    parser.add_argument("--lato-examples-dir", type=Path, default=LATO_EXAMPLES_DIR_DEFAULT)
    parser.add_argument("--plantuml-jar", type=Path, default=DEFAULT_PLANTUML_JAR)
    parser.add_argument("--plantuml-compile-timeout", type=int, default=30)
    parser.add_argument("--metric-matcher", choices=["embedding", "difflib"], default="embedding")
    parser.add_argument("--node-match-threshold", type=float, default=0.85)
    parser.add_argument("--relation-match-threshold", type=float, default=0.85)
    parser.add_argument("--semantic-embedding-model", default=DEFAULT_EMBEDDING_MODEL)
    return parser.parse_args()


def load_manifest_cases(path: Path, datasets_dir: Path) -> list[Case]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    all_cases = load_cases(datasets_dir)
    index = {(case.dataset, case.case_id): case for cases in all_cases.values() for case in cases}
    selected: list[Case] = []
    for row in payload:
        dataset = str(row["dataset"]).strip().lower()
        case_id = str(row["case_id"]).strip()
        key = (dataset, case_id)
        if key not in index:
            raise KeyError(f"Case not found in datasets: {key}")
        selected.append(index[key])
    if not selected:
        raise ValueError(f"No cases loaded from manifest: {path}")
    return selected


def select_test_cases(args: argparse.Namespace) -> list[Case]:
    if args.case_manifest:
        return load_manifest_cases(args.case_manifest, args.datasets_dir)

    datasets = load_cases(args.datasets_dir)
    if args.test_dataset == "all":
        cases = [case for name in sorted(datasets) for case in datasets[name]]
    else:
        key = args.test_dataset.lower()
        if key not in datasets:
            raise ValueError(f"Unknown test dataset {args.test_dataset!r}. Available: {', '.join(sorted(datasets))}")
        cases = datasets[key]
    return select_cases_with_strategy(
        cases,
        limit=args.max_test_cases,
        strategy=args.test_sample_strategy,
        seed=args.sample_seed,
    )


def normalize_case_text(text: str) -> str:
    return str(text or "").replace("\r\n", "\n").strip()


def normalize_prediction_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        rows: list[dict[str, Any]] = []
        for case_id, value in payload.items():
            if isinstance(value, dict):
                row = dict(value)
                row.setdefault("case_id", str(case_id))
                rows.append(row)
            else:
                rows.append({"case_id": str(case_id), "prediction": str(value)})
        return rows
    if not isinstance(payload, list):
        raise ValueError("Prediction file must be JSON list, JSON dict, or JSONL")
    rows = []
    for item in payload:
        if isinstance(item, dict):
            rows.append(item)
        else:
            rows.append({"prediction": str(item)})
    return rows


def read_json_or_jsonl(path: Path) -> Any:
    if path.suffix.lower() == ".jsonl":
        rows = []
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows
    return json.loads(path.read_text(encoding="utf-8"))


def read_prediction_text(row: dict[str, Any]) -> str:
    for key in ("prediction", "generated_plantuml", "plantuml", "output", "result", "code", "response"):
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value)
    raise KeyError(f"Prediction row missing prediction text keys: {sorted(row)}")


def read_case_id(row: dict[str, Any]) -> str | None:
    for key in ("case_id", "id", "sample_id", "uid"):
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return None


def load_prediction_store(path: Path) -> dict[str, Any]:
    rows = normalize_prediction_payload(read_json_or_jsonl(path))
    by_id: dict[str, str] = {}
    ordered: list[str] = []
    for row in rows:
        prediction = read_prediction_text(row)
        ordered.append(prediction)
        case_id = read_case_id(row)
        if case_id:
            by_id[case_id] = prediction
    return {"by_id": by_id, "ordered": ordered}


def align_predictions(cases: list[Case], store: dict[str, Any], label: str) -> tuple[list[str], str]:
    by_id: dict[str, str] = store["by_id"]
    ordered: list[str] = store["ordered"]
    if all(case.case_id in by_id for case in cases):
        return [by_id[case.case_id] for case in cases], "case_id"
    if len(ordered) == len(cases):
        return ordered, "order"
    missing = [case.case_id for case in cases if case.case_id not in by_id][:5]
    raise ValueError(
        f"Cannot align {label} predictions. Missing case_ids sample={missing}, "
        f"and row count {len(ordered)} != case count {len(cases)}."
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def metric_bundle_to_dict(bundle: Any) -> dict[str, Any]:
    return {
        "precision": bundle.precision,
        "recall": bundle.recall,
        "f1": bundle.f1,
        "missing": bundle.missing,
        "extra": bundle.extra,
        "correct": bundle.correct,
        "gold_count": bundle.gold_count,
        "pred_count": bundle.pred_count,
        "matches": bundle.matches,
        "matcher": bundle.matcher,
    }


def serialize_record(record: EvaluationRecord) -> dict[str, Any]:
    return {
        "dataset": record.dataset,
        "case_id": record.case_id,
        "input_requirement": record.input_requirement,
        "gold_plantuml": record.gold_plantuml,
        "generated_plantuml": record.generated_plantuml,
        "syntax": {"passed": record.syntax.passed, "errors": record.syntax.errors},
        "node_metrics": metric_bundle_to_dict(record.node_metrics),
        "relation_metrics": metric_bundle_to_dict(record.relation_metrics),
        "plantuml_compilation": {
            "passed": record.plantuml_compilation.passed,
            "errors": record.plantuml_compilation.errors,
        },
        "llm_element_metrics": {
            "enabled": record.llm_element_metrics.enabled,
            "status": record.llm_element_metrics.status,
            "error": record.llm_element_metrics.error,
        },
        "failure_types": record.failure_types,
    }


def disabled_llm_metrics():
    from llm_element_metrics import LLMElementMetrics, PRF

    zero = PRF(precision=0.0, recall=0.0, f1=0.0)
    return LLMElementMetrics(
        enabled=False,
        status="disabled",
        node_metrics=zero,
        relation_metrics=zero,
        gt_elements={},
        pred_elements={},
        matching={},
        counts={},
        error=None,
    )


def evaluate_prediction(case: Case, generated: str, args: argparse.Namespace) -> EvaluationRecord:
    generated_plantuml = extract_plantuml(generated, wrap_if_needed=False)
    syntax = validate_plantuml(generated, args.plantuml_jar, timeout=args.plantuml_compile_timeout)

    gold_graph = extract_activity_graph(case.gold_plantuml)
    pred_graph = extract_activity_graph(generated_plantuml)
    if not isinstance(gold_graph, ActivityGraph) or not isinstance(pred_graph, ActivityGraph):
        raise TypeError("Activity graph extraction did not return ActivityGraph")

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
    compilation = check_plantuml_compilation(
        generated_plantuml,
        args.plantuml_jar,
        timeout=args.plantuml_compile_timeout,
    )
    failure_types = classify_failures(syntax, node_metrics, relation_metrics)

    return EvaluationRecord(
        dataset=case.dataset,
        case_id=case.case_id,
        input_requirement=case.content,
        gold_plantuml=case.gold_plantuml,
        generated_plantuml=generated_plantuml,
        syntax=syntax,
        node_metrics=node_metrics,
        relation_metrics=relation_metrics,
        plantuml_compilation=compilation,
        llm_element_metrics=disabled_llm_metrics(),
        failure_types=failure_types,
    )


def generate_lato_workflow_predictions(cases: list[Case], args: argparse.Namespace) -> list[dict[str, str]]:
    if not args.lato_repo.exists():
        raise FileNotFoundError(f"LATO repo not found: {args.lato_repo}")
    if not args.lato_config.exists():
        raise FileNotFoundError(f"LATO config not found: {args.lato_config}")
    if not args.lato_examples_dir.exists():
        raise FileNotFoundError(f"LATO examples dir not found: {args.lato_examples_dir}")

    setup_llm, LATO = _import_lato()
    llm, config = setup_llm(args.lato_model, str(args.lato_config))
    try:
        workflow = LATO(llm, config=config)
    except AttributeError as exc:
        message = str(exc)
        if "all_tied_weights_keys" in message:
            raise RuntimeError(
                "LATO workflow initialization failed because fastcoref is incompatible with the current "
                "transformers version in this environment. The observed symptom is missing "
                "'all_tied_weights_keys' on FCorefModel.\n"
                "Recommended fix: install a compatible transformers 4.x release for the LATO environment, "
                "or generate LATO predictions in a separate dedicated environment first.\n"
                "Example: pip install \"transformers<5\" --upgrade"
            ) from exc
        raise

    rows: list[dict[str, str]] = []
    total = len(cases)
    for idx, case in enumerate(cases, start=1):
        print(f"[{args.baseline_name}] {idx}/{total} {case.case_id}", flush=True)
        prediction = workflow.workflow(case.content, str(args.lato_examples_dir))
        rows.append({"case_id": case.case_id, "prediction": normalize_case_text(prediction)})
    return rows


def compare_summaries(baseline: dict[str, Any], method: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "node_precision",
        "node_recall",
        "node_f1",
        "relation_precision",
        "relation_recall",
        "relation_f1",
        "plantuml_compilation_pass_rate",
    )
    delta: dict[str, Any] = {}
    for key in keys:
        base = baseline.get(key)
        meth = method.get(key)
        delta[f"{key}_delta_method_minus_baseline"] = None if base is None or meth is None else meth - base
    return delta


def main() -> int:
    args = parse_args()
    cases = select_test_cases(args)

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    write_case_manifest(output_dir / "cases.json", cases)

    if args.baseline_mode == "run-lato-workflow":
        baseline_rows = generate_lato_workflow_predictions(cases, args)
        baseline_pred_path = output_dir / f"{args.baseline_name}.predictions.jsonl"
        write_jsonl(baseline_pred_path, baseline_rows)
    else:
        if args.baseline_pred is None:
            raise ValueError("--baseline-pred is required when --baseline-mode read-file")
        baseline_pred_path = args.baseline_pred.resolve()

    method_pred_path = args.method_pred.resolve()
    baseline_predictions, baseline_alignment = align_predictions(
        cases, load_prediction_store(baseline_pred_path), args.baseline_name
    )
    method_predictions, method_alignment = align_predictions(
        cases, load_prediction_store(method_pred_path), args.method_name
    )

    baseline_records = [evaluate_prediction(case, prediction, args) for case, prediction in zip(cases, baseline_predictions)]
    method_records = [evaluate_prediction(case, prediction, args) for case, prediction in zip(cases, method_predictions)]

    baseline_summary = summarize_records(baseline_records)
    method_summary = summarize_records(method_records)
    comparison = compare_summaries(baseline_summary, method_summary)

    baseline_records_path = output_dir / f"{args.baseline_name}.records.jsonl"
    method_records_path = output_dir / f"{args.method_name}.records.jsonl"
    write_jsonl(baseline_records_path, [serialize_record(record) for record in baseline_records])
    write_jsonl(method_records_path, [serialize_record(record) for record in method_records])

    report = {
        "dataset_selection": {
            "datasets_dir": str(args.datasets_dir),
            "test_dataset": args.test_dataset,
            "case_manifest": str(args.case_manifest) if args.case_manifest else None,
            "max_test_cases": args.max_test_cases,
            "test_sample_strategy": args.test_sample_strategy,
            "sample_seed": args.sample_seed,
            "case_count": len(cases),
        },
        "baseline": {
            "name": args.baseline_name,
            "mode": args.baseline_mode,
            "prediction_path": str(baseline_pred_path),
            "alignment_mode": baseline_alignment,
            "lato_repo": str(args.lato_repo),
            "lato_config": str(args.lato_config),
            "lato_model": args.lato_model,
            "lato_examples_dir": str(args.lato_examples_dir),
            "summary": baseline_summary,
            "records_path": str(baseline_records_path),
        },
        "method": {
            "name": args.method_name,
            "prediction_path": str(method_pred_path),
            "alignment_mode": method_alignment,
            "summary": method_summary,
            "records_path": str(method_records_path),
        },
        "metric_config": {
            "plantuml_jar": str(args.plantuml_jar),
            "plantuml_compile_timeout": args.plantuml_compile_timeout,
            "metric_matcher": args.metric_matcher,
            "node_match_threshold": args.node_match_threshold,
            "relation_match_threshold": args.relation_match_threshold,
            "semantic_embedding_model": args.semantic_embedding_model,
        },
        "comparison": comparison,
        "notes": [
            "LATO baseline here refers to src.workflow.LATO.workflow, not zero-shot.",
            "This comparison reuses APE deterministic metrics so both methods are scored under one evaluator.",
            "plantuml_compilation_pass_rate is the retained syntax-validity proxy because compilable PlantUML is the stricter executable artifact check.",
        ],
    }
    write_json(output_dir / "report.json", report)
    print(json.dumps(report["comparison"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
