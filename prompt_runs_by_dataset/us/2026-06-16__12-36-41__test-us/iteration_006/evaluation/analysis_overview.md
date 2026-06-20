# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4188
- node_recall: 0.4115
- node_f1: 0.4151
- relation_precision: 0.2872
- relation_recall: 0.3067
- relation_f1: 0.2966
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
- extra_or_wrong_relation: 10
- missing_or_wrong_relation: 9
- wrong_parallel: 2
- wrong_loop: 2

## Representative Failure Cases
### lmc-0053
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - for each pitch angle theta
  - dcm321 provides distinct mapping from vi to vb
  - dcm321 is not distinct for all phi and psi inputs
- extra_nodes:
  - receive input vector vi
  - receive pitch angle theta
  - receive phi and psi inputs
  - theta
  - map vi to vb using dcm321 for theta value 1
  - map vi to vb using dcm321 for theta value 2
  - map vi to vb using dcm321 for theta value n
- missing_relations:
  - for each pitch angle theta -> dcm321 provides distinct mapping from vi to vb
  - dcm321 provides distinct mapping from vi to vb -> dcm321 is not distinct for all phi and psi inputs
- input_excerpt:
  5.	The Rotation Matrix, DCM321, shall provide a distinct mapping from the input vector, Vi, to the output vector, Vb, for each pitch angle, theta.  Note:  the DCM321 is not distinct for all phi and psi inputs.
- generated_excerpt:
  @startuml start :Receive input vector Vi; :Receive pitch angle theta; :Receive phi and psi inputs; switch (theta) case (theta value 1)   :Map Vi to Vb using DCM321 for theta value 1; case (theta value 2)   :Map Vi to Vb using DCM321 for theta value 2; case (theta value n)   :Map Vi to Vb using DCM321 for theta value n; endswitch note right: DCM321 is not distinct for all phi and psi inputs stop @enduml
### lmc-0049
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.0000
- missing_nodes:
  - =roll * pitch * heading 3*3 matrix product?
  - allowed
  - not allowed
- extra_nodes:
  - compute 3x3 euler 1 (heading) rotation matrix
  - compute 3x3 euler 2 (pitch) rotation matrix
  - compute 3x3 euler 3 (roll) rotation matrix
  - multiply 3x3 euler 3 (roll) rotation matrix times 3x3 euler 2 (pitch) rotation matrix
  - multiply the resulting matrix times 3x3 euler 1 (heading) rotation matrix
- missing_relations:
  - rotation matrix output dcm321 -> =roll * pitch * heading 3*3 matrix product?
  - =roll * pitch * heading 3*3 matrix product? -> allowed [yes]
  - =roll * pitch * heading 3*3 matrix product? -> not allowed [no]
- input_excerpt:
  1.	The Rotation Matrix Output, DCM321, of this Function Shall Equal a 3x3 Matrix Product of a 3x3 Euler 3 (Roll) Rotation Matrix times a 3x3 Euler 2 (Pitch) Rotation Matrix times a 3x3 Euler 1 (Heading) Rotation Matrix.
- generated_excerpt:
  @startuml start :Compute 3x3 Euler 1 (Heading) Rotation Matrix; :Compute 3x3 Euler 2 (Pitch) Rotation Matrix; :Compute 3x3 Euler 3 (Roll) Rotation Matrix; :Multiply 3x3 Euler 3 (Roll) Rotation Matrix times 3x3 Euler 2 (Pitch) Rotation Matrix; :Multiply the resulting matrix times 3x3 Euler 1 (Heading) Rotation Matrix; :Set Rotation Matrix Output, DCM321, equal to the final 3x3 matrix product; @enduml
### bp-0014
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2222
- relation_f1: 0.1290
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
  - in the system field enter the name of the central management server (cms) on which the lifecycle manager tool is installed
  - select the appropriate authentication method from the authentication drop-down list
  - authentication type
  - requires a user name and a password that are recognized by the businessobjects enterprise system (default authentication method)
  - requires a user name and a password that are recognized by the businessobjects enterprise system
  - requires a special setup
- missing_relations:
  - select start -> select programs
  - select programs -> select businessobjects xi 3.1
  - select businessobjects xi 3.1 -> select businessobjects enterprise
  - select businessobjects enterprise -> select businessobjects lifecycle manager
  - lifecycle manager login screen appears -> go to system field
  - go to system field -> enter cms name
  - enter cms name -> enter username and password
  - enter username and password -> open authentication drop-down list
- input_excerpt:
  14.	log into the LifeCycle Manager tool.To log into the LifeCycle Manager tool, complete the following steps:1. Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager. The LifeCycle Manager login screen appears.2. In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed.3. Enter the user name and password.4. Select the appropriate authentication method from the Authentication drop-down list.The LifeCycle Manager tool supports the following authentication types:• Enterprise authentication - This authentication type requires a user name and a password that are recognize
- generated_excerpt:
  @startuml start :Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager; :The LifeCycle Manager login screen appears; :In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed; :Enter the user name and password; :Select the appropriate authentication method from the Authentication drop-down list; switch (Authentication type) case (Enterprise authentication)   :Requires a user name and a password that are recognized by the BusinessObjects Enterprise system (default authentication method); case (LDAP authentication)   :Requires a user name and a password that are recogn
### pure-0065
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2609
- relation_f1: 0.0000
- missing_nodes:
  - open keepass
  - select to find something
  - leave search unchecked?
  - all data appear
  - nothing appears
  - select fields
  - selection
  - results appears
- extra_nodes:
  - user opens keepass
  - user selects to find something in a selected group/subgroup
  - user leaves all search in boxes unchecked?
  - nothing appears in the main window
  - user selects the fields which will be searched
  - user selects cancel?
  - user selects ok
  - all data from the group/subgroup appear
- missing_relations:
  - open keepass -> select to find something
  - select to find something -> leave find field empty?
  - leave find field empty? -> leave search unchecked? [yes]
  - leave search unchecked? -> all data appear [no]
  - leave search unchecked? -> nothing appears [yes]
  - leave find field empty? -> type word to search for [no]
  - type word to search for -> leave search unchecked?
  - leave search unchecked? -> select fields [no]
- input_excerpt:
  1. User opens KeePass and selects to find something in a selected group/subgroup 2. User types the word to search for 3. User selects the fields which will be searched 4. User selects OK 5. Results appears at the database main window 3.9.2.2 Alternative Data Flows 3.9.2.2.1 Alternative Data Flow 1 2a. User leaves the find field empty 5. All data from the group/subgroup appear 3.9.2.2.2 Alternative Data Flow 2 3. User leaves all search in boxes unchecked 5. Nothing appears in the main window 3.9.2.2.3 Alternative Data Flow 3 4. User selects cancel 5. The main window appears 3.9.2.2.4 Alternative Data Flow 4 2. User leaves the find field empty 3. User leaves all search in boxes unchecked 5. No
- generated_excerpt:
  @startuml start :User opens KeePass; :User selects to find something in a selected group/subgroup; :User types the word to search for; if (User leaves the find field empty?) then (yes)   :User leaves all search in boxes unchecked?;   if (User leaves all search in boxes unchecked?) then (yes)     :Nothing appears in the main window;     stop   else (no)     :User selects the fields which will be searched;     if (User selects cancel?) then (yes)       :The main window appears;       stop     else (no)       :User selects OK;       :All data from the group/subgroup appear;       stop     endif   endif else (no)   :User selects the fields which will be searched;   if (User leaves all search in 
### bp-0027
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.5161
- missing_nodes:
  - experienced expert user?
  - open the promote window
  - click mappings
  - the connection list is displayed
  - select a connection
  - edit in the source system?
  - edited5 is displayed
  - click save or promote
- extra_nodes:
  - in the promote window click mappings
  - the list of federation connections is displayed
  - select a federation connection
  - this tab displays the list of properties and their values
  - edited a federation connection in the source system?
  - the following message is displayed beside the federation connection edited
  - requirement
  - click save
- missing_relations:
  - experienced expert user? -> open the promote window [yes]
  - open the promote window -> click mappings
  - the connection list is displayed -> select a connection
  - edit in the source system? -> edited5 is displayed [yes]
  - edited5 is displayed -> click save or promote
  - edit in the source system? -> click save or promote [no]
- input_excerpt:
  27.	map a Federation connection1. In the "Promote" window, click Mappings.2. Click Federation Mappings.The list of Federation connections is displayed.3. Select a Federation connection, and click Edit Federation Connection Properties. The "Edit Federation Connection Properties" tab appears. This tab displays the list of properties and their values.4. Modify the appropriate fields, and click Apply. The "Federation Mappings" tab appears.Note:If you edit a Federation connection in the source system, the followingmessage is displayed beside the federation connection: edited5. Click Save or Promote as per your requirement. Important: Mapping must be performed by an expert user who has adequate kn
- generated_excerpt:
  @startuml start :In the "Promote" window, click Mappings; :Click Federation Mappings; :The list of Federation connections is displayed; :Select a Federation connection; :Click Edit Federation Connection Properties; :The "Edit Federation Connection Properties" tab appears; :This tab displays the list of properties and their values; :Modify the appropriate fields; :Click Apply; :The "Federation Mappings" tab appears; if (Edited a Federation connection in the source system?) then (yes)   :The following message is displayed beside the federation connection: edited; else (no) endif switch (Requirement) case (Save)   :Click Save; case (Promote)   :Click Promote; endswitch :Mapping must be performe
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5161
- relation_f1: 0.4615
- missing_nodes:
  - condition judgement
  - shutdown
  - wait 0.8s
  - high-voltage shutdown request charging/discharging =2
- extra_nodes:
  - system starts up
  - condition in state 155?
  - move to state 175
  - fast charging remains inactive?
  - shut down
  - wait 0.8 seconds
  - enter state 175
  - fast charging is inactive afterward?
- missing_relations:
  - switch to state 153 -> bms-fast charger handshake flag=0 and front mcu high-voltage flag=0
  - enter state 155 -> condition judgement
  - condition judgement -> wait 0.8s [case high-voltage shutdown request charging/discharging =2]
  - wait 0.8s -> switch to state 175
  - stay in state 155 -> high-voltage shutdown request charging/discharging =2
  - high-voltage shutdown request charging/discharging =2 -> wait 0.8s [if yes]
  - wait 0.8s -> ignition switch=0
- input_excerpt:
  After the system starts up: - If charging is active (charging=1) and the front MCU high-voltage detection flag is 0, transition to state 153. - If the BMS-fast charger handshake flag is 0 and the front MCU high-voltage flag is 0, enter state 155.  While in state 155: 1. If pre-charge failure occurs, move to state 175. If fast charging remains inactive after this, shut down and end the process. 2. If a high-voltage shutdown request (for charging/discharging) is detected (value=2), wait 0.8 seconds before entering state 175. If fast charging is inactive afterward, shut down and end. 3. If the ignition switch status is 2, remain in state 155. If a high-voltage shutdown request (value=2) exists 
- generated_excerpt:
  @startuml start :System starts up; if (Charging is active (charging=1)\nand front MCU high-voltage\ndetection flag is 0?) then (yes)   :Transition to state 153; else (no)   if (BMS-fast charger handshake flag is 0\nand front MCU high-voltage flag is 0?) then (yes)     :Enter state 155;     switch (Condition in state 155?)     case (Pre-charge failure occurs)       :Move to state 175;       if (Fast charging remains inactive?) then (yes)         :Shut down;         end       else (no)       endif     case (High-voltage shutdown request detected (value=2))       :Wait 0.8 seconds;       :Enter state 175;       if (Fast charging is inactive afterward?) then (yes)         :Shut down;         end
### pure-0040
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5455
- relation_f1: 0.4545
- missing_nodes:
  - see view inventory
  - display category type screen
  - unique item?
  - system validates data
  - system updates information
  - back to category screen
- extra_nodes:
  - category type
  - system validates the category data
  - system updates the category information
  - user is taken back to the category screen
- missing_relations:
  - see view inventory -> navigate to category
  - click edit category button -> display category type screen
  - display category type screen -> unique item?
  - unique item? -> display unique item screen [yes]
  - unique item? -> display stock item screen [no]
  - system validates data -> system updates information
  - system updates information -> back to category screen
- input_excerpt:
  2. Edit Category 2.1. User navigates to a Category (see View Inventory) 2.2. System displays the Edit Category button 2.3. User clicks the Edit Category button 2.4. System displays the appropriate screen for the Category type 2.4.1. Unique Item 2.4.2. Stock Item 2.5. User edits Category data 2.6. System validates the Category data 2.7. System updates the Category information 2.8. User is taken back to the Category screen
- generated_excerpt:
  @startuml start :User navigates to a Category; :System displays the Edit Category button; :User clicks the Edit Category button; switch (Category type) case (Unique Item)   :System displays the appropriate screen for Unique Item; case (Stock Item)   :System displays the appropriate screen for Stock Item; endswitch :User edits Category data; :System validates the Category data; :System updates the Category information; :User is taken back to the Category screen; @enduml
### fsd-0075
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5763
- relation_f1: 0.2466
- missing_nodes:
  - avionics stack comprises
  - fms
  - fadec
  - execute on deterministic rtos
  - acquire data from
  - air pressure sensor
  - altimeter
  - gps module
- extra_nodes:
  - execute avionics stack (fms and fadec) on deterministic rtos with hardware and task-level redundancy
  - parallel procedure for airspeed anomalies
  - discrepancy?
  - acquire data from air pressure sensor
  - acquire data from altimeter
  - acquire data from gps module
  - voting evaluation incomplete?
  - flush to non-volatile memory by low-priority task governed by pmic power state and i/o budget constraints
- missing_relations:
  - avionics stack comprises -> fms [fork]
  - avionics stack comprises -> fadec [fork]
  - fms -> execute on deterministic rtos
  - fadec -> execute on deterministic rtos
  - execute on deterministic rtos -> employ concurrent monitoring tasks with priority queues
  - anomalous flight altitude detected? -> acquire data from [yes]
  - acquire data from -> air pressure sensor [fork]
  - acquire data from -> altimeter [fork]
- input_excerpt:
  The avionics stack, comprising the Flight Management System (FMS) and Full Authority Digital Engine Control (FADEC), executes on a deterministic Real-Time Operating System (RTOS) featuring hardware and task-level redundancy. For fault identification, the system employs concurrent monitoring tasks with priority queues. Upon detecting an anomalous flight altitude, a dedicated health management task initializes a multi-sensor verification routine, simultaneously acquiring data from the air pressure sensor, altimeter, and GPS module. This task then enters an iterative loop, continuously comparing the datasets using a voting mechanism protected by a mutex. If the pressure sensor data is inconsist
- generated_excerpt:
  @startuml start  :Execute avionics stack (FMS and FADEC) on deterministic RTOS with hardware and task-level redundancy;  fork   :Concurrent monitoring tasks with priority queues for fault identification; fork again   :Parallel procedure for airspeed anomalies;   :Compare data from airspeed and angle of attack sensors;   if (Discrepancy?) then (yes)     :Sensor fault diagnosis and alarm;   else (Concurrent abnormalities)     :Emergency handling process (potentially involving FADEC and BMS);   endif end fork  if (Anomalous flight altitude detected?) then (yes)   :Dedicated health management task initializes multi-sensor verification routine;   fork     :Acquire data from air pressure sensor;  

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
