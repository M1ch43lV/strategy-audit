# -*- coding: utf-8 -*-
"""Build the "Regime Specialists" page from the Model 0 evaluation.

The page used to be assembled by hand from exports kept outside the repository, so it
went stale the moment the evaluation was rerun. This puts one command between the two:

    ./ftenv/Scripts/python.exe -m tools.regime_specialists_page

It reads `results/regime/specialist_evaluation/` (Model 0), the Stage 8b stores
(`evidence/EXECUTION_ROBUSTNESS.json`, `evidence/COST_SCREEN.json`) and writes
`regime_specialists.html` (English) at the repository root. Every number in the running text is
computed here and filled into `{{token}}` slots of `tools/REGIME_SPECIALISTS.template.html`;
a claim that depends on the result (that the fully consistent candidates are all
FastSupertrend variants, for one) is written only when the data still shows it.

It also writes `regime_gating.html` (German), the second page: the Model 1/2/3 sections and the top-10
selection are snapshots of the gated runs and live as JSON under
`tools/regime_specialists_data/`; they are not recomputed here. Both pages share
`tools/regime_pages_common.css` and `tools/regime_pages_common.js`.

The Stage 8b annotation is a column and changes no ranking: a row is marked `PASS` when
the strategy passed the 5m detail rerun (measured, or by the owner rule at or below 5m)
and the cost screen in the ADX state the row claims.
"""
from __future__ import annotations

import argparse
import csv
import datetime
import io
import math
import json
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evidence import execution_robustness as er, profile_full_window, verdicts  # noqa: E402


# One name per gate, so a comparison states which verdict class it means. The
# vocabulary and its fail-closed behaviour live in `evidence/verdicts.py`.
def _robustness_verdict(raw):
    return verdicts.value("STRATEGY_STATUS.csv", "execution_robustness_status", raw)


def _cost_verdict(raw):
    return verdicts.value("COST_SCREEN.json", "status", raw)


def _run_verdict(raw):
    return verdicts.value("full_backtest_manifest.json", "status", raw)

SPEC = os.path.join(ROOT, "results", "regime", "specialist_evaluation")
DATA = os.path.join(ROOT, "tools", "regime_specialists_data")
TEMPLATE = os.path.join(ROOT, "tools", "REGIME_SPECIALISTS.template.html")
GATING_TEMPLATE = os.path.join(ROOT, "tools", "REGIME_GATING.template.html")
BENCHMARK_TEMPLATE = os.path.join(ROOT, "tools", "VALIDATION_BENCHMARK.template.html")
COMMON_CSS = os.path.join(ROOT, "tools", "regime_pages_common.css")
COMMON_JS = os.path.join(ROOT, "tools", "regime_pages_common.js")
DETAIL_TOTALS = os.path.join(SPEC, "detail_5m_total_dollar_gain.csv")
GAIN_COLUMNS = ["strategy_id", "trades", "dollar_gain_usd", "benchmark_matched_trades",
                "benchmark_dollar_gain_usd", "excess_dollar_gain_usd"]
# The two artifacts link to each other. The gating page is published first; its address goes here.
MAIN_URL = "https://claude.ai/artifact/6PoC2NwYCruR6UoJ81Bgia"
# Owner's target: at least this return per day on the capital (0.08 %).
DAILY_TARGET = 0.0008
# A pick needs this many trades in its phase; a thinner one is listed but not chosen.
PORTFOLIO_MIN_TRADES = 30
# Until it is published, the benchmark page is linked by its file name.
BENCHMARK_URL = "validation_benchmark.html"
GATING_URL = "https://claude.ai/artifact/LjAu8PjEDrZXdK8vnAbcZM"
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
PROFILES = os.path.join(ROOT, "evidence", "EXECUTION_PROFILES.csv")
POOLED = os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json")
ATTRIBUTION = os.path.join(ROOT, "results", "regime", "attribution_manifest.json")
TRADES = os.path.join(ROOT, "results", "regime", "trade_regime_attribution.csv")

STATES = ["BULL", "BEAR", "SIDEWAYS", "TRANSITION"]
WORDS = {0: "zero times", 1: "once", 2: "twice", 3: "three times", 4: "four times", 5: "five times",
         6: "six times", 7: "seven times", 8: "eight times", 9: "nine times", 10: "ten times",
         11: "eleven times", 12: "twelve times", 13: "thirteen times", 14: "fourteen times",
         15: "fifteen times", 16: "sixteen times", 17: "seventeen times", 18: "eighteen times",
         19: "nineteen times", 20: "twenty times"}
COUNT_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
               9: "nine", 10: "ten"}


def clean(value):
    if isinstance(value, float) and pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def de_int(n):
    """Integer with thousands commas (the name is historical; the page is English now)."""
    return "{:,}".format(int(n))


def de_pct(x, digits=0):
    return ("{:.%df}%%" % digits).format(x)


def _read_json(path):
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


# ------------------------------------------------------------------ robustness
class Robustness(object):
    """Stage 8b, joined to the ranking rows. Reads the stores, never rewrites them."""

    def __init__(self):
        with io.open(STATUS, newline="", encoding="utf-8-sig") as handle:
            self.table = {r["strategy_id"]: r for r in csv.DictReader(handle)}
        self.cost = _read_json(er.COST_OUTPUT)["results"]
        self.record = _read_json(er.ROBUSTNESS_OUTPUT)["results"]

    def timeframe(self, strategy):
        """The strategy's own (author) timeframe and its length in minutes, 0 if unknown."""
        tf = (self.record.get(strategy) or {}).get("main_timeframe") or ""
        return tf, er.TF_MINUTES.get(tf, 0)

    def status(self, strategy):
        return (self.table.get(strategy) or {}).get("execution_robustness_status") or "NA"

    def row(self, strategy, kind, state):
        xs = self.status(strategy)
        ok = _robustness_verdict(xs) == "PASS" and er.qualifies_in(self.cost.get(strategy), kind, state)
        return {"xs": xs, "ok": 1 if ok else 0}

    def total(self, strategy):
        """The whole validation window, all states together."""
        xs = self.status(strategy)
        cost = er.validation_total(self.cost.get(strategy), "btc")
        ok = _robustness_verdict(xs) == "PASS" and _cost_verdict(cost["status"]) == "PASS"
        record = self.record.get(strategy) or {}
        basis = {er.BASIS_RULE: "rule", er.BASIS_MEASURED: "measured"}.get(record.get("basis"), "")
        return {"xs": xs, "ok": 1 if ok else 0, "cv": cost["status"],
                "cm": cost["mean_profit_pct"], "c10": cost["stressed_pct"],
                "tf": record.get("main_timeframe") or "", "xb": basis}

    def universal(self, strategy):
        xs = self.status(strategy)
        ok = _robustness_verdict(xs) == "PASS" and er.qualifies_universal(self.cost.get(strategy), "coin")
        return {"xs": xs, "ok": 1 if ok else 0}


# ------------------------------------------------------------------ confirmation
def confirmation_lookups(frame, universal):
    """Discovery confirmation (regime/discovery_comparison.py) per strategy, kind and phase,
    and per universal candidate, from the 5m-basis pairs (`five_minute_basis`)."""
    rows = {}
    for r in frame.itertuples(index=False):
        both = bool(r.floor_disc and r.floor_val)
        rows[(r.kind, r.strategy_id, r.regime)] = (
            2 if r.confirmed else (1 if both else 0),
            None if pd.isna(r.confirmation_score) else round(float(r.confirmation_score), 4))
    uni = {}
    for r in universal.itertuples(index=False):
        uni[r.strategy_id] = ({"strict": 2, "mild": 1, "none": 0}[r.rule],
                              None if pd.isna(r.score) else round(float(r.score), 4),
                              int(r.phases_better_in_both), int(r.phases_confirmed))
    return rows, uni


def five_minute_basis(robustness, author_tables, universal_ids):
    """The tables every figure on the page is computed from (owner decision 2026-09-26).

    A strategy above 5m contributes its 5m detail run only, because a run at the author timeframe is not
    a real result there; a strategy at or below 5m contributes its baseline, which already is the 5m
    resolution. A strategy above 5m without a finished 5m run contributes nothing. Returns the effective
    BTC, coin and total-gain tables and the set of strategies above 5m."""
    above = {s for s in robustness.record if robustness.timeframe(s)[1] > 5}
    names = {"btc": "detail_5m_btc_specialist_table.csv", "coin": "detail_5m_coin_specialist_table.csv"}
    out = {}
    for kind, file in names.items():
        detail = pd.read_csv(os.path.join(SPEC, file))
        base = author_tables[kind]
        out[kind] = pd.concat([base[~base["strategy_id"].isin(above)],
                               detail[detail["strategy_id"].isin(above)]], ignore_index=True)
    detail = pd.read_csv(DETAIL_TOTALS)[GAIN_COLUMNS]
    base = author_tables["gain"]
    out["gain"] = pd.concat([base[~base["strategy_id"].isin(above)],
                             detail[detail["strategy_id"].isin(above)]], ignore_index=True)
    out["gain"] = out["gain"].sort_values("dollar_gain_usd", ascending=False).reset_index(drop=True)
    return out, above


def discovery_basis(above):
    """Discovery against validation on the 5m basis: the frame, its summary and the universal confirmation."""
    from regime import discovery_comparison as dc
    paired = os.path.join(SPEC, "discovery_vs_validation.csv")
    detail = os.path.join(SPEC, "detail_5m_discovery_vs_validation.csv")
    if not (os.path.isfile(paired) and os.path.isfile(detail)):
        raise SystemExit("run `python -m regime.discovery_comparison` and `python -m regime.detail_totals` first")
    frame = dc.five_minute_basis(pd.read_csv(paired), pd.read_csv(detail), above)
    return frame, dc


def _num(value, digits=6):
    return None if value is None or pd.isna(value) else round(float(value), digits)


def daily_lookup(robustness):
    """Daily return per strategy, kind and phase in the validation window after 0.1 % slippage
    per side (the cost screen's own stressed mean, leverage included), and before slippage in
    the discovery window. regime/daily_return.py defines the two readings."""
    frame = pd.read_csv(os.path.join(SPEC, "phase_daily_return.csv"))
    key = "%.4f" % er.COST["reference_slippage_per_side"]
    phase, total = {}, {}
    disc = {(r.strategy_id, r.kind, r.regime): r for r in frame[frame["window"] == "discovery"].itertuples(index=False)}
    sums = {}
    for r in frame[frame["window"] == "validation"].itertuples(index=False):
        cell = (((robustness.cost.get(r.strategy_id) or {}).get("by_regime") or {}).get(r.kind, {})
                .get(r.regime, {}).get("validation") or {})
        stressed = (cell.get("stressed") or {}).get(key, {}).get("mean_profit_pct")
        net = None if stressed is None else r.trades * stressed / 100.0
        d = disc.get((r.strategy_id, r.kind, r.regime))
        phase[(r.strategy_id, r.kind, r.regime)] = {
            "dc": None if net is None else _num(net / r.capital_days),
            "ds": None if net is None else _num(net / r.slot_days),
            "dd": None if d is None or pd.isna(d.slot_days) else _num(d.ratio_sum / d.slot_days)}
        if r.kind == "btc" and net is not None:
            s = sums.setdefault(r.strategy_id, [0.0, 0.0, 0.0])
            s[0] += net
            s[1] += r.capital_days
            s[2] += r.slot_days
    for sid, (net, days, slots) in sums.items():
        total[sid] = {"dc": _num(net / days), "ds": _num(net / slots)}
    return phase, total


def buy_hold_daily():
    frame = pd.read_csv(os.path.join(SPEC, "buy_hold_daily_return.csv"))
    out = {}
    for r in frame.itertuples(index=False):
        out[(r.kind, r.regime, r.window)] = {"daily": _num(r.daily_return), "episodes": int(r.episodes), "days": int(r.days)}
    return out


def portfolio(coin_rows, bh):
    """One pick per coin phase, by a rule that is computed, not chosen by hand.

    Qualified: Stage 8b PASS in this phase, confirmed in both windows, and a daily return on
    the provided capital of at least the target after slippage and above Buy-and-Hold's. The
    pick is the qualified row with the highest such return among those with enough trades. Where
    none qualifies, the phase shows the best rows that are robust and clear the floor in both
    windows but are not confirmed, flagged as such, and Buy-and-Hold if it reaches the target."""
    phases, weights = [], {}
    total_days = sum(bh[("coin", s, "validation")]["days"] for s in STATES)
    for s in STATES:
        hold = bh[("coin", s, "validation")]
        hold_disc = bh[("coin", s, "discovery")]
        weight = hold["days"] / float(total_days)
        rows = [r for r in coin_rows if r["regime"] == s and r.get("ds") is not None and r["ok"]]

        def entry(r):
            return {"sid": r["strategy_id"], "trades": r["trades"], "episodes": r["episodes"],
                    "excess": r["excess_return"], "lcb": r["episode_excess_lcb"], "cf": r["cf"], "sc": r["sc"],
                    "dc": r["dc"], "ds": r["ds"], "dd": r["dd"], "xs": r["xs"]}

        floor = max(DAILY_TARGET, hold["daily"])
        qualified = sorted((r for r in rows if r["cf"] == 2 and r["ds"] >= floor), key=lambda r: -r["ds"])
        partial = sorted((r for r in rows if r["cf"] == 1 and r["ds"] >= floor), key=lambda r: -r["ds"])
        pick = next((r for r in qualified if r["trades"] >= PORTFOLIO_MIN_TRADES), None)
        status = "confirmed"
        if pick is None:
            pick = next((r for r in partial if r["trades"] >= PORTFOLIO_MIN_TRADES), None)
            status = "unconfirmed"
        phases.append({"regime": s, "weight": round(weight, 4),
                       "hold": {"val": hold["daily"], "disc": hold_disc["daily"], "episodes": hold["episodes"], "days": hold["days"]},
                       "pick": dict(entry(pick), status=status) if pick else None,
                       "qualified": [entry(r) for r in qualified[:6]], "partial": [entry(r) for r in partial[:4]],
                       "n_qualified": len(qualified), "n_partial": len(partial)})
    return {"target": DAILY_TARGET, "min_trades": PORTFOLIO_MIN_TRADES, "phases": phases}


X5_KEYS = ["trades", "episodes", "excess_return", "dollar_gain_usd", "benchmark_dollar_gain_usd",
           "median_excess_return", "max_drawdown", "worst_trade", "sortino", "annualized_return",
           "profit_factor", "freqforge_score", "episode_excess_lcb", "lcb_grade", "dc", "ds", "dd"]


def detail_lookup():
    """The phase rows of the 5m detail runs (regime/detail_totals.py), keyed like the author rows.
    A row under the specialist floor carries only its tier and counts, so the page can say why
    there is no figure."""
    names = {"btc": ("detail_5m_btc_specialist_table.csv", "btc_regime"),
             "coin": ("detail_5m_coin_specialist_table.csv", "coin_regime")}
    path = os.path.join(SPEC, "detail_5m_phase_daily.csv")
    if not os.path.isfile(path):
        raise SystemExit("run `python -m regime.detail_totals` first")
    daily = pd.read_csv(path)
    dmap = {(r.strategy_id, r.kind, r.regime): r for r in daily.itertuples(index=False)}
    out = {}
    for kind, (file, column) in names.items():
        table = pd.read_csv(os.path.join(SPEC, file))
        median = table[table["tier"] == "VALIDATION"].groupby("strategy_id")["excess_return"].median()
        for r in table.to_dict(orient="records"):
            key = (kind, r["strategy_id"], r[column])
            if r["tier"] != "VALIDATION":
                out[key] = {"tier": r["tier"], "trades": int(r["trades"]), "episodes": int(r["episodes"])}
                continue
            d = dmap.get((r["strategy_id"], kind, r[column]))
            record = {k: clean(r[k]) for k in ("excess_return", "dollar_gain_usd", "benchmark_dollar_gain_usd",
                                               "max_drawdown", "worst_trade", "sortino", "annualized_return",
                                               "profit_factor", "freqforge_score", "episode_excess_lcb")}
            record.update(trades=int(r["trades"]), episodes=int(r["episodes"]), lcb_grade=r["lcb_grade"],
                          median_excess_return=_num(median.get(r["strategy_id"])),
                          dc=_num(d.daily_on_capital) if d is not None else None,
                          ds=_num(d.daily_on_slots) if d is not None else None,
                          dd=_num(d.daily_discovery) if d is not None else None, tier="VALIDATION")
            out[key] = record
    return out


def confirmed_phase_counts(frame):
    """Per strategy: in how many coin and BTC phases it is confirmed."""
    done = frame[frame["confirmed"]]
    counts = {}
    for kind in ("coin", "btc"):
        counts[kind] = done[done["kind"] == kind].groupby("strategy_id").size().to_dict()
    return counts


def total_rows(gain, robustness, uconfirm, daily_total, pairs, author_gain):
    """The whole-window table: author timeframe and 5m rerun side by side, robustness and
    confirmation. The 5m side comes from regime/detail_totals.py, never recomputed here.

    The rank (`rk`) is by the 5m gain. A strategy at or below 5m ranks by its own run (that run already is
    the 5m resolution); a strategy above 5m without a 5m run is unranked, because its author-timeframe
    figure is not a real result."""
    if not os.path.isfile(DETAIL_TOTALS):
        raise SystemExit("run `python -m regime.detail_totals` first")
    d5 = pd.read_csv(DETAIL_TOTALS).set_index("strategy_id")
    phases = confirmed_phase_counts(pairs)
    rows = []
    for row in gain.to_dict(orient="records"):
        sid = row["strategy_id"]
        record = {k: clean(v) for k, v in row.items()}
        record.update(robustness.total(sid))
        record.update(daily_total.get(sid, {}))
        if sid in d5.index:
            d = d5.loc[sid]
            record.update(d_trades=int(d["trades"]), d_gain=clean(d["dollar_gain_usd"]),
                          d_bench=clean(d["benchmark_dollar_gain_usd"]),
                          d_excess=clean(d["excess_dollar_gain_usd"]),
                          d_cm=clean(d["cost_mean_pct"]), d_c10=clean(d["cost_stressed_pct"]),
                          d_dc=_num(d["daily_on_capital"]), d_ds=_num(d["daily_on_slots"]))
        tf, minutes = robustness.timeframe(sid)
        record["tfm"] = minutes
        if minutes > 5 and sid in d5.index:
            # above 5m the row already is the 5m run; the author side is not shown
            record.update(dc=record.get("d_dc"), ds=record.get("d_ds"))
        if tf == "5m":
            record.update(d_trades=record["trades"], d_gain=record["dollar_gain_usd"],
                          d_bench=record["benchmark_dollar_gain_usd"], d_excess=record["excess_dollar_gain_usd"],
                          d_cm=record.get("cm"), d_c10=record.get("c10"), d_dc=record.get("dc"), d_ds=record.get("ds"))
        ur, us, up, _ = uconfirm.get(sid, (-1, None, 0, 0))
        cn, bn = phases["coin"].get(sid, 0), phases["btc"].get(sid, 0)
        record.update(ur=ur, us=us, up=up, cn=cn, bn=bn, cq=100 * max(ur, 0) + 10 * cn + bn)
        rows.append(record)
    # above 5m without a finished 5m run: listed with its status, no figures (an author-timeframe figure is not a result)
    have = {r["strategy_id"] for r in rows}
    for row in author_gain.to_dict(orient="records"):
        sid = row["strategy_id"]
        tf, minutes = robustness.timeframe(sid)
        if sid in have or minutes <= 5:
            continue
        record = {"strategy_id": sid}
        record.update(robustness.total(sid))
        record["tfm"] = minutes
        ur, us, up, _ = uconfirm.get(sid, (-1, None, 0, 0))
        record.update(ur=ur, us=us, up=up, cn=0, bn=0, cq=0)
        rows.append(record)
    ranked = []
    for record in rows:
        at_or_below_5m = 0 < record["tfm"] <= 5
        effective = record.get("d_gain")
        if effective is None and at_or_below_5m:
            effective = record.get("dollar_gain_usd")
        record["rk"] = None
        if effective is not None:
            ranked.append((-effective, record["strategy_id"], record))
    for rank, (_, _, record) in enumerate(sorted(ranked, key=lambda t: (t[0], t[1])), start=1):
        record["rk"] = rank
    return rows


# ------------------------------------------------------------------ data exports
def regime_rows(table, regime_col, kind, robustness, confirm, daily, detail):
    qualified = table[table["tier"] == "VALIDATION"].copy()
    median_by_strategy = qualified.groupby("strategy_id")["excess_return"].median()
    qualified["median_excess_return"] = qualified["strategy_id"].map(median_by_strategy)
    rows = []
    for _, row in qualified.iterrows():
        record = {
            "strategy_id": row["strategy_id"], "regime": row[regime_col],
            "trades": int(row["trades"]), "episodes": int(row["episodes"]),
            "excess_return": clean(row["excess_return"]),
            "dollar_gain_usd": clean(row["dollar_gain_usd"]),
            "benchmark_dollar_gain_usd": clean(row["benchmark_dollar_gain_usd"]),
            "median_excess_return": clean(row["median_excess_return"]),
            "max_drawdown": clean(row["max_drawdown"]),
            "worst_trade": clean(row["worst_trade"]),
            "sortino": clean(row["sortino"]),
            "annualized_return": clean(row["annualized_return"]),
            "profit_factor": clean(row["profit_factor"]),
            "freqforge_score": clean(row["freqforge_score"]),
            "episode_excess_lcb": clean(row["episode_excess_lcb"]),
            "lcb_grade": row["lcb_grade"],
        }
        record.update(robustness.row(row["strategy_id"], kind, row[regime_col]))
        cf, sc = confirm.get((kind, row["strategy_id"], row[regime_col]), (0, None))
        record["cf"], record["sc"] = cf, sc
        record.update(daily.get((row["strategy_id"], kind, row[regime_col]), {"dc": None, "ds": None, "dd": None}))
        tf, minutes = robustness.timeframe(row["strategy_id"])
        record["tf"], record["tfm"] = tf, minutes
        if minutes > 5:
            # the row is the 5m run itself; its daily returns come from the 5m run too
            x = detail.get((kind, row["strategy_id"], row[regime_col])) or {}
            record.update(dc=x.get("dc"), ds=x.get("ds"), dd=x.get("dd"))
        if tf == "5m":
            # the author timeframe is 5m: the same run, the same figures
            record["x5"] = {k: record.get(k) for k in X5_KEYS}
        else:
            record["x5"] = detail.get((kind, row["strategy_id"], row[regime_col]))
        rows.append(record)
    return rows


DETAIL_COLS = ["trades", "episodes", "dollar_gain_usd", "benchmark_dollar_gain_usd",
               "max_drawdown", "worst_trade", "sortino", "annualized_return", "profit_factor",
               "freqforge_score", "episode_excess_lcb", "lcb_grade"]


def universal_x5(sid, worst, detail):
    """The 5m rerun's figures at the strategy's worst coin phase, and its median and consistency over
    the four coin phases, or None where the rerun lacks one of them at the floor."""
    cells = {s: detail.get(("coin", sid, s)) for s in STATES}
    if any(c is None or c.get("tier") != "VALIDATION" for c in cells.values()):
        return None
    at = cells.get(worst)
    excess = [c["excess_return"] for c in cells.values()]
    out = {k: at.get(k) for k in ("trades", "episodes", "dollar_gain_usd", "benchmark_dollar_gain_usd", "max_drawdown",
                                  "worst_trade", "sortino", "annualized_return", "profit_factor", "freqforge_score",
                                  "episode_excess_lcb", "lcb_grade")}
    out["worst_regime_return"] = at["excess_return"]
    out["median_regime_excess_return"] = float(pd.Series(excess).median())
    out["regime_consistency"] = float(sum(1 for e in excess if e > 0)) / len(excess)
    return out


def universal_rows(universal, coin, robustness, uconfirm, detail):
    indexed = coin.set_index(["strategy_id", "coin_regime"])
    rows = []
    for row in universal.to_dict(orient="records"):
        record = {k: clean(v) for k, v in row.items()}
        detail = indexed.loc[(row["strategy_id"], row["worst_regime"])]
        for column in DETAIL_COLS:
            record[column] = clean(detail[column])
        record.update(robustness.universal(row["strategy_id"]))
        ur, us, up, uc = uconfirm.get(row["strategy_id"], (0, None, 0, 0))
        record.update({"ur": ur, "us": us, "up": up, "uc": uc})
        tf, minutes = robustness.timeframe(row["strategy_id"])
        record["tf"], record["tfm"] = tf, minutes
        if tf == "5m":
            keys = DETAIL_COLS + ["worst_regime_return", "median_regime_excess_return", "regime_consistency"]
            record["x5"] = {k: record.get(k) for k in keys}
        else:
            record["x5"] = universal_x5(row["strategy_id"], row["worst_regime"], detail)
        rows.append(record)
    return rows


def native_stats(strategy_ids, robustness):
    """Freqtrade's own report block for every strategy that has a run at 5m resolution.

    A strategy above 5m takes the block of its 5m detail run (`EXECUTION_ROBUSTNESS.json`, `detail.archive`);
    a strategy at or below 5m takes its baseline block through the identity-checked lookup that the
    Model 0/1/2/3 comparison uses. Returns the rows and the number of baseline strategies that lookup rejected."""
    from regime import model_compare
    strategy_ids = list(strategy_ids)
    above = [s for s in strategy_ids if robustness.timeframe(s)[1] > 5]
    below = [s for s in strategy_ids if robustness.timeframe(s)[1] <= 5]
    full = _read_json(str(model_compare.MODEL0))
    _, accepted, rejected = model_compare._load_model0(
        model_compare.MODEL0, set(below), full["timerange"])
    accepted = dict(accepted)
    # The owner-approved 5m recovery baselines (dagger) carry another measurement scope than the
    # strict Model 0 check accepts, but the evaluation accepts them (`ACCEPTED_BASELINE_SCOPES`);
    # their archive is read directly.
    manifest = _read_json(POOLED)["results"]
    for item in list(rejected):
        result = manifest.get(item["strategy_id"]) or {}
        if (item["reason"] == "model0_measurement_scope_mismatch" and _run_verdict(result.get("status")) == "MEASURED"
                and result.get("measurement_scope") in er.ACCEPTED_BASELINE_SCOPES and result.get("archive")):
            block = er.read_block(result["archive"], item["strategy_id"])
            if block is not None:
                accepted[item["strategy_id"]] = {"summary": block}
                rejected.remove(item)
    for strategy in above:
        archive = ((robustness.record.get(strategy) or {}).get("detail") or {}).get("archive")
        block = er.read_block(archive, strategy) if archive else None
        if block is not None:
            accepted[strategy] = {"summary": block}
    keep = ("total_trades", "trade_count_long", "trade_count_short", "profit_total",
            "profit_total_abs", "cagr", "sharpe", "sortino", "calmar", "sqn", "profit_factor",
            "expectancy", "expectancy_ratio", "winrate", "wins", "losses", "draws",
            "max_drawdown_account", "max_drawdown_abs", "market_change", "starting_balance",
            "final_balance", "trades_per_day")
    rows = []
    for strategy, record in accepted.items():
        row = {field: record["summary"].get(field) for field in keep}
        row["strategy_id"] = strategy
        rows.append(row)
    return rows, len(rejected)


def discovery_benchmark(robustness):
    """Dollar gain and Freqtrade's own metrics of the discovery window, on the 5m basis
    (`regime/discovery_benchmark.py`): a strategy above 5m takes its 5m detail run, every other one its
    baseline, and a strategy above 5m without a finished 5m run has no row."""
    totals = pd.read_csv(os.path.join(SPEC, "discovery_total_dollar_gain.csv"))
    native = pd.read_csv(os.path.join(SPEC, "discovery_native_stats.csv"))

    def wanted(frame):
        keep = []
        for sid, source in zip(frame["strategy_id"], frame["source"]):
            minutes = robustness.timeframe(sid)[1]
            keep.append(source == "detail_5m" if minutes > 5 else source == "baseline")
        return frame[keep]

    totals, native = wanted(totals), wanted(native)
    gain_rows = []
    for record in totals.sort_values("dollar_gain_usd", ascending=False).to_dict(orient="records"):
        tf, minutes = robustness.timeframe(record["strategy_id"])
        gain_rows.append({"strategy_id": record["strategy_id"], "tf": tf, "tfm": minutes,
                          "trades": int(record["trades"]),
                          "dollar_gain_usd": round(float(record["dollar_gain_usd"]), 2),
                          "benchmark_dollar_gain_usd": _round_or_none(record["benchmark_dollar_gain_usd"], 2),
                          "excess_dollar_gain_usd": _round_or_none(record["excess_dollar_gain_usd"], 2)})
    for rank, row in enumerate(gain_rows, 1):
        row["rk"] = rank
    ft_rows = []
    for record in native.to_dict(orient="records"):
        row = {k: (None if isinstance(v, float) and math.isnan(v) else v) for k, v in record.items() if k != "source"}
        row["tf"], row["tfm"] = robustness.timeframe(row["strategy_id"])
        ft_rows.append(row)
    return gain_rows, ft_rows


def _round_or_none(value, digits):
    return None if pd.isna(value) else round(float(value), digits)


def discovery_blobs(robustness, confirm, frame, summary):
    """Discovery against validation on the 5m basis (regime/discovery_comparison.py), for the page.

    The scatter carries one point per strategy, kind and phase that clears the floor in
    both windows: [kind, phase, discovery excess, validation excess, robustness PASS].
    The top-five table lists, per phase, the best coin rows of the discovery and what
    those rows did in the validation.
    """
    scatter = []
    both = frame[frame["floor_disc"] & frame["floor_val"]]
    for _, row in both.iterrows():
        ok = robustness.row(row["strategy_id"], row["kind"], row["regime"])["ok"]
        scatter.append([0 if row["kind"] == "btc" else 1, STATES.index(row["regime"]),
                        round(float(row["excess_return_disc"]), 4),
                        round(float(row["excess_return_val"]), 4), ok])
    top = {"btc": {}, "coin": {}}
    for kind in ("btc", "coin"):
        for state in STATES:
            part = frame[(frame["kind"] == kind) & (frame["regime"] == state)]
            val = part[part["floor_val"]].sort_values("excess_return_val", ascending=False)
            rank = {s: i + 1 for i, s in enumerate(val["strategy_id"])}
            best = part[part["floor_disc"]].sort_values("excess_return_disc", ascending=False).head(5)
            rows = []
            for _, row in best.iterrows():
                on_floor = bool(row["floor_val"])
                rows.append({
                    "strategy_id": row["strategy_id"],
                    "disc_excess": clean(row["excess_return_disc"]),
                    "disc_trades": int(row["trades_disc"]), "disc_episodes": int(row["episodes_disc"]),
                    "val_excess": clean(row["excess_return_val"]) if on_floor else None,
                    "val_rank": rank.get(row["strategy_id"]) if on_floor else None,
                    "val_rows": len(val),
                    "val_trades": None if pd.isna(row["trades_val"]) else int(row["trades_val"]),
                    "val_episodes": None if pd.isna(row["episodes_val"]) else int(row["episodes_val"]),
                    "ok": robustness.row(row["strategy_id"], kind, state)["ok"]})
                cf, sc = confirm.get((kind, row["strategy_id"], state), (0, None))
                rows[-1]["cf"], rows[-1]["sc"] = cf, sc
            top[kind][state] = rows
    return scatter, top, summary


def top10_annotation(robustness, confirm):
    """Robustness and confirmation of the Model 0 rows behind the gating page's top-10 selection."""
    with io.open(os.path.join(DATA, "top10byregime.json"), encoding="utf-8") as handle:
        selection = json.load(handle)
    out = {}
    for state, block in selection.items():
        for candidate in block["candidates"]:
            sid = candidate["strategy_id"]
            row = robustness.row(sid, "coin", state)
            cf, sc = confirm.get(("coin", sid, state), (0, None))
            out["%s|%s" % (sid, state)] = {"ok": row["ok"], "xs": row["xs"], "cf": cf, "sc": sc}
    return out


def recovery_5m_strategies():
    """Strategies whose accepted baseline is an owner-approved 5m rerun of a 1m strategy (marked with a dagger)."""
    manifest = _read_json(os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json"))["results"]
    return sorted(s for s, r in manifest.items() if _run_verdict(r.get("status")) == "MEASURED"
                  and r.get("measurement_scope") == "owner_approved_timeframe_5m_recovery_pooled_pair_universe")


def dca_strategies():
    enable = re.compile(r"position_adjustment_enable\s*=\s*True\b")
    method = re.compile(r"def\s+adjust_trade_position\s*\(")
    found = []
    with io.open(STATUS, newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            path = os.path.join(ROOT, row.get("source_file") or "")
            if not row.get("source_file") or not os.path.isfile(path):
                continue
            text = io.open(path, encoding="utf-8", errors="replace").read()
            if enable.search(text) and method.search(text):
                found.append(row["strategy_id"])
    return sorted(found)


def forced_exits():
    frame = pd.read_csv(TRADES, usecols=["exit_reason"])
    return int(frame["exit_reason"].isin(["liquidation", "force_exit"]).sum())


# ------------------------------------------------------------------ facts and text
def window_facts(summary):
    """The two analysis windows, from the constants the evaluation itself uses."""
    from regime import attribution, specialist_evaluation
    day = pd.Timedelta(days=1)
    disc_start = attribution.START
    disc_end = specialist_evaluation.VALIDATION_START - day
    val_start = specialist_evaluation.VALIDATION_START
    val_end = attribution.END - day

    def iso(ts):
        return ts.strftime("%Y-%m-%d")

    def code(value):
        return "%s-%s-%s" % (value[:4], value[4:6], value[6:8])

    bt = profile_full_window.TIMERANGE
    return {"disc_start": iso(disc_start), "disc_end": iso(disc_end),
            "val_start": iso(val_start), "val_end": iso(val_end),
            "disc_days": de_int((disc_end - disc_start).days + 1),
            "val_days": de_int((val_end - val_start).days + 1),
            "disc_trades": de_int(summary["discovery_trades"]),
            "val_trades": de_int(summary["validation_trades"]),
            "bt_spot": code(bt["spot"].split("-")[0]), "bt_futures": code(bt["futures"].split("-")[0])}


def detail_check_text():
    """The 5m totals are priced by the evaluation's own code; say so only while the check passes."""
    import contextlib
    from regime import detail_totals
    with contextlib.redirect_stdout(io.StringIO()):
        ok = detail_totals.check()
    if not ok:
        return ('<b>Warning:</b> the cross-check (<code class="mono">regime/detail_totals.py --check</code>) no longer '
                'matches the rankings; the 5m figures are not reliable.')
    return ('The calculation was cross-checked against base archives: the same functions reproduce the figures of the '
            'author-timeframe run to the digit (<code class="mono">regime/detail_totals.py --check</code>).')


def facts_and_text(btc, coin, universal, gain, native, rejected, robustness, futures, dca, rows, summary, total):
    manifest = _read_json(os.path.join(SPEC, "evaluation_manifest.json"))
    attribution = _read_json(ATTRIBUTION)
    pooled = _read_json(POOLED)["results"]
    evaluated = set(manifest["strategies_evaluated"])
    n_eval = len(evaluated)
    n_eligible = attribution["eligible_profiles"]
    assert n_eval == attribution["attributed_profiles"], "evaluation and attribution disagree"
    missing = attribution["missing_strategies"]
    by_status = {}
    for strategy in missing:
        status = (pooled.get(strategy) or {}).get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    assert len(missing) == n_eligible - n_eval

    val_btc = btc[btc["tier"] == "VALIDATION"]
    val_coin = coin[coin["tier"] == "VALIDATION"]
    counts = [len(val_btc[val_btc["btc_regime"] == s]) for s in STATES] + \
             [len(val_coin[val_coin["coin_regime"] == s]) for s in STATES]
    n_universal = len(universal)
    consistent = universal[universal["regime_consistency"] == 1.0]
    n_cons = len(consistent)
    n_floor_coin = val_coin["strategy_id"].nunique()
    n_gain = len(gain)
    weakest_bull = universal[universal["worst_regime"] == "BULL"]

    with io.open(STATUS, newline="", encoding="utf-8-sig") as handle:
        marker = sum(1 for r in csv.DictReader(handle) if "grid_dca" in (r.get("strategy_type") or ""))
    ft_profitable = sum(1 for r in native if (r.get("profit_total") or 0) > 0)
    measured = sum(1 for s, r in pooled.items() if _run_verdict(r.get("status")) == "MEASURED"
                   and r.get("measurement_scope") in er.ACCEPTED_BASELINE_SCOPES)
    verified_btc = sum(r["ok"] for r in rows["btc"])
    verified_coin = sum(r["ok"] for r in rows["coin"])
    verified_universal = sum(r["ok"] for r in rows["universal"])
    confirmed_btc = sum(1 for r in rows["btc"] if r["cf"] == 2)
    confirmed_coin = sum(1 for r in rows["coin"] if r["cf"] == 2)
    univ_strict = sum(1 for r in rows["universal"] if r["ur"] == 2)
    univ_mild = sum(1 for r in rows["universal"] if r["ur"] == 1)
    pending = sum(1 for s in evaluated if _robustness_verdict(robustness.status(s)) == "SKIP")
    sensitive = sum(1 for s in evaluated if _robustness_verdict(robustness.status(s)) == "FOUND")
    # Deliberately raw, not `_robustness_verdict`: a classification ERROR and a
    # plain `NA` both normalize to `NA`, so the mapped comparison would absorb
    # the 673 rows that were never classified into the failure count.
    failed = sum(1 for s in evaluated if robustness.status(s) == "ERROR")
    run_state = ("for %d the 5m run is still pending (timeframe above 5m)" % pending if pending
                 else "all 5m runs are finished")
    if failed:
        run_state += ", for %d it failed or hit the 3600 s time limit" % failed

    def pct(part, whole):
        return de_pct(100.0 * part / whole)

    def width(part, whole):
        return "%.1f" % (100.0 * part / whole)

    trades = attribution["trades"]
    facts = {
        "n_eval": n_eval, "n_eligible": n_eligible, "n_not_measured": len(missing),
        "n_oom": by_status.get("oom_confirmed", 0), "n_perf": by_status.get("performance_limited", 0),
        "n_stake": by_status.get("stake_overflow_confirmed", 0),
        "trades_total": de_int(trades), "trades_mio": "%.2f" % (trades / 1e6),
        "n_forced_exits": de_int(forced_exits()),
        "rows_btc": de_int(len(val_btc)), "rows_coin": de_int(len(val_coin)),
        "cand_range": "%d-%d" % (min(counts), max(counts)),
        "n_universal": n_universal, "n_consistent": n_cons,
        "n_gain_rows": n_gain,
        "n_gain_pos": int((gain["dollar_gain_usd"] > 0).sum()),
        "n_gain_beat": int((gain["excess_dollar_gain_usd"] > 0).sum()),
        "med_gain": ("&minus;" if gain["dollar_gain_usd"].median() < 0 else "") + "$%d" % round(abs(gain["dollar_gain_usd"].median())),
        "med_excess": ("&minus;" if gain["excess_dollar_gain_usd"].median() < 0 else "") + "$%d" % round(abs(gain["excess_dollar_gain_usd"].median())),
        "n_floor_coin": n_floor_coin,
        "n_futures_eval": len(evaluated & set(futures)),
        "n_dca_eval": len(evaluated & set(dca)),
        "n_dca_universal": len(set(universal["strategy_id"]) & set(dca)),
        "n_dca_marker": marker, "n_dca_verified": len(dca),
        "pct_eval": pct(n_eval, n_eligible), "w_eval": width(n_eval, n_eligible),
        "pct_gain": pct(n_gain, n_eligible), "w_gain": width(n_gain, n_eligible),
        "pct_floor": pct(n_floor_coin, n_eligible), "w_floor": width(n_floor_coin, n_eligible),
        "pct_universal": pct(n_universal, n_eligible), "w_universal": width(n_universal, n_eligible),
        "pct_consistent": pct(n_cons, n_eligible), "w_consistent": width(n_cons, n_eligible),
        "drop_no_validation": n_eval - n_gain,
        "drop_exploratory": n_gain - n_floor_coin,
        "drop_exploratory_word": WORDS.get(n_gain - n_floor_coin, "%d times" % (n_gain - n_floor_coin)),
        "drop_not_universal": n_floor_coin - n_universal,
        "drop_not_consistent": n_universal - n_cons,
        "n_uptrend_weakest": len(weakest_bull),
        "pct_uptrend_weakest": de_pct(100.0 * len(weakest_bull) / n_universal, 1),
        "n_ft_profitable": ft_profitable, "pct_ft_profitable": pct(ft_profitable, len(native)),
        "n_measured_baselines": measured,
        "n_verified_rows_btc": verified_btc, "n_verified_rows_coin": verified_coin,
        "n_verified_universal": verified_universal,
        "n_conf_btc": confirmed_btc, "n_conf_coin": confirmed_coin,
        "n_univ_strict": univ_strict, "n_univ_mild": univ_mild,
        "n_consistent_word": COUNT_WORDS.get(n_cons, str(n_cons)),
        "tbl_btc": de_int(len(btc)), "tbl_coin": de_int(len(coin)),
        # Stamped at generation, always: a page that carries an old date reads as current.
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "n_d5": sum(1 for r in total if r.get("d_trades") is not None),
        "gating_url": GATING_URL, "main_url": MAIN_URL, "benchmark_url": BENCHMARK_URL,
        "daily_target": de_pct(100 * DAILY_TARGET, 2), "pf_min_trades": PORTFOLIO_MIN_TRADES,
        "d5_check": detail_check_text(),
    }
    facts.update(window_facts(summary))
    contradictions = int(((btc["dollar_gain_usd"] > btc["benchmark_dollar_gain_usd"]) & (btc["excess_return"] < 0)).sum()
                         + ((coin["dollar_gain_usd"] > coin["benchmark_dollar_gain_usd"]) & (coin["excess_return"] < 0)).sum())
    facts["contradiction_text"] = ("not a single time any more" if contradictions == 0
                                   else "%d times" % contradictions)

    # -- claims that hold only while the data shows them ---------------------
    ids = consistent["strategy_id"].tolist()
    all_ft = bool(ids) and all(i.startswith("FastSupertrend") for i in ids)
    all_transition = bool(ids) and bool((consistent["worst_regime"] == "TRANSITION").all())
    count_word = COUNT_WORDS.get(n_cons, str(n_cons))
    rest = n_universal - n_cons
    intro = ("The strongest subset of the %d universal candidates: not a single one of the four coin regimes with "
             "a negative excess return. Against the phase-wise, episode-weighted benchmark, %d of %d (%s) manage "
             "that" % (n_universal, n_cons, n_universal, de_pct(100.0 * n_cons / n_universal, 1)))
    if all_ft and all_transition:
        intro += (" &mdash; all %s are variants of <code class=\"mono\">FastSupertrend</code>, and for all "
                  "%s it is not ADX Uptrend but ADX Transition that is the (barely positive) weakest regime."
                  % (count_word, count_word))
    else:
        intro += ": " + ", ".join("<code class=\"mono\">%s</code>" % i for i in ids) + "."
    intro += (" For the remaining %d the reason stays documented above: ADX Uptrend turns negative for them almost "
              "everywhere." % rest)
    text = {"consistent_intro": intro, "lcb_example": lcb_example(coin)}

    best = weakest_bull.sort_values("median_regime_excess_return", ascending=False).head(1)
    if len(best):
        row = best.iloc[0]
        text["uptrend_anecdote"] = (
            "Among the candidates for which ADX Uptrend really stays the weakest regime, even the best one by median "
            "excess return, <code class=\"mono\">%s</code> (consistency %s, median excess %s), is on average %s "
            "percentage points %s buy-and-hold in ADX Uptrend."
            % (row["strategy_id"], "%.2f" % row["regime_consistency"],
               de_pct(100 * row["median_regime_excess_return"], 1),
               "%.1f" % abs(100 * row["worst_regime_return"]),
               "behind" if row["worst_regime_return"] < 0 else "ahead of"))
    else:
        text["uptrend_anecdote"] = ""

    ft_tail = ("%d strategies are shown: %d with a 5m detail run, %d with a baseline run at or below 5m "
               "(identity-checked native archive hit, the same check as in the Model 0/1/2/3 comparison; %d baseline "
               "strategies could not be matched)."
               % (len(native), sum(1 for r in native if r.get("tfm", 0) > 5),
                  sum(1 for r in native if r.get("tfm", 0) <= 5), rejected))
    text["ft_intro_tail"] = ft_tail

    bull_lcb = sorted(val_coin[(val_coin["coin_regime"] == "BULL") & (val_coin["episode_excess_lcb"] > 0)]["strategy_id"])
    text["uptrend_recount"] = (
        "Recalculated on 2026-09-20 (%d strategies): %d %s an edge in ADX Uptrend with "
        "<code class=\"mono\">episode_excess_lcb &gt; 0</code>: %s. The selection for Models 1-3 stays as of "
        "15.09., because the gated runs are based on it."
        % (n_eval, len(bull_lcb), "has" if len(bull_lcb) == 1 else "have",
           ", ".join("<code class=\"mono\">%s</code>" % s for s in bull_lcb) or "none"))

    text["callout_recalc"] = (
        '<div class="callout warn"><span class="dot">&#9888;</span><div><b>Recalculated on 2026-09-20.</b> '
        'Four duplicates deleted at intake (<code class="mono">chispei</code>, <code class="mono">MyStratV1</code>, '
        '<code class="mono">Combined_NFIv7_SMA_bAdBoY_20211204</code>, <code class="mono">Combined_NFIv7_SMA_Rallipanos_20210707</code>) '
        'are removed from all result stores; until then <code class="mono">MyStratV1</code> stood next to its representative with four phase '
        'entries each in both rankings. At the same time the evaluation now includes every full-window run measured since 15.09. '
        '(%d instead of 584 strategies). The figures therefore differ from the version of 15.09., and the '
        'difference comes mostly from the newly measured strategies, not from removing the duplicates. '
        'The section on Model 1-3 with the top-10 selection is in its own artifact, Gating hypothesis; it is a '
        'snapshot of the gated runs and was not recalculated.</div></div>'
        % n_eval)
    text["callout_robust"] = (
        '<div class="callout info"><span class="dot">&#8505;</span><div><b>Robustness (stage 8b), in every table with market-phase results.</b> '
        'A specialist counts as <i>verified</i> only if the strategy passes the 5m detail run and the profit in the '
        '<i>claimed</i> ADX state survives an additional slippage of 0.1 %% per side (validation window, '
        'at least 10 trades in that state). For strategies up to 5m the run is not needed; by the owner\'s decision they count as '
        'passed, which is a rule and not a measurement. The column changes no ranking. '
        'State: %d of the %d strategies are <code class="mono">sensitive</code> in the 5m run, %s. <b>Rank and robustness are separate statements:</b> a rank 1 without PASS is only the best '
        'value of a strategy in this phase, not a verified specialist.</div></div>'
        % (sensitive, n_eval, run_state))
    return facts, text, manifest


    return facts, text, manifest


def lcb_example(coin):
    """Two real rows that show what the lower confidence bound does: a high mean over few
    episodes whose bound is below 0, and a smaller mean over many episodes whose bound is
    above 0."""
    val = coin[coin["tier"] == "VALIDATION"].dropna(subset=["episode_excess_lcb"])
    few = val[(val["episodes"].between(5, 15)) & (val["excess_return"] > 0.05) & (val["episode_excess_lcb"] < 0)]
    if few.empty:
        return ""
    a = few.sort_values("excess_return", ascending=False).iloc[0]
    many = val[(val["episodes"] >= 30) & (val["episode_excess_lcb"] > 0) & (val["excess_return"] < a["excess_return"])]
    if many.empty:
        return ""
    b = many.sort_values("episode_excess_lcb", ascending=False).iloc[0]

    def pct(v):
        return ("&minus;" if v < 0 else "+") + ("%.1f" % abs(100 * v)) + "&nbsp;%"

    def label(r):
        return '<code class="mono">%s</code> in %s' % (r["strategy_id"], {
            "BULL": "ADX Uptrend", "BEAR": "ADX Downtrend", "SIDEWAYS": "ADX Sideways",
            "TRANSITION": "ADX Transition"}[r["coin_regime"]])

    return ('<p style="margin:8px 0 0;max-width:none;"><b>Example from the data.</b> %s: mean excess %s, but only %d '
            'episodes, the lower bound is at %s. The lead may be chance. %s: mean excess only %s, but %d '
            'episodes, the lower bound is at %s. This lead is reliable. The mean alone would have put the two '
            'in the wrong order.</p>'
            % (label(a), pct(a["excess_return"]), int(a["episodes"]), pct(a["episode_excess_lcb"]),
               label(b), pct(b["excess_return"]), int(b["episodes"]), pct(b["episode_excess_lcb"])))


def fill(template, facts, text):
    mapping = {k: str(v) for k, v in facts.items()}
    mapping.update(text)
    missing = sorted(set(re.findall(r"\{\{([a-z_0-9]+)\}\}", template)) - set(mapping))
    assert not missing, "template asks for facts that were not computed: %s" % ", ".join(missing)
    return re.sub(r"\{\{([a-z_0-9]+)\}\}", lambda m: mapping[m.group(1)], template)


def render(template_path, facts, text, blobs):
    """The page as a string. Never writes, so `--check` can compare it."""
    template = io.open(template_path, encoding="utf-8").read()
    template = fill(template, facts, text)
    for marker, path in (("/*__COMMON_CSS__*/", COMMON_CSS), ("/*__COMMON_JS__*/", COMMON_JS)):
        assert template.count(marker) == 1, marker
        template = template.replace(marker, io.open(path, encoding="utf-8").read())
    for name, payload in blobs.items():
        token = "__%s_JSON__" % name
        assert template.count(token) <= 1, token
        template = template.replace(token, payload)
    left = re.findall(r"__[A-Z0-9]+_JSON__", template)
    assert not left, "blobs the template asks for were not supplied: %s" % ", ".join(sorted(set(left)))
    assert len(re.findall(r"<section[ >]", template)) == template.count("</section>")
    return template


def render_page(template_path, destination, facts, text, blobs):
    page = render(template_path, facts, text, blobs)
    with io.open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(page)
    return page


def rendered_pages(skip_native=False):
    """Both pages as strings, plus the facts behind them. Never writes.

    `--check` compares these against the files on disk and the writer below
    uses the same function, so a check can never disagree with a build - the
    same split `tools.strategy_status_page` uses.
    """
    robustness = Robustness()
    author = {"btc": pd.read_csv(os.path.join(SPEC, "btc_specialist_table.csv")),
              "coin": pd.read_csv(os.path.join(SPEC, "coin_specialist_table.csv")),
              "gain": pd.read_csv(os.path.join(SPEC, "strategy_total_dollar_gain.csv"))}
    effective, above = five_minute_basis(robustness, author, None)
    btc, coin, gain = effective["btc"], effective["coin"], effective["gain"]
    from regime import specialist_evaluation as se
    universal = se.universal_table(coin)

    pairs, dc = discovery_basis(above)
    summary = dc.summarize(pairs)
    confirmation = dc.universal_confirmation(pairs, universal["strategy_id"])
    summary["confirmation"] = {
        "confirmed_rows": {kind: int(pairs[(pairs["kind"] == kind) & pairs["confirmed"]].shape[0])
                           for kind in ("btc", "coin")},
        "universal": {rule: int((confirmation["rule"] == rule).sum()) for rule in ("strict", "mild", "none")}}
    both_kind = pairs[pairs["kind"] == "btc"]
    summary["discovery_trades"] = int(both_kind["trades_disc"].sum())
    summary["validation_trades"] = int(both_kind["trades_val"].sum())

    confirm, uconfirm = confirmation_lookups(pairs, confirmation)
    daily_phase, daily_total = daily_lookup(robustness)
    detail = detail_lookup()
    rows = {"btc": regime_rows(btc, "btc_regime", "btc", robustness, confirm, daily_phase, detail),
            "coin": regime_rows(coin, "coin_regime", "coin", robustness, confirm, daily_phase, detail),
            "universal": universal_rows(universal, coin, robustness, uconfirm, detail)}
    gain_rows = total_rows(gain, robustness, uconfirm, daily_total, pairs, author["gain"])
    plan = portfolio(rows["coin"], buy_hold_daily())
    if skip_native:
        native, rejected = [], 0
    else:
        native, rejected = native_stats(gain["strategy_id"], robustness)
        for r in native:
            r["tf"], r["tfm"] = robustness.timeframe(r["strategy_id"])

    profiles = pd.read_csv(PROFILES, usecols=["strategy_id", "run_profile"])
    futures = sorted(profiles.loc[profiles["run_profile"].str.startswith("futures_", na=False),
                                  "strategy_id"].unique().tolist())
    dca = dca_strategies()

    dv_scatter, dv_top, dv_summary = discovery_blobs(robustness, confirm, pairs, summary)
    facts, text, _ = facts_and_text(btc, coin, universal, gain, native or [{}], rejected,
                                    robustness, futures, dca, rows, dv_summary, gain_rows)
    static = {name: io.open(os.path.join(DATA, name.lower() + ".json"), encoding="utf-8").read().strip()
              for name in ("GATEDCOMPARE", "GATEDDETAIL", "TOP10BYREGIME", "COINEPISODES", "COINEPISODECOUNTS")}
    # Keyed the same way FUTURES/DCA/REC5 are (bare strategy_id; Modell 1/2/3
    # candidate_ids strip their gate-variant suffix via baseStrategyId before
    # lookup), so one map covers every table on both pages through futuresLabel.
    repo_map = {sid: row["repo"] for sid, row in robustness.table.items() if row.get("repo")}
    shared = {"FUTURESSTRATEGIES": _dump(futures), "DCASTRATEGIES": _dump(dca),
              "RECOVERY5MSTRATEGIES": _dump(recovery_5m_strategies()), "REPOMAP": _dump(repo_map)}
    main_blobs = {
        "REGIMEFULL": _dump({"btc": rows["btc"], "coin": rows["coin"]}),
        "UNIVERSAL": _dump(rows["universal"]), "PORTFOLIO": _dump(plan),
        "DVSCATTER": _dump(dv_scatter), "DVTOP": _dump(dv_top), "DVSUMMARY": _dump(dv_summary),
        "COINEPISODES": static["COINEPISODES"],
        "COINEPISODECOUNTS": static["COINEPISODECOUNTS"]}
    main_blobs.update(shared)
    gating_blobs = {"GATEDCOMPARE": static["GATEDCOMPARE"], "GATEDDETAIL": static["GATEDDETAIL"],
                    "TOP10BYREGIME": static["TOP10BYREGIME"],
                    "TOP10ANNOT": _dump(top10_annotation(robustness, confirm))}
    gating_blobs.update(shared)
    disc_gain, disc_ft = discovery_benchmark(robustness)
    facts.update(n_disc_gain=len(disc_gain), n_disc_pos=sum(1 for r in disc_gain if r["dollar_gain_usd"] > 0),
                 n_disc_ft=len(disc_ft))
    benchmark_blobs = {"TOTALGAIN": _dump(gain_rows), "FTSTATS": _dump(native), "DAILYTARGET": _dump(DAILY_TARGET),
                       "DISCGAIN": _dump(disc_gain), "DISCFT": _dump(disc_ft)}
    benchmark_blobs.update(shared)
    return (facts,
            render(TEMPLATE, facts, text, main_blobs),
            render(GATING_TEMPLATE, facts, text, gating_blobs),
            render(BENCHMARK_TEMPLATE, facts, text, benchmark_blobs))


def build(destination, gating_destination, benchmark_destination, skip_native=False):
    facts, main_page, gating_page, benchmark_page = rendered_pages(skip_native)
    for path, page in ((destination, main_page), (gating_destination, gating_page),
                       (benchmark_destination, benchmark_page)):
        with io.open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(page)
    return facts


RX_STAMP = re.compile(r"(Stand |As of )\d{4}-\d\d-\d\d \d\d:\d\d")


def _without_stamp(content):
    """Blank the build stamp in the page header.

    Both pages name the moment they were built (`Stand {{generated}}` in their
    eyebrow), so a fresh render differs from the file on disk a minute later.
    Blanking that one stamp keeps the rest of the comparison byte-strict. The
    failure this guards against is a page whose tables have moved on while the
    page still reads as the current snapshot - the same defect found in
    `strategy_status.html` on 2026-09-23, where the committed page carried
    `last_tested_at` values two hours behind the CSV it renders from, and the
    two published regime pages had no way to notice it at all.
    """
    return RX_STAMP.sub(r"\g<1><stamp>", content)


def selftest():
    # If the pattern stopped matching the eyebrow, `--check` would silently
    # become byte-exact and report both pages stale the minute after every
    # build; if it matched more than the eyebrow, a real content change could
    # hide behind a blanked field. Both directions are asserted here.
    for template, marker in ((TEMPLATE, "As of {{generated}}"), (GATING_TEMPLATE, "Stand {{generated}}"),
                              (BENCHMARK_TEMPLATE, "As of {{generated}}")):
        assert marker in io.open(template, encoding="utf-8").read(), template
    sample = 'class="eyebrow">Specialist / universal evaluation &middot; As of 2026-09-23 21:56</div>'
    assert len(RX_STAMP.findall(sample)) == 1, "the stamp pattern does not match the eyebrow"
    assert _without_stamp(sample) == _without_stamp(sample.replace("21:56", "22:04")), \
        "a rebuilt page would read as stale"
    assert _without_stamp(sample) != _without_stamp(sample.replace("Specialist", "Gating")), \
        "a content change would hide behind the blanked stamp"
    # Dates that are content rather than the build stamp - an "as of" column,
    # a timerange - must survive the blanking untouched.
    for content in ("| 2026-09-02 | 16:13 |", "20200401-20260821", "Stand der Daten", "As of the data"):
        assert _without_stamp(content) == content, content
    print("regime_specialists_page selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=os.path.join(ROOT, "regime_specialists.html"))
    parser.add_argument("--gating-out", default=os.path.join(ROOT, "regime_gating.html"))
    parser.add_argument("--benchmark-out", default=os.path.join(ROOT, "validation_benchmark.html"))
    parser.add_argument("--skip-native", action="store_true",
                        help="leave the Freqtrade-native block empty (fast, for layout work)")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--check", action="store_true",
                        help="fail when either page no longer matches its own data "
                             "(costs one build, about a minute: it renders both pages, "
                             "most of that in the Model-0 native block)")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if args.check:
        if args.skip_native:
            parser.error("--check cannot be combined with --skip-native: the native "
                         "block is part of the page being compared")
        _facts, main_page, gating_page, benchmark_page = rendered_pages()
        stale = []
        for path, fresh in ((args.out, main_page), (args.gating_out, gating_page),
                            (args.benchmark_out, benchmark_page)):
            if not os.path.exists(path):
                stale.append(os.path.relpath(path, ROOT))
                continue
            if _without_stamp(io.open(path, encoding="utf-8").read()) != _without_stamp(fresh):
                stale.append(os.path.relpath(path, ROOT))
        if stale:
            print("stale: %s" % ", ".join(stale))
            return 1
        print("regime pages: current")
        return 0
    facts = build(args.out, args.gating_out, args.benchmark_out, args.skip_native)
    for path in (args.out, args.gating_out, args.benchmark_out):
        print("built %s (%.1f KB)" % (path, os.path.getsize(path) / 1024.0))
    for key in ("n_eval", "n_eligible", "n_universal", "n_consistent", "n_verified_rows_btc",
                "n_verified_rows_coin", "n_verified_universal"):
        print("  %-22s %s" % (key, facts[key]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
