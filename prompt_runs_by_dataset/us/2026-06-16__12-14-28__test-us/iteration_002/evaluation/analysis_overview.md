# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.8000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4485
- node_recall: 0.4041
- node_f1: 0.4252
- relation_precision: 0.3307
- relation_recall: 0.2793
- relation_f1: 0.3028
- plantuml_compilation_pass_rate: 0.8000
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
- wrong_parallel: 5
- wrong_loop: 2
- syntax_error: 2

## Representative Failure Cases
### pure-0058
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4286
- relation_f1: 0.2581
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
  - master password is wrong?
  - master password is correct?
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
  @startuml start :User opens KeePass and select Open->Database; repeat   :User navigates through his folders;   if (User chooses cancel?) then (yes)     :Exit from KeePass;     stop   else (no)     :User selects a database;     if (Folder type suitable for database?) then (no)       :A message "file not found" appears;       :User selects another folder;     else (yes)       repeat         :User types Master Password;         if (Master Password is wrong?) then (yes)           :A message "invalid/wrong key" appears;           :User types another master key;         else (no)         endif       until (Master Password is correct?) then (no)       repeat         :User types Master Password;    
### rac-0018
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.7097
- relation_f1: 0.6552
- missing_nodes:
  - shutdown
  - condition judgement
- extra_nodes:
  - system starts up
  - shut down and exit
  - vehicle charging/discharging mode is 1 and power battery charging demand is 2?
  - charging/discharging power-up guidance is 2 or 3?
  - vehicle charging/discharging mode is 1?
  - power battery charging demand is 2?
  - battery pre-heating demand is 3?
- missing_relations:
  - slow charging is inactive -> shutdown [if yes]
  - switch to state 95 -> power-up readiness and pre-heating demand exist
  - switch to state 93 -> condition judgement
  - condition judgement -> switch to state 115 [case charging/discharging power-up guidance=2 or 3]
  - condition judgement -> switch to state 115 [case vehicle charging/discharging mode=1]
  - condition judgement -> switch to state 115 [case power battery charging demand=2]
  - condition judgement -> switch to state 115 [case battery pre-heating demand=3]
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU high-voltage detection flag is 0, it switches to state 93. Then: 1. If the front MCU high-voltage flag is 1 and charging/discharging power-up is 1, the system switches to state 95.    a. If a pre-charge failure occurs, it switches to state 115. Additionally, if slow charging is inactive, the system shuts down and exits.    b. If an AC charging/discharging system fault occurs, it switches to state 115. Also, if slow charging is inactive, it shuts down and exits.    c. If slow charging is inactive, it switches to state 115 and then shuts down and exits. 2. If the DCDC state is 1 and there is no battery pre-heating demand,
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active\nand front MCU high-voltage detection flag is 0?) then (yes)   :Switch to state 93; else (no)   ;stop endif if (Front MCU high-voltage flag is 1\nand charging/discharging power-up is 1?) then (yes)   :Switch to state 95;   if (Pre-charge failure occurs?) then (yes)     :Switch to state 115;     if (Slow charging is inactive?) then (yes)       :Shut down and exit;       stop     else (no)     endif   elseif (AC charging/discharging system fault occurs?) then (yes)     :Switch to state 115;     if (Slow charging is inactive?) then (yes)       :Shut down and exit;       stop     else (no)     endif   elseif (Slow charging is inactiv
### lmc-0036
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - input any value
  - minimum value of nn output z >= -0.2?
  - allowed
  - not allowed
- extra_nodes:
  - receive nn output z
  - z >= -0.2?
  - accept z
  - reject z
- missing_relations:
  - input any value -> minimum value of nn output z >= -0.2?
  - minimum value of nn output z >= -0.2? -> allowed [yes]
  - minimum value of nn output z >= -0.2? -> not allowed [no]
- input_excerpt:
  2.	The minimum value of the NN output, z, shall always be greater than or equal to -0.2, regardless of the input values.
- generated_excerpt:
  @startuml start :Receive NN output z; if (z >= -0.2?) then (yes)   :Accept z; else (no)   :Reject z; endif stop @enduml
### lmc-0042
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.3333
- missing_nodes:
  - < 0.01?
  - allowed
  - not allowed
- extra_nodes:
  - 2-norm of buminusd < 0.01?
  - accept buminusd
  - reject buminusd
- missing_relations:
  - < 0.01? -> allowed [yes]
  - < 0.01? -> not allowed [no]
- input_excerpt:
  4.	The 2-norm of the output Buminusd should be less than 0.01.
- generated_excerpt:
  @startuml start :Check 2-norm of Buminusd; if (2-norm of Buminusd < 0.01?) then (Yes)   :Accept Buminusd; else (No)   :Reject Buminusd; endif stop @enduml
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2553
- relation_f1: 0.1569
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
  - in the context menu of the data source choose create info package...
  - enter a description for the info package and choose save
  - go to the tab page schedule and choose start
  - choose monitor in the toolbar of info package maintenance
  - select the date and choose execute
  - select the load process for your data source from the tree at the left of the screen
  - from the context menu of the data source choose create data transfer process....
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
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose Info Provider; :In the context menu of the Data source, choose Create Info Package...; :Enter a description for the Info Package and choose Save; :Go to the tab page Schedule and choose Start; :Choose Monitor in the toolbar of Info Package maintenance; :Select the date and choose Execute; :Select the load process for your Data source from the tree at the left of the screen; :Exit the Info Package maintenance screen; :From the context menu of the Data source, choose Create Data Transfer Process....; :Choose Continue; :Go to tab page Extraction and select extraction mode Full; :Activate the data transfer proces
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3421
- relation_f1: 0.2222
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - select the job want to promote
  - right-click
  - open source and destination systems drop-down lists
  - select source and destination systems
  - have logged into both source and destination systems
  - enter appropriate value
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - select the source and destination systems from the drop-down lists
  - security settings required?
  - select include application rights
  - select do not promote security
  - click view security to view security dependencies
  - view promotion details and status
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
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, select the job that you want to promote; :Select the source and destination systems from the drop-down lists; :Enter the appropriate value in the External Change Management ID field and click Save; :Click Mappings; if (Want to create and validate mappings?) then (yes)   :Click Edit Mappings; endif if (Security Settings required?) then (yes)   :Click Security Settings;   if (Promote Security?) then (yes)     :Select Promote Security;     if (Include application rights?) then (yes)       :Select Include application rights;     endif   else (no)     :Select Do not Promote Security;   endif   :
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4571
- relation_f1: 0.2439
- missing_nodes:
  - condition judgement
  - shutdown
  - wait 0.8s
  - high-voltage shutdown request charging/discharging =2
- extra_nodes:
  - state 153 entry conditions
  - pre-charge failure occurs?
  - move to state 175
  - fast charging remains inactive?
  - shut down and end the process
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
  @startuml start :State 153 Entry Conditions; if (Charging active (charging=1)\nand front MCU high-voltage detection flag is 0?) then (yes)   :Transition to state 153;   stop elseif (BMS-fast charger handshake flag is 0\nand front MCU high-voltage flag is 0?) then (yes) else (no)   stop endif  :Enter state 155;  if (Pre-charge failure occurs?) then (yes)   :Move to state 175;   if (Fast charging remains inactive?) then (yes)     :Shut down and end the process;     stop   else (no)   endif elseif (High-voltage shutdown request detected (value=2)?) then (yes)   :Wait 0.8 seconds;   :Enter state 175;   if (Fast charging is inactive afterward?) then (yes)     :Shut down and end;     stop   else (
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4815
- relation_f1: 0.3667
- missing_nodes:
  - presented with main window
  - open file menu
  - administrator user?
  - include (authenticate user)
  - click recall button
  - read previously saved changes from disk file/database
  - change configuration?
  - click save
- extra_nodes:
  - authenticated as administrator user?
  - authenticate user
  - click recall button to read previously saved changes
  - make desired changes to configuration
  - click save or close ?
  - request confirmation to save changes
  - confirms save?
  - request name for disk file
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - administrator user? -> include (authenticate user) [no]
  - administrator user? -> have appropriate privilege? [yes]
  - have appropriate privilege? -> click recall button [no]
  - read previously saved changes from disk file/database -> populate window with disk file data
  - change configuration? -> click save [yes]
  - request confirmation -> confirm?
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start :Select "Configure Diagnostics" menu item from "File" menu; if (Authenticated as administrator user?) then (No)   :Authenticate User; else (Yes) endif if (Has appropriate privilege?) then (Yes)   :Display configuration window;   :Click "Recall" button to read previously saved changes;   :Populate window with data from disk file;   :Make desired changes to configuration;   if (Click "Save" or "Close"?) then (Click "Save")     :Request confirmation to save changes;     if (Confirms save?) then (Yes)       :Request name for disk file;       if (Enters file name or cancels?) then (Enters file name)         :Save changes;         if (Save operation completes?) then (Yes)          

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
