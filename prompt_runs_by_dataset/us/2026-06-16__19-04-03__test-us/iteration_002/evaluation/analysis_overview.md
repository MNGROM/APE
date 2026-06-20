# Prompt Evaluation Analysis

## Summary
- count: 15
- syntax_pass_rate: 0.8000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4613
- node_recall: 0.4169
- node_f1: 0.4380
- relation_precision: 0.4548
- relation_recall: 0.4037
- relation_f1: 0.4277
- plantuml_compilation_pass_rate: 0.9333
- llm_element_evaluated: 15.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.9292
- llm_node_recall: 0.8342
- llm_node_f1: 0.8689
- llm_relation_precision: 0.7387
- llm_relation_recall: 0.6247
- llm_relation_f1: 0.6600

## Failure Types
- missing_activity: 15
- extra_activity: 15
- extra_or_wrong_relation: 14
- missing_or_wrong_relation: 13
- wrong_parallel: 5
- wrong_loop: 4
- syntax_error: 3

## Representative Failure Cases
- none


## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
