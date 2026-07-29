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

默认 `--candidate-application-mode auto` 解析为 `diagnostic-apply`。需要严格 validation
门槛时显式使用 `cumulative`；只做候选诊断时使用 `isolated`。

真实模型运行需要通过环境变量提供 `ZHIPU_LLM_API_KEY`，不要把凭据写入代码或日志。
