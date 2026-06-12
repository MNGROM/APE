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

- `prompt_evolve.py`: main batch prompt-evolution loop.
- `prompt_workspace/tst.md`: canonical initial UML generation prompt.
- `prompt_workspace/failure_analysis.md`: system prompt for batch failure analysis.
- `prompt_workspace/error_localization.md`: system prompt for section-level error localization.
- `prompt_workspace/prompt_editor.md`: system prompt for structured prompt edits.
- `prompt_datasets/lato/`: six JSONL datasets: `bp`, `fsd`, `lmc`, `pure`, `rac`, `us`.
- `evaluators/llm_element_metrics.py`: PlantUML compilation check and optional LLM semantic element judge.
- `utils/rate_limit.py`: shared provider retry and rate-limit state logging.
- `tools/plantuml/plantuml-1.2025.4.jar`: bundled PlantUML syntax validator.

The active workflow is the standalone prompt optimization loop in
`prompt_evolve.py`.

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

Do not write API keys into Python files, docs, logs, or committed examples.

## Quick Checks

Run the local pipeline without model calls:

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

Run a tiny real training-only smoke test:

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3
```

Use one dataset as held-out test and the other five as training data:

```powershell
python prompt_evolve.py --test-dataset fsd --iterations 3
```

Run leave-one-dataset-out over all six datasets:

```powershell
python prompt_evolve.py --test-dataset all --iterations 3
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
-> program applies valid edits
-> gate batch candidate evaluation
-> accept or reject candidate prompt
```

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
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

The optimization score used for acceptance is:

```text
0.20 * syntax_pass_rate + 0.40 * node_f1 + 0.40 * relation_f1 - 0.50 * infrastructure_error_rate
```

Candidate prompts are accepted only when the gate-batch metrics satisfy the
configured improvement, regression, infrastructure-error, and prompt-size
guards. Held-out testing uses the best training prompt by default.

## Outputs

Runs are written under `prompt_runs/`. Important files include:

- `run_args.json`: sanitized run configuration.
- `train_cases.json`, `test_cases.json`: actual sampled cases.
- `iteration_NNN/analysis_batch_cases.json`: batch used for failure analysis.
- `iteration_NNN/predictions.jsonl`: generated PlantUML and metrics for the analysis batch.
- `iteration_NNN/evaluation_summary.json`: analysis-batch metric summary.
- `iteration_NNN/analysis/overview.md`: human-readable failure report.
- `iteration_NNN/failure_analysis_input.json`: input sent to the failure-analysis model.
- `iteration_NNN/failure_analysis_output.json`: structured failure-analysis result.
- `iteration_NNN/error_localization_input.json`: input sent to the error-localization model.
- `iteration_NNN/error_localization_output.json`: section-level localization result.
- `iteration_NNN/prompt_edit_input.json`: input sent to the prompt-editor model, including failure analysis and localization.
- `iteration_NNN/prompt_edit_output.json`: structured prompt edit result.
- `iteration_NNN/candidate_prompt.md`: candidate prompt after applying edits.
- `iteration_NNN/gate_cases.json`: gate-batch case manifest.
- `iteration_NNN/gate_predictions.jsonl`: candidate gate predictions and metrics.
- `iteration_NNN/gate_summary.json`: candidate gate summary.
- `iteration_NNN/prompt_acceptance.json`: accept/reject decision and score deltas.
- `prompt_best.md`: best prompt observed on training evaluation.
- `prompt_final.md`: prompt used for final held-out testing.
- `test_summary.json`, `test_analysis.md`: held-out test results.
- `run_state.json`, `rate_limit_events.jsonl`: provider retry state and event log.
