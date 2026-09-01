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
# Wave B supplied a warm-up to strategies the analyzer had refused and
# re-ran the gate. Those verdicts were produced before the drift table was
# read correctly, so they are carried as provenance - a date, a log, a
# command - and never as a current verdict.
WAVE_B_WARMUP = os.path.join(ROOT, "ELIGIBILITY_EXPANSION_WARMUP.json")
# What stops each row that never ran, and whether repairing it would restore
# what the author wrote or invent something they did not.
BLOCKED_TRIAGE = os.path.join(ROOT, "BLOCKED_TRIAGE.json")
# A repaired row is measured by its own runner, into its own store. The smoke
# store holds the failure; this holds what happened once the obstacle was
# removed, and outranks it - the same precedence a native gate has over an
# inherited one, applied to the measurement instead of the verdict.
TIMEFRAME_REPAIR = os.path.join(ROOT, "ELIGIBILITY_TIMEFRAME_REPAIR.json")
MODULE_REPAIR = os.path.join(ROOT, "ELIGIBILITY_MODULE_REPAIR.json")
# Two later stores hold look-ahead measured natively for rows whose verdict was
# inherited or missing. They are separate files because they are separate
# cohorts, and forgetting to read one is how the newest evidence stops reaching
# this table while the table still claims to be current.
LOOKAHEAD_STORES = (
    os.path.join(ROOT, "ELIGIBILITY_LOOKAHEAD_BACKFILL.json"),
    os.path.join(ROOT, "ELIGIBILITY_EVIDENCE_GAP.json"),
)
OUTPUT = os.path.join(ROOT, "STRATEGY_STATUS.csv")
REPORT = os.path.join(ROOT, "STRATEGY_STATUS.md")

FIELDS = [
    "strategy_id", "repo", "source_file", "result_archive",
    "run_profile", "expansion_wave", "cohort", "measured",
    "observed_trades", "trade_evidence", "lookahead", "lookahead_evidence",
    "recursive", "recursive_evidence", "coverage_status", "traps_n", "artifact_role",
    "baseline_status", "primary_reason", "exclusion_basis",
    "repair_family", "repair_verdict",
    "runtime_failure", "evidence_gap",
    "last_tested_at",
    "last_tested_source", "settled_startup", "settled_days", "settled_drift_pct",
    "needed_no_override", "cmd_backtest", "cmd_lookahead", "cmd_recursive",
    "evidence_paths", "open_work",
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
    ("strategy_does_not_run",
     "fails before it can be measured; the message is in runtime_failure"),
    ("recursive_bias_found",
     "indicator value still drifts at every warm-up the ladder can reach"),
    ("recursive_bias_unverified",
     "recorded under a parser defect and not re-measured; not a finding"),
    ("recursive_warmup_refused",
     "the analyzer refused for want of a declared warm-up; nothing was measured"),
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

# The audit harness is written in Russian and stores Russian text in every
# result card. `repair/i18n.py` exists to render that as English and keeps the
# original beside it; reusing it is better than inventing a second, unverified
# mapping here. The card generator itself does not yet use it, which is why 872
# of the 896 cards still carry Cyrillic.
sys.path.insert(0, os.path.join(ROOT, "repair"))
import i18n

CORPUS = os.path.join(ROOT, "corpus")
LEDGER = os.path.join(ROOT, "LEDGER.csv")
_CARD_ERROR = re.compile(r"## Could not be measured\s*\n+```\s*\n(.+?)\n", re.S)


# Nothing recorded the freqtrade call until 2026-09-01, so most stored records
# predate it. The arguments are still knowable - they are fixed per gate and
# per run profile - but a reconstruction is not the same claim as a recording,
# and the two are never shown as if they were.
_RECONSTRUCTED = {
    "backtest": ("freqtrade backtesting --config {config} --strategy {strategy} "
              "--strategy-path {path} --timerange {timerange} --fee 0.001 "
              "--export trades --backtest-directory user_data/profile_smoke/"
              "{strategy} --cache none"),
    "lookahead": ("freqtrade lookahead-analysis --config {config} --strategy "
                  "{strategy} --strategy-path {path} --timerange {timerange} "
                  "--no-color"),
    "recursive": ("freqtrade recursive-analysis --config {config} --strategy "
                  "{strategy} --strategy-path {path} --timerange {timerange} "
                  "--no-color"),
}


def profile_bias_window(run_profile):
    """The frozen diagnostic window for a run profile."""
    return ("20200301-20200401" if (run_profile or "").startswith("futures_")
            else "20190101-20190401")


def _config_for(kind, profile):
    mode = "futures" if (profile or "").startswith("futures_") else "spot"
    if mode == "futures":
        return "user_data/profile_configs/futures_%s.json" % profile
    # The bias gates run against a config that forces price_side=other:
    # look-ahead analysis forces market orders and freqtrade will not evaluate
    # a signal without it. A backtest uses the plain config. Showing one
    # invocation for both gates hid exactly this difference.
    return ("user_data/config.json" if kind == "backtest"
            else "user_data/profile_configs/bias_spot.json")


def invocation(record, kind, profile, timerange, strategy, source_file,
               pairs=0):
    """The freqtrade call for ONE gate, labelled by where it comes from.

    A row can have three: a backtest, a look-ahead run and a recursion run. They
    differ in subcommand, in config and in flags, so a single column per row
    could only ever show one of them and silently drop the rest.

    The full-window backtest is eight calls, one per pair. Rendering eight
    command lines into a table cell is unreadable, so the pair is left as a
    placeholder and the count is stated; every individual call, with its own
    console output, is in `user_data/freqtrade_runs.log`.
    """
    stored = (record or {}).get("invocation")
    if stored:
        return "[recorded] " + stored
    template = _RECONSTRUCTED.get(kind)
    if not template or not timerange:
        return ""
    line = template.format(config=_config_for(kind, profile), strategy=strategy,
                           path=os.path.dirname(source_file) or ".",
                           timerange=timerange)
    if kind == "backtest" and pairs > 1:
        line += " --pairs {pair}   # %d pairs, one call each" % pairs
    return "[reconstructed] " + line


def provenance(canonical_file):
    """Owner/repository and source path, read off the canonical file itself.

    Deliberately not taken from the old ledger, which has a `repo` column: this
    is derivable from the manifest the current pipeline maintains, so the table
    gains provenance without gaining a dependency on the first study.
    """
    path = (canonical_file or "").replace("\\", "/")
    marker = "repos/"
    index = path.find(marker)
    if index < 0:
        return "", path
    stem = path[index + len(marker):].split("/")[0]
    owner, _sep, name = stem.partition("_")
    return ("%s/%s" % (owner, name) if name else stem), path


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
    if not match:
        return ""
    return i18n.translate(match.group(1).strip())[:160]


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


EXCLUSION_BASIS = {
    "own_measurement":
        "a disqualifying result measured here, from this implementation",
    "inherited":
        "the disqualifying result comes from the original sweep, not from a "
        "measurement of this implementation",
    "no_finding":
        "no disqualifying result at all - a gate returned nothing, or returned "
        "it under a known reader defect",
    "blocked":
        "the strategy did not run, so nothing about it was judged",
}


def exclusion_basis(reason, lookahead_evidence, trade_evidence):
    """What an exclusion actually rests on.

    The decisive reason says which gate stopped the row. It does not say
    whether that gate produced evidence, and those are different questions: a
    row excluded on `no_verdict_on_recursive` is excluded for the absence of a
    result, which is not the same standing as one excluded on a drift the
    ladder measured at every rung. Keeping the two apart is the difference
    between a finding and a gap in the work.
    """
    if not reason:
        return ""
    if reason.startswith("strategy_does_not_run") \
            or reason.startswith("no run under the current runtime"):
        return "blocked"
    if reason == "lookahead_found":
        return "own_measurement" if lookahead_evidence == "native" else "inherited"
    if reason == "no_trades_in_full_measurement":
        return "own_measurement" if trade_evidence == "full_window" else "inherited"
    if reason in ("recursive_bias_found", "technical_trap_found",
                  "behavior_changed_primary_exclusion"):
        return "own_measurement"
    if reason == "recursive_bias_unverified" \
            or reason == "recursive_warmup_refused" \
            or reason.startswith("no_verdict_on") \
            or reason == "canonical_implementation_not_measured":
        return "no_finding"
    return "no_finding"


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
    wave_b = _json(WAVE_B_WARMUP)
    triage = _json(BLOCKED_TRIAGE)
    repaired = dict(_json(TIMEFRAME_REPAIR))
    # Two repair runners, one precedence: whichever of them last produced a
    # measurement for a row replaces the failure the smoke store holds.
    for name, record in _json(MODULE_REPAIR).items():
        repaired.setdefault(name, record)
    # A native re-measurement outranks whatever PROFILE_BIAS or the baseline
    # holds: it is the same gate, measured later, from this implementation.
    remeasured = {}
    for store in LOOKAHEAD_STORES:
        for name, record in _json(store).items():
            gate = record.get("lookahead") or {}
            if gate.get("status") in ("PASS", "FOUND"):
                remeasured[name] = gate

    out = []
    for strategy in sorted(profiles):
        profile = profiles[strategy]
        base = baseline.get(strategy, {})
        wave = waves.get(strategy, {}).get("expansion_wave", "")
        measurement = smoke.get(strategy) or {}
        repair_run = repaired.get(strategy) or {}
        if repair_run.get("status") in ("measured", "failed"):
            # The obstacle is gone and the row produced trades. Continuing to
            # report the old failure would say the strategy does not run while
            # a run of it sits on disk.
            measurement = repair_run
        window = full.get(strategy) or {}
        diagnostics = bias.get(strategy) or {}
        settled = convergence.get(strategy) or {}
        warmup = wave_b.get(strategy) or {}
        attempt = (warmup.get("attempts") or {}).get(
            str(warmup.get("latest_startup_candle_count"))) or {}

        trades, source = "", ""
        if window.get("status") == "measured":
            trades, source = window.get("trades", ""), "full_window"
        elif measurement.get("status") == "measured":
            trades, source = measurement.get("trades", ""), "smoke"
        elif base.get("canonical_measured") == "true":
            trades, source = base.get("canonical_observed_trades", ""), "baseline"

        for gate in ("lookahead", "recursive"):
            if (repair_run.get(gate) or {}).get("status") in ("PASS", "FOUND"):
                diagnostics = dict(diagnostics)
                diagnostics[gate] = repair_run[gate]
        fresh = remeasured.get(strategy)
        lookahead = (fresh or diagnostics.get("lookahead") or {}).get("status")             or base.get("lookahead") or ""
        lookahead_evidence = ("native" if (fresh or diagnostics.get("lookahead"))
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
        # A FOUND inherited from a run that never got as far as measuring is
        # not a finding. `refused_no_warmup` records that the analyzer declined
        # the strategy because it declared no warm-up - the same non-finding
        # already corrected for the convergence candidates, still on the
        # inherited path for 47 rows. Naming it as what it is keeps the reader
        # from reading a missing precondition as detected bias.
        # Only where no ladder has run. Once it has, what it measured is
        # the answer, and "nothing was ever compared" would be false:
        # four rows said that while the ladder had in fact compared
        # every rung and found drift at all of them.
        if recursive == "FOUND" and not diagnostics.get("recursive") \
                and not settled \
                and base.get("recursive_kind") == "refused_no_warmup":
            recursive = "WARMUP_NEEDED"
            recursive_evidence += ":refused_no_warmup"
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
            # The ladder supplied warm-up after warm-up and the indicator kept
            # drifting. This is the one shape in which a recursion finding is
            # confirmed rather than inherited.
            recursive = "FOUND"
            recursive_evidence = "convergence:not_settled"
        elif attempt:
            # Measured here, at a supplied warm-up, but under the parser that
            # read the wrong table column and treated an undefined cell as a
            # clean one. Re-parsing the 106 wave B logs that survive overturns
            # 58 of them, every one from FOUND to "no verdict"; the runs that
            # produced the PASS verdicts kept no log at all and cannot be
            # re-parsed. So the attempt is shown as superseded and the row is
            # queued for the ladder rather than credited with its old result.
            recursive_evidence = "wave_b:%s:superseded" % (
                attempt.get("startup_candle_count"))

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
            # Untested under THIS pipeline, which is the only claim this table
            # is entitled to make. The original corpus sweep did attempt every
            # row, but it ran in an environment that did not establish the
            # preconditions this audit requires, so its outcome says nothing
            # about whether the strategy works here. Treating its verdict as
            # evidence would import exactly the assumption the re-measurement
            # exists to avoid.
            cohort = "not_tested_in_current_runtime"
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
            if recursive == "WARMUP_NEEDED":
                reasons.discard("recursive_bias_found")
                reasons.add("recursive_warmup_refused")
            if measurement.get("status") == "measured":
                reasons.discard("canonical_implementation_not_measured")
            if measurement and measurement.get("status") != "measured":
                # A strategy that will not run cannot be judged on anything
                # else, so this outranks every gate label - and in particular
                # outranks recursive_bias_unverified, which is a statement
                # about our own measurement rather than about the strategy.
                # The frozen baseline predates these runs, so it says only that
                # no measurement exists. It reads as "never ran", which is
                # wrong: the row did run here, on the date this table shows,
                # and it failed with a message nobody was reading. Saying what
                # actually happened is both truer and actionable - 48 of these
                # turn out to be blocked on nothing but a missing timeframe.
                reasons.discard("canonical_implementation_not_measured")
                failure = i18n.translate(measurement.get("why") or "").strip()
                if failure:
                    reasons.add("strategy_does_not_run")
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
        elif cohort == "not_tested_in_current_runtime":
            # The old card's exception is kept as a hint about what to expect,
            # never as a verdict: it was produced under different preconditions.
            hint = card_error(strategy)
            reason = ("no run under the current runtime"
                      + (" (historical hint: %s)" % hint if hint else ""))

        # An admitted row can still rest on the original author's sweep.
        # regime_eligibility.classify promotes a historical spot PASS to a
        # current one when no native verdict exists, and that sweep ran in an
        # environment which did not establish this audit's preconditions. The
        # row stays admitted - E0 is frozen and this table decides nothing -
        # but the gap is named where anyone reading the row will see it.
        gaps = []
        if cohort in ("E0_strict67", "E1_expanded"):
            if lookahead_evidence.startswith("historical"):
                gaps.append("lookahead_from_original_sweep")
            if recursive_evidence.startswith("historical"):
                gaps.append("recursive_from_original_sweep")

        open_work = []
        if gaps:
            open_work.append("re-measure_gates_in_current_runtime")
        if cohort == "convergence_candidate":
            open_work.append("paired_full_window_equivalence")
            if lookahead not in ("PASS", "FOUND"):
                open_work.append("lookahead_verdict")
        elif cohort == "not_tested_in_current_runtime":
            open_work.append("first_measurement_in_current_runtime")
        elif cohort == "excluded" and settled.get("state") in (
                "not_converged_within_ladder", "inconclusive"):
            open_work.append("convergence_" + settled["state"])
        if recursive == "WARMUP_NEEDED" or recursive_evidence.startswith("wave_b:")                 or (recursive in ("FOUND", "NA") and not settled
                    and recursive_evidence in ("native", "baseline")):
            # A recursion FOUND that no ladder has re-measured rests on the
            # parser that read the wrong column; an NA means the gate ran and
            # produced nothing to judge, usually because the indicators are
            # still undefined at the warm-up the strategy declares. Both are
            # questions for the ladder, not verdicts, so both are queued.
            open_work.append("recursive_ladder_pending")
        # An exclusion that does not rest on a measurement of this
        # implementation is an open question, and has to carry the work
        # that would settle it. Without this a row could sit in the
        # excluded list for good on an absent verdict, a verdict
        # borrowed from another environment, or a crash - and nothing
        # in the table would say so.
        basis = exclusion_basis(reason, lookahead_evidence, source) \
            if cohort in ("excluded", "pending") else ""
        # `excluded` is a verdict, and this audit does not issue a verdict on
        # somebody else's measurement or on the absence of one. A row whose
        # exclusion rests on an inherited result, or on no result at all, is
        # not excluded yet - it is unfinished, and says so until a measurement
        # of ours settles it. The decisive reason and the basis stay on the
        # row, so nothing is hidden by the change of name.
        if cohort == "excluded" and basis in ("inherited", "no_finding"):
            cohort = "exclusion_unconfirmed"
        repair = triage.get(strategy) or {}
        if basis == "blocked":
            # A blocked row that has been triaged says what would fix it. One
            # that has not says only that nobody has looked.
            open_work.append(repair.get("verdict") or "runtime_repair_pending")
        elif basis in ("inherited", "no_finding"):
            # Not only a borrowed verdict. A gate of ours that ran and
            # returned nothing - a timeout, an exception - has produced
            # no verdict either, and the row cannot rest on it.
            if lookahead_evidence != "native" \
                    or lookahead not in ("PASS", "FOUND"):
                open_work.append("lookahead_remeasure_pending")
            if reason == "no_trades_in_full_measurement" \
                    and source != "full_window":
                open_work.append("full_window_measurement_pending")

        records = [measurement, diagnostics, window, settled,
                   fresh or {}, (diagnostics.get("lookahead") or {}),
                   (diagnostics.get("recursive") or {}), attempt]
        stamp, stamp_source = tested_at(records)

        repo, source_file = provenance(profile.get("canonical_file"))
        run_profile = profile.get("run_profile")
        pairs = len((window.get("pair_results") or {}))
        # The full-window record is the better source for the backtest command
        # when it exists, because that run is the one measured over the whole
        # window; the smoke run is the shorter probe.
        backtest_record = window or measurement
        cmd_backtest = invocation(
            backtest_record, "backtest", run_profile,
            backtest_record.get("timerange") or measurement.get("timerange"),
            strategy, source_file, pairs)
        cmd_lookahead = invocation(
            fresh or diagnostics.get("lookahead") or {}, "lookahead", run_profile,
            (fresh or diagnostics.get("lookahead") or {}).get("timerange")
            or profile_bias_window(run_profile),
            strategy, source_file)
        cmd_recursive = invocation(
            settled or (diagnostics.get("recursive") or {}) or attempt,
            "recursive",
            run_profile,
            (settled.get("timerange")
             or (diagnostics.get("recursive") or {}).get("timerange")
             or attempt.get("timerange") or profile_bias_window(run_profile)),
            strategy, source_file)
        archive = next((p for p in evidence_paths(records) if p.endswith(".zip")), "")

        out.append({
            "strategy_id": strategy,
            "repo": repo,
            "source_file": source_file,
            "result_archive": archive,
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
            "exclusion_basis": basis,
            "repair_family": repair.get("family", ""),
            "repair_verdict": repair.get("verdict", ""),
            "primary_reason": reason,
            "runtime_failure": (i18n.translate(measurement.get("why") or "")[:160]
                                if measurement.get("status") not in (None, "measured")
                                else ""),
            "evidence_gap": ";".join(gaps),
            "last_tested_at": stamp,
            "last_tested_source": stamp_source,
            "settled_startup": settled.get("chosen_startup_candle_count", ""),
            "settled_days": settled.get("chosen_ladder_days", ""),
            "settled_drift_pct": settled.get("max_drift_pct", ""),
            "cmd_backtest": cmd_backtest,
            "cmd_lookahead": cmd_lookahead,
            "cmd_recursive": cmd_recursive,
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


def _links(row):
    """Relative links to what the run left behind.

    This file sits beside the paths it points at, so an editor or a repository
    view opens them directly. The freqtrade result archive comes first when one
    exists, because it is the run's actual output; the log is the fallback and
    is all that a failed run leaves.
    """
    parts = []
    if row["result_archive"]:
        parts.append("[archive](%s)" % row["result_archive"])
    for path in row["evidence_paths"].split(";"):
        if path and not path.endswith(".zip"):
            parts.append("[log](%s)" % path)
            break
    return " ".join(parts) or "-"


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
    untested = [r for r in data if r["cohort"] == "not_tested_in_current_runtime"]
    failing = [r for r in data if r["cohort"] == "excluded"]
    unconfirmed = [r for r in data if r["cohort"] == "exclusion_unconfirmed"]
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

    gates = ("cmd_backtest", "cmd_lookahead", "cmd_recursive")
    recorded = sum(1 for row in data for gate in gates
                   if row[gate].startswith("[recorded]"))
    total_cmds = sum(1 for row in data for gate in gates if row[gate])
    lines += [
        "## How freqtrade was called", "",
        "A result is not reproducible from its verdict alone, so each row",
        "carries the command it was produced by. **`recorded`** is the argv that",
        "actually ran. **`reconstructed`** is derived from the run profile and",
        "the window, because nothing stored the call before 2026-09-01; it is",
        "labelled because a reconstruction is a different claim from a",
        "recording. %d of %d commands are recorded so far, and every new run"
        % (recorded, total_cmds),
        "adds one.", "",
        "There is one column per gate, not one per row. A row can carry three",
        "calls and they differ in more than their subcommand, so a single",
        "column could only ever show one of them and drop the rest silently.",
        "The full-window backtest is eight calls, one per pair; the table",
        "leaves the pair as a placeholder and states the count, while every",
        "individual call with its own console output is in",
        "`user_data/freqtrade_runs.log`.", "",
        "The gates differ in more than their subcommand, which is the reason",
        "this is worth publishing at all. A backtest runs with",
        "`--fee 0.001 --export trades --cache none`. The bias gates add",
        "`--no-color` and use a config that forces `price_side=other`, because",
        "look-ahead analysis forces market orders and freqtrade will not",
        "evaluate a single signal without it. The warm-up ladder passes",
        "`--startup-candle` with every rung at once, which is why one run",
        "reports the whole ladder.", "",
        "## Passing - %d strategies" % len(passing), "",
        "Every original gate returned `PASS`: measured in its native mode,",
        "produced trades, clean look-ahead and recursion, complete candle",
        "coverage, no published trap.", "",
        "| Strategy | Profile | Cohort | Trades | Recursive evidence | Tested | Results |",
        "|---|---|---|---:|---|---|---|",
    ]
    for row in sorted(passing, key=lambda r: (r["cohort"], r["strategy_id"])):
        lines.append("| `%s` | `%s` | `%s` | %s | `%s` | %s | %s |" % (
            row["strategy_id"], row["run_profile"], row["cohort"],
            row["observed_trades"], row["recursive_evidence"],
            row["last_tested_at"] or "-", _links(row)))
    lines.append("")
    lines += ["The calls behind each, one per gate:", ""]
    for row in sorted(passing, key=lambda r: (r["cohort"], r["strategy_id"])):
        calls = [(gate.replace("cmd_", ""), row[gate]) for gate in gates
                 if row[gate]]
        if not calls:
            continue
        lines.append("- `%s`" % row["strategy_id"])
        lines.append("  ```")
        for gate, call in calls:
            lines.append("  %-10s %s" % (gate, call))
        lines.append("  ```")
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
            "No run under the current pipeline is recorded for these. The",
            "original corpus sweep did attempt every row, but it ran in an",
            "environment that did not establish the preconditions this audit",
            "requires - which is the whole reason the pre-checks are being",
            "redone - so its outcome is a hint about what to expect and never a",
            "verdict. Where such a hint exists it is shown in brackets.", "",
            "| Strategy | Wave | Status |", "|---|---|---|",
        ]
        for row in sorted(untested, key=lambda r: (r["expansion_wave"],
                                                   r["strategy_id"])):
            lines.append("| `%s` | `%s` | `%s` |" % (
                row["strategy_id"], row["expansion_wave"] or "-",
                row["primary_reason"].replace("|", "\\|")))
        lines.append("")

    texts = dict(REASON_ORDER)
    if unconfirmed:
        held = collections.Counter(row["primary_reason"] for row in unconfirmed)
        lines += [
            "## Exclusion unconfirmed - %d strategies" % len(unconfirmed), "",
            "`excluded` is a verdict, and this audit does not issue one on",
            "somebody else's measurement or on the absence of one. These rows",
            "would have been excluded on exactly that, so they are held here",
            "until a measurement of ours settles them either way. Nothing about",
            "them is hidden by the change of name: the decisive reason and the",
            "basis stay on the row, and the work that would settle it is in",
            "`open_work`.", "",
            "| Held on | Basis | Strategies |", "|---|---|---:|",
        ]
        for key, count in held.most_common():
            example = next(r for r in unconfirmed if r["primary_reason"] == key)
            lines.append("| `%s` | `%s` | %d |"
                         % (key, example["exclusion_basis"], count))
        lines += [
            "",
            "This is not a softening. A row here may well end up excluded - the",
            "38 held on an inherited look-ahead finding probably will, because a",
            "limited environment does not invent bias. It ends up there on our",
            "own evidence or not at all.", "",
        ]
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
        "**Those logs have now been read again.** Of the 124 recursion",
        "records that still have their log, 55 said something other than what",
        "the table showed: 40 turn out to have no verdict at all, because at",
        "the warm-up the strategy declares the indicators are still undefined;",
        "one is clean; and 14 keep their verdict but had the wrong numbers",
        "attached, read off a column belonging to a different warm-up. The",
        "remaining 76 records kept no log and cannot be checked at all, so",
        "they keep what they were given and stay queued for the ladder.", "",
        "**`WARMUP_NEEDED` is not a finding either.** 134 rows in the frozen",
        "baseline carry `recursive_kind=refused_no_warmup`: the analyzer",
        "declined them because the strategy declares no warm-up, so it never",
        "compared anything. That was being shown as recursion `FOUND` for 47",
        "rows. It now reads `WARMUP_NEEDED`, which is what the record says.", "",
        "**`wave_b:<n>:superseded` is a run of ours we do not yet trust.**",
        "Wave B supplied a warm-up to those refused rows and re-ran the gate,",
        "but under the parser described above. Re-parsing the 106 wave B logs",
        "that survive overturns 58 of them, every one from FOUND to no",
        "verdict; the runs behind the PASS verdicts kept no log and cannot be",
        "re-parsed at all. Eight admitted rows rest on such a verdict. They",
        "stay admitted - E0 and E1 are frozen and this table decides nothing -",
        "and they are queued for the ladder as `recursive_ladder_pending`.", "",
        "### What each exclusion rests on", "",
        "The decisive reason names the gate that stopped a row. It does not",
        "say whether that gate produced evidence, and the difference decides",
        "whether the row is finished with or waiting on us.", "",
        "| Basis | Meaning | Strategies |", "|---|---|---:|",
    ]
    basis = collections.Counter(row["exclusion_basis"] for row in failing
                                if row["exclusion_basis"])
    for key in ("own_measurement", "inherited", "no_finding", "blocked"):
        if basis.get(key):
            lines.append("| `%s` | %s | %d |"
                         % (key, EXCLUSION_BASIS[key], basis[key]))
    lines += [
        "",
        "Only `own_measurement` is a closed case. The other three carry the",
        "work that would settle them in `open_work`, and the selftest fails if",
        "one of them carries none.", "",
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
        if key == "strategy_does_not_run":
            # The message is the whole content of this group. Grouping these
            # rows by name alone would repeat the useless label the frozen
            # baseline gave them; grouped by message it says which failures are
            # one shared fix and which are one-offs.
            by_message = collections.defaultdict(list)
            for row in failing:
                if row["primary_reason"] == key:
                    by_message[row["runtime_failure"]].append(row["strategy_id"])
            lines += ["| Failure | Strategies | Which |", "|---|---:|---|"]
            for message, names in sorted(by_message.items(),
                                         key=lambda item: -len(item[1])):
                lines.append("| %s | %d | %s |" % (
                    (message or "(no message recorded)").replace("|", "\\|"),
                    len(names),
                    ", ".join("`%s`" % n for n in sorted(names))))
            lines.append("")
            continue
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

    # Every row invariant belongs in one loop. This block was split in two by
    # a bad patch on 2026-09-01: half of it ended up inside the store
    # cross-check below and ran against a single leftover row, so four checks
    # were passing on 1 of 900 rows. A test that reports PASS while covering
    # almost nothing is worse than no test.
    for row in data:
        if row["cohort"] in ("excluded", "exclusion_unconfirmed", "pending",
                             "not_tested_in_current_runtime"):
            assert row["primary_reason"], row["strategy_id"]
        else:
            assert not row["primary_reason"], row["strategy_id"]
        # A row measured since the freeze is never still listed as never run.
        if row["measured"] == "true":
            assert row["primary_reason"] != "canonical_implementation_not_measured", \
                row["strategy_id"]
        # This cohort means "no run under the current pipeline".
        if row["cohort"] == "not_tested_in_current_runtime":
            assert row["measured"] == "false", row["strategy_id"]
            assert not row["evidence_paths"], row["strategy_id"]
            assert "no run under the current runtime" in row["primary_reason"], \
                row["strategy_id"]
        # A row the ladder settled must not still carry the superseded verdict.
        if row["cohort"] == "convergence_candidate":
            assert row["recursive"] in ("PASS", "PASS_1PCT"), \
                (row["strategy_id"], row["recursive"])
            assert row["settled_startup"] != "", row["strategy_id"]
        # Nothing reaches a reader in the harness's own language. The three
        # messages that used to leak through were not strategy errors at all,
        # but this audit's own verdicts: a timeout, an empty summary, and a
        # timeframe mismatch.
        assert not i18n.has_cyrillic(row["primary_reason"]), row["strategy_id"]
        # An exclusion is either a finding of ours or an open question, and an
        # open question must name the work that would close it.
        if row["cohort"] == "exclusion_unconfirmed":
            assert row["exclusion_basis"] in ("inherited", "no_finding"), \
                (row["strategy_id"], row["exclusion_basis"])
        # An exclusion this audit has not confirmed is a verdict it has not
        # earned. Nothing may sit in `excluded` on borrowed or absent evidence.
        if row["cohort"] == "excluded":
            assert row["exclusion_basis"] in ("own_measurement", "blocked"), \
                (row["strategy_id"], row["exclusion_basis"])
        if row["cohort"] in ("excluded", "exclusion_unconfirmed") \
                and row["exclusion_basis"] != "own_measurement":
            assert row["open_work"], \
                "%s: excluded on %s with no work queued" % (
                    row["strategy_id"], row["exclusion_basis"])
        # A recovered timestamp always names where it came from.
        assert bool(row["last_tested_at"]) == bool(row["last_tested_source"]), \
            row["strategy_id"]

    # Every native re-measurement must be visible in the table. A verdict that
    # exists in a store this generator does not read is worse than no verdict:
    # the table looks current and is not.
    fresh_store = {}
    for store in LOOKAHEAD_STORES:
        for name, record in _json(store).items():
            gate = record.get("lookahead") or {}
            if gate.get("status") in ("PASS", "FOUND"):
                fresh_store[name] = gate["status"]
    by_id = {r["strategy_id"]: r for r in data}
    for name, status in fresh_store.items():
        assert by_id[name]["lookahead"] == status, (name, status)
        assert by_id[name]["lookahead_evidence"] == "native", name

    # The old ledger is reference material, not evidence. It records what the
    # original author's sweep did in an environment that did not establish this
    # audit's preconditions, so a row appearing there proves nothing about
    # whether it works under the current runtime. It is read only to attach a
    # historical hint, never to decide a cohort or to clear a row.
    assert len({r["strategy"] for r in _csv(LEDGER)}) == 895
    print("strategy_status selftest: PASS (%d rows, %d E0, %d E1, %d unmeasured, "
          "%d timestamped)"
          % (len(data), len(listed), len(admitted),
             sum(1 for r in data if r["cohort"] == "not_tested_in_current_runtime"),
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
