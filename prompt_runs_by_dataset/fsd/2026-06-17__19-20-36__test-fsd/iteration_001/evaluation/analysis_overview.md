# Prompt Evaluation Analysis

## Summary
- count: 5
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3805
- node_recall: 0.3623
- node_f1: 0.3712
- relation_precision: 0.2577
- relation_recall: 0.2782
- relation_f1: 0.2676
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 5.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.7511
- llm_node_recall: 0.9129
- llm_node_f1: 0.7900
- llm_relation_precision: 0.5573
- llm_relation_recall: 0.6108
- llm_relation_f1: 0.5211

## Failure Types
- extra_activity: 5
- extra_or_wrong_relation: 5
- missing_activity: 4
- missing_or_wrong_relation: 4
- wrong_loop: 1

## Representative Failure Cases
### us-0046
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4706
- llm_relation_f1: 0.2500
- missing_nodes:
  - embed interactive data preview
  - provide data correctness
- extra_nodes:
  - publisher selects data to embed
  - generate embed code for interactive preview
  - publisher copies embed code
  - publisher pastes embed code into their site
  - site renders interactive data preview
  - user visits the publisher s site
  - user interacts with the data preview
  - does the preview show the correct data?
- missing_relations:
  - embed interactive data preview -> provide data correctness
- input_excerpt:
  As a publisher, I want to embed an interactive preview of my data on my site, so that users can be encouraged that this is the correct data for them.
- generated_excerpt:
  @startuml skinparam style strictuml  title Publisher: Embed Interactive Data Preview on Site  start  :Publisher selects data to embed;  :Generate embed code for interactive preview;  :Publisher copies embed code;  :Publisher pastes embed code into their site;  :Site renders interactive data preview;  :User visits the publisher's site;  :User interacts with the data preview;  if (Does the preview show the correct data?) then (Yes)   :User is encouraged data is correct;   :User proceeds to access/use the data;   stop else (No)   :User leaves or seeks alternative data;   stop endif  @enduml
### lmc-0031
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.2222
- llm_element_status: success
- llm_node_f1: 0.7143
- llm_relation_f1: 0.5714
- missing_nodes:
  - in nlguidance
  - counter clockwise loiter for uav
  - as the picture above?
  - return tangent aim point 2
- extra_nodes:
  - which aim point results in a counter clockwise loiter?
  - select aim point 1
  - select aim point 2
  - return selected aim point
- missing_relations:
  - in nlguidance -> select inertial position vector of aim point 1 or 2
  - counter clockwise loiter for uav -> as the picture above?
  - as the picture above? -> return tangent aim point 2 [yes]
- input_excerpt:
  4.	NLGuidance shall always select an inertial position vector of aim point #1 or #2 which shall result in a counter clockwise loiter for the UAV.  For example, the picture above with vehicle position, UAV, would return Tangent Aim Point #2.
- generated_excerpt:
  @startuml start :Select inertial position vector of aim point #1 or #2; if (Which aim point results in a counter clockwise loiter?) then (Aim Point #1)   :Select Aim Point #1; else (Aim Point #2)   :Select Aim Point #2; endif :Return selected aim point; stop @enduml
### bp-0020
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3158
- relation_f1: 0.0952
- llm_element_status: success
- llm_node_f1: 0.9189
- llm_relation_f1: 0.4828
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
  - enter user credentials select authentication type click login
  - from the destination system drop-down list select login to a new cms
- missing_relations:
  - create a new job -> more information?
  - more information? -> see creating a new job on page 37 [yes]
  - more information? -> open source system drop-down list [no]
  - see creating a new job on page 37 -> open source system drop-down list [merge]
  - open source system drop-down list -> select login
  - select login -> to a new cms
  - to a new cms -> login to system dialog box appears
  - login to system dialog box appears -> enter user credentials
- input_excerpt:
  20.	log into a new CMS1. Log into the LifeCycle Manager tool.2. Create a new job.For more information on creating a new job, see Creating a New Job onpage 37.3. From the Source System drop-down list, select Login to a New CMS.The "Login to System" dialog box appears.4. Enter the user credentials, select the appropriate authentication type, andclick Login.5. From the Destination System drop-down list, select Login to a NewCMS.6. Enter the user credentials, select the appropriate authentication type, andclick Login.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :Create a new job; :From the Source System drop-down list,\nselect "Login to a New CMS"; :The "Login to System" dialog box appears; :Enter user credentials,\nselect authentication type,\nclick Login; :From the Destination System drop-down list,\nselect "Login to a New CMS"; :Enter user credentials,\nselect authentication type,\nclick Login; stop @enduml
### pure-0058
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4444
- relation_f1: 0.2759
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.8571
- missing_nodes:
  - open keepass
  - select open->database
  - navigate through folders
  - select database
  - folder is suitable?
  - file not found appears
  - select another folder
  - password is right?
- extra_nodes:
  - user opens keepass and select open->database
  - user navigates through his folders
  - user selects a database
  - folder type suitable for database?
  - a message file not found appears
  - user selects another folder
  - master password is correct?
- missing_relations:
  - open keepass -> select open->database
  - select open->database -> navigate through folders
  - navigate through folders -> select database
  - select database -> folder is suitable?
  - folder is suitable? -> file not found appears [no]
  - file not found appears -> select another folder
  - select another folder -> navigate through folders [loop]
  - folder is suitable? -> choose cancel [yes]
- input_excerpt:
  1. User opens KeePass and select Open->Database 2. User navigates through his folders 3. User selects a database 4. User types Master Password 5. The main database window opens 3.2.2.2.1 Alternative Data Flow 1 3a. User selects a type of folder non suitable for database 3b. A message “file not found” appears 3c. User selects another folder 3.2.2.2.2 Alternative Data Flow 2 4a. Master Password is wrong 4b. A message “invalid/wrong key” appears 4c. User types another master key 3.2.2.2.3 Alternative Data Flow 3 3. User chooses cancel 4. Exit from KeePass
- generated_excerpt:
  @startuml start :User opens KeePass and select Open->Database; :User navigates through his folders;  if (User chooses cancel?) then (yes)   :Exit from KeePass;   stop else (no)   :User selects a database;   if (Folder type suitable for database?) then (no)     :A message "file not found" appears;     :User selects another folder;   else (yes)   endif endif  :User types Master Password;  if (Master Password is correct?) then (no)   :A message "invalid/wrong key" appears;   :User types another master key; else (yes) endif  :The main database window opens; stop @enduml
### rac-0003
- dataset: rac
- failure_types: extra_activity, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.8333
- relation_f1: 0.7119
- llm_element_status: success
- llm_node_f1: 0.8462
- llm_relation_f1: 0.4444
- missing_nodes:
  - shutdown
- extra_nodes:
  - system startup
  - check remote flag
  - system shuts down
  - check ignition switch front mcu init
  - check ignition switch front mcu init (1)
  - check ignition switch bms counter
  - check ignition switch (additional)
- missing_relations:
  - switch to state 46 -> remote flag becomes 0
  - remote flag is 1 -> ignition switch is 2 and front mcu initialization state is 0 [no]
  - switch to state 46 -> ignition switch becomes 0
  - switch to state 40 -> ignition switch becomes 0
  - ignition switch is 2 and front mcu initialization state is 1 -> ignition switch is 2 and bms self-check counter is 1 [no]
- input_excerpt:
  After the system starts up, the following decision paths apply:  1) When the remote flag is 1, the system enters state 28.    If the power battery discharge protection flag is 1 and SOC is 0, it switches to state 46.    Should the remote flag become 0, the system shuts down and ends.  2) If the ignition switch is at position 2 and the front MCU initialization state is 0, the system switches to state 12.    When the discharge protection flag is 1 and front MCU initialization state is 1, it switches to state 46.    If the ignition switch changes to 0, the system shuts down and ends.  3) When the ignition switch is at 2 and front MCU initialization state is 1, the system switches to state 20.  
- generated_excerpt:
  @startuml start :System Startup;  fork   :Check Remote Flag;   if (Remote flag = 1?) then (Yes)     :Enter State 28;     if (Power battery discharge protection flag = 1\nand SOC = 0?) then (Yes)       :Switch to State 46;       stop     else (No)     endif     if (Remote flag = 0?) then (Yes)       :System shuts down;       end     else (No)     endif   else (No)   endif fork again   :Check Ignition Switch & Front MCU Init;   if (Ignition switch = 2\nand Front MCU init state = 0?) then (Yes)     :Switch to State 12;     if (Discharge protection flag = 1\nand Front MCU init state = 1?) then (Yes)       :Switch to State 46;       stop     else (No)     endif     if (Ignition switch = 0?) then 

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
