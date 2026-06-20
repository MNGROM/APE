# Metrics Overview

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| iteration_001:analysis_current | 1.0000 | 1.0000 | 0.2836 | 0.3059 | 0.2735 | 0.2945 | 0.3309 | 0.2844 | 0.0000 |
| iteration_001:gate_baseline | 1.0000 | 1.0000 | 0.2542 | 0.1692 | 0.2945 | 0.2236 | 0.1812 | 0.1587 | 0.0000 |
| iteration_001:gate_candidate | 1.0000 | 1.0000 | 0.5967 | 0.3900 | 0.6543 | 0.5485 | 0.3867 | 0.3932 | 0.0000 |
| iteration_002:analysis_current | 0.9000 | 0.9000 | 0.5250 | 0.5077 | 0.5443 | 0.5070 | 0.5177 | 0.4980 | 0.0000 |
| iteration_003:analysis_current | 1.0000 | 1.0000 | 0.4134 | 0.3833 | 0.4418 | 0.3884 | 0.4218 | 0.3512 | 0.0000 |
| iteration_003:gate_baseline | 1.0000 | 1.0000 | 0.4647 | 0.3490 | 0.4799 | 0.4505 | 0.3332 | 0.3664 | 0.0000 |
| iteration_003:gate_candidate | 0.9000 | 0.9000 | 0.4443 | 0.1756 | 0.4350 | 0.4541 | 0.1793 | 0.1720 | 0.0000 |
| iteration_004:analysis_current | 1.0000 | 1.0000 | 0.5284 | 0.4651 | 0.5498 | 0.5086 | 0.5005 | 0.4343 | 0.0000 |
| iteration_005:analysis_current | 0.9000 | 0.9000 | 0.4744 | 0.3377 | 0.4811 | 0.4678 | 0.3418 | 0.3336 | 0.0000 |
| iteration_005:gate_baseline | 0.9000 | 0.9000 | 0.4005 | 0.4922 | 0.4233 | 0.3801 | 0.5446 | 0.4490 | 0.0000 |
| iteration_005:gate_candidate | 1.0000 | 1.0000 | 0.3984 | 0.4453 | 0.3895 | 0.4077 | 0.4391 | 0.4517 | 0.0000 |

## Acceptance Decisions

| iteration | accepted | acceptance_mode | rejection_reasons |
| --- | --- | --- | --- |
| iteration_001 | True | standard | none |
| iteration_003 | False | rejected | standard_safety_gate, has_required_metric_benefit, bootstrap_gate |
| iteration_005 | False | rejected | standard_safety_gate, has_required_metric_benefit, bootstrap_gate |
