# -*- coding: utf-8 -*-
"""Compatibility shims for framework changes the strategies predate.

Three of them so far: a hook whose signature gained parameters, a file scan
that assumes a formatting convention, and a column the framework duplicates
when its own analyzer calls a hook twice. None is a defect in a strategy, and
no shim touches a strategy file - they are installed into freqtrade in the
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


INSTALLERS = {RULE: install_min_roi_reached_entry,
              SCAN_RULE: install_tolerant_class_scan,
              ADVISE_RULE: install_idempotent_advise_entry}


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

    print("compat_signature selftest: PASS")


if __name__ == "__main__":
    selftest()
