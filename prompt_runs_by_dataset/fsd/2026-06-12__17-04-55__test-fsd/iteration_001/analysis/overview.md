# Prompt Evaluation Analysis

## Summary
- count: 2
- syntax_pass_rate: 1.0000
- infrastructure_error_rate: 0.0000
- node_precision: 0.3571
- node_recall: 0.3571
- node_f1: 0.3571
- relation_precision: 0.2500
- relation_recall: 0.2500
- relation_f1: 0.2500
- plantuml_compilation_pass_rate: 1.0000
- llm_element_evaluated: 2.0000
- llm_element_failed: 0.0000
- llm_node_precision: 0.6039
- llm_node_recall: 0.9706
- llm_node_f1: 0.6812
- llm_relation_precision: 0.4199
- llm_relation_recall: 0.8750
- llm_relation_f1: 0.5068

## Failure Types
- missing_activity: 2
- extra_activity: 2
- missing_or_wrong_relation: 2
- extra_or_wrong_relation: 2

## Representative Failure Cases
### us-0046
- dataset: us
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.0000
- relation_f1: 0.0000
- llm_element_status: success
- llm_node_f1: 0.4211
- llm_relation_f1: 0.3158
- missing_nodes:
  - embed interactive data preview
  - provide data correctness
- extra_nodes:
  - publisher selects dataset to embed
  - generate embed code snippet
  - copy embed code to clipboard
  - paste embed code into website html
  - publish website updates
  - user visits publisher website
  - embedded preview loads on site
  - is this the correct data for the user?
- missing_relations:
  - embed interactive data preview -> provide data correctness
- input_excerpt:
  As a publisher, I want to embed an interactive preview of my data on my site, so that users can be encouraged that this is the correct data for them.
- generated_excerpt:
  @startuml skinparam style strictuml  title Publisher Embeds Interactive Data Preview  start  :Publisher selects dataset to embed;  :Configure preview settings (interactive elements, display options);  :Generate embed code snippet;  :Copy embed code to clipboard;  :Paste embed code into website HTML;  :Publish website updates;  split   :User visits publisher website; split again   :Embedded preview loads on site; endsplit  :User interacts with data preview (filter, sort, explore);  if (Is this the correct data for the user?) then (Yes)   :User clicks call-to-action   (e.g., "Access Full Dataset");   :User redirected to full dataset; else (No)   :User continues browsing website; endif  stop @e
### rac-0006
- dataset: rac
- failure_types: missing_activity, extra_activity, missing_or_wrong_relation, extra_or_wrong_relation
- syntax_passed: True
- plantuml_compiles: True
- node_f1: 0.7143
- relation_f1: 0.5000
- llm_element_status: success
- llm_node_f1: 0.9412
- llm_relation_f1: 0.6977
- missing_nodes:
  - condition judgement
  - switch to state 110
  - switch to state 110
  - switch to state 28
  - switch to state 28
  - pet mode request handling is finished
- extra_nodes:
  - system startup
  - enter state 110
  - enter state 110
  - go to state 28
  - move to state 28
  - pet mode request handled
- missing_relations:
  - enter power-up mode -> condition judgement
  - condition judgement -> remote mode is enabled
  - remote mode is enabled -> switch to state 110
  - switch to state 110 -> slow charging is inactive
  - switch to state 110 -> slow charging is inactive
  - slow charging is inactive -> switch to state 28
  - switch to state 28 -> remote mode is disabled
  - switch to state 28 -> pet mode request handling is finished
- input_excerpt:
  After the system starts up: If slow charging is active, go into power-up mode. Then: 1.  If remote mode is enabled, enter state 110. Then, if slow charging becomes inactive, go to state 28. Finally, if remote mode is disabled, shut down and end. 2.  If a pet mode request comes in, switch to state 110. Then, if slow charging is inactive, move to state 28. Once the pet mode request is handled, shut down and end. 3.  If the battery SOC is 20, enter state 110. Then, if slow charging is inactive, switch to state 28. If the SOC later reaches 80 and the DCDC state is 3, shut down and end.
- generated_excerpt:
  @startuml start :System Startup; if (Slow charging active?) then (Yes)   :Enter power-up mode;   partition "Remote Mode Path" {     if (Remote mode enabled?) then (Yes)       :Enter state 110;       if (Slow charging inactive?) then (Yes)         :Go to state 28;       endif       if (Remote mode disabled?) then (Yes)         :Shut down;         end       endif     endif   }   partition "Pet Mode Path" {     if (Pet mode request received?) then (Yes)       :Switch to state 110;       if (Slow charging inactive?) then (Yes)         :Move to state 28;       endif       :Pet mode request handled;       :Shut down;       end     endif   }   partition "Battery SOC Path" {     if (Battery SOC == 2

## Prompt Improvement Guidance
- Modify only the run-local `work.md` prompt.
- Preserve the required markdown sections.
- Prefer concrete workflow constraints or reusable knowledge over broad stylistic advice.
- Target the most frequent failure types first and avoid overfitting to a single case.
