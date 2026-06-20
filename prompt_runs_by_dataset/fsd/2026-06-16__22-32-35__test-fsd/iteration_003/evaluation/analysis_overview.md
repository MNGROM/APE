# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 0.9333
- infrastructure_error_rate: 0.0000
- node_precision: 0.3958
- node_recall: 0.4090
- node_f1: 0.4023
- relation_precision: 0.2811
- relation_recall: 0.2879
- relation_f1: 0.2845
- plantuml_compilation_pass_rate: 0.9333
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8864
- llm_node_recall: 0.8392
- llm_node_f1: 0.8426
- llm_relation_precision: 0.6865
- llm_relation_recall: 0.6277
- llm_relation_f1: 0.6306

## Failure Types
- missing_activity: 14
- extra_activity: 14
- extra_or_wrong_relation: 14
- missing_or_wrong_relation: 13
- wrong_parallel: 3
- wrong_loop: 3
- syntax_error: 1

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
