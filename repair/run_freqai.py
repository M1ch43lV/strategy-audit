# -*- coding: utf-8 -*-
"""run_freqai - measure the FreqAI strategies the audit could not run.

FreqAI strategies abort under the audit's config with "freqAI is not enabled".
Enabling it needs a `freqai` block, and that block is not something the strategy
supplies - training window, retrain cadence, feature expansion and the model
itself are all chosen by whoever runs it.

THIS IS THEREFORE NOT A CLASS 1 REPAIR AND NOT COMPARABLE WITH THE SPOT RUN.
Every number produced here says "this strategy under OUR training setup", not
"this strategy". Cards are tagged `run_class="freqai"` and must be reported
separately within the two-population design. The point is to establish that
these strategies RUN and what they do when they do - not to place them on the
audit's ladder or to create a third population.

The choices below, stated so they can be disagreed with:

  train_period_days      30   one month of training per model
  backtest_period_days    7   retrain weekly
  model      LightGBMRegressor   installed, CPU-only, deterministic given a seed
  test_size            0.33   freqtrade's own example value
  include_timeframes   the strategy's own timeframe plus the next higher ones
                       available locally - FreqAI requires the base timeframe to
                       be present, and a strategy asking for candles we do not
                       have would fail for a reason unrelated to the model

`include_corr_pairlist` is left empty on purpose. Correlated-pair features would
add information the strategy never asked for, which is a change of substance
rather than of setup.
"""
import glob
import io
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT
FT_PYTHON = os.path.join(AUD, "ftenv", "Scripts", "python.exe")
OUT_DIR = os.path.join(ROOT, "repair", "results_freqai")
CFG_DIR = os.path.join(AUD, "user_data", "freqai_configs")

LADDER = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"]
RX_TF = re.compile(r"""^\s*timeframe\s*[:=]\s*['"]([^'"]+)['"]""", re.M)

IN_RANGE = "20180301-20200301"
OUT_RANGE = "20200301-20260820"


def available_timeframes():
    out = set()
    for f in glob.glob(os.path.join(AUD, "user_data", "data", "binance", "*.feather")):
        out.add(os.path.basename(f).replace(".feather", "").rsplit("-", 1)[1])
    return out


def build_config(name, base_tf, have):
    """One config per strategy: include_timeframes must start at its own."""
    base = json.load(io.open(os.path.join(AUD, "user_data", "config.json"),
                             encoding="utf-8"))
    idx = LADDER.index(base_tf) if base_tf in LADDER else 0
    tfs = [t for t in LADDER[idx:idx + 3] if t in have] or [base_tf]
    base["freqai"] = {
        "enabled": True,
        "identifier": "freqai_%s" % name,
        "train_period_days": 30,
        "backtest_period_days": 7,
        "purge_old_models": 2,
        "fit_live_predictions_candles": 300,
        "feature_parameters": {
            "include_timeframes": tfs,
            "include_corr_pairlist": [],
            "label_period_candles": 24,
            "include_shifted_candles": 2,
            # Must be > 0. FreqAI only computes the `DI_values` column when the
            # Dissimilarity Index is switched on, and 6 of the 8 strategies read
            # that column directly - with it off they die on KeyError('DI_values'),
            # which looks like a strategy defect and is a setting of ours.
            # 0.9 is freqtrade's own example value.
            "DI_threshold": 0.9,
            "weight_factor": 0.9,
            "principal_component_analysis": False,
            "use_SVM_to_remove_outliers": False,
            "indicator_periods_candles": [10, 20],
        },
        "data_split_parameters": {"test_size": 0.33, "random_state": 1},
        "model_training_parameters": {"n_estimators": 100, "verbosity": -1},
    }
    os.makedirs(CFG_DIR, exist_ok=True)
    p = os.path.join(CFG_DIR, "%s.json" % name)
    io.open(p, "w", encoding="utf-8").write(json.dumps(base, indent=2))
    return p


def strategy_dir(path):
    """Prefer the Class 2 overlay when a patched copy of this file exists.

    Without this the runner silently measures the unpatched original, which is
    how AstroQAV4 came back with the very KeyError its patch had already fixed.
    """
    patched = os.path.join(ROOT, "repair", "patched", path.replace("/", os.sep))
    if os.path.exists(patched):
        return os.path.dirname(patched), "class2-overlay"
    return os.path.dirname(os.path.join(AUD, path)), "original"


def run_one(job):
    name, path, base_tf, have = job
    cfg = build_config(name, base_tf, have)
    sdir, which = strategy_dir(path)
    res = {"strategy": name, "file": path, "run_class": "freqai",
           "source_tree": which,
           "config": os.path.relpath(cfg, AUD), "runs": {}}
    for label, rng in (("in_sample", IN_RANGE), ("out_sample", OUT_RANGE)):
        t0 = time.time()
        # Windows application control may block the generated freqtrade.exe
        # console launcher. Running the same installed package as a module uses
        # the identical ftenv without relying on that launcher executable.
        cmd = [FT_PYTHON, "-m", "freqtrade", "backtesting", "--config", cfg, "--strategy", name,
               "--strategy-path", sdir,
               "--freqaimodel", "LightGBMRegressor",
               "--timerange", rng, "--fee", "0.001"]
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONWARNINGS="ignore")
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=10800, env=env, cwd=AUD)
            out = (r.stdout + r.stderr).decode("utf-8", "replace")
        except subprocess.TimeoutExpired:
            res["runs"][label] = {"level": "NOT-APPLICABLE", "why": "TIMED OUT after 10800s"}
            continue

        def num(pat, cast=float):
            m = re.search(pat, out)
            return cast(m.group(1)) if m else None

        trades = num(r"Total/Daily Avg Trades\s*\S\s*(\d+)", int)
        if trades is None:
            # FreqAI requires every include_timeframes entry to be >= the
            # strategy's MAIN timeframe, and the main timeframe is what
            # freqtrade resolves, not necessarily what a `timeframe = ...` line
            # in the file says - Proton declares 3m and resolves to 5m. Rather
            # than guess, take the value out of the engine's own complaint and
            # rebuild the config once.
            mm = re.search(r"Main timeframe of (\S+) must be smaller or equal", out)
            if mm and not res.get("_tf_retried"):
                res["_tf_retried"] = True
                res["main_timeframe_from_engine"] = mm.group(1)
                cfg = build_config(name, mm.group(1), have)
                cmd[cmd.index("--config") + 1] = cfg
                try:
                    r = subprocess.run(cmd, capture_output=True, timeout=10800,
                                       env=env, cwd=AUD)
                    out = (r.stdout + r.stderr).decode("utf-8", "replace")
                    trades = num(r"Total/Daily Avg Trades\s*\S\s*(\d+)", int)
                except subprocess.TimeoutExpired:
                    trades = None

        if trades is None:
            err = re.findall(r"^([\w.]*(?:Error|Exception)): (.+)$", out, re.M)
            msg = ("%s: %s" % err[-1])[:160] if err else None
            if not msg:
                m = re.search(r"ERROR - (?:Configuration error: )?(.+)", out)
                msg = m.group(1).strip()[:160] if m else "no summary produced"
            res["runs"][label] = {"level": "NOT-APPLICABLE", "why": msg}
            continue
        res["runs"][label] = {
            "level": "PASSED",
            "elapsed_s": round(time.time() - t0, 1),
            "summary": {
                "trades": trades,
                "total_pct": num(r"Total profit %\s*\S\s*(-?[\d.]+)%"),
                "market_change_pct": num(r"Market change\s*\S\s*(-?[\d.]+)%"),
                "p_value": num(r"Mean profit p-value\s*\S\s*(-?[\d.eE+-]+)"),
            },
        }
        if res["runs"][label]["level"] != "PASSED":
            break

    os.makedirs(OUT_DIR, exist_ok=True)
    dst = os.path.join(OUT_DIR, "%s.json" % name)
    io.open(dst, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=2))
    i = res["runs"].get("in_sample", {})
    o = res["runs"].get("out_sample", {})
    return "%-24s in=%-15s out=%-15s %s" % (
        name[:24], i.get("level"), o.get("level"),
        (i.get("why") or "")[:60])


def main():
    have = available_timeframes()
    targets = []
    for line in io.open(sys.argv[1], encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        name, rel = line.split("\t")
        src = io.open(os.path.join(AUD, rel), encoding="utf-8", errors="replace").read()
        m = RX_TF.search(src)
        targets.append((name, rel, m.group(1) if m else "5m", have))
    workers = int(os.environ.get("FREQAI_WORKERS", "3"))
    print("freqai strategies %d | workers %d | timeframes present %s"
          % (len(targets), workers, ",".join(sorted(have))), flush=True)
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(run_one, t) for t in targets]
        for f in as_completed(futs):
            done += 1
            print("[%d/%d] %s" % (done, len(targets), f.result()), flush=True)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
