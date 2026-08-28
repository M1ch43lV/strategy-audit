# -*- coding: utf-8 -*-
"""Compatibility overlay for werkkrew's Solipsis custom indicators.

All upstream names are re-exported. Only RMI is replaced because current
pandas rejects the upstream dataframe-wide ``fillna(0)`` when the Freqtrade
frame includes its timezone-aware ``date`` column. The indicator consumes only
``maxup`` and ``maxdown``; filling those two numeric intermediates preserves
the reachable calculation without coercing unrelated columns.
"""
from __future__ import annotations

import importlib.util
import os


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPSTREAM = os.path.join(
    ROOT, "repos", "werkkrew_freqtrade-strategies", "strategies", "solipsis",
    "custom_indicators.py")
SPEC = importlib.util.spec_from_file_location("_solipsis_custom_indicators_upstream", UPSTREAM)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

for _name in dir(MODULE):
    if not _name.startswith("__"):
        globals()[_name] = getattr(MODULE, _name)


def RMI(dataframe, *, length=20, mom=5):
    """Upstream RMI with dtype-safe filling of its numeric intermediates."""
    df = dataframe.copy()
    df["maxup"] = (df["close"] - df["close"].shift(mom)).clip(lower=0)
    df["maxdown"] = (df["close"].shift(mom) - df["close"]).clip(lower=0)
    df[["maxup", "maxdown"]] = df[["maxup", "maxdown"]].fillna(0)
    df["emaInc"] = ta.EMA(df, price="maxup", timeperiod=length)
    df["emaDec"] = ta.EMA(df, price="maxdown", timeperiod=length)
    df["RMI"] = np.where(
        df["emaDec"] == 0, 0, 100 - 100 / (1 + df["emaInc"] / df["emaDec"]))
    return df["RMI"]
