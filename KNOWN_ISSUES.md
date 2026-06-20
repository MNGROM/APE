# APE 待解决问题与设计备忘

本文档记录当前代码理解阶段发现的工程问题、评估风险和后续设计方向。当前阶段只作为备忘，不代表已经实现。

## 1. prompt_editor 修改 section 数量限制

当前 `analysis/prompt_editor.py::propose_prompt_revision` 会调用 `prompt_ops.validate_prompt_revision_plan` 校验 `revision_plan`，其中 `max_sections_per_edit` 默认来自 `run.py` 的 `--max-sections-per-edit=2`。

问题：

- `prompt_workspace/prompt_editor.md` 没有告诉 agent 最多只能规划 2 个 section。
- 实际运行中 agent 可能输出 3 个 section，例如同时修改 `workflow`、`knowledge`、`rule`。
- 代码会拒绝该输出并写入 `prompt_editor.output.rejected.txt`，导致本轮 evolution 中止。
- 即使取消 section 数量上限，`revision_plan` 仍要求同一个 section 只能出现一次；当前 `prompt_workspace/prompt_editor.md` 没有明确这一点，agent 可能把同一 section 拆成多条 revision plan item，触发 `Section '...' is planned more than once` 校验失败。

短期处理建议：

- 先取消或显著放宽该限制，让 prompt evolution 能继续走到 `prompt_rewriter` 和 gate。
- 如果后续仍需要限制，应同时更新 `prompt_workspace/prompt_editor.md`，明确写入最多可修改的 section 数量。
- 同时需要在 `prompt_workspace/prompt_editor.md` 明确要求：`revision_plan` 中每个 fixed section 最多只能出现一次；若同一 section 有多条修改意图，必须合并到同一个 item 的 `intent` / `change_instruction` 中。

后续更稳妥方案：

- 将 section 数量限制从硬失败改成软约束。
- 当超出限制时，可让 agent 自我压缩 revision plan，或只拒绝低优先级 section。
- 在进入严格 schema 校验前增加一个 normalize/merge 步骤，将同 section 的多条 revision plan item 自动合并，减少整轮 evolution 因格式细节报废。

计划中的代码层修复：

- 优先在 `prompt_ops.py` 中新增 `normalize_prompt_revision_plan`，在 `analysis/prompt_editor.py::propose_prompt_revision` 执行严格校验前调用。
- 合并粒度以 `section` 为键，保留首次出现的 section 顺序。
- 同一 section 下的多个 `intent` 合并为一个简短列表式意图说明。
- 同一 section 下的多个 `change_instruction` 合并为一个总指令，要求后续 rewriter 将这些修改整合成该 section 的一次 coherent revision，而不是拆成多个 section item。
- 合并后再执行现有 `validate_prompt_revision_plan`，因此 invalid section、空 intent、空 change_instruction 等真实 schema 错误仍然会被拒绝。
- `max_sections_per_edit > 0` 时，先合并重复 section，再按合并后的 section 数量判断是否超限；不静默丢弃 section，避免隐藏实验设置。

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
- acceptance gate 继续以 deterministic embedding metrics 为主。
- LLM judge 用作辅助诊断和人工分析参考。

## 6. acceptance gate 采样波动

当前 `run.py::acceptance_decision` 主要比较 gate batch 上的 `node_f1`、`relation_f1`、`plantuml_compilation_pass_rate` 和 `infrastructure_error_rate`。

问题：

- gate batch 较小时，指标波动可能比较大。
- candidate 是否被接受可能受采样影响。
- 当前不急于处理，但需要后续设计。

后续可选方案：

- 增大 gate batch。
- 固定每轮 gate cases，减少采样差异。
- 使用多批次平均。
- 对关键指标设置置信区间或重复评估。
- 分离 smoke gate 和 final validation gate。

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
