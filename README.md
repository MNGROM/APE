# APE

APE is a prompt-evolution workspace for UML activity-diagram PlantUML generation.
It treats the UML generator prompt as the artifact under optimization.

The canonical seed prompt is:

```text
prompt_workspace/tst.md
```

Every run copies this file into its own `prompt_runs/<run>/work.md`. Training
edits only the run-local `work.md`; the seed prompt is not overwritten.

## Repository Layout

- `run.py`: main batch prompt-evolution entry point.
- `prompt_evolve.py`: compatibility wrapper that forwards to `run.py`.
- `config.py`: shared paths, defaults, and prompt-section constants.
- `ape_datasets/lato.py`: LATO dataset loading and sampling.
- `llm.py`: OpenAI-compatible `LLMClient`.
- `prediction.py`: UML agent prediction helpers.
- `metrics.py`: deterministic syntax, node, relation, and scoring metrics.
- `evaluation.py`: batch evaluation workflow.
- `analysis/`: failure analysis, error localization, and prompt editing agents.
- `prompt_ops.py`: prompt section parsing and edit application.
- `versioning.py`: run directory and prompt version files.
- `prompt_workspace/tst.md`: canonical initial UML generation prompt.
- `prompt_workspace/failure_analysis.md`: system prompt for batch failure analysis.
- `prompt_workspace/error_localization.md`: system prompt for section-level error localization.
- `prompt_workspace/prompt_editor.md`: system prompt for structured prompt edits.
- `prompt_datasets/lato/`: six JSONL datasets: `bp`, `fsd`, `lmc`, `pure`, `rac`, `us`.
- `llm_element_metrics.py`: PlantUML compilation check and optional LLM semantic element judge.
- `utils/rate_limit.py`: shared provider retry and rate-limit state logging.
- `tools/plantuml/plantuml-1.2025.4.jar`: bundled PlantUML syntax validator.

The active workflow is the standalone prompt optimization loop in `run.py`.
`prompt_evolve.py` is kept for old commands.

## Environment

Python 3.13 is recommended.

Install dependencies with:

```powershell
uv sync
```

For real model calls, configure an OpenAI-compatible chat-completions provider.
The defaults target Zhipu GLM:

```powershell
$env:ZHIPU_LLM_API_KEY="your-api-key"
$env:ZHIPU_LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
$env:ZHIPU_LLM_MODEL="glm-5.1"
```

`--thinking` is the default thinking mode for all model calls. Agent-specific
options can override it:

```powershell
python run.py --test-dataset fsd --thinking disabled --generation-thinking disabled --analysis-thinking enabled --localization-thinking enabled --editor-thinking disabled --judge-thinking disabled --no-llm-element-metrics
```

Agent-specific options support `inherit`, `enabled`, and `disabled`. A useful
starting point is to keep PlantUML generation, prompt editing, and LLM judging
disabled while enabling failure analysis and error localization.

Do not write API keys into Python files, docs, logs, or committed examples.

## Quick Checks

Run the local pipeline without model calls:

```powershell
python run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

Run a tiny real training-only smoke test:

```powershell
python run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3
```

Use one dataset as held-out test and the other five as training data:

```powershell
python run.py --test-dataset fsd --iterations 3
```

Optionally evaluate the original seed prompt as `iteration_000/test` before
training:

```powershell
python run.py --test-dataset fsd --eval-initial-test
```

Run leave-one-dataset-out over all six datasets:

```powershell
python run.py --test-dataset all --iterations 3
```

When a case limit is used, training defaults to stratified sampling, so
`--test-dataset fsd --max-train-cases 30` samples across `bp/lmc/pure/rac/us`
instead of taking only the merged train-set prefix.

## Workflow

Each iteration follows this loop:

```text
current prompt
-> analysis batch PlantUML generation
-> deterministic evaluation
-> batch failure-analysis model
-> error-localization model maps failures to prompt sections
-> prompt-editor model emits structured section edits
-> epoch-planner model merges batch revision plans
-> prompt-rewriter model emits the next prompt
-> apply the epoch candidate prompt directly
-> held-out test evaluation
```

The `online` update mode still uses the candidate gate after each batch. In the
default `epoch` update mode, the old gate-batch accept/reject path is disabled;
the held-out test metrics are the comparison signal.

The prompt editor does not rewrite arbitrary files. It returns JSON edits for
the fixed markdown sections in `tst.md`:

```text
## agent task
## input
## output
## workflow
## knowledge
## rule
```

By default, at most two sections may be edited per iteration
(`--max-sections-per-edit 2`).

## Evaluation

The primary deterministic metrics are:

- `node_f1` (`N-F1`): normalized activity/condition node matching.
- `relation_f1` (`R-F1`): normalized control-flow relation matching.
- `plantuml_compilation_pass_rate`: local PlantUML syntax compilation pass rate.

Optional LLM semantic metrics are:

- `llm_node_f1` (`LLM-N-F1`)
- `llm_relation_f1` (`LLM-R-F1`)

Disable the LLM semantic judge for cheap local checks:

```powershell
python run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

Online candidate acceptance no longer uses a weighted aggregate score. It uses
metric gates directly. The default epoch mode applies epoch-level prompt updates
directly and does not run the gate-batch acceptance path.

All Safety Gate checks must pass before the Benefit Gate is considered:

```text
plantuml_compile_delta >= -0.05
node_f1_delta >= -0.02
relation_f1_delta >= -0.01
N-F1 and R-F1 must not regress at the same time
infrastructure_error_delta <= 0
prompt_size_ok
```

At least one Benefit Gate signal must pass:

```text
relation_f1_delta >= 0.01
or node_f1_delta >= 0.02
or plantuml_compile_delta >= 0.05 with no N-F1/R-F1 regression
```

This prevents compilation improvements from compensating for semantic quality
regressions in online mode. Held-out testing runs as `iteration_NNN/test`; the
workflow no longer runs a second duplicate held-out test after all training
completes.

Iteration 1 has a bootstrap exception: if both `N-F1` and `R-F1` clearly
improve (`+0.02` and `+0.01` by default), no new infrastructure errors appear,
and the prompt stays within the size guard, the candidate can be accepted.
Later iterations use the standard gates above.

## Outputs

Runs are written under `prompt_runs/`. Important files include:

- `run_args.json`: sanitized run configuration.
- `train_cases.json`, `test_cases.json`: actual sampled cases.
- `prompt_evolution.md`: prompt evolution overview for the run, including the initial prompt, per-iteration change links, and best/final prompts.
- `metrics_overview.md`: metric overview for the run, focused on `iteration_NNN/test` held-out metrics.
- `iteration_NNN/analysis_batch_cases.json`: batch used for failure analysis.
- `iteration_NNN/predictions.jsonl`: generated PlantUML and metrics for the analysis batch.
- `iteration_NNN/evaluation_summary.json`: analysis-batch metric summary.
- `iteration_NNN/prompt_change.md`: per-iteration prompt change report with before/after diff, candidate acceptance, and rejection reasons.
- `iteration_NNN/metrics_report.md`: per-iteration metric report with analysis, baseline gate, candidate gate, and deltas.
- `iteration_NNN/analysis/overview.md`: human-readable failure report.
- `iteration_NNN/failure_analysis_input.json`: input sent to the failure-analysis model.
- `iteration_NNN/failure_analysis_output.json`: structured failure-analysis result.
- `iteration_NNN/error_localization_input.json`: input sent to the error-localization model.
- `iteration_NNN/error_localization_output.json`: section-level localization result.
- `iteration_NNN/prompt_edit_input.json`: input sent to the prompt-editor model, including failure analysis and localization.
- `iteration_NNN/prompt_edit_output.json`: structured prompt edit result.
- `iteration_NNN/candidate_prompt.md`: candidate prompt after applying edits.
- `iteration_NNN/gate_cases.json`: gate-batch case manifest, used by online updates.
- `iteration_NNN/gate_predictions.jsonl`: candidate gate predictions and metrics, used by online updates.
- `iteration_NNN/gate_summary.json`: candidate gate summary, used by online updates.
- `iteration_NNN/prompt_acceptance.json`: prompt update decision; epoch mode records direct application, online mode records gate accept/reject details.
- `iteration_000/test/summary.json`, `iteration_000/test/analysis.md`: optional original-prompt held-out test results when `--eval-initial-test` is used.
- `iteration_NNN/test/summary.json`, `iteration_NNN/test/analysis.md`: per-iteration held-out test results.
- `prompt_final.md`: final current prompt produced by training.
- `run_state.json`, `rate_limit_events.jsonl`: provider retry state and event log.

Existing historical runs can be refreshed without rerunning model calls:

```powershell
python run.py --refresh-reports .\prompt_runs\<run-name>
```

Omit `RUN_DIR` to refresh every run under `prompt_runs/`:

```powershell
python run.py --refresh-reports
```
