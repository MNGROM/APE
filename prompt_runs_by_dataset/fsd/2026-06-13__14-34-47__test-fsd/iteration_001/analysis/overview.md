# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2057
- node_recall: 0.1952
- node_f1: 0.1965
- relation_precision: 0.1372
- relation_recall: 0.1317
- relation_f1: 0.1332
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

## Representative Failure Cases
### lmc-0055
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - dcm321 * dcm321t
  - =identity (3x3
  - allowed
  - not allowed
- extra_nodes:
  - get rotation matrix dcm321
  - calculate transpose of dcm321 (dcm321t)
  - multiply dcm321 by dcm321t
  - is the result the identity (3x3
  - requirement satisfied
  - requirement violated
- missing_relations:
  - dcm321 * dcm321t -> =identity (3x3
  - =identity (3x3 -> allowed
  - allowed -> not allowed
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml start :Get Rotation Matrix DCM321; :Calculate Transpose of DCM321 (DCM321T); :Multiply DCM321 by DCM321T; if (Is the result the Identity (3x3) Matrix?) then (Yes)   :Requirement Satisfied; else (No)   :Requirement Violated; endif stop @enduml
### us-0098
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - edit profile
  - upload new information
- extra_nodes:
  - navigate to profile page
  - view current profile information
  - submit updated profile
  - validate input
  - valid input?
  - save updated profile
  - display success message
- missing_relations:
  - edit profile -> upload new information
- input_excerpt:
  As an Owner, I want to edit my profile, so that that it is updated with new information.
- generated_excerpt:
  @startuml start :Navigate to Profile Page; :View Current Profile Information; repeat :Edit Profile Information; :Submit Updated Profile; :Validate Input; repeat while (Valid Input?) is (No) ->Yes; :Save Updated Profile; :Display Success Message; stop @enduml
### lmc-0048
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - requirement when heading hold mode becomes active
  - pilot uses cockpit control
  - set heading hold reference
- extra_nodes:
  - heading hold mode becomes the active mode
  - set heading hold reference via cockpit control
- missing_relations:
  - requirement when heading hold mode becomes active -> pilot uses cockpit control
  - pilot uses cockpit control -> set heading hold reference
- input_excerpt:
  Requirement	When heading hold mode becomes the active mode the heading hold reference shall be set by the pilot via a cockpit control.
- generated_excerpt:
  @startuml |System| start :Heading hold mode becomes the active mode; |Pilot| :Set heading hold reference via cockpit control; stop @enduml
### us-0092
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - get full details of data package schema changes
  - adjust scripts to handle
- extra_nodes:
  - detect data package schema change
  - request full schema change details
  - retrieve schema change log
  - generate schema diff
  - display full schema change details
  - review schema change details
  - analyze impact on existing scripts
  - adjust scripts to handle schema changes
- missing_relations:
  - get full details of data package schema changes -> adjust scripts to handle
- input_excerpt:
  As a Consumer, I want to know full details of how the data package schema has changed, so that that I can adjust my scripts to handle it.
- generated_excerpt:
  @startuml start :Detect data package schema change; :Request full schema change details;  partition "System" {   :Retrieve schema change log;   :Generate schema diff;   :Display full schema change details; }  partition "Consumer" {   :Review schema change details;   :Analyze impact on existing scripts;   :Adjust scripts to handle schema changes;   :Test adjusted scripts; } stop @enduml
### pure-0078
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1538
- relation_f1: 0.0000
- missing_nodes:
  - selects period within displayed period
  - operation
  - expand
  - contract
  - new viewing period becomes twice
  - encloses selected period
- extra_nodes:
  - user selects a period of time within the displayed viewing period over which to expand or contract in time
  - expand or contract?
  - tool expands the selected period
  - tool contracts the selected period
  - the new viewing period becomes twice as long as the selected period and encloses it
- missing_relations:
  - selects period within displayed period -> operation
  - operation -> expand
  - expand -> selected period becomes new viewing period
  - selected period becomes new viewing period -> contract
  - contract -> new viewing period becomes twice
  - new viewing period becomes twice -> encloses selected period
- input_excerpt:
  1. The user selects a period of time within the displayed viewing period over which to expand or contract in time. 2. The tool expands or contracts the selected period. If expanding, the selected period becomes the new viewing period. If contracting, the new viewing period becomes twice as long as the selected period and encloses it.
- generated_excerpt:
  @startuml start :User selects a period of time within the displayed viewing period over which to expand or contract in time; if (Expand or Contract?) then (Expand)   :Tool expands the selected period;   :The selected period becomes the new viewing period; else (Contract)   :Tool contracts the selected period;   :The new viewing period becomes twice as long as the selected period and encloses it; endif stop @enduml
### bp-0028
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1818
- relation_f1: 0.0000
- missing_nodes:
  - log in
  - more information?
  - see creating a new job
- extra_nodes:
  - log into the lifecycle manager tool
  - select output to a biar file from destination system drop-down list
  - click create
  - click add objects to add infoobjects
  - manage dependencies (optional)
  - click promote
- missing_relations:
  - log in -> create a new job
  - create a new job -> more information?
  - more information? -> see creating a new job
- input_excerpt:
  28.	Exporting a Job to a BIAR File1. Log into the LifeCycle Manager tool, and create a new job. For more information on creating a new job, see Creating a New Job on page 372. In the Destination System drop-down list, select Output to a BIAR file option and click Create.3. Click Add objects to add infoobjects to the job. You can use the Manage Dependencies option to manage the dependencies of the selected job.4. Click Promote.The "Promote - Job Name" screen appears.5. Click Export.The BIAR file is created. You can save a BIAR file to a File System or an FTP location.6. In the "Promote - Job Name"screen, click Biar File Destination. Biar File Destination pane appears.7. Select either File Sys
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Select "Output to a BIAR file" from Destination System drop-down list; :Click Create; :Click Add objects to add infoobjects; :Manage Dependencies (optional); :Click Promote; note right: "Promote - Job Name" screen appears :Click Export; note right: BIAR file is created :Click Biar File Destination; note right: Biar File Destination pane appears if (Select Destination?) then (File System)   :Select File System;   :Click Export;   :BIAR file is exported to a file system; else (FTP)   :Select FTP;   :Enter details\n(host, port, username,\npassword, directory, filename);   :Click Export;   :BIAR file is exported to an FTP 
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2105
- relation_f1: 0.0556
- missing_nodes:
  - click alternative mouse button
  - open context menu
  - open context menu
  - internet channel is the greatest
  - analyze differences for months?
  - open dropdown box calendar year/month
  - open dropdown box calendar year/month
  - select 08.2007
- extra_nodes:
  - sorting method?
  - right-click on revenue field
  - observe greatest revenue is obtained with internet
  - select 08.2007 in calendar year/month dropdown
  - select 07.2007 in calendar year/month dropdown
  - observe internet revenue increased greatly
  - filter data back to september by selecting 09.2007 in dropdown
  - right-click on internet subtotal (567.308 05)
- missing_relations:
  - sort revenue data -> click arrows in revenue eld?
  - sort increasing or decreasing -> click alternative mouse button
  - click alternative mouse button -> open context menu
  - open context menu -> choose sort increasing or sort decreasing
  - choose sort increasing or sort decreasing -> internet channel is the greatest
  - internet channel is the greatest -> analyze differences for months?
  - analyze differences for months? -> open dropdown box calendar year/month
  - open dropdown box calendar year/month -> select 08.2007
- input_excerpt:
  10.	Analyzing Data in the Web Application1. Since you are interested in the revenue, you want to sort the revenue data.2. Click on the arrows in the Revenue eld to sort the revenue data in increasing or decreasing order.3. You can also sort the revenue by clicking the alternative mouse button on Revenue and choosing Sort Sort Increasing or Sort Decreasing in the context menu. You see that the greatest revenue is obtained with the distribution channel Internet.4. To see the differences in the revenue data for the months July, August and September, select rst 08.2007 and then 07.2007 in the dropdown box Calendar Year/Month. You see that the revenue data for the distribution channel Internet in
- generated_excerpt:
  @startuml start :Sort revenue data; if (Sorting method?) then (via Arrows)   :Click arrows in Revenue field;   :Select Sort Increasing or Sort Decreasing; else (via Context Menu)   :Right-click on Revenue field;   :Choose Sort > Sort Increasing or Sort Decreasing; endif :Observe greatest revenue is obtained with Internet; :Select 08.2007 in Calendar Year/Month dropdown; :Select 07.2007 in Calendar Year/Month dropdown; :Observe Internet revenue increased greatly; :Filter data back to September\nby selecting 09.2007 in dropdown; :Right-click on Internet subtotal (567.308,05); :Choose Documents > Create New Comment\nin context menu; :Enter name and description for the document; :Enter text and 
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3750
- relation_f1: 0.4348
- missing_nodes:
  - switch to state 93
  - switch to state 95
  - power-up is ready and vehicle charging/discharging mode is 2
  - switch to state 105
  - switch to state 105
  - switch to state 105
  - switch to state 105
  - condition judgement
- extra_nodes:
  - system starts up
  - transition to state 93
  - move to state 95
  - power-up readiness confirmed and vehicle s charging/discharging mode == 2?
  - proceed to state 105
  - go to state 105
  - slow charging becomes inactive?
  - remote mode deactivated?
- missing_relations:
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - power-up is ready and vehicle charging/discharging mode is 2 -> switch to state 105
  - switch to state 105 -> condition judgement
  - condition judgement -> in remote mode
  - switch to state 28 -> remote mode is closed
  - remote mode is closed -> shutdown
  - shutdown -> pet mode request is received
  - pet mode request is received -> switch to state 105
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System starts up;  partition "Initial Conditions" {   if (Slow charging active AND\nFront MCU high-voltage detection flag == 0?) then (yes)     :Transition to state 93;   elseif (Charging/discharging power-up active AND\nFront MCU high-voltage detection flag == 1?) then (yes)     :Move to state 95;   elseif (Power-up readiness confirmed AND\nVehicle's charging/discharging mode == 2?) then (yes)     :Proceed to state 105;   else (no)   endif }  partition "Handle Cases" {   fork     :In remote mode;     :Go to state 105;     if (Slow charging becomes inactive?) then (yes)       :Shift to state 28;     else (no)       if (Remote mode deactivated?) then (yes)         :Initiate s

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
