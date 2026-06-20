# Iteration 003 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 2936
- chars_after: 4248
- chars_candidate: 4248

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -13,11 +13,12 @@
 ## workflow
 
 1. Identify all actions, decisions, and constraints from the text.
-2. Scan for linguistic cues of parallelism (e.g., 'concurrently', 'simultaneously', 'at the same time', comma-separated lists of simultaneous tasks) and map them to fork/end fork structures.
-3. Enforce a 1-to-1 mapping of explicitly stated actions, UI interactions, and system responses to individual activity nodes, prohibiting summarization or merging of distinct steps.
-4. Classify each condition as either a high-level constraint (mapped directly to a single decision branch) or a procedural step (requiring intermediate actions).
-5. Determine the exact nesting hierarchy of control structures before writing code.
-6. Generate PlantUML code strictly following the mapped hierarchy without adding or flattening levels.
+2. Scan for cyclic, periodic, or repetitive keywords (e.g., 'repeat', 'until', 'periodically', 'cyclically') and map them to `repeat`/`while` structures.
+3. Scan for linguistic cues of parallelism and alternative conditions; explicitly distinguish mutually exclusive alternative conditions (mapped to `switch`/`case` or `if`/`elseif`/`else`) from true concurrent tasks (identified by positive cues like 'concurrently', 'simultaneously', 'at the same time', or comma-separated lists of simultaneous tasks, and mapped to `fork`/`end fork`) before constructing the control flow.
+4. Enforce a 1-to-1 mapping of explicitly stated actions, UI interactions, and system responses to individual activity nodes, prohibiting summarization or merging of distinct steps.
+5. Classify each condition as either a high-level constraint (mapped directly to a single decision branch) or a procedural step (requiring intermediate actions).
+6. Determine the exact nesting hierarchy of control structures before writing code.
+7. Generate PlantUML code strictly following the mapped hierarchy without adding or flattening levels.
 
 ## knowledge
 
@@ -26,6 +27,9 @@
 3. Map implicit natural language conditions (e.g., 'if needed', 'optional', 'can') directly to explicit branching constructs rather than omitting them.
 4. High-level constraints or validations should be modeled as single decision points, not decomposed into multi-step procedural activities.
 5. Distinct UI interactions, system responses, and descriptive clauses mentioned in the text must be represented as separate activity nodes to maintain fine-grained granularity.
+6. Cyclic, periodic, or repeated behaviors indicated by keywords like 'repeat', 'until', 'periodically', or 'cyclically' must be mapped to PlantUML `repeat`/`while` loops.
+7. Multi-branch mutually exclusive conditions (e.g., evaluating a variable against multiple distinct values) should be modeled using `switch`/`case`, not `fork`.
+8. Secondary checks, fallback conditions, and specific timeout/counter values must be explicitly preserved as separate activity nodes or conditional branches to prevent missing activities.
 
 ## rule
 
@@ -33,5 +37,8 @@
 2. ALWAYS preserve the exact nesting depth of control structures as identified in the text (e.g., `switch` inside `if`, `if` inside `repeat`).
 3. NEVER use `fork`/`end fork` for independent, alternative, or mutually exclusive actions.
 4. NEVER omit optional paths or contextual checks—every user choice or conditional step must be represented as a branch.
-5. NEVER introduce decision branches, loops, or error handling not explicitly stated in the text (no inferred implicit flows).
+5. NEVER introduce decision branches, loops, or error handling not explicitly stated in the text (explicitly prohibit hallucinating error handling, loops, or recovery steps not stated in the text).
 6. Alternative flows, exception handling, and recovery steps (e.g., 'select another folder') MUST be modeled as linear paths within if/else or switch conditional branches; explicitly forbid representing them as loops or incorrectly placing them in the main sequential flow.
+7. NEVER represent cyclic, periodic, or repeated behaviors as sequential or conditional flows instead of `repeat`/`while` loops.
+8. NEVER misplace loop boundaries (e.g., looping the wrong set of activities or missing the correct exit condition).
+9. NEVER over-decompose a single stated action into multiple redundant activity nodes.
```
