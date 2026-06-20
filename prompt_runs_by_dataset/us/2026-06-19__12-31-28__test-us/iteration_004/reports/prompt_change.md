# Iteration 004 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 1774
- chars_after: 2463
- chars_candidate: 2463

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,15 +12,16 @@
 
 ## workflow
 
-Step 1: Extract activities strictly from explicit actions in the requirement, grouping lists of attributes, parameters, or properties into a single descriptive activity node rather than splitting them.
-Step 2: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks.
+Step 1: Extract activities strictly from explicit actions in the requirement, grouping lists of attributes, parameters, or properties into a single descriptive activity node *unless* they are joined by explicit concurrency cues (e.g., 'simultaneously', 'in parallel') or represent simultaneous system behaviors (e.g., 'Close window and display statistics'). In those specific cases, decompose the compound step into separate activities for parallel branching.
+Step 2: Decompose any identified concurrent compound steps into separate activities before constructing control-flow.
+Step 3: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks.
 
 ## knowledge
 
-- Concurrency modeling: Only use fork/join blocks when the requirement contains explicit concurrency cues (e.g., 'concurrently', 'simultaneously', 'in parallel'). Explicitly exclude comma-separated lists, attributes, options, and sequential UI steps from fork/join usage; these must remain single activity nodes or sequential flows.
+- Concurrency modeling: Comma-separated lists or 'and'-joined clauses must be decomposed into fork/join blocks *only* when accompanied by explicit concurrency cues or when describing simultaneous system behaviors (e.g., 'Close window and display statistics'). Explicitly exclude comma-separated lists that represent sequential UI steps, configuration options, or sequentially dependent steps in multi-threaded contexts from fork/join usage; these must remain single activity nodes or sequential flows.
 - Loop modeling: Map iterative cues (e.g., 'repeat', 'retry', 'periodically', 'cyclically') to repeat/while loops, ensuring the loop boundary strictly wraps only the iterative portion and does not enclose non-iterative parallel blocks.
 
 ## rule
 
-- Granularity rule: Do not infer implicit system interactions or UI responses unless explicitly stated in the text; do not collapse multiple distinct specified actions into one broad node.
-- Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; do not place stop nodes inside parallel branches or conditional paths unless the requirement explicitly states an immediate process termination for that specific branch.
+- Granularity rule: Do not infer implicit system interactions or UI responses unless explicitly stated in the text; do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement.
+- Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. Instead, conditional paths must merge.
```
