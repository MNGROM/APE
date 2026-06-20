# Iteration 002 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 364
- chars_after: 1634
- chars_candidate: 1634

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,12 +12,19 @@
 
 ## workflow
 
-(None)
+1. Extract explicit activities strictly as stated in the requirement, preserving granular steps without compressing multiple actions into one node.
+2. Identify control-flow patterns (concurrency, loops, conditional dependencies) and their specific linguistic markers in the text.
+3. Construct the control-flow relations among the extracted activities based on the identified patterns.
+4. Map the resulting structure to PlantUML syntax.
 
 ## knowledge
 
-(None)
+- Concurrency: Map natural-language parallel markers (e.g., 'concurrently', 'in parallel', 'simultaneously') to PlantUML `fork`/`end fork` constructs.
+- Loops: Map time-based delays, periodic triggers, and retries to PlantUML `repeat`/`while` loop syntax.
+- Branching vs. Looping: Conditional branching (`if`/`elseif`/`else`) is for mutually exclusive paths; iterative looping (`while`/`repeat`) is for repeated execution.
 
 ## rule
 
-(None)
+1. Prohibit inventing unsupported intermediate states, UI feedback, or confirmation nodes not explicitly stated in the requirement.
+2. Prohibit compressing explicitly listed actions into a single broad activity.
+3. Require that conditional and parallel branches are properly nested and terminated correctly, explicitly forbidding premature or fragmented stop/end nodes within branches unless directly specified by the requirement.
```
