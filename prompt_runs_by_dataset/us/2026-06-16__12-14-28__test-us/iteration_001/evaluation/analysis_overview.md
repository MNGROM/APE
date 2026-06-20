# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4067
- node_recall: 0.3943
- node_f1: 0.4004
- relation_precision: 0.3414
- relation_recall: 0.3236
- relation_f1: 0.3323
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
- extra_or_wrong_relation: 10
- missing_activity: 9
- extra_activity: 9
- missing_or_wrong_relation: 9
- wrong_parallel: 2
- wrong_loop: 1

## Representative Failure Cases
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
  - compute nn output z
  - evaluate maximum value of z
  - z <= 1.1?
  - accept nn output
  - reject nn output / trigger error
- missing_relations:
  - input any value -> maximum value of nn output z <= 1.1?
  - maximum value of nn output z <= 1.1? -> allowed [yes]
  - maximum value of nn output z <= 1.1? -> not allowed [no]
- input_excerpt:
  1.	The maximum value of the NN output, z, shall always be less than or equal to 1.1, regardless of the input values.
- generated_excerpt:
  @startuml start :Receive input values for NN; :Compute NN output z; :Evaluate maximum value of z; if (z <= 1.1?) then (Yes)   :Accept NN output; else (No)   :Reject NN output / Trigger Error; endif stop @enduml
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1818
- relation_f1: 0.2286
- missing_nodes:
  - sort revenue data
  - click arrows in revenue eld?
  - sort increasing or decreasing
  - click alternative mouse button
  - open context menu
  - choose sort increasing or sort decreasing
  - internet channel is the greatest
  - analyze differences for months?
- extra_nodes:
  - click arrows in the revenue field to sort revenue data (increasing/decreasing)
  - alternatively right-click revenue and choose sort > sort increasing or sort decreasing
  - observe greatest revenue is from the internet distribution channel
  - select 08.2007 in calendar year/month dropdown box
  - select 07.2007 in calendar year/month dropdown box
  - observe internet revenue increased greatly (successful marketing campaign)
  - filter data back to september by selecting 09.2007 in dropdown box
  - right-click subtotal of internet distribution channel (567.308 05)
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
  @startuml start :Click arrows in the Revenue field to sort revenue data (Increasing/Decreasing); :Alternatively, right-click Revenue and choose Sort > Sort Increasing or Sort Decreasing; :Observe greatest revenue is from the Internet distribution channel; :Select "08.2007" in Calendar Year/Month dropdown box; :Select "07.2007" in Calendar Year/Month dropdown box; :Observe Internet revenue increased greatly (successful marketing campaign); :Filter data back to September by selecting "09.2007" in dropdown box; :Right-click subtotal of Internet distribution channel (567.308,05); :Choose Documents > Create New Comment from context menu; :Enter a name and description for the document; :Enter a te
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
  - multiply dcm321 by dcm321t (dcm321 * dcm321t)
  - validation passed
  - validation failed
- missing_relations:
  - =identity (3x3) matrix.v? -> allowed [yes]
  - =identity (3x3) matrix.v? -> not allowed [no]
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml start :Initialize Rotation Matrix DCM321; :Compute Transpose of Rotation Matrix DCM321T; :Multiply DCM321 by DCM321T (DCM321 * DCM321T); if (Result == Identity (3x3) Matrix?) then (Yes)   :Validation Passed; else (No)   :Validation Failed; endif stop @enduml
### rac-0012
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3333
- relation_f1: 0.2609
- missing_nodes:
  - charging=1 and front mcu high-voltage detection flag=0
  - bms-fast charger handshake flag=0 and front mcu high-voltage flag=0
  - condition judgement
  - shutdown
  - wait 0.8s
  - high-voltage shutdown request charging/discharging =2
- extra_nodes:
  - system starts up
  - charging = 1?
  - front mcu high-voltage detection flag = 0?
  - continue
  - bms-fast charger handshake flag = 0?
  - front mcu high-voltage flag = 0?
  - pre-charge failure occurs?
  - move to state 175
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
  @startuml start :System starts up;  if (charging = 1?) then (Yes)   if (front MCU high-voltage detection flag = 0?) then (Yes)     :Transition to state 153;     stop   else (No)     :Continue;   endif else (No)   :Continue; endif  if (BMS-fast charger handshake flag = 0?) then (Yes)   if (front MCU high-voltage flag = 0?) then (Yes)     :Enter state 155;   else (No)     stop   endif else (No)   stop endif  repeat :State 155;   if (pre-charge failure occurs?) then (Yes)     :Move to state 175;     if (fast charging inactive?) then (Yes)       :Shut down;       stop     else (No)       break     endif   elseif (high-voltage shutdown request detected (value=2)?) then (Yes)     :Wait 0.8 seconds
### fsd-0083
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3929
- relation_f1: 0.3662
- missing_nodes:
  - thermal management controller executes as state machine on rtos
  - govern pwm fans
  - govern liquid-cooling actuators
  - primary sequence initiates
  - primary power rail nominal?
  - operation proceeds
  - two high-priority tasks spawned
  - hold system state
- extra_nodes:
  - rail voltage nominal?
  - halt operation / fail-safe
  - buffer monitor current data
  - monitor temperature sensor data
  - safety threshold excursion?
  - excursion persistent?
  - halt operation
  - final supervisory state confirm all parameters nominal
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
  @startuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityDiamondBackgroundColor #F9F9F9  title Thermal Management Controller - RTOS State Machine  start  :Check PMIC rail voltage status;  if (Rail voltage nominal?) then (No)     :Halt operation / Fail-safe;     stop else (Yes) endif  fork     :Sample current sensor data;     if (Overcurrent detected?) then (Yes)         :Enter iterative monitoring mode (Ring Buffer);         repeat             :Buffer & monitor current data;         repeat while (Data normalized?) is (No)         ->Yes;     else (No)     endif fork again     :Monitor temperature sensor data;     if (Safety threshold excursion?) then (Yes)         :Trigger immedi
### pure-0076
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4167
- relation_f1: 0.2143
- missing_nodes:
  - initial window?
  - not allowed
  - make new selection
  - print window image?
  - click ok
  - print window
- extra_nodes:
  - display initial window
  - user makes a selection
  - display new window
  - user clicks back button?
  - current window is diagnostic information window?
  - user clicks ok button
  - print image of the diagnostic information window
  - continue application?
- missing_relations:
  - dismiss current window? -> initial window? [yes]
  - initial window? -> not allowed [yes]
  - re-establish previous window as current window -> make new selection
  - not allowed -> print window image?
  - make new selection -> print window image?
  - dismiss current window? -> print window image? [no]
  - print window image? -> click print [yes]
  - select diagnostic information window -> click ok
- input_excerpt:
  1. At any window except the initial window, the user may click the “Back” button to dismiss the current window and re-establish the previous window as the current window. The user may then make a new selection. 2. The user may click a button labeled “Print” on the diagnostic information window to print an image of the window. 3. The tool displays a window listing possible items to print including the diagnostic information window. 4. The user selects the diagnostic information window and clicks the “OK” button to print the window.
- generated_excerpt:
  @startuml start  :Display initial window; repeat   :User makes a selection;   :Display new window;    if (User clicks "Back" button?) then (Yes)     :Dismiss current window;     :Re-establish previous window as current window;     note right: User may make a new selection   else (No)     if (Current window is diagnostic information window?) then (Yes)       if (User clicks "Print" button?) then (Yes)         :Tool displays a window listing possible items to print;         note right: List includes the diagnostic information window         :User selects diagnostic information window;         :User clicks "OK" button;         :Print image of the diagnostic information window;       else (No)  
### fsd-0098
- dataset: fsd
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4211
- relation_f1: 0.2857
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
  - maintain normal operations
  - apply exponential backoff delay
  - awaiting clearance abnormalities persist?
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
### pure-0074
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4242
- relation_f1: 0.3556
- missing_nodes:
  - start diagnostic processing
  - stop?
  - open main menu status
  - include to validate privileges
  - request confirmation
  - responds positively?
  - perform no function
  - user remains authenticated
- extra_nodes:
  - authenticate user
  - has privilege to stop?
  - request confirmation to stop diagnostics
  - user confirms?
  - no function performed
  - exit tool
  - already validated to stop?
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
  @startuml start  fork   :Select "Stop Diagnostics" from "Status" menu;    if (Authenticated as administrator?) then (No)     :Authenticate User;     if (Has privilege to stop?) then (Yes)     else (No)       stop     endif   endif    :Request confirmation to stop diagnostics;    if (User confirms?) then (Yes)     :Stop diagnostic processing;     :Indicate stopped condition;   else (No)     :No function performed;     note right: User remains authenticated   endif  fork again   :Select "Exit" from "File" menu;    if (Diagnostic processing active?) then (No)     :Exit tool;     stop   else (Yes)     if (Already validated to stop?) then (No)       :Authenticate User;       if (Permitted to stop

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
