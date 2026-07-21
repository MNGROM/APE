# APE

APE 是一个 UML 活动图 PlantUML 生成提示词优化工作区。当前优化对象是
UML 生成 agent 的 markdown prompt。

权威初始提示词是：

```text
prompt_workspace/tst.md
```

每次运行都会把它复制到本次 run 的 `prompt_runs/<run>/work.md`。训练和
迭代只修改这个 run-local `work.md`，不会覆盖 `tst.md`。

## 仓库结构

- `run.py`：主要 batch prompt 优化入口。
- `prompt_evolve.py`：兼容入口，转发到 `run.py`。
- `config.py`：共享路径、默认值和 prompt section 常量。
- `ape_datasets/lato.py`：LATO 数据集加载和采样。
- `llm.py`：OpenAI-compatible `LLMClient`。
- `prediction.py`：UML agent 预测辅助逻辑。
- `metrics.py`：语法、辅助 embedding 和 LLM judge 汇总指标。
- `evaluation.py`：batch 评估流程。
- `analysis/`：失败分析、错误定位和 prompt 编辑 agent。
- `prompt_ops.py`：prompt section 解析和 edit 应用。
- `versioning.py`：run 目录和 prompt 版本文件。
- `prompt_workspace/tst.md`：初始 UML 生成 prompt。
- `prompt_workspace/*_v3.md`：当前默认的原子归因、定位、编辑、规划和片段重写 prompts；无版本文件保留用于旧实验复现。
- `prompt_datasets/lato/`：六个 JSONL 数据集：`bp`、`fsd`、`lmc`、`pure`、`rac`、`us`。
- `llm_element_metrics.py`：PlantUML 编译检查和默认 LLM 语义元素 judge。
- `utils/rate_limit.py`：共享 provider 重试与限流状态记录。
- `tools/plantuml/plantuml-1.2025.4.jar`：本地 PlantUML 语法校验工具。

当前唯一工作流是 `run.py` 的独立 prompt 优化循环。`prompt_evolve.py`
保留为旧命令的兼容入口。

## 环境

建议使用 Python 3.13。

安装依赖：

```powershell
uv sync
```

真实调用模型时，配置一个 OpenAI-compatible chat-completions provider。
默认面向智谱 GLM：

```powershell
$env:ZHIPU_LLM_API_KEY="your-api-key"
$env:ZHIPU_LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
$env:ZHIPU_LLM_MODEL="glm-5.1"
```

旧版 APE 支持按职责拆分模型。下面的配置让 PlantUML prediction 使用较低成本的
`glm-4.5`，而 Failure Analysis、Error Localization、Prompt Editor、Epoch Planner 和
Prompt Rewriter 使用 `glm-5.1`；语义 judge 也使用 `glm-5.1`：

```powershell
python run.py --generation-model glm-4.5 --agent-model glm-5.1 --judge-model glm-5.1
```

不指定这些参数时，三个角色都回退到旧的 `--model`，因此旧命令保持兼容。

PlantUML 生成、所有 evolution agents 和语义 judge 默认都显式发送
`do_sample=false`，使用贪心解码。只有明确需要采样实验时才传
`--do-sample true`；`--do-sample omit` 仅用于恢复服务端默认值并复现旧实验。

`--thinking` 是所有模型调用的默认 thinking 模式。也可以按 agent 细分覆盖：

```powershell
python run.py --test-dataset fsd --thinking disabled --generation-thinking disabled --analysis-thinking enabled --localization-thinking enabled --editor-thinking disabled --judge-thinking disabled
```

细分参数支持 `inherit`、`enabled`、`disabled`。推荐先让 PlantUML 生成、prompt editor
和 LLM judge 的 thinking 保持 `disabled`，只尝试给 failure analysis 和 error localization 开启。

不要把 API key 写进代码、文档、日志或提交记录。

## 快速验证

不调用模型，只验证本地流程：

```powershell
python run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

小规模真实训练：

```powershell
python run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3
```

指定一个数据集为 held-out 测试集，其余五个作为训练集：

```powershell
python run.py --test-dataset fsd --iterations 3
```

如果需要在训练前用原始种子 prompt 得到 held-out 基线指标：

```powershell
python run.py --test-dataset fsd --eval-initial-test
```

该基线会写入 `iteration_000/test`。

六个数据集全部做 leave-one-dataset-out：

```powershell
python run.py --test-dataset all --iterations 3
```

限制样例数量时，训练默认使用分层采样。例如
`--test-dataset fsd --max-train-cases 30` 会从 `bp/lmc/pure/rac/us` 中抽样，
不会只取合并训练集的前缀。

## 工作流

每轮循环如下：

```text
当前 prompt
-> analysis batch 生成 PlantUML
-> 确定性评估
-> batch 失败分析模型
-> Python 逐 attribution 校验并建立 taxonomy evidence inventory
-> Python 跨 batch 聚类、过滤并选择一个机制
-> 仅为支持该机制的 batch 调用错误定位和 prompt editor
-> epoch planner 只合并被选机制的 batch revision plans
-> prompt rewriter 只输出 rule fragment，Python 确定性组装下一版 prompt
-> 固定 validation gate 评估并接收/拒绝 candidate
-> held-out test 评估
```

默认会先从采样后的训练池中固定留出 validation gate（`--validation-gate-size 30`，
小样本 run 会限制在采样训练池的大约三分之一以内）。这些样例不会进入
failure analysis 或 prompt evolution agents。epoch candidate 必须先通过这组
固定 validation gate，才会更新 `work.md`。

一个 epoch 内的 training batches 可以用 `--epoch-batch-concurrency N` 并发处理；
默认 `N=1` 保持串行行为。所有 batch 都使用同一个 epoch 起始 prompt，完成 failure analysis 后再由
Python 默认按 `prompt_workspace/mechanism_taxonomy_v3.json` 对 exact atomic signature 聚类 validated observations；
taxonomy v1/v2 保留用于旧实验复现。只有满足 batch、unique case、dataset 和方向一致性门槛的机制才会
进入 localization。现有 supporting-batch localization 结果还必须在同一 section 达到严格多数 Prompt gap，
才会送入 epoch planner。非 supporting batches 不调用 localization/editor，planner 不负责统计 support 或选择机制。

failure analysis v3 按 attribution 独立校验。每个 attribution 只绑定一个 case 的一个 exact evaluator anchor；
非法 attribution 单独审计，其他合法 attribution 继续参与聚类。只有 primary、trigger-grounded、matching 可一一对应的
attribution 参与 support 计数，secondary 或多 signature 冲突的 attribution 只作诊断。机制 ID、signature、attribution/evidence IDs 和
taxonomy 冻结的 positive/negative boundaries 都由 Python 推导或注入，Agent 不能声明或覆盖。
为控制结构化输出规模，Python 每个 v3 batch 最多准入 12 个 anchor：先在 case 内按 compiler/syntax、direct node 和
Node/Relation P/R deficit 排序，再跨 case 轮询。该预算不改变 mechanism promotion threshold。

prompt editor 不能任意重写文件。它只能返回针对 `tst.md` 固定 section 的
JSON edits：

```text
## agent task
## input
## output
## workflow
## knowledge
## rule
```

prompt editor、epoch planner 和 prompt rewriter 都被限制为一个机制、一个 revision item
和一个 section。rewriter 只返回 `rule_text`；Python 只在目标 section 的唯一连续 span 上替换或追加，并拒绝其他 section 的变化。

## 评估

训练和 candidate acceptance 的主指标是 LLM judge 语义指标：

- `llm_node_f1` (`LLM-N-F1`)
- `llm_relation_f1` (`LLM-R-F1`)
- `plantuml_compilation_pass_rate`：本地 PlantUML 编译通过率。

embedding/difflib 指标默认关闭，只能通过 `--embedding-element-metrics`
作为辅助诊断开启：

- `node_f1` (`N-F1`)：活动/条件节点匹配。
- `relation_f1` (`R-F1`)：控制流关系匹配。

便宜本地测试可关闭 LLM judge：

```powershell
python run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

默认 gate 是重复验证后的析取式 `any-improvement`：

```text
mean(Node F1 delta) > configured minimum 且至少 2/3 repeats 上升
OR mean(Relation F1 delta) > configured minimum 且至少 2/3 repeats 上升
```

Compile 和其他性能变化只记录，不能接受或否决 candidate。Prompt 超长、基础设施错误或获胜指标没有完成
所有 paired repeats 属于无效测量，仍会拒绝。默认参数：

```text
--acceptance-policy any-improvement
--validation-repeats 3
--acceptance-min-wins 2
```

旧 Safety/Benefit/Bootstrap gate 保留在 `--acceptance-policy legacy` 下用于复现。
同一 epoch 的 baseline repeats 只生成一次；下一 epoch 即使 Prompt 未变也会重新生成。

正式运行前先校准自然波动：

```powershell
python run.py --test-dataset us --calibrate-validation-only --validation-calibration-repeats 5
```

校准只运行 seed Prompt 的 fixed validation，不训练也不运行 heldout；建议阈值只写报告，
不会自动应用。Compile 校准只作诊断；`data_split_summary.json` 和校准报告包含实际 validation 数量及 split fingerprint；
正式实验必须使用相同 split 配置并显式传入 Node 和 Relation 两个 min-delta。
held-out 测试写入 `iteration_NNN/test`；全部训练结束后不再额外重复运行一次
root-level held-out test。

## 输出

运行结果在 `prompt_runs/` 下。重点文件：

- `run_args.json`：脱敏后的运行配置。
- `data_split_summary.json`：实际 split 数量、dataset 分布和 validation fingerprint。
- `train_pool_cases.json`：validation split 前的采样训练池。
- `train_cases.json`：真正进入 prompt evolution agents 的训练 case。
- `validation_gate_cases.json`：从训练池中固定留出的 validation gate case。
- `test_cases.json`：held-out test case。
- `prompt_evolution.md`：本次 run 的 prompt 演化总览，集中查看初始 prompt、每轮变更入口、best/final prompt。
- `metrics_overview.md`：本次 run 的指标总览，集中查看 `iteration_NNN/test` held-out 指标。
- `iteration_NNN/batches/analysis_cases.json`：本轮实际评估的 optimization cases。
- `iteration_NNN/evaluation/analysis_records.jsonl`：optimization cases 的生成结果和指标。
- `iteration_NNN/evaluation/analysis_summary.json`：optimization cases 汇总指标。
- `iteration_NNN/reports/prompt_change.md`：单轮 prompt 变化报告，包含 before/after diff、candidate 是否接受和拒绝原因。
- `iteration_NNN/reports/metrics_report.md`：单轮指标报告，包含 analysis、validation/gate baseline、candidate 和 delta。
- `iteration_NNN/evaluation/analysis_overview.md`：人工可读失败报告。
- `iteration_NNN/agents/failure_analysis.input.json`：发送给失败分析模型的输入。
- `iteration_NNN/agents/failure_analysis.output.json`：结构化失败分析输出。
- `iteration_NNN/agents/error_localization.input.json`：发送给错误原因定位模型的输入。
- `iteration_NNN/agents/error_localization.output.json`：section 级错误定位输出。
- `iteration_NNN/agents/prompt_editor.input.json`：发送给 prompt editor 的输入，包含失败分析和错误定位。
- `iteration_NNN/agents/prompt_editor.output.json`：结构化 prompt edit 输出。
- `iteration_NNN/train_batches/batch_NNN/agents/failure_analysis.output.raw.txt`：failure-analysis 原始输出。
- `iteration_NNN/train_batches/batch_NNN/agents/failure_analysis.rejected_patterns.json`：兼容文件名；v3 内容为逐 attribution 拒绝审计。
- `iteration_NNN/train_batches/batch_NNN/mechanisms/evidence.json`：batch-local validated observations。
- `iteration_NNN/mechanisms/evidence_inventory.json`：epoch 级完整 evidence inventory。
- `iteration_NNN/mechanisms/clusters.json`、`selected.json`：Python 聚类、过滤和唯一机制选择。
- `iteration_NNN/mechanisms/attribution_lineage.json`：attribution 到 local plan、final fragment 和 acceptance 的 lineage。
- `iteration_NNN/mechanisms/prompt_gap_consensus.json`：supporting batches 的 localization/editor 票、严格多数门槛、目标 section 和 abstention 原因。
- `iteration_NNN/prompts/candidate.md`：prompt rewriter 输出的候选 prompt。
- `iteration_NNN/validation_gate/cases.json`：本轮 candidate acceptance 使用的固定 validation case。
- `iteration_NNN/validation_gate/baseline_records.jsonl`、`iteration_NNN/validation_gate/baseline_summary.json`：当前 prompt 的 validation baseline。
- `iteration_NNN/validation_gate/candidate_records.jsonl`、`iteration_NNN/validation_gate/candidate_summary.json`：candidate prompt 的 validation 结果。
- `iteration_NNN/validation_gate/repeat_NNN/`、`aggregate_summary.json`：paired repeats 和稳定收益统计。
- `iteration_NNN/validation_gate/impact_summary.json`、`impact_report.md`：repeat/case/dataset 级 Node/Relation P/R/F1 delta，仅作诊断。
- `iteration_NNN/decision/acceptance.json`：prompt 更新决策，核心字段是 `accepted: true/false` 和拒绝原因。
- `iteration_000/test/summary.json`、`iteration_000/test/analysis.md`：使用 `--eval-initial-test` 时生成的原始 prompt held-out 基线结果。
- `iteration_NNN/test/summary.json`、`iteration_NNN/test/analysis.md`：每轮 held-out 测试结果。
- `prompt_final.md`：训练结束后的 current prompt。
- `run_state.json`、`rate_limit_events.jsonl`：provider 重试状态和事件流。

旧 run 的 batch-local `supporting_cases` 可以只读导出到一个新的 audit run：

```powershell
py scripts\export_mechanism_evidence.py prompt_runs\<source-run>
```

导出器不会修改 source run；它生成 `mechanism_evidence.jsonl`、人工审计 CSV、
非法引用日志和汇总报告。

已完成的历史 run 可以用下面的命令补生成这几个人类可读报告：

```powershell
python run.py --refresh-reports .\prompt_runs\<run-name>
```

不传 `RUN_DIR` 时会刷新 `prompt_runs/` 下所有 run：

```powershell
python run.py --refresh-reports
```
