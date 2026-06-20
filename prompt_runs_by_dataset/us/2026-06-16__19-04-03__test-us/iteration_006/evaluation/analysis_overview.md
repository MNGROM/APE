# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 0.8667
- infrastructure_error_rate: 0.0000
- node_precision: 0.4968
- node_recall: 0.4507
- node_f1: 0.4726
- relation_precision: 0.4346
- relation_recall: 0.3881
- relation_f1: 0.4100
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.9463
- llm_node_recall: 0.8562
- llm_node_f1: 0.8868
- llm_relation_precision: 0.6776
- llm_relation_recall: 0.5880
- llm_relation_f1: 0.6037

## Failure Types
- missing_activity: 15
- extra_activity: 15
- extra_or_wrong_relation: 14
- missing_or_wrong_relation: 13
- wrong_parallel: 5
- wrong_loop: 4
- syntax_error: 2

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
