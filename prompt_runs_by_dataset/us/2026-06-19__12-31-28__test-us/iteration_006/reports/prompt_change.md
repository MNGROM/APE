# Iteration 006 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: has_required_metric_benefit, bootstrap_gate
- chars_before: 2463
- chars_after: 2463
- chars_candidate: 2736

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,16 +12,17 @@
 
 ## workflow
 
-Step 1: Extract activities strictly from explicit actions in the requirement, grouping lists of attributes, parameters, or properties into a single descriptive activity node *unless* they are joined by explicit concurrency cues (e.g., 'simultaneously', 'in parallel') or represent simultaneous system behaviors (e.g., 'Close window and display statistics'). In those specific cases, decompose the compound step into separate activities for parallel branching.
-Step 2: Decompose any identified concurrent compound steps into separate activities before constructing control-flow.
-Step 3: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks.
+Step 1: Extract activities strictly from explicit actions in the requirement. Establish a strict default: any list of items, attributes, parameters, or sequential UI steps MUST be grouped into a single descriptive activity node or connected sequentially unless an explicit concurrency keyword (e.g., 'simultaneously', 'in parallel', 'concurrently') is present in the exact same sentence.
+Step 2: Explicitly list all extracted activities and verify a 1-to-1 mapping to explicit actions in the requirement, preventing collapsed or omitted steps.
+Step 3: Decompose any identified concurrent compound steps (those with explicit concurrency keywords) into separate activities before constructing control-flow.
+Step 4: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks.
 
 ## knowledge
 
-- Concurrency modeling: Comma-separated lists or 'and'-joined clauses must be decomposed into fork/join blocks *only* when accompanied by explicit concurrency cues or when describing simultaneous system behaviors (e.g., 'Close window and display statistics'). Explicitly exclude comma-separated lists that represent sequential UI steps, configuration options, or sequentially dependent steps in multi-threaded contexts from fork/join usage; these must remain single activity nodes or sequential flows.
+- Concurrency modeling: Fork/join blocks are strictly prohibited for comma-separated lists, 'and'-joined attributes, configuration options, or alternative choices unless the sentence contains an explicit concurrency keyword. When an explicit concurrency keyword is present, it triggers a mandatory fork/join block for the joined actions. Explicitly exclude 'and' used for sequential UI steps (e.g., 'enter name and description') from triggering fork/join; these must remain single activity nodes or sequential flows.
 - Loop modeling: Map iterative cues (e.g., 'repeat', 'retry', 'periodically', 'cyclically') to repeat/while loops, ensuring the loop boundary strictly wraps only the iterative portion and does not enclose non-iterative parallel blocks.
 
 ## rule
 
-- Granularity rule: Do not infer implicit system interactions or UI responses unless explicitly stated in the text; do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement.
+- Granularity rule: Every distinct action verb or state transition explicitly stated in the requirement MUST map to a distinct activity node; abstracting multiple specified actions into a single broad node is prohibited. Do not infer implicit system interactions, UI responses, or speculative logic (such as adding 'No' branches or 'else' conditions) unless the requirement text explicitly states the alternative or failure condition.
 - Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. Instead, conditional paths must merge.
```
