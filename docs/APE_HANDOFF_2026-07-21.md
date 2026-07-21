# APE 当前状态与下一个模型交接说明

更新时间：2026-07-21

本文是当前 `ape_pre/APE` 工作区的交接快照，供后续模型进入任务时使用。它描述代码实际状态、项目目标、实验边界和最近一次运行的证据。它不是新的修改方案，也不覆盖已有规则。

## 1. 阅读顺序与权威来源

进入项目后按以下顺序阅读：

1. 本文：了解当前实现、结果和未解决问题。
2. `docs/APE_NEXT_MODIFICATION_GUARDRAILS.md`：后续修改的正式边界，优先级高于本文的解释性内容。
3. `run.py`、`analysis/` 和对应 `prompt_workspace/*.md`：确认代码契约。
4. 最新 run 的 `manifest.json`、`mechanisms/`、`decision/` 和 `validation_gate/`：只读实际证据。

`docs/APE_PRE_CHECKPOINT_2026-07-20.md` 是历史计划和阶段记录，不能作为当前实现的唯一依据。历史实验产物、真实数据集、`.env` 和用户已有未提交修改都必须保留。

## 2. 项目目标

APE 的任务是从训练集失败案例中发现可迁移的 Prompt 规则，生成一个候选 Prompt，并且只在 validation split 上验证后决定是否接受。最终目标是：

```text
接受的 Prompt 更新在 heldout 上让 Node F1 或 Relation F1
获得大致稳定的泛化收益，而不是只在一次调用中上升。
```

固定接受语义：

```text
Node F1 稳定上升 OR Relation F1 稳定上升 => 接受
```

Compile、Syntax、Precision 和 Recall 是诊断指标。Compile 上升不能单独接受候选，也不因为其他诊断指标下降而否决语义收益。

当前工作重点不是让每个 epoch 都产生候选，而是避免把以下错误推理写入 Prompt：

```text
同一种错误重复出现
=> Prompt 一定缺规则
=> 必须修改 Prompt
```

生成模型违反一条已有但执行不稳定的规则，可能是 generation 波动、复杂语义推理或评估噪声，不等于 Prompt gap。

## 3. 工作边界

可以自主修改：

- 现有阶段内部的 Python 校验、去重、聚类、聚合和确定性排序。
- 紧凑的 agent schema、现有 agent prompt 的职责和边界。
- 审计产物、拒绝原因、离线回放和测试。

需要先停止并征得用户同意的事项：

- 新增、删除、合并或重排 agent 阶段。
- 从单候选变成 Top-K、多候选并发或候选串行叠加。
- 新增 critic、reviewer、judge-of-judge 或同一阶段重复真实模型调用。
- 改变 validation、heldout 的数据边界、调用时机或候选选择职责。
- 明显增加每轮 API 调用数量或改变成本模型。

未经用户明确决定，不运行真实模型、calibration、在线 smoke、正式训练或 heldout。允许的本地验证是单元测试、mock 流程、`compileall`、`git diff --check` 和只读历史 run 分析。

用户已经明确：自然 generation/judge 波动是合理现象，不再推进 judge 结果缓存。不要把缓存重新作为默认修复方向；应提高候选收益相对于自然波动的幅度和稳定性。

## 4. 当前主流程

主流程没有被改成多候选，当前仍是单候选：

```text
case evaluation
  -> batch failure analysis
  -> Python pattern validation / taxonomy mapping
  -> epoch 聚合 evidence inventory / mechanism cluster
  -> Python 选择一个机制
  -> 仅对 selected mechanism 的 supporting batches 做 localization/editor
  -> Prompt-gap 严格多数表决
  -> epoch planner 合并同一 section 的有效 local plans
  -> prompt rewriter
  -> validation repeated paired gate
  -> 接受时才更新 Prompt
```

heldout 不参与机制选择、Prompt 修改、threshold 校准或 acceptance。最近运行配置中初始和最终 heldout 都被执行，但同一 Prompt 的 heldout 数值发生明显波动；这不是候选成功的证据。

## 5. 代码结构

### 根目录入口

- `run.py`：CLI、数据切分、iteration orchestration、batch 并发、机制聚类调用、selected editing、planner/rewriter、validation gate、heldout/report 流程。
- `config.py`：默认参数、模型和 taxonomy 路径。
- `evaluation.py`：生成 PlantUML、编译和结构化 case 评估。
- `prediction.py`、`element_extraction.py`：模型输出解析及元素抽取。
- `llm.py`：模型请求路由、采样参数和重试。
- `llm_element_metrics.py`：LLM 语义 Node/Relation Precision、Recall、F1。
- `metrics.py`、`reporting.py`：统计和报告。
- `prompt_ops.py`：Prompt section 解析、schema 检查、exact substring 和 section diff 检查。

### `analysis/`

- `failure_analysis.py`：构造 failure-analysis 输入，生成 case evidence，调用 failure-analysis agent。
- `mechanism_clustering.py`：稳定 evidence ID、逐 pattern 校验、taxonomy 映射、observation inventory、去重、冲突统计、候选门槛、确定性选择，以及 selected evidence 的 sanitization。
- `error_localization.py`：判断当前 Prompt 是 `missing`、`ambiguous` 还是 `already_covered`，并校验 quote/diagnosis。
- `prompt_editor.py`：selected mechanism 的 batch-local 一个 revision item；不能重新选择机制。
- `epoch_planner.py`：接收同一机制、同一多数 section 的 local plans，输出一个 revision item。
- `prompt_rewriter.py`：返回完整 Prompt；Python 校验目标 section 之外逐字不变。

### `prompt_workspace/`

- `tst.md`：当前初始 Prompt。
- `failure_analysis.md`：failure-analysis schema、枚举和 evidence 约束。
- `error_localization.md`：Prompt-gap 判断规则。
- `prompt_editor.md`：local revision plan 规则。
- `epoch_planner.md`：单机制、单 section、单 item 的合并规则。
- `prompt_rewriter.md`：完整 Prompt 重写规则。
- `mechanism_taxonomy_v1.json`：历史 taxonomy，保持不变以复现旧实验。
- `mechanism_taxonomy_v2.json`：当前默认 taxonomy。

### `tests/`

当前测试覆盖 acceptance gate、validation repeats、mechanism clustering、training flow、model routing、planner、editor、Prompt 操作、reporting 和 batch 流程。最近一次本地结果为 `113` 个测试通过。

## 6. Evidence 与 taxonomy 契约

Python 为每个 case 生成稳定 evidence ID，包含 run、iteration、batch、dataset 和真实 case ID。模型只能引用已存在的 ID；伪造 ID、非法枚举和不一致的 family/state 组合只隔离对应 pattern，不应让整个 batch 作废。

当前聚类签名为六字段：

```text
failure_direction
+ construct_family
+ requirement_trigger
+ gold_state
+ prediction_state
+ node_inventory_status
```

taxonomy v2 把 activity over-decomposition 拆成两个机制：

| mechanism | trigger | gold -> prediction | 资格 |
|---|---|---|---|
| `context_clause_as_activity` | `context_clause` | `none -> single` | `requirement_and_gold` |
| `single_action_split_into_unsupported_substeps` | `unstated_implementation_substeps` | `single -> multiple` | `requirement_and_gold` 或 `requirement_only` |

旧 `single_explicit_action` 仍可读取历史产物，但在 v2 只记录，不生成 candidate。

family-specific `node_inventory_status`：

- `activity`、`syntax`：必须为 `not_applicable`。
- `fork`、`loop`、`branch`、`early_exit`：candidate 必须为 `sufficient`。

`evidence_basis` 的作用是资格过滤，不进入聚类 key：

- `requirement_and_gold`、`requirement_only`：可参与普通 candidate。
- `gold_only`：只记为 `dataset_convention`。
- `ambiguous`：只记录。
- `compiler`：只允许 compiler-confirmed syntax。

普通机制仍需满足：至少 2 个 supporting batches、至少 3 个 unique cases、至少 2 个 training datasets、consistency 至少 `2/3`，且正向 batches 多于 opposite batches。相同 batch 同一 signature 只计一次；同一 case 的重复引用只计一个 unique case。

冻结的 v2 边界由 Python 注入 revision item，模型不能改写。特别是：

- context clause 只排除纯初始状态、前置条件、时间上下文；其中明确动作、状态转换或结果必须保留。
- implementation substeps 只禁止把一个明确行为展开成未陈述的输入、计算、处理或输出步骤；多个独立明确动作不能合并。

## 7. Prompt-gap 资格过滤

selected mechanism 的 failure analysis 会被 sanitization：

- 只保留 Python 已计入该 observation 的 primary evidence IDs。
- catalog 只保留这些 ID 对应的真实 case。
- 删除 `problem`、`possible_causes`、`downstream_guidance` 等未过滤自由文本。
- pattern 没有有效 claims 时删除；batch 没有剩余 pattern 时不调用 localization/editor。

Localization 输出是紧凑扁平结构：

```json
{
  "prompt_gap": "missing|ambiguous|already_covered",
  "existing_prompt_quote": "...",
  "gap_rationale": "...",
  "section_diagnoses": []
}
```

校验要点：

- `already_covered`：quote 必须是当前 Prompt 精确连续子串，diagnoses 必须为空；这是有效 abstention，不是失败。
- `ambiguous`：必须有一个 diagnosis，quote 必须存在于该 section，并解释现有文字如何允许相反解释。
- `missing`：必须有一个 diagnosis，quote 必须为空，并说明缺少的 trigger 或 boundary。
- diagnosis 必须有合法 section、repair type、非空 problem 和 risk。

严格多数：

```python
required_votes = max(2, floor(supporting_batch_count / 2) + 1)
```

只有 `missing/ambiguous`、schema 有效、editor 有一个有效 item、且 target section 与 localization 一致，才计 actionable vote。同一 section 达到多数才进入 planner。结果写入 `mechanisms/prompt_gap_consensus.json`。

## 8. Acceptance gate

默认 `--acceptance-policy any-improvement`。`legacy` 仍保留以复现旧实验，但不是默认策略。

默认语义指标：

- `llm_node_f1`
- `llm_relation_f1`

每个指标在相同 validation cases 上做 paired repeats。当前规则是：

```text
mean_delta > metric_min_delta
AND
wins >= acceptance_min_wins
```

零 delta 不算胜出；所有 paired repeats 必须有效。任一语义指标成为 winning metric 才接受。当前不使用 Compile 作为 winning metric。

校准得到的正式阈值（最近 run 使用）：

```text
Node min delta     = 0.016575050257349625
Relation min delta = 0.020684536500101783
repeats            = 3
min wins           = 2
```

阈值不是为了保证每个正确修复都被接受，而是为了过滤自然波动。没有足够收益时保持旧 Prompt 是预期行为。

## 9. 数据与模型配置

最近正式 smoke 使用：

- training pool：60 cases；实际 train 40，validation 20。
- training datasets：BP、FSD、LMC、PURE、RAC，各 train 8、validation 4。
- heldout：US 10 cases，仅用于观察，不用于选择。
- `sample_seed=13`，validation seed `20260629`。
- validation split fingerprint：`d027296b9c275d5f1041dff5ef7bd9f13d1b1df691a2ec2cd74b14e115e5aa6a`。
- generation model：`glm-4.5`。
- analysis/localization/editor/planner/judge：`glm-5.1`。
- `do_sample=false`，temperature 均为 `0`，thinking disabled。

`do_sample=false` 已在 generation 和 LLM judge 路径显式传递。temperature 为 0 不能消除服务端、模型实现、并发顺序或 judge 评估的全部波动，因此仍使用 paired repeats 和 delta threshold。

## 10. 最近一次实际运行

运行目录：

```text
prompt_runs/2026-07-21__00-55-51__test-us
```

这是一次 one-epoch run，使用 taxonomy v2，候选没有被接受。

### 机制选择

`mechanisms/selected.json` 的结果：

- mechanism：`context_clause_as_activity`
- supporting batches：4
- unique eligible cases：4
- supporting datasets：3（BP、LMC、RAC）
- opposite batches：0
- consistency：1.0
- estimated impact：约 `0.081475`

四个严格合格 case 为 `bp-0004`、`lmc-0009`、`rac-0006`、`rac-0012`。原始 primary evidence 有 6 个 case，但资格和歧义过滤后只剩 4 个。

### Prompt-gap 与候选

四个 supporting batches 都返回 `ambiguous`，目标 section 都是 `workflow`；要求 3 票，实际 4 票。四个 editor plan 均有效，因此 planner/rewriter 正常完成。

候选把 workflow 中的 activity 提取规则从约 1181 字符的 baseline 相关段落扩展为约 1511 字符的候选。候选明确区分 intro precondition、initial state、timing clause 与显式 action/state/outcome。

这说明候选链路已经到达 planner、rewriter 和 repeated validation，但不能说明修改正确。候选行为减少了部分 startup context extra nodes，Precision 每次都上升，却同时影响大量非目标 case。

### Gate 结果

`decision/acceptance.json`：`accepted=false`，原因 `no_stable_improvement`。

| 指标 | 三次 delta | mean | wins | 结果 |
|---|---|---:|---:|---|
| Node F1 | `-0.019640, +0.024115, -0.004380` | `+0.000032` | 1/3 | 拒绝 |
| Relation F1 | `-0.022360, +0.010915, +0.044055` | `+0.010870` | 2/3 | 低于阈值，拒绝 |
| Compile | `+0.050, +0.050, 0` | `+0.033333` | 诊断 | 不能接受 |

候选的主要诊断变化：Node/Relation Precision 都上升，但 Recall 混合下降；这解释了为什么局部 extra-node 修复没有转化为稳定 F1 收益。validation 有效、无基础设施错误、Prompt 长度合法，所以这不是 gate 或 API 失败。

Prompt 最终 hash 与初始 Prompt 相同，说明 rejected candidate 没有被串入下一轮。

同一 run 的 heldout initial/final 即使 Prompt 未改变也有明显数值波动。因此不能用这组 heldout 曲线判断候选效果，也不应为此引入缓存。

## 11. 当前问题判断

当前主要问题不是“gate 太严格”或“temperature 没关”，而是：

1. 可归因机制很多，但跨 dataset、单一方向、对 F1 有足够影响的机制很少。
2. 最容易聚合的 `context_clause_as_activity` 是广泛的 extraction 规则，修改会触发全局行为，容易 Precision 上升、Recall 下降。
3. 多数支持只能证明 batches 对 gap 的判断一致，不能证明一条规则在 validation 上有净收益。
4. failure labels 中 `missing_activity`、`extra_activity`、`missing_or_wrong_relation` 等数量很大，但它们是粗粒度现象，不是一个可直接写进 Prompt 的统一机制。
5. 剩余高频问题集中在 branch/loop/relation 的复杂组合，现有 40 个 train cases 中跨 dataset 的证据不足，硬推 candidate 会把 dataset convention 或语义异质样本混在一起。

当前不能得出“存在无法弥补的硬缺陷”的结论。更准确的结论是：现有小样本和单轮证据尚未发现足够强、足够窄、可迁移的修复机制。多数 epoch 不产生 candidate 是合理的保守结果。

## 12. 机制分布的当前判断

基于最近 40 个 training cases 的离线聚合：

- `context_clause_as_activity`：原始 6 个 primary evidence，严格 eligible 4 个，4 batches、3 datasets；影响较广但实际 F1 收益不足。
- 普通枚举误判为缺 fork：约 4 cases，但只有 1 batch，且可能是 gold notation convention，不宜直接修复。
- `unstated_implementation_substeps`：约 3 cases、2 batches、1 dataset（主要 LMC）；影响较高但迁移证据不足。
- 状态转换描述触发 spurious loop：约 3 cases、2 batches、2 datasets，但语义异质，暂不能晋升 candidate taxonomy。
- explicit concurrency 缺 fork：严格 cluster 只有约 2 cases、1 batch、1 dataset，未达到门槛。
- 其余具体机制大多只有 1-2 个 case。

因此不要因为 coarse label 数量大就降低 candidate 门槛，也不要为了让流程继续而强行选择低支持机制。

## 13. 下一模型的建议起点

下一步应先做只读分析，不立即改代码或跑实验：

1. 读取最新 run 的 `mechanisms/evidence_inventory.json`、`clusters.json`、`selected.json`、`prompt_gap_consensus.json` 和 `decision/acceptance.json`。
2. 对候选修改导致的 validation case 级 Node/Relation 增减做 diff，确认 collateral effect 来自哪些 rule interaction，而不是只看 aggregate F1。
3. 人工审计 `unstated_implementation_substeps`、spurious loop 和 missing fork 的真实 requirement/gold/prediction 引用，判断它们是否属于统一机制，不能只按名字合并。
4. 若需要扩大证据量，优先讨论提高 train pool/case 数；这会改变 split 和 calibration 解释，必须由用户决定并运行实验。
5. 只有找到更窄且跨 dataset 的机制后，才考虑修改 taxonomy 或 Prompt。没有新证据时不要降低 gate 阈值、接受 Compile-only candidate、放宽多数门槛或恢复 caching。

任何真实实验前都应先告诉用户：实验目的、命令、预期产物和成功/失败判据。助手不自行调用 API。

## 14. 最近一次运行命令

下面是复现实验的命令模板。它只用于用户决定后运行，本文记录命令但没有由交接文档自动执行：

```powershell
py run.py `
  --test-dataset us `
  --iterations 1 `
  --max-train-cases 60 `
  --max-test-cases 10 `
  --eval-initial-test `
  --analysis-batch-size 10 `
  --epoch-batch-concurrency 4 `
  --heldout-test-concurrency 10 `
  --validation-gate-concurrency 10 `
  --validation-gate-size 30 `
  --validation-gate-seed 20260629 `
  --validation-repeats 3 `
  --acceptance-min-wins 2 `
  --acceptance-policy any-improvement `
  --any-improvement-node-min-delta 0.016575050257349625 `
  --any-improvement-relation-min-delta 0.020684536500101783 `
  --mechanism-taxonomy-path prompt_workspace\mechanism_taxonomy_v2.json `
  --sample-seed 13 `
  --generation-model glm-4.5 `
  --agent-model glm-5.1 `
  --judge-model glm-5.1 `
  --temperature 0 `
  --analysis-temperature 0 `
  --localization-temperature 0 `
  --editor-temperature 0 `
  --epoch-planner-temperature 0 `
  --llm-judge-temperature 0 `
  --do-sample false `
  --thinking disabled `
  --generation-thinking disabled `
  --analysis-thinking disabled `
  --localization-thinking disabled `
  --editor-thinking disabled `
  --epoch-planner-thinking disabled `
  --judge-thinking disabled
```

注意：这条命令使用 20 个实际 validation cases（请求 30，但当前 split 只有 20），并且会调用真实模型。下一次实验如果改变 train pool、seed、threshold 或模型，必须在 run 记录中明确说明，不要直接拿不同 split 的 delta 横向比较。

## 15. 交接前验证命令

代码修改完成后执行：

```powershell
py -m unittest discover -s tests -q
py -m compileall analysis tests run.py
git diff --check
```

交接时应报告真实测试结果。不要因为测试通过就声称 heldout 已改善；测试只能证明离线契约和流程没有明显回归。

## 16. 交接检查清单

- [ ] 已读本文和 `APE_NEXT_MODIFICATION_GUARDRAILS.md`。
- [ ] 已确认当前默认 taxonomy 是 v2，v1 只用于历史复现。
- [ ] 已确认 gate 的 semantic rule 是 Node F1 OR Relation F1，Compile 不能接受。
- [ ] 已确认 `do_sample=false` 和温度 0 已生效，但仍存在合理波动。
- [ ] 已确认不使用 judge-result caching 作为当前方向。
- [ ] 已确认 heldout 不参与训练信号或候选选择。
- [ ] 修改前先说明是否触及 workflow 红线。
- [ ] 真实实验前停止并交给用户运行。
- [ ] 不回滚工作树中的既有修改，不改历史 run、数据集或 `.env`。
