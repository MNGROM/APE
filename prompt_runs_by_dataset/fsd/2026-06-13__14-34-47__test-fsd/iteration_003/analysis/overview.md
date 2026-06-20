# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3234
- node_recall: 0.2756
- node_f1: 0.2914
- relation_precision: 0.2229
- relation_recall: 0.2048
- relation_f1: 0.2113
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
  - fault
  - fault
  - autopilot not requesting support and limits not exceeded?
  - transition
- missing_relations:
  - autopilot is not requesting support (not request -> limits are not exceeded (not limits
  - limits are not exceeded (not limits -> sensor change states from fault to transition
- input_excerpt:
  12.	The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting support (not request) and limits are not exceeded (not limits).
- generated_excerpt:
  @startuml start :FAULT; if (Autopilot not requesting support and limits not exceeded?) then (yes)   :TRANSITION; else (no)   :FAULT; endif stop @enduml
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1739
- relation_f1: 0.0000
- missing_nodes:
  - go to administration options window
  - list is displayed
  - host names
  - port numbers
  - display names
  - descriptions
  - click add
  - add system dialog box appears
- extra_nodes:
  - display list of host names port numbers display names and descriptions
  - display add system dialog box
  - add host name port number display name and description
  - click add to add the system
  - host system is added to the list
- missing_relations:
  - go to administration options window -> click manage syetems
  - click manage syetems -> list is displayed
  - list is displayed -> host names
  - host names -> port numbers
  - port numbers -> display names
  - display names -> descriptions
  - descriptions -> click add
  - click add -> add system dialog box appears
- input_excerpt:
  15.	use the Manage Systems optionTo add a host system, complete the following steps:1. In the "Administration Options" window, click Manage Systems.The list of host names, port numbers, display names, and descriptions isdisplayed.2. Click Add.The "Add System" dialog box appears.3. Add the host name, port number, display name, and the description inthe appropriate fields.4. Click Add to add the system.The host system is added to the list.
- generated_excerpt:
  @startuml start :Click Manage Systems; :Display list of host names, port numbers, display names, and descriptions; :Click Add; :Display "Add System" dialog box; :Add host name, port number, display name, and description; :Click Add to add the system; :Host system is added to the list; stop @enduml
### rac-0013
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1860
- relation_f1: 0.0714
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
  - the system enters state 155
  - dcdc state monitoring
  - fast charging becomes inactive at any point?
  - shut down and end the process
  - transition to state 156
  - dcdc state is not 1 or 3 seconds pass?
  - move to state 157
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
  @startuml start :System starts up; if (fast charging is active and the BMS manual charging/discharging flag is 0?) then (yes)   :the system enters state 155;   fork     :DCDC state monitoring;     if (fast charging becomes inactive at any point?) then (yes)       :shut down and end the process;       stop     elseif (BMS-fast charger handshake flag becomes 1?) then (yes)       :transition to state 156;     elseif (DCDC state is not 1 or 3 seconds pass?) then (yes)       :move to state 157;     else (DCDC state remains 1)       :stay in state 155;     endif   fork again     :EAS state monitoring;     if (fast charging deactivates?) then (yes)       :shut down and terminate;       stop     els
### lmc-0050
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- missing_nodes:
  - =dcm321 * vi?
  - allowed
  - not allowed
- extra_nodes:
  - get input inertial vector vi
  - get 3x3 rotation matrix output dcm321
  - calculate 3x1 vector product of dcm321 times vi
- missing_relations:
  - body vector output vb -> =dcm321 * vi?
  - =dcm321 * vi? -> allowed
  - allowed -> not allowed
- input_excerpt:
  2.	The Body Vector Output, Vb, of this Function Shall Equal a 3x1 Vector Product of the 3x3 Rotation Matrix Output, DCM321, times the Input Inertial Vector, Vi.
- generated_excerpt:
  @startuml start :Get Input Inertial Vector, Vi; :Get 3x3 Rotation Matrix Output, DCM321; :Calculate 3x1 Vector Product of DCM321 times Vi; :Set Body Vector Output, Vb; stop @enduml
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
  - record workflow plan details in neurohub
  - record execution history in neurohub
  - record results in neurohub
- missing_relations:
  - execute workflow -> get the details of the workflow plan
  - get the details of the workflow plan -> get the execution history
  - get the execution history -> get results recorded in neurohub
- input_excerpt:
  As a researcher, I want to have the details of the workflow plan as well as the execution history and results recorded in Neurohub while executing a workflow
- generated_excerpt:
  @startuml start fork   :Execute workflow; fork again   :Record workflow plan details in Neurohub; fork again   :Record execution history in Neurohub; fork again   :Record results in Neurohub; end fork stop @enduml
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2564
- relation_f1: 0.1081
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - manage dependencies window appears
  - list of infoobjects and their dependents is displayed
  - open select dependents drop-down list
  - dependents are displayed on the right
  - selection
- extra_nodes:
  - select an option from the select dependents drop-down list
  - option is all universes ?
  - explicitly select the dependents you want to promote
  - filter infoobjects?
  - view supported filtering options select an option and click ok
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
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :Click Manage Dependencies; :Select an option from the Select Dependents drop-down list; if (Option is "All Universes"?) then (yes)   :All universes are automatically selected; else (no)   :Explicitly select the dependents you want to promote; endif if (Filter infoobjects?) then (yes)   :View supported filtering options, select an option, and click OK; endif :Click Apply Changes to update the list of dependents; :Click Apply Changes and Close to save the changes; end @enduml
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3810
- relation_f1: 0.3279
- missing_nodes:
  - presented with main window
  - open file menu
  - administrator user?
  - include (authenticate user)
  - read previously saved changes from disk file/database
  - populate window with disk file data
  - change configuration?
  - click save
- extra_nodes:
  - authenticated as administrator?
  - authenticate user
  - populate window with data from disk file
  - make desired changes to configuration
  - button clicked?
  - save
  - request confirmation to save changes
  - confirms save?
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - select configure diagnostics menu item -> administrator user?
  - administrator user? -> include (authenticate user)
  - click recall button -> read previously saved changes from disk file/database
  - read previously saved changes from disk file/database -> populate window with disk file data
  - populate window with disk file data -> change configuration?
  - change configuration? -> click save
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start :Select "Configure Diagnostics" menu item; if (Authenticated as administrator?) then (No)   :Authenticate User; else (Yes) endif if (Has appropriate privilege?) then (Yes)   :Display configuration window; else (No)   stop endif if (Click "Recall" button?) then (Yes)   :Populate window with data from disk file; else (No) endif :Make desired changes to configuration; switch (Button clicked?) case ( "Save" )   :Request confirmation to save changes;   if (Confirms save?) then (Yes)     :Request name for disk file;     switch (User action?)     case ( "Enter name" )       :Save changes;       :Ask if changes are to be relayed to diagnostic processing;       if (Confirms relay?) th
### pure-0026
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4167
- relation_f1: 0.0909
- missing_nodes:
  - national value reactions
  - etcs trainborne equipment command emergency brake
  - failure be shown on dmi
  - failure be shown on dmi
  - etcs trainborne equipment command full service brake
  - train proceed to authority end
  - inform driver about transmission loss
- extra_nodes:
  - national value
  - command the emergency brake immediately
  - show the failure on the dmi
  - show the failure on the dmi
  - command the full service brake immediately
  - proceed unrestricted to the end of its movement authority
  - inform the driver about the loss of transmission
- missing_relations:
  - national value reactions -> option 1
  - option 1 -> etcs trainborne equipment command emergency brake
  - etcs trainborne equipment command emergency brake -> failure be shown on dmi
  - failure be shown on dmi -> option 2
  - option 2 -> etcs trainborne equipment command full service brake
  - etcs trainborne equipment command full service brake -> failure be shown on dmi
  - failure be shown on dmi -> option 3
  - option 3 -> train proceed to authority end
- input_excerpt:
  When the event of a Transmission Failure, the following reactions shall be capable of being applied in accordance with a National Value: Option 1: The ETCS trainborne equipment shall immediately command the emergency brake. The failure shall be shown on the DMI. Option 2: The ETCS trainborne equipment shall immediately command the full service brake. The failure shall be shown on the DMI. Option 3: The train may proceed unrestricted to the end of its movement authority. The indication on the DMI shall remain, and the driver shall be informed about the loss of transmission.
- generated_excerpt:
  @startuml start :Transmission Failure; switch (National Value) case (Option 1)   :Command the emergency brake immediately;   :Show the failure on the DMI; case (Option 2)   :Command the full service brake immediately;   :Show the failure on the DMI; case (Option 3)   :Proceed unrestricted to the end of its movement authority;   :Remain the indication on the DMI;   :Inform the driver about the loss of transmission; endswitch stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
