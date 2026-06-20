# Iteration 003 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate
- chars_before: 2185
- chars_after: 2185
- chars_candidate: 3580

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,13 +12,13 @@
 
 ## workflow
 
-Step 1: Extract explicit activities strictly from the requirement text, explicitly including data sources, system outputs, and displayed information as distinct activity nodes. Identify and preserve structural elements such as swimlanes or partitions mentioned in the requirement.
-Step 2: Construct control-flow relations exclusively among the extracted activities, mapping textual lists and conditions to the appropriate PlantUML constructs. Analyze nested 'if-then' or state-dependent logic and map it using nested PlantUML control structures rather than flattening them into sequential or independent branches.
+Step 1: Extract activities strictly limited to actions explicitly stated in the text, explicitly including data sources, system outputs, and displayed information as distinct activity nodes. Prohibit the inference of sub-steps, the decomposition of high-level goals, and the creation of activity nodes from actor names or swimlane headers. Identify and preserve structural elements such as swimlanes or partitions mentioned in the requirement.
+Step 2: Construct control-flow relations exclusively among the extracted activities, mapping textual lists and conditions to the appropriate PlantUML constructs. Mandate that all extracted intermediate sequential steps, system responses, and state transitions must be preserved as distinct nodes in the control-flow, explicitly prohibiting the compression or collapsing of multiple sequential actions into a single broad node to simplify the overall diagram shape. Analyze nested 'if-then' or state-dependent logic and map it using nested PlantUML control structures rather than flattening them into sequential or independent branches.
 
 ## knowledge
 
-(1) Treat data sources, displayed information, and system outputs as distinct activity nodes when explicitly mentioned. (2) Map iterative keywords (e.g., 'repeat', 'for each', 'perform first X then Y') to PlantUML `repeat`/`while` loops. (3) Map mutually exclusive options, alternative choices, and attribute groupings to `switch`/`case` or `if`/`elseif`/`else` constructs. (4) Use `fork`/`join` for lists of attributes, options, or grouped items that represent independent properties or simultaneous display states, and for actions explicitly stated to occur concurrently or simultaneously; however, do NOT use `fork`/`join` for mutually exclusive alternative choices, sequential UI steps, or sequential actions.
+(1) Treat data sources, displayed information, and system outputs as distinct activity nodes when explicitly mentioned. (2) Map iterative keywords (e.g., 'repeat', 'for each', 'perform first X then Y') to PlantUML `repeat`/`while` loops. (3) Map mutually exclusive options using `switch`/`case` for selecting among discrete alternative options or enumerated types, and use `if`/`elseif`/`else` for evaluating conditional logic, guarded outcomes, or boolean state checks. Nested 'if-then' or state-dependent logic must be mapped using nested PlantUML control structures; do not flatten nested conditions into a single-level sequential or independent branch structure. (4) Use `fork`/`join` exclusively for actions explicitly described by concurrency keywords (e.g., 'simultaneously', 'concurrently', 'in parallel', 'while') or structural cues of independent concurrent execution (e.g., multiple independent monitors running at the same time). Itemized lists, sequential form fields, alternative purposes, and grouped display attributes are NOT concurrent and must not use `fork`/`join`.
 
 ## rule
 
-(1) Do not use `fork`/`join` for mutually exclusive alternative choices or sequential UI steps. (2) Do not invent implicit error-handling branches, validation loops, or recovery paths unless they are explicitly described in the requirement. (3) Do not compress multiple explicitly stated actions into a single abstract node. (4) Do not decompose high-level goals into assumed sub-steps (e.g., inferring 'select file', 'play audio' from 'identify whales') unless those sub-steps are explicitly stated in the text.
+(1) Do not use `fork`/`join` for mutually exclusive alternative choices, sequential UI steps, itemized lists, sequential form fields, alternative purposes, or grouped display attributes. (2) Do not invent implicit error-handling branches, validation loops, or recovery paths unless they are explicitly described in the requirement. (3) Do not compress multiple explicitly stated actions into a single abstract node. (4) Do not decompose high-level goals into assumed sub-steps (e.g., inferring 'select file', 'play audio' from 'identify whales') unless those sub-steps are explicitly stated in the text. (5) Do not generate empty or trivial 'else' branches (e.g., containing 'perform no function' or 'do nothing'); if an 'else' condition has no explicit action in the requirement, the branch must be omitted entirely. (6) Restrict the use of 'stop' to true process termination explicitly stated in the requirement (e.g., system shutdown, end of lifecycle); do not use 'stop' as a substitute for proper flow merging (e.g., closing an `endif`, `endswitch`, or `endfork`).
```
