# Iteration 007 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate
- chars_before: 2463
- chars_after: 2463
- chars_candidate: 3671

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
+Step 1: Extract activities strictly from explicit actions in the requirement. By default, comma-separated lists, 'and'-joined clauses, and enumerations of attributes, options, or roles must be grouped into a single activity node or connected sequentially. Explicit concurrency cues (e.g., 'simultaneously', 'in parallel', 'concurrently') are the only permitted triggers for decomposing these into parallel branches. Remove any ambiguous phrasing that suggests contextual decomposition.
 Step 2: Decompose any identified concurrent compound steps into separate activities before constructing control-flow.
-Step 3: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks.
+Step 3: Construct control-flow by connecting the extracted activities. When the requirement presents mutually exclusive conditions, alternative options, or case-based outcomes, they must be mapped to switch/case or if/elseif structures; deeply nested if/else structures must be avoided for such logic. Map explicit concurrency keywords to fork/join blocks.
 
 ## knowledge
 
-- Concurrency modeling: Comma-separated lists or 'and'-joined clauses must be decomposed into fork/join blocks *only* when accompanied by explicit concurrency cues or when describing simultaneous system behaviors (e.g., 'Close window and display statistics'). Explicitly exclude comma-separated lists that represent sequential UI steps, configuration options, or sequentially dependent steps in multi-threaded contexts from fork/join usage; these must remain single activity nodes or sequential flows.
-- Loop modeling: Map iterative cues (e.g., 'repeat', 'retry', 'periodically', 'cyclically') to repeat/while loops, ensuring the loop boundary strictly wraps only the iterative portion and does not enclose non-iterative parallel blocks.
+- Concurrency modeling: Comma-separated lists, 'and'-joined clauses, and enumerations must be decomposed into fork/join blocks *only* when accompanied by explicit concurrency keywords ('simultaneously', 'in parallel', 'concurrently') or when describing simultaneous system behaviors (e.g., 'Close window and display statistics'). Explicitly exclude the following non-concurrent categories from fork/join usage; these must remain single activity nodes or sequential flows: lists of permissions/rights, configuration attributes, deployment options, and sequential UI steps. The broad 'and'-joined clause trigger is not permitted unless accompanied by explicit concurrency cues.
+- Loop modeling: Map iterative cues (e.g., 'repeat', 'retry', 'periodically', 'cyclically') to repeat/while loops, ensuring the loop boundary strictly wraps only the iterative portion and does not enclose non-iterative parallel blocks. For complex iterative patterns: map 'periodic' or 'monitoring' cues to repeat/while loops enclosing the monitoring action and subsequent logic; map 'retry with exponential backoff' to a repeat/while loop where the loop body contains the retry action followed by a delay/wait activity that increases iteratively.
 
 ## rule
 
-- Granularity rule: Do not infer implicit system interactions or UI responses unless explicitly stated in the text; do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement.
+- Granularity rule: Do not infer implicit system interactions or UI responses unless explicitly stated in the text. Do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement. Additionally: 1) Constraints (e.g., 'shall not exceed', 'must be within') are inherent properties of an action and must be represented as simple activities or guard conditions, not as runtime conditional checks with invented branching outcomes (e.g., 'Error tolerance exceeded'). 2) Complex actions describing multi-part behaviors (e.g., 'exchange content availability and load information') must be decomposed into separate sequential or parallel activities for each constituent part, rather than collapsed into a single broad node.
 - Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. Instead, conditional paths must merge.
```
