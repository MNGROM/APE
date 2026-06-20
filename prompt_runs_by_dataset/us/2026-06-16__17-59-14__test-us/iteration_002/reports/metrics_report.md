# Iteration 002 Metrics

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.7500 | 0.7500 | 0.3070 | 0.3943 | 0.3661 | 0.2644 | 0.5295 | 0.3141 | 0.0000 |
| gate_baseline | 0.7500 | 0.7500 | 0.3958 | 0.5198 | 0.4132 | 0.3798 | 0.6172 | 0.4489 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.5415 | 0.5391 | 0.5643 | 0.5204 | 0.6145 | 0.4801 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.2500 | 0.2500 | 0.1457 | 0.0193 | 0.1511 | 0.1406 | -0.0027 | 0.0312 | 0.0000 |

## Gates

```json
{
  "safety_gate": {
    "compile_not_significantly_worse": true,
    "node_not_significantly_worse": true,
    "relation_not_significantly_worse": true,
    "semantic_metrics_not_both_down": true,
    "infrastructure_delta_ok": true,
    "prompt_size_ok": true
  },
  "benefit_gate": {
    "relation_improved": true,
    "node_improved": true,
    "compile_improved_without_semantic_regression": true
  },
  "bootstrap_gate": {
    "is_first_iteration": false,
    "node_improved": true,
    "relation_improved": true,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
