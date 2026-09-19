# -*- coding: utf-8 -*-
"""Execution robustness: the intracandle-detail classifier and the cost screen.

Two derived stores, both generated from result archives and never edited by hand:

* ``evidence/EXECUTION_ROBUSTNESS.json`` - compares each strategy's canonical
  pooled Full-Backtest with the same run repeated under ``--timeframe-detail``
  and classifies it PASS / SENSITIVE / NA / ERROR
  (see EXECUTION_ROBUSTNESS_PLAN.md).
* ``evidence/COST_SCREEN.json`` - re-prices every measured canonical
  Full-Backtest with extra slippage and reports whether the net profit
  survives. It needs no new backtest, only the trades already in the archive.

The detail runs themselves are produced elsewhere (regime.full_backtest with
``--timeframe-detail``); this module only reads what they left behind. Each
record carries the numbers it was decided on, so the evidence files stay
readable on a checkout that does not have ``user_data/`` (the archives are not
versioned). A rebuild without an archive keeps that strategy's existing record.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import glob
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASELINE_STORE = os.path.join(ROOT, "results", "regime", "full_backtest_manifest.json")
DETAIL_GLOB = os.path.join(ROOT, "results", "regime",
                           "execution_robustness_detail_*.json")
ROBUSTNESS_OUTPUT = os.path.join(ROOT, "evidence", "EXECUTION_ROBUSTNESS.json")
COST_OUTPUT = os.path.join(ROOT, "evidence", "COST_SCREEN.json")
DATA_DIR = os.path.join(ROOT, "user_data", "data", "binance")

CANONICAL_SCOPE = "canonical_pooled_native_pair_universe"
ROBUSTNESS_STAGE = "post_full_backtest_execution_robustness"
COST_STAGE = "post_full_backtest_cost_screen"

TF_MINUTES = {"1m": 1, "3m": 3, "5m": 5, "15m": 15, "30m": 30, "1h": 60,
              "2h": 120, "4h": 240, "6h": 360, "8h": 480, "12h": 720, "1d": 1440}

# Thresholds are declared here, hashed into every record, and were fixed while
# 42 of the 230 five-minute-detail runs existed and before the rest did. They are
# review triggers, not exclusion criteria.
THRESHOLDS = {
    # The plan's "loses more than 50 percent of the baseline net profit",
    # made symmetric: a detail run that GAINS more than half again is exactly
    # as informative, and TrendBreakout went from -52.8 % to +75.6 %.
    "profit_relative_change": 0.50,
    # A different trade set means the regime attribution, which is built on the
    # baseline trades, no longer describes the run that was more realistic.
    "trade_count_relative_change": 0.10,
    # freqtrade silently falls back to the coarse candle where detail data is
    # missing, so a run over partial detail data would still "measure".
    "detail_coverage_min_ratio": 0.99,
}
COST = {
    # The backtests already charge a 0.1 % fee per side. The reference stress
    # doubles that friction: another 0.1 % per side, 0.2 % round trip.
    "reference_slippage_per_side": 0.001,
    "grid_per_side": [0.0005, 0.001, 0.002],
    # "Be cautious if your average profit is below 0.5 %" (Brook Miles,
    # Backtesting Traps in Freqtrade, 2021). Reported as a flag, not decisive.
    "caution_mean_profit_ratio": 0.005,
}
# Detail timeframe by main timeframe. Above 5m the plan's 5m detail; at or
# below 5m the 1m detail (owner decision 2026-09-19); a 1m strategy has no
# finer data to model with.
DETAIL_RULE = {">5m": "5m", "<=5m": "1m", "<=1m": None}


def parameters():
    return {"thresholds": THRESHOLDS, "cost": COST, "detail_rule": DETAIL_RULE}


def parameters_sha256():
    text = json.dumps(parameters(), sort_keys=True, separators=(",", ":"))
    return "sha256_" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def detail_timeframe(main_timeframe):
    minutes = TF_MINUTES.get(main_timeframe)
    if minutes is None or minutes <= 1:
        return None
    return "5m" if minutes > 5 else "1m"


def _load(path):
    if not os.path.exists(path):
        return {}
    with io.open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _write(path, data):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def _round(value, digits=6):
    return None if value is None else round(float(value), digits)


def read_block(archive, strategy, root=ROOT):
    """The native strategy block of one result archive, or None."""
    path = os.path.join(root, archive.replace("/", os.sep))
    if not archive or not os.path.exists(path):
        return None
    with zipfile.ZipFile(path) as bundle:
        names = [n for n in bundle.namelist()
                 if n.endswith(".json") and not n.endswith("_config.json")
                 and not n.endswith(".meta.json")]
        if not names:
            return None
        data = json.loads(bundle.read(names[0]).decode("utf-8"))
    return (data.get("strategy") or {}).get(strategy)


def metrics(block):
    """The quantities both checks are decided on, from one native block."""
    trades = block.get("trades") or []
    n = len(trades)
    minutes = TF_MINUTES.get(block.get("timeframe"))
    if not n:
        return {"trades": 0}
    exits = collections.Counter(t.get("exit_reason") or "" for t in trades)
    profit_abs = sum(t["profit_abs"] for t in trades)
    balance = block.get("starting_balance") or 0
    return {
        "trades": n,
        "profit_abs": _round(profit_abs, 4),
        "profit_pct": _round(100.0 * profit_abs / balance, 4) if balance else None,
        "mean_profit_pct": _round(100.0 * sum(t["profit_ratio"] for t in trades) / n, 4),
        "winrate_pct": _round(100.0 * sum(1 for t in trades if t["profit_abs"] > 0) / n, 3),
        "mean_duration_min": _round(sum(t["trade_duration"] for t in trades) / n, 2),
        # Brook Miles' tell: trades that close on the candle they opened on.
        "same_candle_pct": _round(
            100.0 * sum(1 for t in trades if minutes and t["trade_duration"] < minutes) / n, 3),
        "trailing_exit_pct": _round(
            100.0 * sum(c for r, c in exits.items() if "trailing" in r) / n, 3),
        "exit_reasons": dict(sorted(exits.items())),
        "negative_duration_trades": sum(1 for t in trades if t["trade_duration"] < 0),
        "profit_factor": _round(block.get("profit_factor"), 4),
        "max_drawdown_account": _round(block.get("max_drawdown_account"), 4),
        "sharpe": _round(block.get("sharpe"), 4),
        "starting_balance": balance,
    }


def exit_profile_distance(base, det):
    """Total variation distance of the exit-reason mix. Descriptive only: on the
    first 42 runs its median was 0.002 and its maximum 0.063, so it never
    separated a run that flipped sign from one that did not."""
    nb, nd = base.get("trades") or 0, det.get("trades") or 0
    if not nb or not nd:
        return None
    kinds = set(base["exit_reasons"]) | set(det["exit_reasons"])
    return _round(0.5 * sum(abs(base["exit_reasons"].get(k, 0) / nb
                                - det["exit_reasons"].get(k, 0) / nd) for k in kinds))


def compare(base, det):
    """Pure comparison of two metric dicts -> (trigger names, delta record)."""
    reasons = []
    pb, pd_ = base["profit_abs"], det["profit_abs"]
    relative = abs(pd_ - pb) / abs(pb) if pb else None
    if (pb > 0) != (pd_ > 0):
        reasons.append("profit_sign_flip")
    if relative is not None and relative > THRESHOLDS["profit_relative_change"]:
        reasons.append("profit_change_over_50pct")
    trade_relative = abs(det["trades"] - base["trades"]) / base["trades"]
    if trade_relative > THRESHOLDS["trade_count_relative_change"]:
        reasons.append("trade_count_change_over_10pct")
    delta = {
        "profit_abs": _round(pd_ - pb, 4),
        "profit_pct_points": _round(det["profit_pct"] - base["profit_pct"], 4)
        if base.get("profit_pct") is not None and det.get("profit_pct") is not None else None,
        "profit_relative_change": _round(relative, 4),
        "trades": det["trades"] - base["trades"],
        "trade_relative_change": _round(trade_relative, 4),
        "exit_profile_distance": exit_profile_distance(base, det),
        "same_candle_pct_points": _round(det["same_candle_pct"] - base["same_candle_pct"], 3),
    }
    return reasons, delta


def anomalies(base, det):
    """Findings about the runs, not the strategy. They never change a status."""
    found = []
    if det.get("negative_duration_trades", 0) > base.get("negative_duration_trades", 0):
        found.append("detail_run_has_%d_trades_closing_before_they_opened"
                     % (det["negative_duration_trades"] - base.get("negative_duration_trades", 0)))
    return found


def _identity_mismatch(base_record, det_record):
    fields = ("canonical_sha256", "runtime_config_sha256", "run_profile", "timerange", "pairs")
    return [f for f in fields if base_record.get(f) != det_record.get(f)]


def detail_coverage(mode, pairs, main_tf, detail_tf, timerange, data_dir=DATA_DIR):
    """Detail candles present, as a fraction of what the main candles imply.

    Compared against the main timeframe's own data for the same pair and
    window, so an exchange gap or a delisting (XMR ends 2024-02-20 in every
    timeframe) is not read as missing detail. Returns (min_ratio, per_pair).
    """
    import pandas as pd
    start, end = timerange.split("-")
    lo = pd.Timestamp(start, tz="UTC")
    hi = pd.Timestamp(end, tz="UTC")
    scale = TF_MINUTES[main_tf] / float(TF_MINUTES[detail_tf])
    ratios = {}
    for pair in pairs:
        stem = pair.replace("/", "_").replace(":", "_")
        counts = []
        for tf in (main_tf, detail_tf):
            name = ("%s-%s-futures.feather" % (stem, tf) if mode == "futures"
                    else "%s-%s.feather" % (stem, tf))
            path = os.path.join(data_dir, "futures" if mode == "futures" else "", name)
            if not os.path.exists(path):
                counts.append(None)
                continue
            dates = pd.read_feather(path, columns=["date"])["date"]
            counts.append(int(((dates >= lo) & (dates < hi)).sum()))
        main_count, detail_count = counts
        if main_count is None:
            continue
        if not main_count:
            continue
        ratios[pair] = 0.0 if detail_count is None else round(detail_count / (main_count * scale), 4)
    return (min(ratios.values()) if ratios else None), ratios


def choose_detail_records(paths=None):
    """Best detail record per strategy across every detail store.

    A measured record beats a failed one (the native runtime failed the first
    ten strategies that Docker then measured); ties go to the later attempt.
    """
    best = {}
    for path in sorted(paths if paths is not None else glob.glob(DETAIL_GLOB)):
        if path.endswith(".tmp"):
            continue
        data = _load(path)
        if not isinstance(data.get("results"), dict):
            continue
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        for strategy, record in data["results"].items():
            if not isinstance(record, dict) or not record.get("timeframe_detail"):
                continue
            rank = (record.get("status") == "measured", record.get("attempted_at") or "")
            if strategy not in best or rank > best[strategy][0]:
                best[strategy] = (rank, dict(record, store=rel))
    return {strategy: pair[1] for strategy, pair in best.items()}


def classify(strategy, base_record, det_record, base_block, det_block, coverage=None):
    """One robustness record. ``coverage`` is (min_ratio, per_pair) or None."""
    want = det_record["timeframe_detail"]
    main_tf = (base_block or {}).get("timeframe") or ""
    record = {
        "main_timeframe": main_tf, "detail_timeframe": want,
        "thresholds_sha256": parameters_sha256(),
        "detail": {"status": det_record.get("status"),
                   "store": det_record.get("store"),
                   "runtime_id": det_record.get("runtime_id"),
                   "attempted_at": det_record.get("attempted_at"),
                   "archive": det_record.get("archive"),
                   "trades_sha256": det_record.get("trades_sha256")},
        "baseline": {"runtime_id": base_record.get("runtime_id"),
                     "archive": base_record.get("archive"),
                     "trades_sha256": base_record.get("trades_sha256"),
                     "canonical_sha256": base_record.get("canonical_sha256")},
    }

    def done(status, reasons, **extra):
        record.update(status=status, reasons=reasons, **extra)
        return record

    if det_record.get("status") != "measured":
        return done("ERROR", ["detail_run_%s" % det_record.get("status")])
    if base_block is None or det_block is None:
        return done("ERROR", ["result_archive_unreadable"])
    if detail_timeframe(main_tf) is None:
        return done("NA", ["no_finer_timeframe_than_%s" % main_tf])
    if want != detail_timeframe(main_tf):
        return done("NA", ["detail_timeframe_%s_not_the_rule_for_%s" % (want, main_tf)])
    if det_block.get("timeframe_detail") != want:
        return done("ERROR", ["detail_flag_not_applied_in_native_result"])
    if base_block.get("timeframe_detail"):
        return done("ERROR", ["baseline_is_itself_a_detail_run"])
    mismatch = _identity_mismatch(base_record, det_record)
    if mismatch:
        return done("NA", ["identity_mismatch:" + ",".join(mismatch)])
    base, det = metrics(base_block), metrics(det_block)
    if not base["trades"] or not det["trades"]:
        return done("NA", ["no_trades_to_compare"], baseline_metrics=base, detail_metrics=det)
    if coverage is not None:
        ratio, per_pair = coverage
        record["coverage"] = {"min_ratio": ratio, "per_pair": per_pair}
        if ratio is not None and ratio < THRESHOLDS["detail_coverage_min_ratio"]:
            return done("NA", ["detail_data_incomplete"], baseline_metrics=base,
                        detail_metrics=det)
    reasons, delta = compare(base, det)
    same_runtime = base_record.get("runtime_id") == det_record.get("runtime_id")
    status = "SENSITIVE" if reasons else "PASS"
    return done(
        status, reasons, baseline_metrics=base, detail_metrics=det, delta=delta,
        anomalies=anomalies(base, det),
        comparison={"same_runtime": same_runtime,
                    # A cross-runtime SENSITIVE is not yet attributable to the
                    # detail candles: a Docker run without --timeframe-detail
                    # would separate the two.
                    "control_run_needed": bool(reasons) and not same_runtime})


def cost_screen(block):
    """Re-price the baseline trades with extra slippage; no new backtest.

    First order: the trades and their stakes are the ones the run made. With
    ``stake_amount: unlimited`` a lower balance would shrink later stakes, an
    effect this leaves out; it is second order next to the cost itself.
    """
    trades = block.get("trades") or []
    if not trades:
        return {"status": "NA", "reasons": ["no_trades"]}
    profit = sum(t["profit_abs"] for t in trades)
    notional = sum(t["stake_amount"] * (t.get("leverage") or 1.0) for t in trades)
    balance = block.get("starting_balance") or 0
    per_side = COST["grid_per_side"]
    stressed = {}
    for s in per_side:
        net = profit - 2.0 * s * notional
        stressed["%.4f" % s] = {
            "net_profit_abs": _round(net, 4),
            "net_profit_pct": _round(100.0 * net / balance, 4) if balance else None,
            "mean_profit_pct": _round(100.0 * sum(
                t["profit_ratio"] - 2.0 * s * (t.get("leverage") or 1.0) for t in trades)
                / len(trades), 4),
            "survives": net > 0,
        }
    break_even = profit / (2.0 * notional) if notional else None
    mean_ratio = sum(t["profit_ratio"] for t in trades) / len(trades)
    record = {
        "trades": len(trades),
        "main_timeframe": block.get("timeframe") or "",
        "baseline_profit_abs": _round(profit, 4),
        "baseline_mean_profit_pct": _round(100.0 * mean_ratio, 4),
        "mean_profit_below_caution": mean_ratio < COST["caution_mean_profit_ratio"],
        "break_even_slippage_bps_per_side": _round(1e4 * break_even, 2)
        if break_even is not None else None,
        "stressed": stressed,
        "thresholds_sha256": parameters_sha256(),
    }
    if profit <= 0:
        record.update(status="NA", reasons=["baseline_not_profitable"])
        return record
    reference = stressed["%.4f" % COST["reference_slippage_per_side"]]
    record.update(status="PASS" if reference["survives"] else "SENSITIVE",
                  reasons=[] if reference["survives"] else ["not_profitable_at_reference_slippage"])
    return record


def measured_baselines(baseline):
    return {s: r for s, r in baseline.items()
            if isinstance(r, dict) and r.get("status") == "measured"
            and r.get("measurement_scope") == CANONICAL_SCOPE}


def build(root=ROOT, detail_paths=None, with_coverage=True):
    """Both stores, from the archives that are present. Returns (rob, cost, notes)."""
    baseline = _load(os.path.join(root, "results", "regime",
                                  "full_backtest_manifest.json")).get("results", {})
    old_rob = _load(os.path.join(root, "evidence", "EXECUTION_ROBUSTNESS.json")).get("results", {})
    old_cost = _load(os.path.join(root, "evidence", "COST_SCREEN.json")).get("results", {})
    details = choose_detail_records(detail_paths)
    rob, cost, notes = {}, {}, collections.Counter()
    blocks = {}
    for strategy, record in sorted(measured_baselines(baseline).items()):
        block = read_block(record.get("archive"), strategy, root)
        if block is None:
            notes["baseline_archive_unavailable"] += 1
            if strategy in old_cost:
                cost[strategy] = old_cost[strategy]
            continue
        cost[strategy] = cost_screen(block)
        blocks[strategy] = block
    coverage_cache = {}
    for strategy, record in sorted(details.items()):
        base_record = baseline.get(strategy) or {}
        base_block = blocks.get(strategy)
        det_block = read_block(record.get("archive"), strategy, root) \
            if record.get("status") == "measured" else None
        if record.get("status") == "measured" and (base_block is None or det_block is None):
            notes["detail_archive_unavailable"] += 1
            if strategy in old_rob:
                rob[strategy] = old_rob[strategy]
            continue
        coverage = None
        if with_coverage and det_block is not None and base_block is not None:
            key = (record.get("mode"), tuple(record.get("pairs") or ()),
                   base_block.get("timeframe"), record["timeframe_detail"], record.get("timerange"))
            if key not in coverage_cache:
                try:
                    coverage_cache[key] = detail_coverage(*key)
                except Exception as exc:  # a data-layout surprise is not a verdict
                    coverage_cache[key] = None
                    notes["coverage_unverifiable:%s" % type(exc).__name__] += 1
            coverage = coverage_cache[key]
        rob[strategy] = classify(strategy, base_record, record, base_block, det_block, coverage)
        if det_block is not None and strategy in cost:
            cost[strategy]["detail"] = cost_screen(det_block)
    # A strategy whose main timeframe is already the finest there is has no
    # detail run to wait for.
    for strategy, block in sorted(blocks.items()):
        if strategy not in rob and detail_timeframe(block.get("timeframe")) is None:
            rob[strategy] = {"status": "NA", "reasons": ["no_finer_timeframe_than_%s"
                             % block.get("timeframe")], "main_timeframe": block.get("timeframe"),
                             "thresholds_sha256": parameters_sha256()}
    return rob, cost, notes


def document(results, stage):
    return {"schema_version": 1, "stage": stage, "parameters": parameters(),
            "parameters_sha256": parameters_sha256(), "results": results}


def targets(detail_tf, limit=0):
    """Strategies still owed a detail run at ``detail_tf``, and the command."""
    baseline = measured_baselines(_load(BASELINE_STORE).get("results", {}))
    done = {s for s, r in choose_detail_records().items()
            if r.get("status") == "measured" and r["timeframe_detail"] == detail_tf}
    cost = _load(COST_OUTPUT).get("results", {})
    names = sorted(s for s in baseline if s not in done
                   and detail_timeframe((cost.get(s) or {}).get("main_timeframe")) == detail_tf)
    if limit:
        names = names[:limit]
    return names


def _cmd(detail_tf, names):
    return ("powershell -NoProfile -ExecutionPolicy Bypass -File "
            "runtime\\regime_full_backtest_docker.ps1 --timeframe-detail %s "
            "--output results/regime/execution_robustness_detail_%s_docker.json "
            "--workers 1 --timeout 3600 %s"
            % (detail_tf, detail_tf, " ".join("--strategy %s" % n for n in names)))


def summary(rob, cost):
    lines = ["execution robustness: %s" % dict(collections.Counter(
        r["status"] for r in rob.values()))]
    lines.append("cost screen        : %s" % dict(collections.Counter(
        r["status"] for r in cost.values())))
    flagged = [s for s, r in rob.items() if r.get("comparison", {}).get("control_run_needed")]
    lines.append("SENSITIVE across runtimes, control run advisable: %s" % (flagged or "none"))
    odd = [s for s, r in rob.items() if r.get("anomalies")]
    lines.append("detail runs with anomalies: %d" % len(odd))
    return "\n".join(lines)


# --------------------------------------------------------------------------
def _archive(directory, strategy, tf, trades, detail_tf=None, balance=1000.0, label="base"):
    block = {"timeframe": tf, "starting_balance": balance, "trades": trades,
             "profit_factor": 1.0}
    if detail_tf:
        block["timeframe_detail"] = detail_tf
    name = "%s-%s" % (strategy, label)
    path = os.path.join(directory, name + ".zip")
    with zipfile.ZipFile(path, "w") as bundle:
        bundle.writestr(name + ".json", json.dumps({"strategy": {strategy: block}}))
        bundle.writestr(name + "_config.json", "{}")
    return os.path.relpath(path, directory).replace(os.sep, "/")


def _trade(profit, stake=100.0, duration=120, reason="roi", leverage=1.0):
    return {"profit_abs": profit, "profit_ratio": profit / stake, "stake_amount": stake,
            "trade_duration": duration, "exit_reason": reason, "leverage": leverage}


def selftest():
    assert detail_timeframe("1d") == detail_timeframe("1h") == detail_timeframe("15m") == "5m"
    assert detail_timeframe("5m") == detail_timeframe("3m") == "1m"
    assert detail_timeframe("1m") is None and detail_timeframe("weird") is None

    work = tempfile.mkdtemp(prefix="robustness_selftest_")
    try:
        # Records for the whole store need the archive paths relative to root.
        base_trades = [_trade(2.0) for _ in range(100)]
        arch_base = _archive(work, "S", "1h", base_trades, label="base")

        def run(det_trades, det_status="measured", tf="1h", detail_tf="5m",
                flag=True, same_runtime=True, mismatch=False):
            det_arch = _archive(work, "S", tf, det_trades, detail_tf if flag else None, label="det")
            base_rec = {"archive": arch_base, "runtime_id": "docker:x",
                        "canonical_sha256": "a", "runtime_config_sha256": "c",
                        "run_profile": "spot_long", "timerange": "t", "pairs": ["BTC/USDT"],
                        "trades_sha256": "b"}
            det_rec = dict(base_rec, archive=det_arch, status=det_status,
                           timeframe_detail=detail_tf, store="s",
                           runtime_id="docker:x" if same_runtime else "native")
            if mismatch:
                det_rec["runtime_config_sha256"] = "changed"
            return classify("S", base_rec, det_rec, read_block(arch_base, "S", work),
                            read_block(det_arch, "S", work) if det_status == "measured" else None)

        assert run([_trade(2.0) for _ in range(100)])["status"] == "PASS"
        assert run([_trade(0.5) for _ in range(100)])["reasons"] == ["profit_change_over_50pct"]
        assert "profit_change_over_50pct" in run([_trade(4.0) for _ in range(100)])["reasons"]
        flip = run([_trade(-0.1) for _ in range(100)])
        assert flip["status"] == "SENSITIVE" and "profit_sign_flip" in flip["reasons"]
        assert run([_trade(2.0) for _ in range(80)])["reasons"] == ["trade_count_change_over_10pct"]
        assert run([_trade(2.0) for _ in range(95)])["status"] == "PASS"
        assert run([], det_status="failed")["status"] == "ERROR"
        assert run([_trade(2.0)] * 100, flag=False)["reasons"] == ["detail_flag_not_applied_in_native_result"]
        assert run([_trade(2.0)] * 100, mismatch=True)["status"] == "NA"
        assert run([_trade(2.0)] * 100, detail_tf="1m")["status"] == "NA"
        cross = run([_trade(0.5) for _ in range(100)], same_runtime=False)
        assert cross["comparison"] == {"same_runtime": False, "control_run_needed": True}
        assert run([_trade(0.5) for _ in range(100)])["comparison"]["control_run_needed"] is False
        # A run closing trades before they open is reported and changes nothing.
        odd = run([_trade(2.0)] * 99 + [_trade(2.0, duration=-5)])
        assert odd["status"] == "PASS" and odd["anomalies"], odd
        # A 1m strategy has nothing finer to model with.
        assert classify("S", {"archive": "x"}, {"timeframe_detail": "5m", "status": "measured"},
                        {"timeframe": "1m"}, {"timeframe": "1m", "timeframe_detail": "5m"}
                        )["status"] in ("NA", "ERROR")

        # Cost screen: 100 trades, stake 100, profit 1.0 each.
        screen = cost_screen({"timeframe": "1h", "starting_balance": 1000.0,
                              "trades": [_trade(1.0) for _ in range(100)]})
        assert screen["break_even_slippage_bps_per_side"] == 50.0, screen
        assert screen["status"] == "PASS" and screen["stressed"]["0.0010"]["net_profit_abs"] == 80.0
        thin = cost_screen({"timeframe": "1h", "starting_balance": 1000.0,
                            "trades": [_trade(0.1) for _ in range(100)]})
        assert thin["status"] == "SENSITIVE" and thin["mean_profit_below_caution"]
        assert thin["stressed"]["0.0005"]["survives"] is False or \
            thin["stressed"]["0.0005"]["net_profit_abs"] == 0.0
        assert cost_screen({"timeframe": "1h", "trades": [_trade(-1.0)] * 5})["status"] == "NA"
        # Leverage: cost is charged on the notional, not the margin.
        levered = cost_screen({"timeframe": "1h", "starting_balance": 1000.0,
                               "trades": [_trade(1.0, leverage=3.0) for _ in range(100)]})
        assert abs(levered["stressed"]["0.0010"]["net_profit_abs"] - 40.0) < 1e-3, levered
        # The parameter hash reacts to a threshold change.
        before = parameters_sha256()
        THRESHOLDS["profit_relative_change"] = 0.4
        try:
            assert parameters_sha256() != before
        finally:
            THRESHOLDS["profit_relative_change"] = 0.50
        assert parameters_sha256() == before
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("execution_robustness selftest: PASS")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="fail when the stores differ from a rebuild")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--targets", choices=("5m", "1m"),
                        help="list strategies still owed a detail run and print the command")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--no-coverage", action="store_true",
                        help="skip the detail-data coverage check")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if args.targets:
        names = targets(args.targets, args.limit)
        print("# %d strategies owed a %s detail run" % (len(names), args.targets))
        if names:
            print(_cmd(args.targets, names))
        return 0
    rob, cost, notes = build(with_coverage=not args.no_coverage)
    rob_doc, cost_doc = document(rob, ROBUSTNESS_STAGE), document(cost, COST_STAGE)
    if notes:
        print("notes:", dict(notes))
    if args.check:
        stale = [p for p, d in ((ROBUSTNESS_OUTPUT, rob_doc), (COST_OUTPUT, cost_doc))
                 if _load(p) != json.loads(json.dumps(d, sort_keys=True))]
        if stale:
            print("stale: " + ", ".join(os.path.basename(p) for p in stale), file=sys.stderr)
            return 1
        print("execution robustness: current")
        return 0
    _write(ROBUSTNESS_OUTPUT, rob_doc)
    _write(COST_OUTPUT, cost_doc)
    print(summary(rob, cost))
    return 0


if __name__ == "__main__":
    sys.exit(main())
