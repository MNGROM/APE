# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2909
- node_recall: 0.3321
- node_f1: 0.3102
- relation_precision: 0.2321
- relation_recall: 0.2652
- relation_f1: 0.2476
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.6597
- llm_node_recall: 0.7782
- llm_node_f1: 0.6697
- llm_relation_precision: 0.4686
- llm_relation_recall: 0.5080
- llm_relation_f1: 0.4407

## Failure Types
- extra_activity: 20
- extra_or_wrong_relation: 20
- missing_activity: 19
- missing_or_wrong_relation: 19
- wrong_parallel: 5
- wrong_loop: 1

## Representative Failure Cases
### us-0080
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4000
- llm_relation_f1: 0.1429
- missing_nodes:
  - add campers
  - keep track of each individual camper
- extra_nodes:
  - camp administrator selects add camper
  - enter camper details (name age contact info etc.)
  - submit camper information
  - validate camper details
  - valid details?
  - save camper to database
  - display success message
  - display validation error message
- missing_relations:
  - add campers -> keep track of each individual camper
- input_excerpt:
  As a camp administrator, I want to be able to add campers, so that I can keep track of each individual camper.
- generated_excerpt:
  @startuml start :Camp Administrator selects "Add Camper"; :Enter camper details (name, age, contact info, etc.); :Submit camper information; :Validate camper details; if (Valid details?) then (Yes)   :Save camper to database;   :Display success message; else (No)   :Display validation error message;   :Prompt to correct details; endif stop @enduml
### us-0169
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2105
- llm_relation_f1: 0.0000
- missing_nodes:
  - changes for bulk updating enum value
- extra_nodes:
  - user initiates bulk enum update request
  - receive request with target enum field old value and new value
  - validate request parameters
  - valid parameters?
  - return error response invalid input
  - query database for records matching the old enum value
  - matching records found?
  - return success response no records to update
- input_excerpt:
  As a user, I want backend changes for bulk updating one enum value to another.
- generated_excerpt:
  @startuml start :User initiates bulk enum update request; :Receive request with target enum field, old value, and new value; :Validate request parameters; if (Valid parameters?) then (No)   :Return error response: Invalid input;   stop else (Yes) endif :Query database for records matching the old enum value; if (Matching records found?) then (No)   :Return success response: No records to update;   stop else (Yes) endif :Perform bulk update in database\n(Set enum field to new value); if (Database update successful?) then (No)   :Rollback transaction;   :Return error response: Update failed;   stop else (Yes) endif :Commit transaction; :Return success response with count of updated records; st
### pure-0006
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3333
- llm_relation_f1: 0.1429
- missing_nodes:
  - train real-time grid operators annually
  - system restoration
  - black start use
  - simulator available?
  - conduct simulations
  - system shutdowns
  - system restoration
- extra_nodes:
  - train real-time grid operators annually on system restoration and black start use
  - conduct simulations of system shutdowns and restoration when a simulator becomes available
- missing_relations:
  - train real-time grid operators annually -> system restoration [fork]
  - train real-time grid operators annually -> black start use [fork]
  - system restoration -> simulator available?
  - black start use -> simulator available?
  - simulator available? -> conduct simulations [yes]
  - conduct simulations -> system shutdowns [fork]
  - conduct simulations -> system restoration [fork]
- input_excerpt:
  [Training Steps]Step 1: Train Real-time Grid Operators annually on system restoration and Black Start use.Step 2: Conduct simulations of system shutdowns and restoration when a simulator becomes available.
- generated_excerpt:
  @startuml start :Train Real-time Grid Operators annually on system restoration and Black Start use; :Conduct simulations of system shutdowns and restoration when a simulator becomes available; stop @enduml
### bp-0023
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0800
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5250
- llm_relation_f1: 0.2549
- missing_nodes:
  - log in lifecycle manager tool
  - selection method
  - go to promotion jobs home page
  - select the job want to promote
  - right-click
  - open source and destination systems drop-down lists
  - select source and destination systems
  - have logged into both source and destination systems
- extra_nodes:
  - promote a joblog into the lifecycle manager tool
  - in the promotion jobs home page select the job to promote (alternatively right-click the home page screen and click promote)
  - select source and destination systems from drop-down lists
  - schedule job?
  - click schedule job to schedule the job promotion
- missing_relations:
  - log in lifecycle manager tool -> selection method
  - selection method -> go to promotion jobs home page [case 1]
  - go to promotion jobs home page -> select the job want to promote
  - selection method -> right-click [case 2]
  - right-click -> click promote
  - select the job want to promote -> open source and destination systems drop-down lists
  - click promote -> open source and destination systems drop-down lists
  - open source and destination systems drop-down lists -> select source and destination systems
- input_excerpt:
  23.	promote a jobLog into the LifeCycle Manager tool.2. In the "Promotion Jobs" home page, select the job that you want to promote. You can also right-click the home page screen, and click Promote.3. From the source and the destination systems drop-down lists, select the source and destination systems.Note:Ensure that you have logged into both the source and destination systems before you proceed with the promotion process.4. In the External Change Management ID field, enter the appropriate value, and click Save.5. Click Mappings. Click Edit Mappings if you want to create and validate mappings.6. Click Security Settings, if required. The following options are displayed:• Do not Promote Secur
- generated_excerpt:
  @startuml start :Promote a jobLog into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, select the job to promote\n(Alternatively, right-click the home page screen and click Promote); :Select source and destination systems from drop-down lists; note right: Ensure that you have logged into\nboth source and destination systems\nbefore proceeding. :Enter appropriate value in External Change Management ID field; :Click Save; :Click Mappings; :Click Edit Mappings to create and validate mappings; :Click Security Settings (if required); if (Security Settings?) then (Do not Promote Security)   :Default option selected; elseif (Promote Security?) then (Promote Security)   :Promote jobs
### pure-0023
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1176
- relation_f1: 0.1176
- llm_element_status: success
- llm_node_f1: 0.5882
- llm_relation_f1: 0.0909
- missing_nodes:
  - receive through track-to-train transmission
  - movement authority
  - all other necessary information
  - trainborne equipment active?
  - remain in full supervision
  - exit full supervision
  - shunting is selected?
  - remain in full supervision
- extra_nodes:
  - receive movement authority and all other necessary information through track-to-train transmission
  - trainborne equipment remains in full supervision
  - trainborne equipment is active? shunting is not selected? partial supervision is not received?
- missing_relations:
  - receive through track-to-train transmission -> movement authority [fork]
  - receive through track-to-train transmission -> all other necessary information [fork]
  - movement authority -> transfer to full supervision automatically
  - all other necessary information -> transfer to full supervision automatically
  - trainborne equipment active? -> remain in full supervision [yes]
  - trainborne equipment active? -> exit full supervision [no]
  - remain in full supervision -> shunting is selected?
  - shunting is selected? -> remain in full supervision [no]
- input_excerpt:
  Transferring to Full Supervision shall occur automatically when a movement authority and all other necessary information is received through track-to-train transmission. The trainborne equipment shall remain in Full Supervision until the trainborne equipment is not active any longer, when Shunting is selected, or when Partial Supervision information is received.
- generated_excerpt:
  @startuml start :Receive movement authority and all other necessary information through track-to-train transmission; :Transfer automatically to Full Supervision; repeat   :Trainborne equipment remains in Full Supervision; repeat while (Trainborne equipment is active?\nShunting is NOT selected?\nPartial Supervision is NOT received?) is (Yes) ->No; stop @enduml
### rac-0008
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1277
- relation_f1: 0.0392
- llm_element_status: success
- llm_node_f1: 0.1887
- llm_relation_f1: 0.1754
- missing_nodes:
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - switch to state 127
  - slow charging is inactive and front mcu collateral shutdown request flag is 1
  - switch to state 128
  - shutdown
  - issue 2.2s timeout warning
  - switch to state 128
  - enter shutdown state
- extra_nodes:
  - system starts up
  - high-voltage shutdown request flag == 2?
  - switch to state 115
  - flag drops to 0 with cp duty cycle at 85 ?
  - switch to state 126
  - bms self-check counter == 1?
  - switch to state 130
  - slow charging becomes inactive?
- missing_relations:
  - enter power-up mode -> high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0
  - high-voltage shutdown request charging/discharging is 2 and bms self-check counter is 0 -> switch to state 127 [if yes]
  - switch to state 127 -> slow charging is inactive and front mcu collateral shutdown request flag is 1
  - slow charging is inactive and front mcu collateral shutdown request flag is 1 -> switch to state 128 [if yes]
  - switch to state 128 -> shutdown
  - slow charging is inactive and front mcu collateral shutdown request flag is 1 -> slow charging is inactive [else if]
  - slow charging is inactive -> issue 2.2s timeout warning [if yes]
  - issue 2.2s timeout warning -> switch to state 128
- input_excerpt:
  After the system starts up, if slow charging is active, we enter power-up mode. Then:  1) When the high-voltage shutdown request (charging/discharging) flag is 2, switch to state 115. After switching:    a. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If the BMS self-check counter shows 1, switch to state 130. If slow charging becomes inactive, shut down and end.    b. If the flag drops to 0 with CP duty cycle at 85%, switch to state 126. If battery pre-heating is required, switch to state 130. If slow charging becomes inactive, shut down and end.    c. If the flag drops to 0 while the BMS self-check counter is 1, switch to state 126. If CP duty cycle hits 85% with 
- generated_excerpt:
  @startuml start :System starts up; if (Slow charging active?) then (Yes)   :Enter power-up mode;   partition "1) High-voltage shutdown request flag == 2" {     if (High-voltage shutdown request flag == 2?) then (Yes)       :Switch to state 115;       partition "1a" {         if (Flag drops to 0 with CP duty cycle at 85%?) then (Yes)           :Switch to state 126;         elseif (BMS self-check counter == 1?) then (Yes)           :Switch to state 130;         elseif (Slow charging becomes inactive?) then (Yes)           :Shut down;           stop         endif       }       partition "1b" {         if (Flag drops to 0 with CP duty cycle at 85%?) then (Yes)           :Switch to state 126;    
### lmc-0033
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1905
- relation_f1: 0.2000
- llm_element_status: success
- llm_node_f1: 0.6087
- llm_relation_f1: 0.4000
- missing_nodes:
  - in nlguidance
  - output consistent aim point with static target
  - transient is required to maintain counter clockwise loiter?
  - change with t sample period > (quantity + velocity) * t?
  - erratic changes in aim point command
- extra_nodes:
  - nlguidance receives static target
  - generate aim point command
  - calculate tolerance tolerance = (target velocity + vehicle velocity) * t_sample
  - calculate actual change delta_magnitude = output(t) - output(t-1)
  - delta_magnitude > tolerance?
  - transient behavior is appreciable (erratic changes detected)
  - fail requirement
  - transient behavior is not appreciable
- missing_relations:
  - output consistent aim point with static target -> transient is required to maintain counter clockwise loiter?
  - transient is required to maintain counter clockwise loiter? -> change with t sample period > (quantity + velocity) * t? [no]
  - change with t sample period > (quantity + velocity) * t? -> erratic changes in aim point command [yes]
  - aim point switching -> output consistent aim point with static target
  - change with t sample period > (quantity + velocity) * t? -> output consistent aim point with static target [no]
- input_excerpt:
  6.	NLGuidance shall output consistent aim point with a static target without appreciable transient behavior in the command generation other than aim point switching where a transient is required to maintain a counter clockwise loiter (ref requirement 3).  Appreciable transient behavior is defined as erratic changes in the aim point command, beyond the following specific tolerance: a.	The change in the magnitude of the output over one frame of execution with T sample period shall not exceed the quantity of the combined velocity of the target plus the velocity of the vehicle multiplied by T.
- generated_excerpt:
  @startuml start  :NLGuidance receives static target;  :Generate aim point command;  if (Is aim point switching occurring?) then (No)   :Output consistent aim point;      :Calculate tolerance:\nTolerance = (Target Velocity + Vehicle Velocity) * T_sample;      :Calculate actual change:\nDelta_Magnitude = |Output(t) - Output(t-1)|;      if (Delta_Magnitude > Tolerance?) then (Yes)     :Transient behavior is appreciable\n(erratic changes detected);     :Fail requirement;     stop   else (No)     :Transient behavior is NOT appreciable;     :Pass requirement;   endif    else (Yes, Aim point switching)   :Allow transient behavior\n(to maintain counter-clockwise loiter\nper requirement 3);      :Out
### lmc-0052
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7143
- llm_relation_f1: 0.8571
- missing_nodes:
  - rotation matrix dcm321
  - not invertible
  - invertible
- extra_nodes:
  - input theta value
  - dcm321 is not invertible
  - raise exception or handle singular case
  - dcm321 is invertible
  - compute inverse of dcm321
- missing_relations:
  - rotation matrix dcm321 -> theta = +/- pi/2 radians?
  - theta = +/- pi/2 radians? -> not invertible [yes]
  - theta = +/- pi/2 radians? -> invertible [no]
- input_excerpt:
  4.	The Rotation Matrix, DCM321, shall be invertible with the exception of the case where theta = +/- pi/2 radians.
- generated_excerpt:
  @startuml start :Input theta value; if (theta == +pi/2 OR theta == -pi/2?) then (yes)   :DCM321 is NOT invertible;   :Raise exception or handle singular case; else (no)   :DCM321 is invertible;   :Compute inverse of DCM321; endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
