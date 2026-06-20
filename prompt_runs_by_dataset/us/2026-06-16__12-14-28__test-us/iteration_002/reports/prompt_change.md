# Iteration 002 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, bootstrap_gate
- chars_before: 1774
- chars_after: 1774
- chars_candidate: 2907

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -13,17 +13,21 @@
 ## workflow
 
 1) Extract activities: Identify explicit actions and states directly stated in the requirement without inventing implementation details.
-2) Identify control flow: Analyze the extracted activities to determine their relationships, specifically looking for decision points (mutually exclusive paths), concurrent tasks, and iterative behaviors.
-3) Map to PlantUML: Construct the diagram by mapping the identified activities and control-flow relationships directly to the appropriate PlantUML syntax (if/else, fork/join, repeat/while).
+2) Assess activity granularity: Group closely related clauses into single composite actions and avoid splitting single logical actions into multiple nodes.
+3) Identify control flow: Analyze the extracted activities to determine their relationships, specifically looking for decision points (mutually exclusive paths), concurrent tasks, and iterative behaviors.
+4) Map to PlantUML: Construct the diagram by mapping the identified activities and control-flow relationships directly to the appropriate PlantUML syntax (if/else, fork/join, repeat/while, switch/case).
+5) Structural validation: Verify that all PlantUML blocks (if/endif, fork/end fork, repeat/endrepeat, switch/endswitch) are properly nested and closed to prevent syntax errors.
 
 ## knowledge
 
 1) Conditional branching: Map mutually exclusive choices, alternative paths, or yes/no questions to if/elseif/else structures.
-2) Concurrency: Only use fork/join when the requirement explicitly indicates simultaneous or independent execution (e.g., 'simultaneously', 'concurrently', 'in parallel'); otherwise, default to sequential flow.
-3) Loops: Map phrases like 'retry', 'repeat', or 'periodic' to repeat/while constructs, ensuring the exit condition accurately reflects the requirement's termination clause rather than the entry condition.
+2) Switch/case constructs: Map multi-case decision points with mutually exclusive alternatives (e.g., selecting from a list of distinct options) to switch/case/endswitch constructs rather than if/elseif.
+3) Concurrency: Use fork/fork again/end fork when the requirement explicitly indicates simultaneous or independent execution (e.g., 'simultaneously', 'concurrently', 'in parallel') or implies parallelism through implicit linguistic cues such as 'displayed lists', 'multiple options presented', or 'simultaneous actions'; otherwise, default to sequential flow.
+4) Loops: Map phrases describing a continuous iterative process to repeat/while constructs, ensuring the exit condition accurately reflects the requirement's termination clause rather than the entry condition.
 
 ## rule
 
-1) Do not invent, decompose, or infer implementation steps (e.g., 'Initialize', 'Compute', 'Evaluate') that are not explicitly stated in the requirement text.
+1) Do not invent, decompose, or infer implementation steps (e.g., 'Initialize', 'Compute', 'Evaluate') that are not explicitly stated in the requirement text, except you may infer parallelism when the requirement implies simultaneous display or execution.
 2) Every activity node in the diagram must correspond directly to an action or state described in the input.
 3) Do not convert high-level constraints or mathematical rules into procedural steps.
+4) Distinguish loops from conditional branches: if an action simply returns to a previous step upon failure or as an alternative (e.g., 'retry', 're-enter'), model it as a conditional branch (if/else) leading back to the prior action, rather than a repeat/while loop, unless the requirement describes a continuous iterative process.
```
