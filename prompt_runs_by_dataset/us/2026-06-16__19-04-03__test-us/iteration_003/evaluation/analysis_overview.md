# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 0.8667
- infrastructure_error_rate: 0.0000
- node_precision: 0.4941
- node_recall: 0.4564
- node_f1: 0.4745
- relation_precision: 0.4553
- relation_recall: 0.4025
- relation_f1: 0.4273
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8908
- llm_node_recall: 0.8239
- llm_node_f1: 0.8429
- llm_relation_precision: 0.6706
- llm_relation_recall: 0.5818
- llm_relation_f1: 0.6032

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
