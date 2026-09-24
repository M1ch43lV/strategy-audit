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
writes nothing. `strategy_ideas.py` is the other reader of its kind: it extracts
the facts an interpretation needs, renders `strategy_ideas.html`, and prints the
family ranking (`--rank`) that decides which families that page describes first.
`source_dates.py` completes the set: it collects the dates that really exist per
strategy (a date in the file name, the site's post date, the last commit in the
repository the file came from) into `evidence/SOURCE_DATES.json`, resumable
because the GitHub API is rate limited without a token. It also names the
repositories whose files cluster on one commit date - at least 90 % of at least
five dated files - because in those the commit date is the date of an import, not
of a revision; that derived map is rewritten by `--recompute`.
The remaining programs classify, triage, validate, or
publish current evidence on demand.

Run tools from the repository root. Prefer module form where supported, for
example `python -m tools.harness`; scripts with established command-line entry
points may be called as `python tools/<name>.py`.

The predecessor publication and its retired CI guards live under
`old/predecessor_audit/`. They are historical provenance, not current checks.
The current stage order and owned outputs are documented in `../PIPELINE.md`.
