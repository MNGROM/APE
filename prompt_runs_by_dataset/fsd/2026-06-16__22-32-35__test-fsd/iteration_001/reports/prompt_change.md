# Iteration 001 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 364
- chars_after: 1542
- chars_candidate: 1542

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,12 +12,19 @@
 
 ## workflow
 
-(None)
+1) Identify and list only the explicit activities and actions stated in the input.
+2) Determine the sequential or conditional control flow strictly between those identified activities.
+3) Map the activities and flows directly into PlantUML syntax. No activities or transitions should be added if they are not explicitly grounded in the input text.
 
 ## knowledge
 
-(None)
+1) Basic PlantUML activity diagram syntax: use `start`/`stop` for initial and final nodes, action states, `->` for transitions, `if`/`else`/`endif` for conditional branches, and `while`/`endwhile` for loops.
+2) UML conventions: every diagram requires exactly one start node and at least one end node.
+3) Conditional logic in the text must map to standard branching elements (if/else/endif) rather than linear sequences.
 
 ## rule
 
-(None)
+1) Output must contain only valid PlantUML code with no markdown formatting, explanations, or surrounding text.
+2) Every generated diagram must include exactly one 'start' and at least one 'stop' node.
+3) All activity names and transition labels must closely reflect the exact phrasing from the input requirement.
+4) Do not invent background steps, implicit transitions, or extra activities not explicitly mentioned in the input.
```
