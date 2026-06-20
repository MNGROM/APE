# Iteration 005 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate
- chars_before: 1488
- chars_after: 1488
- chars_candidate: 2621

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,17 +12,21 @@
 
 ## workflow
 
-Step 1: Extract and list all explicit activities and conditional/alternative statements strictly from the requirement text, preserving each distinct behavioral step as a separate item.
-Step 2: Construct the PlantUML diagram by mapping only those extracted items to activities and control-flow constructs, prohibiting any additions.
+Step 1: Extract and list all explicit activities and conditional/alternative statements strictly from the requirement text, preserving each distinct behavioral step as a separate item. Additionally, identify and extract: (a) simultaneous or co-occurring behaviors for fork/join; (b) iterative or repetitive language for repeat/while loops; (c) contextual states, outcome labels, and setup statements as distinct activity items; (d) hierarchical dependencies among conditions.
+Step 2: Construct the PlantUML diagram by mapping only those extracted items to activities and control-flow constructs, prohibiting any additions. Map extracted parallel items to fork/join, iterative items to repeat/while, and preserve the hierarchical nesting of conditions in the diagram structure.
 
 ## knowledge
 
 - fork/join: Used for concurrent, simultaneous actions or parallel information display.
 - if/elseif/else and switch/endswitch: Used for mutually exclusive, alternative paths or user choices.
+- repeat/while: Used for iterative, repetitive, or periodic actions (e.g., language like 'repeat', 'until', 'for each').
+- Hierarchical or dependent conditions (e.g., 'under that condition') must be modeled as nested if/switch structures, not flat independent ones.
+- Outcome labels, state descriptions, and contextual setup statements should be represented as activity nodes.
+- PlantUML syntactic dependencies: elseif must follow an if, and switch requires endswitch.
 - Enumerated sub-steps or listed options represent alternatives (switch/if), not parallelism, unless explicitly stated as simultaneous.
 
 ## rule
 
-(1) Do not invent, infer, or add any activities, steps, or UI interactions (e.g., login, navigation, validation, success/error messages, retry loops) that are not explicitly stated in the requirement.
+(1) Do not invent, infer, or add speculative activities, steps, UI interactions (e.g., login, navigation, validation, success/error messages, retry loops), or control-flow branches that are not explicitly stated in the requirement; however, contextual state descriptions, outcome labels (e.g., 'Allowed'/'Not allowed'), and setup statements explicitly present in the requirement text must be included as activity nodes.
 (2) Do not merge multiple distinct behavioral steps from the requirement into a single activity node; maintain the original granularity.
 (3) Do not insert speculative control-flow branches (e.g., validation checks, error handling) unless explicitly described in the requirement text.
```
