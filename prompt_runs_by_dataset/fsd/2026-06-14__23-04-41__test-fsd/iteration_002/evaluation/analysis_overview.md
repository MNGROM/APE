# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 0.9500
- infrastructure_error_rate: 0.0000
- node_precision: 0.2794
- node_recall: 0.2722
- node_f1: 0.2757
- relation_precision: 0.1970
- relation_recall: 0.2275
- relation_f1: 0.2111
- plantuml_compilation_pass_rate: 0.9500
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7088
- llm_node_recall: 0.8196
- llm_node_f1: 0.7279
- llm_relation_precision: 0.5232
- llm_relation_recall: 0.5332
- llm_relation_f1: 0.4935

## Failure Types
- missing_activity: 20
- extra_activity: 20
- extra_or_wrong_relation: 20
- missing_or_wrong_relation: 19
- wrong_parallel: 4
- syntax_error: 1

## Representative Failure Cases
### pure-0040
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4762
- relation_f1: 0.3000
- llm_element_status: success
- llm_node_f1: 0.8800
- llm_relation_f1: 0.6400
- missing_nodes:
  - see view inventory
  - navigate to category
  - display category type screen
  - unique item?
  - system validates data
  - system updates information
  - back to category screen
- extra_nodes:
  - user navigates to a category (see view inventory)
  - system validates the category data
  - system updates the category information
  - user is taken back to the category screen
- missing_relations:
  - see view inventory -> navigate to category
  - navigate to category -> display edit category button
  - click edit category button -> display category type screen
  - display category type screen -> unique item?
  - unique item? -> display unique item screen [yes]
  - unique item? -> display stock item screen [no]
  - display unique item screen -> edit category data
  - system validates data -> system updates information
- input_excerpt:
  2. Edit Category 2.1. User navigates to a Category (see View Inventory) 2.2. System displays the Edit Category button 2.3. User clicks the Edit Category button 2.4. System displays the appropriate screen for the Category type 2.4.1. Unique Item 2.4.2. Stock Item 2.5. User edits Category data 2.6. System validates the Category data 2.7. System updates the Category information 2.8. User is taken back to the Category screen
- generated_excerpt:
  @startuml start :User navigates to a Category (see View Inventory); :System displays the Edit Category button; :User clicks the Edit Category button; switch case (Unique Item)   :System displays the Unique Item screen; case (Stock Item)   :System displays the Stock Item screen; endswitch :User edits Category data; :System validates the Category data; :System updates the Category information; :User is taken back to the Category screen; stop @enduml
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.0000
- llm_relation_f1: 0.0000
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - go to promotion jobs home page
  - select the job want to promote
  - right-click
  - click promote
  - open source and destination systems drop-down lists
  - select source and destination systems
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - in the promotion jobs home page select the job to promote (alternatively right-click the home page screen and click promote)
  - select source and destination systems from drop-down lists
- missing_relations:
  - log in lifecycle manager tool -> selection method
  - selection method -> go to promotion jobs home page [case 1]
  - go to promotion jobs home page -> select the job want to promote
  - selection method -> right-click [case 2]
  - right-click -> click promote
  - select the job want to promote -> open source and destination systems drop-down lists
  - click promote -> open source and destination systems drop-down lists
  - open source and destination systems drop-down lists -> select source and destination systems
- input_excerpt:
  23.	promote a jobLog into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, select the job that you want to promote. You can also right-click the home page screen, and click Promote.3. From the source and the destination systems drop-down lists, select the source and destination systems.Note:Ensure that you have logged into both the source and destination systems before you proceed with the promotion process.4. In the External Change Management ID field, enter the appropriate value, and click Save.5. Click Mappings. Click Edit Mappings if you want to create and validate mappings.6. Click Security Settings, if required. The following options are displayed:• Do not Promote Secur
- generated_excerpt:
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, select the job to promote\n(Alternatively, right-click the home page screen and click Promote); :Select source and destination systems from drop-down lists; note right: Ensure that you have logged into\nboth source and destination systems\nbefore proceeding. :Enter appropriate value in External Change Management ID field; :Click Save; :Click Mappings; :Click Edit Mappings to create and validate mappings; :Click Security Settings (if required); if (Security Settings?) then (Do not Promote Security)   :Default option selected; elseif (Promote Security?) then (Promote Security)   :Promote jobs
### pure-0010
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - give out successful trade information
  - save trade instruction
- extra_nodes:
  - central trading system give out the successful trade information
  - security account management save the trade information
- missing_relations:
  - give out successful trade information -> save trade instruction
- input_excerpt:
  1. central trading system: give out the successful trade information 2. security account management: save the trade information
- generated_excerpt:
  @startuml start :Central Trading System: Give out the successful trade information; :Security Account Management: Save the trade information; stop @enduml
### us-0153
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4286
- llm_relation_f1: 0.5000
- missing_nodes:
  - receive regular summary reports of research data
  - get trends in data use among staff and postgraduate students
- extra_nodes:
  - schedule regular report generation
  - collect research data usage logs
  - aggregate data for staff and postgraduate students
  - analyze data usage trends
  - generate summary report
  - send summary report to postgraduate convenor
  - postgraduate convenor reviews report
  - convenor understands data use trends
- missing_relations:
  - receive regular summary reports of research data -> get trends in data use among staff and postgraduate students
- input_excerpt:
  As a Postgraduate Convenor, I want to receive regular summary reports of research data, so that I understand trends in data use among staff and postgraduate students.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Schedule regular report generation;  :Collect research data usage logs;  :Aggregate data for staff and postgraduate students;  :Analyze data usage trends;  :Generate summary report;  :Send summary report to Postgraduate Convenor;  :Postgraduate Convenor reviews report;  :Convenor understands data use trends;  stop  @enduml
### us-0216
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2667
- llm_relation_f1: 0.0000
- missing_nodes:
  - identify the number of whales heard in a single audio file
- extra_nodes:
  - admin selects an audio file
  - load audio file into analysis tool
  - play audio file
  - admin listens for whale sounds
  - whale sounds detected?
  - count distinct whale sounds
  - enter number of whales identified
  - enter 0 for number of whales
- input_excerpt:
  As a Zooniverse admin, I want to identify the number of whales heard in a single audio file.
- generated_excerpt:
  @startuml skinparam style strictuml  title Zooniverse Admin: Identify Number of Whales in an Audio File  start  :Admin selects an audio file;  :Load audio file into analysis tool;  :Play audio file;  :Admin listens for whale sounds;  if (Whale sounds detected?) then (Yes)   :Count distinct whale sounds;   :Enter number of whales identified; else (No)   :Enter 0 for number of whales; endif  :Submit whale count;  :Save results to database;  stop @enduml
### us-0064
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4706
- llm_relation_f1: 0.1176
- missing_nodes:
  - get early indications of hypothesess
  - start planning for first prototype
- extra_nodes:
  - identify design goal
  - analyze data for patterns
  - patterns found?
  - viable for prototype?
  - formulate initial hypotheses
  - expand research scope
- missing_relations:
  - get early indications of hypothesess -> start planning for first prototype
- input_excerpt:
  As a designer, I want to know what early indications of hypotheses might be, so that I can start planning for the first prototype.
- generated_excerpt:
  @startuml skinparam style strictuml  title Activity Diagram: Early Indications of Hypotheses for Prototype Planning  start  :Identify Design Goal;  :Gather User Data (Observations, Interviews, Analytics);  :Analyze Data for Patterns;  if (Patterns Found?) then (Yes)   :Extract Early Indications   of Hypotheses;      :Evaluate Indications   for Prototype Viability;      if (Viable for Prototype?) then (Yes)     :Formulate Initial Hypotheses;     :Start Planning for     First Prototype;     stop   else (No)     :Refine Data Gathering     Approach;   endif    else (No)   :Expand Research Scope; endif  @enduml
### us-0198
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3077
- llm_relation_f1: 0.0000
- missing_nodes:
  - restrict a group of files from view
- extra_nodes:
  - select a group of files
  - choose restrict from view option
  - confirm restriction action
  - restriction applied successfully?
  - update file group access permissions
  - hide files from public view
  - display success message
  - display error message
- input_excerpt:
  As an archivist, I want to restrict a group of files from view.
- generated_excerpt:
  @startuml skinparam style strictuml  title Archivist - Restrict a group of files from view  start  :Select a group of files;  :Choose "Restrict from view" option;  :Confirm restriction action;  if (Restriction applied successfully?) then (Yes)   :Update file group access permissions;   :Hide files from public view;   :Display success message; else (No)   :Display error message; endif  stop @enduml
### lmc-0038
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.2000
- llm_element_status: success
- llm_node_f1: 0.7500
- llm_relation_f1: 0.5000
- missing_nodes:
  - for equivalent input of (xt yt)
  - absolute error between zt truth data and output z <= 0.01?
  - allowed
  - not allowed
- extra_nodes:
  - receive input (xt yt)
  - compute output z from (xt yt)
  - retrieve zt truth data for (xt yt)
  - calculate absolute error = zt - z
  - absolute error <= 0.01?
  - validation passed
  - validation failed
  - raise error or flag violation
- missing_relations:
  - absolute error between zt truth data and output z <= 0.01? -> allowed [yes]
  - absolute error between zt truth data and output z <= 0.01? -> not allowed [no]
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Receive input (xt, yt); :Compute output z from (xt, yt); :Retrieve zt truth data for (xt, yt); :Calculate absolute error = |zt - z|; if (Absolute error <= 0.01?) then (Yes)   :Validation passed; else (No)   :Validation failed;   :Raise error or flag violation; endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
