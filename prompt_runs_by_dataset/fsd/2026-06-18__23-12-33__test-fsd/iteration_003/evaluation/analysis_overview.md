# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4759
- node_recall: 0.5074
- node_f1: 0.4912
- relation_precision: 0.3315
- relation_recall: 0.3703
- relation_f1: 0.3498
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8166
- llm_node_recall: 0.8166
- llm_node_f1: 0.8057
- llm_relation_precision: 0.5389
- llm_relation_recall: 0.5417
- llm_relation_f1: 0.5213

## Failure Types
- extra_or_wrong_relation: 20
- extra_activity: 19
- missing_activity: 17
- missing_or_wrong_relation: 17
- wrong_parallel: 5

## Representative Failure Cases
### bp-0030
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.2353
- llm_element_status: success
- llm_node_f1: 0.9756
- llm_relation_f1: 0.3158
- missing_nodes:
  - log in
  - go to promotion jobs
  - click new job
  - enter name
  - enter description
  - enter keywords
  - go to save job field
  - browse and select the folder
- extra_nodes:
  - log into the lifecycle manager tool
  - in the promotion jobs home page click new job
  - enter the name description and keywords for the job in the appropriate fields
  - in the save job in field browse and select the folder in which you want to save the job
  - select the source system and the destination system from the drop-down lists
  - is the name of the system displayed in the drop-down list?
  - click the login to a new cms option
  - enter the name of the system along with the user name and password
- missing_relations:
  - log in -> go to promotion jobs
  - click new job -> new job window appears
  - new job window appears -> enter name [fork]
  - new job window appears -> enter description [fork]
  - new job window appears -> enter keywords [fork]
  - enter name -> go to save job field [merge]
  - enter description -> go to save job field [merge]
  - enter keywords -> go to save job field [merge]
- input_excerpt:
  30.	Creating a New Job1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriate fields.4. In the Save Job in field, browse and select the folder in which you want to save the job.5. Select the source system and the destination system from the drop-down lists. If the name of the system is not displayed in the drop-down list, click the Login to a new CMS option. A new window is launched. Enter the name of the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name, description, and keywords for the job in the appropriate fields; :In the Save Job in field, browse and select the folder in which you want to save the job; :Select the source system and the destination system from the drop-down lists; if (Is the name of the system displayed in the drop-down list?) then (No)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the name of the system along with the user name and password; else (Yes) endif :Click Create; stop @enduml
### us-0129
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7143
- llm_relation_f1: 0.3750
- missing_nodes:
  - get the details of the workflow plan
  - get the execution history
  - get results recorded in neurohub
- extra_nodes:
  - researcher
  - display workflow plan details
  - display execution history
  - display results
  - record in neurohub
- missing_relations:
  - execute workflow -> get the details of the workflow plan [fork]
  - execute workflow -> get the execution history [fork]
  - execute workflow -> get results recorded in neurohub [fork]
  - get the details of the workflow plan -> execute workflow [merge]
  - get the execution history -> execute workflow [merge]
  - get results recorded in neurohub -> execute workflow [merge]
- input_excerpt:
  As a researcher, I want to have the details of the workflow plan as well as the execution history and results recorded in Neurohub while executing a workflow
- generated_excerpt:
  @startuml start :Researcher; switch (Workflow Execution) case (Workflow Plan)   :Display workflow plan details; case (Execution History)   :Display execution history; case (Results)   :Display results; endswitch :Record in Neurohub; stop @enduml
### lmc-0050
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5000
- llm_relation_f1: 0.1818
- missing_nodes:
  - =dcm321 * vi?
  - allowed
  - not allowed
- extra_nodes:
  - input inertial vector vi
  - 3x3 rotation matrix output dcm321
  - calculate 3x1 vector product of dcm321 times vi
- missing_relations:
  - body vector output vb -> =dcm321 * vi?
  - =dcm321 * vi? -> allowed [yes]
  - =dcm321 * vi? -> not allowed [no]
- input_excerpt:
  2.	The Body Vector Output, Vb, of this Function Shall Equal a 3x1 Vector Product of the 3x3 Rotation Matrix Output, DCM321, times the Input Inertial Vector, Vi.
- generated_excerpt:
  @startuml start :Input Inertial Vector, Vi; :3x3 Rotation Matrix Output, DCM321; :Calculate 3x1 Vector Product of DCM321 times Vi; :Body Vector Output, Vb; @enduml
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.6154
- llm_element_status: success
- llm_node_f1: 0.9444
- llm_relation_f1: 0.9545
- missing_nodes:
  - go to administration options window
  - click manage syetems
  - list is displayed
  - host names
  - port numbers
  - descriptions
  - add information
  - host name
- extra_nodes:
  - click manage systems in the administration options window
  - display list of host names
  - display list of port numbers
  - display list of descriptions
  - add host name in the appropriate field
  - add port number in the appropriate field
  - add display name in the appropriate field
  - add description in the appropriate field
- missing_relations:
  - go to administration options window -> click manage syetems
  - click manage syetems -> list is displayed
  - list is displayed -> host names [fork]
  - list is displayed -> port numbers [fork]
  - list is displayed -> display names [fork]
  - list is displayed -> descriptions [fork]
  - add system dialog box appears -> add information
  - add information -> display name [fork]
- input_excerpt:
  15.	use the Manage Systems optionTo add a host system, complete the following steps:1. In the "Administration Options" window, click Manage Systems.The list of host names, port numbers, display names, and descriptions isdisplayed.2. Click Add.The "Add System" dialog box appears.3. Add the host name, port number, display name, and the description inthe appropriate fields.4. Click Add to add the system.The host system is added to the list.
- generated_excerpt:
  @startuml start :Click Manage Systems in the "Administration Options" window; fork :Display list of host names; fork again :Display list of port numbers; fork again :Display list of display names; fork again :Display list of descriptions; end fork :Click Add; :"Add System" dialog box appears; fork :Add host name in the appropriate field; fork again :Add port number in the appropriate field; fork again :Add display name in the appropriate field; fork again :Add description in the appropriate field; end fork :Click Add to add the system; :The host system is added to the list; @enduml
### lmc-0017
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.3636
- llm_relation_f1: 0.0000
- missing_nodes:
  - autopilot is requesting support (request)?
  - sensor change states from transition to nominal
- extra_nodes:
  - transition
  - nominal
- missing_relations:
  - autopilot reports the correct active mode (mode)? -> sensor change states from transition to nominal [yes]
- input_excerpt:
  13.	The sensor shall change states from TRANSITION to NOMINAL when the autopilot is requesting support (request) and the autopilot reports the correct active mode (mode).
- generated_excerpt:
  @startuml start :TRANSITION; if (Autopilot is requesting support (request)\nand autopilot reports the correct active mode (mode)?) then (yes)   :NOMINAL; else (no)   :TRANSITION; endif stop @enduml
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3636
- relation_f1: 0.1714
- llm_element_status: success
- llm_node_f1: 0.8065
- llm_relation_f1: 0.6000
- missing_nodes:
  - presented with main window
  - open file menu
  - administrator user?
  - include (authenticate user)
  - click recall button
  - read previously saved changes from disk file/database
  - populate window with disk file data
  - change configuration?
- extra_nodes:
  - authenticated as administrator user?
  - authenticate user
  - user makes desired changes to configuration
  - user clicks?
  - request confirmation to save changes
  - user confirms?
  - request name for disk file
  - user enters name?
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - administrator user? -> include (authenticate user) [no]
  - administrator user? -> have appropriate privilege? [yes]
  - include (authenticate user) -> have appropriate privilege? [merge]
  - have appropriate privilege? -> click recall button [no]
  - display configuration window -> click recall button [merge]
  - click recall button -> read previously saved changes from disk file/database
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start :Select "Configure Diagnostics" menu item from "File" menu; if (Authenticated as administrator user?) then (No)   :Authenticate User; endif if (Has appropriate privilege?) then (Yes)   :Display configuration window;   repeat     :User makes desired changes to configuration;     if (User clicks?) then ("Save" button)       :Request confirmation to save changes;       if (User confirms?) then (Yes)         :Request name for disk file;         if (User enters name?) then (Yes)           :Save changes to disk file;           if (Save operation completes?) then (Yes)             :Ask user if changes are to be relayed to diagnostic processing;             if (User confirms relay?) 
### rac-0013
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3704
- relation_f1: 0.2500
- llm_element_status: success
- llm_node_f1: 0.7576
- llm_relation_f1: 0.1239
- missing_nodes:
  - condtion judgement
  - dcdc state 1 or 3s elapsed
  - shutdown
  - eas state 1 or 3s elapsed
  - power battery current=6.1
  - current<6.1 or 3s elapsed
  - wtch state=1
  - wtch state=3
- extra_nodes:
  - system starts up
  - dcdc state monitoring
  - shut down
  - transition to state 156
  - move to state 157
  - 3 seconds pass?
  - eas state monitoring
  - handshake flag is 1?
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
  @startuml start :System starts up; if (Fast charging is active\nand BMS manual charging/discharging flag is 0?) then (yes)   :Enter state 155;   fork     :DCDC state monitoring;     repeat       if (Fast charging inactive?) then (yes)         :Shut down;         stop       else (no)         if (BMS-fast charger handshake flag is 1?) then (yes)           :Transition to state 156;           stop         elseif (DCDC state is 1?) then (yes)           :Stay in state 155;         else (no)           :Move to state 157;           stop         endif       endif     repeat while (3 seconds pass?) is (yes)     ->no;        fork again     :EAS state monitoring;     repeat       if (Fast charging inact
### pure-0097
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0800
- llm_element_status: success
- llm_node_f1: 0.9565
- llm_relation_f1: 0.7143
- missing_nodes:
  - filters
  - url
  - mime-types
  - size
  - timestamp
  - use provided pattern
  - stop
- extra_nodes:
  - filter type
  - filter by url
  - filter by mime-types
  - filter by size
  - filter by timestamp
- missing_relations:
  - use command warc_repackage -i options -> filters
  - filters -> url [fork]
  - filters -> mime-types [fork]
  - filters -> size [fork]
  - filters -> timestamp [fork]
  - url -> extract and repackage warc records [merge]
  - mime-types -> extract and repackage warc records [merge]
  - size -> extract and repackage warc records [merge]
- input_excerpt:
  Repackaging Tool Execution: Use the command warc_repackage -i <WARC_FILE> <WARC_PATTERN> [options] to extract and repackage WARC records based on filters like URL, MIME-Types, size, or timestamp. Specify output WARC file names using the provided pattern and include metadata records describing the extraction context.
- generated_excerpt:
  @startuml start :Use command warc_repackage -i <WARC_FILE> <WARC_PATTERN> [options]; :Extract and repackage WARC records; switch (Filter type) case (URL)   :Filter by URL; case (MIME-Types)   :Filter by MIME-Types; case (Size)   :Filter by size; case (Timestamp)   :Filter by timestamp; endswitch :Specify output WARC file names using the provided pattern; :Include metadata records describing the extraction context; @enduml
### lmc-0016
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.4000
- missing_nodes:
  - limits are not exceeded (not limits)?
  - sensor change states from fault to transition
- extra_nodes:
  - change state from fault to transition
- missing_relations:
  - autopilot is not requesting support (not request)? -> limits are not exceeded (not limits)? [yes]
  - limits are not exceeded (not limits)? -> sensor change states from fault to transition [yes]
  - autopilot is not requesting support (not request)? -> limits are not exceeded (not limits)? [no]
  - limits are not exceeded (not limits)? -> autopilot is not requesting support (not request)? [no]
- input_excerpt:
  12.	The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting support (not request) and limits are not exceeded (not limits).
- generated_excerpt:
  @startuml start if (Autopilot is not requesting support and limits are not exceeded?) then (yes)   :Change state from FAULT to TRANSITION; else (no) endif @enduml
### bp-0018
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.1429
- llm_element_status: success
- llm_node_f1: 0.7368
- llm_relation_f1: 0.3333
- missing_nodes:
  - go to promotionjobs screen
  - click the preferences link
  - open enter the maximum page size dialog box
  - go to promotion jobs screen
  - specify the number
  - open show jobs created drop-down list
  - select time interval
- extra_nodes:
  - click the preferences link in the promotion jobs screen
  - in the enter the maximum page size dialog box specify the number of objects that must be displayed per page in the promotion jobs screen
- missing_relations:
  - click the preferences link -> preferences window appears
  - preferences window appears -> open enter the maximum page size dialog box
  - open enter the maximum page size dialog box -> go to promotion jobs screen
  - go to promotion jobs screen -> specify the number
  - specify the number -> open show jobs created drop-down list
  - open show jobs created drop-down list -> select time interval
  - select time interval -> view the jobs created during the specified period
  - view the jobs created during the specified period -> click ok
- input_excerpt:
  18.	specify the number of jobs that must be displayed in the "PromotionJobs" screen. You can also view jobs that were created during a particulartime interval.To set preferences, complete the following steps:1. In the "Promotion Jobs" screen, click the Preferences link.The "Preferences" window appears.2. In the "Enter the Maximum Page Size" dialog box, specify the number ofobjects that must be displayed per page in the "Promotion Jobs" screen.3. From the Show Jobs Created drop-down list, select the time interval toview the jobs created during the specified period.4. Click OK.
- generated_excerpt:
  @startuml start :Click the Preferences link in the "Promotion Jobs" screen; :"Preferences" window appears; fork   :In the "Enter the Maximum Page Size" dialog box, specify the number of objects that must be displayed per page in the "Promotion Jobs" screen; fork again   :From the Show Jobs Created drop-down list, select the time interval to view the jobs created during the specified period; end fork :Click OK; @enduml
### us-0056
- dataset: us
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.8571
- missing_nodes:
  - correct problems
- extra_nodes:
  - select site member profile
  - correct problems for members
- input_excerpt:
  As a site administrator, I want to edit any site member profile, so that I can correct problems for members.
- generated_excerpt:
  @startuml |Site Administrator| start :Select site member profile; :Edit site member profile; :Correct problems for members; stop @enduml
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4737
- relation_f1: 0.4390
- llm_element_status: success
- llm_node_f1: 0.8636
- llm_relation_f1: 0.6222
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - click manage dependencies
  - open select dependents drop-down list
  - selection
  - all universes are automatically selected
  - dependents are added to job
- extra_nodes:
  - in the promotion jobs home page click manage dependencies
  - from the select dependents drop-down list select an option to add dependents to the job
  - explicitly select the dependents you want to promote
  - select an option and click ok
  - click apply changes to update the list of dependents
  - click apply changes and close to save the changes
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37 [yes]
  - see creating a new job on page 37 -> add required infoobjects to new job [merge]
  - click manage dependencies -> manage dependencies window appears
  - list of infoobjects and their dependents is displayed -> open select dependents drop-down list
  - open select dependents drop-down list -> dependents are displayed on the right
  - selection -> dependents are not selected [case no]
  - selection -> all universes are automatically selected [case all universes]
- input_excerpt:
  22.	manage dependencies of an infoobject1. Log into the LifeCycle Manager tool.2. Create a new job. For information on creating a new job, see Creating aNew Job on page 37.3. Add the required infoobjects to the new job.4. In the "Promotion Jobs" home page, click Manage Dependencies. The "Manage Dependencies" window appears. This window displays the list of infoobjects and their dependents, as shown in the following figure:5. From the Select Dependents drop-down list, select any of the options available to add the dependents to the job. The dependents are displayed on the right side. The dependents are not selected by default; you must explicitly select the dependents you want to promote. For
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :In the "Promotion Jobs" home page, click Manage Dependencies; :"Manage Dependencies" window appears; :Display the list of infoobjects and their dependents; :From the Select Dependents drop-down list, select an option to add dependents to the job; :Display the dependents on the right side; if (Dependents are not selected by default?) then (yes)   :Explicitly select the dependents you want to promote; else (no) endif :Click to view the supported filtering options of infoobjects in the drop-down list; :Select an option, and click OK; :Display the filtered infoobjects; :Click A
### lmc-0052
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.2857
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - not invertible
  - invertible
- extra_nodes:
  - dcm321 is not invertible
  - dcm321 is invertible
- missing_relations:
  - theta = +/- pi/2 radians? -> not invertible [yes]
  - theta = +/- pi/2 radians? -> invertible [no]
  - not invertible -> invertible [merge]
- input_excerpt:
  4.	The Rotation Matrix, DCM321, shall be invertible with the exception of the case where theta = +/- pi/2 radians.
- generated_excerpt:
  @startuml start :Compute Rotation Matrix DCM321; if (theta = +/- pi/2 radians?) then (yes)   :DCM321 is not invertible; else (no)   :DCM321 is invertible; endif stop @enduml
### pure-0026
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5263
- relation_f1: 0.2857
- llm_element_status: success
- llm_node_f1: 0.9474
- llm_relation_f1: 0.8571
- missing_nodes:
  - national value reactions
  - train proceed to authority end
  - remain indication on dm
- extra_nodes:
  - national value
  - option 1
  - option 2
  - option 3
  - train may proceed unrestricted to the end of its movement authority
  - the indication on the dmi shall remain
- missing_relations:
  - national value reactions -> etcs trainborne equipment command emergency brake [case option 1]
  - national value reactions -> etcs trainborne equipment command full service brake [case option 2]
  - national value reactions -> train proceed to authority end [case option 3]
  - train proceed to authority end -> remain indication on dm
  - remain indication on dm -> inform driver about transmission loss
- input_excerpt:
  When the event of a Transmission Failure, the following reactions shall be capable of being applied in accordance with a National Value: Option 1: The ETCS trainborne equipment shall immediately command the emergency brake. The failure shall be shown on the DMI. Option 2: The ETCS trainborne equipment shall immediately command the full service brake. The failure shall be shown on the DMI. Option 3: The train may proceed unrestricted to the end of its movement authority. The indication on the DMI shall remain, and the driver shall be informed about the loss of transmission.
- generated_excerpt:
  @startuml start :Transmission Failure; switch (National Value) case (Option 1)   :ETCS trainborne equipment immediately commands the emergency brake;   :Show the failure on the DMI; case (Option 2)   :ETCS trainborne equipment immediately commands the full service brake;   :Show the failure on the DMI; case (Option 3)   :Train may proceed unrestricted to the end of its movement authority;   :The indication on the DMI shall remain;   :Inform the driver about the loss of transmission; endswitch @enduml
### pure-0095
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6000
- relation_f1: 0.2222
- llm_element_status: success
- llm_node_f1: 0.5714
- llm_relation_f1: 0.1429
- missing_nodes:
  - refer to provided configuration
  - specify how fields are translated into warc records
  - handle missing fields
- extra_nodes:
  - are there missing fields?
- missing_relations:
  - use command arc_warc_migrate options -> refer to provided configuration
  - refer to provided configuration -> specify how fields are translated into warc records [fork]
  - refer to provided configuration -> generate errors requiring operator intervention [fork]
  - generate errors requiring operator intervention -> handle missing fields
  - specify how fields are translated into warc records -> migrate content from arc files to warc files [merge]
- input_excerpt:
  Migration Tool Execution: Use the command arc_warc_migrate <ARC_FILES> <CONFIG> [options] to migrate content from ARC files to WARC files based on the provided configuration. Ensure the configuration file specifies how fields are translated into WARC records, and handle missing fields by generating errors requiring operator intervention.
- generated_excerpt:
  @startuml start :Use command arc_warc_migrate <ARC_FILES> <CONFIG> [options]; :Migrate content from ARC files to WARC files based on the provided configuration; if (Are there missing fields?) then (yes)   :Generate errors requiring operator intervention; else (no) endif stop @enduml
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6286
- relation_f1: 0.4545
- llm_element_status: success
- llm_node_f1: 0.8302
- llm_relation_f1: 0.6557
- missing_nodes:
  - condition judgement
  - shutdown
  - wait 0.8s
- extra_nodes:
  - system starts up
  - move to state 175
  - fast charging remains inactive?
  - shut down
  - wait 0.8 seconds
  - enter state 175
  - fast charging is inactive afterward?
  - high-voltage shutdown request (value=2) exists?
- missing_relations:
  - switch to state 153 -> bms-fast charger handshake flag=0 and front mcu high-voltage flag=0
  - enter state 155 -> condition judgement
  - condition judgement -> pre-charge failure occurs [case pre-charge failure occurs]
  - condition judgement -> high-voltage shutdown request charging/discharging =2 [case high-voltage shutdown request charging/discharging =2]
  - high-voltage shutdown request charging/discharging =2 -> wait 0.8s
  - wait 0.8s -> switch to state 175
  - condition judgement -> ignition switch=2 [case ignition switch=2]
  - stay in state 155 -> high-voltage shutdown request charging/discharging =2
- input_excerpt:
  After the system starts up: - If charging is active (charging=1) and the front MCU high-voltage detection flag is 0, transition to state 153. - If the BMS-fast charger handshake flag is 0 and the front MCU high-voltage flag is 0, enter state 155.  While in state 155: 1. If pre-charge failure occurs, move to state 175. If fast charging remains inactive after this, shut down and end the process. 2. If a high-voltage shutdown request (for charging/discharging) is detected (value=2), wait 0.8 seconds before entering state 175. If fast charging is inactive afterward, shut down and end. 3. If the ignition switch status is 2, remain in state 155. If a high-voltage shutdown request (value=2) exists 
- generated_excerpt:
  @startuml start :System starts up;  if (Charging is active (charging=1)\nand front MCU high-voltage\ndetection flag is 0?) then (yes)   :Transition to state 153;   stop elseif (BMS-fast charger handshake flag is 0\nand front MCU high-voltage flag is 0?) then (yes)   :Enter state 155; else (no)   stop endif  if (Pre-charge failure occurs?) then (yes)   :Move to state 175;   if (Fast charging remains inactive?) then (yes)     :Shut down;     end   else (no)     stop   endif elseif (High-voltage shutdown request\n(for charging/discharging) is detected\n(value=2)?) then (yes)   :Wait 0.8 seconds;   :Enter state 175;   if (Fast charging is inactive afterward?) then (yes)     :Shut down;     end  
### us-0073
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.5000
- extra_nodes:
  - store information
  - provide information to admins next year
- missing_relations:
  - keep information in one place -> improve on previous years
- input_excerpt:
  As a camp administrator, I want to be able to keep my information in one place, so that the admins next year can improve on the previous years.
- generated_excerpt:
  @startuml |Camp Administrator| start :Keep information in one place; |System| :Store information; :Provide information to admins next year; |Camp Administrator| :Improve on the previous years; stop @enduml
### rac-0015
- dataset: rac
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7692
- relation_f1: 0.8136
- llm_element_status: success
- llm_node_f1: 0.9778
- llm_relation_f1: 0.9714
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
  - wait 30 seconds
- missing_relations:
  - switch to state 185 -> after 30s?
  - after 30s? -> switch to state 180
  - switch to state 180 -> gw_trigger=0
- input_excerpt:
  After the system starts up, if fast charging is active, it enters the "power-up" state. If a high-voltage shutdown request equals 2 and the DCDC state is 1, the system then enters state 175. Following this:  1.  If the DCDC state becomes 0, switch to state 185. Then:     a.  If fast charging becomes inactive, switch to state 180. Shut down and end.     b.  If the power battery relay control equals 0, switch to state 180. Shut down and end.     c.  If a pre-charge failure occurs, switch to state 180. If fast charging is also inactive at this point, shut down and end.  2.  If the DCDC state is 0 and the insulation resistance is low, switch to state 185. After 30 seconds, switch to state 180. I
- generated_excerpt:
  @startuml start :System starts up; if (Fast charging is active?) then (yes)   :Enter "power-up" state;   if (High-voltage shutdown request equals 2\nand DCDC state is 1?) then (yes)     :Enter state 175;     switch (Condition)     case (DCDC state becomes 0)       :Switch to state 185;       if (Fast charging becomes inactive?) then (yes)         :Switch to state 180;         :Shut down;         end       elseif (Power battery relay control equals 0?) then (yes)         :Switch to state 180;         :Shut down;         end       elseif (Pre-charge failure occurs?) then (yes)         :Switch to state 180;         if (Fast charging is also inactive?) then (yes)           :Shut down;           
### us-0093
- dataset: us
- failure_types: extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8000
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.2500
- extra_nodes:
  - discuss the particular data timeslice of interest with other people
- input_excerpt:
  As a Consumer, I want to view a Datapackage at a particular version online, so that that I can present/discuss the particular data timeslice of interest with other people.
- generated_excerpt:
  @startuml |Consumer| start :View a Datapackage at a particular version online; fork :Present the particular data timeslice of interest; fork again :Discuss the particular data timeslice of interest with other people; end fork; stop @enduml
### rac-0018
- dataset: rac
- failure_types: missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8889
- relation_f1: 0.7541
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.5714
- missing_nodes:
  - shutdown
  - condition judgement
- extra_nodes:
  - system starts up
  - shut down and exit
- missing_relations:
  - switch to state 95 -> power-up readiness and pre-heating demand exist
  - switch to state 93 -> condition judgement
  - condition judgement -> vehicle charging/discharging mode=1 and power battery charging demand=2 [case vehicle charging/discharging mode=1 and power battery charging demand=2]
  - condition judgement -> charging/discharging power-up guidance=2 or 3 [case charging/discharging power-up guidance=2 or 3]
  - condition judgement -> vehicle charging/discharging mode=1 [case vehicle charging/discharging mode=1]
  - condition judgement -> power battery charging demand=2 [case power battery charging demand=2]
  - condition judgement -> battery pre-heating demand=3 [case battery pre-heating demand=3]
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU high-voltage detection flag is 0, it switches to state 93. Then: 1. If the front MCU high-voltage flag is 1 and charging/discharging power-up is 1, the system switches to state 95.    a. If a pre-charge failure occurs, it switches to state 115. Additionally, if slow charging is inactive, the system shuts down and exits.    b. If an AC charging/discharging system fault occurs, it switches to state 115. Also, if slow charging is inactive, it shuts down and exits.    c. If slow charging is inactive, it switches to state 115 and then shuts down and exits. 2. If the DCDC state is 1 and there is no battery pre-heating demand,
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active\nand front MCU high-voltage detection flag is 0?) then (yes)   :Switch to state 93;      if (Front MCU high-voltage flag is 1\nand charging/discharging power-up is 1?) then (yes)     :Switch to state 95;          if (Pre-charge failure occurs?) then (yes)       :Switch to state 115;       if (Slow charging is inactive?) then (yes)         :Shut down and exit;         stop       endif     elseif (AC charging/discharging system fault occurs?) then (yes)       :Switch to state 115;       if (Slow charging is inactive?) then (yes)         :Shut down and exit;         stop       endif     elseif (Slow charging is inactive?) then (yes)

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
