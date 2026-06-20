# Prompt Evaluation Analysis

## Summary
- count: 5
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.1607
- node_recall: 0.1333
- node_f1: 0.1457
- relation_precision: 0.1179
- relation_recall: 0.1405
- relation_f1: 0.1283
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 5.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.4812
- llm_node_recall: 0.5103
- llm_node_f1: 0.4800
- llm_relation_precision: 0.3971
- llm_relation_recall: 0.4023
- llm_relation_f1: 0.3418

## Failure Types
- missing_activity: 5
- extra_activity: 5
- missing_or_wrong_relation: 5
- extra_or_wrong_relation: 5
- wrong_parallel: 1

## Representative Failure Cases
### lmc-0011
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.0000
- llm_relation_f1: 0.0000
- missing_nodes:
  - system is supported?
  - sensor data is good?
  - autopilot change states from pullup to transition
- missing_relations:
  - system is supported? -> sensor data is good? [yes]
  - sensor data is good? -> autopilot change states from pullup to transition [yes]
- input_excerpt:
  7.	The autopilot shall change states from PULLUP to TRANSITION when the system is supported and sensor data is good.
- generated_excerpt:
  @startuml skinparam style strictuml  state PULLUP state TRANSITION  PULLUP --> TRANSITION : [system is supported AND sensor data is good] @enduml
### pure-0061
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4167
- llm_relation_f1: 0.1667
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
  - user types in the search field
  - user does not type anything
  - nothing appears in the main window
  - is search input two or more words?
  - nothing appears in the main window
  - is search input not related to the database?
  - nothing appears in the main window
- missing_relations:
  - open keepass -> information can be input
  - information can be input -> password [fork]
  - information can be input -> user name [fork]
  - information can be input -> url [fork]
  - information can be input -> word of notes [fork]
  - information can be input -> title [fork]
  - information can be input -> group [fork]
  - password -> input
- input_excerpt:
  1. User opens KeePass 2. User types a password, user name, URL, word of notes, title or group that exist in the database 3. The list of data related to search word are appeared in the main window 3.5.2.2 Alternative Data Flows 3.5.2.2.1 Alternative Data Flow 1 2. User types two or more words in the search field 3. Nothing appears in the main window 3.5.2.2.2 Alternative Data Flow 2 2. User does not type anything 3. Nothing appears in the main window 3.5.2.2.3 Alternative Data Flow 3 2a. User types part or even just one character of password, user name, URL, word of notes, title or group 3.5.2.2.4 Alternative Data Flow 4 2. User types data not related with the database 3. Nothing appears in t
- generated_excerpt:
  @startuml start :User opens KeePass; fork   :User types in the search field; fork again   :User does not type anything;   :Nothing appears in the main window;   stop end fork  if (Is search input two or more words?) then (Yes)   :Nothing appears in the main window;   stop elseif (Is search input not related to the database?) then (Yes)   :Nothing appears in the main window;   stop else (No - Input is a single word or part/character)   if (Does the input match password, user name, URL, word of notes, title or group in the database?) then (Yes)     :List of related data appears in the main window;   else (No)     :Nothing appears in the main window;   endif endif stop @enduml
### us-0094
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2353
- llm_relation_f1: 0.2500
- missing_nodes:
  - support multi-version datapackages
  - develop all projects independently
  - deploy projects locally
- extra_nodes:
  - web developer initiates datapackage installation
  - specify datapackage name
  - specify required version
  - is the specified version already installed globally?
  - download specified datapackage version
  - use cached datapackage version
  - install datapackage version into project-specific directory
  - update project dependency manifest
- missing_relations:
  - support multi-version datapackages -> develop all projects independently
  - develop all projects independently -> deploy projects locally
- input_excerpt:
  As a Web Developer, I want to be able to install multiple versions of the same datapackage separately, so that that all my projects could be developed independently and deployed locally.
- generated_excerpt:
  @startuml skinparam style strictuml  title Install Multiple Versions of the Same Datapackage  start  :Web Developer initiates datapackage installation;  :Specify datapackage name; :Specify required version;  if (Is the specified version already installed globally?) then (No)   :Download specified datapackage version; else (Yes)   :Use cached datapackage version; endif  :Install datapackage version into project-specific directory;  :Update project dependency manifest;  :Verify project isolation;  :Confirm independent local deployment capability;  stop  @enduml
### bp-0020
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2400
- relation_f1: 0.0833
- llm_element_status: success
- llm_node_f1: 0.9189
- llm_relation_f1: 0.5517
- missing_nodes:
  - more information?
  - see creating a new job on page 37
  - open source system drop-down list
  - select login
  - to a new cms
  - enter user credentials
  - select appropriate authentication type
  - click login
- extra_nodes:
  - from the source system drop-down list select login to a new cms
  - enter the user credentials select the appropriate authentication type and click login
  - from the destination system drop-down list select login to a new cms
  - enter the user credentials select the appropriate authentication type and click login
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37 [yes]
  - see creating a new job on page 37 -> open source system drop-down list
  - more information? -> open source system drop-down list [no]
  - open source system drop-down list -> select login
  - select login -> to a new cms
  - to a new cms -> login to system dialog box appears
  - login to system dialog box appears -> enter user credentials
- input_excerpt:
  20.	log into a new CMS1. Log into the LifeCycle Manager tool.2. Create a new job.For more information on creating a new job, see Creating a New Job onpage 37.3. From the Source System drop-down list, select Login to a New CMS.The "Login to System" dialog box appears.4. Enter the user credentials, select the appropriate authentication type, andclick Login.5. From the Destination System drop-down list, select Login to a NewCMS.6. Enter the user credentials, select the appropriate authentication type, andclick Login.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :From the Source System drop-down list,\nselect "Login to a New CMS"; :The "Login to System" dialog box appears; :Enter the user credentials,\nselect the appropriate authentication type,\nand click Login; :From the Destination System drop-down list,\nselect "Login to a New CMS"; :Enter the user credentials,\nselect the appropriate authentication type,\nand click Login; stop @enduml
### rac-0006
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4286
- relation_f1: 0.5116
- llm_element_status: success
- llm_node_f1: 0.8293
- llm_relation_f1: 0.7407
- missing_nodes:
  - condition judgement
  - shutdown
  - switch to state 110
  - switch to state 28
  - shutdown
  - switch to state 110
  - switch to state 28
  - battery soc reaches 80 and dcdc state is 3
- extra_nodes:
  - system start up
  - remote mode path
  - remote mode enabled?
  - enter state 110
  - go to state 28
  - shut down
  - pet mode path
  - pet mode request received?
- missing_relations:
  - enter power-up mode -> condition judgement
  - condition judgement -> switch to state 110 [case remote mode is enabled]
  - condition judgement -> switch to state 110 [case pet mode request is received]
  - condition judgement -> switch to state 110 [case battery soc is 20]
  - switch to state 28 -> battery soc reaches 80 and dcdc state is 3
  - battery soc reaches 80 and dcdc state is 3 -> shutdown [if yes]
- input_excerpt:
  After the system starts up: If slow charging is active, go into power-up mode. Then: 1.  If remote mode is enabled, enter state 110. Then, if slow charging becomes inactive, go to state 28. Finally, if remote mode is disabled, shut down and end. 2.  If a pet mode request comes in, switch to state 110. Then, if slow charging is inactive, move to state 28. Once the pet mode request is handled, shut down and end. 3.  If the battery SOC is 20, enter state 110. Then, if slow charging is inactive, switch to state 28. If the SOC later reaches 80 and the DCDC state is 3, shut down and end.
- generated_excerpt:
  @startuml start :System Start Up; if (Slow charging active?) then (Yes)   :Enter Power-Up Mode;   fork     :Remote Mode Path;     if (Remote mode enabled?) then (Yes)       :Enter State 110;       if (Slow charging inactive?) then (Yes)         :Go to State 28;       endif       if (Remote mode disabled?) then (Yes)         :Shut down;         stop       endif     else (No)     endif   fork again     :Pet Mode Path;     if (Pet mode request received?) then (Yes)       :Switch to State 110;       if (Slow charging inactive?) then (Yes)         :Move to State 28;       endif       :Pet mode request handled;       :Shut down;       stop     else (No)     endif   fork again     :Battery SOC Path

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
