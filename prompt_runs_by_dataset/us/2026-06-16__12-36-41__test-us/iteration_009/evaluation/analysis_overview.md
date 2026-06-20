# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.5156
- node_recall: 0.5087
- node_f1: 0.5122
- relation_precision: 0.3515
- relation_recall: 0.3146
- relation_f1: 0.3320
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
- missing_or_wrong_relation: 9
- extra_or_wrong_relation: 9
- wrong_parallel: 4
- wrong_loop: 2

## Representative Failure Cases
### lmc-0040
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.0000
- missing_nodes:
  - determinant of b(inv(wp )b > 1e-12
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - b(inv(wp )b matrix inversion be accurate to 12 digits precision
- extra_nodes:
  - check determinant of b(inv(wp ))b
  - determinant > 1e-12?
  - invert b(inv(wp ))b matrix
  - compute check output matrix
  - verify each element of check output matrix is within 1e-12 tolerance of 3x3 identity matrix
- missing_relations:
  - ridge_on set to false -> determinant of b(inv(wp )b > 1e-12
  - determinant of b(inv(wp )b > 1e-12 -> each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance -> b(inv(wp )b matrix inversion be accurate to 12 digits precision
- input_excerpt:
  2.	When the determinant of B(inv(Wp’)B’ is > 1e-12 as indicated by ridge_on set to False, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 12 digits precision in that each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  @startuml start :Check determinant of B(inv(Wp'))B'; if (Determinant > 1e-12?) then (Yes)   :Set ridge_on to False;   :Invert B(inv(Wp'))B' matrix;   :Compute check output matrix;   :Verify each element of check output matrix is within 1e-12 tolerance of 3x3 identity matrix; else (No) endif stop @enduml
### bp-0002
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.3158
- missing_nodes:
  - log in
  - choose modeling data warehousing workbench modeling
  - open root node context menu
  - choose create info area
  - enter a technical name
  - enter a description
  - info area is displayed
  - open info area context menu
- extra_nodes:
  - log onto the bi system
  - choose create info area from context menu at root node
  - enter technical name and description for info area
  - display info area in info object tree
  - choose create info object catalog from info area context menu
  - enter technical name and description
  - select key figure as info object type
  - create next key figure for revenue quantity price?
- missing_relations:
  - user authorizations are sufficient? -> log in [yes]
  - log in -> choose modeling data warehousing workbench modeling
  - choose modeling data warehousing workbench modeling -> data warehousing workbench is started
  - info object tree is displayed -> open root node context menu
  - open root node context menu -> choose create info area
  - choose create info area -> enter a technical name [fork]
  - choose create info area -> enter a description [fork]
  - enter a technical name -> info area is displayed
- input_excerpt:
  2.	Log onto the BI system1.	Log onto the BI system with a user that has sufficient authorizations for executing the scenario.2.	Start the Data Warehousing Workbench in the SAP menu by choosing Modeling Data Warehousing Workbench: Modeling.3.	Under Modeling, choose Info  Objects. The Info  Object tree is displayed.4.	From the context menu at the root node Info Objects of the Info Object tree, choose Create Info Area.5.	On the next screen, enter a technical name and a description for the Info Area. The Info Area is displayed in the Info Object tree.6.	It is used to group your Info Objects.7.	In the context menu of the Info Area, choose Create Info Object Catalog.8.	On the next screen, enter a 
- generated_excerpt:
  @startuml start :Log onto the BI system; if (User has sufficient authorizations?) then (yes)   :Start Data Warehousing Workbench;   :Choose Info Objects;   :Display Info Object tree;   :Choose Create Info Area from context menu at root node;   :Enter technical name and description for Info Area;   :Display Info Area in Info Object tree;   repeat     :Choose Create Info Object Catalog from Info Area context menu;     :Enter technical name and description;     :Select Key Figure as Info Object Type;     :Create Info Object catalog;     :Activate Info Object catalog;     :Display Info Object catalog in Info Area;   repeat while (Create next key figure for Revenue, Quantity, Price?) is (yes)   -
### bp-0009
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4211
- relation_f1: 0.2353
- missing_nodes:
  - choose start programs business explorer web application designer
  - bex web is started
  - log in
  - initial screen is shown
  - open data provider type dialog box
  - select query
  - data provider is displayed
- extra_nodes:
  - start bex web application designer
  - log onto bi system
  - select query as data provider type
  - display data provider in layout view
- missing_relations:
  - choose start programs business explorer web application designer -> bex web is started
  - bex web is started -> log in
  - log in -> initial screen is shown
  - initial screen is shown -> click create new blank web template
  - choose new data provider -> open data provider type dialog box
  - open data provider type dialog box -> select query
  - select query -> enter zd_sales_2007 as query name
  - choose ok -> data provider is displayed
- input_excerpt:
  9.	Creating Web Applications1. Start the BEx Web application by choosing Start Programs Business Explorer Web Application Designer.2. Log onto the BI system.3. In the initial screen of the Web Application Designer, click on the link Create New Blank Web Template.4. In the lower part of the layout view choose New Data Provider.5. In the dialog box for the data provider type select Query and enter the name of the query ZD_SALES_2007 in the eld following Query.6. Choose OK.7. The data provider is displayed in the lower part of the layout view in the Web Application Designer
- generated_excerpt:
  @startuml start :Start BEx Web Application Designer; :Log onto BI system; :Click Create New Blank Web Template; :Choose New Data Provider; :Select Query as data provider type; :Enter query name ZD_SALES_2007; :Choose OK; :Display data provider in layout view; @enduml
### fsd-0078
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4324
- relation_f1: 0.3396
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
  - retry successful?
  - execute communications handler
  - sensor selection
  - continuously cycle?
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
  @startuml start  repeat :Monitor equipment temperature and rail voltage via protected sensor fusion thread;  if (Temperature or voltage exceeds threshold?) then (yes)   fork     :Execute power management routine;     if (Critical battery state from BMS or abnormal power consumption detected?) then (yes)       repeat :Engage exponential backoff retry logic with PMIC for power optimization;       repeat while (Retry successful?)     else (no)     endif   fork again     :Execute communications handler;     if (Signal strength is insufficient?) then (yes)       :Attempt network signal enhancement;     else (no)     endif     :Secure critical commands with CRC checks over CAN bus;   end fork else
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4571
- relation_f1: 0.4000
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
  - operating condition?
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
  - condition judgement -> switch to state 105 [case pet mode request is received]
  - switch to state 28 -> pet mode open request is closed
  - pet mode open request is closed -> shutdown [if yes]
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System startup;  if (Slow charging is active and front MCU high-voltage detection flag is 0?) then (Yes)   :Transition to state 93; elseif (Charging/discharging power-up is active and front MCU high-voltage detection flag is 1?) then (Yes)   :Move to state 95; elseif (Power-up readiness is confirmed and vehicle charging/discharging mode is 2?) then (Yes)   :Proceed to state 105; endif  switch (Operating condition?) case (Remote mode)   :Go to state 105;   if (Slow charging becomes inactive?) then (Yes)     :Shift to state 28;   endif   if (Remote mode deactivates?) then (Yes)     :Initiate shutdown;     stop   endif case (Pet mode request received)   :Enter state 105;   if (
### rac-0002
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3077
- missing_nodes:
  - gear is s
  - gear check
- extra_nodes:
  - check gear position
  - end sequence
  - gear in s?
  - calculate d_s gear mileage parameter as s gear nominal mileage divided by d gear nominal mileage
  - conclude process
  - continue process
  - gear in d or e?
  - end
- missing_relations:
  - gear is d or n -> gear is s [else if]
  - switch to driving mode -> gear check
  - gear check -> set d_s gear mileage parameter = s gear nominal mileage / d gear nominal mileage [case gear is d or e]
  - gear check -> observe using d_s gear mileage parameter [case gear is n or r]
- input_excerpt:
  After the system starts up, the process begins by checking the gear position. If the gear is in D or N, the D_S gear mileage parameter is set to 1, and the sequence ends. If the gear is in S, the D_S gear mileage parameter is calculated as S gear nominal mileage divided by D gear nominal mileage, then the process concludes. Additionally, if the vehicle status is 30, switch to driving mode. Next, if the gear is in D or E, set the D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage, and end. Finally, if the gear is in N or R, observe using the D_S gear mileage parameter and terminate the process.
- generated_excerpt:
  @startuml start :Check gear position; if (Gear in D or N?) then (yes)   :Set D_S gear mileage parameter to 1;   :End sequence; else (no)   if (Gear in S?) then (yes)     :Calculate D_S gear mileage parameter as S gear nominal mileage divided by D gear nominal mileage;     :Conclude process;   else (no)     :Continue process;   endif endif if (Vehicle status is 30?) then (yes)   :Switch to driving mode; else (no) endif if (Gear in D or E?) then (yes)   :Set D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage;   :End; else (no)   if (Gear in N or R?) then (yes)     :Observe using D_S gear mileage parameter;     :Terminate process;   else (no)   endif endif st
### fsd-0111
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5185
- relation_f1: 0.3056
- missing_nodes:
  - govern multi-stage cooling strategy for
  - pwm fans
  - liquid-cooling loops
  - trigger temperature regulation state
  - high-priority task activates forced-air cooling via pwm fans
  - > critical threshold?
  - initiate via protected can command
  - air conditioning compressor
- extra_nodes:
  - read ambient temperature from sensor fusion routine
  - enter temperature regulation state
  - activate forced-air cooling via pwm fans
  - exceeds critical threshold?
  - initiate air conditioning compressor via protected can command
  - initiate liquid cooling pump via protected can command
  - verify operational status of all thermal control devices via separate monitoring task with mutex-protected sensor data access
  - transmit system status via ring buffer from timer isr telemetry monitor
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern multi-stage cooling strategy for
  - govern multi-stage cooling strategy for -> pwm fans [fork]
  - govern multi-stage cooling strategy for -> liquid-cooling loops [fork]
  - pwm fans -> out-of-range ambient temperature reading?
  - liquid-cooling loops -> out-of-range ambient temperature reading?
  - > critical threshold? -> initiate via protected can command [yes]
  - initiate via protected can command -> air conditioning compressor [fork]
  - initiate via protected can command -> liquid cooling pump [fork]
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing a multi-stage cooling strategy for PWM fans and liquid-cooling loops. An out-of-range ambient temperature reading from the sensor fusion routine triggers the temperature regulation state. If the temperature continues to rise, a high-priority task activates forced-air cooling via the PWM fans. Upon exceeding a critical threshold, the system concurrently initiates the air conditioning compressor and liquid cooling pump via a protected CAN command, with a watchdog monitoring the response. This aggressive cooling phase employs a closed-loop control that cyclically adjusts the fan duty cycle until the temperature
- generated_excerpt:
  @startuml start :Execute thermal management state machine on RTOS; :Read ambient temperature from sensor fusion routine; if (Ambient temperature out-of-range?) then (yes)   :Enter temperature regulation state;   if (Temperature continues to rise?) then (yes)     :Activate forced-air cooling via PWM fans;     if (Exceeds critical threshold?) then (yes)       fork         :Initiate air conditioning compressor via protected CAN command;       fork again         :Initiate liquid cooling pump via protected CAN command;       end fork       :Monitor response via watchdog;       repeat         :Cyclically adjust fan duty cycle;       repeat while (Temperature re-enters safe operating envelope?) is 
### lmc-0034
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.4000
- missing_nodes:
  - in nlguidance
  - define in-plane navigation
- extra_nodes:
  - output equivalent altitude for in-plane navigation
- missing_relations:
  - in nlguidance -> target = vehicle altitude?
  - target = vehicle altitude? -> define in-plane navigation [yes]
- input_excerpt:
  7.	NLGuidance shall output the equivalent altitude of the vehicle for in-plane navigation.  In-plane navigation is defined where the target and the vehicle altitude (3rd component in the input inertial position vectors) are equal.
- generated_excerpt:
  @startuml start :Output equivalent altitude for in-plane navigation; if (Target altitude equals vehicle altitude?) then (yes)   :Output equivalent altitude of vehicle; else (no) endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
