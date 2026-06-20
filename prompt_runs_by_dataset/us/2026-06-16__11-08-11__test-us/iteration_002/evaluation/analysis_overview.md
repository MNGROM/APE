# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3841
- node_recall: 0.3638
- node_f1: 0.3737
- relation_precision: 0.3099
- relation_recall: 0.3031
- relation_f1: 0.3065
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
- wrong_parallel: 4
- wrong_loop: 1

## Representative Failure Cases
### lmc-0036
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.2222
- missing_nodes:
  - input any value
  - minimum value of nn output z >= -0.2?
  - allowed
  - not allowed
- extra_nodes:
  - receive input values
  - compute nn output z
  - z >= -0.2 ?
  - accept output z
  - clamp/adjust output z to -0.2
  - return final output z
- missing_relations:
  - minimum value of nn output z >= -0.2? -> allowed [yes]
  - minimum value of nn output z >= -0.2? -> not allowed [no]
- input_excerpt:
  2.	The minimum value of the NN output, z, shall always be greater than or equal to -0.2, regardless of the input values.
- generated_excerpt:
  @startuml start :Receive input values; :Compute NN output z; if (z >= -0.2 ?) then (Yes)   :Accept output z; else (No)   :Clamp/Adjust output z to -0.2; endif :Return final output z; stop @enduml
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2105
- relation_f1: 0.1837
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - go to promotion jobs home page
  - select the job want to promote
  - right-click
  - open source and destination systems drop-down lists
  - select source and destination systems
  - have logged into both source and destination systems
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - in the promotion jobs home page select the job to promote (alternatively right-click the home page screen and click promote)
  - select source and destination systems from drop-down lists
  - enter appropriate value in external change management id field
  - click edit mappings to create and validate mappings
  - default option selected
  - promote job along with inherited application rights
  - optionally click view security to view security dependencies
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
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, select the job to promote\n(Alternatively, right-click the home page screen and click Promote); :Select source and destination systems from drop-down lists; note right: Ensure that you have logged into\nboth the source and destination\nsystems before proceeding. :Enter appropriate value in External Change Management ID field; :Click Save; :Click Mappings; :Click Edit Mappings to create and validate mappings; :Click Security Settings (if required); if (Security Settings?) then (Do not Promote Security)   :Default option selected; elseif (Promote Security?) then (Promote Security)   :Promote 
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
  - requirement satisfied
  - requirement violated
- missing_relations:
  - < 0.01? -> allowed [yes]
  - < 0.01? -> not allowed [no]
- input_excerpt:
  4.	The 2-norm of the output Buminusd should be less than 0.01.
- generated_excerpt:
  @startuml start :Compute 2-norm of Buminusd; if (2-norm of Buminusd < 0.01?) then (Yes)   :Requirement satisfied; else (No)   :Requirement violated; endif stop @enduml
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2745
- relation_f1: 0.1455
- missing_nodes:
  - go to data warehousing workbench
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - open data source context menu
  - choose create info package...
- extra_nodes:
  - go to the data warehousing workbench in the modeling area choose info provider
  - view the transformation and the data source in the info area below the info cube sales overview
  - in the context menu of the data source choose create info package...
  - enter a description for the info package and choose save
  - go to the tab page schedule and choose start
  - to check the load process choose monitor in the toolbar of info package maintenance
  - select the date and choose execute
  - monitor for the load process is displayed
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
  @startuml start :Go to the Data Warehousing Workbench;\nIn the Modeling area choose Info Provider; :View the transformation and the Data source\nin the Info Area below the Info Cube Sales Overview; :In the context menu of the Data source,\nchoose Create Info Package...; :Enter a description for the Info Package\nand choose Save; :Info Package maintenance screen\nfor the scheduler appears; :Go to the tab page Schedule\nand choose Start; :To check the load process,\nchoose Monitor in the toolbar of Info Package maintenance; :Select the date and choose Execute; :Monitor for the load process is displayed; :Select the load process for your Data source\nfrom the tree at the left of the screen; :Ex
### fsd-0102
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3636
- relation_f1: 0.2264
- missing_nodes:
  - thermal management controller executes as state machine on rtos
  - govern pwm fans
  - govern liquid-cooling pumps
  - high-priority task concurrently activates temperature adjustment module
  - temperature continues to rise?
  - execute rapid cooling subroutine in controlled loop with exponential backoff
  - temperature re-enters safe range?
  - disable fan
- extra_nodes:
  - rtos state machine execution
  - activate temperature adjustment module
  - enable fan cooling (pwm)
  - monitor temperature rise
  - temperature in safe range?
  - halt temperature adjustment module
  - wait for humidity alert
  - wait for humidity normalization
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern pwm fans [fork]
  - thermal management controller executes as state machine on rtos -> govern liquid-cooling pumps [fork]
  - govern pwm fans -> ambient temperature threshold breach?
  - govern liquid-cooling pumps -> ambient temperature threshold breach?
  - ambient temperature threshold breach? -> high-priority task concurrently activates temperature adjustment module [yes]
  - high-priority task concurrently activates temperature adjustment module -> enable fan cooling
  - enable fan cooling -> temperature continues to rise?
  - temperature continues to rise? -> execute rapid cooling subroutine in controlled loop with exponential backoff [yes]
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing PWM fans and liquid-cooling pumps. Upon an ambient temperature threshold breach, a high-priority task concurrently activates the temperature adjustment module and enables fan cooling. If the temperature continues to rise, a rapid cooling subroutine executes in a controlled loop with exponential backoff until the temperature re-enters the safe range, at which point the fan is disabled and the adjustment module is halted. Concurrently, a separate high-priority task, triggered by a humidity alert, initializes a humidity monitor and activates the dehumidifier; both are stopped once humidity normalizes. Throughou
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #F9F9F9 skinparam PartitionBackgroundColor #EEFFFF  title Thermal Management Controller State Machine  start  :RTOS State Machine Execution;  partition "Temperature Management (High-Priority Task)" {     :Wait for Ambient Temperature Threshold Breach;          fork         :Activate Temperature Adjustment Module;     fork again         :Enable Fan Cooling (PWM);     end fork          :Monitor Temperature Rise;          repeat :Execute Rapid Cooling Subroutine;         note right: Controlled loop with\nexponential backoff     repeat while (Temperature in safe range?) is (No)     -> Yes;          :Disable Fan Cooling;     :Halt Temperature Adjustment
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4375
- relation_f1: 0.2791
- missing_nodes:
  - switch to state 153
  - condition judgement
  - shutdown
  - wait 0.8s
  - high-voltage shutdown request charging/discharging =2
- extra_nodes:
  - system starts up
  - enter state 153
  - pre-charge failure occurs?
  - move to state 175
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
  @startuml start :System starts up;  if (charging=1 && front MCU high-voltage detection flag=0) then (yes)   :Enter state 153;   stop elseif (BMS-fast charger handshake flag=0 && front MCU high-voltage flag=0) then (yes)   :Enter state 155; else (no)   stop endif  repeat   if (pre-charge failure occurs?) then (yes)     :Move to state 175;     if (fast charging inactive?) then (yes)       :Shut down;       stop     endif   elseif (high-voltage shutdown request detected (value=2)?) then (yes)     :Wait 0.8 seconds;     :Enter state 175;     if (fast charging inactive?) then (yes)       :Shut down;       stop     endif   elseif (ignition switch status=2?) then (yes)     :Remain in state 155;    
### pure-0058
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4444
- relation_f1: 0.3448
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
  @startuml start :User opens KeePass and select Open->Database; :User navigates through his folders;  if (User chooses cancel?) then (yes)   :Exit from KeePass;   stop else (no)   :User selects a database;   if (Folder type suitable for database?) then (no)     :A message "file not found" appears;     :User selects another folder;   else (yes)   endif endif  :User types Master Password;  if (Master Password is correct?) then (no)   :A message "invalid/wrong key" appears;   :User types another master key; else (yes) endif  :The main database window opens; stop @enduml
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4828
- relation_f1: 0.2535
- missing_nodes:
  - presented with main window
  - open file menu
  - administrator user?
  - include (authenticate user)
  - change configuration?
  - click save
  - request confirmation
  - confirm?
- extra_nodes:
  - authenticated as administrator?
  - authenticate user
  - make desired changes to configuration
  - click which button?
  - request confirmation to save changes
  - user confirms?
  - request name for disk file
  - user enters name or cancels?
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
  @startuml start :Select "Configure Diagnostics" from "File" menu; if (Authenticated as administrator?) then (No)   :Authenticate User; else (Yes) endif if (Has appropriate privilege?) then (Yes)   :Display configuration window;      fork     :Click "Recall" button;     :Read previously saved changes from disk file/database;     :Populate window with data from disk file;   fork again     repeat       :Make desired changes to configuration;              if (Click which button?) then ("Save")         :Request confirmation to save changes;         if (User confirms?) then (Yes)           :Request name for disk file;           if (User enters name or cancels?) then (Enters name)             :Save

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
