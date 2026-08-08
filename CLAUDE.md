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
-> paired repeated source-case behavior contract
-> paired repeated gate1
-> optional fresh paired repeated gate2 only when explicitly enabled
-> application policy
-> heldout audit only after a Prompt change
```

`taxonomy-v3` 只是当前 CLI 中保留的历史名称，不代表候选链路使用 taxonomy。
不得重新引入 atomic attribution、mechanism taxonomy、repair catalog、epoch planner、
`simple-v1` 或 `taxonomy-v3-legacy`。

## Directory contract

- `analysis/`：当前 selector-v4 的失败分析、分组、候选 agent 和 registry。
- `ape_datasets/`：数据加载、采样和 split 辅助逻辑。
- `prompt_workspace/`：当前运行使用的 seed Prompt 和五个 agent Prompt；不保存旧版本。任何
  Prompt 文本修改都必须先提交精确 diff 并获得用户明确审核批准，不能与普通代码修改一并落盘。
- `tests/`：当前支持行为的单元测试和流程测试；不保留已删除兼容流程的测试。
- `scripts/`：仍可运行的离线诊断或实验启动脚本。
- `utils/`：共享文件、限流和 Prompt hash 辅助模块；跨平台 Prompt identity 必须复用这里的实现。
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
  不得补写或追加语义文本。`rule_text` 最多两句；Editor 的 positive trigger 必须保留
  Localization 的 `shared_repair.input_trigger` 与 `structural_operation`，negative boundary
  必须保留 `preservation_boundary`。
- 每个 schema 字段都必须被 validator、聚合器或审计产物实际消费。

source-case behavior contract 由 Python 拥有。它从 validated selected findings 编译精确
obligation，并只把 Localization `shared_repair` 作为可审计的范围文本。Python 不得声称能从
free-text trigger 分类任意输入，也不得声称验证了 selected node、relation 或 compile anchor
没有表达的结构行为。

## Experiment boundaries

- 正式实验默认直接使用 `py run.py` 启动。除非用户主动明确要求使用 PowerShell
  调度脚本，否则不得以 `scripts/*.ps1` 作为实验入口；`.ps1` 仅用于用户明确指定的
  批量调度、跨数据集编排或状态监控场景。使用 `run.py` 时必须在命令中显式写出本次
  实验所需的 provider、模型角色、Gate、采样、重复次数和 application mode 参数，不能
  依赖 `.ps1` 的隐含默认值。

- APE 支持 `zhipu` 与 `deepseek` 两种 OpenAI-compatible provider。provider 优先由
  `APE_LLM_PROVIDER` 显式选择；未设置时仅在只有一个 provider API key 的情况下确定性推导。凭据只能从
  provider 对应环境变量或显式 CLI 参数读取，且 `run_args.json` 只能记录 `*_present`。
- DeepSeek 请求必须使用其当前 Chat Completion 合同：保留 `temperature=0` 和显式
  `thinking.type=disabled`，但不得发送未在 DeepSeek OpenAI API schema 中定义的
  `do_sample`。Zhipu 继续显式发送 `do_sample=false`。
- 所有真实模型调用的 temperature 必须严格为 `0`，包括 generation、failure analysis、
  selector、localization、editor/rewriter、LLM Judge 和 element extraction。CLI 默认值必须为
  `0`，任何非零 temperature 配置必须在模型调用前直接拒绝；历史 run 中的非零配置只保留
  作审计，不得复制到新实验或 replay。
- heldout 不得参与候选发现、排序、修改、阈值校准或 acceptance gate。
- `--heldout-repeats` 只控制 heldout 审计的重复次数，默认 `1`。每个 initial 或 applied
  Prompt 必须在同一组 heldout cases 上完成全部 repeats，并保留逐次 summary 与聚合均值；
  repeats 不得进入 candidate discovery、排序、Gate、application 或 Prompt 修改。
- 同一 epoch 的 candidate attempts 必须使用同一个 base Prompt，不能串行叠加。
- 每个合法且非重复 candidate 必须先通过 paired repeated source-case behavior contract，才可进入
  gate1。replay cases 必须从 selected group members 的完整 requirement 和 ground truth 精确重建；
  它们仍属于 discovery evidence，只证明 candidate 修复声明的 anchors 且未在这些 cases 上引入
  无关 element errors，不得计入 Gate 或 transfer evidence。
- behavior contract 将 `missing_node/extra_node/missing_relation/extra_relation` 映射为 LLM Judge
  matching 中精确的 `FN -> TP` 或 `FP -> absent` obligation，并将 compile/syntax finding 映射为
  `compile fail -> pass`。每个 paired replay 中新增的无关 node/relation `FN` 或 `FP` 都是
  preservation violation。缺少 measurement 是 `inconclusive`；全部 repeats 修复且无 violation
  才是 `proven`；全部 repeats 未修复或均出现 violation 是 `violated`；repeat 分歧是
  `inconclusive`。不得选择最好 repeat，也不使用多数票或 min-wins。
- 只有 `behavior_contract.status=proven` 的 candidate 可以进入 gate1 或被任何 application mode
  应用；`diagnostic-apply` 不得绕过该 eligibility contract。source replay baseline 只允许在相同
  base Prompt 和完全相同 replay split fingerprint 下复用。
- 同一 epoch 最多应用一个 candidate。gate1 baseline 在同一 epoch 内只生成一次并复用；显式
  启用 gate2 时，其 baseline/candidate 必须为每个通过 gate1 的 candidate fresh evaluation，
  不得跨 candidate 复用。
- 正式默认流程只使用一个固定、分层的 30-case gate1，并从 candidate discovery training cases
  中排除。gate1 通过后 `cumulative` 才能应用 candidate。`--gate2` 只用于显式兼容或复现实验；
  启用时 gate2 必须与 gate1、heldout 互不重叠，且只有两关都通过才能应用。
- Python 必须从 validated selected group 的 `anchor_kind` 确定 required metrics：
  `missing_node/extra_node` 使用 `llm_node_f1`，`missing_relation/extra_relation` 使用
  `llm_relation_f1`，同时包含 node 和 relation findings 的 semantic group 必须同时使用两项，
  `syntax_error/compile_error` 使用 `plantuml_compilation_pass_rate`。每个已启用 Gate 中的每个
  required metric 必须同时满足 pooled repeated mean delta、全部 eligible source dataset 等权平均
  delta（正式 LODO run 为五个 source dataset）和按采样前 source population 加权平均 delta 严格
  大于 `0`；不相关指标只作诊断，不能代偿。
  不设置 `min_delta`、`min_wins`、regression floor 或“允许回退多少”的人工阈值。缺少任一
  required metric 的完整 measurement 时 evaluation invalid。`syntax_error` 与
  `compile_error` 属于同一个 compile evidence family，可以同组，并统一使用包装后 PlantUML
  JAR 检查产生的 compilation 指标；`syntax_pass_rate` 只保留为诊断指标，不参与 acceptance。
- 新 run 的 split summary 必须分别记录：排除 heldout 后且均衡采样前的
  `source_dataset_counts`、均衡采样后的 `train_pool_dataset_counts`，以及排除 Gate 后实际用于
  discovery 的 `train_dataset_counts`。Gate weighted acceptance 只能使用
  `source_dataset_counts`；缺失 source count 或任一 source dataset 的 required measurement 时
  evaluation invalid，不得补零或改用 Gate 后 count。
- 该无阈值 acceptance policy 是当前用户明确指定的项目契约。除非用户主动明确要求，后续
  不得重新添加最小提升、最小 wins、semantic/compile floor 或其他等价的回退阈值。
- Gate2 默认关闭，只有显式 `--gate2` 才启用。`auto` application mode 无论 Gate2 是否启用都
  解析为 `cumulative`；单 Gate 正式流程仍必须遵守 gate1 metric decision。旧诊断应用语义只能
  通过 `--candidate-application-mode diagnostic-apply --no-gate2` 显式进入。
- `--stop-after-first-apply` 是正式 paired run 的可选因果隔离开关。启用后，APE 在首个
  applied candidate 对应的 heldout audit 或 skip manifest 完成后结束后续 epoch；若没有
  candidate 应用，则仍完成配置的全部 iterations。该开关不得提前跳过已启用的 Gate2、任一
  heldout repeat 或 heldout 调度。
- 跨 run 的来源-受益分析只能读取既有 `candidate_registry.json`、split、Gate 和 heldout
  产物。新 run 写入 Gate decision 的 required-metric balanced/source-population-weighted delta
  属于正式 acceptance evidence；分析器对历史 run 事后派生的宏平均、weighted 平均、逐数据集
  delta、规范化 PlantUML 文本变化率和 heldout cumulative/incremental delta 仍为 report-only，
  不得回写历史 run 或覆盖原 `accepted`。历史 run 缺少 `source_dataset_counts` 时只能回退使用
  `train_dataset_counts` 并标记 `weight_basis=historical_train_pool`；缺失 paired measurement 必须
  标记 unavailable，不能补成 `0`。
- Localization 必须接收 frozen group 的全部成员证据，并以 `prompt-gap-localization-v2`
  对每个 `finding_id` 恰好返回一次 compatibility check。`localized` 和 `already_covered` 只允许
  coherent group，且必须给出非空 input trigger、structural operation 和 preservation boundary；
  incoherent group 必须返回 `no_prompt_gap`，由 Python 记录为 `group_incoherent`，并跳过 Editor、
  Rewriter、Gate 和 heldout 后继续下一 group。
- 只有相同 base Prompt、相同 finding keys 且已确认 `no_prompt_gap` 或 `group_incoherent` 的
  group 可以过滤；
  不得使用 summary、embedding 或模糊语义匹配跳过新证据。
- 重复 `already_covered` 只能通过现有 `ambiguous + replace_existing` 合同收紧原指导，
  不得追加重复规则。
- `already_covered` 必须由唯一现有原文同时覆盖代表证据的 input-side trigger、目标结构修复
  和 preservation boundary；主题相关但指导不足时使用 `ambiguous + replace_existing`，不得
  以“已有指导覆盖”为理由返回 `no_prompt_gap`。
- Prompt hash 未变化时不得运行 heldout generation 或 judge。
- 未经用户明确同意，不得调用真实模型、运行训练、validation calibration 或 heldout。
- 未经用户逐次审核批准，不得修改 `prompt_workspace/*.md`；可以先提供拟议 diff，但不能落盘。
- Localization Prompt 已同步到严格 v2 contract；后续 Prompt 修改仍必须先提交精确 diff 并获得
  用户逐次审核。当前 workflow 可在离线验证通过且另行获得真实 API 授权后运行。
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
