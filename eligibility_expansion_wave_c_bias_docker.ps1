param(
    [switch] $RebuildRuntime,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $RunArguments
)

$ErrorActionPreference = "Stop"
$auditPath = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$image = "strategy-audit-runtime:2026.7"

docker image inspect $image *> $null
if ($RebuildRuntime -or $LASTEXITCODE -ne 0) {
    docker build --provenance=false `
        -f (Join-Path $auditPath "Dockerfile.audit") `
        -t $image $auditPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$imageId = docker image inspect $image --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Single sequential writer over the Wave C bias queue. Each verdict is stored
# the moment it exists, so an interrupted container leaves decided rows intact
# and the same command resumes with the rest.
docker run --rm `
    -e "PROFILE_RUNTIME_ID=docker:$imageId" `
    -v "${auditPath}:/audit" `
    -w /audit `
    --entrypoint python `
    $image eligibility_expansion_wave_c_bias.py @RunArguments
exit $LASTEXITCODE
