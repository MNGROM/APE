# Prompt Evaluation Analysis

## Summary
- count: 8
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3408
- node_recall: 0.6667
- node_f1: 0.4510
- relation_precision: 0.1429
- relation_recall: 0.1875
- relation_f1: 0.1622
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- extra_activity: 7
- missing_or_wrong_relation: 7
- extra_or_wrong_relation: 7
- missing_activity: 4

## Representative Failure Cases
### us-0006
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - accept zero and blank for non-loan records
- extra_nodes:
  - receive fabs record
  - is the record a non-loan record?
  - validate non-loan record fields
  - field value is zero?
  - accept zero
  - field value is blank?
  - accept blank
  - reject field value
- input_excerpt:
  As an agency user, I want the FABS validation rules to accept zero and blank for non-loan records.
- generated_excerpt:
  @startuml start :Receive FABS record; if (Is the record a non-loan record?) then (yes)   :Validate non-loan record fields;   if (Field value is zero?) then (yes)     :Accept zero;   elseif (Field value is blank?) then (yes)     :Accept blank;   else (no)     :Reject field value;   endif else (no)   :Validate loan record fields; endif stop @enduml
### us-0005
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.2222
- missing_nodes:
  - manage d files generation requests
  - avoid performance issues caused by duplicate requests
- extra_nodes:
  - receive d files generation request
  - check cache for existing d files
  - cache hit?
  - retrieve d files from cache
  - generate d files
  - return d files
- missing_relations:
  - cache d files generation requests -> avoid performance issues caused by duplicate requests
- input_excerpt:
  As a Developer, I want D Files generation requests to be managed and cached, so that duplicate requests do not cause performance issues.
- generated_excerpt:
  @startuml start :Receive D Files generation request; :Check cache for existing D Files; if (Cache hit?) then (Yes)   :Retrieve D Files from cache; else (No)   :Generate D Files;   :Cache generated D Files; endif :Return D Files; stop @enduml
### us-0004
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.0000
- missing_nodes:
  - justify padding
- extra_nodes:
  - receive input field
  - accept field
  - reject field
- missing_relations:
  - use zero-padded fields -> justify padding
- input_excerpt:
  As an owner, I only want zero-padded fields, so that I can justify padding.
- generated_excerpt:
  @startuml start :Receive input field; if (Is field zero-padded?) then (yes)   :Accept field; else (no)   :Reject field; endif stop @enduml
### us-0001
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- extra_nodes:
  - identify sql codes to update
  - review current sql codes
  - save updated sql codes
- input_excerpt:
  As a broker team member, I want to make some updates to the SQL codes for clarity.
- generated_excerpt:
  @startuml start :Identify SQL codes to update; :Review current SQL codes; :Make updates to the SQL codes for clarity; :Save updated SQL codes; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
