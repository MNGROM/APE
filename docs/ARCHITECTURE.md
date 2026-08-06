# APE 当前架构

## 目标

APE 优化一个把自然语言软件需求转换成 PlantUML activity diagram 的 generation Prompt。
每个 epoch 在 training pool 上发现 input-side generation errors，生成窄 candidate，使用
固定 Gate1 做 paired repeated diagnostics，并对 Gate1-passing candidate 在独立 Gate2 split
上做 fresh paired repeats；按 application mode 决定是否写入 run-local Prompt。

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
  -> paired repeated Gate1
  -> fresh paired repeated Gate2 when Gate1 passes
  -> diagnostic-apply / cumulative / isolated
  -> heldout audit only when Prompt hash changes
```

`taxonomy-v3` 是当前 CLI 保留的历史 policy 名称；当前候选链路不加载 taxonomy 或 repair
catalog。每个 epoch 的 groups 以 Selector 返回顺序尝试，候选均基于同一 base Prompt，最多
应用一个 candidate。相同 base Prompt 和相同 finding keys 下已确认 `no_prompt_gap` 的 group
在截断 attempt 数量前过滤；语义相似但 finding keys 不同的 group 不做自动过滤。重复出现的
`already_covered` group 会把精确 recurrence 上下文交给 Localization，由现有
`localized/ambiguous/replace_existing` 合同决定是否收紧原有指导。Gate1 baseline 在第一个合法
candidate 出现时惰性计算一次，并在同一 epoch 内复用；Gate2 baseline 不复用，对每个
Gate1-passing candidate 与 candidate measurement 一起 fresh evaluation。

Localization 只有在唯一现有原文同时覆盖代表样本的 input-side trigger、目标结构修复和
preservation boundary 时才可返回 `already_covered`。主题相关但 trigger 或 correction 不足的
原文通过 `ambiguous + replace_existing` 收紧；“现有指导覆盖”与 `no_prompt_gap` 互斥。

Gate1 和 Gate2 按 selected group 的 validated anchor kinds 使用同一无阈值 acceptance 合同。
Python 将 node findings 映射到 `llm_node_f1`、relation findings 映射到
`llm_relation_f1`、混合 semantic group 映射到两项、compile findings 映射到
`plantuml_compilation_pass_rate`。所有 required metrics 的 repeated mean delta 都必须严格
大于 `0`，不相关指标不能代偿，只保留在诊断报告中。不设置 `min_delta`、`min_wins`、
non-regression floor 或其他允许回退的人工阈值；缺少任一 required measurement 时 evaluation
invalid。`syntax_error` 与 `compile_error` 合并为 compile evidence family，可以同组；compile
finding 不与 semantic finding 混组。`syntax_pass_rate` 只保留在评估和报告中，不参与
acceptance。

除非用户主动明确授权，后续不得重新添加最小提升、最小 wins、semantic/compile floor 或
任何等价的数值回退阈值；validation calibration 只能描述重复波动，不能生成或应用阈值。

Gate1 和 Gate2 从非 heldout training pool 使用独立 seed 固定分层划出，彼此不重叠，也不进入
candidate discovery。只有 Gate1 通过才运行 Gate2；只有两关都通过，`cumulative` 才能应用
candidate。Gate2 失败后继续当前 frozen base Prompt 的下一 group，且不运行 heldout。Gate2
默认启用，此时 `auto` 解析为 `cumulative`，并拒绝
`diagnostic-apply`；显式 `--no-gate2` 才保留旧诊断应用语义。

正式 paired run 可使用 `--stop-after-first-apply` 隔离单个 Prompt 更新。该开关不改变 Gate
或 application decision；首个 candidate 应用后仍完成对应 heldout audit 或 skip manifest，
随后停止创建新的 epoch。没有 candidate 应用时，运行继续到配置的 iteration 上限。

Heldout 支持显式 `--heldout-repeats`，默认 `1`。每次审计在固定 test manifest 上保存独立
repeat 产物，`test/summary.json` 保存全部 repeats 的聚合均值，`test/repeats.json` 保存逐次
summary 和 split fingerprint。heldout repeats 只描述 generation/Judge 波动，不扩大数据集，
也不参与 candidate 或 application decision；`--stop-after-first-apply` 必须等待全部 repeats
完成后才终止。

跨数据集迁移审计位于 `scripts/`，只读连接 candidate evidence、数据集 evidence funnel、
Gate per-dataset delta、recorded/required-metric counterfactual decision 和 heldout delta。
它可以同时报告等域宏平均与按 discovery training pool 份额计算的 weighted 平均，但所有
派生结论都不改写 run-local acceptance；历史 `prompt_runs/` 始终保持只读。

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

以上 Prompt 资产的文本修改必须先提交精确 diff 并获得用户明确审核批准；代码、测试或文档
修改授权不自动授权 Prompt 修改。

## 数据边界

Gate1、Gate2 和 heldout 三者互不重叠。前两者从非 heldout training pool
划出并从 candidate discovery 中排除；heldout 不参与 finding、grouping、candidate、阈值校准
或 acceptance。Prompt 未变化时不调用 heldout generation/judge，只写 skip manifest。
`prompt_runs/`、`prompt_runs_by_dataset/` 和 `baseline_predictions/` 是只读实验产物，本次代码
修改不触碰它们。

## 解码配置

generation、Failure Analysis、Selector、Localization、Editor/Rewriter、LLM Judge 和 element
extraction 的 temperature 统一固定为 `0`。CLI 对这些选项提供 `0` 默认值，并在 orchestration
启动、任何真实模型调用发生前拒绝非零值。历史 run 的非零 temperature 不定义当前行为。

## Provider 配置

APE 的 generation、agent 和 semantic judge 共用 OpenAI-compatible transport，目前支持
`zhipu` 与 `deepseek`。`config.py` 负责从 `APE_LLM_PROVIDER` 和 provider 对应环境变量解析
API key、base URL、shared model、role model 与 thinking mode；所有入口复用同一解析结果。

DeepSeek 默认使用 `https://api.deepseek.com/chat/completions`，Bearer 鉴权和
`choices[0].message.content` 响应结构与现有客户端兼容；`DEEPSEEK_BASE_URL` 可用于受控
代理或兼容 endpoint。其请求体发送 `model`、
`messages`、`temperature=0`、`max_tokens`、`stream=false` 和显式 thinking mode，但省略
DeepSeek schema 未定义的 `do_sample`。Zhipu 路径继续使用 `do_sample=false`。resolved
provider、base URL 和各 role model 写入 `run_args.json`，凭据只记录存在性。
