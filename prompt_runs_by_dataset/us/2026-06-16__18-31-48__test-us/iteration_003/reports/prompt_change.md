# Iteration 003 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate
- chars_before: 1634
- chars_after: 1634
- chars_candidate: 2816

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,19 +12,25 @@
 
 ## workflow
 
-1. Extract explicit activities strictly as stated in the requirement, preserving granular steps without compressing multiple actions into one node.
+1. Extract all explicit activities and structural markers (including implicit parallelism markers) strictly as stated in the requirement, preserving granular steps without compressing multiple actions into one node.
 2. Identify control-flow patterns (concurrency, loops, conditional dependencies) and their specific linguistic markers in the text.
 3. Construct the control-flow relations among the extracted activities based on the identified patterns.
 4. Map the resulting structure to PlantUML syntax.
+5. Cross-check the generated diagram against the extracted activity list to ensure no leaf-level activities are dropped and no simple statements are over-fragmented.
 
 ## knowledge
 
-- Concurrency: Map natural-language parallel markers (e.g., 'concurrently', 'in parallel', 'simultaneously') to PlantUML `fork`/`end fork` constructs.
-- Loops: Map time-based delays, periodic triggers, and retries to PlantUML `repeat`/`while` loop syntax.
+- Concurrency: Map natural-language parallel markers (e.g., 'concurrently', 'in parallel', 'simultaneously', 'separate task', 'periodically', 'in the background') to PlantUML `fork`/`end fork` constructs.
+- Loops: Map 'repeat until' to PlantUML `repeat`/`repeat while` for action-then-condition loops. Map 'while [condition]' or duration/timeout constraints to PlantUML `while`/`end while` for condition-then-action loops.
+- Nested Loop Scoping: When a loop is nested within a conditional branch, the loop must close within its parent conditional branch.
 - Branching vs. Looping: Conditional branching (`if`/`elseif`/`else`) is for mutually exclusive paths; iterative looping (`while`/`repeat`) is for repeated execution.
+- Granularity: A single, simple requirement statement should map to exactly one activity node, prohibiting over-fragmentation.
 
 ## rule
 
 1. Prohibit inventing unsupported intermediate states, UI feedback, or confirmation nodes not explicitly stated in the requirement.
 2. Prohibit compressing explicitly listed actions into a single broad activity.
 3. Require that conditional and parallel branches are properly nested and terminated correctly, explicitly forbidding premature or fragmented stop/end nodes within branches unless directly specified by the requirement.
+4. Prohibit over-decomposing a single, simple requirement statement into multiple unnecessary activity nodes.
+5. Prohibit artificial loop-back flows; loop-back transitions must strictly correspond to explicit iterative markers in the text and must return to the correct scope without crossing conditional boundaries not specified in the requirement.
+6. Require that transitions between activities strictly follow the extracted control-flow relations, prohibiting spurious transitions added to simplify complex structures.
```
