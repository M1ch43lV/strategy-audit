$ErrorActionPreference = 'Continue'
Set-Location C:\Users\micro\GitHub\freqtrade-benchmarks\strategy-audit
$log = 'logs\hippo_top10_dispatch.log'
foreach ($s in 'BinHModWhiteHOV0','CombinedBinHClucAndSMAOffset_2','BB_RPB_TSL_RNG_V2_20211008','BB_RPB_TSL_jilv220_github_20211008','BinClucMadSMACore') {
  for ($i = 1; $i -le 8; $i++) {
    $plan = (& .\ftenv\Scripts\python.exe -m tools.pipeline_dispatcher --strategy $s 2>&1 | Out-String)
    $kind = if ($plan -match '"kind":\s*"(\w+)"') { $Matches[1] } else { 'unknown' }
    $gate = if ($plan -match '"gate":\s*"([\w-]+)"') { $Matches[1] } else { '' }
    "$(Get-Date -Format s) $s step=$i kind=$kind gate=$gate" | Add-Content $log
    if ($kind -ne 'run') { break }
    (& .\ftenv\Scripts\python.exe -m tools.pipeline_dispatcher --strategy $s --apply 2>&1 | Out-String) | Add-Content $log
  }
}
"$(Get-Date -Format s) DONE" | Add-Content $log
