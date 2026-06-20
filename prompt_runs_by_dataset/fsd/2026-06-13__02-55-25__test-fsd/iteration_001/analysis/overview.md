# Prompt Evaluation Analysis

## Summary
- count: 20
- syntax_pass_rate: 0.9500
- infrastructure_error_rate: 0.0000
- node_precision: 0.1880
- node_recall: 0.1799
- node_f1: 0.1756
- relation_precision: 0.1118
- relation_recall: 0.1098
- relation_f1: 0.1094
- plantuml_compilation_pass_rate: 0.9500
- llm_element_evaluated: 0.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

## Failure Types
- extra_activity: 20
- missing_or_wrong_relation: 20
- extra_or_wrong_relation: 20
- missing_activity: 19
- wrong_loop: 1
- syntax_error: 1

## Representative Failure Cases
### pure-0012
- dataset: pure
- failure_types: syntax_error, missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: False
- syntax_errors: ERROR
- plantuml_compiles: False
- plantuml_compile_errors: ERROR | Some diagram description contains errors
- node_f1: 0.3556
- relation_f1: 0.1860
- missing_nodes:
  - initiate call to controller
  - primary controller
  - secondary controller
  - power supply controller
  - unique identity?
  - use external systems to obtain
  - obtain appropriate destination
  - functional identity be displayed
- extra_nodes:
  - radio system provides unique identity?
  - functional identity of connected party available?
  - display functional identity to driver
  - identity contains alphanumeric description?
  - display alphanumeric description to driver
  - called party busy?
  - indicate called party is busy
  - network could not connect?
- missing_relations:
  - initiate call to controller -> primary controller
  - primary controller -> secondary controller
  - secondary controller -> power supply controller
  - power supply controller -> unique identity?
  - unique identity? -> use external systems to obtain
  - use external systems to obtain -> obtain appropriate destination
  - obtain appropriate destination -> attempt to establish call to destination
  - attempt to establish call to destination -> functional identity be displayed
- input_excerpt:
  5.2.2.1 It shall be possible for the driver to initiate a call to any of the following types of controller with a minimum of driver action being required (eg a single keystroke): (M) primary controller; secondary controller; power supply controller. 5.2.2.2 If the radio system cannot give a unique identity for a given type of controller, the identity could be obtained using external systems as defined in 11.4.7. (I) 5.2.2.3 Once an appropriate destination has been obtained, the radio shall attempt to establish a call to this destination. The functional identity shall be displayed to the controller. (M) 5.2.2.3i The functional identity includes the following: − the train number, if available;
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Driver initiates call (single keystroke) to Primary, Secondary, or Power Supply Controller;  if (Radio system provides unique identity?) then (No)   :Obtain identity using external systems   (as defined in 11.4.7); else (Yes) endif  :Determine functional identity to display to controller:   if (Train number available?) then (Yes)     :Use Train Number;   elseif (Engine number available?) then (Yes)     :Use Engine Number;   else (No)     :Use Coach Number of leading cab;   endif;  :Attempt to establish call to destination;  :Provide audible and visual indication that call is proceeding;  if (Call connected?) then (Yes)   :Provide audible and visua
### lmc-0055
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - dcm321 * dcm321t
  - =identity (3x3
  - allowed
  - not allowed
- extra_nodes:
  - initialize rotation matrix dcm321
  - compute transpose of rotation matrix dcm321t
  - multiply dcm321 by dcm321t
  - result == identity (3x3
  - validation passed
  - validation failed
- missing_relations:
  - dcm321 * dcm321t -> =identity (3x3
  - =identity (3x3 -> allowed
  - allowed -> not allowed
- input_excerpt:
  7.	The Rotation Matrix, DCM321, multiplied by the transpose of the Rotation Matrix, DCM321T shall be the Identity (3x3) Matrix.v
- generated_excerpt:
  @startuml start :Initialize Rotation Matrix DCM321; :Compute Transpose of Rotation Matrix DCM321T; :Multiply DCM321 by DCM321T; if (Result == Identity (3x3) Matrix?) then (Yes)   :Validation Passed; else (No)   :Validation Failed; endif stop @enduml
### pure-0078
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - selects period within displayed period
  - operation
  - expand
  - selected period becomes new viewing period
  - contract
  - new viewing period becomes twice
  - encloses selected period
- extra_nodes:
  - expanding?
- missing_relations:
  - selects period within displayed period -> operation
  - operation -> expand
  - expand -> selected period becomes new viewing period
  - selected period becomes new viewing period -> contract
  - contract -> new viewing period becomes twice
  - new viewing period becomes twice -> encloses selected period
- input_excerpt:
  1. The user selects a period of time within the displayed viewing period over which to expand or contract in time. 2. The tool expands or contracts the selected period. If expanding, the selected period becomes the new viewing period. If contracting, the new viewing period becomes twice as long as the selected period and encloses it.
- generated_excerpt:
  @startuml start :The user selects a period of time within the displayed viewing period; if (Expanding?) then (Yes)   :The selected period becomes   the new viewing period; else (No - Contracting)   :The new viewing period becomes   twice as long as the selected period   and encloses it; endif stop @enduml
### us-0098
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - edit profile
  - upload new information
- extra_nodes:
  - owner selects edit profile
  - system displays current profile information
  - owner modifies profile fields
  - owner clicks save
  - system validates input
  - valid input?
  - system updates profile
  - system displays success message
- missing_relations:
  - edit profile -> upload new information
- input_excerpt:
  As an Owner, I want to edit my profile, so that that it is updated with new information.
- generated_excerpt:
  @startuml skinparam style strictuml  start :Owner selects "Edit Profile"; :System displays current profile information; :Owner modifies profile fields; :Owner clicks "Save"; :System validates input; if (Valid input?) then (yes)   :System updates profile;   :System displays success message; else (no)   :System displays error message;   :Owner corrects input;   stop endif stop @enduml
### lmc-0048
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - requirement when heading hold mode becomes active
  - pilot uses cockpit control
  - set heading hold reference
- extra_nodes:
  - heading hold mode becomes the active mode
  - pilot sets heading hold reference via cockpit control
- missing_relations:
  - requirement when heading hold mode becomes active -> pilot uses cockpit control
  - pilot uses cockpit control -> set heading hold reference
- input_excerpt:
  Requirement	When heading hold mode becomes the active mode the heading hold reference shall be set by the pilot via a cockpit control.
- generated_excerpt:
  @startuml start :Heading hold mode becomes the active mode; :Pilot sets heading hold reference via cockpit control; stop @enduml
### us-0092
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - get full details of data package schema changes
  - adjust scripts to handle
- extra_nodes:
  - consumer requests schema change details
  - system retrieves data package schema history
  - system identifies recent schema changes
  - compare previous schema version with current schema version
  - generate detailed change report (added/removed/modified fields)
  - display full schema change details to consumer
  - consumer reviews changes
  - consumer adjusts scripts to handle schema changes
- missing_relations:
  - get full details of data package schema changes -> adjust scripts to handle
- input_excerpt:
  As a Consumer, I want to know full details of how the data package schema has changed, so that that I can adjust my scripts to handle it.
- generated_excerpt:
  @startuml skinparam style strictuml  title Activity: View Data Package Schema Change Details  start  :Consumer requests schema change details;  :System retrieves data package schema history;  :System identifies recent schema changes;  :Compare previous schema version with current schema version;  :Generate detailed change report (added/removed/modified fields);  :Display full schema change details to Consumer;  :Consumer reviews changes;  :Consumer adjusts scripts to handle schema changes;  stop  @enduml
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
  - calculate matrix m = b(inv(wp ))b
  - check determinant of m
  - det(m
  - set ridge_on = false
  - invert matrix m to get m_inv
  - compute check output matrix = m * m_inv
  - compare check output matrix to 3x3 identity matrix
  - each element within 1e-12 tolerance?
- missing_relations:
  - ridge_on set to false -> determinant of b(inv(wp )b > 1e-12
  - determinant of b(inv(wp )b > 1e-12 -> each element with respect to 3x3 identity matrix elements < 1e-12 tolerance
  - each element with respect to 3x3 identity matrix elements < 1e-12 tolerance -> b(inv(wp )b matrix inversion be accurate to 12 digits precision
- input_excerpt:
  2.	When the determinant of B(inv(Wp’)B’ is > 1e-12 as indicated by ridge_on set to False, the inversion of the B(inv(Wp’)B’ matrix should be accurate to 12 digits precision in that each element in the check output matrix is within a 1e-12 tolerance with respect to the elements of a 3x3 identity matrix.
- generated_excerpt:
  @startuml start :Calculate matrix M = B(inv(Wp'))B'; :Check determinant of M; if (det(M) > 1e-12?) then (Yes)   :Set ridge_on = False;   :Invert matrix M to get M_inv;   :Compute check output matrix = M * M_inv;   :Compare check output matrix to 3x3 identity matrix;   if (Each element within 1e-12 tolerance?) then (Yes)     :Inversion accurate to 12 digits precision;   else (No)     :Inversion precision check failed;   endif else (No)   :Set ridge_on = True;   :Handle ill-conditioned matrix; endif stop @enduml
### us-0019
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - issue a notice of violation
  - provide formal communication
- extra_nodes:
  - enforcement staff logs into the system
  - search for the case or responsible party
  - case/party found?
  - select the case record
  - create a new case record
  - initiate issue notice of violation
  - select responsible party details
  - attach supporting evidence/documents
- missing_relations:
  - issue a notice of violation -> provide formal communication
- input_excerpt:
  As an Enforcement Staff member, I want to Issue a Notice of Violation, so that I can provide formal communication to the responsible party.
- generated_excerpt:
  @startuml skinparam style strictuml skinparam ActivityBackgroundColor #E8F5E9 skinparam ActivityBorderColor #2E7D32 skinparam NoteBorderColor #FFA726 skinparam NoteBackgroundColor #FFF3E0  title Issue a Notice of Violation  start  :Enforcement Staff logs into the system;  :Search for the case or responsible party;  if (Case/Party found?) then (Yes)   :Select the case record; else (No)   :Create a new case record; endif  :Initiate "Issue Notice of Violation";  :Enter violation details (Description, Code, Date, Location);  :Select responsible party details;  :Attach supporting evidence/documents;  :Generate Notice of Violation document;  :Review notice details;  if (Notice accurate and complet

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints, hard rules, or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
