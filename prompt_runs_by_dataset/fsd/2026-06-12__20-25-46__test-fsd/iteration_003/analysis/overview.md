# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3072
- node_recall: 0.3239
- node_f1: 0.3075
- relation_precision: 0.1200
- relation_recall: 0.1170
- relation_f1: 0.1169
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
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10

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
  - receive input inertial vector vi
  - receive 3x3 rotation matrix output dcm321
  - multiply dcm321 by vi
  - set body vector output vb equal to the 3x1 vector product
- missing_relations:
  - body vector output vb -> =dcm321 * vi?
  - =dcm321 * vi? -> allowed
  - allowed -> not allowed
- input_excerpt:
  2.	The Body Vector Output, Vb, of this Function Shall Equal a 3x1 Vector Product of the 3x3 Rotation Matrix Output, DCM321, times the Input Inertial Vector, Vi.
- generated_excerpt:
  @startuml start :Receive Input Inertial Vector, Vi; :Receive 3x3 Rotation Matrix Output, DCM321; :Multiply DCM321 by Vi; :Set Body Vector Output, Vb, equal to the 3x1 vector product; @enduml
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1379
- relation_f1: 0.0741
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
  - display list of host names
  - display port numbers
  - display display names
  - display descriptions
  - show add system dialog box
  - add the host name
  - add the port number
  - add the display name
- missing_relations:
  - go to administration options window -> click manage syetems
  - click manage syetems -> list is displayed
  - list is displayed -> host names
  - host names -> port numbers
  - port numbers -> display names
  - display names -> descriptions
  - click add -> add system dialog box appears
  - add system dialog box appears -> add information
- input_excerpt:
  15.	use the Manage Systems optionTo add a host system, complete the following steps:1. In the "Administration Options" window, click Manage Systems.The list of host names, port numbers, display names, and descriptions isdisplayed.2. Click Add.The "Add System" dialog box appears.3. Add the host name, port number, display name, and the description inthe appropriate fields.4. Click Add to add the system.The host system is added to the list.
- generated_excerpt:
  @startuml start partition User {     :Click Manage Systems; } partition System {     :Display list of host names;     :Display port numbers;     :Display display names;     :Display descriptions; } partition User {     :Click Add; } partition System {     :Show "Add System" dialog box; } partition User {     :Add the host name;     :Add the port number;     :Add the display name;     :Add the description;     :Click Add to add the system; } partition System {     :Add the host system to the list; } @enduml
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2188
- relation_f1: 0.0968
- missing_nodes:
  - presented with main window
  - open file menu
  - select configure diagnostics menu item
  - administrator user?
  - include (authenticate user)
  - click recall button
  - read previously saved changes from disk file/database
  - populate window with disk file data
- extra_nodes:
  - select configure diagnostics menu item from the file menu
  - user has not already been authenticated as the administrator user?
  - authenticate user
  - click the recall button to read previously saved changes from a disk file or database
  - populate the window with the data from the disk file
  - make the desired changes to the configuration
  - user clicks button?
  - save
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - select configure diagnostics menu item -> administrator user?
  - administrator user? -> include (authenticate user)
  - include (authenticate user) -> have appropriate privilege?
  - display configuration window -> click recall button
  - click recall button -> read previously saved changes from disk file/database
  - read previously saved changes from disk file/database -> populate window with disk file data
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start partition User {     :Select "Configure Diagnostics" menu item from the "File" menu; } if (User has not already been authenticated as the administrator user?) then (Yes)     :Authenticate User; else (No) endif if (User has the appropriate privilege?) then (Yes)     partition Tool {         :Display the configuration window;     }     partition User {         :Click the "Recall" button to read previously saved changes from a disk file or database;     }     partition Tool {         :Populate the window with the data from the disk file;     }     partition User {         :Make the desired changes to the configuration;     }     switch (User clicks button?)     case (Save)      
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
  - record details of the workflow plan in neurohub
  - record execution history in neurohub
  - record results in neurohub
- missing_relations:
  - execute workflow -> get the details of the workflow plan
  - get the details of the workflow plan -> get the execution history
  - get the execution history -> get results recorded in neurohub
- input_excerpt:
  As a researcher, I want to have the details of the workflow plan as well as the execution history and results recorded in Neurohub while executing a workflow
- generated_excerpt:
  @startuml start partition Researcher {  :Execute a workflow;  fork   :Record details of the workflow plan in Neurohub;  fork again   :Record execution history in Neurohub;  fork again   :Record results in Neurohub;  end fork } @enduml
### lmc-0016
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.0000
- missing_nodes:
  - limits are not exceeded (not limits
  - sensor change states from fault to transition
- extra_nodes:
  - sensor is in fault state
  - limits are not exceeded?
  - change state to transition
- missing_relations:
  - autopilot is not requesting support (not request -> limits are not exceeded (not limits
  - limits are not exceeded (not limits -> sensor change states from fault to transition
- input_excerpt:
  12.	The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting support (not request) and limits are not exceeded (not limits).
- generated_excerpt:
  @startuml start :Sensor is in FAULT state; if (Autopilot is not requesting support?) then (yes)   if (Limits are not exceeded?) then (yes)     :Change state to TRANSITION;   else (no)   endif else (no) endif stop @enduml
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
  - save the profile changes
- missing_relations:
  - edit site member profile -> correct problems
- input_excerpt:
  As a site administrator, I want to edit any site member profile, so that I can correct problems for members.
- generated_excerpt:
  @startuml start partition "Site Administrator" {   :Select a site member profile;   :Edit the site member profile;   :Correct problems for the member;   :Save the profile changes; } stop @enduml
### pure-0026
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
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
  - in accordance with a national value
  - immediately command the emergency brake
  - show the failure
  - show the failure
  - immediately command the full service brake
  - proceed unrestricted to the end of its movement authority
  - remain the indication
  - inform about the loss of transmission
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
  @startuml start :Transmission Failure occurs; switch (In accordance with a National Value) case (Option 1)   partition "ETCS trainborne equipment" {     :Immediately command the emergency brake;   }   partition "DMI" {     :Show the failure;   } case (Option 2)   partition "ETCS trainborne equipment" {     :Immediately command the full service brake;   }   partition "DMI" {     :Show the failure;   } case (Option 3)   partition "Train" {     :Proceed unrestricted to the end of its movement authority;   }   partition "DMI" {     :Remain the indication;   }   partition "Driver" {     :Inform about the loss of transmission;   } endswitch stop @enduml
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3721
- relation_f1: 0.1463
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
  - display the list of infoobjects and their dependents
  - from the select dependents drop-down list select any of the options available to add the dependents to the job
  - dependents are not selected by default?
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
  @startuml start partition User {     :Log into the LifeCycle Manager tool;     :Create a new job;     :Add the required infoobjects to the new job;     :In the "Promotion Jobs" home page, click Manage Dependencies; } partition System {     :The "Manage Dependencies" window appears;     :Display the list of infoobjects and their dependents; } partition User {     :From the Select Dependents drop-down list, select any of the options available to add the dependents to the job; } partition System {     :The dependents are displayed on the right side; } partition User {     if (Dependents are not selected by default?) then (Yes)         :Explicitly select the dependents you want to promote;     e

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
