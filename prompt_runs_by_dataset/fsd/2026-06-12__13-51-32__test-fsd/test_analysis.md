# Prompt Evaluation Analysis

## Summary
- count: 1
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3158
- node_recall: 0.2400
- node_f1: 0.2727
- relation_precision: 0.1667
- relation_recall: 0.1250
- relation_f1: 0.1429
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 1.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8636
- llm_node_recall: 0.7037
- llm_node_f1: 0.7755
- llm_relation_precision: 0.4400
- llm_relation_recall: 0.3143
- llm_relation_f1: 0.3667

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
- plantuml_compiles: True
- node_f1: 0.2727
- relation_f1: 0.1429
- llm_element_status: success
- llm_node_f1: 0.7755
- llm_relation_f1: 0.3667
- missing_nodes:
  - thermal management controller executes as state machine on rtos
  - govern pwm fans
  - govern liquid-cooling loop
  - external ambient exceeds set threshold?
  - temperature sensor isr triggered
  - sensor over-temperature confirmed?
  - priority-based task manages
  - activate multiple pwm fans
- extra_nodes:
  - execute as state machine on rtos
  - trigger on external ambient > threshold
  - use primary sensor reading
  - confirmed over-temperature?
  - activate pwm fans via priority-based task
  - trigger periodic task
  - temperature descends within defined window?
  - initialize liquid-cooling loop (higher-priority task)
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern pwm fans
  - govern pwm fans -> govern liquid-cooling loop
  - govern liquid-cooling loop -> external ambient exceeds set threshold?
  - external ambient exceeds set threshold? -> temperature sensor isr triggered
  - temperature sensor isr triggered -> initiate data validation sequence
  - fail over to redundant sensor path -> sensor over-temperature confirmed?
  - sensor over-temperature confirmed? -> priority-based task manages
  - priority-based task manages -> activate multiple pwm fans
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing PWM fans and a liquid-cooling loop. A temperature sensor ISR, triggered when the external ambient exceeds a set threshold, initiates a data validation sequence; if the primary sensor reading is deemed erroneous, the system fails over to a redundant sensor path. Upon confirmed over-temperature from either sensor, the controller activates multiple PWM fans, managed by a priority-based task, while a separate periodic task, driven by a timer interrupt, monitors the thermal trajectory. If the temperature fails to descend within a defined window, a higher-priority task initializes the liquid-cooling loop to augmen
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEFFEE skinparam ActivityBorderColor #006600 skinparam PartitionBackgroundColor #F0F8FF skinparam PartitionBorderColor #00008B  title Thermal Management Controller - RTOS State Machine  |Main Controller| start :Execute as state machine on RTOS;  |ISR: Temp Sensor| :Trigger on external ambient > threshold; :Initiate data validation sequence;  |Main Controller| if (Primary sensor erroneous?) then (Yes)   :Failover to redundant sensor path; else (No)   :Use primary sensor reading; endif  if (Confirmed over-temperature?) then (Yes)   :Activate PWM fans via priority-based task;      |Timer ISR|   :Trigger periodic task;      |

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
