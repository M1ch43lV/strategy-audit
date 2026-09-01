# -*- coding: utf-8 -*-
"""Current status of every strategy, as an overlay on the frozen baseline.

`REGIME_ELIGIBILITY.csv` is E0 and is deliberately never regenerated: it is the
baseline every published figure is bound to. That means it cannot answer "what
do we know about this strategy today", and after four expansion waves the
answer lives scattered across the smoke, bias, full-window, adjudication and
convergence stores. This file collects them into one reference without touching
E0.

Nothing here decides anything. Admission happens in
`eligibility_expansion_adjudicate.py` and nowhere else; this is a reading of
what has already been decided, regenerated from the evidence so it cannot
quietly go stale - which the canonical manifest did, listing 66 measured rows
as unmeasured for two days.
"""
from __future__ import annotations

import argparse
import collections
import csv
import datetime
import io
import json
import os
import re
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
ELIGIBILITY = os.path.join(ROOT, "REGIME_ELIGIBILITY.csv")
PROFILES = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
CANDIDATES = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_CANDIDATES.csv")
ADJUDICATION = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_ADJUDICATION.csv")
SMOKE = os.path.join(ROOT, "PROFILE_SMOKE.json")
BIAS = os.path.join(ROOT, "PROFILE_BIAS.json")
FULL_WINDOW = os.path.join(ROOT, "PROFILE_FULL_WINDOW.json")
CONVERGENCE = os.path.join(ROOT, "WARMUP_CONVERGENCE.json")
OUTPUT = os.path.join(ROOT, "STRATEGY_STATUS.csv")
REPORT = os.path.join(ROOT, "STRATEGY_STATUS.md")

FIELDS = [
    "strategy_id", "run_profile", "expansion_wave", "cohort", "measured",
    "observed_trades", "trade_evidence", "lookahead", "lookahead_evidence",
    "recursive", "recursive_evidence", "coverage_status", "traps_n", "artifact_role",
    "baseline_status", "primary_reason", "last_tested_at",
    "last_tested_source", "settled_startup", "settled_days", "settled_drift_pct",
    "needed_no_override", "evidence_paths", "open_work",
]

# Why a row does not pass, in decreasing order of finality. A row usually
# carries several reasons; the reference groups by the decisive one, because a
# list sorted by "lookahead_found; recursive_bias_found; no_trades" tells a
# reader nothing they can act on. Order matters: a strategy that reads future
# candles is out regardless of how clean its warm-up is, so look-ahead outranks
# recursion, and both outrank the absence of a measurement.
REASON_ORDER = (
    ("lookahead_found", "reads data it could not have had at the time"),
    ("behavior_changed_primary_exclusion", "repaired in a way that changed behaviour"),
    ("technical_trap_found", "carries a published backtesting trap"),
    ("recursive_bias_found",
     "indicator value still drifts at every warm-up the ladder can reach"),
    ("recursive_bias_unverified",
     "recorded under a parser defect and not re-measured; not a finding"),
    ("no_trades_in_full_measurement", "never trades over the full window"),
    ("canonical_implementation_not_measured", "never ran"),
    ("no_verdict_on_lookahead_and_recursive", "measured; neither gate returned a verdict"),
    ("no_verdict_on_lookahead", "measured and recursion clean; look-ahead has no verdict"),
    ("no_verdict_on_recursive", "measured and look-ahead clean; recursion has no verdict"),
)

# The runners do not stamp a time into their records, so it is recovered from
# what they do leave behind. An archive filename carries the run's own clock; a
# log file's modification time is close but is the file's time, not the run's.
# Where neither exists the field stays empty rather than being invented.
_ARCHIVE_TIME = re.compile(r"-(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})\.zip$")

CORPUS = os.path.join(ROOT, "corpus")
LEDGER = os.path.join(ROOT, "LEDGER.csv")
_CARD_ERROR = re.compile(r"## Could not be measured\s*\n+```\s*\n(.+?)\n", re.S)


def card_error(strategy):
    """The error the corpus sweep recorded for a strategy it could not run.

    Every one of the 900 rows was attempted at least once, in the corpus sweep
    if nowhere else, and each failure named its exception on the strategy's
    card. Reporting a row as untested because this audit's newer stores hold no
    record for it would discard evidence that exists.
    """
    path = os.path.join(CORPUS, strategy + ".md")
    if not os.path.isfile(path):
        return ""
    match = _CARD_ERROR.search(
        io.open(path, encoding="utf-8", errors="replace").read())
    return match.group(1).strip()[:160] if match else ""


def _csv(path):
    if not os.path.exists(path):
        return []
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _json(path, key="results"):
    if not os.path.exists(path):
        return {}
    return json.load(io.open(path, encoding="utf-8")).get(key, {})


def _integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _mtime(relative):
    path = os.path.join(ROOT, (relative or "").replace("/", os.sep))
    if not relative or not os.path.isfile(path):
        return None
    stamp = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    return stamp.replace(microsecond=0).isoformat(sep=" ")


def tested_at(records):
    """Best available run time, plus the evidence it was taken from.

    Returns `(timestamp, source)`. An archive name is the run's own clock and
    is preferred; a log file's modification time is the file's, which is close
    but not the same thing, and it is labelled so nobody reads it as exact.
    """
    for record in records:
        match = _ARCHIVE_TIME.search(record.get("archive") or "")
        if match:
            date, hour, minute, second = match.groups()
            return "%s %s:%s:%s" % (date, hour, minute, second), "run_archive"
    newest, source = None, ""
    for record in records:
        stamp = _mtime(record.get("debug_log"))
        if stamp and (newest is None or stamp > newest):
            newest, source = stamp, "log_mtime"
    return newest or "", source


def evidence_paths(records):
    paths = []
    for record in records:
        for key in ("archive", "debug_log"):
            value = record.get(key)
            if value and value not in paths:
                paths.append(value)
    return paths


def rows():
    baseline = {r["strategy_id"]: r for r in _csv(ELIGIBILITY)}
    profiles = {r["strategy_id"]: r for r in _csv(PROFILES)}
    waves = {r["strategy_id"]: r for r in _csv(CANDIDATES)}
    admitted = {r["strategy_id"] for r in _csv(ADJUDICATION)
                if r["adjudication_status"] == "admitted_E1"}
    smoke = _json(SMOKE)
    bias = _json(BIAS)
    full = _json(FULL_WINDOW)
    convergence = _json(CONVERGENCE)

    out = []
    for strategy in sorted(profiles):
        profile = profiles[strategy]
        base = baseline.get(strategy, {})
        wave = waves.get(strategy, {}).get("expansion_wave", "")
        measurement = smoke.get(strategy) or {}
        window = full.get(strategy) or {}
        diagnostics = bias.get(strategy) or {}
        settled = convergence.get(strategy) or {}

        trades, source = "", ""
        if window.get("status") == "measured":
            trades, source = window.get("trades", ""), "full_window"
        elif measurement.get("status") == "measured":
            trades, source = measurement.get("trades", ""), "smoke"
        elif base.get("canonical_measured") == "true":
            trades, source = base.get("canonical_observed_trades", ""), "baseline"

        lookahead = ((diagnostics.get("lookahead") or {}).get("status")
                     or base.get("lookahead") or "")
        lookahead_evidence = ("native" if diagnostics.get("lookahead")
                              else (base.get("lookahead_evidence_source") or "missing"))
        recursive = ((diagnostics.get("recursive") or {}).get("status")
                     or base.get("recursive") or "")
        # Where a verdict comes from decides whether it may be shown as one.
        # The baseline can carry a PASS from the original corpus sweep for a
        # canonical implementation that was never measured: real evidence, but
        # about a different run and a different file selection. It is recorded
        # with its provenance rather than presented as this row's verdict.
        if diagnostics.get("recursive"):
            recursive_evidence = "native"
        elif base.get("canonical_measured") == "true":
            recursive_evidence = "baseline"
        else:
            recursive_evidence = base.get("recursive_evidence_source") or "missing"
        if settled.get("state") == "converged":
            # The ladder has re-measured this row, so the stored FOUND is the
            # superseded verdict and must not be shown as the current one. Two
            # different passes are possible and the difference is the whole
            # point of the amendment: a row inside the frozen 0.01 percent band
            # needed no relaxation at all, while one inside 1.0 percent is
            # admitted only under the wider band.
            drift = settled.get("max_drift_pct")
            recursive = ("PASS" if (drift or 0) < 0.01 else "PASS_1PCT")
            recursive_evidence = "convergence:%s%s" % (
                settled.get("chosen_startup_candle_count"),
                "" if settled.get("needed_no_override") else ":warmup_supplied")
        elif settled.get("state") == "not_converged_within_ladder":
            recursive_evidence = "convergence:not_settled"

        ran_here = bool(measurement or diagnostics or window or settled)
        if strategy in admitted:
            cohort = "E1_expanded"
        elif base.get("regime_eligible") == "true":
            cohort = "E0_strict67"
        elif settled.get("state") == "converged":
            cohort = "convergence_candidate"
        elif base.get("eligibility_status") == "pending_diagnostics":
            cohort = "pending"
        elif not ran_here and base.get("canonical_measured") != "true":
            # Not "untested". Every row was attempted in the corpus sweep, and
            # these are the ones that never produced a usable measurement -
            # mostly because the file would not load at all. The card holds the
            # exception. Calling them untested would throw that evidence away.
            cohort = "attempted_no_measurement"
        else:
            cohort = "excluded"

        reason = ""
        if cohort in ("excluded", "pending"):
            reasons = set(filter(None,
                                 (base.get("exclusion_reasons") or "").split(";")))
            # Evidence gathered since the freeze outranks the frozen reason.
            if lookahead == "FOUND":
                reasons.add("lookahead_found")
            if recursive == "FOUND":
                reasons.add("recursive_bias_found")
            if measurement.get("status") == "measured":
                reasons.discard("canonical_implementation_not_measured")
            # A recursion label is only as good as the measurement behind it,
            # and the measurement behind most of them is known to be defective:
            # the parser read the drift at 199 candles instead of at the
            # strategy's own warm-up, which flipped the verdict for 47 of 302
            # logs, every one of them from excluded to clean. A row is only
            # confirmed once the convergence ladder has failed to settle it.
            if "recursive_bias_found" in reasons \
                    and settled.get("state") != "not_converged_within_ladder":
                reasons.discard("recursive_bias_found")
                reasons.add("recursive_bias_unverified")
            for key, _text in REASON_ORDER:
                if key in reasons:
                    reason = key
                    break
            if not reason and cohort == "pending":
                reason = "pending_diagnostics"
            if not reason and window.get("status") == "measured" \
                    and _integer(window.get("trades")) == 0:
                # Measured over the whole window and it never traded. The
                # frozen reason cannot say this: at the freeze it had not run.
                reason = "no_trades_in_full_measurement"
            if not reason and "NA" in (lookahead, recursive):
                # Measured, but at least one gate produced no verdict. That is
                # not a finding against the strategy and must not read as one.
                missing = [name for name, value in
                           (("lookahead", lookahead), ("recursive", recursive))
                           if value == "NA"]
                reason = "no_verdict_on_" + "_and_".join(missing)
            if not reason:
                reason = "; ".join(sorted(reasons)) or "unclassified"
        elif cohort == "attempted_no_measurement":
            reason = card_error(strategy) or "attempted, no measurement recorded"

        open_work = []
        if cohort == "convergence_candidate":
            open_work.append("paired_full_window_equivalence")
            if lookahead not in ("PASS", "FOUND"):
                open_work.append("lookahead_verdict")
        elif cohort == "attempted_no_measurement":
            open_work.append("retry_under_current_runtime")
        elif cohort == "excluded" and settled.get("state") in (
                "not_converged_within_ladder", "inconclusive"):
            open_work.append("convergence_" + settled["state"])

        records = [measurement, diagnostics, window, settled,
                   (diagnostics.get("lookahead") or {}),
                   (diagnostics.get("recursive") or {})]
        stamp, stamp_source = tested_at(records)

        out.append({
            "strategy_id": strategy,
            "run_profile": profile.get("run_profile", ""),
            "expansion_wave": wave,
            "cohort": cohort,
            "measured": "true" if (measurement.get("status") == "measured"
                                   or base.get("canonical_measured") == "true")
                        else "false",
            "observed_trades": trades,
            "trade_evidence": source,
            "lookahead": lookahead,
            "lookahead_evidence": lookahead_evidence,
            "recursive": recursive,
            "recursive_evidence": recursive_evidence,
            "coverage_status": base.get("coverage_status", ""),
            "traps_n": base.get("traps_n", ""),
            "artifact_role": profile.get("artifact_role", ""),
            "baseline_status": base.get("eligibility_status", ""),
            "primary_reason": reason,
            "last_tested_at": stamp,
            "last_tested_source": stamp_source,
            "settled_startup": settled.get("chosen_startup_candle_count", ""),
            "settled_days": settled.get("chosen_ladder_days", ""),
            "settled_drift_pct": settled.get("max_drift_pct", ""),
            "needed_no_override": ("true" if settled.get("needed_no_override")
                                   else ("false" if settled.get("state") == "converged"
                                         else "")),
            "evidence_paths": ";".join(evidence_paths(records)),
            "open_work": ";".join(open_work),
        })
    return out


def _csv_bytes(data):
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(data)
    return handle.getvalue().encode("utf-8")


def _table(counter, title, key_name):
    lines = ["| %s | Strategies |" % key_name, "|---|---:|"]
    for key, count in counter.most_common():
        lines.append("| `%s` | %d |" % (key or "(none)", count))
    return [title, ""] + lines + [""]


def _names(strategies, per_line=4):
    """A long name list as a readable block rather than one unbroken line."""
    lines, batch = [], sorted(strategies)
    for start in range(0, len(batch), per_line):
        lines.append(", ".join("`%s`" % name
                               for name in batch[start:start + per_line]))
    return lines


def _report(data):
    cohorts = collections.Counter(row["cohort"] for row in data)
    waves = collections.Counter(row["expansion_wave"] for row in data)
    work = collections.Counter(w for row in data
                               for w in row["open_work"].split(";") if w)
    measured = sum(1 for row in data if row["measured"] == "true")
    traded = sum(1 for row in data if _integer(row["observed_trades"]) > 0)
    stamped = sum(1 for row in data if row["last_tested_at"])
    passing = [r for r in data if r["cohort"] in ("E0_strict67", "E1_expanded")]
    candidates = [r for r in data if r["cohort"] == "convergence_candidate"]
    pending = [r for r in data if r["cohort"] == "pending"]
    untested = [r for r in data if r["cohort"] == "attempted_no_measurement"]
    failing = [r for r in data if r["cohort"] == "excluded"]
    now = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")

    lines = [
        "# Strategy status - current evidence for all %d rows" % len(data), "",
        "**Generated %s by `strategy_status.py`.** Regenerate it rather than "
        "editing it." % now, "",
        "**This table decides nothing.** Admission happens only in",
        "`eligibility_expansion_adjudicate.py`; this is a reading of what has",
        "already been decided, collected from the smoke, bias, full-window,",
        "adjudication and convergence stores.", "",
        "`REGIME_ELIGIBILITY.csv` remains the frozen E0 baseline and is never",
        "regenerated. Where this table and E0 disagree, E0 is not wrong: it is",
        "the state at the freeze, and the difference is the expansion.", "",
        "**On the run times.** The runners do not stamp a time into their",
        "records, so `last_tested_at` is recovered from what they leave behind:",
        "a result archive's filename, which carries the run's own clock, or",
        "failing that a log file's modification time, which is close but is the",
        "file's time and is labelled `log_mtime` for that reason. %d of %d rows"
        % (len(data) - stamped, len(data)),
        "have neither and are left empty rather than given an invented time.", "",
        "## Measurement", "",
        "| | Strategies |", "|---|---:|",
        "| in the manifest | %d |" % len(data),
        "| measured at all | %d |" % measured,
        "| produced trades | %d |" % traded,
        "| carrying a run time | %d |" % stamped,
        "",
    ]
    lines += _table(cohorts, "## Cohort", "Cohort")

    lines += [
        "## Passing - %d strategies" % len(passing), "",
        "Every original gate returned `PASS`: measured in its native mode,",
        "produced trades, clean look-ahead and recursion, complete candle",
        "coverage, no published trap.", "",
        "| Strategy | Profile | Cohort | Trades | Recursive evidence | Tested | Results |",
        "|---|---|---|---:|---|---|---|",
    ]
    for row in sorted(passing, key=lambda r: (r["cohort"], r["strategy_id"])):
        paths = [p for p in row["evidence_paths"].split(";") if p]
        lines.append("| `%s` | `%s` | `%s` | %s | `%s` | %s | %s |" % (
            row["strategy_id"], row["run_profile"], row["cohort"],
            row["observed_trades"], row["recursive_evidence"],
            row["last_tested_at"] or "-",
            "`%s`" % paths[0] if paths else "-"))
    lines.append("")

    if candidates:
        store = _json(CONVERGENCE)
        lines += [
            "## Convergence candidates - %d strategies" % len(candidates), "",
            "A warm-up exists at which every indicator stays inside the band.",
            "That is not admission: the paired full-window run must still show",
            "an identical trade list.", "",
            "| Strategy | Profile | Chosen warm-up | Worst drift | Tested | Results |",
            "|---|---|---|---|---|---|",
        ]
        for row in sorted(candidates, key=lambda r: r["strategy_id"]):
            record = store.get(row["strategy_id"], {})
            lines.append("| `%s` | `%s` | %s candles | %s%% on `%s` | %s | `%s` |" % (
                row["strategy_id"], row["run_profile"],
                record.get("chosen_startup_candle_count", "?"),
                record.get("max_drift_pct", "?"),
                record.get("max_drift_indicator", "?"),
                row["last_tested_at"] or "-",
                record.get("debug_log", "-")))
        lines.append("")

    if pending:
        lines += [
            "## Pending - %d strategies" % len(pending), "",
            "No hard failure and no verdict. Evidence is missing, which is",
            "neither a pass nor a fail.", "",
        ]
        lines += _names([row["strategy_id"] for row in pending])
        lines.append("")

    if untested:
        lines += [
            "## Attempted, no measurement - %d strategies" % len(untested), "",
            "Nothing in this corpus is untested. Every one of the 900 rows was",
            "attempted in the corpus sweep, and these are the ones that never",
            "produced a usable measurement - mostly because the file would not",
            "load at all. Each carries the exception its card recorded, so the",
            "failure is a fact about the strategy rather than a gap in the",
            "audit. They stay listed because a runtime change can revive one.", "",
            "| Strategy | Wave | Recorded failure |", "|---|---|---|",
        ]
        for row in sorted(untested, key=lambda r: (r["expansion_wave"],
                                                   r["strategy_id"])):
            lines.append("| `%s` | `%s` | `%s` |" % (
                row["strategy_id"], row["expansion_wave"] or "-",
                row["primary_reason"].replace("|", "\\|")))
        lines.append("")

    texts = dict(REASON_ORDER)
    grouped = collections.defaultdict(list)
    for row in failing:
        grouped[row["primary_reason"]].append(row["strategy_id"])
    lines += [
        "## Not passing - %d strategies, by decisive reason" % len(failing), "",
        "A row usually fails several gates. It is grouped by the most final",
        "one: a strategy that reads future candles is out however clean its",
        "warm-up is.", "",
        "**`recursive_bias_unverified` is not a finding.** The parser that",
        "produced most recursion verdicts read the drift at 199 candles rather",
        "than at the strategy's own warm-up, because the analyzer sorts its",
        "columns by value and the strategy's column moves. Across 302 retained",
        "logs the correction flipped 47 verdicts, every one of them from",
        "excluded to clean. A recursion label therefore counts as confirmed",
        "only where the convergence ladder has since failed to settle the row;",
        "everywhere else it says what it is - a record made under a known",
        "defect, awaiting re-measurement.", "",
        "| Reason | Meaning | Strategies |", "|---|---|---:|",
    ]
    ordered = [key for key, _t in REASON_ORDER if key in grouped]
    ordered += sorted(key for key in grouped if key not in texts)
    for key in ordered:
        lines.append("| `%s` | %s | %d |"
                     % (key, texts.get(key, "-"), len(grouped[key])))
    lines.append("")
    # Reason against wave. The waves are the units the expansion protocol works
    # in, so this is the table that says which wave is worth another pass and
    # which is exhausted.
    wave_names = sorted({row["expansion_wave"] for row in failing})
    lines += [
        "", "### Reason by wave", "",
        "| Reason | " + " | ".join("`%s`" % (w or "-") for w in wave_names) + " |",
        "|---" * (len(wave_names) + 1) + "|",
    ]
    for key in ordered:
        counts = collections.Counter(
            row["expansion_wave"] for row in failing
            if row["primary_reason"] == key)
        lines.append("| `%s` | %s |" % (key, " | ".join(
            str(counts.get(w, 0)) for w in wave_names)))
    lines.append("")

    for key in ordered:
        lines += ["### `%s` - %d" % (key, len(grouped[key])), ""]
        if key in texts:
            lines += [texts[key].capitalize() + ".", ""]
        by_wave = collections.defaultdict(list)
        for row in failing:
            if row["primary_reason"] == key:
                by_wave[row["expansion_wave"]].append(row["strategy_id"])
        for wave in sorted(by_wave):
            lines += ["Wave `%s` - %d:" % (wave or "-", len(by_wave[wave])), ""]
            lines += _names(by_wave[wave])
            lines.append("")

    lines += _table(waves, "## Expansion wave", "Wave")
    if work:
        lines += _table(work, "## Open work", "Item")
    lines += [
        "Per-row detail, including every evidence path, is in",
        "`STRATEGY_STATUS.csv`.", "",
    ]
    return chr(10).join(lines).encode("utf-8")


def _write(path, content):
    tmp = path + ".tmp"
    with io.open(tmp, "wb") as handle:
        handle.write(content)
    os.replace(tmp, path)


def selftest():
    data = rows()
    assert len(data) == 900, len(data)
    assert len({row["strategy_id"] for row in data}) == 900
    baseline = {r["strategy_id"]: r for r in _csv(ELIGIBILITY)}
    frozen = {s for s, r in baseline.items() if r["regime_eligible"] == "true"}
    assert len(frozen) == 67, len(frozen)
    listed = {row["strategy_id"] for row in data if row["cohort"] == "E0_strict67"}
    admitted = {r["strategy_id"] for r in _csv(ADJUDICATION)
                if r["adjudication_status"] == "admitted_E1"}
    # An admitted row leaves the baseline cohort rather than being counted twice.
    assert listed == frozen - admitted, sorted(listed ^ (frozen - admitted))
    assert {row["strategy_id"] for row in data
            if row["cohort"] == "E1_expanded"} == admitted

    for row in data:
        if row["cohort"] in ("excluded", "pending", "attempted_no_measurement"):
            assert row["primary_reason"], row["strategy_id"]
        else:
            assert not row["primary_reason"], row["strategy_id"]
        # A row measured since the freeze is never still listed as never run.
        if row["measured"] == "true":
            assert row["primary_reason"] != "canonical_implementation_not_measured", \
                row["strategy_id"]
        # This cohort means "attempted and produced nothing", never "untested".
        if row["cohort"] == "attempted_no_measurement":
            assert row["measured"] == "false", row["strategy_id"]
            assert not row["evidence_paths"], row["strategy_id"]
        # A row the ladder settled must not still carry the superseded verdict.
        if row["cohort"] == "convergence_candidate":
            assert row["recursive"] in ("PASS", "PASS_1PCT"),                 (row["strategy_id"], row["recursive"])
            assert row["settled_startup"] != "", row["strategy_id"]
        # A recovered timestamp always names where it came from.
        assert bool(row["last_tested_at"]) == bool(row["last_tested_source"]), \
            row["strategy_id"]

    ledger = {r["strategy"] for r in _csv(LEDGER)}
    # The corpus sweep attempted everything, so nothing may be reported as
    # never looked at. 895 of the 900 are in that ledger; the five that are not
    # are the hand-picked case studies under results/.
    assert len(ledger) == 895, len(ledger)
    for row in data:
        if row["cohort"] == "attempted_no_measurement":
            assert row["strategy_id"] in ledger, row["strategy_id"]
    print("strategy_status selftest: PASS (%d rows, %d E0, %d E1, %d unmeasured, "
          "%d timestamped)"
          % (len(data), len(listed), len(admitted),
             sum(1 for r in data if r["cohort"] == "attempted_no_measurement"),
             sum(1 for r in data if r["last_tested_at"])))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    data = rows()
    rendered = {OUTPUT: _csv_bytes(data), REPORT: _report(data)}
    if args.check:
        # The report embeds its generation time, so it is stale by definition
        # a second after it is written. Only the row data is compared.
        current = io.open(OUTPUT, "rb").read() if os.path.exists(OUTPUT) else b""
        if current != rendered[OUTPUT]:
            print("stale: %s" % os.path.relpath(OUTPUT, ROOT))
            return 1
        print("strategy status: current")
        return 0
    for path, content in rendered.items():
        _write(path, content)
    counts = collections.Counter(row["cohort"] for row in data)
    for cohort, count in counts.most_common():
        print("%s: %d" % (cohort, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
