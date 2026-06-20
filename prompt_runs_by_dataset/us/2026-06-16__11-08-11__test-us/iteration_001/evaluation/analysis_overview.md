# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4346
- node_recall: 0.4336
- node_f1: 0.4341
- relation_precision: 0.3525
- relation_recall: 0.3257
- relation_f1: 0.3386
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
- extra_activity: 10
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10
- missing_activity: 9
- wrong_parallel: 2
- syntax_error: 1
- wrong_loop: 1

## Representative Failure Cases
### fsd-0083
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4912
- relation_f1: 0.3889
- missing_nodes:
  - thermal management controller executes as state machine on rtos
  - govern pwm fans
  - govern liquid-cooling actuators
  - primary sequence initiates
  - primary power rail nominal?
  - operation proceeds
  - two high-priority tasks spawned
  - monitor temperature sensor data against safety thresholds
- extra_nodes:
  - rail voltage nominal?
  - monitor temperature sensor data
  - safety threshold excursion?
  - excursion persistent?
  - final supervisory state confirm all parameters nominal
  - transmit telemetry data
  - communication fault?
  - bounded retry with exponential backoff
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern pwm fans [fork]
  - thermal management controller executes as state machine on rtos -> govern liquid-cooling actuators [fork]
  - govern pwm fans -> primary sequence initiates
  - govern liquid-cooling actuators -> primary sequence initiates
  - primary sequence initiates -> check system rail voltage status via pmic
  - primary power rail nominal? -> operation proceeds [yes]
  - operation proceeds -> two high-priority tasks spawned
  - two high-priority tasks spawned -> sample current sensor data [fork]
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing PWM fans and liquid-cooling actuators. Its primary sequence initiates with a check of the system's rail voltage status via the PMIC; operation proceeds only if this primary power rail is nominal. Upon validation, two high-priority tasks are spawned concurrently: one task samples the current sensor data, and if an overcurrent is detected, it enters an iterative monitoring mode using a ring buffer, holding the system state until the data normalizes. The concurrent task monitors temperature sensor data against safety thresholds; any excursion triggers immediate heat dissipation measures and, if persistent, init
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityDiamondBackgroundColor #F9F9F9  start  :Check PMIC rail voltage status;  if (Rail voltage nominal?) then (No)     stop else (Yes) endif  fork     :Sample current sensor data;     if (Overcurrent detected?) then (Yes)         repeat             :Enter iterative monitoring mode (ring buffer);             :Hold system state;         repeat while (Data normalized?) is (No)         ->Yes;     else (No)     endif fork again     :Monitor temperature sensor data;     if (Safety threshold excursion?) then (Yes)         :Trigger immediate heat dissipation measures;         if (Excursion persistent?) then (Yes)             :Initiate 
### lmc-0035
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - input any value
  - maximum value of nn output z <= 1.1?
  - allowed
  - not allowed
- extra_nodes:
  - receive input values for nn
  - process input through nn
  - calculate nn output z
  - z <= 1.1?
  - accept output z
  - reject output / enforce constraint
  - cap or adjust z to <= 1.1
- missing_relations:
  - input any value -> maximum value of nn output z <= 1.1?
  - maximum value of nn output z <= 1.1? -> allowed [yes]
  - maximum value of nn output z <= 1.1? -> not allowed [no]
- input_excerpt:
  1.	The maximum value of the NN output, z, shall always be less than or equal to 1.1, regardless of the input values.
- generated_excerpt:
  @startuml start :Receive input values for NN; :Process input through NN; :Calculate NN output z; if (z <= 1.1?) then (Yes)   :Accept output z; else (No)   :Reject output / Enforce constraint;   :Cap or adjust z to <= 1.1; endif stop @enduml
### lmc-0055
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.2500
- missing_nodes:
  - dcm321 * dcm321t
  - allowed
  - not allowed
- extra_nodes:
  - initialize rotation matrix dcm321
  - compute transpose of rotation matrix dcm321t
  - multiply dcm321 by dcm321t (result = dcm321 * dcm321t)
  - validation passed
  - validation failed
- missing_relations:
  - =identity (3x3) matrix.v? -> allowed [yes]
  - =identity (3x3) matrix.v? -> not allowed [no]
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml start :Initialize Rotation Matrix DCM321; :Compute Transpose of Rotation Matrix DCM321T; :Multiply DCM321 by DCM321T (Result = DCM321 * DCM321T); if (Result == Identity (3x3) Matrix?) then (Yes)   :Validation Passed; else (No)   :Validation Failed; endif stop @enduml
### pure-0074
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.2727
- missing_nodes:
  - start diagnostic processing
  - stop?
  - open main menu status
  - select stop diagnostics menu item
  - include to validate privileges
  - request confirmation
  - responds positively?
  - perform no function
- extra_nodes:
  - user action?
  - authenticate user
  - privilege validated?
  - request confirmation to stop diagnostics
  - user confirms?
  - no function (user remains authenticated)
  - already validated to stop?
  - no function
- missing_relations:
  - start diagnostic processing -> stop?
  - stop? -> open main menu status [yes]
  - open main menu status -> select stop diagnostics menu item
  - authenticated as administrator user? -> include to validate privileges [no]
  - authenticated as administrator user? -> request confirmation [yes]
  - stop diagnostic processing -> responds positively?
  - responds positively? -> stop diagnostic processing [yes]
  - responds positively? -> perform no function [no]
- input_excerpt:
  1. The user can stop diagnostic processing at any time after the diagnostic processing has started by selecting the “Stop Diagnostics” menu item from the main menu entitled “Status”. 2. If the user is not authenticated as the administrator user, include (Authenticate User) to validate privileges for stopping diagnostic processing. 3. If the user has the appropriate privilege, the tool requests confirmation to stop diagnostic processing. 4. If the user responds positively to the confirmation, the tool stops diagnostic processing and indicates the stopped condition. Otherwise the software performs no function but the user remains authenticated. 5. If the user selects the “Exit” menu item from 
- generated_excerpt:
  @startuml start  if (User Action?) then (Select "Stop Diagnostics" from "Status" menu)   if (Authenticated as administrator?) then (No)     :Authenticate User;     if (Privilege validated?) then (No)       stop     endif   endif   :Request confirmation to stop diagnostics;   if (User confirms?) then (Yes)     :Stop diagnostic processing;     :Indicate stopped condition;   else (No)     :No function (user remains authenticated);   endif  elseif (User Action?) then (Select "Exit" from "File" menu)   if (Diagnostic processing active?) then (Yes)     if (Already validated to stop?) then (No)       :Authenticate User;       if (Privilege validated?) then (No)         :No function;         stop   
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2941
- relation_f1: 0.2703
- missing_nodes:
  - sort revenue data
  - click alternative mouse button
  - open context menu
  - internet channel is the greatest
  - analyze differences for months?
  - open dropdown box calendar year/month
  - select 08.2007
  - select 07.2007
- extra_nodes:
  - observe greatest revenue is with internet channel
  - select 08.2007 in calendar year/month dropdown
  - select 07.2007 in calendar year/month dropdown
  - observe internet revenue increased greatly
  - select 09.2007 in calendar year/month dropdown to filter back
  - right-click on internet subtotal (567.308 05)
  - enter name and description for the document
  - click save
- missing_relations:
  - sort revenue data -> click arrows in revenue eld?
  - click arrows in revenue eld? -> sort increasing or decreasing [yes]
  - click arrows in revenue eld? -> click alternative mouse button [no]
  - click alternative mouse button -> open context menu
  - open context menu -> choose sort increasing or sort decreasing
  - sort increasing or decreasing -> internet channel is the greatest
  - choose sort increasing or sort decreasing -> internet channel is the greatest
  - internet channel is the greatest -> analyze differences for months?
- input_excerpt:
  10.	Analyzing Data in the Web Application1. Since you are interested in the revenue, you want to sort the revenue data.2. Click on the arrows in the Revenue eld to sort the revenue data in increasing or decreasing order.3. You can also sort the revenue by clicking the alternative mouse button on Revenue and choosing Sort Sort Increasing or Sort Decreasing in the context menu. You see that the greatest revenue is obtained with the distribution channel Internet.4. To see the differences in the revenue data for the months July, August and September, select rst 08.2007 and then 07.2007 in the dropdown box Calendar Year/Month. You see that the revenue data for the distribution channel Internet in
- generated_excerpt:
  @startuml start :Click arrows in the Revenue field; fork   :Sort Increasing; fork again   :Sort Decreasing; end fork :Observe greatest revenue is with Internet channel; :Select 08.2007 in Calendar Year/Month dropdown; :Select 07.2007 in Calendar Year/Month dropdown; :Observe Internet revenue increased greatly; :Select 09.2007 in Calendar Year/Month dropdown to filter back; :Right-click on Internet subtotal (567.308,05); :Choose Documents > Create New Comment from context menu; :Enter name and description for the document; :Enter text; :Click Save; stop @enduml
### fsd-0098
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3860
- relation_f1: 0.2597
- missing_nodes:
  - deterministically orchestrate through priority queues
  - traction
  - braking
  - door control
  - diagnostics functions
  - route deviation/track status obstruction detected?
  - issue track maintenance request via high-priority task
  - monitoring task using ring buffer for historical operation data
- extra_nodes:
  - emergency track maintenance task (high priority)
  - route deviation detected? (onboard vs dispatch path)
  - issue track maintenance request
  - obstruction detected? (track status system)
  - continue normal operations
  - re-trigger maintenance request (exponential backoff strategy)
  - abnormalities persist?
  - monitoring task
- missing_relations:
  - tcms executes on preemptive rtos -> deterministically orchestrate through priority queues
  - deterministically orchestrate through priority queues -> traction [fork]
  - deterministically orchestrate through priority queues -> braking [fork]
  - deterministically orchestrate through priority queues -> door control [fork]
  - deterministically orchestrate through priority queues -> diagnostics functions [fork]
  - traction -> route deviation/track status obstruction detected?
  - braking -> route deviation/track status obstruction detected?
  - door control -> route deviation/track status obstruction detected?
- input_excerpt:
  The Train Control and Monitoring System (TCMS), executing on a preemptive RTOS, deterministically orchestrates traction, braking, door control, and diagnostic functions through priority queues. Upon detecting a route deviation between onboard location data and the dispatch center's planned path, or an obstruction from the track status detection system, the TCMS immediately asserts the emergency braking protocol and issues a track maintenance request via a high-priority task. A separate monitoring task, using a ring buffer for historical operation data, performs threshold-based analysis; if exceeded, it triggers a non-blocking data optimization routine before resuming normal scheduling. If tr
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #F9F9F9 skinparam ActivityDiamondBackgroundColor #E8E8E8  title Train Control and Monitoring System (TCMS) - Activity Diagram  start  :Initialize TCMS on Preemptive RTOS; note right   Orchestrates via priority queues:   * Traction   * Braking   * Door Control   * Diagnostics end note  fork   :Emergency & Track Maintenance Task (High Priority);   if (Route Deviation Detected?\n(Onboard vs Dispatch Path)) then (Yes)     :Assert Emergency Braking Protocol;     :Issue Track Maintenance Request;   elseif (Obstruction Detected?\n(Track Status System)) then (Yes)     :Assert Emergency Braking Protocol;     :Issue Track Maintenance Request;   else (No)    
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5161
- relation_f1: 0.2791
- missing_nodes:
  - condition judgement
  - shutdown
  - wait 0.8s
  - high-voltage shutdown request charging/discharging =2
- extra_nodes:
  - system starts up
  - pre-charge failure occurs?
  - move to state 175
  - shut down
  - high-voltage shutdown request detected (value=2)?
  - wait 0.8 seconds
  - enter state 175
  - ignition switch status=2?
- missing_relations:
  - switch to state 153 -> bms-fast charger handshake flag=0 and front mcu high-voltage flag=0
  - enter state 155 -> condition judgement
  - condition judgement -> switch to state 175 [case pre-charge failure occurs]
  - condition judgement -> wait 0.8s [case high-voltage shutdown request charging/discharging =2]
  - wait 0.8s -> switch to state 175
  - condition judgement -> stay in state 155 [case ignition switch=2]
  - stay in state 155 -> high-voltage shutdown request charging/discharging =2
  - high-voltage shutdown request charging/discharging =2 -> wait 0.8s [if yes]
- input_excerpt:
  After the system starts up: - If charging is active (charging=1) and the front MCU high-voltage detection flag is 0, transition to state 153. - If the BMS-fast charger handshake flag is 0 and the front MCU high-voltage flag is 0, enter state 155.  While in state 155: 1. If pre-charge failure occurs, move to state 175. If fast charging remains inactive after this, shut down and end the process. 2. If a high-voltage shutdown request (for charging/discharging) is detected (value=2), wait 0.8 seconds before entering state 175. If fast charging is inactive afterward, shut down and end. 3. If the ignition switch status is 2, remain in state 155. If a high-voltage shutdown request (value=2) exists 
- generated_excerpt:
  @startuml start :System starts up;  if (charging=1 && front MCU high-voltage detection flag=0) then (yes)   :Transition to state 153;   stop elseif (BMS-fast charger handshake flag=0 && front MCU high-voltage flag=0) then (yes)   :Enter state 155; else (no)   stop endif  repeat   if (pre-charge failure occurs?) then (yes)     :Move to state 175;     if (fast charging inactive?) then (yes)       :Shut down;       stop     endif   elseif (high-voltage shutdown request detected (value=2)?) then (yes)     :Wait 0.8 seconds;     :Enter state 175;     if (fast charging inactive?) then (yes)       :Shut down;       stop     endif   elseif (ignition switch status=2?) then (yes)     :Remain in state 
### bp-0028
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6047
- relation_f1: 0.4583
- missing_nodes:
  - log in
  - more information?
  - see creating a new job
  - open drop-lists
  - select output to a biar file
  - click add objects
  - infoobjects are added
  - other operations?
- extra_nodes:
  - log into the lifecycle manager tool
  - select output to a biar file in destination system drop-down list
  - click add objects to add infoobjects to the job
  - click promote
  - select destination?
- missing_relations:
  - log in -> create a new job
  - create a new job -> more information?
  - more information? -> see creating a new job [yes]
  - see creating a new job -> open drop-lists
  - more information? -> open drop-lists [no]
  - open drop-lists -> select output to a biar file
  - click create -> click add objects
  - click add objects -> infoobjects are added
- input_excerpt:
  28.	Exporting a Job to a BIAR File1. Log into the LifeCycle Manager tool, and create a new job. For more information on creating a new job, see Creating a New Job on page 372. In the Destination System drop-down list, select Output to a BIAR file option and click Create.3. Click Add objects to add infoobjects to the job. You can use the Manage Dependencies option to manage the dependencies of the selected job.4. Click Promote.The "Promote - Job Name" screen appears.5. Click Export.The BIAR file is created. You can save a BIAR file to a File System or an FTP location.6. In the "Promote - Job Name"screen, click Biar File Destination. Biar File Destination pane appears.7. Select either File Sys
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Select "Output to a BIAR file" in Destination System drop-down list; :Click Create; :Click Add objects to add infoobjects to the job; :Manage Dependencies (optional); :Click Promote; :"Promote - Job Name" screen appears; :Click Export; :BIAR file is created; :Click Biar File Destination; :Biar File Destination pane appears; if (Select Destination?) then (File System)   :Select File System;   :Click Export;   :BIAR file is exported to a file system; else (FTP)   :Select FTP;   :Enter host, port, username, password, directory, and filename;   :Click Export;   :BIAR file is exported to an FTP location; endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
