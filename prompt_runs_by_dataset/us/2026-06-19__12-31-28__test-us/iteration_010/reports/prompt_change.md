# Iteration 010 Prompt Change

- accepted: False
- acceptance_mode: rejected
- rejection_reasons: standard_safety_gate, has_required_metric_benefit, bootstrap_gate
- chars_before: 3660
- chars_after: 3660
- chars_candidate: 4413

## Applied Change

```diff
# no applied prompt change
```

## Rejected Candidate Diff

```diff
--- prompt_before.md
+++ prompt_candidate.md
@@ -12,17 +12,18 @@
 
 ## workflow
 
-Step 1: Extract activities strictly from explicit actions in the requirement, grouping lists of attributes, parameters, or properties into a single descriptive activity node *unless* they describe independent data entry fields (e.g., 'enter name, description, and keywords') or simultaneous system state attributes, in which case decompose them into separate activity nodes. Grouping is retained only for sequential UI steps, configuration options, or sequentially dependent steps. Additionally, decompose compound steps into separate activities if they are joined by explicit concurrency cues (e.g., 'simultaneously', 'in parallel') or represent simultaneous system behaviors (e.g., 'Close window and display statistics').
+Step 1: Extract activities strictly from explicit actions in the requirement. Every distinct explicit action verb or state transition stated in the requirement must map to a distinct activity node; prohibit collapsing multiple explicitly stated sequential actions into a single abstract node. Group lists of attributes, parameters, properties, sequential UI steps, configuration options, or alternative options into a single descriptive activity node. Only decompose compound steps into separate activities if they are joined by explicit concurrency cues (e.g., 'simultaneously', 'in parallel', 'concurrently'); all other lists must be grouped into a single activity node.
 Step 2: Decompose any identified concurrent compound steps into separate activities before constructing control-flow.
 Step 3: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks.
 Step 4: Review the requirement for implicit conditional state transitions (e.g., 'upon [event]', 'when [state]', 'triggers') and map them to if/switch structures with distinct activities, rather than representing them as sequential flows.
 
 ## knowledge
 
-- Concurrency modeling: Comma-separated lists or 'and'-joined clauses must be decomposed into fork/join blocks when accompanied by explicit concurrency cues, when describing simultaneous system behaviors, or when representing independent data entry fields and simultaneous system state attributes. Strictly exclude applying fork/join to alternative options (e.g., 'either/or', 'options include'), sequential sub-steps, or conditionally executed branches; these must remain single activity nodes or sequential flows.
+- Concurrency modeling: Fork/join blocks are strictly reserved for actions linked by explicit concurrency cues (e.g., 'simultaneously', 'in parallel', 'concurrently', 'at the same time', 'while [Action A], [Action B]'). Common false-positive triggers that must NOT be modeled as fork/join include: sequential UI steps (e.g., 'fill in name, then email'), form field listings, configuration parameters, and alternative options (e.g., 'either/or', 'options include'). These must be represented as a single activity node or sequential flow. Strictly exclude applying fork/join to conditionally executed branches; these must remain single activity nodes or sequential flows.
 - Loop modeling: Distinguish between a 'while' wait condition (e.g., waiting for a timeout or external event), which should be modeled as an if/else branch that stalls the flow, and a 'repeat' loop (e.g., 'continuously', 'periodically', 'retry'), which wraps the iterative actions. Map iterative cues to repeat/while loops, ensuring the loop boundary strictly encloses only the actions explicitly described as repeating, excluding non-iterative setup or teardown steps.
 
 ## rule
 
-- Granularity rule: Do not infer implicit system interactions, UI responses, error-handling, validation, or 'No' branches unless explicitly stated in the text; factual statements or unconditional behaviors must not be gated by artificial decision nodes. Do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement.
-- Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. Nested conditional logic (e.g., an 'if' within an 'if') must be modeled as nested switch/if structures, not flattened into independent sequential checks. 'Else' or default paths must rejoin the main flow strictly after all conditional branches for that specific decision have concluded, avoiding improper merging into unrelated parallel branches.
+- Granularity rule: Do not infer implicit system interactions, UI responses, error-handling, validation, prerequisite actions, intermediate UI interactions, system responses, or 'No' branches unless explicitly stated as actions in the text; factual statements or unconditional behaviors must not be gated by artificial decision nodes. Do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement.
+- Conditional mapping rule: Explicit textual conditional cues (e.g., 'if... then... else if... else') must be mapped directly to nested if/elseif/else PlantUML structures. Prohibit flattening nested conditional logic into sequential checks or dropping alternative paths.
+- Alternative path convergence rule: Prohibit creating sequential control-flow edges between activities that represent mutually exclusive alternative options or independent outcomes. Alternative branches must not be wired sequentially into the main flow, but must converge strictly via their conditional merge points. All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. Nested conditional logic (e.g., an 'if' within an 'if') must be modeled as nested switch/if structures, not flattened into independent sequential checks. 'Else' or default paths must rejoin the main flow strictly after all conditional branches for that specific decision have concluded, avoiding improper merging into unrelated parallel branches.
```
