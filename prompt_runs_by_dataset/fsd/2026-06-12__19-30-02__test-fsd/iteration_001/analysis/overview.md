# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2035
- node_recall: 0.1920
- node_f1: 0.1915
- relation_precision: 0.1096
- relation_recall: 0.1034
- relation_f1: 0.1050
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
  - calculate transpose of rotation matrix (dcm321t)
  - calculate product = dcm321 * dcm321t
  - verify product is identity matrix (3x3)
  - is product == i(3x3
  - requirement satisfied
  - requirement violated
- missing_relations:
  - dcm321 * dcm321t -> =identity (3x3
  - =identity (3x3 -> allowed
  - allowed -> not allowed
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityBorderColor #336699 skinparam NoteBorderColor #336699 skinparam NoteBackgroundColor #FFFFCC  title Rotation Matrix Orthogonality Verification: DCM321 * DCM321T = I(3x3)  start  :Calculate Transpose of Rotation Matrix (DCM321T);  :Calculate Product = DCM321 * DCM321T;  :Verify Product is Identity Matrix (3x3);  if (Is Product == I(3x3)?) then (Yes)   :Requirement Satisfied;   stop else (No)   :Requirement Violated;   stop endif  @enduml
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
  @startuml skinparam style strictuml  start :Owner selects "Edit Profile"; :System displays current profile information; :Owner modifies profile fields; :Owner clicks "Save"; :System validates input; if (Valid input?) then (yes)   :System updates profile information;   :System displays success message; else (no)   :System displays error message;   :Owner corrects input;   stop endif stop @enduml
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
  - pilot sets heading hold reference via cockpit control
- missing_relations:
  - requirement when heading hold mode becomes active -> pilot uses cockpit control
  - pilot uses cockpit control -> set heading hold reference
- input_excerpt:
  Requirement	When heading hold mode becomes the active mode the heading hold reference shall be set by the pilot via a cockpit control.
- generated_excerpt:
  @startuml start :Heading hold mode becomes the active mode; :Pilot sets heading hold reference via cockpit control; stop @enduml
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
  - consumer requests schema change details
  - system retrieves data package schema history
  - system identifies schema changes (e.g. added/removed fields type modifications)
  - system generates detailed change report
  - consumer views schema change details
  - consumer analyzes changes
  - consumer adjusts scripts to handle schema changes
- missing_relations:
  - get full details of data package schema changes -> adjust scripts to handle
- input_excerpt:
  As a Consumer, I want to know full details of how the data package schema has changed, so that that I can adjust my scripts to handle it.
- generated_excerpt:
  @startuml skinparam style strictuml  title Activity: View Data Package Schema Change Details  start  :Consumer requests schema change details;  :System retrieves data package schema history;  :System identifies schema changes (e.g., added/removed fields, type modifications);  :System generates detailed change report;  :Consumer views schema change details;  :Consumer analyzes changes;  :Consumer adjusts scripts to handle schema changes;  stop  @enduml
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
  - the user selects a period of time within the displayed viewing period
  - expand or contract?
  - expand the selected period
  - contract the selected period
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
  @startuml start :The user selects a period of time within the displayed viewing period; if (Expand or Contract?) then (Expand)   :Expand the selected period;   :The selected period becomes the new viewing period; else (Contract)   :Contract the selected period;   :The new viewing period becomes twice as long as the selected period and encloses it; endif stop @enduml
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
  - in the destination system drop-down list select output to a biar file option
  - click create
  - click add objects to add infoobjects to the job
  - manage dependencies (optional)
  - click promote
- missing_relations:
  - log in -> create a new job
  - create a new job -> more information?
  - more information? -> see creating a new job
- input_excerpt:
  28.	Exporting a Job to a BIAR File1. Log into the LifeCycle Manager tool, and create a new job. For more information on creating a new job, see Creating a New Job on page 372. In the Destination System drop-down list, select Output to a BIAR file option and click Create.3. Click Add objects to add infoobjects to the job. You can use the Manage Dependencies option to manage the dependencies of the selected job.4. Click Promote.The "Promote - Job Name" screen appears.5. Click Export.The BIAR file is created. You can save a BIAR file to a File System or an FTP location.6. In the "Promote - Job Name"screen, click Biar File Destination. Biar File Destination pane appears.7. Select either File Sys
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :In the Destination System drop-down list,\nselect Output to a BIAR file option; :Click Create; :Click Add objects to add infoobjects to the job; :Manage Dependencies (optional); :Click Promote; note right: "Promote - Job Name" screen appears :Click Export; note right: BIAR file is created :Click Biar File Destination; note right: Biar File Destination pane appears if (Select Destination?) then (File System)   :Select File System;   :Click Export;   :BIAR file is exported to a file system; else (FTP)   :Select FTP;   :Enter details in host, port, username,\npassword, directory, and filename fields;   :Click Export;   :B
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2703
- relation_f1: 0.1143
- missing_nodes:
  - sort increasing or decreasing
  - click alternative mouse button
  - open context menu
  - open context menu
  - internet channel is the greatest
  - analyze differences for months?
  - open dropdown box calendar year/month
  - open dropdown box calendar year/month
- extra_nodes:
  - right-click revenue field
  - observe greatest revenue is with internet channel
  - select 08.2007 in calendar year/month dropdown
  - select 07.2007 in calendar year/month dropdown
  - observe internet revenue increased greatly
  - filter data back to september (select 09.2007 in dropdown)
  - right-click subtotal of internet channel (567.308 05)
  - choose documents > create new comment from context menu
- missing_relations:
  - click arrows in revenue eld? -> sort increasing or decreasing
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
  @startuml start :Sort revenue data; fork   :Click arrows in Revenue field; fork again   :Right-click Revenue field;   :Choose Sort Increasing or Sort Decreasing from context menu; end fork :Observe greatest revenue is with Internet channel; :Select 08.2007 in Calendar Year/Month dropdown; :Select 07.2007 in Calendar Year/Month dropdown; :Observe Internet revenue increased greatly; :Note right: Marketing campaign was successful :Filter data back to September\n(Select 09.2007 in dropdown); :Right-click subtotal of Internet channel (567.308,05); :Choose Documents > Create New Comment\nfrom context menu; :Enter name and description for the document; :Enter text; :Choose Save; stop @enduml
### pure-0046
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2703
- relation_f1: 0.0571
- missing_nodes:
  - display edit details button
  - display edit details screen
  - all existing item details
  - detail x department assignments
  - detail x category assignments
  - filter view?
  - detail status
  - active
- extra_nodes:
  - system displays the edit details button
  - filter view by detail status?
  - user edits details
  - user changes detail data
  - system updates the item detail information
  - continue editing?
  - user clicks the done button
  - user is taken back to the main inventory screen
- missing_relations:
  - access main inventory screen -> display edit details button
  - display edit details button -> click edit details button
  - click edit details button -> display edit details screen
  - display edit details screen -> all existing item details
  - all existing item details -> detail x department assignments
  - detail x department assignments -> detail x category assignments
  - detail x category assignments -> filter view?
  - filter view? -> detail status
- input_excerpt:
  4. Edit Item Details 4.1. User accesses the main inventory screen 4.2. System displays the Edit Details button 4.3. User clicks the Edit Details button 4.4. System displays the Edit Details screen which displays all existing item details and their detail x department and category assignments 4.5. Optionally, user filters view by detail status (active, inactive, all) 4.6. User edits details 4.6.1. User changes detail x department or category assignments 4.6.2. User changes detail data 4.6.3. User changes detail active x inactive status 4.6.4. User creates new detail 4.6.5. System validates the detail data 4.6.6. System updates the Item detail information 4.7. User clicks the Done button 4.8. 
- generated_excerpt:
  @startuml skinparam style strictuml  start  :User accesses the main inventory screen;  :System displays the Edit Details button;  :User clicks the Edit Details button;  :System displays the Edit Details screen (displays all existing item details, detail x department and category assignments);  if (Filter view by detail status?) then (Yes)   :User filters view by detail status   (active, inactive, all); else (No) endif  repeat   :User edits details;    fork     :User changes detail x department     or category assignments;   fork again     :User changes detail data;   fork again     :User changes detail active x inactive status;   fork again     :User creates new detail;   end fork    :System

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
