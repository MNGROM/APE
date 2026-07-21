# APE 开放假设、证据记忆与分层聚类实施契约

本文档定义 atomic-v3 之后的下一阶段实现。若与旧的严格 promotion 规则冲突，以本文档和更新后的 `APE_NEXT_MODIFICATION_GUARDRAILS.md` 为准。

## 目标

候选阶段只发现一个窄、可验证的 child hypothesis，不提前证明跨 batch、case 或 dataset 的通用性。最终是否接受仍只由 validation gate 决定。

```text
atomic attribution
-> open hierarchical clustering
-> current-run evidence memory
-> one narrow hypothesis
-> one conditional Prompt candidate
-> validation decides acceptance
```

不增加 agent 阶段、exploratory candidate、Top-K、真实模型重复调用或 heldout 反馈。每个 epoch 最多选择一个 candidate。

## Analysis 与资格

- 一个 attribution 绑定一个 `evidence_id` 和一个 exact evaluator anchor。
- Python 生成 `anchor_kind`、`attribution_id`、`matching_quality`、eligibility 和 rejection reasons。
- 非双射 judge matching、secondary relation/construct attribution、`gold_only`、`ambiguous`、非法 quote/anchor 和未通过 trigger grounding 的 attribution 不提供 candidate support。
- context subtype 必须由 exact requirement quote 支持；Python 不自动替模型重分类。
- compiler attribution 必须保留 wrapper、conditional label、block balance 等具体 error class。

## 分层 hypothesis

Parent key 为：

```text
failure_direction + construct_family + gold_state + prediction_state + node_inventory_status
```

Child key 为完整六字段 signature。Parent 只汇总、排序和记录冲突，child 才能修改 Prompt。

一个合格的当前 epoch primary attribution 即可让 child hypothesis 进入候选排序。旧的 `min_batches`、`min_cases`、`min_datasets` 和 `min_consistency` 不再是 hard gate。

taxonomy v3 增加 `policy_revision` 和 `rule_templates`。已知 signature 复用已有 mechanism；未命中 mechanism 但字段合法且命中安全模板时，由 Python 生成稳定 dynamic `hypothesis_id`、positive trigger 和 negative boundary。无安全模板时记录 `no_safe_rule_template`，不得生成宽泛 fallback。

同一 `construct_family + requirement_trigger` 出现方向相反的 primary evidence 时，相关 child hypotheses 标记 `scope_conflict`。冲突不淘汰 parent，但在 trigger/boundary 进一步拆分前不得生成 candidate。

## Current-run memory

run 根目录维护 `mechanism_memory.json`。记录 evidence fingerprint、parent/child key、hypothesis ID、attribution/evidence 快照、Prompt hash、iteration、状态、拒绝原因和 lineage。

同一 Prompt hash、dataset、case、anchor locator、anchor kind 和 requirement quote 只计一次。Memory 只在当前 run 内跨 epoch 生效；candidate 必须有当前 epoch evidence 激活。Prompt 更新后旧 evidence 转为 `historical`，同一 Prompt hash 下 rejected hypothesis 不重复尝试。

## 下游与审计

Localization/editor 只接收 selected child 的当前及 active historical attribution，不接收 parent 的其他 trigger、secondary attribution 或自由文本 pattern 汇总。

Prompt-gap 共识使用完整 revision scope，票数为 `floor(N/2) + 1`。`N=1` 时允许一份有效 local plan 进入 planner；不同 trigger、repair type、quote 或 signature 不得合并。

Rewriter 继续只返回 `{"rule_text": "..."}`。Python 确定性应用唯一目标 span，并验证 canonical positive trigger、negative boundary 和目标 section。

Lineage 必须覆盖：

```text
evidence -> attribution -> child hypothesis -> local plan
-> revision scope -> rule fragment -> validation -> accepted/rejected
```

validation/heldout split、acceptance threshold 和 winning metric 语义保持不变。Training metric 与 impact report 只用于诊断。

## 验证

```powershell
py -m unittest discover -s tests -q
py -m compileall analysis tests run.py
git diff --check
```

只执行离线测试和历史 fixture 回放；真实模型、calibration、正式训练和 heldout 需要用户单独批准。
