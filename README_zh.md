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
- `metrics.py`：确定性语法、节点、关系和分数指标。
- `evaluation.py`：batch 评估流程。
- `analysis/`：失败分析、错误定位和 prompt 编辑 agent。
- `prompt_ops.py`：prompt section 解析和 edit 应用。
- `versioning.py`：run 目录和 prompt 版本文件。
- `prompt_workspace/tst.md`：初始 UML 生成 prompt。
- `prompt_workspace/failure_analysis.md`：失败分析模型的 system prompt。
- `prompt_workspace/error_localization.md`：错误原因定位模型的 system prompt。
- `prompt_workspace/prompt_editor.md`：结构化 prompt 编辑模型的 system prompt。
- `prompt_datasets/lato/`：六个 JSONL 数据集：`bp`、`fsd`、`lmc`、`pure`、`rac`、`us`。
- `llm_element_metrics.py`：PlantUML 编译检查和可选 LLM 语义元素 judge。
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

`--thinking` 是所有模型调用的默认 thinking 模式。也可以按 agent 细分覆盖：

```powershell
python run.py --test-dataset fsd --thinking disabled --generation-thinking disabled --analysis-thinking enabled --localization-thinking enabled --editor-thinking disabled --judge-thinking disabled --no-llm-element-metrics
```

细分参数支持 `inherit`、`enabled`、`disabled`。推荐先让 PlantUML 生成、prompt editor
和 LLM judge 保持 `disabled`，只尝试给 failure analysis 和 error localization 开启。

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
-> 错误原因定位模型把失败映射到 prompt section
-> prompt editor 模型输出结构化 section edits
-> epoch planner 合并 batch revision plans
-> prompt rewriter 输出下一版 prompt
-> 固定 validation gate 评估并接收/拒绝 candidate
-> held-out test 评估
```

默认会先从采样后的训练池中固定留出 validation gate（`--validation-gate-size 30`，
小样本 run 会限制在采样训练池的大约三分之一以内）。这些样例不会进入
failure analysis 或 prompt evolution agents。epoch candidate 必须先通过这组
固定 validation gate，才会更新 `work.md`。

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

epoch planner 会应用最终合并 revision plan 的 section 数量预算：

```text
--initial-max-sections-per-edit 3
--max-sections-per-edit 1
```

## 评估

主要确定性指标：

- `node_f1` (`N-F1`)：活动/条件节点匹配。
- `relation_f1` (`R-F1`)：控制流关系匹配。
- `plantuml_compilation_pass_rate`：本地 PlantUML 编译通过率。

可选 LLM 语义指标：

- `llm_node_f1` (`LLM-N-F1`)
- `llm_relation_f1` (`LLM-R-F1`)

便宜本地测试可关闭 LLM judge：

```powershell
python run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

候选接收不再使用加权总分，而是在 validation gate 汇总指标上直接做
accept/reject 决策。

Safety Gate 全部通过后，才会进入 Benefit Gate：

```text
syntax_pass_rate_delta >= -0.01
plantuml_compile_delta >= -0.01
node_f1_delta >= -0.01
relation_f1_delta >= -0.01
node_precision_delta >= -0.02
relation_precision_delta >= -0.02
如果 LLM node/relation F1 可用，不能超过语义回退 guard
infrastructure_error_delta <= 0
prompt_size_ok
```

Benefit Gate 至少满足一项才接收：

```text
relation_f1_delta >= 0.02
或 node_f1_delta >= 0.02
或 plantuml_compile_delta >= 0.05 且 node/relation F1 都不下降
```

这样编译率提升不能单独抵消节点和关系质量的回退。

第 1 轮有 bootstrap 例外：如果 `N-F1` 和 `R-F1` 都达到明显提升
（默认都是 `+0.05`），syntax/compile pass rate 仍在放宽容忍范围内
（默认 `-0.10`），没有新增基础设施错误、可用的 LLM 指标不回退、
prompt 未超过绝对字符数上限 `--max-prompt-chars`，则可以接收。后续轮次使用上面的标准门控。
held-out 测试写入 `iteration_NNN/test`；全部训练结束后不再额外重复运行一次
root-level held-out test。

## 输出

运行结果在 `prompt_runs/` 下。重点文件：

- `run_args.json`：脱敏后的运行配置。
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
- `iteration_NNN/prompts/candidate.md`：prompt rewriter 输出的候选 prompt。
- `iteration_NNN/validation_gate/cases.json`：本轮 candidate acceptance 使用的固定 validation case。
- `iteration_NNN/validation_gate/baseline_records.jsonl`、`iteration_NNN/validation_gate/baseline_summary.json`：当前 prompt 的 validation baseline。
- `iteration_NNN/validation_gate/candidate_records.jsonl`、`iteration_NNN/validation_gate/candidate_summary.json`：candidate prompt 的 validation 结果。
- `iteration_NNN/decision/acceptance.json`：prompt 更新决策，核心字段是 `accepted: true/false` 和拒绝原因。
- `iteration_000/test/summary.json`、`iteration_000/test/analysis.md`：使用 `--eval-initial-test` 时生成的原始 prompt held-out 基线结果。
- `iteration_NNN/test/summary.json`、`iteration_NNN/test/analysis.md`：每轮 held-out 测试结果。
- `prompt_final.md`：训练结束后的 current prompt。
- `run_state.json`、`rate_limit_events.jsonl`：provider 重试状态和事件流。

已完成的历史 run 可以用下面的命令补生成这几个人类可读报告：

```powershell
python run.py --refresh-reports .\prompt_runs\<run-name>
```

不传 `RUN_DIR` 时会刷新 `prompt_runs/` 下所有 run：

```powershell
python run.py --refresh-reports
```
