# Issue: best prompt selection is only batch-local

## Problem

`prompt_best.md` is selected from iteration analysis summaries, not from a stable held-out or validation set. This means the prompt marked as "best" can be the best prompt for one sampled training batch while not being the best prompt for the final target distribution.

## Evidence

In run `prompt_runs/2026-06-19__22-26-11__test-us`, the final held-out test used `prompt_best.md` because `use_best_prompt_for_test=True`.

The selected best prompt was recorded as:

- `iteration`: 7
- `phase`: `train_before_evolve`
- `selection_policy`: `relation_f1, then node_f1, then plantuml_compilation_pass_rate, with infrastructure_error_rate as a hard priority`
- selected on the iteration analysis batch, not on held-out US

The selected prompt had strong analysis-batch metrics, but its held-out US metrics were lower than the earlier US run:

- old US run: `llm_node_f1=0.8053`, `llm_relation_f1=0.5734`
- new US run: `llm_node_f1=0.7563`, `llm_relation_f1=0.5426`

This shows that current "best" means "best on one sampled analysis batch under deterministic priority", not necessarily "best semantic prompt for held-out evaluation".

## Risk

- A prompt can be selected because it improves deterministic `relation_f1` on a small batch while degrading LLM judge semantic quality.
- Later accepted prompts may be ignored if they do not become the batch-local best before the next iteration.
- Reported final test results can depend heavily on batch sampling rather than true prompt quality.

## Possible Future Direction

- Add a stable validation batch separate from analysis and gate batches.
- Select `prompt_best.md` using validation metrics rather than iteration analysis metrics.
- Consider a selectable best-prompt policy, such as deterministic, LLM judge, or hybrid.
- Report both `last_accepted_prompt` and `best_validation_prompt` to make this distinction explicit.
