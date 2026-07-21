# APE_PRE 工作断点与后续修改方案（2026-07-20）

本文档是 `D:\now_to_use\work4icse\rq1\ape_pre\APE` 的当前唯一接手入口。目标是让后续模型在不重做历史分析、不误读实验结果的前提下，继续完成 `ape_pre` 的 Prompt evolution 改造。

> 后续 acceptance 与执行边界以 `docs/APE_NEXT_MODIFICATION_GUARDRAILS.md` 为准。本文后文中“Compile 可独立接受候选”的旧方案已被用户撤销，Compile 现仅作诊断。

本文档区分三种状态：

- **已实现**：当前代码已经存在，并经过本地测试或运行产物确认。
- **已决定、待实现**：用户已明确方向，但代码尚未修改。
- **暂定、待审计**：只有设计假设或日志线索，不能直接固化为系统规则。

除非用户改变方向，后续工作应以 `ape_pre` 为主，不要继续扩展 `D:\now_to_use\work4icse\rq1\ape` 的新运行时。

---

## 1. 当前研究目标

当前研究问题不是改善 GLM-5.1 自身的生成，而是验证以下 Prompt-level distillation 路线是否有效：

```text
GLM-4.5 生成 PlantUML，提供较明显、较稳定的错误窗口
-> GLM-5.1 分析错误、定位 Prompt、提出修订
-> 修改后的 Prompt 继续驱动 GLM-4.5
-> 只要最终评估指标能够稳定改善，即认为 Prompt intervention 有效
```

当前角色分工已经确定：

| 角色 | 模型 |
|---|---|
| PlantUML prediction | `glm-4.5` |
| failure analysis / localization / editor / epoch planner / rewriter | `glm-5.1` |
| element extraction / semantic judge | `glm-5.1` |

弱模型上的改善不等于 GLM-5.1 生成能力改善，也不需要证明知识能回灌 GLM-5.1。当前目标只要求 Prompt intervention 对 GLM-4.5 的最终指标产生稳定效果。

---

## 2. 接手前必须阅读

按顺序阅读：

1. `docs/APE_PRE_CHECKPOINT_2026-07-20.md`（本文档）
2. `docs/DIFF_FROM_APE_MAIN.md`
3. `docs/KNOWN_ISSUES.md`
4. `prompt_workspace/failure_analysis.md`
5. `prompt_workspace/error_localization.md`
6. `prompt_workspace/prompt_editor.md`
7. `prompt_workspace/epoch_planner.md`
8. `run.py` 中的 `acceptance_decision()`、`evaluate_validation_gate()` 和 epoch candidate 流程
9. `evaluation.py::evaluate_cases()`
10. `metrics.py::summarize_records()`
11. `llm_element_metrics.py`

`ape_pre` 目录当前没有单独的 `CLAUDE.md`。不要据此忽略用户给出的工程约束：较大代码修改前先规划并确认；不得修改真实数据集、official evaluator、`.env`、密钥或历史实验产物。

---

## 3. 当前代码结构

主要模块：

```text
run.py                         主训练、epoch、validation、heldout 流程
evaluation.py                  生成、编译、LLM judge、并发 case 评估
metrics.py                     record/summary、辅助 embedding 指标
llm_element_metrics.py         GLM judge 抽取与 TP/FP/FN 匹配
llm.py                         模型客户端与角色模型路由
prediction.py                  PlantUML generation
prompt_ops.py                  revision plan 解析和校验
reporting.py                   run/iteration 报告

analysis/failure_analysis.py   batch 错误分析
analysis/error_localization.py Prompt section 定位
analysis/prompt_editor.py      batch-local revision plan
analysis/epoch_planner.py      合并 batch plan
analysis/prompt_rewriter.py    生成完整 candidate Prompt

prompt_workspace/*.md          各 Agent system prompt
tests/                         单元测试
prompt_runs/                   历史运行产物，不得覆盖或改写
```

当前 epoch 流程：

```text
固定训练池
-> 每轮分成 30 个 batch
-> 每个 batch 生成、评估、failure analysis、localization、editor
-> epoch planner 汇总 30 个 batch revision plan
-> rewriter 生成一个候选 Prompt
-> fixed validation gate 比较 baseline/candidate
-> 接受或拒绝整个候选
-> 每轮无条件运行 heldout
```

---

## 4. 已完成的代码修改

以下内容已经实现，不要重复实现：

### 4.1 模型角色拆分

`run.py` 已支持：

```text
--generation-model
--agent-model
--judge-model
```

当前路由为：

- prediction 使用 `generation_model`；
- Prompt evolution Agents 使用 `agent_model`；
- LLM element judge 和辅助 extraction 使用 `judge_model`。

### 4.2 并发能力

已经实现：

```text
--epoch-batch-concurrency
--heldout-test-concurrency
```

尚未实现独立的 validation gate 并发参数。`evaluate_cases()` 已有 `case_concurrency`，但 `evaluate_validation_gate()` 当前没有传入 validation 专用 concurrency。

### 4.3 Fixed validation split

validation cases 从 training pool 固定留出，不参与 failure analysis、localization、editor 和 planner。当前默认：

```text
--validation-gate-size 30
--validation-gate-strategy stratified
--validation-gate-seed 20260629
```

### 4.4 依赖问题

绘图依赖名是 `matplotlib`，不是 `matlotlib`。出现：

```text
ModuleNotFoundError: No module named 'matplotlib'
```

时，应在当前 Python 环境安装项目依赖或 `matplotlib`；不要安装拼写错误的 `matlotlib`。

---

## 5. 最近一次正式 `ape_pre` 运行

运行目录：

```text
prompt_runs/2026-07-19__18-42-16__test-us
```

关键参数：

```text
test_dataset=us
iterations=3
generation_model=glm-4.5
agent_model=glm-5.1
judge_model=glm-5.1
analysis_batch_size=10
epoch_batch_concurrency=20
heldout_test_concurrency=20
validation_gate_size=30
validation_gate_strategy=stratified
validation_gate_seed=20260629
eval_initial_test=true
temperature=0
do_sample/top_p omitted
```

注意：temperature 为 0 不代表服务端完全确定。

### 5.1 Validation 结果

| Iteration | Node F1 delta | Relation F1 delta | Compile delta | 旧 gate |
|---|---:|---:|---:|---|
| 1 | +0.040023 | +0.029940 | -0.066667 | rejected |
| 2 | +0.015190 | -0.022960 | -0.033333 | rejected |
| 3 | -0.009543 | +0.012503 | -0.033333 | rejected |

三个 candidate 全部被拒绝，因此三轮 `prompt_after` 实际均等于 seed Prompt。

### 5.2 Heldout US 结果

| Iteration | Compile | Node F1 | Relation F1 |
|---|---:|---:|---:|
| 0 | 0.9909 | 0.8382 | 0.6517 |
| 1 | 0.9864 | 0.8530 | 0.6598 |
| 2 | 0.9818 | 0.8431 | 0.6604 |
| 3 | 0.9909 | 0.8351 | 0.6471 |

由于 Prompt 从未改变，这些 heldout 波动不能解释为三轮 APE 学习效果，只能说明 GLM-4.5 generation 和 GLM-5.1 judge 存在运行方差。

---

## 6. 当前根因判断

日志表明 GLM-5.1 能识别 GLM-4.5 的明显问题，例如：

- 活动过度拆分或不足拆分；
- ordinary list/peer items 与 fork 的混淆；
- periodic/cyclic 描述错误触发 loop；
- explicit loop、early exit 或 alternative branch 遗漏；
- PlantUML construct syntax 错误。

因此主要瓶颈不是“强 Agent 看不出弱模型错误”，而是：

1. 30 个 batch 的多个修订被合并成一个宽候选；
2. 不同机制同时修改多个 Prompt section，无法做因果归因；
3. validation 只对 baseline/candidate 各生成一次，方差较大；
4. validation 只有 30 个 case，compile rate 的最小变化单位为 3.33%；
5. 当前 safety threshold 约为 -1%，所以多一个 compile failure 就会自动失败；
6. 所有 candidate 被拒后，每轮又从同一 seed Prompt 出发，没有形成累积学习；
7. 每轮即使 Prompt 不变也运行 heldout，容易把随机波动误读为效果。

---

## 7. 用户已经明确的 Gate 目标

用户要求将 acceptance 改为析取式规则：

```text
只要一个目标指标上升，candidate 即可接受；
其他指标是否下降不参与否决。
```

建议预先冻结的默认 acceptance metrics：

```text
llm_node_f1
llm_relation_f1
plantuml_compilation_pass_rate
```

Precision、Recall、Syntax 和其他指标继续报告，但默认不参与接受。这样保持与当前 benefit gate 的目标指标一致，避免在实验中临时扩张“任一指标”的范围。

即使采用 any-improvement，也必须保留评估有效性检查：

- candidate Prompt 不超过 `max_prompt_chars`；
- generation/judge 不是基础设施级失败；
- acceptance 指标确实完成评估。

这些检查不是性能 safety gate，而是保证测量有效。

---

## 8. 二级机制方案审计

### 8.1 审计结论

当前 `failure_analysis.md` 定义的 12 个 `failure_direction` 可以保留为一级检索标签，但不能直接等同于因果机制。

对三轮日志的初步统计得到 580 个 Agent 输出 pattern，但它们来自同一训练池上的三轮分析，不能当作 580 个独立事实。`supporting_cases` 还是 batch 内 1-based index；正式统计前必须映射回 `dataset + case_id + generation_run` 并去重。

前一版二级机制列表已经完成设计级审计，结论如下。

### 8.2 可保留为正式审计候选

这些机制有较清晰的可观测定义，但仍需 case-level 审计后才能进入 planner：

| 机制 | 可观测定义 | 当前判断 |
|---|---|---|
| `explicit_actions_merged` | requirement 有多个明确行为谓词，gold 分开，prediction 合并 | 保留；需人工判定“多个动作” |
| `single_action_split_into_unsupported_substeps` | prediction 添加 requirement 未陈述的实现步骤 | 保留；优先审计 |
| `heading_or_label_as_activity` | 标题、编号、说明文本被生成成活动 | 保留；证据较直观 |
| `explicit_concurrency_not_mapped` | requirement 明确并发，gold 有 fork，prediction 无 fork | 保留；高可信 |
| `unsupported_fork` | requirement 无并发证据，gold 无 fork，prediction 有 fork | 保留；按 trigger 记录 subtype |
| `explicit_iteration_not_mapped` | requirement 明确重复/退出条件，gold 有 loop，prediction 无 loop | 保留；高可信 |
| `descriptor_overtriggered_loop` | periodic/cyclic 只描述任务性质，gold 无 loop，prediction 有 loop | 保留；需核对是否存在隐式退出 |
| `explicit_early_exit_omitted` | requirement 和 gold 均有退出路径，prediction 遗漏 | 保留；高价值 |
| `construct_syntax_invalid` | 本地 PlantUML 编译器确认语法错误 | 保留；高可信 |

### 8.3 降级为 dataset/gold convention

这些现象可以用于提高当前 benchmark 指标，但不能包装成通用 UML 知识：

| 暂定机制 | 审计问题 | 处理 |
|---|---|---|
| `peer_item_gold_parallelism_not_reproduced` | 多个对象或列表不天然表示并发，但部分 gold 使用 fork | 标记 `dataset_convention`，与 explicit concurrency 分开 |
| `gold_grouping_node_omitted` | grouping/container 节点可能是 gold 的抽象风格 | 标记 `dataset_convention` |
| `explicit_state_or_outcome_omitted` | 状态是否计为 activity 依赖 gold 粒度 | 标记 `dataset_convention`，逐 dataset 审计 |
| `exclusive_values_not_grouped_as_switch` | nested if 与 switch 可能语义等价，但 judge 要求 relation type 对齐 | 标记 `gold_notation_convention` |

允许这些候选进入指标优化，但报告必须说明其性质是 benchmark convention，不得声称发现了普遍 UML 建模原则。

### 8.4 不应作为独立机制

| 原暂定机制 | 修正 |
|---|---|
| `secondary_to_missing_activities` | 改为 `dependency_flag`；表示 relation 错误可能由 node inventory 引起 |
| `state_transition_misread_as_loop` | 暂作为 `unsupported_loop.trigger_subtype`，证据不足时不单独建类 |
| `branch_order_or_nesting_wrong` | 只有逻辑语义确实改变时才成立；纯 gold 结构差异不成立 |
| `wrapper_missing` | 改为 `output_contract_error`；当前 compile check 会自动补 `@startuml/@enduml` |
| `mixed_or_uncertain` | 永不生成 candidate，只保留为跳过原因 |

### 8.5 不能把 root cause 放进聚类 key

`possible_causes`、`repair_type`、目标 Prompt section 都是 Agent 假设，不是观测事实。正式聚类必须先使用 evidence-conditioned signature：

```json
{
  "failure_direction": "missing_required_parallel",
  "requirement_trigger": "explicit_concurrency",
  "gold_construct": "fork",
  "prediction_construct": "none",
  "node_inventory_status": "required_nodes_present",
  "observed_mismatch": "missing_construct"
}
```

聚类 key：

```text
failure_direction
+ requirement_trigger
+ gold_construct
+ prediction_construct
+ node_inventory_status
+ observed_mismatch
```

以下字段只能附着为待验证假设：

```text
hypothesized_root_cause
repair_type
target_section
change_instruction
```

### 8.6 正式机制审计门槛

在机制进入 `epoch_planner` 前，必须完成：

1. 将 batch-local `supporting_cases` 映射为真实 `dataset/case_id`；
2. 按 `dataset + case_id + generation_run` 去重；
3. 保存 requirement 原文证据、gold 结构证据、prediction 结构证据；
4. 标记 `valid / invalid / ambiguous / dataset_convention`；
5. 至少 3 个 unique cases；
6. 至少覆盖 2 个 training datasets；
7. `valid` 比例至少 80%；
8. `invalid + ambiguous` 不超过 20%；
9. 相反方向证据不能与支持证据接近；
10. 正式实验开始后冻结 taxonomy 版本，不得使用 heldout 更新分类。

人工审计最好由两名标注者独立完成并报告 Cohen's kappa。若只能单人审计，必须保留 Agent 原判断和人工判断差异，不能声称独立双标。

建议审计产物：

```text
mechanism_evidence.jsonl
mechanism_audit.csv
mechanism_taxonomy_v1.json
mechanism_audit_report.md
```

这些文件尚未生成。

---

## 9. 计划中的候选生成与排序

### 9.1 Agent 和代码的职责边界

```text
GLM-5.1：根据证据填写结构化 signature、生成最小 revision 内容
Python：校验 case ID、去重、统计 support、过滤、排序、选择
```

不能让 `epoch_planner` 自行声称某机制有多少支持，也不能只根据自然语言名称相似度聚类。

### 9.2 一个 candidate 一个机制

计划将 epoch planner 输出改为：

```json
{
  "candidate_plans": [
    {
      "candidate_id": "explicit_concurrency_not_mapped",
      "mechanism_signature": {},
      "supporting_evidence_ids": [],
      "revision_plan": [
        {
          "section": "knowledge",
          "operation": "qualify_existing",
          "text_to_modify": "...",
          "intent": "...",
          "change_instruction": "..."
        }
      ]
    }
  ]
}
```

硬约束：

- 一个 candidate 只处理一个 mechanism signature；
- 默认只修改一个 section；
- 一个 revision item 同时写清 positive trigger 和 negative boundary；
- 默认最多生成 3 个 candidate；
- `mixed_or_uncertain` 不得生成 candidate；
- 每个 candidate 的 evidence ID 必须能回查。

### 9.3 Validation 前排序

先执行硬筛选，再使用可解释字典序：

```text
1. distinct supporting batches 降序
2. distinct supporting datasets 降序
3. distinct unique cases 降序
4. direction consistency 降序
5. observed error impact 降序
6. edit length 升序
7. candidate_id 字典序
```

同一个 mechanism signature 只保留一个候选。同一 construct family 出现相反方向且证据接近时，本轮不修改该 construct。

该排序只决定“先验证谁”，不能决定最终采用谁。

### 9.4 Validation 后选择

所有 candidate 必须与同一个 baseline Prompt 独立比较。通过 any-improvement gate 后，每轮最多应用一个 candidate。

建议排序：

```text
1. winning metric 的 median repeat delta 降序
2. winning repeat rate 降序
3. supporting unique cases 降序
4. edit length 升序
```

未选中的候选只能保留为日志，下一轮必须基于更新后的 Prompt 重新验证，不能直接叠加。

---

## 10. Validation 测试设计

### 10.1 重复验证

计划新增：

```text
--validation-repeats 3
--acceptance-min-delta 0
--acceptance-min-win-rate 0.6667
```

同一 validation case set 上：

```text
baseline Prompt 独立生成 3 次
candidate Prompt 独立生成 3 次
每个 repeat 使用相同 case 集
```

当前 Prompt 未变化时复用 baseline repeats；接受新 Prompt 后清空并重新建立 baseline cache。

对指标 `m`：

```text
delta_m[r] = candidate_m[r] - baseline_m[r]
stable_improvement_m = mean(delta_m) > min_delta
                       AND positive_repeat_rate >= min_win_rate
accept = any(stable_improvement_m for m in acceptance_metrics)
```

其他指标下降不参与否决。

### 10.2 机制定向验证

全局 F1 上升不能证明候选修复了它声称的机制。每个候选还应在对应 validation subset 上记录定向指标：

| 机制 | 定向指标 |
|---|---|
| missing explicit fork | `fork_recovery_rate` |
| unsupported fork | `fork_removal_rate` |
| missing explicit loop | `loop_recovery_rate` |
| unsupported loop | `loop_removal_rate` |
| missing early exit | `exit_branch_recovery_rate` |
| missing activity | subset `node_recall` |
| extra activity | subset `node_precision` |
| syntax error | `plantuml_compilation_pass_rate` |

定向指标用于证明 intervention 与机制一致，默认不替代用户指定的全局 any-improvement gate。若定向行为完全没有变化，应在报告中标记 candidate 的机制解释未得到支持。

### 10.3 Final heldout

heldout 不参与机制聚类、candidate 排序或 Prompt 选择。

计划改成：

- `iteration_000` 可运行一次 baseline heldout；
- 只有本轮接受新 Prompt 时运行 iteration heldout；
- 训练结束始终运行 final heldout；
- 正式效果验证对 baseline/final Prompt 各运行 5 次，报告 mean、standard deviation、repeat delta；
- 不根据 heldout 结果回头调整 taxonomy 或选择 candidate。

---

## 11. 待实施代码修改方案

这是已讨论方案的汇总。实施前仍需用户批准具体 patch；不要一次性完成所有阶段后才测试。

### Phase 0：机制审计工具，不改训练行为

目标：先证明二级机制分类可用。

修改/新增范围：

- 增加 failure analysis schema 校验；
- 给每个 batch revision input 添加真实 `batch_id`、`dataset`、`case_id` 证据；
- 从历史 run 导出并去重 mechanism evidence；
- 生成人工审计 CSV 和 taxonomy JSON；
- 不读取 heldout case 内容；
- 不修改真实数据集和 official evaluator。

停止条件：若没有机制满足 unique case、dataset coverage 和 valid-rate 门槛，不继续实现机制驱动 candidate pool。

### Phase 1：Any-improvement gate

修改 `run.py::acceptance_decision()`：

- 新增 `--acceptance-policy any-improvement|legacy`；
- 默认或正式实验显式使用 `any-improvement`；
- 任一冻结目标指标稳定上升即接受；
- 其他指标下降只记录，不否决；
- 保留 evaluation validity 和 Prompt size 检查；
- 输出 `winning_metrics`、每个 repeat delta、win rate；
- `legacy` 保留用于复现旧结果。

先用三轮历史 summary 做离线行为回放。按单次 delta 语义，旧 iteration 1、2、3 都至少有一个指标上升；这只验证 gate 逻辑，不代表三者可以顺序接受。

### Phase 2：重复 validation、baseline cache 和并发

新增：

```text
--validation-repeats
--validation-gate-concurrency
--validation-candidate-concurrency
```

目录计划：

```text
iteration_NNN/validation_gate/
  repeat_001/
    baseline_records.jsonl
    candidate_001_records.jsonl
  repeat_002/
  repeat_003/
  aggregate_summary.json
  acceptance.json
```

要求：

- case 并发复用 `evaluation.evaluate_cases()`；
- candidate 并发默认保守设置为 1 或 2；
- 输出按 repeat/candidate ID 排序；
- Prompt 变更前复用 baseline cache；
- Prompt 接受后 baseline cache 失效；
- 并发只改变速度，不改变聚合结果。

### Phase 3：单机制候选池

修改范围：

- `prompt_workspace/failure_analysis.md`
- `prompt_workspace/error_localization.md`
- `prompt_workspace/prompt_editor.md`
- `prompt_workspace/epoch_planner.md`
- `analysis/failure_analysis.py`
- `analysis/epoch_planner.py`
- `prompt_ops.py`
- `run.py`
- 对应 tests

行为：

- 使用冻结的 `mechanism_taxonomy_v1`；
- 生成最多 3 个独立单机制 candidate；
- 所有 candidate 对比同一 baseline；
- gate 通过后每轮最多应用一个；
- 保存每个 candidate 的 Prompt diff、证据、validation 和未选原因。

### Phase 4：Heldout 和报告语义修正

- 仅在 Prompt 接受后运行 iteration heldout；
- final heldout 始终运行；
- 报告中明确区分：training evidence、mechanism validation、global validation、heldout；
- Prompt 未改变的 iteration 不再生成误导性的 heldout 折线点；
- `acceptance.json` 明确记录 policy、metric set、repeat policy 和 taxonomy version。

---

## 12. 测试计划

### 12.1 Gate 单元测试

必须覆盖：

- Node F1 上升、Relation/Compile 大幅下降，仍接受；
- Relation F1 上升、Node/Compile 下降，仍接受；
- Compile 上升、语义指标下降，仍接受；
- 所有目标指标不升，拒绝；
- 仅 1/3 repeat 上升，不满足稳定性，拒绝；
- 2/3 repeat 上升且 mean delta > 0，接受；
- Prompt 超长或评估无效，拒绝；
- `legacy` 继续复现旧 gate。

### 12.2 机制和候选测试

- batch-local case index 正确映射为真实 case ID；
- 跨 iteration 重复 case 不重复计 support；
- `mixed_or_uncertain` 不生成候选；
- `dependency_flag` 不被误当成机制；
- dataset convention 与通用机制分开；
- 一个 candidate 只有一个 mechanism signature 和一个 revision item；
- Agent 伪造 evidence ID 时校验失败；
- 相反方向证据接近时跳过 construct；
- 多 candidate 只接受排序后的一个。

### 12.3 Validation 流程测试

- baseline cache 在 Prompt 不变时复用；
- Prompt 接受后 cache 失效；
- 串行和并发的结果顺序及聚合一致；
- candidate 失败不会修改 work Prompt；
- 未接受 iteration 不运行 heldout；
- final heldout 始终执行。

当前本地测试命令：

```powershell
Set-Location D:\now_to_use\work4icse\rq1\ape_pre\APE
py -m unittest discover -s tests -q
```

远程 GLM 调用和完整三轮实验由用户运行；本地 Agent 负责单元测试、mock smoke test、历史产物离线回放和日志分析。

---

## 13. 当前可用启动参数与注意事项

`ape_pre` 当前支持 `--analysis-batch-size`。`D:\now_to_use\work4icse\rq1\ape` 的新运行时使用过不同参数，二者不要混用。

当前混合模型调用示例：

```powershell
Set-Location D:\now_to_use\work4icse\rq1\ape_pre\APE

py run.py `
  --test-dataset us `
  --iterations 3 `
  --generation-model glm-4.5 `
  --agent-model glm-5.1 `
  --judge-model glm-5.1 `
  --analysis-batch-size 10 `
  --training-batch-strategy stratified `
  --epoch-batch-concurrency 20 `
  --heldout-test-concurrency 20 `
  --validation-gate-size 30 `
  --validation-gate-strategy stratified `
  --validation-gate-seed 20260629 `
  --eval-initial-test `
  --thinking disabled
```

这条命令只表示当前代码支持的参数，不包含尚未实现的：

```text
--acceptance-policy
--validation-repeats
--validation-gate-concurrency
--validation-candidate-concurrency
```

在这些参数真正进入 `run.py --help` 前，不要把它们交给用户运行。

---

## 14. 禁止事项与停止规则

禁止：

- 修改或覆盖真实数据集；
- 修改 official evaluator 以获得更好指标；
- 使用 heldout 内容生成 taxonomy、规则或候选；
- 覆盖 `prompt_runs/` 中已有实验；
- 把 Agent pattern 出现次数直接当成 unique case support；
- 把 dataset/gold convention 表述为普遍 UML 原理；
- 在机制审计完成前把暂定二级机制硬编码进 planner；
- 因 validation 结果不好而临时改变 acceptance metric set；
- 仅凭 temperature=0 假设生成完全确定；
- 为解决效果问题只增加并发。并发只改善耗时。

停止规则：

1. 若 mechanism audit 无类别达到预设证据门槛，停止 Phase 3；
2. 若 baseline 重复运行的自然波动与 candidate delta 同量级，先解决测量稳定性，不进行 Prompt 选择；
3. 若定向机制指标不变，不能声称候选修复了该机制；
4. 若 validation 提升但 heldout 多次重复不稳定，只能报告 validation-local improvement；
5. 若 taxonomy 或 gate 定义在看到 heldout 后发生变化，该轮结果不得作为正式验证结果。

---

## 15. 建议的下一步

下一步不是直接改 gate 或重写 planner，而是先执行 Phase 0：

```text
从现有三轮 run 导出可追溯、去重的 mechanism evidence
-> 人工审计二级机制
-> 冻结 mechanism_taxonomy_v1
-> 再实现 any-improvement + repeated validation
-> 最后实现单机制候选池
```

原因：gate 修改本身较简单，但如果机制定义错误，后续更快、更宽松的 gate 只会更高效地接受不可解释的规则。

## 16. 2026-07-20 保守式第一阶段实施状态

本文前述“待实施”描述是本次修改前的断点。当前工作区已经完成第一阶段：

- failure-analysis case 使用 Python 生成的稳定 `evidence_id`，Agent 输出经过严格 schema 和真实 ID 校验；
- 新增冻结配置 `prompt_workspace/mechanism_taxonomy_v1.json`，只有九个高置信机制可以生成候选；
- failure-analysis 改为逐 pattern 校验；非法项单独审计，不再使无关合法 pattern 整批失效；
- Python 在 localization/editor 之前聚合 validated observations，完成门槛过滤、冲突统计和确定性排序，每轮只选择一个机制；
- 只有 supporting batches 会运行 localization/editor，机制元数据、evidence IDs 和冻结边界由 Python 注入；
- editor/planner 被限制为一个 revision item 和一个 section，rewriter 的非目标 section 变化会被拒绝；
- 默认 acceptance policy 改为三次 paired validation 的 `any-improvement`，旧 gate 保留为 `legacy`；
- 新增独立 validation calibration 模式，推荐阈值只报告、不自动应用；
- 新增 `data_split_summary.json` 和 validation split fingerprint，显式暴露 requested/actual validation 数量；
- 历史 run 已通过只读 exporter 验证：580 patterns、1592 个有效引用、3 个非法引用，产物写入新的 audit run；
- 当前阶段没有实现 Top 3、多 candidate 并发或 heldout 语义调整。

当前本地验证仍使用：

```powershell
py -m unittest discover -s tests -q
```

当前结果：`76 tests OK`。最新四个真实 batch 的只读离线回放保留合法 pattern 数为 `4/6/8/8`，
隔离非法 pattern 数为 `3/1/0/0`，并在 editor 之前选出
`single_action_split_into_unsupported_substeps`（2 batches、4 cases、2 datasets）。
