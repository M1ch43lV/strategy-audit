# -*- coding: utf-8 -*-
"""Recover the author's timeframe where it exists, and refuse where it does not.

48 rows stop with `Timeframe needs to be set in either configuration or as cli
argument`. That is the largest single family of runtime failures in the corpus,
and none of it is a statement about the strategies: freqtrade will not start
without a timeframe, so nothing about them has ever been measured.

WHY MOST OF THEM ARE RECOVERABLE. 37 of the 48 declare the value in their own
file, under freqtrade's older name for the attribute:

    ticker_interval = '5m'

`ticker_interval` was renamed to `timeframe` in freqtrade 2021.4 and the old
name is no longer read, so a strategy written before that rename declares its
timeframe and is refused for it anyway. Carrying the value across is not a
guess about the author's intent - it is the author's own literal, under the
name it had when they wrote it. The rule reproduces three of the four values
that were derived by hand for `eligibility_timeframe_evidence` (`15m`, `15m`,
`1m`) without being told them, which is the check worth having on it.

WHY THE REST ARE NOT. The timeframe decides everything a strategy does, so a
value we invent measures a strategy that never existed. Eleven rows are
therefore refused, each for a stated reason:

* four declare only `informative_timeframe` - the higher timeframe pulled in
  alongside the base one. It is a different value and the base is not stated.
* five are FreqAI strategies that take the timeframe from the freqai config
  block, not from the strategy.
* `ScalpingCCI` declares `ticker_interval = '15'` with no unit, and its own
  code branches on whether the string contains "m".
* `FixedRiskRewardLoss` has no declaration at all; its `5m` comes from a
  corpus twin matching at 1.00 similarity and is carried here as the manual
  entry it has always been.

TWO STAGES. A recovered timeframe first has to produce a measurement at all
(`--stage smoke`); only then are the bias gates worth running (`--stage gates`).
Both write here, and the gate runs use a per-strategy config so that this
runner never touches the shared spot config another runner may be using.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import sys

import profile_bias
import profile_smoke


ROOT = os.path.dirname(os.path.abspath(__file__))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_TIMEFRAME_REPAIR.json")
TIMERANGE = "20200301-20200401"

FAILURE = "Timeframe needs to be set"

# freqtrade's own literal, under the name it had before the 2021.4 rename.
_TICKER = re.compile(
    r"^\s*ticker_interval\s*(?::\s*[A-Za-z_.\[\]]+\s*)?=\s*[\"']([0-9]+[mhdwM])[\"']",
    re.M)
_INFORMATIVE = re.compile(r"^\s*informative_timeframe\s*=", re.M)
_FREQAI = re.compile(r"freqai", re.I)

VALID = ("1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h",
         "1d", "3d", "1w", "1M")

# Evidence that is not in the file and cannot be derived from it. Kept from
# eligibility_timeframe_evidence, where it was established, with its source.
MANUAL = {
    "FixedRiskRewardLoss": (
        "5m", "corpus_twin",
        "repos/davidzr_freqtrade-strategies/strategies/FixedRiskRewardLoss/"
        "FixedRiskRewardLoss.py, similarity 1.00"),
}


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _load():
    if not os.path.exists(OUTPUT):
        return {"schema_version": 1, "timerange": TIMERANGE,
                "arm": "timeframe_recovered_from_author_declaration",
                "results": {}}
    return json.load(io.open(OUTPUT, encoding="utf-8"))


def _write(data):
    tmp = OUTPUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, OUTPUT)


def derive(strategy, source_file):
    """(timeframe, kind, source) if the author stated it, else (None, "", why).

    Rules are tried in order of how directly they carry the author's own
    words. Nothing here reasons about what a timeframe *ought* to be.
    """
    if not source_file or not os.path.isfile(source_file):
        return None, "", "canonical file not found: %s" % source_file
    text = io.open(source_file, encoding="utf-8", errors="replace").read()

    match = _TICKER.search(text)
    if match:
        value = match.group(1)
        if value not in VALID:
            return None, "", ("declares ticker_interval = %r, which freqtrade "
                              "does not accept as a timeframe" % value)
        line = next((n for n, text_line in enumerate(text.splitlines(), 1)
                     if _TICKER.match(text_line)), 0)
        return value, "author_ticker_interval", (
            "%s:%d declares ticker_interval = '%s'; freqtrade renamed the "
            "attribute to timeframe in 2021.4 and no longer reads the old name"
            % (source_file.replace(os.sep, "/"), line, value))

    if strategy in MANUAL:
        return MANUAL[strategy]

    # Refusals, each naming what was found instead.
    if re.search(r"^\s*ticker_interval\s*=", text, re.M):
        stated = re.search(r"^\s*ticker_interval\s*=\s*(.+)$", text, re.M)
        return None, "", ("declares ticker_interval = %s, which carries no "
                          "unit and cannot be read as a timeframe"
                          % (stated.group(1).strip() if stated else "?"))
    if _FREQAI.search(text):
        return None, "", ("a FreqAI strategy: the timeframe comes from the "
                          "freqai block of the config, not from the strategy")
    if _INFORMATIVE.search(text):
        return None, "", ("declares only informative_timeframe, which is the "
                          "higher timeframe pulled in alongside the base one; "
                          "the base timeframe is not stated")
    return None, "", "no timeframe declaration of any kind in the file"


def cohort():
    """Every row stopped by a missing timeframe, with what could be recovered.

    Re-derived from the status table on every call, so a row repaired since
    drops out on its own rather than being carried in a list.
    """
    profiles = {row["strategy_id"]: row for row in _csv(PROFILES)}
    out = []
    for row in _csv(STATUS):
        if FAILURE not in (row["runtime_failure"] or ""):
            continue
        strategy = row["strategy_id"]
        if strategy not in profiles:
            continue
        timeframe, kind, why = derive(strategy, row["source_file"])
        out.append((profiles[strategy], timeframe, kind, why))
    return out


def _record(row, timeframe, kind, source):
    record = {"strategy_id": row["strategy_id"],
              "timeframe": timeframe,
              "timeframe_evidence": kind,
              "timeframe_evidence_source": source,
              "runtime_id": os.environ.get("PROFILE_RUNTIME_ID",
                                           "native_unversioned")}
    try:
        record.update(profile_smoke._identity(row))
    except (OSError, ValueError, KeyError) as exc:
        record["identity_error"] = "%s: %s" % (type(exc).__name__, exc)
    return record


def record_refusals():
    """Persist why a blocked row was not repaired, next to the repairs.

    A refusal that lives only in a function is invisible to every reader of
    the table: those rows kept reading "to be fixed" while this route had
    already declined them, with a reason, for good.
    """
    data = _load()
    refused = {}
    for row, timeframe, kind, why in cohort():
        if timeframe:
            continue
        refused[row["strategy_id"]] = {"why": why, "route": "timeframe_repair"}
    data["refused"] = refused
    _write(data)
    return refused


def run_smoke(limit, timeout):
    record_refusals()
    data = _load()
    queue = [(row, tf, kind, why) for row, tf, kind, why in cohort()
             if tf and row["strategy_id"] not in data["results"]]
    refused = [(row["strategy_id"], why) for row, tf, _k, why in cohort() if not tf]
    if limit:
        queue = queue[:limit]
    print("timeframe repair: %d rows blocked, %d recoverable, %d refused, "
          "running %d" % (len(cohort()), len(cohort()) - len(refused),
                          len(refused), len(queue)), flush=True)
    for number, (row, timeframe, kind, source) in enumerate(queue, 1):
        strategy = row["strategy_id"]
        result = profile_smoke.run_one(row, TIMERANGE, timeout,
                                       config_overrides={"timeframe": timeframe})
        result.update(_record(row, timeframe, kind, source))
        data["results"][strategy] = result
        _write(data)
        print("[%d/%d] %-34s tf=%-4s %-9s %s"
              % (number, len(queue), strategy, timeframe, result.get("status"),
                 result.get("trades", (result.get("why") or "")[:60])), flush=True)
    measured = sum(1 for r in data["results"].values()
                   if r.get("status") == "measured")
    print("measured %d of %d recorded" % (measured, len(data["results"])),
          flush=True)
    return 0


def run_gates(limit, timeout, fallback_timeout):
    """Both bias gates, for rows the recovered timeframe actually measured."""
    data = _load()
    profiles = {row["strategy_id"]: row for row, _t, _k, _w in cohort()}
    queue = [strategy for strategy, record in sorted(data["results"].items())
             if record.get("status") == "measured"
             and "lookahead" not in record and strategy in profiles]
    if limit:
        queue = queue[:limit]
    print("timeframe gates: %d measured, %d still to gate, running %d"
          % (sum(1 for r in data["results"].values()
                 if r.get("status") == "measured"),
             len(queue), len(queue)), flush=True)
    for number, strategy in enumerate(queue, 1):
        row = profiles[strategy]
        record = data["results"][strategy]
        overrides = {"timeframe": record["timeframe"]}
        for gate in ("lookahead", "recursive"):
            record[gate] = profile_bias.run_diagnostic(
                row, gate, timeout, fallback_timeout,
                config_overrides=overrides)
        _write(data)
        print("[%d/%d] %-34s la=%-5s rec=%-5s"
              % (number, len(queue), strategy,
                 record["lookahead"].get("status"),
                 record["recursive"].get("status")), flush=True)
    return 0


def selftest():
    rows = cohort()
    assert rows, "no blocked rows found - has the failure message changed?"
    recovered = [(r, t, k, w) for r, t, k, w in rows if t]
    refused = [(r, t, k, w) for r, t, k, w in rows if not t]
    assert len(recovered) + len(refused) == len(rows)
    for row, timeframe, kind, source in recovered:
        assert timeframe in VALID, (row["strategy_id"], timeframe)
        assert kind in ("author_ticker_interval", "corpus_twin"), kind
        assert source, row["strategy_id"]
    for _row, _tf, _kind, why in refused:
        # A refusal without a reason is indistinguishable from an oversight.
        assert why and len(why) > 20, why
    # The rule has to reproduce the values that were derived by hand, or it is
    # not reading the same evidence a person read.
    established = {"ADX_15M_USDT": "15m", "ADX_15M_USDT2": "15m",
                   "JustROCR5": "1m", "FixedRiskRewardLoss": "5m"}
    by_id = {row["strategy_id"]: tf for row, tf, _k, _w in rows}
    for strategy, expected in established.items():
        if strategy in by_id:
            assert by_id[strategy] == expected, (strategy, by_id[strategy])
    print("eligibility_timeframe_repair selftest: PASS "
          "(%d blocked, %d recoverable, %d refused with a reason)"
          % (len(rows), len(recovered), len(refused)))


def report():
    for row, timeframe, kind, why in cohort():
        if timeframe:
            print("%-38s %-5s %s" % (row["strategy_id"], timeframe, kind))
        else:
            print("%-38s %-5s %s" % (row["strategy_id"], "-", why[:80]))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="smoke",
                        choices=("smoke", "gates", "report"))
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--fallback-timeout", type=int, default=600)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if args.stage == "report":
        refused = record_refusals()
        print("recorded %d refusals" % len(refused))
        return report()
    if args.stage == "gates":
        return run_gates(args.limit, args.timeout, args.fallback_timeout)
    return run_smoke(args.limit, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
