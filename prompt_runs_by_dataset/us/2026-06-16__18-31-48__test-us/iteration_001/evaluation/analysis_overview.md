# Prompt Evaluation Analysis

## Summary
- count: 4
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4869
- node_recall: 0.5379
- node_f1: 0.5111
- relation_precision: 0.3717
- relation_recall: 0.3936
- relation_f1: 0.3823
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
- missing_activity: 4
- extra_activity: 4
- missing_or_wrong_relation: 4
- extra_or_wrong_relation: 4
- wrong_loop: 2
- wrong_parallel: 1

## Representative Failure Cases
### lmc-0040
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.1667
- missing_nodes:
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - b(inv(wp )b matrix inversion be accurate to 12 digits precision
- extra_nodes:
  - calculate determinant of b(inv(wp ))b
  - invert b(inv(wp ))b matrix
  - calculate check output matrix (multiply result by original matrix)
  - compare check output matrix to 3x3 identity matrix
  - each element within 1e-12 tolerance?
  - inversion accurate to 12 digits precision
  - inversion precision check failed
  - set ridge_on = true
- missing_relations:
  - determinant of b(inv(wp )b > 1e-12 -> each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance -> b(inv(wp )b matrix inversion be accurate to 12 digits precision
- input_excerpt:
  2.	When the determinant of B(inv(Wp’)B’ is > 1e-12 as indicated by ridge_on set to False, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 12 digits precision in that each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  @startuml start :Calculate determinant of B(inv(Wp'))B'; if (det(B(inv(Wp'))B') > 1e-12?) then (Yes)   :Set ridge_on = False;   :Invert B(inv(Wp'))B' matrix;   :Calculate check output matrix\n(Multiply result by original matrix);   :Compare check output matrix\nto 3x3 identity matrix;   if (Each element within 1e-12 tolerance?) then (Yes)     :Inversion accurate to 12 digits precision;   else (No)     :Inversion precision check failed;   endif else (No)   :Set ridge_on = True; endif stop @enduml
### rac-0017
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4211
- relation_f1: 0.3704
- missing_nodes:
  - slow charging is active and front mcu initialization=0
  - bms counter=1 and battery pre-heating demand=3
  - shutdown
  - pre-charge failure occurs
  - ac charging/discharging system fault
  - after 10s
- extra_nodes:
  - system starts up
  - front mcu initialization == 0?
  - condition
  - shut down and exit
  - wait 10-second timeout
- missing_relations:
  - enter state 82 -> bms counter=1 and battery pre-heating demand=3
  - switch to state 126 -> slow charging is inactive
  - slow charging is inactive -> shutdown [if yes]
  - bms counter=1 and battery pre-heating demand=3 -> pre-charge failure occurs [else if]
  - pre-charge failure occurs -> switch to state 126 [if yes]
  - bms counter=1 and battery pre-heating demand=3 -> slow charging is inactive [else if]
  - slow charging is inactive -> switch to state 126 [if yes]
  - bms counter=1 and battery pre-heating demand=3 -> ac charging/discharging system fault [else if]
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU initialization is 0, it enters state 82. From there: - When the BMS counter reaches 1 with a battery pre-heating demand of 3, the system transitions to state 126. If slow charging becomes inactive afterward, it shuts down and exits. - If a pre-charge failure occurs, the system moves to state 126. Should slow charging be inactive at that point, it shuts down and exits. - If slow charging deactivates, the system switches to state 126 before shutting down and exiting. - For AC charging/discharging system faults, the system waits through a 10-second timeout before shifting to state 126. If slow charging is inactive followin
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging active?) then (Yes)   if (Front MCU initialization == 0?) then (Yes)     :Enter state 82;     switch (Condition)     case (BMS counter reaches 1\n& Battery pre-heating demand == 3)       :Transition to state 126;       if (Slow charging inactive?) then (Yes)         :Shut down and exit;         stop       else (No)       endif     case (Pre-charge failure)       :Transition to state 126;       if (Slow charging inactive?) then (Yes)         :Shut down and exit;         stop       else (No)       endif     case (Slow charging deactivates)       :Transition to state 126;       :Shut down and exit;       stop     case (AC charging/discharging
### fsd-0050
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6038
- relation_f1: 0.5067
- missing_nodes:
  - thermal management controller implemented as deterministic state machine on rtos
  - govern pwm fans
  - govern liquid-cooling loops
  - receive user-initiated air conditioner start command
  - indoor temperature > setpoint?
  - user commands for wind speed adjustment serviced via interrupt-driven priority queue
  - enter control loop
  - bounded retries
- extra_nodes:
  - receive user-initiated ac start command
  - does indoor temperature exceed setpoint?
  - monitor condenser temperature
  - interrupt-driven priority queue
  - receive wind speed adjustment command
  - execute with bounded retries exponential backoff for fault handling
  - periodic sensor fusion calibration
  - fault confirmed?
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
  @startuml skinparam style strictuml  title Thermal Management Controller - Activity Diagram  start  :Receive user-initiated AC start command;  if (Is unit in powered-off state?) then (No)   :Return to low-power standby state;   stop else (Yes) endif  if (Does indoor temperature exceed setpoint?) then (No)   :Return to low-power standby state;   stop else (Yes) endif  :Execute air conditioner startup sequence;  fork   :High-priority task (Mutex sync with BMS/PMIC);   repeat     :Monitor compressor status;     :Monitor condenser temperature;   repeat while (Operational parameters within safe bounds?) is (Yes)   ->No;   :Initiate controlled cool-down safety path;   :Return to low-power standby 
### pure-0049
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.4211
- missing_nodes:
  - display inventory departments
  - see view inventory
  - display confirmation screen
- extra_nodes:
  - the screen displays all inventory departments in matrix format
  - the system displays a confirmation screen where a reason for the adjustment must be specified by the user
  - valid item change?
  - display validation error
- missing_relations:
  - access main inventory screen -> display inventory departments
  - display inventory departments -> see view inventory
  - see view inventory -> drill down to desired existing inventory item
  - change item quantity -> display confirmation screen
  - display confirmation screen -> specify adjustment reason
- input_excerpt:
  2. Adjust Item Quantity 2.1. User accesses the main inventory screen 2.2. The screen displays all inventory departments in matrix format 2.3. User drills down to the desired existing inventory item (see View Inventory) 2.4. The item detail screen is presented 2.5. User changes the item quantity 2.6. The system displays a confirmation screen where a reason for the adjustment must be specified by the user 2.7. The system validates the item change 2.8. Item information is updated in the inventory
- generated_excerpt:
  @startuml start :User accesses the main inventory screen; :The screen displays all inventory departments in matrix format; :User drills down to the desired existing inventory item (see View Inventory); :The item detail screen is presented; :User changes the item quantity; :The system displays a confirmation screen where a reason for the adjustment must be specified by the user; :User specifies the reason for the adjustment; :The system validates the item change; if (Valid item change?) then (Yes)   :Item information is updated in the inventory; else (No)   :Display validation error;   stop endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
