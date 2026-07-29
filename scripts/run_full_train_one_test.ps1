param(
    [string]$TestDataset = "fsd",
    [int]$Iterations = 3,
    [int]$AnalysisBatchSize = 10,
    [int]$ValidationGateSize = 10,
    [switch]$Smoke
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

$argsList = @(
    "run.py",
    "--test-dataset", $TestDataset,
    "--iterations", "$Iterations",
    "--max-train-cases", "0",
    "--max-test-cases", "0",
    "--analysis-batch-size", "$AnalysisBatchSize",
    "--validation-gate-size", "$ValidationGateSize"
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
