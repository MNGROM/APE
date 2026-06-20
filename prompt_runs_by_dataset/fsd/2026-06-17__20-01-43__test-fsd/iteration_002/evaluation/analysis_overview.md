# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.5443
- node_recall: 0.5070
- node_f1: 0.5250
- relation_precision: 0.5177
- relation_recall: 0.4980
- relation_f1: 0.5077
- plantuml_compilation_pass_rate: 0.9000
- llm_element_evaluated: 10.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8069
- llm_node_recall: 0.7848
- llm_node_f1: 0.7846
- llm_relation_precision: 0.6318
- llm_relation_recall: 0.6165
- llm_relation_f1: 0.6049

## Failure Types
- missing_activity: 8
- extra_activity: 8
- missing_or_wrong_relation: 7
- extra_or_wrong_relation: 7
- wrong_parallel: 3
- syntax_error: 1

## Representative Failure Cases
### bp-0023
- dataset: bp
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.2785
- relation_f1: 0.3048
- llm_element_status: success
- llm_node_f1: 0.0000
- llm_relation_f1: 0.0000
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - go to promotion jobs home page
  - right-click
  - open source and destination systems drop-down lists
  - select source and destination systems
  - have logged into both source and destination systems
  - enter appropriate value
- extra_nodes:
  - right-click the home page screen
  - select the source and destination systems from the drop-down lists
  - click edit mappings if you want to create and validate mappings
  - security options
  - do not promote security (default option)
  - promote job along with inherited application rights
  - click view security to view the security dependencies of the infoobjects in the job
  - click test promote to ensure that there is no conflict between cuids
- missing_relations:
  - log in lifecycle manager tool -> selection method
  - selection method -> go to promotion jobs home page [case 1]
  - go to promotion jobs home page -> select the job want to promote
  - selection method -> right-click [case 2]
  - right-click -> click promote
  - select the job want to promote -> open source and destination systems drop-down lists [merge]
  - open source and destination systems drop-down lists -> select source and destination systems
  - select source and destination systems -> have logged into both source and destination systems
- input_excerpt:
  23.	promote a jobLog into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, select the job that you want to promote. You can also right-click the home page screen, and click Promote.3. From the source and the destination systems drop-down lists, select the source and destination systems.Note:Ensure that you have logged into both the source and destination systems before you proceed with the promotion process.4. In the External Change Management ID field, enter the appropriate value, and click Save.5. Click Mappings. Click Edit Mappings if you want to create and validate mappings.6. Click Security Settings, if required. The following options are displayed:• Do not Promote Secur
- generated_excerpt:
  @startuml start :Select the job that you want to promote; fork   :Right-click the home page screen;   :Click Promote; end fork :Select the source and destination systems from the drop-down lists; :Enter the appropriate value in the External Change Management ID field; :Click Save; :Click Mappings; :Click Edit Mappings if you want to create and validate mappings; :Click Security Settings if required; switch (Security Options) case (Do not Promote Security)   :Do not Promote Security (default option); case (Promote Security)   :Promote jobs along with the associated security rights;   case (Include application rights)     :Promote job along with inherited application rights;   endswitch endswi
### lmc-0011
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.4000
- missing_nodes:
  - system is supported?
  - sensor data is good?
  - autopilot change states from pullup to transition
- extra_nodes:
  - system is supported and sensor data is good?
  - change state from pullup to transition
- missing_relations:
  - system is supported? -> sensor data is good? [yes]
  - sensor data is good? -> autopilot change states from pullup to transition [yes]
- input_excerpt:
  7.	The autopilot shall change states from PULLUP to TRANSITION when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml start if (System is supported and sensor data is good?) then (yes)   :Change state from PULLUP to TRANSITION; endif stop @enduml
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2692
- relation_f1: 0.1429
- llm_element_status: success
- llm_node_f1: 0.7241
- llm_relation_f1: 0.6452
- missing_nodes:
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - open data source context menu
  - choose create info package...
  - enter description
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
  - info area displays information -> transformation [fork]
  - info area displays information -> data source [fork]
  - transformation -> open data source context menu [merge]
  - data source -> open data source context menu [merge]
  - choose create info package... -> enter description
- input_excerpt:
  7.	Loading Transaction Data1. Go to the Data Warehousing Workbench; in the Modeling area choose Info Provider. The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview.2. In the context menu of the Data source, choose Create Info Package...3. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.4. Go to the tab page Schedule and choose Start.5. To check the load process, choose Monitor in the toolbar of Info Package maintenance.6. On the next screen, select the date and choose Execute. The monitor for the load process is displayed.7. Select the load process f
- generated_excerpt:
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose Info Provider; :The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview; :In the context menu of the Data source, choose Create Info Package...; :On the next screen, enter a description for the Info Package and choose Save; :The Info Package maintenance screen for the scheduler appears; :Go to the tab page Schedule and choose Start; :To check the load process, choose Monitor in the toolbar of Info Package maintenance; :On the next screen, select the date and choose Execute; :The monitor for the load process is displayed; :Select the load process for your Data s
### lmc-0038
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3636
- relation_f1: 0.2000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.6667
- missing_nodes:
  - allowed
  - not allowed
- extra_nodes:
  - zt truth data
  - output z
  - absolute error > 0.01?
  - error exceeds tolerance
  - error within tolerance
- missing_relations:
  - absolute error between zt truth data and output z <= 0.01? -> allowed [yes]
  - absolute error between zt truth data and output z <= 0.01? -> not allowed [no]
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Input (xt, yt); fork :zt truth data; :Output z; end fork :Calculate absolute error between zt truth data and output z; if (Absolute error > 0.01?) then (yes) :Error exceeds tolerance; else (no) :Error within tolerance; endif stop @enduml
### pure-0030
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4615
- relation_f1: 0.1429
- llm_element_status: success
- llm_node_f1: 0.8750
- llm_relation_f1: 0.2353
- missing_nodes:
  - respond to
  - user optional processing sequence
  - parameter changes
  - other affective external inputs
- extra_nodes:
  - respond to user optional processing sequence changes
  - respond to user optional parameter changes
  - respond to other external inputs that affect the data processing pipeline
- missing_relations:
  - respond to -> incoming correlator mode changes [fork]
  - respond to -> user optional processing sequence [fork]
  - respond to -> parameter changes [fork]
  - respond to -> other affective external inputs [fork]
  - incoming correlator mode changes -> update internal parameter tables [merge]
  - user optional processing sequence -> update internal parameter tables [merge]
  - parameter changes -> update internal parameter tables [merge]
  - other affective external inputs -> update internal parameter tables [merge]
- input_excerpt:
  Processing Management – The BE shall respond to incoming correlator mode changes, user optional processing sequence and/or parameter changes, and other external inputs that affect the data processing pipeline. Update internal parameter tables and synchronize data processing pipeline with new operational conditions.
- generated_excerpt:
  @startuml start :Respond to incoming correlator mode changes; :Respond to user optional processing sequence changes; :Respond to user optional parameter changes; :Respond to other external inputs that affect the data processing pipeline; :Update internal parameter tables; :Synchronize data processing pipeline with new operational conditions; stop @enduml
### rac-0004
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.5854
- llm_element_status: success
- llm_node_f1: 0.9143
- llm_relation_f1: 0.6316
- missing_nodes:
  - slow charging state is 1 and charging/discharging power-up is ready
  - condition judgement
  - high-voltage shutdown charging/discharging value is 3 or 4
  - shutdown
  - high-voltage shutdown request is 3 and ignition switch is 2
  - ignition switch becomes 0
  - shut down
- extra_nodes:
  - system starts up
  - slow charging is active (state 1) and the charging/discharging system is powered up?
  - conditions while in state 105
  - high-voltage shutdown value is 3 or 4
  - shut down and end the process
  - high-voltage shutdown request (value 3) occurs while the ignition is on (position 2)
  - return to state 105
  - shut down and end
- missing_relations:
  - switch to state 95 -> vehicle charging/discharging mode is 2 and power-up is ready
  - condition judgement -> high-voltage shutdown charging/discharging value is 3 or 4 [case 1]
  - condition judgement -> high-voltage shutdown request is 3 and ignition switch is 2 [case 2]
  - switch to state 105 -> ignition switch becomes 0
  - condition judgement -> pre-charge failure occurs [case 3]
  - condition judgement -> ac discharge system fault occurs [case 4]
  - condition judgement -> slow charging is inactive [case 5]
- input_excerpt:
  After the system starts up: - If slow charging is active (state 1) and the charging/discharging system is powered up, switch to state 95. - If the vehicle charging/discharging mode is 2 and the system is powered up, switch to state 105. Then, while in state 105:   1) If the high-voltage shutdown value is 3 or 4, switch to state 115. If slow charging becomes inactive during this, shut down and end the process.   2) If a high-voltage shutdown request (value 3) occurs while the ignition is on (position 2), return to state 105. If the ignition turns off (position 0), switch to state 115. If slow charging becomes inactive, shut down and end.   3) If a pre-charge failure happens, switch to state 1
- generated_excerpt:
  @startuml start :system starts up; if (slow charging is active (state 1) and the charging/discharging system is powered up?) then (yes)   :switch to state 95; elseif (vehicle charging/discharging mode is 2 and the system is powered up?) then (yes)   :switch to state 105;   switch (conditions while in state 105)   case (high-voltage shutdown value is 3 or 4)     :switch to state 115;     if (slow charging becomes inactive?) then (yes)       :shut down and end the process;       stop     endif   case (high-voltage shutdown request (value 3) occurs while the ignition is on (position 2))     :return to state 105;     if (slow charging becomes inactive?) then (yes)       :shut down and end;      
### pure-0010
- dataset: pure
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - save trade instruction
- extra_nodes:
  - save the trade information
- input_excerpt:
  1. central trading system: give out the successful trade information 2. security account management: save the trade information
- generated_excerpt:
  @startuml start :give out the successful trade information; :save the trade information; stop @enduml
### rac-0020
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7636
- relation_f1: 0.5581
- llm_element_status: success
- llm_node_f1: 0.8657
- llm_relation_f1: 0.4706
- missing_nodes:
  - remote mode enabled
  - remote mode is disabled
  - shutdown
  - slow charging active
  - slow charging is inactive
  - fast charging active
  - fast charging is inactive
  - battery soc=20
- extra_nodes:
  - system starts up
  - shut down and exit
  - soc is 20?
  - shut down and end
- missing_relations:
  - switch to remote power-up state -> remote mode is disabled
  - switch to state 28 -> gw_trigger=0 and dcdc state=3
  - remote mode enabled -> slow charging active [no]
  - switch to slow charging power-up state -> slow charging is inactive
  - slow charging active -> fast charging active [no]
  - switch to fast charging power-up state -> fast charging is inactive
  - fast charging active -> gw_trigger=2 [no]
  - switch to state 10 -> battery soc=20
- input_excerpt:
  After the system starts up, the following steps occur:  First, for remote mode handling: if remote mode is enabled, switch to the remote power-up state; if disabled, switch to state 49. Then, if GW_trigger equals 2 and battery SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Next, for slow charging handling: if slow charging is active, switch to the slow charging power-up state; if inactive, switch to state 129. Then, if GW_trigger equals 2 and SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Then, for fast charging handling: if fast charging is active, switch to the fast charging power-up state; if
- generated_excerpt:
  @startuml start :System starts up; if (remote mode is enabled?) then (yes)   :switch to the remote power-up state; else (no)   :switch to state 49; endif if (GW_trigger equals 2 and battery SOC is 20?) then (yes)   :switch to state 28; else (no)   if (GW_trigger equals 0 and DCDC state is 3?) then (yes)     :shut down and exit;     stop   else (no)   endif endif if (slow charging is active?) then (yes)   :switch to the slow charging power-up state; else (no)   :switch to state 129; endif if (GW_trigger equals 2 and SOC is 20?) then (yes)   :switch to state 28; else (no)   if (GW_trigger equals 0 and DCDC state is 3?) then (yes)     :shut down and exit;     stop   else (no)   endif endif if (

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
