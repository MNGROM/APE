# Iteration 001 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 364
- chars_after: 1556
- chars_candidate: 1556

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,12 +12,15 @@
 
 ## workflow
 
-(None)
+Step 1: Extract a minimal, exhaustive list of discrete activities explicitly stated in the text, mapping them 1-to-1 to activity nodes without summarizing or adding implicit steps.
+Step 2: Construct the control flow strictly among these extracted nodes, using the text's explicit sequencing and conditional logic, without adding or merging nodes.
 
 ## knowledge
 
-(None)
+- Distinguish sequential actions from concurrent flows: only use `fork`/`join` when the requirement explicitly states simultaneous execution; grammatical lists (e.g., 'enter name and description') or alternative options must be modeled as sequential activities or `if`/`else` branches, not as parallel forks.
+- Map nested conditional logic: map mutually exclusive conditions (e.g., 'if X, else if Y') using nested `if`/`elseif`/`else` constructs rather than flattening them into sequential or unrelated branches.
 
 ## rule
 
-(None)
+- Do not invent implicit steps, validations, error-handling branches, or system responses unless they are explicitly stated in the requirement.
+- Do not add control flow edges that are not directly supported by the requirement's stated sequence or logic; specifically, do not force sequential dependencies between unrelated steps or misroute branches.
```
