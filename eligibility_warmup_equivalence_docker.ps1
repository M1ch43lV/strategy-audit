param(
    [switch] $RebuildRuntime,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $QueueArguments
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

# The queue is a single sequential writer: it runs one original/override pair at
# a time and writes ELIGIBILITY_EXPANSION_EQUIVALENCE.json atomically after each
# pair, so an interrupted container leaves completed pairs intact and resumable.
docker run --rm `
    -e "PROFILE_RUNTIME_ID=docker:$imageId" `
    -v "${auditPath}:/audit" `
    -w /audit `
    --entrypoint python `
    $image eligibility_warmup_equivalence_queue.py @QueueArguments
exit $LASTEXITCODE
