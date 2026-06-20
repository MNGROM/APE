# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3886
- node_recall: 0.3903
- node_f1: 0.3774
- relation_precision: 0.2328
- relation_recall: 0.2523
- relation_f1: 0.2298
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
- extra_activity: 20
- missing_activity: 19
- extra_or_wrong_relation: 19
- missing_or_wrong_relation: 18

## Representative Failure Cases
### lmc-0050
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - body vector output vb
  - =dcm321 * vi?
  - allowed
  - not allowed
- extra_nodes:
  - calculate 3x3 rotation matrix output (dcm321)
  - receive input inertial vector (vi)
  - multiply dcm321 by vi
  - assign the 3x1 vector product to body vector output (vb)
- missing_relations:
  - body vector output vb -> =dcm321 * vi?
  - =dcm321 * vi? -> allowed
  - allowed -> not allowed
- input_excerpt:
  2.	The Body Vector Output, Vb, of this Function Shall Equal a 3x1 Vector Product of the 3x3 Rotation Matrix Output, DCM321, times the Input Inertial Vector, Vi.
- generated_excerpt:
  @startuml start :Calculate 3x3 Rotation Matrix Output (DCM321); :Receive Input Inertial Vector (Vi); :Multiply DCM321 by Vi; :Assign the 3x1 vector product to Body Vector Output (Vb); stop @enduml
### bp-0030
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1333
- relation_f1: 0.0000
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
  - log into the lifecycle manager tool
  - in the promotion jobs home page click new job
  - enter the name description and keywords for the job in the appropriate fields
  - in the save job in field browse and select the folder
  - select the source system and the destination system from the drop-down lists
  - system name is not displayed in the drop-down list?
  - click the login to a new cms option
  - a new window is launched
- missing_relations:
  - log in -> go to promotion jobs
  - go to promotion jobs -> click new job
  - click new job -> new job window appears
  - new job window appears -> enter name
  - enter name -> enter description
  - enter description -> enter keywords
  - enter keywords -> go to save job field
  - go to save job field -> browse and select the folder
- input_excerpt:
  30.	Creating a New Job1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriate fields.4. In the Save Job in field, browse and select the folder in which you want to save the job.5. Select the source system and the destination system from the drop-down lists. If the name of the system is not displayed in the drop-down list, click the Login to a new CMS option. A new window is launched. Enter the name of the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name, description, and keywords for the job in the appropriate fields; :In the Save Job in field, browse and select the folder; :Select the source system and the destination system from the drop-down lists; if (System name is not displayed in the drop-down list?) then (yes)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the name of the system along with the user name and password; else (no) endif :Click Create; @enduml
### bp-0015
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1739
- relation_f1: 0.0952
- missing_nodes:
  - go to administration options window
  - click manage syetems
  - list is displayed
  - host names
  - port numbers
  - display names
  - descriptions
  - click add
- extra_nodes:
  - click manage systems in the administration options window
  - the list of host names port numbers display names and descriptions is displayed
  - add the host name port number display name and the description in the appropriate fields
  - click add to add the system
  - the host system is added to the list
- missing_relations:
  - go to administration options window -> click manage syetems
  - click manage syetems -> list is displayed
  - list is displayed -> host names
  - host names -> port numbers
  - port numbers -> display names
  - display names -> descriptions
  - descriptions -> click add
  - add system dialog box appears -> add information
- input_excerpt:
  15.	use the Manage Systems optionTo add a host system, complete the following steps:1. In the "Administration Options" window, click Manage Systems.The list of host names, port numbers, display names, and descriptions isdisplayed.2. Click Add.The "Add System" dialog box appears.3. Add the host name, port number, display name, and the description inthe appropriate fields.4. Click Add to add the system.The host system is added to the list.
- generated_excerpt:
  @startuml start :Click Manage Systems in the "Administration Options" window; :The list of host names, port numbers, display names, and descriptions is displayed; :Click Add; :The "Add System" dialog box appears; :Add the host name, port number, display name, and the description in the appropriate fields; :Click Add to add the system; :The host system is added to the list; @enduml
### pure-0095
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1818
- relation_f1: 0.0000
- missing_nodes:
  - use command arc_warc_migrate options
  - refer to provided configuration
  - specify how fields are translated into warc records
  - handle missing fields
  - migrate content from arc files to warc files
- extra_nodes:
  - execute arc_warc_migrate options
  - read configuration file
  - are fields translated into warc records specified?
  - migrate content from arc files to warc files based on the provided configuration
- missing_relations:
  - use command arc_warc_migrate options -> refer to provided configuration
  - refer to provided configuration -> specify how fields are translated into warc records
  - specify how fields are translated into warc records -> generate errors requiring operator intervention
  - generate errors requiring operator intervention -> handle missing fields
  - handle missing fields -> migrate content from arc files to warc files
- input_excerpt:
  Migration Tool Execution: Use the command arc_warc_migrate <ARC_FILES> <CONFIG> [options] to migrate content from ARC files to WARC files based on the provided configuration. Ensure the configuration file specifies how fields are translated into WARC records, and handle missing fields by generating errors requiring operator intervention.
- generated_excerpt:
  @startuml start :Execute arc_warc_migrate <ARC_FILES> <CONFIG> [options]; :Read configuration file; if (Are fields translated into WARC records specified?) then (yes)   :Migrate content from ARC files to WARC files based on the provided configuration; else (no)   :Generate errors requiring operator intervention; endif @enduml
### us-0129
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- missing_nodes:
  - get the details of the workflow plan
  - get the execution history
  - get results recorded in neurohub
- extra_nodes:
  - record details of the workflow plan in neurohub
  - record execution history in neurohub
  - record results in neurohub
- missing_relations:
  - execute workflow -> get the details of the workflow plan
  - get the details of the workflow plan -> get the execution history
  - get the execution history -> get results recorded in neurohub
- input_excerpt:
  As a researcher, I want to have the details of the workflow plan as well as the execution history and results recorded in Neurohub while executing a workflow
- generated_excerpt:
  @startuml start :Execute a workflow; fork :Record details of the workflow plan in Neurohub; fork again :Record execution history in Neurohub; fork again :Record results in Neurohub; end fork @enduml
### pure-0082
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0968
- missing_nodes:
  - presented with main window
  - open file menu
  - select configure diagnostics menu item
  - administrator user?
  - include (authenticate user)
  - click recall button
  - populate window with disk file data
  - change configuration?
- extra_nodes:
  - select configure diagnostics menu item from the file menu
  - user has not already been authenticated as the administrator user?
  - authenticate user
  - user clicks?
  - recall button
  - populate the window with the data from the disk file
  - save button
  - request confirmation to save the changes
- missing_relations:
  - presented with main window -> open file menu
  - open file menu -> select configure diagnostics menu item
  - select configure diagnostics menu item -> administrator user?
  - administrator user? -> include (authenticate user)
  - include (authenticate user) -> have appropriate privilege?
  - display configuration window -> click recall button
  - read previously saved changes from disk file/database -> populate window with disk file data
  - populate window with disk file data -> change configuration?
- input_excerpt:
  1. When presented with the main window, the user may select the “Configure Diagnostics” menu item from the menu entitled “File”. 2. If the user has not already been authenticated as the administrator user, include (Authenticate User). 3. If the user has the appropriate privilege, the tool displays the configuration window. 4. The user may click the “Recall” button to read previously saved changes from a disk file or database. 5. The tool populates the window with the data from the disk file. 6. The user makes the desired changes to the configuration and can click the button labeled “Save” to save the changes. Otherwise, the user can click the button labeled “Close”. 7. If the user clicks the
- generated_excerpt:
  @startuml start :Select "Configure Diagnostics" menu item from the "File" menu; if (User has not already been authenticated as the administrator user?) then (yes)     :Authenticate User; else (no) endif if (User has the appropriate privilege?) then (yes)     :Display the configuration window;     switch (User clicks?)     case ("Recall" button)         :Read previously saved changes from a disk file or database;         :Populate the window with the data from the disk file;     case ("Save" button)         :Request confirmation to save the changes;         if (User confirms?) then (yes)             :Request a name for the disk file in which to save the modified data to permanent storage;    
### lmc-0052
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.8000
- missing_nodes:
  - rotation matrix dcm321
  - not invertible
  - invertible
- extra_nodes:
  - invert the rotation matrix dcm321
  - matrix is invertible
- missing_relations:
  - not invertible -> invertible
- input_excerpt:
  4.	The Rotation Matrix, DCM321, shall be invertible with the exception of the case where theta = +/- pi/2 radians.
- generated_excerpt:
  @startuml start :Invert the Rotation Matrix DCM321; if (theta = +/- pi/2 radians?) then (yes) else (no) :Matrix is invertible; endif stop @enduml
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2927
- relation_f1: 0.0513
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - click manage dependencies
  - list of infoobjects and their dependents is displayed
  - open select dependents drop-down list
  - selection
  - no
- extra_nodes:
  - in the promotion jobs home page click manage dependencies
  - from the select dependents drop-down list select any of the options available to add the dependents to the job
  - dependents are not selected by default?
  - explicitly select the dependents you want to promote
  - click to view the supported filtering options of infoobjects in the drop-down list
  - select an option and click ok
  - click apply changes to update the list of dependents
  - click apply changes and close to save the changes
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37
  - see creating a new job on page 37 -> add required infoobjects to new job
  - add required infoobjects to new job -> go to promotion jobs home page
  - go to promotion jobs home page -> click manage dependencies
  - click manage dependencies -> manage dependencies window appears
  - manage dependencies window appears -> list of infoobjects and their dependents is displayed
  - list of infoobjects and their dependents is displayed -> open select dependents drop-down list
- input_excerpt:
  22.	manage dependencies of an infoobject1. Log into the LifeCycle Manager tool.2. Create a new job. For information on creating a new job, see Creating aNew Job on page 37.3. Add the required infoobjects to the new job.4. In the "Promotion Jobs" home page, click Manage Dependencies. The "Manage Dependencies" window appears. This window displays the list of infoobjects and their dependents, as shown in the following figure:5. From the Select Dependents drop-down list, select any of the options available to add the dependents to the job. The dependents are displayed on the right side. The dependents are not selected by default; you must explicitly select the dependents you want to promote. For
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :In the "Promotion Jobs" home page, click Manage Dependencies; :The "Manage Dependencies" window appears; :From the Select Dependents drop-down list, select any of the options available to add the dependents to the job; :The dependents are displayed on the right side; if (Dependents are not selected by default?) then (yes)   :Explicitly select the dependents you want to promote; else (no) endif :Click to view the supported filtering options of infoobjects in the drop-down list; :Select an option, and click OK; :The filtered infoobjects are displayed; :Click Apply Changes to 

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
