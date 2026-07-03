# Resolved: best prompt selection was batch-local

## Historical Problem

Older runs wrote `prompt_best.md` from sampled training-batch summaries. That meant a prompt could be marked as "best" because it performed well on one local batch, even when it was not the best prompt for the final target distribution.

One observed case was `prompt_runs/2026-06-19__22-26-11__test-us`, where the final held-out test used `prompt_best.md` because `use_best_prompt_for_test=True`.

## Resolution

The training workflow now uses the final current prompt produced by accepted epoch-level updates:

- `candidate_prompt`: one batch-local rewrite proposal.
- `current prompt`: the active training prompt, updated only when a candidate passes the gate.
- `prompt_final.md`: the final current prompt after all training iterations.

The batch-local `prompt_best.md` selection path has been removed from new runs.

## Future Direction

If model selection is needed later, add a train-side validation split. The held-out test set must remain evaluation-only and must not drive prompt rewriting, gate decisions, early stopping, or final prompt selection.
