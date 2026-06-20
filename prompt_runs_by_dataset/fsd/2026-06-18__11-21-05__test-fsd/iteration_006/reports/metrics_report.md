# Iteration 006 Metrics

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, bootstrap_gate

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 0.9500 | 0.9500 | 0.4758 | 0.3602 | 0.4827 | 0.4690 | 0.3185 | 0.4145 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.5636 | 0.4452 | 0.5925 | 0.5374 | 0.4490 | 0.4414 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.5232 | 0.5006 | 0.5574 | 0.4929 | 0.4864 | 0.5156 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | 0.0000 | -0.0404 | 0.0554 | -0.0350 | -0.0445 | 0.0374 | 0.0742 | 0.0000 |

## Gates

```json
{
  "safety_gate": {
    "compile_not_significantly_worse": true,
    "node_not_significantly_worse": false,
    "relation_not_significantly_worse": true,
    "semantic_metrics_not_both_down": true,
    "infrastructure_delta_ok": true,
    "prompt_size_ok": true
  },
  "benefit_gate": {
    "relation_improved": true,
    "node_improved": false,
    "compile_improved_without_semantic_regression": false
  },
  "bootstrap_gate": {
    "is_first_iteration": false,
    "node_improved": false,
    "relation_improved": true,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
