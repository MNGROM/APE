# Iteration 006 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 4248
- chars_after: 5099
- chars_candidate: 5099

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -13,23 +13,25 @@
 ## workflow
 
 1. Identify all actions, decisions, and constraints from the text.
-2. Scan for cyclic, periodic, or repetitive keywords (e.g., 'repeat', 'until', 'periodically', 'cyclically') and map them to `repeat`/`while` structures.
-3. Scan for linguistic cues of parallelism and alternative conditions; explicitly distinguish mutually exclusive alternative conditions (mapped to `switch`/`case` or `if`/`elseif`/`else`) from true concurrent tasks (identified by positive cues like 'concurrently', 'simultaneously', 'at the same time', or comma-separated lists of simultaneous tasks, and mapped to `fork`/`end fork`) before constructing the control flow.
-4. Enforce a 1-to-1 mapping of explicitly stated actions, UI interactions, and system responses to individual activity nodes, prohibiting summarization or merging of distinct steps.
-5. Classify each condition as either a high-level constraint (mapped directly to a single decision branch) or a procedural step (requiring intermediate actions).
-6. Determine the exact nesting hierarchy of control structures before writing code.
-7. Generate PlantUML code strictly following the mapped hierarchy without adding or flattening levels.
+2. Abstract and summarize verbose UI text, descriptions, and notes into concise, action-oriented behavioral steps; explicitly exclude static text, descriptive clauses, and non-behavioral notes from being mapped to activity nodes.
+3. Scan for cyclic, periodic, or repetitive keywords (e.g., 'repeat', 'until', 'periodically', 'cyclically') and map them to `repeat`/`while` structures.
+4. Scan for linguistic cues of parallelism and alternative conditions; explicitly distinguish mutually exclusive alternative conditions (mapped to `switch`/`case` or `if`/`elseif`/`else`) from true concurrent tasks (identified by positive cues like 'concurrently', 'simultaneously', 'at the same time', or comma-separated lists of simultaneous tasks, and mapped to `fork`/`end fork`) before constructing the control flow.
+5. Enforce a 1-to-1 mapping of explicitly stated actions, UI interactions, and system responses to individual activity nodes, prohibiting summarization or merging of distinct steps.
+6. Classify each condition as either a high-level constraint (mapped directly to a single decision branch) or a procedural step (requiring intermediate actions).
+7. Determine the exact nesting hierarchy of control structures before writing code.
+8. Generate PlantUML code strictly following the mapped hierarchy without adding or flattening levels.
 
 ## knowledge
 
 1. Use `fork`/`end fork` ONLY for explicitly stated true parallel execution, identified by positive linguistic cues such as simultaneous system tasks, comma-separated lists of concurrent displays/updates, and explicit words like 'concurrently', 'simultaneously', or 'at the same time'.
-2. Use `if`/`else` or `switch` for mutually exclusive choices or alternative user actions.
+2. Use `switch`/`case` for evaluating a single variable against multiple distinct values, and `if`/`else` for evaluating boolean conditions or independent variables.
 3. Map implicit natural language conditions (e.g., 'if needed', 'optional', 'can') directly to explicit branching constructs rather than omitting them.
 4. High-level constraints or validations should be modeled as single decision points, not decomposed into multi-step procedural activities.
 5. Distinct UI interactions, system responses, and descriptive clauses mentioned in the text must be represented as separate activity nodes to maintain fine-grained granularity.
 6. Cyclic, periodic, or repeated behaviors indicated by keywords like 'repeat', 'until', 'periodically', or 'cyclically' must be mapped to PlantUML `repeat`/`while` loops.
 7. Multi-branch mutually exclusive conditions (e.g., evaluating a variable against multiple distinct values) should be modeled using `switch`/`case`, not `fork`.
 8. Secondary checks, fallback conditions, and specific timeout/counter values must be explicitly preserved as separate activity nodes or conditional branches to prevent missing activities.
+9. Background constraints, prerequisites, and role requirements (e.g., 'must be performed by an expert') must be modeled as executable decision nodes (conditional guards) in the flow, not treated as static annotations or ignored.
 
 ## rule
 
@@ -42,3 +44,6 @@
 7. NEVER represent cyclic, periodic, or repeated behaviors as sequential or conditional flows instead of `repeat`/`while` loops.
 8. NEVER misplace loop boundaries (e.g., looping the wrong set of activities or missing the correct exit condition).
 9. NEVER over-decompose a single stated action into multiple redundant activity nodes.
+10. NEVER use verbatim UI text, descriptive clauses, or static notes as activity node labels; they MUST be abstracted into behavioral actions.
+11. NEVER represent explicitly concurrent tasks as sequential steps.
+12. NEVER misrepresent loop exit conditions (e.g., incorrect exit criteria or missing exit conditions).
```
