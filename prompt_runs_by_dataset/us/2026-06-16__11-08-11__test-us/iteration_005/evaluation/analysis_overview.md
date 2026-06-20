# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3588
- node_recall: 0.3990
- node_f1: 0.3779
- relation_precision: 0.2500
- relation_recall: 0.2907
- relation_f1: 0.2688
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
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10
- wrong_parallel: 5
- wrong_loop: 5

## Representative Failure Cases
### lmc-0020
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - in inner loop yaw regulator
  - durations > 100 frames?
  - command angular yaw accelerations <= 50 deg/sec2
- extra_nodes:
  - inner loop yaw regulator commands angular yaw acceleration
  - is commanded yaw acceleration > 50 deg/sec ?
  - allow command
  - reset duration counter to 0
  - increment duration counter
  - has duration exceeded 100 frames (1 second 100 hz)?
  - allow command temporarily
  - limit yaw acceleration command to system capability (<= 50 deg/sec )
- missing_relations:
  - in inner loop yaw regulator -> durations > 100 frames?
  - durations > 100 frames? -> command angular yaw accelerations <= 50 deg/sec2 [yes]
- input_excerpt:
  3.	The Inner Loop Yaw Regulator Shall not command angular yaw accelerations greater than the capability of the system (50 deg/sec2) for durations exceeding 100 frames (1 second @ 100 hz).
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #E8F5E9 skinparam ActivityBorderColor #2E7D32  start  :Inner Loop Yaw Regulator\ncommands angular yaw acceleration;  if (Is commanded yaw acceleration > 50 deg/sec²?) then (No)   :Allow command;   :Reset duration counter to 0; else (Yes)   :Increment duration counter;      if (Has duration exceeded 100 frames\n(1 second @ 100 Hz)?) then (No)     :Allow command temporarily;   else (Yes)     :Limit yaw acceleration command\nto system capability (<= 50 deg/sec²);     :Reset duration counter;   endif endif  stop @enduml
### pure-0001
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - conduct contingency studies
  - determine amount and location of black start generation
  - verify black start units annually
  - number
  - size
  - availability
  - location
  - document cranking paths
- extra_nodes:
  - step 1 the caiso determines the amount and location of black start generation through contingency studies
  - step 2 the caiso annually verifies the number size availability and location of black start units
  - step 3 the caiso documents cranking paths and provides them to wecc upon request
  - step 4 the caiso evaluates diverse fuel resources cranking paths communication unit capabilities and coordination with neighboring plans
  - step 5 the planning process is coordinated with transmission owners and neighboring balancing authorities
  - step 6 the caiso annually enters into rmr and interim black start contracts with qualified generators
- missing_relations:
  - conduct contingency studies -> determine amount and location of black start generation
  - determine amount and location of black start generation -> verify black start units annually
  - verify black start units annually -> number [fork]
  - verify black start units annually -> size [fork]
  - verify black start units annually -> availability [fork]
  - verify black start units annually -> location [fork]
  - number -> document cranking paths
  - size -> document cranking paths
- input_excerpt:
  [Grid Planning Steps] Step 1: The CAISO determines the amount and location of Black Start Generation through contingency studies. Step 2: The CAISO annually verifies the number, size, availability, and location of Black Start units.Step 3: The CAISO documents Cranking Paths and provides them to WECC upon request.Step 4: The CAISO evaluates diverse fuel resources, cranking paths, communication, unit capabilities, and coordination with neighboring plans.Step 5: The planning process is coordinated with transmission owners and neighboring Balancing Authorities.Step 6: The CAISO annually enters into RMR and Interim Black Start Contracts with qualified generators.
- generated_excerpt:
  @startuml start :Step 1: The CAISO determines the amount and location of Black Start Generation through contingency studies; :Step 2: The CAISO annually verifies the number, size, availability, and location of Black Start units; :Step 3: The CAISO documents Cranking Paths and provides them to WECC upon request; :Step 4: The CAISO evaluates diverse fuel resources, cranking paths, communication, unit capabilities, and coordination with neighboring plans; :Step 5: The planning process is coordinated with transmission owners and neighboring Balancing Authorities; :Step 6: The CAISO annually enters into RMR and Interim Black Start Contracts with qualified generators; stop @enduml
### pure-0054
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1818
- relation_f1: 0.0526
- missing_nodes:
  - donor/primary contact has valid donation number
  - arrive at receiving dock
  - see view acquisitions
  - locate donation request
  - see add item to inventory
  - enter information
  - way to add item
  - clone an existing item
- extra_nodes:
  - donor or primary contact arrives at receiving dock with a valid donation number
  - receiving associate locates donation request in the system (see view acquisitions)
  - receiving associate enters information about each donated item into the donation request (see add item to inventory)
  - a new item can be added to the list by cloning an existing item
  - an item can be removed by setting the received quantity to zero
  - receiving associate prints a donation receipt
  - receiving associate optionally writes information to the receipt by hand such as condition
  - receiving associate prints item tags for unique and stock items (see add item to inventory)
- missing_relations:
  - arrive at receiving dock -> see view acquisitions
  - see view acquisitions -> locate donation request
  - locate donation request -> display donation request information
  - display donation request information -> see add item to inventory
  - see add item to inventory -> enter information
  - enter information -> add new item?
  - add new item? -> way to add item [yes]
  - way to add item -> clone an existing item [case clone]
- input_excerpt:
  1. Donor or Primary Contact arrives at receiving dock with a valid donation number 2. Receiving Associate locates donation request in the system (see View Acquisitions) 3. System displays donation request information 4. Receiving Associate enters information about each donated item into the donation request (see Add Item to Inventory) 4.1. A new item can be added to the list by cloning an existing item 4.2. A new item can be added by clicking the Add Item button 4.3. An item can be removed by setting the received quantity to zero 5. Receiving Associate prints a donation receipt 6. Receiving Associate optionally writes information to the receipt by hand such as condition 7. Donation receipt i
- generated_excerpt:
  @startuml start :Donor or Primary Contact arrives at receiving dock\nwith a valid donation number; :Receiving Associate locates\ndonation request in the system\n(see View Acquisitions); :System displays donation\nrequest information; :Receiving Associate enters information\nabout each donated item into the\ndonation request (see Add Item to Inventory); fork   :A new item can be added to the list\nby cloning an existing item; fork again   :A new item can be added\nby clicking the Add Item button; fork again   :An item can be removed by setting\nthe received quantity to zero; end fork :Receiving Associate prints\na donation receipt; :Receiving Associate optionally writes\ninformation to the re
### bp-0005
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1905
- relation_f1: 0.1739
- missing_nodes:
  - choose info objects
  - open characteristics info object catalog
  - open zd_pgroup context menu
  - select maintain master data
  - enter product group
  - enter short description
  - choose continue
  - more values?
- extra_nodes:
  - in the modeling area of the data warehousing workbench choose info objects
  - in the info object catalog for characteristics choose maintain master data from the context menu of info object product group (zd_pgroup)
  - enter product group and short description (e.g. ds10 / computer) and choose continue
  - more values to enter?
  - save your entries and return to the info object tree
  - repeat the process for the characteristic channel (zd_chan) with the following values
- missing_relations:
  - choose info objects -> open characteristics info object catalog
  - open characteristics info object catalog -> open zd_pgroup context menu
  - open zd_pgroup context menu -> select maintain master data
  - select maintain master data -> choose execute
  - choose create -> enter product group [fork]
  - choose create -> enter short description [fork]
  - enter product group -> choose continue
  - enter short description -> choose continue
- input_excerpt:
  5.	Creating Master Data Directly in the System1. In the Modeling area of the Data Warehousing Workbench, choose Info Objects. 2. In the Info Object catalog for characteristics, choose Maintain master data from the context menu of your Info Object Product Group (ZD_PGROUP).3. Choose Execute.4. Choose Create.5. Enter DS10 as Product Group and Computer as the Short description and choose Continue.6. Repeat steps 4 and 5 with the following values:7. Save your entries and return to the Info Object tree.8. Repeat steps 2-7 for the characteristic Channel (ZD_CHAN) with the following values:
- generated_excerpt:
  @startuml start :In the Modeling area of the Data Warehousing Workbench, choose Info Objects; :In the Info Object catalog for characteristics, choose Maintain master data from the context menu of Info Object Product Group (ZD_PGROUP); :Choose Execute; repeat   :Choose Create;   :Enter Product Group and Short description (e.g., DS10 / Computer) and choose Continue; repeat while (More values to enter?) is (Yes) ->No; :Save your entries and return to the Info Object tree; :Repeat the process for the characteristic Channel (ZD_CHAN) with the following values; stop @enduml
### bp-0021
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4167
- relation_f1: 0.3200
- missing_nodes:
  - click new job
  - the list of jobs is displayed
  - select a job from list
  - cick create
  - information is displayed
  - name
  - keywords
  - description
- extra_nodes:
  - select a job from the job list and click create
  - in the save job in field browse and select the folder in which you want to save the job
- missing_relations:
  - log in lifecycle manager tool -> go to promotion jobs home page
  - click the copy an existing job option -> the list of jobs is displayed
  - the list of jobs is displayed -> select a job from list
  - select a job from list -> cick create
  - cick create -> information is displayed
  - information is displayed -> name [fork]
  - information is displayed -> keywords [fork]
  - information is displayed -> description [fork]
- input_excerpt:
  21.	create a new job by copying an existing job.To create a new job by copying an existing job, complete the following steps:1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job.3. Click the Copy an Existing Job option. The list of jobs in the PromotionJob folder is displayed4. Select a job from the job list, and click Create. The name, keywords, and description of the job are displayed. You can modify these fields, if required. However, you cannot change the source system.5. In the Save Job in field, browse and select the folder in which you want to save the job, and click Create.A new job is created.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :Click the Copy an Existing Job option; note right: The list of jobs in the PromotionJob folder is displayed :Select a job from the job list, and click Create; note right: The name, keywords, and description of the job are displayed.\nYou can modify these fields, if required.\nHowever, you cannot change the source system. :In the Save Job in field, browse and select the folder in which you want to save the job; :Click Create; :A new job is created; stop @enduml
### fsd-0104
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4783
- relation_f1: 0.2182
- missing_nodes:
  - thermal management controller operates as state machine within rtos
  - govern pwm fans
  - govern liquid-cooling loops using multi-threaded architecture
  - high-priority isr triggered by pmic/dedicated temperature sensors
  - abnormal temperature rise?
  - employ primary control loop
  - early warning threshold reached?
  - cease
- extra_nodes:
  - receive isr from pmic or temp sensors
  - temp >= early warning threshold?
  - spawn concurrent monitoring task n (from priority queue)
  - cease monitoring
  - escalate thermal response
  - significant temp fluctuation?
  - acquire mutex
  - log anomaly to structured audit trail (ring buffer)
- missing_relations:
  - thermal management controller operates as state machine within rtos -> govern pwm fans [fork]
  - thermal management controller operates as state machine within rtos -> govern liquid-cooling loops using multi-threaded architecture [fork]
  - govern pwm fans -> high-priority isr triggered by pmic/dedicated temperature sensors
  - govern liquid-cooling loops using multi-threaded architecture -> high-priority isr triggered by pmic/dedicated temperature sensors
  - high-priority isr triggered by pmic/dedicated temperature sensors -> abnormal temperature rise?
  - abnormal temperature rise? -> initiate safety protocols [yes]
  - initiate safety protocols -> employ primary control loop
  - employ primary control loop -> early warning threshold reached?
- input_excerpt:
  Operating as a state machine within the RTOS, the thermal management controller governs PWM fans and liquid-cooling loops using a multi-threaded architecture. A high-priority ISR, triggered by the PMIC or dedicated temperature sensors, initiates safety protocols upon detecting an abnormal temperature rise. The system employs a primary control loop which, upon reaching an early warning threshold, spawns concurrent tasks from a priority queue to actively monitor the temperature in fixed cycles; monitoring ceases only when thermal stability is confirmed, otherwise it escalates. If the temperature remains below this threshold but exhibits significant fluctuation, a lower-priority task logs the a
- generated_excerpt:
  @startuml skinparam ActivityDiamondFontSize 12 skinparam ActivityFontSize 12  start  partition "Interrupt Service Routine" {     :Receive ISR from PMIC or Temp Sensors;     :Initiate Safety Protocols; }  partition "Primary Control Loop" {     if (Temp >= Early Warning Threshold?) then (Yes)         fork             :Spawn Concurrent Monitoring Task 1\n(from Priority Queue);         fork again             :Spawn Concurrent Monitoring Task N\n(from Priority Queue);         end fork         :Monitor Temperature in Fixed Cycles;         if (Thermal Stability Confirmed?) then (Yes)             :Cease Monitoring;         else (No)             :Escalate Thermal Response;             stop         en
### lmc-0044
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3158
- missing_nodes:
  - in cockpit
- extra_nodes:
  - autopilot engage switch deselected
  - command to roll actuator = active
  - autopilot engage switch deselected?
  - continue roll autopilot operation
  - switch remains selected
  - wait for switch selection
  - system active
- missing_relations:
  - in cockpit -> autopilot engage switch
- input_excerpt:
  Roll Autopilot shall engage when the pilot selects the autopilot engage switch in the cockpit and disengage when the switch is deselected. When not engaged, the command to the roll actuator shall be zero.
- generated_excerpt:
  @startuml start :Autopilot Engage Switch Deselected; :Roll Autopilot Disengaged; :Command to Roll Actuator = Zero; repeat   if (Autopilot Engage Switch Selected?) then (Yes)     :Roll Autopilot Engaged;     :Command to Roll Actuator = Active;     repeat       if (Autopilot Engage Switch Deselected?) then (Yes)         :Roll Autopilot Disengaged;         :Command to Roll Actuator = Zero;         break       else (No)         :Continue Roll Autopilot Operation;       endif     repeat while (Switch remains selected)   else (No)     :Wait for Switch Selection;   endif repeat while (System active) @enduml
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5161
- relation_f1: 0.2791
- missing_nodes:
  - condition judgement
  - shutdown
  - wait 0.8s
  - high-voltage shutdown request charging/discharging =2
- extra_nodes:
  - system starts up
  - pre-charge failure occurs?
  - move to state 175
  - shut down
  - high-voltage shutdown request detected (value=2)?
  - wait 0.8 seconds
  - enter state 175
  - ignition switch status=2?
- missing_relations:
  - switch to state 153 -> bms-fast charger handshake flag=0 and front mcu high-voltage flag=0
  - enter state 155 -> condition judgement
  - condition judgement -> switch to state 175 [case pre-charge failure occurs]
  - condition judgement -> wait 0.8s [case high-voltage shutdown request charging/discharging =2]
  - wait 0.8s -> switch to state 175
  - condition judgement -> stay in state 155 [case ignition switch=2]
  - stay in state 155 -> high-voltage shutdown request charging/discharging =2
  - high-voltage shutdown request charging/discharging =2 -> wait 0.8s [if yes]
- input_excerpt:
  After the system starts up: - If charging is active (charging=1) and the front MCU high-voltage detection flag is 0, transition to state 153. - If the BMS-fast charger handshake flag is 0 and the front MCU high-voltage flag is 0, enter state 155.  While in state 155: 1. If pre-charge failure occurs, move to state 175. If fast charging remains inactive after this, shut down and end the process. 2. If a high-voltage shutdown request (for charging/discharging) is detected (value=2), wait 0.8 seconds before entering state 175. If fast charging is inactive afterward, shut down and end. 3. If the ignition switch status is 2, remain in state 155. If a high-voltage shutdown request (value=2) exists 
- generated_excerpt:
  @startuml start :System starts up;  if (charging=1 && front MCU high-voltage detection flag=0) then (yes)   :Transition to state 153;   stop elseif (BMS-fast charger handshake flag=0 && front MCU high-voltage flag=0) then (yes)   :Enter state 155; else (no)   stop endif  repeat   if (pre-charge failure occurs?) then (yes)     :Move to state 175;     if (fast charging inactive?) then (yes)       :Shut down;       stop     endif   elseif (high-voltage shutdown request detected (value=2)?) then (yes)     :Wait 0.8 seconds;     :Enter state 175;     if (fast charging inactive?) then (yes)       :Shut down;       stop     endif   elseif (ignition switch status=2?) then (yes)     :Remain in state 

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
