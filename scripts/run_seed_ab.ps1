[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$CandidateAPrompt,
    [Parameter(Mandatory = $true)]
    [string]$CandidateBPrompt,
    [string]$BaselinePrompt = "prompt_workspace\tst.md",
    [string]$ExperimentRootOverride,
    [ValidateSet("bp", "fsd", "lmc", "pure", "rac", "us")]
    [string[]]$Datasets = @("bp", "fsd", "lmc", "pure", "rac", "us"),
    [ValidateRange(1, 1000)]
    [int]$CasesPerDataset = 10,
    [ValidateRange(1, 100)]
    [int]$CaseConcurrency = 10
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ScriptRoot = (Resolve-Path $PSScriptRoot).Path
$RepoRoot = (Resolve-Path (Join-Path $ScriptRoot "..")).Path
$Python = (Get-Command py -ErrorAction Stop).Source

function Get-EnvOrDefault {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Default
    )

    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) {
        return $Default
    }
    return $value.Trim()
}

$RequestedProviderRaw = [Environment]::GetEnvironmentVariable("APE_LLM_PROVIDER")
$RequestedProvider = if ([string]::IsNullOrWhiteSpace($RequestedProviderRaw)) {
    ""
}
else {
    $RequestedProviderRaw.Trim().ToLowerInvariant()
}
$HasZhipuKey = -not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable("ZHIPU_LLM_API_KEY"))
$HasDeepSeekKey = -not [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable("DEEPSEEK_API_KEY"))
if ($RequestedProvider -and $RequestedProvider -notin @("zhipu", "deepseek")) {
    throw "APE_LLM_PROVIDER must be zhipu or deepseek"
}
if (-not $RequestedProvider -and $HasZhipuKey -and $HasDeepSeekKey) {
    throw "Both provider keys are set; set APE_LLM_PROVIDER explicitly"
}
$ActiveProvider = if ($RequestedProvider) {
    $RequestedProvider
}
elseif ($HasDeepSeekKey) {
    "deepseek"
}
else {
    "zhipu"
}
$ActiveKeyName = if ($ActiveProvider -eq "deepseek") { "DEEPSEEK_API_KEY" } else { "ZHIPU_LLM_API_KEY" }
if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($ActiveKeyName))) {
    throw "$ActiveKeyName is required for a real Seed A/B evaluation."
}

if ($ActiveProvider -eq "deepseek") {
    $SharedModel = Get-EnvOrDefault "DEEPSEEK_MODEL" "deepseek-v4-flash"
    $GenerationModel = Get-EnvOrDefault "DEEPSEEK_GENERATION_MODEL" $SharedModel
    $AgentModel = Get-EnvOrDefault "DEEPSEEK_AGENT_MODEL" $SharedModel
    $JudgeModel = Get-EnvOrDefault "DEEPSEEK_JUDGE_MODEL" $SharedModel
    $Thinking = Get-EnvOrDefault "DEEPSEEK_THINKING_TYPE" "disabled"
    $GenerationThinking = Get-EnvOrDefault "DEEPSEEK_GENERATION_THINKING_TYPE" $Thinking
    $JudgeThinking = Get-EnvOrDefault "DEEPSEEK_JUDGE_THINKING_TYPE" $Thinking
    $ElementExtractionThinking = Get-EnvOrDefault "DEEPSEEK_ELEMENT_EXTRACTION_THINKING_TYPE" $Thinking
    $ProviderDoSample = $null
}
else {
    $SharedModel = Get-EnvOrDefault "ZHIPU_LLM_MODEL" "glm-5.2"
    $GenerationModel = Get-EnvOrDefault "ZHIPU_LLM_GENERATION_MODEL" "glm-4.7"
    $AgentModel = Get-EnvOrDefault "ZHIPU_LLM_AGENT_MODEL" $SharedModel
    $JudgeModel = Get-EnvOrDefault "ZHIPU_LLM_JUDGE_MODEL" $SharedModel
    $Thinking = Get-EnvOrDefault "ZHIPU_THINKING_TYPE" "disabled"
    $GenerationThinking = Get-EnvOrDefault "ZHIPU_GENERATION_THINKING_TYPE" $Thinking
    $JudgeThinking = Get-EnvOrDefault "ZHIPU_JUDGE_THINKING_TYPE" $Thinking
    $ElementExtractionThinking = Get-EnvOrDefault "ZHIPU_ELEMENT_EXTRACTION_THINKING_TYPE" $Thinking
    $ProviderDoSample = $false
}

function Resolve-RepoPath {
    param([Parameter(Mandatory = $true)][string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return (Resolve-Path -LiteralPath $Path).Path
    }
    return (Resolve-Path -LiteralPath (Join-Path $RepoRoot $Path)).Path
}

function Write-Utf8File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Content
    )

    [System.IO.File]::WriteAllText(
        $Path,
        $Content,
        [System.Text.UTF8Encoding]::new($false)
    )
}

function Get-PromptHash {
    param([Parameter(Mandatory = $true)][string]$Path)

    $code = @"
import sys
sys.path.insert(0, sys.argv[2])
from pathlib import Path
from utils.prompt_hash import prompt_file_sha256
print(prompt_file_sha256(Path(sys.argv[1])))
"@
    $value = & $Python -c $code $Path $RepoRoot
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace(($value | Select-Object -Last 1))) {
        throw "Could not hash Prompt file: $Path"
    }
    return (($value | Select-Object -Last 1).ToString().Trim())
}

$baselinePath = Resolve-RepoPath $BaselinePrompt
$candidateAPath = Resolve-RepoPath $CandidateAPrompt
$candidateBPath = Resolve-RepoPath $CandidateBPrompt
foreach ($promptPath in @($baselinePath, $candidateAPath, $candidateBPath)) {
    if (-not (Test-Path -LiteralPath $promptPath -PathType Leaf)) {
        throw "Missing Prompt file: $promptPath"
    }
}

$ExperimentRoot = if ([string]::IsNullOrWhiteSpace($ExperimentRootOverride)) {
    $tag = Get-Date -Format "yyyy-MM-dd__HH-mm-ss"
    Join-Path $RepoRoot "seed_prompt_runs\${tag}__seed-ab-tracked"
}
else {
    if ([System.IO.Path]::IsPathRooted($ExperimentRootOverride)) {
        $ExperimentRootOverride
    }
    else {
        Join-Path $RepoRoot $ExperimentRootOverride
    }
}
$ExperimentRoot = [System.IO.Path]::GetFullPath($ExperimentRoot)
$ResultsRoot = Join-Path $ExperimentRoot "results"
if (Test-Path -LiteralPath $ResultsRoot) {
    $existingRuns = @(Get-ChildItem -LiteralPath $ResultsRoot -Directory)
    if ($existingRuns.Count -gt 0) {
        throw "Results already exist under $ResultsRoot. Use a new experiment root."
    }
}
New-Item -ItemType Directory -Force -Path $ResultsRoot | Out-Null
$InputsRoot = Join-Path $ExperimentRoot "inputs"
New-Item -ItemType Directory -Force -Path $InputsRoot | Out-Null
Copy-Item -LiteralPath $baselinePath -Destination (Join-Path $InputsRoot "baseline.md")
Copy-Item -LiteralPath $candidateAPath -Destination (Join-Path $InputsRoot "candidate_a.md")
Copy-Item -LiteralPath $candidateBPath -Destination (Join-Path $InputsRoot "candidate_b.md")

$promptPaths = [ordered]@{
    "baseline" = $baselinePath
    "candidate-a" = $candidateAPath
    "candidate-b" = $candidateBPath
}
$promptHashes = [ordered]@{}
foreach ($condition in $promptPaths.Keys) {
    $promptHashes[$condition] = Get-PromptHash $promptPaths[$condition]
}

$schedule = @(
    [pscustomobject]@{ Repeat = 1; Condition = "baseline" }
    [pscustomobject]@{ Repeat = 1; Condition = "candidate-a" }
    [pscustomobject]@{ Repeat = 1; Condition = "candidate-b" }
    [pscustomobject]@{ Repeat = 2; Condition = "candidate-b" }
    [pscustomobject]@{ Repeat = 2; Condition = "candidate-a" }
    [pscustomobject]@{ Repeat = 2; Condition = "baseline" }
    [pscustomobject]@{ Repeat = 3; Condition = "candidate-a" }
    [pscustomobject]@{ Repeat = 3; Condition = "baseline" }
    [pscustomobject]@{ Repeat = 3; Condition = "candidate-b" }
)
$designManifest = [ordered]@{
    schema_version = "seed-prompt-ab-v3"
    provider = $ActiveProvider
    api_key_environment = $ActiveKeyName
    base_url = if ($ActiveProvider -eq "deepseek") {
        Get-EnvOrDefault "DEEPSEEK_BASE_URL" "https://api.deepseek.com/"
    }
    else {
        Get-EnvOrDefault "ZHIPU_LLM_BASE_URL" "https://open.bigmodel.cn/api/paas/v4/"
    }
    datasets = $Datasets
    cases_per_dataset = $CasesPerDataset
    sample_strategy = "random"
    sample_seed = 20260804
    repeats = 3
    schedule = $schedule
    prompt_sha256 = $promptHashes
    prompt_hash_normalization = "utf8-sig+lf+strip-v1"
    models = [ordered]@{
        shared = $SharedModel
        generation = $GenerationModel
        agent = $AgentModel
        judge = $JudgeModel
    }
    temperature = 0
    do_sample = $ProviderDoSample
    thinking = $Thinking
    case_concurrency = $CaseConcurrency
}
Write-Utf8File -Path (Join-Path $ExperimentRoot "design_manifest.json") -Content (
    $designManifest | ConvertTo-Json -Depth 8
)

$expectedCaseHashes = @{}
$completedRuns = @()
foreach ($entry in $schedule) {
    $condition = [string]$entry.Condition
    $repeat = [int]$entry.Repeat
    $runName = "seed-ab-r$repeat-$condition"
    $promptPath = $promptPaths[$condition]
    Write-Host "[seed-ab] repeat=$repeat condition=$condition"

    $arguments = @(
        (Join-Path $RepoRoot "eval_seed_prompt_all.py")
        "--output-dir", $ResultsRoot
        "--run-name", $runName
        "--prompt-path", $promptPath
        "--datasets", ($Datasets -join ",")
        "--max-test-cases", $CasesPerDataset
        "--case-concurrency", $CaseConcurrency
        "--test-sample-strategy", "random"
        "--sample-seed", "20260804"
        "--model", $SharedModel
        "--generation-model", $GenerationModel
        "--agent-model", $AgentModel
        "--judge-model", $JudgeModel
        "--temperature", "0"
        "--llm-judge-temperature", "0"
        "--element-extraction-temperature", "0"
        "--thinking", $Thinking
        "--generation-thinking", $GenerationThinking
        "--judge-thinking", $JudgeThinking
        "--element-extraction-thinking", $ElementExtractionThinking
        "--metric-matcher", "embedding"
        "--element-extractor", "llm"
        "--llm-element-metrics"
    )
    if ($null -eq $ProviderDoSample) {
        $arguments += @("--do-sample", "omit")
    }
    else {
        $arguments += @("--do-sample", "false")
    }
    & $Python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Seed A/B run failed: repeat=$repeat condition=$condition exit_code=$LASTEXITCODE"
    }

    $matchingRuns = @(
        Get-ChildItem -LiteralPath $ResultsRoot -Directory |
            Where-Object { $_.Name -match "__$([regex]::Escape($runName))(?:__\d+)?$" }
    )
    if ($matchingRuns.Count -ne 1) {
        throw "Expected exactly one output directory for $runName, found $($matchingRuns.Count)."
    }
    $runDir = $matchingRuns[0]

    foreach ($dataset in $Datasets) {
        $caseManifest = Join-Path $runDir.FullName "$dataset\test_cases.json"
        if (-not (Test-Path -LiteralPath $caseManifest -PathType Leaf)) {
            throw "Missing case manifest: $caseManifest"
        }
        $cases = @(Get-Content -Raw -LiteralPath $caseManifest | ConvertFrom-Json)
        if ($cases.Count -ne $CasesPerDataset) {
            throw "Expected $CasesPerDataset cases for dataset=$dataset, found $($cases.Count)."
        }
        $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $caseManifest).Hash.ToLowerInvariant()
        if (-not $expectedCaseHashes.ContainsKey($dataset)) {
            $expectedCaseHashes[$dataset] = $hash
        }
        elseif ($expectedCaseHashes[$dataset] -ne $hash) {
            throw "Case manifest mismatch for dataset=$dataset in $($runDir.FullName)."
        }
    }

    $completedRuns += [pscustomobject]@{
        repeat = $repeat
        condition = $condition
        run_dir = $runDir.FullName
    }
    $executionManifest = [ordered]@{
        schema_version = "seed-prompt-ab-execution-v2"
        completed_runs = $completedRuns
        case_manifest_sha256 = $expectedCaseHashes
    }
    Write-Utf8File -Path (Join-Path $ExperimentRoot "execution_manifest.json") -Content (
        $executionManifest | ConvertTo-Json -Depth 8
    )
}

$analyzerPath = Join-Path $RepoRoot "scripts\analyze_seed_ab.py"
& $Python $analyzerPath `
    --experiment-root $ExperimentRoot `
    --inputs-root $InputsRoot `
    --cases-per-dataset $CasesPerDataset `
    --case-concurrency $CaseConcurrency
if ($LASTEXITCODE -ne 0) {
    throw "Seed A/B analysis failed with exit_code=$LASTEXITCODE"
}
Write-Host "[seed-ab] complete: $ExperimentRoot"
