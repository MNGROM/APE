# Iteration 005 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 2558
- chars_after: 3907
- chars_candidate: 3907

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -13,16 +13,20 @@
 ## workflow
 
 Step 1: Extract a complete and granular, exhaustive list of discrete activities explicitly stated in the text, mapping them 1-to-1 to activity nodes without summarizing or adding implicit steps. Preserve distinct UI elements, data entry fields, and intermediate states as separate nodes rather than summarizing them.
-Step 2: Construct the control flow strictly among these extracted nodes, using the text's explicit sequencing and conditional logic, without adding or merging nodes. Identify linguistic cues for simultaneous execution (e.g., 'simultaneously', 'at the same time', 'concurrently') and construct parallel flows using `fork`/`join` for those specific cases, while keeping sequential or alternative lists as non-parallel.
+Step 2: Identify iterative or repetitive behaviors triggered by textual cues (e.g., 'repeat', 'every', 'until', 'while') and structural elements such as distinct actors or systems. Map these iterative cues to `repeat`/`while` constructs and distinct actors/systems to `partition` blocks.
+Step 3: Construct the control flow strictly among these extracted nodes, using the text's explicit sequencing and conditional logic, without adding or merging nodes. Identify both explicit linguistic cues (e.g., 'simultaneously', 'at the same time', 'concurrently') and contextual cues (e.g., multiple independent attributes being processed or simultaneous sub-tasks that logically occur at the same time) for simultaneous execution, and construct parallel flows using `fork`/`join` for those cases, while keeping dependent or alternative lists as sequential or `if`/`else` branches.
 
 ## knowledge
 
-- Distinguish sequential actions from concurrent flows: only use `fork`/`join` when the requirement explicitly states simultaneous execution; grammatical lists (e.g., 'enter name and description') or alternative options must be modeled as sequential activities or `if`/`else` branches, not as parallel forks. `fork`/`join` must be used when the requirement uses explicit concurrency cues (e.g., 'simultaneously', 'concurrently', 'at the same time').
+- Map iterative keywords (e.g., 'repeat', 'until', 'while') to PlantUML `repeat`/`while` loop constructs rather than linearized sequences. When distinct actors or systems are mentioned, their actions should be enclosed in `partition` blocks named after the actor/system to preserve behavioral boundaries.
+- Distinguish sequential actions from concurrent flows: use `fork`/`join` for explicit concurrency cues AND for contextual cues indicating independent simultaneous operations (e.g., multiple independent attributes processed at once). `fork`/`join` must NOT apply to grammatical lists of dependent steps or mutually exclusive alternatives, which must be modeled as sequential activities or `if`/`else` branches.
 - Map nested conditional logic: map mutually exclusive conditions (e.g., 'if X, else if Y') using nested `if`/`elseif`/`else` constructs rather than flattening them into sequential or unrelated branches. However, for mutually exclusive state-based transitions or case-like logic (e.g., 'depending on state X'), use `switch`/`endswitch` constructs instead of `if`/`elseif`/`else`.
 
 ## rule
 
-- Do not invent implicit steps, validations, error-handling branches, or system responses unless they are explicitly stated in the requirement.
+- Do not invent implicit steps, validations, error-handling branches, or system responses unless they are explicitly stated in the requirement; specifically, prohibit inventing user actions, validations, or interactions for high-level requirements (like user stories) when the text only states a goal—the model must only model what is explicitly detailed without filling in assumed interactions.
 - Do not add control flow edges that are not directly supported by the requirement's stated sequence or logic; specifically, do not force sequential dependencies between unrelated steps or misroute branches.
 - Do not decompose a single stated action into multiple assumed sub-steps unless those sub-steps are explicitly detailed in the text.
 - Preserve granular UI elements, data entry fields, and intermediate system states as distinct activity nodes; do not compress them into broad abstract activities.
+- Preserve all alternative paths, error checks, and specific conditional outcomes explicitly stated in the text; do not drop these activities in favor of only representing the main success path.
+- When distinct actors or systems are mentioned in the requirement, their corresponding activities must be grouped into `partition` blocks; do not omit these structural boundaries.
```
