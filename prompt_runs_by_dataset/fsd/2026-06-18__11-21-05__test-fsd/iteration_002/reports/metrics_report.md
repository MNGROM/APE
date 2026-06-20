# Iteration 002 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.5542 | 0.5130 | 0.5807 | 0.5300 | 0.5581 | 0.4747 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.4436 | 0.3114 | 0.4417 | 0.4456 | 0.3054 | 0.3175 | 0.0000 |
| gate_candidate | 0.9000 | 0.9000 | 0.3888 | 0.3147 | 0.3831 | 0.3947 | 0.3197 | 0.3098 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | -0.1000 | -0.1000 | -0.0548 | 0.0033 | -0.0586 | -0.0509 | 0.0143 | -0.0077 | 0.0000 |

## Gates

```json
{
  "safety_gate": {
    "compile_not_significantly_worse": false,
    "node_not_significantly_worse": false,
    "relation_not_significantly_worse": true,
    "semantic_metrics_not_both_down": true,
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
