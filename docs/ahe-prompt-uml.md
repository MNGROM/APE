# AHE-Native Prompt UML Optimization

This mode keeps the AHE outer loop and changes only the evolved component:

```text
experiments/<run>/workspace/work.md
```

`work.md` is the prompt for the downstream UML PlantUML generation agent. The AHE evolve agent is a separate prompt optimizer and must not execute the instructions inside `work.md`.

## Environment

PowerShell:

```powershell
$env:ZHIPU_LLM_API_KEY="your-zhipu-api-key"
```

Model name, base URL, and thinking mode live in the YAML config. The GLM overlay
uses `glm-5.1` and disables thinking by default.

The prompt UML backend uses local evaluation and does not require `E2B_API_KEY`.
`E2B_API_KEY` is only needed when running the original Harbor/E2B evaluation backend.
The AHE evolve step still requires the project agent runtime dependency `nexau`.
This workspace has a project-local Python 3.13 environment at `.venv/`.
Use `.venv\Scripts\python.exe` for prompt UML runs.

Prompt UML keeps binary `reward`/`pass_rate` for final pass/fail, but also records continuous progress under `prompt_quality` in `iteration_scores.yaml`:

- `quality_score`
- `node_f1`
- `relation_f1`
- `syntax_pass_rate`

Use these fields to judge incremental prompt improvements when pass rate is still 0%.

## Smoke Test Without GLM Calls

This uses gold PlantUML output to verify the AHE-native prompt backend, workspace snapshots, iteration scores, and held-out test path:

```powershell
.\.venv\Scripts\python.exe evolve.py --config configs\experiments\exp-prompt-uml-mock.yaml --experiment prompt-uml-mock-smoke
```

## Real Small Run

Run a cheap first pass without editing yaml:

```powershell
.\.venv\Scripts\python.exe evolve.py --config configs\experiments\exp-prompt-uml-glm51.yaml --experiment prompt-uml-glm51-smoke --prompt-test-dataset fsd --prompt-max-train-cases 5 --prompt-max-test-cases 3 --max-iterations 1
```

Training-only smoke run, without the final held-out test:

```powershell
.\.venv\Scripts\python.exe evolve.py --config configs\experiments\exp-prompt-uml-glm51.yaml --experiment prompt-uml-glm51-train-smoke --prompt-test-dataset fsd --prompt-max-train-cases 3 --prompt-skip-heldout-test --max-iterations 1 --target-pass-rate 1.01
```

## Full Leave-One-Dataset-Out

Run each dataset as a held-out test without editing yaml:

```powershell
.\.venv\Scripts\python.exe evolve.py --config configs\experiments\exp-prompt-uml-glm51.yaml --experiment prompt-uml-glm51-lodo --prompt-sweep-datasets
```

To run only a subset:

```powershell
.\.venv\Scripts\python.exe evolve.py --config configs\experiments\exp-prompt-uml-glm51.yaml --experiment prompt-uml-glm51-lodo --prompt-sweep-datasets fsd,bp
```

Available held-out dataset names:

```text
bp, fsd, lmc, pure, rac, us
```

Each experiment keeps its own AHE workspace, git history, iteration snapshots, change manifests, change attribution, and held-out test output.

