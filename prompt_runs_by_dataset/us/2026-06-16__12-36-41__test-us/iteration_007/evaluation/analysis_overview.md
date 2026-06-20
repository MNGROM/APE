# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.5205
- node_recall: 0.4897
- node_f1: 0.5046
- relation_precision: 0.5080
- relation_recall: 0.4647
- relation_f1: 0.4853
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
- missing_activity: 9
- extra_activity: 9
- missing_or_wrong_relation: 9
- extra_or_wrong_relation: 9
- wrong_parallel: 3
- wrong_loop: 2
- syntax_error: 1

## Representative Failure Cases
### fsd-0078
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4444
- relation_f1: 0.3529
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
  - temperature or voltage exceeds threshold?
  - handle communications
  - network signal strength insufficient?
  - sensor reading status
- missing_relations:
  - thermal management controller operates as state machine within hard real-time rtos -> govern multi-zone pwm fans [fork]
  - thermal management controller operates as state machine within hard real-time rtos -> govern liquid-cooling pump loops [fork]
  - govern multi-zone pwm fans -> primary task scheduled with high priority
  - govern liquid-cooling pump loops -> primary task scheduled with high priority
  - primary task scheduled with high priority -> continuously monitor via protected sensor fusion thread
  - continuously monitor via protected sensor fusion thread -> equipment temperature [fork]
  - continuously monitor via protected sensor fusion thread -> rail voltage [fork]
  - equipment temperature -> either parameter > defined threshold?
- input_excerpt:
  Operating as a state machine within a hard real-time RTOS, the thermal management controller governs multi-zone PWM fans and liquid-cooling pump loops. Its primary task, scheduled with high priority, continuously monitors equipment temperature and rail voltage via a protected sensor fusion thread. Should either parameter exceed its defined threshold, the system initiates concurrent mitigation tasks managed through priority queues and mutex-protected shared resources. These include a power management routine that, upon detecting a critical battery state from the BMS or abnormal power consumption, engages exponential backoff retry logic with the PMIC for power optimization. Simultaneously, a c
- generated_excerpt:
  @startuml start repeat :Monitor equipment temperature and rail voltage via protected sensor fusion thread; if (Temperature or voltage exceeds threshold?) then (yes)   fork     :Execute power management routine;     if (Critical battery state from BMS or abnormal power consumption detected?) then (yes)       :Engage exponential backoff retry logic with PMIC for power optimization;     else (no)     endif   fork again     :Handle communications;     if (Network signal strength insufficient?) then (yes)       :Attempt network signal enhancement;     else (no)     endif     :Secure critical commands with CRC checks over CAN bus;   end fork else (no) endif repeat :Run sensor calibration periodica
### lmc-0038
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.3333
- missing_nodes:
  - for equivalent input of (xt yt)
  - absolute error between zt truth data and output z <= 0.01?
  - allowed
  - not allowed
- extra_nodes:
  - compute absolute error between zt truth data and output z for equivalent input (xt yt)
  - absolute error <= 0.01?
  - pass tolerance check
  - fail tolerance check
- missing_relations:
  - absolute error between zt truth data and output z <= 0.01? -> allowed [yes]
  - absolute error between zt truth data and output z <= 0.01? -> not allowed [no]
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Compute absolute error between zt truth data and output z for equivalent input (xt, yt); if (Absolute error <= 0.01?) then (Yes)   :Pass tolerance check; else (No)   :Fail tolerance check; endif stop @enduml
### bp-0004
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1739
- relation_f1: 0.2727
- missing_nodes:
  - open the toolbar on the right
  - choose choose source system
  - choose the menu option file
  - select source system with technical name pc_file
  - the hierarchical tree is displayed
  - open context menu
  - select create application component...
  - enter technical name and description
- extra_nodes:
  - choose source system from toolbar
  - select source system pc_file from file menu
  - select create application component from context menu at root node
  - enter technical name and description for application component
  - choose create data source from context menu of application component
  - choose transfer
  - enter required data on general info tab page
- missing_relations:
  - open the toolbar on the right -> choose choose source system
  - choose choose source system -> choose the menu option file
  - select source system with technical name pc_file -> the hierarchical tree is displayed
  - the hierarchical tree is displayed -> open context menu
  - open context menu -> select create application component...
  - enter technical name and description -> open context menu
  - open context menu -> choose create data source
  - choose create data source -> click transfer
- input_excerpt:
  4.	Creating Transformations0 Creating Transformations for Master Data of Characteristic "Product"1. You are in the Modeling functional area of the Data Warehousing Workbench.2. Choose Data sources.3. From the toolbar in the right screen area, choose Choose Source System.4. In the menu option File, select the source system with the technical name PC_FILE. A hierarchical tree of the Data sources for this source system is displayed. The Data sources are structured semantically by application component. 5. Select Create application component... from the context menu at the root node of the Data source tree.6. On the next screen, enter a technical name and a description for the application compon
- generated_excerpt:
  @startuml start :Choose Data sources; :Choose Source System from toolbar; :Select source system PC_FILE from File menu; :Select Create application component from context menu at root node; :Enter technical name and description for application component; :Choose Create Data source from context menu of application component; :Enter required data; :Choose Transfer; :Enter required data on General Info tab page; stop @enduml
### bp-0006
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3590
- relation_f1: 0.2381
- missing_nodes:
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - attributes
  - texts
  - open data source context menu
- extra_nodes:
  - choose infoprovider in modeling area
  - view attributes and texts with transformation and datasource
  - open context menu of datasource
  - choose create info package
  - enter description for info package
  - choose monitor in toolbar
  - select date on next screen
  - view load process monitor
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation [fork]
  - info area displays information -> data source [fork]
  - info area displays information -> attributes [fork]
  - info area displays information -> texts [fork]
  - transformation -> open data source context menu
- input_excerpt:
  6.	Loading Master Data forCharacteristic "Product"Go to the Data Warehousing Workbench;in the Modeling area choose Info Provider. The attributes and texts are displayed with transformation and Data source in your Info Area below the characteristic Product.3. Perform the following steps, rst for the attributes of the characteristic and then for the texts of the characteristic.4. From the context menu of the Data source, choose Create Info Package...5. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.6. Go to the tab page Schedule and choose Start.7. To check the load process, choose Monitor in the toolb
- generated_excerpt:
  @startuml start :Go to Data Warehousing Workbench; :Choose InfoProvider in Modeling area; :View attributes and texts with transformation and DataSource; repeat   :Open context menu of DataSource;   :Choose Create Info Package;   :Enter description for Info Package;   :Choose Save;   :View Info Package maintenance screen;   :Go to Schedule tab page;   :Choose Start;   :Choose Monitor in toolbar;   :Select date on next screen;   :Choose Execute;   :View load process monitor;   :Select load process from tree; repeat while (For attributes then texts of characteristic?) -> yes; stop @enduml
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4211
- relation_f1: 0.4167
- missing_nodes:
  - switch to state 95
  - condition judgement
  - remote mode is closed
  - shutdown
  - pet mode open request is closed
- extra_nodes:
  - system startup
  - move to state 95
  - proceed to state 105
  - condition?
  - go to state 105
  - slow charging becomes inactive?
  - shift to state 28
  - remote mode deactivates?
- missing_relations:
  - switch to state 93 -> charging/discharging power-up is active and front mcu high-voltage detection flag is 1
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - switch to state 105 -> condition judgement
  - condition judgement -> switch to state 105 [case in remote mode]
  - switch to state 28 -> remote mode is closed
  - switch to state 28 -> pet mode open request is closed
  - pet mode open request is closed -> shutdown [if yes]
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System startup;  if (Slow charging is active and front MCU high-voltage detection flag is 0?) then (Yes)   :Transition to state 93; elseif (Charging/discharging power-up is active and front MCU high-voltage detection flag is 1?) then (Yes)   :Move to state 95; elseif (Power-up readiness is confirmed and vehicle charging/discharging mode is 2?) then (Yes)   :Proceed to state 105; endif  switch (Condition?) case (Remote mode)   :Go to state 105;   if (Slow charging becomes inactive?) then (Yes)     :Shift to state 28;   endif   if (Remote mode deactivates?) then (Yes)     :Initiate shutdown;     :Terminate;     stop   endif case (Pet mode request received)   :Enter state 105; 
### pure-0064
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.4286
- missing_nodes:
  - message is appeared to confirm
  - selection
  - group/subgroup is deleted
  - group/subgroup is not deleted
- extra_nodes:
  - display delete confirmation message
  - user confirmation
  - delete the group/subgroup
  - do not delete the group/subgroup
- missing_relations:
  - message is appeared to confirm -> selection
  - selection -> group/subgroup is deleted [case yes]
  - group/subgroup is deleted -> main window opens
  - selection -> group/subgroup is not deleted [case no]
- input_excerpt:
  1. User opens KeePass and selects a group/subgroup 2. User selects to delete the group/subgroup 3. A message is appeared to confirm the delete 4. User selects yes 5. The group/subgroup is deleted 6. The main window opens 3.8.2.2 Alternative Data Flows 3.8.2.2.1 Alternative Data Flow 1 4. User selects no 5. The group/subgroup is not deleted
- generated_excerpt:
  @startuml start :Open KeePass; :Select a group/subgroup; :Select to delete the group/subgroup; :Display delete confirmation message; switch (User confirmation) case (Yes)   :Delete the group/subgroup;   :Open the main window; case (No)   :Do not delete the group/subgroup; endswitch @enduml
### fsd-0112
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5417
- relation_f1: 0.3824
- missing_nodes:
  - thermal management controller operates as state machine within rtos
  - govern
  - pwm fans
  - liquid-cooling loops
  - initiate concurrent task set
  - spawn two primary threads managed by rtos scheduler using priority queues
  - periodic task for real-time light intensity monitoring
  - coordinated cooling process
- extra_nodes:
  - monitor real-time light intensity
  - periodic rtos task cycle?
  - smart curtain control enabled?
  - determine curtain adjustment execution via mutex-protected decision logic
  - modulate curtain opening degree based on outdoor light intensity
  - execute sensor fusion and calibration routines
  - engage sensor failover redundancy protocol
- missing_relations:
  - thermal management controller operates as state machine within rtos -> govern
  - govern -> pwm fans [fork]
  - govern -> liquid-cooling loops [fork]
  - pwm fans -> user presence detected?
  - liquid-cooling loops -> user presence detected?
  - ambient light sensor reading < preset threshold? -> initiate concurrent task set [yes]
  - initiate concurrent task set -> spawn two primary threads managed by rtos scheduler using priority queues
  - spawn two primary threads managed by rtos scheduler using priority queues -> activate intelligent lighting module [fork]
- input_excerpt:
  Operating as a state machine within a Real-Time Operating System (RTOS), the thermal management controller governs PWM fans and liquid-cooling loops. Upon detecting user presence, the system initiates a concurrent task set if an ambient light sensor reading falls below a preset threshold. This spawns two primary threads managed by the RTOS scheduler using priority queues: one activates the intelligent lighting module, employing a periodic task for real-time light intensity monitoring to dynamically adjust brightness and evaluate night mode based on system time; the other initializes ambient temperature monitoring via a temperature and humidity sensor, where an over-temperature condition trig
- generated_excerpt:
  @startuml start :Detect user presence; if (Ambient light sensor reading below preset threshold?) then (yes)   fork     :Activate intelligent lighting module;     repeat       :Monitor real-time light intensity;       :Dynamically adjust brightness;       :Evaluate night mode based on system time;     repeat while (Periodic RTOS task cycle?)   fork again     :Initialize ambient temperature monitoring via temperature and humidity sensor;     if (Over-temperature condition detected?) then (yes)       :Trigger intelligent air conditioning system via CAN message;     else (no)     endif   end fork endif :Assess user intent for smart curtain control; if (Smart curtain control enabled?) then (yes) 
### rac-0001
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.6154
- missing_nodes:
  - initial judgement
  - switch to new state
  - query cumulative discharge distance
  - set instantaneous driving mileage gradient = cumulative discharge distance * driving error correction coefficient /2
  - switch to another state
- extra_nodes:
  - check vehicle status value
  - status > 9 and 30 and <= 49?
  - status
  - transition to new state
  - transition to another state
  - move to new state
  - get cumulative discharge distance via call()
  - calculate gradient as (cumulative discharge distance * driving error correction coefficient / 2)
- missing_relations:
  - initial judgement -> switch to new state [case vehicle status == 28 or 29 or 30]
  - current > -current threshold a and < current threshold a -> vehicle speed > speed threshold (kph) [else if]
  - vehicle speed > speed threshold (kph) -> switch to new state [yes]
  - energy recovery mileage >1 -> switch to new state [if yes]
  - current > -current threshold a and < current threshold a -> cumulative discharge distance < energy recovery mileage [else if]
  - query cumulative discharge distance -> cumulative discharge distance >0.1?
  - switch to new state -> set instantaneous driving mileage gradient = cumulative discharge distance * driving error correction coefficient /2
  - current > -current threshold a and < current threshold a -> instantaneous discharge mileage > instantaneous driving mileage? [if no]
- input_excerpt:
  Once the system starts up, it checks the vehicle's status value first.  If the status is greater than 9 but less than 28, or greater than 30 but 49 or less, the system sets the instantaneous driving mileage gradient to 0 and ends.  For a status of 28, 29, or 30, the system transitions to a new state and sets the instantaneous driving mileage to 10. After this state change, it performs additional checks:  *   If the current stays between -Current Threshold A and Current Threshold A, the system sets the instantaneous driving mileage gradient to 0 and ends. *   If the vehicle speed exceeds the speed threshold (kph), the system enters a new state and resets the cumulative discharge distance to 0
- generated_excerpt:
  @startuml start :Check vehicle status value; if (Status > 9 and < 28, or > 30 and <= 49?) then (yes)   :Set instantaneous driving mileage gradient to 0;   end else (no)   switch (Status)   case ( 28, 29, or 30 )     :Transition to new state;     :Set instantaneous driving mileage to 10;     if (Current between -Current Threshold A and Current Threshold A?) then (yes)       :Set instantaneous driving mileage gradient to 0;       end     else (no)       if (Vehicle speed exceeds speed threshold (kph)?) then (yes)         :Enter new state;         :Reset cumulative discharge distance to 0;         if (Energy recovery mileage exceeds 1?) then (yes)           :Transition to another state;        

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
