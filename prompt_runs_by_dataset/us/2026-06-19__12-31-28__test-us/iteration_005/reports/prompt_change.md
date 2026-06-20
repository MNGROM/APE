# Iteration 005 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate
- chars_before: 2463
- chars_after: 2463
- chars_candidate: 3144

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,16 +12,16 @@
 
 ## workflow
 
-Step 1: Extract activities strictly from explicit actions in the requirement, grouping lists of attributes, parameters, or properties into a single descriptive activity node *unless* they are joined by explicit concurrency cues (e.g., 'simultaneously', 'in parallel') or represent simultaneous system behaviors (e.g., 'Close window and display statistics'). In those specific cases, decompose the compound step into separate activities for parallel branching.
+Step 1: Extract each explicitly stated action as its own distinct activity node. Strictly prohibit decomposing lists of attributes, parameters, or properties into parallel branches; keep enumerated attributes/parameters grouped within a single descriptive activity node. Fork/join blocks are only permitted if an explicit concurrency cue (e.g., 'concurrently', 'in parallel', 'simultaneously') is present in the text.
 Step 2: Decompose any identified concurrent compound steps into separate activities before constructing control-flow.
-Step 3: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks.
+Step 3: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures. Whenever an explicit concurrency cue (e.g., 'concurrently', 'simultaneously', 'in parallel') is present, the connected actions must be decomposed into separate activities and mapped to a fork/join block; this is a strict requirement triggered only by these specific textual cues.
 
 ## knowledge
 
-- Concurrency modeling: Comma-separated lists or 'and'-joined clauses must be decomposed into fork/join blocks *only* when accompanied by explicit concurrency cues or when describing simultaneous system behaviors (e.g., 'Close window and display statistics'). Explicitly exclude comma-separated lists that represent sequential UI steps, configuration options, or sequentially dependent steps in multi-threaded contexts from fork/join usage; these must remain single activity nodes or sequential flows.
-- Loop modeling: Map iterative cues (e.g., 'repeat', 'retry', 'periodically', 'cyclically') to repeat/while loops, ensuring the loop boundary strictly wraps only the iterative portion and does not enclose non-iterative parallel blocks.
+- Concurrency modeling: Fork/join blocks must be used if and only if the text contains explicit concurrency keywords (e.g., 'concurrently', 'in parallel', 'simultaneously'). 'And'-joined clauses or comma-separated lists without these exact keywords must not be modeled as parallel; they must remain single activity nodes or sequential flows.
+- Loop modeling: Map iterative cues (e.g., 'repeat', 'retry', 'periodically', 'cyclically') to repeat/while loops. The loop boundary must strictly wrap only the activities explicitly modified by iterative cues, ensuring activities not explicitly part of the iteration remain outside the loop. Identify the exit condition (e.g., text following 'until' or 'if successful') and map it to the 'while' or 'repeat until' construct.
 
 ## rule
 
-- Granularity rule: Do not infer implicit system interactions or UI responses unless explicitly stated in the text; do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement.
-- Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. Instead, conditional paths must merge.
+- Granularity rule: This rule overrides grouping heuristics: distinct specified actions must never be collapsed into a single node unless they are merely attributes/parameters describing a single action. Do not invent control-flow logic (e.g., 'Reject command', 'Allow command', or if-else branches) to enforce constraints unless the requirement text explicitly states alternative outcomes or conditional branching.
+- Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. When a requirement contains multi-branch decision logic (e.g., a switch/case inside an if/else), map the outer condition to an if/elseif/else structure and the inner condition to a nested switch/case or if structure. Inner conditional paths must merge at their local join point before the outer conditional paths merge at the outer join point, preventing the flattening of nested control-flow.
```
