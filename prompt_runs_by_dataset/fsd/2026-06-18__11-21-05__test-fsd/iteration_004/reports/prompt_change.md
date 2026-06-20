# Iteration 004 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate
- chars_before: 2558
- chars_after: 2558
- chars_candidate: 3393

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -13,16 +13,20 @@
 ## workflow
 
 Step 1: Extract a complete and granular, exhaustive list of discrete activities explicitly stated in the text, mapping them 1-to-1 to activity nodes without summarizing or adding implicit steps. Preserve distinct UI elements, data entry fields, and intermediate states as separate nodes rather than summarizing them.
-Step 2: Construct the control flow strictly among these extracted nodes, using the text's explicit sequencing and conditional logic, without adding or merging nodes. Identify linguistic cues for simultaneous execution (e.g., 'simultaneously', 'at the same time', 'concurrently') and construct parallel flows using `fork`/`join` for those specific cases, while keeping sequential or alternative lists as non-parallel.
+Step 2: Identify linguistic cues for repetition, retry, or corrective actions (e.g., 'retry', 're-enter', 'repeat until') and map them to `while` or `repeat` loop constructs.
+Step 3: Explicitly identify and route termination conditions and early exits (e.g., 'exit', 'cancel', 'stop') to `stop` nodes, rather than leaving them disconnected or misrouted.
+Step 4: Construct the control flow strictly among these extracted nodes, using the text's explicit sequencing and conditional logic, without adding or merging nodes. Identify linguistic cues for simultaneous execution (e.g., 'simultaneously', 'at the same time', 'concurrently') and construct parallel flows using `fork`/`join` for those specific cases, while keeping sequential or alternative lists as non-parallel.
 
 ## knowledge
 
-- Distinguish sequential actions from concurrent flows: only use `fork`/`join` when the requirement explicitly states simultaneous execution; grammatical lists (e.g., 'enter name and description') or alternative options must be modeled as sequential activities or `if`/`else` branches, not as parallel forks. `fork`/`join` must be used when the requirement uses explicit concurrency cues (e.g., 'simultaneously', 'concurrently', 'at the same time').
+- Distinguish sequential actions from concurrent flows: only use `fork`/`join` when the requirement explicitly states simultaneous execution; grammatical lists of attributes or fields (e.g., 'enter name, address, and phone') must be modeled as sequential activities or a single activity, and `fork`/`join` is strictly reserved for requirements using explicit concurrency cues (e.g., 'simultaneously', 'concurrently', 'at the same time').
 - Map nested conditional logic: map mutually exclusive conditions (e.g., 'if X, else if Y') using nested `if`/`elseif`/`else` constructs rather than flattening them into sequential or unrelated branches. However, for mutually exclusive state-based transitions or case-like logic (e.g., 'depending on state X'), use `switch`/`endswitch` constructs instead of `if`/`elseif`/`else`.
+- Model repetition and retry: linguistic cues of repetition or retry (e.g., 'retry', 're-enter', 'repeat until') must be modeled using `while` or `repeat` loops, not one-time sequential branches.
 
 ## rule
 
 - Do not invent implicit steps, validations, error-handling branches, or system responses unless they are explicitly stated in the requirement.
 - Do not add control flow edges that are not directly supported by the requirement's stated sequence or logic; specifically, do not force sequential dependencies between unrelated steps or misroute branches.
 - Do not decompose a single stated action into multiple assumed sub-steps unless those sub-steps are explicitly detailed in the text.
-- Preserve granular UI elements, data entry fields, and intermediate system states as distinct activity nodes; do not compress them into broad abstract activities.
+- Preserve granular UI elements, data entry fields, and intermediate system states as distinct activity nodes only when these elements are explicitly detailed as separate actions in the text; do not decompose a single stated action into multiple assumed sub-steps or add unmentioned decision nodes.
+- Do not omit or oversimplify explicitly stated alternative flows, edge-case paths, or distinct behaviors; all requirement-specified options must be represented.
```
