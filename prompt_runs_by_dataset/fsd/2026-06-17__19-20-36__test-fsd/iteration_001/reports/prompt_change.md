# Iteration 001 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 364
- chars_after: 1498
- chars_candidate: 1498

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,12 +12,13 @@
 
 ## workflow
 
-(None)
+1. Extract a closed list of activities directly and explicitly stated in the requirement text, including contextual, purpose-oriented, and final actions, without inferring or adding sub-steps.
+2. Construct the control flow strictly among these extracted activities, mapping sequential steps, alternative/exception flows as branches or loops, and concurrent flows as forks, based solely on the text.
 
 ## knowledge
 
-(None)
+(1) Use if/else-if/else structures for mutually exclusive decision paths or guarded outcomes; (2) Use fork/fork-again only for truly concurrent, independent actions; (3) Model alternative, retry, or exception flows as separate branches that loop back to a previous activity or rejoin the main flow, rather than flattening them into the main sequence.
 
 ## rule
 
-(None)
+(1) Only include activities that are explicitly stated in the requirement; do not invent, decompose, or infer sub-steps, checks, or result actions; (2) Do not introduce if/else decision nodes unless the requirement explicitly describes a conditional choice or alternative paths; (3) Preserve all explicitly mentioned actions, including contextual, purpose-oriented, and final actions, as activity nodes.
```
