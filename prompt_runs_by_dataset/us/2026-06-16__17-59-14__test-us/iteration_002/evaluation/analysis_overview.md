# Prompt Evaluation Analysis

## Summary
- count: 4
- syntax_pass_rate: 0.7500
- infrastructure_error_rate: 0.0000
- node_precision: 0.3661
- node_recall: 0.2644
- node_f1: 0.3070
- relation_precision: 0.5295
- relation_recall: 0.3141
- relation_f1: 0.3943
- plantuml_compilation_pass_rate: 0.7500
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
- extra_or_wrong_relation: 3
- wrong_parallel: 2
- wrong_loop: 2
- syntax_error: 1

## Representative Failure Cases
### fsd-0083
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4815
- relation_f1: 0.3582
- missing_nodes:
  - govern pwm fans
  - govern liquid-cooling actuators
  - primary sequence initiates
  - primary power rail nominal?
  - operation proceeds
  - two high-priority tasks spawned
  - hold system state
  - monitor temperature sensor data against safety thresholds
- extra_nodes:
  - rail voltage nominal?
  - read current data
  - monitor temperature sensor data
  - safety threshold excursion?
  - excursion persistent?
  - final supervisory state confirm all parameters nominal
  - communication fault?
  - bounded retries with exponential backoff
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern pwm fans [fork]
  - thermal management controller executes as state machine on rtos -> govern liquid-cooling actuators [fork]
  - govern pwm fans -> primary sequence initiates
  - govern liquid-cooling actuators -> primary sequence initiates
  - primary sequence initiates -> check system rail voltage status via pmic
  - primary power rail nominal? -> operation proceeds [yes]
  - operation proceeds -> two high-priority tasks spawned
  - two high-priority tasks spawned -> sample current sensor data [fork]
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing PWM fans and liquid-cooling actuators. Its primary sequence initiates with a check of the system's rail voltage status via the PMIC; operation proceeds only if this primary power rail is nominal. Upon validation, two high-priority tasks are spawned concurrently: one task samples the current sensor data, and if an overcurrent is detected, it enters an iterative monitoring mode using a ring buffer, holding the system state until the data normalizes. The concurrent task monitors temperature sensor data against safety thresholds; any excursion triggers immediate heat dissipation measures and, if persistent, init
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityDiamondBackgroundColor #F9F9F9  start  :Initialize Thermal Management Controller on RTOS;  :Check PMIC rail voltage status;  if (Rail Voltage Nominal?) then (No)     #LightCoral:Fail/Halt Operation;     stop else (Yes) endif  fork     :Sample current sensor data;     if (Overcurrent detected?) then (Yes)         repeat             :Enter iterative monitoring mode (Ring Buffer);             :Read current data;         repeat while (Data normalized?) is (No)         ->Yes;     else (No)     endif fork again     :Monitor temperature sensor data;     if (Safety threshold excursion?) then (Yes)         :Trigger immediate heat d
### lmc-0048
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.6667
- missing_nodes:
  - requirement when heading hold mode becomes active
  - pilot uses cockpit control
  - set heading hold reference
- extra_nodes:
  - heading hold mode becomes the active mode
  - pilot sets heading hold reference via cockpit control
- missing_relations:
  - requirement when heading hold mode becomes active -> pilot uses cockpit control
- input_excerpt:
  Requirement	When heading hold mode becomes the active mode the heading hold reference shall be set by the pilot via a cockpit control.
- generated_excerpt:
  @startuml start :Heading hold mode becomes the active mode; :Pilot sets heading hold reference via cockpit control; stop @enduml
### bp-0019
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3125
- relation_f1: 0.1622
- missing_nodes:
  - click new job
  - enter information
  - enter name
  - enter description
  - enter keywords
  - go to save job field
  - browse and select folder
  - open drop-downlists
- extra_nodes:
  - enter the name description and keywords for the job
  - in the save job in field browse and select the folder
  - select the source system and the destination system from the drop-down lists
  - system name displayed in drop-down list?
  - click the login to a new cms option
  - enter the system name user name and password
- missing_relations:
  - log in lifecycle manager tool -> go to promotion jobs home page
  - click new job -> new job window appears
  - new job window appears -> enter information
  - enter information -> enter name [fork]
  - enter information -> enter description [fork]
  - enter information -> enter keywords [fork]
  - enter name -> go to save job field
  - enter description -> go to save job field
- input_excerpt:
  19.	create a new job by using the LifeCycle Manager tool1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriatefields.4. In the Save Job in field, browse and select the folder in which you wantto save the job.5. Select the source system and the destination system from the drop-downlists.If the name of the system is not displayed in the drop-down list, click theLogin to a new CMS option. A new window is launched. Enter the nameof the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name, description, and keywords for the job; :In the Save Job in field, browse and select the folder; :Select the source system and the destination system from the drop-down lists; if (System name displayed in drop-down list?) then (No)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the system name, user name, and password; else (Yes) endif :Click Create; stop @enduml
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
  - system start up
  - front mcu initialization == 0?
  - condition
  - shut down exit
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
  @startuml start :System Start Up; if (Slow Charging Active?) then (Yes)   if (Front MCU Initialization == 0?) then (Yes)     :Enter State 82;     switch (Condition)     case (BMS Counter reaches 1 & Battery Pre-heating Demand == 3)       :Transition to State 126;       if (Slow Charging Inactive?) then (Yes)         :Shut Down & Exit;         stop       else (No)       endif     case (Pre-charge Failure)       :Transition to State 126;       if (Slow Charging Inactive?) then (Yes)         :Shut Down & Exit;         stop       else (No)       endif     case (Slow Charging Deactivates)       :Transition to State 126;       :Shut Down & Exit;       stop     case (AC Charging/Discharging System 

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
