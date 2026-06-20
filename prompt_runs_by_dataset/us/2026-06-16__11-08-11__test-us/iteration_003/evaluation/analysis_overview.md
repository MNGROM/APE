# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3527
- node_recall: 0.3399
- node_f1: 0.3462
- relation_precision: 0.2807
- relation_recall: 0.2266
- relation_f1: 0.2508
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
- wrong_parallel: 4
- wrong_loop: 3

## Representative Failure Cases
### lmc-0030
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - in nlguidance
  - vector define location at standoff 2 with offset from target position?
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point?
  - it is inertial position vector for aim point 2
  - compute the vector
- extra_nodes:
  - compute the tangent relative position vector from the vehicle to aim point 2
  - compute a vector perpendicular to the tangent relative position vector
  - define the offset from the target position using the perpendicular vector
  - compute the inertial position vector for aim point 2 at standoff 2 with the defined offset
- missing_relations:
  - in nlguidance -> vector define location at standoff 2 with offset from target position?
  - vector define location at standoff 2 with offset from target position? -> it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? [yes]
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? -> it is inertial position vector for aim point 2 [yes]
  - it is inertial position vector for aim point 2 -> compute the vector
- input_excerpt:
  3.	NLGuidance shall compute the inertial position vector for aim point 2, defining the location at Standoff 2 with an offset from the target position, and oriented on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point.
- generated_excerpt:
  @startuml start :Compute the tangent relative position vector\nfrom the vehicle to Aim Point 2; :Compute a vector perpendicular\nto the tangent relative position vector; :Define the offset from the target position\nusing the perpendicular vector; :Compute the inertial position vector\nfor Aim Point 2 at Standoff 2\nwith the defined offset; stop @enduml
### lmc-0019
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - in inner loop pitch regulator
  - durations > 100 frames?
  - command angular pitch accelerations <= 50 deg/sec2
- extra_nodes:
  - inner loop pitch regulator commands angular pitch acceleration
  - check commanded acceleration against system capability (50 deg/sec )
  - commanded acceleration > 50 deg/sec ?
  - start/continue duration counter (in frames at 100 hz)
  - duration exceeds 100 frames (1 second)?
  - trigger violation acceleration > 50 deg/sec for > 1 second
  - halt/cap pitch acceleration command
  - allow commanded acceleration (duration < 1 sec is acceptable)
- missing_relations:
  - in inner loop pitch regulator -> durations > 100 frames?
  - durations > 100 frames? -> command angular pitch accelerations <= 50 deg/sec2 [yes]
- input_excerpt:
  2.	The Inner Loop Pitch Regulator Shall not command angular pitch accelerations greater than the capability of the system (50 deg/sec2) for durations exceeding 100 frames (1 second @ 100 hz).
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #E8F5E9 skinparam ActivityBorderColor #2E7D32  start  :Inner Loop Pitch Regulator\ncommands angular pitch acceleration;  :Check commanded acceleration\nagainst system capability (50 deg/sec²);  if (Commanded acceleration > 50 deg/sec²?) then (Yes)   :Start/Continue duration counter\n(in frames at 100 Hz);      if (Duration exceeds 100 frames\n(1 second)?) then (Yes)     :Trigger Violation:\nAcceleration > 50 deg/sec² for > 1 second;     :Halt/Cap Pitch Acceleration Command;     stop   else (No)     :Allow Commanded Acceleration\n(Duration < 1 sec is acceptable);   endif    else (No)   :Reset duration counter to 0;   :Allow Commanded Acceleration; e
### pure-0001
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0741
- relation_f1: 0.0606
- missing_nodes:
  - conduct contingency studies
  - verify black start units annually
  - number
  - size
  - availability
  - location
  - document cranking paths
  - provide to wecc upon request
- extra_nodes:
  - annually verify the number size availability and location of black start units
  - document cranking paths and provide them to wecc upon request
  - evaluate diverse fuel resources cranking paths communication unit capabilities and coordination with neighboring plans
  - coordinate the planning process with transmission owners and neighboring balancing authorities
  - annually enter into rmr and interim black start contracts with qualified generators
- missing_relations:
  - conduct contingency studies -> determine amount and location of black start generation
  - verify black start units annually -> number [fork]
  - verify black start units annually -> size [fork]
  - verify black start units annually -> availability [fork]
  - verify black start units annually -> location [fork]
  - number -> document cranking paths
  - size -> document cranking paths
  - availability -> document cranking paths
- input_excerpt:
  [Grid Planning Steps] Step 1: The CAISO determines the amount and location of Black Start Generation through contingency studies. Step 2: The CAISO annually verifies the number, size, availability, and location of Black Start units.Step 3: The CAISO documents Cranking Paths and provides them to WECC upon request.Step 4: The CAISO evaluates diverse fuel resources, cranking paths, communication, unit capabilities, and coordination with neighboring plans.Step 5: The planning process is coordinated with transmission owners and neighboring Balancing Authorities.Step 6: The CAISO annually enters into RMR and Interim Black Start Contracts with qualified generators.
- generated_excerpt:
  @startuml start :Determine the amount and location of Black Start Generation through contingency studies; :Annually verify the number, size, availability, and location of Black Start units; :Document Cranking Paths and provide them to WECC upon request; :Evaluate diverse fuel resources, cranking paths, communication, unit capabilities, and coordination with neighboring plans; :Coordinate the planning process with transmission owners and neighboring Balancing Authorities; :Annually enter into RMR and Interim Black Start Contracts with qualified generators; stop @enduml
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.3243
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - click manage dependencies
  - manage dependencies window appears
  - list of infoobjects and their dependents is displayed
  - open select dependents drop-down list
  - dependents are displayed on the right
- extra_nodes:
  - in the promotion jobs home page click manage dependencies
  - view the list of infoobjects and their dependents in the manage dependencies window
  - from the select dependents drop-down list select an option to add dependents to the job
  - explicitly select the specific dependents you want to promote
  - select a filtering option and click ok
  - click apply changes to update the list of dependents
  - click apply changes and close to save the changes
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37 [yes]
  - see creating a new job on page 37 -> add required infoobjects to new job
  - go to promotion jobs home page -> click manage dependencies
  - click manage dependencies -> manage dependencies window appears
  - manage dependencies window appears -> list of infoobjects and their dependents is displayed
  - list of infoobjects and their dependents is displayed -> open select dependents drop-down list
  - open select dependents drop-down list -> dependents are displayed on the right
- input_excerpt:
  22.	manage dependencies of an infoobject1. Log into the LifeCycle Manager tool.2. Create a new job. For information on creating a new job, see Creating aNew Job on page 37.3. Add the required infoobjects to the new job.4. In the "Promotion Jobs" home page, click Manage Dependencies. The "Manage Dependencies" window appears. This window displays the list of infoobjects and their dependents, as shown in the following figure:5. From the Select Dependents drop-down list, select any of the options available to add the dependents to the job. The dependents are displayed on the right side. The dependents are not selected by default; you must explicitly select the dependents you want to promote. For
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :In the "Promotion Jobs" home page,\nclick Manage Dependencies; :View the list of infoobjects\nand their dependents in the\n"Manage Dependencies" window; :From the Select Dependents\ndrop-down list, select an option\nto add dependents to the job; :Explicitly select the specific\ndependents you want to promote; :View supported filtering options\nof infoobjects in the drop-down list; :Select a filtering option\nand click OK; :View the filtered infoobjects; :Click Apply Changes to update\nthe list of dependents; :Click Apply Changes and Close\nto save the changes; stop @enduml
### rac-0013
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3478
- relation_f1: 0.1639
- missing_nodes:
  - condtion judgement
  - dcdc state 1 or 3s elapsed
  - shutdown
  - eas state 1 or 3s elapsed
  - current<6.1 or 3s elapsed
- extra_nodes:
  - system starts up
  - fast charging active?
  - dcdc state = 1?
  - transition to state 156
  - dcdc state = 1 or 3 seconds pass?
  - move to state 157
  - shut down and end
  - eas state = 1?
- missing_relations:
  - enter state 155 -> condtion judgement
  - condtion judgement -> stay in state 155 [case dcdc state=1]
  - switch to state 156 -> dcdc state 1 or 3s elapsed
  - dcdc state 1 or 3s elapsed -> switch to state 157 [yes]
  - switch to state 157 -> fast charging is inactive
  - condtion judgement -> stay in state 155 [case eas state=1]
  - switch to state 156 -> eas state 1 or 3s elapsed
  - eas state 1 or 3s elapsed -> switch to state 157 [yes]
- input_excerpt:
  After the system starts up: if fast charging is active and the BMS manual charging/discharging flag is 0, the system enters state 155. While in state 155:  1. For DCDC state monitoring:    - If DCDC state remains 1, stay in state 155.    - If the BMS-fast charger handshake flag becomes 1, transition to state 156.    - If DCDC state is not 1 or 3 seconds pass, move to state 157.    - If fast charging becomes inactive at any point, shut down and end the process.  2. For EAS state monitoring:    - If EAS state stays at 1, remain in state 155.    - If the handshake flag turns to 1, switch to state 156.    - If EAS state isn’t 1 or 3 seconds elapse, shift to state 157.    - Should fast charging d
- generated_excerpt:
  @startuml start  :System starts up;  if (Fast charging active?) then (yes)   if (BMS manual charging/discharging flag = 0?) then (yes)     :Enter State 155;   else (no)     stop   endif else (no)   stop endif  partition "DCDC State Monitoring" {   if (DCDC state = 1?) then (yes)     :Stay in State 155;   else (no)   endif   if (BMS-fast charger handshake flag = 1?) then (yes)     :Transition to State 156;     stop   elseif (DCDC state != 1 OR 3 seconds pass?) then (yes)     :Move to State 157;     stop   else (no)   endif   if (Fast charging inactive?) then (yes)     :Shut down and end;     stop   else (no)   endif }  partition "EAS State Monitoring" {   if (EAS state = 1?) then (yes)     :R
### pure-0094
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3636
- relation_f1: 0.1667
- missing_nodes:
  - menu selection
  - saved?
  - close game
- extra_nodes:
  - receive menu selection (exit game)
  - unsaved progress?
  - save confirmation?
  - save game
- missing_relations:
  - menu selection -> saved?
  - saved? -> prompt to save [no]
  - prompt to save -> close game
  - saved? -> close game [yes]
- input_excerpt:
  Exit Game Input: Menu selection. Processing: Prompt to save if unsaved, then close the game. Output: Close main window.
- generated_excerpt:
  @startuml start :Receive Menu Selection (Exit Game); if (Unsaved Progress?) then (Yes)   :Prompt to Save;   if (Save Confirmation?) then (Yes)     :Save Game;   else (No)   endif else (No) endif :Close main window; stop @enduml
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3636
- relation_f1: 0.1481
- missing_nodes:
  - click manage syetems
  - list is displayed
  - host names
  - port numbers
  - display names
  - descriptions
  - add information
  - host name
- extra_nodes:
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
  @startuml start :In the "Administration Options" window, click Manage Systems; :The list of host names, port numbers, display names, and descriptions is displayed; :Click Add; :The "Add System" dialog box appears; :Add the host name, port number, display name, and the description in the appropriate fields; :Click Add to add the system; :The host system is added to the list; stop @enduml
### fsd-0111
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.3704
- missing_nodes:
  - thermal management controller executes as state machine on rtos
  - govern multi-stage cooling strategy for
  - pwm fans
  - liquid-cooling loops
  - out-of-range ambient temperature reading?
  - trigger temperature regulation state
  - > critical threshold?
  - initiate via protected can command
- extra_nodes:
  - rtos task thermal management controller
  - read ambient temperature from sensor fusion routine
  - temperature out of range?
  - enter temperature regulation state
  - exceeds critical threshold?
  - initiate air conditioning compressor (protected can command)
  - initiate liquid cooling pump (protected can command)
  - closed-loop control adjust fan duty cycle
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern multi-stage cooling strategy for
  - govern multi-stage cooling strategy for -> pwm fans [fork]
  - govern multi-stage cooling strategy for -> liquid-cooling loops [fork]
  - pwm fans -> out-of-range ambient temperature reading?
  - liquid-cooling loops -> out-of-range ambient temperature reading?
  - out-of-range ambient temperature reading? -> trigger temperature regulation state [yes]
  - > critical threshold? -> initiate via protected can command [yes]
  - initiate via protected can command -> air conditioning compressor [fork]
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing a multi-stage cooling strategy for PWM fans and liquid-cooling loops. An out-of-range ambient temperature reading from the sensor fusion routine triggers the temperature regulation state. If the temperature continues to rise, a high-priority task activates forced-air cooling via the PWM fans. Upon exceeding a critical threshold, the system concurrently initiates the air conditioning compressor and liquid cooling pump via a protected CAN command, with a watchdog monitoring the response. This aggressive cooling phase employs a closed-loop control that cyclically adjusts the fan duty cycle until the temperature
- generated_excerpt:
  @startuml skinparam style strictuml  start  :RTOS Task: Thermal Management Controller;  :Read ambient temperature from sensor fusion routine;  if (Temperature out of range?) then (yes)   :Enter Temperature Regulation State;    if (Temperature continues to rise?) then (yes)     :High-priority task: Activate forced-air cooling (PWM Fans);   else (no)   endif    if (Exceeds critical threshold?) then (yes)     fork       :Initiate Air Conditioning Compressor (Protected CAN Command);     fork again       :Initiate Liquid Cooling Pump (Protected CAN Command);     end fork     :Watchdog monitors response;      repeat       :Closed-loop control: Adjust fan duty cycle;     repeat while (Temperature r

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
