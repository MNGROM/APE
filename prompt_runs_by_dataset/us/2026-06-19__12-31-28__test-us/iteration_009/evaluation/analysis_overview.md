# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.5070
- node_recall: 0.4550
- node_f1: 0.4796
- relation_precision: 0.4234
- relation_recall: 0.3378
- relation_f1: 0.3758
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.9000
- llm_node_recall: 0.7829
- llm_node_f1: 0.8256
- llm_relation_precision: 0.7034
- llm_relation_recall: 0.6168
- llm_relation_f1: 0.6374

## Failure Types
- missing_activity: 19
- extra_activity: 19
- missing_or_wrong_relation: 18
- extra_or_wrong_relation: 16
- wrong_parallel: 8
- wrong_loop: 3

## Representative Failure Cases
### lmc-0040
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6250
- llm_relation_f1: 0.3750
- missing_nodes:
  - ridge_on set to false
  - determinant of b(inv(wp )b > 1e-12
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - b(inv(wp )b matrix inversion be accurate to 12 digits precision
- extra_nodes:
  - check determinant of b(inv(wp ))b
  - determinant > 1e-12?
  - invert b(inv(wp ))b matrix
  - check output matrix elements against 3x3 identity matrix
  - elements within 1e-12 tolerance?
  - inversion accurate to 12 digits precision
  - inversion not accurate
  - skip accurate inversion check
- missing_relations:
  - ridge_on set to false -> determinant of b(inv(wp )b > 1e-12
  - determinant of b(inv(wp )b > 1e-12 -> each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance -> b(inv(wp )b matrix inversion be accurate to 12 digits precision
- input_excerpt:
  2.	When the determinant of B(inv(Wp’)B’ is > 1e-12 as indicated by ridge_on set to False, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 12 digits precision in that each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  @startuml start :Check determinant of B(inv(Wp'))B'; if (Determinant > 1e-12?) then (Yes, ridge_on = False)   :Invert B(inv(Wp'))B' matrix;   :Check output matrix elements against 3x3 identity matrix;   if (Elements within 1e-12 tolerance?) then (Yes)     :Inversion accurate to 12 digits precision;   else (No)     :Inversion not accurate;   endif else (No, ridge_on = True)   :Skip accurate inversion check; endif stop @enduml
### lmc-0009
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.8000
- missing_nodes:
  - pilot is in control (standby)?
  - autopilot change states from nominal to standby
- extra_nodes:
  - autopilot in nominal state
  - pilot is in control?
  - change state to standby
- missing_relations:
  - pilot is in control (standby)? -> autopilot change states from nominal to standby [yes]
- input_excerpt:
  5.	The autopilot shall change states from NOMINAL to STANDBY when the pilot is in control (standby).
- generated_excerpt:
  @startuml start :Autopilot in NOMINAL state; if (Pilot is in control?) then (yes)   :Change state to STANDBY; else (no) endif stop @enduml
### bp-0017
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1250
- relation_f1: 0.1176
- llm_element_status: success
- llm_node_f1: 0.8333
- llm_relation_f1: 0.3810
- missing_nodes:
  - go to administration options window
  - open version management systems drop-down list
  - select clearcase
  - enter details
  - clearcase map drive
  - enter mvfs s folder name
  - vob tag name
  - enter vob name
- extra_nodes:
  - open administration options window
  - select clearcase from version management systems drop-down list
  - enter clearcase details - clearcase map drive - vob tag name - view storage directory
- missing_relations:
  - click vms settings -> open version management systems drop-down list
  - open version management systems drop-down list -> select clearcase
  - select clearcase -> enter details
  - enter details -> clearcase map drive [fork]
  - enter details -> vob tag name [fork]
  - enter details -> view storage directory [fork]
  - clearcase map drive -> enter mvfs s folder name
  - vob tag name -> enter vob name
- input_excerpt:
  17.	set the ClearCase version management system in Unix1. In the Administration Options window, click VMS Settings.2. From the Version Management Systems drop-down list, select ClearCase.3. Enter the following details:• ClearCase Map Drive - Enter the name of the folder where the MVFSis located. By default, it is /view• VOB Tag Name - Enter the VOB name and the folder where the VOBis located. For example: VobFolder/VobName• View Storage Directory: Enter the path of the directory where the viewsare created.
- generated_excerpt:
  @startuml start :Open Administration Options Window; :Click VMS Settings; :Select ClearCase from Version Management Systems drop-down list; :Enter ClearCase details:   - ClearCase Map Drive   - VOB Tag Name   - View Storage Directory; stop @enduml
### bp-0030
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.2353
- llm_element_status: success
- llm_node_f1: 0.9756
- llm_relation_f1: 0.3158
- missing_nodes:
  - log in
  - go to promotion jobs
  - click new job
  - enter name
  - enter description
  - enter keywords
  - go to save job field
  - browse and select the folder
- extra_nodes:
  - log into the lifecycle manager tool
  - in the promotion jobs home page click new job
  - enter the name description and keywords for the job in the appropriate fields
  - in the save job in field browse and select the folder in which you want to save the job
  - select the source system and the destination system from the drop-down lists
  - system name displayed in drop-down list?
  - click the login to a new cms option
  - enter the name of the system along with the user name and password
- missing_relations:
  - log in -> go to promotion jobs
  - click new job -> new job window appears
  - new job window appears -> enter name [fork]
  - new job window appears -> enter description [fork]
  - new job window appears -> enter keywords [fork]
  - enter name -> go to save job field [merge]
  - enter description -> go to save job field [merge]
  - enter keywords -> go to save job field [merge]
- input_excerpt:
  30.	Creating a New Job1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriate fields.4. In the Save Job in field, browse and select the folder in which you want to save the job.5. Select the source system and the destination system from the drop-down lists. If the name of the system is not displayed in the drop-down list, click the Login to a new CMS option. A new window is launched. Enter the name of the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page,\nclick New Job; :The "New Job" window appears; :Enter the name, description, and keywords\nfor the job in the appropriate fields; :In the Save Job in field,\nbrowse and select the folder\nin which you want to save the job; :Select the source system and the\ndestination system from the drop-down lists; if (System name displayed in drop-down list?) then (No)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the name of the system\nalong with the user name and password; else (Yes) endif :Click Create; stop @enduml
### bp-0002
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2424
- relation_f1: 0.0556
- llm_element_status: success
- llm_node_f1: 0.7179
- llm_relation_f1: 0.6190
- missing_nodes:
  - user authorizations are sufficient?
  - log in
  - data warehousing workbench is started
  - choose info objects
  - info object tree is displayed
  - open root node context menu
  - choose create info area
  - enter a technical name
- extra_nodes:
  - log onto the bi system with sufficient authorizations
  - under modeling choose info objects (display info object tree)
  - from context menu at root node info objects choose create info area
  - enter technical name and description for the info area
  - info area is displayed in the info object tree (it is used to group your info objects)
  - enter technical name and description select key figure as info object type
  - info object catalog is displayed in your info area (it is used to group your key figures)
  - create a key figure (revenue quantity or price)
- missing_relations:
  - user authorizations are sufficient? -> log in [yes]
  - log in -> choose modeling data warehousing workbench modeling
  - choose modeling data warehousing workbench modeling -> data warehousing workbench is started
  - data warehousing workbench is started -> choose info objects
  - choose info objects -> info object tree is displayed
  - info object tree is displayed -> open root node context menu
  - open root node context menu -> choose create info area
  - choose create info area -> enter a technical name [fork]
- input_excerpt:
  2.	Log onto the BI system1.	Log onto the BI system with a user that has sufficient authorizations for executing the scenario.2.	Start the Data Warehousing Workbench in the SAP menu by choosing Modeling Data Warehousing Workbench: Modeling.3.	Under Modeling, choose Info  Objects. The Info  Object tree is displayed.4.	From the context menu at the root node Info Objects of the Info Object tree, choose Create Info Area.5.	On the next screen, enter a technical name and a description for the Info Area. The Info Area is displayed in the Info Object tree.6.	It is used to group your Info Objects.7.	In the context menu of the Info Area, choose Create Info Object Catalog.8.	On the next screen, enter a 
- generated_excerpt:
  @startuml start :Log onto the BI system with sufficient authorizations; :Start the Data Warehousing Workbench (Modeling -> Data Warehousing Workbench: Modeling); :Under Modeling, choose Info Objects (Display Info Object tree); :From context menu at root node Info Objects, choose Create Info Area; :Enter technical name and description for the Info Area; :Info Area is displayed in the Info Object tree (It is used to group your Info Objects); :In the context menu of the Info Area, choose Create Info Object Catalog; :Enter technical name and description, select Key Figure as Info Object Type; :Choose Create; :Activate the Info Object catalog; :Info Object catalog is displayed in your Info Area (
### fsd-0065
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2791
- relation_f1: 0.3390
- llm_element_status: success
- llm_node_f1: 0.6809
- llm_relation_f1: 0.7097
- missing_nodes:
  - tcms operates on preemptive rtos
  - manage through deterministically scheduled tasks
  - traction
  - braking
  - door control
  - diagnostic functions
  - vehicle speed > defined threshold and detect anomalous signal?
  - trigger high-priority condition
- extra_nodes:
  - manage traction braking door control and diagnostic functions through deterministically scheduled tasks
  - vehicle speed exceeds threshold concurrently with sensor anomalous signal?
  - verify fuel injection and intake volume parameters remain within operational envelopes
  - initialize emergency braking assist function with state synchronization across relevant ecus
  - launch synchronized fault diagnosis routine for abs
  - launch synchronized fault diagnosis routine for ebd
  - execute locked-step self-test and calibration for all involved nodes
  - adhere to fail-safe design principles for graceful degradation (en 50128 en 50129 compliance)
- missing_relations:
  - tcms operates on preemptive rtos -> manage through deterministically scheduled tasks
  - manage through deterministically scheduled tasks -> traction [fork]
  - manage through deterministically scheduled tasks -> braking [fork]
  - manage through deterministically scheduled tasks -> door control [fork]
  - manage through deterministically scheduled tasks -> diagnostic functions [fork]
  - traction -> vehicle speed > defined threshold and detect anomalous signal? [merge]
  - braking -> vehicle speed > defined threshold and detect anomalous signal? [merge]
  - door control -> vehicle speed > defined threshold and detect anomalous signal? [merge]
- input_excerpt:
  Operating on a preemptive RTOS, the Train Control and Monitoring System (TCMS) manages traction, braking, door control, and diagnostic functions through deterministically scheduled tasks. A high-priority condition is triggered when the vehicle speed exceeds a defined threshold concurrently with a sensor detecting an anomalous signal. This event immediately launches two concurrent processes: a dedicated control task enters a loop to continuously sample and analyze engine speed data via a protected ring buffer until stability is restored, while a separate monitoring task verifies that both fuel injection and intake volume parameters remain within their specified operational envelopes. Upon com
- generated_excerpt:
  @startuml start :Manage traction, braking, door control, and diagnostic functions through deterministically scheduled tasks;  if (Vehicle speed exceeds threshold\nconcurrently with sensor anomalous signal?) then (yes)   fork     repeat       :Sample and analyze engine speed data via protected ring buffer;     repeat while (Stability restored?) is (no)     ->yes;   fork again     :Verify fuel injection and intake volume parameters\nremain within operational envelopes;   end fork    if (Braking subsystem reports insufficient pressure?) then (yes)     :Initialize emergency braking assist function\nwith state synchronization across relevant ECUs;     fork       :Launch synchronized fault diagnos
### bp-0009
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.1250
- llm_element_status: success
- llm_node_f1: 0.8696
- llm_relation_f1: 0.9167
- missing_nodes:
  - choose start programs business explorer web application designer
  - bex web is started
  - log in
  - initial screen is shown
  - open data provider type dialog box
  - select query
  - enter zd_sales_2007 as query name
  - data provider is displayed
- extra_nodes:
  - start bex web application (start > programs > business explorer > web application designer)
  - log onto the bi system
  - select query as data provider type and enter zd_sales_2007
  - the data provider is displayed in the layout view
- missing_relations:
  - choose start programs business explorer web application designer -> bex web is started
  - bex web is started -> log in
  - log in -> initial screen is shown
  - initial screen is shown -> click create new blank web template
  - choose new data provider -> open data provider type dialog box
  - open data provider type dialog box -> select query
  - select query -> enter zd_sales_2007 as query name
  - enter zd_sales_2007 as query name -> choose ok
- input_excerpt:
  9.	Creating Web Applications1. Start the BEx Web application by choosing Start Programs Business Explorer Web Application Designer.2. Log onto the BI system.3. In the initial screen of the Web Application Designer, click on the link Create New Blank Web Template.4. In the lower part of the layout view choose New Data Provider.5. In the dialog box for the data provider type select Query and enter the name of the query ZD_SALES_2007 in the eld following Query.6. Choose OK.7. The data provider is displayed in the lower part of the layout view in the Web Application Designer
- generated_excerpt:
  @startuml start :Start BEx Web Application\n(Start > Programs > Business Explorer > Web Application Designer); :Log onto the BI system; :Click on the link\nCreate New Blank Web Template; :Choose New Data Provider; :Select Query as data provider type\nand enter ZD_SALES_2007; :Choose OK; :The data provider is displayed\nin the layout view; stop @enduml
### fsd-0111
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3600
- relation_f1: 0.2985
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.5915
- missing_nodes:
  - govern multi-stage cooling strategy for
  - pwm fans
  - liquid-cooling loops
  - out-of-range ambient temperature reading?
  - trigger temperature regulation state
  - high-priority task activates forced-air cooling via pwm fans
  - > critical threshold?
  - initiate via protected can command
- extra_nodes:
  - detect out-of-range ambient temperature from sensor fusion
  - enter temperature regulation state
  - activate forced-air cooling via pwm fans
  - exceeds critical threshold?
  - initiate air conditioning compressor via protected can command
  - initiate liquid cooling pump via protected can command
  - adjust fan duty cycle (closed-loop control)
  - verify operational status of all thermal control devices (mutex-protected sensor data access)
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern multi-stage cooling strategy for
  - govern multi-stage cooling strategy for -> pwm fans [fork]
  - govern multi-stage cooling strategy for -> liquid-cooling loops [fork]
  - pwm fans -> out-of-range ambient temperature reading? [merge]
  - liquid-cooling loops -> out-of-range ambient temperature reading? [merge]
  - out-of-range ambient temperature reading? -> trigger temperature regulation state [yes]
  - out-of-range ambient temperature reading? -> temperature stabilization at preset target [no]
  - > critical threshold? -> initiate via protected can command [yes]
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing a multi-stage cooling strategy for PWM fans and liquid-cooling loops. An out-of-range ambient temperature reading from the sensor fusion routine triggers the temperature regulation state. If the temperature continues to rise, a high-priority task activates forced-air cooling via the PWM fans. Upon exceeding a critical threshold, the system concurrently initiates the air conditioning compressor and liquid cooling pump via a protected CAN command, with a watchdog monitoring the response. This aggressive cooling phase employs a closed-loop control that cyclically adjusts the fan duty cycle until the temperature
- generated_excerpt:
  @startuml start :Execute thermal management state machine on RTOS; :Detect out-of-range ambient temperature from sensor fusion; :Enter temperature regulation state;  if (Temperature continues to rise?) then (yes)   :Activate forced-air cooling via PWM fans;      if (Exceeds critical threshold?) then (yes)     fork       :Initiate air conditioning compressor via protected CAN command;     fork again       :Initiate liquid cooling pump via protected CAN command;     end fork     :Monitor response via watchdog;          repeat       :Adjust fan duty cycle (closed-loop control);     repeat while (Temperature re-enters safe operating envelope?) is (no)     ->yes;        else (no)   endif    elsei
### fsd-0078
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.2041
- llm_element_status: success
- llm_node_f1: 0.6818
- llm_relation_f1: 0.3000
- missing_nodes:
  - thermal management controller operates as state machine within hard real-time rtos
  - govern multi-zone pwm fans
  - govern liquid-cooling pump loops
  - primary task scheduled with high priority
  - continuously monitor via protected sensor fusion thread
  - equipment temperature
  - rail voltage
  - either parameter > defined threshold?
- extra_nodes:
  - monitor equipment temperature and rail voltage via protected sensor fusion thread
  - temperature or voltage exceeds threshold?
  - retry successful?
  - run sensor calibration
  - periodically
  - out-of-range reading type
- missing_relations:
  - thermal management controller operates as state machine within hard real-time rtos -> govern multi-zone pwm fans [fork]
  - thermal management controller operates as state machine within hard real-time rtos -> govern liquid-cooling pump loops [fork]
  - govern multi-zone pwm fans -> primary task scheduled with high priority [merge]
  - govern liquid-cooling pump loops -> primary task scheduled with high priority [merge]
  - primary task scheduled with high priority -> continuously monitor via protected sensor fusion thread
  - continuously monitor via protected sensor fusion thread -> equipment temperature [fork]
  - continuously monitor via protected sensor fusion thread -> rail voltage [fork]
  - equipment temperature -> either parameter > defined threshold? [merge]
- input_excerpt:
  Operating as a state machine within a hard real-time RTOS, the thermal management controller governs multi-zone PWM fans and liquid-cooling pump loops. Its primary task, scheduled with high priority, continuously monitors equipment temperature and rail voltage via a protected sensor fusion thread. Should either parameter exceed its defined threshold, the system initiates concurrent mitigation tasks managed through priority queues and mutex-protected shared resources. These include a power management routine that, upon detecting a critical battery state from the BMS or abnormal power consumption, engages exponential backoff retry logic with the PMIC for power optimization. Simultaneously, a c
- generated_excerpt:
  @startuml start  :Monitor equipment temperature and rail voltage via protected sensor fusion thread;  if (Temperature or voltage exceeds threshold?) then (yes)   fork     :Power management routine;     if (Critical battery state from BMS or abnormal power consumption?) then (yes)       repeat         :Engage exponential backoff retry logic with PMIC for power optimization;       repeat while (Retry successful?) is (no)       ->yes;     else (no)     endif   fork again     :Communications handler;     if (Signal strength insufficient?) then (yes)       :Attempt network signal enhancement;       :Secure critical commands with CRC checks over CAN bus;     else (no)     endif   end fork else (no
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3922
- llm_element_status: success
- llm_node_f1: 0.8814
- llm_relation_f1: 0.6786
- missing_nodes:
  - switch to state 95
  - condition judgement
  - in remote mode
  - remote mode is closed
  - shutdown
  - pet mode open request is closed
- extra_nodes:
  - system starts up
  - move to state 95
  - proceed to state 105
  - remote mode?
  - go to state 105
  - slow charging becomes inactive?
  - shift to state 28
  - remote mode deactivates?
- missing_relations:
  - switch to state 93 -> charging/discharging power-up is active and front mcu high-voltage detection flag is 1
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - switch to state 105 -> condition judgement
  - condition judgement -> in remote mode [case in remote mode]
  - switch to state 28 -> remote mode is closed
  - condition judgement -> pet mode request is received [case pet mode request is received]
  - switch to state 28 -> pet mode open request is closed
  - pet mode open request is closed -> shutdown [yes]
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging active and front MCU high-voltage detection flag is 0?) then (Yes)   :Transition to state 93; elseif (Charging/discharging power-up active and front MCU high-voltage detection flag is 1?) then (Yes)   :Move to state 95; elseif (Power-up readiness confirmed and vehicle charging/discharging mode is 2?) then (Yes)   :Proceed to state 105; endif if (Remote mode?) then (Yes)   :Go to state 105;   if (Slow charging becomes inactive?) then (Yes)     :Shift to state 28;   endif   if (Remote mode deactivates?) then (Yes)     :Initiate shutdown;     stop   endif elseif (Pet mode request received?) then (Yes)   :Enter state 105;   if (Slow charging i
### lmc-0032
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.5714
- llm_element_status: success
- llm_node_f1: 0.8333
- llm_relation_f1: 0.8571
- missing_nodes:
  - in nlguidance
  - command nearest inertial position
  - reestablish minimum standoff distance
- extra_nodes:
  - command nearest inertial position to reestablish minimum standoff distance
- missing_relations:
  - in nlguidance -> uav relative position to target < minimum standoff distance?
  - command nearest inertial position -> reestablish minimum standoff distance
  - reestablish minimum standoff distance -> maintain target on vehicle port-side [merge]
- input_excerpt:
  5.	When the UAV relative position to the target is less than the minimum standoff distance, NLGuidance shall command the nearest inertial position in order to reestablish the minimum standoff distance while maintaining the target on the port-side of the vehicle.
- generated_excerpt:
  @startuml start if (UAV relative position to target < minimum standoff distance?) then (yes)   fork     :Command nearest inertial position to reestablish minimum standoff distance;   fork again     :Maintain target on the port-side of the vehicle;   end fork else (no) endif stop @enduml
### fsd-0103
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5581
- relation_f1: 0.2857
- llm_element_status: success
- llm_node_f1: 0.8085
- llm_relation_f1: 0.4828
- missing_nodes:
  - thermal management controller implemented as deterministic state machine on rtos
  - govern pwm fan speeds
  - govern liquid-cooling pump actuators
  - scheduler initializes high-priority tasks
  - data acquisition unit logs timestamped readings to ring buffer
  - alarm unit that signals event
  - data acquisition loop protected by mutex for sensor data integrity
  - run continuously
- extra_nodes:
  - initialize high-priority data acquisition unit
  - initialize high-priority alarm unit that signals the event
  - log timestamped readings to ring buffer (protected by mutex for sensor data integrity)
  - terminate data acquisition loop
  - spawn external communication module
  - communication link establishment?
- missing_relations:
  - thermal management controller implemented as deterministic state machine on rtos -> govern pwm fan speeds [fork]
  - thermal management controller implemented as deterministic state machine on rtos -> govern liquid-cooling pump actuators [fork]
  - govern pwm fan speeds -> pmic/fused sensor input indicate ambient temperature > safety threshold? [merge]
  - govern liquid-cooling pump actuators -> pmic/fused sensor input indicate ambient temperature > safety threshold? [merge]
  - pmic/fused sensor input indicate ambient temperature > safety threshold? -> scheduler initializes high-priority tasks [yes]
  - scheduler initializes high-priority tasks -> data acquisition unit logs timestamped readings to ring buffer [fork]
  - scheduler initializes high-priority tasks -> alarm unit that signals event [fork]
  - alarm unit that signals event -> data acquisition loop protected by mutex for sensor data integrity [merge]
- input_excerpt:
  The thermal management controller, implemented as a deterministic state machine on the RTOS, governs PWM fan speeds and liquid-cooling pump actuators. Upon the PMIC or a fused sensor input indicating an ambient temperature exceeding the safety threshold, the scheduler initializes high-priority tasks, including a data acquisition unit that logs timestamped readings to a ring buffer and an alarm unit that signals the event. This data acquisition loop, protected by a mutex for sensor data integrity, runs continuously until the temperature normalizes, at which point it terminates and a final alarm is issued. Should the fault persist without external intervention via a CAN command, secondary task
- generated_excerpt:
  @startuml start :PMIC or fused sensor input indicates\nambient temperature exceeds safety threshold; fork   :Initialize high-priority data acquisition unit; fork again   :Initialize high-priority alarm unit\nthat signals the event; end fork  repeat   :Log timestamped readings to ring buffer\n(protected by mutex for sensor data integrity); repeat while (Temperature normalizes?) is (No) ->Yes;  :Terminate data acquisition loop; :Issue final alarm;  if (Fault persists without external\nintervention via CAN command?) then (Yes)   fork     :Spawn external communication module;   fork again     :Spawn emergency cooling module;   end fork    switch (Communication link establishment?)   case (Succes
### lmc-0034
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.7273
- llm_relation_f1: 0.7273
- missing_nodes:
  - in nlguidance
  - output equivalent altitude of the vehicle
- extra_nodes:
  - output equivalent altitude of the vehicle for in-plane navigation
- missing_relations:
  - in nlguidance -> target = vehicle altitude?
  - target = vehicle altitude? -> output equivalent altitude of the vehicle [no]
- input_excerpt:
  7.	NLGuidance shall output the equivalent altitude of the vehicle for in-plane navigation.  In-plane navigation is defined where the target and the vehicle altitude (3rd component in the input inertial position vectors) are equal.
- generated_excerpt:
  @startuml start :Output equivalent altitude of the vehicle for in-plane navigation; if (Target altitude equals vehicle altitude?) then (Yes)   :Perform in-plane navigation; else (No) endif stop @enduml
### pure-0035
- dataset: pure
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6154
- relation_f1: 0.8000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - display inventory categories
  - click category cell
  - category
  - display list of inventory items
  - not clickable
- extra_nodes:
  - display all inventory categories for the selected department
  - click a sub-category cell (leaf category)
  - category type
  - display a list of all inventory items for that selected category
  - nothing happens - the category cell is not clickable
- missing_relations:
  - display inventory categories -> click category cell
  - category -> not clickable [case under 5]
  - not clickable -> category [merge]
- input_excerpt:
  1. User accesses the main inventory screen 2. The screen displays all inventory departments 3. User clicks a department cell 4. The screen displays all inventory categories for the selected department 5. User clicks a category cell that contains sub-categories 6. The screen displays all inventory sub-categories for the selected category 7. User clicks a sub-category cell (leaf category) 7.1. For a Unique Item category: 7.1.1. The screen displays a list of all inventory items for that selected category 7.1.2. User clicks an item in the items list 7.1.3. The screen displays the details for the item 7.2. For a Stock Item category: 7.2.1. The screen displays the details for that Stock Item categ
- generated_excerpt:
  @startuml start :Access main inventory screen; :Display all inventory departments; :Click a department cell; :Display all inventory categories for the selected department; :Click a category cell that contains sub-categories; :Display all inventory sub-categories for the selected category; :Click a sub-category cell (leaf category); switch (Category type) case (Unique Item)   :Display a list of all inventory items for that selected category;   :Click an item in the items list;   :Display the details for the item; case (Stock Item)   :Display the details for that Stock Item category; case (Under $5)   :Nothing happens – The category cell is not clickable; endswitch stop @enduml
### rac-0017
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6400
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.7857
- llm_relation_f1: 0.8485
- missing_nodes:
  - shutdown
  - after 10s
- extra_nodes:
  - system starts up
  - condition?
  - transition to state 126
  - shut down and exit
  - move to state 126
  - wait 10-second timeout
  - shift to state 126
- missing_relations:
  - enter state 82 -> bms counter=1 and battery pre-heating demand=3
  - slow charging is inactive -> shutdown [yes]
  - bms counter=1 and battery pre-heating demand=3 -> pre-charge failure occurs [no]
  - pre-charge failure occurs -> slow charging is inactive [no]
  - slow charging is inactive -> ac charging/discharging system fault [no]
  - ac charging/discharging system fault -> after 10s [yes]
  - after 10s -> switch to state 126
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU initialization is 0, it enters state 82. From there: - When the BMS counter reaches 1 with a battery pre-heating demand of 3, the system transitions to state 126. If slow charging becomes inactive afterward, it shuts down and exits. - If a pre-charge failure occurs, the system moves to state 126. Should slow charging be inactive at that point, it shuts down and exits. - If slow charging deactivates, the system switches to state 126 before shutting down and exiting. - For AC charging/discharging system faults, the system waits through a 10-second timeout before shifting to state 126. If slow charging is inactive followin
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging active\nand front MCU init = 0?) then (Yes)   :Enter state 82;   switch (Condition?)   case (BMS counter = 1\nand battery pre-heating demand = 3)     :Transition to state 126;     if (Slow charging inactive?) then (Yes)       :Shut down and exit;       stop     else (No)     endif   case (Pre-charge failure)     :Move to state 126;     if (Slow charging inactive?) then (Yes)       :Shut down and exit;       stop     else (No)     endif   case (Slow charging deactivates)     :Switch to state 126;     :Shut down and exit;     stop   case (AC charging/discharging system fault)     :Wait 10-second timeout;     :Shift to state 126;     if (Slow
### pure-0038
- dataset: pure
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7059
- relation_f1: 0.9333
- llm_element_status: success
- llm_node_f1: 0.9524
- llm_relation_f1: 0.9474
- missing_nodes:
  - see view inventory
  - system validates deletion
  - back to main inventory screen
- extra_nodes:
  - system validates the department deletion
  - user is taken back to the main inventory screen
- missing_relations:
  - see view inventory -> navigate to department
- input_excerpt:
  3. Delete Department 3.1. User navigates to a Department (see View Inventory) 3.2. System displays the Edit Department button 3.3. User clicks the Edit Department button 3.4. System displays the Department data 3.5. User clicks the Delete Department button 3.6. System validates the Department deletion 3.7. System removes the Department from the inventory 3.8. User is taken back to the main inventory screen
- generated_excerpt:
  @startuml start :User navigates to a Department; :System displays the Edit Department button; :User clicks the Edit Department button; :System displays the Department data; :User clicks the Delete Department button; :System validates the Department deletion; :System removes the Department from the inventory; :User is taken back to the main inventory screen; stop @enduml
### rac-0002
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7273
- relation_f1: 0.5600
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.7273
- missing_nodes:
  - gear is s
  - gear check
- extra_nodes:
  - system startup
  - check gear position
  - gear in s?
  - calculate d_s gear mileage parameter as s gear nominal mileage / d gear nominal mileage
- missing_relations:
  - switch to driving mode -> gear check
  - gear check -> gear is d or e [case gear is d or e]
  - gear check -> gear is n or r [case gear is n or r]
- input_excerpt:
  After the system starts up, the process begins by checking the gear position. If the gear is in D or N, the D_S gear mileage parameter is set to 1, and the sequence ends. If the gear is in S, the D_S gear mileage parameter is calculated as S gear nominal mileage divided by D gear nominal mileage, then the process concludes. Additionally, if the vehicle status is 30, switch to driving mode. Next, if the gear is in D or E, set the D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage, and end. Finally, if the gear is in N or R, observe using the D_S gear mileage parameter and terminate the process.
- generated_excerpt:
  @startuml start :System startup; :Check gear position; if (Gear in D or N?) then (Yes)   :Set D_S gear mileage parameter to 1; elseif (Gear in S?) then (Yes)   :Calculate D_S gear mileage parameter as S gear nominal mileage / D gear nominal mileage; endif if (Vehicle status is 30?) then (Yes)   :Switch to driving mode; endif if (Gear in D or E?) then (Yes)   :Set D_S gear mileage parameter to S gear nominal mileage / D gear nominal mileage; elseif (Gear in N or R?) then (Yes)   :Observe using D_S gear mileage parameter; endif stop @enduml
### rac-0019
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7333
- relation_f1: 0.5526
- llm_element_status: success
- llm_node_f1: 0.8947
- llm_relation_f1: 0.8039
- missing_nodes:
  - slow charging is active and charging system command=1
  - remote mode is disabled
  - slow charging is inactive
  - fast charging is inactive
  - switch to state 189
- extra_nodes:
  - system starts up
  - move to state 49
  - exit
  - proceed to state 49
  - charging system command is 1?
  - go to state 29
  - transition to state 49
  - move to state 110
- missing_relations:
  - switch to state 29 -> ignition switch=0 and vcc2=12
  - fast charge vcc2=6 -> slow charging is active and charging system command=1 [no]
  - slow charging is active and charging system command=1 -> switch to state 110 [yes]
  - switch to state 110 -> charging system command=4
  - switch to state 29 -> ignition switch=0 and slow charging is inactive
  - switch to state 28 -> remote mode is disabled
  - switch to state 110 -> slow charging is inactive
  - switch to state 170 -> fast charging is inactive
- input_excerpt:
  After the system starts up, if the ignition switch is set to 2, transition to state 30. Then, under that condition: - If the ignition switch becomes 0, move to state 49 and exit. - If the fast charge Vcc2 is 6, observe the charging gun indicator. Should the charging system command be 4, switch to state 29. - If the ignition switch is 0 and Vcc2 is 12, proceed to state 49 and exit. - If slow charging is active and the charging system command is 1, transition to state 110. If the command is 4 instead, go to state 29. Also, if the ignition switch is 0 and slow charging is not active, shift to state 49 and exit.  If remote mode is enabled, switch to state 28. If it's disabled, transition to stat
- generated_excerpt:
  @startuml start :System starts up; if (Ignition switch is 2?) then (Yes)   :Transition to state 30;   if (Ignition switch becomes 0?) then (Yes)     :Move to state 49;     :Exit;   elseif (Fast charge Vcc2 is 6?) then (Yes)     :Observe the charging gun indicator;     if (Charging system command is 4?) then (Yes)       :Switch to state 29;     else (No)     endif   elseif (Ignition switch is 0 and Vcc2 is 12?) then (Yes)     :Proceed to state 49;     :Exit;   elseif (Slow charging is active?) then (Yes)     if (Charging system command is 1?) then (Yes)       :Transition to state 110;     elseif (Charging system command is 4?) then (Yes)       :Go to state 29;     else (No)     endif   elseif
### pure-0096
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7500
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8333
- llm_relation_f1: 0.5000
- missing_nodes:
  - validate migration rapidly
- extra_nodes:
  - sample random percentage of records for rapid verification
- missing_relations:
  - use command arc_warc_verify options -> validate migration rapidly
  - validate migration rapidly -> compare arc and warc records checksums [fork]
  - validate migration rapidly -> optionally sample random records percentage [fork]
  - compare arc and warc records checksums -> validate migration rapidly [merge]
  - optionally sample random records percentage -> validate migration rapidly [merge]
- input_excerpt:
  Validation Tool Execution: Use the command arc_warc_verify <ARCFILE> <WARCFILE> <USER_DEFINED_ARG_READER> [options] to validate the migration. Compare checksums of records in ARC and WARC files, and optionally sample a random percentage of records for rapid verification.
- generated_excerpt:
  @startuml start :Execute arc_warc_verify <ARCFILE> <WARCFILE> <USER_DEFINED_ARG_READER> [options]; :Compare checksums of records in ARC and WARC files; if (Sample random percentage of records?) then (Yes)   :Sample random percentage of records for rapid verification; else (No) endif stop @enduml
### pure-0029
- dataset: pure
- failure_types: missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 1.0000
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8333
- llm_relation_f1: 0.1667
- missing_relations:
  - track buffer locations -> data processing is incomplete
  - data processing is incomplete -> store input data records in memory buffer [yes]
- input_excerpt:
  Input Data Management - The BE shall store input data records in a memory buffer and track buffer locations of all input data until data processing is complete. Report any buffer overflow conditions.
- generated_excerpt:
  @startuml start :Store input data records in a memory buffer; fork   :Track buffer locations of all input data; fork again   :Report any buffer overflow conditions; end fork :Data processing is complete; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
