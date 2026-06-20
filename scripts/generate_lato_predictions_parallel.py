#!/usr/bin/env python3
"""Parallel batch LATO workflow prediction generation.

This script intentionally does not modify generate_lato_predictions.py. It keeps
all JSONL writes in the parent process so multiple workers cannot corrupt output
files.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import queue
import sys
import time
from dataclasses import dataclass
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
from config import DEFAULT_DATASETS_DIR
from utils.io import append_jsonl, write_text


@dataclass
class RunningCase:
    process: mp.Process
    result_queue: mp.Queue
    event_queue: mp.Queue
    case: Case
    dataset_name: str
    idx: int
    total: int
    started: float


def _import_lato():
    from src.utils.config_loader import setup_llm
    from src.workflow import LATO

    return setup_llm, LATO


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def normalize_text(text: str) -> str:
    return str(text or "").replace("\r\n", "\n").strip()


def event_payload(event: str, **fields: Any) -> dict[str, Any]:
    return {"ts": now_iso(), "event": event, **fields}


def print_event(payload: dict[str, Any]) -> None:
    fields = payload
    details = " ".join(
        f"{key}={fields[key]}"
        for key in ("dataset", "case_id", "idx", "total", "worker_slot", "stage", "elapsed_sec", "error_type")
        if key in fields
    )
    print(f"[lato-parallel] {payload['event']}" + (f" {details}" if details else ""), flush=True)


def write_event(path: Path, event: str, **fields: Any) -> None:
    payload = event_payload(event, **fields)
    append_jsonl(path, payload)
    print_event(payload)


def drain_worker_events(event_queue: mp.Queue, progress_path: Path) -> None:
    while True:
        try:
            payload = event_queue.get_nowait()
        except queue.Empty:
            break
        append_jsonl(progress_path, payload)
        print_event(payload)


def existing_case_ids(path: Path) -> set[str]:
    case_ids: set[str] = set()
    if not path.exists():
        return case_ids
    with path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            case_id = payload.get("case_id")
            if isinstance(case_id, str) and case_id.strip():
                case_ids.add(case_id)
    return case_ids


def grouped_cases(cases: list[Case]) -> dict[str, list[Case]]:
    groups: dict[str, list[Case]] = {}
    for case in cases:
        groups.setdefault(case.dataset, []).append(case)
    return groups


def select_test_cases(args: argparse.Namespace) -> list[Case]:
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


def read_example(examples_dir: Path, filename: str) -> str:
    path = examples_dir / filename
    if not path.exists():
        raise FileNotFoundError(f"Example file not found: {path}")
    return path.read_text(encoding="utf-8")


def emit_worker_event(event_queue: mp.Queue, event: str, **fields: Any) -> None:
    event_queue.put(event_payload(event, **fields))


def build_workflow(lato_repo: Path, lato_config: Path, lato_model: str, lato_examples_dir: Path):
    if not lato_repo.exists():
        raise FileNotFoundError(f"LATO repo not found: {lato_repo}")
    if not lato_config.exists():
        raise FileNotFoundError(f"LATO config not found: {lato_config}")
    if not lato_examples_dir.exists():
        raise FileNotFoundError(f"LATO examples dir not found: {lato_examples_dir}")

    setup_llm, LATO = _import_lato()
    llm, config = setup_llm(lato_model, str(lato_config))
    try:
        return LATO(llm, config=config)
    except AttributeError as exc:
        message = str(exc)
        if "all_tied_weights_keys" in message:
            raise RuntimeError(
                "LATO workflow initialization failed because fastcoref is incompatible with the current "
                "transformers version in this environment. The observed symptom is missing "
                "'all_tied_weights_keys' on FCorefModel.\n"
                "Recommended fix: install a compatible transformers 4.x release for the LATO environment, "
                "then rerun this script.\n"
                "Example: pip install \"transformers<5\" --upgrade"
            ) from exc
        raise


def run_lato_workflow_with_stage_events(
    workflow: Any,
    content: str,
    examples_dir: Path,
    event_queue: mp.Queue,
    case_fields: dict[str, Any],
) -> str:
    def run_stage(name: str, callback: Any) -> str:
        started = time.monotonic()
        emit_worker_event(event_queue, "stage_start", stage=name, **case_fields)
        result = callback()
        emit_worker_event(event_queue, "stage_end", stage=name, elapsed_sec=round(time.monotonic() - started, 3), **case_fields)
        return result

    identify_examples = read_example(examples_dir, "identify.txt")
    identify_result = "#Activity Identification\n" + run_stage(
        "activity_identification",
        lambda: workflow.identification.invoke(identify_examples, content),
    )

    decompose_examples = read_example(examples_dir, "decompose.txt")
    decompose_result = "#Relation Decomposition\n" + run_stage(
        "relation_decomposition",
        lambda: workflow.decomposition.invoke(decompose_examples, content + "\n\n"),
    )

    reconstruct_examples = read_example(examples_dir, "reconstruct.txt")
    reconstruct_input = content + "\n\n" + identify_result + "\n\n" + decompose_result + "\n\n"
    reconstruct_result = "#Information Integration\n" + run_stage(
        "information_integration",
        lambda: workflow.reconstruction.invoke(reconstruct_examples, reconstruct_input),
    )

    generate_examples = read_example(examples_dir, "generate.txt")
    generate_input = content + "\n\n" + reconstruct_result + "\n\n"
    return run_stage(
        "generation",
        lambda: workflow.generation.invoke(generate_examples, generate_input),
    )


def case_worker(payload: dict[str, Any], result_queue: mp.Queue, event_queue: mp.Queue) -> None:
    case_fields = payload["case_fields"]
    try:
        emit_worker_event(event_queue, "worker_start", **case_fields)
        workflow = build_workflow(
            Path(payload["lato_repo"]),
            Path(payload["lato_config"]),
            payload["lato_model"],
            Path(payload["lato_examples_dir"]),
        )
        emit_worker_event(event_queue, "workflow_ready", **case_fields)
        prediction = run_lato_workflow_with_stage_events(
            workflow,
            payload["content"],
            Path(payload["lato_examples_dir"]),
            event_queue,
            case_fields,
        )
        result_queue.put({"ok": True, "prediction": normalize_text(prediction)})
    except BaseException as exc:
        result_queue.put({"ok": False, "error_type": type(exc).__name__, "error": str(exc)})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate reusable LATO workflow predictions with parallel case workers.")
    parser.add_argument("--datasets-dir", type=Path, default=DEFAULT_DATASETS_DIR)
    parser.add_argument("--test-dataset", default="all", help="Dataset name under prompt_datasets/lato, or 'all'")
    parser.add_argument("--max-test-cases", type=int, default=0, help="0 means all selected cases")
    parser.add_argument("--test-sample-strategy", choices=["prefix", "random", "stratified"], default="prefix")
    parser.add_argument("--sample-seed", type=int, default=13)
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory to store generated predictions and manifest")
    parser.add_argument("--lato-repo", type=Path, default=LATO_REPO_DEFAULT)
    parser.add_argument("--lato-config", type=Path, default=LATO_REPO_DEFAULT / "src" / "utils" / "args.yaml")
    parser.add_argument("--lato-model", default="deepseek")
    parser.add_argument("--lato-examples-dir", type=Path, default=LATO_EXAMPLES_DIR_DEFAULT)
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing dataset prediction files")
    parser.add_argument("--resume", action=argparse.BooleanOptionalAction, default=True, help="Skip case_ids already present in existing prediction files")
    parser.add_argument("--case-timeout-seconds", type=int, default=1800, help="Per-case wall-clock timeout; 0 disables the timeout")
    parser.add_argument("--continue-on-error", action=argparse.BooleanOptionalAction, default=True, help="Write failed cases to errors.jsonl and continue")
    parser.add_argument("--workers", type=int, default=2, help="Number of case workers to run concurrently")
    return parser.parse_args()


def selected_cases_by_dataset(
    args: argparse.Namespace,
    cases_by_dataset: dict[str, list[Case]],
    progress_path: Path,
) -> dict[str, list[tuple[int, int, Case]]]:
    selected: dict[str, list[tuple[int, int, Case]]] = {}
    for dataset_name, dataset_cases in sorted(cases_by_dataset.items()):
        out_path = args.output_dir / f"{dataset_name}.jsonl"
        if out_path.exists() and args.overwrite:
            write_text(out_path, "")
        elif out_path.exists() and not args.resume:
            raise FileExistsError(f"Prediction file already exists: {out_path}. Use --overwrite to replace it.")
        elif not out_path.exists():
            write_text(out_path, "")

        completed = existing_case_ids(out_path) if args.resume else set()
        total = len(dataset_cases)
        rows: list[tuple[int, int, Case]] = []
        for idx, case in enumerate(dataset_cases, start=1):
            if case.case_id in completed:
                write_event(progress_path, "case_skip_existing", dataset=dataset_name, case_id=case.case_id, idx=idx, total=total)
                continue
            rows.append((idx, total, case))
        selected[dataset_name] = rows
    return selected


def start_case(
    *,
    ctx: Any,
    args: argparse.Namespace,
    case: Case,
    dataset_name: str,
    idx: int,
    total: int,
    worker_slot: int,
    progress_path: Path,
) -> RunningCase:
    case_fields = {
        "dataset": dataset_name,
        "case_id": case.case_id,
        "idx": idx,
        "total": total,
        "worker_slot": worker_slot,
    }
    write_event(progress_path, "case_start", **case_fields)
    result_queue: mp.Queue = ctx.Queue()
    event_queue: mp.Queue = ctx.Queue()
    payload = {
        "lato_repo": str(args.lato_repo),
        "lato_config": str(args.lato_config),
        "lato_model": args.lato_model,
        "lato_examples_dir": str(args.lato_examples_dir),
        "content": case.content,
        "case_fields": case_fields,
    }
    process = ctx.Process(target=case_worker, args=(payload, result_queue, event_queue))
    process.start()
    return RunningCase(process, result_queue, event_queue, case, dataset_name, idx, total, time.monotonic())


def terminate_case(running: RunningCase) -> None:
    if running.process.is_alive():
        running.process.terminate()
        running.process.join(10)
    if running.process.is_alive():
        running.process.kill()
        running.process.join(10)


def finish_case(
    *,
    running: RunningCase,
    result: dict[str, Any],
    progress_path: Path,
    errors_path: Path,
    out_paths: dict[str, Path],
    continue_on_error: bool,
) -> None:
    drain_worker_events(running.event_queue, progress_path)
    elapsed = round(time.monotonic() - running.started, 3)
    if result.get("ok"):
        append_jsonl(
            out_paths[running.dataset_name],
            {
                "dataset": running.case.dataset,
                "case_id": running.case.case_id,
                "input_requirement": running.case.content,
                "prediction": normalize_text(result.get("prediction", "")),
                "elapsed_sec": elapsed,
            },
        )
        write_event(
            progress_path,
            "case_success",
            dataset=running.dataset_name,
            case_id=running.case.case_id,
            idx=running.idx,
            total=running.total,
            elapsed_sec=elapsed,
        )
        return

    error_row = {
        "dataset": running.case.dataset,
        "case_id": running.case.case_id,
        "input_requirement": running.case.content,
        "error_type": result.get("error_type", "Error"),
        "error": result.get("error", "unknown error"),
        "elapsed_sec": elapsed,
    }
    append_jsonl(errors_path, error_row)
    write_event(
        progress_path,
        "case_error",
        dataset=running.dataset_name,
        case_id=running.case.case_id,
        idx=running.idx,
        total=running.total,
        elapsed_sec=elapsed,
        error_type=error_row["error_type"],
    )
    if not continue_on_error:
        raise RuntimeError(f"LATO failed for {running.case.case_id}: {error_row['error']}")


def write_run_args(
    args: argparse.Namespace,
    output_dir: Path,
    all_counts: dict[str, int],
    queued: dict[str, list[tuple[int, int, Case]]],
) -> None:
    metadata = {
        "datasets_dir": str(args.datasets_dir),
        "test_dataset": args.test_dataset,
        "max_test_cases": args.max_test_cases,
        "test_sample_strategy": args.test_sample_strategy,
        "sample_seed": args.sample_seed,
        "lato_repo": str(args.lato_repo),
        "lato_config": str(args.lato_config),
        "lato_model": args.lato_model,
        "lato_examples_dir": str(args.lato_examples_dir),
        "resume": args.resume,
        "case_timeout_seconds": args.case_timeout_seconds,
        "continue_on_error": args.continue_on_error,
        "workers": args.workers,
        "datasets": all_counts,
        "queued_after_resume": {name: len(items) for name, items in sorted(queued.items())},
    }
    write_text(output_dir / "run_args.json", json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")


def main() -> int:
    args = parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    if args.case_timeout_seconds < 0:
        raise ValueError("--case-timeout-seconds must be >= 0")

    args.output_dir = args.output_dir.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    progress_path = args.output_dir / "progress.jsonl"
    errors_path = args.output_dir / "errors.jsonl"

    cases = select_test_cases(args)
    cases_by_dataset = grouped_cases(cases)
    all_counts = {name: len(items) for name, items in sorted(cases_by_dataset.items())}
    write_case_manifest(args.output_dir / "cases.json", cases)
    selected = selected_cases_by_dataset(args, cases_by_dataset, progress_path)
    write_run_args(args, args.output_dir, all_counts, selected)
    out_paths = {dataset_name: args.output_dir / f"{dataset_name}.jsonl" for dataset_name in selected}
    pending: list[tuple[str, int, int, Case]] = [
        (dataset_name, idx, total, case)
        for dataset_name, rows in selected.items()
        for idx, total, case in rows
    ]
    total_pending = len(pending)
    write_event(progress_path, "run_start", output_dir=str(args.output_dir), total_cases=total_pending, workers=args.workers)
    if not pending:
        write_event(progress_path, "run_end", output_dir=str(args.output_dir))
        return 0

    ctx = mp.get_context("spawn")
    running: list[RunningCase] = []
    next_worker_slot = 1

    try:
        while pending or running:
            while pending and len(running) < args.workers:
                dataset_name, idx, total, case = pending.pop(0)
                running.append(
                    start_case(
                        ctx=ctx,
                        args=args,
                        case=case,
                        dataset_name=dataset_name,
                        idx=idx,
                        total=total,
                        worker_slot=next_worker_slot,
                        progress_path=progress_path,
                    )
                )
                next_worker_slot += 1

            for item in list(running):
                drain_worker_events(item.event_queue, progress_path)
                elapsed = time.monotonic() - item.started
                if args.case_timeout_seconds > 0 and elapsed >= args.case_timeout_seconds and item.process.is_alive():
                    terminate_case(item)
                    running.remove(item)
                    finish_case(
                        running=item,
                        result={
                            "ok": False,
                            "error_type": "TimeoutError",
                            "error": f"LATO workflow exceeded {args.case_timeout_seconds} seconds",
                        },
                        progress_path=progress_path,
                        errors_path=errors_path,
                        out_paths=out_paths,
                        continue_on_error=args.continue_on_error,
                    )
                    continue

                if item.process.is_alive():
                    continue

                item.process.join()
                if not item.result_queue.empty():
                    result = item.result_queue.get()
                elif item.process.exitcode == 0:
                    result = {"ok": False, "error_type": "RuntimeError", "error": "LATO worker exited without returning a result"}
                else:
                    result = {"ok": False, "error_type": "RuntimeError", "error": f"LATO worker exited with code {item.process.exitcode}"}
                running.remove(item)
                finish_case(
                    running=item,
                    result=result,
                    progress_path=progress_path,
                    errors_path=errors_path,
                    out_paths=out_paths,
                    continue_on_error=args.continue_on_error,
                )

            time.sleep(0.2)
    finally:
        for item in running:
            terminate_case(item)
            drain_worker_events(item.event_queue, progress_path)

    write_event(progress_path, "run_end", output_dir=str(args.output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
