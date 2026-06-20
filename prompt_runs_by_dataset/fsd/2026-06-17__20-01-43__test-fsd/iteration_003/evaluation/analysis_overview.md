# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4418
- node_recall: 0.3884
- node_f1: 0.4134
- relation_precision: 0.4218
- relation_recall: 0.3512
- relation_f1: 0.3833
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 10.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.9303
- llm_node_recall: 0.8028
- llm_node_f1: 0.8519
- llm_relation_precision: 0.7892
- llm_relation_recall: 0.6042
- llm_relation_f1: 0.6631

## Failure Types
- missing_activity: 10
- extra_activity: 10
- missing_or_wrong_relation: 8
- extra_or_wrong_relation: 8
- wrong_parallel: 2

## Representative Failure Cases
### lmc-0050
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5455
- llm_relation_f1: 0.4000
- missing_nodes:
  - body vector output vb
  - =dcm321 * vi?
  - allowed
  - not allowed
- extra_nodes:
  - calculate the 3x3 rotation matrix output dcm321
  - calculate the input inertial vector vi
  - calculate the body vector output vb as the 3x1 vector product of dcm321 times vi
- missing_relations:
  - body vector output vb -> =dcm321 * vi?
  - =dcm321 * vi? -> allowed [yes]
  - =dcm321 * vi? -> not allowed [no]
- input_excerpt:
  2.	The Body Vector Output, Vb, of this Function Shall Equal a 3x1 Vector Product of the 3x3 Rotation Matrix Output, DCM321, times the Input Inertial Vector, Vi.
- generated_excerpt:
  @startuml start :Calculate the 3x3 Rotation Matrix Output, DCM321; :Calculate the Input Inertial Vector, Vi; :Calculate the Body Vector Output, Vb, as the 3x1 vector product of DCM321 times Vi; stop @enduml
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2727
- relation_f1: 0.1481
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.4848
- missing_nodes:
  - go to administration options window
  - click manage syetems
  - list is displayed
  - host names
  - port numbers
  - display names
  - descriptions
  - add information
- extra_nodes:
  - click manage systems
  - the list of host names port numbers display names and descriptions is displayed
  - add the host name port number display name and the description in the appropriate fields
  - click add to add the system
- missing_relations:
  - go to administration options window -> click manage syetems
  - click manage syetems -> list is displayed
  - list is displayed -> host names [fork]
  - list is displayed -> port numbers [fork]
  - list is displayed -> display names [fork]
  - list is displayed -> descriptions [fork]
  - host names -> click add [merge]
  - port numbers -> click add [merge]
- input_excerpt:
  15.	use the Manage Systems optionTo add a host system, complete the following steps:1. In the "Administration Options" window, click Manage Systems.The list of host names, port numbers, display names, and descriptions isdisplayed.2. Click Add.The "Add System" dialog box appears.3. Add the host name, port number, display name, and the description inthe appropriate fields.4. Click Add to add the system.The host system is added to the list.
- generated_excerpt:
  @startuml start :Click Manage Systems; :The list of host names, port numbers, display names, and descriptions is displayed; :Click Add; :The "Add System" dialog box appears; :Add the host name, port number, display name, and the description in the appropriate fields; :Click Add to add the system; :The host system is added to the list; @enduml
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3077
- relation_f1: 0.2188
- llm_element_status: success
- llm_node_f1: 0.8923
- llm_relation_f1: 0.6076
- missing_nodes:
  - presented with main window
  - open file menu
  - administrator user?
  - include (authenticate user)
  - have appropriate privilege?
  - click recall button
  - change configuration?
  - click save
- extra_nodes:
  - user has not already been authenticated as the administrator user?
  - authenticate user
  - user has the appropriate privilege?
  - user clicks?
  - request confirmation to save the changes
  - user confirms?
  - request a name for the disk file in which to save the modified data to permanent storage
  - user enters a name for the file or cancels the operation?
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - administrator user? -> include (authenticate user) [no]
  - administrator user? -> have appropriate privilege? [yes]
  - include (authenticate user) -> have appropriate privilege? [merge]
  - have appropriate privilege? -> click recall button [no]
  - display configuration window -> click recall button [merge]
  - populate window with disk file data -> change configuration?
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start :Select "Configure Diagnostics" menu item from the "File" menu; if (User has not already been authenticated as the administrator user?) then (Yes)   :Authenticate User; else (No) endif if (User has the appropriate privilege?) then (Yes)   :Display the configuration window;   switch (User clicks?)   case ("Recall" button)     :Read previously saved changes from a disk file or database;     :Populate the window with the data from the disk file;   case ("Save" button)     :Request confirmation to save the changes;     if (User confirms?) then (Yes)       :Request a name for the disk file in which to save the modified data to permanent storage;       if (User enters a name for th
### rac-0013
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3158
- relation_f1: 0.2540
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.5934
- missing_nodes:
  - condtion judgement
  - dcdc state 1 or 3s elapsed
  - shutdown
  - eas state=1
  - eas state 1 or 3s elapsed
  - power battery current=6.1
  - current<6.1 or 3s elapsed
  - wtch state=1
- extra_nodes:
  - shut down and end the process
  - transition to state 156
  - dcdc state is not 1 or 3 seconds pass?
  - move to state 157
  - fast charging deactivates?
  - shut down and terminate
  - eas state stays at 1?
  - remain in state 155
- missing_relations:
  - enter state 155 -> condtion judgement
  - condtion judgement -> dcdc state=1 [case dcdc state=1]
  - stay in state 155 -> bms-fast charger handshake flag=1
  - switch to state 156 -> dcdc state 1 or 3s elapsed
  - dcdc state 1 or 3s elapsed -> switch to state 157 [yes]
  - switch to state 157 -> fast charging is inactive
  - condtion judgement -> eas state=1 [case eas state=1]
  - switch to state 156 -> eas state 1 or 3s elapsed
- input_excerpt:
  After the system starts up: if fast charging is active and the BMS manual charging/discharging flag is 0, the system enters state 155. While in state 155:  1. For DCDC state monitoring:    - If DCDC state remains 1, stay in state 155.    - If the BMS-fast charger handshake flag becomes 1, transition to state 156.    - If DCDC state is not 1 or 3 seconds pass, move to state 157.    - If fast charging becomes inactive at any point, shut down and end the process.  2. For EAS state monitoring:    - If EAS state stays at 1, remain in state 155.    - If the handshake flag turns to 1, switch to state 156.    - If EAS state isn’t 1 or 3 seconds elapse, shift to state 157.    - Should fast charging d
- generated_excerpt:
  @startuml start if (fast charging is active and BMS manual charging/discharging flag is 0?) then (yes)   :Enter state 155;   fork     if (fast charging becomes inactive?) then (yes)       :shut down and end the process;       stop     else (no)       if (DCDC state remains 1?) then (yes)         :stay in state 155;       elseif (BMS-fast charger handshake flag becomes 1?) then (yes)         :transition to state 156;       elseif (DCDC state is not 1 or 3 seconds pass?) then (yes)         :move to state 157;       endif     endif   fork again     if (fast charging deactivates?) then (yes)       :shut down and terminate;       stop     else (no)       if (EAS state stays at 1?) then (yes)     
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3889
- relation_f1: 0.3684
- llm_element_status: success
- llm_node_f1: 0.8095
- llm_relation_f1: 0.6190
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - click manage dependencies
  - list of infoobjects and their dependents is displayed
  - open select dependents drop-down list
  - selection
  - dependents are not selected
- extra_nodes:
  - in the promotion jobs home page click manage dependencies
  - from the select dependents drop-down list select any of the options available to add the dependents to the job
  - explicitly select the dependents you want to promote
  - select an option and click ok
  - click apply changes to update the list of dependents
  - click apply changes and close to save the changes
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37 [yes]
  - see creating a new job on page 37 -> add required infoobjects to new job [merge]
  - click manage dependencies -> manage dependencies window appears
  - manage dependencies window appears -> list of infoobjects and their dependents is displayed
  - list of infoobjects and their dependents is displayed -> open select dependents drop-down list
  - open select dependents drop-down list -> dependents are displayed on the right
  - dependents are displayed on the right -> selection
- input_excerpt:
  22.	manage dependencies of an infoobject1. Log into the LifeCycle Manager tool.2. Create a new job. For information on creating a new job, see Creating aNew Job on page 37.3. Add the required infoobjects to the new job.4. In the "Promotion Jobs" home page, click Manage Dependencies. The "Manage Dependencies" window appears. This window displays the list of infoobjects and their dependents, as shown in the following figure:5. From the Select Dependents drop-down list, select any of the options available to add the dependents to the job. The dependents are displayed on the right side. The dependents are not selected by default; you must explicitly select the dependents you want to promote. For
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :In the "Promotion Jobs" home page, click Manage Dependencies; :The "Manage Dependencies" window appears; :From the Select Dependents drop-down list, select any of the options available to add the dependents to the job; :The dependents are displayed on the right side; :Explicitly select the dependents you want to promote; :Click to view the supported filtering options of infoobjects in the drop-down list; :Select an option, and click OK; :The filtered infoobjects are displayed; :Click Apply Changes to update the list of dependents; :Click Apply Changes and Close to save the 
### lmc-0016
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.6000
- missing_nodes:
  - limits are not exceeded (not limits)?
  - sensor change states from fault to transition
- extra_nodes:
  - change states from fault to transition
- missing_relations:
  - autopilot is not requesting support (not request)? -> limits are not exceeded (not limits)? [yes]
  - limits are not exceeded (not limits)? -> sensor change states from fault to transition [yes]
- input_excerpt:
  12.	The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting support (not request) and limits are not exceeded (not limits).
- generated_excerpt:
  @startuml start if (Autopilot is not requesting support\nand limits are not exceeded?) then (yes)   :Change states from FAULT to TRANSITION; endif stop @enduml
### us-0129
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 0.8333
- llm_relation_f1: 0.5714
- missing_nodes:
  - get the details of the workflow plan
  - get the execution history
- extra_nodes:
  - record details of the workflow plan in neurohub
  - record execution history in neurohub
- missing_relations:
  - execute workflow -> get the details of the workflow plan [fork]
  - execute workflow -> get the execution history [fork]
  - get the details of the workflow plan -> execute workflow [merge]
  - get the execution history -> execute workflow [merge]
- input_excerpt:
  As a researcher, I want to have the details of the workflow plan as well as the execution history and results recorded in Neurohub while executing a workflow
- generated_excerpt:
  @startuml start :Execute a workflow; fork :Record details of the workflow plan in Neurohub; fork again :Record execution history in Neurohub; fork again :Record results in Neurohub; end fork @enduml
### us-0056
- dataset: us
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - correct problems
- extra_nodes:
  - correct problems for members
- input_excerpt:
  As a site administrator, I want to edit any site member profile, so that I can correct problems for members.
- generated_excerpt:
  @startuml start :Edit any site member profile; :Correct problems for members; stop @enduml
### pure-0026
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5263
- relation_f1: 0.4762
- llm_element_status: success
- llm_node_f1: 0.9524
- llm_relation_f1: 0.7826
- missing_nodes:
  - national value reactions
  - option 1
  - option 2
  - option 3
  - train proceed to authority end
  - remain indication on dm
- extra_nodes:
  - in accordance with a national value
  - the train may proceed unrestricted to the end of its movement authority
  - the indication on the dmi shall remain
- missing_relations:
  - national value reactions -> option 1 [case option 1]
  - national value reactions -> option 2 [case option 2]
  - national value reactions -> option 3 [case option 3]
  - option 3 -> train proceed to authority end
  - train proceed to authority end -> remain indication on dm
  - remain indication on dm -> inform driver about transmission loss
  - failure be shown on dmi -> national value reactions [merge]
  - inform driver about transmission loss -> national value reactions [merge]
- input_excerpt:
  When the event of a Transmission Failure, the following reactions shall be capable of being applied in accordance with a National Value: Option 1: The ETCS trainborne equipment shall immediately command the emergency brake. The failure shall be shown on the DMI. Option 2: The ETCS trainborne equipment shall immediately command the full service brake. The failure shall be shown on the DMI. Option 3: The train may proceed unrestricted to the end of its movement authority. The indication on the DMI shall remain, and the driver shall be informed about the loss of transmission.
- generated_excerpt:
  @startuml start :Transmission Failure; switch (In accordance with a National Value) case (Option 1)   :The ETCS trainborne equipment shall immediately command the emergency brake;   :The failure shall be shown on the DMI; case (Option 2)   :The ETCS trainborne equipment shall immediately command the full service brake;   :The failure shall be shown on the DMI; case (Option 3)   :The train may proceed unrestricted to the end of its movement authority;   :The indication on the DMI shall remain;   :The driver shall be informed about the loss of transmission; endswitch stop @enduml
### rac-0015
- dataset: rac
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7692
- relation_f1: 0.8772
- llm_element_status: success
- llm_node_f1: 0.9302
- llm_relation_f1: 0.9722
- missing_nodes:
  - condition judgement
  - shutdown
  - after 30s?
- extra_nodes:
  - system starts up
  - condition
  - fast charging becomes inactive?
  - shut down
  - fast charging is also inactive?
  - after 30 seconds
- missing_relations:
  - switch to state 185 -> after 30s?
  - after 30s? -> switch to state 180
- input_excerpt:
  After the system starts up, if fast charging is active, it enters the "power-up" state. If a high-voltage shutdown request equals 2 and the DCDC state is 1, the system then enters state 175. Following this:  1.  If the DCDC state becomes 0, switch to state 185. Then:     a.  If fast charging becomes inactive, switch to state 180. Shut down and end.     b.  If the power battery relay control equals 0, switch to state 180. Shut down and end.     c.  If a pre-charge failure occurs, switch to state 180. If fast charging is also inactive at this point, shut down and end.  2.  If the DCDC state is 0 and the insulation resistance is low, switch to state 185. After 30 seconds, switch to state 180. I
- generated_excerpt:
  @startuml start :System starts up; if (Fast charging is active?) then (yes)   :Enter "power-up" state;   if (High-voltage shutdown request equals 2\nand DCDC state is 1?) then (yes)     :Enter state 175;     switch (Condition)     case (DCDC state becomes 0)       :Switch to state 185;       if (Fast charging becomes inactive?) then (yes)         :Switch to state 180;         :Shut down;         end       elseif (Power battery relay control equals 0?) then (yes)         :Switch to state 180;         :Shut down;         end       elseif (Pre-charge failure occurs?) then (yes)         :Switch to state 180;         if (Fast charging is also inactive?) then (yes)           :Shut down;           

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
