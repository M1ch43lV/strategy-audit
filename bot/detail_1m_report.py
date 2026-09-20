# -*- coding: utf-8 -*-
"""Report of the 1m-detail batch: canonical 5m run, 5m control in the same window, 1m detail run.

    ./ftenv/Scripts/python.exe -m bot.detail_1m_report

The change caused by the detail candles alone is control -> 1m, both started at 2024-01-01 with the
same runner. canonical -> 1m adds whatever the different start of the window does (a strategy that
holds positions for months, as BuyOrDie does, starts the window in another state).
"""
from __future__ import annotations

import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from bot import detail_1m_batch as batch  # noqa: E402
from evidence import profile_smoke  # noqa: E402


def newest(strategy, key):
    prefix = os.path.join(profile_smoke.EXPORT_DIR, "%s-%s-*.zip" % (profile_smoke._safe(strategy), profile_smoke._safe(key)))
    found = sorted(glob.glob(prefix))
    return found[-1] if found else None


def stats_of(strategy, archive):
    return batch.stats(batch.trades_from(os.path.relpath(archive, ROOT).replace(os.sep, "/"), strategy))


def change(new, old):
    return 100.0 * (new - old) / abs(old) if old else float("nan")


def main():
    manifest = json.load(open(os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json"), encoding="utf-8"))["results"]
    rows = []
    for entry in batch.select():
        sid = entry["strategy_id"]
        d, c = newest(sid, batch.KEY), newest(sid, batch.CONTROL_KEY)
        if not d:
            print("%-38s no 1m run yet" % sid)
            continue
        canonical = batch.stats(batch.trades_from(manifest[sid]["archive"], sid))
        detail = stats_of(sid, d)
        control = stats_of(sid, c) if c else None
        rows.append(dict(strategy_id=sid, canonical=canonical, control=control, detail=detail))
    header = "%-38s %13s %13s %13s | %10s %10s"
    print(header % ("strategy", "canonical", "control 5m", "1m detail", "1m vs ctrl", "1m vs canon"))
    print(header % ("", "n / mean %", "n / mean %", "n / mean %", "mean/trade", "mean/trade"))
    fmt = lambda s: "-" if s is None else "%d / %.3f" % (s["trades"], s["mean_ratio_pct"])
    for r in rows:
        ctrl = r["control"]
        print("%-38s %13s %13s %13s | %+9.1f%% %+9.1f%%" % (
            r["strategy_id"], fmt(r["canonical"]), fmt(ctrl), fmt(r["detail"]),
            change(r["detail"]["mean_ratio_pct"], ctrl["mean_ratio_pct"]) if ctrl else float("nan"),
            change(r["detail"]["mean_ratio_pct"], r["canonical"]["mean_ratio_pct"])))

    def summary(label, pairs):
        if not pairs:
            return
        changes = sorted(change(n["mean_ratio_pct"], o["mean_ratio_pct"]) for n, o in pairs)
        sum_new, sum_old = sum(n["sum_ratio"] for n, o in pairs), sum(o["sum_ratio"] for n, o in pairs)
        trades_new = sum(n["trades"] for n, o in pairs)
        trades_old = sum(o["trades"] for n, o in pairs)
        pooled_new = 100 * sum_new / trades_new
        pooled_old = 100 * sum_old / trades_old
        print("%s (%d strategies): average of the changes %+.1f %%, median %+.1f %%, worse in %d, better in %d; "
              "pooled mean per trade %.3f %% -> %.3f %% (%+.1f %%); sum of ratios %+.1f %%"
              % (label, len(pairs), sum(changes) / len(changes), changes[len(changes) // 2],
                 sum(1 for x in changes if x < 0), sum(1 for x in changes if x > 0), pooled_old, pooled_new,
                 change(pooled_new, pooled_old), change(sum_new, sum_old)))

    summary("detail candles alone (1m vs control)", [(r["detail"], r["control"]) for r in rows if r["control"]])
    summary("1m vs canonical 5m run", [(r["detail"], r["canonical"]) for r in rows])
    json.dump(rows, open(os.path.join(ROOT, "results", "regime", "rotation_bot", "detail_1m_report.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
