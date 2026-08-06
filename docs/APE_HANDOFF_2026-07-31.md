# APE 当前工作交接文档

> 交接日期：2026-07-31
> 仓库：`D:\now_to_use\work4icse\rq1\ape_pre\APE`
> 分支：`ape-open-hypothesis-20260721`
> 代码基线：`fa5f6f8 Simplify APE to selector-v4 workflow`

这份文档用于帮助下一位模型在不重新探索旧实现的情况下继续工作。它描述当前真实支持的
selector-v4 工作流、代码边界、实验规则和最新证据。历史 handoff、旧兼容流程和旧实验设计
只能用于理解背景，不能覆盖当前规范。

## 1. 先读什么

进入仓库后按以下顺序读取：

1. `CLAUDE.md`：工作区规则、目录契约、修改和验证要求。
2. `docs/APE_NEXT_MODIFICATION_GUARDRAILS.md`：当前目标、数据边界和禁止的 workflow 改动。
3. `docs/ARCHITECTURE.md`：selector-v4 架构和代码责任边界。
4. 本文件：当前实验状态、已知问题和交接建议。
5. 最新 run 的 `run_args.json`、`metrics_overview.md` 和 `iteration_test_metrics.csv`。

读取实验日志前使用：

```powershell
pwsh -NoProfile -File `
  C:\Users\16373\.codex\skills\operate-ape-experiments\scripts\summarize_run.ps1 `
  -RepoRoot D:\now_to_use\work4icse\rq1\ape_pre\APE
```

`prompt_runs/`、`prompt_runs_by_dataset/`、`baseline_predictions/` 是只读实验产物，不能编辑、
删除或为了改善报告而回写。

## 2. 项目目标

APE 优化一个 generation Prompt，使模型把自然语言软件需求转换成 PlantUML activity diagram。
真正的目标是提高已接受 Prompt 更新在 heldout 数据上的稳定泛化收益，而不是：

- 让 accepted candidate 数量尽可能多；
- 让每个 epoch 都出现 heldout 指标；
- 让 Prompt 尽快变长；
- 用 heldout 结果反向挑选 candidate 或调阈值。

这里的“训练”是 Prompt 搜索，不是神经网络参数训练。项目不执行权重初始化、激活函数选择、
梯度反传或 Adam/SGD 优化器更新。epoch 的状态变化是 Prompt 文本和 run-local candidate 历史。

## 3. 当前唯一支持的工作流

```text
generation and evaluation
  -> syntax/compiler + LLM element judge
  -> Python numeric findings
  -> batch failure analysis
  -> taxonomy-blind error selector
  -> exact prior-attempt filtering
  -> bounded candidate attempts on one frozen base Prompt
  -> Prompt-gap localization
  -> Prompt editor
  -> Prompt rewriter
  -> deterministic single-section apply
  -> paired repeated validation
  -> application policy
  -> heldout audit only when the Prompt hash changes
```

当前 CLI 仍保留 `taxonomy-v3` 作为历史 policy 名称，但当前候选链路不加载 taxonomy、repair
catalog 或旧的 taxonomy-v3-legacy 流程。不要重新引入以下旧设计：

- `simple-v1` 或 `taxonomy-v3-legacy`；
- atomic attribution、mechanism clustering/memory；
- taxonomy mapping、repair catalog eligibility、taxonomy ID；
- supporting-batch localization voting、epoch planner；
- legacy Safety/Benefit/Bootstrap acceptance gate；
- 额外 critic、reviewer、debate 或 self-consistency 阶段，除非先单独计划并获得确认。

## 4. 代码结构与责任边界

### 根目录模块

| 路径 | 责任 |
| --- | --- |
| `run.py` | CLI、数据 split、epoch orchestration、candidate attempts、validation、heldout 调度和 application policy。 |
| `config.py` | 默认路径、模型和配置辅助。 |
| `evaluation.py` | 单 case generation、syntax/compiler、LLM element judge 和 EvaluationRecord。 |
| `metrics.py` | 指标匹配、embedding 辅助指标、汇总和重复评估统计。 |
| `llm_element_metrics.py` | LLM element judge 的结构化解析和 metric bundle。 |
| `element_extraction.py` | PlantUML activity graph 的节点/关系提取。 |
| `llm.py` | Zhipu/GLM API client、角色 model routing、重试和 rate-limit handling。 |
| `prediction.py` | 数据集 prediction 辅助。 |
| `prompt_ops.py` | Prompt section 解析、canonical contract 校验和单 section 精确修改。 |
| `reporting.py` | run reports、metrics overview 和 csv/markdown 产物。 |
| `versioning.py` | Prompt/hash 版本辅助。 |
| `compare_lato_eval.py` | 历史 LATO evaluation 比较工具；不属于当前主 orchestration。 |
| `eval_seed_prompt_all.py` | seed Prompt 离线比较工具；不改变 selector-v4 主流程。 |

### `analysis/`

| 路径 | 责任 |
| --- | --- |
| `analysis/failure_analysis.py` | 构造 numeric failure input、调用 Failure Analysis agent、校验 `failure-errors-v2`。 |
| `analysis/error_selector.py` | finding admission、primary/diagnostic 分类、完整分组、canonical group ID 和 selector 校验。 |
| `analysis/selector_agents.py` | Localization、Editor、Rewriter 输入辅助、agent contract retry。 |
| `analysis/prompt_rewriter.py` | 只接受 Rewriter 的 `rule_text`，调用 exact single-section apply。 |
| `analysis/candidate_registry.py` | run-local candidate 去重、finding-key history、group attempt history 和 Prompt hash。 |
| `analysis/__init__.py` | package marker。 |

### 数据、Prompt 和测试

| 路径 | 说明 |
| --- | --- |
| `prompt_datasets/lato/` | LATO 数据集原始输入/参考输出，当前实验数据来源。 |
| `ape_datasets/` | 数据加载、sampling 和 split 辅助。 |
| `prompt_workspace/tst.md` | 当前 seed generation Prompt；运行时基于它创建 run-local Prompt。 |
| `prompt_workspace/failure_analysis_selector_v2.md` | Failure Analysis agent Prompt。 |
| `prompt_workspace/error_selector_v4.md` | Error Selector agent Prompt。 |
| `prompt_workspace/prompt_gap_localization_v2.md` | Prompt-gap Localization agent Prompt。 |
| `prompt_workspace/prompt_editor_selector_v2.md` | Prompt Editor agent Prompt。 |
| `prompt_workspace/prompt_rewriter_selector_v1.md` | Prompt Rewriter agent Prompt。 |
| `tools/prompt_snapshots/` | 仅保存用户明确要求的活跃 Prompt 精确回滚快照；运行流程不会读取。 |
| `tests/` | 当前支持行为的 unit tests 和流程 contract tests。 |
| `scripts/` | 离线诊断、单数据集运行、全数据集运行和 partial split 启动脚本。 |

## 5. Agent 与 Python 的职责

### Failure Analysis

Python 先生成 numeric findings。Agent 只能输出每条 finding 的状态、精确 requirement quote、
error summary 和 causal rationale，并引用一个已有 `finding_id`。Python 负责 ID、quote、anchor、
secondary linkage、重复分类和 generic diagnostic 校验。

### Error Selector

Selector 接收当前 epoch 全部 validated actionable primary errors，但不接收 Prompt、taxonomy
或 validation metrics。它必须完整且不重复地划分 finding，并返回 candidate 尝试顺序。Python
推导 canonical group ID 和支持统计。

### Localization、Editor、Rewriter

- Localization 只判断组内是否存在同一类 Prompt gap，返回 `localized`、`already_covered` 或
  `no_prompt_gap`，并只允许 `append_new`、`replace_existing`、`none`。
- `already_covered` 必须由唯一现有原文同时覆盖 input-side trigger、目标结构修复和
  preservation boundary。仅主题相关或术语相同不算覆盖。
- 原指导相关但不够具体时使用现有 `ambiguous + replace_existing` 合同收紧原规则，不能追加
  重复规则。
- `no_prompt_gap` 不能仅以“已有指导覆盖”为理由返回；它表示证据不足、修复冲突、预测有效
  或 generation/judge limitation。
- Editor 只输出 intent、positive trigger、negative boundary 和 change instruction；不能引用
  prediction、gold、metric、dataset 或 evaluator 语言。
- Rewriter 拥有最终 `rule_text` 措辞。Python 只能验证 canonical contract 并精确修改一个
  section，不能向 Rewriter 文本注入或追加语义文本，非目标 section 必须字节一致。

## 6. Candidate 与 acceptance 规则

同一个 epoch 的所有 candidate 必须基于同一个 frozen base Prompt，最多尝试
`max_candidate_attempts_per_epoch` 个 group，最多应用一个 candidate。遇到 invalid、重复、
`already_covered`、`no_prompt_gap` 或 validation rejection 时继续尝试下一个 group。

当前 latest run 的 effective acceptance 配置：

```text
candidate_application_mode = cumulative
validation_gate_size       = 30
validation_repeats         = 3
acceptance_min_wins        = 3
node_min_delta             = 0.01
relation_min_delta         = 0.01
max_candidate_attempts     = 5
validation_gate_seed       = 20260629
```

`any-improvement` 只要 Node F1 或 Relation F1 中至少一个语义指标满足：

1. paired repeats 的平均 delta 严格大于该指标的 `min_delta`；
2. 正 delta 的 repeat 数量不少于 `acceptance_min_wins`；
3. 所有 baseline/candidate measurement 完整且没有 infrastructure error。

Compile 和 Syntax 只能作为诊断，不能单独接受 candidate。最新运行中
`embedding_element_metrics=false`、`llm_element_metrics=true`，所以主 acceptance 使用
`llm_node_f1` 和 `llm_relation_f1`。`metric_matcher=embedding` 只是保留的 embedding matcher
配置，不代表 embedding 指标已经启用；CSV 中 `node_f1`/`relation_f1` 为 0 是预期现象，应读取
`llm_node_f1`/`llm_relation_f1`。

支持的 application mode：

- `diagnostic-apply`：candidate 合法且 measurement 有效就应用，metric decision 只记录；
- `cumulative`：只有 paired validation accepted 才应用；
- `isolated`：只评估 candidate，不写入 work Prompt。

## 7. Heldout 数据边界

Heldout 是泛化审计，不得参与 failure finding、grouping、candidate generation、排序、阈值
校准或 acceptance。Prompt hash 未变化时不得重新调用 heldout generation/judge，只写 skip
manifest。因此没有 accepted candidate 的 epoch 没有新的 heldout 指标点，这是设计行为，不是
日志丢失。

小 validation split 的重复结果容易受 generation 和 LLM judge 波动影响。Heldout 也可能有
模型波动，但它不应被用来选择当前 run 的最佳 epoch。需要比较时同时报告：

- initial absolute F1；
- final absolute F1 和 initial-to-final delta；
- 每个已应用 epoch 的 heldout audit；
- Node/Relation precision 和 recall；
- infrastructure error rate。

## 8. 最新实验状态

最新完整 run：

```text
prompt_runs/2026-07-31__12-31-54__test-us
```

配置：`glm-4.7` generation，`glm-5.2` agent，`glm-5.2` judge；validation 30 条、3 repeats；
heldout 220 条；`acceptance_min_wins=3`；Node/Relation min delta 都是 `0.01`；
`cumulative` application。

### Candidate funnel

```text
epochs completed                 6/6
candidate attempts               25
generated and valid candidates   23
accepted/applied                 3
validation_gate_rejected         20
prompt_rewriter_invalid          2
already_covered                  0
no_prompt_gap                    0
prompt_too_long                  0
infrastructure_error_rate        0
```

Accepted/applied 的 epoch 是 1、4、5。Heldout audit 只出现在 0、1、4、5：

| iteration | status | Node F1 | Relation F1 | compile |
| --- | --- | ---: | ---: | ---: |
| 0 | initial | 0.8412 | 0.6729 | 0.9955 |
| 1 | accepted | 0.8638 | 0.7002 | 0.9955 |
| 2 | no Prompt change | - | - | - |
| 3 | no Prompt change | - | - | - |
| 4 | accepted | 0.8854 | 0.7176 | 0.9955 |
| 5 | accepted | 0.8483 | 0.6809 | 0.9955 |
| 6 | no Prompt change | - | - | - |

Epoch 4 是本次 heldout 峰值，但 epoch 5 虽然通过 validation gate，heldout 反而回落。最终
相对初始 Prompt 只有 Node `+0.0071`、Relation `+0.0079`。这说明当前 acceptance 与 heldout
泛化之间仍不稳定，不能只用 accepted 数量评价训练质量。

### 与近期 run 的对照

| run | `min_wins` | accepted | 最终 Node delta | 最终 Relation delta |
| --- | ---: | ---: | ---: | ---: |
| `2026-07-29__14-10-45__test-us` | 2 | 4 | +0.0431 | +0.0380 |
| `2026-07-29__23-01-04__test-us` | 2 | 6 | +0.0187 | -0.0039 |
| `2026-07-30__19-35-47__test-us` | 3 | 1 | +0.0391 | +0.0587 |
| `2026-07-31__12-31-54__test-us` | 3 | 3 | +0.0071 | +0.0079 |

近期证据表明：接受更多 candidate 不等于最终 heldout 更好。当前 run 的搜索机会和接受数
比上一轮多，但最终指标弱于上一轮。下一次实验必须先说明是复现稳定收益，还是探索新的
candidate 行为，不能把 heldout 峰值当作训练信号。

## 9. 已知问题与当前判断

### 9.1 LLM judge 和 generation 波动

主语义指标来自 LLM element judge。即使 `do_sample=false`，远端模型服务仍不保证每次请求
逐位相同；generation 和 judge 的离散判断会造成 validation delta 波动。`validation_repeats`、
`acceptance_min_wins` 和 `min_delta` 只能降低风险，不能消除噪声。

### 9.2 Validation 与 heldout 不完全一致

最新 epoch 5 在 validation 上 Relation 平均 delta `+0.0303` 且 `3/3` 获胜，但 heldout 从
epoch 4 的 `0.7176` 降至 `0.6809`。这可能是候选泛化失败、validation 样本误导或模型评估
随机性，当前日志不足以单独判定。不要用一次 heldout 回退直接修改 selector 或把 heldout
加入 acceptance。

### 9.3 Prompt 长度与重复规则

最新 Prompt 从 1205 增长到 2029 字符，低于 `max_prompt_chars=4000`，normalized duplicate
sentence groups 为 0。当前没有 prompt-too-long 或重复规则证据，但每次继续追加前仍必须检查
长度、重复、边界和非目标 section 保留。

### 9.4 `already_covered` 语义边界

当前 Localization Prompt 已要求现有规则同时覆盖 trigger、correction 和 preservation
boundary，并禁止以“主题相关”判定覆盖。重复 recurrence 需要使用
`ambiguous + replace_existing` 收紧，而不是追加同义规则。不要把 Python 处理误解为负责生成
Prompt 语义；Python 只校验和确定性应用，语义文本由 agent/Rewriter 产生。

### 9.5 Syntax/compile candidate 的指标对齐

Syntax/compiler finding 可以进入诊断，但 acceptance 的主 gate 仍是 semantic LLM F1。未来若
修改这部分，应让 syntax/compile candidate 证明直接的 syntax/compile 改善，同时保证不能有
语义回退；不能让 Compile 单独替代 semantic acceptance。此问题尚未作为代码修改实施。

### 9.6 Embedding 不是当前主问题

`SentenceTransformer` 代码只在 `embedding_element_metrics=true` 时运行；最新实验关闭了该
指标。当前没有证据表明向量初始化、激活函数、优化器或浮点误差导致实验波动。重点仍是
LLM generation/judge 随机性、validation 样本量和 candidate 泛化。

## 10. 继续工作的建议顺序

1. 先读取本文件和当前最新 run，确认代码是否仍在 `fa5f6f8` 基线上。
2. 不为了获得更密集的折线而降低 acceptance gate。
3. 下一次真实实验只改变一个变量；优先重复当前配置，确认 epoch 1/4 的收益能否复现。
4. 将 heldout 作为审计结果报告，不用它挑选 epoch、candidate 或阈值。
5. 若要研究评估噪声，固定同一个 Prompt 和 validation split，重复 5-10 次，记录生成文本
   hash、judge 结果和汇总 F1；这是诊断实验，不得自动改变 acceptance。
6. 若要研究 acceptance policy，先在 validation 日志上做离线分析，再单独设计新的真实实验；
   不要同时改 Prompt、selector、阈值和并发。
7. 若发现新问题，优先加一个针对实际失败形状的 regression test，再改最小责任边界。

## 11. 验证命令

代码或 Prompt contract 修改后至少执行：

```powershell
py -m unittest discover -s tests -q
py -m compileall -q analysis tests run.py
git diff --check
```

涉及 CLI/orchestration 时，再执行不调用真实模型的 smoke test：

```powershell
py run.py `
  --train-only `
  --train-dataset fsd `
  --iterations 1 `
  --max-train-cases 2 `
  --mock-with-gold `
  --no-evolve `
  --no-llm-element-metrics
```

如果命令涉及真实模型、validation calibration 或 heldout，必须先得到用户明确授权。不要从
`.env`、日志或命令输出复制 API key。

## 12. 最新配置的可复现实验模板

下面是与最新 US run 接近的模板。它只用于用户确认后的真实实验，不能由交接模型自动启动：

```powershell
py run.py `
  --test-dataset us `
  --iterations 6 `
  --eval-initial-test `
  --max-train-cases 0 `
  --max-test-cases 0 `
  --analysis-batch-size 20 `
  --epoch-batch-concurrency 15 `
  --heldout-test-concurrency 10 `
  --validation-gate-concurrency 8 `
  --validation-gate-size 30 `
  --validation-gate-seed 20260629 `
  --validation-repeats 3 `
  --max-candidate-attempts-per-epoch 5 `
  --candidate-application-mode cumulative `
  --acceptance-min-wins 3 `
  --any-improvement-node-min-delta 0.01 `
  --any-improvement-relation-min-delta 0.01 `
  --generation-model glm-4.7 `
  --agent-model glm-5.2 `
  --judge-model glm-5.2 `
  --llm-element-metrics `
  --no-embedding-element-metrics `
  --element-extractor llm `
  --temperature 0.2 `
  --llm-judge-temperature 0.0 `
  --do-sample false
```

模型角色必须明确：

- `--generation-model`：生成 PlantUML；
- `--agent-model`：Failure Analysis、Selector、Localization、Editor、Rewriter；
- `--judge-model`：LLM semantic judge；
- `--model` 只作为共享 fallback，不应掩盖角色配置。

实际运行参数以 run 目录的 `run_args.json` 为准，不要只依据命令模板推断。

## 13. 版本、快照和敏感信息

- 当前 Git 基线：`fa5f6f8`，工作区在本次文档修改前是 clean。
- 活跃 Prompt 回滚快照：
  `tools/prompt_snapshots/2026-07-29__prompt-gap-localization-v2__pre-coverage-proof.md`。
- `tools/prompt_snapshots/` 不会被运行流程读取，也不会自动覆盖当前 Prompt。
- `.env`、`ZHIPU_LLM_API_KEY` 和其他凭据不进入代码、文档、日志或 commit。
- 删除文件、修改 CI/CD、修改 `.env`、Git 历史操作、push 或公开发布前必须先获得用户确认。

## 14. 交接模型的停止条件

遇到以下情况先停下来报告，不要自行扩大范围：

- 需要修改 validation/heldout 数据边界或 acceptance 职责；
- 需要新增 agent、critic、reviewer、debate 或额外真实模型调用；
- 需要改动 `.env`、CI/CD、数据库、Git history 或执行 push；
- 需要删除旧文件或实验产物；
- 发现当前 Prompt、代码和日志之间不一致，无法确定哪一个是用户最新意图。

正常的下一次分析应先给出：最新 run、完整 epoch 数、candidate funnel、accepted/applied 数、
validation/heldout 指标、基础设施重试，以及与可比 run 的配置差异；不能只报告“accepted
了几个 candidate”。
