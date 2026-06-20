# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2801
- node_recall: 0.2463
- node_f1: 0.2592
- relation_precision: 0.1599
- relation_recall: 0.1359
- relation_f1: 0.1460
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
- missing_activity: 10
- extra_activity: 10
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10
- wrong_parallel: 2
- wrong_loop: 2

## Representative Failure Cases
### lmc-0041
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - output u vector
  - 5x1 vector?
  - allowed
  - not allowed
- extra_nodes:
  - create u vector as a 5x1 vector
- missing_relations:
  - output u vector -> 5x1 vector?
  - 5x1 vector? -> allowed
  - allowed -> not allowed
- input_excerpt:
  3.	The output u vector should be a 5x1 vector.
- generated_excerpt:
  @startuml start :Create u vector as a 5x1 vector; stop @enduml
### us-0182
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - indicate subject pertinent to the component
- extra_nodes:
  - select component
  - indicate pertinent subject
- input_excerpt:
  As a repository manager, I want to indicate any subject that is pertinent to the component.
- generated_excerpt:
  @startuml start partition "Repository Manager" {   :Select component;   :Indicate pertinent subject; } stop @enduml
### us-0196
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - allow users to log in using active directory credentials
  - avoid managing set of usernames and passwords
- extra_nodes:
  - configure active directory integration
  - receive login request
  - validate credentials
  - credentials valid?
  - authenticate user
  - grant access
  - deny access
- missing_relations:
  - allow users to log in using active directory credentials -> avoid managing set of usernames and passwords
- input_excerpt:
  As an administrator, I want to allow users to log in using Active Directory credentials, so that I don't have to manage another set of usernames and passwords.
- generated_excerpt:
  @startuml |Administrator| start :Configure Active Directory integration;  |System| :Receive login request;  |Active Directory| :Validate credentials;  |System| if (Credentials valid?) then (yes)   :Authenticate user;   :Grant access; else (no)   :Deny access; endif  stop @enduml
### pure-0017
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1429
- relation_f1: 0.0000
- missing_nodes:
  - leading driver initiate automated request
  - require driver enter train number information?
  - display information entered
  - confirmation?
  - further actions
  - automated request is initiated?
  - accept/reject train number returned
  - ertms/etcs and radio systems available?
- extra_nodes:
  - registration method?
  - show entered train number on display
  - confirm train number
  - initiate automated request
  - return train number
  - accept returned train number?
  - accept train number
  - reject train number
- missing_relations:
  - enter train number -> leading driver initiate automated request
  - leading driver initiate automated request -> register and deregister train number
  - register and deregister train number -> require driver enter train number information?
  - require driver enter train number information? -> display information entered
  - display information entered -> confirmation?
  - confirmation? -> further actions
  - further actions -> automated request is initiated?
  - automated request is initiated? -> accept/reject train number returned
- input_excerpt:
  5.2.3.26 It shall be possible for the driver to register and deregister a train number in the following ways: 1) enter train number; (M) 2) initiate automated request (applicable only for leading driver). (O) 5.2.3.27 Where the driver is required to enter the train number information, the information entered shall be shown on the display and require confirmation by the driver before further actions are possible. (M) 5.2.3.28 If an automated request is initiated (option 2), the driver shall be able to accept or reject the train number returned by the network. (M) 5.2.3.28i Where ERTMS/ETCS and radio systems are available and the driver is required to enter the train number as part of the init
- generated_excerpt:
  @startuml start  partition Driver {     :Register or deregister train number; }  if (Registration method?) then (Enter train number)     partition Driver {         :Enter train number;     }     partition Display {         :Show entered train number on display;     }     partition Driver {         :Confirm train number;     } else (Initiate automated request)     partition Driver {         :Initiate automated request;     }     partition Network {         :Return train number;     }     partition Driver {         if (Accept returned train number?) then (Accept)             :Accept train number;         else (Reject)             :Reject train number;             stop         endif     } endif
### pure-0015
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.1212
- missing_nodes:
  - initiate operations
  - automatic pre-set loudspeaker volume selection
  - other on-train system registration
  - record all self_tests failures
  - connect to last registered mobile network?
  - succeed?
  - display network name
  - give audible indication
- extra_nodes:
  - automatic selection of the pre-set loudspeaker volume
  - registration with other on-train systems such as ertms/etcs
  - connection of the cab radio to an authorised mobile network (network to which the mobile was last registered where available)
  - self-test failures?
  - record failures in the train-borne recorder
  - connection successful?
  - display the name of the network on the mmi
  - give an audible indication of successful connection
- missing_relations:
  - power up cab radio -> initiate operations
  - initiate operations -> automatic self-testing
  - automatic self-testing -> automatic pre-set loudspeaker volume selection
  - automatic pre-set loudspeaker volume selection -> other on-train system registration
  - other on-train system registration -> record all self_tests failures
  - record all self_tests failures -> connect to last registered mobile network?
  - connect to last registered mobile network? -> succeed?
  - succeed? -> display network name
- input_excerpt:
  5.2.3.1 Powering up the Cab radio will initiate the following: − automatic self-testing; (M) − automatic selection of the pre-set loudspeaker volume; (M) − registration with other on-train systems, such as ERTMS/ETCS; (M) − all failures of self-tests should be recorded in the train-borne recorder; (O) − connection of the Cab radio to an authorised mobile network. This shall be the network to which the mobile was last registered (where available); (M) − if connection is successful, the name of the network shall be displayed on the MMI and an audible indication of successful connection shall be given; (M) − if connection is not successful, an audible and visual indication shall be provided. (M
- generated_excerpt:
  @startuml start  partition "Cab Radio" {     :Power up the Cab radio;          fork         :Automatic self-testing;     fork again         :Automatic selection of the pre-set loudspeaker volume;     fork again         :Registration with other on-train systems, such as ERTMS/ETCS;     fork again         :Connection of the Cab radio to an authorised mobile network\n(network to which the mobile was last registered, where available);     end fork          if (Self-test failures?) then (Yes)         :Record failures in the train-borne recorder;     else (No)     endif          if (Connection successful?) then (Yes)         :Display the name of the network on the MMI;         :Give an audible ind
### lmc-0007
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.0000
- missing_nodes:
  - system is supported?
  - sensor data is good?
- extra_nodes:
  - system is supported and sensor data is good?
  - state is nominal
  - state remains transition
- missing_relations:
  - system is supported? -> sensor data is good?
  - sensor data is good? -> autopilot change states from transition to nominal
- input_excerpt:
  3.	The autopilot shall change states from TRANSITION to NOMINAL when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml start partition Autopilot {   :Change state from TRANSITION to NOMINAL;   if (System is supported and sensor data is good?) then (yes)     :State is NOMINAL;   else (no)     :State remains TRANSITION;   endif } @enduml
### rac-0010
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3600
- relation_f1: 0.4167
- missing_nodes:
  - high-voltage shutdown request is 2 and bms self-check counter is 1
  - enter state 126
  - enter state 126
  - high-voltage shutdown request is 2 and bms counter is 0
  - switch to state 127
  - switch state 127
  - condition judgement
  - timeout 2.2s occurs
- extra_nodes:
  - system starts up
  - high-voltage shutdown request == 2?
  - move to state 126
  - remain in power-up mode
  - transition to state 127
  - transition to state 127
  - remain in state 126
  - move to state 142
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request is 2 and bms self-check counter is 1
  - high-voltage shutdown request is 2 and bms self-check counter is 1 -> enter state 126
  - enter state 126 -> high-voltage shutdown request is 2 and bms counter is 0
  - high-voltage shutdown request is 2 and bms counter is 0 -> enter state 126
  - enter state 126 -> fast charging is active and front mcu initialization state is 0
  - front mcu low-voltage shutdown flag is 0 -> switch state 127
  - switch state 127 -> condition judgement
  - condition judgement -> timeout 2.2s occurs
- input_excerpt:
  After the system starts up and slow charging is active, it enters power-up mode. Then, if the high-voltage shutdown request (for charging or discharging) is 2, the system moves to state 126 regardless of whether the BMS self-check counter is 0 or 1.  While in state 126: - If fast charging becomes active and the front MCU initialization state is 0, it transitions to state 127. - Similarly, if the front MCU low-voltage shutdown flag is 0, it also transitions to state 127. - Additionally, the following checks occur:   1. If a 2.2-second timeout triggers, it switches to state 142. Should fast charging be inactive at this point, the system shuts down and ends.   2. If the BMS counter reads 0, it 
- generated_excerpt:
  @startuml start :System starts up; :Slow charging is active; :Enter power-up mode; if (High-voltage shutdown request == 2?) then (yes)   :Move to state 126; else (no)   :Remain in power-up mode;   stop endif  if (Fast charging is active\nand front MCU initialization state == 0?) then (yes)   :Transition to state 127; elseif (Front MCU low-voltage shutdown flag == 0?) then (yes)   :Transition to state 127; else (no)   :Remain in state 126;   stop endif  repeat   :Stay in state 127;   if (Front MCU low-voltage shutdown request flag == 1?) then (yes)     :Move to state 142;     if (Fast charging is inactive?) then (yes)       :System shuts down;       stop     else (no)     endif   elseif (2.2-
### fsd-0031
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3684
- relation_f1: 0.0556
- missing_nodes:
  - supervisory network stack initializes
  - under fixed-priority preemptive model
  - deterministic multi-threaded scheduler within rtos launches concurrent tasks
  - high-priority periodic task
  - continuous device status monitoring managed by watchdog
  - parallel threads for ring buffer management
  - parallel threads for network communication
  - network module initialization
- extra_nodes:
  - initialize network module
  - continuous device status monitoring (watchdog managed)
  - ring buffer management
  - network communication
  - timer-driven telemetry loop (dispatch data to cloud server via can bus with bounded retries and backoff on transmission faults)
  - concurrent parsing and publishing (mutex-protected priority queue)
  - mirror critical status to central fadec or bms (dedicated isr)
  - close modules in controlled sequence
- missing_relations:
  - supervisory network stack initializes -> validate external environmental conditions meet operating specifications
  - validate external environmental conditions meet operating specifications -> check device interface connectivity
  - check device interface connectivity -> prerequisites satisfied?
  - prerequisites satisfied? -> verify sensor data validity via crc check
  - initialize data acquisition module -> under fixed-priority preemptive model
  - under fixed-priority preemptive model -> deterministic multi-threaded scheduler within rtos launches concurrent tasks
  - deterministic multi-threaded scheduler within rtos launches concurrent tasks -> high-priority periodic task
  - high-priority periodic task -> continuous device status monitoring managed by watchdog
- input_excerpt:
  Upon system initialization, the supervisory network stack, employing exponential backoff, keep-alive heartbeats, and link-state monitoring, first validates that external environmental conditions meet operating specifications before checking device interface connectivity. If these prerequisites are satisfied, the system verifies sensor data validity via a CRC check before initializing the data acquisition module. Subsequently, a deterministic, multi-threaded scheduler within the RTOS launches concurrent tasks under a fixed-priority preemptive model. These tasks include a high-priority periodic task for continuous device status monitoring, managed by a watchdog, alongside other parallel thread
- generated_excerpt:
  @startuml start  partition "Supervisory Network Stack" {     :Validate external environmental conditions meet operating specifications;     if (Prerequisites satisfied?) then (yes)         :Check device interface connectivity;         :Verify sensor data validity via CRC check;         :Initialize data acquisition module;     else (no)         stop     endif }  partition "RTOS Scheduler" {     :Initialize network module;     fork         :Continuous device status monitoring (watchdog managed);     fork again         :Ring buffer management;     fork again         :Network communication;     end fork     fork         :Timer-driven telemetry loop (dispatch data to cloud server via CAN bus with

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
