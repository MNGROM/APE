# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3340
- node_recall: 0.3774
- node_f1: 0.3544
- relation_precision: 0.2593
- relation_recall: 0.2881
- relation_f1: 0.2729
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.6295
- llm_node_recall: 0.7900
- llm_node_f1: 0.6760
- llm_relation_precision: 0.4460
- llm_relation_recall: 0.5206
- llm_relation_f1: 0.4274

## Failure Types
- missing_activity: 20
- extra_activity: 20
- extra_or_wrong_relation: 20
- missing_or_wrong_relation: 18
- wrong_parallel: 4
- wrong_loop: 1

## Representative Failure Cases
### us-0056
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4706
- llm_relation_f1: 0.3750
- missing_nodes:
  - edit site member profile
  - correct problems
- extra_nodes:
  - site administrator selects a site member
  - view member profile
  - click edit profile
  - system displays editable profile form
  - administrator modifies profile details
  - administrator submits changes
  - system validates input data
  - valid input?
- missing_relations:
  - edit site member profile -> correct problems
- input_excerpt:
  As a site administrator, I want to edit any site member profile, so that I can correct problems for members.
- generated_excerpt:
  @startuml start :Site Administrator selects a site member; :View member profile; :Click edit profile; :System displays editable profile form; :Administrator modifies profile details; :Administrator submits changes; :System validates input data; if (Valid input?) then (yes)   :System updates member profile;   :Display success message; else (no)   :Display validation error message;   stop endif stop @enduml
### us-0073
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4444
- llm_relation_f1: 0.3158
- missing_nodes:
  - keep information in one place
  - improve on previous years
- extra_nodes:
  - camp administrator logs into the system
  - access information management dashboard
  - review previous year s information
  - input current year s information
  - update existing information
  - save information to centralized repository
  - information saved successfully?
  - confirm information is stored in one place
- missing_relations:
  - keep information in one place -> improve on previous years
- input_excerpt:
  As a camp administrator, I want to be able to keep my information in one place, so that the admins next year can improve on the previous years.
- generated_excerpt:
  @startuml skinparam style strictuml  title Camp Administrator - Manage Yearly Information  start  :Camp Administrator logs into the system;  :Access Information Management Dashboard;  fork   :Review previous year's information; fork again   :Input current year's information; fork again   :Update existing information; end fork  :Save information to centralized repository;  if (Information saved successfully?) then (Yes)   :Confirm information is stored in one place;   :Ensure information is accessible for next year's admins;   :Log out of the system;   stop else (No)   :Display error message;   :Retry saving information;   stop endif  @enduml
### pure-0095
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1250
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7273
- llm_relation_f1: 0.1000
- missing_nodes:
  - refer to provided configuration
  - specify how fields are translated into warc records
  - generate errors requiring operator intervention
  - handle missing fields
  - migrate content from arc files to warc files
- extra_nodes:
  - read arc files
  - load configuration file
  - configuration specifies field translation?
  - translate arc fields into warc records
  - write warc records to output file
  - generate error for missing field(s)
  - halt migration
  - require operator intervention
- missing_relations:
  - use command arc_warc_migrate options -> refer to provided configuration
  - refer to provided configuration -> specify how fields are translated into warc records [fork]
  - refer to provided configuration -> generate errors requiring operator intervention [fork]
  - generate errors requiring operator intervention -> handle missing fields
  - specify how fields are translated into warc records -> migrate content from arc files to warc files
  - handle missing fields -> migrate content from arc files to warc files
- input_excerpt:
  Migration Tool Execution: Use the command arc_warc_migrate <ARC_FILES> <CONFIG> [options] to migrate content from ARC files to WARC files based on the provided configuration. Ensure the configuration file specifies how fields are translated into WARC records, and handle missing fields by generating errors requiring operator intervention.
- generated_excerpt:
  @startuml start :Input command: arc_warc_migrate <ARC_FILES> <CONFIG> [options]; :Read ARC files; :Load configuration file; if (Configuration specifies field translation?) then (Yes)   :Translate ARC fields into WARC records;   :Write WARC records to output file; else (No - Missing fields)   :Generate error for missing field(s);   :Halt migration;   :Require operator intervention;   stop endif :Migration complete; stop @enduml
### bp-0030
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.1765
- llm_element_status: success
- llm_node_f1: 0.9756
- llm_relation_f1: 0.3684
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
  - enter the name description and keywords for the job
  - in the save job in field browse and select the folder
  - select the source system and the destination system from the drop-down lists
  - system name displayed in drop-down list?
  - click the login to a new cms option
  - enter the name of the system along with the user name and password
- missing_relations:
  - log in -> go to promotion jobs
  - click new job -> new job window appears
  - new job window appears -> enter name [fork]
  - new job window appears -> enter description [fork]
  - new job window appears -> enter keywords [fork]
  - enter name -> go to save job field
  - enter description -> go to save job field
  - enter keywords -> go to save job field
- input_excerpt:
  30.	Creating a New Job1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriate fields.4. In the Save Job in field, browse and select the folder in which you want to save the job.5. Select the source system and the destination system from the drop-down lists. If the name of the system is not displayed in the drop-down list, click the Login to a new CMS option. A new window is launched. Enter the name of the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name, description, and keywords for the job; :In the Save Job in field, browse and select the folder; :Select the source system and the destination system from the drop-down lists; if (System name displayed in drop-down list?) then (No)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the name of the system along with the user name and password; else (Yes) endif :Click Create; stop @enduml
### us-0093
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5714
- llm_relation_f1: 0.3077
- missing_nodes:
  - present/discuss particular data timeslice of interest
- extra_nodes:
  - consumer navigates to datapackage
  - select specific version of datapackage
  - version exists?
  - retrieve datapackage at the specific version
  - display datapackage details for the selected version
  - consumer presents/discusses the data timeslice with others
  - display version not found error
- missing_relations:
  - view a datapackage at a particular version online -> present/discuss particular data timeslice of interest
- input_excerpt:
  As a Consumer, I want to view a Datapackage at a particular version online, so that that I can present/discuss the particular data timeslice of interest with other people.
- generated_excerpt:
  @startuml skinparam style strictuml  title Consumer Views a Datapackage at a Particular Version  start  :Consumer navigates to Datapackage;  :Select specific version of Datapackage;  :Request to view Datapackage at selected version;  if (Version exists?) then (Yes)   :Retrieve Datapackage at the specific version;   :Display Datapackage details for the selected version;   :Consumer presents/discusses the data timeslice with others; else (No)   :Display "Version not found" error; endif  stop @enduml
### lmc-0052
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.2500
- llm_element_status: success
- llm_node_f1: 0.6154
- llm_relation_f1: 0.4286
- missing_nodes:
  - rotation matrix dcm321
  - not invertible
  - invertible
- extra_nodes:
  - input theta value
  - dcm321 is not invertible
  - theta == -pi/2 radians?
  - dcm321 is not invertible
  - dcm321 is invertible
- missing_relations:
  - rotation matrix dcm321 -> theta = +/- pi/2 radians?
  - theta = +/- pi/2 radians? -> not invertible [yes]
- input_excerpt:
  4.	The Rotation Matrix, DCM321, shall be invertible with the exception of the case where theta = +/- pi/2 radians.
- generated_excerpt:
  @startuml start :Input theta value; if (theta == +pi/2 radians?) then (yes)   :DCM321 is NOT invertible;   stop elseif (theta == -pi/2 radians?) then (yes)   :DCM321 is NOT invertible;   stop else (no)   :DCM321 is invertible; endif stop @enduml
### pure-0097
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2400
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7742
- llm_relation_f1: 0.6364
- missing_nodes:
  - filters
  - url
  - mime-types
  - size
  - timestamp
  - extract and repackage warc records
  - use provided pattern
- extra_nodes:
  - parse input arguments and options
  - open input warc file(s)
  - read next warc record
  - apply filters?
  - check filter criteria (url mime-type size timestamp)
  - record matches filters?
  - include record for repackaging
  - exclude record
- missing_relations:
  - use command warc_repackage -i options -> filters
  - filters -> url [fork]
  - filters -> mime-types [fork]
  - filters -> size [fork]
  - filters -> timestamp [fork]
  - url -> extract and repackage warc records
  - mime-types -> extract and repackage warc records
  - size -> extract and repackage warc records
- input_excerpt:
  Repackaging Tool Execution: Use the command warc_repackage -i <WARC_FILE> <WARC_PATTERN> [options] to extract and repackage WARC records based on filters like URL, MIME-Types, size, or timestamp. Specify output WARC file names using the provided pattern and include metadata records describing the extraction context.
- generated_excerpt:
  @startuml start :Execute command: warc_repackage -i <WARC_FILE> <WARC_PATTERN> [options]; :Parse input arguments and options; :Open input WARC file(s); repeat   :Read next WARC record;   if (Apply filters?) then     :Check filter criteria\n(URL, MIME-Type, Size, Timestamp);     if (Record matches filters?) then       :Include record for repackaging;     else       :Exclude record;     endif   else     :Include record for repackaging;   endif repeat while (More records in WARC file?) is (Yes) -> No; :Generate output WARC file name\nusing provided pattern; :Create metadata records\ndescribing extraction context; :Write filtered records and\nmetadata to output WARC file; :Close input and output
### bp-0022
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2778
- relation_f1: 0.3243
- llm_element_status: success
- llm_node_f1: 0.8696
- llm_relation_f1: 0.6047
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - go to promotion jobs home page
  - click manage dependencies
  - manage dependencies window appears
  - list of infoobjects and their dependents is displayed
  - open select dependents drop-down list
  - dependents are displayed on the right
- extra_nodes:
  - in the promotion jobs home page click manage dependencies
  - view the manage dependencies window (displaying list of infoobjects and dependents)
  - from the select dependents drop-down list select an option to add dependents to the job
  - explicitly select the specific dependents you want to promote
  - select a filtering option and click ok
  - click apply changes to update the list of dependents
  - click apply changes and close to save the changes
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37 [yes]
  - see creating a new job on page 37 -> add required infoobjects to new job
  - go to promotion jobs home page -> click manage dependencies
  - click manage dependencies -> manage dependencies window appears
  - manage dependencies window appears -> list of infoobjects and their dependents is displayed
  - list of infoobjects and their dependents is displayed -> open select dependents drop-down list
  - open select dependents drop-down list -> dependents are displayed on the right
- input_excerpt:
  22.	manage dependencies of an infoobject1. Log into the LifeCycle Manager tool.2. Create a new job. For information on creating a new job, see Creating aNew Job on page 37.3. Add the required infoobjects to the new job.4. In the "Promotion Jobs" home page, click Manage Dependencies. The "Manage Dependencies" window appears. This window displays the list of infoobjects and their dependents, as shown in the following figure:5. From the Select Dependents drop-down list, select any of the options available to add the dependents to the job. The dependents are displayed on the right side. The dependents are not selected by default; you must explicitly select the dependents you want to promote. For
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Add the required infoobjects to the new job; :In the "Promotion Jobs" home page,\nclick Manage Dependencies; :View the "Manage Dependencies" window\n(displaying list of infoobjects and dependents); :From the Select Dependents drop-down list,\nselect an option to add dependents to the job; :Explicitly select the specific dependents\nyou want to promote; :Click to view supported filtering options\nof infoobjects in the drop-down list; :Select a filtering option and click OK; :Filtered infoobjects are displayed; :Click Apply Changes to update the list of dependents; :Click Apply Changes and Close to save the changes; stop

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
