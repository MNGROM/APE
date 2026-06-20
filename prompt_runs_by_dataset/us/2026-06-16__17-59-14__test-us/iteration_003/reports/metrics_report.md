# Iteration 003 Metrics

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.4913 | 0.5022 | 0.5234 | 0.4629 | 0.5833 | 0.4409 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.4946 | 0.3399 | 0.5300 | 0.4636 | 0.3593 | 0.3224 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.5354 | 0.4387 | 0.6226 | 0.4696 | 0.5138 | 0.3827 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | 0.0000 | 0.0408 | 0.0988 | 0.0926 | 0.0060 | 0.1545 | 0.0603 | 0.0000 |

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
    "is_first_iteration": false,
    "node_improved": true,
    "relation_improved": true,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
