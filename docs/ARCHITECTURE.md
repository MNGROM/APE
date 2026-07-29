# APE 当前架构

## 目标

APE 优化一个把自然语言软件需求转换成 PlantUML activity diagram 的 generation Prompt。
每个 epoch 在 training pool 上发现 input-side generation errors，生成窄 candidate，使用
固定 validation split 做 paired repeated diagnostics，并按 application mode 决定是否写入
run-local Prompt。

## Pipeline

```text
generation
  -> syntax/compiler + LLM element judge
  -> Python numeric findings
  -> Failure Analysis (failure-errors-v2)
  -> taxonomy-blind Error Selector
  -> exact prior-attempt filtering on the same base Prompt
  -> ordered bounded candidate attempts
  -> Prompt Gap Localization
  -> Prompt Editor
  -> Prompt Rewriter (rule_text only)
  -> exact single-section apply
  -> paired repeated validation
  -> diagnostic-apply / cumulative / isolated
  -> heldout audit only when Prompt hash changes
```

`taxonomy-v3` 是当前 CLI 保留的历史 policy 名称；当前候选链路不加载 taxonomy 或 repair
catalog。每个 epoch 的 groups 以 Selector 返回顺序尝试，候选均基于同一 base Prompt，最多
应用一个 candidate。相同 base Prompt 和相同 finding keys 下已确认 `no_prompt_gap` 的 group
在截断 attempt 数量前过滤；语义相似但 finding keys 不同的 group 不做自动过滤。重复出现的
`already_covered` group 会把精确 recurrence 上下文交给 Localization，由现有
`localized/ambiguous/replace_existing` 合同决定是否收紧原有指导。Validation baseline 在
第一个合法 candidate 出现时惰性计算一次。

Localization 只有在唯一现有原文同时覆盖代表样本的 input-side trigger、目标结构修复和
preservation boundary 时才可返回 `already_covered`。主题相关但 trigger 或 correction 不足的
原文通过 `ambiguous + replace_existing` 收紧；“现有指导覆盖”与 `no_prompt_gap` 互斥。

## 代码边界

- `run.py`：CLI、split、batch orchestration、candidate attempts、validation 和 heldout 调度。
- `analysis/failure_analysis.py`：failure report、Failure Analysis 输入/输出和 validator。
- `analysis/error_selector.py`：finding admission、failure error validator、group partition、
  canonical IDs 和 selector 调用。
- `analysis/selector_agents.py`：Localization、Editor、Rewriter 输入辅助和 contract retry。
- `analysis/prompt_rewriter.py`：只接受 `rule_text` 并调用 exact apply。
- `analysis/candidate_registry.py`：run-local candidate 去重、精确 group attempt 历史和 Prompt
  hash。
- `prompt_ops.py`：Prompt section 解析、candidate byte-preservation 和 append/replace apply。
- `evaluation.py`、`metrics.py`、`llm_element_metrics.py`：生成结果评估和指标汇总。

## Prompt 资产

当前运行只使用：

- `prompt_workspace/tst.md`
- `prompt_workspace/failure_analysis_selector_v2.md`
- `prompt_workspace/error_selector_v4.md`
- `prompt_workspace/prompt_gap_localization_v2.md`
- `prompt_workspace/prompt_editor_selector_v2.md`
- `prompt_workspace/prompt_rewriter_selector_v1.md`

## 数据边界

Heldout 不参与 finding、grouping、candidate、阈值校准或 acceptance。Prompt 未变化时不调用
heldout generation/judge，只写 skip manifest。`prompt_runs/`、`prompt_runs_by_dataset/` 和
`baseline_predictions/` 是只读实验产物，本次代码清理不触碰它们。
