# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3726
- node_recall: 0.3956
- node_f1: 0.3837
- relation_precision: 0.3143
- relation_recall: 0.3341
- relation_f1: 0.3239
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8398
- llm_node_recall: 0.8052
- llm_node_f1: 0.8103
- llm_relation_precision: 0.6962
- llm_relation_recall: 0.6172
- llm_relation_f1: 0.6319

## Failure Types
- missing_activity: 14
- extra_activity: 14
- extra_or_wrong_relation: 13
- missing_or_wrong_relation: 11
- wrong_parallel: 3
- wrong_loop: 1

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
