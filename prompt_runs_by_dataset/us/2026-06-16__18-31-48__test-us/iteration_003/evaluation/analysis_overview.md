# Prompt Evaluation Analysis

## Summary
- count: 4
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3847
- node_recall: 0.3395
- node_f1: 0.3607
- relation_precision: 0.6001
- relation_recall: 0.4409
- relation_f1: 0.5083
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
- extra_or_wrong_relation: 3
- wrong_parallel: 2
- wrong_loop: 2

## Representative Failure Cases
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
  - pilot sets the heading hold reference via a cockpit control
- missing_relations:
  - requirement when heading hold mode becomes active -> pilot uses cockpit control
- input_excerpt:
  Requirement	When heading hold mode becomes the active mode the heading hold reference shall be set by the pilot via a cockpit control.
- generated_excerpt:
  @startuml start :Heading hold mode becomes the active mode; :Pilot sets the heading hold reference via a cockpit control; stop @enduml
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
  - enter the name description and keywords for the job in the appropriate fields
  - in the save job in field browse and select the folder in which you want to save the job
  - select the source system and the destination system from the drop-down lists
  - is the name of the system displayed in the drop-down list?
  - click the login to a new cms option
  - enter the name of the system along with the user name and password
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
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name, description, and keywords for the job in the appropriate fields; :In the Save Job in field, browse and select the folder in which you want to save the job; :Select the source system and the destination system from the drop-down lists; if (Is the name of the system displayed in the drop-down list?) then (No)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the name of the system along with the user name and password; else (Yes) endif :Click Create; @enduml
### rac-0017
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4800
- relation_f1: 0.5294
- missing_nodes:
  - bms counter=1 and battery pre-heating demand=3
  - shutdown
  - ac charging/discharging system fault
  - after 10s
- extra_nodes:
  - system starts up
  - condition?
  - transition to state 126
  - shut down and exit
  - move to state 126
  - slow charging deactivates?
  - wait through 10-second timeout
  - shift to state 126
- missing_relations:
  - enter state 82 -> bms counter=1 and battery pre-heating demand=3
  - bms counter=1 and battery pre-heating demand=3 -> pre-charge failure occurs [else if]
  - bms counter=1 and battery pre-heating demand=3 -> slow charging is inactive [else if]
  - bms counter=1 and battery pre-heating demand=3 -> ac charging/discharging system fault [else if]
  - ac charging/discharging system fault -> after 10s [if yes]
  - after 10s -> switch to state 126 [while no]
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU initialization is 0, it enters state 82. From there: - When the BMS counter reaches 1 with a battery pre-heating demand of 3, the system transitions to state 126. If slow charging becomes inactive afterward, it shuts down and exits. - If a pre-charge failure occurs, the system moves to state 126. Should slow charging be inactive at that point, it shuts down and exits. - If slow charging deactivates, the system switches to state 126 before shutting down and exiting. - For AC charging/discharging system faults, the system waits through a 10-second timeout before shifting to state 126. If slow charging is inactive followin
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active\nand front MCU initialization is 0?) then (yes)   :Enter state 82;   repeat     if (Condition?) then (BMS counter reaches 1\nwith battery pre-heating demand of 3)       :Transition to state 126;       if (Slow charging becomes inactive?) then (yes)         :Shut down and exit;         stop       else (no)       endif     elseif (Pre-charge failure occurs?) then (yes)       :Move to state 126;       if (Slow charging is inactive?) then (yes)         :Shut down and exit;         stop       else (no)       endif     elseif (Slow charging deactivates?) then (yes)       :Switch to state 126;       :Shut down and exit;       stop     e
### fsd-0012
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5909
- relation_f1: 0.5965
- missing_nodes:
  - vehicle initialization
  - power management subsystem governed by rtos
  - employ closed-loop control
  - adjust throttle valve opening
  - periodically sample generator output rail voltage and battery charging status
  - trigger adc readings by timer interrupts
  - debounce
  - place into protected ring buffer
- extra_nodes:
  - adjust throttle valve opening via closed-loop control
  - sample generator output rail voltage and battery charging status via adc triggered by timer interrupts
  - debounce adc readings
  - place adc readings into protected ring buffer
  - adjust generator output power via pid controller
  - implement exponential backoff with staged verification cycles
- missing_relations:
  - vehicle initialization -> power management subsystem governed by rtos
  - power management subsystem governed by rtos -> monitor power rails via pmic and bms
  - employ closed-loop control -> adjust throttle valve opening
  - initiate engine start sequence -> periodically sample generator output rail voltage and battery charging status [fork]
  - trigger adc readings by timer interrupts -> debounce
  - debounce -> place into protected ring buffer
  - battery rail voltage within safe operating range -> execute as concurrent rtos tasks managed by priority queues [no]
  - execute as concurrent rtos tasks managed by priority queues -> generator output power adjustment [fork]
- input_excerpt:
  Upon vehicle initialization, the power management subsystem, governed by a real-time operating system (RTOS), monitors all power rails via the PMIC and BMS. If the battery rail voltage is below the defined threshold, a high-priority task checks the engine state. Should the engine be uninitialized and the vehicle confirmed to be in a parking state, an engine start sequence is initiated; this task monitors the engine speed via the FADEC, employing a closed-loop control to adjust the throttle valve opening until the speed stabilizes within the required range. Concurrently, a separate task periodically samples the generator output rail voltage and battery charging status, with these ADC readings
- generated_excerpt:
  @startuml start  :Monitor all power rails via PMIC and BMS;  if (Battery rail voltage below threshold?) then (yes)     :Check engine state via high-priority task;     if (Engine uninitialized and vehicle in parking state?) then (yes)         :Initiate engine start sequence;         repeat             :Monitor engine speed via FADEC;             :Adjust throttle valve opening via closed-loop control;         repeat while (Engine speed stabilizes within required range?) is (no)         ->yes;     endif endif  fork     repeat         :Sample generator output rail voltage and battery charging status via ADC triggered by timer interrupts;         :Debounce ADC readings;         :Place ADC reading

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
