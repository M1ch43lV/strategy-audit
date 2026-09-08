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

ROOT = os.path.dirname(os.path.abspath(__file__))

REPAIR_STORES = (
    os.path.join(ROOT, "ELIGIBILITY_TIMEFRAME_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_MODULE_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_SIGNATURE_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_FREQAI_REPAIR.json"),
    os.path.join(ROOT, "ELIGIBILITY_FREQAI_WTAI.json"),
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
