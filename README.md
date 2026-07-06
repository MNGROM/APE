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
- `metrics.py`: syntax, auxiliary embedding, and LLM-judge summary metrics.
- `evaluation.py`: batch evaluation workflow.
- `analysis/`: failure analysis, error localization, and prompt editing agents.
- `prompt_ops.py`: prompt section parsing and edit application.
- `versioning.py`: run directory and prompt version files.
- `prompt_workspace/tst.md`: canonical initial UML generation prompt.
- `prompt_workspace/failure_analysis.md`: system prompt for batch failure analysis.
- `prompt_workspace/error_localization.md`: system prompt for section-level error localization.
- `prompt_workspace/prompt_editor.md`: system prompt for structured prompt edits.
- `prompt_datasets/lato/`: six JSONL datasets: `bp`, `fsd`, `lmc`, `pure`, `rac`, `us`.
- `llm_element_metrics.py`: PlantUML compilation check and default LLM semantic element judge.
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
python run.py --test-dataset fsd --thinking disabled --generation-thinking disabled --analysis-thinking enabled --localization-thinking enabled --editor-thinking disabled --judge-thinking disabled
```

Agent-specific options support `inherit`, `enabled`, and `disabled`. A useful
starting point is to keep PlantUML generation, prompt editing, and LLM-judge
thinking disabled while enabling failure analysis and error localization.

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
-> fixed validation-gate evaluation accepts or rejects the candidate
-> held-out test evaluation
```

By default, the sampled training pool is split into optimization cases and a
fixed validation gate (`--validation-gate-size 30`, capped at about one third
of the sampled training pool for small runs). Validation cases are not used by
failure analysis or prompt evolution agents. The epoch candidate must pass
this fixed gate before `work.md` is updated.

Training batches inside one epoch can run concurrently with
`--epoch-batch-concurrency N`; the default `N=1` preserves the serial behavior.
All batches use the same epoch-start prompt, then the epoch planner merges the
completed batch revision plans once.

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

The epoch planner applies the section-count budget for the final merged
revision plan: at most three sections may be planned before the first accepted
update (`--initial-max-sections-per-edit 3`), and at most one section after
that (`--max-sections-per-edit 1`).

## Evaluation

The primary training and acceptance metrics are LLM-judge semantic metrics:

- `llm_node_f1` (`LLM-N-F1`)
- `llm_relation_f1` (`LLM-R-F1`)
- `plantuml_compilation_pass_rate`: local PlantUML syntax compilation pass rate.

Auxiliary embedding/difflib metrics are disabled by default and can be enabled
only for diagnostics with `--embedding-element-metrics`:

- `node_f1` (`N-F1`): normalized activity/condition node matching.
- `relation_f1` (`R-F1`): normalized control-flow relation matching.

Disable the LLM semantic judge for cheap local checks:

```powershell
python run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

Candidate acceptance no longer uses a weighted aggregate score. It is a direct
accept/reject decision over the validation gate summaries.

All Safety Gate checks must pass before the Benefit Gate is considered:

```text
syntax_pass_rate_delta >= -0.01
plantuml_compile_delta >= -0.01
node_f1_delta >= -0.01
relation_f1_delta >= -0.01
node_precision_delta >= -0.02
relation_precision_delta >= -0.02
infrastructure_error_delta <= 0
prompt_size_ok
```

Here `node_*` and `relation_*` deltas refer to LLM-judge metrics, not
auxiliary embedding metrics.

At least one Benefit Gate signal must pass:

```text
relation_f1_delta >= 0.02
or node_f1_delta >= 0.02
or plantuml_compile_delta >= 0.05 with no node/relation F1 regression
```

This prevents compilation improvements from compensating for semantic quality
regressions. Held-out testing runs as `iteration_NNN/test`; the workflow no
longer runs a second duplicate held-out test after all training completes.

Iteration 1 has a bootstrap exception: if both `N-F1` and `R-F1` clearly
improve (`+0.05` and `+0.05` by default), syntax/compile pass rates stay within
the relaxed tolerance (`-0.10` by default), no new infrastructure errors appear,
and the prompt stays within the absolute `--max-prompt-chars` limit, the candidate can be accepted. Later
iterations use the standard gates above.

## Outputs

Runs are written under `prompt_runs/`. Important files include:

- `run_args.json`: sanitized run configuration.
- `train_pool_cases.json`: sampled training pool before the validation split.
- `train_cases.json`: optimization cases used by the prompt-evolution agents.
- `validation_gate_cases.json`: fixed validation cases reserved from the training pool.
- `test_cases.json`: held-out test cases.
- `prompt_evolution.md`: prompt evolution overview for the run, including the initial prompt, per-iteration change links, and best/final prompts.
- `metrics_overview.md`: metric overview for the run, focused on `iteration_NNN/test` held-out metrics.
- `iteration_NNN/batches/analysis_cases.json`: optimization cases evaluated in the iteration.
- `iteration_NNN/evaluation/analysis_records.jsonl`: generated PlantUML and metrics for optimization cases.
- `iteration_NNN/evaluation/analysis_summary.json`: optimization-case metric summary.
- `iteration_NNN/reports/prompt_change.md`: per-iteration prompt change report with before/after diff, candidate acceptance, and rejection reasons.
- `iteration_NNN/reports/metrics_report.md`: per-iteration metric report with analysis, validation/gate baseline, candidate, and deltas.
- `iteration_NNN/evaluation/analysis_overview.md`: human-readable failure report.
- `iteration_NNN/agents/failure_analysis.input.json`: input sent to the failure-analysis model.
- `iteration_NNN/agents/failure_analysis.output.json`: structured failure-analysis result.
- `iteration_NNN/agents/error_localization.input.json`: input sent to the error-localization model.
- `iteration_NNN/agents/error_localization.output.json`: section-level localization result.
- `iteration_NNN/agents/prompt_editor.input.json`: input sent to the prompt-editor model, including failure analysis and localization.
- `iteration_NNN/agents/prompt_editor.output.json`: structured prompt edit result.
- `iteration_NNN/prompts/candidate.md`: candidate prompt emitted by the prompt rewriter.
- `iteration_NNN/validation_gate/cases.json`: fixed validation cases used for candidate acceptance.
- `iteration_NNN/validation_gate/baseline_records.jsonl`, `iteration_NNN/validation_gate/baseline_summary.json`: current-prompt validation baseline.
- `iteration_NNN/validation_gate/candidate_records.jsonl`, `iteration_NNN/validation_gate/candidate_summary.json`: candidate-prompt validation result.
- `iteration_NNN/decision/acceptance.json`: prompt update decision with `accepted: true/false` and rejection reasons.
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
