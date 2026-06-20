# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3966
- node_recall: 0.3953
- node_f1: 0.3959
- relation_precision: 0.2617
- relation_recall: 0.2736
- relation_f1: 0.2675
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.9061
- llm_node_recall: 0.8461
- llm_node_f1: 0.8610
- llm_relation_precision: 0.7631
- llm_relation_recall: 0.6840
- llm_relation_f1: 0.6951

## Failure Types
- missing_activity: 14
- extra_activity: 14
- extra_or_wrong_relation: 14
- missing_or_wrong_relation: 13
- wrong_parallel: 3
- wrong_loop: 2

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
