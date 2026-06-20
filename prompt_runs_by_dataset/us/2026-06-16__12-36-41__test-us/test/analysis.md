# Prompt Evaluation Analysis

## Summary
- count: 220
- syntax_pass_rate: 0.9955
- infrastructure_error_rate: 0.0000
- node_precision: 0.1630
- node_recall: 0.3731
- node_f1: 0.2269
- relation_precision: 0.0787
- relation_recall: 0.2216
- relation_f1: 0.1161
- plantuml_compilation_pass_rate: 0.9955
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- extra_activity: 219
- extra_or_wrong_relation: 219
- missing_or_wrong_relation: 181
- missing_activity: 181
- wrong_parallel: 13
- syntax_error: 1

## Representative Failure Cases
### us-0130
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - associate together files involved in a experiment
- extra_nodes:
  - select files for experiment
  - association type?
  - fork file association
  - link first file to next file
  - link next file to subsequent file
  - save experiment association
- input_excerpt:
  As a user, I want to associate together files involved in a experiment.
- generated_excerpt:
  @startuml start :Select files for experiment; switch (Association type?) case (Group files) :Fork file association; end fork case (Link files sequentially) :Link first file to next file; :Link next file to subsequent file; endswitch :Save experiment association; stop @enduml
### us-0003
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - design a schedule from ui sme
  - get timeline of the ui improvements
- extra_nodes:
  - access ui sme
  - select ui improvements
  - is owner?
  - design schedule
  - view potential timeline
  - deny access
- missing_relations:
  - design a schedule from ui sme -> get timeline of the ui improvements
- input_excerpt:
  As an Owner, I want to design a schedule from the UI SME, so that I know the potential timeline of the UI improvements wanted.
- generated_excerpt:
  @startuml start :Access UI SME; :Select UI improvements; if (Is Owner?) then (yes)   :Design schedule;   :View potential timeline; else (no)   :Deny access;   stop endif stop @enduml
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
  - submit fabs record
  - is record a non-loan record?
  - is value zero?
  - accept zero value
  - is value blank?
  - accept blank value
  - apply standard validation
- input_excerpt:
  As an agency user, I want the FABS validation rules to accept zero and blank for non-loan records.
- generated_excerpt:
  @startuml start :Submit FABS record; if (Is record a non-loan record?) then (yes)   if (Is value zero?) then (yes)     :Accept zero value;   elseif (Is value blank?) then (yes)     :Accept blank value;   else (no)     :Apply standard validation;   endif else (no)   :Apply standard validation; endif stop @enduml
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
  - fetch updated financial assistance data
  - display updated financial assistance data
  - daily period elapsed?
- input_excerpt:
  As a website user, I want to see updated financial assistance data daily.
- generated_excerpt:
  @startuml start repeat :Fetch updated financial assistance data; :Display updated financial assistance data; repeat while (Daily period elapsed?) is (No) ->Yes; @enduml
### us-0024
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - use website
  - upload content
  - delete content
- extra_nodes:
  - access website
  - website easy to use?
  - choose action
  - upload stuff step by step
  - delete stuff step by step
  - stop
- missing_relations:
  - use website -> upload content [fork]
  - use website -> delete content [fork]
- input_excerpt:
  As a company, I want to have a website that is easy to use, so that I can upload or delete stuff step by step.
- generated_excerpt:
  @startuml start :Access website; if (Website easy to use?) then (yes)   switch (Choose action)   case (Upload)     :Upload stuff step by step;   case (Delete)     :Delete stuff step by step;   endswitch else (no)   :Stop; endif stop @enduml
### us-0031
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - use data to get results from multiple datasets
  - build user experiences based on dataset
- extra_nodes:
  - authenticate as api user
  - submit data query for multiple datasets
  - retrieve results from dataset 1
  - retrieve results from dataset 2
  - retrieve results from dataset n
  - aggregate results from multiple datasets
  - return aggregated results to build user experience
- missing_relations:
  - use data to get results from multiple datasets -> build user experiences based on dataset
- input_excerpt:
  As an API User, I want to be able to use data to get results from multiple datasets, So that I can build user experiences based on more than one dataset more easily.
- generated_excerpt:
  @startuml start :Authenticate as API User; :Submit data query for multiple datasets; fork  :Retrieve results from dataset 1; fork again  :Retrieve results from dataset 2; fork again  :Retrieve results from dataset N; end fork :Aggregate results from multiple datasets; :Return aggregated results to build user experience; stop @enduml
### us-0032
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - get a csv output of any cube-based query
  - use work with tools that read csv
- extra_nodes:
  - authenticate as api user
  - is api user authenticated?
  - submit cube-based query
  - request csv output format
  - process cube-based query
  - generate csv output
  - return csv output
  - deny access
- missing_relations:
  - get a csv output of any cube-based query -> use work with tools that read csv
- input_excerpt:
  As an API User, I want to be able to get a CSV output of any cube-based query, So that I can use work with tools that read CSV.
- generated_excerpt:
  @startuml start :Authenticate as API User; if (Is API User authenticated?) then (yes)   :Submit cube-based query;   :Request CSV output format;   :Process cube-based query;   :Generate CSV output;   :Return CSV output; else (no)   :Deny access;   stop endif stop @enduml
### us-0045
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - make dataset more useful
  - add useful metadata
  - add in new data columns
- extra_nodes:
  - select dataset
  - enhancement type
  - add metadata to dataset
  - add new data columns to dataset
  - update dataset
- missing_relations:
  - make dataset more useful -> add useful metadata [fork]
  - make dataset more useful -> add in new data columns [fork]
- input_excerpt:
  As a Publisher, I want to add useful metadata or add in new data columns to make the dataset more useful.
- generated_excerpt:
  @startuml start :Select dataset; switch (Enhancement type) case (Add useful metadata)  :Add metadata to dataset; case (Add new data columns)  :Add new data columns to dataset; endswitch :Update dataset; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
