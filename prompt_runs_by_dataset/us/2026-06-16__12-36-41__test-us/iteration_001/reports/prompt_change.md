# Iteration 001 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 364
- chars_after: 1775
- chars_candidate: 1775

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,12 +12,21 @@
 
 ## workflow
 
-(None)
+1. Identify all actions, decisions, and constraints from the text.
+2. Classify each condition as either a high-level constraint (mapped directly to a single decision branch) or a procedural step (requiring intermediate actions).
+3. Determine the exact nesting hierarchy of control structures before writing code.
+4. Generate PlantUML code strictly following the mapped hierarchy without adding or flattening levels.
 
 ## knowledge
 
-(None)
+1. Use `fork`/`end fork` ONLY for explicitly stated true parallel execution.
+2. Use `if`/`else` or `switch` for mutually exclusive choices or alternative user actions.
+3. Map implicit natural language conditions (e.g., 'if needed', 'optional', 'can') directly to explicit branching constructs rather than omitting them.
+4. High-level constraints or validations should be modeled as single decision points, not decomposed into multi-step procedural activities.
 
 ## rule
 
-(None)
+1. Do NOT decompose simple conditional checks into intermediate processing steps (e.g., do not add 'compute' or 'receive' nodes before a validation if the requirement only specifies the validation).
+2. ALWAYS preserve the exact nesting depth of control structures as identified in the text (e.g., `switch` inside `if`, `if` inside `repeat`).
+3. NEVER use `fork`/`end fork` for independent, alternative, or mutually exclusive actions.
+4. NEVER omit optional paths or contextual checks—every user choice or conditional step must be represented as a branch.
```
