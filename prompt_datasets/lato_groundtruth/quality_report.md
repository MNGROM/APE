# LATO Groundtruth Quality Check

Check target: `ape/prompt_datasets/lato`

Groundtruth field: `plantuml`

Extraction output: `ape/prompt_datasets/lato_groundtruth`

Machine-readable report: `ape/prompt_datasets/lato_groundtruth/compile_report.json`

Manifest: `ape/prompt_datasets/lato_groundtruth/manifest.jsonl`

Compiler command: `java -Djava.awt.headless=true -jar plantuml-1.2025.4.jar -syntax`

Note: compile validation adds `@startuml` / `@enduml` wrappers in memory for records that omit them, matching the APE evaluation helper behavior.

## Summary

- Total JSONL records: 542
- Invalid JSON records: 0
- Records missing `content` or `plantuml`: 0
- PlantUML compile passed: 542
- PlantUML compile failed: 0
- Compile pass rate: 100.000%
- Records with explicit wrappers: 116
- Records missing wrappers: 426
- Duplicate `content` groups: 1
- Duplicate `plantuml` groups: 1

## Per-Dataset Compile Result

- `bp`: 30 passed, 0 failed, 30 total
- `fsd`: 116 passed, 0 failed, 116 total
- `lmc`: 56 passed, 0 failed, 56 total
- `pure`: 100 passed, 0 failed, 100 total
- `rac`: 20 passed, 0 failed, 20 total
- `us`: 220 passed, 0 failed, 220 total

## Fixed Compile Failures

- Fixed 14 previously failing records: `bp-0003`, `fsd-0052`, `fsd-0054`, `fsd-0064`, `fsd-0069`, `fsd-0073`, `fsd-0074`, `fsd-0090`, `us-0033`, `us-0069`, `us-0082`, `us-0131`, `us-0137`, `us-0212`.
- Fixes were limited to PlantUML syntax: missing semicolons, full-width semicolons, malformed `if` branches, and unclosed or malformed `fork` / `split` blocks.

## Remaining Quality Notes

- The dataset is structurally healthy as JSONL: every line parses and every record has both required fields.
- All groundtruth PlantUML records now pass the local syntax compiler under the APE wrapper-normalized evaluation path.
- Wrapper style remains inconsistent across subsets. `fsd` includes explicit wrappers; most other subsets rely on downstream wrapper normalization.
- Duplicate records remain unchanged because they are semantic/data-curation questions rather than syntax errors.
