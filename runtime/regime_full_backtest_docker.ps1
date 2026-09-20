param(
    [switch] $RebuildRuntime,
    [switch] $TensorflowRuntime,
    # Optional container limits, for running several containers side by side. The
    # memory limit is also the swap limit, so a run that outgrows it is killed on
    # its own (exit -9, recorded as resource_inconclusive) instead of pushing the
    # whole VM into swap. Without them the container behaves as before.
    [string] $MemoryLimit = "",
    [double] $Cpus = 0,
    [string] $ContainerName = "",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $BacktestArguments
)

$ErrorActionPreference = "Stop"
$auditPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
if ($TensorflowRuntime) {
    $image = "strategy-audit-tensorflow-runtime:2026.7"
    $dockerfile = "Dockerfile.audit-tensorflow"
} else {
    $image = "strategy-audit-runtime:2026.7"
    $dockerfile = "Dockerfile.audit"
}

$existingImageId = docker image ls --quiet $image
if ($RebuildRuntime -or -not $existingImageId) {
    docker build --provenance=false `
        -f (Join-Path $PSScriptRoot $dockerfile) `
        -t $image $auditPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$imageId = docker image inspect $image --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$limits = @()
if ($MemoryLimit) { $limits += @("--memory", $MemoryLimit, "--memory-swap", $MemoryLimit) }
if ($Cpus -gt 0) { $limits += @("--cpus", "$Cpus") }
if ($ContainerName) { $limits += @("--name", $ContainerName) }

docker run --rm @limits `
    -e "PROFILE_RUNTIME_ID=docker:$imageId" `
    -v "${auditPath}:/audit" `
    -w /audit `
    --entrypoint python `
    $image -m regime.full_backtest @BacktestArguments
exit $LASTEXITCODE
