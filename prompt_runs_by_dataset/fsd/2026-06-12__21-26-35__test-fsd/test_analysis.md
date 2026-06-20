# Prompt Evaluation Analysis

## Summary
- count: 116
- syntax_pass_rate: 0.7328
- infrastructure_error_rate: 0.0000
- node_precision: 0.3721
- node_recall: 0.2880
- node_f1: 0.3125
- relation_precision: 0.1942
- relation_recall: 0.1538
- relation_f1: 0.1679
- plantuml_compilation_pass_rate: 0.7328
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
- extra_activity: 115
- wrong_loop: 91
- wrong_parallel: 81
- syntax_error: 31

## Representative Failure Cases
### fsd-0038
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - power management subsystem governed by rtos
  - continuously monitor voltage rails via pmic and bms
  - execute protection policies within dedicated high-priority task
  - signal strength < defined threshold?
  - query battery state
  - sufficient charge?
  - initiate signal compensation routine
  - enter low-power mode
- extra_nodes:
  - monitor voltage rails via pmic bms
- missing_relations:
  - power management subsystem governed by rtos -> continuously monitor voltage rails via pmic and bms
  - continuously monitor voltage rails via pmic and bms -> execute protection policies within dedicated high-priority task
  - execute protection policies within dedicated high-priority task -> signal strength < defined threshold?
  - signal strength < defined threshold? -> query battery state
  - query battery state -> sufficient charge?
  - sufficient charge? -> initiate signal compensation routine
  - initiate signal compensation routine -> enter low-power mode
  - enter low-power mode -> watchdog service dispatch priority-queued warning to central control via can bus
- input_excerpt:
  The power management subsystem, governed by a real-time operating system (RTOS), continuously monitors voltage rails via the PMIC and BMS, executing protection policies within a dedicated high-priority task. Upon detecting signal strength below a defined threshold, the system first queries the battery state. If sufficient charge remains, a signal compensation routine is initiated; if insufficient, the system enters a low-power mode while a watchdog service asynchronously dispatches a priority-queued warning message to the central control system via CAN bus. Concurrently, data acquisition—sampled via timer ISRs and debounced—and uplink transmission tasks execute under the RTOS scheduler, with
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityBorderColor #336699 skinparam NoteBorderColor #888888 skinparam NoteBackgroundColor #FFFFDD  title Power Management & Telemetry Subsystem Activity Diagram  |#PMIC/BMS| Power Management (High Priority) | |#RTOS| RTOS Scheduler | |#Telemetry| Telemetry & Data Acquisition | |#Watchdog| Watchdog Service | |#Audit| Audit & Storage |  |PMIC/BMS| start :Monitor voltage rails via PMIC & BMS; note right: RTOS High-Priority Task  if (Signal strength < threshold?) then (yes)   :Query battery state;      if (Sufficient charge?) then (yes)     :Initiate signal compensation routine;   else (no)     :Enter low-p
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
  - acquire mutex
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
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEFFFF skinparam PartitionBackgroundColor #F5F5F5  title Thermal Management Controller - Hard Real-Time RTOS State Machine  state "Active State Machine" as MainSM {     start     :Acquire Mutex;     note right: Protects Sensor Fusion Ring Buffer     :Sample Sensor Fusion Ring Buffer;     :Read Calibrated Data (Temp, Humidity, Light, Air, Occupancy, Contact, Smoke);     :Release Mutex;      fork         :High-Priority Task: Primary Fault Check;          if (Temp > Threshold OR Humidity > Threshold?) then (yes)             if (Room Occupied? AND Windows Closed?) then (yes)                 :Trigger Concurrent Mitigation Sequ
### fsd-0086
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - embedded control platform implements safety-critical fsm
  - orchestrate
  - high-priority isrs
  - lower-priority deferred rtos tasks
  - fail-safe policies
  - anomalous physiological data detected?
  - initiate dual-path verification sequence
  - executed by concurrent prioritized tasks
- extra_nodes:
  - detect anomalous physiological data
- missing_relations:
  - embedded control platform implements safety-critical fsm -> orchestrate
  - orchestrate -> high-priority isrs
  - high-priority isrs -> lower-priority deferred rtos tasks
  - lower-priority deferred rtos tasks -> fail-safe policies
  - fail-safe policies -> anomalous physiological data detected?
  - anomalous physiological data detected? -> initiate dual-path verification sequence
  - initiate dual-path verification sequence -> executed by concurrent prioritized tasks
  - executed by concurrent prioritized tasks -> primary task enters polling loop managed by timer interrupt
- input_excerpt:
  The embedded control platform implements a safety-critical finite-state machine (FSM) that orchestrates high-priority Interrupt Service Routines (ISRs), lower-priority deferred tasks via an RTOS, and fail-safe policies. Upon detection of anomalous physiological data, the system initiates a dual-path verification sequence executed by concurrent, prioritized tasks. The primary task enters a polling loop, managed by a timer interrupt, to confirm the persistence of the anomaly; this loop exits if the data normalizes, employing exponential backoff to manage the polling frequency. Concurrently, a secondary task performs two consecutive data integrity checks, utilizing a CRC for accuracy and a mute
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEFFDD skinparam PartitionBackgroundColor #F9F9F9  title Safety-Critical FSM: Dual-Path Anomaly Verification & Fail-Safe Orchestration  start  :Detect Anomalous Physiological Data; note right: ISR / High-Priority Trigger  :Initiate Dual-Path Verification Sequence;  fork     :Primary Task: Polling Loop;     partition "Timer-Managed Polling" {         repeat             :Wait via Exponential Backoff;             :Check Data Persistence (Timer Interrupt);         repeat while (Anomaly Persists?) is (Yes)         ->No (Data Normalized);     } fork again     :Secondary Task: Data Integrity Checks;     partition "Mutex-Protecte
### fsd-0103
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - thermal management controller implemented as deterministic state machine on rtos
  - govern pwm fan speeds
  - govern liquid-cooling pump actuators
  - pmic/fused sensor input indicate ambient temperature > safety threshold?
  - scheduler initializes high-priority tasks
  - data acquisition unit logs timestamped readings to ring buffer
  - alarm unit that signals event
  - data acquisition loop protected by mutex for sensor data integrity
- extra_nodes:
  - initialize high-priority task data acquisition unit
  - initialize high-priority task alarm unit (signal event)
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
  @startuml skinparam style strictuml  start  state "Monitoring State\n(Periodic Sensor Fusion & Calibration)" as monitoring  monitoring --> :PMIC or fused sensor input\nindicates ambient temp > safety threshold;  fork   :Initialize High-Priority Task:\nData Acquisition Unit; fork again   :Initialize High-Priority Task:\nAlarm Unit\n(Signal Event); end fork  repeat :Acquire Data\n(Log timestamped readings to ring buffer);   note right: Protected by mutex\nfor sensor data integrity  repeat :Check Temperature; -> Normalized; :Terminate Data Acquisition Loop; :Issue Final Alarm;  -> Fault Persists\n(No external CAN command); fork   :Spawn Secondary Task:\nExternal Communication Module; fork again
### fsd-0060
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0526
- relation_f1: 0.0000
- missing_nodes:
  - avionics stack comprises
  - fms
  - fadec
  - execute on deterministic rtos
  - high-priority isr samples sensor data
  - signal supervisory task
  - altitude < preset threshold?
  - rtos scheduler launches tasks from priority queue
- extra_nodes:
  - initialize on deterministic rtos (hardware software redundancy)
- missing_relations:
  - avionics stack comprises -> fms
  - fms -> fadec
  - fadec -> execute on deterministic rtos
  - execute on deterministic rtos -> detect abnormal aircraft attitude?
  - detect abnormal aircraft attitude? -> high-priority isr samples sensor data
  - high-priority isr samples sensor data -> signal supervisory task
  - signal supervisory task -> altitude < preset threshold?
  - altitude < preset threshold? -> rtos scheduler launches tasks from priority queue
- input_excerpt:
  The avionics stack, comprising the Flight Management System (FMS) and Full Authority Digital Engine Control (FADEC), executes on a deterministic Real-Time Operating System (RTOS) featuring hardware and software redundancy for fault tolerance. Upon detection of an abnormal aircraft attitude, a high-priority ISR samples sensor data and signals a supervisory task. If the current altitude is below a preset threshold, the RTOS scheduler concurrently launches the emergency altitude adjustment and attitude correction tasks from a priority queue. The altitude adjustment task enters a control loop, periodically reading from an air data computer via a protected ring buffer and issuing commands to the 
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEF6FF skinparam ActivityDiamondBackgroundColor #FFF3E0  title Avionics Stack: Abnormal Attitude Fault-Tolerant Response  |FMS / FADEC| start :Initialize on Deterministic RTOS\n(Hardware & Software Redundancy);  :Detect Abnormal Aircraft Attitude; note right: High-Priority ISR  :Sample Sensor Data via ISR; :Signal Supervisory Task;  if (Current Altitude < Preset Threshold?) then (Yes)      fork     |Altitude Adjustment Task|     :Launch from Priority Queue;     repeat       :Read Air Data Computer\n(via Protected Ring Buffer);       :Issue Commands to Servo Actuators;     repeat until (Safe Altitude Reached?)    fork agai
### fsd-0004
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.1754
- relation_f1: 0.0000
- missing_nodes:
  - integrated avionics stack (fms/fadec) executes control laws via
  - high-priority isrs
  - subordinate worker tasks
  - operate within deterministic rtos for redundancy
  - check of critical states
  - engine status valid via fadec?
  - fuel reserves sufficient from bms?
  - communications link stable?
- extra_nodes:
  - altitude ok?
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
  @startuml skinparam ActivityBackgroundColor #F9F9F9 skinparam ActivityDiamondBackgroundColor #E8E8E8  title Integrated Avionics Stack (FMS/FADEC) - Autonomous Flight Mode Control Flow  start  :Engage Autonomous Flight Mode;  partition "Sequential Precondition Checks" {   :Verify altitude within safe envelope;   if (Altitude OK?) then (No)     :Abort Cycle;   else (Yes)     :Check ambient temperature is nominal;     if (Temperature OK?) then (No)       :Abort Cycle;     else (Yes)       :Validate engine status via FADEC;       if (FADEC Status Valid?) then (No)         :Abort Cycle;       else (Yes)         :Check fuel reserves from BMS;         if (Fuel Sufficient?) then (No)           :Abor
### fsd-0091
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.2381
- relation_f1: 0.0500
- missing_nodes:
  - embedded control platform employs fsm
  - coordinate
  - high-priority isrs
  - deferred rtos tasks
  - fail-safe policies under rtos
  - patient heart rate > preset threshold?
  - isr immediately triggers alarm
  - medium-priority task monitors blood oxygen saturation
- extra_nodes:
  - heart rate isr triggered (hr > threshold)
  - trigger alarm
  - receive signal from message queue
  - process alarm event
  - blood oxygen monitor task
  - acquire mutex
  - adjust ventilator o2 supply via pmic
  - release mutex
- missing_relations:
  - embedded control platform employs fsm -> coordinate
  - coordinate -> high-priority isrs
  - high-priority isrs -> deferred rtos tasks
  - deferred rtos tasks -> fail-safe policies under rtos
  - fail-safe policies under rtos -> patient heart rate > preset threshold?
  - patient heart rate > preset threshold? -> isr immediately triggers alarm
  - signal high-priority task via message queue -> medium-priority task monitors blood oxygen saturation
  - medium-priority task monitors blood oxygen saturation -> desaturation detected?
- input_excerpt:
  The embedded control platform employs a finite-state machine (FSM) to coordinate high-priority interrupt service routines (ISRs), deferred task execution, and fail-safe policies under a real-time operating system (RTOS). When the patient's heart rate exceeds a preset threshold, an ISR immediately triggers an alarm and signals a high-priority task via a message queue. Concurrently, a separate medium-priority task monitors blood oxygen saturation; if a desaturation event is detected, it acquires a mutex to safely adjust the ventilator's oxygen supply parameters via the system's power management IC (PMIC) while logging the anomaly with a CRC to a ring buffer for audit. This task then enters a m
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEF6FF skinparam ActivityBorderColor #336699 skinparam PartitionBackgroundColor #F0F8FF skinparam NoteBorderColor #888888  title Embedded Control Platform FSM - RTOS Coordination  |ISR| start :Heart Rate ISR Triggered\n(HR > Threshold); :Trigger Alarm; :Signal High-Priority Task\nvia Message Queue;  |High-Priority Task| :Receive Signal\nfrom Message Queue; :Process Alarm Event;  |Medium-Priority Task| fork   :Blood Oxygen Monitor Task;   if (Desaturation\nEvent Detected?) then (Yes)     :Acquire Mutex;     partition "Critical Section" {       :Adjust Ventilator O2 Supply\nvia PMIC;       :Log Anomaly with CRC\nto Ring Buf
### fsd-0069
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.2632
- relation_f1: 0.2222
- missing_nodes:
  - thermal management controller operates as state machine within rtos
  - govern pwm fan speeds
  - govern liquid-cooling pumps
  - high-priority task potentially serviced by isr
  - temperature
  - ambient humidity
  - cycle cooling assets
  - temperature normalizes
- extra_nodes:
  - monitor temperature humidity (sensor fusion algorithm)
  - acquire mutex (protect shared ring buffer)
  - read sensor data
  - release mutex
  - crc check valid?
  - out-of-range reading detected
  - execute controlled cool-down (exponential backoff strategy)
  - validate temperature reading
- missing_relations:
  - thermal management controller operates as state machine within rtos -> govern pwm fan speeds
  - govern pwm fan speeds -> govern liquid-cooling pumps
  - govern liquid-cooling pumps -> high-priority task potentially serviced by isr
  - high-priority task potentially serviced by isr -> temperature
  - temperature -> ambient humidity
  - ambient humidity -> validated temperature > safety threshold?
  - execute closed-loop cooling operation -> cycle cooling assets
  - cycle cooling assets -> temperature normalizes
- input_excerpt:
  Operating as a state machine within a real-time operating system (RTOS), the thermal management controller governs PWM fans and liquid-cooling pumps. A high-priority task, potentially serviced by an ISR, continuously monitors temperature and ambient humidity via a sensor fusion algorithm. If the temperature reading, validated by a CRC check, exceeds its safety threshold, the controller executes a closed-loop cooling operation, cycling the cooling assets until the temperature normalizes. Concurrently, a lower-priority task monitors the battery rail voltage and current, leveraging data from the PMIC or BMS. Should the voltage drop below a safe level or the current surpass its rated maximum, a 
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityDiamondBackgroundColor #F9F9F9  title Thermal Management Controller (RTOS State Machine)  state "Low-Power Standby Mode" as standby <<Entry>>  |High Priority| start standby --> Monitor_Sensors : Wake / Active Cycle  :Monitor Temperature & Humidity\n(Sensor Fusion Algorithm);  :Acquire Mutex\n(Protect Shared Ring Buffer);  :Read Sensor Data;  :Release Mutex;  if (CRC Check Valid?) then (No)   :Out-of-Range Reading Detected;   :Initiate Redundancy Switch;   :Execute Controlled Cool-down\n(Exponential Backoff Strategy);   :Confirm Normal Status;   :Enter Low-Power Standby Mode;   stop else (Yes)   :Validate Temperature Readin

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
