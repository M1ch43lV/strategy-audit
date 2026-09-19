param(
    [switch] $RebuildRuntime,
    [switch] $TensorflowRuntime,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $SmokeArguments
)

$ErrorActionPreference = "Stop"
$auditPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$image = if ($TensorflowRuntime) {
    "strategy-audit-tensorflow-runtime:2026.7"
} else {
    "strategy-audit-runtime:2026.7"
}
$dockerfile = if ($TensorflowRuntime) {
    "Dockerfile.audit-tensorflow"
} else {
    "Dockerfile.audit"
}

docker image inspect $image *> $null
if ($RebuildRuntime -or $LASTEXITCODE -ne 0) {
    docker build --provenance=false `
        -f (Join-Path $PSScriptRoot $dockerfile) `
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
    $image -m evidence.profile_smoke @SmokeArguments
exit $LASTEXITCODE
