# Prompt Evaluation Analysis

## Summary
- count: 220
- syntax_pass_rate: 0.9318
- infrastructure_error_rate: 0.0000
- node_precision: 0.0362
- node_recall: 0.1424
- node_f1: 0.0537
- relation_precision: 0.0049
- relation_recall: 0.0182
- relation_f1: 0.0068
- plantuml_compilation_pass_rate: 0.9318
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- extra_activity: 220
- extra_or_wrong_relation: 220
- missing_or_wrong_relation: 218
- missing_activity: 209
- syntax_error: 15

## Representative Failure Cases
### us-0014
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - manage hearing calendars
  - track hearing-related activities and due dates
- extra_nodes:
  - staff member logs into the system
  - access hearing calendar module
  - view hearing calendar
  - create new hearing event
  - edit existing hearing event
  - delete hearing event
  - selected action?
  - select date range / filter
- missing_relations:
  - manage hearing calendars -> track hearing-related activities and due dates
- input_excerpt:
  As a Staff member, I want to Manage Hearing Calendars, so that I can track hearing-related activities and due dates.
- generated_excerpt:
  @startuml left to right direction  title Manage Hearing Calendars  start  :Staff member logs into the system;  :Access Hearing Calendar Module;  fork   :View Hearing Calendar; fork again   :Create New Hearing Event; fork again   :Edit Existing Hearing Event; fork again   :Delete Hearing Event; end fork  switch (Selected Action?) case View   :Select Date Range / Filter;   :Display Hearing Calendar;   :Review Hearing Activities and Due Dates; case Create   :Input Hearing Details (Title, Type, Participants);   :Set Hearing Date and Due Dates;   :Validate Inputs;   if (Valid Inputs?) then (Yes)     :Save Hearing Event;     :Confirm Creation;   else (No)     :Display Validation Errors;     stop  
### us-0017
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - assign inspections
  - receive work
- extra_nodes:
  - view pending inspections
  - select inspection to assign
  - review inspection details
  - view available inspectors
  - is an appropriate inspector available?
  - select inspector
  - assign inspection to inspector
  - notify inspector of new assignment
- missing_relations:
  - assign inspections -> receive work
- input_excerpt:
  As an Inspection Staff Supervisor, I want to Assign Inspections, so that I can make sure the appropriate Inspector receives the work.
- generated_excerpt:
  @startuml left to right direction  skinparam ActivityBackgroundColor #E8F5E9 skinparam ActivityBorderColor #2E7D32  start  :View Pending Inspections;  :Select Inspection to Assign;  :Review Inspection Details;  :View Available Inspectors;  if (Is an appropriate Inspector available?) then (Yes)   :Select Inspector;   :Assign Inspection to Inspector;   :Notify Inspector of New Assignment;   :Update Inspection Status to Assigned; else (No)   :Flag Inspection for Reassignment;   :Notify Supervisor of Unassigned Inspection; endif  stop  @enduml
### us-0018
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - issue a development-related permit
  - grant request to begin work
- extra_nodes:
  - development staff member logs into system
  - select issue development permit
  - retrieve submitted permit application
  - is application complete and compliant?
  - return application to applicant for corrections
  - review development request details
  - approve development permit?
  - deny permit request
- missing_relations:
  - issue a development-related permit -> grant request to begin work
- input_excerpt:
  As a Development Staff member, I want to Issue a Development-related Permit, so that I can grant the request to the Applicant to begin work
- generated_excerpt:
  @startuml left to right direction  skinparam activityBackgroundColor #LightBlue skinparam activityDiamondBackgroundColor #LightYellow  start  :Development Staff member logs into system;  :Select "Issue Development Permit";  :Retrieve submitted permit application;  if (Is application complete and compliant?) then (No)   :Return application to Applicant for corrections;   stop else (Yes)   :Review development request details;      if (Approve development permit?) then (No)     :Deny permit request;     :Notify Applicant of denial;     stop   else (Yes)     :Generate Development Permit;     :Record permit issuance in system;     :Grant request to Applicant to begin work;     :Notify Applicant o
### us-0091
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - update previously downloaded data package
  - work with most recent data
- extra_nodes:
  - data analyst selects previously downloaded data package
  - request latest data package version from server
  - new version available?
  - download updated data package
  - replace old data package with new version
  - notify data analyst update successful
  - notify data analyst data is already up-to-date
- missing_relations:
  - update previously downloaded data package -> work with most recent data
- input_excerpt:
  As a Data Analyst, I want to update previously downloaded data package, so that that I can work with the most recent data.
- generated_excerpt:
  @startuml left to right direction  skinparam activityBackgroundColor #LightBlue skinparam activityDiamondBackgroundColor #LightYellow  start :Data Analyst selects previously downloaded data package; :Request latest data package version from server; if (New version available?) then (Yes)   :Download updated data package;   :Replace old data package with new version;   :Notify Data Analyst: Update successful; else (No)   :Notify Data Analyst: Data is already up-to-date; endif stop  @enduml
### us-0124
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - enter metadata
  - describe an experiment protocol
  - cerate file
- extra_nodes:
  - open application / system
  - select new experiment protocol
  - input experiment title
  - input experiment description
  - select experiment category/tags
  - input researcher details
  - review entered metadata
  - is metadata complete and valid?
- missing_relations:
  - enter metadata -> describe an experiment protocol
  - describe an experiment protocol -> cerate file
- input_excerpt:
  As a user, I want to enter metadata / describe an experiment protocol before a file is even created.
- generated_excerpt:
  @startuml skinparam style strictuml  title Enter Metadata / Describe Experiment Protocol  start  :Open Application / System;  :Select "New Experiment Protocol";  :Enter Experiment Metadata {   :Input Experiment Title;   :Input Experiment Description;   :Select Experiment Category/Tags;   :Input Researcher Details; }  :Review Entered Metadata;  if (Is Metadata Complete and Valid?) then (Yes)   :Save Experiment Protocol (No File Created Yet);   :System confirms Protocol saved;   stop else (No)   :Edit Metadata;   :Return to Review; endif  @enduml
### us-0140
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - get an alfred device
  - adapt for user had hearing trouble
- extra_nodes:
  - olderperson uses alfred device
- missing_relations:
  - get an alfred device -> adapt for user had hearing trouble
- input_excerpt:
  As an OlderPerson, I want to have an ALFRED device that can be easily adapted for user that have hearing trouble.
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #E8F5E9 skinparam ActivityBorderColor #2E7D32 skinparam NoteBorderColor #FFA000 skinparam NoteBackgroundColor #FFF8E1  title ALFRED Device Adaptation for Hearing Trouble  start  :OlderPerson uses ALFRED device; note right: User may have\nhearing difficulties  switch (Detect Audio Output Event) case (Notification / Alert)   :Trigger Visual Alert\n(Flashing Screen / LED);   :Trigger Haptic Feedback\n(Vibration); case (Voice Command / Audio Feedback)   :Display Text Transcript\non Screen;   :Provide Haptic Confirmation; case (Incoming Call)   :Flash Screen;   :Vibrate Device;   :Enable Real-Time\nText Subtitles; endswitch  :U
### us-0172
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - link datasets with the project dmp
  - demonstrate compliance with dmp
  - link whole project workflow
- extra_nodes:
  - depositor logs into the system
  - navigate to project workspace
  - select a dataset to link
  - choose to link dataset with dmp
  - select the relevant project dmp from available list
  - confirm the linkage
  - linkage valid and dmp exists?
  - system associates dataset with the selected dmp
- missing_relations:
  - link datasets with the project dmp -> demonstrate compliance with dmp
  - demonstrate compliance with dmp -> link whole project workflow
- input_excerpt:
  As a depositor, I want to link datasets with the project DMP, so that compliance with DMP can be demonstrated and whole project workflow is linked together.
- generated_excerpt:
  @startuml skinparam style strictuml  title Link Dataset with Project DMP  start  :Depositor logs into the system;  :Navigate to project workspace;  :Select a dataset to link;  :Choose to link dataset with DMP;  :Select the relevant Project DMP from available list;  :Confirm the linkage;  if (Linkage valid and DMP exists?) then (yes)   :System associates dataset with the selected DMP;   :Update project workflow to reflect linkage;   :Display success message: "Dataset successfully linked to DMP";   note right     Demonstrates DMP compliance     and links project workflow   end note; else (no)   :Display error message: "Invalid linkage or DMP not found";   :Prompt Depositor to correct selection
### us-0192
- dataset: us
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - upload inventories
  - get time requesting material
- extra_nodes:
  - archivist initiates inventory upload
  - select inventory file
  - is file format valid?
  - display file format error
  - upload inventory file to system
  - process and validate inventory data
  - is inventory data valid?
  - display data validation error
- missing_relations:
  - upload inventories -> get time requesting material
- input_excerpt:
  As an archivist, I want to upload inventories, so that our donor representatives have an easier time requesting their material.
- generated_excerpt:
  @startuml left to right direction  skinparam activityBorderColor #333333 skinparam activityBackgroundColor #F9F9F9 skinparam activityDiamondBackgroundColor #E8E8E8  start  :Archivist initiates inventory upload;  :Select inventory file;  if (Is file format valid?) then (No)   :Display file format error;   stop else (Yes) endif  :Upload inventory file to system;  :Process and validate inventory data;  if (Is inventory data valid?) then (No)   :Display data validation error;   stop else (Yes) endif  :Save inventory to database;  :Update material catalog;  :Notify donor representatives of new inventory;  :Display upload success message;  stop  @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
