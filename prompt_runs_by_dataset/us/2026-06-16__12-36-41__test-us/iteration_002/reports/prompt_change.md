# Iteration 002 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 1775
- chars_after: 2936
- chars_candidate: 2936

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -13,16 +13,19 @@
 ## workflow
 
 1. Identify all actions, decisions, and constraints from the text.
-2. Classify each condition as either a high-level constraint (mapped directly to a single decision branch) or a procedural step (requiring intermediate actions).
-3. Determine the exact nesting hierarchy of control structures before writing code.
-4. Generate PlantUML code strictly following the mapped hierarchy without adding or flattening levels.
+2. Scan for linguistic cues of parallelism (e.g., 'concurrently', 'simultaneously', 'at the same time', comma-separated lists of simultaneous tasks) and map them to fork/end fork structures.
+3. Enforce a 1-to-1 mapping of explicitly stated actions, UI interactions, and system responses to individual activity nodes, prohibiting summarization or merging of distinct steps.
+4. Classify each condition as either a high-level constraint (mapped directly to a single decision branch) or a procedural step (requiring intermediate actions).
+5. Determine the exact nesting hierarchy of control structures before writing code.
+6. Generate PlantUML code strictly following the mapped hierarchy without adding or flattening levels.
 
 ## knowledge
 
-1. Use `fork`/`end fork` ONLY for explicitly stated true parallel execution.
+1. Use `fork`/`end fork` ONLY for explicitly stated true parallel execution, identified by positive linguistic cues such as simultaneous system tasks, comma-separated lists of concurrent displays/updates, and explicit words like 'concurrently', 'simultaneously', or 'at the same time'.
 2. Use `if`/`else` or `switch` for mutually exclusive choices or alternative user actions.
 3. Map implicit natural language conditions (e.g., 'if needed', 'optional', 'can') directly to explicit branching constructs rather than omitting them.
 4. High-level constraints or validations should be modeled as single decision points, not decomposed into multi-step procedural activities.
+5. Distinct UI interactions, system responses, and descriptive clauses mentioned in the text must be represented as separate activity nodes to maintain fine-grained granularity.
 
 ## rule
 
@@ -30,3 +33,5 @@
 2. ALWAYS preserve the exact nesting depth of control structures as identified in the text (e.g., `switch` inside `if`, `if` inside `repeat`).
 3. NEVER use `fork`/`end fork` for independent, alternative, or mutually exclusive actions.
 4. NEVER omit optional paths or contextual checks—every user choice or conditional step must be represented as a branch.
+5. NEVER introduce decision branches, loops, or error handling not explicitly stated in the text (no inferred implicit flows).
+6. Alternative flows, exception handling, and recovery steps (e.g., 'select another folder') MUST be modeled as linear paths within if/else or switch conditional branches; explicitly forbid representing them as loops or incorrectly placing them in the main sequential flow.
```
