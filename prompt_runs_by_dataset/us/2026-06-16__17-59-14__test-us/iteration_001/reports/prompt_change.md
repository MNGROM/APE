# Iteration 001 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, bootstrap_gate
- chars_before: 364
- chars_after: 364
- chars_candidate: 2017

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,12 +12,18 @@
 
 ## workflow
 
-(None)
+1. Identify and extract explicitly stated high-level activities, system states, and architectural components from the requirement as distinct activity nodes.
+2. Identify control flow constructs (concurrency, temporal/periodic behavior, conditional logic) directly from the text.
+3. Construct the diagram by connecting the extracted high-level nodes using the identified control flows, strictly prohibiting the invention of intermediate calculation, verification, or procedural steps not explicitly stated in the requirement.
 
 ## knowledge
 
-(None)
+1. Concurrency: Map explicit concurrent keywords (e.g., 'concurrently', 'simultaneously', 'separate task') to PlantUML 'fork'/'end fork' constructs, ensuring sibling branches contain only parallel logic.
+2. Temporal/Periodic behavior: Map explicit temporal requirements (e.g., 'waits', 'timeout', 'periodic', 'repeated') to PlantUML 'repeat' or 'while' loops, explicitly distinguishing them from standard if/else conditional branches.
+3. Conditional logic: Map requirement conditions directly to diagram guards/conditions (e.g., if/elseif/else) without inventing intermediate procedural steps to evaluate the condition.
 
 ## rule
 
-(None)
+1. Do not invent intermediate activities (e.g., 'Check condition', 'Verify state', 'Calculate value') that are not explicitly stated in the requirement; represent conditions declaratively as guard labels on transitions.
+2. Preserve all explicitly stated high-level activities and system components as distinct nodes; do not subsume them into fine-grained procedural steps.
+3. Only generate activities and transitions that are directly supported by the requirement text; if a behavior is not explicitly described, do not add it.
```
