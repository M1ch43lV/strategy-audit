param(
    [switch] $RebuildRuntime,
    [string] $ContainerName = "",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $EvaluationArguments
)

# Stages 9-13 for Model 0 (tools.regime_evaluation) inside the audit runtime image.
# The host cannot load TA-Lib when Windows application control blocks its DLL, and the
# image is the environment every other stage measures in.
$ErrorActionPreference = "Stop"
$auditPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$image = "strategy-audit-runtime:2026.7"

$existingImageId = docker image ls --quiet $image
if ($RebuildRuntime -or -not $existingImageId) {
    docker build --provenance=false `
        -f (Join-Path $PSScriptRoot "Dockerfile.audit") `
        -t $image $auditPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$imageId = docker image inspect $image --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$limits = @()
if ($ContainerName) { $limits += @("--name", $ContainerName) }

docker run --rm @limits `
    -e "PROFILE_RUNTIME_ID=docker:$imageId" `
    -v "${auditPath}:/audit" `
    -w /audit `
    --entrypoint python `
    $image -m tools.regime_evaluation @EvaluationArguments
exit $LASTEXITCODE
