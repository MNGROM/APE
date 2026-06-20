# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.5221
- node_recall: 0.5250
- node_f1: 0.5235
- relation_precision: 0.4376
- relation_recall: 0.4252
- relation_f1: 0.4313
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8185
- llm_node_recall: 0.8716
- llm_node_f1: 0.8309
- llm_relation_precision: 0.6609
- llm_relation_recall: 0.6673
- llm_relation_f1: 0.6526

## Failure Types
- missing_activity: 16
- missing_or_wrong_relation: 16
- extra_activity: 15
- extra_or_wrong_relation: 15
- wrong_parallel: 4

## Representative Failure Cases
### us-0077
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7273
- llm_relation_f1: 0.4000
- missing_nodes:
  - delete scheduled tasks/activities
  - keep schedule clean of unneeded activities
- extra_nodes:
  - select scheduled task/activity
  - choose deletion target
  - delete task
  - delete activity
  - update schedule
- missing_relations:
  - delete scheduled tasks/activities -> keep schedule clean of unneeded activities
- input_excerpt:
  As a camp administrator, I want to be able to delete tasks/activities I scheduled, so that I can keep the schedule clean of unneeded activities.
- generated_excerpt:
  @startuml start :Select scheduled task/activity; switch (Choose deletion target) case (Task) :Delete task; case (Activity) :Delete activity; endswitch :Update schedule; stop @enduml
### us-0186
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2857
- llm_relation_f1: 0.0000
- missing_nodes:
  - get all files that checksum has changed since last registered
- extra_nodes:
  - request files with changed checksums from preservation manager
  - retrieve all registered files
  - get current checksum
  - get last registered checksum
  - compare current checksum with last registered checksum
  - checksum changed since last registered?
  - include file in results
  - exclude file from results
- input_excerpt:
  As a DAMS manager, I want to know, via the preservation manager, of all files for which the checksum has changed since last registered.
- generated_excerpt:
  @startuml start :Request files with changed checksums from preservation manager; :Retrieve all registered files; fork   :Get current checksum; fork again   :Get last registered checksum; end fork :Compare current checksum with last registered checksum; if (Checksum changed since last registered?) then (Yes)   :Include file in results; else (No)   :Exclude file from results; endif :Present all files with changed checksums to DAMS manager; stop @enduml
### bp-0004
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1379
- relation_f1: 0.3448
- llm_element_status: success
- llm_node_f1: 0.9000
- llm_relation_f1: 1.0000
- missing_nodes:
  - open the toolbar on the right
  - choose choose source system
  - choose the menu option file
  - select source system with technical name pc_file
  - the hierarchical tree is displayed
  - open context menu
  - select create application component...
  - enter technical name and description
- extra_nodes:
  - you are in the modeling functional area of the data warehousing workbench
  - from the toolbar in the right screen area choose choose source system
  - in the menu option file select the source system with the technical name pc_file
  - a hierarchical tree of the data sources for this source system is displayed
  - the data sources are structured semantically by application component
  - select create application component... from the context menu at the root node of the data source tree
  - enter a technical name for the application component
  - enter a description for the application component
- missing_relations:
  - open the toolbar on the right -> choose choose source system
  - choose choose source system -> choose the menu option file
  - the hierarchical tree is displayed -> open context menu
  - open context menu -> select create application component...
  - select create application component... -> enter technical name and description
  - enter technical name and description -> open context menu
  - open context menu -> choose create data source
  - choose create data source -> click transfer
- input_excerpt:
  4.	Creating Transformations0 Creating Transformations for Master Data of Characteristic "Product"1. You are in the Modeling functional area of the Data Warehousing Workbench.2. Choose Data sources.3. From the toolbar in the right screen area, choose Choose Source System.4. In the menu option File, select the source system with the technical name PC_FILE. A hierarchical tree of the Data sources for this source system is displayed. The Data sources are structured semantically by application component. 5. Select Create application component... from the context menu at the root node of the Data source tree.6. On the next screen, enter a technical name and a description for the application compon
- generated_excerpt:
  @startuml start :You are in the Modeling functional area\nof the Data Warehousing Workbench; :Choose Data sources; :From the toolbar in the right screen area,\nchoose Choose Source System; :In the menu option File,\nselect the source system with the technical name PC_FILE; :A hierarchical tree of the Data sources\nfor this source system is displayed; :The Data sources are structured\nsemantically by application component; :Select Create application component...\nfrom the context menu at the root node\nof the Data source tree; fork :Enter a technical name for\nthe application component; fork again :Enter a description for\nthe application component; end fork :The application component is used
### bp-0005
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1905
- relation_f1: 0.1667
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.2857
- missing_nodes:
  - choose info objects
  - open characteristics info object catalog
  - open zd_pgroup context menu
  - select maintain master data
  - enter product group
  - enter short description
  - choose continue
  - more values?
- extra_nodes:
  - choose info objects in the modeling area of the data warehousing workbench
  - choose maintain master data from the context menu of the info object
  - enter product group and short description and choose continue
  - more values to enter?
  - save your entries and return to the info object tree
  - another characteristic to maintain?
- missing_relations:
  - choose info objects -> open characteristics info object catalog
  - open characteristics info object catalog -> open zd_pgroup context menu
  - open zd_pgroup context menu -> select maintain master data
  - select maintain master data -> choose execute
  - choose create -> enter product group [fork]
  - choose create -> enter short description [fork]
  - enter product group -> choose continue [merge]
  - enter short description -> choose continue [merge]
- input_excerpt:
  5.	Creating Master Data Directly in the System1. In the Modeling area of the Data Warehousing Workbench, choose Info Objects. 2. In the Info Object catalog for characteristics, choose Maintain master data from the context menu of your Info Object Product Group (ZD_PGROUP).3. Choose Execute.4. Choose Create.5. Enter DS10 as Product Group and Computer as the Short description and choose Continue.6. Repeat steps 4 and 5 with the following values:7. Save your entries and return to the Info Object tree.8. Repeat steps 2-7 for the characteristic Channel (ZD_CHAN) with the following values:
- generated_excerpt:
  @startuml start :Choose Info Objects\nin the Modeling area of\nthe Data Warehousing Workbench; repeat   :Choose Maintain master data\nfrom the context menu of\nthe Info Object;   :Choose Execute;   repeat     :Choose Create;     :Enter Product Group\nand Short description\nand choose Continue;   repeat while (More values to enter?) is (yes)   ->no;   :Save your entries\nand return to the Info Object tree; repeat while (Another characteristic to maintain?) is (yes) ->no; @enduml
### rac-0008
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.0588
- llm_element_status: success
- llm_node_f1: 0.2759
- llm_relation_f1: 0.1667
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - switch to state 127
  - slow charging is inactive and front mcu collateral shutdown request flag is 1
  - switch to state 128
  - shutdown
  - issue 2.2s timeout warning
  - enter shutdown state
  - slow charging is inactive and bms self-check counter is 1
- extra_nodes:
  - system starts up
  - high-voltage shutdown request flag?
  - 2
  - switch to state 115
  - condition after switching to state 115?
  - flag drops to 0 with cp duty cycle at 85
  - switch to state 126
  - bms self-check counter shows 1
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0 -> switch to state 127 [yes]
  - switch to state 127 -> slow charging is inactive and front mcu collateral shutdown request flag is 1
  - slow charging is inactive and front mcu collateral shutdown request flag is 1 -> switch to state 128 [yes]
  - switch to state 128 -> shutdown
  - slow charging is inactive and front mcu collateral shutdown request flag is 1 -> slow charging is inactive [no]
  - slow charging is inactive -> issue 2.2s timeout warning [yes]
  - issue 2.2s timeout warning -> switch to state 128
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?) then (yes)   :Enter power-up mode;   switch (High-voltage shutdown request flag?)   case (2)     :Switch to state 115;     switch (Condition after switching to state 115?)     case (Flag drops to 0 with CP duty cycle at 85%)       :Switch to state 126;     case (BMS self-check counter shows 1)       :Switch to state 130;     case (Slow charging becomes inactive)       :Shut down and end;       stop     endswitch   case (Central control charging/discharging command is 2 and vehicle isn't in charging/discharging mode)     :Switch to state 110;     if (High-voltage shutdown request flag becomes 2?) then (yes)       :Switch to stat
### lmc-0040
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.7692
- missing_nodes:
  - determinant of b(inv(wp )b > 1e-12
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - b(inv(wp )b matrix inversion be accurate to 12 digits precision
- extra_nodes:
  - check determinant of b(inv(wp ))b
  - determinant > 1e-12?
  - invert b(inv(wp ))b matrix
  - compute check output matrix
  - verify each element in check output matrix is within 1e-12 tolerance of 3x3 identity matrix
- missing_relations:
  - ridge_on set to false -> determinant of b(inv(wp )b > 1e-12
  - determinant of b(inv(wp )b > 1e-12 -> each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance -> b(inv(wp )b matrix inversion be accurate to 12 digits precision
- input_excerpt:
  2.	When the determinant of B(inv(Wp’)B’ is > 1e-12 as indicated by ridge_on set to False, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 12 digits precision in that each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  @startuml start :Check determinant of B(inv(Wp'))B'; if (Determinant > 1e-12?) then (Yes)   :Set ridge_on to False;   :Invert B(inv(Wp'))B' matrix;   :Compute check output matrix;   :Verify each element in check output matrix is within 1e-12 tolerance of 3x3 identity matrix; else (No) endif @enduml
### lmc-0056
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - =10?
  - allowed
  - not allowed
- extra_nodes:
  - is dcm321 equal to 1.0?
  - pass
  - fail
- missing_relations:
  - =10? -> allowed [yes]
  - =10? -> not allowed [no]
- input_excerpt:
  8.	The determinant of the Rotation Matrix, |DCM321|, shall be equal to 1.0.
- generated_excerpt:
  @startuml start :Calculate determinant of the Rotation Matrix |DCM321|; if (Is |DCM321| equal to 1.0?) then (yes)   :Pass; else (no)   :Fail; endif stop @enduml
### bp-0006
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2632
- relation_f1: 0.1463
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.7234
- missing_nodes:
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - attributes
  - texts
  - open data source context menu
- extra_nodes:
  - in the modeling area choose info provider
  - the attributes and texts are displayed with transformation and data source in your info area below the characteristic product
  - from the context menu of the data source choose create info package...
  - on the next screen enter a description for the info package
  - the info package maintenance screen for the scheduler appears
  - to check the load process choose monitor in the toolbar of the info package maintenance screen
  - on the next screen select the date
  - the monitor for the load process is displayed
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation [fork]
  - info area displays information -> data source [fork]
  - info area displays information -> attributes [fork]
  - info area displays information -> texts [fork]
  - transformation -> open data source context menu [merge]
- input_excerpt:
  6.	Loading Master Data forCharacteristic "Product"Go to the Data Warehousing Workbench;in the Modeling area choose Info Provider. The attributes and texts are displayed with transformation and Data source in your Info Area below the characteristic Product.3. Perform the following steps, rst for the attributes of the characteristic and then for the texts of the characteristic.4. From the context menu of the Data source, choose Create Info Package...5. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.6. Go to the tab page Schedule and choose Start.7. To check the load process, choose Monitor in the toolb
- generated_excerpt:
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose Info Provider; :The attributes and texts are displayed with transformation and Data source in your Info Area below the characteristic Product;  repeat   :From the context menu of the Data source, choose Create Info Package...;   :On the next screen, enter a description for the Info Package;   :Choose Save;   :The Info Package maintenance screen for the scheduler appears;   :Go to the tab page Schedule;   :Choose Start;   :To check the load process, choose Monitor in the toolbar of the Info Package maintenance screen;   :On the next screen, select the date;   :Choose Execute;   :The monitor for the load proces
### rac-0004
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4516
- relation_f1: 0.5238
- llm_element_status: success
- llm_node_f1: 0.9444
- llm_relation_f1: 0.7324
- missing_nodes:
  - slow charging state is 1 and charging/discharging power-up is ready
  - condition judgement
  - high-voltage shutdown charging/discharging value is 3 or 4
  - slow charging?
  - shutdown
  - high-voltage shutdown request is 3 and ignition switch is 2
  - ignition switch becomes 0
  - shut down
- extra_nodes:
  - system starts up
  - slow charging is active (state 1) and charging/discharging system is powered up?
  - high-voltage shutdown value is 3 or 4?
  - shut down and end the process
  - high-voltage shutdown request (value 3) occurs and ignition is on (position 2)?
  - return to state 105
  - shut down and end
  - ignition turns off (position 0)?
- missing_relations:
  - switch to state 95 -> vehicle charging/discharging mode is 2 and power-up is ready
  - switch to state 105 -> condition judgement
  - condition judgement -> high-voltage shutdown charging/discharging value is 3 or 4 [case 1]
  - condition judgement -> high-voltage shutdown request is 3 and ignition switch is 2 [case 2]
  - switch to state 105 -> ignition switch becomes 0
  - condition judgement -> pre-charge failure occurs [case 3]
  - condition judgement -> ac discharge system fault occurs [case 4]
  - condition judgement -> slow charging is inactive [case 5]
- input_excerpt:
  After the system starts up: - If slow charging is active (state 1) and the charging/discharging system is powered up, switch to state 95. - If the vehicle charging/discharging mode is 2 and the system is powered up, switch to state 105. Then, while in state 105:   1) If the high-voltage shutdown value is 3 or 4, switch to state 115. If slow charging becomes inactive during this, shut down and end the process.   2) If a high-voltage shutdown request (value 3) occurs while the ignition is on (position 2), return to state 105. If the ignition turns off (position 0), switch to state 115. If slow charging becomes inactive, shut down and end.   3) If a pre-charge failure happens, switch to state 1
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active (state 1)\nand charging/discharging system is powered up?) then (yes)   :Switch to state 95; else (no)   if (Vehicle charging/discharging mode is 2\nand system is powered up?) then (yes)     :Switch to state 105;     repeat       if (High-voltage shutdown value is 3 or 4?) then (yes)         :Switch to state 115;         if (Slow charging becomes inactive?) then (yes)           :Shut down and end the process;           stop         endif       elseif (High-voltage shutdown request (value 3) occurs\nand ignition is on (position 2)?) then (yes)         :Return to state 105;         if (Slow charging becomes inactive?) then (yes)   
### pure-0040
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5455
- relation_f1: 0.5455
- llm_element_status: success
- llm_node_f1: 0.9600
- llm_relation_f1: 0.9600
- missing_nodes:
  - see view inventory
  - display category type screen
  - unique item?
  - system validates data
  - system updates information
  - back to category screen
- extra_nodes:
  - category type
  - system validates the category data
  - system updates the category information
  - user is taken back to the category screen
- missing_relations:
  - see view inventory -> navigate to category
  - click edit category button -> display category type screen
  - unique item? -> display unique item screen [yes]
  - unique item? -> display stock item screen [no]
  - system validates data -> system updates information
  - system updates information -> back to category screen
- input_excerpt:
  2. Edit Category 2.1. User navigates to a Category (see View Inventory) 2.2. System displays the Edit Category button 2.3. User clicks the Edit Category button 2.4. System displays the appropriate screen for the Category type 2.4.1. Unique Item 2.4.2. Stock Item 2.5. User edits Category data 2.6. System validates the Category data 2.7. System updates the Category information 2.8. User is taken back to the Category screen
- generated_excerpt:
  @startuml start :Navigate to a Category; :System displays the Edit Category button; :User clicks the Edit Category button; switch (Category type) case (Unique Item)   :Display screen for Unique Item; case (Stock Item)   :Display screen for Stock Item; endswitch :User edits Category data; :System validates the Category data; :System updates the Category information; :User is taken back to the Category screen; @enduml
### bp-0012
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6111
- relation_f1: 0.1923
- llm_element_status: success
- llm_node_f1: 0.4500
- llm_relation_f1: 0.2121
- missing_nodes:
  - select rights
  - create a job?
  - set
  - edit a job?
  - promote a job?
  - delete a job?
  - use administration options?
  - use version management system?
- extra_nodes:
  - set create a job right
  - set edit a job right
  - set promote a job right
  - set delete a job right
  - set use administration options right
  - set use version management system right
- missing_relations:
  - view security tab is enabled -> select rights
  - select rights -> create a job? [fork]
  - select rights -> edit a job? [fork]
  - select rights -> promote a job? [fork]
  - select rights -> export a biar file? [fork]
  - select rights -> edit a biar file? [fork]
  - select rights -> delete a job? [fork]
  - select rights -> rollback a job? [fork]
- input_excerpt:
  12.	Set granular application rights to various functions within LifeCycleManager.1. Log into CMC and select Applications.2. Double-click LifeCycle Manager.3. Click User Security, and select Administrators.The View Security tab is enabled.4. Select the rights you want to set.You can set the following rights:• Create a job• Edit a job• Promote a job• Export a BIAR file• Edit a BIAR file• Delete a job• Rollback a job• Use Administration options• Edit Connections properties• Use Version Management System5. Click OK.
- generated_excerpt:
  @startuml start :Log into CMC; :Select Applications; :Double-click LifeCycle Manager; :Click User Security; :Select Administrators; :View Security tab is enabled; fork :Set Create a job right; fork again :Set Edit a job right; fork again :Set Promote a job right; fork again :Set Export a BIAR file right; fork again :Set Edit a BIAR file right; fork again :Set Delete a job right; fork again :Set Rollback a job right; fork again :Set Use Administration options right; fork again :Set Edit Connections properties right; fork again :Set Use Version Management System right; end fork :Click OK; @enduml
### pure-0028
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6154
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8750
- llm_relation_f1: 0.4000
- missing_nodes:
  - verify successful receipt
  - accumulation of error statistics
- extra_nodes:
  - verify successful receipt of incoming data from correlator
  - accumulate error statistics
  - out of tolerance conditions exist?
- missing_relations:
  - verify successful receipt -> check for receive errors [fork]
  - verify successful receipt -> determine all expected data was received [fork]
  - verify successful receipt -> accumulation of error statistics [fork]
  - verify successful receipt -> comparison against tolerances [fork]
  - verify successful receipt -> report out of tolerance conditions [fork]
  - check for receive errors -> verify successful receipt [merge]
  - determine all expected data was received -> verify successful receipt [merge]
  - accumulation of error statistics -> verify successful receipt [merge]
- input_excerpt:
  Verify Receive – The BE shall verify the successful receipt of incoming data from the Correlator. This includes checking for receive errors and determining that all expected data was received, accumulation of error statistics and comparison against tolerances, and reporting of all out of tolerance conditions.
- generated_excerpt:
  @startuml start :Verify successful receipt of incoming data from Correlator; :Check for receive errors; :Determine that all expected data was received; fork   :Accumulate error statistics; fork again   :Compare against tolerances; end fork if (Out of tolerance conditions exist?) then (yes)   :Report all out of tolerance conditions; else (no) endif stop @enduml
### rac-0017
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6154
- relation_f1: 0.5455
- llm_element_status: success
- llm_node_f1: 0.8966
- llm_relation_f1: 0.8824
- missing_nodes:
  - shutdown
  - after 10s
- extra_nodes:
  - system starts up
  - trigger condition?
  - transition to state 126
  - shut down and exit
  - move to state 126
  - slow charging deactivates
  - wait through 10-second timeout
  - shift to state 126
- missing_relations:
  - enter state 82 -> bms counter=1 and battery pre-heating demand=3
  - bms counter=1 and battery pre-heating demand=3 -> pre-charge failure occurs [no]
  - pre-charge failure occurs -> slow charging is inactive [no]
  - slow charging is inactive -> ac charging/discharging system fault [no]
  - ac charging/discharging system fault -> after 10s [yes]
  - after 10s -> switch to state 126
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU initialization is 0, it enters state 82. From there: - When the BMS counter reaches 1 with a battery pre-heating demand of 3, the system transitions to state 126. If slow charging becomes inactive afterward, it shuts down and exits. - If a pre-charge failure occurs, the system moves to state 126. Should slow charging be inactive at that point, it shuts down and exits. - If slow charging deactivates, the system switches to state 126 before shutting down and exiting. - For AC charging/discharging system faults, the system waits through a 10-second timeout before shifting to state 126. If slow charging is inactive followin
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?\nand Front MCU initialization is 0?) then (yes)   :Enter state 82;   switch (Trigger condition?)   case (BMS counter reaches 1\nwith battery pre-heating demand of 3)     :Transition to state 126;     if (Slow charging becomes inactive?) then (yes)       :Shut down and exit;       stop     else (no)     endif   case (Pre-charge failure occurs)     :Move to state 126;     if (Slow charging is inactive?) then (yes)       :Shut down and exit;       stop     else (no)     endif   case (Slow charging deactivates)     :Switch to state 126;     :Shut down and exit;     stop   case (AC charging/discharging system fault)     :Wait through
### lmc-0044
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7273
- relation_f1: 0.7273
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.6667
- missing_nodes:
  - in cockpit
- extra_nodes:
  - select autopilot engage switch in cockpit
  - command roll actuator
- missing_relations:
  - roll autopilot engage -> autopilot engage switch [merge]
  - command to roll actuator be zero -> autopilot engage switch [merge]
- input_excerpt:
  Roll Autopilot shall engage when the pilot selects the autopilot engage switch in the cockpit and disengage when the switch is deselected. When not engaged, the command to the roll actuator shall be zero.
- generated_excerpt:
  @startuml start :Select autopilot engage switch in cockpit; if (Autopilot engage switch selected?) then (yes)   :Engage Roll Autopilot;   :Command roll actuator; else (no)   :Disengage Roll Autopilot;   :Set command to roll actuator to zero; endif stop @enduml
### lmc-0030
- dataset: lmc
- failure_types: missing_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7500
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 0.8333
- llm_relation_f1: 0.1667
- missing_nodes:
  - in nlguidance
  - compute the vector
- missing_relations:
  - in nlguidance -> vector define location at standoff 2 with offset from target position?
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? -> it is inertial position vector for aim point 2 [yes]
  - it is inertial position vector for aim point 2 -> compute the vector
- input_excerpt:
  3.	NLGuidance shall compute the inertial position vector for aim point 2, defining the location at Standoff 2 with an offset from the target position, and oriented on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point.
- generated_excerpt:
  @startuml start :Compute inertial position vector for aim point 2; :Define the location at Standoff 2 with an offset from the target position; :Orient on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point; stop @enduml
### rac-0002
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7619
- relation_f1: 0.6087
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.6875
- missing_nodes:
  - gear is s
  - gear check
- extra_nodes:
  - check the gear position
  - gear in s?
  - calculate d_s gear mileage parameter as s gear nominal mileage divided by d gear nominal mileage
- missing_relations:
  - switch to driving mode -> gear check
  - gear check -> gear is d or e [case gear is d or e]
  - gear check -> gear is n or r [case gear is n or r]
- input_excerpt:
  After the system starts up, the process begins by checking the gear position. If the gear is in D or N, the D_S gear mileage parameter is set to 1, and the sequence ends. If the gear is in S, the D_S gear mileage parameter is calculated as S gear nominal mileage divided by D gear nominal mileage, then the process concludes. Additionally, if the vehicle status is 30, switch to driving mode. Next, if the gear is in D or E, set the D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage, and end. Finally, if the gear is in N or R, observe using the D_S gear mileage parameter and terminate the process.
- generated_excerpt:
  @startuml start :Check the gear position; if (Gear in D or N?) then (yes)   :Set D_S gear mileage parameter to 1; else (no)   if (Gear in S?) then (yes)     :Calculate D_S gear mileage parameter as S gear nominal mileage divided by D gear nominal mileage;   endif endif if (Vehicle status is 30?) then (yes)   :Switch to driving mode; endif if (Gear in D or E?) then (yes)   :Set D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage; else (no)   if (Gear in N or R?) then (yes)     :Observe using the D_S gear mileage parameter;   endif endif @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
