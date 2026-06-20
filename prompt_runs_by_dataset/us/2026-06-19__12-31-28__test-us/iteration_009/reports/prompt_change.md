# Iteration 009 Prompt Change

- accepted: True
- acceptance_mode: standard
- rejection_reasons: none
- chars_before: 2463
- chars_after: 3660
- chars_candidate: 3660

## Applied Change

```diff
--- prompt_before.md
+++ prompt_after.md
@@ -12,16 +12,17 @@
 
 ## workflow
 
-Step 1: Extract activities strictly from explicit actions in the requirement, grouping lists of attributes, parameters, or properties into a single descriptive activity node *unless* they are joined by explicit concurrency cues (e.g., 'simultaneously', 'in parallel') or represent simultaneous system behaviors (e.g., 'Close window and display statistics'). In those specific cases, decompose the compound step into separate activities for parallel branching.
+Step 1: Extract activities strictly from explicit actions in the requirement, grouping lists of attributes, parameters, or properties into a single descriptive activity node *unless* they describe independent data entry fields (e.g., 'enter name, description, and keywords') or simultaneous system state attributes, in which case decompose them into separate activity nodes. Grouping is retained only for sequential UI steps, configuration options, or sequentially dependent steps. Additionally, decompose compound steps into separate activities if they are joined by explicit concurrency cues (e.g., 'simultaneously', 'in parallel') or represent simultaneous system behaviors (e.g., 'Close window and display statistics').
 Step 2: Decompose any identified concurrent compound steps into separate activities before constructing control-flow.
 Step 3: Construct control-flow by connecting the extracted activities, mapping mutually exclusive conditions to switch/if/elseif structures and explicit concurrency keywords to fork/join blocks.
+Step 4: Review the requirement for implicit conditional state transitions (e.g., 'upon [event]', 'when [state]', 'triggers') and map them to if/switch structures with distinct activities, rather than representing them as sequential flows.
 
 ## knowledge
 
-- Concurrency modeling: Comma-separated lists or 'and'-joined clauses must be decomposed into fork/join blocks *only* when accompanied by explicit concurrency cues or when describing simultaneous system behaviors (e.g., 'Close window and display statistics'). Explicitly exclude comma-separated lists that represent sequential UI steps, configuration options, or sequentially dependent steps in multi-threaded contexts from fork/join usage; these must remain single activity nodes or sequential flows.
-- Loop modeling: Map iterative cues (e.g., 'repeat', 'retry', 'periodically', 'cyclically') to repeat/while loops, ensuring the loop boundary strictly wraps only the iterative portion and does not enclose non-iterative parallel blocks.
+- Concurrency modeling: Comma-separated lists or 'and'-joined clauses must be decomposed into fork/join blocks when accompanied by explicit concurrency cues, when describing simultaneous system behaviors, or when representing independent data entry fields and simultaneous system state attributes. Strictly exclude applying fork/join to alternative options (e.g., 'either/or', 'options include'), sequential sub-steps, or conditionally executed branches; these must remain single activity nodes or sequential flows.
+- Loop modeling: Distinguish between a 'while' wait condition (e.g., waiting for a timeout or external event), which should be modeled as an if/else branch that stalls the flow, and a 'repeat' loop (e.g., 'continuously', 'periodically', 'retry'), which wraps the iterative actions. Map iterative cues to repeat/while loops, ensuring the loop boundary strictly encloses only the actions explicitly described as repeating, excluding non-iterative setup or teardown steps.
 
 ## rule
 
-- Granularity rule: Do not infer implicit system interactions or UI responses unless explicitly stated in the text; do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement.
-- Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. Instead, conditional paths must merge.
+- Granularity rule: Do not infer implicit system interactions, UI responses, error-handling, validation, or 'No' branches unless explicitly stated in the text; factual statements or unconditional behaviors must not be gated by artificial decision nodes. Do not collapse multiple distinct specified actions into one broad node, especially if they represent simultaneous actions or concurrent behaviors explicitly described in the requirement.
+- Convergence rule: All fork/join branches and switch/case paths must merge before reaching a stop node; 'stop' nodes must not be placed inside conditional branches unless the requirement explicitly states an immediate process termination for that specific branch. Nested conditional logic (e.g., an 'if' within an 'if') must be modeled as nested switch/if structures, not flattened into independent sequential checks. 'Else' or default paths must rejoin the main flow strictly after all conditional branches for that specific decision have concluded, avoiding improper merging into unrelated parallel branches.
```
