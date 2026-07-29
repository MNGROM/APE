# APE

APE automatically improves a generation Prompt that converts natural-language requirements into
PlantUML activity diagrams. The repository supports one workflow: selector-v4. See
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the contracts and data boundaries.

The entry point is `run.py`. Current Prompt assets live in `prompt_workspace/`; datasets are under
`prompt_datasets/lato/`. Experimental logs under `prompt_runs/` and `prompt_runs_by_dataset/` are
retained as read-only artifacts and are not part of code cleanup.

Offline validation:

```powershell
py -m unittest discover -s tests -q
py -m compileall analysis tests run.py
git diff --check
```

Offline smoke test:

```powershell
py run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

Example leave-one-dataset-out run:

```powershell
py run.py --test-dataset us --iterations 3 --eval-initial-test
```

`--eval-initial-test` is a valueless flag and cannot be combined with isolated candidate search.
The default `--candidate-application-mode auto` resolves to `diagnostic-apply`; use `cumulative`
for metric-gated application or `isolated` for diagnostics only.
