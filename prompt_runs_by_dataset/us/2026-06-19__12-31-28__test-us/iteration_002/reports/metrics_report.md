# Iteration 002 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.9500 | 0.9500 | 0.3674 | 0.3147 | 0.3707 | 0.3641 | 0.3218 | 0.3079 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.3896 | 0.3162 | 0.3805 | 0.3993 | 0.2857 | 0.3540 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.3612 | 0.2703 | 0.3644 | 0.3581 | 0.2757 | 0.2650 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | 0.0000 | -0.0284 | -0.0459 | -0.0161 | -0.0411 | -0.0099 | -0.0890 | 0.0000 |

## Gates

```json
{
  "safety_gate": {
    "compile_not_significantly_worse": true,
    "node_not_significantly_worse": true,
    "relation_not_significantly_worse": true,
    "semantic_metrics_not_both_down": false,
    "infrastructure_delta_ok": true,
    "prompt_size_ok": false
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
