# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3216
- node_recall: 0.3139
- node_f1: 0.3046
- relation_precision: 0.2188
- relation_recall: 0.2527
- relation_f1: 0.2244
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

## Representative Failure Cases
### lmc-0050
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - body vector output vb
  - =dcm321 * vi?
  - allowed
  - not allowed
- extra_nodes:
  - input inertial vector vi
  - 3x3 rotation matrix output dcm321
  - compute 3x1 vector product of dcm321 times vi
  - set body vector output vb equal to the product
- missing_relations:
  - body vector output vb -> =dcm321 * vi?
  - =dcm321 * vi? -> allowed
  - allowed -> not allowed
- input_excerpt:
  2.	The Body Vector Output, Vb, of this Function Shall Equal a 3x1 Vector Product of the 3x3 Rotation Matrix Output, DCM321, times the Input Inertial Vector, Vi.
- generated_excerpt:
  @startuml start :Input Inertial Vector, Vi; :3x3 Rotation Matrix Output, DCM321; :Compute 3x1 Vector Product of DCM321 times Vi; :Set Body Vector Output, Vb equal to the product; @enduml
### us-0056
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - edit site member profile
  - correct problems
- extra_nodes:
  - select site member
  - open member profile
  - edit profile details
  - save profile changes
- missing_relations:
  - edit site member profile -> correct problems
- input_excerpt:
  As a site administrator, I want to edit any site member profile, so that I can correct problems for members.
- generated_excerpt:
  @startuml start :Select site member; :Open member profile; :Edit profile details; :Save profile changes; stop @enduml
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1739
- relation_f1: 0.0952
- missing_nodes:
  - go to administration options window
  - click manage syetems
  - list is displayed
  - host names
  - port numbers
  - display names
  - descriptions
  - click add
- extra_nodes:
  - click manage systems in the administration options window
  - the list of host names port numbers display names and descriptions is displayed
  - add the host name port number display name and the description in the appropriate fields
  - click add to add the system
  - the host system is added to the list
- missing_relations:
  - go to administration options window -> click manage syetems
  - click manage syetems -> list is displayed
  - list is displayed -> host names
  - host names -> port numbers
  - port numbers -> display names
  - display names -> descriptions
  - descriptions -> click add
  - add system dialog box appears -> add information
- input_excerpt:
  15.	use the Manage Systems optionTo add a host system, complete the following steps:1. In the "Administration Options" window, click Manage Systems.The list of host names, port numbers, display names, and descriptions isdisplayed.2. Click Add.The "Add System" dialog box appears.3. Add the host name, port number, display name, and the description inthe appropriate fields.4. Click Add to add the system.The host system is added to the list.
- generated_excerpt:
  @startuml start :Click Manage Systems in the Administration Options window; :The list of host names, port numbers, display names, and descriptions is displayed; :Click Add; :The "Add System" dialog box appears; :Add the host name, port number, display name, and the description in the appropriate fields; :Click Add to add the system; :The host system is added to the list; stop @enduml
### rac-0013
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2418
- relation_f1: 0.1348
- missing_nodes:
  - condtion judgement
  - dcdc state=1
  - stay in state 155
  - stay in state 155
  - stay in state 155
  - stay in state 155
  - bms-fast charger handshake flag=1
  - bms-fast charger handshake flag=1
- extra_nodes:
  - system starts up
  - dcdc state monitoring
  - shut down and end process
  - transition to state 156
  - dcdc state is not 1 or 3 seconds pass?
  - move to state 157
  - dcdc state remains 1
  - eas state monitoring
- missing_relations:
  - enter state 155 -> condtion judgement
  - condtion judgement -> dcdc state=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - bms-fast charger handshake flag=1 -> switch to state 156
- input_excerpt:
  After the system starts up: if fast charging is active and the BMS manual charging/discharging flag is 0, the system enters state 155. While in state 155:  1. For DCDC state monitoring:    - If DCDC state remains 1, stay in state 155.    - If the BMS-fast charger handshake flag becomes 1, transition to state 156.    - If DCDC state is not 1 or 3 seconds pass, move to state 157.    - If fast charging becomes inactive at any point, shut down and end the process.  2. For EAS state monitoring:    - If EAS state stays at 1, remain in state 155.    - If the handshake flag turns to 1, switch to state 156.    - If EAS state isn’t 1 or 3 seconds elapse, shift to state 157.    - Should fast charging d
- generated_excerpt:
  @startuml start :System starts up; if (Fast charging is active\nand BMS manual charging/discharging flag is 0?) then (yes)   :Enter state 155;   fork     :DCDC state monitoring;     if (Fast charging is inactive?) then (yes)       :Shut down and end process;       stop     elseif (BMS-fast charger handshake flag is 1?) then (yes)       :Transition to state 156;       stop     elseif (DCDC state is not 1\nor 3 seconds pass?) then (yes)       :Move to state 157;       stop     else (no)       :DCDC state remains 1;       :Stay in state 155;     endif   fork again     :EAS state monitoring;     if (Fast charging is inactive?) then (yes)       :Shut down and terminate;       stop     elseif (Han
### us-0129
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- missing_nodes:
  - get the details of the workflow plan
  - get the execution history
  - get results recorded in neurohub
- extra_nodes:
  - view workflow plan details
  - record execution history in neurohub
  - record execution results in neurohub
- missing_relations:
  - execute workflow -> get the details of the workflow plan
  - get the details of the workflow plan -> get the execution history
  - get the execution history -> get results recorded in neurohub
- input_excerpt:
  As a researcher, I want to have the details of the workflow plan as well as the execution history and results recorded in Neurohub while executing a workflow
- generated_excerpt:
  @startuml start :View workflow plan details; :Execute workflow; fork   :Record execution history in Neurohub; fork again   :Record execution results in Neurohub; end fork stop @enduml
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3000
- relation_f1: 0.0526
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - click manage dependencies
  - list of infoobjects and their dependents is displayed
  - open select dependents drop-down list
  - selection
  - no
- extra_nodes:
  - in the promotion jobs home page click manage dependencies
  - from the select dependents drop-down list select an option to add dependents to the job
  - explicitly select the dependents you want to promote
  - click to view the supported filtering options of infoobjects in the drop-down list
  - select an option and click ok
  - click apply changes to update the list of dependents
  - click apply changes and close to save the changes
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37
  - see creating a new job on page 37 -> add required infoobjects to new job
  - add required infoobjects to new job -> go to promotion jobs home page
  - go to promotion jobs home page -> click manage dependencies
  - click manage dependencies -> manage dependencies window appears
  - manage dependencies window appears -> list of infoobjects and their dependents is displayed
  - list of infoobjects and their dependents is displayed -> open select dependents drop-down list
- input_excerpt:
  22.	manage dependencies of an infoobject1. Log into the LifeCycle Manager tool.2. Create a new job. For information on creating a new job, see Creating aNew Job on page 37.3. Add the required infoobjects to the new job.4. In the "Promotion Jobs" home page, click Manage Dependencies. The "Manage Dependencies" window appears. This window displays the list of infoobjects and their dependents, as shown in the following figure:5. From the Select Dependents drop-down list, select any of the options available to add the dependents to the job. The dependents are displayed on the right side. The dependents are not selected by default; you must explicitly select the dependents you want to promote. For
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :In the "Promotion Jobs" home page, click Manage Dependencies; :The "Manage Dependencies" window appears; :From the Select Dependents drop-down list, select an option to add dependents to the job; :The dependents are displayed on the right side; :Explicitly select the dependents you want to promote; :Click to view the supported filtering options of infoobjects in the drop-down list; :Select an option, and click OK; :The filtered infoobjects are displayed; :Click Apply Changes to update the list of dependents; :Click Apply Changes and Close to save the changes; stop @enduml
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3030
- relation_f1: 0.2500
- missing_nodes:
  - presented with main window
  - open file menu
  - select configure diagnostics menu item
  - administrator user?
  - include (authenticate user)
  - populate window with disk file data
  - change configuration?
  - click save
- extra_nodes:
  - select configure diagnostics from file menu
  - authenticated as administrator?
  - authenticate user
  - populate window with data from disk file
  - make desired changes to configuration
  - click button?
  - save
  - request confirmation to save changes
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - select configure diagnostics menu item -> administrator user?
  - administrator user? -> include (authenticate user)
  - populate window with disk file data -> change configuration?
  - change configuration? -> click save
  - click save -> request confirmation
  - request confirmation -> confirm?
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start :Select "Configure Diagnostics" from "File" menu;  if (Authenticated as administrator?) then (No)   :Authenticate User; else (Yes) endif  if (Has appropriate privilege?) then (Yes)   :Display configuration window;    fork     :Click "Recall" button;     :Read previously saved changes from disk file or database;     :Populate window with data from disk file;   fork again     :Make desired changes to configuration;   end fork    switch (Click button?)   case ("Save")     :Request confirmation to save changes;     if (Confirms save?) then (Yes)       :Request name for disk file;       switch (User action?)       case (Enter file name)         :Save changes to permanent storage; 
### lmc-0016
- dataset: lmc
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4444
- relation_f1: 0.6667
- missing_nodes:
  - sensor change states from fault to transition
- extra_nodes:
  - sensor is in fault state
  - change state to transition
  - remain in fault state
  - remain in fault state
- input_excerpt:
  12.	The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting support (not request) and limits are not exceeded (not limits).
- generated_excerpt:
  @startuml start :Sensor is in FAULT state; if (Autopilot is not requesting support? (not request)) then (yes)   if (Limits are not exceeded? (not limits)) then (yes)     :Change state to TRANSITION;   else (no)     :Remain in FAULT state;   endif else (no)   :Remain in FAULT state; endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
