"""Shared repair-store override lookup.

A repaired row has to be measured the way it was repaired, or a downstream
gate reports on a configuration nobody intends to use (the look-ahead gate
found this with Argrelextrema's timeframe repair, the recursive-bias ladder
separately with the same one). Every stage that runs a repaired row reads the
same repair stores through this one function, so a new repair store only has
to be added in one place.
"""
from __future__ import annotations

import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CONFIG_TIMEFRAME = re.compile(r"^timeframe\s*=\s*['\"]([0-9]+[mhdwM])['\"]", re.M)

REPAIR_STORES = (
    os.path.join(ROOT, "evidence/ELIGIBILITY_TIMEFRAME_REPAIR.json"),
    os.path.join(ROOT, "evidence/ELIGIBILITY_MODULE_REPAIR.json"),
    os.path.join(ROOT, "evidence/ELIGIBILITY_SIGNATURE_REPAIR.json"),
    os.path.join(ROOT, "evidence/ELIGIBILITY_FREQAI_REPAIR.json"),
    os.path.join(ROOT, "evidence/ELIGIBILITY_FREQAI_WTAI.json"),
    os.path.join(ROOT, "evidence/REPAIR_LOCAL_MODULES.json"),
)


def repair_overrides():
    """Config keys a repaired row must be run with, keyed by strategy."""
    out = {}
    for path in REPAIR_STORES:
        if not os.path.exists(path):
            continue
        results = json.load(io.open(path, encoding="utf-8")).get("results", {})
        for strategy, record in results.items():
            overrides = record.get("config_overrides") or {}
            if overrides:
                out.setdefault(strategy, dict(overrides))
    return out


def sibling_config_timeframe(canonical_file):
    """The timeframe from a same-directory `Config*.py`, if the strategy
    reads it from a sibling config module instead of declaring its own.

    2026-09-08, wave-2 futures/short harvest: 18 rows in
    `hamidreza07_freqai-strategy` read the value this way rather than
    stating it, which is why `evidence/execution_profiles.py`'s static source scan -
    looking for a literal `timeframe = ...` in the strategy file itself -
    finds nothing and `evidence/EXECUTION_PROFILES.csv` records `timeframe_source:
    unresolved`. All 18 still ran a real Probelauf, so the value was never
    actually missing, only indirected through the author's own sibling
    file. This reads the same file the strategy imports at runtime; it is
    not a different or invented value.

    Glob rather than a fixed `Config.py`: `SqueezeOff` imports
    `Config_SqueezeOff`, not `Config` - the same repository names its
    per-strategy config module after the strategy in some folders and
    plainly `Config` in others. Scoped to this one directory only, so the
    risk of picking up an unrelated file is the same as it would be for a
    literal `Config.py` check.

    Shared with evidence/execution_profiles.py (2026-09-08): the same 18-strategy gap
    that blocked the ladder's candle math also left evidence/EXECUTION_PROFILES.csv's
    own timeframe column empty for them, which cascades into
    evidence/regime_coverage.py reporting `unsupported_or_unknown_profile` even
    though the row already cleared both bias gates. One function, read from
    both places, so the two never see a different answer for the same file.
    """
    directory = os.path.dirname(os.path.join(ROOT, canonical_file.replace("/", os.sep)))
    if not os.path.isdir(directory):
        return None
    candidates = sorted(name for name in os.listdir(directory)
                        if name.startswith("Config") and name.endswith(".py"))
    for name in candidates:
        found = _timeframe_in_file(os.path.join(directory, name))
        if found:
            return found
    return None


def _timeframe_in_file(path):
    if not os.path.isfile(path):
        return None
    text = io.open(path, encoding="utf-8", errors="replace").read()
    match = _CONFIG_TIMEFRAME.search(text)
    return match.group(1) if match else None


def imported_module_timeframe(python_path, module):
    """The timeframe declared in `module`'s own file at `python_path`.

    Distinct from `sibling_config_timeframe`: that one guesses from a name
    match in the strategy's own directory. This reads the exact file
    `repair/local_modules.py` already proved importable by actually running
    the import - not a same-directory guess, the file the strategy loads.

    2026-09-09: `Hammer` and `KeltnerBounce` (hamidreza07/freqai-strategy)
    read `Config.timeframe` from a sibling module their own directory does
    not carry - `restore_copied_local_module` already resolved `Config` to
    `BuyDips/Config.py`, one of 18 byte-identical copies across the same
    batch, all 21 available copies declaring `timeframe = '5m'`. That
    resolution is the answer to "which file does this strategy actually
    load", so its own declared value is not a guess about the two rows that
    lack a copy - it is the value the copy they do load already states.
    """
    top = module.split(".")[0]
    for relative in (top + ".py", os.path.join(top, "__init__.py")):
        found = _timeframe_in_file(
            os.path.join(ROOT, python_path.replace("/", os.sep), relative))
        if found:
            return found
    return None
