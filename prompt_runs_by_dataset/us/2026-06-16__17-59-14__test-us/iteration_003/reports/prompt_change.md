# Iteration 003 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 1924
- chars_after: 3013
- chars_candidate: 3013

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -13,14 +13,16 @@
 ## workflow
 
 1. Extract all explicit activities and actions from the requirement without abstracting or compressing them.
-2. Identify and flag concurrent/grouped items for parallel fork decomposition.
-3. Identify and flag iterative or continuous monitoring phrases for loop construct mapping.
-4. Identify and flag conditional logic for branching construct mapping.
-5. Construct the PlantUML code strictly based on the extracted activities and identified control-flow constructs.
+2. Distinguish between unconditional triggers (e.g., 'when X happens', 'upon Y', 'after Z') and conditional guards (e.g., 'if X', 'in case of Y'); specify that only conditional guards should be mapped to if/else branching, while unconditional triggers must be modeled as sequential activities.
+3. Identify and flag concurrent/grouped items for parallel fork decomposition.
+4. Identify and flag iterative or continuous monitoring phrases for loop construct mapping.
+5. Identify and flag conditional logic for branching construct mapping.
+6. Analyze the interaction and nesting of the identified constructs, specifically placing parallel forks inside loops when concurrent actions occur within an iterative cycle.
+7. Construct the PlantUML code strictly based on the extracted activities and identified control-flow constructs.
 
 ## knowledge
 
-(1) Lists or grouped concurrent items (e.g., 'A and B', 'A, B, and C') must be decomposed into separate parallel branches using `fork`/`fork again`/`end fork`. (2) Continuous or iterative monitoring (e.g., 'while X remains stable', 'monitor until') must be modeled as loops using `while`/`end while` or `repeat`/`repeat while`, not as simple conditionals or switch statements. (3) Explicit conditional checks (e.g., 'if X', 'in case of Y') must be modeled as decision nodes using `if`/`elseif`/`else`/`endif`, preserving the requirement's logic as guard labels.
+(1) Lists or grouped concurrent items (e.g., 'A and B', 'A, B, and C') must be decomposed into separate parallel branches using `fork`/`fork again`/`end fork`. (2) Continuous or iterative monitoring (e.g., 'while X remains stable', 'monitor until') must be modeled as loops using `while`/`end while` or `repeat`/`repeat while`, not as simple conditionals or switch statements. (3) Explicit conditional checks (e.g., 'if X', 'in case of Y') must be modeled as decision nodes using `if`/`elseif`/`else`/`endif`, preserving the requirement's logic as guard labels. (4) Passive time-based delays/timeouts (e.g., 'wait for X ms', 'timeout') must be modeled using `while`/`end while`, whereas active iterative actions (e.g., 'poll', 'monitor continuously') must be modeled using `repeat`/`repeat while`. (5) When multiple concurrent actions occur within an iterative cycle, the `fork`/`end fork` construct must be nested inside the `while` or `repeat` loop construct. (6) 'If/in case' clauses that represent mutually exclusive decision paths must use `if`/`else`, whereas 'when/upon/after' clauses that simply trigger an action must be modeled as sequential activities without branching.
 
 ## rule
 
```
