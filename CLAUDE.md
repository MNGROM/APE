# APE Workspace Rules

## Supported workflow

APE 只支持当前 `taxonomy-v3` selector-v4 工作流：

```text
generation and evaluation
-> batch failure analysis
-> taxonomy-blind error selector
-> exact prior-attempt filtering on the same base Prompt and finding keys
-> bounded ordered candidate attempts on one base Prompt
-> Prompt-gap localization
-> Prompt editor
-> Prompt rewriter
-> deterministic single-section apply
-> paired repeated validation
-> application policy
-> heldout audit only after a Prompt change
```

`taxonomy-v3` 只是当前 CLI 中保留的历史名称，不代表候选链路使用 taxonomy。
不得重新引入 atomic attribution、mechanism taxonomy、repair catalog、epoch planner、
`simple-v1` 或 `taxonomy-v3-legacy`。

## Directory contract

- `analysis/`：当前 selector-v4 的失败分析、分组、候选 agent 和 registry。
- `ape_datasets/`：数据加载、采样和 split 辅助逻辑。
- `prompt_workspace/`：当前运行使用的 seed Prompt 和五个 agent Prompt；不保存旧版本。
- `tests/`：当前支持行为的单元测试和流程测试；不保留已删除兼容流程的测试。
- `scripts/`：仍可运行的离线诊断或实验启动脚本。
- `docs/`：当前架构、执行边界和交接说明；Git 历史负责保存过时设计。
- `tools/prompt_snapshots/`：仅保存经用户明确要求的活跃 Prompt 精确回滚快照；文件名使用
  `YYYY-MM-DD__<prompt-component>__<reason>.md`，不得由运行流程读取或覆盖当前 Prompt。
- `prompt_runs/`、`prompt_runs_by_dataset/`、`baseline_predictions/`：实验产物，只读保留。
- `tools/`：项目内工具资产。

根目录只放入口、共享运行模块、项目配置和 README。Python 临时文件、缓存、构建产物
和日志由 `.gitignore` 排除，不得提交。

## Naming and ownership

- Python 模块和函数使用 `snake_case`，类型使用 `PascalCase`。
- Prompt 文件使用职责名；只有真实并行支持多个 schema 时才使用版本后缀。
- Python 拥有 ID、hash、计数、排序、去重、聚合和最终确定性决策。
- Agent 只负责其阶段明确需要的语义判断或文本生成。
- Rewriter 拥有最终 `rule_text` 措辞；Python 只能校验 canonical contract 并确定性应用，
  不得补写或追加语义文本。
- 每个 schema 字段都必须被 validator、聚合器或审计产物实际消费。

## Experiment boundaries

- heldout 不得参与候选发现、排序、修改、阈值校准或 acceptance gate。
- 同一 epoch 的 candidate attempts 必须使用同一个 base Prompt，不能串行叠加。
- 同一 epoch 最多应用一个 candidate，validation baseline 只生成一次并复用。
- semantic finding group 必须通过 LLM Node F1 或 Relation F1 的 repeated validation gate。
  `syntax_error` 与 `compile_error` 属于同一个 diagnostic evidence family，可以同组，并统一
  使用包装后 PlantUML JAR 检查产生的 `plantuml_compilation_pass_rate` 作为直接 acceptance
  指标；diagnostic group 还必须满足语义 F1 的 non-regression safety check，不能仅凭无关的
  语义波动被接受。`syntax_pass_rate` 只保留为诊断指标，不参与 acceptance。
- 只有相同 base Prompt、相同 finding keys 且已确认 `no_prompt_gap` 的 group 可以过滤；
  不得使用 summary、embedding 或模糊语义匹配跳过新证据。
- 重复 `already_covered` 只能通过现有 `ambiguous + replace_existing` 合同收紧原指导，
  不得追加重复规则。
- `already_covered` 必须由唯一现有原文同时覆盖代表证据的 input-side trigger、目标结构修复
  和 preservation boundary；主题相关但指导不足时使用 `ambiguous + replace_existing`，不得
  以“已有指导覆盖”为理由返回 `no_prompt_gap`。
- Prompt hash 未变化时不得运行 heldout generation 或 judge。
- 未经用户明确同意，不得调用真实模型、运行训练、validation calibration 或 heldout。
- 不得修改或删除现有实验日志和 run 产物。

## Change discipline

- 修改前先确认本文件和 `docs/APE_NEXT_MODIFICATION_GUARDRAILS.md`。
- 大范围修改先给出计划并等待确认。
- 删除文件、修改敏感配置、CI/CD、数据库、Git 历史、执行 push/rebase/publish 前必须确认。
- 不使用跳过测试、删除断言或隐藏异常的方式让验证通过。
- 修改后至少运行：

```powershell
py -m unittest discover -s tests -q
py -m compileall analysis tests run.py
git diff --check
```

- 涉及 CLI 或 orchestration 时，额外运行不调用真实模型的 mock smoke test。
