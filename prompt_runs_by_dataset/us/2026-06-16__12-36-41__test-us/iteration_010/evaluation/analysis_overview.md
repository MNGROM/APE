# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.6338
- node_recall: 0.4921
- node_f1: 0.5541
- relation_precision: 0.5211
- relation_recall: 0.4645
- relation_f1: 0.4912
- plantuml_compilation_pass_rate: 0.9000
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_activity: 9
- extra_activity: 9
- extra_or_wrong_relation: 8
- missing_or_wrong_relation: 7
- wrong_parallel: 4
- syntax_error: 1
- wrong_loop: 1

## Representative Failure Cases
### fsd-0040
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4255
- relation_f1: 0.3000
- missing_nodes:
  - tcms executes on preemptive rtos
  - manage via deterministic priority-scheduled tasks
  - traction
  - braking
  - door control
  - system diagnostics
  - continuously poll status of trackside signal lights via high-priority monitoring task
  - initiate concurrent operations
- extra_nodes:
  - poll trackside signal lights status
  - continue polling trackside signals?
  - acquire track sensor data via isr
  - headway within safe envelope?
  - continuously monitor traction force against certified operational bounds
  - traction and braking within bounds?
  - archive system state to non-volatile memory
  - transient communication fault?
- missing_relations:
  - tcms executes on preemptive rtos -> manage via deterministic priority-scheduled tasks
  - manage via deterministic priority-scheduled tasks -> traction [fork]
  - manage via deterministic priority-scheduled tasks -> braking [fork]
  - manage via deterministic priority-scheduled tasks -> door control [fork]
  - manage via deterministic priority-scheduled tasks -> system diagnostics [fork]
  - traction -> detect train overspeed condition?
  - braking -> detect train overspeed condition?
  - door control -> detect train overspeed condition?
- input_excerpt:
  The Train Control and Monitoring System (TCMS), executing on a preemptive RTOS, manages traction, braking, door control, and system diagnostics via deterministic, priority-scheduled tasks. Upon detecting a train overspeed condition, the system first verifies the emergency braking arming criteria. It then continuously polls the status of trackside signal lights via a high-priority monitoring task; any signal anomaly triggers an immediate emergency response. This event initiates concurrent operations: a dedicated ISR-driven process acquires track sensor data for real-time upload to the central control unit over a CAN bus with CRC protection, while a parallel safety task, with mutex-protected a
- generated_excerpt:
  @startuml start :Detect train overspeed condition; :Verify emergency braking arming criteria; repeat   :Poll trackside signal lights status;   if (Signal anomaly detected?) then (yes)     :Trigger immediate emergency response;     stop   else (no)   endif repeat while (Continue polling trackside signals?) is (yes) ->no; fork   :Acquire track sensor data via ISR;   :Upload sensor data to central control unit over CAN bus with CRC protection; fork again   :Acquire mutex-protected access to shared sensor ring buffer;   :Assess headway to forward obstacle against safe envelope;   if (Headway within safe envelope?) then (no)     :Trigger immediate emergency response;     stop   else (yes)   endif
### bp-0014
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2963
- relation_f1: 0.2581
- missing_nodes:
  - select start
  - select programs
  - select businessobjects xi 3.1
  - select businessobjects enterprise
  - select businessobjects lifecycle manager
  - go to system field
  - enter cms name
  - open authentication drop-down list
- extra_nodes:
  - select start > programs > businessobjects xi 3.1 > businessobjects enterprise > businessobjects lifecycle manager
  - enter cms name in system field
  - select authentication method from drop-down list
  - authentication method
  - authenticate with ldap credentials
  - authenticate with windows ad credentials
- missing_relations:
  - select start -> select programs
  - select programs -> select businessobjects xi 3.1
  - select businessobjects xi 3.1 -> select businessobjects enterprise
  - select businessobjects enterprise -> select businessobjects lifecycle manager
  - lifecycle manager login screen appears -> go to system field
  - go to system field -> enter cms name
  - select authentication method -> default method?
  - default method? -> enterprise authentication [yes]
- input_excerpt:
  14.	log into the LifeCycle Manager tool.To log into the LifeCycle Manager tool, complete the following steps:1. Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager. The LifeCycle Manager login screen appears.2. In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed.3. Enter the user name and password.4. Select the appropriate authentication method from the Authentication drop-down list.The LifeCycle Manager tool supports the following authentication types:• Enterprise authentication - This authentication type requires a user name and a password that are recognize
- generated_excerpt:
  @startuml start :Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager; :View LifeCycle Manager login screen; :Enter CMS name in System field; :Enter user name and password; :Select authentication method from drop-down list; switch (Authentication method) case (Enterprise)   :Authenticate with Enterprise credentials; case (LDAP)   :Authenticate with LDAP credentials; case (Windows AD)   :Authenticate with Windows AD credentials; endswitch :Click Log on; @enduml
### bp-0017
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4706
- relation_f1: 0.0000
- missing_nodes:
  - go to administration options window
  - open version management systems drop-down list
  - select clearcase
  - enter details
  - enter mvfs s folder name
  - enter vob name
  - enter vob s folder name
  - enter creating path
- extra_nodes:
  - select clearcase from version management systems drop-down list
- missing_relations:
  - go to administration options window -> click vms settings
  - click vms settings -> open version management systems drop-down list
  - open version management systems drop-down list -> select clearcase
  - select clearcase -> enter details
  - enter details -> clearcase map drive [fork]
  - clearcase map drive -> enter mvfs s folder name
  - enter details -> vob tag name [fork]
  - vob tag name -> enter vob name
- input_excerpt:
  17.	set the ClearCase version management system in Unix1. In the Administration Options window, click VMS Settings.2. From the Version Management Systems drop-down list, select ClearCase.3. Enter the following details:• ClearCase Map Drive - Enter the name of the folder where the MVFSis located. By default, it is /view• VOB Tag Name - Enter the VOB name and the folder where the VOBis located. For example: VobFolder/VobName• View Storage Directory: Enter the path of the directory where the viewsare created.
- generated_excerpt:
  @startuml start :Click VMS Settings; :Select ClearCase from Version Management Systems drop-down list; :Enter ClearCase Map Drive folder name; :Enter VOB Tag Name; :Enter View Storage Directory path; @enduml
### fsd-0039
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4762
- relation_f1: 0.3729
- missing_nodes:
  - tcms executes on preemptive rtos
  - manage via priority-scheduled tasks
  - traction
  - braking
  - doors
  - diagnostics
  - critical fault condition
  - emergency signal combined with overspeed and brake failure
- extra_nodes:
  - critical fault type
  - launch fault logging routine with crc-protected telemetry archiving to non-volatile memory
  - poll subsystem status via protected mutex access to sensor rings and can bus data
- missing_relations:
  - tcms executes on preemptive rtos -> manage via priority-scheduled tasks
  - manage via priority-scheduled tasks -> traction [fork]
  - manage via priority-scheduled tasks -> braking [fork]
  - manage via priority-scheduled tasks -> doors [fork]
  - manage via priority-scheduled tasks -> diagnostics [fork]
  - traction -> critical fault condition
  - braking -> critical fault condition
  - doors -> critical fault condition
- input_excerpt:
  The Train Control and Monitoring System (TCMS), executing on a preemptive RTOS, manages traction, braking, doors, and diagnostics via priority-scheduled tasks. Upon detecting a critical fault condition—such as an emergency signal combined with overspeed and brake failure, an unavoidable track obstacle, a persistent communication loss in the control network, main power rail interruption with backup PMIC/BMS activation, door control failure precluding manual override, or a fire alarm with failed suppression—the system triggers a deterministic emergency sequence. This initiates an emergency stop, broadcasts passenger evacuation instructions, and concurrently launches a high-priority self-test a
- generated_excerpt:
  @startuml start :Detect critical fault condition; switch (Critical fault type) case (Emergency signal combined with overspeed and brake failure) case (Unavoidable track obstacle) case (Persistent communication loss in control network) case (Main power rail interruption with backup PMIC/BMS activation) case (Door control failure precluding manual override) case (Fire alarm with failed suppression) endswitch :Initiate emergency stop; :Broadcast passenger evacuation instructions; fork   :Launch high-priority self-test; fork again   :Launch fault logging routine with CRC-protected telemetry archiving to non-volatile memory; end fork repeat   :Poll subsystem status via protected mutex access to s
### rac-0014
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4828
- relation_f1: 0.4286
- missing_nodes:
  - high-voltage shutdown request=2 and dcdc state=1
  - dcdc state=0 and power battery relay control is issued
  - fast charging is inactive
  - shutdown
  - switch to 185
  - condition judgement
  - ignition switch=0 and fast charging is inactive
  - slow charging is inactive and fast charging is inactive
- extra_nodes:
  - system starts up
  - dcdc state is 1?
  - power battery relay control issued?
  - enter state 155
  - shut down
  - condition check
- missing_relations:
  - dcdc state=0 and power battery relay control is issued -> switch to state 185 [yes]
  - switch to state 185 -> high-voltage shutdown request 2
  - high-voltage shutdown request 2 -> switch to state 155 [yes]
  - switch to state 155 -> fast charging is inactive
  - switch to 185 -> condition judgement
  - switch to state 155 -> ignition switch=0 and fast charging is inactive
  - ignition switch=0 and fast charging is inactive -> shutdown [if yes]
  - switch to state 155 -> slow charging is inactive and fast charging is inactive
- input_excerpt:
  After the system starts up, if fast charging is active, it enters the "power-up" state. Then, in this state: if the high-voltage shutdown request is 2 and the DCDC state is 1, the system enters state 175. If the DCDC state is 0 and power battery relay control is issued, it switches to state 185. If the request is not 2, it enters state 155. If fast charging is not active, the system shuts down and ends.  Additionally, if the high-voltage shutdown request is 2 and power battery relay control is issued, the system switches to state 185. Then: a) when the ignition switch is 2 and the request is 0, it switches to state 155; if the ignition switch is 0 and fast charging is inactive, it shuts down
- generated_excerpt:
  @startuml start :System starts up; if (Fast charging active?) then (Yes)   :Enter "power-up" state;   if (High-voltage shutdown request is 2?) then (Yes)     if (DCDC state is 1?) then (Yes)       :Enter state 175;     else (No - DCDC state is 0)       if (Power battery relay control issued?) then (Yes)         :Switch to state 185;       else (No)         endif     endif   else (No - Request is not 2)     :Enter state 155;   endif else (No)   :Shut down;   end endif  if (High-voltage shutdown request is 2 and power battery relay control issued?) then (Yes)   :Switch to state 185;   switch (Condition check)   case (Ignition switch is 2 and request is 0)     :Switch to state 155;   case (Igni
### lmc-0029
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3333
- missing_nodes:
  - in nlguidance
  - it is inertial position vector for aim point 1
  - compute the vector
- extra_nodes:
  - compute inertial position vector for aim point 1
- missing_relations:
  - in nlguidance -> vector define location at standoff 1 with offset from target position?
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? -> it is inertial position vector for aim point 1 [yes]
  - it is inertial position vector for aim point 1 -> compute the vector
- input_excerpt:
  2.	NLGuidance shall compute the inertial position vector for aim point 1, defining the location at Standoff 1 with an offset from the target position, and oriented on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point.
- generated_excerpt:
  @startuml start :Compute inertial position vector for aim point 1; :Define location at Standoff 1 with offset from target position; :Orient on vector perpendicular to tangent relative position vector from vehicle to corresponding aim point; stop @enduml
### pure-0095
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3333
- missing_nodes:
  - refer to provided configuration
  - specify how fields are translated into warc records
  - handle missing fields
- extra_nodes:
  - check configuration file specifies field translation to warc records
  - configuration specifies field translation?
  - missing fields encountered?
- missing_relations:
  - use command arc_warc_migrate options -> refer to provided configuration
  - refer to provided configuration -> specify how fields are translated into warc records [fork]
  - refer to provided configuration -> generate errors requiring operator intervention [fork]
  - generate errors requiring operator intervention -> handle missing fields
- input_excerpt:
  Migration Tool Execution: Use the command arc_warc_migrate <ARC_FILES> <CONFIG> [options] to migrate content from ARC files to WARC files based on the provided configuration. Ensure the configuration file specifies how fields are translated into WARC records, and handle missing fields by generating errors requiring operator intervention.
- generated_excerpt:
  @startuml start :Execute arc_warc_migrate command with ARC files, configuration, and options; :Check configuration file specifies field translation to WARC records; if (Configuration specifies field translation?) then (yes)   :Migrate content from ARC files to WARC files based on configuration; else (no)   :Generate error requiring operator intervention;   stop endif if (Missing fields encountered?) then (no) else (yes)   :Generate error requiring operator intervention;   stop endif stop @enduml
### lmc-0009
- dataset: lmc
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- missing_nodes:
  - pilot is in control (standby)?
- extra_nodes:
  - pilot is in control?
- input_excerpt:
  5.	The autopilot shall change states from NOMINAL to STANDBY when the pilot is in control (standby).
- generated_excerpt:
  @startuml start if (Pilot is in control?) then (yes)   :Change autopilot state from NOMINAL to STANDBY; else (no) endif @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
