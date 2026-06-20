# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4017
- node_recall: 0.3835
- node_f1: 0.3924
- relation_precision: 0.3214
- relation_recall: 0.3387
- relation_f1: 0.3298
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
- extra_or_wrong_relation: 10
- missing_or_wrong_relation: 9
- wrong_parallel: 5
- wrong_loop: 5

## Representative Failure Cases
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
  - the caiso determines the amount and location of black start generation through contingency studies
  - the caiso annually verifies the number size availability and location of black start units
  - the caiso documents cranking paths
  - wecc requests cranking paths?
  - the caiso provides cranking paths to wecc
  - the caiso evaluates diverse fuel resources
  - the caiso evaluates cranking paths
  - the caiso evaluates communication
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
  @startuml start :The CAISO determines the amount and location of Black Start Generation through contingency studies; :The CAISO annually verifies the number, size, availability, and location of Black Start units; :The CAISO documents Cranking Paths; if (WECC requests Cranking Paths?) then (yes)   :The CAISO provides Cranking Paths to WECC; else (no) endif :The CAISO evaluates diverse fuel resources; :The CAISO evaluates cranking paths; :The CAISO evaluates communication; :The CAISO evaluates unit capabilities; :The CAISO evaluates coordination with neighboring plans; :The CAISO coordinates the planning process with transmission owners; :The CAISO coordinates the planning process with neighbo
### pure-0054
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1667
- relation_f1: 0.1395
- missing_nodes:
  - donor/primary contact has valid donation number
  - arrive at receiving dock
  - see view acquisitions
  - locate donation request
  - see add item to inventory
  - enter information
  - add new item?
  - way to add item
- extra_nodes:
  - donor or primary contact arrives at receiving dock with a valid donation number
  - receiving associate locates donation request in the system
  - receiving associate enters information about each donated item into the donation request
  - item entry action
  - a new item is added to the list by cloning an existing item
  - a new item is added by clicking the add item button
  - an item is removed by setting the received quantity to zero
  - more items to enter?
- missing_relations:
  - arrive at receiving dock -> see view acquisitions
  - see view acquisitions -> locate donation request
  - locate donation request -> display donation request information
  - display donation request information -> see add item to inventory
  - see add item to inventory -> enter information
  - add new item? -> way to add item [yes]
  - way to add item -> clone an existing item [case clone]
  - way to add item -> click add item button [case click]
- input_excerpt:
  1. Donor or Primary Contact arrives at receiving dock with a valid donation number 2. Receiving Associate locates donation request in the system (see View Acquisitions) 3. System displays donation request information 4. Receiving Associate enters information about each donated item into the donation request (see Add Item to Inventory) 4.1. A new item can be added to the list by cloning an existing item 4.2. A new item can be added by clicking the Add Item button 4.3. An item can be removed by setting the received quantity to zero 5. Receiving Associate prints a donation receipt 6. Receiving Associate optionally writes information to the receipt by hand such as condition 7. Donation receipt i
- generated_excerpt:
  @startuml start :Donor or Primary Contact arrives at receiving dock with a valid donation number; :Receiving Associate locates donation request in the system; :System displays donation request information; repeat   :Receiving Associate enters information about each donated item into the donation request;   switch (Item entry action)   case (Clone existing item)     :A new item is added to the list by cloning an existing item;   case (Click Add Item button)     :A new item is added by clicking the Add Item button;   case (Remove item)     :An item is removed by setting the received quantity to zero;   endswitch repeat while (More items to enter?) is (yes) -> no; :Receiving Associate prints a 
### bp-0005
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1905
- relation_f1: 0.1667
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
  - choose info objects in the modeling area of the data warehousing workbench
  - choose maintain master data from the context menu of info object product group (zd_pgroup) or channel (zd_chan) in the info object catalog for characteristics
  - enter product group and short description then choose continue
  - more values to enter?
  - save your entries and return to the info object tree
  - more characteristics to maintain?
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
  @startuml start :Choose Info Objects in the Modeling area of the Data Warehousing Workbench; repeat   :Choose Maintain master data from the context menu of Info Object Product Group (ZD_PGROUP) or Channel (ZD_CHAN) in the Info Object catalog for characteristics;   :Choose Execute;   repeat     :Choose Create;     :Enter Product Group and Short description, then choose Continue;   repeat while (More values to enter?)   :Save your entries and return to the Info Object tree; repeat while (More characteristics to maintain?) stop @enduml
### lmc-0020
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2222
- relation_f1: 0.2000
- missing_nodes:
  - in inner loop yaw regulator
  - durations > 100 frames?
- extra_nodes:
  - command angular yaw acceleration
  - duration exceeding 100 frames (1 second 100 hz)?
  - reject command
  - allow command
  - regulator is active
- missing_relations:
  - in inner loop yaw regulator -> durations > 100 frames?
- input_excerpt:
  3.	The Inner Loop Yaw Regulator Shall not command angular yaw accelerations greater than the capability of the system (50 deg/sec2) for durations exceeding 100 frames (1 second @ 100 hz).
- generated_excerpt:
  @startuml start repeat   :Command angular yaw acceleration;   if (Commanded angular yaw acceleration > 50 deg/sec2?) then (Yes)     if (Duration exceeding 100 frames (1 second @ 100 hz)?) then (Yes)       :Reject command;     else (No)       :Allow command;     endif   else (No)     :Allow command;   endif repeat while (Regulator is active) @enduml
### fsd-0104
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3243
- relation_f1: 0.2128
- missing_nodes:
  - thermal management controller operates as state machine within rtos
  - govern pwm fans
  - govern liquid-cooling loops using multi-threaded architecture
  - abnormal temperature rise?
  - initiate safety protocols
  - employ primary control loop
  - spawn concurrent tasks from priority queue
  - actively monitor temperature in fixed cycles
- extra_nodes:
  - initiate safety protocols upon detecting abnormal temperature rise
  - spawn concurrent task from priority queue to monitor temperature in fixed cycles
  - spawn concurrent task from priority queue to actively monitor temperature in fixed cycles
  - significant temperature fluctuation?
  - acquire mutex
  - log anomaly to structured audit trail within ring buffer
  - release mutex
  - verify critical safety actions (sensor fusion calibration routines redundancy management for out-of-range readings)
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
  @startuml start :ISR triggered by PMIC or dedicated temperature sensors; :Initiate safety protocols upon detecting abnormal temperature rise;  repeat   if (Early warning threshold reached?) then (yes)     fork       :Spawn concurrent task from priority queue to monitor temperature in fixed cycles;     fork again       :Spawn concurrent task from priority queue to actively monitor temperature in fixed cycles;     fork again       :Spawn concurrent task from priority queue to actively monitor temperature in fixed cycles;     end fork     if (Thermal stability confirmed?) then (no)       :Escalate;     else (yes)     endif   else (no)     if (Significant temperature fluctuation?) then (yes)    
### bp-0021
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4286
- relation_f1: 0.2000
- missing_nodes:
  - click new job
  - the list of jobs is displayed
  - cick create
  - information is displayed
  - name
  - keywords
  - description
  - modification?
- extra_nodes:
  - the list of jobs in the promotionjob folder is displayed
  - the name keywords and description of the job are displayed
  - modify fields required?
  - modify the name keywords and description fields
  - in the save job in field browse and select the folder in which you want to save the job
- missing_relations:
  - log in lifecycle manager tool -> go to promotion jobs home page
  - click new job -> click the copy an existing job option
  - click the copy an existing job option -> the list of jobs is displayed
  - the list of jobs is displayed -> select a job from list
  - select a job from list -> cick create
  - cick create -> information is displayed
  - information is displayed -> name [fork]
  - information is displayed -> keywords [fork]
- input_excerpt:
  21.	create a new job by copying an existing job.To create a new job by copying an existing job, complete the following steps:1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job.3. Click the Copy an Existing Job option. The list of jobs in the PromotionJob folder is displayed4. Select a job from the job list, and click Create. The name, keywords, and description of the job are displayed. You can modify these fields, if required. However, you cannot change the source system.5. In the Save Job in field, browse and select the folder in which you want to save the job, and click Create.A new job is created.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :Click the Copy an Existing Job option; :The list of jobs in the PromotionJob folder is displayed; :Select a job from the job list; :Click Create; :The name, keywords, and description of the job are displayed; if (Modify fields required?) then (yes)   :Modify the name, keywords, and description fields; else (no) endif; :In the Save Job in field, browse and select the folder in which you want to save the job; :Click Create; :A new job is created; @enduml
### lmc-0044
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3333
- missing_nodes:
  - in cockpit
  - autopilot engage switch
  - roll autopilot disengage
- extra_nodes:
  - pilot selects autopilot engage switch in the cockpit?
- missing_relations:
  - autopilot engage switch -> roll autopilot engage [case select]
  - autopilot engage switch -> roll autopilot disengage [case deselect]
  - roll autopilot disengage -> command to roll actuator be zero
- input_excerpt:
  Roll Autopilot shall engage when the pilot selects the autopilot engage switch in the cockpit and disengage when the switch is deselected. When not engaged, the command to the roll actuator shall be zero.
- generated_excerpt:
  @startuml start if (Pilot selects autopilot engage switch in the cockpit?) then (Yes)   :Engage Roll Autopilot; else (No)   :Command to the roll actuator is zero; endif @enduml
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5161
- relation_f1: 0.4615
- missing_nodes:
  - condition judgement
  - shutdown
  - wait 0.8s
  - high-voltage shutdown request charging/discharging =2
- extra_nodes:
  - system starts up
  - condition in state 155?
  - move to state 175
  - fast charging remains inactive?
  - shut down
  - wait 0.8 seconds
  - enter state 175
  - fast charging is inactive afterward?
- missing_relations:
  - switch to state 153 -> bms-fast charger handshake flag=0 and front mcu high-voltage flag=0
  - enter state 155 -> condition judgement
  - condition judgement -> wait 0.8s [case high-voltage shutdown request charging/discharging =2]
  - wait 0.8s -> switch to state 175
  - stay in state 155 -> high-voltage shutdown request charging/discharging =2
  - high-voltage shutdown request charging/discharging =2 -> wait 0.8s [if yes]
  - wait 0.8s -> ignition switch=0
- input_excerpt:
  After the system starts up: - If charging is active (charging=1) and the front MCU high-voltage detection flag is 0, transition to state 153. - If the BMS-fast charger handshake flag is 0 and the front MCU high-voltage flag is 0, enter state 155.  While in state 155: 1. If pre-charge failure occurs, move to state 175. If fast charging remains inactive after this, shut down and end the process. 2. If a high-voltage shutdown request (for charging/discharging) is detected (value=2), wait 0.8 seconds before entering state 175. If fast charging is inactive afterward, shut down and end. 3. If the ignition switch status is 2, remain in state 155. If a high-voltage shutdown request (value=2) exists 
- generated_excerpt:
  @startuml start :System starts up; if (charging=1 and front MCU high-voltage detection flag=0?) then (yes)   :Transition to state 153; else (no)   if (BMS-fast charger handshake flag=0 and front MCU high-voltage flag=0?) then (yes)     :Enter state 155;     switch (Condition in state 155?)     case (Pre-charge failure occurs)       :Move to state 175;       if (Fast charging remains inactive?) then (yes)         :Shut down;         end       else (no)       endif     case (High-voltage shutdown request detected (value=2))       :Wait 0.8 seconds;       :Enter state 175;       if (Fast charging is inactive afterward?) then (yes)         :Shut down;         end       else (no)       endif     

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
