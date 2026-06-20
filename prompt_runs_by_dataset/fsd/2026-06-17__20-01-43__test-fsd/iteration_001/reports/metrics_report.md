# Iteration 001 Metrics

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none

## Summaries

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| analysis_current | 1.0000 | 1.0000 | 0.2836 | 0.3059 | 0.2735 | 0.2945 | 0.3309 | 0.2844 | 0.0000 |
| gate_baseline | 1.0000 | 1.0000 | 0.2542 | 0.1692 | 0.2945 | 0.2236 | 0.1812 | 0.1587 | 0.0000 |
| gate_candidate | 1.0000 | 1.0000 | 0.5967 | 0.3900 | 0.6543 | 0.5485 | 0.3867 | 0.3932 | 0.0000 |

## Deltas

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| candidate_minus_baseline | 0.0000 | 0.0000 | 0.3425 | 0.2208 | 0.3597 | 0.3249 | 0.2056 | 0.2346 | 0.0000 |

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
    "is_first_iteration": true,
    "node_improved": true,
    "relation_improved": true,
    "infrastructure_delta_ok": true,
    "prompt_chars_ok": true
  }
}
```
