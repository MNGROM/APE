# Iteration 009 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 5232
- chars_after: 6461
- chars_candidate: 6461

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -14,13 +14,13 @@
 
 Step 1: Extract a complete and granular, exhaustive list of discrete activities explicitly stated in the text, mapping them 1-to-1 to activity nodes. Extract only activities explicitly stated as actions in the text. A single stated action must remain a single node, and multiple distinct actions must remain distinct nodes, prohibiting both decomposition into assumed sub-steps and compression of multiple actions into one.
 Step 2: Identify iterative or repetitive behaviors triggered by textual cues (e.g., 'repeat', 'every', 'until', 'while') and structural elements such as distinct actors or systems. Map these iterative cues to `repeat`/`while` constructs and distinct actors/systems to `partition` blocks.
-Step 3: Construct the control flow strictly among these extracted nodes, using the text's explicit sequencing and conditional logic, without adding or merging nodes. Identify explicit linguistic cues (e.g., 'simultaneously', 'at the same time', 'concurrently') for simultaneous execution, and construct parallel flows using `fork`/`join` for those cases. Grammatical lists of items, attributes, or options must NOT be interpreted as concurrent flows UNLESS the listed items represent independent actions that can occur without depending on each other's completion; when a list contains such independent actions, model them using `fork`/`join`. Lists of static attributes, alternative choices, or sequential UI steps must remain sequential or `if`/`else` branches.
+Step 3: Construct the control flow strictly among these extracted nodes, using the text's explicit sequencing and conditional logic, without adding or merging nodes. Identify explicit linguistic cues (e.g., 'simultaneously', 'at the same time', 'concurrently', 'in parallel') for simultaneous execution, and construct parallel flows using `fork`/`join` ONLY when such explicit concurrency cues are present. Grammatical lists of items, attributes, options, or alternative choices must NEVER be modeled with `fork`/`join`, even if they seem independent; they must instead be represented as sequential activities or `if`/`else` branches. Additionally, identify nested preconditions, state-dependent guards, and mutually exclusive conditions. Map these strictly to nested `if`/`elseif`/`else` or `switch`/`endswitch` structures, preserving the exact hierarchical logic. Add conditional guard labels to transitions exactly as stated in the text, and do not flatten nested conditions into a single level.
 
 ## knowledge
 
 - Map iterative keywords (e.g., 'repeat', 'until', 'while') to PlantUML `repeat`/`while` loop constructs rather than linearized sequences. When distinct actors or systems are mentioned, their actions should be enclosed in `partition` blocks named after the actor/system to preserve behavioral boundaries.
-- Distinguish sequential actions from concurrent flows: `fork`/`join` must be used when the text explicitly states simultaneous execution OR when enumerations or lists contain independent actions that can execute without mutual dependency. Lists of static attributes, alternative options, and sequential steps must not be modeled with `fork`/`join`. Mutually exclusive alternatives must be modeled as sequential activities or `if`/`else` branches.
-- Map nested conditional logic: use `switch`/`endswitch` constructs when the requirement evaluates a single variable or entity against multiple distinct, discrete values (e.g., 'depending on [state]', 'based on [type]'). Use `if`/`elseif`/`else` constructs for boolean or overlapping conditions, preserving the exact nesting and topological structure without flattening. When the requirement specifies an early termination or exit from a branch, model it using a `stop` node within that branch rather than forcing the flow to merge back.
+- Distinguish sequential actions from concurrent flows: `fork`/`join` must strictly be used ONLY when the text contains explicit concurrency cues (e.g., 'simultaneously', 'concurrently', 'in parallel'). Alternative choices, grouped attributes, and sequential UI steps are mutually exclusive or sequential and must not be modeled with `fork`/`join`.
+- Map nested conditional logic: use `switch`/`endswitch` constructs when the requirement evaluates a single variable or entity against multiple distinct, discrete values (e.g., 'depending on [state]', 'based on [type]'). Use `if`/`elseif`/`else` constructs for boolean or overlapping conditions, preserving the exact nesting and topological structure without flattening. Map nested preconditions and state-dependent guards to nested `if`/`elseif`/`else` or `switch`/`endswitch` constructs. Ensure that guard labels on transitions reflect the exact condition text. Mutually exclusive alternatives must be modeled as separate branches within these conditional constructs, not as parallel flows. When the requirement specifies an early termination or exit from a branch, model it using a `stop` node within that branch rather than forcing the flow to merge back.
 
 ## rule
 
@@ -31,3 +31,6 @@
 - Preserve all alternative paths, error checks, and specific conditional outcomes explicitly stated in the text; do not drop these activities in favor of only representing the main success path.
 - When distinct actors or systems are mentioned in the requirement, their corresponding activities must be grouped into `partition` blocks; do not omit these structural boundaries.
 - Do not add explicit `else`/`stop` branches for conditions where the requirement does not specify an alternative terminating action; if an `if`-branch represents a conditional step that does not alter the main flow upon failure, the flow must implicitly continue or merge, rather than terminating with a `stop`.
+- Do not model alternative choices, mutually exclusive options, or grouped attributes as parallel flows using `fork`/`join`. Mutually exclusive alternatives must always be modeled using `if`/`else` or `switch`/`endswitch` branches.
+- Do not collapse explicitly stated system responses, intermediate states, or distinct behavioral steps into a single abstract activity node. Each explicitly stated action or reaction must be preserved as a distinct activity node.
+- Do not force sequential dependencies between actions that the text does not explicitly link in a sequence. Do not misroute mutually exclusive branches so that they converge prematurely or connect to incorrect subsequent steps; maintain the exact branching and merging structure implied by the requirement.
```
