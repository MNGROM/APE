# Iteration 003 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.3607 | 0.5083 | 0.3847 | 0.3395 | 0.6001 | 0.4409 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.5395 | 0.4525 | 0.6375 | 0.4676 | 0.5270 | 0.3965 | 0.0000 |
| gate_candidate | 0.7500 | 0.7500 | 0.5267 | 0.3220 | 0.5950 | 0.4724 | 0.3595 | 0.2916 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | -0.2500 | -0.2500 | -0.0128 | -0.1305 | -0.0425 | 0.0048 | -0.1675 | -0.1049 | 0.0000 |

## Gates

```json
{
  "safety_gate": {
    "compile_not_significantly_worse": false,
    "node_not_significantly_worse": true,
    "relation_not_significantly_worse": false,
    "semantic_metrics_not_both_down": false,
    "infrastructure_delta_ok": true,
    "prompt_size_ok": true
  },
  "benefit_gate": {
    "relation_improved": false,
    "node_improved": false,
    "compile_improved_without_semantic_regression": false
  },
  "bootstrap_gate": {
    "is_first_iteration": false,
    "node_improved": false,
    "relation_improved": false,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
