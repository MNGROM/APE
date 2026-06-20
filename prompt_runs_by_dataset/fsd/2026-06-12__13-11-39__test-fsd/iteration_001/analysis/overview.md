# Prompt Evaluation Analysis

## Summary
- count: 2
- syntax_pass_rate: 0.5000
- infrastructure_error_rate: 0.0000
- node_precision: 1.0000
- node_recall: 1.0000
- node_f1: 1.0000
- relation_precision: 1.0000
- relation_recall: 1.0000
- relation_f1: 1.0000
- higen_compilation_pass_rate: 0.5000
- higen_llm_evaluated: 0.0000
- higen_llm_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- syntax_error: 1

## Representative Failure Cases
### us-0033
- dataset: us
- failure_types: syntax_error
- syntax_passed: False
- syntax_errors: ERROR
- higen_compiles: False
- higen_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 1.0000
- relation_f1: 1.0000
- input_excerpt:
  As an OpenSpending Community Member, I want to have a blog that highlights any and all projects in the open fiscal space, So that I can relate to openspending.org as the central hub of fiscal openness.
- generated_excerpt:
  @startuml start :Get blog highlights any and all projects in the open fiscal space; :Relate to openspending.org as the central hub stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
