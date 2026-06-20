# Iteration 004 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 2185
- chars_after: 3243
- chars_candidate: 3243

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,13 +12,13 @@
 
 ## workflow
 
-Step 1: Extract explicit activities strictly from the requirement text, explicitly including data sources, system outputs, and displayed information as distinct activity nodes. Identify and preserve structural elements such as swimlanes or partitions mentioned in the requirement.
-Step 2: Construct control-flow relations exclusively among the extracted activities, mapping textual lists and conditions to the appropriate PlantUML constructs. Analyze nested 'if-then' or state-dependent logic and map it using nested PlantUML control structures rather than flattening them into sequential or independent branches.
+Step 1: Extract explicit activities strictly from the requirement text, explicitly including data sources, system outputs, and displayed information as distinct activity nodes. Explicitly extract and preserve all stated conditions (e.g., 'X available?'), constraints (e.g., 'Cannot do Y'), and specific actions as distinct activity nodes, preventing their collapse into abstract nodes. Identify and preserve structural elements such as swimlanes or partitions mentioned in the requirement.
+Step 2: Construct control-flow relations exclusively among the extracted activities, mapping textual lists and conditions to the appropriate PlantUML constructs. Analyze nested 'if-then' or state-dependent logic and map it using nested PlantUML control structures rather than flattening them into sequential or independent branches. Identify retry or re-entry logic (e.g., 're-enter', 'try again', 're-select') and map it to backward loop edges (using PlantUML `repeat` or `while`) rather than defaulting to linear forward flows.
 
 ## knowledge
 
-(1) Treat data sources, displayed information, and system outputs as distinct activity nodes when explicitly mentioned. (2) Map iterative keywords (e.g., 'repeat', 'for each', 'perform first X then Y') to PlantUML `repeat`/`while` loops. (3) Map mutually exclusive options, alternative choices, and attribute groupings to `switch`/`case` or `if`/`elseif`/`else` constructs. (4) Use `fork`/`join` for lists of attributes, options, or grouped items that represent independent properties or simultaneous display states, and for actions explicitly stated to occur concurrently or simultaneously; however, do NOT use `fork`/`join` for mutually exclusive alternative choices, sequential UI steps, or sequential actions.
+(1) Treat data sources, displayed information, and system outputs as distinct activity nodes when explicitly mentioned. (2) Map iterative keywords (e.g., 'repeat', 'for each', 'perform first X then Y') to PlantUML `repeat`/`while` loops. (3) Map mutually exclusive options, alternative choices, and attribute groupings to `switch`/`case` or `if`/`elseif`/`else` constructs. (4) Use `fork`/`join` ONLY when the requirement text explicitly uses concurrency cues (e.g., 'simultaneously', 'at the same time', 'concurrently', 'in parallel'). Do NOT use `fork`/`join` for comma-separated lists, attribute enumerations, or UI field displays, as they represent sequential entry or independent properties, not concurrent execution; also do NOT use `fork`/`join` for mutually exclusive alternative choices or sequential UI steps.
 
 ## rule
 
-(1) Do not use `fork`/`join` for mutually exclusive alternative choices or sequential UI steps. (2) Do not invent implicit error-handling branches, validation loops, or recovery paths unless they are explicitly described in the requirement. (3) Do not compress multiple explicitly stated actions into a single abstract node. (4) Do not decompose high-level goals into assumed sub-steps (e.g., inferring 'select file', 'play audio' from 'identify whales') unless those sub-steps are explicitly stated in the text.
+(1) Do not use `fork`/`join` for mutually exclusive alternative choices, sequential UI steps, comma-separated lists, attribute enumerations, or UI field displays. (2) Do not invent implicit error-handling branches, validation loops, or recovery paths unless they are explicitly described in the requirement. (3) Do not compress multiple explicitly stated actions into a single abstract node. (4) Do not decompose high-level goals into assumed sub-steps (e.g., inferring 'select file', 'play audio' from 'identify whales') unless those sub-steps are explicitly stated in the text. (5) Do not convert user roles, personas, or purely descriptive text into activity nodes. (6) Distinguish mutually exclusive alternative paths from conditional branches: if the requirement presents a choice among distinct options (e.g., selecting OK, Help, or Cancel; choosing among alternative methods), map it using `switch`/`case`; if the requirement presents a condition that evaluates to true/false (e.g., 'if available, do X, else do Y'), map it using `if`/`elseif`/`else`.
```
