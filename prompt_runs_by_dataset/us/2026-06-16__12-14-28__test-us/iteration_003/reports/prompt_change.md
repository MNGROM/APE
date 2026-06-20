# Iteration 003 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, bootstrap_gate
- chars_before: 1774
- chars_after: 1774
- chars_candidate: 2957

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -13,17 +13,19 @@
 ## workflow
 
 1) Extract activities: Identify explicit actions and states directly stated in the requirement without inventing implementation details.
-2) Identify control flow: Analyze the extracted activities to determine their relationships, specifically looking for decision points (mutually exclusive paths), concurrent tasks, and iterative behaviors.
-3) Map to PlantUML: Construct the diagram by mapping the identified activities and control-flow relationships directly to the appropriate PlantUML syntax (if/else, fork/join, repeat/while).
+2) Identify control flow: Analyze the extracted activities to determine their relationships, specifically looking for decision points, concurrent tasks, and iterative behaviors. (a) Look for structural cues of concurrency, such as lists of items or operations that logically execute simultaneously, and map them to parallel branches. (b) Differentiate complex multi-branch mutually exclusive logic (e.g., monitoring multiple distinct states) from simple binary if/else choices.
+3) Map to PlantUML: Construct the diagram by mapping the identified activities and control-flow relationships directly to the appropriate PlantUML syntax (if/else, switch/case/endswitch, fork/join, repeat/while).
 
 ## knowledge
 
-1) Conditional branching: Map mutually exclusive choices, alternative paths, or yes/no questions to if/elseif/else structures.
-2) Concurrency: Only use fork/join when the requirement explicitly indicates simultaneous or independent execution (e.g., 'simultaneously', 'concurrently', 'in parallel'); otherwise, default to sequential flow.
-3) Loops: Map phrases like 'retry', 'repeat', or 'periodic' to repeat/while constructs, ensuring the exit condition accurately reflects the requirement's termination clause rather than the entry condition.
+1) Conditional branching: Map mutually exclusive choices, alternative paths, or yes/no questions to if/elseif/else structures. Multi-branch mutually exclusive conditions (e.g., monitoring multiple distinct states or switch/case logic) should use PlantUML `switch`/`case`/`endswitch` constructs instead of nested if/else.
+2) Concurrency: Only use fork/join when the requirement explicitly indicates simultaneous or independent execution (e.g., 'simultaneously', 'concurrently', 'in parallel') or when structural cues indicate operations that logically execute simultaneously; otherwise, default to sequential flow.
+3) Loops: Map phrases like 'retry', 'repeat', or 'periodic' to repeat/while constructs, ensuring the exit condition accurately reflects the requirement's termination clause rather than the entry condition. Continuous monitoring or cyclic control system behaviors should be modeled using `repeat`/`while` loops, distinguishing the overarching cyclic behavior from the internal conditional logic of the states.
+4) Contextual states: Contextual system states and operational conditions (e.g., 'In [System Name]') must be treated as essential activity nodes, not descriptive fluff.
 
 ## rule
 
 1) Do not invent, decompose, or infer implementation steps (e.g., 'Initialize', 'Compute', 'Evaluate') that are not explicitly stated in the requirement text.
 2) Every activity node in the diagram must correspond directly to an action or state described in the input.
-3) Do not convert high-level constraints or mathematical rules into procedural steps.
+3) Do not convert constraints, limits, or mathematical rules into sequential procedural actions; they should only be represented as conditional guards on existing control flows.
+4) Preserve all explicitly mentioned contextual system states, operational conditions, and system names as distinct activity nodes in the diagram.
```
