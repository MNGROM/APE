# Iteration 001 Metrics

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.9000 | 0.9000 | 0.4525 | 0.4296 | 0.4568 | 0.4484 | 0.4225 | 0.4371 | 0.0000 |
| gate_baseline | 0.9000 | 0.9000 | 0.4629 | 0.3169 | 0.4785 | 0.4483 | 0.3346 | 0.3010 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.5198 | 0.4631 | 0.5685 | 0.4788 | 0.5298 | 0.4113 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.1000 | 0.1000 | 0.0569 | 0.1462 | 0.0900 | 0.0304 | 0.1952 | 0.1103 | 0.0000 |

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
    "is_first_iteration": true,
    "node_improved": true,
    "relation_improved": true,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
