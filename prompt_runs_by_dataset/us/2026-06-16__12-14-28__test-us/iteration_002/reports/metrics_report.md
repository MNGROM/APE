# Iteration 002 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.8000 | 0.8000 | 0.4252 | 0.3028 | 0.4485 | 0.4041 | 0.3307 | 0.2793 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.3528 | 0.2388 | 0.3752 | 0.3330 | 0.2518 | 0.2271 | 0.0000 |
| gate_candidate | 0.9000 | 0.9000 | 0.3530 | 0.2863 | 0.3699 | 0.3375 | 0.3007 | 0.2732 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | -0.1000 | -0.1000 | 0.0001 | 0.0475 | -0.0052 | 0.0045 | 0.0489 | 0.0461 | 0.0000 |

## Gates

```json
{
  "safety_gate": {
    "compile_not_significantly_worse": false,
    "node_not_significantly_worse": true,
    "relation_not_significantly_worse": true,
    "semantic_metrics_not_both_down": true,
    "infrastructure_delta_ok": true,
    "prompt_size_ok": true
  },
  "benefit_gate": {
    "relation_improved": true,
    "node_improved": false,
    "compile_improved_without_semantic_regression": false
  },
  "bootstrap_gate": {
    "is_first_iteration": false,
    "node_improved": false,
    "relation_improved": true,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
