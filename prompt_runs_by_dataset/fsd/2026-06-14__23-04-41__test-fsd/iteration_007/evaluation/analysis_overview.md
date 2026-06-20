# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3216
- node_recall: 0.3886
- node_f1: 0.3519
- relation_precision: 0.1887
- relation_recall: 0.1812
- relation_f1: 0.1849
- plantuml_compilation_pass_rate: 0.9000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7077
- llm_node_recall: 0.9200
- llm_node_f1: 0.7633
- llm_relation_precision: 0.5606
- llm_relation_recall: 0.7420
- llm_relation_f1: 0.5765

## Failure Types
- missing_or_wrong_relation: 20
- extra_or_wrong_relation: 20
- extra_activity: 19
- missing_activity: 18
- wrong_parallel: 4
- syntax_error: 2
- wrong_loop: 1

## Representative Failure Cases
### us-0010
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.1818
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5000
- llm_relation_f1: 0.3333
- missing_nodes:
  - get approvals from leadership
- extra_nodes:
  - complete round 1 homepage edits
  - apply design updates and refinements
  - submit round 2 designs for review
  - leadership reviews designs
  - leadership approves?
  - round 2 approved
  - receive feedback from leadership
  - revise homepage designs
- missing_relations:
  - move on to round 2 of homepage edits -> get approvals from leadership
- input_excerpt:
  As a UI designer, I want to move on to round 2 of Homepage edits, so that I can get approvals from leadership.
- generated_excerpt:
  @startuml skinparam style strictuml  title UI Designer - Homepage Edits Round 2  start  :Complete Round 1 Homepage Edits;  :Initiate Round 2 Homepage Edits;  :Apply design updates and refinements;  :Submit Round 2 designs for review;  :Leadership reviews designs;  if (Leadership approves?) then (Yes)   :Round 2 approved;   stop else (No)   :Receive feedback from leadership;   :Revise Homepage designs;   note right: Iterate on Round 2   :Resubmit designs for review;   goto Leadership reviews designs; endif  @enduml
### pure-0040
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4762
- relation_f1: 0.3000
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.9231
- missing_nodes:
  - see view inventory
  - navigate to category
  - display category type screen
  - unique item?
  - system validates data
  - system updates information
  - back to category screen
- extra_nodes:
  - user navigates to a category (see view inventory)
  - system validates the category data
  - system updates the category information
  - user is taken back to the category screen
- missing_relations:
  - see view inventory -> navigate to category
  - navigate to category -> display edit category button
  - click edit category button -> display category type screen
  - display category type screen -> unique item?
  - unique item? -> display unique item screen [yes]
  - unique item? -> display stock item screen [no]
  - display unique item screen -> edit category data
  - system validates data -> system updates information
- input_excerpt:
  2. Edit Category 2.1. User navigates to a Category (see View Inventory) 2.2. System displays the Edit Category button 2.3. User clicks the Edit Category button 2.4. System displays the appropriate screen for the Category type 2.4.1. Unique Item 2.4.2. Stock Item 2.5. User edits Category data 2.6. System validates the Category data 2.7. System updates the Category information 2.8. User is taken back to the Category screen
- generated_excerpt:
  @startuml start :User navigates to a Category (see View Inventory); :System displays the Edit Category button; :User clicks the Edit Category button; switch case (Unique Item)   :System displays the Unique Item screen; case (Stock Item)   :System displays the Stock Item screen; endswitch :User edits Category data; :System validates the Category data; :System updates the Category information; :User is taken back to the Category screen; stop @enduml
### pure-0011
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - send a query
  - implement the query
  - structuralize queried data
  - send data to release
- extra_nodes:
  - trading information release system send a query
  - central trading system implement the query
  - central trading system structuralize the queried data
  - central trading system send the data to release
- missing_relations:
  - send a query -> implement the query
  - implement the query -> structuralize queried data
  - structuralize queried data -> send data to release
- input_excerpt:
  1. trading information release system: send a query 2. central trading system: implement the query 3. central trading system: structuralize the queried data 4. central trading system: send the data to release
- generated_excerpt:
  @startuml start :trading information release system: send a query; :central trading system: implement the query; :central trading system: structuralize the queried data; :central trading system: send the data to release; stop @enduml
### us-0077
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5000
- llm_relation_f1: 0.4286
- missing_nodes:
  - delete scheduled tasks/activities
  - keep schedule clean of unneeded activities
- extra_nodes:
  - camp administrator selects a scheduled task/activity
  - system displays task/activity details
  - camp administrator initiates delete action
  - system prompts for confirmation
  - confirm deletion?
  - system deletes the task/activity from the schedule
  - system updates the schedule
  - system displays success message
- missing_relations:
  - delete scheduled tasks/activities -> keep schedule clean of unneeded activities
- input_excerpt:
  As a camp administrator, I want to be able to delete tasks/activities I scheduled, so that I can keep the schedule clean of unneeded activities.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Camp Administrator selects a scheduled task/activity;  :System displays task/activity details;  :Camp Administrator initiates delete action;  :System prompts for confirmation;  if (Confirm deletion?) then (Yes)   :System deletes the task/activity from the schedule;   :System updates the schedule;   :System displays success message; else (No)   :System cancels deletion;   :System returns to schedule view; endif  stop @enduml
### us-0186
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4615
- llm_relation_f1: 0.3333
- missing_nodes:
  - get all files that checksum has changed since last registered
- extra_nodes:
  - dams manager requests checksum change report
  - preservation manager retrieves list of all registered files
  - preservation manager retrieves current checksums for all files
  - preservation manager compares current checksums against last registered checksums
  - filter files with changed checksums
  - generate report of changed files
  - preservation manager notifies dams manager
  - dams manager views report of files with changed checksums
- input_excerpt:
  As a DAMS manager, I want to know, via the preservation manager, of all files for which the checksum has changed since last registered.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :DAMS Manager requests checksum change report;  fork   :Preservation Manager retrieves list of all registered files; fork again   :Preservation Manager retrieves current checksums for all files; end fork  :Preservation Manager compares current checksums against last registered checksums;  :Filter files with changed checksums;  :Generate report of changed files;  :Preservation Manager notifies DAMS Manager;  :DAMS Manager views report of files with changed checksums;  stop @enduml
### bp-0006
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0571
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.6667
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
  - in the modeling area choose infoprovider
  - the attributes and texts are displayed with transformation and datasource in your infoarea below the characteristic product
  - from the context menu of the datasource choose create info package...
  - on the next screen enter a description for the info package and choose save
  - the info package maintenance screen for the scheduler appears
  - go to the tab page schedule and choose start
  - to check the load process choose monitor in the toolbar of the info package maintenance screen
  - on the next screen select the date and choose execute
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation [fork]
  - info area displays information -> data source [fork]
  - info area displays information -> attributes [fork]
  - info area displays information -> texts [fork]
  - transformation -> open data source context menu
- input_excerpt:
  6.	Loading Master Data forCharacteristic "Product"Go to the Data Warehousing Workbench;in the Modeling area choose Info Provider. The attributes and texts are displayed with transformation and Data source in your Info Area below the characteristic Product.3. Perform the following steps, rst for the attributes of the characteristic and then for the texts of the characteristic.4. From the context menu of the Data source, choose Create Info Package...5. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.6. Go to the tab page Schedule and choose Start.7. To check the load process, choose Monitor in the toolb
- generated_excerpt:
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose InfoProvider; :The attributes and texts are displayed\nwith transformation and Datasource\nin your InfoArea below the characteristic Product; repeat   :From the context menu of the Datasource,\nchoose Create Info Package...;   :On the next screen, enter a description\nfor the Info Package and choose Save;   :The Info Package maintenance screen\nfor the scheduler appears;   :Go to the tab page Schedule and choose Start;   :To check the load process, choose Monitor\nin the toolbar of the Info Package maintenance screen;   :On the next screen, select the date\nand choose Execute;   :The monitor for the load proc
### bp-0012
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0645
- relation_f1: 0.0667
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.4444
- missing_nodes:
  - log in to cmc
  - select applications
  - click user security
  - select administrators
  - view security tab is enabled
  - select rights
  - create a job?
  - set
- extra_nodes:
  - log into cmc and select applications
  - click user security and select administrators
- missing_relations:
  - log in to cmc -> select applications
  - double-click lifecycle manager -> click user security
  - click user security -> select administrators
  - select administrators -> view security tab is enabled
  - view security tab is enabled -> select rights
  - select rights -> create a job? [fork]
  - create a job? -> set [yes]
  - select rights -> edit a job? [fork]
- input_excerpt:
  12.	Set granular application rights to various functions within LifeCycleManager.1. Log into CMC and select Applications.2. Double-click LifeCycle Manager.3. Click User Security, and select Administrators.The View Security tab is enabled.4. Select the rights you want to set.You can set the following rights:• Create a job• Edit a job• Promote a job• Export a BIAR file• Edit a BIAR file• Delete a job• Rollback a job• Use Administration options• Edit Connections properties• Use Version Management System5. Click OK.
- generated_excerpt:
  @startuml start :Log into CMC and select Applications; :Double-click LifeCycle Manager; :Click User Security, and select Administrators; note right: The View Security tab is enabled fork   :Create a job; fork again   :Edit a job; fork again   :Promote a job; fork again   :Export a BIAR file; fork again   :Edit a BIAR file; fork again   :Delete a job; fork again   :Rollback a job; fork again   :Use Administration options; fork again   :Edit Connections properties; fork again   :Use Version Management System; end fork :Click OK; stop @enduml
### rac-0008
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1200
- relation_f1: 0.0656
- llm_element_status: success
- llm_node_f1: 0.5902
- llm_relation_f1: 0.3529
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - switch to state 127
  - slow charging is inactive and front mcu collateral shutdown request flag is 1
  - switch to state 128
  - shutdown
  - issue 2.2s timeout warning
  - switch to state 128
  - enter shutdown state
- extra_nodes:
  - system starts up
  - high-voltage shutdown request (charging/discharging) flag == 2?
  - switch to state 115
  - flag drops to 0?
  - cp duty cycle == 85 ?
  - switch to state 126
  - bms self-check counter == 1?
  - switch to state 130
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0 -> switch to state 127 [if yes]
  - switch to state 127 -> slow charging is inactive and front mcu collateral shutdown request flag is 1
  - slow charging is inactive and front mcu collateral shutdown request flag is 1 -> switch to state 128 [if yes]
  - switch to state 128 -> shutdown
  - slow charging is inactive and front mcu collateral shutdown request flag is 1 -> slow charging is inactive [else if]
  - slow charging is inactive -> issue 2.2s timeout warning [if yes]
  - issue 2.2s timeout warning -> switch to state 128
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging active?) then (Yes)   :Enter power-up mode;   partition "1) High-voltage shutdown request flag == 2" {     if (High-voltage shutdown request (charging/discharging) flag == 2?) then (Yes)       :Switch to state 115;       partition "1a" {         if (Flag drops to 0?) then (Yes)           if (CP duty cycle == 85%?) then (Yes)             :Switch to state 126;           elseif (BMS self-check counter == 1?) then (Yes)             :Switch to state 130;           endif         endif       }       if (Slow charging becomes inactive?) then (Yes)         :Shut down;         end       endif       partition "1b" {         if (Flag drops to 0?) then

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
