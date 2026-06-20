# Iteration 003 Metrics

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.3258 | 0.2162 | 0.3633 | 0.3052 | 0.2270 | 0.2106 | 0.0000 |
| gate_baseline | 0.9500 | 0.9500 | 0.2910 | 0.1442 | 0.2974 | 0.3127 | 0.1523 | 0.1388 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.3662 | 0.1749 | 0.3876 | 0.3694 | 0.1774 | 0.1769 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0500 | 0.0500 | 0.0752 | 0.0307 | 0.0902 | 0.0568 | 0.0251 | 0.0380 | 0.0000 |

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
