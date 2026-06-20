# Iteration 010 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.9500 | 0.9500 | 0.5298 | 0.4303 | 0.5817 | 0.4864 | 0.4519 | 0.4107 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.4132 | 0.2401 | 0.4595 | 0.3753 | 0.2517 | 0.2295 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.2760 | 0.1915 | 0.2960 | 0.2585 | 0.2179 | 0.1708 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | 0.0000 | -0.1372 | -0.0486 | -0.1635 | -0.1168 | -0.0338 | -0.0587 | 0.0000 |

## Gates

```json
{
  "safety_gate": {
    "compile_not_significantly_worse": true,
    "node_not_significantly_worse": true,
    "relation_not_significantly_worse": true,
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
