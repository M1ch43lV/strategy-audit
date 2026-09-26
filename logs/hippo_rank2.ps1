$ErrorActionPreference = 'Continue'
Set-Location C:\Users\micro\GitHub\freqtrade-benchmarks\strategy-audit
$log = 'logs\hippo_rank2.log'
$s = 'CombinedBinHClucAndSMAOffset'
(& .\ftenv\Scripts\python.exe -m evidence.strategy_status 2>&1 | Out-String) | Add-Content $log
for ($i = 1; $i -le 8; $i++) {
  $plan = (& .\ftenv\Scripts\python.exe -m tools.pipeline_dispatcher --strategy $s 2>&1 | Out-String)
  $kind = if ($plan -match '"kind":\s*"(\w+)"') { $Matches[1] } else { 'unknown' }
  $gate = if ($plan -match '"gate":\s*"([\w-]+)"') { $Matches[1] } else { '' }
  "$(Get-Date -Format s) $s step=$i kind=$kind gate=$gate" | Add-Content $log
  if ($kind -ne 'run') { break }
  (& .\ftenv\Scripts\python.exe -m tools.pipeline_dispatcher --strategy $s --apply 2>&1 | Out-String) | Add-Content $log
}
"$(Get-Date -Format s) DONE" | Add-Content $log
