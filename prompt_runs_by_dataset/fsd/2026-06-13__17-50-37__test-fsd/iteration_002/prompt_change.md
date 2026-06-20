# Iteration 002 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate
- chars_before: 1463
- chars_after: 1463
- chars_candidate: 2309

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,12 +12,14 @@
 
 ## workflow
 
-1. Extract activities strictly from the explicit text of the requirement. Identify each distinct action as a single concise activity, preserving the core action and object without merging sequential distinct actions.
-2. Identify control-flow constructs in the requirement: alternative paths (if/else), mutually exclusive cases based on a variable (switch/case), and concurrent actions (fork).
-3. Generate the PlantUML code by assembling only the extracted activities and identified control-flow constructs, strictly following the sequence and logic described in the requirement.
+1. Extract activities strictly from the explicit text of the requirement. Identify each distinct action as a single concise activity, preserving the core action and object. Do not infer, assume, or decompose actions into sub-steps beyond what is explicitly written; do not merge sequential distinct actions into one.
+2. Identify control-flow constructs in the requirement: alternative paths (if/else), mutually exclusive cases based on a variable (switch/case), concurrent actions (fork), and compound conditions requiring nested logic.
+3. Generate the PlantUML code by assembling only the extracted activities and identified control-flow constructs. Ensure all control-flow edges strictly follow the sequence and logic described in the requirement, connecting only the explicitly extracted activities without adding or skipping steps.
 
 ## knowledge
 
 An activity should represent a single distinct action stated in the requirement; do not decompose a stated action into sub-steps or merge sequential distinct actions into one. Use PlantUML `switch`/`case`/`endswitch` when the requirement describes multiple mutually exclusive paths based on different values of a single variable or category; use `if`/`else` for simple binary conditions. Use `fork`/`fork again`/`end fork` when the requirement indicates that multiple actions happen concurrently or represent independent parallel components.
 
+Use PlantUML `fork`/`fork again`/`end fork` when the requirement lists multiple independent items that occur concurrently, represent independent system components, or are displayed simultaneously as separate attributes. When a requirement specifies a compound condition (e.g., 'when A and B'), model it as nested `if`/`else` blocks to reflect the distinct decision points, rather than flattening it into a single combined guard. Use PlantUML `partition` blocks to group activities performed by the same system or actor when the requirement explicitly names distinct responsible entities.
+
 ## rule
```
