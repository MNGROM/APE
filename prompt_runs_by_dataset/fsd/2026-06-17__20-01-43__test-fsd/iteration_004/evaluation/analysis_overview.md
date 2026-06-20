# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.5498
- node_recall: 0.5086
- node_f1: 0.5284
- relation_precision: 0.5005
- relation_recall: 0.4343
- relation_f1: 0.4651
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 10.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.8122
- llm_node_recall: 0.7985
- llm_node_f1: 0.7938
- llm_relation_precision: 0.6211
- llm_relation_recall: 0.5357
- llm_relation_f1: 0.5604

## Failure Types
- missing_activity: 8
- extra_activity: 8
- missing_or_wrong_relation: 8
- extra_or_wrong_relation: 8
- wrong_parallel: 2
- wrong_loop: 1

## Representative Failure Cases
### rac-0008
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1875
- relation_f1: 0.0476
- llm_element_status: success
- llm_node_f1: 0.1724
- llm_relation_f1: 0.0635
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - switch to state 127
  - slow charging is inactive and front mcu collateral shutdown request flag is 1
  - switch to state 128
  - shutdown
  - issue 2.2s timeout warning
  - enter shutdown state
  - slow charging is inactive and bms self-check counter is 1
- extra_nodes:
  - system starts up
  - condition
  - high-voltage shutdown request flag is 2
  - switch to state 115
  - condition after switching
  - flag drops to 0 with cp duty cycle at 85
  - switch to state 126
  - bms self-check counter shows 1
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0 -> switch to state 127 [yes]
  - switch to state 127 -> slow charging is inactive and front mcu collateral shutdown request flag is 1
  - slow charging is inactive and front mcu collateral shutdown request flag is 1 -> switch to state 128 [yes]
  - switch to state 128 -> shutdown
  - slow charging is inactive and front mcu collateral shutdown request flag is 1 -> slow charging is inactive [no]
  - slow charging is inactive -> issue 2.2s timeout warning [yes]
  - issue 2.2s timeout warning -> switch to state 128
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active?) then (yes)   :Enter power-up mode;   switch (Condition)     case (High-voltage shutdown request flag is 2)       :Switch to state 115;       switch (Condition after switching)         case (Flag drops to 0 with CP duty cycle at 85%)           :Switch to state 126;         case (BMS self-check counter shows 1)           :Switch to state 130;         case (Slow charging becomes inactive)           :Shut down and end;       endswitch     case (High-voltage shutdown request flag is 2)       :Switch to state 115;       switch (Condition after switching)         case (Flag drops to 0 with CP duty cycle at 85%)           :Switch to st
### bp-0019
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.0541
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.3902
- missing_nodes:
  - log in lifecycle manager tool
  - click new job
  - enter information
  - enter name
  - enter description
  - enter keywords
  - go to save job field
  - browse and select folder
- extra_nodes:
  - log into the lifecycle manager tool.
  - enter the name description and keywords for the job in the appropriate fields.
  - in the save job in field browse and select the folder in which you want to save the job.
  - select the source system and the destination system from the drop-down lists.
  - the name of the system is not displayed in the drop-down list?
  - click the login to a new cms option.
  - enter the name of the system along with the user name and password.
- missing_relations:
  - log in lifecycle manager tool -> go to promotion jobs home page
  - click new job -> new job window appears
  - new job window appears -> enter information
  - enter information -> enter name [fork]
  - enter information -> enter description [fork]
  - enter information -> enter keywords [fork]
  - enter name -> go to save job field [merge]
  - enter description -> go to save job field [merge]
- input_excerpt:
  19.	create a new job by using the LifeCycle Manager tool1. Log into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, click New Job. The "New Job"window appears .3. Enter the name, description, and keywords for the job in the appropriatefields.4. In the Save Job in field, browse and select the folder in which you wantto save the job.5. Select the source system and the destination system from the drop-downlists.If the name of the system is not displayed in the drop-down list, click theLogin to a new CMS option. A new window is launched. Enter the nameof the system along with the user name and password.6. Click Create.
- generated_excerpt:
  @startuml start :Log into the LifeCycle Manager tool.; :In the "Promotion Jobs" home page, click New Job.; :The "New Job" window appears.; :Enter the name, description, and keywords for the job in the appropriate fields.; :In the Save Job in field, browse and select the folder in which you want to save the job.; :Select the source system and the destination system from the drop-down lists.; if (the name of the system is not displayed in the drop-down list?) then (yes)   :click the Login to a new CMS option.;   :A new window is launched.;   :Enter the name of the system along with the user name and password.; else (no) endif :Click Create.; stop @enduml
### bp-0026
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2581
- relation_f1: 0.2581
- llm_element_status: success
- llm_node_f1: 0.6316
- llm_relation_f1: 0.3784
- missing_nodes:
  - open the promote window
  - click mappings
  - select required crystal report
  - modify appropriate fields
  - click apply
  - edited in source system?
  - edited is displayed
  - created using universes?
- extra_nodes:
  - in the promote window click mappings
  - this tab displays the list of properties and their values
  - modify the appropriate fields and click apply
  - the crystal report mappings tab appears
  - per your requirements
  - click save
  - click promote
- missing_relations:
  - open the promote window -> click mappings
  - list of crystal reports is displayed -> select required crystal report
  - edit crystal report properties tab appears -> modify appropriate fields
  - modify appropriate fields -> click apply
  - click apply -> edited in source system?
  - edited in source system? -> edited is displayed [yes]
  - edited in source system? -> created using universes? [no]
  - edited is displayed -> created using universes? [merge]
- input_excerpt:
  26.	modify the properties of a Crystal report1. In the "Promote" window, click Mappings.2. Click Crystal Report Mappings.The list of Crystal reports in the source system is displayed.3. Select the required Crystal report, and click Edit Crystal Report Properties. The "Edit Crystal Report Properties" tab appears, as shown in the following figure: This tab displays the list of properties and their values.4. Modify the appropriate fields, and click Apply. The Crystal Report Mappings tab appears.Note:• If you edit a Crystal report in the source system, the following message is displayed beside the Crystal report: edited• A Crystal Report created using Universes cannot be mapped in the Crystal Re
- generated_excerpt:
  @startuml start :In the "Promote" window, click Mappings; :Click Crystal Report Mappings; :The list of Crystal reports in the source system is displayed; :Select the required Crystal report, and click Edit Crystal Report Properties; :The "Edit Crystal Report Properties" tab appears; :This tab displays the list of properties and their values; :Modify the appropriate fields, and click Apply; :The Crystal Report Mappings tab appears; if (per your requirements) then (Save)   :Click Save; else (Promote)   :Click Promote; endif @enduml
### lmc-0040
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2857
- relation_f1: 0.6667
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.4000
- missing_nodes:
  - ridge_on set to false
  - determinant of b(inv(wp )b > 1e-12
  - b(inv(wp )b matrix inversion be accurate to 12 digits precision
- extra_nodes:
  - determinant of b(inv(wp ))b > 1e-12 (ridge_on set to false)?
  - invert the b(inv(wp ))b matrix
- missing_relations:
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance -> b(inv(wp )b matrix inversion be accurate to 12 digits precision
- input_excerpt:
  2.	When the determinant of B(inv(Wp’)B’ is > 1e-12 as indicated by ridge_on set to False, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 12 digits precision in that each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  @startuml start if (determinant of B(inv(Wp'))B' > 1e-12\n(ridge_on set to False)?) then (Yes)   :Invert the B(inv(Wp'))B' matrix;   :Check if each element in the output matrix\nis within a 1e-12 tolerance with respect\nto the elements of a 3x3 identity matrix; else (No) endif stop @enduml
### pure-0058
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4444
- relation_f1: 0.2069
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.7647
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
  - user selects a type of folder non suitable for database?
  - a message file not found appears
  - user selects another folder
  - master password is wrong?
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
  @startuml start :User opens KeePass and select Open->Database; :User navigates through his folders; if (User chooses cancel?) then (yes)   :Exit from KeePass;   stop else (no)   :User selects a database;   if (User selects a type of folder non suitable for database?) then (yes)     :A message "file not found" appears;     :User selects another folder;   else (no)   endif   :User types Master Password;   if (Master Password is wrong?) then (yes)     :A message "invalid/wrong key" appears;     :User types another master key;   else (no)   endif   :The main database window opens; endif stop @enduml
### pure-0023
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5333
- relation_f1: 0.3333
- llm_element_status: success
- llm_node_f1: 0.3158
- llm_relation_f1: 0.0800
- missing_nodes:
  - receive through track-to-train transmission
  - movement authority
  - all other necessary information
  - trainborne equipment active?
  - remain in full supervision
- extra_nodes:
  - receive a movement authority and all other necessary information through track-to-train transmission
  - trainborne equipment is not active any longer
- missing_relations:
  - receive through track-to-train transmission -> movement authority [fork]
  - receive through track-to-train transmission -> all other necessary information [fork]
  - movement authority -> transfer to full supervision automatically [merge]
  - all other necessary information -> transfer to full supervision automatically [merge]
  - transfer to full supervision automatically -> trainborne equipment active?
  - trainborne equipment active? -> remain in full supervision [yes]
  - remain in full supervision -> shunting is selected?
  - shunting is selected? -> remain in full supervision [no]
- input_excerpt:
  Transferring to Full Supervision shall occur automatically when a movement authority and all other necessary information is received through track-to-train transmission. The trainborne equipment shall remain in Full Supervision until the trainborne equipment is not active any longer, when Shunting is selected, or when Partial Supervision information is received.
- generated_excerpt:
  @startuml start :Receive a movement authority and all other necessary information through track-to-train transmission; :Transfer to Full Supervision automatically; switch (Condition to exit Full Supervision) case (Trainborne equipment is not active any longer) case (Shunting is selected) case (Partial Supervision information is received) endswitch stop @enduml
### lmc-0052
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5714
- relation_f1: 0.4000
- llm_element_status: success
- llm_node_f1: 0.9091
- llm_relation_f1: 0.7273
- missing_nodes:
  - not invertible
  - invertible
- extra_nodes:
  - matrix is invertible
- missing_relations:
  - theta = +/- pi/2 radians? -> not invertible [yes]
  - theta = +/- pi/2 radians? -> invertible [no]
- input_excerpt:
  4.	The Rotation Matrix, DCM321, shall be invertible with the exception of the case where theta = +/- pi/2 radians.
- generated_excerpt:
  @startuml start :Invert the Rotation Matrix DCM321; if (theta = +/- pi/2 radians?) then (yes) else (no)   :Matrix is invertible; endif stop @enduml
### rac-0017
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.6154
- relation_f1: 0.5455
- llm_element_status: success
- llm_node_f1: 0.9091
- llm_relation_f1: 0.8000
- missing_nodes:
  - shutdown
  - after 10s
- extra_nodes:
  - system starts up
  - condition?
  - transition to state 126
  - shut down and exit
  - move to state 126
  - slow charging deactivates
  - wait through a 10-second timeout
  - shift to state 126
- missing_relations:
  - enter state 82 -> bms counter=1 and battery pre-heating demand=3
  - bms counter=1 and battery pre-heating demand=3 -> pre-charge failure occurs [no]
  - pre-charge failure occurs -> slow charging is inactive [no]
  - slow charging is inactive -> ac charging/discharging system fault [no]
  - ac charging/discharging system fault -> after 10s [yes]
  - after 10s -> switch to state 126
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU initialization is 0, it enters state 82. From there: - When the BMS counter reaches 1 with a battery pre-heating demand of 3, the system transitions to state 126. If slow charging becomes inactive afterward, it shuts down and exits. - If a pre-charge failure occurs, the system moves to state 126. Should slow charging be inactive at that point, it shuts down and exits. - If slow charging deactivates, the system switches to state 126 before shutting down and exiting. - For AC charging/discharging system faults, the system waits through a 10-second timeout before shifting to state 126. If slow charging is inactive followin
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active\nand front MCU initialization is 0?) then (yes)   :Enter state 82;   switch (Condition?)   case (BMS counter reaches 1\nwith battery pre-heating demand of 3)     :Transition to state 126;     if (Slow charging becomes inactive?) then (yes)       :Shut down and exit;       stop     else (no)     endif   case (Pre-charge failure occurs)     :Move to state 126;     if (Slow charging is inactive?) then (yes)       :Shut down and exit;       stop     else (no)     endif   case (Slow charging deactivates)     :Switch to state 126;     :Shut down and exit;     stop   case (AC charging/discharging system fault)     :Wait through a 10-sec

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
