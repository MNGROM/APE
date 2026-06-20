# Prompt Evaluation Analysis

## Summary
- count: 2
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.2443
- node_recall: 0.1909
- node_f1: 0.1981
- relation_precision: 0.0000
- relation_recall: 0.0000
- relation_f1: 0.0000
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 2.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.6000
- llm_node_recall: 0.6429
- llm_node_f1: 0.6177
- llm_relation_precision: 0.3984
- llm_relation_recall: 0.2858
- llm_relation_f1: 0.3222

## Failure Types
- missing_activity: 2
- extra_activity: 2
- missing_or_wrong_relation: 2
- extra_or_wrong_relation: 2

## Representative Failure Cases
### lmc-0031
- dataset: lmc
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.1538
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.2353
- llm_relation_f1: 0.1111
- missing_nodes:
  - in nlguidance
  - counter clockwise loiter for uav
  - as the picture above?
  - return tangent aim point 2
- extra_nodes:
  - select inertial position vector for aim point 1
  - does aim point 1 result in a counter-clockwise loiter?
  - select aim point 1
  - does aim point 2 result in a counter-clockwise loiter?
  - select aim point 2
  - error no valid aim point for counter-clockwise loiter
  - return selected inertial position vector
- missing_relations:
  - in nlguidance -> select inertial position vector of aim point 1 or 2
  - select inertial position vector of aim point 1 or 2 -> counter clockwise loiter for uav
  - counter clockwise loiter for uav -> as the picture above?
  - as the picture above? -> return tangent aim point 2
- input_excerpt:
  4.	NLGuidance shall always select an inertial position vector of aim point #1 or #2 which shall result in a counter clockwise loiter for the UAV.  For example, the picture above with vehicle position, UAV, would return Tangent Aim Point #2.
- generated_excerpt:
  @startuml start :Select inertial position vector for Aim Point #1; :Select inertial position vector for Aim Point #2; if (Does Aim Point #1 result in a counter-clockwise loiter?) then (Yes)   :Select Aim Point #1; else (No)   if (Does Aim Point #2 result in a counter-clockwise loiter?) then (Yes)     :Select Aim Point #2;   else (No)     :Error: No valid aim point for counter-clockwise loiter;     stop   endif endif :Return selected inertial position vector; stop @enduml
### bp-0019
- dataset: bp
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.2424
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 1.0000
- llm_relation_f1: 0.5333
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
  - enter the name description and keywords for the job
  - browse and select the folder to save the job in
  - select the source system and the destination system from the drop-down lists
  - system name displayed in drop-down list?
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
  @startuml start :Log into the LifeCycle Manager tool; :In the "Promotion Jobs" home page, click New Job; :The "New Job" window appears; :Enter the name, description, and keywords for the job; :Browse and select the folder to save the job in; :Select the source system and the destination system from the drop-down lists; if (System name displayed in drop-down list?) then (No)   :Click the Login to a new CMS option;   :A new window is launched;   :Enter the system name, user name, and password; else (Yes) endif :Click Create; stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
