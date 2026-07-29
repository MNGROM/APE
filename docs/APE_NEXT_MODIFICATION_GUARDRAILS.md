# APE 修改目标与执行边界

本文档约束当前 APE selector-v4 实现。过时 handoff、旧 implementation 文档和 Git
历史只用于理解既有实验，不定义当前行为。

## 1. 最终目标

在不使用 heldout 选择候选或调参的前提下，提高 APE 接受的 Prompt 更新在 heldout
Node F1 或 Relation F1 上获得稳定泛化收益的概率。

稳定收益应通过固定 validation split 上的 paired repeats、win count、平均 delta 和波动
范围解释，不能主要依赖单次 generation 或 judge 波动。

## 2. 唯一支持的工作流

```text
generation + syntax/compiler + LLM element judge
-> Python numeric findings
-> batch failure analysis
-> Python exact validation
-> taxonomy-blind error selector
-> ordered bounded candidate attempts on one frozen base Prompt
-> taxonomy-free Prompt-gap localization
-> Prompt editor
-> Prompt rewriter
-> deterministic single-section candidate assembly
-> paired repeated validation
-> application policy
-> heldout only when the applied Prompt hash changes
```

`taxonomy-v3` 是保留的 CLI policy 名称，当前链路不加载 taxonomy 或 repair catalog。
以下流程和资产不再受支持：

- `simple-v1`；
- `taxonomy-v3-legacy`；
- atomic attribution 和 mechanism clustering/memory；
- taxonomy mapping、repair catalog eligibility 和 taxonomy ID；
- supporting-batch localization voting 和 epoch planner；
- legacy single-run Safety/Benefit/Bootstrap acceptance gate。

## 3. 当前数据契约

### Failure Analysis

输入是 Python 生成的 numeric findings。Agent 输出 `failure-errors-v2`，每项只引用一个
现有 `finding_id`，并返回 status、exact requirement quote、error summary 和 causal
rationale。Python 校验 ID、quote、anchor/matching quality、secondary linkage、重复分类和
generic diagnostics。

### Error Selector

Selector 接收当前 epoch 全部 validated actionable primary errors，不接收 Prompt、taxonomy
或 validation metrics。它必须完整且不重复地划分所有 finding，并按 candidate 尝试优先级
返回 groups；`selected_group_id` 指向第一组。Python 推导 canonical group ID 和支持统计。

### Candidate attempts

同一 epoch 按 Selector 顺序最多尝试 `max_candidate_attempts_per_epoch` 个 group。所有
candidate 相对同一个 base Prompt 独立生成。遇到 ineligible、`no_prompt_gap`、
`already_covered`、无效或重复 candidate、validation rejection 时继续下一组；第一个满足
application policy 的 candidate 结束本 epoch。

Candidate registry 记录每个实际尝试 group 的精确 finding-key signature 和终止结果。只有
相同 base Prompt、相同 finding keys 且此前已确认 `no_prompt_gap` 的 group 可以在 attempt
截断前过滤；不得用 summary 文本、embedding 或模糊语义匹配跳过新证据。重复
`already_covered` 不直接过滤，而是把同 Prompt recurrence 交给 Localization 判断已有指导
是否过于抽象；如能安全收紧，只能使用现有 `ambiguous + replace_existing` 合同。

### Localization, Editor and Rewriter

Localization 对冻结 group 先验证一条安全规则能否覆盖全组，再返回 `localized`、
`already_covered` 或 `no_prompt_gap`。只允许 `append_new`、`replace_existing`、`none`。
Selector 只有在全组成员需要同一种结构修复且保留相同边界时才能合并；原因主题相似但需要
删除、移动或改变不同结构的 findings 必须拆分，不确定时使用 singleton group。

`already_covered` 必须由一段唯一现有原文同时覆盖每个代表样本的 input-side trigger、目标
结构修复和 preservation boundary；仅使用相同术语或讨论相关主题不构成覆盖。相关原文若
触发条件或结构操作仍然间接、缺失或允许当前错误，应使用现有
`ambiguous + replace_existing` 合同收紧，而不是追加重叠规则。现有指导确实覆盖时只能返回
`already_covered`，不得返回 `no_prompt_gap`；`no_prompt_gap` 只表示组内修复冲突、预测有效、
证据不足或 judge/generation limitation。

Editor 只返回 intent、positive trigger、negative boundary 和 change instruction。trigger 和
boundary 必须是 input-side generation language，不得依赖 prediction、gold、evaluator、
dataset 或 metric。

Rewriter 只返回 `rule_text` 并拥有最终规则措辞。Python 只按忽略大小写、标点和空格差异的
canonical contract 做校验，再确定性修改一个 section；不得向 Rewriter 文本追加或注入语义
片段，非目标 section 必须字节一致。

### Validation and application

结构合法性、validation 是否执行、measurement 是否有效、metric decision 和是否应用必须
分开记录。支持三种 application mode：

- `diagnostic-apply`：candidate 合法且 measurement 有效即应用；metric decision 只记录。
- `cumulative`：只有 paired validation metric decision accepted 才应用。
- `isolated`：只评估 candidate，不修改 work Prompt。

默认 `auto` 解析为 `diagnostic-apply`。`any-improvement` 要求至少一个语义指标满足配置的
平均 delta 和最小 wins；Compile 和 Syntax 只作诊断，不能单独接受 candidate。

## 4. Heldout 和真实实验红线

- heldout 不参与 finding、grouping、candidate、阈值或 acceptance 决策。
- `--eval-initial-test` 只生成 iteration-0 baseline；它是无值开关。
- `isolated` 不得与 `--eval-initial-test` 同时使用。
- Prompt 未变化时只写 skip manifest，不调用 heldout generation 或 judge。
- 未经用户明确同意，不运行真实模型、训练、calibration、在线 smoke 或 heldout。
- 到达 experiment-ready 检查点时停止，向用户提供命令、目的、产物和判据。

## 5. 允许的自主修改

在已确认目标内，可以修改：

- 当前阶段内部的 Python 实现、validator、聚合和确定性排序；
- 被当前 validator 或报告消费的紧凑 schema；
- 当前五个 agent Prompt 的职责和边界；
- 审计字段、拒绝原因、单元测试、mock 流程测试和历史 run 的只读分析；
- 不改变 split、heldout 或 application 语义的向后兼容 CLI 调整。

以下属于 workflow 大改，必须先计划并获得确认：

- 新增、删除、合并或重排 agent 阶段；
- 增加 critic、reviewer、debate、self-consistency 或额外真实模型调用；
- 改为并行候选、validation 后择优或单 epoch 多次应用；
- 改变 validation/heldout 数据边界、调用时机或 candidate selection 职责；
- 显著改变 API 调用数量、并发或成本模型。

## 6. Schema 和 Prompt 复杂度边界

- 只保留当前 validator、聚合器或审计产物消费的字段。
- Agent 不得返回 Python 可计算的 ID、count、rank、hash 或 canonical metadata。
- 优先扁平字段和短列表；能够推导的信息不重复保存。
- Prompt 修改优先替换和收紧，追加次之；正向 trigger 和负向 boundary 紧邻表达。
- 不在多个 Prompt 中复制相同完整规则集。
- 每次修改后检查 Prompt 长度、重复规则、职责冲突和非目标 section 字节保留。

## 7. 验证和产物边界

可以自主执行：单元测试、compileall、静态检查、`git diff --check`、mock smoke 和历史
run 的只读分析。不得删除或回写 `prompt_runs/`、`prompt_runs_by_dataset/`、
`baseline_predictions/` 或其他实验产物。

完成实现后至少验证：

```powershell
py -m unittest discover -s tests -q
py -m compileall analysis tests run.py
git diff --check
```

涉及 CLI/orchestration 时还必须运行 `--mock-with-gold --no-evolve
--no-llm-element-metrics` 的离线 smoke test。

## 8. 约定变更

若后续需要改变本目标或边界，先更新本文档和根目录 `CLAUDE.md`，再修改代码。不得先
实施超出边界的 workflow，再补写规范。
