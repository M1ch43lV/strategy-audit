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

Run standalone repair tools as modules from the repository root, for example
`\.\ftenv\Scripts\python.exe -m repair.local_modules --selftest`.
