param(
    [switch] $RebuildRuntime,
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $BiasArguments
)

$ErrorActionPreference = "Stop"
$auditPath = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$image = "strategy-audit-runtime:2026.7"

docker image inspect $image *> $null
if ($RebuildRuntime -or $LASTEXITCODE -ne 0) {
    docker build --provenance=false `
        -f (Join-Path $PSScriptRoot "Dockerfile.audit") `
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
    $image -m evidence.profile_bias @BiasArguments
$runExit = $LASTEXITCODE
if ($runExit -ne 0) { exit $runExit }

# A shard owns its output while the analyzer runs. Once complete, merge it
# through the identity-checked canonical writer, which also regenerates every
# published pipeline-state view under one serialization lock.
$outputPath = $null
for ($index = 0; $index -lt $BiasArguments.Count; $index++) {
    if ($BiasArguments[$index] -eq "--output" -and
            $index + 1 -lt $BiasArguments.Count) {
        $outputPath = $BiasArguments[$index + 1]
        break
    }
    if ($BiasArguments[$index] -like "--output=*") {
        $outputPath = $BiasArguments[$index].Substring("--output=".Length)
        break
    }
}

if ($outputPath) {
    $canonical = [IO.Path]::GetFullPath((Join-Path $auditPath "evidence/PROFILE_BIAS.json"))
    $shard = if ([IO.Path]::IsPathRooted($outputPath)) {
        [IO.Path]::GetFullPath($outputPath)
    } else {
        [IO.Path]::GetFullPath((Join-Path $auditPath $outputPath))
    }
    if ($shard -ne $canonical) {
        $localPython = Join-Path $auditPath "ftenv/Scripts/python.exe"
        & $localPython -m evidence.profile_bias_merge --input $shard
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }
}
exit 0
