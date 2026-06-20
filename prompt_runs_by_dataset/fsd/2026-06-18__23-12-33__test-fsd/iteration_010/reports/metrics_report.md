# Iteration 010 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: has_required_metric_benefit, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.4639 | 0.4104 | 0.4358 | 0.4960 | 0.3896 | 0.4335 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.3407 | 0.2793 | 0.3182 | 0.3667 | 0.2491 | 0.3177 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.3684 | 0.2825 | 0.3495 | 0.3896 | 0.2784 | 0.2868 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | 0.0000 | 0.0277 | 0.0032 | 0.0313 | 0.0229 | 0.0292 | -0.0310 | 0.0000 |

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
