# Metrics Overview

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| iteration_001:analysis_current | 1.0000 | 1.0000 | 0.5111 | 0.3823 | 0.4869 | 0.5379 | 0.3717 | 0.3936 | 0.0000 |
| iteration_001:gate_baseline | 1.0000 | 1.0000 | 0.4110 | 0.3205 | 0.3692 | 0.4635 | 0.3005 | 0.3433 | 0.0000 |
| iteration_001:gate_candidate | 1.0000 | 1.0000 | 0.3281 | 0.3646 | 0.3951 | 0.2805 | 0.4087 | 0.3291 | 0.0000 |
| iteration_002:analysis_current | 1.0000 | 1.0000 | 0.3049 | 0.3742 | 0.3602 | 0.2644 | 0.4938 | 0.3013 | 0.0000 |
| iteration_002:gate_baseline | 1.0000 | 1.0000 | 0.4587 | 0.5158 | 0.5038 | 0.4210 | 0.6250 | 0.4391 | 0.0000 |
| iteration_002:gate_candidate | 1.0000 | 1.0000 | 0.5017 | 0.5764 | 0.5083 | 0.4952 | 0.6633 | 0.5096 | 0.0000 |
| iteration_003:analysis_current | 1.0000 | 1.0000 | 0.3607 | 0.5083 | 0.3847 | 0.3395 | 0.6001 | 0.4409 | 0.0000 |
| iteration_003:gate_baseline | 1.0000 | 1.0000 | 0.5395 | 0.4525 | 0.6375 | 0.4676 | 0.5270 | 0.3965 | 0.0000 |
| iteration_003:gate_candidate | 0.7500 | 0.7500 | 0.5267 | 0.3220 | 0.5950 | 0.4724 | 0.3595 | 0.2916 | 0.0000 |
| held_out_test | 1.0000 | 1.0000 | 0.4510 | 0.1622 | 0.3408 | 0.6667 | 0.1429 | 0.1875 | 0.0000 |

## Acceptance Decisions

| iteration | accepted | acceptance_mode | rejection_reasons |
| --- | --- | --- | --- |
| iteration_001 | False | rejected | standard_safety_gate, bootstrap_gate |
| iteration_002 | True | standard | none |
| iteration_003 | False | rejected | standard_safety_gate, has_required_metric_benefit, bootstrap_gate |
