# Metrics Overview

| item | plantuml_compilation_pass_rate | syntax_pass_rate | node_f1 | relation_f1 | node_precision | node_recall | relation_precision | relation_recall | infrastructure_error_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| iteration_001:analysis_current | 1.0000 | 1.0000 | 0.1646 | 0.0914 | 0.1868 | 0.1746 | 0.0893 | 0.0953 | 0.0000 |
| iteration_001:gate_baseline | 0.9500 | 0.9500 | 0.1877 | 0.0902 | 0.2376 | 0.1773 | 0.1184 | 0.0837 | 0.0000 |
| iteration_001:gate_candidate | 0.9000 | 0.9000 | 0.3865 | 0.2307 | 0.3958 | 0.3904 | 0.2311 | 0.2316 | 0.0000 |
| iteration_002:analysis_current | 1.0000 | 1.0000 | 0.3457 | 0.1822 | 0.3496 | 0.3527 | 0.1915 | 0.1754 | 0.0000 |
| iteration_002:gate_baseline | 1.0000 | 1.0000 | 0.3299 | 0.1767 | 0.3189 | 0.3671 | 0.1725 | 0.1825 | 0.0000 |
| iteration_002:gate_candidate | 1.0000 | 1.0000 | 0.2882 | 0.1564 | 0.2855 | 0.3255 | 0.1648 | 0.1558 | 0.0000 |
| iteration_003:analysis_current | 1.0000 | 1.0000 | 0.3258 | 0.2162 | 0.3633 | 0.3052 | 0.2270 | 0.2106 | 0.0000 |
| iteration_003:gate_baseline | 0.9500 | 0.9500 | 0.2910 | 0.1442 | 0.2974 | 0.3127 | 0.1523 | 0.1388 | 0.0000 |
| iteration_003:gate_candidate | 1.0000 | 1.0000 | 0.3662 | 0.1749 | 0.3876 | 0.3694 | 0.1774 | 0.1769 | 0.0000 |
| held_out_test | 0.8966 | 0.8966 | 0.4527 | 0.2927 | 0.5366 | 0.3987 | 0.3500 | 0.2563 | 0.0000 |

## Acceptance Decisions

| iteration | accepted | acceptance_mode | rejection_reasons |
| --- | --- | --- | --- |
| iteration_001 | True | standard | none |
| iteration_002 | False | rejected | standard_safety_gate, has_required_metric_benefit, bootstrap_gate |
| iteration_003 | True | standard | none |
