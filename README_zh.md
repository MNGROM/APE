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
-> 程序应用合法 edits
-> gate batch 评估候选 prompt
-> 接受或拒绝候选 prompt
```

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

默认每轮最多修改两个 section：

```text
--max-sections-per-edit 2
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

候选接收不再使用加权总分，而是使用多指标门控。

Safety Gate 全部通过后，才会进入 Benefit Gate：

```text
plantuml_compile_delta >= -0.05
node_f1_delta >= -0.02
relation_f1_delta >= -0.01
N-F1 和 R-F1 不能同时下降
infrastructure_error_delta <= 0
prompt_size_ok
```

Benefit Gate 至少满足一项才接收：

```text
relation_f1_delta >= 0.01
或 node_f1_delta >= 0.02
或 plantuml_compile_delta >= 0.05 且 N-F1/R-F1 都不下降
```

这样编译率提升不能单独抵消节点和关系质量的回退。

第 1 轮有 bootstrap 例外：如果 `N-F1` 和 `R-F1` 都达到明显提升
（默认分别为 `+0.02` 和 `+0.01`），且没有新增基础设施错误、prompt 未超长，
则可以接收。后续轮次使用上面的标准门控。
最终 held-out 测试默认使用训练中表现最好的 prompt。

## 输出

运行结果在 `prompt_runs/` 下。重点文件：

- `run_args.json`：脱敏后的运行配置。
- `train_cases.json`、`test_cases.json`：实际采样 case。
- `prompt_evolution.md`：本次 run 的 prompt 演化总览，集中查看初始 prompt、每轮变更入口、best/final prompt。
- `metrics_overview.md`：本次 run 的指标总览，集中查看每轮 analysis/gate/candidate 以及 held-out test 指标。
- `iteration_NNN/analysis_batch_cases.json`：失败分析 batch。
- `iteration_NNN/predictions.jsonl`：analysis batch 的生成结果和指标。
- `iteration_NNN/evaluation_summary.json`：analysis batch 汇总指标。
- `iteration_NNN/prompt_change.md`：单轮 prompt 变化报告，包含 before/after diff、candidate 是否接受和拒绝原因。
- `iteration_NNN/metrics_report.md`：单轮指标报告，包含 analysis、baseline gate、candidate gate 和 delta。
- `iteration_NNN/analysis/overview.md`：人工可读失败报告。
- `iteration_NNN/failure_analysis_input.json`：发送给失败分析模型的输入。
- `iteration_NNN/failure_analysis_output.json`：结构化失败分析输出。
- `iteration_NNN/error_localization_input.json`：发送给错误原因定位模型的输入。
- `iteration_NNN/error_localization_output.json`：section 级错误定位输出。
- `iteration_NNN/prompt_edit_input.json`：发送给 prompt editor 的输入，包含失败分析和错误定位。
- `iteration_NNN/prompt_edit_output.json`：结构化 prompt edit 输出。
- `iteration_NNN/candidate_prompt.md`：应用 edits 后的候选 prompt。
- `iteration_NNN/gate_cases.json`：gate batch 样例。
- `iteration_NNN/gate_predictions.jsonl`：candidate gate 生成结果和指标。
- `iteration_NNN/gate_summary.json`：candidate gate 汇总。
- `iteration_NNN/prompt_acceptance.json`：接收/拒绝决策，包含 `safety_gate`、`benefit_gate` 和 `rejection_reasons`。
- `prompt_final.md`：训练结束后的 current prompt，也是最终测试使用的 prompt。
- `test_summary.json`、`test_analysis.md`：held-out 测试结果。
- `run_state.json`、`rate_limit_events.jsonl`：provider 重试状态和事件流。

已完成的历史 run 可以用下面的命令补生成这几个人类可读报告：

```powershell
python run.py --refresh-reports .\prompt_runs\<run-name>
```

不传 `RUN_DIR` 时会刷新 `prompt_runs/` 下所有 run：

```powershell
python run.py --refresh-reports
```
