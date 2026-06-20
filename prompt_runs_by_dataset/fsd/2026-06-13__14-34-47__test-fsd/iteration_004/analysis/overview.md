# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3059
- node_recall: 0.3199
- node_f1: 0.2969
- relation_precision: 0.1217
- relation_recall: 0.1316
- relation_f1: 0.1250
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
- missing_activity: 10
- extra_activity: 10
- missing_or_wrong_relation: 10
- extra_or_wrong_relation: 10

## Representative Failure Cases
### lmc-0040
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - ridge_on set to false
  - determinant of b(inv(wp )b > 1e-12
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - b(inv(wp )b matrix inversion be accurate to 12 digits precision
- extra_nodes:
  - determinant of b(inv(wp
  - invert b(inv(wp )b ) matrix
  - check each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix
- missing_relations:
  - ridge_on set to false -> determinant of b(inv(wp )b > 1e-12
  - determinant of b(inv(wp )b > 1e-12 -> each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance -> b(inv(wp )b matrix inversion be accurate to 12 digits precision
- input_excerpt:
  2.	When the determinant of B(inv(Wp’)B’ is > 1e-12 as indicated by ridge_on set to False, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 12 digits precision in that each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  @startuml start if (determinant of B(inv(Wp')B') > 1e-12\nas indicated by ridge_on set to False) then (yes)   :Invert B(inv(Wp')B') matrix;   :Check each element in the check output matrix is within a 1e-12 tolerance\nwith respect to the elements of a 3x3 identity matrix; endif stop @enduml
### us-0169
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - changes for bulk updating enum value
- extra_nodes:
  - user requests bulk updating one enum value to another
  - system performs bulk updating one enum value to another
- input_excerpt:
  As a user, I want backend changes for bulk updating one enum value to another.
- generated_excerpt:
  @startuml start :User requests bulk updating one enum value to another; :System performs bulk updating one enum value to another; stop @enduml
### bp-0026
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1053
- relation_f1: 0.0000
- missing_nodes:
  - open the promote window
  - click mappings
  - list of crystal reports is displayed
  - select required crystal report
  - click edit crystal report properties
  - modify appropriate fields
  - click apply
  - edited in source system?
- extra_nodes:
  - in the promote window click mappings
  - the list of crystal reports in the source system is displayed
  - select the required crystal report and click edit crystal report properties
  - this tab displays the list of properties and their values
  - modify the appropriate fields and click apply
  - the crystal report mappings tab appears
  - you edit a crystal report in the source system?
  - the following message is displayed beside the crystal report edited
- missing_relations:
  - open the promote window -> click mappings
  - click mappings -> click crystal report mappings
  - click crystal report mappings -> list of crystal reports is displayed
  - list of crystal reports is displayed -> select required crystal report
  - select required crystal report -> click edit crystal report properties
  - click edit crystal report properties -> edit crystal report properties tab appears
  - edit crystal report properties tab appears -> modify appropriate fields
  - modify appropriate fields -> click apply
- input_excerpt:
  26.	modify the properties of a Crystal report1. In the "Promote" window, click Mappings.2. Click Crystal Report Mappings.The list of Crystal reports in the source system is displayed.3. Select the required Crystal report, and click Edit Crystal Report Properties. The "Edit Crystal Report Properties" tab appears, as shown in the following figure: This tab displays the list of properties and their values.4. Modify the appropriate fields, and click Apply. The Crystal Report Mappings tab appears.Note:• If you edit a Crystal report in the source system, the following message is displayed beside the Crystal report: edited• A Crystal Report created using Universes cannot be mapped in the Crystal Re
- generated_excerpt:
  @startuml start :In the "Promote" window, click Mappings; :Click Crystal Report Mappings; :The list of Crystal reports in the source system is displayed; :Select the required Crystal report, and click Edit Crystal Report Properties; :The "Edit Crystal Report Properties" tab appears; :This tab displays the list of properties and their values; :Modify the appropriate fields, and click Apply; :The Crystal Report Mappings tab appears; if (you edit a Crystal report in the source system?) then (yes)   :the following message is displayed beside the Crystal report: edited; else (no) endif switch (per your requirements) case (Save)   :Click Save; case (Promote)   :Click Promote; endswitch end @enduml
### bp-0019
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3077
- relation_f1: 0.0541
- missing_nodes:
  - go to promotion jobs home page
  - click new job
  - enter information
  - enter information
  - enter name
  - enter description
  - enter keywords
  - go to save job field
- extra_nodes:
  - in the promotion jobs home page click new job
  - enter the name for the job
  - enter the description for the job
  - enter the keywords for the job
  - browse for the folder in the save job in field
  - select the folder in the save job in field
  - select the source system from the drop-down list
  - select the destination system from the drop-down list
- missing_relations:
  - log in lifecycle manager tool -> go to promotion jobs home page
  - go to promotion jobs home page -> click new job
  - click new job -> new job window appears
  - new job window appears -> enter information
  - enter information -> enter name
  - enter name -> enter description
  - enter description -> enter keywords
  - enter keywords -> go to save job field
- input_excerpt:
  19.	create a new job by using the LifeCycle Manager tool1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriatefields.4. In the Save Job in field, browse and select the folder in which you wantto save the job.5. Select the source system and the destination system from the drop-downlists.If the name of the system is not displayed in the drop-down list, click theLogin to a new CMS option. A new window is launched. Enter the nameof the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name for the job; :Enter the description for the job; :Enter the keywords for the job; :Browse for the folder in the Save Job in field; :Select the folder in the Save Job in field; :Select the source system from the drop-down list; :Select the destination system from the drop-down list; if (Name of the system is not displayed in the drop-down list?) then (yes)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the name of the system;   :Enter the user name;   :Enter the password; else (no) endif :Click Create; stop @endu
### rac-0008
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3214
- relation_f1: 0.0370
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - slow charging is inactive and front mcu collateral shutdown request flag is 1
  - issue 2.2s timeout warning
  - enter shutdown state
  - slow charging is inactive and bms self-check counter is 1
- extra_nodes:
  - system starts up
  - trigger condition
  - high-voltage shutdown request (charging/discharging
  - switch to state 115
  - switch to state 115
  - state 115 scenario
  - scenario a
  - scenario a condition
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0 -> switch to state 127
  - switch to state 127 -> slow charging is inactive and front mcu collateral shutdown request flag is 1
  - slow charging is inactive and front mcu collateral shutdown request flag is 1 -> switch to state 128
  - switch to state 128 -> shutdown
  - switch to state 128 -> shutdown
  - shutdown -> slow charging is inactive
  - slow charging is inactive -> issue 2.2s timeout warning
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (slow charging is active?) then (yes)   :Enter power-up mode;   switch (Trigger condition)   case (high-voltage shutdown request (charging/discharging) flag is 2)     :Switch to state 115;     switch (State 115 scenario)     case (Scenario a)       switch (Scenario a condition)       case (flag drops to 0 with CP duty cycle at 85%)         :Switch to state 126;       case (BMS self-check counter shows 1)         :Switch to state 130;       case (slow charging becomes inactive)         :Shut down;         stop       endswitch     case (Scenario b)       switch (Scenario b condition)       case (flag drops to 0 with CP duty cycle at 85%)         :Switch to
### rac-0017
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3684
- relation_f1: 0.2778
- missing_nodes:
  - bms counter=1 and battery pre-heating demand=3
  - switch to state 126
  - switch to state 126
  - slow charging is inactive
  - slow charging is inactive
  - shutdown
  - shutdown
  - shutdown
- extra_nodes:
  - system starts up
  - event in state 82
  - bms counter reaches 1 with a battery pre-heating demand of 3
  - transitions to state 126
  - slow charging becomes inactive afterward
  - shuts down and exits
  - shuts down and exits
  - shuts down and exits
- missing_relations:
  - enter state 82 -> bms counter=1 and battery pre-heating demand=3
  - bms counter=1 and battery pre-heating demand=3 -> switch to state 126
  - switch to state 126 -> slow charging is inactive
  - slow charging is inactive -> shutdown
  - switch to state 126 -> slow charging inactive
  - switch to state 126 -> slow charging inactive
  - slow charging inactive -> shutdown
  - slow charging inactive -> shutdown
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU initialization is 0, it enters state 82. From there: - When the BMS counter reaches 1 with a battery pre-heating demand of 3, the system transitions to state 126. If slow charging becomes inactive afterward, it shuts down and exits. - If a pre-charge failure occurs, the system moves to state 126. Should slow charging be inactive at that point, it shuts down and exits. - If slow charging deactivates, the system switches to state 126 before shutting down and exiting. - For AC charging/discharging system faults, the system waits through a 10-second timeout before shifting to state 126. If slow charging is inactive followin
- generated_excerpt:
  @startuml start :System starts up; if (slow charging is active and the front MCU initialization is 0) then (yes)   :Enters state 82;   switch (Event in state 82)   case (BMS counter reaches 1 with a battery pre-heating demand of 3)     :Transitions to state 126;     if (slow charging becomes inactive afterward) then (yes)       :Shuts down and exits;     else (no)     endif   case (Pre-charge failure occurs)     :Moves to state 126;     if (slow charging is inactive at that point) then (yes)       :Shuts down and exits;     else (no)     endif   case (Slow charging deactivates)     :Switches to state 126;     :Shuts down and exits;   case (AC charging/discharging system faults)     :Waits th
### pure-0023
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.0000
- missing_nodes:
  - receive through track-to-train transmission
  - movement authority
  - all other necessary information
  - trainborne equipment active?
  - remain in full supervision
  - remain in full supervision
  - exit full supervision
  - exit full supervision
- extra_nodes:
  - receive movement authority and all other necessary information through track-to-train transmission
  - exit condition
  - trainborne equipment is not active any longer
- missing_relations:
  - receive through track-to-train transmission -> movement authority
  - movement authority -> all other necessary information
  - all other necessary information -> transfer to full supervision automatically
  - transfer to full supervision automatically -> trainborne equipment active?
  - trainborne equipment active? -> remain in full supervision
  - remain in full supervision -> exit full supervision
  - remain in full supervision -> exit full supervision
  - remain in full supervision -> exit full supervision
- input_excerpt:
  Transferring to Full Supervision shall occur automatically when a movement authority and all other necessary information is received through track-to-train transmission. The trainborne equipment shall remain in Full Supervision until the trainborne equipment is not active any longer, when Shunting is selected, or when Partial Supervision information is received.
- generated_excerpt:
  @startuml start :Receive movement authority and all other necessary information through track-to-train transmission; :Transfer to Full Supervision automatically; :Remain in Full Supervision; switch (Exit condition) case (Trainborne equipment is not active any longer) case (Shunting is selected) case (Partial Supervision information is received) endswitch end @enduml
### pure-0058
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4667
- relation_f1: 0.2143
- missing_nodes:
  - open keepass
  - select open->database
  - select database
  - folder is suitable?
  - file not found appears
  - choose cancel
  - password is right?
- extra_nodes:
  - user opens keepass and select open->database
  - user action after navigating
  - user chooses cancel
  - user selects a type of folder non suitable for database
  - user selects a type of folder non suitable for database
  - a message file not found appears
  - user selects a database
  - master password is wrong
- missing_relations:
  - open keepass -> select open->database
  - select open->database -> navigate through folders
  - navigate through folders -> select database
  - select database -> folder is suitable?
  - folder is suitable? -> file not found appears
  - file not found appears -> select another folder
  - select another folder -> choose cancel
  - exit from keepass -> type master password
- input_excerpt:
  1. User opens KeePass and select Open->Database 2. User navigates through his folders 3. User selects a database 4. User types Master Password 5. The main database window opens 3.2.2.2.1 Alternative Data Flow 1 3a. User selects a type of folder non suitable for database 3b. A message “file not found” appears 3c. User selects another folder 3.2.2.2.2 Alternative Data Flow 2 4a. Master Password is wrong 4b. A message “invalid/wrong key” appears 4c. User types another master key 3.2.2.2.3 Alternative Data Flow 3 3. User chooses cancel 4. Exit from KeePass
- generated_excerpt:
  @startuml start :User opens KeePass and select Open->Database; repeat   :User navigates through his folders;   switch (User action after navigating)   case (User chooses cancel)     :Exit from KeePass;     stop   case (User selects a type of folder non suitable for database)     :A message "file not found" appears;     :User selects another folder;   case (User selects a database)     :User types Master Password;     repeat       if (Master Password is wrong) then (yes)         :A message "invalid/wrong key" appears;         :User types another master key;       else (no)         :The main database window opens;       endif     repeat while (Master Password is wrong)     stop   endswitch rep

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
