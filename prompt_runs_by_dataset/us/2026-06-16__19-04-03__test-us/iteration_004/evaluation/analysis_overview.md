# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 0.7333
- infrastructure_error_rate: 0.0000
- node_precision: 0.4837
- node_recall: 0.4423
- node_f1: 0.4620
- relation_precision: 0.4215
- relation_recall: 0.3787
- relation_f1: 0.3989
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8763
- llm_node_recall: 0.8016
- llm_node_f1: 0.8250
- llm_relation_precision: 0.6780
- llm_relation_recall: 0.5529
- llm_relation_f1: 0.5975

## Failure Types
- missing_activity: 15
- extra_activity: 15
- extra_or_wrong_relation: 14
- missing_or_wrong_relation: 13
- wrong_parallel: 5
- wrong_loop: 4
- syntax_error: 4

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
