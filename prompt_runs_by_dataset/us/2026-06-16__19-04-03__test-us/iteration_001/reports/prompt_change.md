# Iteration 001 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 364
- chars_after: 1541
- chars_candidate: 1541

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,12 +12,19 @@
 
 ## workflow
 
-(None)
+1) Identify and list only the explicitly stated activities/actions from the requirement.
+2) Determine the sequential or conditional control flow between these extracted activities.
+3) Map the control flow to PlantUML structures (e.g., if/else for conditionals, fork/end fork for parallelism).
+4) Assemble the components into the final PlantUML code. Emphasize that activities must be strictly grounded in the input text to avoid hallucinating extra nodes.
 
 ## knowledge
 
-(None)
+1) PlantUML activity diagram syntax basics: start/end nodes using 'start' and 'stop', action states, transitions using '->', conditional branches using 'if/elseif/else/endif', and parallel activities using 'fork/end fork'.
+2) UML modeling guidance: decision nodes represent mutually exclusive or guarded paths, and merge/join nodes synchronize flows.
 
 ## rule
 
-(None)
+1) Every diagram must include exactly one 'start' and at least one 'stop' node.
+2) Output PlantUML code only, with no markdown formatting, explanations, or comments.
+3) Do not invent activities or transitions that are not explicitly stated or logically necessary in the requirement.
+4) Ensure all conditional blocks are properly closed with 'endif' and all parallel blocks with 'end fork'.
```
