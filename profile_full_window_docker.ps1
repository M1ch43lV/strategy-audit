param(
    [switch] $RebuildRuntime,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $FullWindowArguments
)

$ErrorActionPreference = "Stop"
$auditPath = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$image = "strategy-audit-runtime:2026.7"

docker image inspect $image *> $null
if ($RebuildRuntime -or $LASTEXITCODE -ne 0) {
    docker build --provenance=false -f (Join-Path $auditPath "Dockerfile.audit") `
        -t $image $auditPath
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
$imageId = docker image inspect $image --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

docker run --rm -e "PROFILE_RUNTIME_ID=docker:$imageId" `
    -v "${auditPath}:/audit" -w /audit --entrypoint python `
    $image profile_full_window.py @FullWindowArguments
exit $LASTEXITCODE
