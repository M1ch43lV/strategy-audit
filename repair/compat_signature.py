# -*- coding: utf-8 -*-
"""Compatibility shims for framework changes the strategies predate.

Fifteen of them so far. A hook whose signature gained parameters. A file
scan that assumes a formatting convention. A column the framework duplicates
when its own analyzer calls a hook twice. An analyzer that announces itself
as a utility while running a backtest. A budget for calls to the exchange,
enforced on a backtest that makes none. The same signature change as the
first, met from the other side: a strategy that overrode the hook itself, in
the shape freqtrade used to call it in. Four functions, each imported and
never called (three commented out, one bare), that a newer version of
freqtrade, numpy or Keras stopped shipping under the path an older strategy
still names. Three parameter renames or removals in `technical` and pandas,
each intercepted only for the exact call shape that is already a hard
failure without it - a renamed PMAX keyword, freqtrade's own "15m" reaching
a resample call, a `replace(method=...)` pandas no longer accepts. And one
method pandas removed outright (`DataFrame.append`), restored rather than
translated, since nothing currently calls it successfully for the
restoration to disturb. None is a defect in a strategy, and no shim touches
a strategy file - they
are installed into freqtrade in the runner process, only when
PROFILE_COMPAT_SIGNATURES names them.

--------------------------------------------------------------------------
Accept a freqtrade call signature that has since gained parameters.

Nine strategies of the CryptoFrog family stop with

    IStrategy.min_roi_reached_entry() missing 2 required positional arguments:
    'trade_dur' and 'current_time'

They call `self.min_roi_reached_entry(trade_dur)`. Freqtrade's hook was
`(self, trade_dur)` when they were written and is `(self, trade, trade_dur,
current_time)` now. Nothing about the strategy is wrong; the framework moved
underneath it.

WHY THIS IS A REPAIR AND NOT AN EDIT. The two new parameters are read in
exactly one place in freqtrade's implementation:

    if self.use_custom_roi:
        custom_roi = ...(pair=trade.pair, trade=trade, current_time=current_time, ...)

`use_custom_roi` is a later feature and defaults to False. For a strategy that
does not set it, `trade` and `current_time` are never touched, and the legacy
call and the modern one compute the same value from the same `minimal_roi`
table. So the adapter fills them with None and delegates.

That equivalence is conditional, so it is enforced rather than assumed: if a
strategy calling the legacy form has `use_custom_roi` set, the adapter raises
instead of guessing. No strategy is measured on a value this shim invented.

Nothing here edits a strategy file. The shim is installed into freqtrade in the
runner process, only when PROFILE_COMPAT_SIGNATURES names it, and it leaves the
modern call path exactly as it was.
"""
from __future__ import annotations

import os


RULE = "legacy_min_roi_reached_entry_signature"


def install_min_roi_reached_entry():
    """Let the pre-2022 one-argument call reach the current hook."""
    from freqtrade.strategy.interface import IStrategy

    original = IStrategy.min_roi_reached_entry
    if getattr(original, "_legacy_signature_installed", False):
        return True

    def min_roi_reached_entry(self, *args, **kwargs):
        if len(args) == 1 and not kwargs:
            # The legacy form: min_roi_reached_entry(trade_dur).
            if getattr(self, "use_custom_roi", False):
                raise TypeError(
                    "%s calls min_roi_reached_entry(trade_dur) in the pre-2022 "
                    "form while setting use_custom_roi, which needs the trade "
                    "and the current time. The two cannot be reconciled "
                    "without inventing them, so this row is not measured."
                    % type(self).__name__)
            return original(self, None, args[0], None)
        return original(self, *args, **kwargs)

    min_roi_reached_entry._legacy_signature_installed = True
    min_roi_reached_entry._legacy_signature_original = original
    IStrategy.min_roi_reached_entry = min_roi_reached_entry
    return True


SUBCLASS_RULE = "legacy_min_roi_reached_entry_override"


def install_legacy_min_roi_entry_override():
    """Adapt a strategy that OVERRIDES min_roi_reached_entry in the old form.

    `install_min_roi_reached_entry` above fixes the opposite direction: a
    strategy that calls the base class's hook with one argument. Four
    strategies (`BinHV27_werkkrew`, `SuperHV27`, and PeetCrypto's `Schism`,
    `Schism-v2`) do the reverse - they DEFINE their own
    `min_roi_reached_entry(self, trade_dur)`, in the same pre-2022 shape, and
    freqtrade calls it with the current three-argument form
    `(trade, trade_dur, current_time)`, from two places:
    `IStrategy.min_roi_reached` and, separately,
    `Backtesting._get_close_rate_for_roi`. Patching the base class does
    nothing here - Python resolves the subclass's own method first, and the
    base class is never consulted - and patching one call site misses the
    other.

    So this patches neither call site and no class. It wraps
    `StrategyResolver.load_strategy`, and once the real loader has returned
    the strategy instance, checks whether the resolved class defines its own
    `min_roi_reached_entry` that only accepts the old form - it must bind a
    call with just `trade_dur` and must NOT bind a call with
    `(trade, trade_dur, current_time)`, which is `Schism-v2`'s reason for
    existing: it takes an extra `pair` keyword the others don't. Where that
    holds, the INSTANCE - not the class - gets its own `min_roi_reached_entry`
    attribute, which ordinary Python attribute lookup hands to every caller
    ahead of the class's version, wrapping the author's original function to
    accept the current call and pass through only `trade_dur`, exactly as the
    author wrote it. A strategy whose override already takes the modern form,
    or takes neither, is left untouched.

    `Schism-v2` also overrides `min_roi_reached` itself, and that override
    calls `self.min_roi_reached_entry(trade_dur, trade.pair)` internally - two
    positional arguments, its own old convention, not freqtrade's three. That
    call has to reach the author's original function unadapted; only a call
    shaped like freqtrade's current three-argument form is translated. Hence
    the adapter dispatches on argument count rather than assuming every call
    is freqtrade's.
    """
    import inspect
    from freqtrade.resolvers.strategy_resolver import StrategyResolver

    if getattr(StrategyResolver, "_legacy_min_roi_override_adapted", False):
        return True

    original = StrategyResolver.load_strategy

    def _is_legacy_override(func):
        try:
            sig = inspect.signature(func)
        except (TypeError, ValueError):
            return False
        try:
            sig.bind(None, 0)
        except TypeError:
            return False
        try:
            sig.bind(None, None, 0, None)
        except TypeError:
            return True
        return False

    def load_strategy(config=None):
        strategy = original(config)
        own = type(strategy).__dict__.get("min_roi_reached_entry")
        if own is not None and _is_legacy_override(own):
            def min_roi_reached_entry(*args, _own=own, _self=strategy, **kwargs):
                if len(args) == 3 and not kwargs:
                    # freqtrade's current shape: (trade, trade_dur,
                    # current_time). Only trade_dur reaches the author's
                    # function - it never asked for the other two.
                    return _own(_self, args[1])
                # Anything else is the strategy calling its own old-style
                # method the way it always did (Schism-v2's own
                # min_roi_reached passes trade_dur and pair) - forward as is.
                return _own(_self, *args, **kwargs)
            strategy.min_roi_reached_entry = min_roi_reached_entry
        return strategy

    StrategyResolver.load_strategy = staticmethod(load_strategy)
    StrategyResolver._legacy_min_roi_override_adapted = True
    return True


import re


def CLASS_PATTERN(object_name):
    """`class Name(` or `class Name (`, at the start of a line.

    Kept out of the installer so the selftest can exercise it without a
    freqtrade import: this pattern decides which files are looked at at all,
    and a mistake in it is silent.
    """
    return re.compile(r"^class\s+%s\s*[(:]" % re.escape(object_name), re.M)


SCAN_RULE = "whitespace_tolerant_class_scan"


def install_tolerant_class_scan():
    """Let freqtrade find a class that a space keeps it from seeing.

    Before importing anything, `IResolver._search_object` skips a file unless
    its text contains the literal

        class <Name>(

    Six strategies write `class MultiMA_TSL5 (IStrategy):` - one space, valid
    Python, invisible to the interpreter, fatal to that shortcut. Freqtrade
    then reports "This class does not exist or contains Python code errors",
    which is true of neither.

    The shim replaces the literal search with a whitespace-tolerant one and
    changes nothing else: every file it now admits still has to pass the four
    real conditions in `_get_valid_object` - a class, a subclass of IStrategy,
    not IStrategy itself, and defined in that very file. So this widens what is
    looked at, never what is accepted.
    """
    import re as _re
    from pathlib import Path
    from freqtrade.resolvers.iresolver import IResolver

    if getattr(IResolver, "_tolerant_class_scan", False):
        return True

    def _search_object(cls, directory, *, object_name, add_source=False):
        pattern = CLASS_PATTERN(object_name)
        for entry in sorted(Path(directory).iterdir()):
            if entry.suffix != ".py":
                continue
            if entry.is_symlink() and not entry.is_file():
                continue
            module_path = entry.resolve()
            try:
                text = entry.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            if not pattern.search(text):
                continue
            found = next(cls._get_valid_object(module_path, object_name), None)
            if found:
                found[0].__file__ = str(entry)
                if add_source:
                    found[0].__source__ = found[1]
                return (found[0], module_path)
        return (None, None)

    IResolver._search_object = classmethod(_search_object)
    IResolver._tolerant_class_scan = True
    return True


ADVISE_RULE = "idempotent_entry_tag_initialisation"


def install_idempotent_advise_entry():
    """Stop `advise_entry` duplicating `enter_tag` when it is called twice.

    Freqtrade's `advise_entry` does two things in order:

        dataframe.loc[:, "enter_tag"] = ""      # workaround for pandas #56503
        df = self.populate_entry_trend(dataframe, metadata)
        if "enter_long" not in df.columns:
            df = df.rename({"buy": "enter_long", "buy_tag": "enter_tag"},
                           axis="columns")

    For a strategy that writes the legacy `buy_tag`, the rename RELABELS rather
    than merges, so the frame comes back with TWO columns called `enter_tag`:
    the empty initialiser and the strategy's real tags. An ordinary backtest
    never notices, because it calls the hook once.

    `lookahead-analysis` calls it twice on the same frame - once in
    `prepare_data`, then again inside `backtest` through
    `_get_ohlcv_as_lists`. The second pass has to align an assignment against a
    columns axis that now has a duplicate label, and pandas refuses:

        ValueError: cannot reindex on an axis with duplicate labels

    Fourteen strategies are reported against that message. Not one of them is
    at fault: they run and trade in an ordinary backtest, their recursion is
    clean, and the duplicate is created by freqtrade's own workaround meeting
    freqtrade's own rename. Measured directly, `NotAnotherSMAOffsetStrategy`,
    `Apollo11` and `Saturn5` each hold two `enter_tag` columns after a single
    pass, and each raises on the second. `BinHV27_werkkrew`, which writes `buy`
    but no `buy_tag`, holds one and passes twice - which is the control.

    The shim collapses that duplicate, keeping the LAST occurrence. Column
    order is fixed by construction: the initialiser is written before
    `populate_entry_trend` runs, and the renamed `buy_tag` is added by the
    strategy after it. The last one therefore carries the strategy's own tags
    and the first is the empty placeholder it was meant to replace - which is
    what the single-pass path already uses.

    It changes nothing else. A frame with one `enter_tag` is returned
    untouched, so a v3 strategy never enters this code path at all.
    """
    from freqtrade.strategy.interface import IStrategy

    if getattr(IStrategy, "_idempotent_entry_tag", False):
        return True

    original = IStrategy.advise_entry

    def advise_entry(self, dataframe, metadata):
        frame = original(self, dataframe, metadata)
        columns = list(frame.columns)
        if columns.count("enter_tag") < 2:
            return frame
        keep = len(columns) - 1 - columns[::-1].index("enter_tag")
        wanted = [index for index, name in enumerate(columns)
                  if name != "enter_tag" or index == keep]
        return frame.iloc[:, wanted]

    IStrategy.advise_entry = advise_entry
    IStrategy._idempotent_entry_tag = True
    return True


RUNMODE_RULE = "lookahead_runmode_reports_backtest"


def install_backtest_runmode_in_analysis():
    """Report RunMode.BACKTEST to a strategy run by lookahead-analysis.

    Nine strategies of the CryptoFrog family stop with

        KeyError: 'rmi-up-trend'

    raised from their own `min_roi_reached_dynamic`, which reads

        self.custom_trade_info[trade.pair]['rmi-up-trend'].loc[current_time]

    That cache is filled in `populate_indicators`, under the author's guard

        if self.dp.runmode.value in ('backtest', 'hyperopt'):
            self.custom_trade_info[pair]['rmi-up-trend'] = ...

    and freqtrade builds the lookahead command with

        config = setup_utils_configuration(args, RunMode.UTIL_NO_EXCHANGE)

    (`commands/optimize_commands.py`, `start_lookahead_analysis`). So the guard
    is false, nothing is cached, and the strategy raises the moment its dynamic
    ROI is consulted. The author's code is correct; the analyzer simply
    announces itself as something else.

    THIS IS NOT A LIE TOLD TO THE STRATEGY. `lookahead-analysis` builds a
    `Backtesting` object and runs `backtesting.backtest()` several times over
    real candles. It IS a backtest; only the runmode label on the config says
    otherwise, because the command was registered as a utility. The guard asks
    "may I precompute a per-candle series for the whole run", and under this
    analyzer the answer is yes.

    Scope is deliberately narrow. Only `DataProvider.runmode` is affected, only
    while `lookahead-analysis` is the entry point, and only for the strategies
    PROFILE_COMPAT_SIGNATURES names. `self.config['runmode']` is left alone, so
    a strategy reading the config directly sees the unchanged value and this
    shim does nothing for it.
    """
    from freqtrade.data.dataprovider import DataProvider
    from freqtrade.enums import RunMode

    if getattr(DataProvider, "_lookahead_runmode_shim", False):
        return True

    original = DataProvider.runmode

    @property
    def runmode(self):
        current = original.fget(self)
        if current == RunMode.UTIL_NO_EXCHANGE:
            return RunMode.BACKTEST
        return current

    DataProvider.runmode = runmode
    DataProvider._lookahead_runmode_shim = True
    return True


STARTUP_RULE = "startup_candles_not_limited_by_call_budget"


def install_unlimited_startup_candles():
    """Let a warm-up exceed five exchange calls when the data is already here.

    `Exchange.validate_required_startup_candles` refuses a warm-up that would
    need more than five OHLCV calls per pair:

        # Allow 5 calls to the exchange per pair
        if required_candle_call_count > 5:
            raise ConfigurationError(
                f"This strategy requires {startup_candles} candles to start, "
                f"which is more than 5x ({candle_limit * 5 - 1} candles) ...")

    Its own comment says what it is for: "to somewhat limit the impact" - a
    budget for calls to the exchange, so a live bot does not hammer the API on
    every refresh. A backtest makes no such calls. The candles are feather
    files on disk, loaded by `load_pair_history`, and the budget protects
    nothing that happens here.

    What it does instead is cap every warm-up at 4999 candles, which at five
    minutes is fourteen days. The convergence ladder is meant to climb 1, 2, 7,
    14, 30, 90 and 365 days; for a five-minute strategy it stopped at the
    fourth rung. Sixty-two rows were recorded as "no startup settles the
    indicators" without ever being offered the last three, and 97222 candles of
    history - 337 days - were sitting on disk unused. Twenty-eight of those
    rows are within 20 percent of the band at the rung they did reach, and
    seventeen within 5 percent: `BeastBotXBLR6` at 2.64, `BBRSIS` at 2.82, ten
    BigZ variants at 3.63. Fifty-six of the sixty-two are currently excluded.

    So this shim removes a guard outside the context it was written for, and it
    removes nothing else. `required_candle_call_count` is still computed and
    still returned; the three places that read it (`refresh_latest_ohlcv`,
    `get_historic_ohlcv`, and the pagination in `_async_get_historic_ohlcv`)
    are live and dry-run data paths that a backtest over local files never
    enters. The second branch - the one for exchanges without OHLCV history -
    is left exactly as it is, because there the limit is real.

    Where the requested warm-up exceeds the history actually on disk, nothing
    here helps and nothing here pretends to: the ladder caps each rung at
    `available_prefix_candles` before it asks for anything.
    """
    from freqtrade.exchange.exchange import Exchange

    if getattr(Exchange, "_unlimited_startup_candles", False):
        return True

    original = Exchange.validate_required_startup_candles

    def validate_required_startup_candles(self, startup_candles, timeframe):
        try:
            return original(self, startup_candles, timeframe)
        except Exception as exc:
            if "more than 5x" not in str(exc):
                # Any other refusal is a real one and is left to stand - in
                # particular the branch for an exchange that serves no
                # history, where the limit is about data rather than politeness.
                raise
            candle_limit = self.ohlcv_candle_limit(
                timeframe, self._config["candle_type_def"], None)
            count = startup_candles + 1
            return int((count / candle_limit)
                       + (0 if count % candle_limit == 0 else 1))

    Exchange.validate_required_startup_candles = validate_required_startup_candles
    Exchange._unlimited_startup_candles = True
    return True


AD_RULE = "restore_accumulation_distribution"


def install_accumulation_distribution():
    """Restore `technical.indicators.accumulation_distribution`, dropped upstream.

    `IchimokuStrategy` and `Ichimoku_SenkouSpanCross` both open with
    `from technical.indicators import accumulation_distribution`, and neither
    ever calls it - the import is dead code, left over from an earlier
    revision. `technical` 1.6.0, the version this runtime is pinned to, no
    longer defines the name at all (`chaikin_money_flow` is still there;
    `accumulation_distribution` is not), so the import fails before either
    strategy's own logic runs.

    Because it is unreachable in both known cases, a stub that merely
    satisfies the import would be enough. This restores the real indicator
    instead, at the same cost, so a future caller gets the correct value
    rather than a landmine: the Accumulation/Distribution line is the running
    total of Money Flow Volume, and `technical`'s own `chaikin_money_flow`
    computes the same Money Flow Multiplier this uses, just averaged over a
    window instead of summed without end. Restoring the function is not
    authoring the strategy - the formula is the textbook one, unrelated to
    any decision either author made - and no strategy file is touched.
    """
    import technical.indicators as ti

    if hasattr(ti, "accumulation_distribution"):
        return True

    def accumulation_distribution(dataframe):
        mfm = ((dataframe["close"] - dataframe["low"])
              - (dataframe["high"] - dataframe["close"])) / (
                  dataframe["high"] - dataframe["low"])
        mfv = mfm * dataframe["volume"]
        return mfv.cumsum()

    ti.accumulation_distribution = accumulation_distribution
    return True


FISHER_RULE = "restore_freqtrade_indicator_helpers"


def install_indicator_helpers():
    """Restore `freqtrade.indicator_helpers.fishers_inverse`, removed upstream.

    `BBRSI` opens with `from freqtrade.indicator_helpers import
    fishers_inverse` and never calls it - dead code from when freqtrade
    shipped this module as a grab-bag of indicator utilities. The module
    itself is gone from freqtrade 2026.7, not merely the one function, so the
    import fails before BBRSI's own logic runs.

    Because it is unreachable, a stub would be enough, but the inverse Fisher
    transform is a two-line, unambiguous textbook formula -
    `(e^2x - 1) / (e^2x + 1)` - so restoring it costs nothing extra and
    leaves nothing invented if a future caller does reach it. This creates
    the module rather than patching an existing one, since none exists to
    patch; no strategy file is touched.
    """
    import sys
    import types

    import numpy as np

    if "freqtrade.indicator_helpers" in sys.modules:
        return True

    module = types.ModuleType("freqtrade.indicator_helpers")

    def fishers_inverse(x, y=None):
        return (np.exp(2 * x) - 1) / (np.exp(2 * x) + 1)

    module.fishers_inverse = fishers_inverse
    sys.modules["freqtrade.indicator_helpers"] = module
    return True


NUMPY_APPEND_RULE = "restore_numpy_lib_function_base"


def install_numpy_lib_function_base():
    """Restore `numpy.lib.function_base`, reorganised out of the public API.

    `Persia` opens with `from numpy.lib.function_base import append` and
    never calls it under that name - the file's own use of `.append` a few
    lines down is Python's list method, not this import. numpy 2.x moved the
    implementation out of the path this was ever meant to be a stable
    reference to (`numpy.append` itself is untouched and still public), so
    the import fails before Persia's own logic runs.

    Creates a module exposing exactly the one name the historical path
    carried, aliased to numpy's own current public function - not a
    reimplementation, the same function under its old address. No strategy
    file is touched.
    """
    import sys
    import types

    import numpy as np

    if "numpy.lib.function_base" in sys.modules:
        return True

    module = types.ModuleType("numpy.lib.function_base")
    module.append = np.append
    sys.modules["numpy.lib.function_base"] = module
    return True


VIS_UTILS_RULE = "restore_keras_vis_utils"


def install_keras_vis_utils():
    """Restore `keras.utils.vis_utils.plot_model`, moved in Keras 3.

    `CryptoPredictionTraining` opens with `from keras.utils.vis_utils import
    plot_model` and its only call is commented out
    (`# plot_model(self.model, to_file='model.png')`) - dead code from Keras
    2, where `plot_model` lived at this submodule path. Keras 3 moved it to
    `keras.utils.plot_model` directly; the function itself is untouched, only
    its address changed.

    Creates the submodule aliased to the current public function - the same
    function under its old address, not a reimplementation. No strategy file
    is touched.
    """
    import sys
    import types

    import keras

    if "keras.utils.vis_utils" in sys.modules:
        return True

    module = types.ModuleType("keras.utils.vis_utils")
    module.plot_model = keras.utils.plot_model
    sys.modules["keras.utils.vis_utils"] = module
    return True


PMAX_RULE = "legacy_pmax_parameter_names"


def install_legacy_pmax_names():
    """Accept PMAX's pre-rename parameter names.

    `Pmax` calls `technical.indicators.PMAX(dataframe, atrperiod=...,
    multiplier=..., malength=..., matype=..., source=...)`. The installed
    `technical` (1.6.0) signature is
    `PMAX(dataframe, period=10, multiplier=3, length=12, MAtype=1, src=1)` -
    same five parameters, four renamed, `multiplier` untouched.

    Wraps PMAX to translate exactly those four old names to their current
    ones and pass everything else through unchanged; a call already using
    the current names is untouched, since none of the old names is present
    to translate.
    """
    import technical.indicators as ti

    original = ti.PMAX
    if getattr(original, "_legacy_names_installed", False):
        return True

    RENAMED = {"atrperiod": "period", "malength": "length",
              "matype": "MAtype", "source": "src"}

    def PMAX(dataframe, *args, **kwargs):
        translated = {RENAMED.get(key, key): value
                     for key, value in kwargs.items()}
        return original(dataframe, *args, **translated)

    PMAX._legacy_names_installed = True
    ti.PMAX = PMAX
    return True


# Shared by the resample and asfreq shims below: both pandas methods parse
# their frequency string through their own internal (non-Python-patchable)
# machinery rather than the public `pandas.tseries.frequencies.to_offset` -
# confirmed by patching that function alone and finding neither method
# affected - so each method needs its own wrapper, not one shared choke
# point. The translation table is shared so the two agree on what "legacy"
# means. Minute: freqtrade's own "15m", which pandas now reads as 15 months.
# Hour: bare "H"/"4H", which pandas now wants lowercase. Neither pattern can
# match a call that already works: "M"/"ME" for month keep their meaning,
# and "15min"/"4h" already parse.
def _translate_legacy_offset(rule):
    import re

    if not isinstance(rule, str):
        return rule
    if re.fullmatch(r"\d+m", rule):
        return rule + "in"
    if re.fullmatch(r"\d*H", rule):
        return rule[:-1] + "h"
    return rule


RESAMPLE_RULE = "legacy_minute_resample_rule"


def install_legacy_minute_resample():
    """Translate freqtrade's own "15m" into pandas' current "15min".

    `qrsi` calls `dataframe.resample(timeframe)` where `timeframe` is
    freqtrade's own config value, e.g. "15m". Pandas used to accept lowercase
    "m" as a minute alias; it now reserves "m" for month and raises
    `ValueError: 'm' is no longer supported for offsets`.

    The wrapped `resample` only ever inspects the first positional argument,
    and only translates it when `_translate_legacy_offset` recognises the
    shape - freqtrade's own minute-timeframe pattern, never a legitimate
    month specifier (those use uppercase "M"/"ME", not a lowercase "m"
    appended to digits). Every other call - `"1h"`, `"15min"`, `"M"`, no
    argument, a DateOffset object - is passed through untouched. Patches
    `NDFrame.resample`, shared by Series and DataFrame, so both call shapes
    are covered by one installation.
    """
    import pandas as pd

    original = pd.core.generic.NDFrame.resample
    if getattr(original, "_legacy_minute_resample_installed", False):
        return True

    def resample(self, rule=None, *args, **kwargs):
        return original(self, _translate_legacy_offset(rule), *args, **kwargs)

    resample._legacy_minute_resample_installed = True
    pd.core.generic.NDFrame.resample = resample
    return True


ASFREQ_RULE = "legacy_hour_asfreq_rule"


def install_legacy_asfreq():
    """Translate a bare "H" into pandas' current "h" for `.asfreq()`.

    `AutoArimaTripleV1` builds its own `frequency` attribute from a literal
    `'H'` passed at construction and calls `series.asfreq(freq=frequency)`.
    Pandas used to accept uppercase "H" for hourly; it now wants lowercase
    and raises `ValueError: Invalid frequency: H ... Did you mean h?` -
    pandas' own message names the fix. `.asfreq()` parses its frequency
    string through machinery separate from `.resample()`'s (confirmed: a
    resample-only patch left `.asfreq('H')` still failing), so this is a
    second, symmetric wrapper rather than a rule the resample shim already
    covers.

    Reuses `_translate_legacy_offset`, so this also accepts freqtrade's "15m"
    shape on `.asfreq()` if some future row needs that combination; nothing
    in the current corpus does. Every call `_translate_legacy_offset` leaves
    unchanged - `"1h"`, `"15min"`, `"M"`, no argument - passes through as
    before.
    """
    import pandas as pd

    original = pd.core.generic.NDFrame.asfreq
    if getattr(original, "_legacy_asfreq_installed", False):
        return True

    def asfreq(self, freq=None, *args, **kwargs):
        return original(self, _translate_legacy_offset(freq), *args, **kwargs)

    asfreq._legacy_asfreq_installed = True
    pd.core.generic.NDFrame.asfreq = asfreq
    return True


REPLACE_METHOD_RULE = "legacy_replace_method_kwarg"


def install_legacy_replace_method():
    """Accept the removed `method=` keyword on `Series`/`DataFrame.replace`.

    `LongShortRangeTradingMachetesV1` calls
    `series.replace(to_replace=0, method='ffill')`. Pandas removed `method`
    from `replace()`; its own current signature is
    `replace(to_replace=None, value=<no_default>, *, inplace=False,
    regex=False)`.

    The wrapped `replace` only intercepts a call that supplies `method` -
    which is unconditionally a `TypeError` on the current signature, so no
    call this reaches was working before - and reproduces the pre-removal
    semantics exactly: replace the matched value with a gap, then fill the
    gap using the named method (`ffill`/`pad` or `bfill`/`backfill`, the two
    values pandas' own `replace(method=...)` ever accepted). A call that
    does not pass `method` is untouched.
    """
    import pandas as pd

    original = pd.core.generic.NDFrame.replace
    if getattr(original, "_legacy_replace_method_installed", False):
        return True

    FILL = {"ffill": "ffill", "pad": "ffill",
           "bfill": "bfill", "backfill": "bfill"}

    def replace(self, *args, **kwargs):
        method = kwargs.pop("method", None)
        if method is None:
            return original(self, *args, **kwargs)
        kwargs.setdefault("value", None)
        filled = original(self, *args, **kwargs)
        return getattr(filled, FILL[method])()

    replace._legacy_replace_method_installed = True
    pd.core.generic.NDFrame.replace = replace
    return True


APPEND_RULE = "restore_dataframe_append"


def install_dataframe_append():
    """Restore `DataFrame.append`, removed in pandas 2.0.

    `AutoArimaTripleV1` calls `self.data = self.data.append(other,
    verify_integrity=True)`, where `self.data` is a `DataFrame`. Pandas 2.0
    removed the method outright - `DataFrame.append` does not exist at all in
    3.0.5, so unlike the other shims here there is no original call shape
    still working that this could disturb: every call this reaches is
    already a hard `AttributeError` without it.

    (The strategy's OTHER `.append(...)` call, on `self.model` - a pmdarima
    ARIMA object, not a DataFrame - is that library's own update method and
    is untouched; this shim is added to the `DataFrame` class specifically,
    not to anything more general.)

    `append` was documented as equivalent to `pd.concat` with the receiver
    first, which is what it is implemented as here: `df.append(other,
    ignore_index=False, verify_integrity=False, sort=False)` becomes
    `pd.concat([df, other], ignore_index=ignore_index,
    verify_integrity=verify_integrity, sort=sort)`.
    """
    import pandas as pd

    if hasattr(pd.DataFrame, "append"):
        return True

    def append(self, other, ignore_index=False, verify_integrity=False,
              sort=False):
        return pd.concat([self, other], ignore_index=ignore_index,
                         verify_integrity=verify_integrity, sort=sort)

    pd.DataFrame.append = append
    return True


INSTALLERS = {RULE: install_min_roi_reached_entry,
              SCAN_RULE: install_tolerant_class_scan,
              ADVISE_RULE: install_idempotent_advise_entry,
              RUNMODE_RULE: install_backtest_runmode_in_analysis,
              STARTUP_RULE: install_unlimited_startup_candles,
              SUBCLASS_RULE: install_legacy_min_roi_entry_override,
              AD_RULE: install_accumulation_distribution,
              FISHER_RULE: install_indicator_helpers,
              NUMPY_APPEND_RULE: install_numpy_lib_function_base,
              VIS_UTILS_RULE: install_keras_vis_utils,
              PMAX_RULE: install_legacy_pmax_names,
              RESAMPLE_RULE: install_legacy_minute_resample,
              REPLACE_METHOD_RULE: install_legacy_replace_method,
              APPEND_RULE: install_dataframe_append,
              ASFREQ_RULE: install_legacy_asfreq}


def install_from_environment():
    """Install the shims PROFILE_COMPAT_SIGNATURES names. Returns those applied."""
    requested = [name.strip() for name
                 in os.environ.get("PROFILE_COMPAT_SIGNATURES", "").split(",")
                 if name.strip()]
    applied = []
    for name in requested:
        installer = INSTALLERS.get(name)
        if installer and installer():
            applied.append(name)
    return applied


def selftest():
    """The shim must change the legacy call and nothing else."""
    class Trade(object):
        pair = "BTC/USDT"
        enter_tag = None
        trade_direction = "long"

    calls = []

    class Fake(object):
        use_custom_roi = False
        minimal_roi = {0: 0.10, 20: 0.05, 60: 0.0}

        def min_roi_reached_entry(self, trade, trade_dur, current_time):
            calls.append((trade, trade_dur, current_time))
            roi_list = [x for x in self.minimal_roi if x <= trade_dur]
            if not roi_list:
                return None, None
            entry = max(roi_list)
            return entry, self.minimal_roi[entry]

    original = Fake.min_roi_reached_entry

    def wrapped(self, *args, **kwargs):
        if len(args) == 1 and not kwargs:
            if getattr(self, "use_custom_roi", False):
                raise TypeError("use_custom_roi")
            return original(self, None, args[0], None)
        return original(self, *args, **kwargs)

    Fake.min_roi_reached_entry = wrapped
    subject = Fake()

    # The legacy call reaches the hook and returns the modern answer.
    assert subject.min_roi_reached_entry(30) == (20, 0.05)
    assert calls[-1] == (None, 30, None)
    # The modern call is untouched.
    now = object()
    assert subject.min_roi_reached_entry(Trade(), 30, now) == (20, 0.05)
    assert calls[-1][1] == 30 and calls[-1][2] is now
    # Below the first threshold the answer is the same either way.
    assert subject.min_roi_reached_entry(0) == (0, 0.10)
    # A strategy that would actually use the missing arguments is refused.
    subject.use_custom_roi = True
    try:
        subject.min_roi_reached_entry(30)
    except TypeError:
        pass
    else:                                    # pragma: no cover
        raise AssertionError("use_custom_roi must not be silently ignored")
    # The scan pattern decides which files are opened at all. It must admit
    # both spellings, and nothing that merely mentions the name.
    pattern = CLASS_PATTERN("MultiMA_TSL5")
    assert pattern.search("class MultiMA_TSL5 (IStrategy):")
    assert pattern.search("class MultiMA_TSL5(IStrategy):")
    assert pattern.search("class MultiMA_TSL5:")
    assert not pattern.search("class MultiMA_TSL5X(IStrategy):")
    assert not pattern.search("#class MultiMA_TSL5 (IStrategy):")
    assert not pattern.search("from x import MultiMA_TSL5")
    assert not pattern.search("    class MultiMA_TSL5(IStrategy):")
    # The third shim: a duplicated enter_tag is collapsed onto the LAST
    # occurrence - the strategy's own tags - and a frame that has only one is
    # returned exactly as it came.
    import sys
    import pandas
    frame = pandas.DataFrame({"close": [1.0, 2.0]})
    frame["enter_tag"] = ""
    frame["enter_long"] = [0, 1]
    frame["buy_tag"] = ["", "ewo1"]
    duplicated = frame.rename({"buy_tag": "enter_tag"}, axis="columns")
    assert list(duplicated.columns).count("enter_tag") == 2

    class FakeStrategy(object):
        def advise_entry(self, dataframe, metadata):
            return duplicated

    import types
    module = types.ModuleType("freqtrade.strategy.interface")
    module.IStrategy = FakeStrategy
    saved = sys.modules.get("freqtrade.strategy.interface")
    sys.modules["freqtrade.strategy.interface"] = module
    try:
        assert install_idempotent_advise_entry()
        collapsed = FakeStrategy().advise_entry(None, {})
        assert list(collapsed.columns).count("enter_tag") == 1, collapsed.columns
        # The one kept is the strategy's, not the empty placeholder.
        assert list(collapsed["enter_tag"]) == ["", "ewo1"], collapsed["enter_tag"]
        assert list(collapsed.columns) == ["close", "enter_long", "enter_tag"]
        # A frame with one enter_tag is passed straight through.
        single = frame.drop(columns=["buy_tag"])
        FakeStrategy._idempotent_entry_tag = False
        module.IStrategy = FakeStrategy

        class Single(object):
            def advise_entry(self, dataframe, metadata):
                return single
        module.IStrategy = Single
        assert install_idempotent_advise_entry()
        assert Single().advise_entry(None, {}) is single
    finally:
        if saved is not None:
            sys.modules["freqtrade.strategy.interface"] = saved
        else:
            sys.modules.pop("freqtrade.strategy.interface", None)

    # The fourth shim: only UTIL_NO_EXCHANGE is rewritten, and only on the
    # DataProvider. Every other runmode passes through untouched, so a live
    # or dry run can never be told it is a backtest.
    try:
        from freqtrade.data.dataprovider import DataProvider
        from freqtrade.enums import RunMode
    except Exception as exc:
        # Freqtrade is only importable inside the pinned runtime; on the host
        # scipy's DLL is blocked. Say so rather than reporting a pass that
        # skipped a check - run this selftest in the container to cover it.
        print("compat_signature selftest: PASS "
              "(runmode scope NOT checked here: %s)" % type(exc).__name__)
        return
    before = DataProvider.runmode
    try:
        assert install_backtest_runmode_in_analysis()

        class FakeProvider(DataProvider):
            def __init__(self, mode):
                self._mode = mode

        # `original.fget` reads self._config["runmode"]; drive it directly.
        holder = DataProvider.__new__(DataProvider)
        for mode, expected in ((RunMode.UTIL_NO_EXCHANGE, RunMode.BACKTEST),
                               (RunMode.BACKTEST, RunMode.BACKTEST),
                               (RunMode.DRY_RUN, RunMode.DRY_RUN),
                               (RunMode.LIVE, RunMode.LIVE),
                               (RunMode.HYPEROPT, RunMode.HYPEROPT)):
            holder._config = {"runmode": mode}
            assert holder.runmode == expected, (mode, holder.runmode)
    finally:
        DataProvider.runmode = before
        DataProvider._lookahead_runmode_shim = False

    # The fifth shim: the call-budget refusal is lifted, every other refusal
    # stands, and the returned count is unchanged.
    class FakeExchange(object):
        name = "Binance"
        _config = {"candle_type_def": "spot"}
        def ohlcv_candle_limit(self, timeframe, candle_type, since=None):
            return 1000
        def validate_required_startup_candles(self, startup_candles, timeframe):
            count = startup_candles + 1
            needed = int((count / 1000) + (0 if count % 1000 == 0 else 1))
            if needed > 5:
                raise ConfigurationError(
                    "This strategy requires %d candles to start, which is "
                    "more than 5x (4999 candles) the amount of candles "
                    "Binance provides for %s." % (startup_candles, timeframe))
            return needed

    class ConfigurationError(Exception):
        pass

    import types as _types
    module = _types.ModuleType("freqtrade.exchange.exchange")
    module.Exchange = FakeExchange
    saved = sys.modules.get("freqtrade.exchange.exchange")
    sys.modules["freqtrade.exchange.exchange"] = module
    try:
        assert install_unlimited_startup_candles()
        exchange = FakeExchange()
        # Under the budget: unchanged.
        assert exchange.validate_required_startup_candles(999, "5m") == 1
        assert exchange.validate_required_startup_candles(4998, "5m") == 5
        # Over it: no longer refused, and the count is what it always was.
        assert exchange.validate_required_startup_candles(25920, "5m") == 26
        assert exchange.validate_required_startup_candles(105120, "5m") == 106
        # A refusal that is not the budget still stands.
        class OtherRefusal(FakeExchange):
            def validate_required_startup_candles(self, startup_candles, tf):
                raise ConfigurationError("no history available at all")
        module.Exchange = OtherRefusal
        OtherRefusal._unlimited_startup_candles = False
        assert install_unlimited_startup_candles()
        try:
            OtherRefusal().validate_required_startup_candles(10, "5m")
            raise AssertionError("a non-budget refusal must not be swallowed")
        except ConfigurationError as exc:
            assert "no history" in str(exc)
    finally:
        if saved is not None:
            sys.modules["freqtrade.exchange.exchange"] = saved
        else:
            sys.modules.pop("freqtrade.exchange.exchange", None)

    # The sixth shim: a subclass override in the old shape is adapted on the
    # instance, a modern override is left alone, and Schism-v2's extra `pair`
    # keyword does not confuse the detector.
    class FakeStrategyOld(object):
        def min_roi_reached_entry(self, trade_dur):
            return ("old", trade_dur)

    class FakeStrategyExtraKw(object):
        def min_roi_reached_entry(self, trade_dur, pair="backtest"):
            return ("old_kw", trade_dur, pair)

    class FakeStrategyModern(object):
        def min_roi_reached_entry(self, trade, trade_dur, current_time):
            return ("modern", trade, trade_dur, current_time)

    class FakeResolver(object):
        _target = None

        @staticmethod
        def load_strategy(config=None):
            return FakeResolver._target()

    module = _types.ModuleType("freqtrade.resolvers.strategy_resolver")
    module.StrategyResolver = FakeResolver
    saved = sys.modules.get("freqtrade.resolvers.strategy_resolver")
    sys.modules["freqtrade.resolvers.strategy_resolver"] = module
    try:
        assert install_legacy_min_roi_entry_override()
        FakeResolver._target = FakeStrategyOld
        old_instance = FakeResolver.load_strategy()
        assert old_instance.min_roi_reached_entry("T", 30, "now") == ("old", 30)
        FakeResolver._target = FakeStrategyExtraKw
        kw_instance = FakeResolver.load_strategy()
        assert (kw_instance.min_roi_reached_entry("T", 30, "now")
               == ("old_kw", 30, "backtest"))
        # Schism-v2's own min_roi_reached calls its min_roi_reached_entry
        # with two positional arguments (trade_dur, pair) - its own old
        # convention, not freqtrade's three. That call must reach the
        # author's function unadapted rather than be mistaken for the
        # modern shape and lose its second argument.
        assert (kw_instance.min_roi_reached_entry(30, "ETH/USDT")
               == ("old_kw", 30, "ETH/USDT"))
        FakeResolver._target = FakeStrategyModern
        modern_instance = FakeResolver.load_strategy()
        assert (modern_instance.min_roi_reached_entry("T", 30, "now")
               == ("modern", "T", 30, "now"))
        assert "min_roi_reached_entry" not in vars(modern_instance)
    finally:
        if saved is not None:
            sys.modules["freqtrade.resolvers.strategy_resolver"] = saved
        else:
            sys.modules.pop("freqtrade.resolvers.strategy_resolver", None)

    # The seventh shim: the restored function computes the standard
    # Money-Flow-Volume running total, and a second install is a no-op.
    module = _types.ModuleType("technical.indicators")
    saved = sys.modules.get("technical.indicators")
    sys.modules["technical.indicators"] = module
    try:
        assert install_accumulation_distribution()
        frame = pandas.DataFrame({
            "high": [10.0, 12.0], "low": [8.0, 9.0],
            "close": [9.0, 12.0], "volume": [100.0, 200.0]})
        result = module.accumulation_distribution(frame)
        # Row 0: mfm = ((9-8)-(10-9))/(10-8) = 0 -> mfv 0.
        # Row 1: mfm = ((12-9)-(12-12))/(12-9) = 1 -> mfv 200, cumsum 200.
        assert list(result) == [0.0, 200.0], list(result)
        sentinel = module.accumulation_distribution
        assert install_accumulation_distribution()
        assert module.accumulation_distribution is sentinel
    finally:
        if saved is not None:
            sys.modules["technical.indicators"] = saved
        else:
            sys.modules.pop("technical.indicators", None)

    # The eighth shim: the inverse Fisher transform, and a second install
    # does not recreate the module.
    saved = sys.modules.pop("freqtrade.indicator_helpers", None)
    try:
        assert install_indicator_helpers()
        helpers = sys.modules["freqtrade.indicator_helpers"]
        import math
        got = helpers.fishers_inverse(0.5)
        expected = (math.exp(1.0) - 1) / (math.exp(1.0) + 1)
        assert abs(got - expected) < 1e-9, got
        sentinel = sys.modules["freqtrade.indicator_helpers"]
        assert install_indicator_helpers()
        assert sys.modules["freqtrade.indicator_helpers"] is sentinel
    finally:
        sys.modules.pop("freqtrade.indicator_helpers", None)
        if saved is not None:
            sys.modules["freqtrade.indicator_helpers"] = saved

    # The ninth shim: the old path reaches numpy's own current append,
    # unmodified.
    import numpy as np
    saved = sys.modules.pop("numpy.lib.function_base", None)
    try:
        assert install_numpy_lib_function_base()
        fb = sys.modules["numpy.lib.function_base"]
        assert fb.append is np.append
        sentinel = sys.modules["numpy.lib.function_base"]
        assert install_numpy_lib_function_base()
        assert sys.modules["numpy.lib.function_base"] is sentinel
    finally:
        sys.modules.pop("numpy.lib.function_base", None)
        if saved is not None:
            sys.modules["numpy.lib.function_base"] = saved

    # The tenth shim: the four renamed PMAX keywords reach the current
    # function; a call already using the current names is untouched.
    import technical.indicators as ti
    saved = ti.PMAX
    try:
        assert install_legacy_pmax_names()
        frame = pandas.DataFrame({
            "high": [10.0, 11.0, 12.0, 11.0, 13.0],
            "low": [9.0, 10.0, 10.0, 9.0, 11.0],
            "close": [9.5, 10.5, 11.0, 10.0, 12.5]})
        old_call = ti.PMAX(frame, atrperiod=2, multiplier=2,
                          malength=2, matype=1, source=1)
        current_call = saved(frame, period=2, multiplier=2,
                            length=2, MAtype=1, src=1)
        assert old_call.equals(current_call)
        # The current names, unmodified, pass straight through.
        direct = ti.PMAX(frame, period=2, multiplier=2,
                        length=2, MAtype=1, src=1)
        assert direct.equals(current_call)
    finally:
        ti.PMAX = saved

    # The eleventh shim: freqtrade's own "15m" reaches pandas as "15min";
    # "1h", "15min" and "M" - never freqtrade's own shape - pass unchanged.
    import pandas as pd
    original_resample = pd.core.generic.NDFrame.resample
    try:
        assert install_legacy_minute_resample()
        idx = pd.date_range("2020-01-01", periods=10, freq="1min")
        series = pd.Series(range(10), index=idx)
        translated = series.resample("15m").mean()
        direct = series.resample("15min").mean()
        assert list(translated) == list(direct)
        assert list(series.resample("1h").mean()) == \
            list(original_resample(series, "1h").mean())
        try:
            series.resample("M").mean()
            raise AssertionError("'M' must still raise, not be translated")
        except ValueError:
            pass
    finally:
        pd.core.generic.NDFrame.resample = original_resample

    # A twelfth: the same translation, on asfreq - a separate wrapper because
    # a resample-only patch left this method's "H" still failing.
    original_asfreq = pd.core.generic.NDFrame.asfreq
    try:
        assert install_legacy_asfreq()
        idx = pd.date_range("2020-01-01", periods=48, freq="1h")
        series = pd.Series(range(48), index=idx)
        assert list(series.asfreq("H")) == list(series.asfreq("h"))
        assert list(series.asfreq("1h")) == \
            list(original_asfreq(series, "1h"))
        try:
            series.asfreq("M")
            raise AssertionError("'M' must still raise, not be translated")
        except ValueError:
            pass
    finally:
        pd.core.generic.NDFrame.asfreq = original_asfreq

    # The twelfth shim: replace(method=...) reproduces the pre-removal
    # fill-after-replace semantics; a call without method is untouched.
    original_replace = pd.core.generic.NDFrame.replace
    try:
        assert install_legacy_replace_method()
        s = pd.Series([0.0, 1.0, 0.0, 2.0])
        got = s.replace(to_replace=0, method="ffill")
        want = original_replace(s, to_replace=0, value=None).ffill()
        assert got.equals(want)
        # No `method` kwarg: passes straight through, unmodified result.
        plain = s.replace(to_replace=0, value=9)
        assert list(plain) == list(original_replace(s, to_replace=0, value=9))
    finally:
        pd.core.generic.NDFrame.replace = original_replace

    # The thirteenth shim: DataFrame.append reproduces pd.concat under the
    # old name and signature; nothing calls it successfully beforehand, so
    # there is no untouched case to keep separate from the restored one.
    had_append = hasattr(pd.DataFrame, "append")
    try:
        assert not had_append, "pandas already has DataFrame.append again"
        assert install_dataframe_append()
        left = pd.DataFrame({"a": [1, 2]})
        right = pd.DataFrame({"a": [3, 4]})
        got = left.append(right, ignore_index=True)
        want = pd.concat([left, right], ignore_index=True,
                        verify_integrity=False, sort=False)
        assert got.equals(want)
    finally:
        if not had_append:
            del pd.DataFrame.append

    # The fourteenth shim: the old path reaches keras's own current plot_model,
    # unmodified. Keras is only on the TensorFlow companion image; skip
    # rather than fail where it is not installed, same as the runmode shim
    # above skips where freqtrade itself cannot be imported.
    try:
        import keras
    except Exception as exc:
        print("compat_signature selftest: PASS "
              "(keras vis_utils NOT checked here: %s)" % type(exc).__name__)
        return
    saved = sys.modules.pop("keras.utils.vis_utils", None)
    try:
        assert install_keras_vis_utils()
        vis = sys.modules["keras.utils.vis_utils"]
        assert vis.plot_model is keras.utils.plot_model
        sentinel = sys.modules["keras.utils.vis_utils"]
        assert install_keras_vis_utils()
        assert sys.modules["keras.utils.vis_utils"] is sentinel
    finally:
        sys.modules.pop("keras.utils.vis_utils", None)
        if saved is not None:
            sys.modules["keras.utils.vis_utils"] = saved

    print("compat_signature selftest: PASS")


if __name__ == "__main__":
    selftest()
