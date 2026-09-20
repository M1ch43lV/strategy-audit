# Repair layer

This directory contains compatibility and environment restorations used to run
published strategies without silently changing their trading logic. Generated
repair evidence remains under [`../evidence/`](../evidence/); patched strategy
copies, when required, stay below `repair/patched/` and never replace upstream
sources under `repos/`.

`overrides.py` is the shared read-only lookup used by profile and warm-up
runners. `local_modules.py` restores author-supplied helper modules to the
import path and records its decisions. Other programs here implement or verify
specific repair classes documented in [`REGISTER.md`](REGISTER.md).

## Common repair controller

`repair.controller` is the single explicit entry point for the automatic
Class 1 and Class 2 repair writers and source-bound repair adjudication. It is
an orchestration layer, not a third source-repair class: Class 1 remains
source-preserving, while Class 2 remains a separate, proven overlay with its
own diff and source identity.

```powershell
.\ftenv\Scripts\python.exe -m repair.controller             # review only
.\ftenv\Scripts\python.exe -m repair.controller --apply     # run both classes serially
.\ftenv\Scripts\python.exe -m repair.controller --class class2 --apply
.\ftenv\Scripts\python.exe -m repair.controller --selftest
```

The controller refuses `--apply` while Docker has an active benchmark runner
or another repair controller owns its lock. It never changes `repos/`, it does
not promote a repair to a gate verdict, and it does not replace handler-owned
evidence. Each handler attempt is appended to
`evidence/REPAIR_CONTROLLER.jsonl`; Class 1 and Class 2 evidence remains in
their existing stores.

The Class 1 timeframe handler retries only records whose author-evidenced
timeframe attempt timed out, preserving each earlier attempt in the same
record. The adjudication handler writes `evidence/REPAIR_ADJUDICATION.json`
only for exact source-digest matches. It distinguishes source-bound
`refuse_repair` from an explicit `exclude_by_user_policy` scope decision. The
latter closes an unselected repair branch without claiming the strategy is
intrinsically unrepairable, and its technical triage context remains in the
record. A later owner decision can reopen it by changing the policy store;
neither kind of record changes source code.

## 1m OOM recovery at 5m

`repair.timeframe_5m_recovery` is a source-preserving resource-repair route.
It selects only the 60 implementations whose canonical 1m eight-pair pooled
Full-Backtest is `oom_confirmed` or `resource_inconclusive`. At an isolated 5m
execution timeframe it repeats Smoke, Look-ahead, Warm-up convergence, and
final Recursive-bias in that order. Only four passes permit an isolated
eight-pair 5m Full-Backtest.

It writes `evidence/TIMEFRAME_5M_RECOVERY.json` and
`evidence/TIMEFRAME_5M_RECOVERY_FULL.json`. These files do not change source,
canonical state, or generated status. A successful alternate full run remains
`pending_owner_promotion`; it never silently treats 5m as equal to the
authored 1m result. Run it with
`python -m repair.controller --class resource --apply`.

Run standalone repair tools as modules from the repository root, for example
`\.\ftenv\Scripts\python.exe -m repair.local_modules --selftest`.
