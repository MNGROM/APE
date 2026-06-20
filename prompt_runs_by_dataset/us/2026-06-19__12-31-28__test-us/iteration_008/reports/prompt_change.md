# Iteration 008 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: has_required_metric_benefit, bootstrap_gate
- chars_before: 2463
- chars_after: 2463
- chars_candidate: 4219

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,16 +12,18 @@
 
 ## workflow
 
-Step 1: Extract activities strictly from explicit actions in the requirement, grouping lists of attributes, parameters, or properties into a single descriptive activity node *unless* they are joined by explicit concurrency cues (e.g., 'simultaneously', 'in parallel') or represent simultaneous system behaviors (e.g., 'Close window and display statistics'). In those specific cases, decompose the compound step into separate activities for parallel branching.
-Step 2: Decompose any identified concurrent compound steps into separate activities before constructing control-flow.
-Step 3: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks.
+Step 1: Extract activities strictly from explicit actions in the requirement, grouping lists of attributes, parameters, or properties into a single descriptive activity node. Add a verification sub-step requiring you to explicitly confirm that any decomposed activities can execute at the exact same time; if they represent sequential UI entries, alternative options, or attribute lists, they must remain grouped as a single activity node.
+Step 2: List every distinct behavioral step or state transition explicitly stated in the requirement as a separate activity node, without abstracting or compressing multiple specified actions into a single node. Control-flow construction must only occur after this exhaustive list is generated.
+Step 3: Decompose any identified concurrent compound steps into separate activities before constructing control-flow.
+Step 4: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks. Add a verification sub-step requiring you to confirm that fork/join branches are structurally independent from the main sequential flow and are not nested inside loops unless the requirement explicitly states that the parallel tasks repeat together.
 
 ## knowledge
 
-- Concurrency modeling: Comma-separated lists or 'and'-joined clauses must be decomposed into fork/join blocks *only* when accompanied by explicit concurrency cues or when describing simultaneous system behaviors (e.g., 'Close window and display statistics'). Explicitly exclude comma-separated lists that represent sequential UI steps, configuration options, or sequentially dependent steps in multi-threaded contexts from fork/join usage; these must remain single activity nodes or sequential flows.
-- Loop modeling: Map iterative cues (e.g., 'repeat', 'retry', 'periodically', 'cyclically') to repeat/while loops, ensuring the loop boundary strictly wraps only the iterative portion and does not enclose non-iterative parallel blocks.
+- Concurrency modeling: Comma-separated lists or 'and'-joined clauses must be decomposed into fork/join blocks *only* when accompanied by explicit concurrency keywords (e.g., 'simultaneously', 'in parallel'). Explicitly exclude comma-separated lists that represent alternative options (e.g., 'display current or historical info'), form fields (e.g., 'enter name, description, keywords'), monitoring conditions (e.g., 'monitor DCDC, EAS, WTCH'), sequential UI steps, configuration options, or sequentially dependent steps in multi-threaded contexts from fork/join usage; these must remain single activity nodes or sequential flows. When a requirement describes a background, periodic, or continuous task (e.g., 'periodic telemetry monitor', 'sensor fusion routines') alongside a main sequential process, the background task must be modeled in a fork/join block parallel to the main sequential flow, not sequentially after it or nested inside the main loop.
+- Loop modeling: (1) Simple threshold or duration monitoring (e.g., 'monitor duration') must be modeled as a conditional branch (if/else), not a loop, unless an explicit iterative cue like 'repeat until' is present. (2) Periodic tasks (e.g., 'periodically calibrate') must be modeled as concurrent parallel loops inside a fork/join block, not as sequential repeat loops in the main flow. (3) Loop boundaries must strictly wrap the entire repetitive cycle, including any restart or re-initialization logic specified for that cycle.
 
 ## rule
 
-- Granularity rule: Do not infer implicit system interactions or UI responses unless explicitly stated in the text; do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement.
-- Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. Instead, conditional paths must merge.
+- Fabrication rule: Do not infer, fabricate, or insert any activities, loops, or control logic (e.g., 'Start duration counter', 'Continue commanding acceleration', 'Validate with CRC') that are not explicitly stated in the requirement text. Persistent states must be modeled as such, not as fabricated backward loops.
+- Granularity rule: Multiple distinct specified actions (e.g., 'Regulate PWM fans' and 'Regulate liquid-cooling loops') must be preserved as separate activity nodes; do not collapse or abstract them into a single broad node even if they belong to the same system component. Do not infer implicit system interactions or UI responses unless explicitly stated in the text.
+- Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches or fork/join branches unless the requirement explicitly states an immediate process termination for that specific branch. All fork branches must converge at a join node before reaching a stop node. Instead, conditional paths must merge.
```
