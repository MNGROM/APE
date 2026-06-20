# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2304
- node_recall: 0.2085
- node_f1: 0.2189
- relation_precision: 0.2252
- relation_recall: 0.2234
- relation_f1: 0.2243
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 20.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.5689
- llm_node_recall: 0.6869
- llm_node_f1: 0.5873
- llm_relation_precision: 0.4649
- llm_relation_recall: 0.4905
- llm_relation_f1: 0.4249

## Failure Types
- missing_activity: 20
- extra_activity: 20
- extra_or_wrong_relation: 20
- missing_or_wrong_relation: 19
- wrong_parallel: 4
- wrong_loop: 1

## Representative Failure Cases
### lmc-0015
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
  - autopilot is not requesting support (not request)?
  - sensor change states from nominal to transition
- missing_relations:
  - autopilot is not requesting support (not request)? -> sensor change states from nominal to transition [yes]
- input_excerpt:
  11.	The sensor shall change states from NOMINAL to TRANSITION when the autopilot is not requesting support (not request).
- generated_excerpt:
  @startuml skinparam style strictuml  state NOMINAL state TRANSITION  NOMINAL --> TRANSITION : autopilot is not requesting support (not request) @enduml
### pure-0027
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7500
- llm_relation_f1: 1.0000
- missing_nodes:
  - get correlator-backend network interface
  - receive incoming data packets
- extra_nodes:
  - receive incoming data packets from correlator to backend network interface
- missing_relations:
  - get correlator-backend network interface -> receive incoming data packets
- input_excerpt:
  Data Receive – The BE shall receive incoming data packets from the Correlator to Backend network interface. This network is a part of the BE System.
- generated_excerpt:
  @startuml start :Receive incoming data packets from Correlator to Backend network interface; note right: Network is part of the BE System :Process received data packets; stop @enduml
### us-0132
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.5333
- llm_relation_f1: 0.1429
- missing_nodes:
  - design own app
  - stand to a few rules
- extra_nodes:
  - developer starts app design
  - access design interface
  - design app components
  - apply custom styling and layout
  - submit design for validation
  - system validates design against rules
  - design passes all rules?
  - design approved and saved
- missing_relations:
  - design own app -> stand to a few rules
- input_excerpt:
  As a developer, I want to be able to design my App on my own - though there will be a few rules I have to stand to.
- generated_excerpt:
  @startuml start :Developer starts App design; :Access design interface; repeat   :Design App components;   :Apply custom styling and layout;   :Submit design for validation;   :System validates design against rules;   -> if validation fails; repeat while (Design passes all rules?) is (No) -> Yes; :Design approved and saved; :App design completed; stop @enduml
### bp-0003
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_parallel
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.7547
- llm_relation_f1: 0.7200
- missing_nodes:
  - info provider tree is displayed
  - the info area is displayed
  - open context menu
  - choose create info cube
  - enter zd_sales as the technical name
  - enter sales overview as the description
  - select standard info cube as info provider type
  - choose create
- extra_nodes:
  - you are in the modeling functional area of the data warehousing workbench
  - choose info provider
- missing_relations:
  - info provider tree is displayed -> the info area is displayed
  - the info area is displayed -> open context menu
  - open context menu -> choose create info cube
  - choose create info cube -> enter zd_sales as the technical name [fork]
  - choose create info cube -> enter sales overview as the description [fork]
  - enter zd_sales as the technical name -> select standard info cube as info provider type
  - enter sales overview as the description -> select standard info cube as info provider type
  - select standard info cube as info provider type -> choose create
- input_excerpt:
  3.	Creating Data sources for Master Data of Characteristic "Product"1. You are in the Modeling functional area of the Data Warehousing Workbench2. Choose Info Provider. The Info Provider tree is displayed. The Info Area created previously in the Info Object tree is also displayed in the Info Provider tree. It contains the characteristics that were dened as Info Provider and is used to group further objects.3. In the context menu of the Info Area, choose Create Info Cube.4. In the next screen, enter ZD_SALES as the technical name under Info Cube and Sales Overview as the description.5. Select Standard Info Cube as Info Provider Type and choose Create. You go to the screen for Info Cube editin
- generated_excerpt:
  @startuml start :You are in the Modeling functional area\nof the Data Warehousing Workbench; :Choose Info Provider; note right: Info Provider tree is displayed :In the context menu of the Info Area,\nchoose Create Info Cube; :Enter ZD_SALES as technical name\nand Sales Overview as description; :Select Standard Info Cube\nas Info Provider Type and choose Create; note right: Go to Info Cube editing screen :Choose Create New Dimensions\nin context menu of Dimensions folder; :Enter Product as description\nand choose Create Another Dimension; :Enter Sales Organization as description\nand choose Continue; note right: Dimensions are inserted :Choose Info Object Catalog in toolbar; :Select Info Obje
### lmc-0026
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.3333
- llm_relation_f1: 0.3636
- missing_nodes:
  - in inner loop airspeed regulator
  - command transient changes in translational axial acceleration <= 32 ft/sec2/sec
- extra_nodes:
  - receive airspeed regulation command
  - calculate required translational axial acceleration
  - is calculated acceleration > 32 ft/sec /sec?
  - cap acceleration command to 32 ft/sec /sec
  - pass calculated acceleration command
  - output acceleration command to inner loop
- missing_relations:
  - in inner loop airspeed regulator -> command transient changes in translational axial acceleration <= 32 ft/sec2/sec
- input_excerpt:
  9.	The Inner Loop Airspeed Regulator Shall not command transient changes in translational axial acceleration greater than 32 ft/sec2/sec.
- generated_excerpt:
  @startuml skinparam style strictuml title Inner Loop Airspeed Regulator - Translational Axial Acceleration Limit  start  :Receive Airspeed Regulation Command;  :Calculate Required Translational Axial Acceleration;  if (Is Calculated Acceleration > 32 ft/sec²/sec?) then (Yes)   :Cap Acceleration Command to 32 ft/sec²/sec; else (No)   :Pass Calculated Acceleration Command; endif  :Output Acceleration Command to Inner Loop;  stop  @enduml
### us-0198
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4615
- llm_relation_f1: 0.3333
- missing_nodes:
  - restrict a group of files from view
- extra_nodes:
  - archivist selects a group of files
  - choose restrict from view option
  - confirm restriction action
  - restriction applied successfully?
  - update file group access permissions
  - hide files from public view
  - display success message
  - display error message
- input_excerpt:
  As an archivist, I want to restrict a group of files from view.
- generated_excerpt:
  @startuml skinparam style strictuml  title Archivist: Restrict a group of files from view  start  :Archivist selects a group of files;  :Choose "Restrict from view" option;  :Confirm restriction action;  if (Restriction applied successfully?) then (Yes)   :Update file group access permissions;   :Hide files from public view;   :Display success message; else (No)   :Display error message; endif  stop @enduml
### us-0140
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.1739
- llm_relation_f1: 0.0833
- missing_nodes:
  - get an alfred device
  - adapt for user had hearing trouble
- extra_nodes:
  - power on alfred device
  - access device settings menu
  - select accessibility option
  - select hearing adaptation mode
  - choose hearing adaptation type
  - enable visual alerts and notifications
  - adjust screen flash intensity
  - increase audio volume
- missing_relations:
  - get an alfred device -> adapt for user had hearing trouble
- input_excerpt:
  As an OlderPerson, I want to have an ALFRED device that can be easily adapted for user that have hearing trouble.
- generated_excerpt:
  @startuml skinparam style strictuml  title Activity Diagram: OlderPerson adapting ALFRED device for hearing trouble  start  :Power on ALFRED device;  :Access device settings menu;  :Select "Accessibility" option;  :Select "Hearing Adaptation" mode;  switch (Choose hearing adaptation type) case (Visual Alerts)   :Enable visual alerts and notifications;   :Adjust screen flash intensity; case (Audio Adjustments)   :Increase audio volume;   :Adjust audio frequency (tone);   :Enable audio amplification; case (Haptic Feedback)   :Enable vibration alerts;   :Adjust vibration intensity; endswitch  :Save accessibility settings;  :Test adapted settings;  if (Are the settings suitable?) then (No)   :Re
### lmc-0029
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2667
- llm_relation_f1: 0.2667
- missing_nodes:
  - in nlguidance
  - vector define location at standoff 1 with offset from target position?
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point?
  - it is inertial position vector for aim point 1
  - compute the vector
- extra_nodes:
  - compute inertial position vector for aim point 1
- missing_relations:
  - in nlguidance -> vector define location at standoff 1 with offset from target position?
  - vector define location at standoff 1 with offset from target position? -> it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? [yes]
  - it oriented on vector perpendicular to tangent relative position vector from vehicle to aim point? -> it is inertial position vector for aim point 1 [yes]
  - it is inertial position vector for aim point 1 -> compute the vector
- input_excerpt:
  2.	NLGuidance shall compute the inertial position vector for aim point 1, defining the location at Standoff 1 with an offset from the target position, and oriented on a vector perpendicular to the tangent relative position vector from the vehicle to the corresponding aim point.
- generated_excerpt:
  @startuml start :Compute inertial position vector for Aim Point 1; note right: Defines location at Standoff 1 :Calculate offset from target position; :Determine tangent relative position vector\nfrom vehicle to Aim Point 1; :Calculate vector perpendicular\nto tangent relative position vector; :Orient offset on the\nperpendicular vector; :Set final inertial position vector\nfor Aim Point 1; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
