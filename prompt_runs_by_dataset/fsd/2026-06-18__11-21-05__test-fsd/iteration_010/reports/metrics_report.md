# Iteration 010 Metrics

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.5606 | 0.4771 | 0.5441 | 0.5781 | 0.4986 | 0.4574 | 0.0000 |
| gate_baseline | 0.9000 | 0.9000 | 0.3619 | 0.2406 | 0.3775 | 0.3475 | 0.2555 | 0.2274 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.4213 | 0.2363 | 0.4617 | 0.3874 | 0.2389 | 0.2337 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.1000 | 0.1000 | 0.0594 | -0.0043 | 0.0842 | 0.0398 | -0.0165 | 0.0063 | 0.0000 |

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
    "compile_improved_without_semantic_regression": false
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
