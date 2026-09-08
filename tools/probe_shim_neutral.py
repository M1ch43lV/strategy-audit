# -*- coding: utf-8 -*-
"""Does the enter_tag shim change what an ordinary backtest produces?

The shim exists so `lookahead-analysis` can call the signal hooks twice. But
it also sits in the ordinary single-pass path, where the duplicate column is
harmless and freqtrade has always tolerated it. A repair that quietly changed
the trade list would be worse than the problem it solves.

So: run the same strategy over the same window twice - once as freqtrade
ships, once with the shim installed - and compare the entry signals and the
tags they carry, row for row. Anything but an exact match means the shim is
not neutral and must not be used.
"""
from __future__ import print_function

import json
import os
import sys

sys.path.insert(0, "/audit")
os.environ.setdefault("AUDIT_ROOT", "/audit")

from freqtrade.configuration import Configuration
from freqtrade.data.history import load_pair_history
from freqtrade.enums import CandleType
from freqtrade.resolvers import StrategyResolver

sys.path.insert(0, "/audit/repair")
import compat_signature


def signals(name, path, shimmed):
    config = Configuration.from_files(["/audit/user_data/config.json"])
    config["strategy"] = name
    config["strategy_path"] = os.path.dirname(os.path.join("/audit", path))
    strategy = StrategyResolver.load_strategy(config)
    frame = load_pair_history(pair="BTC/USDT", timeframe=strategy.timeframe,
                              datadir=config["datadir"],
                              candle_type=CandleType.SPOT)
    frame = frame.iloc[-6000:].reset_index(drop=True)
    meta = {"pair": "BTC/USDT"}
    out = strategy.ft_advise_signals(strategy.advise_indicators(frame, meta), meta)
    # With the duplicate present, out["enter_tag"] is a frame, not a series.
    # Take the last occurrence either way - that is the one freqtrade's
    # single-pass path effectively uses, and the one the shim keeps.
    columns = list(out.columns)
    last = len(columns) - 1 - columns[::-1].index("enter_tag")
    tags = out.iloc[:, last]
    return {
        "duplicate_columns": columns.count("enter_tag"),
        "entries": [int(v) for v in out["enter_long"].fillna(0).astype(int)],
        "tags": ["" if v is None or v != v else str(v) for v in tags],
    }


def main():
    targets = json.loads(sys.argv[1])
    results = []
    for name, path in targets.items():
        entry = {"strategy": name}
        try:
            # The shim patches IStrategy class-wide, so it has to be taken
            # off again between strategies. Without this only the first row
            # of the run is a real comparison and every later "plain" pass is
            # already shimmed - which is how the first version of this probe
            # reported duplicate_before as 1 for four strategies that have 2.
            from freqtrade.strategy.interface import IStrategy
            untouched = IStrategy.advise_entry
            had_flag = getattr(IStrategy, "_idempotent_entry_tag", False)
            IStrategy._idempotent_entry_tag = False
            plain = signals(name, path, False)
            assert compat_signature.install_idempotent_advise_entry()
            shim = signals(name, path, True)
            IStrategy.advise_entry = untouched
            IStrategy._idempotent_entry_tag = had_flag
            entry["duplicate_before"] = plain["duplicate_columns"]
            entry["duplicate_after"] = shim["duplicate_columns"]
            entry["entries_identical"] = plain["entries"] == shim["entries"]
            entry["tags_identical"] = plain["tags"] == shim["tags"]
            entry["entry_count"] = sum(plain["entries"])
            if not entry["entries_identical"]:
                differ = [i for i, (a, b) in
                          enumerate(zip(plain["entries"], shim["entries"]))
                          if a != b]
                entry["entries_differ_at"] = differ[:10]
            if not entry["tags_identical"]:
                differ = [(i, a, b) for i, (a, b) in
                          enumerate(zip(plain["tags"], shim["tags"])) if a != b]
                entry["tags_differ_at"] = differ[:10]
        except Exception as exc:
            entry["error"] = "%s: %s" % (type(exc).__name__, exc)
        results.append(entry)
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
