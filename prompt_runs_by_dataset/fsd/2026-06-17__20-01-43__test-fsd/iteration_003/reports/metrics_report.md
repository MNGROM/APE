# Iteration 003 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.4134 | 0.3833 | 0.4418 | 0.3884 | 0.4218 | 0.3512 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.4647 | 0.3490 | 0.4799 | 0.4505 | 0.3332 | 0.3664 | 0.0000 |
| gate_candidate | 0.9000 | 0.9000 | 0.4443 | 0.1756 | 0.4350 | 0.4541 | 0.1793 | 0.1720 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | -0.1000 | -0.1000 | -0.0204 | -0.1734 | -0.0449 | 0.0035 | -0.1539 | -0.1944 | 0.0000 |

## Gates

```json
{
  "safety_gate": {
    "compile_not_significantly_worse": false,
    "node_not_significantly_worse": false,
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
