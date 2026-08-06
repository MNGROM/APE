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
Gate2 is enabled by default, so `--candidate-application-mode auto` resolves to `cumulative`:
candidates must pass both Gate1 and a fresh Gate2 evaluation. Use `isolated` for diagnostics only.
The legacy `diagnostic-apply` mode requires an explicit `--no-gate2`.

Provider configuration is read from the environment. Use `APE_LLM_PROVIDER=zhipu` with
`ZHIPU_LLM_API_KEY`, or `APE_LLM_PROVIDER=deepseek` with `DEEPSEEK_API_KEY`. If exactly one
provider key is present, APE infers that provider; if both are present, set the provider explicitly.
DeepSeek defaults to `https://api.deepseek.com/` and `deepseek-v4-flash`; its requests omit the
provider-specific `do_sample` field. See [`.env.example`](.env.example) for role-model overrides.

PowerShell example for an offline-safe smoke run (replace the key only for an authorized real run):

```powershell
$env:APE_LLM_PROVIDER = "deepseek"
$env:DEEPSEEK_API_KEY = "<your-key>"
pwsh -NoProfile -File scripts/run_dataset_pairs.ps1 -Datasets lmc -MaxParallel 1 -Smoke
```

The tracked dataset scheduler enables Gate2 explicitly. Run target datasets sequentially when
reproducing validation evidence:

```powershell
pwsh -NoProfile -File scripts/run_dataset_pairs.ps1 -Datasets lmc -MaxParallel 1 -HeldoutRepeats 3
pwsh -NoProfile -File scripts/run_dataset_pairs.ps1 -Datasets pure -MaxParallel 1 -HeldoutRepeats 3
```

The scheduler prints a structured status heartbeat every 10 seconds by default, including the
dataset, phase, recent case, heldout repeat, retry state, and log path. Adjust it with
`-StatusIntervalSeconds 30`; full stdout/stderr logs are still retained in the temporary scheduler
log directory.

The cross-run source-to-benefit audit reads existing artifacts without modifying them and prints
Markdown by default:

```powershell
py scripts/analyze_cross_dataset_transfer.py prompt_runs\<run-a> prompt_runs\<run-b>
```

Its training-pool weighted metrics are diagnostic-only and never rewrite historical acceptance.

`-NoGate2` is diagnostic-only and switches to `diagnostic-apply`; its output must not be used as
formal two-stage evidence. For fixed Seed A/B diagnostics, provide both candidate Prompt paths:

```powershell
pwsh -NoProfile -File scripts/run_seed_ab.ps1 `
  -CandidateAPrompt path\to\candidate_a.md `
  -CandidateBPrompt path\to\candidate_b.md
```

The A/B runner stores canonical Prompt hashes and verifies them before producing its report.
