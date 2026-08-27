#!/bin/bash
# Kerzen fuer alle Timeframes, die die 312 ladenden Strategien deklarieren.
# Reihenfolge nach Anzahl betroffener Strategien - der groesste Nutzen zuerst,
# damit ein Abbruch die wichtigsten Daten schon auf der Platte hat.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
export AUDIT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$AUDIT_ROOT"
PY="./ftenv/Scripts/python.exe"
for TF in 5m 15m 4h 1d 30m 6h 3m 2h 1w 1m; do
  echo "=============== $TF  ($(date +%H:%M:%S)) ==============="
  PYTHONIOENCODING=utf-8 "$PY" repair/fetch_bulk_upstream.py "$TF" 2>&1 | tail -20
  echo "--- $TF fertig ($(date +%H:%M:%S)) ---"
done
echo "ALLE TIMEFRAMES FERTIG"
