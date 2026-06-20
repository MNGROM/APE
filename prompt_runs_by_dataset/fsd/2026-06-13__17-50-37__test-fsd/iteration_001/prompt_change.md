# Iteration 001 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 341
- chars_after: 1463
- chars_candidate: 1463

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -4,7 +4,7 @@
 
 ## input
 
-The input is a single textual software requirement or scenario description. 
+The input is a single textual software requirement or scenario description.
 
 ## output
 
@@ -12,6 +12,12 @@
 
 ## workflow
 
+1. Extract activities strictly from the explicit text of the requirement. Identify each distinct action as a single concise activity, preserving the core action and object without merging sequential distinct actions.
+2. Identify control-flow constructs in the requirement: alternative paths (if/else), mutually exclusive cases based on a variable (switch/case), and concurrent actions (fork).
+3. Generate the PlantUML code by assembling only the extracted activities and identified control-flow constructs, strictly following the sequence and logic described in the requirement.
+
 ## knowledge
 
+An activity should represent a single distinct action stated in the requirement; do not decompose a stated action into sub-steps or merge sequential distinct actions into one. Use PlantUML `switch`/`case`/`endswitch` when the requirement describes multiple mutually exclusive paths based on different values of a single variable or category; use `if`/`else` for simple binary conditions. Use `fork`/`fork again`/`end fork` when the requirement indicates that multiple actions happen concurrently or represent independent parallel components.
+
 ## rule
```
