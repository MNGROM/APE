# Iteration 008 Metrics

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.9500 | 0.9500 | 0.4685 | 0.4084 | 0.4585 | 0.4790 | 0.3675 | 0.4594 | 0.0000 |
| gate_baseline | 0.8000 | 0.8000 | 0.4047 | 0.3553 | 0.3599 | 0.4622 | 0.2971 | 0.4419 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.4443 | 0.3610 | 0.4440 | 0.4446 | 0.3140 | 0.4246 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.2000 | 0.2000 | 0.0396 | 0.0057 | 0.0841 | -0.0175 | 0.0169 | -0.0173 | 0.0000 |

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
    "relation_improved": false,
    "node_improved": true,
    "compile_improved_without_semantic_regression": true
  },
  "bootstrap_gate": {
    "is_first_iteration": false,
    "node_improved": true,
    "relation_improved": false,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
