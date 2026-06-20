# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4780
- node_recall: 0.4292
- node_f1: 0.4523
- relation_precision: 0.4303
- relation_recall: 0.3504
- relation_f1: 0.3862
- plantuml_compilation_pass_rate: 0.9000
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
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10
- wrong_parallel: 3
- wrong_loop: 3
- syntax_error: 1

## Representative Failure Cases
### bp-0026
- dataset: bp
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4516
- relation_f1: 0.4516
- missing_nodes:
  - open the promote window
  - click mappings
  - edited in source system?
  - edited is displayed
  - created using universes?
  - cannot be mapped
  - use connections mappings
  - proceed with mapping
- extra_nodes:
  - in the promote window click mappings
  - the crystal report mappings tab appears
  - click save
  - click promote
- missing_relations:
  - open the promote window -> click mappings
  - click apply -> edited in source system?
  - edited in source system? -> edited is displayed [yes]
  - edited is displayed -> created using universes?
  - edited in source system? -> created using universes? [if no]
  - created using universes? -> cannot be mapped [yes]
  - cannot be mapped -> use connections mappings
  - created using universes? -> proceed with mapping [if no]
- input_excerpt:
  26.	modify the properties of a Crystal report1. In the "Promote" window, click Mappings.2. Click Crystal Report Mappings.The list of Crystal reports in the source system is displayed.3. Select the required Crystal report, and click Edit Crystal Report Properties. The "Edit Crystal Report Properties" tab appears, as shown in the following figure: This tab displays the list of properties and their values.4. Modify the appropriate fields, and click Apply. The Crystal Report Mappings tab appears.Note:• If you edit a Crystal report in the source system, the following message is displayed beside the Crystal report: edited• A Crystal Report created using Universes cannot be mapped in the Crystal Re
- generated_excerpt:
  @startuml start :In the "Promote" window, click Mappings; :Click Crystal Report Mappings; :The list of Crystal reports in the source system is displayed; :Select the required Crystal report; :Click Edit Crystal Report Properties; :The "Edit Crystal Report Properties" tab appears; note right   This tab displays the list   of properties and their values. end note :Modify the appropriate fields; :Click Apply; :The Crystal Report Mappings tab appears; note right   **Notes:**   * If you edit a Crystal report in the     source system, "edited" is displayed     beside the Crystal report.   * A Crystal Report created using Universes     cannot be mapped here, but can be mapped     in the Connections
### lmc-0012
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - pilot is not in control (not standby)?
  - autopilot change states from standby to transition
- extra_nodes:
  - standby
  - transition
- missing_relations:
  - pilot is not in control (not standby)? -> autopilot change states from standby to transition [yes]
- input_excerpt:
  8.	The autopilot shall change states from STANDBY to TRANSITION when the pilot is not in control (not standby).
- generated_excerpt:
  @startuml skinparam style strictuml  state "STANDBY" as STANDBY state "TRANSITION" as TRANSITION  STANDBY --> TRANSITION : [Pilot is not in control] @enduml
### lmc-0039
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.1667
- missing_nodes:
  - each element with respect to 3x3 identity matrix elements < 1e-6 tolerance
  - b(inv(wp )b matrix inversion be accurate to 6 digits precision
- extra_nodes:
  - calculate determinant of b(inv(wp ))b
  - invert b(inv(wp ))b matrix
  - multiply inverted matrix by b(inv(wp ))b to get check output matrix
  - compare check output matrix to 3x3 identity matrix
  - each element within 1e-6 tolerance?
  - inversion accurate to 6 digits precision
  - inversion fails precision check
  - set ridge_on = false
- missing_relations:
  - determinant of b(inv(wp )b <= 1e-12 -> each element with respect to 3x3 identity matrix elements < 1e-6 tolerance
  - each element with respect to 3x3 identity matrix elements < 1e-6 tolerance -> b(inv(wp )b matrix inversion be accurate to 6 digits precision
- input_excerpt:
  1.	When the determinant of B(inv(Wp’)B’ is <= 1e-12 as indicated by ridge_on set to True, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 6 digits precision in that each element in the check output matrix is within a 1e-6 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  @startuml start :Calculate determinant of B(inv(Wp'))B'; if (det(B(inv(Wp'))B') <= 1e-12?) then (Yes)   :Set ridge_on = True;   :Invert B(inv(Wp'))B' matrix;   :Multiply inverted matrix by B(inv(Wp'))B'   to get check output matrix;   :Compare check output matrix   to 3x3 identity matrix;   if (Each element within 1e-6 tolerance?) then (Yes)     :Inversion accurate to 6 digits precision;   else (No)     :Inversion fails precision check;     stop   endif else (No)   :Set ridge_on = False; endif stop @enduml
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
  - enter the name description and keywords for the job
  - in the save job in field browse and select the folder
  - select the source system and the destination system from the drop-down lists
  - system name displayed in drop-down list?
  - click the login to a new cms option
  - enter the system name user name and password
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
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name, description, and keywords for the job; :In the Save Job in field, browse and select the folder; :Select the source system and the destination system from the drop-down lists; if (System name displayed in drop-down list?) then (No)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the system name, user name, and password; else (Yes) endif :Click Create; stop @enduml
### pure-0024
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3529
- relation_f1: 0.3750
- missing_nodes:
  - apply emergency brake
  - not stationary?
  - acknowledge train trip condition
  - continue movement
  - backwards?
  - drive for national value distance
- extra_nodes:
  - apply emergency brake until traction unit is stationary
  - traction unit becomes stationary
  - driver acknowledges train trip condition
  - driver is able to continue movement
  - train is able to be driven backwards for a certain distance (defined by national value)
- missing_relations:
  - trigger emergency brake -> apply emergency brake
  - apply emergency brake -> not stationary?
  - not stationary? -> apply emergency brake [loop]
  - not stationary? -> acknowledge train trip condition [not stationary?]
  - continue movement -> backwards?
  - backwards? -> drive for national value distance [yes]
- input_excerpt:
  When a traction unit passes a stop-signal, the emergency brake shall be triggered. The emergency brake shall be applied until the traction unit is stationary. When the traction unit is stationary, the driver shall be required to acknowledge the train trip condition. This acknowledgement will release the emergency brake. After the acknowledgement, the driver shall be able to continue the movement. After the acknowledgement, the train shall be able to be driven backwards for a certain distance defined by national value.
- generated_excerpt:
  @startuml start :Traction unit passes a stop-signal; :Trigger emergency brake; :Apply emergency brake until traction unit is stationary; :Traction unit becomes stationary; :Driver acknowledges train trip condition; :Release emergency brake; :Driver is able to continue movement; :Train is able to be driven backwards for a certain distance (defined by national value); stop @enduml
### rac-0019
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5283
- relation_f1: 0.6562
- missing_nodes:
  - switch to state 30
  - switch to state 49
  - switch to state 29
  - switch to state 110
  - switch to state 28
  - remote mode is disabled
  - slow charging is inactive
  - switch to state 129
- extra_nodes:
  - system startup
  - state 30
  - state 49
  - state 29
  - state 110
  - slow charging active and charging system command = 4?
  - state 28
  - state 129
- missing_relations:
  - switch to state 29 -> ignition switch=0 and vcc2=12
  - switch to state 110 -> charging system command=4
  - switch to state 29 -> ignition switch=0 and slow charging is inactive
  - ignition switch=2 -> remote mode enabled [else if]
  - switch to state 28 -> remote mode is disabled
  - switch to state 49 -> slow charging is active
  - ignition switch=0 and vcc2=12 -> slow charging is active [if no]
  - ignition switch=2 -> slow charging is active [if no]
- input_excerpt:
  After the system starts up, if the ignition switch is set to 2, transition to state 30. Then, under that condition: - If the ignition switch becomes 0, move to state 49 and exit. - If the fast charge Vcc2 is 6, observe the charging gun indicator. Should the charging system command be 4, switch to state 29. - If the ignition switch is 0 and Vcc2 is 12, proceed to state 49 and exit. - If slow charging is active and the charging system command is 1, transition to state 110. If the command is 4 instead, go to state 29. Also, if the ignition switch is 0 and slow charging is not active, shift to state 49 and exit.  If remote mode is enabled, switch to state 28. If it's disabled, transition to stat
- generated_excerpt:
  @startuml start :System Startup; if (Ignition switch = 2?) then (Yes)   :State 30;   if (Ignition switch = 0?) then (Yes)     :State 49;     stop   elseif (Fast charge Vcc2 = 6?) then (Yes)     :Observe charging gun indicator;     if (Charging system command = 4?) then (Yes)       :State 29;       stop     else (No)       stop     endif   elseif (Ignition switch = 0 and Vcc2 = 12?) then (Yes)     :State 49;     stop   elseif (Slow charging active and Charging system command = 1?) then (Yes)     :State 110;     stop   elseif (Slow charging active and Charging system command = 4?) then (Yes)     :State 29;     stop   elseif (Ignition switch = 0 and Slow charging not active?) then (Yes)     :St
### fsd-0050
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5517
- relation_f1: 0.4250
- missing_nodes:
  - thermal management controller implemented as deterministic state machine on rtos
  - govern pwm fans
  - govern liquid-cooling loops
  - receive user-initiated air conditioner start command
  - execute air conditioner startup sequence
  - user commands for wind speed adjustment serviced via interrupt-driven priority queue
  - enter control loop
  - bounded retries
- extra_nodes:
  - receive user-initiated ac start command
  - discard command / remain in current state
  - abort startup
  - execute ac startup sequence
  - monitor condenser temperature
  - interrupt-driven priority queue
  - receive wind speed adjustment command
  - execute telemetry monitor
- missing_relations:
  - thermal management controller implemented as deterministic state machine on rtos -> govern pwm fans [fork]
  - thermal management controller implemented as deterministic state machine on rtos -> govern liquid-cooling loops [fork]
  - govern pwm fans -> receive user-initiated air conditioner start command
  - govern liquid-cooling loops -> receive user-initiated air conditioner start command
  - continuously monitor compressor status and condenser temperature -> ensure operational parameters within safe bounds
  - execute air conditioner startup sequence -> user commands for wind speed adjustment serviced via interrupt-driven priority queue [fork]
  - enter control loop -> regulate pwm duty cycle
  - regulate pwm duty cycle -> actual fan speed matches requested value
- input_excerpt:
  The thermal management controller, implemented as a deterministic state machine on the RTOS, governs the PWM fans and liquid-cooling loops. Upon receiving a user-initiated air conditioner start command, the system first verifies the unit is in a powered-off state and then checks if the indoor temperature exceeds the setpoint. If both conditions are met, it executes the air conditioner startup sequence, during which a high-priority task, synchronized via mutexes with a BMS/PMIC interface, continuously monitors the compressor status and condenser temperature to ensure operational parameters remain within safe bounds. A medium-priority periodic task, scheduled by the RTOS, polls indoor temperat
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityDiamondBackgroundColor #F8F8F8  start  :Receive user-initiated AC start command;  if (Is unit in powered-off state?) then (No)   :Discard command / Remain in current state;   stop else (Yes) endif  if (Indoor temperature > setpoint?) then (No)   :Abort startup;   stop else (Yes) endif  :Execute AC startup sequence;  fork   :High-priority task (Mutex sync with BMS/PMIC);   repeat     :Monitor compressor status;     :Monitor condenser temperature;   repeat while (Operational parameters within safe bounds?) is (Yes)   ->No;   :Initiate controlled cool-down safety path;    fork again   :Medium-priority periodic task (RTOS sche
### fsd-0061
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5667
- relation_f1: 0.4932
- missing_nodes:
  - thermal management controller executes as state machine on rtos
  - govern pwm fans
  - govern liquid-cooling loops
  - primary diagnostic
  - critical system failure?
  - spawn high-priority task
  - temperature > safety threshold?
  - correlate events
- extra_nodes:
  - primary diagnostic critical system failure?
  - spawn high-priority thread 1
  - safety threshold exceeded?
  - continue monitoring
  - spawn high-priority thread 2
  - correlate events to locate fault source
  - release mutex
  - spawn parallel thread 1
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern pwm fans [fork]
  - thermal management controller executes as state machine on rtos -> govern liquid-cooling loops [fork]
  - govern pwm fans -> detect external signal abnormality?
  - govern liquid-cooling loops -> detect external signal abnormality?
  - detect external signal abnormality? -> primary diagnostic [yes]
  - primary diagnostic -> critical system failure?
  - critical system failure? -> spawn high-priority task [yes]
  - temperature > safety threshold? -> terminate operation [yes]
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing PWM fans and liquid-cooling loops. Upon detecting an external signal abnormality, a primary diagnostic determines if it constitutes a critical system failure. If critical, a high-priority task is spawned: its first thread continuously monitors temperature sensor data via a protected ring buffer, terminating operation and triggering an alarm via the system watchdog if a safety threshold is exceeded, while its second thread, using a mutex to access the structured audit log, correlates events to locate the fault source. For non-critical faults, a separate parallel process is initiated, where one thread validate
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Detect external signal abnormality;  if (Primary diagnostic: Critical system failure?) then (Yes)   fork     :Spawn High-Priority Thread 1;     repeat       :Read temperature sensor data\nvia protected ring buffer;       if (Safety threshold exceeded?) then (Yes)         :Terminate operation;         :Trigger alarm via system watchdog;         stop       endif     repeat while (Continue monitoring)   fork again     :Spawn High-Priority Thread 2;     :Acquire mutex for structured audit log;     :Correlate events to locate fault source;     :Release mutex;   end fork  else (No - Non-critical fault)   fork     :Spawn Parallel Thread 1;     :Validate 

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
