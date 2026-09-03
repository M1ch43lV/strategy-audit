# -*- coding: utf-8 -*-
"""Compatibility shims for framework changes the strategies predate.

Five of them so far. A hook whose signature gained parameters. A file scan
that assumes a formatting convention. A column the framework duplicates when
its own analyzer calls a hook twice. An analyzer that announces itself as a
utility while running a backtest. And a budget for calls to the exchange,
enforced on a backtest that makes none. None is a defect in a strategy, and no
shim touches a strategy file - they are installed into freqtrade in the
runner process, only when PROFILE_COMPAT_SIGNATURES names them.

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


INSTALLERS = {RULE: install_min_roi_reached_entry,
              SCAN_RULE: install_tolerant_class_scan,
              ADVISE_RULE: install_idempotent_advise_entry,
              RUNMODE_RULE: install_backtest_runmode_in_analysis,
              STARTUP_RULE: install_unlimited_startup_candles}


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

    print("compat_signature selftest: PASS")


if __name__ == "__main__":
    selftest()
