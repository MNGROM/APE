# Metrics Overview

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| iteration_001:analysis_current | 1.0000 | 1.0000 | 0.5100 | 0.4307 | 0.4722 | 0.5543 | 0.4165 | 0.4459 | 0.0000 |
| iteration_001:gate_baseline | 1.0000 | 1.0000 | 0.4602 | 0.3696 | 0.4343 | 0.4894 | 0.3623 | 0.3772 | 0.0000 |
| iteration_001:gate_candidate | 1.0000 | 1.0000 | 0.3996 | 0.4117 | 0.4784 | 0.3430 | 0.5111 | 0.3447 | 0.0000 |
| iteration_002:analysis_current | 0.7500 | 0.7500 | 0.3070 | 0.3943 | 0.3661 | 0.2644 | 0.5295 | 0.3141 | 0.0000 |
| iteration_002:gate_baseline | 0.7500 | 0.7500 | 0.3958 | 0.5198 | 0.4132 | 0.3798 | 0.6172 | 0.4489 | 0.0000 |
| iteration_002:gate_candidate | 1.0000 | 1.0000 | 0.5415 | 0.5391 | 0.5643 | 0.5204 | 0.6145 | 0.4801 | 0.0000 |
| iteration_003:analysis_current | 1.0000 | 1.0000 | 0.4913 | 0.5022 | 0.5234 | 0.4629 | 0.5833 | 0.4409 | 0.0000 |
| iteration_003:gate_baseline | 1.0000 | 1.0000 | 0.4946 | 0.3399 | 0.5300 | 0.4636 | 0.3593 | 0.3224 | 0.0000 |
| iteration_003:gate_candidate | 1.0000 | 1.0000 | 0.5354 | 0.4387 | 0.6226 | 0.4696 | 0.5138 | 0.3827 | 0.0000 |
| held_out_test | 1.0000 | 1.0000 | 0.2671 | 0.0907 | 0.1658 | 0.6875 | 0.0530 | 0.3125 | 0.0000 |

## Acceptance Decisions

| iteration | accepted | acceptance_mode | rejection_reasons |
| --- | --- | --- | --- |
| iteration_001 | False | rejected | standard_safety_gate, bootstrap_gate |
| iteration_002 | True | standard | none |
| iteration_003 | True | standard | none |
