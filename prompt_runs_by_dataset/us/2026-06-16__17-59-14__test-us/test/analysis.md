# Prompt Evaluation Analysis

## Summary
- count: 8
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.1658
- node_recall: 0.6875
- node_f1: 0.2671
- relation_precision: 0.0530
- relation_recall: 0.3125
- relation_f1: 0.0907
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
- extra_activity: 8
- extra_or_wrong_relation: 8
- missing_or_wrong_relation: 6
- missing_activity: 3

## Representative Failure Cases
### us-0007
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - update financial assistance data daily
- extra_nodes:
  - visit website
  - check if data is updated daily
  - data needs daily update?
  - continue using website
- input_excerpt:
  As a website user, I want to see updated financial assistance data daily.
- generated_excerpt:
  @startuml start :Visit website; repeat :View financial assistance data; :Check if data is updated daily; repeat while (Data needs daily update?) is (yes) ->no; :Continue using website; stop @enduml
### us-0005
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.1538
- missing_nodes:
  - manage d files generation requests
  - cache d files generation requests
  - avoid performance issues caused by duplicate requests
- extra_nodes:
  - receive d files generation request
  - check cache for existing d files
  - cache hit?
  - retrieve d files from cache
  - generate d files
  - store d files in cache
  - update cache index
  - return d files
- missing_relations:
  - cache d files generation requests -> avoid performance issues caused by duplicate requests
- input_excerpt:
  As a Developer, I want D Files generation requests to be managed and cached, so that duplicate requests do not cause performance issues.
- generated_excerpt:
  @startuml start :Receive D Files generation request; :Check cache for existing D Files; if (Cache hit?) then (Yes)   :Retrieve D Files from cache; else (No)   :Generate D Files;   fork     :Store D Files in cache;   fork again     :Update cache index;   end fork endif :Return D Files; repeat :Monitor for duplicate D Files generation requests; repeat while (Duplicate request received?) is (Yes) ->No; :End request management; @enduml
### us-0001
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- extra_nodes:
  - log in as broker team member
  - identify sql codes requiring clarity updates
  - select sql code to update
  - review current sql code
  - make updates to the sql code for clarity
  - finalize sql code updates
- input_excerpt:
  As a broker team member, I want to make some updates to the SQL codes for clarity.
- generated_excerpt:
  @startuml start :Log in as broker team member; :Identify SQL codes requiring clarity updates; repeat :Select SQL code to update; :Review current SQL code; :Make updates to the SQL code for clarity; repeat while (More SQL codes to update?) is (Yes) ->No; :Finalize SQL code updates; stop @enduml
### us-0006
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.0000
- extra_nodes:
  - agency user initiates fabs validation
  - is the record a non-loan record?
  - accept zero for the non-loan record
  - apply standard fabs validation rules
  - complete fabs validation
- input_excerpt:
  As an agency user, I want the FABS validation rules to accept zero and blank for non-loan records.
- generated_excerpt:
  @startuml start :Agency user initiates FABS validation; if (Is the record a non-loan record?) then (yes)   fork     :Accept zero for the non-loan record;   fork again     :Accept blank for the non-loan record;   end fork else (no)   :Apply standard FABS validation rules; endif :Complete FABS validation; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
