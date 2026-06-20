# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.1700
- node_recall: 0.1661
- node_f1: 0.1571
- relation_precision: 0.1016
- relation_recall: 0.1003
- relation_f1: 0.1000
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
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - sort revenue data
  - click arrows in revenue eld?
  - sort increasing or decreasing
  - click alternative mouse button
  - open context menu
  - open context menu
  - choose sort increasing or sort decreasing
  - internet channel is the greatest
- extra_nodes:
  - click arrows in revenue field to sort data
  - sort revenue in increasing or decreasing order
- missing_relations:
  - sort revenue data -> click arrows in revenue eld?
  - click arrows in revenue eld? -> sort increasing or decreasing
  - sort increasing or decreasing -> click alternative mouse button
  - click alternative mouse button -> open context menu
  - open context menu -> choose sort increasing or sort decreasing
  - choose sort increasing or sort decreasing -> internet channel is the greatest
  - internet channel is the greatest -> analyze differences for months?
  - analyze differences for months? -> open dropdown box calendar year/month
- input_excerpt:
  10.	Analyzing Data in the Web Application1. Since you are interested in the revenue, you want to sort the revenue data.2. Click on the arrows in the Revenue eld to sort the revenue data in increasing or decreasing order.3. You can also sort the revenue by clicking the alternative mouse button on Revenue and choosing Sort Sort Increasing or Sort Decreasing in the context menu. You see that the greatest revenue is obtained with the distribution channel Internet.4. To see the differences in the revenue data for the months July, August and September, select rst 08.2007 and then 07.2007 in the dropdown box Calendar Year/Month. You see that the revenue data for the distribution channel Internet in
- generated_excerpt:
  @startuml start :Click arrows in Revenue field to sort data; :Sort revenue in increasing or decreasing order; note right: Alternative: Right-click Revenue\nand choose Sort Increasing/Decreasing :Observe greatest revenue is from\nInternet distribution channel; :Select 08.2007 in Calendar Year/Month dropdown; :Select 07.2007 in Calendar Year/Month dropdown; :Observe Internet revenue increased greatly\n(Marketing campaign successful); :Filter data back to September\n(Select 09.2007 in dropdown); :Right-click subtotal of Internet channel (567.308,05); :Choose Documents > Create New Comment\nfrom context menu; :Enter name and description for the document; :Enter text and choose Save; stop @enduml
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
  - initialize rotation matrix dcm321
  - compute transpose of rotation matrix dcm321t
  - multiply dcm321 by dcm321t (dcm321 * dcm321t)
  - result == identity (3x3
  - validation passed
  - validation failed
- missing_relations:
  - dcm321 * dcm321t -> =identity (3x3
  - =identity (3x3 -> allowed
  - allowed -> not allowed
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml start :Initialize Rotation Matrix DCM321; :Compute Transpose of Rotation Matrix DCM321T; :Multiply DCM321 by DCM321T (DCM321 * DCM321T); if (Result == Identity (3x3) Matrix?) then (Yes)   :Validation Passed; else (No)   :Validation Failed; endif stop @enduml
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
  - system validates input data
  - valid input?
  - system updates profile information
  - system displays success message
- missing_relations:
  - edit profile -> upload new information
- input_excerpt:
  As an Owner, I want to edit my profile, so that that it is updated with new information.
- generated_excerpt:
  @startuml skinparam style strictuml  title Edit Profile  start :Owner selects "Edit Profile"; :System displays current profile information; :Owner modifies profile fields; :Owner clicks "Save"; :System validates input data;  if (Valid input?) then (Yes)   :System updates profile information;   :System displays success message; else (No)   :System displays validation error message;   :Owner corrects input data;   stop   note right: Returns to edit form endif  stop @enduml
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
  - retrieve data package schema history
  - identify schema changes (added modified removed fields)
  - display full schema change details to consumer
  - consumer reviews changes
  - consumer adjusts scripts to handle schema changes
- missing_relations:
  - get full details of data package schema changes -> adjust scripts to handle
- input_excerpt:
  As a Consumer, I want to know full details of how the data package schema has changed, so that that I can adjust my scripts to handle it.
- generated_excerpt:
  @startuml skinparam style strictuml  title Activity: View Data Package Schema Change Details  start  :Consumer requests schema change details;  :Retrieve data package schema history;  :Identify schema changes (added, modified, removed fields);  :Display full schema change details to Consumer;  :Consumer reviews changes;  :Consumer adjusts scripts to handle schema changes;  stop  @enduml
### bp-0028
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0833
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
  - promote - job name screen appears
  - click export
- missing_relations:
  - log in -> create a new job
  - create a new job -> more information?
  - more information? -> see creating a new job
- input_excerpt:
  28.	Exporting a Job to a BIAR File1. Log into the LifeCycle Manager tool, and create a new job. For more information on creating a new job, see Creating a New Job on page 372. In the Destination System drop-down list, select Output to a BIAR file option and click Create.3. Click Add objects to add infoobjects to the job. You can use the Manage Dependencies option to manage the dependencies of the selected job.4. Click Promote.The "Promote - Job Name" screen appears.5. Click Export.The BIAR file is created. You can save a BIAR file to a File System or an FTP location.6. In the "Promote - Job Name"screen, click Biar File Destination. Biar File Destination pane appears.7. Select either File Sys
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :In the Destination System drop-down list,\nselect "Output to a BIAR file" option; :Click Create; :Click Add objects to add infoobjects to the job; :Manage Dependencies (optional); :Click Promote; :"Promote - Job Name" screen appears; :Click Export; :BIAR file is created; :Click Biar File Destination; :Biar File Destination pane appears; if (Select Destination?) then (File System)   :Select File System;   :Click Export;   :BIAR file is exported to a file system; else (FTP)   :Select FTP;   :Enter details (host, port, username,\npassword, directory, filename);   :Click Export;   :BIAR file is exported to an FTP location;
### pure-0078
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1818
- relation_f1: 0.0000
- missing_nodes:
  - selects period within displayed period
  - operation
  - expand
  - contract
  - new viewing period becomes twice
  - encloses selected period
- extra_nodes:
  - the user selects a period of time within the displayed viewing period over which to expand or contract in time
  - expand or contract?
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
  @startuml start :The user selects a period of time within the displayed viewing period over which to expand or contract in time; if (Expand or Contract?) then (Expand)   :The selected period becomes the new viewing period; else (Contract)   :The new viewing period becomes twice as long as the selected period and encloses it; endif stop @enduml
### pure-0046
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2222
- relation_f1: 0.0588
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
  @startuml skinparam style strictuml  start  :User accesses the main inventory screen;  :System displays the Edit Details button;  :User clicks the Edit Details button;  :System displays the Edit Details screen (displays all existing item details, detail x department, and category assignments);  if (Filter view by detail status?) then (Yes)   :User filters view by detail status   (active, inactive, all); else (No) endif  repeat   :User edits details;    fork     :User changes detail x department     or category assignments;   fork again     :User changes detail data;   fork again     :User changes detail active     x inactive status;   fork again     :User creates new detail;   end fork    :S

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
