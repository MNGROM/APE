# APE

APE 用于自动改进把自然语言需求转换为 PlantUML activity diagram 的 generation Prompt。
当前只支持 selector-v4 工作流，架构细节见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)。

## 入口与资产

- `run.py`：唯一运行入口。
- `config.py`：默认路径和模型配置。
- `analysis/`：Failure Analysis、Selector、Prompt agent 和 candidate registry。
- `prompt_ops.py`：Prompt section 解析与精确单 section 修改。
- `prompt_workspace/tst.md`：只读 seed Prompt。
- `prompt_datasets/lato/`：LATO 六个数据集。
- `prompt_runs/`、`prompt_runs_by_dataset/`：实验日志，保留为只读产物。

## 离线验证

```powershell
py -m unittest discover -s tests -q
py -m compileall analysis tests run.py
git diff --check
```

不调用真实模型的 smoke test：

```powershell
py run.py --train-only --train-dataset fsd --iterations 1 --max-train-cases 2 --mock-with-gold --no-evolve --no-llm-element-metrics
```

## 运行

指定一个 heldout 数据集：

```powershell
py run.py --test-dataset us --iterations 3
```

训练开始前评估原始 seed Prompt：

```powershell
py run.py --test-dataset us --iterations 3 --eval-initial-test
```

`--eval-initial-test` 是无值开关；不能和 `--candidate-application-mode isolated` 同时使用。

Gate2 默认启用，因此 `--candidate-application-mode auto` 解析为 `cumulative`：candidate
必须同时通过 Gate1 和 fresh Gate2。只做候选诊断时使用
`isolated`；旧 `diagnostic-apply` 模式必须显式配合 `--no-gate2`。

真实模型运行通过环境变量选择 provider 和提供凭据。使用 `APE_LLM_PROVIDER=zhipu`
配合 `ZHIPU_LLM_API_KEY`，或使用 `APE_LLM_PROVIDER=deepseek` 配合 `DEEPSEEK_API_KEY`。
如果只有一个 provider key，APE 会自动推断；两个 key 同时存在时必须显式设置
`APE_LLM_PROVIDER`。DeepSeek 默认地址为 `https://api.deepseek.com/`、模型为
`deepseek-v4-flash`，请求会省略不属于其接口的 `do_sample`。角色模型和地址覆盖见
[`.env.example`](.env.example)。凭据不会写入 `run_args.json`。

PowerShell smoke 示例（仅在获得真实调用授权后把占位 key 换成实际 key）：

```powershell
$env:APE_LLM_PROVIDER = "deepseek"
$env:DEEPSEEK_API_KEY = "<your-key>"
pwsh -NoProfile -File scripts/run_dataset_pairs.ps1 -Datasets lmc -MaxParallel 1 -Smoke
```

tracked scheduler 会显式启用 Gate2。复现 validation 证据时按顺序运行目标数据集：

```powershell
pwsh -NoProfile -File scripts/run_dataset_pairs.ps1 -Datasets lmc -MaxParallel 1 -HeldoutRepeats 3
pwsh -NoProfile -File scripts/run_dataset_pairs.ps1 -Datasets pure -MaxParallel 1 -HeldoutRepeats 3
```

scheduler 默认每 10 秒在控制台打印 dataset、阶段、最近 case、heldout repeat、重试和日志路径；可用
`-StatusIntervalSeconds 30` 调整状态心跳间隔。完整 stdout/stderr 仍会保存在临时 scheduler
日志目录中。

跨 run 的来源-受益审计只读消费现有产物，默认输出到控制台：

```powershell
py scripts/analyze_cross_dataset_transfer.py prompt_runs\<run-a> prompt_runs\<run-b>
```

该报告中的 training-pool weighted 指标仅供诊断，不会改写历史 acceptance。

`-NoGate2` 仅用于诊断，并会切换到 `diagnostic-apply`；该模式的结果不能作为正式双 Gate
证据。固定 Seed A/B 诊断需要显式提供两个候选 Prompt：

```powershell
pwsh -NoProfile -File scripts/run_seed_ab.ps1 `
  -CandidateAPrompt path\to\candidate_a.md `
  -CandidateBPrompt path\to\candidate_b.md
```

A/B runner 会记录 canonical Prompt hash，并在生成报告前校验 hash 和 case split。
