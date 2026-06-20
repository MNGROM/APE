# Iteration 001 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: has_required_metric_benefit, bootstrap_gate
- chars_before: 341
- chars_after: 341
- chars_candidate: 932

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -4,7 +4,7 @@
 
 ## input
 
-The input is a single textual software requirement or scenario description. 
+The input is a single textual software requirement or scenario description.
 
 ## output
 
@@ -12,6 +12,12 @@
 
 ## workflow
 
+1. Extract distinct, explicitly stated activities from the requirement.
+2. Identify control flow: sequence, branches, loops, and parallelism.
+3. Generate PlantUML code mapping the activities and control flow, ensuring every branch and parallel section is properly closed.
+
 ## knowledge
 
+PlantUML control flow: use if/else/endif for decision/merge, fork/fork again/end fork for parallel execution, and while/end while for loops. An activity is a distinct, actionable step explicitly stated in the requirement; do not create activities for implicit sub-steps or compress multiple explicit actions into one.
+
 ## rule
```
