# Prompt Evaluation Analysis

## Summary
- count: 116
- syntax_pass_rate: 0.9483
- infrastructure_error_rate: 0.0000
- node_precision: 0.6540
- node_recall: 0.4288
- node_f1: 0.5180
- relation_precision: 0.4787
- relation_recall: 0.2886
- relation_f1: 0.3601
- plantuml_compilation_pass_rate: 0.9483
- llm_element_evaluated: 116.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.9156
- llm_node_recall: 0.6231
- llm_node_f1: 0.7345
- llm_relation_precision: 0.6119
- llm_relation_recall: 0.3961
- llm_relation_f1: 0.4757

## Failure Types
- missing_activity: 116
- missing_or_wrong_relation: 116
- extra_or_wrong_relation: 115
- wrong_parallel: 115
- extra_activity: 108
- wrong_loop: 84
- syntax_error: 6

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
