# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2730
- node_recall: 0.2463
- node_f1: 0.2541
- relation_precision: 0.1702
- relation_recall: 0.1493
- relation_f1: 0.1562
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
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10
- missing_activity: 9
- extra_activity: 9

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
  - receive input inertial vector vi (3x1)
  - receive rotation matrix output dcm321 (3x3)
  - calculate body vector output vb (3x1) vb = dcm321 * vi
  - output vb
- missing_relations:
  - body vector output vb -> =dcm321 * vi?
  - =dcm321 * vi? -> allowed
  - allowed -> not allowed
- input_excerpt:
  2.	The Body Vector Output, Vb, of this Function Shall Equal a 3x1 Vector Product of the 3x3 Rotation Matrix Output, DCM321, times the Input Inertial Vector, Vi.
- generated_excerpt:
  @startuml start :Receive Input Inertial Vector, Vi (3x1); :Receive Rotation Matrix Output, DCM321 (3x3); :Calculate Body Vector Output, Vb (3x1)\nVb = DCM321 * Vi; :Output Vb; stop @enduml
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
  - site administrator selects a site member
  - view member profile
  - click edit profile
  - modify profile details
  - submit changes
  - changes valid?
  - save updated profile
  - display success message
- missing_relations:
  - edit site member profile -> correct problems
- input_excerpt:
  As a site administrator, I want to edit any site member profile, so that I can correct problems for members.
- generated_excerpt:
  @startuml start :Site Administrator selects a site member; :View member profile; :Click edit profile; :Modify profile details; :Submit changes; if (Changes valid?) then (yes)   :Save updated profile;   :Display success message; else (no)   :Display validation errors;   :Return to edit form; endif stop @enduml
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
  - sensor in fault state
  - autopilot requesting support?
  - remain in fault state
  - remain in fault state
  - limits exceeded?
  - change state to transition
- missing_relations:
  - autopilot is not requesting support (not request -> limits are not exceeded (not limits
  - limits are not exceeded (not limits -> sensor change states from fault to transition
- input_excerpt:
  12.	The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting support (not request) and limits are not exceeded (not limits).
- generated_excerpt:
  @startuml skinparam style strictuml title Sensor State Change: FAULT to TRANSITION start :Sensor in FAULT state; if (Autopilot requesting support?) then (yes)   :Remain in FAULT state;   stop else (no)   if (Limits exceeded?) then (yes)     :Remain in FAULT state;     stop   else (no)     :Change state to TRANSITION;     stop   endif endif @enduml
### us-0129
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - execute workflow
  - get the details of the workflow plan
  - get the execution history
  - get results recorded in neurohub
- extra_nodes:
  - researcher logs into neurohub
  - select or create a workflow project
  - define workflow plan details
- missing_relations:
  - execute workflow -> get the details of the workflow plan
  - get the details of the workflow plan -> get the execution history
  - get the execution history -> get results recorded in neurohub
- input_excerpt:
  As a researcher, I want to have the details of the workflow plan as well as the execution history and results recorded in Neurohub while executing a workflow
- generated_excerpt:
  @startuml skinparam style strictuml  title Researcher: Record Workflow Plan Details, Execution History, and Results in Neurohub  start  :Researcher logs into Neurohub; :Select or create a workflow project;  :Define workflow plan details; note right: Includes steps, parameters, inputs, etc.  :Submit workflow plan to Neurohub; :Neurohub records workflow plan details;  :Initiate workflow execution; :Neurohub records execution start (history);  repeat   :Execute next workflow step;   :Neurohub records step execution status (history);      if (Step successful?) then (Yes)     :Neurohub records step results;   else (No)     :Neurohub records error details (history);     :Handle error / Abort workf
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
  - in the administration options window click manage systems
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
  @startuml start :In the "Administration Options" window,\nclick Manage Systems; :The list of host names, port numbers,\ndisplay names, and descriptions is displayed; :Click Add; :The "Add System" dialog box appears; :Add the host name, port number,\ndisplay name, and the description\nin the appropriate fields; :Click Add to add the system; :The host system is added to the list; stop @enduml
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1905
- relation_f1: 0.1000
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - click manage dependencies
  - manage dependencies window appears
  - list of infoobjects and their dependents is displayed
  - open select dependents drop-down list
  - dependents are displayed on the right
- extra_nodes:
  - in the promotion jobs home page click manage dependencies
  - view the manage dependencies window (displaying list of infoobjects and dependents)
  - from the select dependents drop-down list select an option to add dependents to the job
  - view dependents displayed on the right side (not selected by default)
  - explicitly select the dependents you want to promote
  - view supported filtering options?
  - click to view filtering options in the drop-down list
  - select a filtering option
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
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :In the "Promotion Jobs" home page,\nclick Manage Dependencies; :View the "Manage Dependencies" window\n(displaying list of infoobjects and dependents); :From the Select Dependents drop-down list,\nselect an option to add dependents to the job; :View dependents displayed on the right side\n(Not selected by default); :Explicitly select the dependents\nyou want to promote; if (View supported filtering options?) then (Yes)   :Click to view filtering options\nin the drop-down list;   :Select a filtering option;   :Click OK;   :View the filtered infoobjects; else (No) endif :Clic
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.2333
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
  - click save or close ?
  - request confirmation to save changes
  - user confirms?
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
  @startuml start :Select "Configure Diagnostics" from "File" menu; if (Authenticated as administrator?) then (No)   :Authenticate User; else (Yes) endif if (Has appropriate privilege?) then (Yes)   :Display configuration window;      fork     :Click "Recall" button;     :Read previously saved changes from disk file/database;     :Populate window with data from disk file;   fork again     :Make desired changes to configuration;          if (Click "Save" or "Close"?) then (Save)       :Request confirmation to save changes;       if (User confirms?) then (Yes)         :Request name for disk file;         if (User enters name or cancels?) then (Enters name)           :Save changes to permanent st
### rac-0013
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4468
- relation_f1: 0.1798
- missing_nodes:
  - fast charging is active and bms manual charging/discharging flag=0
  - condtion judgement
  - stay in state 155
  - stay in state 155
  - stay in state 155
  - bms-fast charger handshake flag=1
  - bms-fast charger handshake flag=1
  - bms-fast charger handshake flag=1
- extra_nodes:
  - system starts up
  - bms manual charging/discharging flag = 0?
  - dcdc state monitoring
  - transition to state 156
  - 3 seconds pass?
  - 3 seconds pass?
  - move to state 157
  - move to state 157
- missing_relations:
  - fast charging is active and bms manual charging/discharging flag=0 -> enter state 155
  - enter state 155 -> condtion judgement
  - condtion judgement -> dcdc state=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
- input_excerpt:
  After the system starts up: if fast charging is active and the BMS manual charging/discharging flag is 0, the system enters state 155. While in state 155:  1. For DCDC state monitoring:    - If DCDC state remains 1, stay in state 155.    - If the BMS-fast charger handshake flag becomes 1, transition to state 156.    - If DCDC state is not 1 or 3 seconds pass, move to state 157.    - If fast charging becomes inactive at any point, shut down and end the process.  2. For EAS state monitoring:    - If EAS state stays at 1, remain in state 155.    - If the handshake flag turns to 1, switch to state 156.    - If EAS state isn’t 1 or 3 seconds elapse, shift to state 157.    - Should fast charging d
- generated_excerpt:
  @startuml start  :System starts up;  if (Fast charging active?) then (yes)   if (BMS manual charging/discharging flag = 0?) then (yes)     :Enter State 155;   else (no)     stop   endif else (no)   stop endif  repeat    fork     :DCDC State Monitoring;     if (Fast charging inactive?) then (yes)       :Shut down;       stop     else (no)       if (BMS-fast charger handshake flag = 1?) then (yes)         :Transition to State 156;         stop       elseif (DCDC state = 1?) then (yes)         :Stay in State 155;       else (no)         if (3 seconds pass?) then (yes)           :Move to State 157;           stop         else (no)           :Move to State 157;           stop         endif       

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
