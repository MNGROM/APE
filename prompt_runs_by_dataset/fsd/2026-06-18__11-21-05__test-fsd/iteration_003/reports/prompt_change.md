# Iteration 003 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 1556
- chars_after: 2558
- chars_candidate: 2558

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,15 +12,17 @@
 
 ## workflow
 
-Step 1: Extract a minimal, exhaustive list of discrete activities explicitly stated in the text, mapping them 1-to-1 to activity nodes without summarizing or adding implicit steps.
-Step 2: Construct the control flow strictly among these extracted nodes, using the text's explicit sequencing and conditional logic, without adding or merging nodes.
+Step 1: Extract a complete and granular, exhaustive list of discrete activities explicitly stated in the text, mapping them 1-to-1 to activity nodes without summarizing or adding implicit steps. Preserve distinct UI elements, data entry fields, and intermediate states as separate nodes rather than summarizing them.
+Step 2: Construct the control flow strictly among these extracted nodes, using the text's explicit sequencing and conditional logic, without adding or merging nodes. Identify linguistic cues for simultaneous execution (e.g., 'simultaneously', 'at the same time', 'concurrently') and construct parallel flows using `fork`/`join` for those specific cases, while keeping sequential or alternative lists as non-parallel.
 
 ## knowledge
 
-- Distinguish sequential actions from concurrent flows: only use `fork`/`join` when the requirement explicitly states simultaneous execution; grammatical lists (e.g., 'enter name and description') or alternative options must be modeled as sequential activities or `if`/`else` branches, not as parallel forks.
-- Map nested conditional logic: map mutually exclusive conditions (e.g., 'if X, else if Y') using nested `if`/`elseif`/`else` constructs rather than flattening them into sequential or unrelated branches.
+- Distinguish sequential actions from concurrent flows: only use `fork`/`join` when the requirement explicitly states simultaneous execution; grammatical lists (e.g., 'enter name and description') or alternative options must be modeled as sequential activities or `if`/`else` branches, not as parallel forks. `fork`/`join` must be used when the requirement uses explicit concurrency cues (e.g., 'simultaneously', 'concurrently', 'at the same time').
+- Map nested conditional logic: map mutually exclusive conditions (e.g., 'if X, else if Y') using nested `if`/`elseif`/`else` constructs rather than flattening them into sequential or unrelated branches. However, for mutually exclusive state-based transitions or case-like logic (e.g., 'depending on state X'), use `switch`/`endswitch` constructs instead of `if`/`elseif`/`else`.
 
 ## rule
 
 - Do not invent implicit steps, validations, error-handling branches, or system responses unless they are explicitly stated in the requirement.
 - Do not add control flow edges that are not directly supported by the requirement's stated sequence or logic; specifically, do not force sequential dependencies between unrelated steps or misroute branches.
+- Do not decompose a single stated action into multiple assumed sub-steps unless those sub-steps are explicitly detailed in the text.
+- Preserve granular UI elements, data entry fields, and intermediate system states as distinct activity nodes; do not compress them into broad abstract activities.
```
