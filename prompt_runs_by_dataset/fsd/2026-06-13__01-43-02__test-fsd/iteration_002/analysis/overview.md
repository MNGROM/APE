# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3726
- node_recall: 0.4560
- node_f1: 0.3948
- relation_precision: 0.2328
- relation_recall: 0.2525
- relation_f1: 0.2360
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
- extra_activity: 10
- missing_activity: 9
- missing_or_wrong_relation: 9
- extra_or_wrong_relation: 9

## Representative Failure Cases
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
  - process audio file
  - identify number of whales heard
  - display number of whales heard
- input_excerpt:
  As a Zooniverse admin, I want to identify the number of whales heard in a single audio file.
- generated_excerpt:
  @startuml start :Select audio file; :Process audio file; :Identify number of whales heard; :Display number of whales heard; stop @enduml
### lmc-0038
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1818
- relation_f1: 0.0000
- missing_nodes:
  - absolute error between zt truth data and output z <= 0.01?
  - allowed
  - not allowed
- extra_nodes:
  - compute output z
  - retrieve zt truth data
  - calculate absolute error between zt and z
  - absolute error <= 0.01?
  - tolerance met
  - tolerance exceeded
- missing_relations:
  - for equivalent input of (xt yt) -> absolute error between zt truth data and output z <= 0.01?
  - absolute error between zt truth data and output z <= 0.01? -> allowed
  - allowed -> not allowed
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Receive equivalent input (xt, yt); :Compute output z; :Retrieve zt truth data; :Calculate absolute error between zt and z; if (Absolute error <= 0.01?) then (Yes)   :Tolerance met; else (No)   :Tolerance exceeded; endif stop @enduml
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
  - respond to user parameter changes
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
  @startuml start :Respond to incoming correlator mode changes; :Respond to user optional processing sequence changes; :Respond to user parameter changes; :Respond to other external inputs affecting data processing pipeline; :Update internal parameter tables; :Synchronize data processing pipeline with new operational conditions; stop @enduml
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3273
- relation_f1: 0.1887
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - 1
  - go to promotion jobs home page
  - 2
  - right-click
  - select source and destination systems
  - go to external change management id field
- extra_nodes:
  - enter external change management id and click save
  - security settings required?
  - security option
  - select do not promote security (default)
  - promote security
  - select promote security
  - include application rights?
  - select include application rights
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
  @startuml start :Select the job to promote; :Select source and destination systems from drop-down lists; :Ensure logged into both source and destination systems; :Enter External Change Management ID and click Save; :Click Mappings; if (Want to create and validate mappings?) then (Yes)   :Click Edit Mappings; else (No) endif if (Security Settings required?) then (Yes)   :Click Security Settings;   switch (Security Option)   case (Do not Promote Security)     :Select Do not Promote Security (default);   case (Promote Security)     :Select Promote Security;     if (Include application rights?) then (Yes)       :Select Include application rights;     else (No)     endif   endswitch   if (View Se
### lmc-0011
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4444
- relation_f1: 0.3333
- missing_nodes:
  - autopilot change states from pullup to transition
- extra_nodes:
  - pullup
  - transition
  - remain in pullup
  - remain in pullup
- missing_relations:
  - sensor data is good? -> autopilot change states from pullup to transition
- input_excerpt:
  7.	The autopilot shall change states from PULLUP to TRANSITION when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml start :PULLUP; if (System is supported?) then (yes)   if (Sensor data is good?) then (yes)     :TRANSITION;   else (no)     :Remain in PULLUP;   endif else (no)   :Remain in PULLUP; endif stop @enduml
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4746
- relation_f1: 0.2807
- missing_nodes:
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - open data source context menu
  - open data source context menu
  - choose create info package...
- extra_nodes:
  - in modeling area choose info provider
  - view transformation and data source under info cube sales overview
  - in context menu of data source choose create info package
  - enter description for info package
  - view info package maintenance screen for scheduler
  - choose monitor in toolbar of info package maintenance
  - view monitor for load process
  - select load process for data source from tree
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
  @startuml start :Go to Data Warehousing Workbench; :In Modeling area, choose Info Provider; :View transformation and Data source under Info Cube Sales Overview; :In context menu of Data source, choose Create Info Package; :Enter description for Info Package; :Choose Save; :View Info Package maintenance screen for scheduler; :Go to tab page Schedule; :Choose Start; :Choose Monitor in toolbar of Info Package maintenance; :Select date; :Choose Execute; :View monitor for load process; :Select load process for Data source from tree; :Exit Info Package maintenance screen; :From context menu of Data source, choose Create Data Transfer Process; :View generated description, type, source and target of
### rac-0004
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.1852
- missing_nodes:
  - slow charging state is 1 and charging/discharging power-up is ready
  - vehicle charging/discharging mode is 2 and power-up is ready
  - switch to state 105
  - condition judgement
  - high-voltage shutdown charging/discharging value is 3 or 4
  - slow charging?
  - slow charging?
  - slow charging?
- extra_nodes:
  - system starts up
  - slow charging is active (state 1
  - vehicle charging/discharging mode is 2 and system is powered up?
  - condition while in state 105?
  - high-voltage shutdown value is 3 or 4
  - slow charging becomes inactive?
  - slow charging becomes inactive?
  - slow charging becomes inactive?
- missing_relations:
  - slow charging state is 1 and charging/discharging power-up is ready -> switch to state 95
  - switch to state 95 -> vehicle charging/discharging mode is 2 and power-up is ready
  - vehicle charging/discharging mode is 2 and power-up is ready -> switch to state 105
  - switch to state 105 -> condition judgement
  - condition judgement -> high-voltage shutdown charging/discharging value is 3 or 4
  - high-voltage shutdown charging/discharging value is 3 or 4 -> switch to state 115
  - switch to state 115 -> slow charging?
  - switch to state 115 -> slow charging?
- input_excerpt:
  After the system starts up: - If slow charging is active (state 1) and the charging/discharging system is powered up, switch to state 95. - If the vehicle charging/discharging mode is 2 and the system is powered up, switch to state 105. Then, while in state 105:   1) If the high-voltage shutdown value is 3 or 4, switch to state 115. If slow charging becomes inactive during this, shut down and end the process.   2) If a high-voltage shutdown request (value 3) occurs while the ignition is on (position 2), return to state 105. If the ignition turns off (position 0), switch to state 115. If slow charging becomes inactive, shut down and end.   3) If a pre-charge failure happens, switch to state 1
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active (state 1)\nand charging/discharging system is powered up?) then (yes)   :Switch to state 95; else (no)   if (Vehicle charging/discharging mode is 2\nand system is powered up?) then (yes)     :Switch to state 105;     switch (Condition while in state 105?)     case (High-voltage shutdown value is 3 or 4)       :Switch to state 115;       if (Slow charging becomes inactive?) then (yes)         :Shut down;         end       else (no)       endif     case (High-voltage shutdown request (value 3)\noccurs while ignition is on (position 2))       :Return to state 105;       if (Slow charging becomes inactive?) then (yes)         :Shut d
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
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
