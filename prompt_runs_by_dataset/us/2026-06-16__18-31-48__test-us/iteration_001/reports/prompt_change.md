# Iteration 001 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, bootstrap_gate
- chars_before: 364
- chars_after: 364
- chars_candidate: 1454

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,12 +12,16 @@
 
 ## workflow
 
-(None)
+Step 1: Identify and list all explicit activities and structural nodes strictly from the requirement text, preserving granular details without generalizing or collapsing them.
+Step 2: Construct the control flow (transitions, branches, loops) exclusively using the activities identified in Step 1. Do not add any implicit activities not explicitly stated in the requirement.
 
 ## knowledge
 
-(None)
+(1) Concurrency: Use the 'fork/end fork' structure. All parallel branches must converge at the 'end fork'. Never use 'stop' inside a fork block.
+(2) Temporal logic: For waits, periodic tasks, or retries, use 'repeat/repeat while' or 'while/end while' loop constructs. Duration-based conditions (e.g., 'wait X seconds') represent loop delays, not standard conditional branches.
 
 ## rule
 
-(None)
+(1) Do NOT add implicit error-handling, validation checks, or speculative 'happy path vs. error path' branches unless they are explicitly described in the requirement.
+(2) Do NOT use 'stop' inside a 'fork' block.
+(3) All control flows and transitions must be strictly grounded in the requirement; do not create transitions to or from hallucinated activities.
```
