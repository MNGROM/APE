#!/usr/bin/env python3
"""Batch-generate LATO workflow predictions for all selected datasets."""

from __future__ import annotations

import argparse
import importlib
import json
import multiprocessing as mp
import re
import sys
import time
from pathlib import Path
from textwrap import shorten
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


def _import_lato(
    progress_path: Path | None = None,
    case_fields: dict[str, Any] | None = None,
    diagnostic_logs: bool = False,
):
    modules = [
        "src.utils.config_loader",
        "src.utils.prompt_manager",
        "src.modules.extract",
        "src.modules.construct",
        "src.modules.integrate",
        "src.modules.identify",
        "src.workflow",
    ]
    imported = {}
    for module_name in modules:
        started = time.monotonic()
        log_build_detail(
            progress_path,
            case_fields,
            diagnostic_logs,
            "module_import_start",
            step="build_workflow",
            module_name=module_name,
        )
        try:
            imported[module_name] = importlib.import_module(module_name)
        except BaseException as exc:
            log_build_detail(
                progress_path,
                case_fields,
                diagnostic_logs,
                "module_import_error",
                step="build_workflow",
                module_name=module_name,
                elapsed_sec=round(time.monotonic() - started, 3),
                error_type=type(exc).__name__,
                error=summarize_error(exc),
            )
            raise
        log_build_detail(
            progress_path,
            case_fields,
            diagnostic_logs,
            "module_import_end",
            step="build_workflow",
            module_name=module_name,
            elapsed_sec=round(time.monotonic() - started, 3),
        )

    return imported["src.utils.config_loader"].setup_llm, imported["src.workflow"].LATO


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    append_jsonl(path, payload)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def log_event(path: Path, event: str, **fields: Any) -> None:
    payload = {"ts": _now(), "event": event, **fields}
    _append_jsonl(path, payload)
    printable_keys = {
        "dataset",
        "case_id",
        "idx",
        "total",
        "stage",
        "step",
        "module_name",
        "prompt_name",
        "example_file",
        "llm_call_id",
        "prompt_kind",
        "decompose_level",
        "dependency_lines",
        "elapsed_sec",
        "input_chars",
        "output_chars",
        "ok",
        "error_type",
    }
    details = " ".join(
        f"{key}={value}"
        for key, value in fields.items()
        if key in printable_keys
    )
    print(f"[lato-log] {event}" + (f" {details}" if details else ""), flush=True)


def make_diagnostic(progress_path: Path, case_fields: dict[str, Any], enabled: bool) -> dict[str, Any]:
    return {
        "progress_path": progress_path,
        "case_fields": dict(case_fields),
        "enabled": enabled,
        "stage": None,
        "llm_call_id": 0,
    }


def log_detail(diagnostic: dict[str, Any] | None, event: str, **fields: Any) -> None:
    if not diagnostic or not diagnostic.get("enabled", False):
        return
    payload = dict(diagnostic["case_fields"])
    stage = diagnostic.get("stage")
    if stage and "stage" not in fields:
        payload["stage"] = stage
    payload.update(fields)
    log_event(diagnostic["progress_path"], event, **payload)


def log_build_detail(
    progress_path: Path | None,
    case_fields: dict[str, Any] | None,
    enabled: bool,
    event: str,
    **fields: Any,
) -> None:
    if not enabled or progress_path is None:
        return
    payload = dict(case_fields or {})
    payload.update(fields)
    log_event(progress_path, event, **payload)


def summarize_error(exc: BaseException) -> str:
    return shorten(str(exc).replace("\n", " "), width=500, placeholder="...")


def output_text_length(result: Any) -> int:
    content = getattr(result, "content", result)
    return len(str(content or ""))


def llm_input_to_text(value: Any) -> str:
    if value is None:
        return ""
    if hasattr(value, "to_string"):
        try:
            return str(value.to_string())
        except Exception:
            pass
    messages = getattr(value, "messages", None)
    if messages is not None:
        parts = []
        for message in messages:
            parts.append(str(getattr(message, "content", message)))
        return "\n".join(parts)
    if isinstance(value, list):
        return "\n".join(str(getattr(item, "content", item)) for item in value)
    return str(value)


def classify_llm_prompt(prompt_text: str) -> str:
    if "CoReference Information" in prompt_text:
        return "identify_calibrate"
    if "#Dependency Tree:" in prompt_text:
        return "decompose_verify"
    if "Please output the result for the current Layer" in prompt_text:
        return "decompose_layer"
    if "Integrate the identified activities" in prompt_text:
        return "reconstruct"
    if "Errors found during validation" in prompt_text or "Original TASK:" in prompt_text:
        return "generate_regenerate"
    if "Generate the PlantUML code" in prompt_text or "produce valid PlantUML" in prompt_text:
        return "generate"
    if "Identify **all** atomic activity" in prompt_text:
        return "identify"
    return "unknown"


def llm_prompt_metadata(prompt_text: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {"prompt_kind": classify_llm_prompt(prompt_text)}
    level_match = re.search(r"Level\s+[-–]\s+Level\s+(\d+)", prompt_text)
    if level_match:
        metadata["decompose_level"] = int(level_match.group(1))
    if "#Dependency Tree:" in prompt_text:
        dependency_text = prompt_text.split("#Dependency Tree:", 1)[1]
        metadata["dependency_chars"] = len(dependency_text.strip())
        metadata["dependency_lines"] = len([line for line in dependency_text.splitlines() if line.strip()])
    return metadata


def install_build_diagnostics(progress_path: Path | None, case_fields: dict[str, Any] | None, enabled: bool) -> None:
    if not enabled:
        return

    import src.modules.identify as identify_module
    import src.utils.prompt_manager as prompt_manager_module

    identify_module._ape_build_progress_path = progress_path
    identify_module._ape_build_case_fields = dict(case_fields or {})
    identify_module._ape_build_enabled = enabled

    if not hasattr(identify_module, "_ape_original_FCoref"):
        identify_module._ape_original_FCoref = identify_module.FCoref

        def FCoref_with_diagnostics(*args: Any, **kwargs: Any):
            started = time.monotonic()
            path = getattr(identify_module, "_ape_build_progress_path", None)
            fields = getattr(identify_module, "_ape_build_case_fields", {})
            is_enabled = bool(getattr(identify_module, "_ape_build_enabled", False))
            device = kwargs.get("device")
            if device is None and args:
                device = args[0]
            log_build_detail(path, fields, is_enabled, "coref_model_init_start", step="build_workflow", device=device)
            try:
                model = identify_module._ape_original_FCoref(*args, **kwargs)
            except BaseException as exc:
                log_build_detail(
                    path,
                    fields,
                    is_enabled,
                    "coref_model_init_error",
                    step="build_workflow",
                    elapsed_sec=round(time.monotonic() - started, 3),
                    error_type=type(exc).__name__,
                    error=summarize_error(exc),
                )
                raise
            log_build_detail(
                path,
                fields,
                is_enabled,
                "coref_model_init_end",
                step="build_workflow",
                elapsed_sec=round(time.monotonic() - started, 3),
            )
            return model

        identify_module.FCoref = FCoref_with_diagnostics

    prompt_manager_module._ape_build_progress_path = progress_path
    prompt_manager_module._ape_build_case_fields = dict(case_fields or {})
    prompt_manager_module._ape_build_enabled = enabled

    if not hasattr(prompt_manager_module.PromptManager, "_ape_original_load_prompt"):
        prompt_manager_module.PromptManager._ape_original_load_prompt = prompt_manager_module.PromptManager.load_prompt

        def load_prompt_with_diagnostics(self: Any, prompt_name: str):
            started = time.monotonic()
            path = getattr(prompt_manager_module, "_ape_build_progress_path", None)
            fields = getattr(prompt_manager_module, "_ape_build_case_fields", {})
            is_enabled = bool(getattr(prompt_manager_module, "_ape_build_enabled", False))
            log_build_detail(
                path,
                fields,
                is_enabled,
                "prompt_load_start",
                step="build_workflow",
                prompt_name=prompt_name,
            )
            try:
                prompt = self._ape_original_load_prompt(prompt_name)
            except BaseException as exc:
                log_build_detail(
                    path,
                    fields,
                    is_enabled,
                    "prompt_load_error",
                    step="build_workflow",
                    prompt_name=prompt_name,
                    elapsed_sec=round(time.monotonic() - started, 3),
                    error_type=type(exc).__name__,
                    error=summarize_error(exc),
                )
                raise
            log_build_detail(
                path,
                fields,
                is_enabled,
                "prompt_load_end",
                step="build_workflow",
                prompt_name=prompt_name,
                elapsed_sec=round(time.monotonic() - started, 3),
            )
            return prompt

        prompt_manager_module.PromptManager.load_prompt = load_prompt_with_diagnostics


def install_module_diagnostics(diagnostic: dict[str, Any]) -> None:
    import src.modules.construct as construct_module
    import src.modules.extract as extract_module

    if not hasattr(extract_module, "_ape_original_getTree"):
        extract_module._ape_original_getTree = extract_module.getTree

        def getTree_with_diagnostics(data: str, host: str = "http://localhost", port: int = 9000, timeout: int = 30000):
            diag = getattr(extract_module, "_ape_lato_diagnostic", None)
            started = time.monotonic()
            log_detail(
                diag,
                "corenlp_start",
                step="dependency_tree",
                input_chars=len(str(data or "")),
                corenlp_host=host,
                corenlp_port=port,
                corenlp_timeout_ms=timeout,
            )
            try:
                result = extract_module._ape_original_getTree(data, host=host, port=port, timeout=timeout)
            except BaseException as exc:
                log_detail(
                    diag,
                    "corenlp_error",
                    step="dependency_tree",
                    elapsed_sec=round(time.monotonic() - started, 3),
                    error_type=type(exc).__name__,
                    error=summarize_error(exc),
                )
                raise
            log_detail(
                diag,
                "corenlp_end",
                step="dependency_tree",
                elapsed_sec=round(time.monotonic() - started, 3),
                output_chars=len(str(result or "")),
                dependency_lines=len(str(result or "").splitlines()),
            )
            return result

        extract_module.getTree = getTree_with_diagnostics

    if not hasattr(construct_module, "_ape_original_validate_uml_with_syntax_check"):
        construct_module._ape_original_validate_uml_with_syntax_check = construct_module.validate_uml_with_syntax_check

        def validate_uml_with_diagnostics(uml_code: str, config: Any = None):
            diag = getattr(construct_module, "_ape_lato_diagnostic", None)
            started = time.monotonic()
            log_detail(
                diag,
                "plantuml_syntax_start",
                step="syntax_check",
                input_chars=len(str(uml_code or "")),
            )
            try:
                ok, errors = construct_module._ape_original_validate_uml_with_syntax_check(uml_code, config)
            except BaseException as exc:
                log_detail(
                    diag,
                    "plantuml_syntax_error",
                    step="syntax_check",
                    elapsed_sec=round(time.monotonic() - started, 3),
                    error_type=type(exc).__name__,
                    error=summarize_error(exc),
                )
                raise
            log_detail(
                diag,
                "plantuml_syntax_end",
                step="syntax_check",
                elapsed_sec=round(time.monotonic() - started, 3),
                ok=bool(ok),
                error_count=len(errors or []),
                first_error=shorten(str((errors or [""])[0]), width=300, placeholder="...") if errors else "",
            )
            return ok, errors

        construct_module.validate_uml_with_syntax_check = validate_uml_with_diagnostics

    extract_module._ape_lato_diagnostic = diagnostic
    construct_module._ape_lato_diagnostic = diagnostic


def install_workflow_diagnostics(workflow: Any, diagnostic: dict[str, Any]) -> None:
    if not diagnostic.get("enabled", False):
        return

    install_module_diagnostics(diagnostic)

    llm = workflow.identification.llm
    original_invoke = llm.invoke

    def invoke_with_diagnostics(*args: Any, **kwargs: Any):
        diagnostic["llm_call_id"] += 1
        call_id = diagnostic["llm_call_id"]
        prompt_text = llm_input_to_text(args[0] if args else kwargs.get("input"))
        prompt_fields = llm_prompt_metadata(prompt_text)
        started = time.monotonic()
        log_detail(
            diagnostic,
            "llm_call_start",
            step="llm",
            llm_call_id=call_id,
            input_chars=len(prompt_text),
            **prompt_fields,
        )
        try:
            result = original_invoke(*args, **kwargs)
        except BaseException as exc:
            log_detail(
                diagnostic,
                "llm_call_error",
                step="llm",
                llm_call_id=call_id,
                elapsed_sec=round(time.monotonic() - started, 3),
                error_type=type(exc).__name__,
                error=summarize_error(exc),
                **prompt_fields,
            )
            raise
        log_detail(
            diagnostic,
            "llm_call_end",
            step="llm",
            llm_call_id=call_id,
            elapsed_sec=round(time.monotonic() - started, 3),
            output_chars=output_text_length(result),
            **prompt_fields,
        )
        return result

    try:
        llm.invoke = invoke_with_diagnostics
    except Exception:
        object.__setattr__(llm, "invoke", invoke_with_diagnostics)

    coref_model = getattr(workflow.identification, "model", None)
    if coref_model is not None and hasattr(coref_model, "predict"):
        original_predict = coref_model.predict

        def predict_with_diagnostics(*args: Any, **kwargs: Any):
            texts = kwargs.get("texts")
            if texts is None and args:
                texts = args[0]
            text_count = len(texts) if isinstance(texts, list) else 0
            input_chars = sum(len(str(item or "")) for item in texts) if isinstance(texts, list) else 0
            started = time.monotonic()
            log_detail(
                diagnostic,
                "coref_start",
                step="coreference",
                input_chars=input_chars,
                text_count=text_count,
            )
            try:
                result = original_predict(*args, **kwargs)
            except BaseException as exc:
                log_detail(
                    diagnostic,
                    "coref_error",
                    step="coreference",
                    elapsed_sec=round(time.monotonic() - started, 3),
                    error_type=type(exc).__name__,
                    error=summarize_error(exc),
                )
                raise
            log_detail(
                diagnostic,
                "coref_end",
                step="coreference",
                elapsed_sec=round(time.monotonic() - started, 3),
                result_count=len(result) if hasattr(result, "__len__") else None,
            )
            return result

        try:
            coref_model.predict = predict_with_diagnostics
        except Exception:
            object.__setattr__(coref_model, "predict", predict_with_diagnostics)

    workflow._ape_lato_diagnostic = diagnostic


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


def run_lato_workflow_with_stage_logs(
    workflow: Any,
    content: str,
    examples_dir: Path,
    progress_path: Path,
    case_fields: dict[str, Any],
    diagnostic: dict[str, Any] | None = None,
) -> str:
    def read_example(filename: str) -> str:
        path = examples_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Example file not found: {path}")
        started = time.monotonic()
        log_detail(diagnostic, "example_read_start", step="read_example", example_file=filename)
        text = path.read_text(encoding="utf-8")
        log_detail(
            diagnostic,
            "example_read_end",
            step="read_example",
            example_file=filename,
            elapsed_sec=round(time.monotonic() - started, 3),
            output_chars=len(text),
        )
        return text

    def run_stage(name: str, callback: Any) -> str:
        started = time.monotonic()
        if diagnostic is not None:
            diagnostic["stage"] = name
        log_event(progress_path, "stage_start", stage=name, **case_fields)
        try:
            result = callback()
        except BaseException as exc:
            log_event(
                progress_path,
                "stage_error",
                stage=name,
                elapsed_sec=round(time.monotonic() - started, 3),
                error_type=type(exc).__name__,
                error=summarize_error(exc),
                **case_fields,
            )
            raise
        finally:
            if diagnostic is not None:
                diagnostic["stage"] = None
        log_event(
            progress_path,
            "stage_end",
            stage=name,
            elapsed_sec=round(time.monotonic() - started, 3),
            output_chars=output_text_length(result),
            **case_fields,
        )
        return result

    log_detail(diagnostic, "workflow_input", step="workflow", input_chars=len(content))
    identify_examples = read_example("identify.txt")
    identify_result = "#Activity Identification\n" + run_stage(
        "activity_identification",
        lambda: workflow.identification.invoke(identify_examples, content),
    )

    decompose_examples = read_example("decompose.txt")
    decompose_input = content + "\n\n"
    decompose_result = "#Relation Decomposition\n" + run_stage(
        "relation_decomposition",
        lambda: workflow.decomposition.invoke(decompose_examples, decompose_input),
    )

    reconstruct_examples = read_example("reconstruct.txt")
    reconstruct_input = content + "\n\n" + identify_result + "\n\n" + decompose_result + "\n\n"
    reconstruct_result = "#Information Integration\n" + run_stage(
        "information_integration",
        lambda: workflow.reconstruction.invoke(reconstruct_examples, reconstruct_input),
    )

    generate_examples = read_example("generate.txt")
    generate_input = content + "\n\n" + reconstruct_result + "\n\n"
    return run_stage(
        "generation",
        lambda: workflow.generation.invoke(generate_examples, generate_input),
    )


def _run_case_worker(payload: dict[str, Any], queue: mp.Queue) -> None:
    try:
        class Args:
            pass

        worker_args = Args()
        worker_args.lato_repo = Path(payload["lato_repo"])
        worker_args.lato_config = Path(payload["lato_config"])
        worker_args.lato_model = payload["lato_model"]
        worker_args.lato_examples_dir = Path(payload["lato_examples_dir"])
        progress_path = Path(payload["progress_path"])
        case_fields = payload["case_fields"]
        diagnostic = make_diagnostic(progress_path, case_fields, bool(payload.get("diagnostic_logs", True)))
        log_event(progress_path, "worker_start", **case_fields)
        workflow = build_workflow(worker_args, progress_path=progress_path, case_fields=case_fields, diagnostic_logs=diagnostic["enabled"])
        install_workflow_diagnostics(workflow, diagnostic)
        log_event(progress_path, "workflow_ready", **case_fields)
        prediction = run_lato_workflow_with_stage_logs(
            workflow,
            payload["content"],
            worker_args.lato_examples_dir,
            progress_path,
            case_fields,
            diagnostic,
        )
        queue.put({"ok": True, "prediction": normalize_text(prediction)})
    except BaseException as exc:
        queue.put({"ok": False, "error_type": type(exc).__name__, "error": str(exc)})


def run_case_with_timeout(
    case: Case,
    args: argparse.Namespace,
    timeout_seconds: int,
    progress_path: Path,
    case_fields: dict[str, Any],
) -> dict[str, Any]:
    payload = {
        "lato_repo": str(args.lato_repo),
        "lato_config": str(args.lato_config),
        "lato_model": args.lato_model,
        "lato_examples_dir": str(args.lato_examples_dir),
        "content": case.content,
        "progress_path": str(progress_path),
        "case_fields": case_fields,
        "diagnostic_logs": args.diagnostic_logs,
    }
    queue: mp.Queue = mp.Queue()
    process = mp.Process(target=_run_case_worker, args=(payload, queue))
    process.start()
    process.join(timeout_seconds)
    if process.is_alive():
        process.terminate()
        process.join(10)
        if process.is_alive():
            process.kill()
            process.join(10)
        return {
            "ok": False,
            "error_type": "TimeoutError",
            "error": f"LATO workflow exceeded {timeout_seconds} seconds",
        }
    if not queue.empty():
        return queue.get()
    if process.exitcode == 0:
        return {"ok": False, "error_type": "RuntimeError", "error": "LATO worker exited without returning a result"}
    return {"ok": False, "error_type": "RuntimeError", "error": f"LATO worker exited with code {process.exitcode}"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate reusable LATO workflow predictions for LATO datasets.")
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
    parser.add_argument("--diagnostic-logs", action=argparse.BooleanOptionalAction, default=True, help="Write fine-grained timing events to progress.jsonl")
    return parser.parse_args()


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


def grouped_cases(cases: list[Case]) -> dict[str, list[Case]]:
    groups: dict[str, list[Case]] = {}
    for case in cases:
        groups.setdefault(case.dataset, []).append(case)
    return groups


def normalize_text(text: str) -> str:
    return str(text or "").replace("\r\n", "\n").strip()


def build_workflow(
    args: argparse.Namespace,
    *,
    progress_path: Path | None = None,
    case_fields: dict[str, Any] | None = None,
    diagnostic_logs: bool = False,
):
    if not args.lato_repo.exists():
        raise FileNotFoundError(f"LATO repo not found: {args.lato_repo}")
    if not args.lato_config.exists():
        raise FileNotFoundError(f"LATO config not found: {args.lato_config}")
    if not args.lato_examples_dir.exists():
        raise FileNotFoundError(f"LATO examples dir not found: {args.lato_examples_dir}")

    started = time.monotonic()
    log_build_detail(progress_path, case_fields, diagnostic_logs, "lato_import_start", step="build_workflow")
    setup_llm, LATO = _import_lato(progress_path, case_fields, diagnostic_logs)
    install_build_diagnostics(progress_path, case_fields, diagnostic_logs)
    log_build_detail(
        progress_path,
        case_fields,
        diagnostic_logs,
        "lato_import_end",
        step="build_workflow",
        elapsed_sec=round(time.monotonic() - started, 3),
    )

    started = time.monotonic()
    log_build_detail(
        progress_path,
        case_fields,
        diagnostic_logs,
        "llm_setup_start",
        step="build_workflow",
        lato_model=args.lato_model,
    )
    llm, config = setup_llm(args.lato_model, str(args.lato_config))
    log_build_detail(
        progress_path,
        case_fields,
        diagnostic_logs,
        "llm_setup_end",
        step="build_workflow",
        elapsed_sec=round(time.monotonic() - started, 3),
    )

    try:
        started = time.monotonic()
        log_build_detail(progress_path, case_fields, diagnostic_logs, "workflow_init_start", step="build_workflow")
        workflow = LATO(llm, config=config)
        log_build_detail(
            progress_path,
            case_fields,
            diagnostic_logs,
            "workflow_init_end",
            step="build_workflow",
            elapsed_sec=round(time.monotonic() - started, 3),
        )
        return workflow
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


def main() -> int:
    args = parse_args()
    cases = select_test_cases(args)
    by_dataset = grouped_cases(cases)

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    write_case_manifest(output_dir / "cases.json", cases)

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
        "diagnostic_logs": args.diagnostic_logs,
        "datasets": {name: len(items) for name, items in sorted(by_dataset.items())},
    }
    write_text(output_dir / "run_args.json", json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")
    progress_path = output_dir / "progress.jsonl"
    errors_path = output_dir / "errors.jsonl"
    log_event(progress_path, "run_start", output_dir=str(output_dir), total_cases=len(cases))

    for dataset_name, dataset_cases in sorted(by_dataset.items()):
        out_path = output_dir / f"{dataset_name}.jsonl"
        if out_path.exists() and args.overwrite:
            write_text(out_path, "")
        elif out_path.exists() and not args.resume:
            raise FileExistsError(f"Prediction file already exists: {out_path}. Use --overwrite to replace it.")
        elif not out_path.exists():
            write_text(out_path, "")

        completed = existing_case_ids(out_path) if args.resume else set()
        total = len(dataset_cases)
        for idx, case in enumerate(dataset_cases, start=1):
            if case.case_id in completed:
                log_event(progress_path, "case_skip_existing", dataset=dataset_name, case_id=case.case_id, idx=idx, total=total)
                continue

            started = time.monotonic()
            log_event(progress_path, "case_start", dataset=dataset_name, case_id=case.case_id, idx=idx, total=total)
            if args.case_timeout_seconds > 0:
                result = run_case_with_timeout(
                    case,
                    args,
                    args.case_timeout_seconds,
                    progress_path,
                    {"dataset": dataset_name, "case_id": case.case_id, "idx": idx, "total": total},
                )
            else:
                try:
                    diagnostic = make_diagnostic(progress_path, {"dataset": dataset_name, "case_id": case.case_id, "idx": idx, "total": total}, args.diagnostic_logs)
                    workflow = build_workflow(
                        args,
                        progress_path=progress_path,
                        case_fields={"dataset": dataset_name, "case_id": case.case_id, "idx": idx, "total": total},
                        diagnostic_logs=args.diagnostic_logs,
                    )
                    install_workflow_diagnostics(workflow, diagnostic)
                    prediction = run_lato_workflow_with_stage_logs(
                        workflow,
                        case.content,
                        args.lato_examples_dir,
                        progress_path,
                        {"dataset": dataset_name, "case_id": case.case_id, "idx": idx, "total": total},
                        diagnostic,
                    )
                    result = {"ok": True, "prediction": normalize_text(prediction)}
                except BaseException as exc:
                    result = {"ok": False, "error_type": type(exc).__name__, "error": str(exc)}
            elapsed = round(time.monotonic() - started, 3)

            if not result.get("ok"):
                error_row = {
                    "dataset": case.dataset,
                    "case_id": case.case_id,
                    "input_requirement": case.content,
                    "error_type": result.get("error_type", "Error"),
                    "error": result.get("error", "unknown error"),
                    "elapsed_sec": elapsed,
                }
                _append_jsonl(errors_path, error_row)
                log_event(
                    progress_path,
                    "case_error",
                    dataset=dataset_name,
                    case_id=case.case_id,
                    idx=idx,
                    total=total,
                    elapsed_sec=elapsed,
                    error_type=error_row["error_type"],
                )
                if not args.continue_on_error:
                    raise RuntimeError(f"LATO failed for {case.case_id}: {error_row['error']}")
                continue

            append_jsonl(
                out_path,
                {
                    "dataset": case.dataset,
                    "case_id": case.case_id,
                    "input_requirement": case.content,
                    "prediction": normalize_text(result.get("prediction", "")),
                    "elapsed_sec": elapsed,
                },
            )
            completed.add(case.case_id)
            log_event(progress_path, "case_success", dataset=dataset_name, case_id=case.case_id, idx=idx, total=total, elapsed_sec=elapsed)
    log_event(progress_path, "run_end", output_dir=str(output_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
