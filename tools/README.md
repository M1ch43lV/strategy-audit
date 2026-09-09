# Manual and corpus tools

This directory contains maintained support programs that are not benchmark
result stores. Corpus intake uses `harvest.py`, `census_repos.py`, `expand.py`,
`tfscan.py`, and the shared `harness.py`; `fetch_bulk.py` supplies archived
Binance spot candles. The remaining programs classify, triage, validate, or
publish current evidence on demand.

Run tools from the repository root. Prefer module form where supported, for
example `python -m tools.harness`; scripts with established command-line entry
points may be called as `python tools/<name>.py`.

The predecessor publication and its retired CI guards live under
`old/predecessor_audit/`. They are historical provenance, not current checks.
The current stage order and owned outputs are documented in `../PIPELINE.md`.
