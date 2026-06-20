# Iteration 008 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 5099
- chars_after: 6209
- chars_candidate: 6209

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -14,12 +14,13 @@
 
 1. Identify all actions, decisions, and constraints from the text.
 2. Abstract and summarize verbose UI text, descriptions, and notes into concise, action-oriented behavioral steps; explicitly exclude static text, descriptive clauses, and non-behavioral notes from being mapped to activity nodes.
-3. Scan for cyclic, periodic, or repetitive keywords (e.g., 'repeat', 'until', 'periodically', 'cyclically') and map them to `repeat`/`while` structures.
-4. Scan for linguistic cues of parallelism and alternative conditions; explicitly distinguish mutually exclusive alternative conditions (mapped to `switch`/`case` or `if`/`elseif`/`else`) from true concurrent tasks (identified by positive cues like 'concurrently', 'simultaneously', 'at the same time', or comma-separated lists of simultaneous tasks, and mapped to `fork`/`end fork`) before constructing the control flow.
-5. Enforce a 1-to-1 mapping of explicitly stated actions, UI interactions, and system responses to individual activity nodes, prohibiting summarization or merging of distinct steps.
-6. Classify each condition as either a high-level constraint (mapped directly to a single decision branch) or a procedural step (requiring intermediate actions).
-7. Determine the exact nesting hierarchy of control structures before writing code.
-8. Generate PlantUML code strictly following the mapped hierarchy without adding or flattening levels.
+3. Enforce a 1-to-1 mapping of explicitly stated actions, UI interactions, and system responses to individual activity nodes, prohibiting summarization or merging of distinct steps.
+4. Extract and map parallel and iterative behaviors: Before constructing the main sequential or conditional control flow, identify and map parallel behaviors (to `fork`/`end fork`) and iterative behaviors (to `repeat`/`while`) as a distinct, mandatory phase. Explicitly list out concurrent actions and iterative actions with their linguistic cues as intermediate output before diagramming.
+5. Scan for cyclic, periodic, or repetitive keywords (e.g., 'repeat', 'until', 'periodically', 'cyclically') and map them to `repeat`/`while` structures.
+6. Scan for linguistic cues of parallelism and alternative conditions; explicitly distinguish mutually exclusive alternative conditions (mapped to `switch`/`case` or `if`/`elseif`/`else`) from true concurrent tasks (identified by positive cues like 'concurrently', 'simultaneously', 'at the same time', or comma-separated lists of simultaneous tasks, and mapped to `fork`/`end fork`) before constructing the control flow.
+7. Classify each condition as either a high-level constraint (mapped directly to a single decision branch) or a procedural step (requiring intermediate actions).
+8. Determine the exact nesting hierarchy of control structures before writing code.
+9. Generate PlantUML code strictly following the mapped hierarchy without adding or flattening levels.
 
 ## knowledge
 
@@ -32,6 +33,8 @@
 7. Multi-branch mutually exclusive conditions (e.g., evaluating a variable against multiple distinct values) should be modeled using `switch`/`case`, not `fork`.
 8. Secondary checks, fallback conditions, and specific timeout/counter values must be explicitly preserved as separate activity nodes or conditional branches to prevent missing activities.
 9. Background constraints, prerequisites, and role requirements (e.g., 'must be performed by an expert') must be modeled as executable decision nodes (conditional guards) in the flow, not treated as static annotations or ignored.
+10. Lists of independent attributes, UI fields, or simultaneous system responses must be preserved as separate, fine-grained activity nodes and not compressed into a single node.
+11. Bounded retries (e.g., 'retry up to N times') and persistent cycles (e.g., 'continuously', 'keeps doing') must be mapped into PlantUML `repeat`/`while` loops with appropriate exit conditions based strictly on the text.
 
 ## rule
 
@@ -47,3 +50,5 @@
 10. NEVER use verbatim UI text, descriptive clauses, or static notes as activity node labels; they MUST be abstracted into behavioral actions.
 11. NEVER represent explicitly concurrent tasks as sequential steps.
 12. NEVER misrepresent loop exit conditions (e.g., incorrect exit criteria or missing exit conditions).
+13. NEVER invent placeholder loop conditions or control logic not explicitly stated in the text (e.g., do not add 'retry' loops if only a simple check is requested).
+14. NEVER flatten nested conditional logic; if/else or switch/case structures identified as nested in the text MUST remain nested in the PlantUML code.
```
