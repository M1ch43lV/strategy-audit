# -*- coding: utf-8 -*-
"""Measure Wave C rows whose timeframe is evidenced, not guessed.

48 Wave C rows declare no timeframe and freqtrade refuses to run them. For four
of them the author's value is recoverable from evidence rather than invented:

* `ADX_15M_USDT`, `ADX_15M_USDT2` carry `15M` in the author's own class name.
* `FixedRiskRewardLoss` and `JustROCR5` have near-identical twin copies
  elsewhere in the corpus that do declare a timeframe; the twins match the
  canonical file at 1.00 and 0.98 similarity respectively.

The remaining 44 have no recoverable value and are deliberately absent. The
timeframe decides a strategy's whole behaviour, so supplying one from nothing
would measure a strategy that never existed.

The evidence and its source are stored with every result.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys

import profile_smoke


ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(ROOT, "ELIGIBILITY_TIMEFRAME_EVIDENCE.json")
TIMERANGE = "20200301-20200401"

EVIDENCE = {
    "ADX_15M_USDT": ("15m", "author_class_name",
                     "the author's own name states 15M"),
    "ADX_15M_USDT2": ("15m", "author_class_name",
                      "the author's own name states 15M"),
    "FixedRiskRewardLoss": ("5m", "corpus_twin",
                            "repos/davidzr_freqtrade-strategies/strategies/"
                            "FixedRiskRewardLoss/FixedRiskRewardLoss.py, similarity 1.00"),
    "JustROCR5": ("1m", "corpus_twin",
                  "three independent twins declare 1m, similarity 0.98"),
}


def _load():
    if not os.path.exists(OUTPUT):
        return {"schema_version": 1, "timerange": TIMERANGE,
                "arm": "wave_c_evidenced_timeframe", "results": {}}
    return json.load(io.open(OUTPUT, encoding="utf-8"))


def _write(data):
    tmp = OUTPUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, OUTPUT)


def rows():
    manifest = {row["strategy_id"]: row
                for row in profile_smoke.read_manifest(profile_smoke.MANIFEST)}
    return [(manifest[name], EVIDENCE[name]) for name in sorted(EVIDENCE)
            if name in manifest]


def run(timeout):
    data = _load()
    queue = [(row, ev) for row, ev in rows()
             if row["strategy_id"] not in data["results"]]
    print("evidenced rows: %d, pending: %d" % (len(rows()), len(queue)), flush=True)
    for number, (row, (timeframe, kind, source)) in enumerate(queue, 1):
        strategy = row["strategy_id"]
        result = profile_smoke.run_one(row, TIMERANGE, timeout,
                                       config_overrides={"timeframe": timeframe})
        try:
            result.update(profile_smoke._identity(row))
        except (OSError, ValueError, KeyError) as exc:
            result["identity_error"] = "%s: %s" % (type(exc).__name__, exc)
        result.update({
            "timeframe": timeframe,
            "timeframe_evidence": kind,
            "timeframe_evidence_source": source,
            "runtime_id": os.environ.get("PROFILE_RUNTIME_ID", "native_unversioned"),
        })
        data["results"][strategy] = result
        _write(data)
        print("[%d/%d] %-24s tf=%-4s %-9s %s" %
              (number, len(queue), strategy, timeframe, result["status"],
               result.get("trades", result.get("why", ""))), flush=True)
    print("evidenced timeframe results: %d" % len(data["results"]))


def selftest():
    known = {name for name, _ in ((k, v) for k, v in EVIDENCE.items())}
    assert known == set(EVIDENCE)
    for name, (tf, kind, source) in EVIDENCE.items():
        assert tf.endswith(("m", "h")) and source, name
        assert kind in ("author_class_name", "corpus_twin"), name
    assert len(rows()) == 4, len(rows())
    print("eligibility_timeframe_evidence selftest: PASS (%d rows)" % len(rows()))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=900)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    run(args.timeout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
