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

# Single sequential writer for the zero-warm-up diagnostic pilot. Each attempt
# is stored under its own startup value the moment it exists, so an interrupted
# container leaves finished attempts intact and the same command resumes.
# Re-measures the gate verdicts that 30 admitted rows inherited from the
# original author's sweep. Replaces an inherited verdict with a measured one.
docker run --rm `
    -e "PROFILE_RUNTIME_ID=docker:$imageId" `
    -v "${auditPath}:/audit" `
    -w /audit `
    --entrypoint python `
    $image eligibility_evidence_gap.py @RunArguments
exit $LASTEXITCODE
