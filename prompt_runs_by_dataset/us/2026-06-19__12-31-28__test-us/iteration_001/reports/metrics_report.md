# Iteration 001 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.3930 | 0.2557 | 0.3992 | 0.3869 | 0.2612 | 0.2503 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.4899 | 0.3630 | 0.5227 | 0.4609 | 0.3825 | 0.3454 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.5223 | 0.3720 | 0.5887 | 0.4695 | 0.4303 | 0.3277 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | 0.0000 | 0.0325 | 0.0090 | 0.0659 | 0.0086 | 0.0478 | -0.0177 | 0.0000 |

## Gates

```json
{
  "safety_gate": {
    "compile_not_significantly_worse": true,
    "node_not_significantly_worse": true,
    "relation_not_significantly_worse": true,
    "semantic_metrics_not_both_down": true,
    "infrastructure_delta_ok": true,
    "prompt_size_ok": false
  },
  "benefit_gate": {
    "relation_improved": false,
    "node_improved": true,
    "compile_improved_without_semantic_regression": false
  },
  "bootstrap_gate": {
    "is_first_iteration": true,
    "node_improved": true,
    "relation_improved": false,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
