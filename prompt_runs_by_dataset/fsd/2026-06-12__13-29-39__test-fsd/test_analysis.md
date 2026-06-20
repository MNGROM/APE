# Prompt Evaluation Analysis

## Summary
- count: 1
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.0000
- node_recall: 0.0000
- node_f1: 0.0000
- relation_precision: 0.0000
- relation_recall: 0.0000
- relation_f1: 0.0000
- higen_compilation_pass_rate: 1.0000
- higen_llm_evaluated: 0.0000
- higen_llm_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_activity: 1
- extra_activity: 1
- missing_or_wrong_relation: 1
- extra_or_wrong_relation: 1
- wrong_loop: 1

## Representative Failure Cases
### fsd-0001
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- higen_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - thermal management controller executes as state machine on rtos
  - govern pwm fans
  - govern liquid-cooling loop
  - external ambient exceeds set threshold?
  - temperature sensor isr triggered
  - initiate data validation sequence
  - primary sensor reading erroneous?
  - fail over to redundant sensor path
- extra_nodes:
  - temp sensor isr
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern pwm fans
  - govern pwm fans -> govern liquid-cooling loop
  - govern liquid-cooling loop -> external ambient exceeds set threshold?
  - external ambient exceeds set threshold? -> temperature sensor isr triggered
  - temperature sensor isr triggered -> initiate data validation sequence
  - initiate data validation sequence -> primary sensor reading erroneous?
  - primary sensor reading erroneous? -> fail over to redundant sensor path
  - fail over to redundant sensor path -> sensor over-temperature confirmed?
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing PWM fans and a liquid-cooling loop. A temperature sensor ISR, triggered when the external ambient exceeds a set threshold, initiates a data validation sequence; if the primary sensor reading is deemed erroneous, the system fails over to a redundant sensor path. Upon confirmed over-temperature from either sensor, the controller activates multiple PWM fans, managed by a priority-based task, while a separate periodic task, driven by a timer interrupt, monitors the thermal trajectory. If the temperature fails to descend within a defined window, a higher-priority task initializes the liquid-cooling loop to augmen
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEEBEB skinparam ActivityDiamondBackgroundColor #F3F3F3  title Thermal Management Controller - RTOS State Machine  start  partition "Interrupt Service Routines" {     :Temp Sensor ISR;     note right: Triggered when ambient > threshold }  partition "Data Validation & Failover" {     :Initiate Data Validation Sequence;     if (Primary Sensor Erroneous?) then (yes)         :Failover to Redundant Sensor Path;     else (no)         :Use Primary Sensor Path;     endif     if (Confirmed Over-Temperature?) then (yes)         :Activate PWM Fans;         note right: Managed by priority-based task     else (no)         :Return to S

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
