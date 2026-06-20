# Iteration 002 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 364
- chars_after: 1924
- chars_candidate: 1924

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,12 +12,16 @@
 
 ## workflow
 
-(None)
+1. Extract all explicit activities and actions from the requirement without abstracting or compressing them.
+2. Identify and flag concurrent/grouped items for parallel fork decomposition.
+3. Identify and flag iterative or continuous monitoring phrases for loop construct mapping.
+4. Identify and flag conditional logic for branching construct mapping.
+5. Construct the PlantUML code strictly based on the extracted activities and identified control-flow constructs.
 
 ## knowledge
 
-(None)
+(1) Lists or grouped concurrent items (e.g., 'A and B', 'A, B, and C') must be decomposed into separate parallel branches using `fork`/`fork again`/`end fork`. (2) Continuous or iterative monitoring (e.g., 'while X remains stable', 'monitor until') must be modeled as loops using `while`/`end while` or `repeat`/`repeat while`, not as simple conditionals or switch statements. (3) Explicit conditional checks (e.g., 'if X', 'in case of Y') must be modeled as decision nodes using `if`/`elseif`/`else`/`endif`, preserving the requirement's logic as guard labels.
 
 ## rule
 
-(None)
+(1) Do not omit, abstract, or compress any activity explicitly mentioned in the requirement; every stated action must appear as a distinct activity node. (2) Do not collapse conditional checks or alternative paths into sequential actions; they must be explicitly modeled. (3) Use correct PlantUML syntax for control flow: `fork`/`end fork` for parallel branches, `while`/`end while` or `repeat`/`repeat while` for loops, and `if`/`else`/`endif` for conditionals. Do not substitute these with incorrect constructs (e.g., do not use `switch` for loops).
```
