# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.8000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2179
- node_recall: 0.2385
- node_f1: 0.2168
- relation_precision: 0.1065
- relation_recall: 0.1068
- relation_f1: 0.1051
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
- missing_activity: 10
- extra_activity: 10
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10
- syntax_error: 2
- wrong_loop: 2

## Representative Failure Cases
### fsd-0095
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.2500
- relation_f1: 0.1053
- missing_nodes:
  - tcms operates on preemptive rtos
  - manage subsystems with deterministic scheduling via priority queues
  - traction
  - braking
  - door
  - diagnostics
  - station arrival?
  - initiate cyclic control process
- extra_nodes:
  - station arrival detected
  - telemetry logger task (async) log events to ring buffer for nvm archival
  - watchdog pmic/bms task enforce graceful degradation (en 50128/en 50129 compliance)
  - safety-critical monitoring task (high-priority / isr-triggered) monitor passenger egress/ingress
  - cyclic control process 1. monitor door switch status 2. check locking mechanism (can bus message + crc)
  - acquire mutex
  - update mutex-protected state variable (signal readiness for departure)
  - release mutex
- missing_relations:
  - tcms operates on preemptive rtos -> manage subsystems with deterministic scheduling via priority queues
  - manage subsystems with deterministic scheduling via priority queues -> traction
  - traction -> braking
  - braking -> door
  - door -> diagnostics
  - diagnostics -> station arrival?
  - station arrival? -> verify door status via dedicated monitoring task
  - issue door closure command -> initiate cyclic control process
- input_excerpt:
  The Train Control and Monitoring System (TCMS), executing on a preemptive RTOS, coordinates traction, braking, door management, and diagnostic subsystems via deterministic scheduling and priority queues. Upon station arrival, the system first verifies door status via a dedicated monitoring task. If any door is detected as open, a door closure command is issued, initiating a cyclic control process that iteratively monitors the door switch status and checks the locking mechanism via a CAN bus message with a confirming CRC until a fully closed and locked state is achieved. Concurrently, a high-priority task, potentially serviced by an ISR from platform sensors, performs safety-critical monitori
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #LightYellow skinparam ActivityDiamondBackgroundColor #LightBlue  title TCMS: Station Arrival, Door Management, and Departure Sequence  start  :Station Arrival Detected;  fork   :Telemetry Logger Task (Async)\nLog events to Ring Buffer\nfor NVM Archival; fork again   :Watchdog & PMIC/BMS Task\nEnforce Graceful Degradation\n(EN 50128/EN 50129 Compliance); end fork  :Verify Door Status\n(Dedicated Monitoring Task);  if (Any Door Open?) then (Yes)   :Issue Door Closure Command;    repeat     fork       :Safety-Critical Monitoring Task\n(High-Priority / ISR-triggered)\nMonitor Passenger Egress/Ingress;     fork again       :Cyclic Control Process:\n1. 
### rac-0019
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4118
- relation_f1: 0.1212
- missing_nodes:
  - switch to state 30
  - switch to state 49
  - switch to state 49
  - switch to state 49
  - switch to state 49
  - switch to state 49
  - charging system command=4
  - switch to state 29
- extra_nodes:
  - system startup
  - state 30
  - state 49
  - state 49
  - state 49
  - state 49
  - state 49
  - state 29
- missing_relations:
  - ignition switch=2 -> switch to state 30
  - switch to state 30 -> ignition switch=0
  - ignition switch=0 -> switch to state 49
  - switch to state 49 -> fast charge vcc2=6
  - charging system command=4 -> switch to state 29
  - charging system command=4 -> switch to state 29
  - switch to state 29 -> ignition switch=0 and vcc2=12
  - ignition switch=0 and vcc2=12 -> switch to state 49
- input_excerpt:
  After the system starts up, if the ignition switch is set to 2, transition to state 30. Then, under that condition: - If the ignition switch becomes 0, move to state 49 and exit. - If the fast charge Vcc2 is 6, observe the charging gun indicator. Should the charging system command be 4, switch to state 29. - If the ignition switch is 0 and Vcc2 is 12, proceed to state 49 and exit. - If slow charging is active and the charging system command is 1, transition to state 110. If the command is 4 instead, go to state 29. Also, if the ignition switch is 0 and slow charging is not active, shift to state 49 and exit.  If remote mode is enabled, switch to state 28. If it's disabled, transition to stat
- generated_excerpt:
  @startuml start :System Startup; if (Ignition switch == 2?) then (Yes)   :State 30;   if (Ignition switch == 0?) then (Yes)     :State 49;     exit   elseif (Fast charge Vcc2 == 6?) then (Yes)     :Observe charging gun indicator;     if (Charging system command == 4?) then (Yes)       :State 29;       stop     else (No)       stop     endif   elseif (Ignition switch == 0 and Vcc2 == 12?) then (Yes)     :State 49;     exit   elseif (Slow charging active and Charging system command == 1?) then (Yes)     :State 110;     stop   elseif (Slow charging active and Charging system command == 4?) then (Yes)     :State 29;     stop   elseif (Ignition switch == 0 and Slow charging not active?) then (Yes
### lmc-0028
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - in nlguidance
  - maintain target on vehicle port-side
- extra_nodes:
  - vehicle is operating
  - detect target position
  - calculate relative bearing of target
  - is target on port-side?
  - maintain current course
  - adjust vehicle heading
- missing_relations:
  - in nlguidance -> maintain target on vehicle port-side
- input_excerpt:
  1.	NLGuidance shall always maintain the target on the port-side of the vehicle.
- generated_excerpt:
  @startuml start :Vehicle is operating; repeat   :Detect target position;   :Calculate relative bearing of target;   if (Is target on port-side?) then (Yes)     :Maintain current course;   else (No)     :Adjust vehicle heading;     note right: Turn to move target\nto port-side   endif repeat while (Vehicle is operating) is (Yes) ->No; stop @enduml
### pure-0007
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - give buy instruction
  - save buy instruction
  - match instructions with same stock id
  - make a trade by matching
  - modify information of matched instructions
- extra_nodes:
  - transaction user interface give the buy instruction
  - central trading system save the buy instruction
  - central trading system match the instructions with the same stock id
  - central trading system make a trade by matching
  - central trading system modify the information of matched instructions
- missing_relations:
  - give buy instruction -> save buy instruction
  - save buy instruction -> match instructions with same stock id
  - match instructions with same stock id -> make a trade by matching
  - make a trade by matching -> modify information of matched instructions
- input_excerpt:
  1. transaction user interface: give the buy instruction 2. central trading system: save the buy instruction 3. central trading system: match the instructions with the same stock id 4. central trading system: make a trade by matching 5. central trading system: modify the information of matched instructions
- generated_excerpt:
  @startuml start :Transaction User Interface: Give the buy instruction; :Central Trading System: Save the buy instruction; :Central Trading System: Match the instructions with the same stock id; :Central Trading System: Make a trade by matching; :Central Trading System: Modify the information of matched instructions; stop @enduml
### us-0062
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - begin identifying interview candidates
  - understand what educators and science influencers need
- extra_nodes:
  - access nsf.gov research portal
  - initiate participant identification process
  - search and compile list of potential participants
  - review candidate profiles for relevance
  - candidates meet criteria?
  - add candidates to interview participant list
  - exclude candidates
  - finalize initial participant list
- missing_relations:
  - begin identifying interview candidates -> understand what educators and science influencers need
- input_excerpt:
  As a user researcher, I want to begin identifying interview participants, so that I can understand what educators and science influencers need from a future nsf.gov website.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Access nsf.gov research portal;  :Initiate participant identification process;  :Define target audience criteria (Educators, Science Influencers);  :Search and compile list of potential participants;  :Review candidate profiles for relevance;  if (Candidates meet criteria?) then (Yes)   :Add candidates to interview participant list; else (No)   :Exclude candidates;   stop endif  :Finalize initial participant list;  :Prepare for interviews to gather nsf.gov website needs;  stop @enduml
### us-0099
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - showcase published examples
  - get useful and simple datapackage format and registry
- extra_nodes:
  - publisher visits the registry
  - browse list of published packages
  - select a specific package to view
  - view real examples of published packages
  - is the datapackage format clear and simple?
  - understand the usefulness and simplicity of the format
  - explore additional package examples
- missing_relations:
  - showcase published examples -> get useful and simple datapackage format and registry
- input_excerpt:
  As a Publisher, I want to see real examples of published packages so that I can understand how useful and simple the datapackage format and the registry is.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Publisher visits the registry;  :Browse list of published packages;  :Select a specific package to view;  :View real examples of published packages;  if (Is the datapackage format clear and simple?) then (Yes)   :Understand the usefulness and simplicity of the format; else (No)   :Explore additional package examples;   note right: Repeat until understood endif  stop @enduml
### fsd-0108
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2400
- relation_f1: 0.0833
- missing_nodes:
  - embedded communications layer validates incoming can frames by
  - check id
  - check dlc
  - check crc
  - subsequent processing
  - supervisory control task scheduled by rtos
  - continuously evaluate
  - current operational state of device
- extra_nodes:
  - receive can frame
  - validate can frame (id dlc crc)
  - valid frame?
  - discard frame
  - current operational state?
  - idle
  - active
  - preempt current operation
- missing_relations:
  - embedded communications layer validates incoming can frames by -> check id
  - check id -> check dlc
  - check dlc -> check crc
  - check crc -> place into lock-free ring buffers
  - place into lock-free ring buffers -> subsequent processing
  - subsequent processing -> supervisory control task scheduled by rtos
  - supervisory control task scheduled by rtos -> manage device access requests from multiple sources
  - arbitrate requests based on priority scheme -> continuously evaluate
- input_excerpt:
  The embedded communications layer validates incoming CAN frames by checking the ID, DLC, and CRC before placing them into lock-free ring buffers for subsequent processing. A supervisory control task, scheduled by the RTOS, manages device access requests from multiple sources; it arbitrates these requests based on a priority scheme, continuously evaluating both the request priority and the current operational state of the device (e.g., idle or active). If the device is idle, all pending requests are serviced from a priority queue. However, if the device is already active, the system enters a state where high-priority requests preempt the current operation, while lower-priority requests are ma
- generated_excerpt:
  @startuml skinparam style strictuml  title Embedded Communications and Control System  start  partition "CAN Communication Layer" {     :Receive CAN Frame;     :Validate CAN Frame (ID, DLC, CRC);     if (Valid Frame?) then (Yes)         :Place into Lock-Free Ring Buffer;     else (No)         :Discard Frame;         stop     endif }  partition "Supervisory Control Task (RTOS Scheduled)" {     :Manage Device Access Requests from Multiple Sources;     :Arbitrate based on Priority Scheme;          switch (Current Operational State?)     case ( Idle )         :Service all pending requests\nfrom Priority Queue;     case ( Active )         if (Request Priority?) then (High)             :Preempt Cu
### lmc-0025
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- missing_nodes:
  - in inner loop yaw regulator
- extra_nodes:
  - inner loop yaw regulator computes yaw control commands
  - calculate commanded transient change in angular yaw acceleration
  - clamp/limit command to ensure transient change does not exceed 50 deg/sec /sec
  - pass command unchanged
  - output yaw command to system actuators
- missing_relations:
  - in inner loop yaw regulator -> command transient changes in angular yaw acceleration <= 50 deg/sec2/sec
- input_excerpt:
  8.	The Inner Loop Yaw Regulator Shall not command transient changes in angular yaw acceleration greater than 50 deg/sec2/sec.
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityBorderColor #0044AA skinparam NoteBorderColor #0044AA skinparam NoteBackgroundColor #FFFDE7  title Inner Loop Yaw Regulator: Transient Angular Yaw Acceleration Limit  start  :Inner Loop Yaw Regulator\ncomputes yaw control commands;  :Calculate commanded\ntransient change in\nangular yaw acceleration;  if (Is commanded transient change\nin angular yaw acceleration\n> 50 deg/sec²/sec?) then (Yes)   :Clamp/limit command to ensure\ntransient change does not exceed\n50 deg/sec²/sec;   note right     **Requirement Constraint**     Shall not command transient changes     in angular yaw acceleration     greater than 50 deg/sec²/se

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
