# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3496
- node_recall: 0.3527
- node_f1: 0.3457
- relation_precision: 0.1915
- relation_recall: 0.1754
- relation_f1: 0.1822
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
  - select the job to promote in the promotion jobs home page
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
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :Select the job to promote in the "Promotion Jobs" home page; note right: You can also right-click the home page screen, and click Promote :Select the source and destination systems from drop-down lists; note right: Ensure that you have logged into both the source and destination systems before you proceed :Enter the appropriate value in the External Change Management ID field; :Click Save; :Click Mappings; :Click Edit Mappings to create and validate mappings; :Click Security Settings if required; switch (Security Settings Option) case (Do not Promote Security)   :Select Do not Promote Security (default); case (Promote Securi
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
  - input (xt yt)
  - compute output z
  - retrieve zt truth data
  - calculate absolute error between zt and z
  - absolute error > 0.01?
  - exceed tolerance
  - within tolerance
- missing_relations:
  - for equivalent input of (xt yt) -> absolute error between zt truth data and output z <= 0.01?
  - absolute error between zt truth data and output z <= 0.01? -> allowed
  - allowed -> not allowed
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Input (xt, yt); :Compute output z; :Retrieve zt truth data; :Calculate absolute error between zt and z; if (Absolute error > 0.01?) then (yes) :Exceed tolerance; else (no) :Within tolerance; endif stop @enduml
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
  - record whale count
- input_excerpt:
  As a Zooniverse admin, I want to identify the number of whales heard in a single audio file.
- generated_excerpt:
  @startuml start :Select audio file; :Play audio file; :Identify number of whales heard; :Record whale count; stop @enduml
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
  - respond to other external inputs that affect the data processing pipeline
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
  @startuml start :Respond to incoming correlator mode changes; :Respond to user optional processing sequence changes; :Respond to user optional parameter changes; :Respond to other external inputs that affect the data processing pipeline; :Update internal parameter tables; :Synchronize data processing pipeline with new operational conditions; stop @enduml
### lmc-0011
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.0000
- missing_nodes:
  - system is supported?
  - sensor data is good?
- extra_nodes:
  - change state from pullup to transition
  - system is supported and sensor data is good?
- missing_relations:
  - system is supported? -> sensor data is good?
  - sensor data is good? -> autopilot change states from pullup to transition
- input_excerpt:
  7.	The autopilot shall change states from PULLUP to TRANSITION when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml start :Change state from PULLUP to TRANSITION; if (System is supported and sensor data is good?) then (yes)   :Change state from PULLUP to TRANSITION; else (no) endif stop @enduml
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
  - in the modeling area choose info provider
  - view the transformation and the data source in the info area below the info cube sales overview
  - in the context menu of the data source choose create info package
  - enter a description for the info package
  - view the info package maintenance screen for the scheduler
  - to check the load process choose monitor in the toolbar of info package maintenance
  - view the monitor for the load process
  - select the load process for your data source from the tree at the left of the screen
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
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose Info Provider; :View the transformation and the Data source in the Info Area below the Info Cube Sales Overview; :In the context menu of the Data source, choose Create Info Package; :Enter a description for the Info Package; :Choose Save; :View the Info Package maintenance screen for the scheduler; :Go to the tab page Schedule; :Choose Start; :To check the load process, choose Monitor in the toolbar of Info Package maintenance; :Select the date; :Choose Execute; :View the monitor for the load process; :Select the load process for your Data source from the tree at the left of the screen; :Exit the Info Package
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
  @startuml start :Give out the successful trade information; fork :Save the trade information; fork again end fork @enduml
### rac-0004
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5185
- relation_f1: 0.1923
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
  @startuml start :System starts up; if (Slow charging is active (state 1) and charging/discharging system is powered up?) then (yes)   :Switch to state 95; elseif (Vehicle charging/discharging mode is 2 and system is powered up?) then (yes)   :Switch to state 105;   switch (Condition while in state 105?)   case (High-voltage shutdown value is 3 or 4)     :Switch to state 115;     if (Slow charging becomes inactive?) then (yes)       :Shut down;       end     endif   case (High-voltage shutdown request (value 3) occurs while ignition is on (position 2))     :Return to state 105;   case (Ignition turns off (position 0))     :Switch to state 115;     if (Slow charging becomes inactive?) then (ye

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
