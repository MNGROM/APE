# Prompt Evolution Workflow

This workflow evolves one run-local prompt file for UML activity-diagram PlantUML generation:

```text
prompt_runs/<run>/work.md
```

The seed prompt is kept at `prompt_workspace/tst.md`. Each run copies it to its own `work.md`, and only that run-local file is updated.

The LATO datasets are copied under:

```text
prompt_datasets/lato/
```

## Environment

Set the GLM API key before running real evaluations:

```powershell
$env:ZHIPU_LLM_API_KEY="your-zhipu-api-key"
$env:ZHIPU_LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
```

Java and PlantUML syntax validation use:

```text
tools/plantuml/plantuml-1.2025.4.jar
```

## Run

Dry-run the local pipeline without model calls:

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve
```

Run a tiny real training-only smoke test on a few rows from one dataset:

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --llm-timeout 300
```

`--thinking` defaults to `disabled`, and `--llm-timeout` defaults to 300 seconds. When `--thinking enabled` is used with long inputs, raise the timeout explicitly, for example `--llm-timeout 600`.

The script sends GLM Chat Completions parameters according to the official API shape: `thinking.type` is `enabled` or `disabled`, `max_tokens` is positive, `do_sample` is omitted unless `--do-sample true|false` is provided, and `top_p` is omitted unless `--top-p <value>` is provided.

Prompt candidates are not accepted just because they are well-formed. After the evolve model proposes `prompt_candidate.md`, the script evaluates that candidate and accepts it only when the weighted score improves by at least `--acceptance-min-delta`. The score is:

```text
0.20 * syntax_pass_rate + 0.40 * node_f1 + 0.40 * relation_f1 - 0.50 * infrastructure_error_rate
```

Use `--candidate-max-cases <N>` to validate candidates on a smaller subset before accepting them. The default `0` validates on the same full training set.

Run one held-out test dataset:

```powershell
python prompt_evolve.py --test-dataset fsd --iterations 3
```

Run leave-one-dataset-out over all datasets:

```powershell
python prompt_evolve.py --test-dataset all --iterations 3
```

By default, `--test-dataset all` resets the prompt to the same initial prompt before each split.

## Outputs

Each run writes artifacts under `prompt_runs/`, including:

- `prompt_initial.md`
- `run_args.json`
- `work.md`
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
