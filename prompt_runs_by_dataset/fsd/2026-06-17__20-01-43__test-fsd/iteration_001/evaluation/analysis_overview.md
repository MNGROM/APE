# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2735
- node_recall: 0.2945
- node_f1: 0.2836
- relation_precision: 0.3309
- relation_recall: 0.2844
- relation_f1: 0.3059
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 10.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7660
- llm_node_recall: 0.8391
- llm_node_f1: 0.7588
- llm_relation_precision: 0.6387
- llm_relation_recall: 0.7041
- llm_relation_f1: 0.6151

## Failure Types
- missing_activity: 10
- extra_activity: 10
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 9
- wrong_parallel: 1

## Representative Failure Cases
### us-0098
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5000
- llm_relation_f1: 0.2667
- missing_nodes:
  - edit profile
  - upload new information
- extra_nodes:
  - owner selects edit profile
  - system displays current profile information
  - owner modifies profile fields
  - owner clicks save
  - system validates input
  - valid input?
  - system updates profile information
  - system displays success message
- missing_relations:
  - edit profile -> upload new information
- input_excerpt:
  As an Owner, I want to edit my profile, so that that it is updated with new information.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Owner selects "Edit Profile";  :System displays current profile information;  :Owner modifies profile fields;  :Owner clicks "Save";  :System validates input;  if (Valid input?) then (Yes)   :System updates profile information;   :System displays success message; else (No)   :System displays error message;   :Owner corrects input;   stop   note right: Returns to edit form endif  stop @enduml
### us-0092
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3000
- llm_relation_f1: 0.3158
- missing_nodes:
  - get full details of data package schema changes
  - adjust scripts to handle
- extra_nodes:
  - consumer logs into the system
  - navigate to data package section
  - select a data package
  - view schema change history
  - schema changes available?
  - display detailed schema changes
  - list of added fields
  - list of removed fields
- missing_relations:
  - get full details of data package schema changes -> adjust scripts to handle
- input_excerpt:
  As a Consumer, I want to know full details of how the data package schema has changed, so that that I can adjust my scripts to handle it.
- generated_excerpt:
  @startuml skinparam style strictuml  title Consumer: View Data Package Schema Change Details  start  :Consumer logs into the system; :Navigate to Data Package section;  :Select a Data Package;  :View Schema Change History;  if (Schema Changes Available?) then (Yes)   :Display detailed schema changes;   partition "Schema Change Details" {     :List of added fields;     :List of removed fields;     :List of modified fields (type changes, constraints, etc.);     :Version comparison (Previous vs Current);   }      :Consumer reviews change details;      :Consumer adjusts external scripts to handle schema changes;      :Consumer validates updated scripts;    else (No)   :Display "No schema changes
### lmc-0048
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.8571
- missing_nodes:
  - requirement when heading hold mode becomes active
  - pilot uses cockpit control
  - set heading hold reference
- extra_nodes:
  - heading hold mode becomes the active mode
  - pilot sets heading hold reference via cockpit control
- missing_relations:
  - requirement when heading hold mode becomes active -> pilot uses cockpit control
- input_excerpt:
  Requirement	When heading hold mode becomes the active mode the heading hold reference shall be set by the pilot via a cockpit control.
- generated_excerpt:
  @startuml start :Heading hold mode becomes the active mode; :Pilot sets heading hold reference via cockpit control; stop @enduml
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1143
- relation_f1: 0.1053
- llm_element_status: success
- llm_node_f1: 0.7000
- llm_relation_f1: 0.4583
- missing_nodes:
  - click arrows in revenue eld?
  - sort increasing or decreasing
  - click alternative mouse button
  - open context menu
  - choose sort increasing or sort decreasing
  - internet channel is the greatest
  - analyze differences for months?
  - open dropdown box calendar year/month
- extra_nodes:
  - interested in revenue data
  - click arrows in revenue field to sort (increasing/decreasing)
  - right-click revenue field
  - choose sort increasing or sort decreasing from context menu
  - observe greatest revenue is from internet channel
  - select 08.2007 in calendar year/month dropdown
  - select 07.2007 in calendar year/month dropdown
  - observe internet revenue increased greatly (marketing campaign successful)
- missing_relations:
  - sort revenue data -> click arrows in revenue eld?
  - click arrows in revenue eld? -> sort increasing or decreasing [yes]
  - click arrows in revenue eld? -> click alternative mouse button [no]
  - sort increasing or decreasing -> internet channel is the greatest [merge]
  - click alternative mouse button -> open context menu
  - open context menu -> choose sort increasing or sort decreasing
  - choose sort increasing or sort decreasing -> internet channel is the greatest [merge]
  - internet channel is the greatest -> analyze differences for months?
- input_excerpt:
  10.	Analyzing Data in the Web Application1. Since you are interested in the revenue, you want to sort the revenue data.2. Click on the arrows in the Revenue eld to sort the revenue data in increasing or decreasing order.3. You can also sort the revenue by clicking the alternative mouse button on Revenue and choosing Sort Sort Increasing or Sort Decreasing in the context menu. You see that the greatest revenue is obtained with the distribution channel Internet.4. To see the differences in the revenue data for the months July, August and September, select rst 08.2007 and then 07.2007 in the dropdown box Calendar Year/Month. You see that the revenue data for the distribution channel Internet in
- generated_excerpt:
  @startuml start :Interested in revenue data; :Sort revenue data; fork   :Click arrows in Revenue field to sort (Increasing/Decreasing); fork again   :Right-click Revenue field;   :Choose Sort Increasing or Sort Decreasing from context menu; end fork :Observe greatest revenue is from Internet channel; :Select 08.2007 in Calendar Year/Month dropdown; :Select 07.2007 in Calendar Year/Month dropdown; :Observe Internet revenue increased greatly\n(Marketing campaign successful); :Filter data back to September\n(Select 09.2007 in dropdown); :Right-click subtotal of Internet channel (567,308.05); :Choose Documents > Create New Comment\nfrom context menu; :Enter name and description for the document;
### lmc-0055
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.2500
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.8571
- missing_nodes:
  - dcm321 * dcm321t
  - allowed
  - not allowed
- extra_nodes:
  - initialize rotation matrix dcm321
  - compute transpose of rotation matrix dcm321t
  - multiply dcm321 by dcm321t (dcm321 * dcm321t)
  - validation passed
  - validation failed
- missing_relations:
  - =identity (3x3) matrix.v? -> allowed [yes]
  - =identity (3x3) matrix.v? -> not allowed [no]
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml start :Initialize Rotation Matrix DCM321; :Compute Transpose of Rotation Matrix DCM321T; :Multiply DCM321 by DCM321T (DCM321 * DCM321T); if (Result == Identity (3x3) Matrix?) then (Yes)   :Validation Passed; else (No)   :Validation Failed; endif stop @enduml
### pure-0046
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3243
- relation_f1: 0.3750
- llm_element_status: success
- llm_node_f1: 0.7500
- llm_relation_f1: 0.6275
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
  - system displays the edit details screen which displays all existing item details and their detail x department and category assignments
  - user filters view by detail status?
  - user filters view by detail status (active inactive all)
  - user edits details
  - user changes detail x department or category assignments
  - user changes detail data
  - user creates new detail
  - system updates the item detail information
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
  @startuml skinparam style strictuml  start  :User accesses the main inventory screen;  :System displays the Edit Details button;  :User clicks the Edit Details button;  :System displays the Edit Details screen which displays all existing item details and their detail x department and category assignments;  if (User filters view by detail status?) then (Yes)   :User filters view by detail status   (active, inactive, all); else (No) endif  repeat   :User edits details;    fork     :User changes detail x department     or category assignments;   fork again     :User changes detail data;   fork again     :User changes detail active x inactive status;   fork again     :User creates new detail;   
### pure-0078
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3636
- relation_f1: 0.1818
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.8000
- missing_nodes:
  - selects period within displayed period
  - operation
  - encloses selected period
- extra_nodes:
  - the user selects a period of time within the displayed viewing period
  - expand or contract?
  - expand the selected period
  - contract the selected period
- missing_relations:
  - selects period within displayed period -> operation
  - operation -> selected period becomes new viewing period [case expand]
  - operation -> new viewing period becomes twice [case contract]
- input_excerpt:
  1. The user selects a period of time within the displayed viewing period over which to expand or contract in time. 2. The tool expands or contracts the selected period. If expanding, the selected period becomes the new viewing period. If contracting, the new viewing period becomes twice as long as the selected period and encloses it.
- generated_excerpt:
  @startuml start :The user selects a period of time within the displayed viewing period; if (Expand or Contract?) then (Expand)   :Expand the selected period;   :The selected period becomes the new viewing period; else (Contract)   :Contract the selected period;   :The new viewing period becomes twice as long as the selected period and encloses it; endif stop @enduml
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4651
- relation_f1: 0.3830
- llm_element_status: success
- llm_node_f1: 0.8710
- llm_relation_f1: 0.5846
- missing_nodes:
  - switch to state 95
  - condition judgement
  - in remote mode
  - remote mode is closed
  - shutdown
  - pet mode open request is closed
- extra_nodes:
  - system starts up
  - move to state 95
  - proceed to state 105
  - remote mode?
  - go to state 105
  - slow charging becomes inactive?
  - shift to state 28
  - remote mode deactivates?
- missing_relations:
  - switch to state 93 -> charging/discharging power-up is active and front mcu high-voltage detection flag is 1
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - switch to state 105 -> condition judgement
  - condition judgement -> in remote mode [case in remote mode]
  - switch to state 28 -> remote mode is closed
  - condition judgement -> pet mode request is received [case pet mode request is received]
  - switch to state 28 -> pet mode open request is closed
  - pet mode open request is closed -> shutdown [yes]
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System starts up;  if (Slow charging is active\nand front MCU high-voltage detection flag = 0?) then (Yes)   :Transition to state 93; elseif (Charging/discharging power-up is active\nand front MCU high-voltage detection flag = 1?) then (Yes)   :Move to state 95; elseif (Power-up readiness is confirmed\nand vehicle charging/discharging mode = 2?) then (Yes)   :Proceed to state 105; endif  partition "Case Handling" {   if (Remote mode?) then (Yes)     :Go to state 105;     if (Slow charging becomes inactive?) then (Yes)       :Shift to state 28;     endif     if (Remote mode deactivates?) then (Yes)       :Initiate shutdown;       :Terminate;       stop     endif   elseif (Pet
### bp-0028
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6047
- relation_f1: 0.4906
- llm_element_status: success
- llm_node_f1: 0.8400
- llm_relation_f1: 0.7500
- missing_nodes:
  - log in
  - more information?
  - see creating a new job
  - open drop-lists
  - select output to a biar file
  - click add objects
  - infoobjects are added
  - other operations?
- extra_nodes:
  - log into lifecycle manager tool
  - select output to a biar file from destination system drop-down list
  - click add objects to add infoobjects to the job
  - click promote
  - select destination?
- missing_relations:
  - log in -> create a new job
  - create a new job -> more information?
  - more information? -> see creating a new job [yes]
  - more information? -> open drop-lists [no]
  - see creating a new job -> open drop-lists [merge]
  - open drop-lists -> select output to a biar file
  - click create -> click add objects
  - click add objects -> infoobjects are added
- input_excerpt:
  28.	Exporting a Job to a BIAR File1. Log into the LifeCycle Manager tool, and create a new job. For more information on creating a new job, see Creating a New Job on page 372. In the Destination System drop-down list, select Output to a BIAR file option and click Create.3. Click Add objects to add infoobjects to the job. You can use the Manage Dependencies option to manage the dependencies of the selected job.4. Click Promote.The "Promote - Job Name" screen appears.5. Click Export.The BIAR file is created. You can save a BIAR file to a File System or an FTP location.6. In the "Promote - Job Name"screen, click Biar File Destination. Biar File Destination pane appears.7. Select either File Sys
- generated_excerpt:
  @startuml start :Log into LifeCycle Manager tool; :Create a new job; :Select "Output to a BIAR file" from Destination System drop-down list; :Click Create; :Click Add objects to add infoobjects to the job; :Manage Dependencies (optional); :Click Promote; :"Promote - Job Name" screen appears; :Click Export; :BIAR file is created; :Click Biar File Destination; :Biar File Destination pane appears; if (Select Destination?) then (File System)   :Select File System;   :Click Export;   :BIAR file is exported to a file system; else (FTP)   :Select FTP;   :Enter host, port, username, password, directory, and filename;   :Click Export;   :BIAR file is exported to an FTP location; endif stop @enduml
### rac-0006
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6897
- relation_f1: 0.4571
- llm_element_status: success
- llm_node_f1: 0.9697
- llm_relation_f1: 0.6341
- missing_nodes:
  - condition judgement
  - shutdown
  - battery soc reaches 80 and dcdc state is 3
- extra_nodes:
  - system startup
  - enter state 110
  - go to state 28
  - shut down
  - move to state 28
  - soc == 80 and dcdc state == 3?
- missing_relations:
  - enter power-up mode -> condition judgement
  - condition judgement -> remote mode is enabled [case remote mode is enabled]
  - switch to state 28 -> remote mode is disabled
  - condition judgement -> pet mode request is received [case pet mode request is received]
  - switch to state 28 -> pet mode request handling is finished
  - condition judgement -> battery soc is 20 [case battery soc is 20]
  - switch to state 28 -> battery soc reaches 80 and dcdc state is 3
  - battery soc reaches 80 and dcdc state is 3 -> shutdown [yes]
- input_excerpt:
  After the system starts up: If slow charging is active, go into power-up mode. Then: 1.  If remote mode is enabled, enter state 110. Then, if slow charging becomes inactive, go to state 28. Finally, if remote mode is disabled, shut down and end. 2.  If a pet mode request comes in, switch to state 110. Then, if slow charging is inactive, move to state 28. Once the pet mode request is handled, shut down and end. 3.  If the battery SOC is 20, enter state 110. Then, if slow charging is inactive, switch to state 28. If the SOC later reaches 80 and the DCDC state is 3, shut down and end.
- generated_excerpt:
  @startuml start :System Startup; if (Slow charging active?) then (Yes)   :Enter power-up mode;   partition "Remote Mode Path" {     if (Remote mode enabled?) then (Yes)       :Enter state 110;       if (Slow charging inactive?) then (Yes)         :Go to state 28;       endif       if (Remote mode disabled?) then (Yes)         :Shut down;         end       endif     endif   }   partition "Pet Mode Path" {     if (Pet mode request received?) then (Yes)       :Switch to state 110;       if (Slow charging inactive?) then (Yes)         :Move to state 28;       endif       :Pet mode request handled;       :Shut down;       end     endif   }   partition "Battery SOC Path" {     if (Battery SOC == 2

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
