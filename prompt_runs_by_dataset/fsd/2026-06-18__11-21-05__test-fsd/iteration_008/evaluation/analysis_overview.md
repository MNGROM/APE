# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4853
- node_recall: 0.4695
- node_f1: 0.4772
- relation_precision: 0.3960
- relation_recall: 0.3410
- relation_f1: 0.3665
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8740
- llm_node_recall: 0.7873
- llm_node_f1: 0.8196
- llm_relation_precision: 0.6329
- llm_relation_recall: 0.5245
- llm_relation_f1: 0.5585

## Failure Types
- extra_activity: 18
- missing_or_wrong_relation: 18
- missing_activity: 17
- extra_or_wrong_relation: 17
- wrong_parallel: 4
- wrong_loop: 1

## Representative Failure Cases
### lmc-0015
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.3333
- missing_nodes:
  - autopilot is not requesting support (not request)?
  - sensor change states from nominal to transition
- extra_nodes:
  - change state from nominal to transition
- missing_relations:
  - autopilot is not requesting support (not request)? -> sensor change states from nominal to transition [yes]
- input_excerpt:
  11.	The sensor shall change states from NOMINAL to TRANSITION when the autopilot is not requesting support (not request).
- generated_excerpt:
  @startuml start partition Sensor {   :Change state from NOMINAL to TRANSITION; } stop @enduml
### pure-0027
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.8000
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
  @startuml partition "BE System" {   start   :Receive incoming data packets from the Correlator to Backend network interface;   stop } @enduml
### bp-0030
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.1765
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.4500
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
  - log into the lifecycle manager tool.
  - in the promotion jobs home page click new job.
  - enter the name description and keywords for the job in the appropriate fields.
  - in the save job in field browse and select the folder in which you want to save the job.
  - select the source system and the destination system from the drop-down lists.
  - is the name of the system displayed in the drop-down list?
  - click the login to a new cms option.
  - enter the name of the system along with the user name and password.
- missing_relations:
  - log in -> go to promotion jobs
  - click new job -> new job window appears
  - new job window appears -> enter name [fork]
  - new job window appears -> enter description [fork]
  - new job window appears -> enter keywords [fork]
  - enter name -> go to save job field [merge]
  - enter description -> go to save job field [merge]
  - enter keywords -> go to save job field [merge]
- input_excerpt:
  30.	Creating a New Job1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriate fields.4. In the Save Job in field, browse and select the folder in which you want to save the job.5. Select the source system and the destination system from the drop-down lists. If the name of the system is not displayed in the drop-down list, click the Login to a new CMS option. A new window is launched. Enter the name of the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start partition User {     :Log into the LifeCycle Manager tool.;     :In the "Promotion Jobs" home page, click New Job.; } partition System {     :The "New Job" window appears.; } partition User {     :Enter the name, description, and keywords for the job in the appropriate fields.;     :In the Save Job in field, browse and select the folder in which you want to save the job.;     :Select the source system and the destination system from the drop-down lists.;     if (Is the name of the system displayed in the drop-down list?) then (No)         :Click the Login to a new CMS option.;         partition System {             :A new window is launched.;         }         partition User 
### pure-0021
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2963
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7097
- llm_relation_f1: 0.4651
- missing_nodes:
  - transfer to shunting on driver s selection?
  - manually select shunting
  - not allowed
  - automatic transfer?
  - speed <= supervised speed?
  - etcs requests driver confirmation
  - automatic transfer
  - driver selects exit from shunting
- extra_nodes:
  - select shunting
  - current operation?
  - stand by operation
  - transfer to shunting
  - evaluate speed and trackside information
  - automatic transfer to shunting from full supervision operation or partial supervision operation at speed <= supervised shunting speed
  - request confirmation from driver
  - confirmation received?
- missing_relations:
  - transfer to shunting on driver s selection? -> stationary? [yes]
  - stationary? -> from stand by/full supervision/partial supervision operation [yes]
  - from stand by/full supervision/partial supervision operation -> manually select shunting
  - stationary? -> not allowed [no]
  - transfer to shunting on driver s selection? -> automatic transfer? [no]
  - manually select shunting -> automatic transfer?
  - not allowed -> automatic transfer?
  - automatic transfer? -> speed <= supervised speed? [yes]
- input_excerpt:
  Transfer to Shunting on driver's selection shall only be possible when stationary. It shall be possible to manually select Shunting from Stand By operation, Full Supervision operation, or Partial Supervision operation. Automatic transfer to Shunting may be from Full Supervision operation and Partial Supervision operation status at any speed lower than or equal to the supervised shunting speed based on trackside information. Before automatic transition to Shunting, ETCS shall request confirmation from the driver. Exit from Shunting shall only be possible when the train is stationary. Exit from Shunting shall take place when the driver selects exit from shunting.
- generated_excerpt:
  @startuml start partition Driver {     :Select Shunting; } if (Stationary?) then (Yes)     switch (Current operation?)     case (Stand By operation)         :Transfer to Shunting;     case (Full Supervision operation)         :Transfer to Shunting;     case (Partial Supervision operation)         :Transfer to Shunting;     endswitch else (No)     stop endif  partition ETCS {     :Evaluate speed and trackside information; } repeat :Automatic transfer to Shunting from Full Supervision operation or Partial Supervision operation at speed <= supervised shunting speed; partition ETCS {     :Request confirmation from driver; } repeat while (Confirmation received?) is (No) ->Yes;  partition Driver {
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
  - modify the name keywords and description of the job if required
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
  @startuml start partition User {     :Log into the LifeCycle Manager tool;     :In the "Promotion Jobs" home page, click New Job;     :Click the Copy an Existing Job option; } partition System {     :The list of jobs in the PromotionJob folder is displayed; } partition User {     :Select a job from the job list, and click Create; } partition System {     :The name, keywords, and description of the job are displayed; } partition User {     :Modify the name, keywords, and description of the job, if required;     :In the Save Job in field, browse and select the folder in which you want to save the job, and click Create; } partition System {     :A new job is created; } stop @enduml
### lmc-0002
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 0.8000
- llm_relation_f1: 0.6000
- missing_nodes:
  - in no-fail state
  - a first failure in progress?
  - not affect method for determining selected value
- extra_nodes:
  - state?
- missing_relations:
  - a first failure in progress? -> not affect method for determining selected value [yes]
  - a first failure in progress? -> not affect method for determining selected value [no]
- input_excerpt:
  [RM-002] In the no-fail state, the mid-value shall be the selected value.  Note: a first failure in progress will not affect the method for determining the selected value.
- generated_excerpt:
  @startuml start if (State?) then (no-fail state)   :Select the mid-value as the selected value; elseif (first failure in progress) then (first failure in progress)   :Select the mid-value as the selected value; endif stop @enduml
### lmc-0026
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4444
- llm_relation_f1: 0.2857
- missing_nodes:
  - in inner loop airspeed regulator
- extra_nodes:
  - command translational axial acceleration
  - do not command transient change
- missing_relations:
  - in inner loop airspeed regulator -> command transient changes in translational axial acceleration <= 32 ft/sec2/sec
- input_excerpt:
  9.	The Inner Loop Airspeed Regulator Shall not command transient changes in translational axial acceleration greater than 32 ft/sec2/sec.
- generated_excerpt:
  @startuml start partition "Inner Loop Airspeed Regulator" {   :Command translational axial acceleration;   if (Transient change in translational axial acceleration > 32 ft/sec2/sec?) then (yes)     :Do not command transient change;     stop   else (no)   endif } @enduml
### pure-0003
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7778
- llm_relation_f1: 0.0952
- missing_nodes:
  - units must satisfy caiso technical requirements
  - caiso requirements
  - conduct tests with or without notice
  - possible test contents
  - successive starts
  - reactive power production
- extra_nodes:
  - satisfy caiso technical requirements
  - conduct performance tests with or without notice
  - may be tested for successive starts and reactive power production
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
  @startuml start partition "Units" {   :Satisfy CAISO technical requirements; } partition "CAISO" {   :Conduct performance tests with or without notice;   :Determine when Black Start operation is required;   :Annually test at least one-third of RMR and Interim Black Start units; } partition "Units" {   :May be tested for self-providing start-up power;   :May be tested for successive starts and reactive power production; } @enduml
### us-0192
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - get time requesting material
- extra_nodes:
  - request material
- missing_relations:
  - upload inventories -> get time requesting material
- input_excerpt:
  As an archivist, I want to upload inventories, so that our donor representatives have an easier time requesting their material.
- generated_excerpt:
  @startuml start partition Archivist {   :Upload inventories; } partition DonorRepresentative {   :Request material; } stop @enduml
### pure-0004
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 0.7692
- llm_element_status: success
- llm_node_f1: 0.9500
- llm_relation_f1: 0.7727
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
  - ramp down or continue in market transaction after the test
  - submit ambient temperature information after the test
  - submit four ambient temperature points to the caiso
  - determine the bs unit s availability by averaging mwh output
  - output meets 99 threshold?
- missing_relations:
  - ramp to requested mw -> maintain requested mw for 4 hours
  - test -> ramp down/continue market transaction
  - submit ambient temperature -> submit 4 ambient temperature points
  - submit 4 ambient temperature points -> average mwh output
  - determine bs unit s availability -> output >= 99 ?
- input_excerpt:
  [RMR & Interim BS Unit Owner Actions]Step 1: Request an Availability Test at any time.Step 2: Submit a request using G-213H Black Start Test Report Form.Step 3: If testing above contract MNDC, request this in the form.Step 4: If a unit retests and passes, correct its Availability in SLIC.Alhambra Generation Dispatcher ActionsStep 5: Notify the BS Unit SC via telephone before the test starts.Step 6: Transmit an Availability Test Dispatch Notice before the test.[BS Generating Unit Operator Actions]Step 7: Ramp to the requested MW before the test starts.Step 8: Maintain the requested MW for four full hours.Step 9: Ramp down or continue in Market Transaction after the test.[RMR Generating Unit O
- generated_excerpt:
  @startuml start  partition "RMR & Interim BS Unit Owner" {   :Request an Availability Test at any time;   :Submit a request using G-213H Black Start Test Report Form;   if (Testing above contract MNDC?) then (Yes)     :Request this in the form;   else (No)   endif   if (Unit retests and passes?) then (Yes)     :Correct its Availability in SLIC;   else (No)   endif }  partition "Alhambra Generation Dispatcher" {   :Notify the BS Unit SC via telephone before the test starts;   :Transmit an Availability Test Dispatch Notice before the test; }  partition "BS Generating Unit Operator" {   :Ramp to the requested MW before the test starts;   :Maintain the requested MW for four full hours;   :Ramp d
### us-0132
- dataset: us
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - design own app
- extra_nodes:
  - design app
- input_excerpt:
  As a developer, I want to be able to design my App on my own - though there will be a few rules I have to stand to.
- generated_excerpt:
  @startuml start partition Developer {   :Design App;   :Stand to a few rules; } stop @enduml
### us-0140
- dataset: us
- failure_types: missing_activity, extra_activity
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5000
- relation_f1: 1.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 1.0000
- missing_nodes:
  - adapt for user had hearing trouble
- extra_nodes:
  - adapt alfred device for hearing trouble
- input_excerpt:
  As an OlderPerson, I want to have an ALFRED device that can be easily adapted for user that have hearing trouble.
- generated_excerpt:
  @startuml start partition OlderPerson {  :Have an ALFRED device;  :Adapt ALFRED device for hearing trouble; } stop @enduml
### rac-0010
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5143
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.8372
- llm_relation_f1: 0.5915
- missing_nodes:
  - high-voltage shutdown request is 2 and bms self-check counter is 1
  - enter state 126
  - high-voltage shutdown request is 2 and bms counter is 0
  - switch to state 127
  - switch state 127
  - condition judgement
  - shutdown
  - stay in state 127
- extra_nodes:
  - system starts up
  - high-voltage shutdown request is 2?
  - move to state 126
  - in state 126?
  - fast charging becomes active and front mcu initialization state is 0?
  - transition to state 127
  - 2.2-second timeout triggers?
  - system shuts down
- missing_relations:
  - slow charging is active -> fast charging is active and front mcu initialization state is 0 [no]
  - enter power-up mode -> high-voltage shutdown request is 2 and bms self-check counter is 1
  - high-voltage shutdown request is 2 and bms self-check counter is 1 -> enter state 126 [yes]
  - high-voltage shutdown request is 2 and bms self-check counter is 1 -> high-voltage shutdown request is 2 and bms counter is 0 [no]
  - high-voltage shutdown request is 2 and bms counter is 0 -> enter state 126 [yes]
  - switch to state 127 -> condition judgement [merge]
  - switch state 127 -> condition judgement [merge]
  - condition judgement -> timeout 2.2s occurs [case timeout 2.2s occurs]
- input_excerpt:
  After the system starts up and slow charging is active, it enters power-up mode. Then, if the high-voltage shutdown request (for charging or discharging) is 2, the system moves to state 126 regardless of whether the BMS self-check counter is 0 or 1.  While in state 126: - If fast charging becomes active and the front MCU initialization state is 0, it transitions to state 127. - Similarly, if the front MCU low-voltage shutdown flag is 0, it also transitions to state 127. - Additionally, the following checks occur:   1. If a 2.2-second timeout triggers, it switches to state 142. Should fast charging be inactive at this point, the system shuts down and ends.   2. If the BMS counter reads 0, it 
- generated_excerpt:
  @startuml start :System starts up; :Slow charging is active; :Enter power-up mode; if (High-voltage shutdown request is 2?) then (yes)   :Move to state 126; else (no)   stop endif while (In state 126?) is (yes)   if (Fast charging becomes active and front MCU initialization state is 0?) then (yes)     :Transition to state 127;     stop   elseif (Front MCU low-voltage shutdown flag is 0?) then (yes)     :Transition to state 127;     stop   elseif (2.2-second timeout triggers?) then (yes)     :Switch to state 142;     if (Fast charging is inactive?) then (yes)       :System shuts down;       stop     else (no)     endif   elseif (BMS counter reads 0?) then (yes)     :Switch to state 142;     i
### bp-0020
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.4348
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.6875
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - open source system drop-down list
  - select login
  - to a new cms
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
  - click login -> open destination system drop-down list
  - open destination system drop-down list -> select login
- input_excerpt:
  20.	log into a new CMS1. Log into the LifeCycle Manager tool.2. Create a new job.For more information on creating a new job, see Creating a New Job onpage 37.3. From the Source System drop-down list, select Login to a New CMS.The "Login to System" dialog box appears.4. Enter the user credentials, select the appropriate authentication type, andclick Login.5. From the Destination System drop-down list, select Login to a NewCMS.6. Enter the user credentials, select the appropriate authentication type, andclick Login.
- generated_excerpt:
  @startuml start partition User {     :Log into the LifeCycle Manager tool;     :Create a new job;     :From the Source System drop-down list, select Login to a New CMS; } partition System {     :The "Login to System" dialog box appears; } partition User {     :Enter the user credentials;     :Select the appropriate authentication type;     :Click Login;     :From the Destination System drop-down list, select Login to a New CMS;     :Enter the user credentials;     :Select the appropriate authentication type;     :Click Login; } @enduml
### bp-0003
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5833
- relation_f1: 0.4528
- llm_element_status: success
- llm_node_f1: 0.8889
- llm_relation_f1: 0.7667
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
  - display the info area created previously in the info object tree
  - enter zd_sales as the technical name under info cube
  - choose create new dimensions in the context menu of the folder dimensions
  - choose info object catalog in the toolbar in the left area
  - display the info object catalog in the left area with the characteristics you created
  - assign the characteristics to the dimensions with drag and drop
  - choose info object direct input in the context menu of the dimension sales organization
  - enter the characteristic 0doc_number ( sales document )
- missing_relations:
  - info provider tree is displayed -> the info area is displayed
  - the info area is displayed -> open context menu
  - open context menu -> choose create info cube
  - choose create info cube -> enter sales overview as the description [fork]
  - enter zd_sales as the technical name -> select standard info cube as info provider type [merge]
  - screen for info cube editing is shown -> open context menu
  - open context menu -> choose create new dimensions
  - choose create new dimensions -> enter product as the new dimension description
- input_excerpt:
  3.	Creating Data sources for Master Data of Characteristic "Product"1. You are in the Modeling functional area of the Data Warehousing Workbench2. Choose Info Provider. The Info Provider tree is displayed. The Info Area created previously in the Info Object tree is also displayed in the Info Provider tree. It contains the characteristics that were dened as Info Provider and is used to group further objects.3. In the context menu of the Info Area, choose Create Info Cube.4. In the next screen, enter ZD_SALES as the technical name under Info Cube and Sales Overview as the description.5. Select Standard Info Cube as Info Provider Type and choose Create. You go to the screen for Info Cube editin
- generated_excerpt:
  @startuml start partition "User" {   :Choose Info Provider; } partition "System" {   :Display Info Provider tree;   :Display the Info Area created previously in the Info Object tree; } partition "User" {   :Choose Create Info Cube in the context menu of the Info Area;   :Enter ZD_SALES as the technical name under Info Cube;   :Enter Sales Overview as the description;   :Select Standard Info Cube as Info Provider Type;   :Choose Create; } partition "System" {   :Go to the screen for Info Cube editing; } partition "User" {   :Choose Create New Dimensions in the context menu of the folder Dimensions;   :Enter Product as the description for the new dimension;   :Choose Create Another Dimension; 
### rac-0006
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6000
- relation_f1: 0.4000
- llm_element_status: success
- llm_node_f1: 0.9167
- llm_relation_f1: 0.6667
- missing_nodes:
  - condition judgement
  - shutdown
  - pet mode request handling is finished
  - battery soc reaches 80 and dcdc state is 3
- extra_nodes:
  - system starts up
  - enter state 110
  - slow charging becomes inactive?
  - go to state 28
  - shut down
  - pet mode request comes in?
  - move to state 28
  - soc reaches 80 and dcdc state is 3?
- missing_relations:
  - enter power-up mode -> condition judgement
  - condition judgement -> remote mode is enabled [case remote mode is enabled]
  - switch to state 28 -> remote mode is disabled
  - condition judgement -> pet mode request is received [case pet mode request is received]
  - switch to state 28 -> pet mode request handling is finished
  - pet mode request handling is finished -> shutdown [yes]
  - condition judgement -> battery soc is 20 [case battery soc is 20]
  - switch to state 28 -> battery soc reaches 80 and dcdc state is 3
- input_excerpt:
  After the system starts up: If slow charging is active, go into power-up mode. Then: 1.  If remote mode is enabled, enter state 110. Then, if slow charging becomes inactive, go to state 28. Finally, if remote mode is disabled, shut down and end. 2.  If a pet mode request comes in, switch to state 110. Then, if slow charging is inactive, move to state 28. Once the pet mode request is handled, shut down and end. 3.  If the battery SOC is 20, enter state 110. Then, if slow charging is inactive, switch to state 28. If the SOC later reaches 80 and the DCDC state is 3, shut down and end.
- generated_excerpt:
  @startuml start partition System {   :System starts up;   if (Slow charging is active?) then (yes)     :Go into power-up mode;     if (Remote mode is enabled?) then (yes)       :Enter state 110;       if (Slow charging becomes inactive?) then (yes)         :Go to state 28;       endif       if (Remote mode is disabled?) then (yes)         :Shut down;         stop       endif     elseif (Pet mode request comes in?) then (yes)       :Switch to state 110;       if (Slow charging is inactive?) then (yes)         :Move to state 28;       endif       :Pet mode request is handled;       :Shut down;       stop     elseif (Battery SOC is 20?) then (yes)       :Enter state 110;       if (Slow charging
### us-0198
- dataset: us
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6667
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.8571
- llm_relation_f1: 0.4000
- extra_nodes:
  - select a group of files
- input_excerpt:
  As an archivist, I want to restrict a group of files from view.
- generated_excerpt:
  @startuml start partition Archivist {   :Select a group of files;   :Restrict the group of files from view; } stop @enduml
### rac-0002
- dataset: rac
- failure_types: extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6923
- relation_f1: 0.5385
- llm_element_status: success
- llm_node_f1: 0.7742
- llm_relation_f1: 0.4444
- missing_nodes:
  - gear check
- extra_nodes:
  - system starts up
  - check the gear position
  - sequence ends
  - calculate d_s gear mileage parameter as s gear nominal mileage divided by d gear nominal mileage
  - process concludes
  - end
  - terminate the process
- missing_relations:
  - switch to driving mode -> gear check
  - gear check -> gear is d or e [case gear is d or e]
  - gear check -> gear is n or r [case gear is n or r]
- input_excerpt:
  After the system starts up, the process begins by checking the gear position. If the gear is in D or N, the D_S gear mileage parameter is set to 1, and the sequence ends. If the gear is in S, the D_S gear mileage parameter is calculated as S gear nominal mileage divided by D gear nominal mileage, then the process concludes. Additionally, if the vehicle status is 30, switch to driving mode. Next, if the gear is in D or E, set the D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage, and end. Finally, if the gear is in N or R, observe using the D_S gear mileage parameter and terminate the process.
- generated_excerpt:
  @startuml start :System starts up; :Check the gear position; if (Gear is in D or N?) then (yes)   :Set the D_S gear mileage parameter to 1;   :Sequence ends;   stop elseif (Gear is in S?) then (yes)   :Calculate D_S gear mileage parameter as S gear nominal mileage divided by D gear nominal mileage;   :Process concludes;   stop endif if (Vehicle status is 30?) then (yes)   :Switch to driving mode; endif if (Gear is in D or E?) then (yes)   :Set the D_S gear mileage parameter to S gear nominal mileage divided by D gear nominal mileage;   :End;   stop elseif (Gear is in N or R?) then (yes)   :Observe using the D_S gear mileage parameter;   :Terminate the process;   stop else (no) endif @enduml
### lmc-0029
- dataset: lmc
- failure_types: missing_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7500
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 0.8333
- llm_relation_f1: 0.1667
- missing_nodes:
  - in nlguidance
  - compute the vector
- missing_relations:
  - in nlguidance -> vector define location at standoff 1 with offset from target position?
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? -> it is inertial position vector for aim point 1 [yes]
  - it is inertial position vector for aim point 1 -> compute the vector
- input_excerpt:
  2.	NLGuidance shall compute the inertial position vector for aim point 1, defining the location at Standoff 1 with an offset from the target position, and oriented on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point.
- generated_excerpt:
  @startuml start partition NLGuidance {   :Compute the inertial position vector for aim point 1;   :Define the location at Standoff 1 with an offset from the target position;   :Orient on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point; } stop @enduml
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
  - switch to state 93 -> front mcu high-voltage flag=1 and charging/discharging power-up=1
  - switch to state 95 -> power-up readiness and pre-heating demand exist
  - front mcu high-voltage flag=1 and charging/discharging power-up=1 -> front mcu high-voltage flag=1 and power-up readiness [no]
  - switch to state 93 -> condition judgement
  - condition judgement -> vehicle charging/discharging mode=1 and power battery charging demand=2 [case 1]
  - condition judgement -> charging/discharging power-up guidance=2 or 3 [case 2]
  - condition judgement -> vehicle charging/discharging mode=1 [case 3]
  - condition judgement -> power battery charging demand=2 [case 4]
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU high-voltage detection flag is 0, it switches to state 93. Then: 1. If the front MCU high-voltage flag is 1 and charging/discharging power-up is 1, the system switches to state 95.    a. If a pre-charge failure occurs, it switches to state 115. Additionally, if slow charging is inactive, the system shuts down and exits.    b. If an AC charging/discharging system fault occurs, it switches to state 115. Also, if slow charging is inactive, it shuts down and exits.    c. If slow charging is inactive, it switches to state 115 and then shuts down and exits. 2. If the DCDC state is 1 and there is no battery pre-heating demand,
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active and front MCU high-voltage detection flag is 0?) then (yes)   :Switch to state 93; else (no)   stop endif if (Front MCU high-voltage flag is 1 and charging/discharging power-up is 1?) then (yes)   :Switch to state 95;   if (Pre-charge failure occurs?) then (yes)     :Switch to state 115;     if (Slow charging is inactive?) then (yes)       :Shut down and exit;       stop     else (no)     endif   elseif (AC charging/discharging system fault occurs?) then (yes)     :Switch to state 115;     if (Slow charging is inactive?) then (yes)       :Shut down and exit;       stop     else (no)     endif   elseif (Slow charging is inactive?)

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
