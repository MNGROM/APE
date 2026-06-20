# Prompt Evaluation Analysis

## Summary
- count: 56
- syntax_pass_rate: 0.9821
- infrastructure_error_rate: 0.0000
- node_precision: 0.1342
- node_recall: 0.2230
- node_f1: 0.1617
- relation_precision: 0.0411
- relation_recall: 0.0704
- relation_f1: 0.0509
- plantuml_compilation_pass_rate: 0.9821
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- extra_activity: 56
- extra_or_wrong_relation: 56
- missing_activity: 55
- missing_or_wrong_relation: 55
- wrong_loop: 10
- syntax_error: 1

## Representative Failure Cases
### lmc-0033
- dataset: lmc
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.1250
- relation_f1: 0.0000
- missing_nodes:
  - in nlguidance
  - output consistent aim point with static target
  - output consistent aim point with static target
  - aim point switching
  - change with t sample period > (quantity + velocity
  - erratic changes in aim point command
- extra_nodes:
  - nlguidance receives static target input
  - is aim point switching occurring?
  - output aim point command with transient behavior
  - calculate tolerance for transient behavior
  - calculate change in magnitude of output over one frame (t)
  - change in magnitude > tolerance?
  - appreciable transient behavior detected
  - output consistent aim point command
- missing_relations:
  - in nlguidance -> output consistent aim point with static target
  - output consistent aim point with static target -> transient is required to maintain counter clockwise loiter?
  - transient is required to maintain counter clockwise loiter? -> aim point switching
  - aim point switching -> change with t sample period > (quantity + velocity
  - change with t sample period > (quantity + velocity -> erratic changes in aim point command
  - erratic changes in aim point command -> output consistent aim point with static target
- input_excerpt:
  6.	NLGuidance shall output consistent aim point with a static target without appreciable transient behavior in the command generation other than aim point switching where a transient is required to maintain a counter clockwise loiter (ref requirement 3).  Appreciable transient behavior is defined as erratic changes in the aim point command, beyond the following specific tolerance: a.	The change in the magnitude of the output over one frame of execution with T sample period shall not exceed the quantity of the combined velocity of the target plus the velocity of the vehicle multiplied by T.
- generated_excerpt:
  @startuml start  :NLGuidance receives static target input;  if (Is aim point switching occurring?) then (Yes)   :Output aim point command with transient behavior;   :Transient required to maintain counter clockwise loiter (ref req 3); else (No)   :Calculate tolerance for transient behavior;   note right     Tolerance = (Target Velocity + Vehicle Velocity) * T     (where T is the sample period)   end note;      :Calculate change in magnitude of output over one frame (T);      if (Change in magnitude > Tolerance?) then (Yes)     :Appreciable transient behavior detected;     #Pink:Erratic change in aim point command;     stop   else (No)     :Output consistent aim point command;   endif endif  
### lmc-0008
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - sensor data is good?
  - autopilot change states from nominal to maneuver
- missing_relations:
  - sensor data is good? -> autopilot change states from nominal to maneuver
- input_excerpt:
  4.	The autopilot shall change states from NOMINAL to MANEUVER when the sensor data is not good.
- generated_excerpt:
  @startuml skinparam style strictuml  state NOMINAL state MANEUVER  [*] --> NOMINAL  NOMINAL --> MANEUVER : sensor data is not good  @enduml
### lmc-0012
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - pilot is not in control (not standby
  - autopilot change states from standby to transition
- extra_nodes:
  - autopilot in standby state
  - is pilot in control (standby
  - remain in standby
  - change state to transition
- missing_relations:
  - pilot is not in control (not standby -> autopilot change states from standby to transition
- input_excerpt:
  8.	The autopilot shall change states from STANDBY to TRANSITION when the pilot is not in control (not standby).
- generated_excerpt:
  @startuml skinparam style strictuml title Autopilot State Change: STANDBY to TRANSITION  start :Autopilot in STANDBY state; if (Is pilot in control (standby)?) then (Yes)   :Remain in STANDBY;   stop else (No)   :Change state to TRANSITION;   stop endif @enduml
### lmc-0013
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - a failure occurs (apfail
  - autopilot change states from standby to maneuver
- missing_relations:
  - a failure occurs (apfail -> autopilot change states from standby to maneuver
- input_excerpt:
  9.	The autopilot shall change states from STANDBY to MANEUVER when a failure occurs (apfail).
- generated_excerpt:
  @startuml skinparam style strictuml  state STANDBY state MANEUVER  STANDBY --> MANEUVER : apfail @enduml
### lmc-0016
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - autopilot is not requesting support (not request
  - limits are not exceeded (not limits
  - sensor change states from fault to transition
- extra_nodes:
  - sensor state fault
  - autopilot requesting support?
  - remain in fault
  - remain in fault
  - limits exceeded?
  - change state to transition
- missing_relations:
  - autopilot is not requesting support (not request -> limits are not exceeded (not limits
  - limits are not exceeded (not limits -> sensor change states from fault to transition
- input_excerpt:
  12.	The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting support (not request) and limits are not exceeded (not limits).
- generated_excerpt:
  @startuml start :Sensor State: FAULT; if (Autopilot requesting support?) then (Yes)   :Remain in FAULT; else (No - not request)   if (Limits exceeded?) then (Yes)     :Remain in FAULT;   else (No - not limits)     :Change state to TRANSITION;   endif endif @enduml
### lmc-0018
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - in inner loop roll regulator
  - durations > 100 frames?
  - command angular roll accelerations <= 50 deg/sec2
- extra_nodes:
  - inner loop roll regulator commands angular roll acceleration
  - is commanded roll acceleration > 50 deg/sec ?
  - allow commanded roll acceleration
  - allow commanded roll acceleration
  - reset duration counter
  - reset duration counter
  - start/continue duration counter (in frames 100hz)
  - does duration exceed 100 frames (1 second
- missing_relations:
  - in inner loop roll regulator -> durations > 100 frames?
  - durations > 100 frames? -> command angular roll accelerations <= 50 deg/sec2
- input_excerpt:
  1.	The Inner Loop Roll Regulator Shall not command angular roll accelerations greater than the capability of the system (50 deg/sec2) for durations exceeding 100 frames (1 second @ 100 hz).
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #E8F5E9 skinparam ActivityBorderColor #2E7D32  title Inner Loop Roll Regulator - Roll Acceleration Limitation  start  :Inner Loop Roll Regulator\ncommands angular roll acceleration;  if (Is commanded roll acceleration\n> 50 deg/sec²?) then (No)   :Allow commanded\nroll acceleration;   :Reset duration counter; else (Yes)   :Start/Continue duration counter\n(in frames @ 100Hz);      if (Does duration exceed\n100 frames (1 second)?) then (No)     :Allow commanded\nroll acceleration;   else (Yes)     :Limit/Cap roll acceleration\nto ≤ 50 deg/sec²;     :Reset duration counter;   endif endif  stop @enduml
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
  - is commanded acceleration > 50 deg/sec ?
  - acceleration exceeds system capability
  - start/continue frame counter for duration at > 50 deg/sec
  - does duration exceed 100 frames (1 second 100 hz
  - trigger violation commanded acceleration > capability for > 100 frames
  - duration within limits
  - continue monitoring
- missing_relations:
  - in inner loop pitch regulator -> durations > 100 frames?
  - durations > 100 frames? -> command angular pitch accelerations <= 50 deg/sec2
- input_excerpt:
  2.	The Inner Loop Pitch Regulator Shall not command angular pitch accelerations greater than the capability of the system (50 deg/sec2) for durations exceeding 100 frames (1 second @ 100 hz).
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor White skinparam ActivityBorderColor Black  start  :Inner Loop Pitch Regulator commands angular pitch acceleration;  if (Is commanded acceleration > 50 deg/sec²?) then (Yes)   :Acceleration exceeds system capability;   :Start/continue frame counter for duration at > 50 deg/sec²;   if (Does duration exceed 100 frames (1 second @ 100 Hz)?) then (Yes)     :Trigger violation: Commanded acceleration > capability for > 100 frames;     stop   else (No)     :Duration within limits;     :Continue monitoring;     stop   endif else (No)   :Acceleration within system capability;   :Reset frame counter for > 50 deg/sec²;   :Continue monitoring;   stop endif  @en
### lmc-0020
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - in inner loop yaw regulator
  - durations > 100 frames?
  - command angular yaw accelerations <= 50 deg/sec2
- extra_nodes:
  - inner loop yaw regulator commands angular yaw acceleration
  - is commanded yaw acceleration > 50 deg/sec ?
  - allow command
  - reset duration counter
  - reset duration counter
  - increment duration counter
  - has duration exceeded 100 frames (1 second
  - allow command temporarily
- missing_relations:
  - in inner loop yaw regulator -> durations > 100 frames?
  - durations > 100 frames? -> command angular yaw accelerations <= 50 deg/sec2
- input_excerpt:
  3.	The Inner Loop Yaw Regulator Shall not command angular yaw accelerations greater than the capability of the system (50 deg/sec2) for durations exceeding 100 frames (1 second @ 100 hz).
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #E8F5E9 skinparam ActivityBorderColor #1B5E20  start  :Inner Loop Yaw Regulator\ncommands angular yaw acceleration;  if (Is commanded yaw acceleration\n> 50 deg/sec²?) then (No)   :Allow command;   :Reset duration counter; else (Yes)   :Increment duration counter;      if (Has duration exceeded\n100 frames (1 second)?) then (No)     :Allow command temporarily;   else (Yes)     :Reject / Limit command\n(Enforce system capability);     :Reset duration counter;   endif endif  stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
