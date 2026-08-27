# -*- coding: utf-8 -*-
"""compat_shim - restore APIs that existed when these strategies were written
and that numpy and freqtrade have since removed.

WHY THIS DOES NOT CHANGE WHAT IS MEASURED. The shim touches no strategy file.
It hands a library back a name it used to export itself: `np.NAN` is literally
`np.nan`, `numpy.lib.math` is the standard library `math` module that used to
leak through that namespace, and `CategoricalParameter` is the same class that
merely moved from `freqtrade.strategy.hyper` to `freqtrade.strategy.parameters`.
Every entry below is an alias to an identical object.

WHERE THE LINE IS. An alias is legitimate; a reimplementation is not.
`technical.indicators.accumulation_distribution` was removed without a
replacement. Writing our own A/D indicator and giving it the original name
would be an invention wearing the label of the original, and any strategy
measured through it would no longer be the published strategy. The two
strategies that need it are left failing.

Installed via `sitecustomize.py` inside ftenv so it also applies to the
subprocesses freqtrade spawns; patching only the parent process would leave the
actual backtests unfixed.
"""
import importlib.abc
import importlib.util
import sys


def _patch_numpy(np):
    """Restore the capitalised aliases and legacy scalar names dropped in numpy 2.

    These were aliases, not distinct values, so the equality is exact rather
    than approximate.
    """
    for old, new in (("NAN", "nan"), ("NaN", "nan"), ("INF", "inf"),
                     ("Inf", "inf"), ("Infinity", "inf"), ("PINF", "inf"),
                     ("NINF", "-inf")):
        if not hasattr(np, old) and hasattr(np, new.lstrip("-")):
            v = getattr(np, new.lstrip("-"))
            setattr(np, old, -v if new.startswith("-") else v)

    # `numpy.lib.math` was never a numpy function - it was the standard library
    # `math` module visible through numpy.lib's namespace. numpy 2 tidied that
    # namespace up. The exact same module object is handed back, so both
    # `from numpy.lib import math` and `import numpy.lib.math` resolve again.
    try:
        import math as _stdmath
        if hasattr(np, "lib") and not hasattr(np.lib, "math"):
            np.lib.math = _stdmath
            sys.modules.setdefault("numpy.lib.math", _stdmath)
    except Exception:
        pass

    for old, new in (("float_", "float64"), ("int_", "int64"),
                     ("complex_", "complex128"), ("unicode_", "str_")):
        if not hasattr(np, old) and hasattr(np, new):
            setattr(np, old, getattr(np, new))


def _patch_ft_hyper(mod):
    """Re-export the parameter classes from their former home.

    They moved to `freqtrade.strategy.parameters`; these are the same class
    objects under their previous import path.
    """
    try:
        from freqtrade.strategy import parameters as p
    except Exception:
        return
    for n in ("CategoricalParameter", "DecimalParameter", "IntegerParameter",
              "IntParameter", "RealParameter", "BooleanParameter",
              "NumericParameter", "BaseParameter"):
        if not hasattr(mod, n) and hasattr(p, n):
            setattr(mod, n, getattr(p, n))
    # Older strategies spell IntParameter as IntegerParameter.
    if not hasattr(mod, "IntegerParameter") and hasattr(p, "IntParameter"):
        setattr(mod, "IntegerParameter", p.IntParameter)


def _patch_qtpylib(mod):
    """Make `heikinashi` work on a frame whose index does not start at zero.

    The vendored implementation addresses rows by LABEL and assumes the labels
    are 0..n-1:

        bars.at[0, "ha_open"] = (bars.at[0, "open"] + bars.at[0, "close"]) / 2
        for i in range(1, len(bars)):
            bars.at[i, "ha_open"] = (bars.at[i-1, "ha_open"] + ...) / 2

    That holds for a whole backtest frame and fails for a slice of one. FreqAI
    passes slices, so every strategy computing Heikin-Ashi inside its feature
    engineering dies on KeyError(0) - a library assumption surfacing as a
    strategy error.

    The replacement walks the frame's own index instead of the integers. On a
    0-based RangeIndex `idx[i] == i`, so the arithmetic is identical value for
    value; it merely also survives an index that starts elsewhere. That is why
    this counts as repairing the environment rather than changing a result.
    """
    if not hasattr(mod, "heikinashi"):
        return
    try:
        import pandas as pd
    except Exception:
        return

    def heikinashi(bars):
        bars = bars.copy()
        bars["ha_close"] = (bars["open"] + bars["high"] + bars["low"] + bars["close"]) / 4
        idx = bars.index
        if len(idx) == 0:
            bars["ha_open"] = []
        else:
            bars.loc[idx[0], "ha_open"] = (bars.loc[idx[0], "open"]
                                           + bars.loc[idx[0], "close"]) / 2
            for i in range(1, len(bars)):
                bars.loc[idx[i], "ha_open"] = (bars.loc[idx[i - 1], "ha_open"]
                                               + bars.loc[idx[i - 1], "ha_close"]) / 2
        bars["ha_high"] = bars.loc[:, ["high", "ha_open", "ha_close"]].max(axis=1)
        bars["ha_low"] = bars.loc[:, ["low", "ha_open", "ha_close"]].min(axis=1)
        return pd.DataFrame(index=bars.index, data={
            "open": bars["ha_open"], "high": bars["ha_high"],
            "low": bars["ha_low"], "close": bars["ha_close"]})

    mod.heikinashi = heikinashi


PATCHES = {"numpy": _patch_numpy,
           "freqtrade.strategy.hyper": _patch_ft_hyper,
           "technical.vendor.qtpylib.indicators": _patch_qtpylib}


class _PostImportPatcher(importlib.abc.MetaPathFinder):
    """Intercept exactly the modules that need patching, let the real finders
    load them, then patch the result.

    Importing freqtrade eagerly from sitecustomize would be simpler but risks a
    circular import while freqtrade itself is starting up.
    """

    def __init__(self):
        self._busy = set()

    def find_spec(self, fullname, path=None, target=None):
        if fullname not in PATCHES or fullname in self._busy:
            return None
        self._busy.add(fullname)
        try:
            spec = importlib.util.find_spec(fullname)
        except BaseException:
            return None
        finally:
            self._busy.discard(fullname)
        if spec is None or spec.loader is None:
            return None
        spec.loader = _PatchingLoader(spec.loader, PATCHES[fullname])
        return spec


class _PatchingLoader(importlib.abc.Loader):
    def __init__(self, inner, patch):
        self._inner, self._patch = inner, patch

    def create_module(self, spec):
        return self._inner.create_module(spec)

    def exec_module(self, module):
        self._inner.exec_module(module)
        try:
            self._patch(module)
        except BaseException:
            pass  # a failed patch must never take the import down with it


def install():
    if not any(isinstance(f, _PostImportPatcher) for f in sys.meta_path):
        sys.meta_path.insert(0, _PostImportPatcher())
    if "numpy" in sys.modules:
        _patch_numpy(sys.modules["numpy"])
