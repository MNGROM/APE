# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4213
- node_recall: 0.4237
- node_f1: 0.4201
- relation_precision: 0.3893
- relation_recall: 0.3941
- relation_f1: 0.3909
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
- missing_activity: 8
- extra_activity: 8
- missing_or_wrong_relation: 7
- extra_or_wrong_relation: 7

## Representative Failure Cases
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
### pure-0030
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1429
- relation_f1: 0.1667
- missing_nodes:
  - respond to
  - incoming correlator mode changes
  - user optional processing sequence
  - parameter changes
  - other affective external inputs
  - synchronize data processing pipeline
- extra_nodes:
  - receive incoming input affecting data processing pipeline
  - input type
  - correlator mode change
  - user optional processing sequence/parameter change
  - other external input
  - synchronize data processing pipeline with new operational conditions
- missing_relations:
  - respond to -> incoming correlator mode changes
  - incoming correlator mode changes -> user optional processing sequence
  - user optional processing sequence -> parameter changes
  - parameter changes -> other affective external inputs
  - update internal parameter tables -> synchronize data processing pipeline
- input_excerpt:
  Processing Management – The BE shall respond to incoming correlator mode changes, user optional processing sequence and/or parameter changes, and other external inputs that affect the data processing pipeline. Update internal parameter tables and synchronize data processing pipeline with new operational conditions.
- generated_excerpt:
  @startuml start :Receive incoming input affecting data processing pipeline; switch (Input Type) case (Correlator mode change) case (User optional processing sequence/parameter change) case (Other external input) endswitch :Update internal parameter tables; :Synchronize data processing pipeline with new operational conditions; stop @enduml
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
  - go to data warehousing workbench in modeling area choose info provider
  - view transformation and data source in info area below info cube sales overview
  - in context menu of data source choose create info package...
  - enter description for info package and choose save
  - view info package maintenance screen for the scheduler
  - go to tab page schedule and choose start
  - choose monitor in toolbar of info package maintenance
  - select date and choose execute
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
  @startuml start :Go to Data Warehousing Workbench; in Modeling area choose Info Provider; :View transformation and Data source in Info Area below Info Cube Sales Overview; :In context menu of Data source, choose Create Info Package...; :Enter description for Info Package and choose Save; :View Info Package maintenance screen for the scheduler; :Go to tab page Schedule and choose Start; :Choose Monitor in toolbar of Info Package maintenance; :Select date and choose Execute; :View monitor for the load process; :Select load process for Data source from tree at left of screen; :Exit Info Package maintenance screen; :From context menu of Data source, choose Create Data Transfer Process...; :View 
### lmc-0038
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- missing_nodes:
  - for equivalent input of (xt yt)
  - allowed
  - not allowed
- extra_nodes:
  - absolute error exceeds tolerance of 0.01?
  - error exceeds tolerance
  - error within tolerance
- missing_relations:
  - for equivalent input of (xt yt) -> absolute error between zt truth data and output z <= 0.01?
  - absolute error between zt truth data and output z <= 0.01? -> allowed
  - allowed -> not allowed
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Calculate absolute error between zt truth data and output z; if (Absolute error exceeds tolerance of 0.01?) then (Yes)   :Error exceeds tolerance; else (No)   :Error within tolerance; endif end @enduml
### rac-0004
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.1538
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
  - vehicle charging/discharging mode is 2 and the system is powered up?
  - event while in state 105?
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
  @startuml start :System starts up; if (Slow charging is active (state 1) and the charging/discharging system is powered up?) then (yes)   :Switch to state 95; elseif (Vehicle charging/discharging mode is 2 and the system is powered up?) then (yes)   :Switch to state 105;   switch (Event while in state 105?)   case (High-voltage shutdown value is 3 or 4)     :Switch to state 115;     if (Slow charging becomes inactive?) then (yes)       :Shut down and end the process;       stop     else (no)     endif   case (High-voltage shutdown request (value 3) occurs while the ignition is on (position 2))     :Return to state 105;     if (Ignition turns off (position 0)?) then (yes)       :Switch to sta
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3750
- relation_f1: 0.1739
- missing_nodes:
  - log in lifecycle manager tool
  - 1
  - go to promotion jobs home page
  - 2
  - right-click
  - open source and destination systems drop-down lists
  - have logged into both source and destination systems
  - go to external change management id field
- extra_nodes:
  - right-click the home page screen and click promote
  - enter the appropriate value in the external change management id field and click save
  - security settings required?
  - security option?
  - promote security
  - include application rights
  - want to view the security dependencies?
  - click view security
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
  @startuml start switch (Selection Method?) case (Select the job that you want to promote) case (Right-click the home page screen, and click Promote) endswitch  :Select the source and destination systems;  :Enter the appropriate value in the External Change Management ID field, and click Save;  :Click Mappings;  if (Want to create and validate mappings?) then (yes)   :Click Edit Mappings; endif  if (Security Settings required?) then (yes)   :Click Security Settings;   switch (Security Option?)   case (Do not Promote Security)   case (Promote Security)   case (Include application rights)   endswitch   if (Want to view the security dependencies?) then (yes)     :Click View Security;   endif end
### rac-0020
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4490
- relation_f1: 0.3750
- missing_nodes:
  - remote mode is disabled
  - remote mode is disabled
  - gw_trigger=2 and battery soc=20
  - gw_trigger=0 and dcdc state=3
  - gw_trigger=0 and dcdc state=3
  - gw_trigger=0 and dcdc state=3
  - shutdown
  - shutdown
- extra_nodes:
  - system starts up
  - remote mode handling
  - remote mode trigger condition
  - gw_trigger equals 2 and battery soc is 20
  - gw_trigger equals 0 and dcdc state is 3
  - gw_trigger equals 0 and dcdc state is 3
  - gw_trigger equals 0 and dcdc state is 3
  - shut down and exit
- missing_relations:
  - switch to remote power-up state -> remote mode is disabled
  - remote mode is disabled -> switch to state 49
  - switch to state 49 -> gw_trigger=2 and battery soc=20
  - gw_trigger=0 and dcdc state=3 -> shutdown
  - gw_trigger=0 and dcdc state=3 -> shutdown
  - gw_trigger=0 and dcdc state=3 -> shutdown
  - shutdown -> slow charging active
  - switch to slow charging power-up state -> slow charging is inactive
- input_excerpt:
  After the system starts up, the following steps occur:  First, for remote mode handling: if remote mode is enabled, switch to the remote power-up state; if disabled, switch to state 49. Then, if GW_trigger equals 2 and battery SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Next, for slow charging handling: if slow charging is active, switch to the slow charging power-up state; if inactive, switch to state 129. Then, if GW_trigger equals 2 and SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Then, for fast charging handling: if fast charging is active, switch to the fast charging power-up state; if
- generated_excerpt:
  @startuml start :System starts up;  :Remote mode handling; if (remote mode is enabled?) then (yes)   :switch to the remote power-up state; else (no)   :switch to state 49; endif  switch (Remote mode trigger condition) case (GW_trigger equals 2 and battery SOC is 20)   :switch to state 28; case (GW_trigger equals 0 and DCDC state is 3)   :shut down and exit;   stop endswitch  :Slow charging handling; if (slow charging is active?) then (yes)   :switch to the slow charging power-up state; else (no)   :switch to state 129; endif  switch (Slow charging trigger condition) case (GW_trigger equals 2 and SOC is 20)   :switch to state 28; case (GW_trigger equals 0 and DCDC state is 3)   :shut down and
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
  @startuml |central trading system| start :Give out the successful trade information; |security account management| :Save the trade information; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
