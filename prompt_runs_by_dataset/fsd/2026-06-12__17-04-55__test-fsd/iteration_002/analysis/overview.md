# Prompt Evaluation Analysis

## Summary
- count: 2
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4167
- node_recall: 0.4271
- node_f1: 0.3586
- relation_precision: 0.1250
- relation_recall: 0.2500
- relation_f1: 0.1667
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 2.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7625
- llm_node_recall: 0.8215
- llm_node_f1: 0.7596
- llm_relation_precision: 0.6500
- llm_relation_recall: 0.7333
- llm_relation_f1: 0.6550

## Failure Types
- missing_activity: 2
- extra_activity: 2
- missing_or_wrong_relation: 2
- extra_or_wrong_relation: 2

## Representative Failure Cases
### pure-0043
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2727
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7500
- llm_relation_f1: 0.5600
- missing_nodes:
  - display edit attributes screen
  - all existing item attributes
  - attribute x department assignments
  - filter view?
  - attribute status
  - active
  - active status
  - inactive
- extra_nodes:
  - user wants to filter view?
  - user clicks the done button
  - user is taken back to the main inventory screen
- missing_relations:
  - access main inventory screen -> display edit attributes button
  - display edit attributes button -> click edit attributes button
  - click edit attributes button -> display edit attributes screen
  - display edit attributes screen -> all existing item attributes
  - all existing item attributes -> attribute x department assignments
  - attribute x department assignments -> filter view?
  - filter view? -> attribute status
  - attribute status -> active
- input_excerpt:
  1. View Item Attributes 1.1. User accesses the main inventory screen 1.2. System displays the Edit Attributes button 1.3. User clicks the Edit Attributes button 1.4. System displays the Edit Attributes screen which displays all existing item attributes and their attribute x department assignments 1.5. Optionally, user filters view by attribute status (active, inactive, all) 1.6. User clicks the Done button 1.7. User is taken back to the main inventory screen
- generated_excerpt:
  @startuml start :User accesses the main inventory screen; :System displays the Edit Attributes button; :User clicks the Edit Attributes button; :System displays the Edit Attributes screen (all existing item attributes and their attribute x department assignments); if (User wants to filter view?) then (Yes)   :User filters view by attribute status   (active, inactive, all); else (No) endif :User clicks the Done button; :User is taken back to the main inventory screen; stop @enduml
### lmc-0011
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4444
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 0.7692
- llm_relation_f1: 0.7500
- missing_nodes:
  - autopilot change states from pullup to transition
- extra_nodes:
  - autopilot in pullup state
  - change state to transition
  - remain in pullup state
  - remain in pullup state
- missing_relations:
  - sensor data is good? -> autopilot change states from pullup to transition
- input_excerpt:
  7.	The autopilot shall change states from PULLUP to TRANSITION when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml skinparam style strictuml title Autopilot State Change: PULLUP to TRANSITION  start :Autopilot in PULLUP state; if (System supported?) then (Yes)   if (Sensor data is good?) then (Yes)     :Change state to TRANSITION;   else (No)     :Remain in PULLUP state;   endif else (No)   :Remain in PULLUP state; endif stop  @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
