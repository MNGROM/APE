# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 0.9500
- infrastructure_error_rate: 0.0000
- node_precision: 0.2348
- node_recall: 0.2760
- node_f1: 0.2538
- relation_precision: 0.2351
- relation_recall: 0.2297
- relation_f1: 0.2323
- plantuml_compilation_pass_rate: 0.9500
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7265
- llm_node_recall: 0.8282
- llm_node_f1: 0.7178
- llm_relation_precision: 0.5811
- llm_relation_recall: 0.6511
- llm_relation_f1: 0.5364

## Failure Types
- missing_activity: 20
- extra_activity: 20
- missing_or_wrong_relation: 19
- extra_or_wrong_relation: 19
- wrong_parallel: 5
- wrong_loop: 2
- syntax_error: 1

## Representative Failure Cases
### pure-0012
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4186
- relation_f1: 0.2353
- llm_element_status: success
- llm_node_f1: 0.7692
- llm_relation_f1: 0.5758
- missing_nodes:
  - initiate call to controller
  - primary controller
  - secondary controller
  - power supply controller
  - unique identity?
  - use external systems to obtain
  - obtain appropriate destination
  - functional identity be displayed
- extra_nodes:
  - radio provides unique identity for controller type?
  - obtain identity using external systems (per 11.4.7)
  - display functional identity to controller
  - display functional identity to driver
  - identity contains alphanumeric description?
  - display alphanumeric description to driver
- missing_relations:
  - initiate call to controller -> primary controller [fork]
  - initiate call to controller -> secondary controller [fork]
  - initiate call to controller -> power supply controller [fork]
  - primary controller -> unique identity?
  - secondary controller -> unique identity?
  - power supply controller -> unique identity?
  - unique identity? -> use external systems to obtain [no]
  - use external systems to obtain -> obtain appropriate destination
- input_excerpt:
  5.2.2.1 It shall be possible for the driver to initiate a call to any of the following types of controller with a minimum of driver action being required (eg a single keystroke): (M) primary controller; secondary controller; power supply controller. 5.2.2.2 If the radio system cannot give a unique identity for a given type of controller, the identity could be obtained using external systems as defined in 11.4.7. (I) 5.2.2.3 Once an appropriate destination has been obtained, the radio shall attempt to establish a call to this destination. The functional identity shall be displayed to the controller. (M) 5.2.2.3i The functional identity includes the following: − the train number, if available;
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Driver initiates call (single keystroke) to Primary, Secondary, or Power Supply Controller;  if (Radio provides unique identity for controller type?) then (No)   :Obtain identity using external systems (per 11.4.7); else (Yes) endif  :Determine functional identity of the caller:   if (Train number available?) then (Yes)     :Use Train number;   else (No)     if (Engine number available?) then (Yes)       :Use Engine number;     else (No)       :Use Coach number of leading cab;     endif   endif;  :Display functional identity to controller;  :Attempt to establish call to destination;  :Provide audible and visual indication to driver that call is pr
### us-0098
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5333
- llm_relation_f1: 0.2857
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
  - system updates profile in database
  - system displays success message
- missing_relations:
  - edit profile -> upload new information
- input_excerpt:
  As an Owner, I want to edit my profile, so that that it is updated with new information.
- generated_excerpt:
  @startuml skinparam style strictuml  start :Owner selects "Edit Profile"; :System displays current profile information; :Owner modifies profile fields; :Owner clicks "Save"; :System validates input; if (Valid input?) then (yes)   :System updates profile in database;   :System displays success message; else (no)   :System displays error message;   stop endif stop @enduml
### us-0092
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5000
- llm_relation_f1: 0.2857
- missing_nodes:
  - get full details of data package schema changes
  - adjust scripts to handle
- extra_nodes:
  - consumer requests schema change details
  - system retrieves data package schema history
  - system identifies recent schema changes
  - are schema changes clear?
  - consumer reviews change details
  - consumer adjusts scripts to handle new schema
  - consumer requests further clarification
  - system provides additional schema documentation
- missing_relations:
  - get full details of data package schema changes -> adjust scripts to handle
- input_excerpt:
  As a Consumer, I want to know full details of how the data package schema has changed, so that that I can adjust my scripts to handle it.
- generated_excerpt:
  @startuml skinparam style strictuml  title Consumer: View Data Package Schema Change Details  start  :Consumer requests schema change details;  :System retrieves data package schema history;  :System identifies recent schema changes;  :System presents full details of schema changes (differences, added/removed fields, type changes);  if (Are schema changes clear?) then (Yes)   :Consumer reviews change details;   :Consumer adjusts scripts to handle new schema;   stop else (No)   :Consumer requests further clarification;   :System provides additional schema documentation;   stop endif  @enduml
### bp-0002
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7368
- llm_relation_f1: 0.6111
- missing_nodes:
  - user authorizations are sufficient?
  - log in
  - choose modeling data warehousing workbench modeling
  - data warehousing workbench is started
  - choose info objects
  - info object tree is displayed
  - open root node context menu
  - choose create info area
- extra_nodes:
  - log onto the bi system with a user that has sufficient authorizations
  - start the data warehousing workbench in the sap menu (modeling -> data warehousing workbench modeling)
  - under modeling choose info objects (the info object tree is displayed)
  - from the context menu at the root node info objects choose create info area
  - enter a technical name and a description for the info area (the info area is displayed in the info object tree)
- missing_relations:
  - user authorizations are sufficient? -> log in [yes]
  - log in -> choose modeling data warehousing workbench modeling
  - choose modeling data warehousing workbench modeling -> data warehousing workbench is started
  - data warehousing workbench is started -> choose info objects
  - choose info objects -> info object tree is displayed
  - info object tree is displayed -> open root node context menu
  - open root node context menu -> choose create info area
  - choose create info area -> enter a technical name [fork]
- input_excerpt:
  2.	Log onto the BI system1.	Log onto the BI system with a user that has sufficient authorizations for executing the scenario.2.	Start the Data Warehousing Workbench in the SAP menu by choosing Modeling Data Warehousing Workbench: Modeling.3.	Under Modeling, choose Info  Objects. The Info  Object tree is displayed.4.	From the context menu at the root node Info Objects of the Info Object tree, choose Create Info Area.5.	On the next screen, enter a technical name and a description for the Info Area. The Info Area is displayed in the Info Object tree.6.	It is used to group your Info Objects.7.	In the context menu of the Info Area, choose Create Info Object Catalog.8.	On the next screen, enter a 
- generated_excerpt:
  @startuml start :Log onto the BI system with a user that has sufficient authorizations; :Start the Data Warehousing Workbench in the SAP menu\n(Modeling -> Data Warehousing Workbench: Modeling); :Under Modeling, choose Info Objects\n(The Info Object tree is displayed); :From the context menu at the root node Info Objects,\nchoose Create Info Area; :Enter a technical name and a description for the Info Area\n(The Info Area is displayed in the Info Object tree); note right: It is used to group your Info Objects :In the context menu of the Info Area,\nchoose Create Info Object Catalog; :Enter a technical name and description,\nand select Key Figure as the Info Object Type; :Choose Create; :Acti
### us-0208
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3333
- llm_relation_f1: 0.1111
- missing_nodes:
  - associate a researcherid or orcid with a submission
  - avoid ambiguity between my work and others
- extra_nodes:
  - faculty member initiates submission
  - enter submission details
  - enter name in contributor field
  - disambiguation needed?
  - system prompts for unique identifier
  - enter researcherid or orcid
  - system validates identifier format
  - identifier valid?
- missing_relations:
  - associate a researcherid or orcid with a submission -> avoid ambiguity between my work and others
- input_excerpt:
  As a Cornell faculty member, I want to associate a researcherID or ORCID with a submission, so that there is no ambiguity between my work and someone else with the same name.
- generated_excerpt:
  @startuml skinparam style strictuml  title Associate ResearcherID or ORCID with Submission  start  :Faculty member initiates submission;  :Enter submission details;  :Enter name in contributor field;  if (Disambiguation needed?) then (Yes)   :System prompts for unique identifier;   :Enter ResearcherID or ORCID;   :System validates identifier format;   if (Identifier valid?) then (Yes)     :Associate identifier with contributor;   else (No)     :Display validation error;     stop   endif else (No) endif  :Complete and submit;  :System links submission to unique identifier;  stop @enduml
### lmc-0048
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.8889
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
### bp-0006
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0571
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7179
- llm_relation_f1: 0.5714
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
### bp-0028
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0833
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8846
- llm_relation_f1: 0.5660
- missing_nodes:
  - log in
  - more information?
  - see creating a new job
- extra_nodes:
  - log into the lifecycle manager tool
  - select output to a biar file from the destination system drop-down list
  - click create
  - click add objects to add infoobjects to the job
  - manage dependencies (optional)
  - click promote
  - promote - job name screen appears
  - click export
- missing_relations:
  - log in -> create a new job
  - create a new job -> more information?
  - more information? -> see creating a new job [yes]
- input_excerpt:
  28.	Exporting a Job to a BIAR File1. Log into the LifeCycle Manager tool, and create a new job. For more information on creating a new job, see Creating a New Job on page 372. In the Destination System drop-down list, select Output to a BIAR file option and click Create.3. Click Add objects to add infoobjects to the job. You can use the Manage Dependencies option to manage the dependencies of the selected job.4. Click Promote.The "Promote - Job Name" screen appears.5. Click Export.The BIAR file is created. You can save a BIAR file to a File System or an FTP location.6. In the "Promote - Job Name"screen, click Biar File Destination. Biar File Destination pane appears.7. Select either File Sys
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Select "Output to a BIAR file" from the Destination System drop-down list; :Click Create; :Click Add objects to add infoobjects to the job; :Manage Dependencies (optional); :Click Promote; :"Promote - Job Name" screen appears; :Click Export; :The BIAR file is created; :Click Biar File Destination; :Biar File Destination pane appears; switch (Select destination type) case (File System)   :Select File System;   :Click Export;   :The BIAR file is exported to a file system; case (FTP)   :Select FTP;   :Enter details (host, port, username, password, directory, filename);   :Click Export;   :The BIAR file is exported to an F

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
