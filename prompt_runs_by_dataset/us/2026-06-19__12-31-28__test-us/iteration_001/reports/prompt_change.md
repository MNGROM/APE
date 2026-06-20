# Iteration 001 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, bootstrap_gate
- chars_before: 364
- chars_after: 364
- chars_candidate: 2430

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,12 +12,17 @@
 
 ## workflow
 
-(None)
+Step 1: Identify and list every explicit action, state, and intermediate step mentioned in the requirement without compression or abstraction.
+Step 2: Construct the control-flow relations (sequence, branch, loop, fork/join) strictly among the activities identified in Step 1. Adding any activity not listed in Step 1 is prohibited.
 
 ## knowledge
 
-(None)
+- Concurrency modeling rule: Only use fork/join when the requirement text explicitly indicates simultaneous execution (e.g., using 'simultaneously', 'in parallel', 'concurrently'). Explicitly exclude enumerations of attributes, alternative options, or sequential UI steps from fork/join usage; these must be modeled as sequential activities or if/else branches.
+- Fork/join boundary rule: All forked branches must converge at a corresponding join node before any subsequent sequential or conditional logic begins. Sequential or conditional logic must not be nested inside a fork block unless the requirement explicitly specifies it as concurrent to that specific branch.
+- Conditional mapping rule: Requirements containing nested 'if-else' or multi-level decision logic must be mapped to nested if/elseif/else PlantUML constructs. Flattening nested conditions into a single level or misrouting them as sequential steps is prohibited.
+- Loop modeling rule: Map explicit loop indicators (e.g., 'repeatable', 'periodic', 'retry') to loop constructs. Distinguish between 'while' (condition checked before the loop body) and 'repeat/until' (condition checked after the loop body) based on the requirement text, and place the condition check at the exact point specified.
 
 ## rule
 
-(None)
+- Strict exclusion rule: Do not add error-handling, validation, or rejection branches unless the requirement text explicitly describes them. Simple checks must only be modeled as specified, without inferring failure paths.
+- Control-flow constraint: Sequential procedural steps must be modeled as a linear flow. Do not route sequential steps through if/else or switch blocks. Mutually exclusive alternatives must only be used when the requirement explicitly specifies choices or options.
```
