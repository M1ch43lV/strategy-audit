# -*- coding: utf-8 -*-
"""scan_base_classes - how many corpus entries are base classes, not strategies?

`harness.find_strategies()` collects every class that inherits `IStrategy`. That
is the right structural test - a name-based one would be worse - but it also
picks up abstract bases that exist only to be subclassed. `ClucCrypROI` is one:
it defines neither `stoploss` nor `minimal_roi`, and the runnable strategies are
`ClucCrypROI_ETH` and `ClucCrypROI_BTC`, which inherit from it and supply both.

freqtrade then rejects the base with `'stoploss' is a required property`, and the
card reads "could not be measured" - which is true, and misleading, because the
thing was never a strategy.

This cannot be repaired by configuration. Supplying a stoploss through the config
would make us measure a class the author never meant to run, and the value would
be ours. It is reported instead.

A class is counted here when, in the same file, another class inherits FROM it
and it lacks a stoploss of its own.
"""
import ast
import csv
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT


def base_names(node):
    out = []
    for b in node.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        else:
            out.append(getattr(b, "attr", ""))
    return out


def assigned(node):
    out = set()
    for x in node.body:
        if isinstance(x, ast.Assign):
            for t in x.targets:
                if isinstance(t, ast.Name):
                    out.add(t.id)
        elif isinstance(x, ast.AnnAssign) and isinstance(x.target, ast.Name):
            out.add(x.target.id)
    return out


def main():
    ledger = sys.argv[1] if len(sys.argv) > 1 else os.path.join(AUD, "LEDGER.csv")
    rows = list(csv.DictReader(io.open(ledger, encoding="utf-8")))
    hits = []
    for r in rows:
        p = os.path.join(AUD, r["file"])
        if not os.path.exists(p):
            continue
        try:
            tree = ast.parse(io.open(p, encoding="utf-8", errors="replace").read())
        except SyntaxError:
            continue
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        by_name = {c.name: c for c in classes}
        target = by_name.get(r["strategy"])
        if target is None:
            continue
        subclassed = any(r["strategy"] in base_names(c)
                         for c in classes if c.name != r["strategy"])
        if not subclassed:
            continue
        own = assigned(target)
        if "stoploss" in own:
            continue
        children = [c.name for c in classes if r["strategy"] in base_names(c)]
        hits.append((r["strategy"], r["dropped_at"], children))

    print("corpus entries that look like abstract bases: %d" % len(hits))
    print("(subclassed inside their own file, and carrying no stoploss themselves)")
    print()
    print("  %-30s %-16s %s" % ("counted as a strategy", "audit verdict", "actual strategies"))
    for name, drop, kids in sorted(hits):
        print("  %-30s %-16s %s" % (name[:30], drop or "survivor", ", ".join(kids[:3])))


if __name__ == "__main__":
    main()
