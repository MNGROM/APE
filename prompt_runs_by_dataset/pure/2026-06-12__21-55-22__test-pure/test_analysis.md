# Prompt Evaluation Analysis

## Summary
- count: 100
- syntax_pass_rate: 0.9700
- infrastructure_error_rate: 0.0000
- node_precision: 0.3221
- node_recall: 0.2837
- node_f1: 0.2796
- relation_precision: 0.1002
- relation_recall: 0.0893
- relation_f1: 0.0919
- plantuml_compilation_pass_rate: 0.9700
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- missing_or_wrong_relation: 99
- extra_or_wrong_relation: 99
- extra_activity: 97
- missing_activity: 96
- wrong_loop: 5
- syntax_error: 3

## Representative Failure Cases
### pure-0031
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation, wrong_loop
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
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
  - apply time domain process
  - chain output available
  - chain to another process? (including replica of self or fourier transform
  - final processed output
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
  @startuml skinparam style strictuml  start  :Select Time Domain Process(es);  repeat   :Apply Time Domain Process;      :Chain Output Available;      repeat while (Chain to another process?\n(Including replica of self\nor Fourier Transform)) is (Yes)   ->No;    until (All selected processes applied?) is (Yes) ->No;  :Final Processed Output;  stop @enduml
### pure-0022
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.4667
- relation_f1: 0.0714
- missing_nodes:
  - by driver?
  - driver selects
  - by track-to-train transmission information
  - specified acknowledgement?
  - acknowledge transfer in 5s
- extra_nodes:
  - selection source
  - driver
  - driver selects partial supervision
  - track-to-train transmission
  - receive selection from track-to-train transmission
  - acknowledgement is specified?
  - driver acknowledges transfer from full supervision to partial supervision
  - acknowledged within 5 seconds?
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
  @startuml start :Select Partial Supervision; switch (Selection source) case (Driver)   :Driver selects Partial Supervision; case (Track-to-train transmission)   :Receive selection from track-to-train transmission; endswitch  if (Acknowledgement is specified?) then (Yes)   :Driver acknowledges transfer from Full Supervision to Partial Supervision;   if (Acknowledged within 5 seconds?) then (Yes)     :Enter Partial Supervision;   else (No)     :Handle acknowledgement timeout;     stop   endif else (No)   :Enter Partial Supervision; endif  repeat   :Operate in Partial Supervision; repeat while (Exit condition met?) is (Yes) ->No;  stop  state "Exit Conditions" as exit_conditions {   :Trainborne
### pure-0051
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.5333
- relation_f1: 0.3077
- missing_nodes:
  - display inventory departments
  - see view inventory
  - display item history screen
  - current inventory item information
  - historical inventory item information
- extra_nodes:
  - the screen displays all inventory departments in matrix format
  - the system displays the item history screen containing current and historical information about the inventory item
- missing_relations:
  - access main inventory screen -> display inventory departments
  - display inventory departments -> see view inventory
  - see view inventory -> drill down to desired existing inventory item
  - click item history button -> display item history screen
  - display item history screen -> current inventory item information
  - current inventory item information -> historical inventory item information
- input_excerpt:
  4. View Inventory Item History 4.1. User accesses the main inventory screen 4.2. The screen displays all inventory departments in matrix format 4.3. User drills down to the desired existing inventory item (see View Inventory) 4.4. The item detail screen is presented 4.5. User clicks the Item History button 4.6. The system displays the Item History screen containing current and historical information about the inventory item
- generated_excerpt:
  @startuml start :User accesses the main inventory screen; :The screen displays all inventory departments in matrix format; :User drills down to the desired existing inventory item; (see View Inventory) :The item detail screen is presented; :User clicks the Item History button; :The system displays the Item History screen\ncontaining current and historical information\nabout the inventory item; stop @enduml
### pure-0001
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - conduct contingency studies
  - determine amount and location of black start generation
  - verify black start units annually
  - number
  - size
  - availability
  - location
  - document cranking paths
- extra_nodes:
  - determine the amount and location of black start generation through contingency studies
  - annually verify the number size availability and location of black start units
  - document cranking paths and provide them to wecc upon request
  - evaluate diverse fuel resources cranking paths communication unit capabilities and coordination with neighboring plans
  - coordinate the planning process with transmission owners and neighboring balancing authorities
  - annually enter into rmr and interim black start contracts with qualified generators
- missing_relations:
  - conduct contingency studies -> determine amount and location of black start generation
  - determine amount and location of black start generation -> verify black start units annually
  - verify black start units annually -> number
  - number -> size
  - size -> availability
  - availability -> location
  - location -> document cranking paths
  - document cranking paths -> provide to wecc upon request
- input_excerpt:
  [Grid Planning Steps] Step 1: The CAISO determines the amount and location of Black Start Generation through contingency studies. Step 2: The CAISO annually verifies the number, size, availability, and location of Black Start units.Step 3: The CAISO documents Cranking Paths and provides them to WECC upon request.Step 4: The CAISO evaluates diverse fuel resources, cranking paths, communication, unit capabilities, and coordination with neighboring plans.Step 5: The planning process is coordinated with transmission owners and neighboring Balancing Authorities.Step 6: The CAISO annually enters into RMR and Interim Black Start Contracts with qualified generators.
- generated_excerpt:
  @startuml start :Determine the amount and location of Black Start Generation through contingency studies; :Annually verify the number, size, availability, and location of Black Start units; :Document Cranking Paths and provide them to WECC upon request; :Evaluate diverse fuel resources, cranking paths, communication, unit capabilities, and coordination with neighboring plans; :Coordinate the planning process with transmission owners and neighboring Balancing Authorities; :Annually enter into RMR and Interim Black Start Contracts with qualified generators; stop @enduml
### pure-0006
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - train real-time grid operators annually
  - system restoration
  - system restoration
  - black start use
  - simulator available?
  - conduct simulations
  - system shutdowns
- extra_nodes:
  - train real-time grid operators annually on system restoration and black start use
  - conduct simulations of system shutdowns and restoration when a simulator becomes available
- missing_relations:
  - train real-time grid operators annually -> system restoration
  - system restoration -> black start use
  - black start use -> simulator available?
  - simulator available? -> conduct simulations
  - conduct simulations -> system shutdowns
  - system shutdowns -> system restoration
- input_excerpt:
  [Training Steps]Step 1: Train Real-time Grid Operators annually on system restoration and Black Start use.Step 2: Conduct simulations of system shutdowns and restoration when a simulator becomes available.
- generated_excerpt:
  @startuml start :Train Real-time Grid Operators annually on system restoration and Black Start use; :Conduct simulations of system shutdowns and restoration when a simulator becomes available; stop @enduml
### pure-0007
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - give buy instruction
  - save buy instruction
  - match instructions with same stock id
  - make a trade by matching
  - modify information of matched instructions
- extra_nodes:
  - transaction user interface give the buy instruction
  - central trading system save the buy instruction
  - central trading system match the instructions with the same stock id
  - central trading system make a trade by matching
  - central trading system modify the information of matched instructions
- missing_relations:
  - give buy instruction -> save buy instruction
  - save buy instruction -> match instructions with same stock id
  - match instructions with same stock id -> make a trade by matching
  - make a trade by matching -> modify information of matched instructions
- input_excerpt:
  1. transaction user interface: give the buy instruction 2. central trading system: save the buy instruction 3. central trading system: match the instructions with the same stock id 4. central trading system: make a trade by matching 5. central trading system: modify the information of matched instructions
- generated_excerpt:
  @startuml start :Transaction User Interface: Give the buy instruction; :Central Trading System: Save the buy instruction; :Central Trading System: Match the instructions with the same stock id; :Central Trading System: Make a trade by matching; :Central Trading System: Modify the information of matched instructions; stop @enduml
### pure-0008
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - give sell instruction
  - save sell instruction
  - match instructions with same stock id
  - make a trade by matching
  - modify information of matched instructions
- extra_nodes:
  - transaction user interface give the sell instruction
  - central trading system save the sell instruction
  - central trading system match the instructions with the same stock id
  - central trading system make a trade by matching
  - central trading system modify the information of matched instructions
- missing_relations:
  - give sell instruction -> save sell instruction
  - save sell instruction -> match instructions with same stock id
  - match instructions with same stock id -> make a trade by matching
  - make a trade by matching -> modify information of matched instructions
- input_excerpt:
  1. transaction user interface: give the sell instruction 2. central trading system: save the sell instruction 3. central trading system: match the instructions with the same stock id 4. central trading system: make a trade by matching 5. central trading system: modify the information of matched instructions
- generated_excerpt:
  @startuml start :Transaction User Interface: Give the sell instruction; :Central Trading System: Save the sell instruction; :Central Trading System: Match the instructions with the same stock id; :Central Trading System: Make a trade by matching; :Central Trading System: Modify the information of matched instructions; stop @enduml
### pure-0009
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - give cancel instruction
  - save cancel instruction
  - cancel correlative instruction
- extra_nodes:
  - transaction user interface give the cancel instruction
  - central trading system save the cancel instruction
  - central trading system cancel the correlative instruction
- missing_relations:
  - give cancel instruction -> save cancel instruction
  - save cancel instruction -> cancel correlative instruction
- input_excerpt:
  1. transaction user interface: give the cancel instruction 2. central trading system: save the cancel instruction 3. central trading system: cancel the correlative instruction
- generated_excerpt:
  @startuml start :transaction user interface: give the cancel instruction; :central trading system: save the cancel instruction; :central trading system: cancel the correlative instruction; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
