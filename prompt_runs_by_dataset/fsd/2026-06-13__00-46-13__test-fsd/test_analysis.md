# Prompt Evaluation Analysis

## Summary
- count: 116
- syntax_pass_rate: 0.7931
- infrastructure_error_rate: 0.0000
- node_precision: 0.3582
- node_recall: 0.2790
- node_f1: 0.2960
- relation_precision: 0.1650
- relation_recall: 0.1352
- relation_f1: 0.1433
- plantuml_compilation_pass_rate: 0.7931
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_activity: 116
- missing_or_wrong_relation: 116
- extra_or_wrong_relation: 116
- extra_activity: 114
- wrong_loop: 88
- wrong_parallel: 78
- syntax_error: 24

## Representative Failure Cases
### fsd-0027
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - thermal management controller operates as state machine within rtos
  - govern pwm fans
  - govern liquid-cooling loops
  - detect anomalous energy consumption?
  - determine if equipment overload occurred
  - equipment overload?
  - classify overload type
  - over-voltage condition on power rail?
- missing_relations:
  - thermal management controller operates as state machine within rtos -> govern pwm fans
  - govern pwm fans -> govern liquid-cooling loops
  - govern liquid-cooling loops -> detect anomalous energy consumption?
  - detect anomalous energy consumption? -> determine if equipment overload occurred
  - determine if equipment overload occurred -> equipment overload?
  - equipment overload? -> classify overload type
  - classify overload type -> over-voltage condition on power rail?
  - over-voltage condition on power rail? -> initialize voltage regulation mechanism immediately
- input_excerpt:
  Operating as a state machine within the RTOS, the thermal management controller governs PWM fans and liquid-cooling loops. Upon detecting anomalous energy consumption, the system first determines if an equipment overload has occurred; if so, it classifies the overload type, and in the event of an over-voltage condition on the power rail, immediately initializes the voltage regulation mechanism. Concurrently, a high-priority task continuously samples current data via an ADC, performing real-time calculations to update an adaptive energy consumption model, while a medium-priority task monitors operational hours against a preset threshold, triggering the generation of structured audit logs and 
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEFFEE skinparam ActivityBorderColor #336633  title Thermal Management Controller - RTOS State Machine  state "Detect Anomalous Energy Consumption" as detect_anomaly state "Determine Equipment Overload" as check_overload state "Classify Overload Type" as classify_overload state "Initialize Voltage Regulation Mechanism" as init_vreg  state "Sample Current Data via ADC\n(High-Priority Task)" as sample_adc state "Update Adaptive Energy Consumption Model\n(Real-time Calculations)" as update_model  state "Monitor Operational Hours\n(Medium-Priority Task)" as monitor_hours state "Generate Structured Audit Logs\n& Maintenance Re
### fsd-0051
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - thermal management controller operates as state machine on hard real-time rtos
  - continuously sample sensor fusion ring buffer protected by mutex
  - aggregate calibrated data from
  - temperature sensors
  - humidity sensors
  - light sensors
  - air quality sensors
  - occupancy sensors
- extra_nodes:
  - sample sensor fusion ring buffer
- missing_relations:
  - thermal management controller operates as state machine on hard real-time rtos -> continuously sample sensor fusion ring buffer protected by mutex
  - continuously sample sensor fusion ring buffer protected by mutex -> aggregate calibrated data from
  - aggregate calibrated data from -> temperature sensors
  - temperature sensors -> humidity sensors
  - humidity sensors -> light sensors
  - light sensors -> air quality sensors
  - air quality sensors -> occupancy sensors
  - occupancy sensors -> contact sensors
- input_excerpt:
  Operating as a state machine within a hard real-time RTOS, the thermal management controller orchestrates a multi-subsystem response to environmental sensor inputs. The system continuously samples a sensor fusion ring buffer, protected by a mutex, which aggregates calibrated data from temperature, humidity, light, air quality, occupancy, contact, and smoke sensors. Upon detecting a primary fault condition—such as temperature or humidity exceeding their respective thresholds while the room is occupied and windows are closed—the controller triggers a concurrent mitigation sequence. This involves commanding the FADEC to activate the air conditioner's cooling and the dehumidifier via PWM-control
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEEBDD skinparam ActivityDiamondBackgroundColor #E8E8E8  title Thermal Management Controller - Hard Real-Time RTOS State Machine  state "RTOS Task: Sensor Fusion & Calibration" as sf_task #LightBlue {     :Sample sensor fusion ring buffer;     note right: Protected by Mutex     :Aggregate calibrated data\n(Temperature, Humidity, Light,\nAir Quality, Occupancy, Contact, Smoke);     if (Readings out of range?) then (Yes)         :Engage redundant sensors;     else (No)     endif }  state "Primary Fault Mitigation\n(High Priority Task)" as pf_task #LightCoral {     :Evaluate primary fault condition;     if (Temp/Humidity > T
### fsd-0078
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - thermal management controller operates as state machine within hard real-time rtos
  - govern multi-zone pwm fans
  - govern liquid-cooling pump loops
  - primary task scheduled with high priority
  - continuously monitor via protected sensor fusion thread
  - equipment temperature
  - rail voltage
  - either parameter > defined threshold?
- extra_nodes:
  - monitor equipment temperature rail voltage
- missing_relations:
  - thermal management controller operates as state machine within hard real-time rtos -> govern multi-zone pwm fans
  - govern multi-zone pwm fans -> govern liquid-cooling pump loops
  - govern liquid-cooling pump loops -> primary task scheduled with high priority
  - primary task scheduled with high priority -> continuously monitor via protected sensor fusion thread
  - continuously monitor via protected sensor fusion thread -> equipment temperature
  - equipment temperature -> rail voltage
  - rail voltage -> either parameter > defined threshold?
  - either parameter > defined threshold? -> initiate concurrent mitigation tasks
- input_excerpt:
  Operating as a state machine within a hard real-time RTOS, the thermal management controller governs multi-zone PWM fans and liquid-cooling pump loops. Its primary task, scheduled with high priority, continuously monitors equipment temperature and rail voltage via a protected sensor fusion thread. Should either parameter exceed its defined threshold, the system initiates concurrent mitigation tasks managed through priority queues and mutex-protected shared resources. These include a power management routine that, upon detecting a critical battery state from the BMS or abnormal power consumption, engages exponential backoff retry logic with the PMIC for power optimization. Simultaneously, a c
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #LightYellow skinparam ActivityBorderColor #DarkSlateGray  title Thermal Management Controller - RTOS State Machine  state "Active RTOS State Machine" as ActiveSM #LightBlue  |High Priority| start :Monitor Equipment Temperature & Rail Voltage; note right: Protected Sensor Fusion Thread  if (Temp or Voltage Exceed Threshold?) then (Yes)   :Initiate Concurrent Mitigation Tasks;   note right: Managed via Priority Queues\n& Mutex-Protected Shared Resources    fork     |Power Management|     :Check Battery State from BMS\n& Power Consumption;     if (Critical Battery State or\nAbnormal Power Consumption?) then (Yes)       :Engage Exponential Backoff\nRe
### fsd-0095
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - tcms operates on preemptive rtos
  - manage subsystems with deterministic scheduling via priority queues
  - traction
  - braking
  - door
  - diagnostics
  - station arrival?
  - verify door status via dedicated monitoring task
- extra_nodes:
  - rtos deterministic scheduler priority queues active
  - asynchronous telemetry logging
- missing_relations:
  - tcms operates on preemptive rtos -> manage subsystems with deterministic scheduling via priority queues
  - manage subsystems with deterministic scheduling via priority queues -> traction
  - traction -> braking
  - braking -> door
  - door -> diagnostics
  - diagnostics -> station arrival?
  - station arrival? -> verify door status via dedicated monitoring task
  - verify door status via dedicated monitoring task -> any door open?
- input_excerpt:
  The Train Control and Monitoring System (TCMS), executing on a preemptive RTOS, coordinates traction, braking, door management, and diagnostic subsystems via deterministic scheduling and priority queues. Upon station arrival, the system first verifies door status via a dedicated monitoring task. If any door is detected as open, a door closure command is issued, initiating a cyclic control process that iteratively monitors the door switch status and checks the locking mechanism via a CAN bus message with a confirming CRC until a fully closed and locked state is achieved. Concurrently, a high-priority task, potentially serviced by an ISR from platform sensors, performs safety-critical monitori
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityDiamondBackgroundColor #F9F9F9  title TCMS Station Arrival and Departure Sequence  start  :RTOS Deterministic Scheduler & Priority Queues Active;  fork   :Asynchronous Telemetry Logging;   note right: Ring Buffer -> NVM fork again   :Watchdog & PMIC/BMS Fail-Safe Monitoring;   note right: EN 50128/EN 50129 Compliance fork again    :Station Arrival Event;    :Verify Door Status (Dedicated Monitoring Task);    if (Any Door Open?) then (Yes)     :Issue Door Closure Command;      repeat       fork         :Monitor Door Switch Status;       fork again         :Check Locking Mechanism via CAN Bus;         :Verify CAN Bus CRC;   
### fsd-0024
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.1579
- relation_f1: 0.0556
- missing_nodes:
  - thermal management controller operates as state machine within rtos
  - govern pwm fans
  - govern liquid-cooling loops
  - detect fault conditions
  - abnormal current fluctuations
  - exceeded rail voltage thresholds
  - frequency anomalies
  - overtemperature
- extra_nodes:
  - log anomalies to structured audit log
- missing_relations:
  - thermal management controller operates as state machine within rtos -> govern pwm fans
  - govern pwm fans -> govern liquid-cooling loops
  - govern liquid-cooling loops -> detect fault conditions
  - detect fault conditions -> abnormal current fluctuations
  - abnormal current fluctuations -> exceeded rail voltage thresholds
  - exceeded rail voltage thresholds -> frequency anomalies
  - frequency anomalies -> overtemperature
  - overtemperature -> communication loss
- input_excerpt:
  Operating as a state machine within a Real-Time Operating System (RTOS), the thermal management controller governs PWM fans and liquid-cooling loops. Upon detecting any fault condition—such as abnormal current fluctuations, exceeded rail voltage thresholds, frequency anomalies, overtemperature, communication loss, hardware failure, or a standby state—the system activates its emergency protection mechanism. This initiates concurrent, prioritized tasks: a data acquisition task cyclically reads sensor data and updates the system status using a ring buffer, while a self-test task iteratively checks hardware integrity via the PMIC and BMS, logging any anomalies to a structured audit log protected
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #E8F5E9 skinparam ActivityDiamondBackgroundColor #FFF3E0  title Thermal Management Controller - Emergency Protection State Machine  state "Fault Detection" as fault_detect <<Choice>> state "Emergency Protection Activated" as emergency_active  partition "Concurrent High-Priority Tasks" {     fork         :Data Acquisition Task;         repeat :Cyclically read sensor data;         :Update system status (Ring Buffer);         repeatwhile (Continue cycle?) is (yes)         ->no;     fork again         :Self-Test Task;         repeat :Check hardware integrity (PMIC & BMS);         :Log anomalies to structured audit log;        
### fsd-0049
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.1935
- relation_f1: 0.0690
- missing_nodes:
  - embedded control system employs fsm
  - orchestrate
  - isrs
  - priority-scheduled rtos tasks
  - fail-safe policies
  - photodiode-driven isr serviced upon timer interrupt
  - continuously sample ambient light intensity
  - < defined threshold?
- extra_nodes:
  - ambient light < threshold?
  - system in night mode?
  - detect intrusion in monitoring area
  - intrusion detected?
- missing_relations:
  - embedded control system employs fsm -> orchestrate
  - orchestrate -> isrs
  - isrs -> priority-scheduled rtos tasks
  - priority-scheduled rtos tasks -> fail-safe policies
  - fail-safe policies -> photodiode-driven isr serviced upon timer interrupt
  - photodiode-driven isr serviced upon timer interrupt -> continuously sample ambient light intensity
  - continuously sample ambient light intensity -> < defined threshold?
  - < defined threshold? -> medium-priority task acquires mutex
- input_excerpt:
  The embedded control system employs a finite-state machine (FSM) to orchestrate interrupt service routines (ISRs), priority-scheduled RTOS tasks, and fail-safe policies. A photodiode-driven ISR, serviced upon a timer interrupt, continuously samples ambient light intensity. When this value falls below a defined threshold, a medium-priority task acquires a mutex to check if the system is in night mode. If confirmed, the system initializes an object detection algorithm; upon identifying an intrusion within the monitoring area, it triggers the infrared fill light via a GPIO command. Concurrently, a high-priority task enters a loop to capture infrared image data into a ring buffer, applying real-
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEFFFF skinparam ActivityDiamondBackgroundColor #FFFFEE  title Embedded Control System FSM: ISR, RTOS Tasks, and Fail-Safe Orchestration  state "FSM: Normal Monitoring State" as FSM_Normal  FSM_Normal --> :Timer Interrupt Triggered\nPhotodiode ISR Samples Ambient Light  if (Ambient Light < Threshold?) then (Yes)   :Medium-Priority Task\nAcquire Mutex;   if (System in Night Mode?) then (Yes)     :Initialize Object Detection Algorithm;          fork       :Detect Intrusion in Monitoring Area;       if (Intrusion Detected?) then (Yes)         :Trigger Infrared Fill Light\n(GPIO Command);         note right: Critical Event: F
### fsd-0103
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.2069
- relation_f1: 0.0000
- missing_nodes:
  - thermal management controller implemented as deterministic state machine on rtos
  - govern pwm fan speeds
  - govern liquid-cooling pump actuators
  - pmic/fused sensor input indicate ambient temperature > safety threshold?
  - data acquisition loop protected by mutex for sensor data integrity
  - run continuously
  - temperature normalized?
  - terminate loop
- extra_nodes:
  - ambient temperature exceeds safety threshold?
- missing_relations:
  - thermal management controller implemented as deterministic state machine on rtos -> govern pwm fan speeds
  - govern pwm fan speeds -> govern liquid-cooling pump actuators
  - govern liquid-cooling pump actuators -> pmic/fused sensor input indicate ambient temperature > safety threshold?
  - pmic/fused sensor input indicate ambient temperature > safety threshold? -> scheduler initializes high-priority tasks
  - scheduler initializes high-priority tasks -> data acquisition unit logs timestamped readings to ring buffer
  - data acquisition unit logs timestamped readings to ring buffer -> alarm unit that signals event
  - alarm unit that signals event -> data acquisition loop protected by mutex for sensor data integrity
  - data acquisition loop protected by mutex for sensor data integrity -> run continuously
- input_excerpt:
  The thermal management controller, implemented as a deterministic state machine on the RTOS, governs PWM fan speeds and liquid-cooling pump actuators. Upon the PMIC or a fused sensor input indicating an ambient temperature exceeding the safety threshold, the scheduler initializes high-priority tasks, including a data acquisition unit that logs timestamped readings to a ring buffer and an alarm unit that signals the event. This data acquisition loop, protected by a mutex for sensor data integrity, runs continuously until the temperature normalizes, at which point it terminates and a final alarm is issued. Should the fault persist without external intervention via a CAN command, secondary task
- generated_excerpt:
  @startuml skinparam style strictuml  start  state "Monitoring State\n(Periodic Sensor Fusion & Calibration)" as monitor  monitor --> :Receive PMIC/Fused Sensor Input;  if (Ambient Temperature\nExceeds Safety Threshold?) then (yes)   :Scheduler Initializes High-Priority Tasks;    fork     :Alarm Unit Signals Event;   fork again     :Data Acquisition Unit\nLogs Timestamped Readings to Ring Buffer;     note right: Protected by Mutex\nfor Sensor Data Integrity      repeat       :Acquire & Log Sensor Data;     repeat while (Temperature Normalized?) is (no)     ->yes;     :Terminate Data Acquisition Loop;     :Issue Final Alarm;   end fork    if (Fault Persists without\nExternal CAN Command Interv
### fsd-0004
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.2105
- relation_f1: 0.0000
- missing_nodes:
  - integrated avionics stack (fms/fadec) executes control laws via
  - high-priority isrs
  - subordinate worker tasks
  - operate within deterministic rtos for redundancy
  - check of critical states
  - engine status valid via fadec?
  - fuel reserves sufficient from bms?
  - power rail valid as monitored by pmic?
- extra_nodes:
  - altitude safe?
  - abort cycle
  - abort cycle
  - abort cycle
  - abort cycle
  - abort cycle
  - abort cycle
  - abort cycle
- missing_relations:
  - integrated avionics stack (fms/fadec) executes control laws via -> high-priority isrs
  - high-priority isrs -> subordinate worker tasks
  - subordinate worker tasks -> operate within deterministic rtos for redundancy
  - operate within deterministic rtos for redundancy -> engagement of autonomous flight mode
  - engagement of autonomous flight mode -> check of critical states
  - check of critical states -> altitude within safe envelope?
  - altitude within safe envelope? -> ambient temperature nominal?
  - ambient temperature nominal? -> engine status valid via fadec?
- input_excerpt:
  Operating within a deterministic RTOS for redundancy, the integrated avionics stack (FMS/FADEC) executes control laws via high-priority ISRs and subordinate worker tasks. Upon engagement of autonomous flight mode, the system performs a sequential, conditional check of critical states: verifying altitude is within a safe envelope, ambient temperature is nominal, engine status is valid via FADEC, fuel reserves are sufficient from the BMS, the navigation system is operational, the communications link is stable, and the power rail is valid as monitored by the PMIC. Only if all preconditions are met does the system advance to a concurrent processing phase. Here, a priority-based scheduler manages
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #F9F9F9 skinparam ActivityDiamondBackgroundColor #E8E8E8  title Integrated Avionics Stack (FMS/FADEC) - Autonomous Flight Mode Control Flow  start  :Engage Autonomous Flight Mode;  partition "Sequential Precondition Checks" {   :Verify Altitude within Safe Envelope;   if (Altitude Safe?) then (No)     :Abort Cycle;   else (Yes)     :Verify Ambient Temperature Nominal;     if (Temperature Nominal?) then (No)       :Abort Cycle;     else (Yes)       :Verify Engine Status via FADEC;       if (Engine Status Valid?) then (No)         :Abort Cycle;       else (Yes)         :Verify Fuel Reserves via BMS;         if (Fuel Sufficient?) then (No)           :

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
