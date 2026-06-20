# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.6568
- node_recall: 0.6111
- node_f1: 0.6331
- relation_precision: 0.4653
- relation_recall: 0.4702
- relation_f1: 0.4677
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
- extra_or_wrong_relation: 10
- missing_activity: 9
- extra_activity: 9
- missing_or_wrong_relation: 9
- wrong_parallel: 3
- wrong_loop: 3

## Representative Failure Cases
### bp-0019
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3125
- relation_f1: 0.1622
- missing_nodes:
  - click new job
  - enter information
  - enter name
  - enter description
  - enter keywords
  - go to save job field
  - browse and select folder
  - open drop-downlists
- extra_nodes:
  - enter the name description and keywords for the job in the appropriate fields
  - in the save job in field browse and select the folder in which you want to save the job
  - select the source system and the destination system from the drop-down lists
  - is the name of the system displayed in the drop-down list?
  - click the login to a new cms option
  - enter the name of the system along with the user name and password
- missing_relations:
  - log in lifecycle manager tool -> go to promotion jobs home page
  - click new job -> new job window appears
  - new job window appears -> enter information
  - enter information -> enter name [fork]
  - enter information -> enter description [fork]
  - enter information -> enter keywords [fork]
  - enter name -> go to save job field
  - enter description -> go to save job field
- input_excerpt:
  19.	create a new job by using the LifeCycle Manager tool1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriatefields.4. In the Save Job in field, browse and select the folder in which you wantto save the job.5. Select the source system and the destination system from the drop-downlists.If the name of the system is not displayed in the drop-down list, click theLogin to a new CMS option. A new window is launched. Enter the nameof the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name, description, and keywords for the job in the appropriate fields; :In the Save Job in field, browse and select the folder in which you want to save the job; :Select the source system and the destination system from the drop-down lists; if (Is the name of the system displayed in the drop-down list?) then (No)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the name of the system along with the user name and password; else (Yes) endif :Click Create; @enduml
### bp-0026
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.2727
- missing_nodes:
  - open the promote window
  - click mappings
  - edited in source system?
  - edited is displayed
  - created using universes?
  - cannot be mapped
  - proceed with mapping
  - mapping scope
- extra_nodes:
  - in the promote window click mappings
  - this tab displays the list of properties and their values
  - the crystal report mappings tab appears
  - if you edit a crystal report in the source system?
  - the following message is displayed beside the crystal report edited
  - mapping type based on crystal report creation?
  - cannot be mapped in the crystal report mappings
  - mapping scope based on grouping?
- missing_relations:
  - open the promote window -> click mappings
  - edit crystal report properties tab appears -> modify appropriate fields
  - click apply -> edited in source system?
  - edited in source system? -> edited is displayed [yes]
  - edited is displayed -> created using universes?
  - edited in source system? -> created using universes? [if no]
  - created using universes? -> cannot be mapped [yes]
  - cannot be mapped -> use connections mappings
- input_excerpt:
  26.	modify the properties of a Crystal report1. In the "Promote" window, click Mappings.2. Click Crystal Report Mappings.The list of Crystal reports in the source system is displayed.3. Select the required Crystal report, and click Edit Crystal Report Properties. The "Edit Crystal Report Properties" tab appears, as shown in the following figure: This tab displays the list of properties and their values.4. Modify the appropriate fields, and click Apply. The Crystal Report Mappings tab appears.Note:• If you edit a Crystal report in the source system, the following message is displayed beside the Crystal report: edited• A Crystal Report created using Universes cannot be mapped in the Crystal Re
- generated_excerpt:
  @startuml start :In the "Promote" window, click Mappings; :Click Crystal Report Mappings; :The list of Crystal reports in the source system is displayed; :Select the required Crystal report; :Click Edit Crystal Report Properties; :The "Edit Crystal Report Properties" tab appears; :This tab displays the list of properties and their values; :Modify the appropriate fields; :Click Apply; :The Crystal Report Mappings tab appears; if (If you edit a Crystal report in the source system?) then (Yes)   :The following message is displayed beside the Crystal report: edited; else (No) endif switch (Mapping type based on Crystal Report creation?) case (Created using Universes)   :Cannot be mapped in the C
### pure-0024
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5556
- relation_f1: 0.4444
- missing_nodes:
  - not stationary?
  - continue movement
  - backwards?
  - drive for national value distance
- extra_nodes:
  - traction unit is stationary?
  - driver acknowledges the train trip condition
  - driver is able to continue the movement
  - train is able to be driven backwards for a certain distance defined by national value
- missing_relations:
  - apply emergency brake -> not stationary?
  - not stationary? -> apply emergency brake [loop]
  - not stationary? -> acknowledge train trip condition [not stationary?]
  - continue movement -> backwards?
  - backwards? -> drive for national value distance [yes]
- input_excerpt:
  When a traction unit passes a stop-signal, the emergency brake shall be triggered. The emergency brake shall be applied until the traction unit is stationary. When the traction unit is stationary, the driver shall be required to acknowledge the train trip condition. This acknowledgement will release the emergency brake. After the acknowledgement, the driver shall be able to continue the movement. After the acknowledgement, the train shall be able to be driven backwards for a certain distance defined by national value.
- generated_excerpt:
  @startuml start :Traction unit passes a stop-signal; :Trigger emergency brake; repeat :Apply emergency brake; repeat while (Traction unit is stationary?) is (No) -> Yes; :Require driver to acknowledge the train trip condition; :Driver acknowledges the train trip condition; :Release emergency brake; :Driver is able to continue the movement; :Train is able to be driven backwards for a certain distance defined by national value; stop @enduml
### fsd-0061
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5862
- relation_f1: 0.4595
- missing_nodes:
  - govern pwm fans
  - govern liquid-cooling loops
  - primary diagnostic
  - critical system failure?
  - temperature > safety threshold?
  - correlate events
  - locate fault source
  - initiate separate parallel process
- extra_nodes:
  - govern pwm fans and liquid-cooling loops
  - primary diagnostic critical system failure?
  - safety threshold exceeded?
  - correlate events to locate fault source
  - first thread validate communication module s status with crc check over can bus
  - second thread interface with pmic or bms to detect power rail instability
  - execute corresponding repair operations based on detection results
  - bounded retries exhausted?
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern pwm fans [fork]
  - thermal management controller executes as state machine on rtos -> govern liquid-cooling loops [fork]
  - govern pwm fans -> detect external signal abnormality?
  - govern liquid-cooling loops -> detect external signal abnormality?
  - detect external signal abnormality? -> primary diagnostic [yes]
  - primary diagnostic -> critical system failure?
  - temperature > safety threshold? -> terminate operation [yes]
  - use mutex to access structured audit log -> correlate events
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing PWM fans and liquid-cooling loops. Upon detecting an external signal abnormality, a primary diagnostic determines if it constitutes a critical system failure. If critical, a high-priority task is spawned: its first thread continuously monitors temperature sensor data via a protected ring buffer, terminating operation and triggering an alarm via the system watchdog if a safety threshold is exceeded, while its second thread, using a mutex to access the structured audit log, correlates events to locate the fault source. For non-critical faults, a separate parallel process is initiated, where one thread validate
- generated_excerpt:
  @startuml start :Execute thermal management state machine on RTOS; :Govern PWM fans and liquid-cooling loops; if (External signal abnormality detected?) then (yes)   if (Primary diagnostic: critical system failure?) then (yes)     :Spawn high-priority task;     fork       :First thread: continuously monitor temperature sensor data via protected ring buffer;       if (Safety threshold exceeded?) then (yes)         :Terminate operation;         :Trigger alarm via system watchdog;         stop       else (no)       endif     fork again       :Second thread: use mutex to access structured audit log;       :Correlate events to locate fault source;     end fork   else (no - non-critical fault)    
### fsd-0050
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5926
- relation_f1: 0.5000
- missing_nodes:
  - thermal management controller implemented as deterministic state machine on rtos
  - govern pwm fans
  - govern liquid-cooling loops
  - indoor temperature > setpoint?
  - high-priority task synchronized via mutexes with bms/pmic interface
  - medium-priority periodic task scheduled by rtos
  - enter control loop
  - bounded retries
- extra_nodes:
  - verify unit is in powered-off state
  - check if indoor temperature exceeds setpoint
  - indoor temperature exceeds setpoint?
  - high-priority task monitor compressor status and condenser temperature
  - monitor condenser temperature
  - medium-priority periodic task poll indoor temperature sensors
  - execute telemetry monitor with bounded retries and exponential backoff for fault handling
  - fault handled and retries exhausted?
- missing_relations:
  - thermal management controller implemented as deterministic state machine on rtos -> govern pwm fans [fork]
  - thermal management controller implemented as deterministic state machine on rtos -> govern liquid-cooling loops [fork]
  - govern pwm fans -> receive user-initiated air conditioner start command
  - govern liquid-cooling loops -> receive user-initiated air conditioner start command
  - unit in powered-off state? -> indoor temperature > setpoint? [yes]
  - execute air conditioner startup sequence -> high-priority task synchronized via mutexes with bms/pmic interface [fork]
  - high-priority task synchronized via mutexes with bms/pmic interface -> continuously monitor compressor status and condenser temperature
  - continuously monitor compressor status and condenser temperature -> ensure operational parameters within safe bounds
- input_excerpt:
  The thermal management controller, implemented as a deterministic state machine on the RTOS, governs the PWM fans and liquid-cooling loops. Upon receiving a user-initiated air conditioner start command, the system first verifies the unit is in a powered-off state and then checks if the indoor temperature exceeds the setpoint. If both conditions are met, it executes the air conditioner startup sequence, during which a high-priority task, synchronized via mutexes with a BMS/PMIC interface, continuously monitors the compressor status and condenser temperature to ensure operational parameters remain within safe bounds. A medium-priority periodic task, scheduled by the RTOS, polls indoor temperat
- generated_excerpt:
  @startuml start :Receive user-initiated air conditioner start command; :Verify unit is in powered-off state; if (Unit is in powered-off state?) then (yes)   :Check if indoor temperature exceeds setpoint;   if (Indoor temperature exceeds setpoint?) then (yes)     :Execute air conditioner startup sequence;     fork       :High-priority task: Monitor compressor status and condenser temperature;       repeat         :Monitor compressor status;         :Monitor condenser temperature;       repeat while (Operational parameters remain within safe bounds?) is (yes)       ->no;     fork again       :Medium-priority periodic task: Poll indoor temperature sensors;       repeat         :Poll indoor temp
### pure-0055
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6000
- relation_f1: 0.5000
- missing_nodes:
  - show items to be purchased
  - system updates inventory
  - reflect sale
- extra_nodes:
  - the system updates the inventory to reflect the sale
- missing_relations:
  - buyer arrives at cashier/checkout desk -> show items to be purchased
  - show items to be purchased -> sales associate scans tags
  - system updates inventory -> reflect sale
- input_excerpt:
  1. Buyer arrives at the cashier or checkout desk with the items to be purchased 2. Sales associate scans the item tags 3. Sales associate processes the sale of the items in QuickBooks POS 4. The system updates the inventory to reflect the sale
- generated_excerpt:
  @startuml start :Buyer arrives at the cashier or checkout desk with the items to be purchased; :Sales associate scans the item tags; :Sales associate processes the sale of the items in QuickBooks POS; :The system updates the inventory to reflect the sale; @enduml
### rac-0019
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7213
- relation_f1: 0.5952
- missing_nodes:
  - remote mode is disabled
  - slow charging is inactive
  - fast charging is inactive
  - switch to state 189
  - soc=80 and dcdc state=3
- extra_nodes:
  - system starts up
  - move to state 49
  - exit
  - proceed to state 49
  - slow charging is active and charging system command is 4?
  - go to state 29
  - transition to state 49
  - move to state 110
- missing_relations:
  - switch to state 29 -> ignition switch=0 and vcc2=12
  - switch to state 110 -> charging system command=4
  - switch to state 29 -> ignition switch=0 and slow charging is inactive
  - ignition switch=0 and vcc2=12 -> slow charging is active [if no]
  - ignition switch=2 -> slow charging is active [if no]
  - switch to state 110 -> slow charging is inactive
  - switch to state 170 -> fast charging is inactive
  - switch to state 10 -> battery soc=20 and dcdc state=1
- input_excerpt:
  After the system starts up, if the ignition switch is set to 2, transition to state 30. Then, under that condition: - If the ignition switch becomes 0, move to state 49 and exit. - If the fast charge Vcc2 is 6, observe the charging gun indicator. Should the charging system command be 4, switch to state 29. - If the ignition switch is 0 and Vcc2 is 12, proceed to state 49 and exit. - If slow charging is active and the charging system command is 1, transition to state 110. If the command is 4 instead, go to state 29. Also, if the ignition switch is 0 and slow charging is not active, shift to state 49 and exit.  If remote mode is enabled, switch to state 28. If it's disabled, transition to stat
- generated_excerpt:
  @startuml start :System starts up; if (Ignition switch is set to 2?) then (yes)   :Transition to state 30;   if (Ignition switch becomes 0?) then (yes)     :Move to state 49;     :Exit;   elseif (Fast charge Vcc2 is 6?) then (yes)     :Observe the charging gun indicator;     if (Charging system command is 4?) then (yes)       :Switch to state 29;     else (no)       endif   elseif (Ignition switch is 0 and Vcc2 is 12?) then (yes)     :Proceed to state 49;     :Exit;   elseif (Slow charging is active and charging system command is 1?) then (yes)     :Transition to state 110;   elseif (Slow charging is active and charging system command is 4?) then (yes)     :Go to state 29;   elseif (Ignition
### rac-0020
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7843
- relation_f1: 0.4878
- missing_nodes:
  - remote mode is disabled
  - shutdown
  - slow charging is inactive
  - fast charging is inactive
  - battery soc=20
  - condition judgement
- extra_nodes:
  - system starts up
  - shut down and exit
  - soc is 20?
  - ignition switch is 2?
  - shut down and end
- missing_relations:
  - switch to remote power-up state -> remote mode is disabled
  - switch to state 28 -> gw_trigger=0 and dcdc state=3
  - remote mode enabled -> slow charging active [else if]
  - switch to slow charging power-up state -> slow charging is inactive
  - remote mode enabled -> fast charging active [else if]
  - switch to fast charging power-up state -> fast charging is inactive
  - remote mode enabled -> gw_trigger=2 [else if]
  - switch to state 10 -> battery soc=20
- input_excerpt:
  After the system starts up, the following steps occur:  First, for remote mode handling: if remote mode is enabled, switch to the remote power-up state; if disabled, switch to state 49. Then, if GW_trigger equals 2 and battery SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Next, for slow charging handling: if slow charging is active, switch to the slow charging power-up state; if inactive, switch to state 129. Then, if GW_trigger equals 2 and SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Then, for fast charging handling: if fast charging is active, switch to the fast charging power-up state; if
- generated_excerpt:
  @startuml start :System starts up;  if (Remote mode enabled?) then (yes)   :Switch to remote power-up state; else (no)   :Switch to state 49; endif  if (GW_trigger equals 2 and battery SOC is 20?) then (yes)   :Switch to state 28; elseif (GW_trigger equals 0 and DCDC state is 3?) then (yes)   :Shut down and exit;   stop else (no) endif  if (Slow charging active?) then (yes)   :Switch to slow charging power-up state; else (no)   :Switch to state 129; endif  if (GW_trigger equals 2 and SOC is 20?) then (yes)   :Switch to state 28; elseif (GW_trigger equals 0 and DCDC state is 3?) then (yes)   :Shut down and exit;   stop else (no) endif  if (Fast charging active?) then (yes)   :Switch to fast c

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
