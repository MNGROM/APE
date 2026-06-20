# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.6004
- node_recall: 0.5103
- node_f1: 0.5517
- relation_precision: 0.3488
- relation_recall: 0.3301
- relation_f1: 0.3392
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
- extra_or_wrong_relation: 10
- extra_activity: 9
- missing_or_wrong_relation: 8
- wrong_parallel: 6
- wrong_loop: 2

## Representative Failure Cases
### bp-0030
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2143
- relation_f1: 0.0000
- missing_nodes:
  - log in
  - go to promotion jobs
  - new job window appears
  - enter name
  - enter description
  - enter keywords
  - go to save job field
  - drop-lists appears
- extra_nodes:
  - log into lifecycle manager
  - enter name description and keywords
  - select source and destination systems
  - system name displayed in drop-down list?
  - click login to a new cms option
  - enter system name user name and password
- missing_relations:
  - log in -> go to promotion jobs
  - go to promotion jobs -> click new job
  - click new job -> new job window appears
  - new job window appears -> enter name [fork]
  - new job window appears -> enter description [fork]
  - new job window appears -> enter keywords [fork]
  - enter name -> go to save job field
  - enter description -> go to save job field
- input_excerpt:
  30.	Creating a New Job1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriate fields.4. In the Save Job in field, browse and select the folder in which you want to save the job.5. Select the source system and the destination system from the drop-down lists. If the name of the system is not displayed in the drop-down list, click the Login to a new CMS option. A new window is launched. Enter the name of the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into LifeCycle Manager; :Click New Job; :Enter name, description, and keywords; :Browse and select folder; :Select source and destination systems; if (System name displayed in drop-down list?) then (No)   :Click Login to a new CMS option;   :Enter system name, user name, and password; else (Yes) endif :Click Create; @enduml
### lmc-0007
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
  - change autopilot state to transition
  - system is supported and sensor data is good?
- missing_relations:
  - system is supported? -> sensor data is good? [yes]
  - sensor data is good? -> autopilot change states from transition to nominal [yes]
- input_excerpt:
  3.	The autopilot shall change states from TRANSITION to NOMINAL when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml start :Change autopilot state to TRANSITION; if (System is supported and sensor data is good?) then (yes)   :Change autopilot state to NOMINAL; else (no) endif stop @enduml
### fsd-0031
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4286
- relation_f1: 0.2222
- missing_nodes:
  - supervisory network stack initializes
  - prerequisites satisfied?
  - under fixed-priority preemptive model
  - deterministic multi-threaded scheduler within rtos launches concurrent tasks
  - high-priority periodic task
  - continuous device status monitoring managed by watchdog
  - parallel threads for ring buffer management
  - parallel threads for network communication
- extra_nodes:
  - environmental conditions met?
  - interface connectivity verified?
  - monitor device status
  - watchdog timer expired?
  - manage ring buffer
  - execute network communication
  - dispatch telemetry data to cloud server
  - transmission fault and bounded retries remaining?
- missing_relations:
  - supervisory network stack initializes -> validate external environmental conditions meet operating specifications
  - validate external environmental conditions meet operating specifications -> check device interface connectivity
  - check device interface connectivity -> prerequisites satisfied?
  - prerequisites satisfied? -> verify sensor data validity via crc check [yes]
  - initialize data acquisition module -> under fixed-priority preemptive model
  - under fixed-priority preemptive model -> deterministic multi-threaded scheduler within rtos launches concurrent tasks
  - deterministic multi-threaded scheduler within rtos launches concurrent tasks -> high-priority periodic task [fork]
  - high-priority periodic task -> continuous device status monitoring managed by watchdog
- input_excerpt:
  Upon system initialization, the supervisory network stack, employing exponential backoff, keep-alive heartbeats, and link-state monitoring, first validates that external environmental conditions meet operating specifications before checking device interface connectivity. If these prerequisites are satisfied, the system verifies sensor data validity via a CRC check before initializing the data acquisition module. Subsequently, a deterministic, multi-threaded scheduler within the RTOS launches concurrent tasks under a fixed-priority preemptive model. These tasks include a high-priority periodic task for continuous device status monitoring, managed by a watchdog, alongside other parallel thread
- generated_excerpt:
  @startuml start :Validate external environmental conditions; if (Environmental conditions met?) then (yes)   :Check device interface connectivity; else (no)   stop endif if (Interface connectivity verified?) then (yes)   :Verify sensor data validity via CRC check;   :Initialize data acquisition module; else (no)   stop endif :Initialize network module; fork   repeat     :Monitor device status;   repeat while (Watchdog timer expired?) is (no) not (yes) fork again   :Manage ring buffer; fork again   :Execute network communication; end fork fork   repeat     :Dispatch telemetry data to cloud server;   repeat while (Transmission fault and bounded retries remaining?) is (yes) not (no) fork again 
### fsd-0022
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4490
- relation_f1: 0.1875
- missing_nodes:
  - thermal management controller implemented as state machine on rtos
  - regulate pwm fans
  - regulate liquid-cooling loop
  - initiate primary control logic
  - trigger conditional verification sequence
  - charging current within safe range?
  - battery temperature < upper limit?
  - battery health status confirmed good?
- extra_nodes:
  - initiate control logic
  - charging current within safe range? battery temperature below upper limit? battery health status good?
  - spawn charging task (higher priority)
  - monitor battery rail voltage
  - monitor battery temperature
  - charging task iteration condition?
  - spawn discharge task
  - discharge task iteration condition?
- missing_relations:
  - thermal management controller implemented as state machine on rtos -> regulate pwm fans [fork]
  - thermal management controller implemented as state machine on rtos -> regulate liquid-cooling loop [fork]
  - regulate pwm fans -> battery rail voltage < threshold?
  - regulate liquid-cooling loop -> battery rail voltage < threshold?
  - initiate primary control logic -> trigger conditional verification sequence
  - trigger conditional verification sequence -> charging current within safe range?
  - charging current within safe range? -> battery temperature < upper limit? [yes]
  - battery temperature < upper limit? -> battery health status confirmed good? [yes]
- input_excerpt:
  The thermal management controller, implemented as a state machine on the RTOS, regulates PWM fans and liquid-cooling loops. Its primary control logic is initiated when the battery rail voltage falls below a set threshold, triggering a conditional sequence to verify the charging current is within a safe range, the battery temperature is below its upper limit, and the battery health status is confirmed as good. Upon passing these checks, the system spawns concurrent RTOS tasks for charge and discharge cycles. The charging task, initialized with a higher priority, iteratively monitors the battery rail voltage and temperature, while the discharge task monitors output power. These tasks are synch
- generated_excerpt:
  @startuml start :Initiate control logic; if (Battery rail voltage below threshold?) then (yes)   if (Charging current within safe range?\nBattery temperature below upper limit?\nBattery health status good?) then (yes)     fork       :Spawn charging task (higher priority);       repeat         :Monitor battery rail voltage;         :Monitor battery temperature;       repeat while (Charging task iteration condition?)       fork again         :Spawn discharge task;         repeat           :Monitor output power;         repeat while (Discharge task iteration condition?)     end fork     :Synchronize tasks;     repeat       if (Rail voltage remains below threshold?) then (yes)         :Restart t
### bp-0003
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4889
- relation_f1: 0.5600
- missing_nodes:
  - info provider tree is displayed
  - the info area is displayed
  - open context menu
  - enter sales overview as the description
  - screen for info cube editing is shown
  - enter product as the new dimension description
  - enter sales organization as the next dimension description
  - dimensions are inserted
- extra_nodes:
  - navigate to modeling functional area
  - choose info provider
  - open context menu of info area
  - open context menu of dimensions folder
  - enter description product
  - enter description sales organization
  - choose info object catalog in toolbar
  - assign characteristics to dimensions via drag and drop
- missing_relations:
  - info provider tree is displayed -> the info area is displayed
  - choose create info cube -> enter zd_sales as the technical name [fork]
  - choose create info cube -> enter sales overview as the description [fork]
  - enter sales overview as the description -> select standard info cube as info provider type
  - choose create -> screen for info cube editing is shown
  - screen for info cube editing is shown -> open context menu
  - enter sales organization as the next dimension description -> choose continue
  - choose continue -> dimensions are inserted
- input_excerpt:
  3.	Creating Data sources for Master Data of Characteristic "Product"1. You are in the Modeling functional area of the Data Warehousing Workbench2. Choose Info Provider. The Info Provider tree is displayed. The Info Area created previously in the Info Object tree is also displayed in the Info Provider tree. It contains the characteristics that were dened as Info Provider and is used to group further objects.3. In the context menu of the Info Area, choose Create Info Cube.4. In the next screen, enter ZD_SALES as the technical name under Info Cube and Sales Overview as the description.5. Select Standard Info Cube as Info Provider Type and choose Create. You go to the screen for Info Cube editin
- generated_excerpt:
  @startuml start :Navigate to Modeling functional area; :Choose Info Provider; :Open context menu of Info Area; :Select Create Info Cube; :Enter technical name ZD_SALES and description Sales Overview; :Select Standard Info Cube as Info Provider Type; :Choose Create; :Open context menu of Dimensions folder; :Select Create New Dimensions; :Enter description Product; :Choose Create Another Dimension; :Enter description Sales Organization; :Choose Continue; :Choose Info Object Catalog in toolbar; :Select Info Object catalog for characteristics as template; :Choose Continue; :Assign characteristics to dimensions via drag and drop; :Open context menu of dimension Sales Organization; :Select Info Ob
### rac-0011
- dataset: rac
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6486
- relation_f1: 0.7018
- missing_nodes:
  - enter power-up mode
  - ac charging system fault=1
  - shutdown
  - high-voltage shutdown request charging/discharging is 2
  - high-voltage shutdown request charging/discharging is 2 and bms counter=2
  - switch to state 105
- extra_nodes:
  - start up
  - enter power-up state
  - condition?
  - enter state 82
  - shut down
  - enter state 105
  - enter state 127
- missing_relations:
  - enter power-up mode -> ac charging system fault=1
  - ac charging system fault=1 -> high-voltage shutdown request charging/discharging is 2 [else if]
  - high-voltage shutdown request charging/discharging is 2 -> switch to state 126 [if yes]
  - ac charging system fault=1 -> high-voltage shutdown request charging/discharging is 2 and bms counter=2 [else if]
  - high-voltage shutdown request charging/discharging is 2 and bms counter=2 -> switch to state 126 [if yes]
- input_excerpt:
  After the system starts up, the following logic applies:  1. If slow charging is active, the system enters the "power-up" state. Then:    a. When the AC charging system fault is 1, the system switches to state 127. If recharge demand is 1 and front MCU initialization state is 0, it enters state 82. Should slow charging become inactive at any point, the system shuts down and ends.    b. If a high-voltage shutdown request (for charging/discharging) is 2, the system switches to state 126. When recharge demand is 1 and the front MCU low-voltage shutdown flag is 0, it enters state 127. If the front MCU low-voltage flag becomes 1 or a 2.2-second timeout occurs, it switches to state 82. Should slow
- generated_excerpt:
  @startuml start :Start up; if (Slow charging active?) then (yes)   :Enter "power-up" state;   switch (Condition?)   case (AC charging system fault is 1)     :Switch to state 127;     if (Recharge demand is 1 and front MCU initialization state is 0?) then (yes)       :Enter state 82;     endif   case (High-voltage shutdown request is 2)     :Switch to state 126;     if (Recharge demand is 1 and front MCU low-voltage shutdown flag is 0?) then (yes)       :Switch to state 127;     endif     if (Front MCU low-voltage flag becomes 1 or 2.2-second timeout occurs?) then (yes)       :Switch to state 82;     endif   case (High-voltage shutdown request is 2 and BMS counter is 2)     :Switch to state 1
### pure-0051
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.4615
- missing_nodes:
  - display inventory departments
  - see view inventory
  - current inventory item information
  - historical inventory item information
- extra_nodes:
  - display inventory departments in matrix format
- missing_relations:
  - access main inventory screen -> display inventory departments
  - display inventory departments -> see view inventory
  - see view inventory -> drill down to desired existing inventory item
  - display item history screen -> current inventory item information [fork]
  - display item history screen -> historical inventory item information [fork]
- input_excerpt:
  4. View Inventory Item History 4.1. User accesses the main inventory screen 4.2. The screen displays all inventory departments in matrix format 4.3. User drills down to the desired existing inventory item (see View Inventory) 4.4. The item detail screen is presented 4.5. User clicks the Item History button 4.6. The system displays the Item History screen containing current and historical information about the inventory item
- generated_excerpt:
  @startuml start :Access main inventory screen; :Display inventory departments in matrix format; :Drill down to desired existing inventory item; :Present item detail screen; :Click Item History button; :Display Item History screen with current and historical information; @enduml
### rac-0009
- dataset: rac
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7059
- relation_f1: 0.8276
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2
  - condition judgement
  - shutdown
  - command becomes 4
- extra_nodes:
  - system starts up
  - high-voltage shutdown request == 2?
  - condition evaluation
  - shut down
  - slow charging inactive and bms self-check counter == 1?
  - onboard charger command == 4?
- missing_relations:
  - stay in state 127 -> command becomes 4
  - command becomes 4 -> switch to state 12 [yes]
- input_excerpt:
  After the system starts up, if slow charging is active, it enters power-up mode. Then, if the high-voltage shutdown request (for charging or discharging) is set to 2, it switches to state 127. Once in state 127, the following actions apply based on conditions:  1. If the ignition switch is at position 2 and the front MCU state remains unchanged, the system stays in state 127.    a. Should slow charging become inactive and a timeout of 2.2 seconds occur, it switches to state 12. If the ignition switch is off at this point, the system shuts down and ends.    b. Similarly, if slow charging is inactive and the BMS self-check counter reads 1, it switches to state 12. Again, if the ignition switch
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging active?) then (yes)   :Enter power-up mode;   if (High-voltage shutdown request == 2?) then (yes)     :Switch to state 127;     switch (Condition evaluation)     case (Ignition switch at position 2 and front MCU state unchanged)       :Stay in state 127;       if (Slow charging inactive and timeout of 2.2 seconds?) then (yes)         :Switch to state 12;         if (Ignition switch off?) then (yes)           :Shut down;           end         endif       elseif (Slow charging inactive and BMS self-check counter == 1?) then (yes)         :Switch to state 12;         if (Ignition switch off?) then (yes)           :Shut down;           end    

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
