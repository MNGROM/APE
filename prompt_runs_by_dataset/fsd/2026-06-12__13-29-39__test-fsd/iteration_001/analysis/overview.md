# Prompt Evaluation Analysis

## Summary
- count: 2
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.1818
- node_recall: 0.2500
- node_f1: 0.2105
- relation_precision: 0.1500
- relation_recall: 0.2143
- relation_f1: 0.1765
- higen_compilation_pass_rate: 1.0000
- higen_llm_evaluated: 0.0000
- higen_llm_failed: 0.0000
- llm_node_precision: 0.0000
- llm_node_recall: 0.0000
- llm_node_f1: 0.0000
- llm_relation_precision: 0.0000
- llm_relation_recall: 0.0000
- llm_relation_f1: 0.0000

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
- higen_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- missing_nodes:
  - get summary on major findings from the event
- extra_nodes:
  - open workshop app
  - select completed workshop
  - navigate to event summary section
  - request major findings summary
  - findings available?
  - display major findings summary
  - review findings
  - display no findings available message
- input_excerpt:
  As a workshop attendee, I want to see a summary on major findings from the event.
- generated_excerpt:
  @startuml skinparam style strictuml  start  :Open Workshop App;  :Select Completed Workshop;  :Navigate to Event Summary Section;  :Request Major Findings Summary;  if (Findings Available?) then (Yes)   :Display Major Findings Summary;   :Review Findings; else (No)   :Display "No Findings Available" Message; endif  stop  @enduml
### pure-0020
- dataset: pure
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- higen_compiles: True
- node_f1: 0.4211
- relation_f1: 0.3529
- missing_nodes:
  - exist multiple channels?
  - use ppt for voice transmission
  - normal services resume?
  - give audible/visual indication
- extra_nodes:
  - use normal mode
  - multiple channels exist?
  - use push-to-talk (ptt) for voice transmission
  - device is portable?
  - wait for normal services
  - provide audible/visual indication that normal services resumed
  - switch back to normal mode
- missing_relations:
  - normal services unavailable -> switch to direct mode
  - use ppt for voice transmission -> provide portables battery warnings
  - provide portables battery warnings -> normal services resume?
  - normal services resume? -> give audible/visual indication
- input_excerpt:
  User switches to Direct Mode only when normal services are unavailable. Manual channel selection (if multiple channels exist). Push-To-Talk (PTT) is used for voice transmission. Battery warnings are provided for portables. Audible/visual indication is given when normal services resume.
- generated_excerpt:
  @startuml start if (Normal services available?) then (Yes)   :Use Normal Mode; else (No)   :Switch to Direct Mode;   if (Multiple channels exist?) then (Yes)     :Manual channel selection;   else (No)   endif   :Use Push-To-Talk (PTT)\nfor voice transmission;   if (Device is portable?) then (Yes)     :Provide battery warnings;   else (No)   endif   :Wait for normal services;   :Provide audible/visual indication\nthat normal services resumed;   :Switch back to Normal Mode; endif stop @enduml

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
