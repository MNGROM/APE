# Iteration 001 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 364
- chars_after: 1553
- chars_candidate: 1553

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,12 +12,13 @@
 
 ## workflow
 
-(None)
+Step 1: Extract explicit activities strictly from the requirement text, explicitly including data sources, system outputs, and displayed information as distinct activity nodes.
+Step 2: Construct control-flow relations exclusively among the extracted activities, mapping textual lists and conditions to the appropriate PlantUML constructs.
 
 ## knowledge
 
-(None)
+(1) Treat data sources, displayed information, and system outputs as distinct activity nodes when explicitly mentioned. (2) Map iterative keywords (e.g., 'repeat', 'for each', 'perform first X then Y') to PlantUML `repeat`/`while` loops. (3) Map mutually exclusive options, alternative choices, and attribute groupings to `switch`/`case` or `if`/`elseif`/`else` constructs. (4) Reserve `fork`/`join` strictly for actions explicitly stated to occur concurrently or simultaneously.
 
 ## rule
 
-(None)
+(1) Do not use `fork`/`join` for sequential steps, alternative options, attribute listings, or UI steps; only use it when true concurrency is explicitly stated. (2) Do not invent implicit error-handling branches, validation loops, or recovery paths unless they are explicitly described in the requirement. (3) Do not compress multiple explicitly stated actions into a single abstract node.
```
