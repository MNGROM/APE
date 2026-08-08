param(
    [ValidateSet("bp", "fsd", "lmc", "pure", "rac", "us")]
    [string[]]$Datasets = @("bp", "fsd", "lmc", "pure", "rac", "us"),
    [ValidateRange(1, 2)]
    [int]$MaxParallel = 2,
    [ValidateRange(5, 300)]
    [int]$StatusIntervalSeconds = 10,
    [ValidateRange(1, 5)]
    [int]$HeldoutRepeats = 1,
    [switch]$Smoke,
    [switch]$Gate2,
    [switch]$NoGate2
)

$ErrorActionPreference = "Stop"
$Gate2AndNoGate2 = $Gate2 -and $NoGate2
if ($Gate2AndNoGate2) {
    throw "Use either -Gate2 or -NoGate2, not both."
}
$Repo = Split-Path -Parent $PSScriptRoot
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

if ($ActiveProvider -eq "deepseek") {
    $SharedModel = Get-EnvOrDefault "DEEPSEEK_MODEL" "deepseek-v4-flash"
    $GenerationModel = Get-EnvOrDefault "DEEPSEEK_GENERATION_MODEL" $SharedModel
    $AgentModel = Get-EnvOrDefault "DEEPSEEK_AGENT_MODEL" $SharedModel
    $JudgeModel = Get-EnvOrDefault "DEEPSEEK_JUDGE_MODEL" $SharedModel
    $Thinking = Get-EnvOrDefault "DEEPSEEK_THINKING_TYPE" "disabled"
    $GenerationThinking = Get-EnvOrDefault "DEEPSEEK_GENERATION_THINKING_TYPE" $Thinking
    $AnalysisThinking = Get-EnvOrDefault "DEEPSEEK_ANALYSIS_THINKING_TYPE" $Thinking
    $SelectorThinking = Get-EnvOrDefault "DEEPSEEK_SELECTOR_THINKING_TYPE" $Thinking
    $LocalizationThinking = Get-EnvOrDefault "DEEPSEEK_LOCALIZATION_THINKING_TYPE" $Thinking
    $EditorThinking = Get-EnvOrDefault "DEEPSEEK_EDITOR_THINKING_TYPE" $Thinking
    $JudgeThinking = Get-EnvOrDefault "DEEPSEEK_JUDGE_THINKING_TYPE" $Thinking
    $ElementExtractionThinking = Get-EnvOrDefault "DEEPSEEK_ELEMENT_EXTRACTION_THINKING_TYPE" $Thinking
    # DeepSeek's OpenAI-compatible schema does not define do_sample.
    $ProviderArguments = @(
        "--model", $SharedModel,
        "--generation-model", $GenerationModel,
        "--agent-model", $AgentModel,
        "--judge-model", $JudgeModel,
        "--thinking", $Thinking,
        "--generation-thinking", $GenerationThinking,
        "--analysis-thinking", $AnalysisThinking,
        "--selector-thinking", $SelectorThinking,
        "--localization-thinking", $LocalizationThinking,
        "--editor-thinking", $EditorThinking,
        "--judge-thinking", $JudgeThinking,
        "--element-extraction-thinking", $ElementExtractionThinking,
        "--do-sample", "omit"
    )
}
else {
    $SharedModel = Get-EnvOrDefault "ZHIPU_LLM_MODEL" "glm-5.2"
    $GenerationModel = Get-EnvOrDefault "ZHIPU_LLM_GENERATION_MODEL" "glm-4.7"
    $AgentModel = Get-EnvOrDefault "ZHIPU_LLM_AGENT_MODEL" $SharedModel
    $JudgeModel = Get-EnvOrDefault "ZHIPU_LLM_JUDGE_MODEL" $SharedModel
    $Thinking = Get-EnvOrDefault "ZHIPU_THINKING_TYPE" "disabled"
    $GenerationThinking = Get-EnvOrDefault "ZHIPU_GENERATION_THINKING_TYPE" $Thinking
    $AnalysisThinking = Get-EnvOrDefault "ZHIPU_ANALYSIS_THINKING_TYPE" $Thinking
    $SelectorThinking = Get-EnvOrDefault "ZHIPU_SELECTOR_THINKING_TYPE" $Thinking
    $LocalizationThinking = Get-EnvOrDefault "ZHIPU_LOCALIZATION_THINKING_TYPE" $Thinking
    $EditorThinking = Get-EnvOrDefault "ZHIPU_EDITOR_THINKING_TYPE" $Thinking
    $JudgeThinking = Get-EnvOrDefault "ZHIPU_JUDGE_THINKING_TYPE" $Thinking
    $ElementExtractionThinking = Get-EnvOrDefault "ZHIPU_ELEMENT_EXTRACTION_THINKING_TYPE" $Thinking
    $ProviderArguments = @(
        "--model", $SharedModel,
        "--generation-model", $GenerationModel,
        "--agent-model", $AgentModel,
        "--judge-model", $JudgeModel,
        "--thinking", $Thinking,
        "--generation-thinking", $GenerationThinking,
        "--analysis-thinking", $AnalysisThinking,
        "--selector-thinking", $SelectorThinking,
        "--localization-thinking", $LocalizationThinking,
        "--editor-thinking", $EditorThinking,
        "--judge-thinking", $JudgeThinking,
        "--element-extraction-thinking", $ElementExtractionThinking,
        "--do-sample", "false"
    )
}
$ActiveKeyName = if ($ActiveProvider -eq "deepseek") { "DEEPSEEK_API_KEY" } else { "ZHIPU_LLM_API_KEY" }
if (-not $Smoke -and [string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($ActiveKeyName))) {
    throw "$ActiveKeyName is required for a real dataset-pair evaluation. Use -Smoke for offline validation."
}
$RunTag = Get-Date -Format "yyyy-MM-dd__HH-mm-ss"
$LogDir = Join-Path ([System.IO.Path]::GetTempPath()) "ape_scheduler\$RunTag"
New-Item -ItemType Directory -Path $LogDir -Force | Out-Null

function New-ExperimentArguments {
    param([string]$Dataset)

    $gateArguments = if ($NoGate2) {
        Write-Warning "NoGate2 is diagnostic-only; using diagnostic-apply and excluding the run from formal evidence."
        @(
            "--no-gate2",
            "--candidate-application-mode", "diagnostic-apply"
        )
    }
    elseif ($Gate2) {
        @(
            "--gate2",
            "--gate2-size", "30",
            "--gate2-strategy", "stratified",
            "--gate2-seed", "20260630",
            "--candidate-application-mode", "cumulative"
        )
    }
    else {
        @(
            "--no-gate2",
            "--candidate-application-mode", "cumulative"
        )
    }
    if (-not $NoGate2) {
        $gateArguments += "--stop-after-first-apply"
    }

    $arguments = @(
        "run.py",
        "--test-dataset", $Dataset,
        "--iterations", "8",
        "--eval-initial-test",
        "--analysis-batch-size", "30",
        "--training-batch-strategy", "stratified",
        "--epoch-batch-concurrency", "15",
        "--gate-concurrency", "10",
        "--gate1",
        "--gate1-size", "30",
        "--gate1-strategy", "stratified",
        "--gate1-seed", "20260629"
    )
    $arguments += $gateArguments
    $arguments += $ProviderArguments
    $arguments += @(
        "--validation-repeats", "3",
        "--max-candidate-attempts-per-epoch", "5",
        "--temperature", "0",
        "--analysis-temperature", "0",
        "--selector-temperature", "0",
        "--localization-temperature", "0",
        "--editor-temperature", "0",
        "--llm-judge-temperature", "0",
        "--element-extraction-temperature", "0",
        "--heldout-test-concurrency", "10",
        "--heldout-repeats", "$HeldoutRepeats"
    )

    if ($Smoke) {
        $arguments += @(
            "--iterations", "1",
            "--max-train-cases", "4",
            "--max-test-cases", "2",
            "--analysis-batch-size", "2",
            "--gate1-size", "1",
            "--epoch-batch-concurrency", "2",
            "--gate-concurrency", "2",
            "--heldout-test-concurrency", "2",
            "--mock-with-gold",
            "--no-evolve",
            "--metric-matcher", "difflib",
            "--no-llm-element-metrics",
            "--runs-dir", (Join-Path $LogDir "runs")
        )
    }

    return $arguments
}

function New-ProcessLauncher {
    param(
        [string]$Dataset,
        [string[]]$Arguments,
        [string]$StdoutPath,
        [string]$StderrPath
    )

    $launcherPath = Join-Path $LogDir "$Dataset.launch.cmd"
    $statusPath = Join-Path $LogDir "$Dataset.exitcode.txt"
    $quotedArguments = ($Arguments | ForEach-Object { '"' + $_.Replace('"', '""') + '"' }) -join " "
    $escapedPython = $Python.Replace('"', '""')
    $escapedStdout = $StdoutPath.Replace('"', '""')
    $escapedStderr = $StderrPath.Replace('"', '""')
    $escapedStatus = $statusPath.Replace('"', '""')
    $launcher = @"
@echo off
"$escapedPython" $quotedArguments 1>"$escapedStdout" 2>"$escapedStderr"
set "exit_code=%ERRORLEVEL%"
>"$escapedStatus" echo %exit_code%
exit /b %exit_code%
"@
    Set-Content -LiteralPath $launcherPath -Value $launcher -Encoding ascii

    return [pscustomobject]@{
        Launcher = $launcherPath
        Status = $statusPath
    }
}

function Format-Elapsed {
    param([datetime]$StartedAt)

    $elapsed = (Get-Date) - $StartedAt
    return "{0:00}:{1:00}:{2:00}" -f [int]$elapsed.TotalHours, $elapsed.Minutes, $elapsed.Seconds
}

function Get-RunDirectory {
    param([object]$Item)

    if ($Item.RunDir -and (Test-Path -LiteralPath $Item.RunDir)) {
        return $Item.RunDir
    }
    if (-not (Test-Path -LiteralPath $Item.RunsRoot)) {
        return $null
    }

    $pattern = "*test-$($Item.Dataset)"
    $candidate = Get-ChildItem -LiteralPath $Item.RunsRoot -Directory -Filter $pattern -ErrorAction SilentlyContinue |
        Where-Object { $_.CreationTime -ge $Item.StartedAt.AddMinutes(-1) } |
        Sort-Object CreationTime -Descending |
        Select-Object -First 1
    if ($candidate) {
        $Item.RunDir = $candidate.FullName
        return $candidate.FullName
    }
    return $null
}

function Get-LogSnapshot {
    param([string]$Path)

    $lines = @(Get-Content -LiteralPath $Path -Tail 120 -ErrorAction SilentlyContinue)
    if ($lines.Count -eq 0) {
        return [pscustomobject]@{
            Phase = "starting"
            Latest = "waiting for child output"
            RecentEval = "none"
            HeldoutRepeat = "none"
            RetryCount = 0
            LastRetry = "none"
        }
    }

    $evalLines = @($lines | Where-Object { $_ -match '^\[eval\]\s+' })
    $heldoutLines = @($lines | Where-Object { $_ -match '^\[iteration \d+\] held-out repeat \d+/\d+\s+' })
    $retryLines = @($lines | Where-Object { $_ -match '^\[llm-retry\]\s+' })
    $latest = [string]$lines[-1]
    $phase = if ($latest -match '^\[(?<tag>[^\]]+)\]') { $Matches.tag } else { "log" }
    $recentEval = if ($evalLines.Count -gt 0) {
        ([string]$evalLines[-1]) -replace '^\[eval\]\s+', ''
    } else {
        "none"
    }
    $lastRetry = if ($retryLines.Count -gt 0) {
        ([string]$retryLines[-1]) -replace '^\[llm-retry\]\s+', ''
    } else {
        "none"
    }
    $heldoutRepeat = if ($heldoutLines.Count -gt 0 -and [string]$heldoutLines[-1] -match 'held-out repeat (?<value>\d+/\d+)') {
        $Matches.value
    } else {
        "none"
    }

    foreach ($property in @("Latest", "RecentEval", "LastRetry")) {
        $value = [string](Get-Variable -Name $property.ToLowerInvariant() -ValueOnly -ErrorAction SilentlyContinue)
        if ($value.Length -gt 120) {
            Set-Variable -Name $property.ToLowerInvariant() -Value ($value.Substring(0, 117) + "...")
        }
    }

    return [pscustomobject]@{
        Phase = $phase
        Latest = $latest
        RecentEval = $recentEval
        HeldoutRepeat = $heldoutRepeat
        RetryCount = $retryLines.Count
        LastRetry = $lastRetry
    }
}

function Get-RunStateSummary {
    param([object]$Item)

    $runDir = Get-RunDirectory -Item $Item
    if (-not $runDir) {
        return "run=pending"
    }

    $statePath = Join-Path $runDir "run_state.json"
    if (-not (Test-Path -LiteralPath $statePath)) {
        return "run=$(Split-Path -Leaf $runDir) retry=none"
    }

    try {
        $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
        $errorType = if ($state.error.type) { [string]$state.error.type } else { "none" }
        $statusCode = if ($state.error.status_code) { "/$($state.error.status_code)" } else { "" }
        $wait = if ($null -ne $state.wait_seconds) { " wait=$($state.wait_seconds)s" } else { "" }
        return "run=$(Split-Path -Leaf $runDir) retry=$errorType$statusCode$wait"
    } catch {
        return "run=$(Split-Path -Leaf $runDir) retry=state-unreadable"
    }
}

function Write-ActiveStatus {
    param([object]$Item)

    $snapshot = Get-LogSnapshot -Path $Item.Stdout
    $stateSummary = Get-RunStateSummary -Item $Item
    $retrySummary = if ($snapshot.RetryCount -gt 0) {
        "recent=$($snapshot.RetryCount) last=$($snapshot.LastRetry)"
    } else {
        "recent=0"
    }
    $statusFormat = (
        "[scheduler][status] dataset={0} pid={1} state=running elapsed={2} phase={3} " +
        "recent_eval='{4}' heldout_repeat={5} retries={6} {7} log='{8}'"
    )
    Write-Host ($statusFormat -f `
            $Item.Dataset,
            $Item.Process.Id,
            (Format-Elapsed -StartedAt $Item.StartedAt),
            $snapshot.Phase,
            $snapshot.RecentEval,
            $snapshot.HeldoutRepeat,
            $retrySummary,
            $stateSummary,
            $Item.Stdout
    )
}

$pending = [System.Collections.Generic.Queue[string]]::new()
foreach ($dataset in $Datasets) {
    $pending.Enqueue($dataset)
}

$active = [System.Collections.Generic.List[object]]::new()
$results = [System.Collections.Generic.List[object]]::new()

$StopAfterFirstApply = -not $NoGate2
Write-Host "[scheduler] provider=$ActiveProvider datasets=$($Datasets -join ',') max_parallel=$MaxParallel smoke=$Smoke gate2=$Gate2 legacy_no_gate2=$NoGate2 stop_after_first_apply=$StopAfterFirstApply heldout_repeats=$HeldoutRepeats"
Write-Host "[scheduler] process logs=$LogDir"
Write-Host "[scheduler] status interval=${StatusIntervalSeconds}s (use -StatusIntervalSeconds to adjust)"

while ($pending.Count -gt 0 -or $active.Count -gt 0) {
    while ($pending.Count -gt 0 -and $active.Count -lt $MaxParallel) {
        $dataset = $pending.Dequeue()
        $stdoutPath = Join-Path $LogDir "$dataset.stdout.log"
        $stderrPath = Join-Path $LogDir "$dataset.stderr.log"
        $startedAt = Get-Date
        $launcher = New-ProcessLauncher `
            -Dataset $dataset `
            -Arguments (New-ExperimentArguments -Dataset $dataset) `
            -StdoutPath $stdoutPath `
            -StderrPath $stderrPath
        $process = Start-Process `
            -FilePath $env:ComSpec `
            -ArgumentList @("/d", "/c", $launcher.Launcher) `
            -WorkingDirectory $Repo `
            -WindowStyle Hidden `
            -PassThru

        $active.Add([pscustomobject]@{
            Dataset = $dataset
            Process = $process
            StartedAt = $startedAt
            Stdout = $stdoutPath
            Stderr = $stderrPath
            Status = $launcher.Status
            RunsRoot = if ($Smoke) { Join-Path $LogDir "runs" } else { Join-Path $Repo "prompt_runs" }
            RunDir = $null
        })
        Write-Host "[scheduler] started dataset=$dataset pid=$($process.Id) at=$($startedAt.ToString('s'))"
    }

    $completed = @($active | Where-Object { $_.Process.HasExited })
    if ($completed.Count -eq 0) {
        foreach ($item in @($active)) {
            Write-ActiveStatus -Item $item
        }
        Start-Sleep -Seconds $StatusIntervalSeconds
        continue
    }

    foreach ($item in $completed) {
        $item.Process.WaitForExit()
        $finishedAt = Get-Date
        $status = (Get-Content -LiteralPath $item.Status -Raw -ErrorAction SilentlyContinue).Trim()
        if ($status -notmatch "^-?\d+$") {
            $exitCode = -1
            Write-Host "[scheduler] missing or invalid exit status for dataset=$($item.Dataset): $status"
        } else {
            $exitCode = [int]$status
        }
        $duration = $finishedAt - $item.StartedAt
        $results.Add([pscustomobject]@{
            Dataset = $item.Dataset
            ExitCode = $exitCode
            Duration = $duration
            Stdout = $item.Stdout
            Stderr = $item.Stderr
        })
        [void]$active.Remove($item)
        $resultFormat = (
            "[scheduler][result] dataset={0} state=finished exit={1} duration={2:hh\:mm\:ss} " +
            "run={3} stdout={4} stderr={5}"
        )
        Write-Host ($resultFormat -f `
                $item.Dataset,
                $exitCode,
                $duration,
                (Get-RunDirectory -Item $item),
                $item.Stdout,
                $item.Stderr
        )
        $stderrTail = @(Get-Content -LiteralPath $item.Stderr -Tail 3 -ErrorAction SilentlyContinue)
        if ($stderrTail.Count -gt 0) {
            Write-Host ("[scheduler][result] dataset={0} stderr_tail='{1}'" -f $item.Dataset, ([string]::Join(" | ", $stderrTail)))
        }
    }
}

Write-Host "[scheduler] all scheduled datasets finished"
foreach ($result in $results) {
    Write-Host (
        "[scheduler] dataset={0} exit={1} duration={2:hh\:mm\:ss} stdout={3} stderr={4}" -f `
            $result.Dataset, $result.ExitCode, $result.Duration, $result.Stdout, $result.Stderr
    )
}

$failed = @($results | Where-Object { $_.ExitCode -ne 0 })
if ($failed.Count -gt 0) {
    exit 1
}
