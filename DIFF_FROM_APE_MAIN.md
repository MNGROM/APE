# Diff From ape_main

本文档记录当前 `ape` 相对 `ape_main` 的主要修改，方便后续回溯实验设计。

对比基线：

```text
ape_main: d2ae976 Checkpoint before epoch batch evolution
ape: epoch-batch-online-training / 5027f5d Archive epoch training workflow state + 当前工作区修改
```

说明：本文聚焦源码、prompt、文档和测试，不统计 `prompt_runs/`、`__pycache__/` 等运行产物。

## 总览

当前 `ape` 不再只是 batch-local prompt evolution，而是改成了以 epoch-level prompt revision、fixed validation gate 和更硬 acceptance gate 为核心的实验框架。

粗略差异：

```text
21 个已跟踪文件变化
约 +2540 / -711 行
另有当前未跟踪测试文件：
- tests/test_prompt_editor.py
- tests/test_prompt_ops.py
```

## 主流程变化

### 1. 训练更新模式

`run.py` 新增两种训练更新模式：

```text
--training-update-mode epoch
--training-update-mode online
```

默认是 `epoch`。

`epoch` 模式流程：

```text
训练集分 batch
-> 每个 batch 做 evaluation / failure_analysis / error_localization / prompt_editor
-> 收集 batch-local revision_plan
-> epoch_planner 合并多个 batch plan
-> prompt_rewriter 生成一个 epoch candidate
-> fixed validation gate 接收或拒绝
-> 每轮 held-out test
```

`online` 模式仍保留 batch 级即时更新，但默认也会使用 fixed validation gate。

### 2. Fixed validation gate

新增固定 validation gate split：

```text
--validation-gate
--validation-gate-size
--validation-gate-strategy
--validation-gate-seed
```

训练池现在会拆成：

```text
train_pool_cases.json
train_cases.json
validation_gate_cases.json
test_cases.json
```

validation cases 不参与 failure analysis、error localization、prompt editor 或 epoch planner，只用于 candidate acceptance。

小样本时，validation gate 会被限制在训练池约三分之一以内。

### 3. Acceptance gate 重写

旧版本支持 `acceptance_metric_source`，可以用 deterministic / LLM / hybrid 指标驱动接收。

当前版本改成：

```text
deterministic node_f1 / relation_f1 是主收益指标
LLM metrics 只作为可选语义回退 guard
syntax / compile / precision / infrastructure 进入 safety gate
```

标准 gate 要求：

```text
syntax_pass_rate 不显著下降
plantuml_compilation_pass_rate 不显著下降
node_f1 不显著下降
relation_f1 不显著下降
node_precision 不显著下降
relation_precision 不显著下降
LLM semantic guard 通过（如果 LLM metrics 可用）
infrastructure_error_rate 不增加
prompt size 通过
```

Benefit gate 至少满足一个：

```text
relation_f1 提升
node_f1 提升
compile 提升且 node/relation F1 不回退
```

另有 bootstrap 例外：首次 accepted update 前，如果 deterministic node/relation F1 都强提升，可以容忍较小 syntax/compile 回退。

## Agent 和 Prompt 变化

### 1. 新增 epoch planner

新增：

```text
analysis/epoch_planner.py
prompt_workspace/epoch_planner.md
```

职责：把多个 batch-local revision plan 合并成一个保守的 epoch-level revision plan。

### 2. Prompt editor 输入新增 edit_budget

`prompt_editor` 和 `epoch_planner` 的输入 payload 现在包含：

```json
"edit_budget": {
  "max_revision_items": 1,
  "guidance": [
    "..."
  ]
}
```

预算由程序决定并用于校验：

```text
首次 accepted update 前：--initial-max-sections-per-edit 3
首次 accepted update 后：--max-sections-per-edit 1
```

对应修改：

```text
analysis/prompt_editor.py
analysis/epoch_planner.py
prompt_workspace/prompt_editor.md
prompt_workspace/epoch_planner.md
run.py
```

### 3. revision_plan schema 扩展

`prompt_ops.py` 中扩展了 revision plan item schema。

当前推荐格式：

```json
{
  "section": "knowledge",
  "operation": "qualify_existing",
  "text_to_modify": "Use fork only for explicit parallel work.",
  "intent": "Tighten fork/join modeling knowledge.",
  "change_instruction": "Revise the existing fork guidance to exclude ordinary lists, alternatives, attributes, and sequential UI steps unless the requirement explicitly states parallel or simultaneous execution."
}
```

允许的 `operation`：

```text
append_new
replace_existing
qualify_existing
merge_existing
```

规则：

```text
operation 缺失时，normalize 为 append_new，保持旧格式兼容。
replace_existing / qualify_existing / merge_existing 必须提供非空 text_to_modify。
暂时不检查 text_to_modify 是否 exact match 当前 prompt 原文。
```

### 4. Prompt rewriter length constraints

`prompt_rewriter` 输入现在可包含 `candidate_constraints`，用于告诉 rewriter 候选 prompt 的字符预算。

相关文件：

```text
analysis/prompt_rewriter.py
prompt_workspace/prompt_rewriter.md
run.py
```

注意：当前没有改成结构化 patch，rewriter 仍输出完整 `candidate_prompt`。

## 报告与输出变化

### 1. Iteration-level held-out test

现在每轮训练后都会将 held-out test 写入：

```text
iteration_NNN/test/records.jsonl
iteration_NNN/test/summary.json
iteration_NNN/test/analysis.md
```

如果启用 `--eval-initial-test`，原始 seed prompt 基线写入：

```text
iteration_000/test/
```

### 2. Run-level overview

`reporting.py` 更新后，`metrics_overview.md` 优先展示：

```text
iteration_000:test
iteration_001:test
iteration_002:test
...
```

而不是混入 analysis/gate 指标。

### 3. Validation gate report

每轮 candidate acceptance 的固定 validation gate 输出：

```text
iteration_NNN/validation_gate/cases.json
iteration_NNN/validation_gate/baseline_records.jsonl
iteration_NNN/validation_gate/baseline_summary.json
iteration_NNN/validation_gate/candidate_records.jsonl
iteration_NNN/validation_gate/candidate_summary.json
iteration_NNN/validation_gate/analysis.md
iteration_NNN/decision/acceptance.json
```

### 4. Held-out metric plot

新增：

```text
iteration_test_metrics.csv
iteration_test_metrics.png
```

因此 `pyproject.toml` 增加：

```text
matplotlib>=3.8
```

## 新增工具

新增：

```text
eval_seed_prompt_all.py
```

用途：固定评估 `prompt_workspace/tst.md` 在所有 LATO 数据集上的 baseline，不执行 prompt evolution。

相关忽略项：

```text
seed_prompt_runs/
```

## 文档变化

主要更新：

```text
README.md
README_zh.md
KNOWN_ISSUES.md
ISSUE_best_prompt_selection.md
```

重点变化：

- 记录 epoch-level workflow。
- 记录 fixed validation gate。
- 记录新的 acceptance gate 规则。
- 将 batch-local best prompt selection 问题标记为 resolved。
- 说明新 runs 使用 final current prompt，而不是 batch-local `prompt_best.md` 驱动最终测试。

## 测试变化

新增或大改测试覆盖：

```text
tests/test_acceptance_gate.py
tests/test_epoch_planner.py
tests/test_prompt_editor.py
tests/test_prompt_ops.py
tests/test_reporting.py
tests/test_training_batches.py
```

覆盖内容：

- acceptance gate 的 deterministic benefit、LLM guard、precision regression、bootstrap。
- epoch planner payload 和默认 epoch 模式。
- edit_budget 输入与超预算拒绝。
- revision_plan operation / text_to_modify schema。
- fixed validation split。
- stratified training batches。
- metrics overview 使用 iteration-level held-out test。

当前本地验证命令：

```powershell
python -m unittest discover -s tests
```

当前结果：

```text
30 tests OK
```

测试中出现的日志：

```text
[evolve] Rejected prompt revision plan: At most 1 sections may be revised
```

这是超预算拒绝测试触发的预期日志，不代表测试失败。

## 当前未处理或暂缓的问题

以下内容已经讨论过，但当前没有实现：

- 多候选 prompt 生成与选择。
- 两级 validation gate。
- rejected candidate 信息回灌下一轮 planner。
- 禁止 refinement 阶段使用 `append_new`。
- 校验 `text_to_modify` 是否真的出现在当前 prompt section 中。
- 将 prompt rewrite 改成结构化 patch。

已完成：

- 移除 prompt growth ratio 硬门槛，只保留绝对字符数上限 `--max-prompt-chars`。
