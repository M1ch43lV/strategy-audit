# -*- coding: utf-8 -*-
"""check_rolling_any - is `.rolling(n).sum() > 0` a safe stand-in for the
removed `.rolling(n).any()`?

The patcher refuses this substitution. This script shows why, on the actual
expression from A9AV:

    (~dataframe['sell_signal'].rolling(window=2).any())

pandas removed `Rolling.any`, so the original behaviour cannot be observed here
any more - which is itself part of the problem: an equivalence that cannot be
tested cannot be claimed. What CAN be shown is how the candidate replacements
behave in the warm-up region, where the window is incomplete, and what the
leading `~` does to each of them.
"""
import pandas as pd
import numpy as np

s = pd.Series([0, 0, 1, 0, 0, 0, 1, 1, 0, 0], name="sell_signal")
n = 2

print("source column (as the strategy builds it: integer 0/1)")
print(list(s))
print()

variants = {
    "rolling(n).sum() > 0": lambda: s.rolling(n).sum() > 0,
    "rolling(n).max() > 0": lambda: s.rolling(n).max() > 0,
    "rolling(n).max().astype(bool)": lambda: s.rolling(n).max().astype(bool),
    "rolling(n, min_periods=1).sum() > 0": lambda: s.rolling(n, min_periods=1).sum() > 0,
}

for label, fn in variants.items():
    try:
        v = fn()
        head = list(v)[:4]
        try:
            inv = list((~v))[:4]
            invnote = str(inv)
        except Exception as e:
            invnote = "~ FAILS: %s" % type(e).__name__
        print("%-38s dtype=%-8s first4=%-28s ~first4=%s"
              % (label, v.dtype, str(head), invnote))
    except Exception as e:
        print("%-38s raises %s" % (label, type(e).__name__))

print()
print("The disagreement is confined to the first n-1 rows, where the window is")
print("incomplete. `sum() > 0` silently treats NaN as False, so the negated")
print("condition is TRUE there and an entry may fire; a variant that keeps NaN")
print("makes it False and no entry fires. Which of the two matches the removed")
print("`Rolling.any` cannot be checked, because the method no longer exists.")
print()
print("n-1 rows out of ~200,000 is a rounding error in aggregate - but it lands")
print("exactly on the warm-up boundary, and this strategy's whole condition is")
print("'no opposing signal in the last n candles'. Being wrong there flips entry")
print("signals rather than shifting a number. Unproven equivalence, so: no patch.")
