# APE

APE 是一个基于 Agentic Harness Engineering (AHE) 思路改造的提示词优化项目。
当前优化目标是 UML 活动图生成提示词：系统会用自然语言软件需求评估提示词，
让模型生成 PlantUML 活动图代码，再与参考答案比较，分析失败原因，并让 LLM
改进当前 run 自己的提示词副本。

初始提示词保存在：

```text
prompt_workspace/tst.md
```

每次运行都会把这个初始文件复制到 `prompt_runs/` 下本轮自己的 `work.md`。
训练和迭代只修改这个 run-local 文件，不会覆盖原始 `tst.md`。

## 仓库内容

- `prompt_evolve.py`：独立提示词优化主程序。
- `prompt_workspace/tst.md`：UML 生成 agent 的初始提示词规范。
- `prompt_datasets/lato/`：用于训练/测试划分的 LATO 数据集。
- `evaluators/prompt_uml.py`：PlantUML 语法、结构、节点和控制流关系评估器。
- `tools/plantuml/plantuml-1.2025.4.jar`：本地 PlantUML 校验工具。
- `docs/prompt-evolution.md`：独立提示词优化流程说明。
- `docs/ahe-prompt-uml.md`：AHE-native prompt UML 后端说明。
- `docs/glm51-compat.md`：智谱 GLM 5.1 兼容层说明。

原 AHE 的部分代码仍保留在仓库中，因为当前项目复用了 AHE 的
`evaluate -> analyze -> improve` 思路，只是把被优化组件从 coding-agent
harness 改成了提示词文件。

## 环境配置

建议使用 Python 3.13，因为继承的 AHE 项目声明了 `requires-python >=3.13`。

安装依赖：

```powershell
uv sync
```

真实调用 GLM 时，需要在 PowerShell 中配置智谱 API key：

```powershell
$env:ZHIPU_LLM_API_KEY="your-zhipu-api-key"
$env:ZHIPU_LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
```

不要把 API key 写进 Python、YAML、README、日志或提交记录。

独立的 `prompt_evolve.py` 流程不需要 E2B。E2B 只用于原 AHE/Harbor/E2B
评测后端。

## 快速验证

不调用模型，只验证本地流程：

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve
```

用 GLM 做一个很小的训练 smoke test：

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3
```

指定一个数据集作为测试集，其余数据集作为训练集：

```powershell
python prompt_evolve.py --test-dataset fsd --iterations 3
```

对所有数据集做 leave-one-dataset-out：

```powershell
python prompt_evolve.py --test-dataset all --iterations 3
```

可用数据集名称：

```text
bp, fsd, lmc, pure, rac, us
```

## GLM 兼容

默认模型是 `glm-5.1`。

脚本通过智谱 OpenAI-compatible Chat Completions API 调用模型，并处理以下兼容点：

- `thinking.type` 默认是 `disabled`。
- 除非显式传入 `--do-sample true|false`，否则不发送 `do_sample`。
- 除非显式传入 `--top-p <value>`，否则不发送 `top_p`。
- `max_tokens` 默认使用正数。
- `ZHIPU_LLM_BASE_URL` 可以写 API base URL，脚本会自动拼接 `chat/completions`。

常用覆盖参数：

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3 --llm-timeout 600
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3 --thinking enabled --llm-timeout 900
```

## 更换模型

更换模型不需要改代码。优先级为：命令行参数最高，其次是环境变量，最后是代码里的默认值。

使用另一个智谱 GLM 模型：

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3 --model glm-4.7-flashx
```

也可以给当前 PowerShell 会话设置默认模型：

```powershell
$env:ZHIPU_LLM_MODEL="glm-5.1"
$env:ZHIPU_LLM_API_KEY="your-zhipu-api-key"
$env:ZHIPU_LLM_BASE_URL="https://open.bigmodel.cn/api/paas/v4/"
```

如果要接入其他 OpenAI-compatible provider，需要同时设置模型名和 base URL：

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 3 --model your-model-name --base-url https://your-provider.example.com/v1/
```

当前评估脚本假设后端兼容 Chat Completions 接口。如果 provider 拒绝 GLM 特有字段，
先使用默认参数运行；默认情况下 `thinking` 已关闭，`do_sample` 和 `top_p` 也不会发送。

## 评估方式

每个 case 会比较生成 PlantUML 和参考 PlantUML。当前评估包含：

- 通过本地 PlantUML jar 检查语法。
- 检查活动图结构，包括开始/结束节点、悬空边和不可达节点。
- 对活动节点文本做归一化匹配。
- 对抽取出的语义活动之间的控制流关系做匹配。
- HiGenModel 风格的 PlantUML 编译通过率，字段为 `higen_compilation_pass_rate`。
- 可选的 HiGenModel 风格 LLM-as-judge 节点/关系 P/R/F1，字段为 `llm_node_f1` 和 `llm_relation_f1`。

提示词质量分数为：

```text
0.20 * syntax_pass_rate + 0.40 * node_f1 + 0.40 * relation_f1 - 0.50 * infrastructure_error_rate
```

候选提示词不会因为格式合法就直接采纳。系统会先评估候选提示词，只有当候选
分数比当前提示词至少提升 `--acceptance-min-delta` 时，才会替换本轮 `work.md`。

开启可选 LLM-as-judge 指标的小规模命令：

```powershell
python prompt_evolve.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --higen-llm-metrics
```

LLM judge 默认复用 GLM 相关环境变量，也可以通过 `--higen-judge-model`、
`--higen-judge-api-key` 和 `--higen-judge-base-url` 单独覆盖。

## 输出文件

运行结果保存在 `prompt_runs/`。典型文件包括：

- `prompt_initial.md`
- `work.md`
- `run_args.json`
- `iteration_NNN/train_records.jsonl`
- `iteration_NNN/train_summary.json`
- `iteration_NNN/analysis/overview.md`
- `iteration_NNN/prompt_candidate.md`
- `iteration_NNN/candidate_records.jsonl`
- `iteration_NNN/candidate_summary.json`
- `iteration_NNN/prompt_acceptance.json`
- `iteration_NNN/prompt_after.md`
- `test_records.jsonl`
- `test_summary.json`
- `test_analysis.md`
- `prompt_final.md`

## 说明

这是一个研究实验型工作区。当前实现优先保证提示词迭代过程可复现、可检查，
而不是优先做成完整发布级 Python 包。
