# 当前已知问题

## LLM judge 波动

LLM element judge 是 training 和 validation 的主语义指标。paired repeats、最小 wins 和
平均 delta 用于降低单次 judge 波动，但不能保证每次实验都提升。

## Heldout 解释

没有同 run 的 iteration-0 seed baseline 时，只能报告更新后的 heldout 数值，不能声称获得
提升。Heldout 仍是最终泛化审计，不是训练信号。

## PlantUML parser

deterministic parser 对复杂嵌套 fork、shorthand branch 和 `elseif` 链仍可能近似解析。LLM
element metrics 可作为语义诊断，但 parser 风险需要通过真实 gold/pred 回归样例单独分析。

## Prompt 长度和边界

Prompt rewriter 只返回 `rule_text`，Python 只修改一个 section。候选过长、非目标 section
变化、缺少 canonical trigger/boundary 或 validation measurement 不完整时，candidate 无效。
