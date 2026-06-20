# Iteration 006 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: has_required_metric_benefit, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.4350 | 0.2971 | 0.4685 | 0.4060 | 0.3235 | 0.2746 | 0.0000 |
| gate_baseline | 0.9000 | 0.9000 | 0.4880 | 0.4234 | 0.5281 | 0.4536 | 0.4326 | 0.4146 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.5157 | 0.3725 | 0.5511 | 0.4846 | 0.3698 | 0.3752 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.1000 | 0.1000 | 0.0276 | -0.0510 | 0.0230 | 0.0309 | -0.0628 | -0.0395 | 0.0000 |

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
