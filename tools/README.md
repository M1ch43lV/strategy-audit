# Manual and corpus tools

This directory contains maintained support programs that are not benchmark
result stores. Corpus intake uses `harvest.py` (repositories) and
`adopt_source.py` (one file published without a repository, agreed with the
owner first, `PIPELINE_EXTENSIONS.md` Part 5), plus `census_repos.py`,
`expand.py`, `tfscan.py`, and the shared `harness.py`; `fetch_bulk.py` supplies
archived Binance spot candles. `evidence.strategy_feed` is a separate, review-only
Stage-0 discovery scanner: it records pinned feed sources but never downloads
them into `repos/`. `frequenthippo_ranking.py` belongs to the same review-only
group: it turns a third party's published ranking into one rank per strategy and
writes nothing. The remaining programs classify, triage, validate, or
publish current evidence on demand.

Run tools from the repository root. Prefer module form where supported, for
example `python -m tools.harness`; scripts with established command-line entry
points may be called as `python tools/<name>.py`.

The predecessor publication and its retired CI guards live under
`old/predecessor_audit/`. They are historical provenance, not current checks.
The current stage order and owned outputs are documented in `../PIPELINE.md`.
