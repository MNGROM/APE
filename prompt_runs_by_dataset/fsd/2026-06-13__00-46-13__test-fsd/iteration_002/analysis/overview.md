# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 0.9000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2621
- node_recall: 0.2772
- node_f1: 0.2468
- relation_precision: 0.0865
- relation_recall: 0.0777
- relation_f1: 0.0814
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
- missing_activity: 10
- extra_activity: 10
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10
- syntax_error: 1

## Representative Failure Cases
### rac-0004
- dataset: rac
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.5455
- relation_f1: 0.2642
- missing_nodes:
  - slow charging state is 1 and charging/discharging power-up is ready
  - switch to state 105
  - condition judgement
  - high-voltage shutdown charging/discharging value is 3 or 4
  - slow charging?
  - slow charging?
  - slow charging?
  - slow charging?
- extra_nodes:
  - system startup
  - slow charging active (state 1
  - high-voltage shutdown value is 3 or 4?
  - slow charging becomes inactive?
  - slow charging becomes inactive?
  - slow charging becomes inactive?
  - slow charging becomes inactive?
  - high-voltage shutdown request (value 3
- missing_relations:
  - slow charging state is 1 and charging/discharging power-up is ready -> switch to state 95
  - switch to state 105 -> condition judgement
  - condition judgement -> high-voltage shutdown charging/discharging value is 3 or 4
  - high-voltage shutdown charging/discharging value is 3 or 4 -> switch to state 115
  - switch to state 115 -> slow charging?
  - switch to state 115 -> slow charging?
  - switch to state 115 -> slow charging?
  - switch to state 115 -> slow charging?
- input_excerpt:
  After the system starts up: - If slow charging is active (state 1) and the charging/discharging system is powered up, switch to state 95. - If the vehicle charging/discharging mode is 2 and the system is powered up, switch to state 105. Then, while in state 105:   1) If the high-voltage shutdown value is 3 or 4, switch to state 115. If slow charging becomes inactive during this, shut down and end the process.   2) If a high-voltage shutdown request (value 3) occurs while the ignition is on (position 2), return to state 105. If the ignition turns off (position 0), switch to state 115. If slow charging becomes inactive, shut down and end.   3) If a pre-charge failure happens, switch to state 1
- generated_excerpt:
  @startuml start :System Startup;  if (Slow charging active (state 1)\nand charging/discharging powered up?) then (Yes)   :Switch to state 95;   stop elseif (Vehicle charging/discharging mode is 2\nand system powered up?) then (Yes)   :Switch to state 105;      repeat     if (High-voltage shutdown value is 3 or 4?) then (Yes)       :Switch to state 115;       if (Slow charging becomes inactive?) then (Yes)         :Shut down;         end       endif     elseif (High-voltage shutdown request (value 3)\nand ignition on (position 2)?) then (Yes)       :Return to state 105;       backward:Repeat state 105 checks;     elseif (Ignition turns off (position 0)?) then (Yes)       :Switch to state 115;
### pure-0010
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - give out successful trade information
  - save trade instruction
- extra_nodes:
  - central trading system give out the successful trade information
  - security account management save the trade information
- missing_relations:
  - give out successful trade information -> save trade instruction
- input_excerpt:
  1. central trading system: give out the successful trade information 2. security account management: save the trade information
- generated_excerpt:
  @startuml start :Central Trading System: Give out the successful trade information; :Security Account Management: Save the trade information; stop @enduml
### us-0153
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - receive regular summary reports of research data
  - get trends in data use among staff and postgraduate students
- extra_nodes:
  - schedule regular reporting interval
  - automated system aggregates research data usage logs
  - analyze data use trends among staff and postgraduate students
  - generate summary report
  - send notification to postgraduate convenor
  - postgraduate convenor receives report notification
  - review report?
  - access and review summary report
- missing_relations:
  - receive regular summary reports of research data -> get trends in data use among staff and postgraduate students
- input_excerpt:
  As a Postgraduate Convenor, I want to receive regular summary reports of research data, so that I understand trends in data use among staff and postgraduate students.
- generated_excerpt:
  @startuml skinparam style strictuml  title Receive Regular Summary Reports of Research Data  start  :Schedule regular reporting interval;  :Automated system aggregates research data usage logs;  :Analyze data use trends among staff and postgraduate students;  :Generate summary report;  :Send notification to Postgraduate Convenor;  :Postgraduate Convenor receives report notification;  if (Review report?) then (Yes)   :Access and review summary report;   :Understand data use trends; else (No)   :Archive report for later review; endif  stop  @enduml
### us-0216
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - identify the number of whales heard in a single audio file
- extra_nodes:
  - admin selects an audio file
  - load audio file into the system
  - play audio / visualize spectrogram
  - admin listens and watches for whale sounds
  - identify a whale sound
  - increment whale count by 1
  - more whale sounds identified?
  - log total whale count for the audio file
- input_excerpt:
  As a Zooniverse admin, I want to identify the number of whales heard in a single audio file.
- generated_excerpt:
  @startuml skinparam style strictuml  title Zooniverse Admin: Identify the number of whales heard in a single audio file  start  :Admin selects an audio file;  :Load audio file into the system;  :Play audio / Visualize spectrogram;  :Admin listens and watches for whale sounds;  repeat   :Identify a whale sound;   :Increment whale count by 1; repeat while (More whale sounds identified?) is (Yes) -> No;  :Log total whale count for the audio file;  stop @enduml
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0833
- relation_f1: 0.0000
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - 1
  - go to promotion jobs home page
  - select the job want to promote
  - 2
  - right-click
  - click promote
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - in the promotion jobs home page select the job to promote (or right-click the home page screen and click promote)
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
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, select the job to promote\n(Or right-click the home page screen and click Promote); :Select source and destination systems from drop-down lists; note right: Ensure that you have logged into\nboth the source and destination\nsystems before proceeding :Enter appropriate value in External Change Management ID field; :Click Save; :Click Mappings; if (Want to create and validate mappings?) then (Yes)   :Click Edit Mappings;   :Create and validate mappings; else (No) endif if (Security Settings required?) then (Yes)   :Click Security Settings;   switch (Security Option)   case (Do not Promote Sec
### lmc-0038
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1667
- relation_f1: 0.0000
- missing_nodes:
  - absolute error between zt truth data and output z <= 0.01?
  - allowed
  - not allowed
- extra_nodes:
  - compute zt truth data
  - compute output z
  - calculate absolute error = zt - z
  - absolute error <= 0.01?
  - requirement met
  - requirement violated
  - raise error or alert
- missing_relations:
  - for equivalent input of (xt yt) -> absolute error between zt truth data and output z <= 0.01?
  - absolute error between zt truth data and output z <= 0.01? -> allowed
  - allowed -> not allowed
- input_excerpt:
  4.	The absolute error between the zt truth data and the output z shall never exceed a tolerance of 0.01, for the equivalent input of (xt, yt).
- generated_excerpt:
  @startuml start :Receive equivalent input (xt, yt); :Compute zt truth data; :Compute output z; :Calculate absolute error = |zt - z|; if (Absolute error <= 0.01?) then (Yes)   :Requirement met; else (No)   :Requirement violated;   :Raise error or alert; endif stop @enduml
### bp-0007
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1852
- relation_f1: 0.0385
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
  - view the transformation and data source in the info area below the info cube sales overview
  - in the context menu of the data source choose create info package...
  - enter a description for the info package and choose save
  - info package maintenance screen for the scheduler appears
  - go to the tab page schedule and choose start
  - to check the load process choose monitor in the toolbar of info package maintenance
  - select the date and choose execute
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
  @startuml start :Go to the Data Warehousing Workbench; :In the Modeling area choose Info Provider; :View the transformation and Data source\nin the Info Area below the Info Cube Sales Overview; :In the context menu of the Data source,\nchoose Create Info Package...; :Enter a description for the Info Package\nand choose Save; :Info Package maintenance screen\nfor the scheduler appears; :Go to the tab page Schedule\nand choose Start; :To check the load process,\nchoose Monitor in the toolbar of Info Package maintenance; :Select the date and choose Execute; :Monitor for the load process is displayed; :Select the load process for your Data source\nfrom the tree at the left of the screen; :Exit t
### pure-0030
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3158
- relation_f1: 0.0000
- missing_nodes:
  - respond to
  - incoming correlator mode changes
  - other affective external inputs
  - synchronize data processing pipeline
- extra_nodes:
  - receive external input
  - input type
  - correlator mode change
  - process correlator mode change
  - process processing sequence change
  - process parameter change
  - other external input
  - process other external input
- missing_relations:
  - respond to -> incoming correlator mode changes
  - incoming correlator mode changes -> user optional processing sequence
  - user optional processing sequence -> parameter changes
  - parameter changes -> other affective external inputs
  - other affective external inputs -> update internal parameter tables
  - update internal parameter tables -> synchronize data processing pipeline
- input_excerpt:
  Processing Management – The BE shall respond to incoming correlator mode changes, user optional processing sequence and/or parameter changes, and other external inputs that affect the data processing pipeline. Update internal parameter tables and synchronize data processing pipeline with new operational conditions.
- generated_excerpt:
  @startuml skinparam style strictuml  title Processing Management – Correlator Mode & Parameter Updates  start  :Receive External Input;  switch (Input Type) case (Correlator Mode Change)   :Process Correlator Mode Change; case (User Optional Processing Sequence Change)   :Process Processing Sequence Change; case (Parameter Change)   :Process Parameter Change; case (Other External Input)   :Process Other External Input; endswitch  :Update Internal Parameter Tables;  :Synchronize Data Processing Pipeline\nwith New Operational Conditions;  stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
