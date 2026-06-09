# APE

APE is a prompt-evolution project adapted from Agentic Harness Engineering (AHE).
The current target is a UML activity-diagram generation prompt: APE evaluates a
prompt on natural-language software requirements, compares the generated
PlantUML against reference diagrams, analyzes failures, and asks an LLM to
improve a run-local copy of the prompt.

The seed prompt is kept read-only at:

```text
prompt_workspace/tst.md
```

Each run copies that seed into its own `work.md` under `prompt_runs/`. The
original seed prompt is not overwritten by training.

## What This Repository Contains

- `prompt_evolve.py`: standalone prompt evolution loop.
- `prompt_workspace/tst.md`: initial prompt specification for the UML generation agent.
- `prompt_datasets/lato/`: LATO-derived JSONL datasets used for train/test splits.
- `evaluators/prompt_uml.py`: PlantUML syntax, structure, node, and relation evaluator.
- `tools/plantuml/plantuml-1.2025.4.jar`: bundled PlantUML validator.
- `docs/prompt-evolution.md`: notes for the standalone prompt evolution flow.
- `docs/ahe-prompt-uml.md`: notes for the AHE-native prompt UML backend.
- `docs/glm51-compat.md`: Zhipu GLM 5.1 compatibility notes.

The original AHE code is still present because this project keeps the AHE
evaluate-analyze-improve idea and adapts the evolved component from a coding
agent harness to a prompt file.

## Environment

Python 3.13 is recommended because the inherited AHE project declares
`requires-python >=3.13`.

Install dependencies with `uv`:

```powershell
uv sync
```

For real GLM calls, configure the Zhipu API key in the shell environment:

```powershell
$env:ZHIPU_LLM_API_KEY="your-zhipu-api-key"
$env:ZHIPU_LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
```

Do not write API keys into Python files, YAML files, committed examples, or logs.

The standalone prompt flow does not require E2B. E2B is only needed for the
original Harbor/E2B evaluation backend inherited from AHE.

## Quick Checks

Verify the local pipeline without LLM calls:

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve
```

Run a tiny training-only GLM smoke test:

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3
```

Run one held-out split, using one dataset as the test set and all other datasets
as training data:

```powershell
python prompt_evolve.py --test-dataset fsd --iterations 3
```

Run leave-one-dataset-out across all datasets:

```powershell
python prompt_evolve.py --test-dataset all --iterations 3
```

Available dataset names:

```text
bp, fsd, lmc, pure, rac, us
```

## GLM Compatibility

The default model is `glm-5.1`.

The script sends requests to the OpenAI-compatible Zhipu Chat Completions API
and normalizes common provider details:

- `thinking.type` defaults to `disabled`.
- `do_sample` is omitted unless `--do-sample true|false` is passed.
- `top_p` is omitted unless `--top-p <value>` is passed.
- `max_tokens` defaults to a positive value.
- `ZHIPU_LLM_BASE_URL` may be the API base URL; the script appends
  `chat/completions` internally.

Useful overrides:

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3 --llm-timeout 600
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3 --thinking enabled --llm-timeout 900
```

## Changing Models

The model can be changed without editing code. Command-line arguments have the
highest priority, then environment variables, then the built-in defaults.

Use another Zhipu GLM model:

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3 --model glm-4.7-flashx
```

Or configure the default model for the current shell:

```powershell
$env:ZHIPU_LLM_MODEL="glm-5.1"
$env:ZHIPU_LLM_API_KEY="your-zhipu-api-key"
$env:ZHIPU_LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
```

To use another OpenAI-compatible provider, set both the model and base URL:

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3 --model your-model-name --base-url https://your-provider.example.com/v1/
```

The prompt evaluator assumes a Chat Completions-compatible endpoint. If a
provider rejects GLM-specific fields, run with the defaults first because
`thinking`, `do_sample`, and `top_p` are already omitted or disabled unless
explicitly requested.

## Evaluation

Each case is evaluated by comparing generated PlantUML with the reference
PlantUML. The evaluator checks:

- PlantUML syntax through the bundled PlantUML jar.
- Basic activity-diagram structure, including start/end nodes and dangling or unreachable flow.
- Activity node matching with normalized text similarity.
- Control-flow relation matching between extracted semantic activities.

The prompt quality score is:

```text
0.20 * syntax_pass_rate + 0.40 * node_f1 + 0.40 * relation_f1 - 0.50 * infrastructure_error_rate
```

A candidate prompt is only accepted when its validation score improves over the
current prompt by at least `--acceptance-min-delta` on the candidate validation
set.

## Outputs

Runs are written under `prompt_runs/`. A typical run contains:

- `prompt_initial.md`
- `work.md`
- `run_args.json`
- `iteration_NNN/train_records.jsonl`
- `iteration_NNN/train_summary.json`
- `iteration_NNN/analysis/overview.md`
- `iteration_NNN/prompt_candidate.md`
- `iteration_NNN/candidate_records.jsonl`
- `iteration_NNN/candidate_summary.json`
- `iteration_NNN/prompt_acceptance.json`
- `iteration_NNN/prompt_after.md`
- `test_records.jsonl`
- `test_summary.json`
- `test_analysis.md`
- `prompt_final.md`

## Notes

This repository is an experimental research workspace. The implementation
prioritizes reproducible prompt iteration and inspection of generated artifacts
over packaging polish.
