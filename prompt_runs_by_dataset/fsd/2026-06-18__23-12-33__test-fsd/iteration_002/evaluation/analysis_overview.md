# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4357
- node_recall: 0.4307
- node_f1: 0.4332
- relation_precision: 0.3490
- relation_recall: 0.3607
- relation_f1: 0.3548
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7747
- llm_node_recall: 0.7951
- llm_node_f1: 0.7632
- llm_relation_precision: 0.6001
- llm_relation_recall: 0.5496
- llm_relation_f1: 0.5553

## Failure Types
- extra_or_wrong_relation: 19
- extra_activity: 18
- missing_or_wrong_relation: 18
- missing_activity: 17
- wrong_parallel: 4

## Representative Failure Cases
### lmc-0011
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4000
- llm_relation_f1: 0.0000
- missing_nodes:
  - system is supported?
  - sensor data is good?
  - autopilot change states from pullup to transition
- extra_nodes:
  - pullup
  - system is supported and sensor data is good?
  - transition
- missing_relations:
  - system is supported? -> sensor data is good? [yes]
  - sensor data is good? -> autopilot change states from pullup to transition [yes]
- input_excerpt:
  7.	The autopilot shall change states from PULLUP to TRANSITION when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml start :PULLUP; if (System is supported and sensor data is good?) then (yes)   :TRANSITION; else (no) endif stop @enduml
### pure-0010
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
  - give out successful trade information
  - save trade instruction
- extra_nodes:
  - central trading system give out the successful trade information
  - security account management save the trade information
- missing_relations:
  - give out successful trade information -> save trade instruction
- input_excerpt:
  1. central trading system: give out the successful trade information 2. security account management: save the trade information
- generated_excerpt:
  @startuml start :central trading system: give out the successful trade information; :security account management: save the trade information; stop @enduml
### us-0216
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3333
- llm_relation_f1: 0.0000
- missing_nodes:
  - identify the number of whales heard in a single audio file
- extra_nodes:
  - select a single audio file
  - play audio file
  - listen for whale sounds
  - identify heard whale
  - increment whale count
  - more whale sounds?
  - display number of whales heard
- input_excerpt:
  As a Zooniverse admin, I want to identify the number of whales heard in a single audio file.
- generated_excerpt:
  @startuml start :Select a single audio file; :Play audio file; repeat   :Listen for whale sounds;   :Identify heard whale;   :Increment whale count; repeat while (More whale sounds?) is (yes) ->no; :Display number of whales heard; stop @enduml
### us-0198
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4444
- llm_relation_f1: 0.0000
- missing_nodes:
  - restrict a group of files from view
- extra_nodes:
  - select a group of files
  - choose restrict from view option
  - apply restriction to the group of files
  - update file visibility status
- input_excerpt:
  As an archivist, I want to restrict a group of files from view.
- generated_excerpt:
  @startuml start :Select a group of files; :Choose restrict from view option; :Apply restriction to the group of files; :Update file visibility status; stop @enduml
### bp-0014
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2069
- relation_f1: 0.0606
- llm_element_status: success
- llm_node_f1: 0.6316
- llm_relation_f1: 0.5778
- missing_nodes:
  - select start
  - select programs
  - select businessobjects xi 3.1
  - select businessobjects enterprise
  - select businessobjects lifecycle manager
  - go to system field
  - enter cms name
  - open authentication drop-down list
- extra_nodes:
  - select start > programs > businessobjects xi 3.1 > businessobjects enterprise > businessobjects lifecycle manager
  - in the system field enter the name of the central management server (cms) on which the lifecycle manager tool is installed
  - select the appropriate authentication method from the authentication drop-down list
  - authentication type
  - requires a user name and a password recognized by the businessobjects enterprise system (default)
  - requires a user name and a password recognized by the businessobjects enterprise system
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
  @startuml start :Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager; :The LifeCycle Manager login screen appears; :In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed; :Enter the user name and password; :Select the appropriate authentication method from the Authentication drop-down list; switch (Authentication type) case (Enterprise authentication)   :Requires a user name and a password recognized by the BusinessObjects Enterprise system (Default); case (LDAP authentication)   :Requires a user name and a password recognized by the BusinessObjects Enterprise s
### lmc-0047
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.7273
- missing_nodes:
  - in the cockpit
  - select heading switch
  - active mode deactivates
- extra_nodes:
  - pilot selects heading switch in the cockpit
  - pilot deselects the heading switch
  - heading hold deactivates
- missing_relations:
  - in the cockpit -> select heading switch
  - select heading switch -> heading hold becomes active mode [case select]
  - select heading switch -> active mode deactivates [case deselect]
  - heading hold becomes active mode -> select heading switch [merge]
  - active mode deactivates -> select heading switch [merge]
- input_excerpt:
  Heading Hold shall become the active mode when the pilot selects the heading switch in the cockpit and deactivate when the switch is deselected.
- generated_excerpt:
  @startuml start :Pilot selects heading switch in the cockpit; :Heading Hold becomes the active mode; :Pilot deselects the heading switch; :Heading Hold deactivates; stop @enduml
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
  - pass
  - fail
- missing_relations:
  - =10? -> allowed [yes]
  - =10? -> not allowed [no]
- input_excerpt:
  8.	The determinant of the Rotation Matrix, |DCM321|, shall be equal to 1.0.
- generated_excerpt:
  @startuml start :Calculate determinant of the Rotation Matrix |DCM321|; if (|DCM321| == 1.0?) then (Yes)   :Pass; else (No)   :Fail; endif stop @enduml
### lmc-0038
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3636
- relation_f1: 0.4444
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.6667
- missing_nodes:
  - allowed
  - not allowed
- extra_nodes:
  - output z
  - zt truth data
  - absolute error > 0.01?
  - exceed tolerance of 0.01
  - within tolerance of 0.01
- missing_relations:
  - absolute error between zt truth data and output z <= 0.01? -> not allowed [no]
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Input (xt, yt); :Output z; :zt truth data; :Calculate absolute error between zt truth data and output z; if (Absolute error > 0.01?) then (yes)   :Exceed tolerance of 0.01; else (no)   :Within tolerance of 0.01; endif stop @enduml
### bp-0021
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3704
- relation_f1: 0.2143
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.6875
- missing_nodes:
  - click new job
  - the list of jobs is displayed
  - select a job from list
  - cick create
  - information is displayed
  - name
  - keywords
  - description
- extra_nodes:
  - the list of jobs in the promotionjob folder is displayed
  - select a job from the job list and click create
  - the name keywords and description of the job are displayed
  - modify name keywords and description if required
  - in the save job in field browse and select the folder in which you want to save the job
- missing_relations:
  - log in lifecycle manager tool -> go to promotion jobs home page
  - click new job -> click the copy an existing job option
  - click the copy an existing job option -> the list of jobs is displayed
  - the list of jobs is displayed -> select a job from list
  - select a job from list -> cick create
  - cick create -> information is displayed
  - information is displayed -> name [fork]
  - information is displayed -> keywords [fork]
- input_excerpt:
  21.	create a new job by copying an existing job.To create a new job by copying an existing job, complete the following steps:1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job.3. Click the Copy an Existing Job option. The list of jobs in the PromotionJob folder is displayed4. Select a job from the job list, and click Create. The name, keywords, and description of the job are displayed. You can modify these fields, if required. However, you cannot change the source system.5. In the Save Job in field, browse and select the folder in which you want to save the job, and click Create.A new job is created.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :Click the Copy an Existing Job option; :The list of jobs in the PromotionJob folder is displayed; :Select a job from the job list, and click Create; :The name, keywords, and description of the job are displayed; :Modify name, keywords, and description if required; :In the Save Job in field, browse and select the folder in which you want to save the job; :Click Create; :A new job is created; stop @enduml
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4286
- relation_f1: 0.3279
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.7692
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
  - on the next screen enter a description for the info package
  - the info package maintenance screen for the scheduler appears
  - to check the load process choose monitor in the toolbar of info package maintenance
  - on the next screen select the date
  - the monitor for the load process is displayed
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation [fork]
  - info area displays information -> data source [fork]
  - transformation -> open data source context menu [merge]
  - data source -> open data source context menu [merge]
  - choose create info package... -> enter description
- input_excerpt:
  7.	Loading Transaction Data1. Go to the Data Warehousing Workbench; in the Modeling area choose Info Provider. The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview.2. In the context menu of the Data source, choose Create Info Package...3. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.4. Go to the tab page Schedule and choose Start.5. To check the load process, choose Monitor in the toolbar of Info Package maintenance.6. On the next screen, select the date and choose Execute. The monitor for the load process is displayed.7. Select the load process f
- generated_excerpt:
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose Info Provider; :The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview; :In the context menu of the Data source, choose Create Info Package...; :On the next screen, enter a description for the Info Package; :Choose Save; :The Info Package maintenance screen for the scheduler appears; :Go to the tab page Schedule; :Choose Start; :To check the load process, choose Monitor in the toolbar of Info Package maintenance; :On the next screen, select the date; :Choose Execute; :The monitor for the load process is displayed; :Select the load process for your Data source 
### pure-0030
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4615
- relation_f1: 0.1429
- llm_element_status: success
- llm_node_f1: 0.8750
- llm_relation_f1: 0.2353
- missing_nodes:
  - respond to
  - user optional processing sequence
  - parameter changes
  - other affective external inputs
- extra_nodes:
  - respond to user optional processing sequence changes
  - respond to user optional parameter changes
  - respond to other external inputs that affect the data processing pipeline
- missing_relations:
  - respond to -> incoming correlator mode changes [fork]
  - respond to -> user optional processing sequence [fork]
  - respond to -> parameter changes [fork]
  - respond to -> other affective external inputs [fork]
  - incoming correlator mode changes -> update internal parameter tables [merge]
  - user optional processing sequence -> update internal parameter tables [merge]
  - parameter changes -> update internal parameter tables [merge]
  - other affective external inputs -> update internal parameter tables [merge]
- input_excerpt:
  Processing Management – The BE shall respond to incoming correlator mode changes, user optional processing sequence and/or parameter changes, and other external inputs that affect the data processing pipeline. Update internal parameter tables and synchronize data processing pipeline with new operational conditions.
- generated_excerpt:
  @startuml start :Respond to incoming correlator mode changes; :Respond to user optional processing sequence changes; :Respond to user optional parameter changes; :Respond to other external inputs that affect the data processing pipeline; :Update internal parameter tables; :Synchronize data processing pipeline with new operational conditions; stop @enduml
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4615
- relation_f1: 0.3793
- llm_element_status: success
- llm_node_f1: 0.0000
- llm_relation_f1: 0.0000
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - select the job want to promote
  - right-click
  - open source and destination systems drop-down lists
  - enter appropriate value
  - create and validate mappings
  - click edit mappings
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - right-click the home page screen and click promote
  - click edit mappings to create and validate mappings
  - security options
  - do not promote security (default option)
  - promote the job along with inherited application rights
  - click view security to view the security dependencies of the infoobjects in the job
  - click test promote to ensure that there is no conflict between cuids
- missing_relations:
  - log in lifecycle manager tool -> selection method
  - selection method -> go to promotion jobs home page [case 1]
  - selection method -> right-click [case 2]
  - right-click -> click promote
  - select the job want to promote -> open source and destination systems drop-down lists [merge]
  - click promote -> open source and destination systems drop-down lists [merge]
  - open source and destination systems drop-down lists -> select source and destination systems
  - enter appropriate value -> click save
- input_excerpt:
  23.	promote a jobLog into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, select the job that you want to promote. You can also right-click the home page screen, and click Promote.3. From the source and the destination systems drop-down lists, select the source and destination systems.Note:Ensure that you have logged into both the source and destination systems before you proceed with the promotion process.4. In the External Change Management ID field, enter the appropriate value, and click Save.5. Click Mappings. Click Edit Mappings if you want to create and validate mappings.6. Click Security Settings, if required. The following options are displayed:• Do not Promote Secur
- generated_excerpt:
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, select the job that you want to promote; :Right-click the home page screen, and click Promote; :From the source and destination systems drop-down lists, select the source and destination systems; :Ensure that you have logged into both the source and destination systems; :In the External Change Management ID field, enter the appropriate value; :Click Save; :Click Mappings; :Click Edit Mappings to create and validate mappings; :Click Security Settings; switch (Security Options) case (Do not Promote Security)   :Do not Promote Security (default option); case (Promote Security)   :Promote jobs 
### pure-0040
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
  - system validates data
  - system updates information
  - back to category screen
- extra_nodes:
  - category type
  - validate the category data
  - update the category information
  - take user back to the category screen
- missing_relations:
  - see view inventory -> navigate to category
  - unique item? -> display unique item screen [yes]
  - unique item? -> display stock item screen [no]
  - system validates data -> system updates information
  - system updates information -> back to category screen
- input_excerpt:
  2. Edit Category 2.1. User navigates to a Category (see View Inventory) 2.2. System displays the Edit Category button 2.3. User clicks the Edit Category button 2.4. System displays the appropriate screen for the Category type 2.4.1. Unique Item 2.4.2. Stock Item 2.5. User edits Category data 2.6. System validates the Category data 2.7. System updates the Category information 2.8. User is taken back to the Category screen
- generated_excerpt:
  @startuml start :Navigate to a Category; :System displays the Edit Category button; :Click the Edit Category button; switch (Category type) case (Unique Item)   :Display screen for Unique Item; case (Stock Item)   :Display screen for Stock Item; endswitch :Edit Category data; :Validate the Category data; :Update the Category information; :Take User back to the Category screen; stop @enduml
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.3830
- llm_element_status: success
- llm_node_f1: 0.9545
- llm_relation_f1: 0.6349
- missing_nodes:
  - condition judgement
  - shutdown
  - high-voltage shutdown request charging/discharging =2
  - wait 0.8s
- extra_nodes:
  - system starts up
  - move to state 175
  - fast charging remains inactive?
  - shut down
  - high-voltage shutdown request detected (value=2)?
  - wait 0.8 seconds
  - enter state 175
  - fast charging is inactive afterward?
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
  @startuml start :System starts up;  if (Charging is active (charging=1)\nand front MCU high-voltage detection flag is 0?) then (yes)   :Transition to state 153;   stop elseif (BMS-fast charger handshake flag is 0\nand front MCU high-voltage flag is 0?) then (yes)   :Enter state 155; else (no)   stop endif  repeat   if (Pre-charge failure occurs?) then (yes)     :Move to state 175;     if (Fast charging remains inactive?) then (yes)       :Shut down;       end     else (no)       break     endif   elseif (High-voltage shutdown request detected (value=2)?) then (yes)     :Wait 0.8 seconds;     :Enter state 175;     if (Fast charging is inactive afterward?) then (yes)       :Shut down;       en
### rac-0004
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5806
- relation_f1: 0.6000
- llm_element_status: success
- llm_node_f1: 0.5357
- llm_relation_f1: 0.4651
- missing_nodes:
  - slow charging state is 1 and charging/discharging power-up is ready
  - condition judgement
  - high-voltage shutdown charging/discharging value is 3 or 4
  - shutdown
  - high-voltage shutdown request is 3 and ignition switch is 2
  - ignition switch becomes 0
- extra_nodes:
  - system starts up
  - slow charging is active (state 1) and charging/discharging system is powered up?
  - in state 105
  - condition?
  - high-voltage shutdown request (value 3) occurs while ignition is on (position 2)
  - return to state 105
  - ignition turns off (position 0)
- missing_relations:
  - switch to state 95 -> vehicle charging/discharging mode is 2 and power-up is ready
  - switch to state 105 -> condition judgement
  - condition judgement -> high-voltage shutdown charging/discharging value is 3 or 4 [case 1]
  - high-voltage shutdown charging/discharging value is 3 or 4 -> switch to state 115
  - slow charging? -> shutdown [no]
  - condition judgement -> high-voltage shutdown request is 3 and ignition switch is 2 [case 2]
  - switch to state 105 -> ignition switch becomes 0
- input_excerpt:
  After the system starts up: - If slow charging is active (state 1) and the charging/discharging system is powered up, switch to state 95. - If the vehicle charging/discharging mode is 2 and the system is powered up, switch to state 105. Then, while in state 105:   1) If the high-voltage shutdown value is 3 or 4, switch to state 115. If slow charging becomes inactive during this, shut down and end the process.   2) If a high-voltage shutdown request (value 3) occurs while the ignition is on (position 2), return to state 105. If the ignition turns off (position 0), switch to state 115. If slow charging becomes inactive, shut down and end.   3) If a pre-charge failure happens, switch to state 1
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active (state 1)\nand charging/discharging system is powered up?) then (yes)   :Switch to state 95; elseif (Vehicle charging/discharging mode is 2\nand system is powered up?) then (yes)   :Switch to state 105;   while (In state 105) is (true)     if (Condition?) then (High-voltage shutdown value is 3 or 4)       :Switch to state 115;       if (Slow charging becomes inactive?) then (yes)         :Shut down;         end       else (no)       endif     elseif (High-voltage shutdown request (value 3)\noccurs while ignition is on (position 2))       :Return to state 105;     elseif (Ignition turns off (position 0))       :Switch to state 115
### pure-0055
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6000
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.8333
- missing_nodes:
  - show items to be purchased
  - system updates inventory
  - reflect sale
- extra_nodes:
  - the system updates the inventory to reflect the sale
- missing_relations:
  - buyer arrives at cashier/checkout desk -> show items to be purchased
  - show items to be purchased -> sales associate scans tags
  - system updates inventory -> reflect sale
- input_excerpt:
  1. Buyer arrives at the cashier or checkout desk with the items to be purchased 2. Sales associate scans the item tags 3. Sales associate processes the sale of the items in QuickBooks POS 4. The system updates the inventory to reflect the sale
- generated_excerpt:
  @startuml start :Buyer arrives at the cashier or checkout desk with the items to be purchased; :Sales associate scans the item tags; :Sales associate processes the sale of the items in QuickBooks POS; :The system updates the inventory to reflect the sale; stop @enduml
### us-0153
- dataset: us
- failure_types: extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.7500
- extra_nodes:
  - collect research data
  - receive regular summary reports
- input_excerpt:
  As a Postgraduate Convenor, I want to receive regular summary reports of research data, so that I understand trends in data use among staff and postgraduate students.
- generated_excerpt:
  @startuml start :Collect research data; :Generate regular summary reports of research data; :Receive regular summary reports; :Understand trends in data use among staff and postgraduate students; stop @enduml
### rac-0007
- dataset: rac
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8000
- relation_f1: 0.6038
- llm_element_status: success
- llm_node_f1: 0.8444
- llm_relation_f1: 0.2105
- missing_nodes:
  - shutdown
  - flag becomes 2
- extra_nodes:
  - system starts up
  - condition?
  - condition after switching to state 115?
  - shut down
  - condition after switching to state 110?
  - high-voltage shutdown request flag becomes 2
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging flag is 2
  - bms self-check counter is 1 -> battery pre-heating is required [no]
  - flag becomes 0 and cp duty cycle is 85 -> flag becomes 0 and bms self-check counter is 1 [no]
  - high-voltage shutdown request charging/discharging flag is 2 -> central control command is 2 and vehicle is not in charging/discharging mode [no]
  - switch to state 110 -> flag becomes 2
  - flag becomes 2 -> switch to state 115 [yes]
  - switch to state 126 -> central control command is 2 and charging state is 2
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?) then (Yes)   :Enter power-up mode;   switch (Condition?)   case (High-voltage shutdown request flag is 2)     :Switch to state 115;     switch (Condition after switching to state 115?)     case (Flag drops to 0 with CP duty cycle at 85%)       :Switch to state 126;     case (BMS self-check counter shows 1)       :Switch to state 130;     case (Slow charging becomes inactive)       :Shut down;       end     endswitch   case (High-voltage shutdown request flag is 2)     :Switch to state 115;     switch (Condition after switching to state 115?)     case (Flag drops to 0 with CP duty cycle at 85%)       :Switch to state 126;     ca
### rac-0020
- dataset: rac
- failure_types: missing_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8276
- relation_f1: 0.5783
- llm_element_status: success
- llm_node_f1: 0.9412
- llm_relation_f1: 0.6591
- missing_nodes:
  - shutdown
  - battery soc=20
  - condition judgement
  - remote mode is enabled
  - slow charging is active
  - fast charging is active
- extra_nodes:
  - system starts up
  - shut down and exit
  - soc is 20?
  - shut down and end
- missing_relations:
  - switch to remote power-up state -> remote mode is disabled
  - switch to state 28 -> gw_trigger=0 and dcdc state=3
  - switch to slow charging power-up state -> slow charging is inactive
  - switch to fast charging power-up state -> fast charging is inactive
  - fast charging active -> gw_trigger=2 [no]
  - switch to state 10 -> battery soc=20
  - battery soc=20 -> switch to state 28 [yes]
  - switch to state 28 -> gw_trigger=0 and soc=80
- input_excerpt:
  After the system starts up, the following steps occur:  First, for remote mode handling: if remote mode is enabled, switch to the remote power-up state; if disabled, switch to state 49. Then, if GW_trigger equals 2 and battery SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Next, for slow charging handling: if slow charging is active, switch to the slow charging power-up state; if inactive, switch to state 129. Then, if GW_trigger equals 2 and SOC is 20, switch to state 28; if GW_trigger equals 0 and DCDC state is 3, shut down and exit.  Then, for fast charging handling: if fast charging is active, switch to the fast charging power-up state; if
- generated_excerpt:
  @startuml start :System starts up;  if (Remote mode enabled?) then (Yes)   :Switch to remote power-up state; else (No)   :Switch to state 49; endif  if (GW_trigger equals 2 and battery SOC is 20?) then (Yes)   :Switch to state 28; elseif (GW_trigger equals 0 and DCDC state is 3?) then (Yes)   :Shut down and exit;   stop else (No) endif  if (Slow charging active?) then (Yes)   :Switch to slow charging power-up state; else (No)   :Switch to state 129; endif  if (GW_trigger equals 2 and SOC is 20?) then (Yes)   :Switch to state 28; elseif (GW_trigger equals 0 and DCDC state is 3?) then (Yes)   :Shut down and exit;   stop else (No) endif  if (Fast charging active?) then (Yes)   :Switch to fast c

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
