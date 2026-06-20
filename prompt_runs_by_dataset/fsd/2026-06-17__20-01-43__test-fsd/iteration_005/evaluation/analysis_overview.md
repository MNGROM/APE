# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4811
- node_recall: 0.4678
- node_f1: 0.4744
- relation_precision: 0.3418
- relation_recall: 0.3336
- relation_f1: 0.3377
- plantuml_compilation_pass_rate: 0.9000
- llm_element_evaluated: 10.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8979
- llm_node_recall: 0.8576
- llm_node_f1: 0.8702
- llm_relation_precision: 0.5247
- llm_relation_recall: 0.4195
- llm_relation_f1: 0.4548

## Failure Types
- missing_or_wrong_relation: 9
- extra_or_wrong_relation: 9
- missing_activity: 8
- extra_activity: 8
- wrong_parallel: 3
- syntax_error: 1

## Representative Failure Cases
### rac-0005
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.5366
- relation_f1: 0.5217
- llm_element_status: success
- llm_node_f1: 0.9057
- llm_relation_f1: 0.5357
- missing_nodes:
  - slow charging is 1 and front mcu high-voltage detection flag is 0
  - condition judgement
  - remote mode is closed
  - shutdown
  - pet mode open request is closed
- extra_nodes:
  - case
  - go to state 105
  - slow charging becomes inactive
  - shift to state 28
  - remote mode deactivates
  - initiate shutdown
  - terminate
  - enter state 105
- missing_relations:
  - slow charging is 1 and front mcu high-voltage detection flag is 0 -> switch to state 93 [yes]
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - switch to state 105 -> condition judgement
  - condition judgement -> in remote mode [case in remote mode]
  - switch to state 28 -> remote mode is closed
  - switch to state 28 -> pet mode open request is closed
  - pet mode open request is closed -> shutdown [yes]
  - condition judgement -> battery soc is 20 [case battery soc is 20]
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :Transition to state 93; elseif (Charging/discharging power-up is active and front MCU high-voltage detection flag is 1) then :Transition to state 95; elseif (Power-up readiness is confirmed and vehicle charging/discharging mode is 2) then :Transition to state 105; endif  switch (Case) case (Remote mode)   :Go to state 105;   if (Slow charging becomes inactive) then     :Shift to state 28;   endif   if (Remote mode deactivates) then     :Initiate shutdown;     :Terminate;     stop   endif case (Pet mode request received)   :Enter state 105;   if (Slow charging is inactive) then     :Transition to state 28;   endif   :Process pet mode request;   :Perform shutdown;   :End opera
### lmc-0055
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.4444
- missing_nodes:
  - dcm321 * dcm321t
  - =identity (3x3) matrix.v?
  - allowed
  - not allowed
- extra_nodes:
  - multiply rotation matrix dcm321 by the transpose of rotation matrix dcm321t
  - result shall be the identity (3x3) matrix
- missing_relations:
  - dcm321 * dcm321t -> =identity (3x3) matrix.v?
  - =identity (3x3) matrix.v? -> allowed [yes]
  - =identity (3x3) matrix.v? -> not allowed [no]
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml start :Multiply Rotation Matrix DCM321 by the transpose of Rotation Matrix DCM321T; :Result shall be the Identity (3x3) Matrix; stop @enduml
### us-0165
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5714
- llm_relation_f1: 0.0000
- missing_nodes:
  - configure the help center url and topic mappings
- extra_nodes:
  - configure the help center url
  - configure topic mappings
- input_excerpt:
  As an Application Administrator , I want to be able to configure the help center URL and topic mappings.
- generated_excerpt:
  @startuml start :Configure the help center URL; :Configure topic mappings; stop @enduml
### bp-0005
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1905
- relation_f1: 0.0909
- llm_element_status: success
- llm_node_f1: 0.5600
- llm_relation_f1: 0.2308
- missing_nodes:
  - choose info objects
  - open characteristics info object catalog
  - open zd_pgroup context menu
  - select maintain master data
  - enter product group
  - enter short description
  - choose continue
  - more values?
- extra_nodes:
  - choose info objects in the modeling area of the data warehousing workbench
  - choose maintain master data from the context menu of info object product group (zd_pgroup)
  - enter ds10 as product group and computer as short description and choose continue
  - repeat create and enter steps with following values
  - save entries and return to the info object tree
  - repeat steps 2-7 for characteristic channel (zd_chan) with following values
- missing_relations:
  - choose info objects -> open characteristics info object catalog
  - open characteristics info object catalog -> open zd_pgroup context menu
  - open zd_pgroup context menu -> select maintain master data
  - select maintain master data -> choose execute
  - choose create -> enter product group [fork]
  - choose create -> enter short description [fork]
  - enter product group -> choose continue [merge]
  - enter short description -> choose continue [merge]
- input_excerpt:
  5.	Creating Master Data Directly in the System1. In the Modeling area of the Data Warehousing Workbench, choose Info Objects. 2. In the Info Object catalog for characteristics, choose Maintain master data from the context menu of your Info Object Product Group (ZD_PGROUP).3. Choose Execute.4. Choose Create.5. Enter DS10 as Product Group and Computer as the Short description and choose Continue.6. Repeat steps 4 and 5 with the following values:7. Save your entries and return to the Info Object tree.8. Repeat steps 2-7 for the characteristic Channel (ZD_CHAN) with the following values:
- generated_excerpt:
  @startuml start :Choose Info Objects in the Modeling area of the Data Warehousing Workbench; :Choose Maintain master data from the context menu of Info Object Product Group (ZD_PGROUP); :Choose Execute; :Choose Create; :Enter DS10 as Product Group and Computer as Short description and choose Continue; :Repeat Create and Enter steps with following values; :Save entries and return to the Info Object tree; :Repeat steps 2-7 for characteristic Channel (ZD_CHAN) with following values; stop @enduml
### bp-0021
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3077
- relation_f1: 0.1481
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.6452
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
  - modify these fields if required
  - in the save job in field browse and select the folder in which you want to save the job and click create
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
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :Click the Copy an Existing Job option; :The list of jobs in the PromotionJob folder is displayed; :Select a job from the job list, and click Create; :The name, keywords, and description of the job are displayed; :Modify these fields, if required; :In the Save Job in field, browse and select the folder in which you want to save the job, and click Create; :A new job is created; @enduml
### pure-0028
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.9333
- llm_relation_f1: 0.0000
- missing_nodes:
  - verify successful receipt
  - accumulation of error statistics
  - comparison against tolerances
- extra_nodes:
  - verify successful receipt of incoming data from the correlator
  - accumulate error statistics
  - compare error statistics against tolerances
- missing_relations:
  - verify successful receipt -> check for receive errors [fork]
  - verify successful receipt -> determine all expected data was received [fork]
  - verify successful receipt -> accumulation of error statistics [fork]
  - verify successful receipt -> comparison against tolerances [fork]
  - verify successful receipt -> report out of tolerance conditions [fork]
  - check for receive errors -> verify successful receipt [merge]
  - determine all expected data was received -> verify successful receipt [merge]
  - accumulation of error statistics -> verify successful receipt [merge]
- input_excerpt:
  Verify Receive – The BE shall verify the successful receipt of incoming data from the Correlator. This includes checking for receive errors and determining that all expected data was received, accumulation of error statistics and comparison against tolerances, and reporting of all out of tolerance conditions.
- generated_excerpt:
  @startuml start :Verify successful receipt of incoming data from the Correlator; :Check for receive errors; :Determine that all expected data was received; :Accumulate error statistics; :Compare error statistics against tolerances; :Report all out of tolerance conditions; stop @enduml
### pure-0029
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.2857
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.6667
- missing_nodes:
  - track buffer locations
  - data processing is incomplete
- extra_nodes:
  - track buffer locations of all input data until data processing is complete
  - buffer overflow condition?
- missing_relations:
  - track buffer locations -> data processing is incomplete
  - data processing is incomplete -> store input data records in memory buffer [yes]
  - data processing is incomplete -> report any buffer overflow conditions [no]
- input_excerpt:
  Input Data Management - The BE shall store input data records in a memory buffer and track buffer locations of all input data until data processing is complete. Report any buffer overflow conditions.
- generated_excerpt:
  @startuml start :Store input data records in a memory buffer; :Track buffer locations of all input data until data processing is complete; if (Buffer overflow condition?) then (yes)   :Report buffer overflow condition; else (no) endif stop @enduml
### rac-0019
- dataset: rac
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7541
- relation_f1: 0.6027
- llm_element_status: success
- llm_node_f1: 0.9315
- llm_relation_f1: 0.5250
- missing_nodes:
  - remote mode is disabled
  - slow charging is inactive
  - fast charging is inactive
  - switch to state 189
- extra_nodes:
  - system starts up
  - move to state 49
  - exit
  - proceed to state 49
  - slow charging is active and charging system command is 4?
  - go to state 29
  - transition to state 49
  - move to state 110
- missing_relations:
  - fast charge vcc2=6 -> slow charging is active and charging system command=1 [no]
  - switch to state 29 -> ignition switch=0 and vcc2=12
  - slow charging is active and charging system command=1 -> remote mode enabled [no]
  - switch to state 110 -> charging system command=4
  - switch to state 29 -> ignition switch=0 and slow charging is inactive
  - switch to state 28 -> remote mode is disabled
  - switch to state 110 -> slow charging is inactive
  - switch to state 170 -> fast charging is inactive
- input_excerpt:
  After the system starts up, if the ignition switch is set to 2, transition to state 30. Then, under that condition: - If the ignition switch becomes 0, move to state 49 and exit. - If the fast charge Vcc2 is 6, observe the charging gun indicator. Should the charging system command be 4, switch to state 29. - If the ignition switch is 0 and Vcc2 is 12, proceed to state 49 and exit. - If slow charging is active and the charging system command is 1, transition to state 110. If the command is 4 instead, go to state 29. Also, if the ignition switch is 0 and slow charging is not active, shift to state 49 and exit.  If remote mode is enabled, switch to state 28. If it's disabled, transition to stat
- generated_excerpt:
  @startuml start :System starts up; if (Ignition switch is set to 2?) then (yes)   :Transition to state 30;   if (Ignition switch becomes 0?) then (yes)     :Move to state 49;     :Exit;   elseif (Fast charge Vcc2 is 6?) then (yes)     :Observe the charging gun indicator;     if (Charging system command is 4?) then (yes)       :Switch to state 29;     endif   elseif (Ignition switch is 0 and Vcc2 is 12?) then (yes)     :Proceed to state 49;     :Exit;   elseif (Slow charging is active and charging system command is 1?) then (yes)     :Transition to state 110;   elseif (Slow charging is active and charging system command is 4?) then (yes)     :Go to state 29;   elseif (Ignition switch is 0 and
### lmc-0002
- dataset: lmc
- failure_types: missing_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8571
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.5000
- missing_nodes:
  - not affect method for determining selected value
- missing_relations:
  - a first failure in progress? -> not affect method for determining selected value [yes]
- input_excerpt:
  [RM-002] In the no-fail state, the mid-value shall be the selected value.  Note: a first failure in progress will not affect the method for determining the selected value.
- generated_excerpt:
  @startuml start if (No-fail state?) then (yes)   :Mid-value shall be the selected value; elseif (First failure in progress?) then (yes)   :Mid-value shall be the selected value; endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
