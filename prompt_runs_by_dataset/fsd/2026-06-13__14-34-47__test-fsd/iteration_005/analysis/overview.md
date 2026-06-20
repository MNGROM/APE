# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3610
- node_recall: 0.3746
- node_f1: 0.3617
- relation_precision: 0.2443
- relation_recall: 0.2772
- relation_f1: 0.2589
- plantuml_compilation_pass_rate: 0.9000
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_activity: 9
- extra_activity: 9
- extra_or_wrong_relation: 9
- missing_or_wrong_relation: 8
- syntax_error: 1

## Representative Failure Cases
### rac-0019
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: Missing required @startuml/@enduml wrapper | ERROR
- plantuml_compiles: False
- plantuml_compile_errors: No PlantUML content to compile.
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - ignition switch=2
  - switch to state 30
  - ignition switch=0
  - switch to state 49
  - switch to state 49
  - switch to state 49
  - switch to state 49
  - switch to state 49
- missing_relations:
  - ignition switch=2 -> switch to state 30
  - switch to state 30 -> ignition switch=0
  - ignition switch=0 -> switch to state 49
  - switch to state 49 -> fast charge vcc2=6
  - fast charge vcc2=6 -> observe charging gun indicator
  - observe charging gun indicator -> charging system command=4
  - charging system command=4 -> switch to state 29
  - charging system command=4 -> switch to state 29
- input_excerpt:
  After the system starts up, if the ignition switch is set to 2, transition to state 30. Then, under that condition: - If the ignition switch becomes 0, move to state 49 and exit. - If the fast charge Vcc2 is 6, observe the charging gun indicator. Should the charging system command be 4, switch to state 29. - If the ignition switch is 0 and Vcc2 is 12, proceed to state 49 and exit. - If slow charging is active and the charging system command is 1, transition to state 110. If the command is 4 instead, go to state 29. Also, if the ignition switch is 0 and slow charging is not active, shift to state 49 and exit.  If remote mode is enabled, switch to state 28. If it's disabled, transition to stat
- generated_excerpt:
  
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
  - multiply dcm321 by dcm321t
  - result equals identity (3x3
- missing_relations:
  - dcm321 * dcm321t -> =identity (3x3
  - =identity (3x3 -> allowed
  - allowed -> not allowed
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml start :Multiply DCM321 by DCM321T; if (Result equals Identity (3x3) Matrix?) then (yes) else (no) endif @enduml
### us-0165
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - configure the help center url and topic mappings
- extra_nodes:
  - configure help center url
  - configure topic mappings
- input_excerpt:
  As an Application Administrator , I want to be able to configure the help center URL and topic mappings.
- generated_excerpt:
  @startuml start :Configure help center URL; :Configure topic mappings; stop @enduml
### bp-0021
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2353
- relation_f1: 0.0625
- missing_nodes:
  - go to promotion jobs home page
  - click new job
  - the list of jobs is displayed
  - select a job from list
  - cick create
  - information is displayed
  - name
  - keywords
- extra_nodes:
  - in the promotion jobs home page click new job
  - the list of jobs in the promotionjob folder is displayed
  - select a job from the job list and click create
  - the name of the job is displayed
  - the keywords of the job are displayed
  - the description of the job is displayed
  - modify these fields required?
  - modify name
- missing_relations:
  - log in lifecycle manager tool -> go to promotion jobs home page
  - go to promotion jobs home page -> click new job
  - click new job -> click the copy an existing job option
  - click the copy an existing job option -> the list of jobs is displayed
  - the list of jobs is displayed -> select a job from list
  - select a job from list -> cick create
  - cick create -> information is displayed
  - information is displayed -> name
- input_excerpt:
  21.	create a new job by copying an existing job.To create a new job by copying an existing job, complete the following steps:1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job.3. Click the Copy an Existing Job option. The list of jobs in the PromotionJob folder is displayed4. Select a job from the job list, and click Create. The name, keywords, and description of the job are displayed. You can modify these fields, if required. However, you cannot change the source system.5. In the Save Job in field, browse and select the folder in which you want to save the job, and click Create.A new job is created.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :Click the Copy an Existing Job option; :The list of jobs in the PromotionJob folder is displayed; :Select a job from the job list, and click Create; fork   :The name of the job is displayed; fork again   :The keywords of the job are displayed; fork again   :The description of the job is displayed; end fork if (Modify these fields required?) then (yes)   :Modify name;   :Modify keywords;   :Modify description; else (no) endif if (Change source system?) then (yes)   :Reject change;   stop else (no) endif :In the Save Job in field, browse and select the folder in which you want to save the 
### bp-0005
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2667
- relation_f1: 0.1538
- missing_nodes:
  - choose info objects
  - open characteristics info object catalog
  - open zd_pgroup context menu
  - select maintain master data
  - enter product group
- extra_nodes:
  - choose info objects in modeling area of data warehousing workbench
  - choose maintain master data from context menu of info object product group (zd_pgroup) in info object catalog for characteristics
  - enter ds10 as product group and computer as short description and choose continue
  - repeat steps 4 and 5 with the following values
  - save your entries and return to info object tree
  - repeat steps 2-7 for characteristic channel (zd_chan) with the following values
- missing_relations:
  - choose info objects -> open characteristics info object catalog
  - open characteristics info object catalog -> open zd_pgroup context menu
  - open zd_pgroup context menu -> select maintain master data
  - select maintain master data -> choose execute
  - choose create -> enter product group
- input_excerpt:
  5.	Creating Master Data Directly in the System1. In the Modeling area of the Data Warehousing Workbench, choose Info Objects. 2. In the Info Object catalog for characteristics, choose Maintain master data from the context menu of your Info Object Product Group (ZD_PGROUP).3. Choose Execute.4. Choose Create.5. Enter DS10 as Product Group and Computer as the Short description and choose Continue.6. Repeat steps 4 and 5 with the following values:7. Save your entries and return to the Info Object tree.8. Repeat steps 2-7 for the characteristic Channel (ZD_CHAN) with the following values:
- generated_excerpt:
  @startuml start :Choose Info Objects in Modeling area of Data Warehousing Workbench; :Choose Maintain master data from context menu of Info Object Product Group (ZD_PGROUP) in Info Object catalog for characteristics; :Choose Execute; :Choose Create; :Enter DS10 as Product Group and Computer as Short description and choose Continue; :Repeat steps 4 and 5 with the following values; :Save your entries and return to Info Object tree; :Repeat steps 2-7 for characteristic Channel (ZD_CHAN) with the following values; end @enduml
### lmc-0002
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.0000
- missing_nodes:
  - in no-fail state
  - a first failure in progress?
  - not affect method for determining selected value
- extra_nodes:
  - no-fail state or first failure in progress?
- missing_relations:
  - in no-fail state -> mid-value be selected value
  - mid-value be selected value -> a first failure in progress?
  - a first failure in progress? -> not affect method for determining selected value
- input_excerpt:
  [RM-002] In the no-fail state, the mid-value shall be the selected value.  Note: a first failure in progress will not affect the method for determining the selected value.
- generated_excerpt:
  @startuml start if (No-fail state or first failure in progress?) then (yes)   :Mid-value shall be the selected value; else (no) endif stop @enduml
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3462
- relation_f1: 0.3600
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
  - power-up readiness is confirmed and the vehicle s charging/discharging mode is set to 2?
  - proceed to state 105
  - operating condition
  - go to state 105
  - slow charging becomes inactive?
- missing_relations:
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - power-up is ready and vehicle charging/discharging mode is 2 -> switch to state 105
  - switch to state 105 -> condition judgement
  - condition judgement -> in remote mode
  - in remote mode -> switch to state 105
  - switch to state 28 -> remote mode is closed
  - remote mode is closed -> shutdown
  - shutdown -> pet mode request is received
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System starts up;  if (slow charging is active and the front MCU high-voltage detection flag is 0?) then (yes)   :Transition to state 93; elseif (charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1?) then (yes)   :Move to state 95; elseif (power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2?) then (yes)   :Proceed to state 105; endif  switch (Operating condition) case (Remote mode)   :Go to state 105;   if (slow charging becomes inactive?) then (yes)     :Shift to state 28;   endif   if (remote mode deactivates?) then (yes)     :Initiate shutdown;     :Terminate;     stop   endif case (Receiving 
### pure-0029
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.2857
- missing_nodes:
  - track buffer locations
- extra_nodes:
  - track buffer locations of all input data
  - buffer overflow condition?
- missing_relations:
  - track buffer locations -> data processing is incomplete
  - data processing is incomplete -> report any buffer overflow conditions
- input_excerpt:
  Input Data Management - The BE shall store input data records in a memory buffer and track buffer locations of all input data until data processing is complete. Report any buffer overflow conditions.
- generated_excerpt:
  @startuml start repeat   :Store input data records in a memory buffer;   :Track buffer locations of all input data;   if (Buffer overflow condition?) then (yes)     :Report buffer overflow conditions;   else (no)   endif repeat while (Data processing is complete?) is (no) ->yes; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
