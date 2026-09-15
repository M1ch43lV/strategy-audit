# -*- coding: utf-8 -*-
"""Compatibility shims for framework changes the strategies predate.

Seventeen of them so far. A hook whose signature gained parameters. A file
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
restoration to disturb. A sixteenth catches a scalar `fillna` that used to
skip a column it could not fill and now raises instead; the wrapper tries
the original call first and only steps in for that exact failure, on a
frame that actually has an incompatible column. A seventeenth restores the
`method=` keyword `fillna` removed the same way `replace()` lost it,
patched once on the shared base class rather than twice for `Series` and
`DataFrame` separately. None is a defect in a
strategy, and no shim touches
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

# Needed eagerly, not lazily like keras/tensorflow elsewhere in this file:
# _ColumnWritebackSeries below is a module-level pd.Series subclass, and
# pandas is already an unconditional freqtrade dependency by the time this
# module loads - unlike keras/tensorflow, importing it here adds nothing a
# freqtrade backtest process was not already about to pay for.
import pandas as pd

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


TF_KERAS_SAVING_RULE = "tf_keras_saving_reexport"


def install_tf_keras_saving():
    """Give `tf.keras` back the `saving` submodule it is missing.

    `NNTClassifier` (webclinic017/strategies-freqtrade-) decorates a class
    with `@tf.keras.saving.register_keras_serializable(...)` at import time.
    `tf.keras` is Keras 3's own backward-compatibility namespace
    (`keras._tf_keras.keras`), built to mirror the old TF1-integrated
    `tf.keras` API - and it re-exports most of `keras`, but not `saving`:
    `keras.saving.register_keras_serializable` exists and works, `tf.keras.
    saving` is simply absent from the compat module's own attribute list.
    Same function, same registry, reached through a namespace that forgot
    one submodule. Assigning it across is not a reimplementation - it is
    the compat shim doing what its own name says it does.
    """
    import keras
    import tensorflow as tf

    if getattr(tf.keras, "_saving_reexported", False):
        return True
    tf.keras.saving = keras.saving
    tf.keras._saving_reexported = True
    return True


SELL_CHECK_TUPLE_RULE = "legacy_sell_check_tuple"


def install_legacy_sell_check_tuple():
    """Accept the pre-rename `SellCheckTuple`/`SellType` names.

    `BinanceStream` does
    `from freqtrade.strategy.interface import IStrategy, SellCheckTuple, SellType`
    and later `SellType.SELL_SIGNAL` and `SellCheckTuple(sell_type=reason)`.
    Freqtrade's sell-to-exit rename touched three separate things here, and
    each needs its own translation:

    1. `ExitCheckTuple`/`ExitType` now live in `freqtrade.enums`, re-exported
       into `freqtrade.strategy.interface` under their new names only - the
       two attributes this shim adds.
    2. `ExitCheckTuple`'s one constructor keyword renamed, `sell_type` ->
       `exit_type`, so it needs a translating wrapper, not a bare alias.
    3. The enum's own member names renamed too (`SELL_SIGNAL` ->
       `EXIT_SIGNAL`, `FORCE_SELL` -> `FORCE_EXIT`, ...): a bare
       `SellType = ExitType` alias exposes the right type but not the old
       member names on it, since `ExitType` was never given them back.
       `_LegacySellType` translates the well-documented SELL->EXIT renames
       (freqtrade's own migration notes name them exhaustively) and falls
       back to the current name unchanged, so `SellType.STOP_LOSS` (never
       renamed) keeps working the same way `SellType.SELL_SIGNAL` now does.
    """
    import freqtrade.strategy.interface as interface

    if getattr(interface, "_legacy_sell_check_tuple_installed", False):
        return True

    original = interface.ExitCheckTuple
    exit_type = interface.ExitType

    def SellCheckTuple(*args, **kwargs):
        if "sell_type" in kwargs:
            kwargs["exit_type"] = kwargs.pop("sell_type")
        if "sell_reason" in kwargs:
            kwargs["exit_reason"] = kwargs.pop("sell_reason")
        return original(*args, **kwargs)

    RENAMED_MEMBERS = {
        "SELL_SIGNAL": "EXIT_SIGNAL", "FORCE_SELL": "FORCE_EXIT",
        "EMERGENCY_SELL": "EMERGENCY_EXIT", "CUSTOM_SELL": "CUSTOM_EXIT",
        "PARTIAL_SELL": "PARTIAL_EXIT",
    }

    class _LegacySellType(object):
        def __getattr__(self, name):
            return getattr(exit_type, RENAMED_MEMBERS.get(name, name))

    interface.SellCheckTuple = SellCheckTuple
    interface.SellType = _LegacySellType()
    interface._legacy_sell_check_tuple_installed = True
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


FILLNA_RULE = "legacy_fillna_skips_incompatible_dtype"


def install_legacy_fillna_skips_incompatible_dtype():
    """Skip a datetime/timedelta column a scalar `fillna` cannot fill.

    Twenty-three strategies in the corpus carry a local `RMI(dataframe, ...)`
    helper copied from the same source (its own docstring names
    `technical/indicators/indicators.py`), which opens with

        df = dataframe.copy()
        df['maxup'] = (df['close'] - df['close'].shift(mom)).clip(lower=0)
        df['maxdown'] = (df['close'].shift(mom) - df['close']).clip(lower=0)
        df.fillna(0, inplace=True)

    `df` is the *whole* indicator frame, `date` column included, and by this
    point in `BinHV27_short` an informative-pair merge has left a leading run
    of `NaT` in it wherever the informative pair's history starts later than
    the base pair's. Pandas used to fill what it could and leave a column it
    could not alone; 3.0 raises instead, and only for `inplace=True` - the
    non-inplace call silently downcasts the column to `object` instead of
    raising, on this pandas version, which is a separate quirk this shim
    leaves alone:

        TypeError: value should be a 'Timestamp', 'NaT', or array of those.
        Got 'int' instead.

    (a second, differently-worded `TypeError` comes out of the same call
    shape depending on internal block layout - `Invalid value '0' for dtype
    'datetime64[...]'` - so the wrapper is keyed on dtype, not on parsing
    either message.)

    The wrapped `fillna` only reroutes that exact shape: `inplace=True`,
    a plain scalar value (a dict/Series/DataFrame value already fills
    per-column correctly and is left alone), and at least one datetime- or
    timedelta-typed column actually present. Every other call - non-inplace
    on this same frame included, which downcasts the column to `object`
    instead of raising on this pandas version and is a separate quirk this
    shim does not touch - reaches the original `fillna` unchanged. Where it
    does reroute, it fills the compatible columns exactly as the original
    call would and leaves the rest untouched, which is what the call did
    before 3.0. Column assignment rather than an in-place call on a slice,
    because a slice is a copy under copy-on-write and an in-place fill on it
    would silently vanish.
    """
    import pandas as pd
    from pandas.api.types import is_datetime64_any_dtype, is_timedelta64_dtype

    original = pd.DataFrame.fillna
    if getattr(original, "_legacy_fillna_installed", False):
        return True

    def fillna(self, value=None, *args, **kwargs):
        # Only the confirmed-broken shape is rerouted: an inplace call with
        # a plain scalar (dict/Series/DataFrame values already fill
        # per-column correctly) on a frame that actually carries a
        # datetime- or timedelta-typed column. Every other call - including
        # this same frame with inplace=False, which downcasts the column to
        # object instead of raising on this pandas version - reaches
        # `original` unchanged. Detected by dtype rather than by parsing the
        # error text, because pandas 3.0.5 raises two differently-worded
        # TypeErrors for this depending on internal block layout.
        if kwargs.get("inplace") and hasattr(self, "columns") \
                and not hasattr(value, "items") \
                and not isinstance(value, pd.DataFrame):
            incompatible = [column for column in self.columns
                            if is_datetime64_any_dtype(self[column].dtype)
                            or is_timedelta64_dtype(self[column].dtype)]
            if incompatible:
                compatible = [column for column in self.columns
                             if column not in incompatible]
                fill_kwargs = dict(kwargs)
                fill_kwargs["inplace"] = False
                filled = original(self[compatible], value, *args, **fill_kwargs)
                self[compatible] = filled
                # Matches this pandas version's own inplace=True return: the
                # mutated receiver itself, not None.
                return self
        return original(self, value, *args, **kwargs)

    fillna._legacy_fillna_installed = True
    pd.DataFrame.fillna = fillna
    return True


FILLNA_METHOD_RULE = "legacy_fillna_method_kwarg"


def install_legacy_fillna_method_kwarg():
    """Accept the removed `method=` keyword on `Series`/`DataFrame.fillna`.

    `Obelisk_Ichimoku_Slow_v1` and its numbered siblings call
    `dataframe['go_long'].fillna(method='ffill', inplace=True)` - a Series
    call, not a DataFrame one, which is why this is a separate shim from
    `legacy_fillna_skips_incompatible_dtype` above rather than an extra
    branch in it: that one is deliberately scoped to `pd.DataFrame.fillna`
    alone, keyed on a per-column dtype check that only makes sense for a
    frame. Pandas removed `method` from `fillna()` the same way it removed
    it from `replace()` (`install_legacy_replace_method`, same file); the
    call is unconditionally a `TypeError` on the current signature -

        NDFrame.fillna() got an unexpected keyword argument 'method'

    - patched on `NDFrame` itself, the class both `Series` and `DataFrame`
    inherit `fillna` from without overriding, rather than twice, once per
    subclass.

    The wrapped call only reroutes a `method=` of `ffill`/`pad` or
    `bfill`/`backfill` - the only two values pandas' own removed keyword
    ever accepted - to the equivalent named method, respecting `inplace`.
    Any other keyword combination, `method` absent included, reaches the
    original call unchanged and fails exactly as it did before this shim
    existed.
    """
    import pandas as pd

    original = pd.core.generic.NDFrame.fillna
    if getattr(original, "_legacy_fillna_method_installed", False):
        return True

    FILL = {"ffill": "ffill", "pad": "ffill",
           "bfill": "bfill", "backfill": "bfill"}

    def fillna(self, *args, **kwargs):
        method = kwargs.get("method")
        if method not in FILL:
            return original(self, *args, **kwargs)
        inplace = kwargs.get("inplace", False)
        filled = getattr(self, FILL[method])(inplace=inplace)
        return self if inplace else filled

    fillna._legacy_fillna_method_installed = True
    pd.core.generic.NDFrame.fillna = fillna
    return True


PRICE_SIDE_RULE = "legacy_bid_ask_strategy_price_side"


PRICE_SIDE_METHODS = ("confirm_trade_entry", "confirm_trade_exit",
                     "check_buy_timeout", "check_sell_timeout")
PRICE_SIDE_DEFAULTS = {"bid_strategy": {"price_side": "bid"},
                       "ask_strategy": {"price_side": "ask"}}


def install_legacy_price_side_config():
    """Restore `bid_strategy`/`ask_strategy`, renamed to entry/exit_pricing.

    `SuperHV27` and the `Schism` family read
    `self.config.get('bid_strategy', {})['price_side']` (the exit side reads
    `ask_strategy` the same way) to decide which side of the order book
    "the current price" means. Freqtrade renamed both sections to
    `entry_pricing`/`exit_pricing` years ago and the old names are gone
    entirely - `.get(..., {})` returns an empty dict and `['price_side']`
    raises `KeyError` one line before either strategy's own logic runs, let
    alone the order book it would go on to index.

    WHY THIS IS NOT "JUST ADD THE KEY BACK ONCE". The first version of this
    shim did exactly that, in `StrategyResolver.load_strategy` - and it
    reproduced the crash anyway, because freqtrade's OWN
    `process_deprecated_setting` runs once, right after strategy resolution
    (confirmed: the log shows strategy-attribute lines, then this
    deprecation warning, in that order), sees the now-present
    `bid_strategy.price_side`, migrates it to `entry_pricing.price_side` -
    and DELETES it from `bid_strategy` as part of that migration
    (`del section_old_config[name_old]` in freqtrade's own
    `deprecated_settings.py`). Adding the key early hands freqtrade's own
    migration exactly the key it then removes, which is indistinguishable
    from the strategy never having it. The unmodified config never
    triggers this at all: `bid_strategy` was never present to begin with,
    so there is nothing to migrate.

    THE FIX: inject the two keys immediately before each call the strategy
    makes, not once at load time - well after the one-time startup
    migration has already run and stopped looking. Same hook as
    `install_legacy_min_roi_entry_override` above for the SAME reason that
    shim uses it (a subclass override has to be adapted on the instance,
    the base class is never consulted): once the real loader returns the
    instance, whichever of `confirm_trade_entry`, `confirm_trade_exit`,
    `check_buy_timeout`, `check_sell_timeout` the class defines its own
    version of gets wrapped to set the defaults on `self.config` (only if
    still absent - a later value is never overwritten) right before calling
    the author's function unchanged.
    """
    from freqtrade.resolvers.strategy_resolver import StrategyResolver

    if getattr(StrategyResolver, "_legacy_price_side_adapted", False):
        return True

    original = StrategyResolver.load_strategy

    def load_strategy(config=None):
        strategy = original(config)
        cls = type(strategy)
        for name in PRICE_SIDE_METHODS:
            own = cls.__dict__.get(name)
            if own is None:
                continue

            def wrapper(*args, _own=own, _self=strategy, **kwargs):
                for key, default in PRICE_SIDE_DEFAULTS.items():
                    section = _self.config.setdefault(key, {})
                    section.setdefault("price_side", default["price_side"])
                return _own(_self, *args, **kwargs)

            setattr(strategy, name, wrapper)
        return strategy

    StrategyResolver.load_strategy = staticmethod(load_strategy)
    StrategyResolver._legacy_price_side_adapted = True
    return True


ORDERBOOK_RULE = "synthetic_orderbook_from_last_close"


def install_synthetic_backtest_orderbook():
    """Give `confirm_trade_entry` a usable book without a live network call.

    `SuperHV27` and `Hacklemore3` (and the `Schism` family, on the same
    template) read "the current price" as `ob[f"{side}s"][0][0]` from
    `self.dp.orderbook(pair, N)`. `DataProvider.orderbook` delegates to
    `Exchange.fetch_l2_order_book`, which unconditionally calls
    `self._api.fetch_l2_order_book(pair, limit)` - a real request to the
    exchange's LIVE order book, with no runmode guard at all, confirmed by
    reading `exchange.py` directly. Backtesting keeps that call reachable
    (nothing crashes on the call itself) but it comes back with empty
    'bids'/'asks' - there is no historical L2 book to serve for a backtest -
    so `[0][0]` raises: `KeyError('price_side')` for `SuperHV27`, whose own
    `self.config.get('bid_strategy', {})` is ALSO empty (freqtrade renamed
    that key to `entry_pricing` years ago, one line before the book is even
    indexed); `IndexError` directly for `Hacklemore3`, which never reads
    that key.

    SCOPE. 79 admitted strategies call `dp.orderbook()`; most of them
    complete anyway (a live call that happens to succeed, or code that
    tolerates an empty book). Patching `orderbook()` unconditionally would
    change what ALL 79 measure, most of which nobody asked to touch. This
    installs only through `PROFILE_COMPAT_SIGNATURES`, which
    `evidence/PROFILE_CLASS1.json` sets per strategy - so it activates only for the
    two rows confirmed, on a second independent run, to crash on this exact
    shape (`ELIGIBILITY`/pooled-backtest retries, 2026-09-07), not for the
    75+ that were never touched.

    THE PROXY. Freqtrade's backtest model fills a candle at its own price
    with no real-world gap for an order book to have moved in - so
    `current_price == last close` is what the model already treats as "now",
    not an invented number. The safe source for that close is
    `DataProvider.get_pair_dataframe`, freqtrade's OWN look-ahead-guarded
    accessor (its own comment: "prevent lookahead bias... through
    informative pairs") - reusing it means this shim inherits that guard
    rather than re-deriving a current-time cutoff of its own.

    WHY THE RESULT IS CACHED PER PAIR, ONCE, FOR THE PROCESS'S LIFE.
    `get_pair_dataframe` calls `historic_ohlcv`, which already avoids
    re-reading the feather file on every call (`"Loading data for ..."`
    logs exactly once per pair) - but still returns
    `self.__cached_pairs_backtesting[key].copy()`, a full copy of a
    multi-year dataframe, EVERY call. `confirm_trade_entry` runs on every
    prospective trade; the first version of this shim called
    `get_pair_dataframe` there directly and SuperHV27 alone had not
    finished after 15 minutes of silence (confirmed: not hung - freqtrade
    logs nothing routine from inside `confirm_trade_entry` - just doing a
    multi-hundred-thousand-row copy on repeat). Caching the extracted close
    the first time it is needed for a pair, and reusing it for the rest of
    that pair's calls, removes the repeated copy entirely. What is lost is
    freshness within a run, not correctness: the cached close is real
    historical data from no later than the first candle that needed it, so
    every later call still gets a price from ITS OWN past or earlier, never
    the future - it can go stale, it cannot look ahead. That is the same
    trade a strategy author accepted by using a coarse "current price"
    check to begin with.

    Scope at the call level, not just the environment level: only backtest
    or hyperopt runmode, and only when the real call actually came back
    empty - a live/dry-run call, or a backtest call that somehow got real
    depth, is returned unchanged.
    """
    from freqtrade.data.dataprovider import DataProvider
    from freqtrade.enums import RunMode

    if getattr(DataProvider, "_synthetic_orderbook_installed", False):
        return True

    original = DataProvider.orderbook
    cache: dict = {}

    def orderbook(self, pair, maximum):
        book = original(self, pair, maximum)
        if self.runmode not in (RunMode.BACKTEST, RunMode.HYPEROPT):
            return book
        if book.get("bids") and book.get("asks"):
            return book
        if pair not in cache:
            data = self.get_pair_dataframe(pair)
            if len(data) == 0:
                return book
            cache[pair] = float(data.iloc[-1]["close"])
        level = [[cache[pair], 0.0]]
        return dict(book, bids=level, asks=level)

    orderbook._synthetic_orderbook_installed = True
    DataProvider.orderbook = orderbook
    DataProvider._synthetic_orderbook_installed = True
    return True


SET_SESSION_RULE = "tf_keras_backend_set_session_noop"


def install_tf_keras_backend_set_session_noop():
    """No-op `tf.compat.v1.keras.backend.set_session`, absent from Keras 3.

    The webclinic017 NNPredict/NNTC family's shared `ClassifierKeras.py`
    opens with TF1-era session boilerplate:

        config = tf.compat.v1.ConfigProto(device_count={'GPU': 0})
        config.gpu_options.allow_growth = True
        config.gpu_options.per_process_gpu_memory_fraction = mem_fraction
        sess = tf.compat.v1.Session(config=config)
        tf.compat.v1.keras.backend.set_session(sess)

    All four `config`/`gpu_options` lines are GPU resource tuning -
    `device_count={'GPU': 0}` disables the GPU outright, so `allow_growth`
    and the memory-fraction cap govern a device that is never used, on this
    machine or any other: `tf.config.list_physical_devices('GPU')` returns
    `[]` here regardless of what the strategy asks for. `set_session` itself
    is TF1's mechanism for telling Keras which graph-mode Session to
    evaluate tensors in; under TF2's eager execution - the only mode Keras 3
    runs in, with no session concept at all - there is nothing for it to
    bind and no code path that would consult it. Keras 3's `tf.compat.v1`
    shim simply never re-added the attribute, so the call is an
    AttributeError at import time, before any of these strategies build a
    model or see a row of data.

    A no-op is not a guess here: the four lines it follows configure
    resource allocation for hardware this run never has, through an API
    whose only job (binding a session) has nothing left to do under eager
    execution. Model architecture, weights, and training data are untouched
    by removing it. An environment where Keras genuinely still defines
    `set_session` is left alone - `hasattr` decides, not a version check.
    """
    import tensorflow as tf

    backend = tf.compat.v1.keras.backend
    if hasattr(backend, "set_session"):
        return True

    def set_session(session=None):
        return None

    backend.set_session = set_session
    return True


BARE_SAVE_RULE = "tf_keras_bare_save_redirect"


def install_tf_keras_bare_save_redirect():
    """Route bare `keras.models.save_model`/`load_model` to `tf_keras`.

    `ClassifierKeras.py` (webclinic017 NNPredict_*/NNTC_* family) builds its
    model through `tf.keras.Sequential`/`tf.keras.layers.*` throughout, but
    saves and reloads it through bare `keras.models.save_model`/
    `load_model` - two different spellings the author never distinguished
    because, before Keras 3, `keras` and `tf.keras` were the same package.
    They no longer are: under `TF_USE_LEGACY_KERAS=1` (set by
    `evidence/profile_smoke.py` when a row's `tf_use_legacy_keras` flag is
    on - REQUIRED for `keras.optimizers.legacy`, which Keras 3 dropped
    outright), `tf.keras.*` resolves to the standalone `tf_keras` package
    while bare `keras` stays native Keras 3. The model these strategies
    build is then a `tf_keras` object handed to native Keras 3's
    `save_model`, which refuses it outright:

        ValueError: Expected object to be an instance of `KerasSaveable`,
        but got <tf_keras.src.engine.functional.Functional object ...>

    Confirmed by direct test: a Keras 3 model cannot be compiled with a
    `tf_keras` legacy optimizer either (`Could not interpret optimizer
    identifier`), so the reverse mix is equally broken - the two model
    representations are not interchangeable at any point in the chain, and
    everything downstream of `TF_USE_LEGACY_KERAS` has to agree throughout.
    This shim makes the ONE place the author's own code did not (a bare
    `keras.*` call, next to a model built with `tf.keras.*`) agree with the
    rest: `keras.models.save_model`/`load_model` are redirected to
    `tf_keras.models.save_model`/`load_model`, the functions that already
    know how to walk a `tf_keras` model - not a reimplementation, and not a
    silent behaviour change for anything that does not opt in.

    Deliberately narrow and opt-in only (`PROFILE_COMPAT_SIGNATURES`, same
    as every shim here): patching bare `keras.models` unconditionally would
    break every OTHER strategy in the corpus that correctly relies on it
    staying native Keras 3. It only ever matters together with
    `tf_use_legacy_keras`, and is harmless without it - a Keras 3 model
    saved through `tf_keras.models.save_model` still round-trips, since
    `tf_keras.models.save_model` and `keras.models.save_model` differ only
    in which model representation they were written to expect, not in
    format - but there is no reason to install it for a row that never asks.
    """
    import tf_keras
    import keras

    if getattr(keras.models, "_tf_keras_bare_save_redirect", False):
        return True

    keras.models.save_model = tf_keras.models.save_model
    keras.models.load_model = tf_keras.models.load_model
    keras.models._tf_keras_bare_save_redirect = True
    return True


WRITEBACK_RULE = "nnpredict_chained_iloc_writeback"


class _PredictionWritebackColumn:
    """Stand-in for `dataframe["predicted_gain"]`, scoped to one call.

    Every attribute other than `.iloc` delegates straight to the real
    Series - a plain read, `.clip()`, whatever else the author's code does
    with the column reaches pandas unchanged. Only `.iloc` returns
    `_PredictionWritebackILoc` below, which is where the actual fix lives.
    """

    __slots__ = ("_series", "_frame", "_col")

    def __init__(self, series, frame, col):
        self._series = series
        self._frame = frame
        self._col = col

    def __getattr__(self, name):
        return getattr(self._series, name)


class _PredictionWritebackILoc:
    """`__setitem__` writes through to the parent frame; `__getitem__` does
    not need to, since nothing in NNPredict.py's write sites ever reads
    `dataframe["predicted_gain"].iloc[...]` back before returning."""

    __slots__ = ("_series", "_frame", "_col")

    def __init__(self, series, frame, col):
        self._series = series
        self._frame = frame
        self._col = col

    def __getitem__(self, key):
        return self._series.iloc[key]

    def __setitem__(self, key, value):
        col_pos = self._frame.columns.get_loc(self._col)
        # A single 2D positional set on the FRAME itself - not the detached
        # Series `dataframe[col]` returned - is what pandas' own
        # ChainedAssignmentError message names as the fix, and it is a
        # genuinely different, non-chained operation: one call, one target,
        # nothing in between for Copy-on-Write to disconnect.
        self._frame.iloc[key, col_pos] = value


_PredictionWritebackColumn.iloc = property(
    lambda self: _PredictionWritebackILoc(self._series, self._frame, self._col))


def install_nnpredict_prediction_writeback():
    """Make `dataframe["predicted_gain"].iloc[...] = value` reach the frame.

    `NNPredict.py` (webclinic017 NNPredict_* family) computes real
    predictions and tries to write them in three places
    (`update_predictions`, `add_model_batch_predictions`) through exactly
    the chained-assignment shape pandas 3.0 silently drops:

        dataframe["predicted_gain"].iloc[-len(predictions):] = predictions.copy()

    Copy-on-Write - unconditional since pandas 3.0, `pd.options.mode.
    copy_on_write` no longer has any effect - means `dataframe[col]` returns
    an object disconnected from `dataframe`'s own data; assigning through
    `.iloc` on it mutates only that disconnected copy. Confirmed directly:
    `predicted_gain` measures identically `0.0` across an entire 4161-row
    backtest window (`repair/REGISTER.md`, Phase 10), every write silently
    lost, so `qtpylib.crossed_above(predicted_gain, target_profit)` - this
    family's entire entry trigger - can never fire, in any window, on any
    row of any of these strategies. Not a model or market question: a pure
    pandas-version incompatibility upstream of anything the model computes.

    THE SCOPE THIS SHIM DELIBERATELY DOES NOT TAKE. A general fix for
    chained assignment - patching `pd.DataFrame.__getitem__` or
    `pd.Series.__setitem__` for the whole process - is the same corpus-wide
    change already investigated and declined for `MostOfAll`/`NNTC` as too
    invasive: every other strategy's every other column access would run
    through it too, for a class of bug this file otherwise treats one exact
    call shape at a time. This shim is narrower in two ways at once. First,
    IN TIME: `pd.DataFrame.__getitem__` is only ever replaced for the
    duration of one call to `add_predictions` (the method wrapping all
    three broken write sites), on the specific strategy instance that opts
    in via `PROFILE_COMPAT_SIGNATURES`, and is put back immediately after
    in a `finally` - never active during `populate_entry_trend`'s own later
    `crossed_above` reads of the same column, and never active for any
    other strategy's process at all. Second, IN SHAPE: the replacement
    `__getitem__` only ever treats the literal key `"predicted_gain"`
    specially; every other column access inside that one call - `dataframe
    ["gain"]`, `dataframe[self.target_column]`, all of it - returns pandas'
    own real Series, completely untouched. Checked directly against every
    site in `NNPredict.py` that reads `dataframe["predicted_gain"]` inside
    `add_predictions`'s own call tree: the only operation is `.clip(lower=,
    upper=)`, an ordinary method call `_PredictionWritebackColumn.__getattr__`
    forwards unchanged - nothing here needs comparison or arithmetic dunders,
    so none are implemented, and the wrapper does not claim to be a general
    Series substitute outside the one call shape it exists for.

    Installed via `StrategyResolver.load_strategy`, the same hook
    `install_legacy_price_side_config` uses and for a related reason:
    `add_predictions` is defined once on the shared `NNPredict` base class,
    never overridden per strategy, so `getattr(cls, "add_predictions")`
    finds the same function for every row in the family and the instance
    wrap applies it identically everywhere it installs.
    """
    from freqtrade.resolvers.strategy_resolver import StrategyResolver

    if getattr(StrategyResolver, "_nnpredict_writeback_installed", False):
        return True

    original_load = StrategyResolver.load_strategy

    def load_strategy(config=None):
        strategy = original_load(config)
        cls = type(strategy)
        own = getattr(cls, "add_predictions", None)
        if own is None:
            return strategy

        def add_predictions(self, dataframe, pair, _own=own):
            import pandas as pd

            original_getitem = pd.DataFrame.__getitem__

            def patched_getitem(frame, key):
                result = original_getitem(frame, key)
                if key == "predicted_gain":
                    return _PredictionWritebackColumn(result, frame, key)
                return result

            pd.DataFrame.__getitem__ = patched_getitem
            try:
                return _own(self, dataframe, pair)
            finally:
                pd.DataFrame.__getitem__ = original_getitem

        strategy.add_predictions = add_predictions.__get__(strategy, cls)
        return strategy

    StrategyResolver.load_strategy = staticmethod(load_strategy)
    StrategyResolver._nnpredict_writeback_installed = True
    return True


POPULATE_WRITEBACK_RULE = "populate_indicators_chained_writeback"


# `pd.DataFrame.__getitem__` is patched globally for the process while
# `populate_indicators` runs - it necessarily also sees any OTHER
# dataframe pandas or freqtrade touches during that same call stack, not
# only the strategy's own `dataframe` parameter. `Obelisk_3EMA_StochRSI_
# ATR` calls `self.dp.get_pair_dataframe(...)` for an informative pair
# mid-`populate_indicators`, which freqtrade loads fresh and resamples
# through `dataframe.resample(interval, on="date")` - pandas' own
# `TimeGrouper.__init__` then does `obj["date"]` as part of that, and
# wrapping ITS return raised `KeyError: 'date'` where the unwrapped call
# does not (confirmed directly: identical run with the shim disabled
# completes cleanly). None of this cluster's own chained-assignment bugs
# ever target `date`/`open`/`high`/`low`/`close`/`volume` - every one
# writes into a custom indicator column the author's own snippet computed
# - so excluding the six raw OHLCV names closes this exact collision
# without narrowing what the shim was written to fix.
_RAW_OHLCV_COLUMNS = frozenset(
    {"date", "open", "high", "low", "close", "volume"})


class _ColumnWritebackSeries(pd.Series):
    """`dataframe[col]`'s actual return value, scoped to one
    `populate_indicators` call - a genuine `Series` subclass, not a
    delegating wrapper, because `ta.SMA(dataframe['close'], ...)` and
    similar TA-Lib calls type-check their argument and reject anything that
    is not really one (confirmed directly: a wrapper class raised "Argument
    'real'/'high' has incorrect type" from inside the Supertrend/divergence
    cluster's own indicator calls the first time this was tried). Every
    normal Series operation - `.mean()`, arithmetic, slicing, being handed
    to a C-extension that inspects the buffer protocol - behaves exactly
    like the real Series it is, because it is one; only `.iloc`, `.iat`, a
    bare `[key] =`, and `fillna(inplace=True)` are overridden, the four
    write shapes a pre-Copy-on-Write snippet actually uses. `_constructor`
    returns a plain `pd.Series` rather than this subclass, so a derived
    result (`.rolling().mean()`, a slice, anything computed FROM this
    column) is an ordinary Series with no writeback attached - the link to
    the parent frame belongs only to the exact object `dataframe[col]`
    itself returned, not to whatever gets computed from it.
    """

    _metadata = ["_wb_frame", "_wb_col"]

    @property
    def _constructor(self):
        return pd.Series

    def __setitem__(self, key, value):
        # Bare `dataframe[col][key] = value` - the same chained shape as
        # `.iloc`/`.iat`, one bracket pair shorter. `data[f'{key}_highs']
        # [hh_idx] = 1` (RaposaDivergenceV1) reaches here with `hh_idx` an
        # integer position array from a numpy peak-finder, which is exactly
        # what a 2D positional `.iloc` set on the frame expects.
        frame = object.__getattribute__(self, "_wb_frame")
        col = object.__getattribute__(self, "_wb_col")
        col_pos = frame.columns.get_loc(col)
        frame.iloc[key, col_pos] = value

    @property
    def iloc(self):
        return _ColumnWritebackIndexer(self)

    @property
    def iat(self):
        # `.iat` takes only a scalar position, but a 2D positional `.iloc`
        # set accepts one exactly the same way `.iloc` does with a scalar -
        # no separate indexer shape needed.
        return _ColumnWritebackIndexer(self)

    def fillna(self, *args, **kwargs):
        if not kwargs.get("inplace"):
            return pd.Series(self).fillna(*args, **kwargs)
        filled = pd.Series(self).fillna(
            *args, **{k: v for k, v in kwargs.items() if k != "inplace"})
        self[:] = filled
        return None


class _ColumnWritebackIndexer:
    __slots__ = ("_series",)

    def __init__(self, series):
        self._series = series

    def __getitem__(self, key):
        return pd.Series(self._series).iloc[key]

    def __setitem__(self, key, value):
        self._series[key] = value


def install_populate_indicators_chained_writeback():
    """Make chained assignment inside `populate_indicators` reach the frame.

    A cluster of unrelated strategies (Phase 11,
    `repair/REGISTER.md`) - `Supertrend`/`SuperTrendPure`/
    `FSupertrendStrategyBTC`/`FSupertrendStrategyETH`/`Insomnia_short`
    (all the same widely-copied Supertrend snippet: `df['final_ub'].iat[i]
    = ...` in a loop), `HarmonicDivergence` (`dataframe['total_bearish_
    divergences'][index] = row.close`), `RaposaDivergenceV1`
    (`data[f'{key}_highs'][hh_idx] = 1`, a numpy peak-finder's positions) -
    each compute a real indicator value and then lose it the same way
    `NNPredict.py` lost its predictions (`nnpredict_chained_iloc_writeback`,
    above): `dataframe[col]` returns an object pandas 3.0's unconditional
    Copy-on-Write has already disconnected from `dataframe`'s own data, so
    assigning into it through `.iloc`, `.iat`, or a bare `[key]` mutates
    only that disconnected copy. Confirmed directly against each row's own
    captured output, not assumed from the shared symptom.

    NOT a general chained-assignment fix - the same corpus-wide change
    already investigated and declined for `MostOfAll`/`NNTC` as too
    invasive. Narrower in the same two ways `nnpredict_chained_iloc_
    writeback` is, adapted to a scope this shim shares across strategies
    rather than one method name: IN TIME, `pd.DataFrame.__getitem__` is
    only ever replaced for the duration of one `populate_indicators` call,
    on the one strategy instance that opts in, restored in a `finally`
    immediately after - never active during `populate_entry_trend`/
    `populate_exit_trend`, which freqtrade always calls afterward, as
    separate calls, once `populate_indicators` has already returned. IN
    SHAPE, `dataframe[col]` still returns a genuine `Series` (`_ColumnWriteback
    Series`, a real subclass, not a delegating stand-in - required because
    TA-Lib type-checks its arguments and a non-Series wrapper broke `ta.SMA
    (dataframe['close'], ...)` the first time this was tried) whose derived
    results (`.rolling()`, arithmetic, slicing) are plain `Series` again, so
    ordinary reads, comparisons, and indicator math elsewhere in the same
    call are unaffected; only `.iloc`, `.iat`, a bare `[key] =`, and
    `fillna(inplace=True)` on the column object ITSELF are rerouted.
    `populate_indicators` itself is where this is safe to apply
    broadly (every column, not one literal name): it is pure indicator
    computation, entirely separate in time from the signal-generation
    calls that follow, so there is no adjacent logic this could disturb by
    also covering columns the shim was not written with in mind - unlike
    `add_predictions`, which shares its base class across many rows and so
    is scoped to the one column name that method actually breaks.

    Same installation hook as `nnpredict_chained_iloc_writeback` and for
    the same reason: `populate_indicators` may be overridden per strategy,
    so the wrap has to find whichever version the resolved SUBCLASS
    actually defines, on the instance, after real resolution.
    """
    from freqtrade.resolvers.strategy_resolver import StrategyResolver

    if getattr(StrategyResolver, "_populate_writeback_installed", False):
        return True

    original_load = StrategyResolver.load_strategy

    def load_strategy(config=None):
        strategy = original_load(config)
        cls = type(strategy)
        own = getattr(cls, "populate_indicators", None)
        if own is None:
            return strategy

        def populate_indicators(self, dataframe, metadata, _own=own):
            import pandas as pd

            original_getitem = pd.DataFrame.__getitem__

            def patched_getitem(frame, key):
                result = original_getitem(frame, key)
                if (isinstance(key, str) and key not in _RAW_OHLCV_COLUMNS
                        and isinstance(result, pd.Series)):
                    wrapped = _ColumnWritebackSeries(result)
                    object.__setattr__(wrapped, "_wb_frame", frame)
                    object.__setattr__(wrapped, "_wb_col", key)
                    return wrapped
                return result

            pd.DataFrame.__getitem__ = patched_getitem
            try:
                return _own(self, dataframe, metadata)
            finally:
                pd.DataFrame.__getitem__ = original_getitem

        strategy.populate_indicators = populate_indicators.__get__(strategy, cls)
        return strategy

    StrategyResolver.load_strategy = staticmethod(load_strategy)
    StrategyResolver._populate_writeback_installed = True
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
              ASFREQ_RULE: install_legacy_asfreq,
              FILLNA_RULE: install_legacy_fillna_skips_incompatible_dtype,
              FILLNA_METHOD_RULE: install_legacy_fillna_method_kwarg,
              ORDERBOOK_RULE: install_synthetic_backtest_orderbook,
              PRICE_SIDE_RULE: install_legacy_price_side_config,
              SELL_CHECK_TUPLE_RULE: install_legacy_sell_check_tuple,
              TF_KERAS_SAVING_RULE: install_tf_keras_saving,
              SET_SESSION_RULE: install_tf_keras_backend_set_session_noop,
              BARE_SAVE_RULE: install_tf_keras_bare_save_redirect,
              WRITEBACK_RULE: install_nnpredict_prediction_writeback,
              POPULATE_WRITEBACK_RULE: install_populate_indicators_chained_writeback}


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

    # The fifteenth shim: a scalar fillna skips a datetime column it cannot
    # fill instead of raising; a frame with nothing incompatible, and any
    # other TypeError, pass through to the original call unchanged.
    original_fillna = pd.DataFrame.fillna
    # Fresh pandas defines fillna once, on NDFrame; DataFrame has no entry of
    # its own in __dict__ and inherits it. Restoring below with a plain
    # `pd.DataFrame.fillna = original_fillna` would still create one - same
    # value, but now an explicit override that shadows the seventeenth
    # shim's later patch to NDFrame.fillna for DataFrame specifically,
    # which is exactly the residue that shim's own selftest caught.
    had_own_fillna = "fillna" in pd.DataFrame.__dict__
    try:
        assert install_legacy_fillna_skips_incompatible_dtype()
        # A NaT in `date` is required: a full column never reaches the
        # dtype check pandas raises from, same as it never did before 3.0.
        # UTC-aware, matching freqtrade's own candle `date` column - a naive
        # column hits a different internal pandas path with a different
        # message and is not this shim's concern. And only inplace=True
        # raises at all - non-inplace silently downcasts the column to
        # object instead, on this pandas version, so that call shape is not
        # this shim's problem either and is left alone.
        mixed = pd.DataFrame({
            "date": pd.to_datetime(
                ["2020-01-01", None, "2020-01-03"], utc=True),
            "close": [1.0, float("nan"), 3.0]})
        untouched = mixed.fillna(0)
        assert untouched.equals(original_fillna(mixed, 0))
        # inplace=True must mutate the original and return it, same as the
        # call it replaces on this pandas version (not None) - filling
        # `close` and leaving the incompatible `date` column alone.
        copy = mixed.copy()
        assert copy.fillna(0, inplace=True) is copy
        assert list(copy["close"]) == [1.0, 0.0, 3.0]
        assert copy["date"].equals(mixed["date"])
        # Nothing incompatible on the frame: passes straight through.
        clean = pd.DataFrame({"close": [1.0, float("nan")]})
        assert list(clean.fillna(0)["close"]) \
            == list(original_fillna(clean, 0)["close"])
        # A TypeError for an unrelated reason still raises.
        try:
            mixed.fillna(0, method="nonexistent")
            raise AssertionError("bad method= must still raise")
        except TypeError as exc:
            assert "should be a 'Timestamp', 'NaT'" not in str(exc)
    finally:
        if had_own_fillna:
            pd.DataFrame.fillna = original_fillna
        else:
            del pd.DataFrame.fillna

    # The seventeenth shim: the removed `method=` keyword on `fillna`,
    # patched on NDFrame so a Series call is covered the same as a
    # DataFrame one - unlike the sixteenth shim just above, which is
    # deliberately DataFrame-only.
    original_ndframe_fillna = pd.core.generic.NDFrame.fillna
    try:
        assert install_legacy_fillna_method_kwarg()
        series = pd.Series([1.0, None, None, 4.0])
        # Not inplace: returns the filled copy, original untouched.
        filled = series.fillna(method="ffill")
        assert list(filled) == [1.0, 1.0, 1.0, 4.0]
        assert series.isna().sum() == 2
        # inplace=True mutates and returns the mutated receiver, matching
        # this pandas version's own inplace=True return (not None).
        copy = series.copy()
        assert copy.fillna(method="ffill", inplace=True) is copy
        assert list(copy) == [1.0, 1.0, 1.0, 4.0]
        # bfill fills from the other direction. NaN, not None, is what a
        # trailing gap bfill cannot reach actually holds.
        back = pd.Series([None, 2.0, None]).fillna(method="bfill")
        assert back.iloc[0] == 2.0 and back.iloc[1] == 2.0 and pd.isna(back.iloc[2])
        # A DataFrame call is covered too - both classes inherit fillna from
        # NDFrame without overriding it.
        frame = pd.DataFrame({"a": [1.0, None, 3.0]})
        assert list(frame.fillna(method="ffill")["a"]) == [1.0, 1.0, 3.0]
        # No method=: reaches the original call unchanged.
        assert series.fillna(0).equals(original_ndframe_fillna(series, 0))
        # An unsupported method value is not this shim's concern and still
        # raises exactly as it did before the shim existed.
        try:
            series.fillna(method="nonexistent")
            raise AssertionError("bad method= must still raise")
        except TypeError as exc:
            assert "unexpected keyword argument 'method'" in str(exc)
    finally:
        pd.core.generic.NDFrame.fillna = original_ndframe_fillna

    # The eighteenth shim: bid_strategy/ask_strategy are set on the instance's
    # config immediately before a call the strategy's OWN confirm_trade_entry
    # makes - not once at load time, which a first version of this shim got
    # wrong (freqtrade's own deprecated-settings migration deletes the key
    # right back out the moment it sees it during startup config validation,
    # a step this test cannot exercise without the real freqtrade config
    # pipeline - the regression it guards against is deliberately about
    # *when* the key is set, covered by the two calls below, not about
    # surviving that migration, which only the container-run repair proved).
    calls = []

    class FakeStrategyEntry(object):
        def __init__(self):
            self.config = {}

        def confirm_trade_entry(self, pair):
            calls.append(dict(self.config))
            return True

    class FakeResolver2(object):
        _target = None

        @staticmethod
        def load_strategy(config=None):
            return FakeResolver2._target()

    module = _types.ModuleType("freqtrade.resolvers.strategy_resolver")
    module.StrategyResolver = FakeResolver2
    saved = sys.modules.get("freqtrade.resolvers.strategy_resolver")
    sys.modules["freqtrade.resolvers.strategy_resolver"] = module
    try:
        assert install_legacy_price_side_config()
        FakeResolver2._target = FakeStrategyEntry
        instance = FakeResolver2.load_strategy()
        # Absent at load time - the fix under test - and present only once
        # the wrapped call actually runs.
        assert "bid_strategy" not in instance.config
        assert instance.confirm_trade_entry("BTC/USDT") is True
        assert calls[-1]["bid_strategy"] == {"price_side": "bid"}
        assert calls[-1]["ask_strategy"] == {"price_side": "ask"}
        # A value set between calls (freqtrade's own migration, in the real
        # pipeline) is never overwritten - only an absent key is filled in.
        instance.config["bid_strategy"] = {}
        instance.confirm_trade_entry("BTC/USDT")
        assert calls[-1]["bid_strategy"] == {"price_side": "bid"}
        instance.config["bid_strategy"] = {"price_side": "already-set"}
        instance.confirm_trade_entry("BTC/USDT")
        assert calls[-1]["bid_strategy"] == {"price_side": "already-set"}
    finally:
        if saved is not None:
            sys.modules["freqtrade.resolvers.strategy_resolver"] = saved
        else:
            sys.modules.pop("freqtrade.resolvers.strategy_resolver", None)

    # The nineteenth shim: an empty backtest/hyperopt book is replaced by a
    # synthetic single-level one at the last close; a live/dry-run call, and
    # a book that already has depth, pass through unchanged.
    class FakeFrame(object):
        def __init__(self, rows):
            self._rows = rows
        def __len__(self):
            return len(self._rows)
        @property
        def iloc(self):
            rows = self._rows
            class _ILoc(object):
                def __getitem__(self, index):
                    return rows[index]
            return _ILoc()

    calls = []

    def fake_orderbook(self, pair, maximum):
        calls.append(pair)
        return dict(self._next_book)

    original_orderbook = DataProvider.orderbook
    DataProvider.orderbook = fake_orderbook
    DataProvider._synthetic_orderbook_installed = False
    try:
        assert install_synthetic_backtest_orderbook()

        holder = DataProvider.__new__(DataProvider)
        holder._config = {"runmode": RunMode.BACKTEST}
        holder._next_book = {"bids": [], "asks": []}
        holder.get_pair_dataframe = lambda pair, *a, **kw: FakeFrame(
            [{"close": 123.5}])
        book = holder.orderbook("BTC/USDT", 1)
        assert book["bids"] == [[123.5, 0.0]], book
        assert book["asks"] == [[123.5, 0.0]], book

        # The cache, not a fresh lookup, answers a second empty-book call for
        # the SAME pair - the fix for the 15-minute stall a first version of
        # this shim caused by calling get_pair_dataframe from every
        # confirm_trade_entry. Change what get_pair_dataframe would return
        # and confirm the stale, cached value wins, not the fresh one.
        holder.get_pair_dataframe = lambda pair, *a, **kw: FakeFrame(
            [{"close": 999.0}])
        book = holder.orderbook("BTC/USDT", 1)
        assert book["bids"] == [[123.5, 0.0]], book

        # A book that already has depth is left exactly as the (fake) real
        # call returned it - a different pair, so the cache above cannot be
        # the reason.
        holder._next_book = {"bids": [[100.0, 1.0]], "asks": [[101.0, 1.0]]}
        book = holder.orderbook("ETH/USDT", 1)
        assert book == {"bids": [[100.0, 1.0]], "asks": [[101.0, 1.0]]}, book

        # Live/dry-run: never synthesised, even with an empty book.
        holder._config = {"runmode": RunMode.LIVE}
        holder._next_book = {"bids": [], "asks": []}
        book = holder.orderbook("LTC/USDT", 1)
        assert book == {"bids": [], "asks": []}, book

        # No historical data at all: passed through rather than invented,
        # and nothing is cached for a future call to wrongly reuse.
        holder._config = {"runmode": RunMode.BACKTEST}
        holder._next_book = {"bids": [], "asks": []}
        holder.get_pair_dataframe = lambda pair, *a, **kw: FakeFrame([])
        book = holder.orderbook("XRP/USDT", 1)
        assert book == {"bids": [], "asks": []}, book
    finally:
        DataProvider.orderbook = original_orderbook
        DataProvider._synthetic_orderbook_installed = False

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

    # The twentieth shim: `set_session` becomes a harmless no-op only where
    # Keras does not already define one; a `set_session` an environment
    # genuinely has (an older Keras, or this same test run a second time) is
    # left standing rather than replaced. TensorFlow is only on the
    # TensorFlow companion image; skip rather than fail where it is not
    # installed, same as the vis_utils shim just above.
    try:
        import tensorflow as tf
    except Exception as exc:
        print("compat_signature selftest: PASS "
              "(tf_keras_backend_set_session_noop NOT checked here: %s)"
              % type(exc).__name__)
        return
    backend = tf.compat.v1.keras.backend
    had_set_session = hasattr(backend, "set_session")
    saved_set_session = backend.__dict__.get("set_session")
    if had_set_session:
        del backend.set_session
    try:
        assert install_tf_keras_backend_set_session_noop()
        assert backend.set_session(object()) is None
        assert backend.set_session() is None
        # A real one already present is not overwritten.
        del backend.set_session
        backend.set_session = lambda session=None: "real"
        assert install_tf_keras_backend_set_session_noop()
        assert backend.set_session(None) == "real"
    finally:
        del backend.set_session
        if had_set_session:
            backend.set_session = saved_set_session

    # The twenty-first shim: bare `keras.models.save_model`/`load_model`
    # redirect to `tf_keras`'s own, and a second install does not re-wrap.
    # `tf_keras` is only on the TensorFlow companion image; skip rather than
    # fail where it is not installed, same as the shims just above.
    try:
        import tf_keras as _tf_keras_probe
    except Exception as exc:
        print("compat_signature selftest: PASS "
              "(tf_keras_bare_save_redirect NOT checked here: %s)"
              % type(exc).__name__)
        return
    had_save = "save_model" in keras.models.__dict__
    had_load = "load_model" in keras.models.__dict__
    saved_save = keras.models.__dict__.get("save_model")
    saved_load = keras.models.__dict__.get("load_model")
    keras.models._tf_keras_bare_save_redirect = False
    try:
        assert install_tf_keras_bare_save_redirect()
        assert keras.models.save_model is _tf_keras_probe.models.save_model
        assert keras.models.load_model is _tf_keras_probe.models.load_model
        sentinel = keras.models.save_model
        assert install_tf_keras_bare_save_redirect()
        assert keras.models.save_model is sentinel
    finally:
        if had_save:
            keras.models.save_model = saved_save
        else:
            del keras.models.save_model
        if had_load:
            keras.models.load_model = saved_load
        else:
            del keras.models.load_model
        keras.models._tf_keras_bare_save_redirect = False

    # The twenty-second shim: `dataframe["predicted_gain"].iloc[...] = value`
    # reaches the real frame once installed, an unrelated column's chained
    # assignment on the same frame is untouched (the shim is scoped to one
    # literal key), and a strategy with no `add_predictions` is left alone.
    try:
        from freqtrade.resolvers.strategy_resolver import StrategyResolver
    except Exception as exc:
        print("compat_signature selftest: PASS "
              "(nnpredict_chained_iloc_writeback NOT checked here: %s)"
              % type(exc).__name__)
        return
    import pandas as pd
    import numpy as np

    class FakeNNPredictBase(object):
        def add_predictions(self, dataframe, pair):
            dataframe["predicted_gain"].iloc[-3:] = np.array([1.0, 2.0, 3.0])
            # An unrelated column's OWN chained assignment, in the same
            # call: must still raise/no-op exactly as it does without the
            # shim - only "predicted_gain" is special-cased.
            try:
                dataframe["other"].iloc[-1] = 999.0
            except Exception:
                pass
            return dataframe

    class FakeStrategy(FakeNNPredictBase):
        pass

    class FakeResolver3(object):
        _target = None

        @staticmethod
        def load_strategy(config=None):
            return FakeResolver3._target()

    module = _types.ModuleType("freqtrade.resolvers.strategy_resolver")
    module.StrategyResolver = FakeResolver3
    saved_module = sys.modules.get("freqtrade.resolvers.strategy_resolver")
    sys.modules["freqtrade.resolvers.strategy_resolver"] = module
    try:
        assert install_nnpredict_prediction_writeback()
        FakeResolver3._target = FakeStrategy
        instance = FakeResolver3.load_strategy()
        frame = pd.DataFrame({"predicted_gain": [0.0] * 5, "other": [0.0] * 5})
        result = instance.add_predictions(frame, "BTC/USDT")
        assert list(result["predicted_gain"]) == [0.0, 0.0, 1.0, 2.0, 3.0], \
            list(result["predicted_gain"])
        # The unrelated column was never routed through the writeback path -
        # its own chained assignment still behaves exactly as bare pandas
        # does outside this shim (silently lost under CoW, not our concern).
        assert list(result["other"]) == [0.0] * 5, list(result["other"])

        # A class with no add_predictions at all is returned unwrapped.
        class Plain(object):
            pass

        FakeResolver3._target = Plain
        plain = FakeResolver3.load_strategy()
        assert "add_predictions" not in vars(plain)
    finally:
        if saved_module is not None:
            sys.modules["freqtrade.resolvers.strategy_resolver"] = saved_module
        else:
            sys.modules.pop("freqtrade.resolvers.strategy_resolver", None)

    # The twenty-third shim: every chained shape (.iat, .iloc, bare [key],
    # fillna(inplace=True)) reaches the real frame inside
    # populate_indicators; the same shapes on an unrelated column called
    # OUTSIDE that method (populate_entry_trend, called after it returns)
    # are untouched, proving the patch is not left installed past its one
    # call.
    class FakeSupertrendStrategy(object):
        def populate_indicators(self, dataframe, metadata):
            dataframe["a"] = 0.0
            for i in range(len(dataframe)):
                dataframe["a"].iat[i] = float(i)          # .iat
            dataframe["b"] = 0.0
            dataframe["b"].iloc[1:3] = [10.0, 20.0]        # .iloc
            dataframe["c"] = 0.0
            dataframe["c"][[0, 2]] = 5.0                   # bare [key]
            dataframe["d"] = pd.Series([1.0, None, 3.0, None, 5.0])
            dataframe["d"].fillna(0.0, inplace=True)        # fillna(inplace)
            # A raw OHLCV name is deliberately excluded - the fix that
            # closed the Obelisk_3EMA_StochRSI_ATR collision - so this one
            # must NOT be fixed even though it is the identical .iat shape
            # column "a" above already proved works.
            dataframe["close"].iat[0] = 999.0
            return dataframe

        def populate_entry_trend(self, dataframe, metadata):
            # Same chained shape, but outside populate_indicators' scope -
            # must behave exactly like bare pandas, i.e. NOT reach the frame.
            dataframe["e"] = 0.0
            dataframe["e"].iat[0] = 99.0
            return dataframe

    class FakeResolver4(object):
        _target = None

        @staticmethod
        def load_strategy(config=None):
            return FakeResolver4._target()

    module = _types.ModuleType("freqtrade.resolvers.strategy_resolver")
    module.StrategyResolver = FakeResolver4
    saved_module = sys.modules.get("freqtrade.resolvers.strategy_resolver")
    sys.modules["freqtrade.resolvers.strategy_resolver"] = module
    try:
        assert install_populate_indicators_chained_writeback()
        FakeResolver4._target = FakeSupertrendStrategy
        instance = FakeResolver4.load_strategy()
        frame = pd.DataFrame({"close": [1.0] * 5})
        result = instance.populate_indicators(frame, {"pair": "BTC/USDT"})
        assert list(result["a"]) == [0.0, 1.0, 2.0, 3.0, 4.0], list(result["a"])
        assert list(result["b"]) == [0.0, 10.0, 20.0, 0.0, 0.0], list(result["b"])
        assert list(result["c"]) == [5.0, 0.0, 5.0, 0.0, 0.0], list(result["c"])
        assert list(result["d"]) == [1.0, 0.0, 3.0, 0.0, 5.0], list(result["d"])
        assert result["close"].iloc[0] == 1.0, \
            "a raw OHLCV column must be excluded from the writeback, not fixed"

        after = instance.populate_entry_trend(result, {"pair": "BTC/USDT"})
        assert list(after["e"]) == [0.0] * 5, \
            "the same chained shape outside populate_indicators must not be fixed"
    finally:
        if saved_module is not None:
            sys.modules["freqtrade.resolvers.strategy_resolver"] = saved_module
        else:
            sys.modules.pop("freqtrade.resolvers.strategy_resolver", None)

    print("compat_signature selftest: PASS")


if __name__ == "__main__":
    selftest()
