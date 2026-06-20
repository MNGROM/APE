# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4358
- node_recall: 0.4960
- node_f1: 0.4639
- relation_precision: 0.3896
- relation_recall: 0.4335
- relation_f1: 0.4104
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8465
- llm_node_recall: 0.8348
- llm_node_f1: 0.8238
- llm_relation_precision: 0.5928
- llm_relation_recall: 0.5858
- llm_relation_f1: 0.5630

## Failure Types
- extra_activity: 18
- extra_or_wrong_relation: 18
- missing_activity: 17
- missing_or_wrong_relation: 15
- wrong_parallel: 4
- wrong_loop: 1

## Representative Failure Cases
### bp-0017
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5714
- llm_relation_f1: 0.3571
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
  - enter the clearcase map drive - enter the name of the folder where the mvfs is located. by default it is /view
  - enter the vob tag name - enter the vob name and the folder where the vob is located. for example vobfolder/vobname
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
  @startuml start :In the Administration Options window, click VMS Settings; :From the Version Management Systems drop-down list, select ClearCase; fork   :Enter the ClearCase Map Drive - Enter the name of the folder where the MVFS is located. By default, it is /view; fork again   :Enter the VOB Tag Name - Enter the VOB name and the folder where the VOB is located. For example: VobFolder/VobName; fork again   :Enter the View Storage Directory - Enter the path of the directory where the views are created; end fork @enduml
### us-0038
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2000
- llm_relation_f1: 0.0000
- missing_nodes:
  - stepped zoom on map visualisations
  - get control over navigation experience
- extra_nodes:
  - open map visualisation
  - select stepped zoom action
  - apply stepped zoom level
  - desired navigation control achieved?
- missing_relations:
  - stepped zoom on map visualisations -> get control over navigation experience
- input_excerpt:
  As a Data Consuming User, I want to be able to have stepped zoom on map visualisations, So that I can have better control over the navigation experience inside a map view.
- generated_excerpt:
  @startuml start :Open map visualisation; repeat :Select stepped zoom action; :Apply stepped zoom level; repeat while (Desired navigation control achieved?) is (No) -> Yes; @enduml
### lmc-0002
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.5000
- missing_nodes:
  - in no-fail state
  - mid-value be selected value
  - a first failure in progress?
  - not affect method for determining selected value
- extra_nodes:
  - in the no-fail state the mid-value shall be the selected value
- missing_relations:
  - in no-fail state -> mid-value be selected value
  - mid-value be selected value -> a first failure in progress?
  - a first failure in progress? -> not affect method for determining selected value [yes]
  - a first failure in progress? -> not affect method for determining selected value [no]
- input_excerpt:
  [RM-002] In the no-fail state, the mid-value shall be the selected value.  Note: a first failure in progress will not affect the method for determining the selected value.
- generated_excerpt:
  @startuml start :In the no-fail state, the mid-value shall be the selected value; note right: a first failure in progress will not affect the method for determining the selected value @enduml
### bp-0014
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1429
- relation_f1: 0.0606
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.3784
- missing_nodes:
  - select start
  - select programs
  - select businessobjects xi 3.1
  - select businessobjects enterprise
  - select businessobjects lifecycle manager
  - go to system field
  - enter cms name
  - enter username and password
- extra_nodes:
  - select start > programs > businessobjects xi 3.1 > businessobjects enterprise > businessobjects lifecycle manager
  - in the system field enter the name of the central management server (cms) on which the lifecycle manager tool is installed
  - enter the user name
  - enter the password
  - select the appropriate authentication method from the authentication drop-down list
  - enter a user name and a password recognized by the businessobjects enterprise system
- missing_relations:
  - select start -> select programs
  - select programs -> select businessobjects xi 3.1
  - select businessobjects xi 3.1 -> select businessobjects enterprise
  - select businessobjects enterprise -> select businessobjects lifecycle manager
  - lifecycle manager login screen appears -> go to system field
  - go to system field -> enter cms name
  - enter cms name -> enter username and password
  - enter username and password -> open authentication drop-down list
- input_excerpt:
  14.	log into the LifeCycle Manager tool.To log into the LifeCycle Manager tool, complete the following steps:1. Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager. The LifeCycle Manager login screen appears.2. In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed.3. Enter the user name and password.4. Select the appropriate authentication method from the Authentication drop-down list.The LifeCycle Manager tool supports the following authentication types:• Enterprise authentication - This authentication type requires a user name and a password that are recognize
- generated_excerpt:
  @startuml start :Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager; :The LifeCycle Manager login screen appears; :In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed; fork :Enter the user name; fork again :Enter the password; end fork switch (Select the appropriate authentication method from the Authentication drop-down list) case (Enterprise authentication)   :Enter a user name and a password recognized by the BusinessObjects Enterprise system; case (LDAP authentication)   :Enter a user name and a password recognized by the BusinessObjects Enterprise system
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
  - dcm321 == 1.0?
  - determinant is valid
  - determinant is invalid
- missing_relations:
  - =10? -> allowed [yes]
  - =10? -> not allowed [no]
- input_excerpt:
  8.	The determinant of the Rotation Matrix, |DCM321|, shall be equal to 1.0.
- generated_excerpt:
  @startuml start :Calculate determinant of the Rotation Matrix |DCM321|; if (|DCM321| == 1.0?) then (Yes)   :Determinant is valid; else (No)   :Determinant is invalid; endif stop @enduml
### us-0208
- dataset: us
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 0.7273
- llm_relation_f1: 0.4000
- missing_nodes:
  - avoid ambiguity between my work and others
- extra_nodes:
  - identifier type?
  - enter researcherid
  - enter orcid
  - resolve ambiguity between work and someone else with the same name
- input_excerpt:
  As a Cornell faculty member, I want to associate a researcherID or ORCID with a submission, so that there is no ambiguity between my work and someone else with the same name.
- generated_excerpt:
  @startuml start :Associate a researcherID or ORCID with a submission; switch (Identifier type?) case (researcherID)   :Enter researcherID; case (ORCID)   :Enter ORCID; endswitch :Resolve ambiguity between work and someone else with the same name; stop @enduml
### bp-0001
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3158
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7826
- llm_relation_f1: 0.4348
- missing_nodes:
  - load master data
  - dene a query
  - analyze data
  - add comments to data
- extra_nodes:
  - load the data
  - loading master data for characteristic product
  - define a query that is used as the basis for a web application and allows for an ad-hoc analysis of the data in the web
  - defining queries
  - create a web application with navigation options and functions such as printing based on the query
  - analyze the data in the web application
  - add comments to it
  - analyzing data in the web application
- missing_relations:
  - load master data -> load transaction data
  - load transaction data -> dene a query
  - dene a query -> create web applications
  - create web applications -> analyze data
  - analyze data -> add comments to data
  - add comments to data -> broadcast the data by e-mail to other employees
- input_excerpt:
  1.	Creating Master Data Directly in the System0.	Load the data. Creating Master Data Directly in the System1.	Loading Master Data for Characteristic "Product"2.	Loading Transaction Data3.	Dene a query that is used as the basis for a Web application and allows for an ad-hoc analysis of the data in the Web.4.	You create the query in the following step:5.	Dening Queries6.	Create a Web application with navigation options and functions, such as printing based on the query.7.	You create the Web application in the following step:8.	Creating Web Applications9.	Analyze the data in the Web application, add comments to it, and broadcast it by E-mail to other employees.10.	You analyze and broadcast the 
- generated_excerpt:
  @startuml start :Load the data; :Loading Master Data for Characteristic "Product"; :Loading Transaction Data; :Define a query that is used as the basis for a Web application and allows for an ad-hoc analysis of the data in the Web; :Defining Queries; :Create a Web application with navigation options and functions, such as printing based on the query; :Creating Web Applications; fork   :Analyze the data in the Web application; fork again   :Add comments to it; fork again   :Broadcast it by E-mail to other employees; end fork :Analyzing Data in the Web Application; :Broadcasting Web Applications by E-Mail; stop @enduml
### lmc-0013
- dataset: lmc
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.6667
- missing_nodes:
  - autopilot change states from standby to maneuver
- extra_nodes:
  - autopilot in standby
  - change state to maneuver
- input_excerpt:
  9.	The autopilot shall change states from STANDBY to MANEUVER when a failure occurs (apfail).
- generated_excerpt:
  @startuml start :Autopilot in STANDBY; if (A failure occurs (apfail)?) then (yes)   :Change state to MANEUVER; else (no) endif @enduml
### pure-0098
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4444
- relation_f1: 0.3636
- llm_element_status: success
- llm_node_f1: 0.6364
- llm_relation_f1: 0.0769
- missing_nodes:
  - refer to warc file content
  - summaries
  - mime-type breakdowns
  - generate reports
  - apply filters
- extra_nodes:
  - report type?
  - generate summary report
  - generate mime-type breakdown report
  - export format?
  - export report in csv format
- missing_relations:
  - use command warc_summary options -> refer to warc file content
  - refer to warc file content -> summaries [fork]
  - refer to warc file content -> mime-type breakdowns [fork]
  - refer to warc file content -> hostname reports [fork]
  - generate reports -> export reports in formats like xml/csv [fork]
  - generate reports -> apply filters [fork]
  - apply filters -> restrict reports by time ranges/domains
- input_excerpt:
  Reporting Tool Execution: Use the command warc_summary <WARC_FILES> [options] to generate reports on WARC file content, such as summaries, MIME-type breakdowns, or hostname reports. Export reports in formats like XML or CSV and apply filters to restrict reports by time ranges or domains.
- generated_excerpt:
  @startuml start :Execute command warc_summary <WARC_FILES> [options]; switch (Report type?) case (Summary)   :Generate summary report; case (MIME-type breakdown)   :Generate MIME-type breakdown report; case (Hostname report)   :Generate hostname report; endswitch switch (Export format?) case (XML)   :Export report in XML format; case (CSV)   :Export report in CSV format; endswitch :Apply filters to restrict reports by time ranges or domains; @enduml
### pure-0058
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4444
- relation_f1: 0.1875
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.6061
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
  - folder non suitable for database?
  - a message file not found appears
  - user selects another folder
  - master password is wrong?
- missing_relations:
  - open keepass -> select open->database
  - select open->database -> navigate through folders
  - navigate through folders -> select database
  - select database -> folder is suitable?
  - folder is suitable? -> file not found appears [no]
  - file not found appears -> select another folder
  - select another folder -> navigate through folders [loop]
  - folder is suitable? -> choose cancel [yes]
- input_excerpt:
  1. User opens KeePass and select Open->Database 2. User navigates through his folders 3. User selects a database 4. User types Master Password 5. The main database window opens 3.2.2.2.1 Alternative Data Flow 1 3a. User selects a type of folder non suitable for database 3b. A message “file not found” appears 3c. User selects another folder 3.2.2.2.2 Alternative Data Flow 2 4a. Master Password is wrong 4b. A message “invalid/wrong key” appears 4c. User types another master key 3.2.2.2.3 Alternative Data Flow 3 3. User chooses cancel 4. Exit from KeePass
- generated_excerpt:
  @startuml start :User opens KeePass and select Open->Database; repeat   :User navigates through his folders;   if (User chooses cancel?) then (yes)     :Exit from KeePass;     stop   else (no)     :User selects a database;     if (Folder non suitable for database?) then (yes)       :A message "file not found" appears;       :User selects another folder;     else (no)       repeat         :User types Master Password;         if (Master Password is wrong?) then (yes)           :A message "invalid/wrong key" appears;           :User types another master key;         else (no)         endif       repeat while (Master Password is wrong?) is (yes) not (no)     endif   endif repeat while (Folder no
### us-0215
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.2857
- extra_nodes:
  - receive related information about persons
  - receive videos
- input_excerpt:
  As a user, I want to identify persons in videos, and receive related information about them.
- generated_excerpt:
  @startuml start :Identify persons in videos; fork   :Receive related information about persons; fork again   :Receive videos; end fork stop @enduml
### rac-0006
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3636
- llm_element_status: success
- llm_node_f1: 0.8947
- llm_relation_f1: 0.8261
- missing_nodes:
  - condition judgement
  - remote mode is enabled
  - shutdown
  - pet mode request handling is finished
  - battery soc is 20
  - battery soc reaches 80 and dcdc state is 3
- extra_nodes:
  - if slow charging is active
  - trigger?
  - enter state 110
  - slow charging becomes inactive?
  - go to state 28
  - shut down
  - move to state 28
  - soc reaches 80 and dcdc state is 3?
- missing_relations:
  - enter power-up mode -> condition judgement
  - condition judgement -> remote mode is enabled [case 1]
  - switch to state 28 -> remote mode is disabled
  - condition judgement -> pet mode request is received [case 2]
  - switch to state 28 -> pet mode request handling is finished
  - pet mode request handling is finished -> shutdown [yes]
  - condition judgement -> battery soc is 20 [case 3]
  - battery soc is 20 -> switch to state 110
- input_excerpt:
  After the system starts up: If slow charging is active, go into power-up mode. Then: 1.  If remote mode is enabled, enter state 110. Then, if slow charging becomes inactive, go to state 28. Finally, if remote mode is disabled, shut down and end. 2.  If a pet mode request comes in, switch to state 110. Then, if slow charging is inactive, move to state 28. Once the pet mode request is handled, shut down and end. 3.  If the battery SOC is 20, enter state 110. Then, if slow charging is inactive, switch to state 28. If the SOC later reaches 80 and the DCDC state is 3, shut down and end.
- generated_excerpt:
  @startuml start :If slow charging is active; if (Slow charging active?) then (yes)   :Go into power-up mode;   switch (Trigger?)   case (Remote mode enabled)     :Enter state 110;     if (Slow charging becomes inactive?) then (yes)       :Go to state 28;     endif     if (Remote mode is disabled?) then (yes)       :Shut down;       end     endif   case (Pet mode request comes in)     :Switch to state 110;     if (Slow charging is inactive?) then (yes)       :Move to state 28;     endif     :Pet mode request is handled;     :Shut down;     end   case (Battery SOC is 20)     :Enter state 110;     if (Slow charging is inactive?) then (yes)       :Switch to state 28;     endif     if (SOC reache
### lmc-0047
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.5000
- missing_nodes:
  - in the cockpit
  - active mode deactivates
- extra_nodes:
  - select heading switch in the cockpit
  - heading hold deactivates
- missing_relations:
  - select heading switch -> active mode deactivates [case deselect]
  - heading hold becomes active mode -> select heading switch [merge]
  - active mode deactivates -> select heading switch [merge]
- input_excerpt:
  Heading Hold shall become the active mode when the pilot selects the heading switch in the cockpit and deactivate when the switch is deselected.
- generated_excerpt:
  @startuml start :Select heading switch in the cockpit; if (Heading switch selected?) then (yes)   :Heading Hold becomes the active mode; else (no)   :Heading Hold deactivates; endif stop @enduml
### pure-0095
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5455
- relation_f1: 0.4000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.2667
- missing_nodes:
  - refer to provided configuration
  - specify how fields are translated into warc records
  - handle missing fields
- extra_nodes:
  - ensure configuration file specifies how fields are translated into warc records
  - fields missing?
- missing_relations:
  - use command arc_warc_migrate options -> refer to provided configuration
  - refer to provided configuration -> specify how fields are translated into warc records [fork]
  - refer to provided configuration -> generate errors requiring operator intervention [fork]
  - generate errors requiring operator intervention -> handle missing fields
- input_excerpt:
  Migration Tool Execution: Use the command arc_warc_migrate <ARC_FILES> <CONFIG> [options] to migrate content from ARC files to WARC files based on the provided configuration. Ensure the configuration file specifies how fields are translated into WARC records, and handle missing fields by generating errors requiring operator intervention.
- generated_excerpt:
  @startuml start :Use command arc_warc_migrate <ARC_FILES> <CONFIG> [options]; :Ensure configuration file specifies how fields are translated into WARC records; :Migrate content from ARC files to WARC files based on the provided configuration; if (Fields missing?) then (yes)   :Generate errors requiring operator intervention; else (no) endif @enduml
### pure-0041
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5455
- relation_f1: 0.6364
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.8889
- missing_nodes:
  - see view inventory
  - display category type screen
  - unique item?
  - system validates deletion
  - system removes category
  - back to parent department/category
- extra_nodes:
  - category type
  - system validates the category deletion
  - system removes the category from the inventory
  - user is taken back to the parent department or category of the deleted category
- missing_relations:
  - see view inventory -> navigate to category
  - click edit category button -> display category type screen
  - unique item? -> display unique item screen [yes]
  - unique item? -> display stock item screen [no]
  - system removes category -> back to parent department/category
- input_excerpt:
  3. Delete Category 3.1. User navigates to a Category (see View Inventory) 3.2. System displays the Edit Category button 3.3. User clicks the Edit Category button 3.4. System displays the appropriate screen for the Category type 3.4.1. Unique Item 3.4.2. Stock Item 3.5. User clicks the Delete Category button 3.6. System validates the Category deletion 3.7. System removes the Category from the inventory 3.8. User is taken back to the parent Department or Category of the deleted Category
- generated_excerpt:
  @startuml start :User navigates to a Category; :System displays the Edit Category button; :User clicks the Edit Category button; switch (Category type) case (Unique Item)   :System displays the Unique Item screen; case (Stock Item)   :System displays the Stock Item screen; endswitch :User clicks the Delete Category button; :System validates the Category deletion; :System removes the Category from the inventory; :User is taken back to the parent Department or Category of the deleted Category; stop @enduml
### rac-0011
- dataset: rac
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7179
- relation_f1: 0.8462
- llm_element_status: success
- llm_node_f1: 0.9655
- llm_relation_f1: 0.8772
- missing_nodes:
  - enter power-up mode
  - shutdown
  - high-voltage shutdown request charging/discharging is 2
  - switch to state 105
- extra_nodes:
  - system starts up
  - enter power-up state
  - enter state 82
  - high-voltage shutdown request is 2?
  - enter state 127
  - system shuts down and ends
  - enter state 105
- missing_relations:
  - switch to state 82 -> slow charging is inactive
  - high-voltage shutdown request charging/discharging is 2 -> high-voltage shutdown request charging/discharging is 2 and bms counter=2 [no]
  - switch to state 127 -> recharge demand =1 and ac discharge system no fault
- input_excerpt:
  After the system starts up, the following logic applies:  1. If slow charging is active, the system enters the "power-up" state. Then:    a. When the AC charging system fault is 1, the system switches to state 127. If recharge demand is 1 and front MCU initialization state is 0, it enters state 82. Should slow charging become inactive at any point, the system shuts down and ends.    b. If a high-voltage shutdown request (for charging/discharging) is 2, the system switches to state 126. When recharge demand is 1 and the front MCU low-voltage shutdown flag is 0, it enters state 127. If the front MCU low-voltage flag becomes 1 or a 2.2-second timeout occurs, it switches to state 82. Should slow
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?) then (yes)   :Enter "power-up" state;   if (AC charging system fault is 1?) then (yes)     :Switch to state 127;     if (Recharge demand is 1 and front MCU initialization state is 0?) then (yes)       :Enter state 82;     endif   elseif (High-voltage shutdown request is 2?) then (yes)     :Switch to state 126;     if (Recharge demand is 1 and front MCU low-voltage shutdown flag is 0?) then (yes)       :Enter state 127;     endif     if (Front MCU low-voltage flag becomes 1 or 2.2-second timeout occurs?) then (yes)       :Switch to state 82;     endif   elseif (High-voltage shutdown request is 2 and BMS counter is 2?) then (yes)
### rac-0019
- dataset: rac
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7541
- relation_f1: 0.5946
- llm_element_status: success
- llm_node_f1: 0.9315
- llm_relation_f1: 0.4944
- missing_nodes:
  - remote mode is disabled
  - slow charging is inactive
  - fast charging is inactive
  - switch to state 189
- extra_nodes:
  - system starts up
  - move to state 49
  - exit
  - proceed to state 49
  - slow charging is active and charging system command is 4?
  - go to state 29
  - transition to state 49
  - move to state 110
- missing_relations:
  - switch to state 29 -> ignition switch=0 and vcc2=12
  - fast charge vcc2=6 -> slow charging is active and charging system command=1 [no]
  - switch to state 110 -> charging system command=4
  - switch to state 29 -> ignition switch=0 and slow charging is inactive
  - switch to state 28 -> remote mode is disabled
  - switch to state 110 -> slow charging is inactive
  - switch to state 170 -> fast charging is inactive
  - switch to state 10 -> battery soc=20 and dcdc state=1
- input_excerpt:
  After the system starts up, if the ignition switch is set to 2, transition to state 30. Then, under that condition: - If the ignition switch becomes 0, move to state 49 and exit. - If the fast charge Vcc2 is 6, observe the charging gun indicator. Should the charging system command be 4, switch to state 29. - If the ignition switch is 0 and Vcc2 is 12, proceed to state 49 and exit. - If slow charging is active and the charging system command is 1, transition to state 110. If the command is 4 instead, go to state 29. Also, if the ignition switch is 0 and slow charging is not active, shift to state 49 and exit.  If remote mode is enabled, switch to state 28. If it's disabled, transition to stat
- generated_excerpt:
  @startuml start :System starts up; if (Ignition switch is set to 2?) then (yes)   :Transition to state 30;   if (Ignition switch becomes 0?) then (yes)     :Move to state 49;     :Exit;   elseif (Fast charge Vcc2 is 6?) then (yes)     :Observe the charging gun indicator;     if (Charging system command is 4?) then (yes)       :Switch to state 29;     else (no)       endif   elseif (Ignition switch is 0 and Vcc2 is 12?) then (yes)     :Proceed to state 49;     :Exit;   elseif (Slow charging is active and charging system command is 1?) then (yes)     :Transition to state 110;   elseif (Slow charging is active and charging system command is 4?) then (yes)     :Go to state 29;   elseif (Ignition
### rac-0009
- dataset: rac
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8000
- relation_f1: 0.8000
- llm_element_status: success
- llm_node_f1: 0.9388
- llm_relation_f1: 0.7532
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2
  - condition judgement
  - shutdown
  - command becomes 4
- extra_nodes:
  - system starts up
  - high-voltage shutdown request is set to 2?
  - condition check
  - system shuts down
  - onboard charger command changes to 4?
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
  @startuml start :System starts up; if (Slow charging is active?) then (yes)   :Enter power-up mode;   if (High-voltage shutdown request is set to 2?) then (yes)     :Switch to state 127;     switch (Condition check)     case (Ignition switch at position 2 and front MCU state unchanged)       :Stay in state 127;       if (Slow charging is inactive and timeout of 2.2 seconds occur?) then (yes)         :Switch to state 12;         if (Ignition switch is off?) then (yes)           :System shuts down;           end         endif       elseif (Slow charging is inactive and BMS self-check counter reads 1?) then (yes)         :Switch to state 12;         if (Ignition switch is off?) then (yes)      
### bp-0025
- dataset: bp
- failure_types: missing_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8372
- relation_f1: 0.7170
- llm_element_status: success
- llm_node_f1: 0.9362
- llm_relation_f1: 0.9474
- missing_nodes:
  - go to promote window
  - click mappings
  - tabs are displayed
  - open destination url drop-down list
  - select a destination url
- extra_nodes:
  - in the promote window click mappings
  - from the destination url drop-down list select a destination url for the selected source url
- missing_relations:
  - click mappings -> click edit mappings
  - click edit mappings -> tabs are displayed
  - tabs are displayed -> connection mappings [fork]
  - tabs are displayed -> qaaws mappings [fork]
  - tabs are displayed -> crystal report mappings [fork]
  - tabs are displayed -> federation mappings [fork]
  - destination field displays edited source url -> open destination url drop-down list [merge]
  - open destination url drop-down list -> select a destination url
- input_excerpt:
  25.	map a QaaWS1. In the "Promote" window, click Mappings.2. Click Edit Mappings.The following tabs are displayed:• Connection Mappings• QaaWS Mappings• Crystal Report Mappings• Federation Mappings3. Click QaaWS Mappings.The source URL and the Query as a Web Service types are displayed. If you want to edit the properties of the source URL, select the source URL, and click Edit QaaWs Properties. The Edit QaaWS Propertiestab appears. This tab displays the list of properties and their values. Modify the values per your requirements, and click Apply. The QaaWS Mappings tab appears.Note:If you edit the source URL, the destination field displays the following message: Edited Source URL4. From the 
- generated_excerpt:
  @startuml start :In the "Promote" window, click Mappings; :Click Edit Mappings; fork   :Connection Mappings; fork again   :QaaWS Mappings; fork again   :Crystal Report Mappings; fork again   :Federation Mappings; end fork :Click QaaWS Mappings; :The source URL and the Query as a Web Service types are displayed; if (Want to edit the properties of the source URL?) then (Yes)   :Select the source URL;   :Click Edit QaaWs Properties;   :The Edit QaaWS Properties tab appears;   :The list of properties and their values are displayed;   :Modify the values per your requirements;   :Click Apply;   :The QaaWS Mappings tab appears;   :The destination field displays the message: Edited Source URL; else 

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
