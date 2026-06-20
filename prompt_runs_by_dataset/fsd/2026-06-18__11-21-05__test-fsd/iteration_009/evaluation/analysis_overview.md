# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4968
- node_recall: 0.4539
- node_f1: 0.4744
- relation_precision: 0.4352
- relation_recall: 0.3825
- relation_f1: 0.4072
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8744
- llm_node_recall: 0.8045
- llm_node_f1: 0.8244
- llm_relation_precision: 0.6756
- llm_relation_recall: 0.5651
- llm_relation_f1: 0.5978

## Failure Types
- missing_or_wrong_relation: 18
- extra_or_wrong_relation: 18
- missing_activity: 16
- extra_activity: 16
- wrong_parallel: 5

## Representative Failure Cases
### bp-0017
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - go to administration options window
  - click vms settings
  - open version management systems drop-down list
  - select clearcase
  - enter details
  - clearcase map drive
  - enter mvfs s folder name
  - vob tag name
- extra_nodes:
  - in the administration options window click vms settings
  - from the version management systems drop-down list select clearcase
  - enter the clearcase map drive - enter the name of the folder where the mvfs is located
  - enter the vob tag name - enter the vob name and the folder where the vob is located
  - enter the view storage directory - enter the path of the directory where the views are created
- missing_relations:
  - go to administration options window -> click vms settings
  - click vms settings -> open version management systems drop-down list
  - open version management systems drop-down list -> select clearcase
  - select clearcase -> enter details
  - enter details -> clearcase map drive [fork]
  - enter details -> vob tag name [fork]
  - enter details -> view storage directory [fork]
  - clearcase map drive -> enter mvfs s folder name
- input_excerpt:
  17.	set the ClearCase version management system in Unix1. In the Administration Options window, click VMS Settings.2. From the Version Management Systems drop-down list, select ClearCase.3. Enter the following details:• ClearCase Map Drive - Enter the name of the folder where the MVFSis located. By default, it is /view• VOB Tag Name - Enter the VOB name and the folder where the VOBis located. For example: VobFolder/VobName• View Storage Directory: Enter the path of the directory where the viewsare created.
- generated_excerpt:
  @startuml start partition Unix {     :In the Administration Options window, click VMS Settings;     :From the Version Management Systems drop-down list, select ClearCase;     :Enter the ClearCase Map Drive - Enter the name of the folder where the MVFS is located;     :Enter the VOB Tag Name - Enter the VOB name and the folder where the VOB is located;     :Enter the View Storage Directory - Enter the path of the directory where the views are created; } @enduml
### lmc-0041
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.5000
- missing_nodes:
  - output u vector
  - 5x1 vector?
  - allowed
  - not allowed
- extra_nodes:
  - create output u vector as a 5x1 vector
- missing_relations:
  - output u vector -> 5x1 vector?
  - 5x1 vector? -> allowed [yes]
  - 5x1 vector? -> not allowed [no]
- input_excerpt:
  3.	The output u vector should be a 5x1 vector.
- generated_excerpt:
  @startuml start :Create output u vector as a 5x1 vector; stop @enduml
### us-0214
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5000
- llm_relation_f1: 0.0000
- missing_nodes:
  - educate volunteer with text an image or a video
- extra_nodes:
  - know whether to educate a volunteer with text
  - know whether to educate a volunteer with an image
  - know whether to educate a volunteer with a video
- input_excerpt:
  As a Zooniverse admin, I want to know whether I should educate a volunteer with text, an image, or a video.
- generated_excerpt:
  @startuml start partition "Zooniverse admin" {     :Know whether to educate a volunteer with text;     :Know whether to educate a volunteer with an image;     :Know whether to educate a volunteer with a video; } stop @enduml
### us-0116
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.4444
- missing_nodes:
  - deploy new version of app
  - it includes older version of dataset type?
  - dataset instances use type code
- extra_nodes:
  - deploy a new version of an app that includes an older version of a dataset type deployed by another app
  - create dataset instances by this app
  - use the dataset type code included in this app for the dataset instances
- missing_relations:
  - it includes older version of dataset type? -> dataset instances use type code [yes]
- input_excerpt:
  As an app developer, I want to ensure that when I deploy a new version of an app that includes an older version of a dataset type deployed by another app and I expect that the dataset instances created by this app use the dataset type code included in this app.
- generated_excerpt:
  @startuml start partition "App Developer" {     :Deploy a new version of an app that includes an older version of a dataset type deployed by another app; } partition "System" {     :Create dataset instances by this app;     :Use the dataset type code included in this app for the dataset instances; } @enduml
### bp-0009
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1111
- relation_f1: 0.2500
- llm_element_status: success
- llm_node_f1: 0.8696
- llm_relation_f1: 0.8000
- missing_nodes:
  - choose start programs business explorer web application designer
  - bex web is started
  - log in
  - initial screen is shown
  - click create new blank web template
  - choose new data provider
  - open data provider type dialog box
  - select query
- extra_nodes:
  - start the bex web application by choosing start programs business explorer web application designer
  - log onto the bi system
  - in the initial screen of the web application designer click on the link create new blank web template
  - in the lower part of the layout view choose new data provider
  - in the dialog box for the data provider type select query and enter the name of the query zd_sales_2007 in the field following query
  - the data provider is displayed in the lower part of the layout view in the web application designer
- missing_relations:
  - bex web is started -> log in
  - log in -> initial screen is shown
  - initial screen is shown -> click create new blank web template
  - choose new data provider -> open data provider type dialog box
  - open data provider type dialog box -> select query
  - select query -> enter zd_sales_2007 as query name
  - enter zd_sales_2007 as query name -> choose ok
  - choose ok -> data provider is displayed
- input_excerpt:
  9.	Creating Web Applications1. Start the BEx Web application by choosing Start Programs Business Explorer Web Application Designer.2. Log onto the BI system.3. In the initial screen of the Web Application Designer, click on the link Create New Blank Web Template.4. In the lower part of the layout view choose New Data Provider.5. In the dialog box for the data provider type select Query and enter the name of the query ZD_SALES_2007 in the eld following Query.6. Choose OK.7. The data provider is displayed in the lower part of the layout view in the Web Application Designer
- generated_excerpt:
  @startuml start :Start the BEx Web application by choosing Start Programs Business Explorer Web Application Designer; :Log onto the BI system; :In the initial screen of the Web Application Designer, click on the link Create New Blank Web Template; :In the lower part of the layout view choose New Data Provider; :In the dialog box for the data provider type select Query and enter the name of the query ZD_SALES_2007 in the field following Query; :Choose OK; :The data provider is displayed in the lower part of the layout view in the Web Application Designer; stop @enduml
### pure-0021
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1739
- relation_f1: 0.0645
- llm_element_status: success
- llm_node_f1: 0.7742
- llm_relation_f1: 0.5641
- missing_nodes:
  - transfer to shunting on driver s selection?
  - from stand by/full supervision/partial supervision operation
  - manually select shunting
  - not allowed
  - automatic transfer?
  - speed <= supervised speed?
  - from full supervision/partial supervision operation
  - etcs requests driver confirmation
- extra_nodes:
  - select shunting from stand by operation full supervision operation or partial supervision operation
  - transfer to shunting
  - evaluate automatic transfer to shunting from full supervision operation or partial supervision operation
  - speed lower than or equal to the supervised shunting speed based on trackside information?
  - request confirmation from the driver
  - confirm automatic transition to shunting?
  - automatic transition to shunting
  - select exit from shunting
- missing_relations:
  - transfer to shunting on driver s selection? -> stationary? [yes]
  - stationary? -> from stand by/full supervision/partial supervision operation [yes]
  - from stand by/full supervision/partial supervision operation -> manually select shunting
  - stationary? -> not allowed [no]
  - transfer to shunting on driver s selection? -> automatic transfer? [no]
  - manually select shunting -> automatic transfer?
  - not allowed -> automatic transfer?
  - automatic transfer? -> speed <= supervised speed? [yes]
- input_excerpt:
  Transfer to Shunting on driver's selection shall only be possible when stationary. It shall be possible to manually select Shunting from Stand By operation, Full Supervision operation, or Partial Supervision operation. Automatic transfer to Shunting may be from Full Supervision operation and Partial Supervision operation status at any speed lower than or equal to the supervised shunting speed based on trackside information. Before automatic transition to Shunting, ETCS shall request confirmation from the driver. Exit from Shunting shall only be possible when the train is stationary. Exit from Shunting shall take place when the driver selects exit from shunting.
- generated_excerpt:
  @startuml start partition Driver {     :Select Shunting from Stand By operation, Full Supervision operation, or Partial Supervision operation;     if (Stationary?) then (yes)         :Transfer to Shunting;     else (no)     endif } partition ETCS {     :Evaluate automatic transfer to Shunting from Full Supervision operation or Partial Supervision operation;     if (Speed lower than or equal to the supervised shunting speed based on trackside information?) then (yes)         :Request confirmation from the driver;     else (no)     endif } partition Driver {     if (Confirm automatic transition to Shunting?) then (yes)         :Automatic transition to Shunting;     else (no)     endif     if (
### bp-0030
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.2353
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.3590
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
  - log into the lifecycle manager tool.
  - in the promotion jobs home page click new job
  - enter the name description and keywords for the job in the appropriate fields
  - in the save job in field browse and select the folder in which you want to save the job
  - select the source system and the destination system from the drop-down lists
  - is the name of the system not displayed in the drop-down list?
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
  @startuml start :Log into the LifeCycle Manager tool.; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name, description, and keywords for the job in the appropriate fields; :In the Save Job in field, browse and select the folder in which you want to save the job; :Select the source system and the destination system from the drop-down lists; if (Is the name of the system not displayed in the drop-down list?) then (yes)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the name of the system along with the user name and password; else (no) endif :Click Create; stop @enduml
### bp-0002
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2778
- relation_f1: 0.1538
- llm_element_status: success
- llm_node_f1: 0.7143
- llm_relation_f1: 0.7273
- missing_nodes:
  - user authorizations are sufficient?
  - log in
  - choose modeling data warehousing workbench modeling
  - data warehousing workbench is started
  - choose info objects
  - open root node context menu
  - choose create info area
  - enter a technical name
- extra_nodes:
  - log onto the bi system with a user that has sufficient authorizations for executing the scenario
  - start the data warehousing workbench in the sap menu by choosing modeling data warehousing workbench modeling
  - under modeling choose info objects
  - from the context menu at the root node info objects of the info object tree choose create info area
  - on the next screen enter a technical name and a description for the info area
  - the info area is displayed in the info object tree
  - it is used to group your info objects
  - on the next screen enter a technical name and description and select key figure as the info object type
- missing_relations:
  - user authorizations are sufficient? -> log in [yes]
  - log in -> choose modeling data warehousing workbench modeling
  - choose modeling data warehousing workbench modeling -> data warehousing workbench is started
  - data warehousing workbench is started -> choose info objects
  - info object tree is displayed -> open root node context menu
  - open root node context menu -> choose create info area
  - choose create info area -> enter a technical name [fork]
  - choose create info area -> enter a description [fork]
- input_excerpt:
  2.	Log onto the BI system1.	Log onto the BI system with a user that has sufficient authorizations for executing the scenario.2.	Start the Data Warehousing Workbench in the SAP menu by choosing Modeling Data Warehousing Workbench: Modeling.3.	Under Modeling, choose Info  Objects. The Info  Object tree is displayed.4.	From the context menu at the root node Info Objects of the Info Object tree, choose Create Info Area.5.	On the next screen, enter a technical name and a description for the Info Area. The Info Area is displayed in the Info Object tree.6.	It is used to group your Info Objects.7.	In the context menu of the Info Area, choose Create Info Object Catalog.8.	On the next screen, enter a 
- generated_excerpt:
  @startuml start partition "User" {   :Log onto the BI system with a user that has sufficient authorizations for executing the scenario;   :Start the Data Warehousing Workbench in the SAP menu by choosing Modeling Data Warehousing Workbench: Modeling;   :Under Modeling, choose Info Objects; } partition "BI System" {   :The Info Object tree is displayed; } partition "User" {   :From the context menu at the root node Info Objects of the Info Object tree, choose Create Info Area;   :On the next screen, enter a technical name and a description for the Info Area; } partition "BI System" {   :The Info Area is displayed in the Info Object tree;   :It is used to group your Info Objects; } partition "
### lmc-0016
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.8000
- missing_nodes:
  - limits are not exceeded (not limits)?
  - sensor change states from fault to transition
- extra_nodes:
  - change state from fault to transition
- missing_relations:
  - autopilot is not requesting support (not request)? -> limits are not exceeded (not limits)? [yes]
  - limits are not exceeded (not limits)? -> sensor change states from fault to transition [yes]
- input_excerpt:
  12.	The sensor shall change states from FAULT to TRANSITION when the autopilot is not requesting support (not request) and limits are not exceeded (not limits).
- generated_excerpt:
  @startuml start if (Autopilot is not requesting support and limits are not exceeded?) then (yes)   :Change state from FAULT to TRANSITION; endif stop @enduml
### rac-0004
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5333
- relation_f1: 0.4878
- llm_element_status: success
- llm_node_f1: 0.8235
- llm_relation_f1: 0.5217
- missing_nodes:
  - slow charging state is 1 and charging/discharging power-up is ready
  - condition judgement
  - high-voltage shutdown charging/discharging value is 3 or 4
  - slow charging?
  - shutdown
  - high-voltage shutdown request is 3 and ignition switch is 2
  - ignition switch becomes 0
- extra_nodes:
  - system starts up
  - slow charging is active (state 1) and charging/discharging system is powered up?
  - in state 105?
  - high-voltage shutdown value is 3 or 4?
  - high-voltage shutdown request (value 3) occurs and ignition is on (position 2)?
  - return to state 105
  - ignition turns off (position 0)?
- missing_relations:
  - switch to state 95 -> vehicle charging/discharging mode is 2 and power-up is ready
  - switch to state 105 -> condition judgement
  - condition judgement -> high-voltage shutdown charging/discharging value is 3 or 4 [case 1]
  - slow charging? -> shutdown [no]
  - condition judgement -> high-voltage shutdown request is 3 and ignition switch is 2 [case 2]
  - switch to state 105 -> ignition switch becomes 0
  - condition judgement -> pre-charge failure occurs [case 3]
  - condition judgement -> ac discharge system fault occurs [case 4]
- input_excerpt:
  After the system starts up: - If slow charging is active (state 1) and the charging/discharging system is powered up, switch to state 95. - If the vehicle charging/discharging mode is 2 and the system is powered up, switch to state 105. Then, while in state 105:   1) If the high-voltage shutdown value is 3 or 4, switch to state 115. If slow charging becomes inactive during this, shut down and end the process.   2) If a high-voltage shutdown request (value 3) occurs while the ignition is on (position 2), return to state 105. If the ignition turns off (position 0), switch to state 115. If slow charging becomes inactive, shut down and end.   3) If a pre-charge failure happens, switch to state 1
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active (state 1) and charging/discharging system is powered up?) then (yes)   :Switch to state 95; elseif (Vehicle charging/discharging mode is 2 and system is powered up?) then (yes)   :Switch to state 105;   while (In state 105?) is (yes)     if (High-voltage shutdown value is 3 or 4?) then (yes)       :Switch to state 115;       if (Slow charging becomes inactive?) then (yes)         :Shut down;         stop       else (no)       endif     elseif (High-voltage shutdown request (value 3) occurs and ignition is on (position 2)?) then (yes)       :Return to state 105;     elseif (Ignition turns off (position 0)?) then (yes)       :Switc
### pure-0095
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5455
- relation_f1: 0.6000
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.1333
- missing_nodes:
  - refer to provided configuration
  - specify how fields are translated into warc records
  - handle missing fields
- extra_nodes:
  - ensure the configuration file specifies how fields are translated into warc records
  - missing fields?
- missing_relations:
  - refer to provided configuration -> specify how fields are translated into warc records [fork]
  - refer to provided configuration -> generate errors requiring operator intervention [fork]
  - handle missing fields -> migrate content from arc files to warc files [merge]
- input_excerpt:
  Migration Tool Execution: Use the command arc_warc_migrate <ARC_FILES> <CONFIG> [options] to migrate content from ARC files to WARC files based on the provided configuration. Ensure the configuration file specifies how fields are translated into WARC records, and handle missing fields by generating errors requiring operator intervention.
- generated_excerpt:
  @startuml start partition MigrationTool {     :Use the command arc_warc_migrate <ARC_FILES> <CONFIG> [options];     :Migrate content from ARC files to WARC files based on the provided configuration;     :Ensure the configuration file specifies how fields are translated into WARC records;     if (Missing fields?) then (yes)         :Generate errors requiring operator intervention;     else (no)     endif } stop @enduml
### pure-0046
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8421
- llm_relation_f1: 0.6809
- missing_nodes:
  - display edit details screen
  - all existing item details
  - detail x department assignments
  - detail x category assignments
  - filter view?
  - detail status
  - active status
  - inactive status
- extra_nodes:
  - display the edit details screen which displays all existing item details and their detail x department and category assignments
  - optionally filter view by detail status (active inactive all)
  - change detail data
  - update the item detail information
- missing_relations:
  - click edit details button -> display edit details screen
  - display edit details screen -> all existing item details [fork]
  - display edit details screen -> detail x department assignments [fork]
  - display edit details screen -> detail x category assignments [fork]
  - all existing item details -> filter view? [merge]
  - detail x department assignments -> filter view? [merge]
  - detail x category assignments -> filter view? [merge]
  - filter view? -> detail status [yes]
- input_excerpt:
  4. Edit Item Details 4.1. User accesses the main inventory screen 4.2. System displays the Edit Details button 4.3. User clicks the Edit Details button 4.4. System displays the Edit Details screen which displays all existing item details and their detail x department and category assignments 4.5. Optionally, user filters view by detail status (active, inactive, all) 4.6. User edits details 4.6.1. User changes detail x department or category assignments 4.6.2. User changes detail data 4.6.3. User changes detail active x inactive status 4.6.4. User creates new detail 4.6.5. System validates the detail data 4.6.6. System updates the Item detail information 4.7. User clicks the Done button 4.8. 
- generated_excerpt:
  @startuml start partition User {     :Access the main inventory screen; } partition System {     :Display the Edit Details button; } partition User {     :Click the Edit Details button; } partition System {     :Display the Edit Details screen which displays all existing item details and their detail x department and category assignments; } partition User {     :Optionally, filter view by detail status (active, inactive, all);     :Edit details; } fork     :Change detail x department or category assignments; fork again     :Change detail data; fork again     :Change detail active x inactive status; fork again     :Create new detail; end fork partition System {     :Validate the detail data; 
### rac-0001
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6512
- relation_f1: 0.7407
- llm_element_status: success
- llm_node_f1: 0.9804
- llm_relation_f1: 0.9706
- missing_nodes:
  - initial judgement
  - (vehicle status > 9 and 30 and <= 49)
  - vehicle status == 28 or 29 or 30
  - switch to new state
  - query cumulative discharge distance
  - set instantaneous driving mileage gradient = cumulative discharge distance * driving error correction coefficient /2
  - switch to another state
- extra_nodes:
  - check the vehicle s status value
  - status > 9 and 30 and <= 49?
  - transition to a new state
  - transition to another state
  - move to a new state
  - use call() to get the cumulative discharge distance
  - calculate the gradient as (cumulative discharge distance driving error correction coefficient 2)
  - enter another state
- missing_relations:
  - initial judgement -> (vehicle status > 9 and 30 and <= 49) [case (vehicle status > 9 and 30 and <= 49)]
  - initial judgement -> vehicle status == 28 or 29 or 30 [case (vehicle status == 28 or 29 or 30)]
  - vehicle status == 28 or 29 or 30 -> switch to new state
  - vehicle speed > speed threshold (kph) -> switch to new state [yes]
  - query cumulative discharge distance -> cumulative discharge distance >0.1?
  - switch to new state -> set instantaneous driving mileage gradient = cumulative discharge distance * driving error correction coefficient /2
  - vehicle speed < speed threshold (kph) -> vehicle speed > speed threshold (kph) [no]
  - instantaneous discharge mileage > instantaneous driving mileage? -> switch to another state [no]
- input_excerpt:
  Once the system starts up, it checks the vehicle's status value first.  If the status is greater than 9 but less than 28, or greater than 30 but 49 or less, the system sets the instantaneous driving mileage gradient to 0 and ends.  For a status of 28, 29, or 30, the system transitions to a new state and sets the instantaneous driving mileage to 10. After this state change, it performs additional checks:  *   If the current stays between -Current Threshold A and Current Threshold A, the system sets the instantaneous driving mileage gradient to 0 and ends. *   If the vehicle speed exceeds the speed threshold (kph), the system enters a new state and resets the cumulative discharge distance to 0
- generated_excerpt:
  @startuml start :Check the vehicle's status value;  if (Status > 9 and < 28, or > 30 and <= 49?) then (yes)   :Set the instantaneous driving mileage gradient to 0;   stop else (no)   :Transition to a new state;   :Set the instantaneous driving mileage to 10;    if (Current stays between -Current Threshold A and Current Threshold A?) then (yes)     :Set the instantaneous driving mileage gradient to 0;     stop   else (no)   endif    if (Vehicle speed exceeds the speed threshold (kph)?) then (yes)     :Enter a new state;     :Reset the cumulative discharge distance to 0;      if (Energy recovery mileage exceeds 1?) then (yes)       :Transition to another state;       :Reset the energy recovery
### us-0139
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 0.6000
- llm_relation_f1: 0.2222
- missing_nodes:
  - do exercise
- extra_nodes:
  - guide exercises
- missing_relations:
  - do exercise -> get guided exercises with alfred
- input_excerpt:
  As an OlderPerson, I want to do guided exercises with ALFRED and ALFRED should also use sensors to capture health data while I am doing exercises.
- generated_excerpt:
  @startuml start partition OlderPerson {   :Do guided exercises with ALFRED; } partition ALFRED {   fork     :Guide exercises;   fork again     :Use sensors to capture health data;   end fork } @enduml
### rac-0009
- dataset: rac
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7660
- relation_f1: 0.7536
- llm_element_status: success
- llm_node_f1: 0.7826
- llm_relation_f1: 0.3797
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2
  - condition judgement
  - shutdown
  - command becomes 4
- extra_nodes:
  - system starts up
  - high-voltage shutdown request is set to 2?
  - condition?
  - system shuts down
  - onboard charger command changes to 4?
  - slow charging turns inactive?
  - slow charging becomes inactive?
- missing_relations:
  - stay in state 127 -> command becomes 4
  - command becomes 4 -> switch to state 12 [yes]
  - switch to state 12 -> ignition switch is off and slow charging is inactive
  - switch to state 12 -> remote mode is disabled
  - switch to state 12 -> pet request mode ends
  - switch to state 12 -> soc reaches 100 and dcdc state is 2
- input_excerpt:
  After the system starts up, if slow charging is active, it enters power-up mode. Then, if the high-voltage shutdown request (for charging or discharging) is set to 2, it switches to state 127. Once in state 127, the following actions apply based on conditions:  1. If the ignition switch is at position 2 and the front MCU state remains unchanged, the system stays in state 127.    a. Should slow charging become inactive and a timeout of 2.2 seconds occur, it switches to state 12. If the ignition switch is off at this point, the system shuts down and ends.    b. Similarly, if slow charging is inactive and the BMS self-check counter reads 1, it switches to state 12. Again, if the ignition switch
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?) then (yes)   :Enter power-up mode;   if (High-voltage shutdown request is set to 2?) then (yes)     :Switch to state 127;     switch (Condition?)     case (Ignition switch at position 2 and front MCU state unchanged)       :Stay in state 127;       if (Slow charging inactive and timeout of 2.2 seconds?) then (yes)         :Switch to state 12;         if (Ignition switch is off?) then (yes)           :System shuts down;           stop         endif       elseif (Slow charging inactive and BMS self-check counter reads 1?) then (yes)         :Switch to state 12;         if (Ignition switch is off?) then (yes)           :System shu
### lmc-0003
- dataset: lmc
- failure_types: missing_activity, missing_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8000
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.8571
- missing_nodes:
  - in single fail state
- missing_relations:
  - in single fail state -> a good channel average of the remaining two good branches
- input_excerpt:
  [RM-003] In the single fail state, a good channel average of the remaining two good branches shall be used to determine the selected value.
- generated_excerpt:
  @startuml start partition System {   :Determine good channel average of the remaining two good branches;   :Determine selected value; } stop @enduml
### rac-0007
- dataset: rac
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8205
- relation_f1: 0.4231
- llm_element_status: success
- llm_node_f1: 0.6897
- llm_relation_f1: 0.7937
- missing_nodes:
  - shutdown
  - flag becomes 2
- extra_nodes:
  - system starts up
  - condition?
  - condition after switching?
  - shut down
  - high-voltage shutdown request flag becomes 2
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging flag is 2
  - flag becomes 0 and cp duty cycle is 85 -> switch to state 126 [yes]
  - switch to state 126 -> bms self-check counter is 1
  - switch to state 130 -> slow charging is inactive
  - bms self-check counter is 1 -> battery pre-heating is required [no]
  - flag becomes 0 and cp duty cycle is 85 -> flag becomes 0 and bms self-check counter is 1 [no]
  - switch to state 126 -> cp duty cycle is 85 and cp amplitude is 3000
  - high-voltage shutdown request charging/discharging flag is 2 -> central control command is 2 and vehicle is not in charging/discharging mode [no]
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?) then (yes)   :Enter power-up mode;   switch (Condition?)   case (High-voltage shutdown request flag is 2)     :Switch to state 115;     switch (Condition after switching?)     case (Flag drops to 0 with CP duty cycle at 85%)       :Switch to state 126;     case (BMS self-check counter shows 1)       :Switch to state 130;     case (Slow charging becomes inactive)       :Shut down;       stop     endswitch   case (Flag drops to 0 with CP duty cycle at 85%)     :Switch to state 126;   case (Battery pre-heating is required)     :Switch to state 130;   case (Slow charging becomes inactive)     :Shut down;     stop   endswitch   swit
### pure-0020
- dataset: pure
- failure_types: missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8750
- relation_f1: 0.7059
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.8696
- missing_nodes:
  - use ppt for voice transmission
- extra_nodes:
  - use push-to-talk (ptt) for voice transmission
- missing_relations:
  - exist multiple channels? -> use ppt for voice transmission [no]
  - manual channel selection -> use ppt for voice transmission [merge]
  - normal services resume? -> give audible/visual indication [no]
- input_excerpt:
  User switches to Direct Mode only when normal services are unavailable. Manual channel selection (if multiple channels exist). Push-To-Talk (PTT) is used for voice transmission. Battery warnings are provided for portables. Audible/visual indication is given when normal services resume.
- generated_excerpt:
  @startuml start if (Normal services unavailable?) then (yes)   :Switch to Direct Mode;   if (Multiple channels exist?) then (yes)     :Manual channel selection;   else (no)   endif   :Use Push-To-Talk (PTT) for voice transmission;   :Provide battery warnings for portables;   if (Normal services resume?) then (yes)     :Give audible/visual indication;   else (no)   endif else (no) endif stop @enduml
### lmc-0002
- dataset: lmc
- failure_types: missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 1.0000
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.3333
- missing_relations:
  - mid-value be selected value -> a first failure in progress?
  - a first failure in progress? -> not affect method for determining selected value [no]
- input_excerpt:
  [RM-002] In the no-fail state, the mid-value shall be the selected value.  Note: a first failure in progress will not affect the method for determining the selected value.
- generated_excerpt:
  @startuml start if (In no-fail state?) then (yes)   :Mid-value shall be the selected value; elseif (First failure in progress?) then (yes)   :Method for determining the selected value is not affected;   :Mid-value shall be the selected value; endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
