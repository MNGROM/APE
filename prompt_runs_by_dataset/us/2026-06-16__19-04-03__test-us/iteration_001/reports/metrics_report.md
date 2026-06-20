# Iteration 001 Metrics

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.9333 | 0.9333 | 0.4536 | 0.4133 | 0.4516 | 0.4556 | 0.4165 | 0.4102 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.4591 | 0.3404 | 0.4620 | 0.4563 | 0.3314 | 0.3498 | 0.0000 |
| gate_candidate | 1.0000 | 0.9000 | 0.5357 | 0.3642 | 0.5868 | 0.4928 | 0.3942 | 0.3384 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | -0.1000 | 0.0766 | 0.0238 | 0.1248 | 0.0365 | 0.0628 | -0.0114 | 0.0000 |

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
    "compile_improved_without_semantic_regression": false
  },
  "bootstrap_gate": {
    "is_first_iteration": true,
    "node_improved": true,
    "relation_improved": true,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
