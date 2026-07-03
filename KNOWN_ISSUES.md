# APE 待解决问题与设计备忘

本文档记录当前代码理解阶段发现的工程问题、评估风险和后续设计方向。当前阶段只作为备忘，不代表已经实现。

## 1. prompt_editor 修改 section 数量限制（已处理）

当前 `analysis/prompt_editor.py::propose_prompt_revision` 不再按 `max_revision_items` 硬拒绝 section 数量，只做 `revision_plan` schema 和重复 section 校验。`prompt_editor` 输入中的 `edit_budget` 现在只提供 guidance；`epoch_planner` 仍使用 `max_revision_items` 约束最终 epoch-level revision plan。

仍需注意：

- `revision_plan` 中同一个 section 仍然只能出现一次。
- 如果后续要恢复 section 数量限制，应放回 `epoch_planner`，而不是 `prompt_editor`。

## 2. failure_analysis 输出 schema 校验不足

当前 `analysis/failure_analysis.py::analyze_failures` 只要求模型输出能被 `prompt_ops.extract_json_object` 解析成 JSON object。

问题：

- 没有校验 `error_patterns` 是否存在。
- 没有校验每个 pattern 是否包含 `name`、`problem`、`possible_causes`。
- 后续 `error_localization` 和 `prompt_editor` 会直接消费该 JSON，低质量或结构偏离的输出可能继续传播。

建议：

- 新增 `validate_failure_analysis_payload`。
- 至少校验：
  - `error_patterns` 是非空 list；
  - 每项是 object；
  - `name` 和 `problem` 是非空 string；
  - `possible_causes` 是 string list，允许为空但不允许类型错误。

## 3. PlantUML parser 能力不足

当前 deterministic parser 主要在 `metrics.py::extract_activity_graph` 中实现，已经支持常见 activity、if/else、switch/case、while、repeat、fork、split、state 和基础 transition。

已修复：

- 已增加对 `fork end` 的识别，使其与 `end fork` 等价。
- 已改进 transition 解析，支持 `-[bold]->`、`-[#color]->`、`-[dashed]->` 等 styled arrow，避免把样式文本吞进 source 或 target。
- 已处理 `-> label;` 这类无显式 source 的 PlantUML shorthand，将 label 应用于下一条关系。
- 已为上述语法加入最小 parser 回归测试。

仍需观察的风险：

- 复杂嵌套 fork、条件内 fork、PlantUML shorthand branch 和 merge 语义可能与真实图不一致。
- `elseif` / `else if` 链式条件目前是近似解析，后续条件可能被挂回最初的 `if` 条件，而不是沿 false/else path 串接到前一个条件。该问题主要影响 relation source/target 的准确性，进而影响 relation precision/recall。
- 最新 gold parser diagnostics 显示，`rac` 数据集 20 条中有 15 条使用 `elseif`，该风险主要集中在 RAC；`fsd` gold 基本不使用 `elseif`，当前 FSD 低分更可能来自生成 PlantUML 的活动粒度和结构差异。
- parser 越补越复杂，长期维护成本会上升。

后续建议：

- 继续补充来自真实 gold/pred PlantUML 的失败样例。
- 后续如评估 RAC 或全量 LATO，应优先考虑用 RAC gold 增加 `elseif` 链式语义回归测试，再决定是否修改 parser。
- 增加 parser confidence / unsupported syntax warning。
- 如复杂语法持续增加，再考虑 LLM extraction fallback。

## 4. 是否改用 LLM 抽取活动和关系

当前项目已经有两套评估链路：

- deterministic embedding metrics：`metrics.py` 解析 PlantUML 后用 `sentence-transformers/all-MiniLM-L6-v2` 和 0.85 阈值做一对一匹配。
- LLM element metrics：`llm_element_metrics.py` 让 LLM 抽取 nodes/relations，再让 LLM 判定 TP/FP/FN。

可以考虑把 parser 也改成 LLM 抽取，或者做混合架构。

### 方案 A：继续维护 deterministic parser

优点：

- 可复现、成本低、速度快。
- 适合作为 acceptance gate 的稳定主指标。
- 不依赖 LLM judge 的格式稳定性和调用成功率。

缺点：

- PlantUML 语法覆盖会越来越复杂。
- 对 shorthand、styled arrow、复杂嵌套结构支持成本高。
- parser bug 会直接影响 node/relation F1。

### 方案 B：完全改为 LLM 抽取 nodes/relations

优点：

- 能更灵活理解 PlantUML 变体和语义。
- 对复杂控制流、注释、样式、语法糖更鲁棒。
- 更接近“活动和关系语义”而不是文本正则解析。

缺点：

- 成本高、慢、不可完全复现。
- LLM 输出 schema 仍需严格校验和重试。
- judge 可能偏宽松，导致与 LATO embedding 指标不可比。
- acceptance gate 如果依赖 LLM，运行波动会变大。

### 方案 C：混合架构

建议优先考虑混合架构：

- deterministic parser 继续作为主指标和 gate 默认路径。
- LLM extraction 作为 fallback 或诊断指标。
- 当 deterministic parser 检测到 unsupported syntax、styled arrow、fork shorthand 等风险语法时，额外运行 LLM extraction。
- 报告中同时保留 deterministic metrics 和 LLM metrics，明确分开解释。

推荐方向：

- 短期先修补 parser 的明确 bug。
- 中期增加 parser confidence / unsupported syntax warning。
- 长期可引入 LLM extraction fallback，但不直接替代 LATO-style embedding 主指标，除非实验设计明确改变。

## 5. LLM judge 与 embedding metrics 的关系

当前二者已经分开：

- `node_f1`、`relation_f1` 来自 deterministic parser + embedding matcher。
- `llm_node_f1`、`llm_relation_f1` 来自 LLM judge。

需要注意：

- 二者定义不同，不能直接混为一个指标。
- LLM judge 会把 start/stop 也纳入 node extraction，而 deterministic parser 通常不计入 start/stop。
- LLM judge 更偏语义宽松，embedding metrics 更贴近 LATO 论文的 all-MiniLM-L6-v2 + 0.85 设置。

当前处理建议：

- 保持二者分开。
- acceptance gate 使用 deterministic `node_f1` / `relation_f1` 做 accept/reject 的收益和非回退判断。
- LLM judge 用作辅助诊断；当 LLM metrics 可用时，也作为语义回退 guard。

## 6. acceptance gate 采样波动（已处理）

当前 `run.py::split_validation_gate_cases` 会先从 sampled training pool 中固定留出 validation gate cases，
小样本 run 会把 validation gate 限制在训练池的大约三分之一以内。
这些样例不会进入 failure analysis、error localization、prompt editor 或 epoch planner。
`run.py::acceptance_decision` 比较 fixed validation gate 上的 `node_f1`、`relation_f1`、
`plantuml_compilation_pass_rate`、`syntax_pass_rate`、precision、LLM guard 和
`infrastructure_error_rate`。

已处理的问题：

- candidate 是否被接受不再依赖每轮重新抽样的 gate batch。
- epoch candidate 先经过 fixed validation gate，再决定是否更新 current prompt.

剩余风险：

- validation gate 仍然来自 training pool，不等同于 held-out test。
- validation gate 过小仍可能有代表性不足的问题。
- 如果后续要进一步降低方差，可以增大 `--validation-gate-size` 或做重复运行比较。

## 7. compare_lato_eval 异常分类

当前 `compare_lato_eval.py::run_method` 在 generation/evaluation 异常时会生成空预测，并标记：

- `generation_error`
- `syntax_error`
- `missing_activity`
- `missing_or_wrong_relation`

问题：

- 没有像 `evaluation.py::evaluate_cases` 一样调用 `is_infrastructure_error`。
- provider/network/timeout/429/5xx 等基础设施问题可能被统计成普通 generation failure。
- 这会影响 APE vs LATO zero-shot 对比的解释。

建议：

- 在 `compare_lato_eval.py` 中复用 `evaluation.is_infrastructure_error`。
- 异常属于基础设施问题时追加 `infrastructure_error`。
- summary 中已有 `infrastructure_error_rate` 字段，可直接受益。

## 8. 多候选 prompt 生成与选择（待设计）

当前每轮只生成一个 candidate prompt。收紧 validation gate 后，单个 candidate 很容易因为某个局部回退被拒绝，即使它在另一些核心指标上有明显收益。

问题：

- 单候选机制把一次 LLM 改写的偶然性直接传递给 gate。
- candidate 可能同时包含有效改进和有害副作用，当前流程只能整体接受或整体拒绝。
- 如果 candidate 被拒，下一轮通常重新生成一个新 candidate，而不是围绕“接近通过但失败的 candidate”做修复。

后续可考虑的设计：

- 对同一个 revision plan 生成多个候选，例如：
  - `conservative`：只做最小必要修改，优先替换或压缩已有规则；
  - `balanced`：按 revision plan 正常修改；
  - `aggressive`：允许更完整地重写相关 section。
- 所有候选先经过同一组 validation gate。
- 只接受通过 safety gate 且收益最大的 candidate。
- 如果没有候选通过，记录最接近通过的候选及其失败原因，供下一轮 planner 使用。
- 报告中需要列出每个候选的 prompt diff、validation summary、gate delta 和 rejection reasons，避免结果不可解释。

实现影响：

- `prompt_rewriter` 输出 schema 需要从单个 `candidate_prompt` 扩展为候选列表，或新增独立 multi-candidate rewriter。
- `run.py` 需要支持 candidate 级目录结构，例如 `candidates/candidate_001/`。
- acceptance decision 需要从单候选判断扩展为候选排序和选择。
- 成本会上升，适合在 validation gate 已稳定后再实现。

## 9. 两级 validation gate（待设计）

当前 candidate 直接进入固定 validation gate。gate 变硬后，完整评估成本较高，而且所有候选都承担同样的评估成本。

后续可考虑两级 gate：

- `mini_gate`：固定小样本，用于快速筛掉明显差的 candidate。
- `full_gate`：较大的固定 validation set，只评估通过 mini gate 或接近通过的 candidate。
- 最终 accept/reject 只能基于 full gate，mini gate 只用于节省成本和排序候选。

设计原则：

- mini gate 和 full gate 都必须从 training pool 中固定切分，不能使用 held-out test。
- mini gate 不能替代 full gate 做最终接收决策。
- 报告中需要明确 candidate 是在哪一级 gate 被拒绝。
- 如果使用多候选机制，mini gate 可以先对候选排序，再把 top-k 送入 full gate。

实现影响：

- `split_validation_gate_cases` 需要扩展为 mini/full 两组固定 case。
- `evaluate_validation_gate` 需要支持分阶段输出。
- `acceptance.json` 需要记录 mini/full 两级 summary、delta 和 rejection reasons。
- `metrics_report.md` 需要区分 `mini_gate_*` 与 `full_gate_*`。
