# Prompt Evaluation Analysis

## Summary
- count: 4
- syntax_pass_rate: 0.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.0000
- node_recall: 0.0000
- node_f1: 0.0000
- relation_precision: 0.0000
- relation_recall: 0.0000
- relation_f1: 0.0000
- plantuml_compilation_pass_rate: 0.0000
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- generation_error: 4
- syntax_error: 4
- missing_activity: 4
- missing_or_wrong_relation: 4

## Representative Failure Cases
### pure-0049
- dataset: pure
- failure_types: generation_error, syntax_error, missing_activity, missing_or_wrong_relation
- syntax_passed: False
- syntax_errors: LLM generation failed: ZHIPU_LLM_API_KEY is required unless --mock-with-gold is used.
- plantuml_compiles: False
- plantuml_compile_errors: No PlantUML content to compile.
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - access main inventory screen
  - display inventory departments
  - see view inventory
  - drill down to desired existing inventory item
  - item detail screen is presented
  - change item quantity
  - display confirmation screen
  - specify adjustment reason
- missing_relations:
  - access main inventory screen -> display inventory departments
  - display inventory departments -> see view inventory
  - see view inventory -> drill down to desired existing inventory item
  - drill down to desired existing inventory item -> item detail screen is presented
  - item detail screen is presented -> change item quantity
  - change item quantity -> display confirmation screen
  - display confirmation screen -> specify adjustment reason
  - specify adjustment reason -> system validates item change
- input_excerpt:
  2. Adjust Item Quantity 2.1. User accesses the main inventory screen 2.2. The screen displays all inventory departments in matrix format 2.3. User drills down to the desired existing inventory item (see View Inventory) 2.4. The item detail screen is presented 2.5. User changes the item quantity 2.6. The system displays a confirmation screen where a reason for the adjustment must be specified by the user 2.7. The system validates the item change 2.8. Item information is updated in the inventory
- generated_excerpt:
  
### rac-0017
- dataset: rac
- failure_types: generation_error, syntax_error, missing_activity, missing_or_wrong_relation
- syntax_passed: False
- syntax_errors: LLM generation failed: ZHIPU_LLM_API_KEY is required unless --mock-with-gold is used.
- plantuml_compiles: False
- plantuml_compile_errors: No PlantUML content to compile.
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - slow charging is active and front mcu initialization=0
  - enter state 82
  - bms counter=1 and battery pre-heating demand=3
  - switch to state 126
  - slow charging is inactive
  - shutdown
  - pre-charge failure occurs
  - slow charging inactive
- missing_relations:
  - slow charging is active and front mcu initialization=0 -> enter state 82 [if yes]
  - enter state 82 -> bms counter=1 and battery pre-heating demand=3
  - bms counter=1 and battery pre-heating demand=3 -> switch to state 126 [if yes]
  - switch to state 126 -> slow charging is inactive
  - slow charging is inactive -> shutdown [if yes]
  - bms counter=1 and battery pre-heating demand=3 -> pre-charge failure occurs [else if]
  - pre-charge failure occurs -> switch to state 126 [if yes]
  - switch to state 126 -> slow charging inactive
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU initialization is 0, it enters state 82. From there: - When the BMS counter reaches 1 with a battery pre-heating demand of 3, the system transitions to state 126. If slow charging becomes inactive afterward, it shuts down and exits. - If a pre-charge failure occurs, the system moves to state 126. Should slow charging be inactive at that point, it shuts down and exits. - If slow charging deactivates, the system switches to state 126 before shutting down and exiting. - For AC charging/discharging system faults, the system waits through a 10-second timeout before shifting to state 126. If slow charging is inactive followin
- generated_excerpt:
  
### lmc-0040
- dataset: lmc
- failure_types: generation_error, syntax_error, missing_activity, missing_or_wrong_relation
- syntax_passed: False
- syntax_errors: LLM generation failed: ZHIPU_LLM_API_KEY is required unless --mock-with-gold is used.
- plantuml_compiles: False
- plantuml_compile_errors: No PlantUML content to compile.
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - ridge_on set to false
  - determinant of b(inv(wp )b > 1e-12
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - b(inv(wp )b matrix inversion be accurate to 12 digits precision
- missing_relations:
  - ridge_on set to false -> determinant of b(inv(wp )b > 1e-12
  - determinant of b(inv(wp )b > 1e-12 -> each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance -> b(inv(wp )b matrix inversion be accurate to 12 digits precision
- input_excerpt:
  2.	When the determinant of B(inv(Wp’)B’ is > 1e-12 as indicated by ridge_on set to False, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 12 digits precision in that each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  
### fsd-0050
- dataset: fsd
- failure_types: generation_error, syntax_error, missing_activity, missing_or_wrong_relation
- syntax_passed: False
- syntax_errors: LLM generation failed: ZHIPU_LLM_API_KEY is required unless --mock-with-gold is used.
- plantuml_compiles: False
- plantuml_compile_errors: No PlantUML content to compile.
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - thermal management controller implemented as deterministic state machine on rtos
  - govern pwm fans
  - govern liquid-cooling loops
  - receive user-initiated air conditioner start command
  - unit in powered-off state?
  - indoor temperature > setpoint?
  - execute air conditioner startup sequence
  - high-priority task synchronized via mutexes with bms/pmic interface
- missing_relations:
  - thermal management controller implemented as deterministic state machine on rtos -> govern pwm fans [fork]
  - thermal management controller implemented as deterministic state machine on rtos -> govern liquid-cooling loops [fork]
  - govern pwm fans -> receive user-initiated air conditioner start command
  - govern liquid-cooling loops -> receive user-initiated air conditioner start command
  - receive user-initiated air conditioner start command -> unit in powered-off state?
  - unit in powered-off state? -> indoor temperature > setpoint? [yes]
  - indoor temperature > setpoint? -> execute air conditioner startup sequence [yes]
  - execute air conditioner startup sequence -> high-priority task synchronized via mutexes with bms/pmic interface [fork]
- input_excerpt:
  The thermal management controller, implemented as a deterministic state machine on the RTOS, governs the PWM fans and liquid-cooling loops. Upon receiving a user-initiated air conditioner start command, the system first verifies the unit is in a powered-off state and then checks if the indoor temperature exceeds the setpoint. If both conditions are met, it executes the air conditioner startup sequence, during which a high-priority task, synchronized via mutexes with a BMS/PMIC interface, continuously monitors the compressor status and condenser temperature to ensure operational parameters remain within safe bounds. A medium-priority periodic task, scheduled by the RTOS, polls indoor temperat
- generated_excerpt:
  

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
