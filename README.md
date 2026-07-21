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
- `prompt_workspace/*_v3.md`: default atomic attribution, localization, editing, planning, and fragment-rewrite prompts; unversioned prompts remain for legacy reproduction.
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

Sampling is disabled by default for PlantUML generation, evolution agents, and
the semantic judge: APE sends `do_sample=false` and uses greedy decoding.
Use `--do-sample true` only for an explicitly sampled experiment; `--do-sample omit`
restores the provider default for legacy reproduction.

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
-> Python validates each attribution and builds taxonomy evidence observations
-> Python clusters across batches and selects one mechanism
-> localization and prompt editing run only for supporting batches
-> epoch planner merges only plans for the selected mechanism
-> prompt-rewriter model emits one rule fragment and Python assembles the next prompt
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
All batches use the same epoch-start prompt. Python clusters validated observations
with the default `prompt_workspace/mechanism_taxonomy_v3.json` using exact atomic
signatures before localization or editing; taxonomy v1/v2 remain available for legacy
reproduction. Only supporting batches invoke those agents. Their localization results
must agree by strict majority on the complete prompt-gap scope before the epoch planner runs. The epoch
planner never declares support counts or selects a mechanism.

Failure-analysis v3 attributions are validated independently. Each attribution binds
one case to one exact evaluator anchor. Invalid attributions are audited while unrelated
valid attributions continue. Only primary, trigger-grounded attributions from bijective
judge matching count toward support; secondary or multi-signature conflicts remain diagnostic. Python derives attribution/evidence IDs and
injects canonical mechanism metadata plus frozen positive/negative boundaries.
To bound structured output, Python admits at most 12 anchors per v3 batch. It ranks
compiler/syntax and direct-node evidence before dependent relations within each case,
then allocates the budget across cases. This does not change promotion thresholds.

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

The prompt editor, epoch planner, and rewriter are limited to one mechanism,
one revision item, and one section. The rewriter returns only `rule_text`; Python
applies it to one unique contiguous target span or appends it to the target section.

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

The default gate is repeated, disjunctive `any-improvement` acceptance:

```text
mean(Node F1 delta) > configured minimum with at least 2/3 repeat wins
OR mean(Relation F1 delta) > configured minimum with at least 2/3 repeat wins
```

Compilation and other performance changes are reported but cannot accept or veto
the candidate.
Prompt length, infrastructure failures, and incomplete winning-metric repeats
remain measurement-validity checks. Defaults are:

```text
--acceptance-policy any-improvement
--validation-repeats 3
--acceptance-min-wins 2
```

The previous Safety/Benefit/Bootstrap gate remains available as
`--acceptance-policy legacy`. Baseline repeats are reused only inside one epoch
and are regenerated in the next epoch even if the prompt did not change.

Calibrate natural variation before a formal run:

```powershell
python run.py --test-dataset us --calibrate-validation-only --validation-calibration-repeats 5
```

Calibration evaluates only the fixed validation split with the seed prompt;
it does not train or run held-out evaluation. Recommended thresholds are
reported but never applied automatically. Node/Relation recommendations drive
formal acceptance; Compile calibration is diagnostic only. `data_split_summary.json` and the
calibration report include the actual validation size and split fingerprint.
Held-out behavior is unchanged in
this phase.

## Outputs

Runs are written under `prompt_runs/`. Important files include:

- `run_args.json`: sanitized run configuration.
- `data_split_summary.json`: actual split sizes, dataset counts, and validation fingerprint.
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
- `iteration_NNN/train_batches/batch_NNN/agents/failure_analysis.output.raw.txt`: raw failure-analysis output.
- `iteration_NNN/train_batches/batch_NNN/agents/failure_analysis.rejected_patterns.json`: compatibility filename; v3 stores per-attribution rejection audit.
- `iteration_NNN/train_batches/batch_NNN/mechanisms/evidence.json`: validated batch observations.
- `iteration_NNN/mechanisms/evidence_inventory.json`: complete epoch evidence inventory.
- `iteration_NNN/mechanisms/clusters.json`, `selected.json`: deterministic clustering and the one selected mechanism.
- `iteration_NNN/mechanisms/attribution_lineage.json`: attribution lineage through local plans, final fragment, and acceptance.
- `iteration_NNN/mechanisms/prompt_gap_consensus.json`: supporting-batch localization/editor votes, strict-majority threshold, selected section, and abstention reason.
- `iteration_NNN/prompts/candidate.md`: candidate prompt emitted by the prompt rewriter.
- `iteration_NNN/validation_gate/cases.json`: fixed validation cases used for candidate acceptance.
- `iteration_NNN/validation_gate/baseline_records.jsonl`, `iteration_NNN/validation_gate/baseline_summary.json`: current-prompt validation baseline.
- `iteration_NNN/validation_gate/candidate_records.jsonl`, `iteration_NNN/validation_gate/candidate_summary.json`: candidate-prompt validation result.
- `iteration_NNN/validation_gate/repeat_NNN/`, `aggregate_summary.json`: paired repeats and stable-improvement statistics.
- `iteration_NNN/validation_gate/impact_summary.json`, `impact_report.md`: diagnostic repeat/case/dataset Node/Relation P/R/F1 deltas.
- `iteration_NNN/decision/acceptance.json`: prompt update decision with `accepted: true/false` and rejection reasons.
- `iteration_000/test/summary.json`, `iteration_000/test/analysis.md`: optional original-prompt held-out test results when `--eval-initial-test` is used.
- `iteration_NNN/test/summary.json`, `iteration_NNN/test/analysis.md`: per-iteration held-out test results.
- `prompt_final.md`: final current prompt produced by training.
- `run_state.json`, `rate_limit_events.jsonl`: provider retry state and event log.

Export legacy batch-local `supporting_cases` into a separate audit run without
modifying the source run:

```powershell
py scripts\export_mechanism_evidence.py prompt_runs\<source-run>
```

The audit run contains traceable JSONL evidence, a manual-audit CSV, invalid
reference logs, and a summary report.

Existing historical runs can be refreshed without rerunning model calls:

```powershell
python run.py --refresh-reports .\prompt_runs\<run-name>
```

Omit `RUN_DIR` to refresh every run under `prompt_runs/`:

```powershell
python run.py --refresh-reports
```
