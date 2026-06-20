# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.8000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4735
- node_recall: 0.4546
- node_f1: 0.4579
- relation_precision: 0.4028
- relation_recall: 0.4044
- relation_f1: 0.4024
- plantuml_compilation_pass_rate: 0.8000
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_activity: 8
- extra_activity: 8
- missing_or_wrong_relation: 7
- extra_or_wrong_relation: 7
- syntax_error: 2

## Representative Failure Cases
### rac-0004
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.3396
- relation_f1: 0.1569
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
  - slow charging is active (state 1
  - the vehicle charging/discharging mode is 2 and the system is powered up
  - the high-voltage shutdown value is 3 or 4
  - slow charging becomes inactive during this
  - shut down and end the process
  - a high-voltage shutdown request (value 3
  - return to state 105
  - the ignition turns off (position 0
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
  @startuml start if (slow charging is active (state 1) and the charging/discharging system is powered up) then   :switch to state 95; elseif (the vehicle charging/discharging mode is 2 and the system is powered up) then   :switch to state 105;   repeat     switch       case (the high-voltage shutdown value is 3 or 4)         :switch to state 115;         if (slow charging becomes inactive during this) then           :shut down and end the process;           stop         endif       endcase       case (a high-voltage shutdown request (value 3) occurs while the ignition is on (position 2))         :return to state 105;         if (the ignition turns off (position 0)) then           :switch to s
### rac-0020
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.6170
- relation_f1: 0.7609
- missing_nodes:
  - gw_trigger=2 and battery soc=20
  - gw_trigger=0 and dcdc state=3
  - gw_trigger=0 and dcdc state=3
  - gw_trigger=0 and dcdc state=3
  - shutdown
  - shutdown
  - shutdown
  - shutdown
- extra_nodes:
  - system starts up
  - gw_trigger equals 2 and battery soc is 20
  - gw_trigger equals 0 and dcdc state is 3
  - gw_trigger equals 0 and dcdc state is 3
  - gw_trigger equals 0 and dcdc state is 3
  - shut down and exit
  - shut down and exit
  - shut down and exit
- missing_relations:
  - gw_trigger=0 and dcdc state=3 -> shutdown
  - gw_trigger=0 and dcdc state=3 -> shutdown
  - gw_trigger=0 and dcdc state=3 -> shutdown
  - shutdown -> slow charging active
  - shutdown -> fast charging active
  - shutdown -> gw_trigger=2
  - switch to state 10 -> battery soc=20
  - battery soc=20 -> switch to state 28
- input_excerpt:
  After the system starts up, the following steps occur:  First, for remote mode handling: if remote mode is enabled, switch to the remote power-up state; if disabled, switch to state 49. Then, if GW_trigger equals 2 and battery SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Next, for slow charging handling: if slow charging is active, switch to the slow charging power-up state; if inactive, switch to state 129. Then, if GW_trigger equals 2 and SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Then, for fast charging handling: if fast charging is active, switch to the fast charging power-up state; if
- generated_excerpt:
  @startuml start :system starts up;  switch case (remote mode is enabled)   :switch to the remote power-up state; case (remote mode is disabled)   :switch to state 49; endswitch  if (GW_trigger equals 2 and battery SOC is 20) then (true)   :switch to state 28; elseif (GW_trigger equals 0 and DCDC state is 3) then (true)   :shut down and exit;   stop else (false) endif  switch case (slow charging is active)   :switch to the slow charging power-up state; case (slow charging is inactive)   :switch to state 129; endswitch  if (GW_trigger equals 2 and SOC is 20) then (true)   :switch to state 28; elseif (GW_trigger equals 0 and DCDC state is 3) then (true)   :shut down and exit;   stop else (false
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
  - compute the absolute error between the zt truth data and the output z for the equivalent input of (xt yt)
  - the absolute error between the zt truth data and the output z exceeds a tolerance of 0.01 for the equivalent input of (xt yt
- missing_relations:
  - for equivalent input of (xt yt) -> absolute error between zt truth data and output z <= 0.01?
  - absolute error between zt truth data and output z <= 0.01? -> allowed
  - allowed -> not allowed
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start repeat :Compute the absolute error between the zt truth data and the output z for the equivalent input of (xt, yt); repeat while (The absolute error between the zt truth data and the output z exceeds a tolerance of 0.01, for the equivalent input of (xt, yt)) is (Yes) ->No; @enduml
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1852
- relation_f1: 0.0385
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
  - the transformation and the data source are displayed in the info area below the info cube sales overview
  - in the context menu of the data source choose create info package...
  - on the next screen enter a description for the info package and choose save
  - the info package maintenance screen for the scheduler appears
  - go to the tab page schedule and choose start
  - to check the load process choose monitor in the toolbar of info package maintenance
  - on the next screen select the date and choose execute
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
  @startuml start :Go to the Data Warehousing Workbench; :in the Modeling area choose Info Provider; :The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview; :In the context menu of the Data source, choose Create Info Package...; :On the next screen, enter a description for the Info Package and choose Save; :The Info Package maintenance screen for the scheduler appears; :Go to the tab page Schedule and choose Start; :To check the load process, choose Monitor in the toolbar of Info Package maintenance; :On the next screen, select the date and choose Execute; :The monitor for the load process is displayed; :Select the load process for your Data s
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2295
- relation_f1: 0.0678
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - 1
  - go to promotion jobs home page
  - 2
  - right-click
  - open source and destination systems drop-down lists
  - select source and destination systems
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - in the promotion jobs home page select the job that you want to promote
  - right-click the home page screen and click promote
  - from the source and the destination systems drop-down lists select the source and destination systems
  - ensure that you have logged into both the source and destination systems before you proceed with the promotion process
  - in the external change management id field enter the appropriate value and click save
  - required
  - security option
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
  @startuml start :promote a jobLog into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, select the job that you want to promote; fork   :select the job that you want to promote; fork again   :right-click the home page screen, and click Promote; end fork :From the source and the destination systems drop-down lists, select the source and destination systems; :Ensure that you have logged into both the source and destination systems before you proceed with the promotion process; :In the External Change Management ID field, enter the appropriate value, and click Save; :Click Mappings; if (you want to create and validate mappings) then (yes)   :Click Edit Mappings; endif if (require
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
  - respond to parameter changes
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
  @startuml start :Respond to incoming correlator mode changes; :Respond to user optional processing sequence changes; :Respond to parameter changes; :Respond to other external inputs that affect the data processing pipeline; :Update internal parameter tables; :Synchronize data processing pipeline with new operational conditions; stop @enduml
### lmc-0011
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- missing_nodes:
  - system is supported?
  - sensor data is good?
- extra_nodes:
  - system is supported and sensor data is good
- missing_relations:
  - system is supported? -> sensor data is good?
  - sensor data is good? -> autopilot change states from pullup to transition
- input_excerpt:
  7.	The autopilot shall change states from PULLUP to TRANSITION when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml start if (system is supported and sensor data is good) then (true)   :change states from PULLUP to TRANSITION; else (false) endif @enduml
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
  @startuml start :give out the successful trade information; fork   :save the trade information; end fork @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
