# -*- coding: utf-8 -*-
"""Does calling ft_advise_signals twice duplicate a column?

`lookahead-analysis` calls the strategy's signal hooks twice on the same
dataframe: once in `prepare_data`, then again inside `backtest` via
`_get_ohlcv_as_lists`. The ordinary backtest calls them once.

`advise_entry` initialises `enter_tag` to "" before calling the strategy, and
then, for an interface-v2 strategy that wrote `buy`/`buy_tag`, renames
`buy_tag` to `enter_tag`. Renaming does not merge: after one pass the frame
would hold TWO columns called `enter_tag`. A second pass then has to align
against a columns axis with duplicate labels, which is what pandas refuses.

If that is what happens, the error belongs to freqtrade's analyzer and to the
v2 interface, not to the fourteen strategies it is reported against - all of
which run and trade in an ordinary backtest.

This prints what the columns actually do. It asserts nothing; the point is to
look.
"""
from __future__ import print_function

import collections
import json
import os
import sys

sys.path.insert(0, "/audit")
os.environ.setdefault("AUDIT_ROOT", "/audit")

from freqtrade.configuration import Configuration
from freqtrade.data.history import load_pair_history
from freqtrade.enums import CandleType
from freqtrade.resolvers import StrategyResolver


def dupes(frame):
    counts = collections.Counter(frame.columns)
    return {name: n for name, n in counts.items() if n > 1}


def probe(name, path):
    out = {"strategy": name}
    config = Configuration.from_files(["/audit/user_data/config.json"])
    config["strategy"] = name
    config["strategy_path"] = os.path.dirname(os.path.join("/audit", path))
    strategy = StrategyResolver.load_strategy(config)
    out["interface_version"] = getattr(strategy, "INTERFACE_VERSION", None)
    out["writes_legacy_columns"] = hasattr(strategy, "populate_buy_trend")

    frame = load_pair_history(pair="BTC/USDT", timeframe=strategy.timeframe,
                              datadir=config["datadir"],
                              candle_type=CandleType.SPOT)
    if frame.empty:
        out["error"] = "no candles"
        return out
    frame = frame.iloc[-4000:].reset_index(drop=True)
    meta = {"pair": "BTC/USDT"}

    frame = strategy.advise_indicators(frame, meta)
    first = strategy.ft_advise_signals(frame, meta)
    out["after_one_pass"] = dupes(first)
    try:
        second = strategy.ft_advise_signals(first, meta)
        out["after_two_passes"] = dupes(second)
        out["second_pass"] = "ok"
    except Exception as exc:
        out["second_pass"] = "%s: %s" % (type(exc).__name__, exc)
    return out


def main():
    targets = json.loads(sys.argv[1])
    results = []
    for name, path in targets.items():
        try:
            results.append(probe(name, path))
        except Exception as exc:
            results.append({"strategy": name,
                            "error": "%s: %s" % (type(exc).__name__, exc)})
    print(json.dumps(results, indent=1, default=str))


if __name__ == "__main__":
    main()
