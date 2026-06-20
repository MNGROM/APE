# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 0.9333
- infrastructure_error_rate: 0.0000
- node_precision: 0.4516
- node_recall: 0.4556
- node_f1: 0.4536
- relation_precision: 0.4165
- relation_recall: 0.4102
- relation_f1: 0.4133
- plantuml_compilation_pass_rate: 0.9333
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8418
- llm_node_recall: 0.8775
- llm_node_f1: 0.8476
- llm_relation_precision: 0.6514
- llm_relation_recall: 0.6435
- llm_relation_f1: 0.6214

## Failure Types
- missing_activity: 15
- extra_activity: 15
- missing_or_wrong_relation: 14
- extra_or_wrong_relation: 14
- wrong_parallel: 5
- wrong_loop: 4
- syntax_error: 1

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
