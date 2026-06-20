# Iteration 001 Metrics

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.9500 | 0.9500 | 0.2986 | 0.2649 | 0.2949 | 0.3024 | 0.2841 | 0.2482 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.2873 | 0.1843 | 0.2988 | 0.2766 | 0.1878 | 0.1809 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.4457 | 0.3816 | 0.4595 | 0.4326 | 0.3669 | 0.3974 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | 0.0000 | 0.1584 | 0.1972 | 0.1607 | 0.1560 | 0.1791 | 0.2165 | 0.0000 |

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
