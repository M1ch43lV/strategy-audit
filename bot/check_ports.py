# -*- coding: utf-8 -*-
"""Check the bot's ports against the original strategies, and its regime against the frozen table.

    ./ftenv/Scripts/python.exe -m bot.check_ports

The original classes are loaded from `repos/` and run through their own `populate_indicators` and
`populate_buy_trend`/`populate_sell_trend` on the same futures candles the bot uses. What is
compared:

- EI3v2_tag_cofi_green: entry and exit signal, candle by candle (the original's protections and
  trailing are not signals and are not compared).
- BuyOrDie: entry signal, candle by candle.
- Ichimoku_v31: the crossing events of the 4h series (the original sees them on 1h rows, the
  bot on 5m rows; both name the 4h candle they come from) and the "below the cloud" state.
- regime: the bot's daily phase per pair against `results/regime/regime_daily.csv`. That table
  was built on spot candles and the bot reads the same spot daily candles, so it must be identical.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "bot"))
DATA = os.path.join(ROOT, "user_data", "data", "binance", "futures")
PAIRS = ["ETH/USDT:USDT", "ADA/USDT:USDT", "LTC/USDT:USDT", "XRP/USDT:USDT"]
BTC = "BTC/USDT:USDT"
START, END = pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2022-12-31", tz="UTC")


class StubProvider(object):
    """Just enough of the data provider: futures candles from disk, a fresh copy on every call."""

    def __init__(self, pairs):
        self.pairs = pairs
        self.runmode = type("R", (), {"value": "backtest"})()

    def current_whitelist(self):
        return self.pairs

    def get_pair_dataframe(self, pair, timeframe="5m", candle_type=""):
        if pair == "BTC/USDT":
            pair = BTC
        if candle_type == "spot":
            stem = pair.split(":")[0].replace("/", "_")
            frame = pd.read_feather(os.path.join(os.path.dirname(DATA), "%s-%s.feather" % (stem, timeframe)))
        else:
            stem = pair.replace("/", "_").replace(":", "_")
            frame = pd.read_feather(os.path.join(DATA, "%s-%s-futures.feather" % (stem, timeframe)))
        frame["date"] = pd.to_datetime(frame["date"], utc=True)
        return frame.reset_index(drop=True)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def config():
    text = io.open(os.path.join(ROOT, "runtime", "profile_futures_config.json"), encoding="utf-8").read()
    cfg = json.loads(re.sub(r"//.*", "", text))
    cfg["runmode"] = "backtest"
    return cfg


def window(frame):
    return frame[(frame["date"] >= START) & (frame["date"] <= END)].reset_index(drop=True)


def report(name, ours, theirs):
    ours, theirs = np.asarray(ours).astype(bool), np.asarray(theirs).astype(bool)
    both, only_o, only_t = int((ours & theirs).sum()), int((ours & ~theirs).sum()), int((~ours & theirs).sum())
    print("%-34s both %5d  only bot %4d  only original %4d  %s" % (
        name, both, only_o, only_t, "IDENTICAL" if not (only_o or only_t) else "DIFFERENT"))
    return not (only_o or only_t)


def main():
    from RegimeRotationBot import RegimeRotationBot
    cfg = config()
    provider = StubProvider(PAIRS)
    bot = RegimeRotationBot(cfg)
    bot.dp = provider
    ok = True

    ei_mod = load(os.path.join(ROOT, "repos", "MMR-19_freqtrade-strategies", "strategies", "EI3v2_tag_cofi_green.py"), "orig_ei3v2")
    bod_mod = load(os.path.join(ROOT, "repos", "mikedigriz_freqtrade-strategy-mikedigriz", "strategies", "BuyOrDie.py"), "orig_bod")
    ich_mod = load(os.path.join(ROOT, "repos", "PeetCrypto_freqtrade-stuff", "Ichimoku_v31_Heikin.py"), "orig_ich")

    for pair in PAIRS:
        print("==", pair)
        base = provider.get_pair_dataframe(pair, "5m")
        mine = bot.populate_indicators(base.copy(), {"pair": pair})
        mine = window(mine)

        ei = ei_mod.EI3v2_tag_cofi_green(cfg)
        ei.dp = provider
        theirs = ei.populate_indicators(base.copy(), {"pair": pair})
        theirs = ei.populate_buy_trend(theirs, {"pair": pair})
        theirs = ei.populate_sell_trend(theirs, {"pair": pair})
        theirs = window(theirs)
        ok &= report("EI3v2 entry", mine["ei_buy"].eq(1), theirs["buy"].fillna(0).eq(1))
        ok &= report("EI3v2 exit", mine["ei_sell"].eq(1), theirs["sell"].fillna(0).eq(1))

        bod = bod_mod.BuyOrDie(cfg)
        theirs = bod.populate_indicators(base.copy(), {"pair": pair})
        theirs = window(bod.populate_buy_trend(theirs, {"pair": pair}))
        ok &= report("BuyOrDie entry", mine["bod_buy"].eq(1), theirs["buy"].fillna(0).eq(1))

        ich = ich_mod.Ichimoku_v31(cfg)
        ich.dp = provider
        one_hour = provider.get_pair_dataframe(pair, "1h")
        theirs = ich.populate_indicators(one_hour.copy(), {"pair": pair})
        theirs = ich.populate_buy_trend(theirs, {"pair": pair})
        theirs = ich.populate_sell_trend(theirs, {"pair": pair})
        theirs = window(theirs)
        # events: original 1h row at (4h open + 3h), bot 5m row at (4h open + 3h55m); compare the 4h candle
        t_events = set((theirs.loc[theirs["buy"].fillna(0).eq(1), "date"] - pd.Timedelta(hours=3)).tolist())
        m_events = set((mine.loc[mine["ich_buy"].eq(1), "date"] - pd.Timedelta(hours=3, minutes=55)).tolist())
        same = t_events == m_events
        print("%-34s original %d  bot %d  only bot %d  only original %d  %s" % (
            "Ichimoku 4h crossings", len(t_events), len(m_events), len(m_events - t_events), len(t_events - m_events),
            "IDENTICAL" if same else "DIFFERENT"))
        ok &= same
        # state: compare at the hour boundaries where both have the 4h value settled
        m_state = mine.set_index("date")["ich_sell"]
        t_state = theirs.set_index("date")["sell"].fillna(0)
        common = t_state.index.intersection(m_state.index)
        shifted = m_state.reindex(common + pd.Timedelta(minutes=55)).to_numpy()
        keep = ~np.isnan(shifted.astype(float))
        agree = float((shifted[keep].astype(int) == t_state.loc[common].to_numpy()[keep].astype(int)).mean())
        print("%-34s agreement at the hour: %.4f" % ("Ichimoku below-cloud state", agree))
        ok &= agree > 0.999

    print("== regime against results/regime/regime_daily.csv")
    daily = pd.read_csv(os.path.join(ROOT, "results", "regime", "regime_daily.csv"),
                        usecols=["date", "pair", "btc_regime", "coin_regime"])
    daily["date"] = pd.to_datetime(daily["date"], utc=True)
    for pair in PAIRS + [BTC]:
        base = provider.get_pair_dataframe(pair, "5m")
        mine = bot.populate_indicators(base.copy(), {"pair": pair})
        mine = mine[(mine["date"] >= pd.Timestamp("2021-01-01", tz="UTC")) & (mine["date"] < pd.Timestamp("2026-08-21", tz="UTC"))]
        day = mine.assign(day=mine["date"].dt.normalize()).groupby("day")[["btc_regime", "coin_regime"]].first()
        spot = daily[daily["pair"] == pair.split(":")[0]].set_index("date")
        joined = day.join(spot, how="inner", rsuffix="_spot")
        for kind in ("btc_regime", "coin_regime"):
            match = float((joined[kind] == joined[kind + "_spot"]).mean())
            print("%-16s %-12s days %5d  equal to the frozen table: %.4f" % (pair, kind, len(joined), match))
            ok &= match > 0.9999
    print("ALL CHECKS PASSED" if ok else "SOME CHECKS DIFFER")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
