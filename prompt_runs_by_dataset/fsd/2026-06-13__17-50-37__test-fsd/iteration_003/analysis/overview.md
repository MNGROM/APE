# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3633
- node_recall: 0.3052
- node_f1: 0.3258
- relation_precision: 0.2270
- relation_recall: 0.2106
- relation_f1: 0.2162
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
- missing_or_wrong_relation: 9
- extra_or_wrong_relation: 9

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
  - read input inertial vector vi
  - read 3x3 rotation matrix output dcm321
  - compute 3x1 body vector output vb as dcm321 * vi
  - output vb
- missing_relations:
  - body vector output vb -> =dcm321 * vi?
  - =dcm321 * vi? -> allowed
  - allowed -> not allowed
- input_excerpt:
  2.	The Body Vector Output, Vb, of this Function Shall Equal a 3x1 Vector Product of the 3x3 Rotation Matrix Output, DCM321, times the Input Inertial Vector, Vi.
- generated_excerpt:
  @startuml start :Read Input Inertial Vector Vi; :Read 3x3 Rotation Matrix Output DCM321; :Compute 3x1 Body Vector Output Vb as DCM321 * Vi; :Output Vb; stop @enduml
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
  - view workflow plan details
  - record execution history in neurohub
  - record results in neurohub
- missing_relations:
  - execute workflow -> get the details of the workflow plan
  - get the details of the workflow plan -> get the execution history
  - get the execution history -> get results recorded in neurohub
- input_excerpt:
  As a researcher, I want to have the details of the workflow plan as well as the execution history and results recorded in Neurohub while executing a workflow
- generated_excerpt:
  @startuml start :View workflow plan details; fork :Record execution history in Neurohub; fork again :Record results in Neurohub; end fork stop @enduml
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1667
- relation_f1: 0.0909
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
  - use the manage systems option
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
  @startuml start :Use the Manage Systems option; :In the "Administration Options" window, click Manage Systems; :The list of host names, port numbers, display names, and descriptions is displayed; :Click Add; :The "Add System" dialog box appears; :Add the host name, port number, display name, and the description in the appropriate fields; :Click Add to add the system; :The host system is added to the list; stop @enduml
### rac-0013
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2326
- relation_f1: 0.0238
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
  - shut down and end the process
  - transition to state 156
  - dcdc state remains 1?
  - move to state 157
  - eas state monitoring
  - fast charging deactivates?
- missing_relations:
  - enter state 155 -> condtion judgement
  - condtion judgement -> dcdc state=1
  - dcdc state=1 -> stay in state 155
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
- input_excerpt:
  After the system starts up: if fast charging is active and the BMS manual charging/discharging flag is 0, the system enters state 155. While in state 155:  1. For DCDC state monitoring:    - If DCDC state remains 1, stay in state 155.    - If the BMS-fast charger handshake flag becomes 1, transition to state 156.    - If DCDC state is not 1 or 3 seconds pass, move to state 157.    - If fast charging becomes inactive at any point, shut down and end the process.  2. For EAS state monitoring:    - If EAS state stays at 1, remain in state 155.    - If the handshake flag turns to 1, switch to state 156.    - If EAS state isn’t 1 or 3 seconds elapse, shift to state 157.    - Should fast charging d
- generated_excerpt:
  @startuml start :System starts up; if (Fast charging is active\nand BMS manual charging/discharging flag is 0?) then (yes)   :Enter state 155;   fork     :DCDC state monitoring;     if (Fast charging becomes inactive?) then (yes)       :Shut down and end the process;       stop     else (no)       if (BMS-fast charger handshake flag becomes 1?) then (yes)         :Transition to state 156;         stop       elseif (DCDC state remains 1?) then (yes)         :Stay in state 155;       else (no: DCDC state is not 1 or 3 seconds pass)         :Move to state 157;         stop       endif     endif   fork again     :EAS state monitoring;     if (Fast charging deactivates?) then (yes)       :Shut do
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2564
- relation_f1: 0.0541
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - click manage dependencies
  - list of infoobjects and their dependents is displayed
  - open select dependents drop-down list
  - dependents are displayed on the right
  - selection
- extra_nodes:
  - click manage dependencies in the promotion jobs home page
  - select an option from the select dependents drop-down list to add dependents to the job
  - explicitly select the dependents you want to promote
  - view the supported filtering options of infoobjects in the drop-down list
  - select a filtering option and click ok
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
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :Click Manage Dependencies in the "Promotion Jobs" home page; :The "Manage Dependencies" window appears; :Select an option from the Select Dependents drop-down list to add dependents to the job; :Explicitly select the dependents you want to promote; :View the supported filtering options of infoobjects in the drop-down list; :Select a filtering option and click OK; :The filtered infoobjects are displayed; :Click Apply Changes to update the list of dependents; :Click Apply Changes and Close to save the changes; stop @enduml
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3692
- relation_f1: 0.2222
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
  - select configure diagnostics menu item from the file menu
  - user authenticated as administrator?
  - authenticate user
  - user action
  - populate window with data from disk file
  - click save button
  - request confirmation to save changes
  - user confirms?
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - select configure diagnostics menu item -> administrator user?
  - administrator user? -> include (authenticate user)
  - include (authenticate user) -> have appropriate privilege?
  - display configuration window -> click recall button
  - populate window with disk file data -> change configuration?
  - change configuration? -> click save
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start :Select "Configure Diagnostics" menu item from the "File" menu; if (User authenticated as administrator?) then (No)   :Authenticate User; else (Yes) endif if (User has appropriate privilege?) then (Yes)   :Display configuration window;   switch (User action)   case (Click "Recall" button)     :Read previously saved changes from disk file or database;     :Populate window with data from disk file;   case (Click "Save" button)     :Request confirmation to save changes;     if (User confirms?) then (Yes)       :Request name for disk file;       switch (User response)       case (Enter name for file)         :Save changes;         if (Save operation completes?) then (Yes)        
### lmc-0016
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- missing_nodes:
  - autopilot is not requesting support (not request
  - limits are not exceeded (not limits
- extra_nodes:
  - autopilot is not requesting support and limits are not exceeded?
- missing_relations:
  - autopilot is not requesting support (not request -> limits are not exceeded (not limits
  - limits are not exceeded (not limits -> sensor change states from fault to transition
- input_excerpt:
  12.	The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting support (not request) and limits are not exceeded (not limits).
- generated_excerpt:
  @startuml start if (Autopilot is not requesting support and limits are not exceeded?) then (yes)   :Change sensor state from FAULT to TRANSITION; else (no) endif stop @enduml
### pure-0026
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.0000
- missing_nodes:
  - national value reactions
  - etcs trainborne equipment command emergency brake
  - failure be shown on dmi
  - failure be shown on dmi
  - etcs trainborne equipment command full service brake
  - train proceed to authority end
- extra_nodes:
  - national value
  - command emergency brake immediately
  - show failure on dmi
  - show failure on dmi
  - command full service brake immediately
  - proceed unrestricted to end of movement authority
- missing_relations:
  - transmission failure -> national value reactions
  - national value reactions -> option 1
  - option 1 -> etcs trainborne equipment command emergency brake
  - etcs trainborne equipment command emergency brake -> failure be shown on dmi
  - failure be shown on dmi -> option 2
  - option 2 -> etcs trainborne equipment command full service brake
  - etcs trainborne equipment command full service brake -> failure be shown on dmi
  - failure be shown on dmi -> option 3
- input_excerpt:
  When the event of a Transmission Failure, the following reactions shall be capable of being applied in accordance with a National Value: Option 1: The ETCS trainborne equipment shall immediately command the emergency brake. The failure shall be shown on the DMI. Option 2: The ETCS trainborne equipment shall immediately command the full service brake. The failure shall be shown on the DMI. Option 3: The train may proceed unrestricted to the end of its movement authority. The indication on the DMI shall remain, and the driver shall be informed about the loss of transmission.
- generated_excerpt:
  @startuml start :Transmission Failure occurs; switch (National Value) case (Option 1)   :Command emergency brake immediately;   :Show failure on DMI; case (Option 2)   :Command full service brake immediately;   :Show failure on DMI; case (Option 3)   :Proceed unrestricted to end of movement authority;   :Maintain indication on DMI;   :Inform driver about loss of transmission; endswitch @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
