# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2783
- node_recall: 0.3123
- node_f1: 0.2943
- relation_precision: 0.2233
- relation_recall: 0.2287
- relation_f1: 0.2260
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.6194
- llm_node_recall: 0.7730
- llm_node_f1: 0.6632
- llm_relation_precision: 0.4583
- llm_relation_recall: 0.4958
- llm_relation_f1: 0.4416

## Failure Types
- extra_activity: 15
- extra_or_wrong_relation: 15
- missing_activity: 14
- missing_or_wrong_relation: 14
- wrong_parallel: 3
- wrong_loop: 2

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
