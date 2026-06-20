# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.8000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3815
- node_recall: 0.4160
- node_f1: 0.3581
- relation_precision: 0.2905
- relation_recall: 0.3183
- relation_f1: 0.2901
- plantuml_compilation_pass_rate: 0.8000
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_activity: 8
- extra_activity: 8
- missing_or_wrong_relation: 8
- extra_or_wrong_relation: 8
- syntax_error: 2
- wrong_loop: 1

## Representative Failure Cases
### fsd-0114
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - swipe card for entrance
  - verify user
  - valid?
  - on lights
  - activate sensor
  - activate sensor
  - set ac
  - check temperature
- extra_nodes:
  - swipe card for identity verification
  - card valid?
  - deny access
  - turn on the lights
  - start the ac
  - temperature condition?
  - close the blinds
  - set ac to high fan speed
- missing_relations:
  - swipe card for entrance -> verify user
  - verify user -> valid?
  - valid? -> on lights
  - on lights -> activate sensor
  - activate sensor -> set ac
  - set ac -> check temperature
  - check temperature -> hot
  - hot -> close blinds and set ac to high
- input_excerpt:
  When a user attempts to enter the system, they must first swipe a card to complete identity verification. If the card is invalid, the system will deny access and terminate the flow; if the card is valid, the system will first turn on the lights, start the air conditioning (AC), and then execute subsequent steps in parallel. Based on current temperature conditions, the system will make the following adjustments: if it is hot, the system will close the blinds and set the AC to high fan speed; if normal, it will set the AC to medium fan speed; if cloudy, it will turn off the AC and open the blinds. Simultaneously with temperature detection, the system will activate environmental sensors for rea
- generated_excerpt:
  @startuml start partition User {     :Swipe card for identity verification; } partition System {     if (Card valid?) then (no)         :Deny access;         stop     else (yes)         :Turn on the lights;         :Start the AC;         fork             if (Temperature condition?) then (hot)                 :Close the blinds;                 :Set AC to high fan speed;             else (normal)                 :Set AC to medium fan speed;             else (cloudy)                 :Turn off the AC;                 :Open the blinds;             endif         fork again             :Activate environmental sensors for real-time monitoring;             if (Smoke detected?) then (yes)             
### rac-0004
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.5000
- relation_f1: 0.1852
- missing_nodes:
  - slow charging state is 1 and charging/discharging power-up is ready
  - vehicle charging/discharging mode is 2 and power-up is ready
  - switch to state 105
  - condition judgement
  - high-voltage shutdown charging/discharging value is 3 or 4
  - slow charging?
  - slow charging?
  - slow charging?
- extra_nodes:
  - system starts up
  - slow charging is active (state 1
  - vehicle charging/discharging mode is 2 and system is powered up?
  - high-voltage shutdown value is 3 or 4?
  - slow charging becomes inactive?
  - slow charging becomes inactive?
  - slow charging becomes inactive?
  - slow charging becomes inactive?
- missing_relations:
  - slow charging state is 1 and charging/discharging power-up is ready -> switch to state 95
  - switch to state 95 -> vehicle charging/discharging mode is 2 and power-up is ready
  - vehicle charging/discharging mode is 2 and power-up is ready -> switch to state 105
  - switch to state 105 -> condition judgement
  - condition judgement -> high-voltage shutdown charging/discharging value is 3 or 4
  - high-voltage shutdown charging/discharging value is 3 or 4 -> switch to state 115
  - switch to state 115 -> slow charging?
  - switch to state 115 -> slow charging?
- input_excerpt:
  After the system starts up: - If slow charging is active (state 1) and the charging/discharging system is powered up, switch to state 95. - If the vehicle charging/discharging mode is 2 and the system is powered up, switch to state 105. Then, while in state 105:   1) If the high-voltage shutdown value is 3 or 4, switch to state 115. If slow charging becomes inactive during this, shut down and end the process.   2) If a high-voltage shutdown request (value 3) occurs while the ignition is on (position 2), return to state 105. If the ignition turns off (position 0), switch to state 115. If slow charging becomes inactive, shut down and end.   3) If a pre-charge failure happens, switch to state 1
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active (state 1)\nand charging/discharging system is powered up?) then (yes)   :Switch to state 95; elseif (Vehicle charging/discharging mode is 2\nand system is powered up?) then (yes)   :Switch to state 105;   repeat     if (High-voltage shutdown value is 3 or 4?) then (yes)       :Switch to state 115;       if (Slow charging becomes inactive?) then (yes)         :Shut down;         end       endif     elseif (High-voltage shutdown request (value 3) occurs\nand ignition is on (position 2)?) then (yes)       :Return to state 105;       if (Slow charging becomes inactive?) then (yes)         :Shut down;         end       endif     elsei
### lmc-0037
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - use first order finite backward difference equation
  - n index to current values
  - n-1 prior values
  - included truth data for xt and yt
  - z/ xt = (z(n 1)-z(n-1))/(xt(n 1)-xt(n-1 1))
  - z/ yt = (z(n 1)-z(n-1))/(yt(n 1)-yt(n-1 1))
  - -35 <= spatial derivatives <= 10?
  - allowed
- extra_nodes:
  - z/ xt > +10?
  - enforce top bound z/ xt = +10
  - z/ xt < -35?
  - enforce bottom bound z/ xt = -35
  - z/ yt > +10?
  - enforce top bound z/ yt = +10
  - z/ yt < -35?
  - enforce bottom bound z/ yt = -35
- missing_relations:
  - use first order finite backward difference equation -> n index to current values
  - n index to current values -> n-1 prior values
  - n-1 prior values -> included truth data for xt and yt
  - included truth data for xt and yt -> z/ xt = (z(n 1)-z(n-1))/(xt(n 1)-xt(n-1 1))
  - z/ xt = (z(n 1)-z(n-1))/(xt(n 1)-xt(n-1 1)) -> z/ yt = (z(n 1)-z(n-1))/(yt(n 1)-yt(n-1 1))
  - z/ yt = (z(n 1)-z(n-1))/(yt(n 1)-yt(n-1 1)) -> -35 <= spatial derivatives <= 10?
  - -35 <= spatial derivatives <= 10? -> allowed
  - allowed -> not allowed
- input_excerpt:
  3.	Using a first order finite backward difference equation, the spatial derivatives of Δz/ Δxt = (z(n,1)-z(n-1))/(xt(n,1)-xt(n-1,1) and Δz/ Δyt = (z(n,1)-z(n-1))/(yt(n,1)-yt(n-1,1) shall never exceed a top bound of +10 or bottom bound of -35 (e.g. -35 <= Δz/ Δ(xt,yt) <= 10), where n denotes an index to the current values and n-1 denotes the prior values in the included truth data for xt and yt.
- generated_excerpt:
  @startuml start partition "System" {   :Compute Δz/Δxt using first order finite backward difference:   (z(n,1) - z(n-1)) / (xt(n,1) - xt(n-1,1));   :Compute Δz/Δyt using first order finite backward difference:   (z(n,1) - z(n-1)) / (yt(n,1) - yt(n-1,1));   if (Δz/Δxt > +10?) then (yes)     :Enforce top bound: Δz/Δxt = +10;   elseif (Δz/Δxt < -35?) then (yes)     :Enforce bottom bound: Δz/Δxt = -35;   else (no)   endif   if (Δz/Δyt > +10?) then (yes)     :Enforce top bound: Δz/Δyt = +10;   elseif (Δz/Δyt < -35?) then (yes)     :Enforce bottom bound: Δz/Δyt = -35;   else (no)   endif } stop @enduml
### lmc-0042
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - 2-norm of output buminusd
  - < 0.01?
  - allowed
  - not allowed
- extra_nodes:
  - compute 2-norm of buminusd
  - 2-norm of buminusd < 0.01?
  - pass
  - fail
- missing_relations:
  - 2-norm of output buminusd -> < 0.01?
  - < 0.01? -> allowed
  - allowed -> not allowed
- input_excerpt:
  4.	The 2-norm of the output Buminusd should be less than 0.01.
- generated_excerpt:
  @startuml start :Compute 2-norm of Buminusd; if (2-norm of Buminusd < 0.01?) then (yes)   :Pass; else (no)   :Fail; endif stop @enduml
### us-0008
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.0000
- missing_nodes:
  - give advanced notice to ensure buy-in
- extra_nodes:
  - give testers advanced notice
  - testers buy-in?
  - confirm user testing
  - reschedule user testing
- missing_relations:
  - schedule user testing -> give advanced notice to ensure buy-in
- input_excerpt:
  As a UI designer, I want to schedule user testing, so that I can give the testers advanced notice to ensure buy-in.
- generated_excerpt:
  @startuml |UI Designer| start :Schedule user testing; :Give testers advanced notice; if (Testers buy-in?) then (Yes)   :Confirm user testing; else (No)   :Reschedule user testing; endif stop @enduml
### fsd-0050
- dataset: fsd
- failure_types: missing_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.0588
- missing_nodes:
  - thermal management controller implemented as deterministic state machine on rtos
  - govern pwm fans
  - govern liquid-cooling loops
  - high-priority task synchronized via mutexes with bms/pmic interface
  - ensure operational parameters within safe bounds
  - medium-priority periodic task scheduled by rtos
  - poll indoor temperature sensors
  - setpoint achieved?
- extra_nodes:
  - return to low-power standby state
- missing_relations:
  - thermal management controller implemented as deterministic state machine on rtos -> govern pwm fans
  - govern pwm fans -> govern liquid-cooling loops
  - govern liquid-cooling loops -> receive user-initiated air conditioner start command
  - unit in powered-off state? -> indoor temperature > setpoint?
  - indoor temperature > setpoint? -> execute air conditioner startup sequence
  - execute air conditioner startup sequence -> high-priority task synchronized via mutexes with bms/pmic interface
  - high-priority task synchronized via mutexes with bms/pmic interface -> continuously monitor compressor status and condenser temperature
  - continuously monitor compressor status and condenser temperature -> ensure operational parameters within safe bounds
- input_excerpt:
  The thermal management controller, implemented as a deterministic state machine on the RTOS, governs the PWM fans and liquid-cooling loops. Upon receiving a user-initiated air conditioner start command, the system first verifies the unit is in a powered-off state and then checks if the indoor temperature exceeds the setpoint. If both conditions are met, it executes the air conditioner startup sequence, during which a high-priority task, synchronized via mutexes with a BMS/PMIC interface, continuously monitors the compressor status and condenser temperature to ensure operational parameters remain within safe bounds. A medium-priority periodic task, scheduled by the RTOS, polls indoor temperat
- generated_excerpt:
  @startuml start partition "Thermal Management Controller" {     :Receive user-initiated air conditioner start command;     if (Is unit in powered-off state?) then (No)         :Return to low-power standby state;         stop     else (Yes)         if (Does indoor temperature exceed setpoint?) then (No)             :Return to low-power standby state;             stop         else (Yes)             :Execute air conditioner startup sequence;             fork                 :Continuously monitor compressor status and condenser temperature;                 note right: High-priority task\n(synchronized via mutexes with BMS/PMIC interface)             fork again                 repeat             
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4167
- relation_f1: 0.4348
- missing_nodes:
  - switch to state 93
  - switch to state 95
  - switch to state 105
  - switch to state 105
  - switch to state 105
  - switch to state 105
  - condition judgement
  - remote mode is closed
- extra_nodes:
  - system startup
  - transition to state 93
  - move to state 95
  - proceed to state 105
  - go to state 105
  - slow charging becomes inactive?
  - remote mode deactivates?
  - initiate shutdown
- missing_relations:
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - power-up is ready and vehicle charging/discharging mode is 2 -> switch to state 105
  - switch to state 105 -> condition judgement
  - condition judgement -> in remote mode
  - switch to state 28 -> remote mode is closed
  - remote mode is closed -> shutdown
  - shutdown -> pet mode request is received
  - pet mode request is received -> switch to state 105
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System startup;  if (Slow charging is active\nand front MCU high-voltage detection flag is 0?) then (Yes)   :Transition to state 93; elseif (Charging/discharging power-up is active\nand front MCU high-voltage detection flag is 1?) then (Yes)   :Move to state 95; elseif (Power-up readiness is confirmed\nand vehicle charging/discharging mode is 2?) then (Yes)   :Proceed to state 105; endif  if (In remote mode?) then (Yes)   :Go to state 105;   if (Slow charging becomes inactive?) then (Yes)     :Shift to state 28;   endif   if (Remote mode deactivates?) then (Yes)     :Initiate shutdown;     stop   endif elseif (Received pet mode request?) then (Yes)   :Enter state 105;   if (
### pure-0010
- dataset: pure
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- missing_nodes:
  - save trade instruction
- extra_nodes:
  - save the trade information
- input_excerpt:
  1. central trading system: give out the successful trade information 2. security account management: save the trade information
- generated_excerpt:
  @startuml partition "Central Trading System" {   :Give out the successful trade information; } partition "Security Account Management" {   :Save the trade information; } @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
