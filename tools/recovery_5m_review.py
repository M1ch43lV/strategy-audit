# -*- coding: utf-8 -*-
"""Was the 5m rerun of the 1m out-of-memory strategies worth it, and where do the strategies stand?

    ./ftenv/Scripts/python.exe -m tools.recovery_5m_review

Reads what the published Regime-Spezialisten page shows (`regime_specialists.html`: the whole-window table, the BTC and
coin phase rows, the universal candidates) and the manifest of the accepted baselines, so the numbers are the ones a reader
sees. The strategies are those whose accepted baseline has the scope
`owner_approved_timeframe_5m_recovery_pooled_pair_universe`. Every comparison is against all other strategies on the same
page. Descriptive; it decides nothing.
"""
from __future__ import annotations

import json
import os
import re
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "regime_specialists.html")
MANIFEST = os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json")
SCOPE = "owner_approved_timeframe_5m_recovery_pooled_pair_universe"
OUT = os.path.join(ROOT, "results", "regime", "recovery_5m_review.json")


def blob(html, name):
    return json.loads(re.search(r"const %s = (.*?);\n" % name, html, re.S).group(1))


def main():
    html = open(PAGE, encoding="utf-8").read()
    total, phases, universal = blob(html, "TOTALGAIN"), blob(html, "REGIMEFULL"), blob(html, "UNIVERSAL")
    manifest = json.load(open(MANIFEST, encoding="utf-8"))["results"]
    rec = {s for s, r in manifest.items() if r.get("status") == "measured" and r.get("measurement_scope") == SCOPE}

    n_total = len(total)
    mine = [r for r in total if r["strategy_id"] in rec]
    others = [r for r in total if r["strategy_id"] not in rec]
    out = {"recovered_strategies": len(rec), "with_total_row": len(mine), "all_with_total_row": n_total}

    ranks = sorted(r["rk"] for r in mine)
    out["rank"] = {"median": statistics.median(ranks), "population_median": (n_total + 1) / 2,
                   **{"top_%d" % k: sum(1 for x in ranks if x <= k) for k in (10, 25, 50, 100, 200)}}
    share = lambda rows, f: round(sum(1 for r in rows if f(r)) / max(1, len(rows)), 3)
    out["gain_positive"] = {"recovered": share(mine, lambda r: r["dollar_gain_usd"] > 0), "others": share(others, lambda r: r["dollar_gain_usd"] > 0)}
    out["beats_buy_and_hold"] = {"recovered": share(mine, lambda r: r["excess_dollar_gain_usd"] > 0), "others": share(others, lambda r: r["excess_dollar_gain_usd"] > 0)}
    out["robustness_pass"] = {"recovered": share(mine, lambda r: r.get("xs") == "PASS"), "others": share(others, lambda r: r.get("xs") == "PASS")}
    out["cost_pass_whole_run"] = {"recovered": share(mine, lambda r: r.get("cv") == "PASS"), "others": share(others, lambda r: r.get("cv") == "PASS")}

    def per_strategy(kind):
        by = {}
        for row in phases[kind]:
            by.setdefault(row["strategy_id"], []).append(row)
        return by

    verified, confirmed, tier_rows = {}, {}, {}
    for kind in ("btc", "coin"):
        by = per_strategy(kind)
        for sid, rows in by.items():
            verified.setdefault(sid, 0)
            confirmed.setdefault(sid, 0)
            tier_rows.setdefault(sid, 0)
            verified[sid] += sum(1 for r in rows if r.get("ok") == 1)
            confirmed[sid] += sum(1 for r in rows if r.get("cf") == 2)
            tier_rows[sid] += len(rows)
    evaluated = set(verified) | {r["strategy_id"] for r in total}
    mine_ids = {r["strategy_id"] for r in mine} | (rec & set(verified))
    others_ids = evaluated - rec
    out["specialist"] = {
        "strategies_with_validation_rows": {"recovered": sum(1 for s in rec if tier_rows.get(s)), "others": sum(1 for s in others_ids if tier_rows.get(s))},
        "at_least_one_verified_row": {"recovered": sum(1 for s in rec if verified.get(s)), "others": sum(1 for s in others_ids if verified.get(s))},
        "at_least_one_confirmed_row": {"recovered": sum(1 for s in rec if confirmed.get(s)), "others": sum(1 for s in others_ids if confirmed.get(s))},
        "verified_rows": {"recovered": sum(verified.get(s, 0) for s in rec), "all": sum(verified.values())},
        "confirmed_rows": {"recovered": sum(confirmed.get(s, 0) for s in rec), "all": sum(confirmed.values())},
    }

    # position in the Top 10 of each phase (ranked by excess return, VALIDATION tier), verified rows only and all rows
    tops = {}
    for kind in ("btc", "coin"):
        for state in ("BULL", "BEAR", "SIDEWAYS", "TRANSITION"):
            rows = sorted((r for r in phases[kind] if r["regime"] == state), key=lambda r: -r["excess_return"])
            vrows = [r for r in rows if r.get("ok") == 1]
            tops["%s/%s" % (kind, state)] = {
                "rows": len(rows), "recovered_in_top10": sum(1 for r in rows[:10] if r["strategy_id"] in rec),
                "verified_rows": len(vrows), "recovered_in_verified_top10": sum(1 for r in vrows[:10] if r["strategy_id"] in rec),
                "recovered_verified": [(i + 1, r["strategy_id"]) for i, r in enumerate(vrows) if r["strategy_id"] in rec][:5]}
    out["phase_top10"] = tops
    out["universal"] = {"candidates": len(universal), "recovered": [u["strategy_id"] for u in universal if u["strategy_id"] in rec],
                        "recovered_verified": [u["strategy_id"] for u in universal if u["strategy_id"] in rec and u.get("ok") == 1],
                        "verified_total": sum(1 for u in universal if u.get("ok") == 1)}
    out["best"] = [{"rank": r["rk"], "strategy_id": r["strategy_id"], "gain_usd": round(r["dollar_gain_usd"]), "excess_usd": round(r["excess_dollar_gain_usd"]),
                    "robust": r.get("xs"), "verified_rows": verified.get(r["strategy_id"], 0), "confirmed_rows": confirmed.get(r["strategy_id"], 0)}
                   for r in sorted(mine, key=lambda r: r["rk"])[:12]]

    hashes = {}
    for s in rec:
        hashes.setdefault(manifest[s].get("trades_sha256"), []).append(s)
    same_as_other = {h for h in hashes if any(r.get("trades_sha256") == h and s not in rec for s, r in manifest.items())}
    out["duplicates"] = {"distinct_trade_sets": len(hashes), "sets_shared_by_several_recovered": sum(1 for v in hashes.values() if len(v) > 1),
                         "sets_equal_to_a_non_recovered_strategy": len(same_as_other)}
    out["compute"] = {"full_backtest_hours": round(sum(manifest[s].get("elapsed_s") or 0 for s in rec) / 3600, 1),
                      "peak_memory_mib_max": max(manifest[s].get("peak_memory_mib") or 0 for s in rec)}
    with open(OUT, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(out, handle, indent=1, sort_keys=True, default=str)
        handle.write("\n")
    print(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
