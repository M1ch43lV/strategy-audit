param(
    [switch] $RebuildRuntime,
    [switch] $TensorflowRuntime,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $BacktestArguments
)

$ErrorActionPreference = "Stop"
$auditPath = (Resolve-Path -LiteralPath $PSScriptRoot).Path
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
        -f (Join-Path $auditPath $dockerfile) `
        -t $image $auditPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$imageId = docker image inspect $image --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

docker run --rm `
    -e "PROFILE_RUNTIME_ID=docker:$imageId" `
    -v "${auditPath}:/audit" `
    -w /audit `
    --entrypoint python `
    $image -m regime.full_backtest @BacktestArguments
exit $LASTEXITCODE
