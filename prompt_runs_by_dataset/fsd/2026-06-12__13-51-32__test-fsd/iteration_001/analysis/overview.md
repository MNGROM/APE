# Prompt Evaluation Analysis

## Summary
- count: 2
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.1471
- node_recall: 0.3125
- node_f1: 0.2000
- relation_precision: 0.1250
- relation_recall: 0.2857
- relation_f1: 0.1739
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 2.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.4500
- llm_node_recall: 0.9500
- llm_node_f1: 0.5907
- llm_relation_precision: 0.2459
- llm_relation_recall: 0.8182
- llm_relation_f1: 0.3667

## Failure Types
- missing_activity: 2
- extra_activity: 2
- missing_or_wrong_relation: 2
- extra_or_wrong_relation: 2

## Representative Failure Cases
### us-0065
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
  - get summary on major findings from the event
- extra_nodes:
  - open workshop app
  - navigate to event summary section
  - select specific workshop event
  - request major findings summary
  - findings available?
  - load summary data
  - display major findings to attendee
  - display no findings available message
- input_excerpt:
  As a workshop attendee, I want to see a summary on major findings from the event.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Open Workshop App;  :Navigate to Event Summary Section;  :Select Specific Workshop Event;  :Request Major Findings Summary;  if (Findings Available?) then (Yes)   :Load Summary Data;   :Display Major Findings to Attendee; else (No)   :Display "No Findings Available" Message; endif  stop  @enduml
### pure-0020
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.4000
- relation_f1: 0.3478
- llm_element_status: success
- llm_node_f1: 0.7200
- llm_relation_f1: 0.4000
- missing_nodes:
  - exist multiple channels?
  - use ppt for voice transmission
  - give audible/visual indication
- extra_nodes:
  - use normal mode
  - multiple channels exist?
  - use push-to-talk (ptt) for voice transmission
  - use push-to-talk (ptt) for voice transmission
  - device is portable?
  - device is portable?
  - provide battery warnings
  - wait for services
- missing_relations:
  - normal services unavailable -> switch to direct mode
  - use ppt for voice transmission -> provide portables battery warnings
  - normal services resume? -> give audible/visual indication
- input_excerpt:
  User switches to Direct Mode only when normal services are unavailable. Manual channel selection (if multiple channels exist). Push-To-Talk (PTT) is used for voice transmission. Battery warnings are provided for portables. Audible/visual indication is given when normal services resume.
- generated_excerpt:
  @startuml start if (Normal services available?) then (Yes)   :Use Normal Mode; else (No)   :Switch to Direct Mode;   if (Multiple channels exist?) then (Yes)     :Manual channel selection;   else (No)   endif   :Use Push-To-Talk (PTT)\nfor voice transmission;   if (Device is portable?) then (Yes)     :Provide battery warnings;   else (No)   endif   :Wait for services;   if (Normal services resumed?) then (No)     :Continue Direct Mode;     repeat       :Use Push-To-Talk (PTT)\nfor voice transmission;       if (Device is portable?) then (Yes)         :Provide battery warnings;       else (No)       endif     repeat while (Normal services resumed?) is (No)   else (Yes)     :Provide audible/vis

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
