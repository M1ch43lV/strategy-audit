# -*- coding: utf-8 -*-
"""Component search: does any strategy of the corpus beat cash in the phases where the rotation bot sits idle?

    ./ftenv/Scripts/python.exe -m bot.component_search

The rule is `PIPELINE_EXTENSIONS.md`, Part 4.4 (written before this was run). Phases and episodes are those of
`bot/phase_choice.py`. For every candidate and phase the return of an episode is the sum of the net returns of the
candidate's trades that opened in it (0 without a trade); the test is one-sided against cash over all episodes of the
phase in the training window, Benjamini-Hochberg at q = 0.10 over all tests, the first pass with leverage 1, the passers
again with the archive's own leverage (one-sided p < 0.05). The chosen candidate of a phase is the passer with the highest
mean episode return.

Two runs of the procedure: a walk-forward check inside the discovery window (train 2020-04-01..2022-12-31, test 2023)
and the final choice on the whole discovery window. The validation window is only read for information, in the final
portfolio, and is no longer out of sample.

Writes `results/regime/rotation_bot/component_search.json`.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from bot import phase_choice as pc, rotation_eval as ev  # noqa: E402
from evidence import execution_robustness as er  # noqa: E402
from regime import daily_return, specialist_evaluation as se  # noqa: E402

OUT = os.path.join(ev.RESULTS, "component_search.json")
PHASES = ("bear", "side", "trans")
FLOOR_TRADES = 30
Q = 0.10
P_TRUE_COST = 0.05
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
BASE_VARIANT = "RegimeRotationBot"
BOT_TAGS = ("ei3v2", "ichimoku", "buyordie")
WINDOWS = {  # name -> (first day of an episode, first day after)
    "train_wf": (ev.START, TRAIN_END),
    "test_wf": (TRAIN_END, se.VALIDATION_START),
    "disc": (ev.START, se.VALIDATION_START),
    "val": (se.VALIDATION_START, ev.END),
}


# ------------------------------------------------------------------ episodes
def daily_frame():
    daily = pd.read_csv(daily_return.DAILY, usecols=["date", "pair", "btc_regime", "coin_regime"])
    daily["date"] = pd.to_datetime(daily["date"], utc=True)
    daily = daily[(daily["date"] >= ev.START) & (daily["date"] < ev.END)].sort_values(["pair", "date"]).reset_index(drop=True)
    daily["coin"] = daily["pair"].str.split("/").str[0]
    daily["phase"] = pc.bot_phase(daily)
    ep = np.zeros(len(daily), dtype=np.int64)
    counter = 0
    for _, idx in daily.groupby("coin").indices.items():
        part = daily.iloc[idx]
        run = (part["phase"] != part["phase"].shift()) | (part["date"].diff() != pd.Timedelta(days=1))
        ep[idx] = counter + run.cumsum().to_numpy()
        counter = int(ep.max())
    daily["ep"] = ep
    first = daily.groupby("ep").agg(start=("date", "min"), phase=("phase", "first"), coin=("coin", "first"), days=("date", "size"),
                                    end=("date", "max")).reset_index()
    return daily[["coin", "date", "phase", "ep"]], first


def window_of_start(start):
    return {name: bool((start >= a) & (start < b)) for name, (a, b) in WINDOWS.items()}


# ------------------------------------------------------------------ per-candidate episode sums
class Sums:
    """Sum and sum of squares of the episode returns of candidates, per (candidate, episode)."""

    def __init__(self):
        self.parts = []

    def add(self, cand, ep, net, trades=None):
        frame = pd.DataFrame({"cand": cand, "ep": ep, "net": net, "n": 1})
        self.parts.append(frame.groupby(["cand", "ep"], as_index=False).agg(net=("net", "sum"), n=("n", "sum")))

    def table(self):
        allp = pd.concat(self.parts, ignore_index=True)
        return allp.groupby(["cand", "ep"], as_index=False).agg(net=("net", "sum"), n=("n", "sum"))


def candidate_ids():
    with io.open(os.path.join(ROOT, "STRATEGY_STATUS.csv"), encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return sorted(r["strategy_id"] for r in rows
                  if r["cohort"] == "E1_expanded" and r["execution_robustness_status"] == "PASS")


def read_corpus(candidates, lookup):
    """Episode sums of every candidate strategy from the Model 0 attribution table, leverage 1 assumed."""
    keep = set(candidates)
    sums = Sums()
    columns = ["strategy_id", "pair", "open_date", "profit_ratio"]
    for chunk in pd.read_csv(daily_return.TRADES, usecols=columns, chunksize=500_000, dtype={"strategy_id": "string", "pair": "string"}):
        chunk = chunk[chunk["strategy_id"].isin(keep)]
        if chunk.empty:
            continue
        chunk["day"] = pd.to_datetime(chunk["open_date"], utc=True).dt.floor("D")
        chunk["coin"] = chunk["pair"].str.split("/").str[0]
        merged = chunk.merge(lookup, left_on=["coin", "day"], right_on=["coin", "date"], how="inner")
        merged = merged[merged["phase"].isin(PHASES)]
        sums.add(merged["strategy_id"].astype(str).to_numpy(), merged["ep"].to_numpy(),
                 (merged["profit_ratio"] - 2.0 * ev.SLIP).to_numpy())
    return sums.table()


def bot_components(lookup, opens):
    """Episode sums of the four components of the bot: EI3v2, Ichimoku, BuyOrDie from the base variant's trades."""
    trades, missing = ev.load_trades(BASE_VARIANT)
    assert not missing, missing
    frame = ev.build_frame(trades, BASE_VARIANT)
    frame["day"] = frame["open_date"].dt.floor("D")
    frame["coin"] = frame["pair"].str.split("/").str[0]
    merged = frame[frame["enter_tag"].isin(BOT_TAGS)].merge(lookup, left_on=["coin", "day"], right_on=["coin", "date"], how="inner")
    sums = Sums()
    sums.add("bot:" + merged["enter_tag"].astype(str), merged["ep"].to_numpy(),
             (merged["profit_ratio"] - 2.0 * ev.SLIP * merged["leverage"]).to_numpy())
    return sums.table()


def hold_in_phase(first, opens):
    """Buy-and-Hold of the coin for the length of each episode, net of a round trip (candidate `bot:hold_phase`)."""
    rows = []
    for _, r in first[first["phase"].isin(PHASES)].iterrows():
        v = pc.hold_return(r["coin"], r["start"], r["end"], opens)
        if not np.isnan(v):
            rows.append({"cand": "bot:hold_phase", "ep": int(r["ep"]), "net": v, "n": 1})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ statistics
def tests(table, first, window, floor=FLOOR_TRADES):
    """One row per (candidate, phase): trades, episodes, mean, one-sided p against cash."""
    flags = first.copy()
    a, b = WINDOWS[window]
    flags = flags[(flags["start"] >= a) & (flags["start"] < b) & flags["phase"].isin(PHASES)]
    n_eps = flags.groupby("phase").size().to_dict()
    merged = table.merge(flags[["ep", "phase"]], on="ep", how="inner")
    merged["sq"] = merged["net"] ** 2
    grouped = merged.groupby(["cand", "phase"], as_index=False).agg(S=("net", "sum"), SS=("sq", "sum"), trades=("n", "sum"), traded=("ep", "size"))
    grouped["N"] = grouped["phase"].map(n_eps)
    grouped["mean"] = grouped["S"] / grouped["N"]
    var = (grouped["SS"] - grouped["N"] * grouped["mean"] ** 2) / (grouped["N"] - 1)
    grouped["sd"] = np.sqrt(var.clip(lower=0))
    tstat = grouped["mean"] / (grouped["sd"] / np.sqrt(grouped["N"]))
    grouped["p"] = 1.0 - stats.t.cdf(tstat, grouped["N"] - 1)
    grouped.loc[~np.isfinite(grouped["p"]), "p"] = 1.0
    return grouped[grouped["trades"] >= floor].reset_index(drop=True) if floor else grouped


def benjamini_hochberg(p, q):
    p = np.asarray(p, dtype=float)
    order = np.argsort(p)
    m = len(p)
    passed = np.zeros(m, dtype=bool)
    threshold = -1
    for rank, idx in enumerate(order, start=1):
        if p[idx] <= q * rank / m:
            threshold = rank
    if threshold > 0:
        passed[order[:threshold]] = True
    return passed


def archive_trades(strategy, manifest):
    entry = manifest.get(strategy) or {}
    block = er.read_block(entry.get("archive"), strategy) if entry.get("archive") else None
    return (block or {}).get("trades") or []


def true_cost_table(cands, lookup, manifest):
    """Episode sums with the archive's own leverage, for the given strategies (bot candidates are already exact)."""
    sums = Sums()
    for sid in cands:
        trades = archive_trades(sid, manifest)
        if not trades:
            continue
        frame = pd.DataFrame({"pair": [t["pair"] for t in trades], "open": [t["open_date"] for t in trades],
                              "pr": [t["profit_ratio"] for t in trades], "lev": [t.get("leverage") or 1.0 for t in trades]})
        frame["day"] = pd.to_datetime(frame["open"], utc=True).dt.floor("D")
        frame["coin"] = frame["pair"].str.split("/").str[0]
        m = frame.merge(lookup, left_on=["coin", "day"], right_on=["coin", "date"], how="inner")
        m = m[m["phase"].isin(PHASES)]
        sums.add(np.repeat(sid, len(m)), m["ep"].to_numpy(), (m["pr"] - 2.0 * ev.SLIP * m["lev"]).to_numpy())
    return sums.table()


def select(table, exact_tables, first, window, manifest, lookup):
    """The procedure on one training window. Returns the test frame with `passed`, `passed_true` and the chosen candidate."""
    t = tests(table, first, window)
    t["bh"] = benjamini_hochberg(t["p"].to_numpy(), Q)
    strategies = sorted({c for c in t.loc[t["bh"], "cand"] if not str(c).startswith("bot:")})
    exact = true_cost_table(strategies, lookup, manifest)
    t2 = tests(exact, first, window, floor=0) if len(exact) else pd.DataFrame(columns=["cand", "phase", "p", "mean"])
    key = t2.set_index(["cand", "phase"])
    t["p_true"] = [key["p"].get((c, ph), np.nan) if not str(c).startswith("bot:") else p for c, ph, p in zip(t["cand"], t["phase"], t["p"])]
    t["mean_true"] = [key["mean"].get((c, ph), np.nan) if not str(c).startswith("bot:") else m for c, ph, m in zip(t["cand"], t["phase"], t["mean"])]
    t["passed"] = t["bh"] & (t["p_true"] < P_TRUE_COST)
    chosen = {}
    for phase in PHASES:
        ok = t[(t["phase"] == phase) & t["passed"]]
        chosen[phase] = None if ok.empty else ok.sort_values("mean_true", ascending=False).iloc[0]["cand"]
    return t, chosen


def main():
    lookup, first = daily_frame()
    opens = {}
    for coin in ev.PAIRS:
        d = pd.read_feather(os.path.join(ROOT, "user_data", "data", "binance", "%s_USDT-1d.feather" % coin), columns=["date", "open"])
        d["date"] = pd.to_datetime(d["date"], utc=True)
        opens[coin] = d.set_index("date")["open"]
    manifest = json.load(open(os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json"), encoding="utf-8"))["results"]

    candidates = candidate_ids()
    print("candidates (E1, execution PASS): %d" % len(candidates), flush=True)
    table = pd.concat([read_corpus(candidates, lookup), bot_components(lookup, opens), hold_in_phase(first, opens)], ignore_index=True)
    print("episode table rows: %d" % len(table), flush=True)

    out = {"rule": "PIPELINE_EXTENSIONS.md Part 4.4", "candidates": len(candidates), "q": Q, "floor_trades": FLOOR_TRADES}

    # --- check of the procedure: train 2020-04..2022, test 2023
    t_wf, chosen_wf = select(table, None, first, "train_wf", manifest, lookup)
    test = tests(table, first, "test_wf", floor=0).set_index(["cand", "phase"])
    wf = {}
    for phase in PHASES:
        cand_rows = t_wf[t_wf["phase"] == phase]
        passers = cand_rows[cand_rows["passed"]]

        def test_mean(c):
            return float(test["mean"].get((c, phase), 0.0))
        ref = [test_mean(c) for c in cand_rows["cand"]]
        wf[phase] = {"floor_candidates": int(len(cand_rows)), "passers": int(len(passers)), "chosen": chosen_wf[phase],
                     "train_mean_pct_chosen": None if chosen_wf[phase] is None else round(100 * float(passers.set_index("cand").loc[chosen_wf[phase], "mean_true"]), 4),
                     "test_mean_pct_chosen": None if chosen_wf[phase] is None else round(100 * test_mean(chosen_wf[phase]), 4),
                     "test_mean_pct_passers": None if passers.empty else round(100 * float(np.mean([test_mean(c) for c in passers["cand"]])), 4),
                     "test_mean_pct_reference_all_floor_candidates": round(100 * float(np.mean(ref)), 4) if ref else None,
                     "share_passers_positive_in_test": None if passers.empty else round(float(np.mean([test_mean(c) > 0 for c in passers["cand"]])), 3)}
    out["walk_forward"] = wf
    for phase, r in wf.items():
        print("WF %-6s floor %4d passers %3d chosen %-32s train %s test %s | passers' test %s | reference %s | share>0 %s" % (
            phase, r["floor_candidates"], r["passers"], r["chosen"], r["train_mean_pct_chosen"], r["test_mean_pct_chosen"],
            r["test_mean_pct_passers"], r["test_mean_pct_reference_all_floor_candidates"], r["share_passers_positive_in_test"]), flush=True)

    # --- final choice on the whole discovery window
    t_fin, chosen = select(table, None, first, "disc", manifest, lookup)
    out["final"] = {"chosen": chosen, "passers": {ph: t_fin[(t_fin["phase"] == ph) & t_fin["passed"]].sort_values("mean_true", ascending=False)
                                                    [["cand", "trades", "mean_true", "p_true"]].head(15).to_dict("records") for ph in PHASES}}
    for phase in PHASES:
        print("FINAL %-6s chosen %s; passers %d" % (phase, chosen[phase], int(((t_fin["phase"] == phase) & t_fin["passed"]).sum())), flush=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(out, handle, indent=1, sort_keys=True, default=lambda o: None if o is None else float(o) if hasattr(o, "__float__") else str(o))
        handle.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
