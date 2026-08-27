$env:PYTHONIOENCODING="utf-8"
$jobs = @()

for ($i = 0; $i -lt 8; $i++) {
    Write-Host "Starting shard $i/8..."
    $job = Start-Job -ScriptBlock {
        param($shardIndex)
        Set-Location "c:\Users\micro\GitHub\freqtrade-benchmarks\strategy-audit"
        $env:PYTHONIOENCODING="utf-8"
        ..\.venv\Scripts\python.exe corpus.py --shard "$shardIndex/8"
    } -ArgumentList $i
    $jobs += $job
}

Write-Host "All 8 shards started. Waiting for completion..."
Wait-Job -Job $jobs
Write-Host "All shards completed. Receiving output:"
Receive-Job -Job $jobs
