# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.5200
- node_recall: 0.4449
- node_f1: 0.4795
- relation_precision: 0.2633
- relation_recall: 0.2131
- relation_f1: 0.2356
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
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10
- extra_activity: 8
- wrong_parallel: 4
- wrong_loop: 3

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
  - the caiso documents cranking paths and provides them to wecc upon request
  - the caiso evaluates diverse fuel resources cranking paths communication unit capabilities and coordination with neighboring plans
  - the planning process is coordinated with transmission owners and neighboring balancing authorities
  - the caiso annually enters into rmr and interim black start contracts with qualified generators
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
  @startuml start :The CAISO determines the amount and location of Black Start Generation through contingency studies; :The CAISO annually verifies the number, size, availability, and location of Black Start units; :The CAISO documents Cranking Paths and provides them to WECC upon request; :The CAISO evaluates diverse fuel resources, cranking paths, communication, unit capabilities, and coordination with neighboring plans; :The planning process is coordinated with transmission owners and neighboring Balancing Authorities; :The CAISO annually enters into RMR and Interim Black Start Contracts with qualified generators; stop @enduml
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2727
- relation_f1: 0.1481
- missing_nodes:
  - go to administration options window
  - click manage syetems
  - list is displayed
  - host names
  - port numbers
  - display names
  - descriptions
  - add information
- extra_nodes:
  - click manage systems
  - the list of host names port numbers display names and descriptions is displayed
  - add the host name port number display name and the description in the appropriate fields
  - click add to add the system
- missing_relations:
  - go to administration options window -> click manage syetems
  - click manage syetems -> list is displayed
  - list is displayed -> host names [fork]
  - list is displayed -> port numbers [fork]
  - list is displayed -> display names [fork]
  - list is displayed -> descriptions [fork]
  - host names -> click add
  - port numbers -> click add
- input_excerpt:
  15.	use the Manage Systems optionTo add a host system, complete the following steps:1. In the "Administration Options" window, click Manage Systems.The list of host names, port numbers, display names, and descriptions isdisplayed.2. Click Add.The "Add System" dialog box appears.3. Add the host name, port number, display name, and the description inthe appropriate fields.4. Click Add to add the system.The host system is added to the list.
- generated_excerpt:
  @startuml start :Click Manage Systems; :The list of host names, port numbers, display names, and descriptions is displayed; :Click Add; :The "Add System" dialog box appears; :Add the host name, port number, display name, and the description in the appropriate fields; :Click Add to add the system; :The host system is added to the list; stop @enduml
### rac-0013
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2745
- relation_f1: 0.1231
- missing_nodes:
  - condtion judgement
  - stay in state 155
  - dcdc state 1 or 3s elapsed
  - shutdown
  - eas state 1 or 3s elapsed
  - current<6.1 or 3s elapsed
- extra_nodes:
  - dcdc state monitoring
  - shut down
  - transition to state 156
  - dcdc state is not 1 or 3 seconds pass?
  - move to state 157
  - dcdc state remains 1
  - remain in state 155 for dcdc monitoring
  - eas state monitoring
- missing_relations:
  - enter state 155 -> condtion judgement
  - condtion judgement -> stay in state 155 [case dcdc state=1]
  - stay in state 155 -> bms-fast charger handshake flag=1
  - switch to state 156 -> dcdc state 1 or 3s elapsed
  - dcdc state 1 or 3s elapsed -> switch to state 157 [yes]
  - switch to state 157 -> fast charging is inactive
  - condtion judgement -> stay in state 155 [case eas state=1]
  - switch to state 156 -> eas state 1 or 3s elapsed
- input_excerpt:
  After the system starts up: if fast charging is active and the BMS manual charging/discharging flag is 0, the system enters state 155. While in state 155:  1. For DCDC state monitoring:    - If DCDC state remains 1, stay in state 155.    - If the BMS-fast charger handshake flag becomes 1, transition to state 156.    - If DCDC state is not 1 or 3 seconds pass, move to state 157.    - If fast charging becomes inactive at any point, shut down and end the process.  2. For EAS state monitoring:    - If EAS state stays at 1, remain in state 155.    - If the handshake flag turns to 1, switch to state 156.    - If EAS state isn’t 1 or 3 seconds elapse, shift to state 157.    - Should fast charging d
- generated_excerpt:
  @startuml start :Fast charging is active and BMS manual charging/discharging flag is 0; :Enter state 155; fork   :DCDC state monitoring;   repeat     if (Fast charging inactive?) then (yes)       :Shut down;       stop     elseif (BMS-fast charger handshake flag becomes 1?) then (yes)       :Transition to state 156;       stop     elseif (DCDC state is not 1 or 3 seconds pass?) then (yes)       :Move to state 157;       stop     else (no)       :DCDC state remains 1;     endif   repeat while (Remain in state 155 for DCDC monitoring) is (yes)   ->no; fork again   :EAS state monitoring;   repeat     if (Fast charging inactive?) then (yes)       :Shut down;       stop     elseif (Handshake flag
### lmc-0030
- dataset: lmc
- failure_types: missing_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.0000
- missing_nodes:
  - in nlguidance
  - vector define location at standoff 2 with offset from target position?
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point?
  - compute the vector
- missing_relations:
  - in nlguidance -> vector define location at standoff 2 with offset from target position?
  - vector define location at standoff 2 with offset from target position? -> it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? [yes]
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? -> it is inertial position vector for aim point 2 [yes]
  - it is inertial position vector for aim point 2 -> compute the vector
- input_excerpt:
  3.	NLGuidance shall compute the inertial position vector for aim point 2, defining the location at Standoff 2 with an offset from the target position, and oriented on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point.
- generated_excerpt:
  @startuml start :Compute the inertial position vector for aim point 2; note right   Defining the location at Standoff 2   with an offset from the target position,   and oriented on a vector perpendicular   to the tangent relative position vector   from the vehicle to the corresponding aim point. end note stop @enduml
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3889
- relation_f1: 0.3684
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - click manage dependencies
  - list of infoobjects and their dependents is displayed
  - open select dependents drop-down list
  - selection
  - dependents are not selected
- extra_nodes:
  - in the promotion jobs home page click manage dependencies
  - from the select dependents drop-down list select any of the options available to add the dependents to the job
  - explicitly select the dependents you want to promote
  - select an option and click ok
  - click apply changes to update the list of dependents
  - click apply changes and close to save the changes
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37 [yes]
  - see creating a new job on page 37 -> add required infoobjects to new job
  - click manage dependencies -> manage dependencies window appears
  - manage dependencies window appears -> list of infoobjects and their dependents is displayed
  - list of infoobjects and their dependents is displayed -> open select dependents drop-down list
  - open select dependents drop-down list -> dependents are displayed on the right
  - dependents are displayed on the right -> selection
- input_excerpt:
  22.	manage dependencies of an infoobject1. Log into the LifeCycle Manager tool.2. Create a new job. For information on creating a new job, see Creating aNew Job on page 37.3. Add the required infoobjects to the new job.4. In the "Promotion Jobs" home page, click Manage Dependencies. The "Manage Dependencies" window appears. This window displays the list of infoobjects and their dependents, as shown in the following figure:5. From the Select Dependents drop-down list, select any of the options available to add the dependents to the job. The dependents are displayed on the right side. The dependents are not selected by default; you must explicitly select the dependents you want to promote. For
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :In the "Promotion Jobs" home page, click Manage Dependencies; :The "Manage Dependencies" window appears; :From the Select Dependents drop-down list, select any of the options available to add the dependents to the job; :The dependents are displayed on the right side; :Explicitly select the dependents you want to promote; :Click to view the supported filtering options of infoobjects in the drop-down list; :Select an option, and click OK; :The filtered infoobjects are displayed; :Click Apply Changes to update the list of dependents; :Click Apply Changes and Close to save the 
### fsd-0111
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4082
- relation_f1: 0.2857
- missing_nodes:
  - thermal management controller executes as state machine on rtos
  - govern multi-stage cooling strategy for
  - pwm fans
  - liquid-cooling loops
  - out-of-range ambient temperature reading?
  - trigger temperature regulation state
  - high-priority task activates forced-air cooling via pwm fans
  - > critical threshold?
- extra_nodes:
  - out-of-range ambient temperature reading triggers temperature regulation state
  - activate forced-air cooling via pwm fans
  - exceeds critical threshold?
  - initiate air conditioning compressor via protected can command
  - initiate liquid cooling pump via protected can command
  - persistent low-temperature condition initializes heater circuit
  - monitoring task verifies operational status of all thermal control devices (mutex-protected access to sensor data)
  - telemetry monitor transmits system status via ring buffer (timer isr)
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern multi-stage cooling strategy for
  - govern multi-stage cooling strategy for -> pwm fans [fork]
  - govern multi-stage cooling strategy for -> liquid-cooling loops [fork]
  - pwm fans -> out-of-range ambient temperature reading?
  - liquid-cooling loops -> out-of-range ambient temperature reading?
  - trigger temperature regulation state -> temperature continues to rise?
  - > critical threshold? -> initiate via protected can command [yes]
  - initiate via protected can command -> air conditioning compressor [fork]
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing a multi-stage cooling strategy for PWM fans and liquid-cooling loops. An out-of-range ambient temperature reading from the sensor fusion routine triggers the temperature regulation state. If the temperature continues to rise, a high-priority task activates forced-air cooling via the PWM fans. Upon exceeding a critical threshold, the system concurrently initiates the air conditioning compressor and liquid cooling pump via a protected CAN command, with a watchdog monitoring the response. This aggressive cooling phase employs a closed-loop control that cyclically adjusts the fan duty cycle until the temperature
- generated_excerpt:
  @startuml start :Out-of-range ambient temperature reading triggers temperature regulation state; if (Temperature continues to rise?) then (yes)   :Activate forced-air cooling via PWM fans;   if (Exceeds critical threshold?) then (yes)     fork       :Initiate air conditioning compressor via protected CAN command;     fork again       :Initiate liquid cooling pump via protected CAN command;     end fork     :Watchdog monitors response;     repeat       :Cyclically adjust fan duty cycle;     repeat while (Temperature re-enters safe operating envelope?) is (no)     ->yes;   else (no)   endif else (no)   :Persistent low-temperature condition initializes heater circuit; endif fork   :Monitoring t
### lmc-0019
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4444
- relation_f1: 0.0000
- missing_nodes:
  - in inner loop pitch regulator
- extra_nodes:
  - acceleration > 50 deg/sec ?
  - duration?
  - reject command
  - allow command
- missing_relations:
  - in inner loop pitch regulator -> durations > 100 frames?
  - durations > 100 frames? -> command angular pitch accelerations <= 50 deg/sec2 [yes]
- input_excerpt:
  2.	The Inner Loop Pitch Regulator Shall not command angular pitch accelerations greater than the capability of the system (50 deg/sec2) for durations exceeding 100 frames (1 second @ 100 hz).
- generated_excerpt:
  @startuml start :Command angular pitch acceleration; if (Acceleration > 50 deg/sec²?) then (Yes)   :Duration exceeds 100 frames?;   if (Duration?) then (> 100 frames)     :Reject command;   else (<= 100 frames)     :Allow command;   endif else (No)   :Allow command; endif stop @enduml
### rac-0009
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6316
- relation_f1: 0.4483
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2
  - condition judgement
  - shutdown
  - command becomes 4
- extra_nodes:
  - system starts up
  - high-voltage shutdown request = 2?
  - ignition switch at position 2 and front mcu state unchanged?
  - system shuts down
  - slow charging inactive and bms self-check counter = 1?
  - ignition switch at position 2 and onboard charger command = 1?
  - onboard charger command = 4?
  - remote mode active and front mcu state unchanged?
- missing_relations:
  - switch to state 127 -> condition judgement
  - condition judgement -> stay in state 127 [case ignition switch is 2 and front mcu state unchanged]
  - slow charging is inactive and timeout 2.2s occurs -> switch to state 12 [yes]
  - condition judgement -> stay in state 127 [case ignition switch is 2 and onboard charger command is 1]
  - stay in state 127 -> command becomes 4
  - command becomes 4 -> switch to state 12 [yes]
  - switch to state 12 -> ignition switch is off and slow charging is inactive
  - condition judgement -> stay in state 127 [case remote mode is active and front mcu state unchanged]
- input_excerpt:
  After the system starts up, if slow charging is active, it enters power-up mode. Then, if the high-voltage shutdown request (for charging or discharging) is set to 2, it switches to state 127. Once in state 127, the following actions apply based on conditions:  1. If the ignition switch is at position 2 and the front MCU state remains unchanged, the system stays in state 127.    a. Should slow charging become inactive and a timeout of 2.2 seconds occur, it switches to state 12. If the ignition switch is off at this point, the system shuts down and ends.    b. Similarly, if slow charging is inactive and the BMS self-check counter reads 1, it switches to state 12. Again, if the ignition switch
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging active?) then (yes)   :Enter power-up mode;   if (High-voltage shutdown request = 2?) then (yes)     :Switch to state 127;     if (Ignition switch at position 2 and front MCU state unchanged?) then (yes)       :Stay in state 127;       if (Slow charging inactive and timeout 2.2s?) then (yes)         :Switch to state 12;         if (Ignition switch off?) then (yes)           :System shuts down;           end         else (no)         endif       elseif (Slow charging inactive and BMS self-check counter = 1?) then (yes)         :Switch to state 12;         if (Ignition switch off?) then (yes)           :System shuts down;           end      

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
