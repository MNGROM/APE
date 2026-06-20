# Prompt Evaluation Analysis

## Summary
- count: 220
- syntax_pass_rate: 0.9682
- infrastructure_error_rate: 0.0000
- node_precision: 0.0420
- node_recall: 0.1839
- node_f1: 0.0684
- relation_precision: 0.0194
- relation_recall: 0.0996
- relation_f1: 0.0325
- plantuml_compilation_pass_rate: 0.9682
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- extra_activity: 220
- extra_or_wrong_relation: 220
- missing_activity: 205
- missing_or_wrong_relation: 203
- wrong_parallel: 13
- syntax_error: 7
- wrong_loop: 1

## Representative Failure Cases
### us-0050
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - match-making service for packaging data
  - pair owners with data packages
- extra_nodes:
  - repositorymanagerresearcher initiates match-making
  - owner submits packaging data request
  - specify data type and packaging requirements
  - packager submits availability and skills
  - specify packaging capabilities
  - app receives and validates submissions
  - valid submissions?
  - request corrections
- missing_relations:
  - match-making service for packaging data -> pair owners with data packages
- input_excerpt:
  As a RepositoryManagerResearcher, I want an app that acts as a match-making service for packaging data, so that owners are paired with data packagers.
- generated_excerpt:
  @startuml left to right direction  skinparam activityBackgroundColor #LightBlue skinparam activityDiamondBackgroundColor #LightYellow  start  :RepositoryManagerResearcher initiates match-making;  partition "Data Owner Submission" {     :Owner submits packaging data request;     :Specify data type and packaging requirements; }  partition "Data Packager Submission" {     :Packager submits availability and skills;     :Specify packaging capabilities; }  :App receives and validates submissions;  if (Valid submissions?) then (No)     :Request corrections;     stop else (Yes) endif  :App analyzes data requirements vs packager capabilities;  :App calculates compatibility scores;  if (Compatible mat
### us-0170
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - manage digital objects
- extra_nodes:
  - archivist
  - view list of digital objects
  - select action
  - enter digital object details
  - submit new digital object
  - system validates input
  - valid?
  - save digital object
- input_excerpt:
  As an Archivist, I want to manage Digital Objects.
- generated_excerpt:
  @startuml left to right direction  skinparam activityBackgroundColor #LightBlue skinparam activityDiamondBackgroundColor #LightYellow  start  :Archivist;  partition "Manage Digital Objects" {   :View List of Digital Objects;    switch (Select Action)   case (Create)     :Enter Digital Object Details;     :Submit New Digital Object;     :System Validates Input;     if (Valid?) then (Yes)       :Save Digital Object;       :Display Success Message;     else (No)       :Display Validation Errors;       stop     endif    case (Read / View)     :Select Digital Object;     :Fetch Digital Object Details;     :Display Digital Object;    case (Update)     :Select Digital Object;     :Fetch Current Det
### us-0015
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0870
- relation_f1: 0.0000
- missing_nodes:
  - manage inspector workload
- extra_nodes:
  - inspection supervisor logs into the system
  - access inspector workload dashboard
  - view current workload assignments and service level metrics
  - monitor current assignments
  - exit workflow
  - identify workload imbalances or quality risks
  - select adjustment action
  - select inspections to reassign
- missing_relations:
  - manage inspector workload -> meet service level and quality requirements
- input_excerpt:
  As an Inspection Supervisor, I want to Manage Inspector Workload, so that I can meet service level and quality requirements.
- generated_excerpt:
  @startuml left to right direction  skinparam activityBackgroundColor #E8F4FD skinparam activityDiamondBackgroundColor #FFF3E0  title Manage Inspector Workload - Activity Diagram  start  :Inspection Supervisor logs into the system;  :Access Inspector Workload Dashboard;  :View current workload assignments and service level metrics;  if (Are service level and quality requirements met?) then (Yes)   :Monitor current assignments;   :Exit workflow;   stop else (No)   :Identify workload imbalances or quality risks;      if (Select adjustment action) then (Reassign Inspections)     :Select inspections to reassign;     :Choose target inspector with available capacity;     :Reassign inspections;   el
### us-0018
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.1250
- relation_f1: 0.0000
- missing_nodes:
  - grant request to begin work
- extra_nodes:
  - development staff member logs into system
  - select issue development permit
  - retrieve submitted permit application
  - application complete and valid?
  - notify applicant of missing/invalid information
  - review development request details
  - complies with development regulations?
  - reject permit request
- missing_relations:
  - issue a development-related permit -> grant request to begin work
- input_excerpt:
  As a Development Staff member, I want to Issue a Development-related Permit, so that I can grant the request to the Applicant to begin work
- generated_excerpt:
  @startuml left to right direction  skinparam activityBackgroundColor #LightBlue skinparam activityDiamondBackgroundColor #LightYellow  start  :Development Staff member logs into system;  :Select "Issue Development Permit";  :Retrieve submitted permit application;  if (Application complete and valid?) then (No)   :Notify Applicant of missing/invalid information;   stop else (Yes)   :Review development request details;      if (Complies with development regulations?) then (No)     :Reject permit request;     :Notify Applicant of rejection and reasons;     stop   else (Yes)     :Approve permit request;     :Generate Development Permit;     :Record permit issuance in system;     :Issue Developme
### us-0066
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.1333
- relation_f1: 0.0000
- missing_nodes:
  - implement beta site without established brand guidelines
- extra_nodes:
  - team member initiates design direction process
  - review existing brand assets and partial guidelines
  - are there any usable brand guidelines?
  - extract applicable design elements (colors typography spacing)
  - define temporary foundational styles (neutral palette standard fonts)
  - create low-fidelity mockups for top design directions
  - review mockups with the team
  - team alignment achieved?
- missing_relations:
  - determine a design direction for the beta social page -> implement beta site without established brand guidelines
- input_excerpt:
  As a team member, I want to determine a design direction for the beta social page, so that we can implement a beta site quickly without established brand guidelines.
- generated_excerpt:
  @startuml skinparam style strictuml  title Determine Design Direction for Beta Social Page  start  :Team member initiates design direction process;  :Review existing brand assets and partial guidelines;  if (Are there any usable brand guidelines?) then (Yes)   :Extract applicable design elements\n(colors, typography, spacing); else (No)   :Define temporary foundational styles\n(neutral palette, standard fonts); endif  :Explore design directions for beta social page;  :Create low-fidelity mockups\nfor top design directions;  :Review mockups with the team;  if (Team alignment achieved?) then (Yes)   :Select design direction; else (No)   :Gather feedback and iterate;   note right: Loop back to 
### us-0091
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.1667
- relation_f1: 0.0000
- missing_nodes:
  - work with most recent data
- extra_nodes:
  - data analyst selects previously downloaded data package
  - request update for data package
  - check for newer version on server
  - display loading indicator
  - newer version available?
  - replace old data package with new data
  - notify user data package updated successfully
  - notify user data is already up to date
- missing_relations:
  - update previously downloaded data package -> work with most recent data
- input_excerpt:
  As a Data Analyst, I want to update previously downloaded data package, so that that I can work with the most recent data.
- generated_excerpt:
  @startuml left to right direction  skinparam activityBackgroundColor #LightBlue skinparam activityDiamondBackgroundColor #LightYellow  start  :Data Analyst selects previously downloaded data package;  :Request update for data package;  fork   :Check for newer version on server; fork again   :Display loading indicator; end fork  if (Newer version available?) then (Yes)   :Download updated data package;   :Replace old data package with new data;   :Notify user: Data package updated successfully; else (No)   :Notify user: Data is already up to date; endif  :Data Analyst works with the most recent data;  stop  @enduml
### us-0045
- dataset: us
- failure_types: syntax_error, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.6000
- relation_f1: 0.0000
- extra_nodes:
  - publisher selects dataset
  - review updates
  - save and publish updated dataset
  - edit updates
- missing_relations:
  - make dataset more useful -> add useful metadata [fork]
  - make dataset more useful -> add in new data columns [fork]
- input_excerpt:
  As a Publisher, I want to add useful metadata or add in new data columns to make the dataset more useful.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Publisher selects dataset;  fork   :Add useful metadata;   note right: e.g., tags, descriptions, provenance fork again   :Add new data columns;   note right: e.g., derived metrics, new attributes end fork  :Review updates;  if (Is dataset more useful?) then (Yes)   :Save and publish updated dataset;   stop else (No)   :Edit updates;   rewind endif  @enduml
### us-0001
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - make updates to sql codes
- extra_nodes:
  - start sql code update
  - identify sql code requiring clarity updates
  - open sql code in editor
  - review current sql code logic
  - refactor sql code for clarity (e.g. aliasing formatting comments)
  - validate updated sql code syntax
  - syntax valid?
  - run test queries
- input_excerpt:
  As a broker team member, I want to make some updates to the SQL codes for clarity.
- generated_excerpt:
  @startuml start :Start SQL Code Update; :Identify SQL code requiring clarity updates; :Open SQL code in editor; :Review current SQL code logic; :Refactor SQL code for clarity (e.g., aliasing, formatting, comments); :Validate updated SQL code syntax; if (Syntax Valid?) then (Yes)   :Run test queries;   if (Results Match Expected?) then (Yes)     :Commit updated SQL code;     :Finish;     stop   else (No)     :Debug logic errors;     :Refactor SQL code for clarity;     note right: Retry   endif else (No)   :Fix syntax errors;   :Refactor SQL code for clarity;   note right: Retry endif @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
