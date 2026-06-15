param(
    [int]$Iterations = 3,
    [int]$AnalysisBatchSize = 10,
    [int]$GateBatchSize = 10,
    [switch]$Smoke
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

$argsList = @(
    "run.py",
    "--test-dataset", "all",
    "--iterations", "$Iterations",
    "--max-train-cases", "0",
    "--max-test-cases", "0",
    "--analysis-batch-size", "$AnalysisBatchSize",
    "--gate-batch-size", "$GateBatchSize"
)

if ($Smoke) {
    $argsList += @(
        "--mock-with-gold",
        "--no-evolve",
        "--metric-matcher", "difflib",
        "--no-llm-element-metrics"
    )
}

python @argsList
