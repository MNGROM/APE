# APE 后续修改目标与执行边界

本文档记录 `ape_pre/APE` 后续 goal 的共同约定。其作用是约束接下来的设计、代码修改、验证和实验行为；除非用户明确修改约定，否则后续工作必须遵守本文档。

## 1. 最终目标

后续修改的最终目的不是让训练流程形式上跑通，而是：

```text
在不使用 heldout 选择候选或调参的前提下，
提高 APE 接受的 Prompt 更新在 heldout Node F1 或 Relation F1 上
获得大致稳定泛化收益的概率。
```

这里的“大致稳定”不是保证每次运行都上升，而是要求收益能够通过配对重复评估体现，不能主要来自单次生成或 judge 波动。

当前 acceptance 语义固定为：

```text
Node F1 稳定上升
OR Relation F1 稳定上升
=> 接受候选
```

Compile、Syntax、Precision 和其他诊断指标继续完整记录，但 Compile 不能成为 winning metric，也不因其他诊断指标下降而自动否决候选。Prompt 超长、基础设施错误和收益指标评估不完整仍属于无效测量。

## 2. 基本判断原则

所有修改应从当前失败证据出发，优先选择复杂度最低、可验证且可解释的方案。

- 区分“强模型发现了错误”和“该错误能被一条 Prompt 规则稳定修复”。
- 区分系统性主因、次要伴随错误、dataset convention 和随机生成波动。
- Python 负责 ID 校验、计数、去重、聚合、排序和最终确定性决策。
- Agent 负责语义判断和修改内容生成，不得自行声明 support 数量或覆盖 canonical metadata。
- 新机制必须能够记录中间证据、进行离线回放，并可通过消融或对照解释其作用。
- 不为了使用论文中的方法而引入方法；只有它直接解决已观察到的问题时才采用。

## 3. 允许自主修改的范围

在已确认的 goal 内，可以自主修改：

- 现有阶段内部的 Python 实现细节、校验器、聚合和确定性排序逻辑。
- 轻量、可验证的 agent 输入输出 schema。
- 现有 agent prompt 中的职责、枚举、输出约束和错误边界。
- 当前产物中的审计字段、拒绝原因和诊断报告。
- 单元测试、流程测试、fixture 和基于历史日志的离线回放工具。
- 必要且向后兼容的 CLI 参数，但不得借此改变实验 split 或 heldout 边界。

允许在现有数据上采用常见研究机制，例如：

- 基于现有 batch observations 的多数投票或共识过滤。
- self-consistency 统计和一致性阈值。
- case-level confidence filtering。
- paired comparison、稳定胜出次数和噪声阈值。
- 冲突证据隔离、反向证据检查和确定性 tie-break。
- 在不接触 heldout 的前提下进行消融、离线回放和错误归因审计。

当前 selected-mechanism editing 采用 Prompt-gap 资格过滤：

- supporting batch 的 localization 必须区分 `missing`、`ambiguous` 和 `already_covered`。
- generation model 违反现有明确规则，不自动构成新的 Prompt gap。
- Python 只复用当前 supporting batches 已产生的一次 localization/editor 结果做严格多数表决，不增加 agent 调用。
- 只有完整 revision scope 相同的有效 local plans 达到 `floor(N/2) + 1`，才允许进入 epoch planner；`N=1` 时一份有效计划即可继续。
- `already_covered` 是有效 abstention，不是 agent 或基础设施失败。

后续最小归因实现使用新的 `mechanism_taxonomy_v3.json`。v1、v2 taxonomy 和对应的旧版 agent prompt 保持不变，用于复现既有实验；新 run 默认使用 v3，并在产物中记录实际 taxonomy 和 agent prompt 路径。

这些机制必须满足：最终计数和选择由 Python 完成；输入证据可追溯；结果可复现；不把启发式分数伪装成真实 validation 收益。

## 4. Schema 复杂度边界

Schema 可以调整，但必须保持紧凑。

- 只新增后续 validator、聚合器或审计产物实际消费的字段。
- 每个新增必填字段必须有明确语义、校验代码和测试。
- 不同时保存可以直接推导出的多份重复信息。
- 优先使用扁平字段和短列表，避免不必要的多层嵌套。
- evidence ID、case ID、mechanism ID 和 signature 必须有唯一 canonical 来源。
- Agent 不得返回可由 Python 计算的 batch count、case count、dataset count、consistency 或排名。
- 若一个 schema 需要长篇说明才能避免歧义，应优先缩小状态空间，而不是继续增加字段。

case-level 证据可以包含精确引用，例如 requirement span、预测元素、gold 元素和 primary/secondary 角色；但只有确实用于验证机制归因的最小字段才能进入正式 schema。

### 4.1 原子归因契约

v3 failure analysis 不再让 Agent 预先把多个 case 或多个 evaluator 错误聚合为一个 pattern。正式输入单元为 atomic attribution：

- 一个 attribution 只能引用一个真实 `evidence_id` 和一个 exact evaluator anchor。
- Python 根据 anchor 来源生成 canonical `anchor_kind` 和稳定 `attribution_id`，Agent 不得提供或覆盖。
- 同一 case 的不同 anchor 可以支持不同机制；同一 attribution 若被分配到多个 signature，只隔离该 attribution。
- 依赖错误 activity inventory 的 relation/construct 错误只能作为 secondary attribution，不能提供 candidate support。
- LLM judge 的 TP matching 若不是一一对应，该 case 不得提供 primary attribution，但仍保留为 ambiguous/secondary 审计证据。
- Agent 只负责逐 attribution 的语义判断；Python 负责归一化、去重、聚类、计数和候选选择。

为避免复杂 case 的大量下游 anchor 使结构化输出截断，v3 在调用 Agent 前由 Python 执行 evidence admission：

- 每个 batch 最多提供 12 个 atomic anchor；该预算只限制 analysis 输入规模，不改变 candidate promotion threshold。
- Python 根据 compiler/syntax failure 以及 Node/Relation precision/recall deficit 对各 case 内 anchor 排序；存在 node 错误时，direct node anchor 必须排在依赖该 inventory 的 relation anchor 之前。随后跨 case 轮询分配预算，不能让单个 case 占满输入。
- v3 输入为每个入选 anchor 提供 canonical `anchor_kind`、允许的 primary failure directions 和 matching 是否允许 primary；Agent 只能复制这些 anchor，且同一 anchor 最多输出一次。
- direct missing/extra node attribution 不得仅因存在下游 relation 错误而降为 secondary；只有依赖错误 node inventory 的 relation/construct attribution使用 secondary。
- activity 和 syntax attribution 的 `node_inventory_status` 固定为 `not_applicable`；非 compiler quote 必须是长度不超过 300 的 exact requirement substring。

v1/v2 的 `error_patterns` 继续只读兼容。v3 新 run 使用 `error_attributions`，不得同时输出两种 schema。

### 4.2 开放分层假设契约

v3 的候选发现不再要求一个归因先在多个 batch、case 或 dataset 上证明通用性。一个当前 epoch 的合格 primary attribution 即可形成待验证 child hypothesis；通用性和净收益由 validation gate 判断。

- parent key 使用除 `requirement_trigger` 外的五个 signature 字段，只用于证据汇总、排序和冲突审计，不得直接生成 Prompt 修改。
- child key 使用完整六字段 atomic signature，只有 child hypothesis 可以成为 candidate。
- taxonomy 是受控词汇、trigger/boundary 模板和已知 mechanism 的集合，不再是 candidate whitelist。
- 未命中已知 mechanism 的 schema-valid attribution 由 Python 生成稳定 `hypothesis_id`；若存在安全的窄规则模板，可以参与候选选择。
- 无安全模板的 hypothesis 记录 `no_safe_rule_template`；不得使用宽泛 fallback 规则。
- 同一 `construct_family + requirement_trigger` 出现方向相反的 primary evidence 时，相关 child hypotheses 标记 `scope_conflict` 并暂停候选，直到 trigger 或边界进一步拆分。
- 每个 epoch 仍只选择一个 candidate；不引入 exploratory candidate、Top-K 或额外 agent 调用。

候选最小资格固定为：当前 epoch 至少一个合法 primary attribution、matching 允许 primary、quote/anchor/trigger grounding 有效、evidence basis 非 `gold_only`/`ambiguous`、不存在未解决 scope conflict，且同一 Prompt hash 下未被明确拒绝。旧的 batch、case、dataset 和 consistency promotion hard gate 不再适用于开放假设策略。

### 4.3 Current-run evidence memory

新 run 在 run 根目录维护 `mechanism_memory.json`，仅在该 run 的 epoch 间复用，不跨 run 自动导入。

- Python 使用 `prompt_hash + dataset + case_id + anchor_kind + canonical anchor locator + exact requirement quote` 生成 evidence fingerprint 并去重。
- Prompt hash 相同的历史证据可以补充 child hypothesis 的支持、冲突和排序，但 candidate 必须有当前 epoch attribution 激活。
- 同一 Prompt hash 下已 rejected 的 hypothesis 不重复尝试。
- Prompt 接受并变化后，旧 Prompt hash 下的 evidence 保留为 `historical`，不再提供 active support。
- memory 只保存可追溯的 attribution/evidence 快照和 candidate outcome，不把启发式统计伪装成 validation 收益。

## 5. Agent Prompt 膨胀边界

Prompt 修改遵循“替换和收紧优先，追加次之”。

- 优先改写已有职责或规则，不重复增加语义相同的段落。
- 正向触发条件和负向边界应紧邻表达。
- 不在多个 agent prompt 中复制同一套完整 taxonomy；由 Python 注入必要子集。
- 不要求 Agent 完成 Python 可以确定性完成的计数、排序和 ID 推导。
- 示例只在枚举或边界无法简洁表达时加入，并限制为最小正反例。
- 每次修改后检查 prompt 长度、重复规则和职责冲突。

v3 prompt rewriter 保留现有阶段和单次调用，但只返回目标规则片段。Python 根据经过校验的 operation 和 exact `text_to_modify` 确定性组装完整 Prompt；模型不得返回或改写完整 Prompt。

## 6. Workflow 红线

默认保持当前主流程及阶段顺序：

```text
batch evaluation
-> batch failure analysis
-> Python pattern validation / taxonomy mapping / epoch clustering
-> selected-mechanism localization and editor
-> epoch planner
-> prompt rewriter
-> repeated validation
```

以下行为视为大幅修改 workflow，不能自主实施：

- 新增、删除、合并或重排 agent 阶段。
- 从单候选改为 Top-K、多候选并发或候选串行叠加。
- 新增 critic、reviewer、judge-of-judge 等 agent 角色。
- 对同一阶段增加多次真实模型调用以做 self-consistency、debate 或 agent voting。
- 改变 validation、heldout 的调用时机、数据边界或候选选择职责。
- 显著改变每个 epoch 的 API 调用数量、并发结构或成本模型。

如果实现目标确实需要上述修改，必须停止当前工作，说明：需要改变什么、为什么现有 workflow 无法解决、预期收益、额外成本和更保守的替代方案；获得用户同意后才能继续。

利用当前已经产生的多个 batch observations 做 Python 多数投票，不属于 workflow 大改。为了投票额外重复调用模型，则属于 workflow 大改。

开放假设策略允许原有下游阶段在单个 supporting batch 上运行。这不新增阶段或单阶段调用次数，只取消候选发现和 Prompt-gap 共识中的人为双 batch 下限。

## 7. Heldout 与实验边界

Heldout 是最终泛化审计，不是训练信号。

- heldout 不参与 taxonomy、机制聚类、候选排序、Prompt 修改、threshold 校准或 acceptance gate。
- validation 仍是候选接受的唯一数据 split。
- 不能因为看到 heldout 个别 case 的结果而直接为其增加 Prompt 规则。
- 若后续根据多轮 heldout 反馈继续调整设计，必须明确记录测试集反馈风险，必要时更换新的 untouched heldout。
- heldout 的单次上升不等于稳定改善；应结合配对重复、胜出次数、平均增量和噪声范围解释。

可以自主执行的验证仅包括：

- 单元测试和流程测试。
- `compileall`、静态检查和 `git diff --check`。
- 不调用外部模型的 mock/smoke test。
- 只读历史 run 的离线回放和统计分析。

未经用户明确同意，不得自主执行：

- 任何真实模型 API 调用。
- calibration、在线 smoke run、单 case 在线探测或正式训练。
- heldout evaluation 或完整实验。

到达实验检查点时必须停止，向用户提供建议命令、配置、实验目的、预期产物和成功/失败判据，由用户决定并运行。

## 8. Goal 执行约定

- 讨论和方案确认阶段不创建修改 goal。
- 用户明确要求开始后，再以已确认目标和本文边界创建 goal。
- Goal 不扩大权限；即使自动继续，也不得越过 workflow 和实验红线。
- 较大实现开始前先给出具体计划，说明哪些文件和契约会变化。
- 每个阶段完成后运行允许范围内的本地验证，并报告真实结果。
- 若发现必须修改 workflow，立即停止实现并请求批准。
- 若代码已经 experiment-ready 但需要真实实验验证，停止在实验检查点，不擅自运行。
- 在没有实验结果前，不声称 heldout 已经改善；只能说明代码和离线证据支持某种预期。

## 9. 当前已知基线

- generation model 为 `glm-4.5`，analysis/editor/judge 为 `glm-5.1`。
- generation、agents 和 judge 默认显式使用 `do_sample=false`；采样实验必须主动传入 `--do-sample true`。
- 最近一次 candidate 仅因 Compile 上升而被现有实现接受；按本文固定语义应追溯为 rejected。
- 后续实验不应从该错误接受的 Prompt 继续叠加，应从未接受该修改的基线 Prompt 开始。
- 当前优先问题是让窄、可验证的 child hypothesis 能进入 validation，同时避免 parent cluster 或 taxonomy fallback 扩大规则边界。
- training batch 指标只用于诊断，不作为 candidate 是否值得验证的前置证明。
- validation 仍决定 Prompt 候选的净收益；允许局部 case 或 training metric 回退，但不改变既有 acceptance threshold。

## 10. 约定变更

如果后续讨论改变上述目标或边界，应先更新本文档，再按新约定修改代码。不能先越过边界实施，再补写文档。
