# Freqtrade market-regime benchmark

This repository builds a reproducible benchmark of public Freqtrade strategies
across different market conditions. It first proves that a strategy loads,
trades, and passes the required look-ahead and recursive-bias checks. It then
measures admitted strategies over one pooled eight-pair portfolio and attributes
their trades to causal BTC and coin-specific regimes.

The current status contains 1,050 implementations. Counts change as resumable
measurements finish, so use [`strategy_status.html`](strategy_status.html) or
[`STRATEGY_STATUS.csv`](STRATEGY_STATUS.csv) rather than copying a count from
this README.

## Benchmark models

The frozen primary model is Wilder DMI/ADX(14), calculated from completed daily
candles and shifted by one UTC day. It yields `BULL`, `BEAR`, `SIDEWAYS`, and
`TRANSITION`. A six-phase reporting view additionally separates volatility.

- **Model 0:** original strategy without a regime gate.
- **Model 1:** entries gated by preregistered global BTC states.
- **Model 2:** entries gated only by local coin states; it does not use BTC.
- **Model 3:** entries require both the Model 1 BTC and Model 2 coin gate.

Original exits remain authoritative. Ranked output is forbidden while choices
marked `OPEN` in [`REGIME_PREREGISTRATION.md`](REGIME_PREREGISTRATION.md)
remain unresolved.

## Start here

1. [`HANDOFF.md`](HANDOFF.md): live runner and machine state.
2. [`DOCUMENT_MAP.md`](DOCUMENT_MAP.md): authority and reading order.
3. [`REGIME_PREREGISTRATION.md`](REGIME_PREREGISTRATION.md): frozen rules.
4. [`PIPELINE.md`](PIPELINE.md): program order, inputs, and outputs.
5. [`strategy_status.html`](strategy_status.html): current strategy evidence.

`REGIME_AUDIT_PLAN.md` records design reasoning, but is not the rulebook.

## Repository layout

```text
strategy-audit/
├── README.md, HANDOFF.md, DOCUMENT_MAP.md, PIPELINE.md
│   User entry points, live baton, authority map, and run order
├── REGIME_PREREGISTRATION.md, REGIME_AUDIT_PLAN.md
│   Frozen methodology and detailed design record
├── STRATEGY_STATUS.{csv,md}, strategy_status.html
│   Current published strategy inventory
├── regime/
│   Regime features, Model 0/1/2/3 runners, attribution, comparison
├── results/regime/
│   Resumable benchmark manifests, archives, and regime summaries
├── repair/                 Compatibility overlays and repair provenance
├── tools/                  Manual generators, triage, and publication tools
├── runtime/                Dockerfiles, requirements, configs, and wrappers
├── cluster/                A-priori strategy taxonomy, never an entry gate
├── repos/                  Downloaded upstream sources; not versioned
├── user_data/              Candles and Freqtrade runtime state; not versioned
├── corpus/                 Historical cards still consumed as provenance
├── old/                    Superseded and predecessor-study material
└── graphify-out/           Local generated code graph; not versioned
```

Current eligibility/profile generators and their stores will be relocated only
as dependency-checked families. Moving a store independently from its atomic
writer would break resume and staleness guarantees.

## Reproduction and safety

Use `ftenv/Scripts/python.exe` for native commands. Before any benchmark, run
the process, Docker, lock, and artifact checks in `HANDOFF.md`; never start two
writers for one manifest.

```powershell
.\ftenv\Scripts\python.exe strategy_status.py --check
.\ftenv\Scripts\python.exe tools\strategy_classification.py --check
.\ftenv\Scripts\python.exe strategy_status.py --selftest
```

After code changes use `graphify update .`. This is the AST-only path. Do not
use `graphify extract .` for routine updates: it performs semantic document
extraction and consumes API quota. A local fail-open post-commit hook runs the
AST-only update when Graphify is installed.

## Interpretation limits

- Admission means technically auditable, not profitable.
- Process exit `-9` is resource-inconclusive, not a strategy defect.
- Pairwise checks do not replace pooled shared-capital backtests.
- Attribution of existing trades is not a gated backtest.
- Missing local regime evidence fails closed for Models 2 and 3.

Historical case studies and side investigations are retained under
[`old/predecessor_audit/`](old/predecessor_audit/).

## Licence

MIT for code. Analysis text may be quoted with attribution.
