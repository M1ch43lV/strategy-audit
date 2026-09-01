# -*- coding: utf-8 -*-
"""Compatibility shims for framework changes the strategies predate.

Two of them so far: a hook whose signature gained parameters, and a file scan
that assumes a formatting convention. Neither is a defect in a strategy, and
neither shim touches a strategy file - they are installed into freqtrade in the
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


INSTALLERS = {RULE: install_min_roi_reached_entry,
              SCAN_RULE: install_tolerant_class_scan}


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
    print("compat_signature selftest: PASS")


if __name__ == "__main__":
    selftest()
