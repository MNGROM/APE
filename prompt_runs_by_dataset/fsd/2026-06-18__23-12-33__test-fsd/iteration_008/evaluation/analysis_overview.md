# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 0.9500
- infrastructure_error_rate: 0.0000
- node_precision: 0.4585
- node_recall: 0.4790
- node_f1: 0.4685
- relation_precision: 0.3675
- relation_recall: 0.4594
- relation_f1: 0.4084
- plantuml_compilation_pass_rate: 0.9500
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7625
- llm_node_recall: 0.7791
- llm_node_f1: 0.7538
- llm_relation_precision: 0.5325
- llm_relation_recall: 0.5203
- llm_relation_f1: 0.5042

## Failure Types
- extra_or_wrong_relation: 19
- extra_activity: 18
- missing_activity: 16
- missing_or_wrong_relation: 16
- wrong_parallel: 2
- syntax_error: 1

## Representative Failure Cases
### pure-0003
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.1000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8696
- llm_relation_f1: 0.2308
- missing_nodes:
  - caiso requirements
  - conduct tests with or without notice
  - determine when black start operation
  - test >= 1/3 rmr and interim black start units annually
  - possible test contents
  - self-providing start-up power
  - successive starts
  - reactive power production
- extra_nodes:
  - caiso determines black start operation is required?
  - caiso conducts performance tests?
  - with notice
  - perform performance test
  - without notice
  - annual testing selection
  - at least one-third of rmr and interim black start units
  - test selected units
- missing_relations:
  - units must satisfy caiso technical requirements -> caiso requirements
  - caiso requirements -> conduct tests with or without notice [fork]
  - caiso requirements -> determine when black start operation [fork]
  - caiso requirements -> test >= 1/3 rmr and interim black start units annually [fork]
  - conduct tests with or without notice -> possible test contents [merge]
  - determine when black start operation -> possible test contents [merge]
  - test >= 1/3 rmr and interim black start units annually -> possible test contents [merge]
  - possible test contents -> self-providing start-up power [fork]
- input_excerpt:
  [RMR & Interim Black Start Testing Steps]Step 1: Units must satisfy CAISO technical requirements.Step 2: The CAISO may conduct performance tests with or without notice.Step 3: The CAISO determines when Black Start operation is required.Step 4: The CAISO annually tests at least one-third of RMR and Interim Black Start units.Step 5: Units may be tested for self-providing start-up power.Step 6: Units may be tested for successive starts and reactive power production.
- generated_excerpt:
  @startuml start :Units satisfy CAISO technical requirements; if (CAISO determines Black Start operation is required?) then (yes)   switch (CAISO conducts performance tests?)   case (With notice)     :Perform performance test;   case (Without notice)     :Perform performance test;   endswitch   switch (Annual testing selection)   case (At least one-third of RMR and Interim Black Start units)     :Test selected units;   endswitch   fork     :Test unit for self-providing start-up power;   fork     :Test unit for successive starts and reactive power production;   end fork else (no) endif @enduml
### pure-0027
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.5000
- missing_nodes:
  - get correlator-backend network interface
  - receive incoming data packets
- extra_nodes:
  - receive incoming data packets from the correlator to backend network interface
- missing_relations:
  - get correlator-backend network interface -> receive incoming data packets
- input_excerpt:
  Data Receive – The BE shall receive incoming data packets from the Correlator to Backend network interface. This network is a part of the BE System.
- generated_excerpt:
  @startuml start :Receive incoming data packets from the Correlator to Backend network interface; note right: This network is a part of the BE System @enduml
### us-0198
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3636
- llm_relation_f1: 0.0000
- missing_nodes:
  - restrict a group of files from view
- extra_nodes:
  - select a group of files
  - enter a technical name
  - enter a description
  - restriction available?
  - apply restriction to the group of files
  - notify archivist restriction is unavailable
- input_excerpt:
  As an archivist, I want to restrict a group of files from view.
- generated_excerpt:
  @startuml start :Select a group of files; fork   :Enter a technical name; fork again   :Enter a description; end fork if (Restriction available?) then (yes)   :Apply restriction to the group of files; else (no)   :Notify archivist restriction is unavailable; endif stop @enduml
### us-0140
- dataset: us
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.1818
- llm_element_status: success
- llm_node_f1: 0.5000
- llm_relation_f1: 0.2500
- missing_nodes:
  - get an alfred device
  - adapt for user had hearing trouble
- extra_nodes:
  - start alfred device adaptation
  - user has hearing trouble?
  - enable hearing adaptation mode
  - increase audio volume
  - enable visual alerts
  - enable haptic feedback
  - keep standard mode
  - complete adaptation
- input_excerpt:
  As an OlderPerson, I want to have an ALFRED device that can be easily adapted for user that have hearing trouble.
- generated_excerpt:
  @startuml start :Start ALFRED device adaptation; if (User has hearing trouble?) then (yes)   :Enable hearing adaptation mode;   fork     :Increase audio volume;   fork again     :Enable visual alerts;   fork again     :Enable haptic feedback;   end fork else (no)   :Keep standard mode; endif :Complete adaptation; stop @enduml
### bp-0021
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3871
- relation_f1: 0.1667
- llm_element_status: success
- llm_node_f1: 0.9767
- llm_relation_f1: 0.9000
- missing_nodes:
  - click new job
  - the list of jobs is displayed
  - cick create
  - information is displayed
  - name
  - keywords
  - description
  - modification?
- extra_nodes:
  - the list of jobs in the promotionjob folder is displayed
  - the name of the job is displayed
  - the keywords of the job are displayed
  - the description of the job is displayed
  - modify required?
  - modify the displayed fields
  - you cannot change the source system
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
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :Click the Copy an Existing Job option; :The list of jobs in the PromotionJob folder is displayed; :Select a job from the job list; :click Create; fork :The name of the job is displayed; fork again :The keywords of the job are displayed; fork again :The description of the job is displayed; end fork if (Modify required?) then (Yes)   :Modify the displayed fields; else (No) endif :You cannot change the source system; :In the Save Job in field, browse and select the folder in which you want to save the job; :click Create; :A new job is created; @enduml
### us-0192
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.6667
- llm_relation_f1: 0.2500
- missing_nodes:
  - get time requesting material
- extra_nodes:
  - enter a technical name
  - enter a description
- missing_relations:
  - upload inventories -> get time requesting material
- input_excerpt:
  As an archivist, I want to upload inventories, so that our donor representatives have an easier time requesting their material.
- generated_excerpt:
  @startuml start :Upload inventories; fork     :Enter a technical name; fork again     :Enter a description; end fork stop @enduml
### us-0132
- dataset: us
- failure_types: missing_activity, extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.5000
- missing_nodes:
  - design own app
- extra_nodes:
  - design app
  - adjust design
- input_excerpt:
  As a developer, I want to be able to design my App on my own - though there will be a few rules I have to stand to.
- generated_excerpt:
  @startuml start :Design App; if (Stand to rules?) then (No)   :Adjust design;   stop else (Yes) endif stop @enduml
### bp-0030
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4571
- relation_f1: 0.5581
- llm_element_status: success
- llm_node_f1: 0.9756
- llm_relation_f1: 0.8085
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
  - enter the name for the job in the appropriate field
  - enter the description for the job in the appropriate field
  - enter the keywords for the job in the appropriate field
  - in the save job in field browse and select the folder in which you want to save the job
  - is the name of the system displayed in the drop-down list?
  - click the login to a new cms option
- missing_relations:
  - log in -> go to promotion jobs
  - click new job -> new job window appears
  - enter name -> go to save job field [merge]
  - enter description -> go to save job field [merge]
  - enter keywords -> go to save job field [merge]
  - go to save job field -> browse and select the folder
  - browse and select the folder -> drop-lists appears
  - drop-lists appears -> system name is displayed?
- input_excerpt:
  30.	Creating a New Job1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriate fields.4. In the Save Job in field, browse and select the folder in which you want to save the job.5. Select the source system and the destination system from the drop-down lists. If the name of the system is not displayed in the drop-down list, click the Login to a new CMS option. A new window is launched. Enter the name of the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; fork   :Enter the name for the job in the appropriate field; fork again   :Enter the description for the job in the appropriate field; fork again   :Enter the keywords for the job in the appropriate field; end fork :In the Save Job in field, browse and select the folder in which you want to save the job; :Select the source system from the drop-down list; :Select the destination system from the drop-down list; if (Is the name of the system displayed in the drop-down list?) then (No)   :Click the Login to a new CMS option;   :A new window is launched;   fork  
### pure-0021
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4615
- relation_f1: 0.1579
- llm_element_status: success
- llm_node_f1: 0.5946
- llm_relation_f1: 0.2500
- missing_nodes:
  - stationary?
  - manually select shunting
  - not allowed
  - automatic transfer?
  - speed <= supervised speed?
  - automatic transfer
  - exit
- extra_nodes:
  - is train stationary?
  - select shunting from
  - stand by operation
  - transfer to shunting
  - is speed <= supervised shunting speed based on trackside information?
  - automatic transition to shunting
  - in shunting mode
- missing_relations:
  - stationary? -> from stand by/full supervision/partial supervision operation [yes]
  - from stand by/full supervision/partial supervision operation -> manually select shunting
  - stationary? -> not allowed [no]
  - transfer to shunting on driver s selection? -> automatic transfer? [no]
  - manually select shunting -> automatic transfer?
  - not allowed -> automatic transfer?
  - automatic transfer? -> speed <= supervised speed? [yes]
  - speed <= supervised speed? -> from full supervision/partial supervision operation [yes]
- input_excerpt:
  Transfer to Shunting on driver's selection shall only be possible when stationary. It shall be possible to manually select Shunting from Stand By operation, Full Supervision operation, or Partial Supervision operation. Automatic transfer to Shunting may be from Full Supervision operation and Partial Supervision operation status at any speed lower than or equal to the supervised shunting speed based on trackside information. Before automatic transition to Shunting, ETCS shall request confirmation from the driver. Exit from Shunting shall only be possible when the train is stationary. Exit from Shunting shall take place when the driver selects exit from shunting.
- generated_excerpt:
  @startuml start :Driver selects transfer to Shunting; if (Is train stationary?) then (yes)   switch (Select Shunting from:)   case (Stand By operation)     :Transfer to Shunting;   case (Full Supervision operation)     :Transfer to Shunting;   case (Partial Supervision operation)     :Transfer to Shunting;   endswitch else (no) endif fork   :Full Supervision operation; fork again   :Partial Supervision operation; end fork if (Is speed <= supervised shunting speed based on trackside information?) then (yes)   :ETCS requests confirmation from driver;   :Automatic transition to Shunting; else (no) endif :In Shunting mode; if (Is train stationary?) then (yes)   if (Does driver select exit from s
### pure-0004
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4737
- relation_f1: 0.7317
- llm_element_status: success
- llm_node_f1: 0.7692
- llm_relation_f1: 0.6809
- missing_nodes:
  - request in the form
  - notify bs unit sc via telephone
  - ramp to requested mw
  - test
  - ramp down/continue market transaction
  - submit ambient temperature
  - submit 4 ambient temperature points
  - average mwh output
- extra_nodes:
  - request this in the form
  - notify the bs unit sc via telephone before the test starts
  - ramp to the requested mw before the test starts
  - post-test action
  - ramp down after the test
  - continue in market transaction after the test
  - submit ambient temperature information after the test
  - submit four ambient temperature points to the caiso
- missing_relations:
  - test -> ramp down/continue market transaction
  - ramp down/continue market transaction -> submit ambient temperature
  - submit ambient temperature -> submit 4 ambient temperature points
  - submit 4 ambient temperature points -> average mwh output
  - determine bs unit s availability -> output >= 99 ?
- input_excerpt:
  [RMR & Interim BS Unit Owner Actions]Step 1: Request an Availability Test at any time.Step 2: Submit a request using G-213H Black Start Test Report Form.Step 3: If testing above contract MNDC, request this in the form.Step 4: If a unit retests and passes, correct its Availability in SLIC.Alhambra Generation Dispatcher ActionsStep 5: Notify the BS Unit SC via telephone before the test starts.Step 6: Transmit an Availability Test Dispatch Notice before the test.[BS Generating Unit Operator Actions]Step 7: Ramp to the requested MW before the test starts.Step 8: Maintain the requested MW for four full hours.Step 9: Ramp down or continue in Market Transaction after the test.[RMR Generating Unit O
- generated_excerpt:
  @startuml |RMR & Interim BS Unit Owner| start :Request an Availability Test at any time; :Submit a request using G-213H Black Start Test Report Form; if (Testing above contract MNDC?) then (Yes)   :Request this in the form; endif if (Unit retests and passes?) then (Yes)   :Correct its Availability in SLIC; endif  |Alhambra Generation Dispatcher| :Notify the BS Unit SC via telephone before the test starts; :Transmit an Availability Test Dispatch Notice before the test;  |BS Generating Unit Operator| :Ramp to the requested MW before the test starts; :Maintain the requested MW for four full hours; switch (Post-test action) case (Ramp down)   :Ramp down after the test; case (Continue in Market T
### bp-0020
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.1667
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.6857
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - open source system drop-down list
  - select login
  - to a new cms
  - login to system dialog box appears
  - open destination system drop-down list
  - click create
- extra_nodes:
  - from the source system drop-down list select login to a new cms
  - from the destination system drop-down list select login to a new cms
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37 [yes]
  - more information? -> open source system drop-down list [no]
  - see creating a new job on page 37 -> open source system drop-down list [merge]
  - open source system drop-down list -> select login
  - to a new cms -> login to system dialog box appears
  - login to system dialog box appears -> enter user credentials
  - enter user credentials -> select appropriate authentication type
- input_excerpt:
  20.	log into a new CMS1. Log into the LifeCycle Manager tool.2. Create a new job.For more information on creating a new job, see Creating a New Job onpage 37.3. From the Source System drop-down list, select Login to a New CMS.The "Login to System" dialog box appears.4. Enter the user credentials, select the appropriate authentication type, andclick Login.5. From the Destination System drop-down list, select Login to a NewCMS.6. Enter the user credentials, select the appropriate authentication type, andclick Login.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :From the Source System drop-down list, select Login to a New CMS; fork   :Enter the user credentials; fork again   :Select the appropriate authentication type; end fork :Click Login; :From the Destination System drop-down list, select Login to a New CMS; fork   :Enter the user credentials; fork again   :Select the appropriate authentication type; end fork :Click Login; @enduml
### lmc-0029
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 0.8333
- llm_relation_f1: 0.1667
- missing_nodes:
  - in nlguidance
  - it is inertial position vector for aim point 1
  - compute the vector
- extra_nodes:
  - compute inertial position vector for aim point 1
- missing_relations:
  - in nlguidance -> vector define location at standoff 1 with offset from target position?
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? -> it is inertial position vector for aim point 1 [yes]
  - it is inertial position vector for aim point 1 -> compute the vector
- input_excerpt:
  2.	NLGuidance shall compute the inertial position vector for aim point 1, defining the location at Standoff 1 with an offset from the target position, and oriented on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point.
- generated_excerpt:
  @startuml start :Compute inertial position vector for aim point 1; :Define the location at Standoff 1 with an offset from the target position; :Orient on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point; stop @enduml
### rac-0006
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.3529
- llm_element_status: success
- llm_node_f1: 0.9730
- llm_relation_f1: 0.8372
- missing_nodes:
  - condition judgement
  - remote mode is enabled
  - shutdown
  - pet mode request handling is finished
  - battery soc is 20
  - battery soc reaches 80 and dcdc state is 3
- extra_nodes:
  - system starts up
  - condition?
  - enter state 110
  - slow charging becomes inactive?
  - go to state 28
  - shut down
  - move to state 28
  - soc reaches 80 and dcdc state is 3?
- missing_relations:
  - enter power-up mode -> condition judgement
  - condition judgement -> remote mode is enabled [case 1]
  - switch to state 28 -> remote mode is disabled
  - condition judgement -> pet mode request is received [case 2]
  - switch to state 28 -> pet mode request handling is finished
  - pet mode request handling is finished -> shutdown [yes]
  - condition judgement -> battery soc is 20 [case 3]
  - battery soc is 20 -> switch to state 110
- input_excerpt:
  After the system starts up: If slow charging is active, go into power-up mode. Then: 1.  If remote mode is enabled, enter state 110. Then, if slow charging becomes inactive, go to state 28. Finally, if remote mode is disabled, shut down and end. 2.  If a pet mode request comes in, switch to state 110. Then, if slow charging is inactive, move to state 28. Once the pet mode request is handled, shut down and end. 3.  If the battery SOC is 20, enter state 110. Then, if slow charging is inactive, switch to state 28. If the SOC later reaches 80 and the DCDC state is 3, shut down and end.
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?) then (Yes)   :Go into power-up mode;   switch (Condition?)   case (Remote mode is enabled)     :Enter state 110;     if (Slow charging becomes inactive?) then (Yes)       :Go to state 28;     endif     if (Remote mode is disabled?) then (Yes)       :Shut down;       end     endif   case (Pet mode request comes in)     :Switch to state 110;     if (Slow charging is inactive?) then (Yes)       :Move to state 28;     endif     :Pet mode request is handled;     :Shut down;     end   case (Battery SOC is 20)     :Enter state 110;     if (Slow charging is inactive?) then (Yes)       :Switch to state 28;     endif     if (SOC reaches 
### lmc-0015
- dataset: lmc
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - sensor change states from nominal to transition
- extra_nodes:
  - change state from nominal to transition
- input_excerpt:
  11.	The sensor shall change states from NOMINAL to TRANSITION when the autopilot is not requesting support (not request).
- generated_excerpt:
  @startuml start if (Autopilot is not requesting support (not request)?) then (yes)   :Change state from NOMINAL to TRANSITION; else (no) endif @enduml
### rac-0010
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5128
- relation_f1: 0.3509
- llm_element_status: success
- llm_node_f1: 0.7761
- llm_relation_f1: 0.4524
- missing_nodes:
  - high-voltage shutdown request is 2 and bms self-check counter is 1
  - high-voltage shutdown request is 2 and bms counter is 0
  - switch to state 127
  - switch state 127
  - condition judgement
  - shutdown
  - stay in state 127
- extra_nodes:
  - system starts up
  - high-voltage shutdown request == 2?
  - move to state 126
  - continue
  - fast charging becomes active and front mcu initialization state == 0?
  - transition to state 127
  - 2.2-second timeout triggers?
  - system shuts down and ends
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request is 2 and bms self-check counter is 1
  - high-voltage shutdown request is 2 and bms self-check counter is 1 -> enter state 126 [yes]
  - high-voltage shutdown request is 2 and bms self-check counter is 1 -> high-voltage shutdown request is 2 and bms counter is 0 [no]
  - high-voltage shutdown request is 2 and bms counter is 0 -> enter state 126 [yes]
  - front mcu low-voltage shutdown flag is 0 -> condition judgement [no]
  - switch to state 127 -> condition judgement
  - switch state 127 -> condition judgement
  - enter state 126 -> condition judgement
- input_excerpt:
  After the system starts up and slow charging is active, it enters power-up mode. Then, if the high-voltage shutdown request (for charging or discharging) is 2, the system moves to state 126 regardless of whether the BMS self-check counter is 0 or 1.  While in state 126: - If fast charging becomes active and the front MCU initialization state is 0, it transitions to state 127. - Similarly, if the front MCU low-voltage shutdown flag is 0, it also transitions to state 127. - Additionally, the following checks occur:   1. If a 2.2-second timeout triggers, it switches to state 142. Should fast charging be inactive at this point, the system shuts down and ends.   2. If the BMS counter reads 0, it 
- generated_excerpt:
  @startuml start :System starts up; :Slow charging is active; :Enter power-up mode; if (High-voltage shutdown request == 2?) then (yes)   :Move to state 126; else (no)   :Continue;   stop endif repeat :State 126;   fork     if (Fast charging becomes active AND front MCU initialization state == 0?) then (yes)       :Transition to state 127;     elseif (Front MCU low-voltage shutdown flag == 0?) then (yes)       :Transition to state 127;     else (no)     endif   fork again     if (2.2-second timeout triggers?) then (yes)       :Switch to state 142;       if (Fast charging is inactive?) then (yes)         :System shuts down and ends;         stop       else (no)       endif     else (no)     en
### bp-0003
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5490
- relation_f1: 0.5263
- llm_element_status: success
- llm_node_f1: 0.8421
- llm_relation_f1: 0.9836
- missing_nodes:
  - the info area is displayed
  - open context menu
  - enter zd_sales as the technical name
  - choose create new dimensions
  - open the toolbar on the left
  - choose info object catalog
  - info object catalog is displayed
  - choose info object direct input
- extra_nodes:
  - you are in the modeling functional area of the data warehousing workbench
  - the info area created previously in the info object tree is also displayed in the info provider tree
  - it contains the characteristics that were dened as info provider and is used to group further objects
  - enter zd_sales as the technical name under info cube
  - choose create new dimensions in the context menu of the folder dimensions
  - in the toolbar in the left area choose info object catalog
  - the info object catalog is displayed in the left area with the characteristics you created
  - assign the characteristics to the dimensions as follows with drag and drop
- missing_relations:
  - the info area is displayed -> open context menu
  - open context menu -> choose create info cube
  - screen for info cube editing is shown -> open context menu
  - open context menu -> choose create new dimensions
  - choose create new dimensions -> enter product as the new dimension description
  - open the toolbar on the left -> choose info object catalog
  - choose continue -> info object catalog is displayed
  - info object catalog is displayed -> open context menu
- input_excerpt:
  3.	Creating Data sources for Master Data of Characteristic "Product"1. You are in the Modeling functional area of the Data Warehousing Workbench2. Choose Info Provider. The Info Provider tree is displayed. The Info Area created previously in the Info Object tree is also displayed in the Info Provider tree. It contains the characteristics that were dened as Info Provider and is used to group further objects.3. In the context menu of the Info Area, choose Create Info Cube.4. In the next screen, enter ZD_SALES as the technical name under Info Cube and Sales Overview as the description.5. Select Standard Info Cube as Info Provider Type and choose Create. You go to the screen for Info Cube editin
- generated_excerpt:
  @startuml start :You are in the Modeling functional area of the Data Warehousing Workbench; :Choose Info Provider; :The Info Provider tree is displayed; :The Info Area created previously in the Info Object tree is also displayed in the Info Provider tree; :It contains the characteristics that were dened as Info Provider and is used to group further objects; :In the context menu of the Info Area, choose Create Info Cube; fork   :Enter ZD_SALES as the technical name under Info Cube; fork again   :Enter Sales Overview as the description; end fork :Select Standard Info Cube as Info Provider Type; :Choose Create; :You go to the screen for Info Cube editing; :Choose Create New Dimensions in the co
### lmc-0026
- dataset: lmc
- failure_types: extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.6000
- llm_relation_f1: 0.2222
- extra_nodes:
  - do not command transient change
  - command transient change
- input_excerpt:
  9.	The Inner Loop Airspeed Regulator Shall not command transient changes in translational axial acceleration greater than 32 ft/sec2/sec.
- generated_excerpt:
  @startuml start :Command Inner Loop Airspeed Regulator; if (Transient change in translational axial acceleration > 32 ft/sec2/sec?) then (Yes)   :Do not command transient change; else (No)   :Command transient change; endif stop @enduml
### rac-0002
- dataset: rac
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8571
- relation_f1: 0.6087
- llm_element_status: success
- llm_node_f1: 0.9231
- llm_relation_f1: 0.7500
- missing_nodes:
  - gear check
- extra_nodes:
  - check the gear position
  - calculate d_s gear mileage parameter as s gear nominal mileage divided by d gear nominal mileage
- missing_relations:
  - switch to driving mode -> gear check
  - gear check -> gear is d or e [case gear is d or e]
  - gear check -> gear is n or r [case gear is n or r]
- input_excerpt:
  After the system starts up, the process begins by checking the gear position. If the gear is in D or N, the D_S gear mileage parameter is set to 1, and the sequence ends. If the gear is in S, the D_S gear mileage parameter is calculated as S gear nominal mileage divided by D gear nominal mileage, then the process concludes. Additionally, if the vehicle status is 30, switch to driving mode. Next, if the gear is in D or E, set the D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage, and end. Finally, if the gear is in N or R, observe using the D_S gear mileage parameter and terminate the process.
- generated_excerpt:
  @startuml start :Check the gear position; if (Gear is in D or N?) then (yes)   :Set the D_S gear mileage parameter to 1; else (no)   if (Gear is in S?) then (yes)     :Calculate D_S gear mileage parameter as S gear nominal mileage divided by D gear nominal mileage;   endif endif if (Vehicle status is 30?) then (yes)   :Switch to driving mode; endif if (Gear is in D or E?) then (yes)   :Set the D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage; else (no)   if (Gear is in N or R?) then (yes)     :Observe using the D_S gear mileage parameter;   endif endif @enduml
### rac-0018
- dataset: rac
- failure_types: missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8889
- relation_f1: 0.6885
- llm_element_status: success
- llm_node_f1: 0.0000
- llm_relation_f1: 0.0000
- missing_nodes:
  - shutdown
  - condition judgement
- extra_nodes:
  - system starts up
  - shut down and exit
- missing_relations:
  - pre-charge failure -> slow charging is inactive [no]
  - switch to state 95 -> power-up readiness and pre-heating demand exist
  - front mcu high-voltage flag=1 and charging/discharging power-up=1 -> front mcu high-voltage flag=1 and power-up readiness [no]
  - switch to state 93 -> condition judgement
  - condition judgement -> vehicle charging/discharging mode=1 and power battery charging demand=2 [case vehicle charging/discharging mode=1 and power battery charging demand=2]
  - condition judgement -> charging/discharging power-up guidance=2 or 3 [case charging/discharging power-up guidance=2 or 3]
  - condition judgement -> vehicle charging/discharging mode=1 [case vehicle charging/discharging mode=1]
  - condition judgement -> power battery charging demand=2 [case power battery charging demand=2]
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU high-voltage detection flag is 0, it switches to state 93. Then: 1. If the front MCU high-voltage flag is 1 and charging/discharging power-up is 1, the system switches to state 95.    a. If a pre-charge failure occurs, it switches to state 115. Additionally, if slow charging is inactive, the system shuts down and exits.    b. If an AC charging/discharging system fault occurs, it switches to state 115. Also, if slow charging is inactive, it shuts down and exits.    c. If slow charging is inactive, it switches to state 115 and then shuts down and exits. 2. If the DCDC state is 1 and there is no battery pre-heating demand,
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active\nand front MCU high-voltage\ndetection flag is 0?) then (yes)   :Switch to state 93;   if (Front MCU high-voltage flag is 1\nand charging/discharging\npower-up is 1?) then (yes)     :Switch to state 95;     if (Pre-charge failure occurs?) then (yes)       :Switch to state 115;       if (Slow charging is inactive?) then (yes)         :Shut down and exit;         stop       else (no)       endif     elseif (AC charging/discharging\nsystem fault occurs?) then (yes)       :Switch to state 115;       if (Slow charging is inactive?) then (yes)         :Shut down and exit;         stop       else (no)       endif     elseif (Slow chargi
### lmc-0002
- dataset: lmc
- failure_types: missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 1.0000
- relation_f1: 0.5714
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.6154
- missing_relations:
  - mid-value be selected value -> a first failure in progress?
  - a first failure in progress? -> not affect method for determining selected value [no]
- input_excerpt:
  [RM-002] In the no-fail state, the mid-value shall be the selected value.  Note: a first failure in progress will not affect the method for determining the selected value.
- generated_excerpt:
  @startuml start if (In no-fail state?) then (yes)   :Mid-value shall be the selected value; else (no)   if (First failure in progress?) then (yes)     :Will not affect the method for determining the selected value;   else (no)   endif endif @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
