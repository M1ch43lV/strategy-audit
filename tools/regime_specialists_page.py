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

The Model 1/2/3 sections and the top-10 selection are snapshots of the gated runs and
live as JSON under `tools/regime_specialists_data/`; they are not recomputed here.

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
from evidence import execution_robustness as er  # noqa: E402

SPEC = os.path.join(ROOT, "results", "regime", "specialist_evaluation")
DATA = os.path.join(ROOT, "tools", "regime_specialists_data")
TEMPLATE = os.path.join(ROOT, "tools", "REGIME_SPECIALISTS.template.html")
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
        return {"xs": xs, "ok": 1 if ok else 0, "cv": cost["status"],
                "cm": cost["mean_profit_pct"], "c10": cost["stressed_pct"]}

    def universal(self, strategy):
        xs = self.status(strategy)
        ok = xs == "PASS" and er.qualifies_universal(self.cost.get(strategy), "coin")
        return {"xs": xs, "ok": 1 if ok else 0}


# ------------------------------------------------------------------ data exports
def regime_rows(table, regime_col, kind, robustness):
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
        rows.append(record)
    return rows


DETAIL_COLS = ["trades", "episodes", "dollar_gain_usd", "benchmark_dollar_gain_usd",
               "max_drawdown", "worst_trade", "sortino", "annualized_return", "profit_factor",
               "freqforge_score", "episode_excess_lcb", "lcb_grade"]


def universal_rows(universal, coin, robustness):
    indexed = coin.set_index(["strategy_id", "coin_regime"])
    rows = []
    for row in universal.to_dict(orient="records"):
        record = {k: clean(v) for k, v in row.items()}
        detail = indexed.loc[(row["strategy_id"], row["worst_regime"])]
        for column in DETAIL_COLS:
            record[column] = clean(detail[column])
        record.update(robustness.universal(row["strategy_id"]))
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
def facts_and_text(btc, coin, universal, gain, native, rejected, robustness, futures, dca, rows):
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
        "tbl_btc": de_int(len(btc)), "tbl_coin": de_int(len(coin)),
        # Stamped at generation, always: a page that carries an old date reads as current.
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
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
    text = {"consistent_intro": intro}

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
    ft_tail += (" Stand der Neuberechnung 2026-09-20: %s/%s VALIDATION-Zeilen, %d Universal-Kandidaten."
                % (de_int(len(val_btc)), de_int(len(val_coin)), n_universal))
    text["ft_intro_tail"] = ft_tail

    bull_lcb = sorted(val_coin[(val_coin["coin_regime"] == "BULL") & (val_coin["episode_excess_lcb"] > 0)]["strategy_id"])
    text["uptrend_recount"] = (
        "Neuberechnung 2026-09-20 (%d Strategien): %d %s in ADX Uptrend einen Coin-Edge mit "
        "<code class=\"mono\">episode_excess_lcb &gt; 0</code>: %s. Die Auswahl für Modell 1-3 bleibt der Stand vom "
        "15.09., weil die gegateten Läufe darauf beruhen."
        % (n_eval, len(bull_lcb), "hat" if len(bull_lcb) == 1 else "haben",
           ", ".join("<code class=\"mono\">%s</code>" % s for s in bull_lcb) or "keine"))

    text["callout_update"] = (
        '<div class="callout warn"><span class="dot">&#9888;</span><div><b>Neu berechnet am 2026-09-20.</b> '
        'Vier beim Intake gelöschte Duplikate (<code class="mono">chispei</code>, <code class="mono">MyStratV1</code>, '
        '<code class="mono">Combined_NFIv7_SMA_bAdBoY_20211204</code>, <code class="mono">Combined_NFIv7_SMA_Rallipanos_20210707</code>) '
        'sind aus allen Ergebnisspeichern entfernt; <code class="mono">MyStratV1</code> stand bis dahin mit je vier Zeilen '
        'in beiden Ranglisten neben seinem Vertreter. Zugleich bezieht die Auswertung jetzt alle seit dem 15.09. gemessenen '
        'Vollfenster-Läufe ein (%d statt 584 Strategien). Die Zahlen weichen deshalb von der Fassung vom 15.09. ab, und die '
        'Abweichung stammt überwiegend aus den neu gemessenen Strategien, nicht aus dem Entfernen der Duplikate. '
        'Der Abschnitt zu Modell 1-3 und die Top-10-Auswahl darunter sind Momentaufnahmen der gegateten Läufe und wurden nicht '
        'neu gerechnet.</div></div>\n'
        '<div class="callout info"><span class="dot">&#8505;</span><div><b>Robustheit (Stufe 8b), in jeder Tabelle mit Regime-Zeilen.</b> '
        'Ein Spezialist gilt erst als <i>verified</i>, wenn die Strategie den 5m-Detaillauf besteht und der Gewinn im '
        '<i>behaupteten</i> ADX-Zustand einen zusätzlichen Slippage von 0,1 %% je Seite übersteht (Validierungsfenster, '
        'mindestens 10 Trades in diesem Zustand). Bei Strategien bis 5m entfällt der Lauf, sie zählen per Entscheidung des '
        'Eigentümers als bestanden; das ist eine Regel und keine Messung. Die Spalte ändert kein Ranking. '
        'Stand: %d der %d Strategien sind im 5m-Lauf <code class="mono">sensitiv</code>, %s. <b>Rangfolge und Robustheit sind getrennte Aussagen:</b> Ein Rang 1 ohne PASS ist nur der beste '
        'Wert einer Zeile, kein verifizierter Spezialist.</div></div>'
        % (n_eval, sensitive, n_eval, run_state))
    return facts, text, manifest


def fill(template, facts, text):
    mapping = {k: str(v) for k, v in facts.items()}
    mapping.update(text)
    missing = sorted(set(re.findall(r"\{\{([a-z_0-9]+)\}\}", template)) - set(mapping))
    assert not missing, "template asks for facts that were not computed: %s" % ", ".join(missing)
    return re.sub(r"\{\{([a-z_0-9]+)\}\}", lambda m: mapping[m.group(1)], template)


def build(destination, skip_native=False):
    robustness = Robustness()
    btc = pd.read_csv(os.path.join(SPEC, "btc_specialist_table.csv"))
    coin = pd.read_csv(os.path.join(SPEC, "coin_specialist_table.csv"))
    universal = pd.read_csv(os.path.join(SPEC, "universal_strategies.csv"))
    gain = pd.read_csv(os.path.join(SPEC, "strategy_total_dollar_gain.csv"))

    rows = {"btc": regime_rows(btc, "btc_regime", "btc", robustness),
            "coin": regime_rows(coin, "coin_regime", "coin", robustness),
            "universal": universal_rows(universal, coin, robustness)}
    gain_rows = []
    for row in gain.to_dict(orient="records"):
        record = {k: clean(v) for k, v in row.items()}
        record.update(robustness.total(row["strategy_id"]))
        gain_rows.append(record)
    if skip_native:
        native, rejected = [], 0
    else:
        native, rejected = native_stats(universal["strategy_id"])

    profiles = pd.read_csv(PROFILES, usecols=["strategy_id", "run_profile"])
    futures = sorted(profiles.loc[profiles["run_profile"].str.startswith("futures_", na=False),
                                  "strategy_id"].unique().tolist())
    dca = dca_strategies()

    facts, text, _ = facts_and_text(btc, coin, universal, gain, native or [{}], rejected,
                                    robustness, futures, dca, rows)
    template = io.open(TEMPLATE, encoding="utf-8").read()
    template = fill(template, facts, text)

    static = {name: io.open(os.path.join(DATA, name.lower() + ".json"), encoding="utf-8").read().strip()
              for name in ("GATEDCOMPARE", "GATEDDETAIL", "TOP10BYREGIME", "COINEPISODES", "COINEPISODECOUNTS")}
    blobs = {
        "REGIMEFULL": _dump({"btc": rows["btc"], "coin": rows["coin"]}),
        "UNIVERSAL": _dump(rows["universal"]), "TOTALGAIN": _dump(gain_rows),
        "FTSTATS": _dump(native), "FUTURESSTRATEGIES": _dump(futures), "DCASTRATEGIES": _dump(dca),
    }
    blobs.update(static)
    for name, payload in blobs.items():
        token = "__%s_JSON__" % name
        assert template.count(token) == 1, token
        template = template.replace(token, payload)
    assert len(re.findall(r"<section[ >]", template)) == template.count("</section>")
    with io.open(destination, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(template)
    return facts


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=os.path.join(ROOT, "regime_specialists.html"))
    parser.add_argument("--skip-native", action="store_true",
                        help="leave the Freqtrade-native block empty (fast, for layout work)")
    args = parser.parse_args(argv)
    facts = build(args.out, args.skip_native)
    print("built %s (%.1f KB)" % (args.out, os.path.getsize(args.out) / 1024.0))
    for key in ("n_eval", "n_eligible", "n_universal", "n_consistent", "n_verified_rows_btc",
                "n_verified_rows_coin", "n_verified_universal"):
        print("  %-22s %s" % (key, facts[key]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
