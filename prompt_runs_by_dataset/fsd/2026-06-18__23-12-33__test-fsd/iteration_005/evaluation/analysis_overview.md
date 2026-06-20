# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4650
- node_recall: 0.5326
- node_f1: 0.4965
- relation_precision: 0.2954
- relation_recall: 0.3549
- relation_f1: 0.3224
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7777
- llm_node_recall: 0.8347
- llm_node_f1: 0.7936
- llm_relation_precision: 0.4885
- llm_relation_recall: 0.5115
- llm_relation_f1: 0.4838

## Failure Types
- extra_or_wrong_relation: 19
- extra_activity: 18
- missing_or_wrong_relation: 18
- missing_activity: 16
- wrong_parallel: 4

## Representative Failure Cases
### us-0165
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4444
- llm_relation_f1: 0.0000
- missing_nodes:
  - configure the help center url and topic mappings
- extra_nodes:
  - configure help center url
  - select topic mapping type?
  - map topic to url
  - map topic to content
- input_excerpt:
  As an Application Administrator , I want to be able to configure the help center URL and topic mappings.
- generated_excerpt:
  @startuml start :Configure help center URL; switch (Select topic mapping type?) case (Map topic to URL)   :Map topic to URL; case (Map topic to content)   :Map topic to content; endswitch stop @enduml
### us-0180
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4444
- llm_relation_f1: 0.0000
- missing_nodes:
  - deposit arbitrarily large files
  - remove restrictions on what files can and cannot be stored
- extra_nodes:
  - depositor
  - select arbitrarily large file
  - deposit file
- missing_relations:
  - deposit arbitrarily large files -> remove restrictions on what files can and cannot be stored
- input_excerpt:
  As a depositor, I want to deposit arbitrarily large files, so that I am not limited in what files I can and cannot deposit.
- generated_excerpt:
  @startuml start :Depositor; :Select arbitrarily large file; :Deposit file; note right: No limitation on what files can and cannot be deposited stop @enduml
### bp-0005
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1905
- relation_f1: 0.0833
- llm_element_status: success
- llm_node_f1: 0.9655
- llm_relation_f1: 0.5926
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
  - in the modeling area of the data warehousing workbench choose info objects
  - in the info object catalog for characteristics choose maintain master data from the context menu of your info object
  - enter product group and short description choose continue
  - repeat steps 4 and 5?
  - save your entries and return to the info object tree
  - repeat steps 2-7 for another characteristic?
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
  @startuml start :In the Modeling area of the Data Warehousing Workbench, choose Info Objects; repeat   :In the Info Object catalog for characteristics, choose Maintain master data from the context menu of your Info Object;   repeat     :Choose Execute;     :Choose Create;     :Enter Product Group and Short description, choose Continue;   repeat while (Repeat steps 4 and 5?)   :Save your entries and return to the Info Object tree; repeat while (Repeat steps 2-7 for another characteristic?) @enduml
### bp-0014
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.1143
- llm_element_status: success
- llm_node_f1: 0.7317
- llm_relation_f1: 0.6939
- missing_nodes:
  - select start
  - select programs
  - select businessobjects xi 3.1
  - select businessobjects enterprise
  - select businessobjects lifecycle manager
  - go to system field
  - enter cms name
  - open authentication drop-down list
- extra_nodes:
  - select start > programs > businessobjects xi 3.1 > businessobjects enterprise > businessobjects lifecycle manager
  - in the system field enter the name of the central management server (cms)
  - select the appropriate authentication method from the authentication drop-down list
  - authentication type
  - requires a user name and a password recognized by the businessobjects enterprise system (default)
  - requires a user name and a password recognized by the businessobjects enterprise system
  - requires a special setup
- missing_relations:
  - select start -> select programs
  - select programs -> select businessobjects xi 3.1
  - select businessobjects xi 3.1 -> select businessobjects enterprise
  - select businessobjects enterprise -> select businessobjects lifecycle manager
  - lifecycle manager login screen appears -> go to system field
  - go to system field -> enter cms name
  - enter cms name -> enter username and password
  - enter username and password -> open authentication drop-down list
- input_excerpt:
  14.	log into the LifeCycle Manager tool.To log into the LifeCycle Manager tool, complete the following steps:1. Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager. The LifeCycle Manager login screen appears.2. In the System field, enter the name of the Central Management Server (CMS) on which the LifeCycle Manager tool is installed.3. Enter the user name and password.4. Select the appropriate authentication method from the Authentication drop-down list.The LifeCycle Manager tool supports the following authentication types:• Enterprise authentication - This authentication type requires a user name and a password that are recognize
- generated_excerpt:
  @startuml start :Select Start > Programs > BusinessObjects XI 3.1 > BusinessObjects Enterprise > BusinessObjects LifeCycle Manager; :The LifeCycle Manager login screen appears; :In the System field, enter the name of the Central Management Server (CMS); :Enter the user name and password; :Select the appropriate authentication method from the Authentication drop-down list; switch (Authentication type) case (Enterprise authentication)   :Requires a user name and a password recognized by the BusinessObjects Enterprise system (Default); case (LDAP authentication)   :Requires a user name and a password recognized by the BusinessObjects Enterprise system;   :Requires a special setup; case (Windows
### lmc-0055
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.8000
- missing_nodes:
  - dcm321 * dcm321t
  - allowed
  - not allowed
- extra_nodes:
  - compute rotation matrix dcm321
  - compute transpose of rotation matrix dcm321t
  - multiply dcm321 by dcm321t
  - requirement satisfied
  - requirement violated
- missing_relations:
  - =identity (3x3) matrix.v? -> allowed [yes]
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml start :Compute Rotation Matrix DCM321; :Compute Transpose of Rotation Matrix DCM321T; :Multiply DCM321 by DCM321T; if (Result equals Identity (3x3) Matrix?) then (Yes)   :Requirement Satisfied; else (No)   :Requirement Violated; endif stop @enduml
### bp-0021
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3448
- relation_f1: 0.1935
- llm_element_status: success
- llm_node_f1: 0.9744
- llm_relation_f1: 0.5714
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
  - modify fields required?
  - modify name keywords and description
  - cannot change the source system
  - in the save job in field browse and select the folder in which you want to save the job
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
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :Click the Copy an Existing Job option; :The list of jobs in the PromotionJob folder is displayed; :Select a job from the job list, and click Create; :The name, keywords, and description of the job are displayed; if (Modify fields required?) then (yes)   :Modify name, keywords, and description; else (no) endif :Cannot change the source system; :In the Save Job in field, browse and select the folder in which you want to save the job; :Click Create; :A new job is created; @enduml
### us-0200
- dataset: us
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.8571
- missing_nodes:
  - cite files in publication
- extra_nodes:
  - select a file
  - display structured citation data
- input_excerpt:
  As a researcher, I want to generate structured citation data, so that so I can cite a file in a publication.
- generated_excerpt:
  @startuml start :Select a file; :Generate structured citation data; :Display structured citation data; stop @enduml
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4390
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8929
- llm_relation_f1: 0.6667
- missing_nodes:
  - switch to state 95
  - power-up is ready and vehicle charging/discharging mode is 2
  - condition judgement
  - remote mode is closed
  - shutdown
  - pet mode open request is closed
  - battery soc is 20
- extra_nodes:
  - system starts up
  - move to state 95
  - power-up readiness is confirmed and vehicle s charging/discharging mode is 2?
  - proceed to state 105
  - case condition
  - go to state 105
  - slow charging becomes inactive?
  - shift to state 28
- missing_relations:
  - switch to state 93 -> charging/discharging power-up is active and front mcu high-voltage detection flag is 1
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - switch to state 105 -> condition judgement
  - switch to state 28 -> remote mode is closed
  - switch to state 28 -> pet mode open request is closed
  - pet mode open request is closed -> shutdown [yes]
  - condition judgement -> battery soc is 20 [case battery soc is 20]
  - switch to state 105 -> soc reaches 80 and dcdc state is 3
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System starts up;  if (Slow charging is active\nand front MCU high-voltage detection flag is 0?) then (yes)   :Transition to state 93; elseif (Charging/discharging power-up is active\nand front MCU high-voltage detection flag is 1?) then (yes)   :Move to state 95; elseif (Power-up readiness is confirmed\nand vehicle's charging/discharging mode is 2?) then (yes)   :Proceed to state 105; endif  switch (Case condition) case (In remote mode)   :Go to state 105;   if (Slow charging becomes inactive?) then (yes)     :Shift to state 28;   endif   if (Remote mode deactivates?) then (yes)     :Initiate shutdown;     stop   endif case (Upon receiving a pet mode request)   :Enter state
### pure-0028
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4615
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7500
- llm_relation_f1: 0.1053
- missing_nodes:
  - verify successful receipt
  - accumulation of error statistics
  - comparison against tolerances
- extra_nodes:
  - receive incoming data from correlator
  - accumulate error statistics
  - compare error statistics against tolerances
  - out of tolerance conditions exist?
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
  @startuml start :Receive incoming data from Correlator; :Check for receive errors; :Determine that all expected data was received; :Accumulate error statistics; :Compare error statistics against tolerances; if (Out of tolerance conditions exist?) then (yes)   :Report all out of tolerance conditions; else (no) endif stop @enduml
### bp-0013
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.2222
- llm_element_status: success
- llm_node_f1: 0.8125
- llm_relation_f1: 0.2857
- missing_nodes:
  - have existing job?
  - add infoobjects
  - promote all dependencies?
  - use manage dependencies
  - open type drop-down list
  - select dependent want to promote
  - click import biar tab
- extra_nodes:
  - create job method?
  - add infoobjects to the job you want to promote
  - want to promote all dependents?
  - use the manage dependencies option to select the dependents you want to promote
  - select the type of dependents you want to promote from the type drop-down list
  - create a job
  - use the manage dependencies option to select the required dependents
- missing_relations:
  - have existing job? -> create a new job [no]
  - have existing job? -> copy existing job [yes]
  - create a new job -> add infoobjects [merge]
  - add infoobjects -> promote all dependencies?
  - promote all dependencies? -> use manage dependencies [yes]
  - promote all dependencies? -> source and the destination systems connected? [no]
  - use manage dependencies -> open type drop-down list
  - open type drop-down list -> select dependent want to promote
- input_excerpt:
  13.	promote a job when the source and the destination systems are connected, complete the following steps:1. Connect to the source system.2. Create a new job. You can also copy an existing job.3. Add infoobjects to the job you want to promote. If you do not want to promote all the dependents of the infoobjects, you can use the Manage Dependencies option to select the dependents you want to promote.Note:You can select the type of dependents you want to promote from the Type drop-down list.4. Promote the job.Promoting a job when the source system and the destination system are not connected18 To promote a job when the source and the destination systems are not connected, complete the following
- generated_excerpt:
  @startuml start if (Source and destination systems connected?) then (yes)   :Connect to the source system;   :Create a new job;   switch (Create job method?)   case (Create new)     :Create a new job;   case (Copy existing)     :Copy an existing job;   endswitch   :Add infoobjects to the job you want to promote;   if (Want to promote all dependents?) then (no)     :Use the Manage Dependencies option to select the dependents you want to promote;     :Select the type of dependents you want to promote from the Type drop-down list;   else (yes)   endif   :Promote the job; else (no)   :Connect to the source system;   :Create a job;   switch (Create job method?)   case (Create new)     :Create a n
### rac-0002
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5263
- relation_f1: 0.4762
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.2069
- missing_nodes:
  - gear is d or n
  - gear is s
  - gear check
  - gear is d or e
  - gear is n or r
- extra_nodes:
  - system starts up
  - check the gear position
  - gear position
  - calculate d_s gear mileage parameter as s gear nominal mileage divided by d gear nominal mileage
- missing_relations:
  - gear is d or n -> gear is s [no]
  - gear is s -> set d_s gear mileage parameter = s gear nominal mileage / d gear nominal mileage [yes]
  - switch to driving mode -> gear check
  - gear check -> gear is d or e [case gear is d or e]
  - gear check -> gear is n or r [case gear is n or r]
- input_excerpt:
  After the system starts up, the process begins by checking the gear position. If the gear is in D or N, the D_S gear mileage parameter is set to 1, and the sequence ends. If the gear is in S, the D_S gear mileage parameter is calculated as S gear nominal mileage divided by D gear nominal mileage, then the process concludes. Additionally, if the vehicle status is 30, switch to driving mode. Next, if the gear is in D or E, set the D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage, and end. Finally, if the gear is in N or R, observe using the D_S gear mileage parameter and terminate the process.
- generated_excerpt:
  @startuml start :System starts up; :Check the gear position; switch (Gear position) case (D or N)   :Set D_S gear mileage parameter to 1; case (S)   :Calculate D_S gear mileage parameter as S gear nominal mileage divided by D gear nominal mileage; endswitch if (Vehicle status is 30?) then (yes)   :Switch to driving mode; endif switch (Gear position) case (D or E)   :Set D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage; case (N or R)   :Observe using the D_S gear mileage parameter; endswitch @enduml
### pure-0002
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5294
- relation_f1: 0.1500
- llm_element_status: success
- llm_node_f1: 0.8421
- llm_relation_f1: 0.2222
- missing_nodes:
  - testing records
  - include dates
  - include duration
  - compliance with requirements
  - units requirments
  - without external assistance
  - tests requirments
  - include key operating aids
- extra_nodes:
  - record testing dates
  - record testing duration
  - record compliance with requirements
  - include key operating aids (telephone communications and scada)
  - unit type?
  - meet start-up/synchronizing time limit (within 30 minutes)
  - meet applicable start-up/synchronizing time limit
- missing_relations:
  - notify caiso of test results -> testing records
  - testing records -> include dates [fork]
  - testing records -> include duration [fork]
  - testing records -> compliance with requirements [fork]
  - include dates -> units requirments [merge]
  - include duration -> units requirments [merge]
  - compliance with requirements -> units requirments [merge]
  - units requirments -> maintain voltage within emergency limits [fork]
- input_excerpt:
  Generator Unit Testing Steps (Minimal Requirements)Step 1: Owners of Voluntary Black Start units must demonstrate capability every five years, submit documentation, and notify the CAISO of test results.Step 2: Testing records must include dates, duration, and compliance with requirements.Step 3: Units must maintain voltage within emergency limits.Step 4: Units must have governors capable of isochronous mode.Step 5: Adequate transmission capacity must be available.Step 6: Units must start and energize transmission paths without external assistance.Step 7: Tests should include key operating aids like telephone communications and SCADA.Step 8: Start-up/synchronizing time limits apply based on u
- generated_excerpt:
  @startuml start :Demonstrate capability every five years; :Submit documentation; :Notify the CAISO of test results; :Record testing dates; :Record testing duration; :Record compliance with requirements; if (Adequate transmission capacity available?) then (yes) else (no)   stop endif :Start and energize transmission paths without external assistance; :Maintain voltage within emergency limits; :Ensure governors are capable of isochronous mode; :Include key operating aids (telephone communications and SCADA); switch (Unit type?) case (Hydro)   :Meet start-up/synchronizing time limit (within 30 minutes); case (Other)   :Meet applicable start-up/synchronizing time limit; endswitch :Meet minimum r
### lmc-0005
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.4000
- llm_element_status: success
- llm_node_f1: 0.9091
- llm_relation_f1: 0.7143
- missing_nodes:
  - exceeding sensor limits latch an autopilot pullup
- extra_nodes:
  - sensor limits exceeded?
  - latch autopilot pullup
- missing_relations:
  - system is supported without failures (not apfail)? -> exceeding sensor limits latch an autopilot pullup [yes]
- input_excerpt:
  1.	Exceeding sensor limits shall latch an autopilot pullup when the pilot is not in control (not standby) and the system is supported without failures (not apfail).
- generated_excerpt:
  @startuml start if (Sensor limits exceeded?) then (yes)   if (Pilot in control (standby)?) then (no)     if (System supported without failures (not apfail)?) then (yes)         :Latch autopilot pullup;       else (no)       endif     else (yes)     endif   else (no)   endif stop @enduml
### pure-0029
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.6000
- llm_element_status: success
- llm_node_f1: 0.7692
- llm_relation_f1: 0.4286
- missing_nodes:
  - data processing is incomplete
- extra_nodes:
  - buffer overflow?
  - data processing complete?
- missing_relations:
  - track buffer locations -> data processing is incomplete
- input_excerpt:
  Input Data Management - The BE shall store input data records in a memory buffer and track buffer locations of all input data until data processing is complete. Report any buffer overflow conditions.
- generated_excerpt:
  @startuml start :Store input data records in a memory buffer; :Track buffer locations of all input data; if (Buffer overflow?) then (yes)   :Report buffer overflow condition; else (no) endif; if (Data processing complete?) then (no)   :Store input data records in a memory buffer;   :Track buffer locations of all input data;   if (Buffer overflow?) then (yes)     :Report buffer overflow condition;   else (no)   endif;   stop else (yes) endif; stop @enduml
### lmc-0012
- dataset: lmc
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.6000
- extra_nodes:
  - remain in standby state
  - change state to transition
- missing_relations:
  - pilot is not in control (not standby)? -> autopilot change states from standby to transition [yes]
- input_excerpt:
  8.	The autopilot shall change states from STANDBY to TRANSITION when the pilot is not in control (not standby).
- generated_excerpt:
  @startuml start :Autopilot in STANDBY state; if (Pilot in control (standby)?) then (yes)   :Remain in STANDBY state; else (no)   :Change state to TRANSITION; endif @enduml
### us-0205
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.7500
- extra_nodes:
  - identify influential judge or legal thinker
  - read thesis paper
- missing_relations:
  - get thesis paper of influential judge or legal thinker -> gain insight into how initial scholarship start
- input_excerpt:
  As an academicresearcher, I want to the thesis paper of an influential judge or legal thinker to gain insight into how their initial scholarship got started.
- generated_excerpt:
  @startuml start :Identify influential judge or legal thinker; :Retrieve thesis paper of the judge or legal thinker; :Read thesis paper; :Gain insight into how their initial scholarship got started; @enduml
### rac-0007
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6842
- relation_f1: 0.4783
- llm_element_status: success
- llm_node_f1: 0.7442
- llm_relation_f1: 0.3636
- missing_nodes:
  - shutdown
  - battery pre-heating is required
  - flag becomes 0 and bms self-check counter is 1
  - cp duty cycle is 85 and cp amplitude is 3000
  - flag becomes 2
- extra_nodes:
  - system starts up
  - condition?
  - condition after switching to state 115?
  - shut down and end
  - condition after switching to state 110?
  - high-voltage shutdown request flag becomes 2
  - end
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging flag is 2
  - bms self-check counter is 1 -> battery pre-heating is required [no]
  - battery pre-heating is required -> switch to state 130 [yes]
  - flag becomes 0 and cp duty cycle is 85 -> flag becomes 0 and bms self-check counter is 1 [no]
  - flag becomes 0 and bms self-check counter is 1 -> switch to state 126 [yes]
  - switch to state 126 -> cp duty cycle is 85 and cp amplitude is 3000
  - cp duty cycle is 85 and cp amplitude is 3000 -> switch to state 130 [yes]
  - high-voltage shutdown request charging/discharging flag is 2 -> central control command is 2 and vehicle is not in charging/discharging mode [no]
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging active?) then (yes)   :Enter power-up mode;   switch (Condition?)   case (High-voltage shutdown request flag is 2)     :Switch to state 115;     switch (Condition after switching to state 115?)     case (Flag drops to 0 with CP duty cycle at 85%)       :Switch to state 126;     case (BMS self-check counter shows 1)       :Switch to state 130;     case (Slow charging becomes inactive)       :Shut down and end;     endswitch   case (Central control charging/discharging command is 2 and vehicle isn't in charging/discharging mode)     :Switch to state 110;     switch (Condition after switching to state 110?)     case (High-voltage shutdown req
### rac-0019
- dataset: rac
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7541
- relation_f1: 0.6111
- llm_element_status: success
- llm_node_f1: 0.8919
- llm_relation_f1: 0.4536
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
  - switch to state 29 -> ignition switch=0 and vcc2=12
  - fast charge vcc2=6 -> slow charging is active and charging system command=1 [no]
  - switch to state 110 -> charging system command=4
  - switch to state 29 -> ignition switch=0 and slow charging is inactive
  - switch to state 28 -> remote mode is disabled
  - switch to state 110 -> slow charging is inactive
  - switch to state 170 -> fast charging is inactive
  - switch to state 10 -> battery soc=20 and dcdc state=1
- input_excerpt:
  After the system starts up, if the ignition switch is set to 2, transition to state 30. Then, under that condition: - If the ignition switch becomes 0, move to state 49 and exit. - If the fast charge Vcc2 is 6, observe the charging gun indicator. Should the charging system command be 4, switch to state 29. - If the ignition switch is 0 and Vcc2 is 12, proceed to state 49 and exit. - If slow charging is active and the charging system command is 1, transition to state 110. If the command is 4 instead, go to state 29. Also, if the ignition switch is 0 and slow charging is not active, shift to state 49 and exit.  If remote mode is enabled, switch to state 28. If it's disabled, transition to stat
- generated_excerpt:
  @startuml start :System starts up; if (Ignition switch is set to 2?) then (yes)   :Transition to state 30;   if (Ignition switch becomes 0?) then (yes)     :Move to state 49;     :Exit;     stop   elseif (Fast charge Vcc2 is 6?) then (yes)     :Observe the charging gun indicator;     if (Charging system command is 4?) then (yes)       :Switch to state 29;       stop     else (no)       stop     endif   elseif (Ignition switch is 0 and Vcc2 is 12?) then (yes)     :Proceed to state 49;     :Exit;     stop   elseif (Slow charging is active and charging system command is 1?) then (yes)     :Transition to state 110;     stop   elseif (Slow charging is active and charging system command is 4?) the
### lmc-0002
- dataset: lmc
- failure_types: missing_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8571
- relation_f1: 0.2857
- llm_element_status: success
- llm_node_f1: 0.9091
- llm_relation_f1: 0.3636
- missing_nodes:
  - not affect method for determining selected value
- missing_relations:
  - in no-fail state -> mid-value be selected value
  - a first failure in progress? -> not affect method for determining selected value [yes]
  - a first failure in progress? -> not affect method for determining selected value [no]
- input_excerpt:
  [RM-002] In the no-fail state, the mid-value shall be the selected value.  Note: a first failure in progress will not affect the method for determining the selected value.
- generated_excerpt:
  @startuml start :In no-fail state; if (First failure in progress?) then (No)   :Mid-value is the selected value; else (Yes)   :Mid-value is the selected value; endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
