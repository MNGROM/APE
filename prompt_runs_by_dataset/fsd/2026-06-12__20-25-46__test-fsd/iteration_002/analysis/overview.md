# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2268
- node_recall: 0.2136
- node_f1: 0.2183
- relation_precision: 0.1655
- relation_recall: 0.1623
- relation_f1: 0.1634
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
- missing_activity: 10
- extra_activity: 10
- missing_or_wrong_relation: 9
- extra_or_wrong_relation: 9

## Representative Failure Cases
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - 1
  - go to promotion jobs home page
  - select the job want to promote
  - 2
  - right-click
  - click promote
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - in the promotion jobs home page select the job that you want to promote
  - select the job
  - right-click the home page screen and click promote
  - from the source and the destination systems drop-down lists select the source and destination systems
- missing_relations:
  - log in lifecycle manager tool -> selection method
  - selection method -> 1
  - 1 -> go to promotion jobs home page
  - go to promotion jobs home page -> select the job want to promote
  - select the job want to promote -> 2
  - 2 -> right-click
  - right-click -> click promote
  - click promote -> open source and destination systems drop-down lists
- input_excerpt:
  23.	promote a jobLog into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, select the job that you want to promote. You can also right-click the home page screen, and click Promote.3. From the source and the destination systems drop-down lists, select the source and destination systems.Note:Ensure that you have logged into both the source and destination systems before you proceed with the promotion process.4. In the External Change Management ID field, enter the appropriate value, and click Save.5. Click Mappings. Click Edit Mappings if you want to create and validate mappings.6. Click Security Settings, if required. The following options are displayed:• Do not Promote Secur
- generated_excerpt:
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, select the job that you want to promote; fork   :Select the job; fork again   :Right-click the home page screen, and click Promote; end fork :From the source and the destination systems drop-down lists, select the source and destination systems; note right: Ensure that you have logged into both the source and destination systems before you proceed :In the External Change Management ID field, enter the appropriate value, and click Save; :Click Mappings; if (Want to create and validate mappings?) then (yes)   :Click Edit Mappings; else (no) endif if (Security Settings required?) then (yes)   
### lmc-0011
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - system is supported?
  - sensor data is good?
  - autopilot change states from pullup to transition
- extra_nodes:
  - pullup
  - system is supported and sensor data is good?
  - transition
- missing_relations:
  - system is supported? -> sensor data is good?
  - sensor data is good? -> autopilot change states from pullup to transition
- input_excerpt:
  7.	The autopilot shall change states from PULLUP to TRANSITION when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml start :PULLUP; if (System is supported and sensor data is good?) then (yes)   :TRANSITION; else (no) endif stop @enduml
### us-0153
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - receive regular summary reports of research data
  - get trends in data use among staff and postgraduate students
- extra_nodes:
  - schedule regular reporting interval
  - collect research data usage logs
  - aggregate usage data for staff
  - aggregate usage data for postgraduate students
  - generate summary report of research data
  - send summary report to postgraduate convenor
- missing_relations:
  - receive regular summary reports of research data -> get trends in data use among staff and postgraduate students
- input_excerpt:
  As a Postgraduate Convenor, I want to receive regular summary reports of research data, so that I understand trends in data use among staff and postgraduate students.
- generated_excerpt:
  @startuml start :Schedule regular reporting interval; :Collect research data usage logs; :Aggregate usage data for staff; :Aggregate usage data for postgraduate students; :Generate summary report of research data; :Send summary report to Postgraduate Convenor; stop @enduml
### lmc-0038
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - for equivalent input of (xt yt)
  - absolute error between zt truth data and output z <= 0.01?
  - allowed
  - not allowed
- extra_nodes:
  - compute absolute error between zt truth data and output z for equivalent input (xt yt)
  - absolute error > 0.01?
  - requirement violation
  - requirement satisfied
- missing_relations:
  - for equivalent input of (xt yt) -> absolute error between zt truth data and output z <= 0.01?
  - absolute error between zt truth data and output z <= 0.01? -> allowed
  - allowed -> not allowed
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Compute absolute error between zt truth data and output z for equivalent input (xt, yt); if (Absolute error > 0.01?) then (Yes)   :Requirement violation;   stop else (No)   :Requirement satisfied;   stop endif @enduml
### us-0216
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - identify the number of whales heard in a single audio file
- extra_nodes:
  - select audio file
  - play audio file
  - identify number of whales heard
  - log whale count
- input_excerpt:
  As a Zooniverse admin, I want to identify the number of whales heard in a single audio file.
- generated_excerpt:
  @startuml start :Select audio file; :Play audio file; :Identify number of whales heard; :Log whale count; stop @enduml
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1509
- relation_f1: 0.0392
- missing_nodes:
  - go to data warehousing workbench
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - open data source context menu
  - open data source context menu
- extra_nodes:
  - go to the data warehousing workbench in the modeling area choose info provider
  - view transformation and data source in the info area below the info cube sales overview
  - in the context menu of the data source choose create info package...
  - enter a description for the info package and choose save
  - the info package maintenance screen for the scheduler appears
  - go to the tab page schedule and choose start
  - to check the load process choose monitor in the toolbar of info package maintenance
  - select the date and choose execute
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation
  - transformation -> data source
  - data source -> open data source context menu
  - open data source context menu -> choose create info package...
  - choose create info package... -> enter description
- input_excerpt:
  7.	Loading Transaction Data1. Go to the Data Warehousing Workbench; in the Modeling area choose Info Provider. The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview.2. In the context menu of the Data source, choose Create Info Package...3. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.4. Go to the tab page Schedule and choose Start.5. To check the load process, choose Monitor in the toolbar of Info Package maintenance.6. On the next screen, select the date and choose Execute. The monitor for the load process is displayed.7. Select the load process f
- generated_excerpt:
  @startuml start :Go to the Data Warehousing Workbench;\nin the Modeling area choose Info Provider; :View transformation and Data source\nin the Info Area below the Info Cube Sales Overview; :In the context menu of the Data source,\nchoose Create Info Package...; :Enter a description for the Info Package\nand choose Save; :The Info Package maintenance screen\nfor the scheduler appears; :Go to the tab page Schedule\nand choose Start; :To check the load process,\nchoose Monitor in the toolbar of Info Package maintenance; :Select the date and choose Execute; :The monitor for the load process is displayed; :Select the load process for your Data source\nfrom the tree at the left of the screen; :Ex
### pure-0030
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3077
- relation_f1: 0.0000
- missing_nodes:
  - respond to
  - user optional processing sequence
  - parameter changes
  - other affective external inputs
  - synchronize data processing pipeline
- extra_nodes:
  - respond to user optional processing sequence changes
  - respond to user optional parameter changes
  - respond to other external inputs affecting data processing pipeline
  - synchronize data processing pipeline with new operational conditions
- missing_relations:
  - respond to -> incoming correlator mode changes
  - incoming correlator mode changes -> user optional processing sequence
  - user optional processing sequence -> parameter changes
  - parameter changes -> other affective external inputs
  - other affective external inputs -> update internal parameter tables
  - update internal parameter tables -> synchronize data processing pipeline
- input_excerpt:
  Processing Management – The BE shall respond to incoming correlator mode changes, user optional processing sequence and/or parameter changes, and other external inputs that affect the data processing pipeline. Update internal parameter tables and synchronize data processing pipeline with new operational conditions.
- generated_excerpt:
  @startuml start :Respond to incoming correlator mode changes; :Respond to user optional processing sequence changes; :Respond to user optional parameter changes; :Respond to other external inputs affecting data processing pipeline; :Update internal parameter tables; :Synchronize data processing pipeline with new operational conditions; stop @enduml
### pure-0010
- dataset: pure
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- missing_nodes:
  - save trade instruction
- extra_nodes:
  - save the trade information
- input_excerpt:
  1. central trading system: give out the successful trade information 2. security account management: save the trade information
- generated_excerpt:
  @startuml start :Give out the successful trade information; :Save the trade information; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
