# Prompt Evaluation Analysis

## Summary
- count: 10
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.4139
- node_recall: 0.3833
- node_f1: 0.3848
- relation_precision: 0.2713
- relation_recall: 0.2467
- relation_f1: 0.2538
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
- missing_activity: 9
- extra_activity: 9
- missing_or_wrong_relation: 9
- extra_or_wrong_relation: 9

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
  - check determinant of b(inv(wp ))b
  - determinant > 1e-12?
  - set ridge_on to false
  - invert b(inv(wp ))b matrix
  - compute check output matrix
  - verify each element of check output matrix is within 1e-12 tolerance of 3x3 identity matrix
- missing_relations:
  - ridge_on set to false -> determinant of b(inv(wp )b > 1e-12
  - determinant of b(inv(wp )b > 1e-12 -> each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance -> b(inv(wp )b matrix inversion be accurate to 12 digits precision
- input_excerpt:
  2.	When the determinant of B(inv(Wp’)B’ is > 1e-12 as indicated by ridge_on set to False, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 12 digits precision in that each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  @startuml start :Check determinant of B(inv(Wp'))B'; if (determinant > 1e-12?) then (Yes)   :Set ridge_on to False;   :Invert B(inv(Wp'))B' matrix;   :Compute check output matrix;   :Verify each element of check output matrix is within 1e-12 tolerance of 3x3 identity matrix; else (No) endif stop @enduml
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
  - select enum value to update
  - select target enum value
  - is confirmation provided?
  - bulk update enum value to target
  - cancel bulk update
- input_excerpt:
  As a user, I want backend changes for bulk updating one enum value to another.
- generated_excerpt:
  @startuml start :Select enum value to update; :Select target enum value; if (Is confirmation provided?) then (yes)   :Bulk update enum value to target; else (no)   :Cancel bulk update; endif stop @enduml
### bp-0019
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1290
- relation_f1: 0.0000
- missing_nodes:
  - go to promotion jobs home page
  - click new job
  - new job window appears
  - enter information
  - enter information
  - enter name
  - enter description
  - enter keywords
- extra_nodes:
  - click new job in the promotion jobs home page
  - enter the name description and keywords for the job
  - browse and select the folder to save the job in
  - select the source system and the destination system
  - system name in drop-down list?
  - click the login to a new cms option
  - enter the system name user name and password
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
  @startuml start :Log into the LifeCycle Manager tool; :Click New Job in the "Promotion Jobs" home page; :Enter the name, description, and keywords for the job; :Browse and select the folder to save the job in; :Select the source system and the destination system; if (System name in drop-down list?) then (No)   :Click the Login to a new CMS option;   :Enter the system name, user name, and password; else (Yes) endif :Click Create; stop @enduml
### lmc-0052
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2500
- relation_f1: 0.3333
- missing_nodes:
  - rotation matrix dcm321
  - not invertible
  - invertible
- extra_nodes:
  - check theta value
  - dcm321 is not invertible
  - dcm321 is invertible
- missing_relations:
  - rotation matrix dcm321 -> theta = +/- pi/2 radians?
  - not invertible -> invertible
- input_excerpt:
  4.	The Rotation Matrix, DCM321, shall be invertible with the exception of the case where theta = +/- pi/2 radians.
- generated_excerpt:
  @startuml start :Check theta value; if (theta = +/- pi/2 radians?) then (Yes) :DCM321 is not invertible; else (No) :DCM321 is invertible; endif stop @enduml
### bp-0026
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.3429
- relation_f1: 0.2424
- missing_nodes:
  - open the promote window
  - click mappings
  - list of crystal reports is displayed
  - edited in source system?
  - edited is displayed
  - created using universes?
  - cannot be mapped
  - use connections mappings
- extra_nodes:
  - click mappings in the promote window
  - the list of crystal reports in the source system is displayed
  - the crystal report mappings tab appears
  - requirement?
  - click save
  - click promote
- missing_relations:
  - open the promote window -> click mappings
  - click mappings -> click crystal report mappings
  - click crystal report mappings -> list of crystal reports is displayed
  - list of crystal reports is displayed -> select required crystal report
  - click apply -> edited in source system?
  - edited in source system? -> edited is displayed
  - edited is displayed -> created using universes?
  - created using universes? -> cannot be mapped
- input_excerpt:
  26.	modify the properties of a Crystal report1. In the "Promote" window, click Mappings.2. Click Crystal Report Mappings.The list of Crystal reports in the source system is displayed.3. Select the required Crystal report, and click Edit Crystal Report Properties. The "Edit Crystal Report Properties" tab appears, as shown in the following figure: This tab displays the list of properties and their values.4. Modify the appropriate fields, and click Apply. The Crystal Report Mappings tab appears.Note:• If you edit a Crystal report in the source system, the following message is displayed beside the Crystal report: edited• A Crystal Report created using Universes cannot be mapped in the Crystal Re
- generated_excerpt:
  @startuml start :Click Mappings in the "Promote" window; :Click Crystal Report Mappings; :The list of Crystal reports in the source system is displayed; :Select the required Crystal report; :Click Edit Crystal Report Properties; :The "Edit Crystal Report Properties" tab appears; :Modify the appropriate fields; :Click Apply; :The Crystal Report Mappings tab appears; if (Requirement?) then (Save)   :Click Save; else (Promote)   :Click Promote; endif @enduml
### rac-0008
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4390
- relation_f1: 0.0513
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - slow charging is inactive and front mcu collateral shutdown request flag is 1
  - issue 2.2s timeout warning
  - enter shutdown state
  - slow charging is inactive and bms self-check counter is 1
- extra_nodes:
  - system starts up
  - high-voltage shutdown request flag is 2?
  - switch to state 115
  - switch to state 115
  - condition met?
  - condition met?
  - flag drops to 0 with cp duty cycle at 85
  - bms self-check counter is 1
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
  @startuml start :System starts up; if (Slow charging is active?) then (yes)   :Enter power-up mode;   if (High-voltage shutdown request flag is 2?) then (yes)     :Switch to state 115;     switch (Condition met?)     case (Flag drops to 0 with CP duty cycle at 85%)       :Switch to state 126;     case (BMS self-check counter is 1)       :Switch to state 130;     case (Battery pre-heating is required)       :Switch to state 130;     case (CP duty cycle hits 85% with CP amplitude at 3000)       :Switch to state 130;     case (Slow charging becomes inactive)       :Shut down;       end     endswitch   elseif (Central control charging/discharging command is 2\nand vehicle isn't in charging/disch
### rac-0017
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5263
- relation_f1: 0.4444
- missing_nodes:
  - bms counter=1 and battery pre-heating demand=3
  - switch to state 126
  - switch to state 126
  - shutdown
  - shutdown
  - shutdown
  - shutdown
  - after 10s
- extra_nodes:
  - system starts up
  - what happens next?
  - bms counter reaches 1 with battery pre-heating demand of 3
  - transition to state 126
  - shut down and exit
  - shut down and exit
  - shut down and exit
  - shut down and exit
- missing_relations:
  - enter state 82 -> bms counter=1 and battery pre-heating demand=3
  - bms counter=1 and battery pre-heating demand=3 -> switch to state 126
  - switch to state 126 -> slow charging inactive
  - switch to state 126 -> slow charging inactive
  - slow charging inactive -> shutdown
  - slow charging inactive -> shutdown
  - shutdown -> slow charging is inactive
  - ac charging/discharging system fault -> after 10s
- input_excerpt:
  After the system starts up, if slow charging is active and the front MCU initialization is 0, it enters state 82. From there: - When the BMS counter reaches 1 with a battery pre-heating demand of 3, the system transitions to state 126. If slow charging becomes inactive afterward, it shuts down and exits. - If a pre-charge failure occurs, the system moves to state 126. Should slow charging be inactive at that point, it shuts down and exits. - If slow charging deactivates, the system switches to state 126 before shutting down and exiting. - For AC charging/discharging system faults, the system waits through a 10-second timeout before shifting to state 126. If slow charging is inactive followin
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging is active\nand front MCU initialization is 0?) then (yes)   :Enter state 82;   switch (What happens next?)     case (BMS counter reaches 1\nwith battery pre-heating demand of 3)       :Transition to state 126;       if (Slow charging becomes inactive?) then (yes)         :Shut down and exit;         stop       else (no)       endif     case (Pre-charge failure occurs)       :Move to state 126;       if (Slow charging is inactive?) then (yes)         :Shut down and exit;         stop       else (no)       endif     case (Slow charging deactivates)       :Switch to state 126;       :Shut down and exit;       stop     case (AC charging/discha
### pure-0023
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.5455
- relation_f1: 0.3000
- missing_nodes:
  - receive through track-to-train transmission
  - movement authority
  - all other necessary information
  - trainborne equipment active?
  - remain in full supervision
  - remain in full supervision
  - remain in full supervision
- extra_nodes:
  - receive movement authority and all other necessary information through track-to-train transmission
  - condition to exit full supervision
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
  @startuml start :Receive movement authority and all other necessary information through track-to-train transmission; :Transfer to Full Supervision automatically; switch (Condition to exit Full Supervision) case (Trainborne equipment is not active any longer) :Exit Full Supervision; case (Shunting is selected) :Exit Full Supervision; case (Partial Supervision information is received) :Exit Full Supervision; endswitch @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
