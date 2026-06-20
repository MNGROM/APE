# Iteration 001 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 364
- chars_after: 1488
- chars_candidate: 1488

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,12 +12,17 @@
 
 ## workflow
 
-(None)
+Step 1: Extract and list all explicit activities and conditional/alternative statements strictly from the requirement text, preserving each distinct behavioral step as a separate item.
+Step 2: Construct the PlantUML diagram by mapping only those extracted items to activities and control-flow constructs, prohibiting any additions.
 
 ## knowledge
 
-(None)
+- fork/join: Used for concurrent, simultaneous actions or parallel information display.
+- if/elseif/else and switch/endswitch: Used for mutually exclusive, alternative paths or user choices.
+- Enumerated sub-steps or listed options represent alternatives (switch/if), not parallelism, unless explicitly stated as simultaneous.
 
 ## rule
 
-(None)
+(1) Do not invent, infer, or add any activities, steps, or UI interactions (e.g., login, navigation, validation, success/error messages, retry loops) that are not explicitly stated in the requirement.
+(2) Do not merge multiple distinct behavioral steps from the requirement into a single activity node; maintain the original granularity.
+(3) Do not insert speculative control-flow branches (e.g., validation checks, error handling) unless explicitly described in the requirement text.
```
