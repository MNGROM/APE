# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3725
- node_recall: 0.4023
- node_f1: 0.3868
- relation_precision: 0.2742
- relation_recall: 0.2914
- relation_f1: 0.2825
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8698
- llm_node_recall: 0.7899
- llm_node_f1: 0.8026
- llm_relation_precision: 0.7050
- llm_relation_recall: 0.6154
- llm_relation_f1: 0.6217

## Failure Types
- missing_activity: 14
- extra_activity: 14
- extra_or_wrong_relation: 13
- missing_or_wrong_relation: 12
- wrong_parallel: 3
- wrong_loop: 2

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
