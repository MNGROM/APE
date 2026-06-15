param(
    [string]$TestDataset = "fsd",
    [int]$Iterations = 1,
    [int]$MaxTrainCases = 20,
    [int]$MaxTestCases = 10,
    [int]$AnalysisBatchSize = 5,
    [int]$GateBatchSize = 5,
    [switch]$Smoke
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

$argsList = @(
    "run.py",
    "--test-dataset", $TestDataset,
    "--iterations", "$Iterations",
    "--max-train-cases", "$MaxTrainCases",
    "--max-test-cases", "$MaxTestCases",
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
