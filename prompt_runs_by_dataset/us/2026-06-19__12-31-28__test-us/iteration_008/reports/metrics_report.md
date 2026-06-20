# Iteration 008 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: has_required_metric_benefit, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.9500 | 0.9500 | 0.5241 | 0.3838 | 0.5571 | 0.4948 | 0.4220 | 0.3520 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.4329 | 0.3030 | 0.4681 | 0.4026 | 0.3050 | 0.3009 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.4561 | 0.2512 | 0.4911 | 0.4257 | 0.2846 | 0.2249 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | 0.0000 | 0.0232 | -0.0517 | 0.0230 | 0.0231 | -0.0204 | -0.0761 | 0.0000 |

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
