# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4302
- node_recall: 0.3909
- node_f1: 0.4096
- relation_precision: 0.3919
- relation_recall: 0.3542
- relation_f1: 0.3721
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
- wrong_parallel: 5
- wrong_loop: 1

## Representative Failure Cases
### lmc-0042
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - 2-norm of output buminusd
  - < 0.01?
  - allowed
  - not allowed
- extra_nodes:
  - is the 2-norm of buminusd < 0.01?
- missing_relations:
  - 2-norm of output buminusd -> < 0.01?
  - < 0.01? -> allowed [yes]
  - < 0.01? -> not allowed [no]
- input_excerpt:
  4.	The 2-norm of the output Buminusd should be less than 0.01.
- generated_excerpt:
  @startuml start if (Is the 2-norm of Buminusd < 0.01?) then (Yes) else (No) endif @enduml
### lmc-0036
- dataset: lmc
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 1.0000
- missing_nodes:
  - input any value
  - allowed
  - not allowed
- extra_nodes:
  - process nn input values
  - accept nn output
  - reject nn output
- input_excerpt:
  2.	The minimum value of the NN output, z, shall always be greater than or equal to -0.2, regardless of the input values.
- generated_excerpt:
  @startuml start :Process NN input values; if (Is the minimum value of NN output z >= -0.2?) then (Yes)   :Accept NN output; else (No)   :Reject NN output; endif stop @enduml
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2692
- relation_f1: 0.1429
- missing_nodes:
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - open data source context menu
  - choose create info package...
  - enter description
- extra_nodes:
  - in the modeling area choose info provider
  - the transformation and the data source are displayed in the info area below the info cube sales overview
  - in the context menu of the data source choose create info package...
  - on the next screen enter a description for the info package and choose save
  - the info package maintenance screen for the scheduler appears
  - go to the tab page schedule and choose start
  - to check the load process choose monitor in the toolbar of info package maintenance
  - on the next screen select the date and choose execute
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation [fork]
  - info area displays information -> data source [fork]
  - transformation -> open data source context menu
  - data source -> open data source context menu
  - choose create info package... -> enter description
- input_excerpt:
  7.	Loading Transaction Data1. Go to the Data Warehousing Workbench; in the Modeling area choose Info Provider. The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview.2. In the context menu of the Data source, choose Create Info Package...3. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.4. Go to the tab page Schedule and choose Start.5. To check the load process, choose Monitor in the toolbar of Info Package maintenance.6. On the next screen, select the date and choose Execute. The monitor for the load process is displayed.7. Select the load process f
- generated_excerpt:
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose Info Provider; :The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview; :In the context menu of the Data source, choose Create Info Package...; :On the next screen, enter a description for the Info Package and choose Save; :The Info Package maintenance screen for the scheduler appears; :Go to the tab page Schedule and choose Start; :To check the load process, choose Monitor in the toolbar of Info Package maintenance; :On the next screen, select the date and choose Execute; :The monitor for the load process is displayed; :Select the load process for your Data s
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4091
- relation_f1: 0.3448
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - go to promotion jobs home page
  - select the job want to promote
  - right-click
  - open source and destination systems drop-down lists
  - select source and destination systems
  - enter appropriate value
- extra_nodes:
  - select the job to promote (alternatively right-click home page screen and click promote)
  - select source and destination systems from drop-down lists
  - stop
  - want to create and validate mappings?
  - security settings required?
  - security option
  - select do not promote security (default option)
  - select include application rights
- missing_relations:
  - log in lifecycle manager tool -> selection method
  - selection method -> go to promotion jobs home page [case 1]
  - go to promotion jobs home page -> select the job want to promote
  - selection method -> right-click [case 2]
  - right-click -> click promote
  - select the job want to promote -> open source and destination systems drop-down lists
  - click promote -> open source and destination systems drop-down lists
  - open source and destination systems drop-down lists -> select source and destination systems
- input_excerpt:
  23.	promote a jobLog into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, select the job that you want to promote. You can also right-click the home page screen, and click Promote.3. From the source and the destination systems drop-down lists, select the source and destination systems.Note:Ensure that you have logged into both the source and destination systems before you proceed with the promotion process.4. In the External Change Management ID field, enter the appropriate value, and click Save.5. Click Mappings. Click Edit Mappings if you want to create and validate mappings.6. Click Security Settings, if required. The following options are displayed:• Do not Promote Secur
- generated_excerpt:
  @startuml start :Select the job to promote\n(Alternatively: Right-click home page screen and click Promote); :Select source and destination systems\nfrom drop-down lists; if (Logged into both source\nand destination systems?) then (yes) else (no)   :Stop;   stop endif :Enter External Change Management ID; :Click Save; :Click Mappings; if (Want to create and validate mappings?) then (yes)   :Click Edit Mappings;   :Create and validate mappings; else (no) endif if (Security Settings required?) then (yes)   :Click Security Settings;   switch (Security Option)   case (Do not Promote Security)     :Select Do not Promote Security\n(Default option);   case (Promote Security)     :Select Promote Sec
### pure-0058
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4286
- relation_f1: 0.2667
- missing_nodes:
  - open keepass
  - select open->database
  - navigate through folders
  - select database
  - folder is suitable?
  - file not found appears
  - select another folder
  - password is right?
- extra_nodes:
  - user opens keepass and select open->database
  - user navigates through his folders
  - user selects a database
  - folder type suitable for database?
  - a message file not found appears
  - user selects another folder
  - master password is correct?
  - retry
- missing_relations:
  - open keepass -> select open->database
  - select open->database -> navigate through folders
  - navigate through folders -> select database
  - select database -> folder is suitable?
  - folder is suitable? -> file not found appears [no]
  - file not found appears -> select another folder
  - select another folder -> choose cancel
  - folder is suitable? -> choose cancel [yes]
- input_excerpt:
  1. User opens KeePass and select Open->Database 2. User navigates through his folders 3. User selects a database 4. User types Master Password 5. The main database window opens 3.2.2.2.1 Alternative Data Flow 1 3a. User selects a type of folder non suitable for database 3b. A message “file not found” appears 3c. User selects another folder 3.2.2.2.2 Alternative Data Flow 2 4a. Master Password is wrong 4b. A message “invalid/wrong key” appears 4c. User types another master key 3.2.2.2.3 Alternative Data Flow 3 3. User chooses cancel 4. Exit from KeePass
- generated_excerpt:
  @startuml start :User opens KeePass and select Open->Database; repeat   :User navigates through his folders;   if (User chooses cancel?) then (yes)     :Exit from KeePass;     stop   else (no)     :User selects a database;     if (Folder type suitable for database?) then (no)       :A message "file not found" appears;       :User selects another folder;     else (yes)       :User types Master Password;       if (Master Password is correct?) then (no)         :A message "invalid/wrong key" appears;         :User types another master key;       else (yes)         :The main database window opens;         stop       endif     endif   endif repeat while (retry) @enduml
### fsd-0009
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4727
- relation_f1: 0.3784
- missing_nodes:
  - operating on preemptive rtos
  - tcms manages via deterministic scheduling
  - traction
  - braking
  - doors
  - diagnostics
  - detect acceleration threshold exceedance
  - high-priority task
- extra_nodes:
  - inertial sensor detects vehicle acceleration threshold exceedance
  - medium-priority task evaluate need for esp intervention
  - cyclic task with mutex-protected ring buffer process wheel speed sensor data
  - esp active?
  - adjust electronic power steering system s output torque through can message with crc checksum
  - steering assist active?
  - state evaluation task assess overall vehicle stability
  - communication fault?
- missing_relations:
  - operating on preemptive rtos -> tcms manages via deterministic scheduling
  - tcms manages via deterministic scheduling -> traction [fork]
  - tcms manages via deterministic scheduling -> braking [fork]
  - tcms manages via deterministic scheduling -> doors [fork]
  - tcms manages via deterministic scheduling -> diagnostics [fork]
  - traction -> detect acceleration threshold exceedance
  - braking -> detect acceleration threshold exceedance
  - doors -> detect acceleration threshold exceedance
- input_excerpt:
  Operating on a preemptive RTOS, the Train Control and Monitoring System (TCMS) manages traction, braking, doors, and diagnostics via deterministic scheduling. Upon an inertial sensor detecting a vehicle acceleration threshold exceedance, the system first verifies brake system status via a protected BMS query. If braking pressure is deemed insufficient, a high-priority task immediately commands emergency braking assistance, while a concurrent, medium-priority task evaluates the need for Electronic Stability Program (ESP) intervention. During ESP activation, a cyclic task with a mutex-protected ring buffer processes wheel speed sensor data, calculates individual wheel slip rates, and executes 
- generated_excerpt:
  @startuml start :Inertial sensor detects vehicle acceleration threshold exceedance; :Verify brake system status via protected BMS query; if (Braking pressure insufficient?) then (yes)   fork     :High-priority task: Command emergency braking assistance;   fork again     :Medium-priority task: Evaluate need for ESP intervention;     if (ESP activation needed?) then (yes)       repeat         :Cyclic task with mutex-protected ring buffer: Process wheel speed sensor data;         :Calculate individual wheel slip rates;         :Execute real-time braking force distribution algorithm;       repeat while (ESP active?) is (yes) not (no)     endif   end fork   if (Steering angle sensor indicates ano
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4848
- relation_f1: 0.3000
- missing_nodes:
  - condition judgement
  - shutdown
  - wait 0.8s
  - high-voltage shutdown request charging/discharging =2
- extra_nodes:
  - system starts up
  - pre-charge failure occurs?
  - move to state 175
  - fast charging remains inactive?
  - shut down
  - high-voltage shutdown request detected (value=2)?
  - wait 0.8 seconds
  - enter state 175
- missing_relations:
  - switch to state 153 -> bms-fast charger handshake flag=0 and front mcu high-voltage flag=0
  - enter state 155 -> condition judgement
  - condition judgement -> switch to state 175 [case pre-charge failure occurs]
  - condition judgement -> wait 0.8s [case high-voltage shutdown request charging/discharging =2]
  - wait 0.8s -> switch to state 175
  - condition judgement -> stay in state 155 [case ignition switch=2]
  - stay in state 155 -> high-voltage shutdown request charging/discharging =2
  - high-voltage shutdown request charging/discharging =2 -> wait 0.8s [if yes]
- input_excerpt:
  After the system starts up: - If charging is active (charging=1) and the front MCU high-voltage detection flag is 0, transition to state 153. - If the BMS-fast charger handshake flag is 0 and the front MCU high-voltage flag is 0, enter state 155.  While in state 155: 1. If pre-charge failure occurs, move to state 175. If fast charging remains inactive after this, shut down and end the process. 2. If a high-voltage shutdown request (for charging/discharging) is detected (value=2), wait 0.8 seconds before entering state 175. If fast charging is inactive afterward, shut down and end. 3. If the ignition switch status is 2, remain in state 155. If a high-voltage shutdown request (value=2) exists 
- generated_excerpt:
  @startuml start :System starts up; if (Charging is active (charging=1)\nand front MCU high-voltage detection flag is 0?) then (yes)   :Transition to state 153; else (no)   if (BMS-fast charger handshake flag is 0\nand front MCU high-voltage flag is 0?) then (yes)     :Enter state 155;          if (Pre-charge failure occurs?) then (yes)       :Move to state 175;       if (Fast charging remains inactive?) then (yes)         :Shut down;         end       else (no)       endif     elseif (High-voltage shutdown request detected (value=2)?) then (yes)       :Wait 0.8 seconds;       :Enter state 175;       if (Fast charging is inactive afterward?) then (yes)         :Shut down;         end       el
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4906
- relation_f1: 0.2712
- missing_nodes:
  - presented with main window
  - open file menu
  - administrator user?
  - include (authenticate user)
  - click recall button
  - change configuration?
  - click save
  - request confirmation
- extra_nodes:
  - authenticated as administrator?
  - authenticate user
  - user action
  - request confirmation to save changes
  - user confirms save?
  - request name for disk file
  - user enters file name?
  - diagnostic processing currently active?
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - administrator user? -> include (authenticate user) [no]
  - administrator user? -> have appropriate privilege? [yes]
  - display configuration window -> click recall button
  - have appropriate privilege? -> click recall button [no]
  - populate window with disk file data -> change configuration?
  - change configuration? -> click save [yes]
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start :Select "Configure Diagnostics" from "File" menu; if (Authenticated as administrator?) then (No)   :Authenticate User; else (Yes) endif if (Has appropriate privilege?) then (Yes)   :Display configuration window;   switch (User action)   case (Click "Recall" button)     :Read previously saved changes from disk file or database;     :Populate window with data from disk file;   case (Click "Save" button)     :Request confirmation to save changes;     if (User confirms save?) then (Yes)       :Request name for disk file;       if (User enters file name?) then (Yes)         :Save changes;         if (Save operation completes?) then (Yes)           :Ask if changes are to be relayed

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
