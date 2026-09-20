# -*- coding: utf-8 -*-
"""Build the "Regime-Spezialisten" page from the Model 0 evaluation.

The page used to be assembled by hand from exports kept outside the repository, so it
went stale the moment the evaluation was rerun. This puts one command between the two:

    ./ftenv/Scripts/python.exe -m tools.regime_specialists_page

It reads `results/regime/specialist_evaluation/` (Model 0), the Stage 8b stores
(`evidence/EXECUTION_ROBUSTNESS.json`, `evidence/COST_SCREEN.json`) and writes
`regime_specialists.html` at the repository root. Every number in the running text is
computed here and filled into `{{token}}` slots of `tools/REGIME_SPECIALISTS.template.html`;
a claim that depends on the result (that the fully consistent candidates are all
FastSupertrend variants, for one) is written only when the data still shows it.

It also writes `regime_gating.html`, the second page: the Model 1/2/3 sections and the top-10
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
import json
import os
import re
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evidence import execution_robustness as er, profile_full_window  # noqa: E402

SPEC = os.path.join(ROOT, "results", "regime", "specialist_evaluation")
DATA = os.path.join(ROOT, "tools", "regime_specialists_data")
TEMPLATE = os.path.join(ROOT, "tools", "REGIME_SPECIALISTS.template.html")
GATING_TEMPLATE = os.path.join(ROOT, "tools", "REGIME_GATING.template.html")
COMMON_CSS = os.path.join(ROOT, "tools", "regime_pages_common.css")
COMMON_JS = os.path.join(ROOT, "tools", "regime_pages_common.js")
DETAIL_TOTALS = os.path.join(SPEC, "detail_5m_total_dollar_gain.csv")
# The two artifacts link to each other. The gating page is published first; its address goes here.
MAIN_URL = "https://claude.ai/artifact/6PoC2NwYCruR6UoJ81Bgia"
GATING_URL = "https://claude.ai/artifact/LjAu8PjEDrZXdK8vnAbcZM"
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
PROFILES = os.path.join(ROOT, "evidence", "EXECUTION_PROFILES.csv")
POOLED = os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json")
ATTRIBUTION = os.path.join(ROOT, "results", "regime", "attribution_manifest.json")
TRADES = os.path.join(ROOT, "results", "regime", "trade_regime_attribution.csv")

STATES = ["BULL", "BEAR", "SIDEWAYS", "TRANSITION"]
WORDS = {0: "keinmal", 1: "einmal", 2: "zweimal", 3: "dreimal", 4: "viermal", 5: "fünfmal",
         6: "sechsmal", 7: "siebenmal", 8: "achtmal", 9: "neunmal", 10: "zehnmal",
         11: "elfmal", 12: "zwölfmal", 13: "dreizehnmal", 14: "vierzehnmal",
         15: "fünfzehnmal", 16: "sechzehnmal", 17: "siebzehnmal", 18: "achtzehnmal",
         19: "neunzehnmal", 20: "zwanzigmal"}
COUNT_WORDS = {2: "zwei", 3: "drei", 4: "vier", 5: "fünf", 6: "sechs", 7: "sieben", 8: "acht",
               9: "neun", 10: "zehn"}


def clean(value):
    if isinstance(value, float) and pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def de_int(n):
    return "{:,}".format(int(n)).replace(",", ".")


def de_pct(x, digits=0):
    return ("{:.%df}%%" % digits).format(x).replace(".", ",")


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

    def status(self, strategy):
        return (self.table.get(strategy) or {}).get("execution_robustness_status") or "NA"

    def row(self, strategy, kind, state):
        xs = self.status(strategy)
        ok = xs == "PASS" and er.qualifies_in(self.cost.get(strategy), kind, state)
        return {"xs": xs, "ok": 1 if ok else 0}

    def total(self, strategy):
        """The whole validation window, all states together."""
        xs = self.status(strategy)
        cost = er.validation_total(self.cost.get(strategy), "btc")
        ok = xs == "PASS" and cost["status"] == "PASS"
        record = self.record.get(strategy) or {}
        basis = {er.BASIS_RULE: "rule", er.BASIS_MEASURED: "measured"}.get(record.get("basis"), "")
        return {"xs": xs, "ok": 1 if ok else 0, "cv": cost["status"],
                "cm": cost["mean_profit_pct"], "c10": cost["stressed_pct"],
                "tf": record.get("main_timeframe") or "", "xb": basis}

    def universal(self, strategy):
        xs = self.status(strategy)
        ok = xs == "PASS" and er.qualifies_universal(self.cost.get(strategy), "coin")
        return {"xs": xs, "ok": 1 if ok else 0}


# ------------------------------------------------------------------ confirmation
def confirmation_lookups():
    """Discovery confirmation (regime/discovery_comparison.py) per strategy, kind and phase,
    and per universal candidate. Read, never recomputed here."""
    paired = os.path.join(SPEC, "discovery_vs_validation.csv")
    universal = os.path.join(SPEC, "universal_confirmation.csv")
    if not (os.path.isfile(paired) and os.path.isfile(universal)):
        raise SystemExit("run `python -m regime.discovery_comparison` first")
    frame = pd.read_csv(paired)
    rows = {}
    for r in frame.itertuples(index=False):
        both = bool(r.floor_disc and r.floor_val)
        rows[(r.kind, r.strategy_id, r.regime)] = (
            2 if r.confirmed else (1 if both else 0),
            None if pd.isna(r.confirmation_score) else round(float(r.confirmation_score), 4))
    uni = {}
    for r in pd.read_csv(universal).itertuples(index=False):
        uni[r.strategy_id] = ({"strict": 2, "mild": 1, "none": 0}[r.rule],
                              None if pd.isna(r.score) else round(float(r.score), 4),
                              int(r.phases_better_in_both), int(r.phases_confirmed))
    return rows, uni


def confirmed_phase_counts():
    """Per strategy: in how many coin and BTC phases it is confirmed."""
    frame = pd.read_csv(os.path.join(SPEC, "discovery_vs_validation.csv"))
    done = frame[frame["confirmed"]]
    counts = {}
    for kind in ("coin", "btc"):
        counts[kind] = done[done["kind"] == kind].groupby("strategy_id").size().to_dict()
    return counts


def total_rows(gain, robustness, uconfirm):
    """The whole-window table: author timeframe and 5m rerun side by side, robustness and
    confirmation. The 5m side comes from regime/detail_totals.py, never recomputed here."""
    if not os.path.isfile(DETAIL_TOTALS):
        raise SystemExit("run `python -m regime.detail_totals` first")
    d5 = pd.read_csv(DETAIL_TOTALS).set_index("strategy_id")
    phases = confirmed_phase_counts()
    rows = []
    for rank, row in enumerate(gain.to_dict(orient="records"), start=1):
        sid = row["strategy_id"]
        record = {k: clean(v) for k, v in row.items()}
        record["rk"] = rank
        record.update(robustness.total(sid))
        if sid in d5.index:
            d = d5.loc[sid]
            record.update(d_trades=int(d["trades"]), d_gain=clean(d["dollar_gain_usd"]),
                          d_bench=clean(d["benchmark_dollar_gain_usd"]),
                          d_excess=clean(d["excess_dollar_gain_usd"]),
                          d_cm=clean(d["cost_mean_pct"]), d_c10=clean(d["cost_stressed_pct"]))
        ur, us, up, _ = uconfirm.get(sid, (-1, None, 0, 0))
        cn, bn = phases["coin"].get(sid, 0), phases["btc"].get(sid, 0)
        record.update(ur=ur, us=us, up=up, cn=cn, bn=bn, cq=100 * max(ur, 0) + 10 * cn + bn)
        rows.append(record)
    return rows


# ------------------------------------------------------------------ data exports
def regime_rows(table, regime_col, kind, robustness, confirm):
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
        rows.append(record)
    return rows


DETAIL_COLS = ["trades", "episodes", "dollar_gain_usd", "benchmark_dollar_gain_usd",
               "max_drawdown", "worst_trade", "sortino", "annualized_return", "profit_factor",
               "freqforge_score", "episode_excess_lcb", "lcb_grade"]


def universal_rows(universal, coin, robustness, uconfirm):
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
        rows.append(record)
    return rows


def native_stats(strategy_ids):
    """Freqtrade's own report block for each strategy, through the identity-checked
    lookup that the Model 0/1/2/3 comparison uses."""
    from regime import model_compare
    full = _read_json(str(model_compare.MODEL0))
    _, accepted, rejected = model_compare._load_model0(
        model_compare.MODEL0, set(strategy_ids), full["timerange"])
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


def discovery_blobs(robustness, confirm):
    """Discovery against validation (regime/discovery_comparison.py), for the page.

    The scatter carries one point per strategy, kind and phase that clears the floor in
    both windows: [kind, phase, discovery excess, validation excess, robustness PASS].
    The top-five table lists, per phase, the best coin rows of the discovery and what
    those rows did in the validation.
    """
    paired = os.path.join(SPEC, "discovery_vs_validation.csv")
    summary = os.path.join(SPEC, "discovery_vs_validation_summary.json")
    if not (os.path.isfile(paired) and os.path.isfile(summary)):
        raise SystemExit("run `python -m regime.discovery_comparison` first")
    frame = pd.read_csv(paired)
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
    return scatter, top, _read_json(summary)


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
        return ('<b>Achtung:</b> die Gegenprobe (<code class="mono">regime/detail_totals.py --check</code>) stimmt '
                'nicht mehr mit den Ranglisten überein; die 5m-Zahlen sind nicht belastbar.')
    return ('Die Rechnung wurde an Basis-Archiven gegengeprüft: dieselben Funktionen reproduzieren die Zahlen der '
            'Autor-Timeframe-Seite auf die Stelle genau (<code class="mono">regime/detail_totals.py --check</code>).')


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
    measured = sum(1 for s, r in pooled.items() if r.get("status") == "measured"
                   and r.get("measurement_scope") == er.CANONICAL_SCOPE)
    verified_btc = sum(r["ok"] for r in rows["btc"])
    verified_coin = sum(r["ok"] for r in rows["coin"])
    verified_universal = sum(r["ok"] for r in rows["universal"])
    confirmed_btc = sum(1 for r in rows["btc"] if r["cf"] == 2)
    confirmed_coin = sum(1 for r in rows["coin"] if r["cf"] == 2)
    univ_strict = sum(1 for r in rows["universal"] if r["ur"] == 2)
    univ_mild = sum(1 for r in rows["universal"] if r["ur"] == 1)
    pending = sum(1 for s in evaluated if robustness.status(s) == "PENDING")
    sensitive = sum(1 for s in evaluated if robustness.status(s) == "SENSITIVE")
    failed = sum(1 for s in evaluated if robustness.status(s) == "ERROR")
    run_state = ("bei %d steht der 5m-Lauf noch aus (Timeframe über 5m)" % pending if pending
                 else "alle 5m-Läufe sind abgeschlossen")
    if failed:
        run_state += ", bei %d ist er fehlgeschlagen oder am Zeitlimit von 3600 s gescheitert" % failed

    def pct(part, whole):
        return de_pct(100.0 * part / whole)

    def width(part, whole):
        return "%.1f" % (100.0 * part / whole)

    trades = attribution["trades"]
    facts = {
        "n_eval": n_eval, "n_eligible": n_eligible, "n_not_measured": len(missing),
        "n_oom": by_status.get("oom_confirmed", 0), "n_perf": by_status.get("performance_limited", 0),
        "n_stake": by_status.get("stake_overflow_confirmed", 0),
        "trades_total": de_int(trades), "trades_mio": ("%.2f" % (trades / 1e6)).replace(".", ","),
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
        "drop_exploratory_word": WORDS.get(n_gain - n_floor_coin, "%d-mal" % (n_gain - n_floor_coin)),
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
        "gating_url": GATING_URL, "main_url": MAIN_URL,
        "d5_check": detail_check_text(),
    }
    facts.update(window_facts(summary))
    contradictions = int(((btc["dollar_gain_usd"] > btc["benchmark_dollar_gain_usd"]) & (btc["excess_return"] < 0)).sum()
                         + ((coin["dollar_gain_usd"] > coin["benchmark_dollar_gain_usd"]) & (coin["excess_return"] < 0)).sum())
    facts["contradiction_text"] = ("kein einziges Mal mehr" if contradictions == 0
                                   else "%d-mal" % contradictions)

    # -- claims that hold only while the data shows them ---------------------
    ids = consistent["strategy_id"].tolist()
    all_ft = bool(ids) and all(i.startswith("FastSupertrend") for i in ids)
    all_transition = bool(ids) and bool((consistent["worst_regime"] == "TRANSITION").all())
    count_word = COUNT_WORDS.get(n_cons, str(n_cons))
    rest = n_universal - n_cons
    intro = ("Die stärkste Teilmenge der %d Universal-Kandidaten: kein einziges der vier Coin-Regime mit "
             "negativem Excess-Return. Unter dem phasenweiten, episoden-gewichteten Benchmark schaffen "
             "das %d von %d (%s)" % (n_universal, n_cons, n_universal, de_pct(100.0 * n_cons / n_universal, 1)))
    if all_ft and all_transition:
        intro += (" &mdash; alle %s sind Varianten von <code class=\"mono\">FastSupertrend</code>, und bei allen "
                  "%s ist nicht ADX Uptrend, sondern ADX Transition das (knapp positive) schwächste Regime."
                  % (count_word, count_word))
    else:
        intro += ": " + ", ".join("<code class=\"mono\">%s</code>" % i for i in ids) + "."
    intro += (" Für die übrigen %d bleibt der Grund oben belegt: ADX Uptrend kippt bei ihnen fast überall "
              "ins Negative." % rest)
    text = {"consistent_intro": intro, "lcb_example": lcb_example(coin)}

    best = weakest_bull.sort_values("median_regime_excess_return", ascending=False).head(1)
    if len(best):
        row = best.iloc[0]
        text["uptrend_anecdote"] = (
            "Unter den Kandidaten, bei denen ADX Uptrend tatsächlich das schwächste Regime bleibt, liegt "
            "selbst der nach Median-Excess-Return beste, <code class=\"mono\">%s</code> (Konsistenz %s, "
            "Median-Excess %s), in ADX Uptrend im Mittel %s Prozentpunkte %s Buy-and-Hold."
            % (row["strategy_id"], ("%.2f" % row["regime_consistency"]).replace(".", ","),
               de_pct(100 * row["median_regime_excess_return"], 1),
               ("%.1f" % abs(100 * row["worst_regime_return"])).replace(".", ","),
               "hinter" if row["worst_regime_return"] < 0 else "vor"))
    else:
        text["uptrend_anecdote"] = ""

    if rejected:
        ft_tail = ("%d von %d lassen sich zuordnen (identitätsgeprüfter nativer Archiv-Treffer, dieselbe "
                   "Prüfung wie beim Modell-0/1/2/3-Vergleich); %d nicht." % (len(native), n_universal, rejected))
    else:
        ft_tail = ("Alle %d lassen sich zuordnen (identitätsgeprüfter nativer Archiv-Treffer, dieselbe Prüfung "
                   "wie beim Modell-0/1/2/3-Vergleich &mdash; passendes Profil, Archiv-Hash, Zeitraum)." % n_universal)
    ft_tail += (" Stand der Neuberechnung 2026-09-20: %s/%s Strategien im VALIDATION-Tier (je Phase gezählt), %d Universal-Kandidaten."
                % (de_int(len(val_btc)), de_int(len(val_coin)), n_universal))
    text["ft_intro_tail"] = ft_tail

    bull_lcb = sorted(val_coin[(val_coin["coin_regime"] == "BULL") & (val_coin["episode_excess_lcb"] > 0)]["strategy_id"])
    text["uptrend_recount"] = (
        "Neuberechnung 2026-09-20 (%d Strategien): %d %s in ADX Uptrend einen Coin-Edge mit "
        "<code class=\"mono\">episode_excess_lcb &gt; 0</code>: %s. Die Auswahl für Modell 1-3 bleibt der Stand vom "
        "15.09., weil die gegateten Läufe darauf beruhen."
        % (n_eval, len(bull_lcb), "hat" if len(bull_lcb) == 1 else "haben",
           ", ".join("<code class=\"mono\">%s</code>" % s for s in bull_lcb) or "keine"))

    text["callout_recalc"] = (
        '<div class="callout warn"><span class="dot">&#9888;</span><div><b>Neu berechnet am 2026-09-20.</b> '
        'Vier beim Intake gelöschte Duplikate (<code class="mono">chispei</code>, <code class="mono">MyStratV1</code>, '
        '<code class="mono">Combined_NFIv7_SMA_bAdBoY_20211204</code>, <code class="mono">Combined_NFIv7_SMA_Rallipanos_20210707</code>) '
        'sind aus allen Ergebnisspeichern entfernt; <code class="mono">MyStratV1</code> stand bis dahin mit je vier Phasen-Einträgen '
        'in beiden Ranglisten neben seinem Vertreter. Zugleich bezieht die Auswertung jetzt alle seit dem 15.09. gemessenen '
        'Vollfenster-Läufe ein (%d statt 584 Strategien). Die Zahlen weichen deshalb von der Fassung vom 15.09. ab, und die '
        'Abweichung stammt überwiegend aus den neu gemessenen Strategien, nicht aus dem Entfernen der Duplikate. '
        'Der Abschnitt zu Modell 1-3 mit der Top-10-Auswahl steht im eigenen Artefakt Gating-Hypothese; er ist eine '
        'Momentaufnahme der gegateten Läufe und wurde nicht neu gerechnet.</div></div>'
        % n_eval)
    text["callout_robust"] = (
        '<div class="callout info"><span class="dot">&#8505;</span><div><b>Robustheit (Stufe 8b), in jeder Tabelle mit Marktphasen-Ergebnissen.</b> '
        'Ein Spezialist gilt erst als <i>verified</i>, wenn die Strategie den 5m-Detaillauf besteht und der Gewinn im '
        '<i>behaupteten</i> ADX-Zustand einen zusätzlichen Slippage von 0,1 %% je Seite übersteht (Validierungsfenster, '
        'mindestens 10 Trades in diesem Zustand). Bei Strategien bis 5m entfällt der Lauf, sie zählen per Entscheidung des '
        'Eigentümers als bestanden; das ist eine Regel und keine Messung. Die Spalte ändert kein Ranking. '
        'Stand: %d der %d Strategien sind im 5m-Lauf <code class="mono">sensitiv</code>, %s. <b>Rangfolge und Robustheit sind getrennte Aussagen:</b> Ein Rang 1 ohne PASS ist nur der beste '
        'Wert einer Strategie in dieser Phase, kein verifizierter Spezialist.</div></div>'
        % (sensitive, n_eval, run_state))
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
        return ("&minus;" if v < 0 else "+") + ("%.1f" % abs(100 * v)).replace(".", ",") + "&nbsp;%"

    def label(r):
        return '<code class="mono">%s</code> in %s' % (r["strategy_id"], {
            "BULL": "ADX Uptrend", "BEAR": "ADX Downtrend", "SIDEWAYS": "ADX Sideways",
            "TRANSITION": "ADX Transition"}[r["coin_regime"]])

    return ('<p style="margin:8px 0 0;max-width:none;"><b>Beispiel aus den Daten.</b> %s: mittlerer Excess %s, aber nur %d '
            'Episoden, die Untergrenze liegt bei %s. Der Vorsprung kann Zufall sein. %s: mittlerer Excess nur %s, dafür %d '
            'Episoden, die Untergrenze liegt bei %s. Dieser Vorsprung ist belastbar. Der Mittelwert allein hätte die beiden '
            'in die falsche Reihenfolge gebracht.</p>'
            % (label(a), pct(a["excess_return"]), int(a["episodes"]), pct(a["episode_excess_lcb"]),
               label(b), pct(b["excess_return"]), int(b["episodes"]), pct(b["episode_excess_lcb"])))


def fill(template, facts, text):
    mapping = {k: str(v) for k, v in facts.items()}
    mapping.update(text)
    missing = sorted(set(re.findall(r"\{\{([a-z_0-9]+)\}\}", template)) - set(mapping))
    assert not missing, "template asks for facts that were not computed: %s" % ", ".join(missing)
    return re.sub(r"\{\{([a-z_0-9]+)\}\}", lambda m: mapping[m.group(1)], template)


def render_page(template_path, destination, facts, text, blobs):
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
    with io.open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(template)


def build(destination, gating_destination, skip_native=False):
    robustness = Robustness()
    btc = pd.read_csv(os.path.join(SPEC, "btc_specialist_table.csv"))
    coin = pd.read_csv(os.path.join(SPEC, "coin_specialist_table.csv"))
    universal = pd.read_csv(os.path.join(SPEC, "universal_strategies.csv"))
    gain = pd.read_csv(os.path.join(SPEC, "strategy_total_dollar_gain.csv"))

    confirm, uconfirm = confirmation_lookups()
    rows = {"btc": regime_rows(btc, "btc_regime", "btc", robustness, confirm),
            "coin": regime_rows(coin, "coin_regime", "coin", robustness, confirm),
            "universal": universal_rows(universal, coin, robustness, uconfirm)}
    gain_rows = total_rows(gain, robustness, uconfirm)
    if skip_native:
        native, rejected = [], 0
    else:
        native, rejected = native_stats(universal["strategy_id"])

    profiles = pd.read_csv(PROFILES, usecols=["strategy_id", "run_profile"])
    futures = sorted(profiles.loc[profiles["run_profile"].str.startswith("futures_", na=False),
                                  "strategy_id"].unique().tolist())
    dca = dca_strategies()

    dv_scatter, dv_top, dv_summary = discovery_blobs(robustness, confirm)
    facts, text, _ = facts_and_text(btc, coin, universal, gain, native or [{}], rejected,
                                    robustness, futures, dca, rows, dv_summary, gain_rows)
    static = {name: io.open(os.path.join(DATA, name.lower() + ".json"), encoding="utf-8").read().strip()
              for name in ("GATEDCOMPARE", "GATEDDETAIL", "TOP10BYREGIME", "COINEPISODES", "COINEPISODECOUNTS")}
    shared = {"FUTURESSTRATEGIES": _dump(futures), "DCASTRATEGIES": _dump(dca)}
    main_blobs = {
        "REGIMEFULL": _dump({"btc": rows["btc"], "coin": rows["coin"]}),
        "UNIVERSAL": _dump(rows["universal"]), "TOTALGAIN": _dump(gain_rows),
        "DVSCATTER": _dump(dv_scatter), "DVTOP": _dump(dv_top), "DVSUMMARY": _dump(dv_summary),
        "FTSTATS": _dump(native), "COINEPISODES": static["COINEPISODES"],
        "COINEPISODECOUNTS": static["COINEPISODECOUNTS"]}
    main_blobs.update(shared)
    gating_blobs = {"GATEDCOMPARE": static["GATEDCOMPARE"], "GATEDDETAIL": static["GATEDDETAIL"],
                    "TOP10BYREGIME": static["TOP10BYREGIME"],
                    "TOP10ANNOT": _dump(top10_annotation(robustness, confirm))}
    gating_blobs.update(shared)
    render_page(TEMPLATE, destination, facts, text, main_blobs)
    render_page(GATING_TEMPLATE, gating_destination, facts, text, gating_blobs)
    return facts


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=os.path.join(ROOT, "regime_specialists.html"))
    parser.add_argument("--gating-out", default=os.path.join(ROOT, "regime_gating.html"))
    parser.add_argument("--skip-native", action="store_true",
                        help="leave the Freqtrade-native block empty (fast, for layout work)")
    args = parser.parse_args(argv)
    facts = build(args.out, args.gating_out, args.skip_native)
    for path in (args.out, args.gating_out):
        print("built %s (%.1f KB)" % (path, os.path.getsize(path) / 1024.0))
    for key in ("n_eval", "n_eligible", "n_universal", "n_consistent", "n_verified_rows_btc",
                "n_verified_rows_coin", "n_verified_universal"):
        print("  %-22s %s" % (key, facts[key]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
