# -*- coding: utf-8 -*-
"""Why does a strategy that has entry logic never enter?

Load it the way freqtrade does, run populate_indicators and the entry hook
over real data, and count how many rows the entry condition marks. That
separates "the condition is never true" from "the indicator is not there".
"""
import io, json, os, sys, traceback
sys.path.insert(0, "/audit")
os.environ.setdefault("AUDIT_ROOT", "/audit")

import pandas as pd
from freqtrade.configuration import Configuration
from freqtrade.resolvers import StrategyResolver
from freqtrade.data.history import load_pair_history
from freqtrade.enums import CandleType

TARGETS = json.loads(sys.argv[1])
out = {}
for name, path in TARGETS.items():
    entry = {"strategy": name}
    try:
        directory = os.path.dirname(os.path.join("/audit", path))
        config = Configuration.from_files(["/audit/user_data/config.json"])
        config["strategy"] = name
        config["strategy_path"] = directory
        strategy = StrategyResolver.load_strategy(config)
        tf = strategy.timeframe
        df = load_pair_history(pair="BTC/USDT", timeframe=tf,
                               datadir=config["datadir"],
                               candle_type=CandleType.SPOT)
        # The whole history makes a Python-loop indicator take hours. The
        # question here is whether the entry condition ever fires, and the
        # last 30000 candles answer it as well as 700000 do.
        if len(df) > 30000:
            df = df.iloc[-30000:].reset_index(drop=True)
        entry["timeframe"] = tf
        entry["candles"] = len(df)
        if df.empty:
            entry["why"] = "no candles for this timeframe"
            out[name] = entry
            continue
        meta = {"pair": "BTC/USDT"}
        ind = strategy.advise_indicators(df.copy(), meta)
        sig = strategy.advise_entry(ind.copy(), meta)
        cols = [c for c in ("enter_long", "enter_short", "buy") if c in sig.columns]
        entry["entry_columns"] = cols
        entry["signals"] = {c: int(pd.to_numeric(sig[c], errors="coerce").fillna(0).astype(bool).sum())
                            for c in cols}
        # which named indicator columns are entirely missing or all-NaN
        allnan = sorted(c for c in ind.columns
                        if ind[c].isna().all())
        entry["all_nan_columns"] = allnan[:12]
    except Exception as exc:
        entry["error"] = "%s: %s" % (type(exc).__name__, exc)
        entry["trace"] = traceback.format_exc()[-400:]
    out[name] = entry
print(json.dumps(out, indent=1, default=str))
