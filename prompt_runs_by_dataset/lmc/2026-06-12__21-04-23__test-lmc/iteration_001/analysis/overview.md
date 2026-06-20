# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.8000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2701
- node_recall: 0.3034
- node_f1: 0.2738
- relation_precision: 0.1862
- relation_recall: 0.2134
- relation_f1: 0.1920
- plantuml_compilation_pass_rate: 0.8000
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
- syntax_error: 2
- wrong_loop: 2

## Representative Failure Cases
### fsd-0098
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.3158
- relation_f1: 0.1852
- missing_nodes:
  - tcms executes on preemptive rtos
  - deterministically orchestrate through priority queues
  - traction
  - braking
  - door control
  - diagnostics functions
  - issue track maintenance request via high-priority task
  - monitoring task using ring buffer for historical operation data
- extra_nodes:
  - initialize preemptive rtos priority queues
  - **emergency track monitoring task** (high priority)
  - issue track maintenance request
  - apply exponential backoff delay
  - awaiting clearance abnormalities persist?
  - normal scheduling
  - **historical data monitoring task** (ring buffer)
  - thresholds exceeded?
- missing_relations:
  - tcms executes on preemptive rtos -> deterministically orchestrate through priority queues
  - deterministically orchestrate through priority queues -> traction
  - traction -> braking
  - braking -> door control
  - door control -> diagnostics functions
  - diagnostics functions -> route deviation/track status obstruction detected?
  - assert emergency braking protocol -> issue track maintenance request via high-priority task
  - issue track maintenance request via high-priority task -> monitoring task using ring buffer for historical operation data
- input_excerpt:
  The Train Control and Monitoring System (TCMS), executing on a preemptive RTOS, deterministically orchestrates traction, braking, door control, and diagnostic functions through priority queues. Upon detecting a route deviation between onboard location data and the dispatch center's planned path, or an obstruction from the track status detection system, the TCMS immediately asserts the emergency braking protocol and issues a track maintenance request via a high-priority task. A separate monitoring task, using a ring buffer for historical operation data, performs threshold-based analysis; if exceeded, it triggers a non-blocking data optimization routine before resuming normal scheduling. If tr
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityDiamondBackgroundColor #F9F9F9  title TCMS Deterministic Orchestration and Safety Compliance  start  :Initialize Preemptive RTOS & Priority Queues;  fork   :**Emergency & Track Monitoring Task**\n(High Priority);      if (Route deviation or\nTrack obstruction detected?) then (Yes)     :Assert Emergency Braking Protocol;     :Issue Track Maintenance Request;          if (Track abnormalities persist?) then (Yes)       repeat         :Apply Exponential Backoff Delay;         :Re-trigger Maintenance Request;       repeat while (Awaiting Clearance\nAbnormalities persist?) is (Yes)       ->No;     endif
### fsd-0083
- dataset: fsd
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.3448
- relation_f1: 0.3214
- missing_nodes:
  - thermal management controller executes as state machine on rtos
  - govern pwm fans
  - govern liquid-cooling actuators
  - primary sequence initiates
  - check system rail voltage status via pmic
  - primary power rail nominal?
  - operation proceeds
  - two high-priority tasks spawned
- extra_nodes:
  - check pmic rail voltage status
  - rail voltage nominal?
  - halt operation
  - monitor temperature sensor data
  - safety threshold excursion?
  - excursion persistent?
  - abort further checks
  - final supervisory state confirm all parameters nominal
- missing_relations:
  - thermal management controller executes as state machine on rtos -> govern pwm fans
  - govern pwm fans -> govern liquid-cooling actuators
  - govern liquid-cooling actuators -> primary sequence initiates
  - primary sequence initiates -> check system rail voltage status via pmic
  - check system rail voltage status via pmic -> primary power rail nominal?
  - primary power rail nominal? -> operation proceeds
  - operation proceeds -> two high-priority tasks spawned
  - two high-priority tasks spawned -> sample current sensor data
- input_excerpt:
  The thermal management controller executes as a state machine on the RTOS, governing PWM fans and liquid-cooling actuators. Its primary sequence initiates with a check of the system's rail voltage status via the PMIC; operation proceeds only if this primary power rail is nominal. Upon validation, two high-priority tasks are spawned concurrently: one task samples the current sensor data, and if an overcurrent is detected, it enters an iterative monitoring mode using a ring buffer, holding the system state until the data normalizes. The concurrent task monitors temperature sensor data against safety thresholds; any excursion triggers immediate heat dissipation measures and, if persistent, init
- generated_excerpt:
  @startuml skinparam ActivityBackgroundColor #EEF7FF skinparam ActivityDiamondBackgroundColor #F9F9F9  title Thermal Management Controller State Machine  start  :Check PMIC rail voltage status;  if (Rail voltage nominal?) then (No)   :Halt operation;   stop else (Yes) endif  fork   :Sample current sensor data;    if (Overcurrent detected?) then (Yes)     repeat       :Enter iterative monitoring mode (Ring Buffer);       :Hold system state;     repeat while (Data normalized?) is (No)     ->Yes;    else (No)   endif fork again   :Monitor temperature sensor data;    if (Safety threshold excursion?) then (Yes)     :Trigger immediate heat dissipation measures;      if (Excursion persistent?) then 
### pure-0031
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - apply user selected time domain processes
  - process construction requirments
  - chainable
  - any output can be piped to any input
  - replica?
  - replica of self
  - fourier transform
  - repeatable in chain
- extra_nodes:
  - select time domain process(es)
  - chain another process?
- missing_relations:
  - apply user selected time domain processes -> process construction requirments
  - process construction requirments -> chainable
  - chainable -> any output can be piped to any input
  - any output can be piped to any input -> replica?
  - replica? -> replica of self
  - replica of self -> fourier transform
  - fourier transform -> repeatable in chain
  - repeatable in chain -> no proposed optional time domain processes
- input_excerpt:
  Time Domain Processing – The BE shall be able to apply user selected time domain processes. These processes should be constructed to be chainable (output of any time domain process can be piped to input of any other, including replica of self and Fourier Transform) and repeatable in the chain. No Optional time domain processes have as yet been proposed.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Select Time Domain Process(es);  repeat :Apply Time Domain Process;  note right   Processes are chainable:   * Output can pipe to any     other time domain process   * Output can pipe to a     replica of self   * Output can pipe to     Fourier Transform   * Processes are repeatable     in the chain end note  repeat while (Chain another process?) is (Yes)  ->No;  stop  @enduml
### us-0193
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - upload and tag staff generated working papers
  - access papers
- extra_nodes:
  - log into archive system
  - select upload working papers
  - choose local file(s) to upload
  - enter metadata and tags for the papers
  - submit upload and tags
  - upload and tagging successful?
  - system indexes and stores working papers
  - papers become searchable and accessible to staff and researchers
- missing_relations:
  - upload and tag staff generated working papers -> access papers
- input_excerpt:
  As an assistant archivist, I want to upload and tag staff generated working papers, so that staff and researchers are able to easily access them.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Log into archive system;  :Select "Upload Working Papers";  :Choose local file(s) to upload;  :Enter metadata and tags for the papers;  :Submit upload and tags;  if (Upload and Tagging Successful?) then (Yes)   :System indexes and stores working papers;   :Papers become searchable and accessible to staff and researchers;   :Display success message; else (No)   :Display error message;   :Retry upload and tagging;   stop endif  stop @enduml
### bp-0028
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0833
- relation_f1: 0.0000
- missing_nodes:
  - log in
  - more information?
  - see creating a new job
- extra_nodes:
  - log into the lifecycle manager tool
  - select output to a biar file in destination system drop-down list
  - click create
  - click add objects to add infoobjects to the job
  - manage dependencies (optional)
  - click promote
  - promote - job name screen appears
  - click export
- missing_relations:
  - log in -> create a new job
  - create a new job -> more information?
  - more information? -> see creating a new job
- input_excerpt:
  28.	Exporting a Job to a BIAR File1. Log into the LifeCycle Manager tool, and create a new job. For more information on creating a new job, see Creating a New Job on page 372. In the Destination System drop-down list, select Output to a BIAR file option and click Create.3. Click Add objects to add infoobjects to the job. You can use the Manage Dependencies option to manage the dependencies of the selected job.4. Click Promote.The "Promote - Job Name" screen appears.5. Click Export.The BIAR file is created. You can save a BIAR file to a File System or an FTP location.6. In the "Promote - Job Name"screen, click Biar File Destination. Biar File Destination pane appears.7. Select either File Sys
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :Select "Output to a BIAR file" in Destination System drop-down list; :Click Create; :Click Add objects to add infoobjects to the job; :Manage Dependencies (optional); :Click Promote; :"Promote - Job Name" screen appears; :Click Export; :The BIAR file is created; :Click Biar File Destination; :Biar File Destination pane appears; if (Select Destination?) then (File System)   :Select File System;   :Click Export;   :The BIAR file is exported to a file system; else (FTP)   :Select FTP;   :Enter host, port, username, password, directory, and filename;   :Click Export;   :The BIAR file is exported to an FTP location; endif s
### pure-0022
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1000
- relation_f1: 0.0000
- missing_nodes:
  - by driver?
  - driver selects
  - by track-to-train transmission information
  - specified acknowledgement?
  - acknowledge transfer in 5s
  - trainborne equipment is not operative?
  - leave partial supervision
  - leave partial supervision
- extra_nodes:
  - selection source
  - driver
  - driver selects partial supervision
  - track-to-train transmission
  - receive selection from track-to-train
  - acknowledgement specified?
  - acknowledge transfer from full supervision to partial supervision
- missing_relations:
  - select partial supervision -> by driver?
  - by driver? -> driver selects
  - driver selects -> by track-to-train transmission information
  - by track-to-train transmission information -> specified acknowledgement?
  - specified acknowledgement? -> acknowledge transfer in 5s
  - acknowledge transfer in 5s -> trainborne equipment is not operative?
  - trainborne equipment is not operative? -> leave partial supervision
  - leave partial supervision -> shunting is selected?
- input_excerpt:
  Partial Supervision shall be selected either by the Driver or by information received from track-to-train transmission. If acknowledgement is specified, the driver shall acknowledge transfer from Full Supervision to Partial Supervision within 5 seconds. The train shall leave Partial Supervision when the trainborne equipment is not operative any longer, when Shunting is selected, or when Full Supervision is available.
- generated_excerpt:
  @startuml start :Select Partial Supervision; switch (Selection source) case (Driver)   :Driver selects Partial Supervision; case (Track-to-train transmission)   :Receive selection from track-to-train; endswitch  if (Acknowledgement specified?) then (Yes)   :Acknowledge transfer from Full Supervision to Partial Supervision;   note right: Must be within 5 seconds else (No) endif  :Enter Partial Supervision;  repeat   :Operate in Partial Supervision; repeat while (Leave Partial Supervision?) is (No) -> Yes;  switch (Reason for leaving) case (Trainborne equipment not operative)   :Leave Partial Supervision; case (Shunting selected)   :Leave Partial Supervision; case (Full Supervision available) 
### us-0124
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2222
- relation_f1: 0.2857
- missing_nodes:
  - enter metadata
  - cerate file
- extra_nodes:
  - open application
  - select new experiment protocol
  - enter experiment metadata
  - required fields complete?
  - save protocol / metadata
- missing_relations:
  - describe an experiment protocol -> cerate file
- input_excerpt:
  As a user, I want to enter metadata / describe an experiment protocol before a file is even created.
- generated_excerpt:
  @startuml skinparam style strictuml  title Enter Metadata / Describe Experiment Protocol  start  :Open Application;  :Select "New Experiment Protocol";  :Enter Experiment Metadata; note right   e.g., Name, Objective,   Hypothesis, Researcher end note  :Describe Experiment Protocol; note right   e.g., Steps, Materials,   Conditions, Parameters end note  if (Required fields complete?) then (Yes)   :Save Protocol / Metadata;   note right: No file created yet   :Confirm Protocol Saved; else (No)   :Prompt to fill missing fields;   stop endif  stop @enduml
### bp-0010
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2703
- relation_f1: 0.1143
- missing_nodes:
  - sort increasing or decreasing
  - click alternative mouse button
  - open context menu
  - open context menu
  - internet channel is the greatest
  - analyze differences for months?
  - open dropdown box calendar year/month
  - open dropdown box calendar year/month
- extra_nodes:
  - right-click revenue field
  - observe greatest revenue is with internet channel
  - select 08.2007 in calendar year/month dropdown
  - select 07.2007 in calendar year/month dropdown
  - observe internet revenue increased greatly
  - filter data back to september (select 09.2007 in dropdown)
  - right-click subtotal of internet channel (567.308 05)
  - choose documents > create new comment from context menu
- missing_relations:
  - click arrows in revenue eld? -> sort increasing or decreasing
  - sort increasing or decreasing -> click alternative mouse button
  - click alternative mouse button -> open context menu
  - open context menu -> choose sort increasing or sort decreasing
  - choose sort increasing or sort decreasing -> internet channel is the greatest
  - internet channel is the greatest -> analyze differences for months?
  - analyze differences for months? -> open dropdown box calendar year/month
  - open dropdown box calendar year/month -> select 08.2007
- input_excerpt:
  10.	Analyzing Data in the Web Application1. Since you are interested in the revenue, you want to sort the revenue data.2. Click on the arrows in the Revenue eld to sort the revenue data in increasing or decreasing order.3. You can also sort the revenue by clicking the alternative mouse button on Revenue and choosing Sort Sort Increasing or Sort Decreasing in the context menu. You see that the greatest revenue is obtained with the distribution channel Internet.4. To see the differences in the revenue data for the months July, August and September, select rst 08.2007 and then 07.2007 in the dropdown box Calendar Year/Month. You see that the revenue data for the distribution channel Internet in
- generated_excerpt:
  @startuml start :Sort revenue data; fork   :Click arrows in Revenue field; fork again   :Right-click Revenue field;   :Choose Sort Increasing or Sort Decreasing from context menu; end fork :Observe greatest revenue is with Internet channel; :Select 08.2007 in Calendar Year/Month dropdown; :Select 07.2007 in Calendar Year/Month dropdown; :Observe Internet revenue increased greatly; :Note right: Marketing campaign was successful :Filter data back to September\n(Select 09.2007 in dropdown); :Right-click subtotal of Internet channel (567.308,05); :Choose Documents > Create New Comment\nfrom context menu; :Enter name and description for the document; :Enter text; :Choose Save; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
