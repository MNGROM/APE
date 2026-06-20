# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3599
- node_recall: 0.3693
- node_f1: 0.3563
- relation_precision: 0.2145
- relation_recall: 0.2078
- relation_f1: 0.2094
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
- missing_or_wrong_relation: 9
- extra_or_wrong_relation: 9
- syntax_error: 1

## Representative Failure Cases
### pure-0026
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.3333
- relation_f1: 0.0000
- missing_nodes:
  - national value reactions
  - etcs trainborne equipment command emergency brake
  - failure be shown on dmi
  - failure be shown on dmi
  - etcs trainborne equipment command full service brake
  - train proceed to authority end
  - remain indication on dm
  - inform driver about transmission loss
- extra_nodes:
  - national value?
  - the etcs trainborne equipment shall immediately command the emergency brake
  - the failure shall be shown on the dmi
  - the failure shall be shown on the dmi
  - the etcs trainborne equipment shall immediately command the full service brake
  - the train may proceed unrestricted to the end of its movement authority
  - the indication on the dmi shall remain
  - the driver shall be informed about the loss of transmission
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
  @startuml start if (Transmission Failure event?) then (yes)   switch (National Value?)   case (Option 1)     :The ETCS trainborne equipment shall immediately command the emergency brake;     :The failure shall be shown on the DMI;   endcase   case (Option 2)     :The ETCS trainborne equipment shall immediately command the full service brake;     :The failure shall be shown on the DMI;   endcase   case (Option 3)     :The train may proceed unrestricted to the end of its movement authority;     fork       :The indication on the DMI shall remain;     fork again       :the driver shall be informed about the loss of transmission;     end fork   endcase   endswitch endif stop @enduml
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
  - calculate the 3x3 rotation matrix output dcm321
  - receive the input inertial vector vi
  - compute the 3x1 vector product of dcm321 times vi
  - set the body vector output vb to the computed 3x1 vector product
- missing_relations:
  - body vector output vb -> =dcm321 * vi?
  - =dcm321 * vi? -> allowed
  - allowed -> not allowed
- input_excerpt:
  2.	The Body Vector Output, Vb, of this Function Shall Equal a 3x1 Vector Product of the 3x3 Rotation Matrix Output, DCM321, times the Input Inertial Vector, Vi.
- generated_excerpt:
  @startuml start :Calculate the 3x3 Rotation Matrix Output, DCM321; :Receive the Input Inertial Vector, Vi; :Compute the 3x1 Vector Product of DCM321 times Vi; :Set the Body Vector Output, Vb, to the computed 3x1 Vector Product; @enduml
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0606
- relation_f1: 0.0312
- missing_nodes:
  - presented with main window
  - open file menu
  - select configure diagnostics menu item
  - administrator user?
  - include (authenticate user)
  - have appropriate privilege?
  - display configuration window
  - populate window with disk file data
- extra_nodes:
  - select the configure diagnostics menu item from the menu entitled file
  - the user has not already been authenticated as the administrator user
  - authenticate user
  - the user has the appropriate privilege
  - the tool displays the configuration window
  - user action
  - the tool populates the window with the data from the disk file
  - the user makes the desired changes to the configuration
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - select configure diagnostics menu item -> administrator user?
  - administrator user? -> include (authenticate user)
  - include (authenticate user) -> have appropriate privilege?
  - have appropriate privilege? -> display configuration window
  - display configuration window -> click recall button
  - read previously saved changes from disk file/database -> populate window with disk file data
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start :Select the "Configure Diagnostics" menu item from the menu entitled "File"; if (The user has not already been authenticated as the administrator user) then (Yes)   :Authenticate User; else (No) endif if (The user has the appropriate privilege) then (Yes)   :The tool displays the configuration window;   switch (User action)   case (Click the "Recall" button)     :Read previously saved changes from a disk file or database;     :The tool populates the window with the data from the disk file;     :The user makes the desired changes to the configuration;   case (Click the button labeled "Save")     :The user makes the desired changes to the configuration;     :The tool will reque
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1333
- relation_f1: 0.0714
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
  - the list of host names is displayed
  - the list of port numbers is displayed
  - the list of display names is displayed
  - the list of descriptions is displayed
  - add the host name in the appropriate fields
  - add the port number in the appropriate fields
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
  @startuml start :use the Manage Systems option; :In the "Administration Options" window, click Manage Systems; fork :The list of host names is displayed; fork again :The list of port numbers is displayed; fork again :The list of display names is displayed; fork again :The list of descriptions is displayed; end fork :Click Add; :The "Add System" dialog box appears; :Add the host name in the appropriate fields; :Add the port number in the appropriate fields; :Add the display name in the appropriate fields; :Add the description in the appropriate fields; :Click Add to add the system; :The host system is added to the list; @enduml
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
  - record the details of the workflow plan in neurohub
  - record the execution history in neurohub
  - record the results in neurohub
- missing_relations:
  - execute workflow -> get the details of the workflow plan
  - get the details of the workflow plan -> get the execution history
  - get the execution history -> get results recorded in neurohub
- input_excerpt:
  As a researcher, I want to have the details of the workflow plan as well as the execution history and results recorded in Neurohub while executing a workflow
- generated_excerpt:
  @startuml start partition "Researcher" {   :Execute a workflow;   fork     :Record the details of the workflow plan in Neurohub;   fork again     :Record the execution history in Neurohub;   fork again     :Record the results in Neurohub;   end fork } @enduml
### rac-0013
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2772
- relation_f1: 0.0808
- missing_nodes:
  - fast charging is active and bms manual charging/discharging flag=0
  - condtion judgement
  - dcdc state=1
  - bms-fast charger handshake flag=1
  - bms-fast charger handshake flag=1
  - bms-fast charger handshake flag=1
  - bms-fast charger handshake flag=1
  - switch to state 156
- extra_nodes:
  - bms manual charging/discharging flag is 0
  - dcdc state monitoring
  - shut down and end the process
  - dcdc state remains 1
  - transition to state 156
  - dcdc state is not 1 or 3 seconds pass
  - move to state 157
  - in state 155
- missing_relations:
  - fast charging is active and bms manual charging/discharging flag=0 -> enter state 155
  - enter state 155 -> condtion judgement
  - condtion judgement -> dcdc state=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - stay in state 155 -> bms-fast charger handshake flag=1
  - bms-fast charger handshake flag=1 -> switch to state 156
- input_excerpt:
  After the system starts up: if fast charging is active and the BMS manual charging/discharging flag is 0, the system enters state 155. While in state 155:  1. For DCDC state monitoring:    - If DCDC state remains 1, stay in state 155.    - If the BMS-fast charger handshake flag becomes 1, transition to state 156.    - If DCDC state is not 1 or 3 seconds pass, move to state 157.    - If fast charging becomes inactive at any point, shut down and end the process.  2. For EAS state monitoring:    - If EAS state stays at 1, remain in state 155.    - If the handshake flag turns to 1, switch to state 156.    - If EAS state isn’t 1 or 3 seconds elapse, shift to state 157.    - Should fast charging d
- generated_excerpt:
  @startuml start if (fast charging is active) then (yes)   if (BMS manual charging/discharging flag is 0) then (yes)     :enter state 155;     fork       :DCDC state monitoring;       repeat         if (fast charging becomes inactive) then (yes)           :shut down and end the process;           stop         else (no)           if (DCDC state remains 1) then (yes)             :stay in state 155;           else (no)             if (BMS-fast charger handshake flag becomes 1) then (yes)               :transition to state 156;               stop             else (no)               if (DCDC state is not 1 or 3 seconds pass) then (yes)                 :move to state 157;                 stop      
### us-0056
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.0000
- missing_nodes:
  - correct problems
- extra_nodes:
  - select a site member profile
  - correct problems for the member
  - save the profile
- missing_relations:
  - edit site member profile -> correct problems
- input_excerpt:
  As a site administrator, I want to edit any site member profile, so that I can correct problems for members.
- generated_excerpt:
  @startuml partition "Site Administrator" {   start   :Select a site member profile;   :Edit the site member profile;   :Correct problems for the member;   :Save the profile;   stop } @enduml
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3810
- relation_f1: 0.1500
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
  - this window displays the list of infoobjects and their dependents
  - from the select dependents drop-down list select any of the options available to add the dependents to the job
  - explicitly select the dependents you want to promote
  - click to view the supported filtering options of infoobjects in the drop-down list
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
  @startuml start partition "User" {   :Log into the LifeCycle Manager tool;   :Create a new job;   :Add the required infoobjects to the new job;   :In the "Promotion Jobs" home page, click Manage Dependencies; } partition "System" {   :The "Manage Dependencies" window appears;   :This window displays the list of infoobjects and their dependents; } partition "User" {   :From the Select Dependents drop-down list, select any of the options available to add the dependents to the job; } partition "System" {   :The dependents are displayed on the right side; } partition "User" {   :explicitly select the dependents you want to promote;   :Click to view the supported filtering options of infoobjects 

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
