# -*- coding: utf-8 -*-
"""Prove the FOttStrategy linear recurrence matches its original outputs."""
from __future__ import annotations

import importlib.util
import os
import types

import numpy as np
import pandas as pd


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.FOttStrategy({})


def _load_legacy_reference(path):
    """Emulate the writable Series view supplied by pre-Copy-on-Write pandas."""
    source = open(path, encoding="utf-8").read()
    old = 'df["Var"].iat[i] = (alpha * df["CMO"].iat[i] * df["close"].iat[i])'
    new = ('df.loc[df.index[i], "Var"] = '
           '(alpha * df["CMO"].iat[i] * df["close"].iat[i])')
    if source.count(old) != 1:
        raise AssertionError("FOtt legacy assignment anchor changed")
    source = source.replace(old, new)
    old_short = 'df["shortstop"] = 999999999999999999'
    if source.count(old_short) != 1:
        raise AssertionError("FOtt legacy shortstop anchor changed")
    # Pre-pandas-3 silently upcast this integer column when floats were stored.
    source = source.replace(old_short, 'df["shortstop"] = 999999999999999999.0')
    module = types.ModuleType("fott_legacy_reference")
    exec(compile(source, path, "exec"), module.__dict__)
    return module.FOttStrategy({})


def _frame(length, kind):
    rng = np.random.default_rng(20260828 + length)
    if kind == "rise":
        close = np.linspace(10.0, 30.0, length)
    elif kind == "fall":
        close = np.linspace(30.0, 10.0, length)
    else:
        close = 20.0 + np.cumsum(rng.normal(0, 0.3, length))
    return pd.DataFrame({"close": close})


def main():
    original_path = os.path.join(
        ROOT, "repos", "MelvynClark_Freqtrade-Strategy", "FOTT.py")
    original = _load_legacy_reference(original_path)
    repaired = _load("fott_repaired", os.path.join(
        ROOT, "user_data", "profile_repairs", "FOttStrategy.py"))
    checked = 0
    for length in (20, 50, 150, 300):
        for kind in ("rise", "fall", "random"):
            expected = original.ott(_frame(length, kind))
            actual = repaired.ott(_frame(length, kind))
            pd.testing.assert_frame_equal(actual, expected, check_exact=True)
            checked += 1
    print("FOtt linear recurrence equivalence: PASS (%d cases)" % checked)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
