# Metrics Overview

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| iteration_001:analysis_current | 1.0000 | 1.0000 | 0.4004 | 0.3323 | 0.4067 | 0.3943 | 0.3414 | 0.3236 | 0.0000 |
| iteration_001:gate_baseline | 0.9000 | 0.9000 | 0.4653 | 0.3484 | 0.4769 | 0.4542 | 0.3421 | 0.3550 | 0.0000 |
| iteration_001:gate_candidate | 1.0000 | 1.0000 | 0.4762 | 0.3818 | 0.5475 | 0.4213 | 0.4600 | 0.3263 | 0.0000 |
| iteration_002:analysis_current | 0.8000 | 0.8000 | 0.4252 | 0.3028 | 0.4485 | 0.4041 | 0.3307 | 0.2793 | 0.0000 |
| iteration_002:gate_baseline | 1.0000 | 1.0000 | 0.3528 | 0.2388 | 0.3752 | 0.3330 | 0.2518 | 0.2271 | 0.0000 |
| iteration_002:gate_candidate | 0.9000 | 0.9000 | 0.3530 | 0.2863 | 0.3699 | 0.3375 | 0.3007 | 0.2732 | 0.0000 |
| iteration_003:analysis_current | 1.0000 | 1.0000 | 0.4795 | 0.2356 | 0.5200 | 0.4449 | 0.2633 | 0.2131 | 0.0000 |
| iteration_003:gate_baseline | 0.9000 | 0.9000 | 0.4592 | 0.3254 | 0.4861 | 0.4352 | 0.3345 | 0.3168 | 0.0000 |
| iteration_003:gate_candidate | 0.9000 | 0.9000 | 0.4367 | 0.3404 | 0.4671 | 0.4100 | 0.3650 | 0.3190 | 0.0000 |

## Acceptance Decisions

| iteration | accepted | acceptance_mode | rejection_reasons |
| --- | --- | --- | --- |
| iteration_001 | True | standard | none |
| iteration_002 | False | rejected | standard_safety_gate, bootstrap_gate |
| iteration_003 | False | rejected | standard_safety_gate, bootstrap_gate |
