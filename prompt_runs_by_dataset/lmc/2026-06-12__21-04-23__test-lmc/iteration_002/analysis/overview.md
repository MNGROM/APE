# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4419
- node_recall: 0.4524
- node_f1: 0.4181
- relation_precision: 0.2167
- relation_recall: 0.1863
- relation_f1: 0.1966
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
- extra_activity: 10
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10
- missing_activity: 9
- wrong_loop: 3
- wrong_parallel: 1

## Representative Failure Cases
### pure-0061
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - open keepass
  - information can be input
  - password
  - user name
  - url
  - word of notes
  - title
  - group
- extra_nodes:
  - user opens keepass
  - user input type?
  - user types two or more words in the search field
  - nothing appears in the main window
  - nothing appears in the main window
  - nothing appears in the main window
  - nothing?
  - partial match?
- missing_relations:
  - open keepass -> information can be input
  - information can be input -> password
  - password -> user name
  - user name -> url
  - url -> word of notes
  - word of notes -> title
  - title -> group
  - group -> input
- input_excerpt:
  1. User opens KeePass 2. User types a password, user name, URL, word of notes, title or group that exist in the database 3. The list of data related to search word are appeared in the main window 3.5.2.2 Alternative Data Flows 3.5.2.2.1 Alternative Data Flow 1 2. User types two or more words in the search field 3. Nothing appears in the main window 3.5.2.2.2 Alternative Data Flow 2 2. User does not type anything 3. Nothing appears in the main window 3.5.2.2.3 Alternative Data Flow 3 2a. User types part or even just one character of password, user name, URL, word of notes, title or group 3.5.2.2.4 Alternative Data Flow 4 2. User types data not related with the database 3. Nothing appears in t
- generated_excerpt:
  @startuml start :User opens KeePass; if (User input type?) then (Two or more words)   :User types two or more words in the search field;   :Nothing appears in the main window; elseif (Nothing?) then (User does not type anything)   :Nothing appears in the main window; elseif (Partial match?) then (User types part or just one character of password, user name, URL, word of notes, title or group)   :The list of data related to search word are appeared in the main window; elseif (No match?) then (User types data not related with the database)   :Nothing appears in the main window; else (Exact match)   :User types a password, user name, URL, word of notes, title or group that exist in the database
### us-0052
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0000
- missing_nodes:
  - get company support of scrum
- extra_nodes:
  - corporate sponsor requests to display logo
  - submit company logo
  - logo meets display criteria?
  - others see the company s support of scrum
  - reject logo submission
- missing_relations:
  - display logo on sponsors page -> get company support of scrum
- input_excerpt:
  As a corporatesponsor, I want to display my logo on a corporate sponsors page, so that others see the company's support of Scrum.
- generated_excerpt:
  @startuml start :Corporate sponsor requests to display logo; :Submit company logo; if (Logo meets display criteria?) then (yes)   :Display logo on corporate sponsors page;   :Others see the company's support of Scrum; else (no)   :Reject logo submission; endif stop @enduml
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.1852
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - 1
  - go to promotion jobs home page
  - select the job want to promote
  - 2
  - right-click
  - select source and destination systems
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - select the job to promote from the promotion jobs home page
  - enter appropriate value in the external change management id field
  - security settings required?
  - promote security?
  - select promote security
  - include application rights?
  - select include application rights
- missing_relations:
  - log in lifecycle manager tool -> selection method
  - selection method -> 1
  - 1 -> go to promotion jobs home page
  - go to promotion jobs home page -> select the job want to promote
  - select the job want to promote -> 2
  - 2 -> right-click
  - right-click -> click promote
  - click promote -> open source and destination systems drop-down lists
- input_excerpt:
  23.	promote a jobLog into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, select the job that you want to promote. You can also right-click the home page screen, and click Promote.3. From the source and the destination systems drop-down lists, select the source and destination systems.Note:Ensure that you have logged into both the source and destination systems before you proceed with the promotion process.4. In the External Change Management ID field, enter the appropriate value, and click Save.5. Click Mappings. Click Edit Mappings if you want to create and validate mappings.6. Click Security Settings, if required. The following options are displayed:• Do not Promote Secur
- generated_excerpt:
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :Select the job to promote from the "Promotion Jobs" home page; :Select source and destination systems from drop-down lists; :Enter appropriate value in the External Change Management ID field; :Click Save; :Click Mappings; if (Want to create and validate mappings?) then (Yes)   :Click Edit Mappings; else (No) endif if (Security Settings required?) then (Yes)   :Click Security Settings;   if (Promote Security?) then (Yes)     :Select Promote Security;     if (Include application rights?) then (Yes)       :Select Include application rights;     else (No)     endif   else (No)     :Select Do not Promote Security;   endif   :Cli
### fsd-0009
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3571
- relation_f1: 0.2593
- missing_nodes:
  - operating on preemptive rtos
  - tcms manages via deterministic scheduling
  - traction
  - braking
  - doors
  - diagnostics
  - detect acceleration threshold exceedance
  - high-priority task
- extra_nodes:
  - detect vehicle acceleration threshold exceedance via inertial sensor
  - command emergency braking assistance (high-priority task)
  - evaluate need for esp intervention (medium-priority task)
  - esp activation required?
  - process wheel speed sensor data via mutex-protected ring buffer
  - esp cyclic task active?
  - adjust electronic power steering system output torque via can message with crc checksum
  - steering assist active?
- missing_relations:
  - operating on preemptive rtos -> tcms manages via deterministic scheduling
  - tcms manages via deterministic scheduling -> traction
  - traction -> braking
  - braking -> doors
  - doors -> diagnostics
  - diagnostics -> detect acceleration threshold exceedance
  - braking pressure insufficient? -> high-priority task
  - high-priority task -> command emergency braking assistance immediately
- input_excerpt:
  Operating on a preemptive RTOS, the Train Control and Monitoring System (TCMS) manages traction, braking, doors, and diagnostics via deterministic scheduling. Upon an inertial sensor detecting a vehicle acceleration threshold exceedance, the system first verifies brake system status via a protected BMS query. If braking pressure is deemed insufficient, a high-priority task immediately commands emergency braking assistance, while a concurrent, medium-priority task evaluates the need for Electronic Stability Program (ESP) intervention. During ESP activation, a cyclic task with a mutex-protected ring buffer processes wheel speed sensor data, calculates individual wheel slip rates, and executes 
- generated_excerpt:
  @startuml start :Detect vehicle acceleration threshold exceedance via inertial sensor; :Verify brake system status via protected BMS query; if (Braking pressure insufficient?) then (yes)   fork     :Command emergency braking assistance (high-priority task);   fork again     :Evaluate need for ESP intervention (medium-priority task);     if (ESP activation required?) then (yes)       repeat         :Process wheel speed sensor data via mutex-protected ring buffer;         :Calculate individual wheel slip rates;         :Execute real-time braking force distribution algorithm;       repeat while (ESP cyclic task active?) is (yes)       ->no;     endif;   end fork   if (Steering angle sensor indi
### pure-0019
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3636
- relation_f1: 0.0000
- missing_nodes:
  - group members (not driver) initiate las
  - one member transmits?
  - not allowed
  - mode 1
  - mode 2
  - timeout?
  - intermittent tone
  - 800-850 hz
- extra_nodes:
  - activate link assurance signal (las)
  - button continuously pressed?
  - periodic button press before timeout?
- missing_relations:
  - group members (not driver) initiate las -> one member transmits?
  - one member transmits? -> not allowed
  - not allowed -> maintenance mode
  - maintenance mode -> mode 1
  - mode 1 -> continuous button press
  - continuous button press -> mode 2
  - mode 2 -> periodic button press
  - periodic button press -> timeout?
- input_excerpt:
  Shunting group members (except the driver) can activate the Link Assurance Signal (LAS). Only one member may transmit LAS at a time. Maintenance modes for LAS activation: Mode 1: Continuous button press required. Mode 2: Periodic button press required (timeout deactivates LAS). LAS is an intermittent tone (800–850 Hz, 1 sec on / 2 sec off). LAS is interrupted upon receiving a Shunting Emergency Call.
- generated_excerpt:
  @startuml start :Activate Link Assurance Signal (LAS); if (Maintenance Mode?) then (Mode 1: Continuous)   repeat     :Require continuous button press;     :Transmit LAS intermittent tone     (800-850 Hz, 1 sec on / 2 sec off);   repeat while (Button continuously pressed?) is (yes)   ->no; else (Mode 2: Periodic)   repeat     :Require periodic button press;     :Transmit LAS intermittent tone     (800-850 Hz, 1 sec on / 2 sec off);   repeat while (Periodic button press before timeout?) is (yes)   ->no; endif :Deactivate LAS; stop @enduml
### rac-0005
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4583
- relation_f1: 0.3043
- missing_nodes:
  - switch to state 93
  - switch to state 95
  - switch to state 105
  - switch to state 105
  - switch to state 105
  - switch to state 105
  - condition judgement
  - remote mode is closed
- extra_nodes:
  - system startup
  - transition to state 93
  - transition to state 95
  - transition to state 105
  - transition to state 105
  - go to state 105
  - slow charging becomes inactive?
  - remote mode deactivates?
- missing_relations:
  - switch to state 95 -> power-up is ready and vehicle charging/discharging mode is 2
  - power-up is ready and vehicle charging/discharging mode is 2 -> switch to state 105
  - switch to state 105 -> condition judgement
  - condition judgement -> in remote mode
  - in remote mode -> switch to state 105
  - switch to state 105 -> slow charging is inactive
  - switch to state 105 -> slow charging is inactive
  - switch to state 28 -> remote mode is closed
- input_excerpt:
  After the system starts up: - If slow charging is active and the front MCU high-voltage detection flag is 0, transition to state 93. - If charging/discharging power-up is active while the front MCU high-voltage detection flag reads 1, move to state 95. - When power-up readiness is confirmed and the vehicle's charging/discharging mode is set to 2, proceed to state 105.  Then handle these cases: 1. In remote mode: Go to state 105. If slow charging becomes inactive, shift to state 28. Should remote mode deactivate, initiate shutdown and terminate. 2. Upon receiving a pet mode request: Enter state 105. If slow charging is inactive, transition to state 28. After processing the pet mode request, p
- generated_excerpt:
  @startuml start :System startup;  if (Slow charging active\nand front MCU high-voltage detection flag = 0?) then (Yes)   :Transition to state 93; else (No)   if (Charging/discharging power-up active\nand front MCU high-voltage detection flag = 1?) then (Yes)     :Transition to state 95;   else (No)     if (Power-up readiness confirmed\nand vehicle charging/discharging mode = 2?) then (Yes)       :Transition to state 105;     else (No)     endif   endif endif  if (Remote mode?) then (Yes)   :Go to state 105;   if (Slow charging becomes inactive?) then (Yes)     :Shift to state 28;   else (No)   endif   if (Remote mode deactivates?) then (Yes)     :Initiate shutdown;     stop   else (No)   end
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4746
- relation_f1: 0.2807
- missing_nodes:
  - go to modeling area
  - choose info provider
  - info area displays information
  - transformation
  - data source
  - open data source context menu
  - open data source context menu
  - choose create info package...
- extra_nodes:
  - in the modeling area choose info provider
  - view transformation and data source in the info area below the info cube sales overview
  - in the context menu of the data source choose create info package...
  - enter a description for the info package
  - view info package maintenance screen for the scheduler
  - choose monitor in the toolbar of info package maintenance
  - view the monitor for the load process
  - select the load process for your data source from the tree at the left of the screen
- missing_relations:
  - go to data warehousing workbench -> go to modeling area
  - go to modeling area -> choose info provider
  - choose info provider -> info area displays information
  - info area displays information -> transformation
  - transformation -> data source
  - data source -> open data source context menu
  - open data source context menu -> choose create info package...
  - choose create info package... -> enter description
- input_excerpt:
  7.	Loading Transaction Data1. Go to the Data Warehousing Workbench; in the Modeling area choose Info Provider. The transformation and the Data source are displayed in the Info Area below the Info Cube Sales Overview.2. In the context menu of the Data source, choose Create Info Package...3. On the next screen, enter a description for the Info Package and choose Save. The Info Package maintenance screen for the scheduler appears.4. Go to the tab page Schedule and choose Start.5. To check the load process, choose Monitor in the toolbar of Info Package maintenance.6. On the next screen, select the date and choose Execute. The monitor for the load process is displayed.7. Select the load process f
- generated_excerpt:
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose Info Provider; :View transformation and Data source in the Info Area below the Info Cube Sales Overview; :In the context menu of the Data source, choose Create Info Package...; :Enter a description for the Info Package; :Choose Save; :View Info Package maintenance screen for the scheduler; :Go to the tab page Schedule; :Choose Start; :Choose Monitor in the toolbar of Info Package maintenance; :Select the date; :Choose Execute; :View the monitor for the load process; :Select the load process for your Data source from the tree at the left of the screen; :Exit the Info Package maintenance screen; :From the conte
### rac-0007
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6275
- relation_f1: 0.4490
- missing_nodes:
  - high-voltage shutdown request charging/discharging flag is 2
  - flag becomes 0 and cp duty cycle is 85
  - switch to state 126
  - switch to state 130
  - switch to state 130
  - slow charging is inactive
  - slow charging is inactive
  - shutdown
- extra_nodes:
  - system starts up
  - high-voltage shutdown request flag is 2?
  - condition after state 115?
  - condition after state 110?
  - flag drops to 0 with cp duty cycle at 88 ?
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging flag is 2
  - high-voltage shutdown request charging/discharging flag is 2 -> switch to state 115
  - switch to state 115 -> flag becomes 0 and cp duty cycle is 85
  - flag becomes 0 and cp duty cycle is 85 -> switch to state 126
  - switch to state 130 -> slow charging is inactive
  - switch to state 130 -> slow charging is inactive
  - slow charging is inactive -> shutdown
  - slow charging is inactive -> shutdown
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?) then (yes)   :Enter power-up mode;      if (High-voltage shutdown request flag is 2?) then (yes)     :Switch to state 115;          if (Condition after state 115?) then (Flag drops to 0 with CP duty cycle at 85%)       :Switch to state 126;     elseif (BMS self-check counter is 1?) then (yes)       :Switch to state 130;     elseif (Slow charging becomes inactive?) then (yes)       :Shut down;       end     endif        elseif (Central control charging/discharging command is 2\nand vehicle isn't in charging/discharging mode?) then (yes)     :Switch to state 110;          if (Condition after state 110?) then (High-voltage shutdow

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
