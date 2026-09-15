#!/bin/bash
# Candles for every timeframe declared by the 312 strategies being downloaded.
# Process timeframes in descending order of affected strategies so the greatest
# benefit is available first if the run is interrupted.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export AUDIT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$AUDIT_ROOT"
PY="./ftenv/Scripts/python.exe"
for TF in 5m 15m 4h 1d 30m 6h 3m 2h 1w 1m; do
  echo "=============== $TF  ($(date +%H:%M:%S)) ==============="
  PYTHONIOENCODING=utf-8 "$PY" repair/fetch_bulk_upstream.py "$TF" 2>&1 | tail -20
  echo "--- $TF complete ($(date +%H:%M:%S)) ---"
done
echo "ALL TIMEFRAMES COMPLETE"
