# -*- coding: utf-8 -*-
"""Current status of every strategy from the complete audit evidence chain.

`evidence/REGIME_ELIGIBILITY.csv` is the invalidated historical E0 snapshot. It is never
an admission fallback: its former membership is retained only as provenance.
Current evidence lives across the smoke, bias, full-window, adjudication and
convergence stores. This file collects that evidence into one reference without
rewriting the historical artifact.

Nothing here decides anything. Admission happens in
`evidence/eligibility_expansion_adjudicate.py` and nowhere else; this is a reading of
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


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BS_SEP = chr(92)
ELIGIBILITY = os.path.join(ROOT, "evidence/REGIME_ELIGIBILITY.csv")
# The frozen baseline's own coverage_status was copied in from a run of this
# file at freeze time and never refreshed; every row added by a later wave
# has no entry there at all. This is regenerated freely (a filesystem check
# of already-downloaded candle files, no backtest) and read here in
# preference to the baseline for exactly that reason - confirmed by a full
# re-run reproducing all 900 frozen values unchanged before this took over.
COVERAGE = os.path.join(ROOT, "evidence/REGIME_COVERAGE.csv")
PROFILES = os.path.join(ROOT, "evidence/EXECUTION_PROFILES.csv")
CANDIDATES = os.path.join(ROOT, "evidence/ELIGIBILITY_EXPANSION_CANDIDATES.csv")
ADJUDICATION = os.path.join(ROOT, "evidence/ELIGIBILITY_EXPANSION_ADJUDICATION.csv")
SMOKE = os.path.join(ROOT, "evidence/PROFILE_SMOKE.json")
BIAS = os.path.join(ROOT, "evidence/PROFILE_BIAS.json")
FULL_WINDOW = os.path.join(ROOT, "evidence/PROFILE_FULL_WINDOW.json")
FULL_BACKTEST_MANIFEST = os.path.join(
    ROOT, "results", "regime", "full_backtest_manifest.json")
CONVERGENCE = os.path.join(ROOT, "evidence/WARMUP_CONVERGENCE.json")
# Wave B supplied a warm-up to strategies the analyzer had refused and
# re-ran the gate. Those verdicts were produced before the drift table was
# read correctly, so they are carried as provenance - a date, a log, a
# command - and never as a current verdict.
WAVE_B_WARMUP = os.path.join(ROOT, "evidence/ELIGIBILITY_EXPANSION_WARMUP.json")
# What stops each row that never ran, and whether repairing it would restore
# what the author wrote or invent something they did not.
BLOCKED_TRIAGE = os.path.join(ROOT, "evidence/BLOCKED_TRIAGE.json")
ZERO_TRADE_TRIAGE = os.path.join(ROOT, "evidence/ZERO_TRADE_TRIAGE.json")
# A repaired row is measured by its own runner, into its own store. The smoke
# store holds the failure; this holds what happened once the obstacle was
# removed, and outranks it - the same precedence a native gate has over an
# inherited one, applied to the measurement instead of the verdict.
TIMEFRAME_REPAIR = os.path.join(ROOT, "evidence/ELIGIBILITY_TIMEFRAME_REPAIR.json")
MODULE_REPAIR = os.path.join(ROOT, "evidence/ELIGIBILITY_MODULE_REPAIR.json")
SIGNATURE_REPAIR = os.path.join(ROOT, "evidence/ELIGIBILITY_SIGNATURE_REPAIR.json")
FREQAI_REPAIR = os.path.join(ROOT, "evidence/ELIGIBILITY_FREQAI_REPAIR.json")
FREQAI_WTAI = os.path.join(ROOT, "evidence/ELIGIBILITY_FREQAI_WTAI.json")
# A separate arm with its own runtime and its own configs, completed before
# this table existed. Its records are per-strategy files rather than one store,
# and nothing has ever read them here - which is how a strategy that PASSED a
# FreqAI measurement came to be listed as excluded.
FREQAI_ARM = os.path.join(ROOT, "repair", "results_freqai")
LOCAL_MODULES = os.path.join(ROOT, "evidence/REPAIR_LOCAL_MODULES.json")
# A route that has run and found nothing has still run. Leaving such a row on
# "to be fixed" says the work is ahead of us when it is behind us and failed.
CLASS1 = os.path.join(ROOT, "evidence/PROFILE_CLASS1.json")
# Timeframe and signal-family label, read from the strategy's own source in
# strategy_classification.py. Neither is a measurement, so neither lives in
# any of the stores above; both are regenerated from source alone.
CLASSIFICATION = os.path.join(ROOT, "evidence/STRATEGY_CLASSIFICATION.json")
# Which of the six market phases each strategy is predicted to work in,
# written by evidence/market_phase_hypothesis.py before the benchmark that will test
# it. A prediction, not a measurement: it decides no cohort and clears no row,
# and it is carried here so the benchmark reads it from the same table it
# reports against rather than from a note somebody kept separately.
PHASE_HYPOTHESIS = os.path.join(ROOT, "evidence/MARKET_PHASE_HYPOTHESIS.json")

# What has actually become of a row that could not start. The triage says what
# ought to be done; these say what was done and what it achieved, which is a
# different question and the one a reader asks second.
REPAIR_STATE = {
    "repaired": "a repair was applied and the row now produces a measurement",
    "repair_attempted": "a repair route has run on this row and it still does "
                        "not start; what remains is the reason on the row",
    "repair_withdrawn": "a repair was applied and taken back, because it made "
                        "the row fail in a new way",
    "to_be_fixed": "what stops the row is ours, or is the author's own words "
                   "under a name the framework has since changed",
    "needs_a_look": "repairable in principle, but not by a rule that can be "
                    "written now",
    "refuse_repair": "the strategy does not declare what freqtrade requires; "
                     "supplying it would measure our invention",
}
# Two later stores hold look-ahead measured natively for rows whose verdict was
# inherited or missing. They are separate files because they are separate
# cohorts, and forgetting to read one is how the newest evidence stops reaching
# this table while the table still claims to be current.
LOOKAHEAD_STORES = (
    os.path.join(ROOT, "evidence/ELIGIBILITY_LOOKAHEAD_BACKFILL.json"),
    os.path.join(ROOT, "evidence/ELIGIBILITY_EVIDENCE_GAP.json"),
)
# Hand-reviewed exceptions to a lookahead=FOUND verdict: rows where
# freqtrade's own lookahead-analysis flagged an intermediate column but its
# entry/exit signal check found nothing, and a source read confirms why.
# Bound to canonical_sha256 so an upstream edit re-opens the question.
LOOKAHEAD_INDICATOR_REVIEW = os.path.join(ROOT, "evidence/LOOKAHEAD_INDICATOR_REVIEW.json")
# Wherever a gate downstream asks "is this row's lookahead evidence current
# and trustworthy", a reviewed exception counts exactly as a native run does
# - the difference between the two is provenance, which lookahead_evidence
# itself keeps visible, not how much either can be trusted.
NATIVE_LOOKAHEAD_EVIDENCE = ("native", "reviewed_indicator_only")
OUTPUT = os.path.join(ROOT, "STRATEGY_STATUS.csv")
REPORT = os.path.join(ROOT, "STRATEGY_STATUS.md")

FIELDS = [
    "strategy_id", "repo", "source_file", "result_archive",
    "run_profile", "expansion_wave", "timeframe", "strategy_type",
    "assumed_market_regime", "assumed_market_regime_evidence",
    "cohort", "measured",
    "observed_trades", "trade_evidence", "test_duration_s",
    "test_duration_evidence", "lookahead", "lookahead_evidence",
    "recursive", "recursive_evidence", "coverage_status", "coverage_evidence",
    "full_backtest_status", "technical_chain_complete",
    "traps_n", "artifact_role",
    "baseline_status", "primary_reason", "exclusion_basis",
    "repair_family", "repair_verdict", "repair_settings", "required_image",
    "gate_notes", "runtime_failure", "evidence_gap",
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
# What an artifact is, when it is not a strategy. Kept apart from
# REASON_ORDER because these are not failures: nothing went wrong, the file
# was simply never a strategy to begin with.
ROLE_REASON = {
    "test_candidate": "a fixture from somebody's test suite",
    "template_candidate": "a template with no strategy filled in",
}


REASON_ORDER = (
    ("lookahead_found", "reads data it could not have had at the time"),
    ("behavior_changed_primary_exclusion", "repaired in a way that changed behaviour"),
    ("strategy_does_not_run",
     "fails before it can be measured; the message is in runtime_failure"),
    ("recursive_bias_found",
     "indicator value still drifts at every warm-up the ladder can reach"),
    ("recursive_bias_unverified",
     "recorded under a parser defect and not re-measured; not a finding"),
    ("recursive_warmup_refused",
     "the analyzer refused for want of a declared warm-up; nothing was measured"),
    ("measured_outside_its_design",
     "opened nothing because our setup stopped it, not because it is idle"),
    ("too_few_trades_to_measure",
     "trades fewer than ten times over the full window and all eight pairs, "
     "which is below what any check or ranking can work with"),
    ("no_trades_in_full_measurement", "never trades over the full window"),
    ("repair_refused_would_invent_strategy",
     "declares no timeframe, no stoploss, no exit logic, or names a model "
     "that no longer exists and cannot be restored; supplying one would "
     "measure our invention rather than the author's strategy"),
    ("local_module_repair_exhausted",
     "imports a helper the author shipped beside it; every candidate copy "
     "in the corpus either fails to import, would shadow an installed "
     "package, or imports cleanly but does not define what the strategy "
     "calls"),
    ("measured_only_in_freqai_arm",
     "runs only under its author's own FreqAI configuration, measured "
     "separately in that arm; not comparable with the ordinary spot audit"),
    ("third_party_package_declined",
     "needs a Python package this runtime does not install; declined "
     "because installing one changes the runtime every other strategy runs "
     "under, owner's call 2026-09-04"),
    ("shared_runtime_change_declined",
     "the fix is understood - pandas' or numpy's own type-coercion rules "
     "have tightened - but applying it would touch every strategy's column "
     "writes, not just this row's; declined, owner's call 2026-09-04"),
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
LEDGER = os.path.join(ROOT, "old", "predecessor_audit", "LEDGER.csv")
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
    return "20200301-20200601"


def repair_settings(entry, run=None):
    """What a repair consists of, as one line a person can act on.

    A repaired row's gate commands are reconstructed, and a reconstruction that
    silently drops the repair is worse than none: following it reproduces the
    original failure and looks like the strategy's fault. So the repair is
    stated here in full, and the reconstructions are built from the same facts
    rather than from the generic template.
    """
    parts = []
    # A timeframe recovered at run time lives in the repair record, not in the
    # class-1 registry: it is written into a generated override config whose
    # name nobody can guess. Stated here as the flag that reproduces it.
    overrides = (run or {}).get("config_overrides") or {}
    for key, value in sorted(overrides.items()):
        parts.append("%s=%s (recovered)" % (key, value))
    if (run or {}).get("timeframe_evidence"):
        parts.append("timeframe_evidence=" + run["timeframe_evidence"])
    entry = entry or {}
    rules = entry.get("rules") or []
    if rules:
        parts.append("rules=" + ",".join(rules))
    if entry.get("config_source"):
        parts.append("config=" + entry["config_source"])
    if entry.get("config_keys"):
        parts.append("config_keys=" + ",".join(entry["config_keys"]))
    if entry.get("freqaimodel"):
        parts.append("freqaimodel=" + entry["freqaimodel"])
    if entry.get("freqaimodel_path"):
        parts.append("freqaimodel_path=" + entry["freqaimodel_path"])
    for key, name in (("python_paths", "PYTHONPATH"),
                      ("freqtrade_paths", "PROFILE_FREQTRADE_PATH")):
        if entry.get(key):
            parts.append("%s+=%s" % (name, ":".join(entry[key])))
    signatures = [rule for rule in rules
                  if rule in ("legacy_min_roi_reached_entry_signature",
                              "whitespace_tolerant_class_scan")]
    if signatures:
        parts.append("PROFILE_COMPAT_SIGNATURES=" + ",".join(signatures))
    if entry.get("packages"):
        parts.append("packages=" + ",".join(
            "%s==%s" % (p.get("name"), p.get("version"))
            for p in entry["packages"]))
    if entry.get("status"):
        parts.append("status=" + entry["status"])
    return "; ".join(parts)


def repair_flags(entry, run=None):
    """The extra freqtrade arguments a repaired row needs."""
    extra = []
    timeframe = ((run or {}).get("config_overrides") or {}).get("timeframe")
    if timeframe:
        # The gate configs are shared, so the recovered value is passed on the
        # command line rather than by pointing at the generated override.
        extra.append("--timeframe " + timeframe)
    entry = entry or {}
    if entry.get("freqaimodel"):
        extra.append("--freqaimodel " + entry["freqaimodel"])
    if entry.get("freqaimodel_path"):
        extra.append("--freqaimodel-path " + entry["freqaimodel_path"])
    return (" " + " ".join(extra)) if extra else ""


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
               pairs=0, repair=None, run=None):
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
    # A repaired row runs against the config the repair produced, not the
    # generic one, and needs whatever flags the repair registered.
    config = _config_for(kind, profile)
    if repair and repair.get("config_source"):
        config = repair["config_source"]
    # The gates run against an isolated directory holding this strategy alone,
    # because freqtrade's resolver imports every .py beside it and a neighbour
    # that raises at import time takes the run with it - one file in
    # PeetCrypto_freqtrade-stuff opens a log at module level and kills any gate
    # pointed at that directory. Naming the repo path here would print a
    # command that fails for a reason that has nothing to do with the row.
    path = (os.path.dirname(source_file) or "." if kind == "backtest"
            else "user_data/profile_bias_strategies/%s" % strategy)
    line = template.format(config=config, strategy=strategy, path=path,
                           timerange=timerange)
    line += repair_flags(repair, run)
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


# The widest window `lookahead-analysis` falls back to: the full span over
# all eight pairs. A "too few trades" reported against it is a statement
# about the strategy, not about a window that was too short.
FULL_FALLBACK = "20200301-20260820"
TRADE_FLOOR = 10
# Which image a row needs, for the benchmark run this table exists to feed.
# Read from PROFILE_CLASS1's own per-strategy "image" field where a row
# needed one - BuyRegions and CryptoPredictionTraining on the TensorFlow
# companion image, four rows on the packages one - and this otherwise, which
# is what every row without an explicit override actually runs on.
DEFAULT_IMAGE = "strategy-audit-runtime:2026.7"
# Criterion C4 (evidence/exclusion_criteria.py): a repair route ran, read what the
# author actually wrote, and refused to invent what is missing rather than
# leave the row "to be fixed" forever. `freqai_arm` and `freqai_config_built`
# are deliberately not here - both are `refuse_repair` for THIS audit only
# because the row is measured separately in the FreqAI arm, which is a
# different question from "no measurement is possible at all".
NO_REPAIR_POSSIBLE = {"timeframe_not_recoverable", "no_stoploss",
                      "no_exit_logic", "freqai_model",
                      "no_populate_indicators", "missing_author_data_file",
                      "invalid_declared_config",
                      # No model name appears anywhere in the strategy's own
                      # repository (checked directly, not assumed) - distinct
                      # from `freqai_model`, where a name IS given but the
                      # class it names does not exist.
                      "freqai_no_model_named",
                      # A local-module search found and applied a genuine
                      # candidate, but the attribute the strategy reads from
                      # it is confirmed absent from every copy in the corpus
                      # AND the module's true origin repository - not a
                      # search gap, a gap in what the author ever published.
                      "local_module_incomplete",
                      "author_logic_incomplete",
                      "author_parameter_missing",
                      "author_signal_missing",
                      "backtest_mode_not_implemented",
                      "insufficient_authored_history_contract",
                      "missing_author_runtime",
                      "unsupported_exchange_timeframe",
                      "local_module_repair_exhausted"}


def _json(path, key="results"):
    if not os.path.exists(path):
        return {}
    return json.load(io.open(path, encoding="utf-8")).get(key, {})


def _full_backtest_document():
    """Read the pooled Stage-7 store without treating a partial write as proof."""
    if not os.path.exists(FULL_BACKTEST_MANIFEST):
        return {"results": {}, "timerange": {}}
    document = json.load(io.open(FULL_BACKTEST_MANIFEST, encoding="utf-8"))
    return {"results": document.get("results") or {},
            "timerange": document.get("timerange") or {}}


def completed_full_backtest(profile, record):
    """Whether this exact implementation completed the canonical pooled run."""
    if not record or record.get("status") != "measured":
        return False
    return (
        record.get("measurement_scope") == "canonical_pooled_native_pair_universe"
        and record.get("run_profile") == profile.get("run_profile")
        and record.get("canonical_sha256") == profile.get("source_sha256")
    )


def _integer(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


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


def exclusion_basis(reason, lookahead_evidence, trade_evidence,
                    recursive_evidence=""):
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
    # Our fault, not the strategy's. `blocked` is the basis that says exactly
    # that: nothing about the strategy was judged, because the run never gave
    # it the chance.
    if reason == "measured_outside_its_design":
        return "blocked"
    if reason.startswith("too_few_trades_to_measure"):
        # Ours either way: the count comes from our own run over the full
        # window. A second clause naming our setup does not change that.
        return "own_measurement"
    if reason == "no_trades_in_full_measurement":
        return "own_measurement" if trade_evidence == "full_window" else "inherited"
    # `recursive_bias_found` is our own only when our ladder produced it. A
    # FOUND carried over from the baseline is inherited evidence and says so,
    # whatever else the row carries: 15 rows sat under `own_measurement`
    # solely because the trap reason forced that label, and not one of them
    # had a ladder run of ours.
    if reason == "recursive_bias_found":
        return ("own_measurement"
                if str(recursive_evidence).startswith("convergence")
                else "inherited")
    # Also our own only when our ladder produced it - the shrinking-ladder
    # retry in evidence/warmup_convergence.py's resolve() ran to its 3-longest-rungs
    # floor and still crashed. Never inherited: no earlier wave or baseline
    # sweep could have carried this specific verdict, since the state did
    # not exist before 2026-09-08.
    if reason == "recursive_check_incomplete_at_longest_rungs":
        return "own_measurement"
    if reason == "behavior_changed_primary_exclusion":
        return "own_measurement"
    if reason == "recursive_bias_unverified" \
            or reason == "recursive_warmup_refused" \
            or reason.startswith("no_verdict_on") \
            or reason == "canonical_implementation_not_measured":
        return "no_finding"
    return "no_finding"


def test_duration(measurement, diagnostics, window, settled, fresh, tried,
                  attempt):
    """Wall-clock seconds this audit's own tooling has spent measuring a row.

    Every runner times its own subprocess call and stores the figure beside
    the result; nothing here re-derives it, only collects it. A row can carry
    several distinct calls at once - a trial-run backtest, a bias-store
    look-ahead and recursion pair from the original sweep, a later native
    re-measurement of look-ahead, the warm-up ladder, a wave B recursion
    attempt, and the eight-pair full-window backtest - because later waves
    measured on top of earlier ones rather than replacing them, and each is
    real time genuinely spent, not a duplicate of another. So this is a sum,
    unlike `observed_trades`'s pick-one-source priority chain: the point is
    to see where the time actually went, and hiding a superseded run's cost
    would understate what the row cost to measure. Blank where nothing here
    carries a stamp.
    """
    parts = []
    if measurement.get("elapsed_s"):
        parts.append(("backtest", measurement["elapsed_s"]))
    full_window_elapsed = round(sum(
        (pair.get("elapsed_s") or 0)
        for pair in (window.get("pair_results") or {}).values()), 1)
    if full_window_elapsed:
        parts.append(("full_window", full_window_elapsed))
    if (diagnostics.get("lookahead") or {}).get("elapsed_s"):
        parts.append(("lookahead", diagnostics["lookahead"]["elapsed_s"]))
    remeasured_lookahead = (fresh or tried or {}).get("elapsed_s")
    if remeasured_lookahead:
        parts.append(("lookahead_remeasured", remeasured_lookahead))
    if (diagnostics.get("recursive") or {}).get("elapsed_s"):
        parts.append(("recursive", diagnostics["recursive"]["elapsed_s"]))
    if settled.get("elapsed_s"):
        parts.append(("recursive_ladder", settled["elapsed_s"]))
    if attempt.get("elapsed_s"):
        parts.append(("recursive_wave_b", attempt["elapsed_s"]))
    total = round(sum(value for _, value in parts), 1)
    evidence = "; ".join("%s=%ss" % (name, value) for name, value in parts)
    return (total if total else "", evidence)


def freqai_arm():
    """What the FreqAI arm measured, keyed by strategy.

    These runs are not comparable with the ordinary spot audit - a different
    runtime, the authors' own freqai configs, a different question - so they
    are surfaced as their own evidence and never merged into a cohort. What
    they can do is stop the table asserting things the arm has disproved.
    """
    out = {}
    if not os.path.isdir(FREQAI_ARM):
        return out
    for name in sorted(os.listdir(FREQAI_ARM)):
        if not name.endswith(".json"):
            continue
        try:
            record = json.load(io.open(os.path.join(FREQAI_ARM, name),
                                       encoding="utf-8"))
        except ValueError:
            continue
        runs = record.get("runs") or {}
        sample = runs.get("in_sample") or {}
        out[record.get("strategy", name[:-5])] = {
            "level": sample.get("level", ""),
            "why": (sample.get("why") or "").strip(),
            "trades": (sample.get("summary") or {}).get("trades", ""),
            "config": record.get("config", ""),
        }
    return out


def rows():
    baseline = {r["strategy_id"]: r for r in _csv(ELIGIBILITY)}
    coverage = {r["strategy_id"]: r for r in _csv(COVERAGE)}
    profiles = {r["strategy_id"]: r for r in _csv(PROFILES)}
    waves = {r["strategy_id"]: r for r in _csv(CANDIDATES)}
    admitted = {r["strategy_id"] for r in _csv(ADJUDICATION)
                if r["adjudication_status"] == "admitted_E1"}
    classification = _json(CLASSIFICATION)
    phase_hypothesis = _json(PHASE_HYPOTHESIS)
    smoke = dict(_json(SMOKE))
    bias = _json(BIAS)
    full = _json(FULL_WINDOW)
    full_backtest_document = _full_backtest_document()
    full_backtests = full_backtest_document["results"]
    convergence = _json(CONVERGENCE)
    wave_b = _json(WAVE_B_WARMUP)
    triage = _json(BLOCKED_TRIAGE)
    # Zero trades over the full window is the strategy's own
    # property only when nothing on our side stopped it trading.
    # Four of the eleven turned out to be ours: a basket strategy
    # measured one pair at a time, an indicator broken by pandas
    # copy-on-write, and two run under a profile their entry
    # logic cannot be satisfied in.
    zero_trades = _json(ZERO_TRADE_TRIAGE, "results")
    setup_faults = {name: record for name, record
                    in zero_trades.items()
                    if record.get("verdict") == "setup_fault"}
    freqai = freqai_arm()
    # Which runner repaired a row is part of what happened to it.
    repair_source = {name: "timeframe_missing"
                     for name in _json(TIMEFRAME_REPAIR)}
    for name in _json(MODULE_REPAIR):
        repair_source.setdefault(name, "local_module_off_path")
    for name in _json(SIGNATURE_REPAIR):
        repair_source.setdefault(name, "framework_compat_shim")
    for name in _json(FREQAI_REPAIR):
        repair_source.setdefault(name, "freqai_model")
    for name in _json(FREQAI_WTAI):
        repair_source.setdefault(name, "freqai_config_built")
    # A shim registered in PROFILE_CLASS1 but not carried by any
    # measurement store is still a repair that was applied to that row.
    # Without this the 14 rows the enter_tag shim answers showed their
    # rule in `repair_settings` and nothing in `repair_family` - the
    # settings said what was done and the family said nothing was.
    SHIM_FAMILY = {
        "legacy_min_roi_reached_entry_signature": "framework_compat_shim",
        "legacy_min_roi_reached_entry_override": "framework_compat_shim",
        "whitespace_tolerant_class_scan": "framework_compat_shim",
        "idempotent_entry_tag_initialisation": "framework_compat_shim",
        "lookahead_runmode_reports_backtest": "framework_compat_shim",
        "startup_candles_not_limited_by_call_budget": "framework_compat_shim",
        "restore_accumulation_distribution": "framework_compat_shim",
        "restore_copied_local_module": "local_module_off_path",
        "restore_fetched_local_module": "local_module_off_path",
        "datetime_safe_rmi_fillna": "dtype_drift",
    }
    for name, entry in (_json(CLASS1, "strategies") or {}).items():
        if entry.get("status") not in ("applied", "partial"):
            continue
        for rule in entry.get("rules") or []:
            if rule in SHIM_FAMILY:
                repair_source.setdefault(name, SHIM_FAMILY[rule])
                break
    # A route that has declined a row, with a reason, has decided it. Leaving
    # such a row on "to be fixed" promises work that will never be done.
    refused_timeframe = _json(TIMEFRAME_REPAIR, "refused")
    # A route that ran and concluded the row cannot be repaired without
    # inventing something. Recorded where the runners already look.
    class1 = _json(CLASS1, "strategies") or {}
    # `family` is optional: most refusals leave the family blocked_triage.py's
    # fresh probe already assigned untouched. It is only set here when that
    # family is not itself a member of NO_REPAIR_POSSIBLE and the refusal
    # needs a family that is, so C4 can actually reach the row (E0V1EAI:
    # freqai_not_enabled is a legitimate family for a row nobody has looked
    # at yet, but this one HAS been looked at and refused, on the specific
    # ground that no model is named anywhere in its repository).
    refused_repair = {name: (entry.get("note", ""), entry.get("family"))
                      for name, entry in (_json(CLASS1, "strategies") or {}).items()
                      if entry.get("status") == "refused"}
    withdrawn = {name for name, entry
                 in (_json(CLASS1, "strategies") or {}).items()
                 if entry.get("status") == "withdrawn"}
    attempted = {name: record.get("why", "")
                 for name, record in _json(LOCAL_MODULES).items()
                 if record.get("status") != "resolved"}
    repaired = dict(_json(TIMEFRAME_REPAIR))
    # Two repair runners, one precedence: whichever of them last produced a
    # measurement for a row replaces the failure the smoke store holds.
    for name, record in _json(MODULE_REPAIR).items():
        repaired.setdefault(name, record)
    for name, record in _json(SIGNATURE_REPAIR).items():
        repaired.setdefault(name, record)
    for name, record in _json(FREQAI_REPAIR).items():
        repaired.setdefault(name, record)
    for name, record in _json(FREQAI_WTAI).items():
        repaired.setdefault(name, record)
    # A native re-measurement outranks whatever PROFILE_BIAS or the baseline
    # holds: it is the same gate, measured later, from this implementation.
    remeasured = {}
    remeasured_sha = {}
    # Separately: every row a gate of ours has been run against, verdict or
    # not. An NA is not a verdict, but it is emphatically not "never measured
    # here" either - the run happened, it produced nothing, and the reason is
    # worth showing. Recording it as `missing` said the opposite of the truth
    # for 22 convergence candidates.
    attempted_gate = {}
    for store in LOOKAHEAD_STORES:
        for name, record in _json(store).items():
            gate = record.get("lookahead") or {}
            if gate.get("status") in ("PASS", "FOUND"):
                remeasured[name] = gate
                remeasured_sha[name] = record.get("canonical_sha256")
            elif gate.get("status"):
                attempted_gate.setdefault(name, gate)
    # freqtrade's lookahead-analysis flags `has_bias=Yes` the moment ANY
    # dataframe column differs between a short and a long data window - that
    # is also what a correctly-built lagging/leading Ichimoku span looks
    # like by construction (a raw intermediate value briefly holds a real
    # future close before the strategy re-aligns or never reads it). Its own
    # signal-level check is stronger evidence: entries/exits actually
    # replayed against 20 sampled trades. Where that check found zero biased
    # entries and zero biased exits, and a strategy's own code has been read
    # by hand to confirm the flagged column never reaches populate_entry/
    # exit_trend un-neutralised, evidence/LOOKAHEAD_INDICATOR_REVIEW.json records the
    # finding bound to the file's hash - so a later edit of the strategy
    # invalidates the review instead of silently keeping it.
    lookahead_review = _json(LOOKAHEAD_INDICATOR_REVIEW, key="reviewed")

    out = []
    for strategy in sorted(profiles):
        profile = profiles[strategy]
        full_backtest = full_backtests.get(strategy) or {}
        full_backtest_complete = completed_full_backtest(profile, full_backtest)
        base = baseline.get(strategy, {})
        wave = waves.get(strategy, {}).get("expansion_wave", "")
        measurement = smoke.get(strategy) or {}
        repair_run = repaired.get(strategy) or {}
        # `repaired` is a handful of one-off runner stores, each written once
        # and never touched again once no script remains that regenerates it.
        # `smoke` is evidence/PROFILE_SMOKE.json, re-run directly whenever a rule is
        # added or corrected. When both hold a record and disagree on which
        # rules were active, the fresher one is whichever measured under the
        # rules PROFILE_CLASS1 currently registers - not by construction
        # whichever store this is. Solipsis4 and Dyna_opti needed a second
        # shim after their module-path repair was already measured and
        # filed; a bare `status in (...)` check kept reporting that stale
        # failure days after a passing run sat in `smoke`.
        #
        # Rule-matching alone answers "did the registered compat rules
        # change", not "did the underlying file change" - a different
        # staleness question, and RLAgentStrategy fell straight through the
        # gap between them: its upstream repo moved (a new dependency,
        # datasieve, replacing the old optunahub one FREQAI_REPAIR.json was
        # filed against), PROFILE_CLASS1's registered rule for it was
        # untouched, so the rule check alone said "still current" over a
        # canonical_sha256 that no longer existed on disk. Comparing hashes
        # is the same fix `evidence/profile_smoke.py`'s own skip check needed for the
        # same three rows this session, applied where a repair store
        # competes with a fresh smoke measurement instead of with itself.
        current_rules = class1.get(strategy, {}).get("rules") or []
        smoke_is_current_measurement = (
            measurement.get("status") == "measured"
            and measurement.get("class1_rules", current_rules) == current_rules)
        if repair_run.get("status") in ("measured", "failed") \
                and not smoke_is_current_measurement \
                and repair_run.get("class1_rules", current_rules) == current_rules \
                and (not measurement.get("canonical_sha256")
                     or repair_run.get("canonical_sha256")
                     == measurement.get("canonical_sha256")):
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
        tried = attempted_gate.get(strategy)
        lookahead_evidence = (
            "native" if (fresh or diagnostics.get("lookahead") or tried)
            else (base.get("lookahead_evidence_source") or "missing"))
        if not lookahead and tried:
            lookahead = tried.get("status") or ""
        # A reviewed exception: the indicator freqtrade flagged never
        # decided this row's actual entries/exits (see the note where
        # LOOKAHEAD_INDICATOR_REVIEW is loaded), and the file has not
        # changed since a human read confirmed why.
        review = lookahead_review.get(strategy)
        review_note = ""
        if lookahead == "FOUND" and review:
            active_sha = (remeasured_sha.get(strategy) if fresh is not None
                          else diagnostics.get("canonical_sha256"))
            if active_sha and active_sha == review.get("canonical_sha256"):
                lookahead = "PASS"
                lookahead_evidence = "reviewed_indicator_only"
                review_note = ("lookahead reviewed: flagged column not "
                               "decisive (%s, see evidence/LOOKAHEAD_INDICATOR_REVIEW.json)"
                               % review.get("pattern", ""))
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
        # Same precedence, for the same reason: evidence/REGIME_COVERAGE.csv is
        # regenerated freely and now covers every row evidence/EXECUTION_PROFILES.csv
        # does, so it is read first; the frozen baseline is the fallback for
        # a row somehow missing from a regeneration, not the normal path.
        coverage_row = coverage.get(strategy)
        if coverage_row:
            coverage_status = coverage_row.get("coverage_status", "")
            coverage_evidence = "native"
            coverage_detail = coverage_row.get("coverage_evidence", "")
        elif base.get("coverage_status"):
            coverage_status = base.get("coverage_status", "")
            coverage_evidence = "baseline"
            coverage_detail = base.get("coverage_evidence", "")
        else:
            coverage_status = ""
            coverage_evidence = "missing"
            coverage_detail = ""
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
        elif settled.get("state") == "crashes_even_at_longest_rungs":
            # Not a finding - no drift was ever observed, because the row
            # never produced a drift table to observe it in. TRIX_LS
            # (`rsi_.rolling(length)` on `None`) and kijun_cross_strong_s (a
            # `NoneType` subscript) both crash inside their own indicator
            # code, and both already pass a real Probelauf on full history,
            # so this is the ladder's extreme short rungs, not a defect
            # visible under real use. The shrinking-ladder retry (`resolve()`
            # in evidence/warmup_convergence.py) already gave every rung down to the 3
            # longest a chance to be the reason and it still crashes there.
            # `recursive` stays `NA` - honestly, no bias verdict exists - but
            # the recursive-bias check is not optional for any row, so
            # failing to complete it even at the most generous remaining
            # warm-up is treated as failing to pass it.
            recursive = "NA"
            recursive_evidence = "convergence:crash_exhausted"
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

        # Freqtrade ships its own fixtures under tests/strategy/strats, and
        # eleven of them are in the corpus. They load, they trade, they clear
        # both bias checks - and they are not strategies anyone wrote to
        # trade, so no measurement can ever admit one.
        role = profile.get("artifact_role", "")
        # Ten trades is what `lookahead-analysis` needs before it will judge
        # anything, so a row it turned away for want of them cannot be given a
        # verdict by any amount of re-running. Read from the widest window the
        # check tried, which is the full 6.5 years over all eight pairs.
        gate_record = (fresh or tried
                       or (diagnostics.get("lookahead") or {}) or {})
        too_few = (
            gate_record.get("status") == "NA"
            and "too few trades" in (gate_record.get("why") or "")
            and FULL_FALLBACK in (gate_record.get("attempted_timeranges") or []))
        # C4, reached from the gate rather than from a trial-run failure:
        # `TGMA` measures and trades fine, but its own declared
        # trailing_stop_positive_offset is smaller than its own declared
        # trailing_stop_positive, and freqtrade's lookahead-analysis refuses
        # to start over it. Both values are the author's; adjusting either
        # would be guessing which one they meant, the same ground as a
        # missing stoploss, just found by a gate instead of the trial run.
        invalid_gate_config = (
            gate_record.get("status") == "NA"
            and "needs to be greater than trailing_stop_positive"
               in (gate_record.get("why") or ""))
        ran_here = bool(measurement or diagnostics or window or settled)
        if role != "strategy":
            # Decided before any measurement is consulted, because no
            # measurement can change it. `StrategyTestV2` clears both bias
            # checks with 26070 trades behind it and is still a fixture from
            # freqtrade's own test suite.
            cohort = "not_a_strategy"
        elif strategy in admitted:
            cohort = "E1_expanded"
        elif settled.get("state") == "converged" and lookahead == "PASS" \
                and lookahead_evidence in NATIVE_LOOKAHEAD_EVIDENCE:
            # Convergence answers one question: is there a warm-up at which no
            # indicator drifts. It says nothing about whether the strategy
            # reads data it could not have had, and a look-ahead finding is
            # disqualifying however settled the warm-up is.
            #
            # A candidate is a row on its way to admission, so it needs a
            # look-ahead PASS, not merely the absence of a FOUND. 35 rows were
            # candidates on an NA - the gate ran and returned nothing, for
            # eleven different reasons - and each was queued for the paired
            # full-window run, hours of computation for a row that could not
            # be admitted whatever that run showed.
            cohort = "convergence_candidate"
        elif lookahead == "FOUND" and lookahead_evidence == "native"                 or recursive_evidence == "convergence:not_settled"                 or recursive_evidence == "convergence:crash_exhausted":
            # A finding of ours settles the row, and settles it whatever else
            # is still outstanding. Without this the "diagnostics not
            # completed" branch below outranked the finding: dropping the trap
            # as a failure reason left 19 rows with a confirmed ladder failure
            # reading as merely pending, because their look-ahead had not run
            # yet. A missing second check is no reason to un-fail the first.
            cohort = "excluded"
        elif too_few:
            # Neither excluded nor usable. Nothing was found against it, so
            # `excluded` would claim a verdict nobody reached; and it cannot
            # be ranked by market phase, because three trades in six and a
            # half years distribute across nothing.
            cohort = "too_few_trades"
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
        elif measurement and measurement.get("status") != "measured":
            # The trial run is the first precondition, and a strategy that
            # fails it has not been judged on anything else: no gate has seen
            # it. It is therefore open, not excluded, until the obstacle is
            # either removed or shown to be the strategy's own. What kind of
            # obstacle it is stays in `repair_verdict`, which is a different
            # question from whether the strategy is still in play.
            cohort = "pending"
        elif strategy in setup_faults and not too_few:
            # It ran the whole window and opened nothing, but the reason is
            # ours. `BasketStrategy` marks 8831 entries and sizes every one
            # of them to zero, because a portfolio basket measured one pair
            # at a time has no portfolio to take a weight of. `MostOfAll`
            # loses its supertrend to pandas copy-on-write. `FundingCarry`
            # needs funding rates it cannot have on spot, and
            # `Insomnia_short` only ever raises short signals with
            # `can_short` unset. None of that is a statement about the
            # strategy, so none of it excludes one.
            cohort = "pending"
        else:
            cohort = "excluded"

        reason = ""
        if cohort in ("excluded", "pending", "too_few_trades"):
            if cohort == "too_few_trades":
                # Decided by the cohort, not by the frozen reason set: the
                # baseline predates the run that established it.
                reason = "too_few_trades_to_measure"
                if strategy in setup_faults:
                    # Where our own setup is part of why it trades so
                    # rarely, the row says so. `BasketStrategy` weights
                    # every entry against a portfolio the measurement never
                    # gave it; `FundingCarry` needs funding rates that only
                    # exist in futures mode. The cohort states where the
                    # strategy stands; this states what would have to change
                    # before that is re-examined.
                    reason += "; measured_outside_its_design"
            reasons = set(filter(None,
                                 (base.get("exclusion_reasons") or "").split(";")))
            # Evidence gathered since the freeze outranks the frozen reason.
            if lookahead == "FOUND":
                reasons.add("lookahead_found")
            else:
                # A frozen baseline can carry "lookahead_found" from a sweep
                # this table has since superseded - a native PASS (or a
                # reviewed exception, see evidence/LOOKAHEAD_INDICATOR_REVIEW.json)
                # must retract it the same way a settled ladder retracts
                # recursive_bias_found below, or the row stays excluded on a
                # finding nothing here still supports.
                reasons.discard("lookahead_found")
            if recursive == "FOUND":
                reasons.add("recursive_bias_found")
            if recursive == "WARMUP_NEEDED":
                reasons.discard("recursive_bias_found")
                reasons.add("recursive_warmup_refused")
            if measurement.get("status") == "measured":
                reasons.discard("canonical_implementation_not_measured")
            # The frozen baseline still carries `technical_trap_found`, and
            # it stays there: the baseline is not rewritten. It is no longer a
            # reason a row fails, though. `traps.py` reads the source for the
            # patterns the freqtrade community's "Backtesting Traps" article
            # names, which is a heuristic rather than a measurement, and what
            # it describes - a trailing stop tighter than a realistic spread -
            # inflates how much a strategy appears to earn rather than showing
            # it read the future. Excluding on it dropped 40 rows that run and
            # trade before either bias check saw them. The flag stays visible
            # in `traps_n`, and the realism problem is met in the run itself,
            # with `--timeframe-detail 1m`.
            reasons.discard("technical_trap_found")
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
            if settled.get("state") == "converged":
                # The ladder answered the recursion question and the answer was
                # PASS. Keeping the frozen reason would let a settled row be
                # excluded for the very thing that was settled, and would hide
                # the reason it is actually held on.
                reasons.discard("recursive_bias_found")
                reasons.discard("recursive_bias_unverified")
            if "recursive_bias_found" in reasons \
                    and settled.get("state") != "not_converged_within_ladder":
                reasons.discard("recursive_bias_found")
                reasons.add("recursive_bias_unverified")
            # REASON_ORDER puts `strategy_does_not_run` above the recursion
            # finding, which is right while a non-running row can only carry
            # a borrowed one: nothing of ours has seen it, so nothing of ours
            # may name it. A finding OUR ladder produced is the other case.
            # The ladder ran, printed its drift table, and no rung held every
            # indicator inside the band - a measurement of this strategy that
            # a failed backtest downstream does not undo. The failure stays on
            # the row in `repair_verdict` and `runtime_failure`; it just stops
            # being what the row is called.
            if recursive_evidence == "convergence:not_settled":
                reason = "recursive_bias_found"
            elif recursive_evidence == "convergence:crash_exhausted":
                reason = "recursive_check_incomplete_at_longest_rungs"
            for key, _text in REASON_ORDER:
                if reason:
                    break
                if key in reasons:
                    reason = key
                    break
            if not reason and cohort == "pending":
                reason = "pending_diagnostics"
            if strategy in setup_faults and cohort != "too_few_trades":
                # Named before the zero-trade reason can claim the row, so
                # the table says what actually happened rather than what it
                # looks like from the trade count alone. A row already in
                # the too-few-trades cohort keeps that as its first clause
                # and carries this one after it.
                reason = "measured_outside_its_design"
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
        elif cohort == "not_a_strategy":
            reason = ROLE_REASON.get(profile.get("artifact_role"),
                                     "not_a_trading_strategy")
            failure = i18n.translate(measurement.get("why") or "").strip()
            if measurement and measurement.get("status") != "measured" \
                    and failure:
                # It would not have run either. Two separate facts, and
                # dropping the second would lose a real observation.
                reason += "; strategy_does_not_run"
        elif cohort == "not_tested_in_current_runtime":
            # The old card's exception is kept as a hint about what to expect,
            # never as a verdict: it was produced under different preconditions.
            hint = card_error(strategy)
            reason = ("no run under the current runtime"
                      + (" (historical hint: %s)" % hint if hint else ""))

        # A row that has an active E1 adjudication can still carry a historical
        # gate verdict from the original author's sweep. E0 membership itself
        # never admits it; the gap is named so that current-runtime evidence can
        # replace the inherited verdict without hiding its provenance.
        gaps = []
        if cohort == "E1_expanded":
            if lookahead_evidence.startswith("historical"):
                gaps.append("lookahead_from_original_sweep")
            if recursive_evidence.startswith("historical"):
                gaps.append("recursive_from_original_sweep")

        open_work = []
        if gaps:
            open_work.append("re-measure_gates_in_current_runtime")
        if cohort == "convergence_candidate":
            # `paired_full_window_equivalence` used to be listed here. The
            # preregistration retired it on 2026-09-02, together with
            # requirement 7: the settled warm-up IS the measurement, and a
            # trade list that changes under it is the consequence of measuring
            # properly rather than a reason to hold the row back. Asking for a
            # test that no longer exists promises work nobody will do.
            if lookahead not in ("PASS", "FOUND"):
                open_work.append("lookahead_verdict")
        elif cohort == "not_tested_in_current_runtime":
            open_work.append("first_measurement_in_current_runtime")
        elif cohort == "excluded" and settled.get("state") in (
                "not_converged_within_ladder", "inconclusive"):
            open_work.append("convergence_" + settled["state"])
        # A recursion PASS that is not ours is as open a question as no
        # verdict at all. 79 unfinished rows rest on a PASS from the original
        # sweep or the frozen baseline - `BigPete` among them, which clears
        # both checks on inherited evidence alone and would otherwise sit
        # with nothing left to do and nothing of ours behind it. Admitted
        # rows already carry `re-measure_gates_in_current_runtime` for this;
        # the unfinished ones need the ladder itself.
        inherited_recursive_pass = (
            recursive in ("PASS", "PASS_1PCT")
            and not recursive_evidence.startswith("convergence")
            and cohort in ("excluded", "pending"))
        # `diagnostics` counts as having run here too. A row whose look-ahead
        # we measured natively has plainly started under this pipeline, even
        # when the trial-run store holds nothing for it - `mabStra` carries a
        # native WARMUP_NEEDED, a native look-ahead PASS, and was queued for
        # nothing, because the condition asked only about the two run stores.
        # Recursion evidence can exist under a store that keys
        # differently than measurement/window/diagnostics do -
        # `MabStra` carries a wave_b:28:superseded marker with none of
        # the other three present, because that store and
        # evidence/PROFILE_BIAS.json disagreed on which of two differently-cased,
        # differently-authored strategies (`MabStra` from davidzr,
        # `mabStra` from PeetCrypto) each entry belonged to. Any
        # recorded recursive_evidence is itself proof the row has been
        # touched before.
        if (measurement or window or diagnostics or recursive_evidence) \
                and (recursive not in ("PASS", "PASS_1PCT")
                     or inherited_recursive_pass):
            # Anything that runs and has no settled recursion verdict is a
            # question for the ladder: a FOUND no ladder has re-measured
            # rests on the parser that read the wrong column, an NA means
            # the check produced nothing to judge, WARMUP_NEEDED means it
            # never started, and an empty value means nobody has looked.
            open_work.append("recursive_ladder_pending")
        # An exclusion that does not rest on a measurement of this
        # implementation is an open question, and has to carry the work
        # that would settle it. Without this a row could sit in the
        # excluded list for good on an absent verdict, a verdict
        # borrowed from another environment, or a crash - and nothing
        # in the table would say so.
        if cohort == "not_a_strategy":
            # No work would change the answer, so none is listed. The reason
            # and the repair family still say what the file is and what went
            # wrong when it ran; only the promise of effort is dropped.
            open_work = []
        basis = exclusion_basis(reason, lookahead_evidence, source,
                                recursive_evidence) \
            if cohort in ("excluded", "pending", "too_few_trades") else ""
        # `excluded` is a verdict, and this audit does not issue a verdict on
        # somebody else's measurement or on the absence of one. A row whose
        # exclusion rests on an inherited result, or on no result at all, is
        # not excluded yet - it is unfinished, and says so until a measurement
        # of ours settles it. The decisive reason and the basis stay on the
        # row, so nothing is hidden by the change of name.
        if cohort == "excluded" and basis in ("inherited", "no_finding"):
            cohort = "exclusion_unconfirmed"
        repair = dict(triage.get(strategy) or {})
        # A row that was repaired has left the blocked set, and with it the
        # triage - so the label saying what ought to be done disappeared at
        # exactly the moment it became worth reading. What was done to it is
        # recovered from the repair runners instead.
        #
        # Except when triage still has something to say: a row can clear one
        # blocker through a repair route and still be blocked by a second,
        # unrelated one underneath it - FBB_2 left `local_module_off_path`
        # once `custom_indicators` was restored, and the next run surfaced
        # `no_stoploss`, which blocked_triage.py's fresh probe already
        # classified as `refuse_repair`. Overwriting that with the repair
        # route's own generic "repair_attempted" would hide a decided,
        # specific finding behind a vaguer one that is no longer current.
        if strategy in repair_source and repair.get("verdict") != "refuse_repair":
            repair["family"] = repair_source[strategy]
            if repair_run.get("status") == "measured":
                repair["verdict"] = "repaired"
            elif repair_run.get("status") == "failed":
                repair["verdict"] = "repair_attempted"
        # `attempted` is `repair/local_modules.py`'s OWN corpus-only search,
        # which only ever looks under `repos/**`. A row this audit repaired
        # by a different, later route - fetching the missing module from the
        # strategy's origin GitHub repo instead of finding a copy already in
        # the corpus - stays `unresolved` there forever, because that search
        # was never pointed at where the fetched copy actually lives
        # (`repair/compat_helpers/`). Without this guard a genuine
        # `repaired` verdict, set two lines above from a real `measured`
        # result, was silently overwritten back to `repair_attempted` here -
        # confirmed on `EmaCrossStrategy`/`PolymarketMeanReversionStrategy`/
        # `PolymarketMomentumStrategy`, each already trading (28/2/10 trades)
        # under a config `eligibility_timeframe_repair.py` built for it.
        # Same guard the block above already has, and for the same reason:
        # a fresh `refuse_repair` from `blocked_triage.py`'s own probe (e.g.
        # `no_stoploss`, once a module fix clears the way to a *second*,
        # unrelated blocker underneath it - `BinanceStream` does exactly
        # this) is a decided, specific finding and must not be replaced by
        # this block's vaguer "repair_attempted" either. Missing here
        # originally; only the sibling block above was guarded.
        if strategy in attempted and repair.get("verdict") not in (
                "repaired", "refuse_repair"):
            repair["verdict"] = "repair_attempted"
            repair["family"] = "local_module_off_path"
            repair["note"] = attempted[strategy]
        # `refused_timeframe` comes from `eligibility_timeframe_repair.py`'s
        # `cohort()`, which re-derives itself fresh from THIS row's current
        # `runtime_failure` on every call - membership here is never stale,
        # unlike `repair_source`, which can still name an earlier blocker a
        # later repair already cleared. `strategy not in repair_source` used
        # to gate this, so a row with ANY repair-store history (e.g.
        # `FileLoadingStrategy`, module-fixed then found to have no
        # timeframe declaration underneath) kept its old, now-superseded
        # `local_module_off_path` label instead of the current, correctly
        # refused one - the same "second blocker under the first" case the
        # comment above this block already describes, just not yet guarded
        # against here. Only skip if the row has since genuinely started
        # working.
        if strategy in refused_timeframe and repair.get("verdict") != "repaired":
            repair["verdict"] = "refuse_repair"
            repair["family"] = "timeframe_not_recoverable"
            repair["note"] = refused_timeframe[strategy].get("why", "")
        arm = freqai.get(strategy)
        if arm and arm.get("config"):
            arm_config = arm["config"].replace(BS_SEP, "/")
            repair.setdefault("settings_extra",
                              "freqai_config=" + arm_config +
                              "; freqaimodel=LightGBMRegressor")
        if arm:
            # The arm ran. Whatever the ordinary runner says about freqAI not
            # being enabled describes the ordinary config, not this strategy.
            repair["family"] = "freqai_arm"
            if arm["level"] == "PASSED":
                repair["verdict"] = "repaired"
                repair["note"] = ("measured by the FreqAI arm under the "
                                  "author's own config: %s trades. That run is "
                                  "not comparable with the spot audit and does "
                                  "not admit the row." % arm["trades"])
            elif "DI_cutoff" in arm["why"]:
                repair["verdict"] = "refuse_repair"
                repair["note"] = ("expects a custom model return freqtrade "
                                  "2026.7 does not emit (DI_cutoff) and its "
                                  "repository holds no matching model. "
                                  "Initialising the placeholder would change "
                                  "the decision logic, so it is not done.")
            elif "OperationalException" in arm["why"]:
                # A named, structural freqtrade exception (RLStrategy: "all
                # training data dropped due to NaNs") is a different claim
                # from the `else` branch below's "ran and produced nothing" -
                # freqtrade itself is stating why no model could ever train
                # under this row's feature window, not merely failing
                # silently. Supplying more/different training data than the
                # author configured would be authorship, not repair.
                repair["verdict"] = "refuse_repair"
                repair["note"] = ("the FreqAI arm's own run stopped on a "
                                  "named structural exception, not a silent "
                                  "failure: %s" % arm["why"][:150])
            else:
                repair["verdict"] = "repair_attempted"
                repair["note"] = ("the FreqAI arm ran it and it did not "
                                  "produce a summary: %s" % arm["why"][:120])
        if strategy in setup_faults:
            fault = setup_faults[strategy]
            repair["family"] = (fault.get("family")
                                or "measured_outside_its_design")
            repair["verdict"] = "to_be_fixed"
            repair["note"] = fault.get("why", "")
            repair["settings_extra"] = "would fix it: " + fault.get("fix", "")
        # What a shim earned depends on whether the check it unblocks has
        # since run. A native verdict means the repair did its job; no
        # verdict yet means the route is known and the run is still owed.
        if repair.get("family") == "framework_compat_shim" \
                and not repair.get("verdict"):
            repair["verdict"] = (
                "repaired"
                if lookahead_evidence in NATIVE_LOOKAHEAD_EVIDENCE
                and lookahead in ("PASS", "FOUND") else "to_be_fixed")
        if strategy in refused_repair:
            repair["verdict"] = "refuse_repair"
            repair["note"], refusal_family = refused_repair[strategy]
            if refusal_family:
                repair["family"] = refusal_family
        if strategy in withdrawn:
            repair["verdict"] = "repair_withdrawn"
            repair["family"] = "local_module_off_path"
        # C4: the repair route ran and refused on the author's own account -
        # not "nobody has looked yet" but "supplying this would invent the
        # strategy". `pending` promised a look that will never happen and
        # never change the answer, so the row is decided.
        if cohort == "pending" and repair.get("verdict") == "refuse_repair" \
                and repair.get("family") in NO_REPAIR_POSSIBLE:
            cohort = "excluded"
            reason = "repair_refused_would_invent_strategy"
            basis = "own_measurement"
            # Nothing is still owed: no ladder will ever run on a row that
            # never starts, so the pending-side flag from before this row was
            # decided does not belong on it any more.
            open_work = []
        # C4, reached from the gate rather than a trial-run failure: see
        # `invalid_gate_config` above. The row measures and trades fine, so
        # `repair` never carries a verdict for it; the refusal is the
        # lookahead gate's own, over the author's declared trailing-stop
        # combination.
        if cohort == "pending" and invalid_gate_config:
            cohort = "excluded"
            reason = "repair_refused_would_invent_strategy"
            basis = "own_measurement"
            repair["family"] = "invalid_declared_config"
            repair["verdict"] = "refuse_repair"
            open_work = []
        # C5: a repair route ran, searched the corpus for a candidate (or
        # applied one), and the row still does not start. `repair_attempted`
        # already means every candidate was tried and none worked;
        # `repair_withdrawn` means the one candidate that satisfied the
        # import shadowed an installed package and had to be taken back. In
        # three cases - Solipsis6, SolipsisMM, DWT - a candidate WAS applied
        # and the row moved past the import to a second, unrelated failure
        # (a missing attribute the module never defined, a read-only numpy
        # buffer); the search is exhausted either way, not merely undone.
        if cohort == "pending" and repair.get("family") == "local_module_off_path" \
                and repair.get("verdict") in ("repair_attempted", "repair_withdrawn"):
            cohort = "excluded"
            reason = "local_module_repair_exhausted"
            basis = "own_measurement"
            open_work = []
        # C6: the FreqAI arm already measured this row under the author's own
        # config, in a runtime this audit does not share. That is a genuine
        # measurement, not a gap - the row is decided, just not by this
        # audit's ordinary cohort. `refuse_repair` here means "not
        # comparable", not "no fix exists", which is why it is its own
        # criterion rather than folded into C4.
        if cohort == "pending" and repair.get("verdict") == "refuse_repair" \
                and repair.get("family") in ("freqai_arm", "freqai_config_built"):
            cohort = "excluded"
            reason = "measured_only_in_freqai_arm"
            basis = "own_measurement"
            open_work = []
        # C7 (owner's call, 2026-09-04): a package the author depended on is
        # not installed, and installing one changes the runtime every other
        # strategy runs under - not a decision to make row by row. Twenty
        # rows each name a specific missing module (`BBRSI` wants
        # `freqtrade.indicator_helpers`, `KMM` wants `openai`, and so on);
        # none of that changes by looking harder, only by deciding to
        # install it, which is declined here for all of them at once.
        if cohort == "pending" and repair.get("family") == "third_party_package":
            cohort = "excluded"
            reason = "third_party_package_declined"
            basis = "own_measurement"
            open_work = []
        # C8 (owner's call, 2026-09-04): every one of these 19 rows traces to
        # the same two mechanisms, not 19 different bugs. Eleven assign a
        # Python bool, int or float into a column pandas 3.0.5 now refuses to
        # coerce silently (`Invalid value '1' for dtype 'bool'` and its mirror
        # images). Eight - a Supertrend snippet credited to
        # freqtrade/freqtrade-strategies#30, copied near-verbatim into five
        # unrelated repositories - build a direction column with
        # `np.where(cond, np.where(..., 'down', 'up'), np.NaN)`, mixing a
        # string branch with a float NaN in one array, which numpy 2.5.2
        # refuses to promote to a common dtype where older numpy coerced it.
        # Both are fixable in principle - relax pandas' item-assignment
        # dtype check, or numpy's promotion rule - and both fixes would run
        # under every column write in the corpus, not just these rows' own.
        # That is the "large intervention" a narrow shim exists to avoid, so
        # none is written.
        #
        # Re-examined 2026-09-05, on the question of whether an upstream
        # source refresh would retire any of them. It would not. The snippet's
        # own author fixed it - `freqtrade/freqtrade-strategies` now calls
        # `ftt.supertrend` and keeps the direction column a pure string with
        # `.fillna("")` - and this corpus already carries that fixed file:
        # `FSupertrendStrategy` is admitted to E1 on it. The eight blocked
        # rows are stale COPIES in repositories whose own authors never
        # followed the fix, so re-fetching those repositories returns the same
        # broken line. What the re-examination did establish is that both
        # mechanisms raise rather than mis-compute, which is the bar every
        # other shim here is held to; whether that reopens the owner's call is
        # the owner's to decide, not this generator's.
        # `repair["family"]` can still read an earlier, already-fixed
        # problem - a row a compat shim rescued from "class does not load"
        # can land on this same dtype wall afterward, and the shim's family
        # keeps the slot (`MultiMA_TSL5`: whitespace_tolerant_class_scan
        # fixed the import, framework_compat_shim is what repair_source
        # still says, and the row is on the C8 dtype wall regardless). So
        # the raw failure text is checked too, not only the family tag.
        dtype_wall = (repair.get("family") == "dtype_drift"
                     or "could not be promoted" in (measurement.get("why") or ""))
        if cohort == "pending" and dtype_wall:
            cohort = "excluded"
            reason = "shared_runtime_change_declined"
            basis = "own_measurement"
            open_work = []
        if basis == "blocked" and not repair.get("verdict"):
            repair["verdict"] = "to_be_fixed"
        if basis == "blocked":
            # A blocked row that has been triaged says what would fix it. One
            # that has not says only that nobody has looked.
            open_work.append(repair.get("verdict") or "runtime_repair_pending")
        elif basis in ("inherited", "no_finding"):
            # Not only a borrowed verdict. A gate of ours that ran and
            # returned nothing - a timeout, an exception - has produced
            # no verdict either, and the row cannot rest on it.
            if lookahead_evidence not in NATIVE_LOOKAHEAD_EVIDENCE \
                    or lookahead not in ("PASS", "FOUND"):
                open_work.append("lookahead_remeasure_pending")
            if reason == "no_trades_in_full_measurement" \
                    and source != "full_window":
                open_work.append("full_window_measurement_pending")

        # An actual exclusion is terminal for the work queue.  Preserve its
        # evidence and reason, but do not promise a new measurement merely
        # because a supporting gate record is historical or incomplete.
        # `exclusion_unconfirmed` is intentionally not covered: it is not an
        # earned exclusion and must retain the work needed to decide it.
        if cohort == "excluded":
            open_work = []

        # Owner decision 2026-09-10: a successful, identity-bound canonical
        # pooled full backtest proves that this implementation already passed
        # the technical chain leading into Stage 7.  A later diagnostic-window
        # amendment must not put that completed implementation back in the
        # work queue.  This is deliberately a queue/provenance rule only: it
        # does not rewrite its historical cohort or exclusion decision.
        if full_backtest_complete:
            open_work = []
            gaps = []

        records = [measurement, diagnostics, window, settled,
                   fresh or {}, (diagnostics.get("lookahead") or {}),
                   (diagnostics.get("recursive") or {}), attempt]
        stamp, stamp_source = tested_at(records)
        duration_s, duration_evidence = test_duration(
            measurement, diagnostics, window, settled, fresh, tried, attempt)

        repo, source_file = provenance(profile.get("canonical_file"))
        run_profile = profile.get("run_profile")
        pairs = len((window.get("pair_results") or {}))
        # The full-window record is the better source for the backtest command
        # when it exists, because that run is the one measured over the whole
        # window; the smoke run is the shorter probe.
        backtest_record = window or measurement
        class1_entry = class1.get(strategy) or {}
        cmd_backtest = invocation(
            backtest_record, "backtest", run_profile,
            backtest_record.get("timerange") or measurement.get("timerange"),
            strategy, source_file, pairs, repair=class1_entry,
            run=repair_run)
        cmd_lookahead = invocation(
            fresh or diagnostics.get("lookahead") or {}, "lookahead", run_profile,
            (fresh or diagnostics.get("lookahead") or {}).get("timerange")
            or profile_bias_window(run_profile),
            strategy, source_file, repair=class1_entry,
            run=repair_run)
        cmd_recursive = invocation(
            settled or (diagnostics.get("recursive") or {}) or attempt,
            "recursive",
            run_profile,
            (settled.get("timerange")
             or (diagnostics.get("recursive") or {}).get("timerange")
             or attempt.get("timerange") or profile_bias_window(run_profile)),
            strategy, source_file, repair=class1_entry,
            run=repair_run)
        archive = next((p for p in evidence_paths(records) if p.endswith(".zip")), "")

        out.append({
            "strategy_id": strategy,
            "repo": repo,
            "source_file": source_file,
            "result_archive": archive,
            "run_profile": profile.get("run_profile", ""),
            "expansion_wave": wave,
            # evidence/execution_profiles.py's own column is the fresher,
            # more complete derivation - it also tries a sibling Config*.py
            # and a repair-store override, neither of which
            # evidence/STRATEGY_CLASSIFICATION.json's older, narrower pass
            # ever attempted. 54 rows carried a real value in one and
            # nothing in the other before this preferred it; a further 3
            # disagreed outright (`FisherBBDynamic`: this file's own live
            # `timeframe = '5m'`, one line under an author's commented-out
            # `# timeframe = '15m'` the older pass evidently read instead).
            # Falls back to classification only for the 2 rows where it
            # alone has a value.
            "timeframe": (profile.get("execution_timeframe")
                         or classification.get(strategy, {}).get("timeframe", "")),
            "strategy_type": classification.get(strategy, {}).get(
                "strategy_type", ""),
            "assumed_market_regime": phase_hypothesis.get(strategy, {}).get(
                "assumed_market_regime", ""),
            "assumed_market_regime_evidence": phase_hypothesis.get(
                strategy, {}).get("assumed_market_regime_evidence", ""),
            "cohort": cohort,
            "measured": "true" if (measurement.get("status") == "measured"
                                   or base.get("canonical_measured") == "true")
                        else "false",
            "observed_trades": trades,
            "trade_evidence": source,
            "test_duration_s": duration_s,
            "test_duration_evidence": duration_evidence,
            "lookahead": lookahead,
            "lookahead_evidence": lookahead_evidence,
            "recursive": recursive,
            "recursive_evidence": recursive_evidence,
            "coverage_status": coverage_status,
            "coverage_evidence": coverage_evidence,
            "full_backtest_status": full_backtest.get("status", ""),
            "technical_chain_complete": "true" if full_backtest_complete else "false",
            "traps_n": base.get("traps_n", ""),
            "artifact_role": profile.get("artifact_role", ""),
            "baseline_status": base.get("eligibility_status", ""),
            "exclusion_basis": basis,
            "repair_family": repair.get("family", ""),
            "repair_verdict": repair.get("verdict", ""),
            "gate_notes": "; ".join(part for part in (
                ("lookahead NA: " + ((fresh or tried
                                      or diagnostics.get("lookahead")
                                      or {}).get("why") or "no record")[:110])
                if lookahead == "NA" else "",
                ("recursive NA: " + ((diagnostics.get("recursive")
                                      or settled or {}).get("why")
                                     or "no record")[:110])
                if recursive == "NA" else "",
                # Provenance kept, never decisive: this row was part of the
                # original frozen 67 before the cohort was retired
                # 2026-09-03. Its own C1/C2 measurement now decides it like
                # every other row.
                ("originally in the frozen E0 baseline, retired 2026-09-03"
                 if base.get("regime_eligible") == "true" else ""),
                review_note,
                ("coverage %s: %s" % (coverage_status or "absent", coverage_detail[:110])
                 if coverage_status != "PASS" else "")) if part),
            "repair_settings": "; ".join(
                part for part in (repair_settings(class1_entry, repair_run),
                                  repair.get("settings_extra", "")) if part),
            "required_image": class1_entry.get("image", DEFAULT_IMAGE),
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


RUNTIME_OUT = os.path.join(ROOT, "RUNTIME_ENVIRONMENTS.md")

IMAGES = {
    "strategy-audit-runtime:2026.7": {
        "dockerfile": "runtime/Dockerfile.audit",
        "base": "freqtradeorg/freqtrade:2026.7 (pinned digest)",
        "adds": "runtime/requirements-audit-runtime.txt: numpy 2.5.2, pandas 3.0.5, "
                "scipy 1.18.1, TA-Lib 0.7.1, and the corpus's other ordinary "
                "dependencies.",
        "purpose": "The default. Every row not listed under one of the "
                   "images below runs on this one.",
    },
    "strategy-audit-tensorflow-runtime:2026.7": {
        "dockerfile": "runtime/Dockerfile.audit-tensorflow",
        "base": "python:3.12-slim (pinned digest) + freqtrade==2026.7 "
                "installed directly - a different base line from the "
                "default image, not a layer on top of it.",
        "adds": "runtime/requirements-audit-tensorflow.txt: the same "
                "runtime/requirements-audit-runtime.txt, plus tensorflow==2.21.0, "
                "keras==3.15.1, matplotlib==3.11.1. Its own build asserts "
                "numpy/pandas/scipy/talib/freqtrade land at the exact "
                "versions the default image pins, despite the different "
                "base - that assertion is what makes a row measured here "
                "comparable with one measured on the default image.",
        "purpose": "Rows whose own code imports TensorFlow/Keras at module "
                   "load time, independent of anything this audit does.",
    },
    "strategy-audit-packages-runtime:2026.7": {
        "dockerfile": "runtime/Dockerfile.audit-packages",
        "base": "strategy-audit-runtime:2026.7 - a layer on top of the "
                "default image, not a separate base line.",
        "adds": "runtime/requirements-audit-packages.txt: matplotlib, catboost, "
                "tslearn, pykalman. Each was checked with `pip install "
                "--dry-run` before being added - numpy, pandas and scipy "
                "were already satisfied at the pinned versions for all "
                "four, so none of them moves the core stack.",
        "purpose": "Rows whose own code imports a package the default "
                   "image does not carry, where that package installs "
                   "cleanly without touching the pinned numerical core.",
    },
}


def _runtime_environments_report(data):
    now = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")
    by_image = collections.defaultdict(list)
    for row in data:
        by_image[row["required_image"]].append(row)

    lines = [
        "# Runtime environments - what each strategy needs to run",
        "",
        "**Generated %s by `evidence/strategy_status.py`.** Regenerate it rather "
        "than editing it." % now,
        "",
        "For the benchmark run: before measuring a row, look up its "
        "`required_image` in `STRATEGY_STATUS.csv` and launch it under "
        "that image rather than the default. Everything else - which "
        "compatibility shims to install, which warm-up to use, which "
        "config overrides apply - is read automatically from "
        "`evidence/PROFILE_CLASS1.json` and `evidence/WARMUP_CONVERGENCE.json` by the same "
        "`profile_smoke.run_one` / `evidence/profile_full_window.py` machinery this "
        "audit already uses; the image is the one thing that machinery "
        "cannot decide for itself, because it is chosen before any Python "
        "in the container runs.",
        "",
        "## Images", "",
        "| Image | Dockerfile | Base | Rows |",
        "|---|---|---|---:|",
    ]
    for image, meta in IMAGES.items():
        lines.append("| `%s` | `%s` | %s | %d |" % (
            image, meta["dockerfile"], meta["base"], len(by_image.get(image, []))))
    lines.append("")

    for image, meta in IMAGES.items():
        rows_here = by_image.get(image, [])
        lines += [
            "## `%s`" % image, "",
            "**Adds:** %s" % meta["adds"], "",
            "**For:** %s" % meta["purpose"], "",
        ]
        if image == DEFAULT_IMAGE:
            lines += ["All %d rows not listed under another image below." %
                      len(rows_here), ""]
            continue
        lines += ["| Strategy | Cohort | Why |", "|---|---|---|"]
        for row in sorted(rows_here, key=lambda r: r["strategy_id"]):
            why = (row["repair_settings"] or row["runtime_failure"] or "")[:150]
            lines.append("| `%s` | %s | %s |" % (
                row["strategy_id"], row["cohort"], why.replace("|", "\\|")))
        lines.append("")

    return "\n".join(lines).encode("utf-8")


def _report(data):
    cohorts = collections.Counter(row["cohort"] for row in data)
    waves = collections.Counter(row["expansion_wave"] for row in data)
    work = collections.Counter(w for row in data
                               for w in row["open_work"].split(";") if w)
    measured = sum(1 for row in data if row["measured"] == "true")
    traded = sum(1 for row in data if _integer(row["observed_trades"]) > 0)
    stamped = sum(1 for row in data if row["last_tested_at"])
    completed_full = sum(1 for row in data
                         if row["technical_chain_complete"] == "true")
    passing = [r for r in data if r["cohort"] == "E1_expanded"]
    candidates = [r for r in data if r["cohort"] == "convergence_candidate"]
    pending = [r for r in data if r["cohort"] == "pending"]
    untested = [r for r in data if r["cohort"] == "not_tested_in_current_runtime"]
    failing = [r for r in data if r["cohort"] == "excluded"]
    unconfirmed = [r for r in data if r["cohort"] == "exclusion_unconfirmed"]
    now = datetime.datetime.now().replace(microsecond=0).isoformat(sep=" ")

    lines = [
        "# Strategy status - current evidence for all %d rows" % len(data), "",
        "**Generated %s by `evidence/strategy_status.py`.** Regenerate it rather than "
        "editing it." % now, "",
        "**This table decides nothing.** Admission happens only in",
        "`evidence/eligibility_expansion_adjudicate.py`; this is a reading of what has",
        "already been decided, collected from the smoke, bias, full-window,",
        "adjudication and convergence stores.", "",
        "**Completed full-backtest closure.** %d rows carry an exact, successful"
        % completed_full,
        "canonical pooled Stage-7 full-backtest identity (source hash, run profile and",
        "mode timerange). Their `technical_chain_complete=true` closes the technical",
        "work queue, even if a later diagnostic-window amendment made earlier evidence",
        "historical. This does not grant admission or overwrite an exclusion finding.", "",
        "**Terminal exclusions.** Every row in the `excluded` cohort is closed and",
        "therefore has no `open_work`. `exclusion_unconfirmed` is a distinct, unfinished",
        "cohort: it remains queued because the audit has not earned an exclusion verdict.", "",
        "`evidence/REGIME_ELIGIBILITY.csv` remains a frozen file and is never",
        "regenerated - but as of 2026-09-03 this table no longer treats its",
        "`regime_eligible=true` rows as automatically usable. The recursion",
        "check that produced them used freqtrade's own hardcoded candle",
        "counts, never converted to a strategy's timeframe, not the",
        "calendar-day ladder every other row is held to; measured under this",
        "audit's own ladder for the first time this week, 64 of the 67 held",
        "up and 1 (`MacdStrategy`) did not. Each of the 67 is now decided by",
        "the same C1/C2/C3 criteria as every other row. Original membership",
        "is kept as provenance in `gate_notes`, never as a reason to skip a",
        "check.", "",
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

    timeframes = collections.Counter(row["timeframe"] for row in data
                                     if row["timeframe"])
    types = collections.Counter(t for row in data
                                for t in row["strategy_type"].split(";") if t)
    no_type = len(data) - sum(1 for row in data if row["strategy_type"])
    no_tf = len(data) - sum(1 for row in data if row["timeframe"])
    lines += [
        "## Timeframe and signal family", "",
        "Both read from the strategy's own source by `strategy_classification.py`,",
        "not measured - see that module's docstring for the marker table and its",
        "limits. `timeframe` is blank on %d rows the source does not state it "
        "for. `strategy_type` can be more than one label - most rows carry two "
        "or three - and is blank on %d rows where no marker matched at all, so "
        "its counts below add up to more than %d." % (no_tf, no_type, len(data)),
        "",
    ]
    lines += _table(timeframes, "### Timeframe", "Timeframe")
    lines += _table(types, "### Signal family", "Type")

    phases = collections.Counter(
        phase for row in data
        for phase in row["assumed_market_regime"].split(";") if phase)
    no_phase = [row for row in data if not row["assumed_market_regime"]]
    model_driven = sum(1 for row in no_phase
                       if row["assumed_market_regime_evidence"].startswith(
                           "model_driven"))
    store = json.load(io.open(PHASE_HYPOTHESIS, encoding="utf-8")) \
        if os.path.exists(PHASE_HYPOTHESIS) else {}
    lines += [
        "## Assumed market phase", "",
        "**A prediction, written down before the benchmark that will test it.**",
        "It decides nothing here and clears no row. It is recorded now because",
        "a hypothesis formed after the per-phase numbers are on screen is not a",
        "hypothesis - the mirror image of the rule against tuning the regime",
        "labels to make strategies look specialised.", "",
        "The frozen primary model emits four states. These six split `SIDEWAYS`",
        "on volatility and add a shock phase that outranks the DMI label,",
        "because a dead low-volatility drift and a violent range reward",
        "opposite machinery, and a top-decile volatility day is the market",
        "whichever way ADX points. Owner's decision of 2026-09-05 on",
        "preregistration OPEN item 6; the amendment records it.", "",
        "| Phase | Market-side rule | Strategies predicted |",
        "|---|---|---:|",
    ]
    for phase, rule in (store.get("phases") or {}).items():
        lines.append("| `%s` | `%s` | %d |" % (phase, rule, phases.get(phase, 0)))
    lines += [
        "",
        "A row may carry more than one phase, and %d carry none: %d are "
        "model-driven, where the indicators are features of a model and say "
        "nothing about which phase it favours, and %d name no phase-bearing "
        "marker at all. Both are left blank rather than given an invented "
        "prior - a blank is itself testable, as the prediction that the row "
        "is phase-neutral." % (len(no_phase), model_driven,
                               len(no_phase) - model_driven),
        "",
        "`bear_trend` is rare by construction: %d of %d rows are long-only "
        "and a long-only strategy cannot earn in a sustained downtrend, so "
        "the direction gate removes it whatever the indicators suggest."
        % (sum(1 for row in _csv(PROFILES)
               if row.get("direction_capability") not in
               ("short_only", "long_short")), len(data)), "",
    ]

    timed = [row for row in data if row["test_duration_s"]]
    lines += [
        "## Test duration", "",
        "Wall-clock seconds each runner timed its own call at, summed per row",
        "across whichever of the trial-run backtest, the bias-store",
        "look-ahead/recursion pair, a later native look-ahead",
        "re-measurement, the warm-up ladder, a wave B recursion attempt, and",
        "the eight-pair full-window backtest actually ran for it - see",
        "`test_duration` in evidence/strategy_status.py for why this is a sum rather",
        "than a pick-one-source figure. %d of %d rows carry no stamp at all,"
        % (len(data) - len(timed), len(data)),
        "either because nothing has run yet or because no runner on that",
        "path records its own time.", "",
    ]
    if timed:
        total_hours = sum(_float(row["test_duration_s"]) for row in timed) / 3600.0
        lines += ["Summed across the %d rows that do: **%.1f hours** of this "
                  "audit's own compute so far." % (len(timed), total_hours), ""]
        slowest = sorted(timed, key=lambda r: -_float(r["test_duration_s"]))[:15]
        lines += ["### Slowest 15", "",
                  "| Strategy | Total | Breakdown |", "|---|---:|---|"]
        for row in slowest:
            lines.append("| `%s` | %ss | %s |" % (
                row["strategy_id"], row["test_duration_s"],
                row["test_duration_evidence"].replace("|", "\\|")))
        lines.append("")

    gates = ("cmd_backtest", "cmd_lookahead", "cmd_recursive")
    recorded = sum(1 for row in data for gate in gates
                   if row[gate].startswith("[recorded]"))
    total_cmds = sum(1 for row in data for gate in gates if row[gate])
    lines += [
        "## The order the checks run in", "",
        "The order is not arbitrary; each step needs what the one before it",
        "produces.", "",
        "**1. Trial run.** One month over eight pairs, widened to three months",
        "and then one year while fewer than ten trades are observed: does the",
        "strategy start, and does it trade. A strategy that fails here is `open`, never",
        "`excluded` - no check has seen it, so nothing about it has been",
        "judged. It is labelled `to_be_fixed` until the obstacle is either",
        "removed or shown to be the strategy's own; `repair_verdict` then says",
        "which it is, and that is a separate question from whether the strategy",
        "is still in play.", "",
        "**2. Recursion, on the warm-up ladder.** Second because it needs no",
        "trades - it compares indicator values, not signals - so it can judge a",
        "strategy the look-ahead check cannot yet touch. It produces the warm-up",
        "at which the indicators settle, which the next step needs.", "",
        "**3. Look-ahead, at that warm-up.** Freqtrade's `lookahead-analysis`",
        "builds a Backtesting object, and `Backtesting.__init__` takes",
        "`required_startup` from the strategy's declared `startup_candle_count`.",
        "So the check runs at whatever warm-up is in force - and 125 strategies",
        "declare none, which would have their signals compared on indicators",
        "still undefined at the start of the window. Running it after the ladder",
        "means running it at a value shown to settle them. This check needs ten",
        "trades and widens its window rather than failing when there are fewer.",
        "",
        "**4. Backtest over the full window.** Only for a strategy that has",
        "cleared both bias checks: `20200301-20260821`, six and a half years",
        "over all eight pairs, at the warm-up the ladder settled on. It is the",
        "most expensive step by a wide margin, which is why it comes last and",
        "only for strategies whose numbers can be trusted. Admission follows",
        "from it, and the market-phase work is built on it.", "",
        "## What excludes a strategy", "",
        "Three things, and nothing else. Each is a result this audit produced",
        "itself, on this data, in this runtime.", "",
        "| | Criterion | Machine test |",
        "|---|---|---|",
        "| C1 | Look-ahead found | `lookahead == \"FOUND\"` and "
        "`lookahead_evidence == \"native\"` |",
        "| C2 | Recursion found | `recursive_evidence == "
        "\"convergence:not_settled\"` |",
        "| C3 | Never trades | `no_trades_in_full_measurement` with "
        "`trade_evidence == \"full_window\"` |", "",
        "**A strategy satisfying none of these is not excluded.** It is",
        "unfinished, and `open_work` names what is missing. Five things have",
        "at one time or another excluded strategies here and have been",
        "withdrawn: the source-code trap heuristic, a verdict inherited from",
        "the original sweep, an `NA`, the analyzer refusing for want of a",
        "warm-up, and a failed trial run. Three of them had removed",
        "strategies from the work before anyone looked at them.", "",
        "C3 has one further condition, and four of the eleven rows failed it:",
        "zero trades is the strategy's own property only when nothing on our",
        "side stopped it trading. `BasketStrategy` marks 8831 entries and",
        "sizes every one to zero, because a portfolio basket measured one",
        "pair at a time has no portfolio to weight against. `MostOfAll` loses",
        "its supertrend to pandas copy-on-write. `FundingCarry` needs funding",
        "rates it cannot have on spot, and `Insomnia_short` raises only short",
        "signals with `can_short` unset. Those four read `open`, not",
        "`excluded`.", "",
        "The criteria in full are in `evidence/exclusion_criteria_list.md`, and every",
        "repair route taken - with the message freqtrade gave beforehand - in",
        "`evidence/repair_measures_list.md`. Both are written by this same command,",
        "from these same rows, and the generator refuses a row excluded for a",
        "reason nobody has written down, or a repair route taken and not",
        "recorded. So a new ground or a new repair reaches those lists by",
        "being used, not by being remembered.", "",
        "## Windows and pairs each check uses", "",
        "A number cannot be read without knowing what it was measured over.",
        "The checks do not share a window, and two of them do not share the",
        "pair set either.", "",
        "| Check | Window | Pairs |",
        "|---|---|---|",
        "| Trial run (`profile_smoke`) | 1 month -> 3 months -> 1 year; stop at 10 trades | all 8 |",
        "| Bias check, spot | `20200301-20200601`, three months | `BTC/USDT` only |",
        "| Bias check, futures | `20200301-20200601`, three months | `BTC/USDT:USDT` only |",
        "| Look-ahead, first fallback | `20200101-20220101` | BTC only |",
        "| Look-ahead, second fallback | `20200301-20260820` | BTC only |",
        "| Full run (`profile_full_window`) | `20200301-20260821`, 6.5 years | all 8 |",
        "",
        "The eight pairs against USDT are BTC, ETH, LTC, XRP, ADA, XLM, XMR and",
        "DASH, at a 0.1 percent fee with `max_open_trades=8`.",
        "",
        "**One pair for the bias checks is freqtrade's own doing**, not a choice",
        "of this audit: `recursive-analysis` logs \"Using pair BTC/USDT only for",
        "recursive analysis. Replacing whitelist.\" and replaces whatever the",
        "config holds.",
        "",
        "**The look-ahead check widens its window rather than failing.** It needs",
        "ten trades; when the frozen window yields fewer it retries on the first",
        "fallback and then the second, and the record keeps every window it",
        "tried in `attempted_timeranges`. A verdict from a wider window is still",
        "that strategy's verdict, but it was not reached over the same span as",
        "its neighbour's.",
        "",
        "**The trial run answers one question:** does the strategy start and",
        "trade. It begins with one month and, below ten trades, follows the",
        "fixed three-month and one-year rungs. What it earns is measured later,",
        "over the full window.",
        "",
        "The warm-up ladder steps in days - 1, 2, 7, 14, 30, 90, 365 - converted",
        "to each strategy's own timeframe, and accepts a rung once every",
        "indicator stays inside 1.0 percent.", "",
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
        "stay admitted - E1 is frozen and this table decides nothing -",
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
    assert profile_bias_window("spot_long") == "20200301-20200601"
    assert profile_bias_window("futures_longshort") == "20200301-20200601"
    data = rows()
    corpus_size = len(_csv(PROFILES))
    assert len(data) == corpus_size, (len(data), corpus_size)
    assert len({row["strategy_id"] for row in data}) == corpus_size
    # E0_strict67 was retired as a cohort on 2026-09-03: the recursion check
    # that produced these 67 used freqtrade's own hardcoded defaults, never
    # converted to the strategy's timeframe, not the calendar-day ladder
    # every other row is held to. Its own name is kept as provenance in
    # `gate_notes`, never as a shortcut past a row's own C1/C2 measurement.
    baseline = {r["strategy_id"]: r for r in _csv(ELIGIBILITY)}
    frozen = {s for s, r in baseline.items() if r["regime_eligible"] == "true"}
    assert len(frozen) == 67, len(frozen)
    assert not {row["strategy_id"] for row in data
               if row["cohort"] == "E0_strict67"},         "E0_strict67 must never be assigned again"
    noted = {row["strategy_id"] for row in data
            if "frozen E0 baseline" in row["gate_notes"]}
    assert noted == frozen, sorted(noted ^ frozen)
    admitted = {r["strategy_id"] for r in _csv(ADJUDICATION)
                if r["adjudication_status"] == "admitted_E1"}
    assert {row["strategy_id"] for row in data
            if row["cohort"] == "E1_expanded"} == admitted
    completed = [row for row in data
                 if row["technical_chain_complete"] == "true"]
    assert completed, "expected current canonical full-backtest completions"
    assert all(not row["open_work"] for row in completed), \
        "completed full backtests must not be queued again"

    # Every row invariant belongs in one loop. This block was split in two by
    # a bad patch on 2026-09-01: half of it ended up inside the store
    # cross-check below and ran against a single leftover row, so four checks
    # were passing on 1 of 900 rows. A test that reports PASS while covering
    # almost nothing is worse than no test.
    for row in data:
        # Excluded means one of exactly nine things, and every one of them
        # is a result this audit produced itself: the look-ahead check found
        # bias, our own ladder failed to settle the indicators (either by
        # exceeding the drift threshold, or by crashing at every rung down to
        # the three longest lead times - the ladder must be passable by every
        # strategy, so exhausting it is itself the finding), the strategy
        # ran the whole window and never traded, a repair route read the file
        # and refused to invent what the author never wrote, a repair route
        # exhausted every candidate module the corpus holds, the row is
        # already measured (just in the separate FreqAI arm), or the only
        # known fix would change something every strategy in the corpus
        # shares - an installed package, or pandas'/numpy's own type rules -
        # and touching that for one row was declined. Nothing else may put a
        # row here - in particular not the source-code trap heuristic, which
        # excluded 40 running strategies before either bias check had seen
        # them, and not a verdict inherited from the original sweep.
        if row["cohort"] == "excluded":
            assert row["exclusion_basis"] == "own_measurement",                 (row["strategy_id"], row["exclusion_basis"])
            assert (
                (row["lookahead"] == "FOUND"
                 and row["lookahead_evidence"] == "native")
                or row["recursive_evidence"] == "convergence:not_settled"
                or row["recursive_evidence"] == "convergence:crash_exhausted"
                or row["primary_reason"] == "no_trades_in_full_measurement"
                or row["primary_reason"] == "repair_refused_would_invent_strategy"
                or row["primary_reason"] == "local_module_repair_exhausted"
                or row["primary_reason"] == "measured_only_in_freqai_arm"
                or row["primary_reason"] == "third_party_package_declined"
                or row["primary_reason"] == "shared_runtime_change_declined"
            ), (row["strategy_id"], row["primary_reason"],
                row["lookahead"], row["recursive_evidence"])
        # A trap is a fact about the source, never a verdict. It may sit on
        # any row, and it may decide none.
        # Too rare to measure is not a verdict against the strategy, so it
        # is never `excluded`, and it is never usable either. It rests on our
        # own run over the full window, so it must say so.
        if row["cohort"] == "too_few_trades":
            # The reason may carry a second clause naming our own setup,
            # which is a fact about the measurement rather than a second
            # verdict. What may not happen is the first clause changing.
            assert row["primary_reason"].startswith(
                "too_few_trades_to_measure"), row["strategy_id"]
            assert row["exclusion_basis"] == "own_measurement",                 row["strategy_id"]
            assert row["lookahead"] == "NA", row["strategy_id"]
        # A file that is not a strategy is neither admitted nor excluded:
        # there is no verdict to reach about a test fixture. It says what it
        # is, and it asks for nothing.
        if row["artifact_role"] and row["artifact_role"] != "strategy":
            assert row["cohort"] == "not_a_strategy",                 (row["strategy_id"], row["cohort"])
            assert not row["open_work"], row["strategy_id"]
        if row["cohort"] == "not_a_strategy":
            assert row["artifact_role"] != "strategy", row["strategy_id"]
        if row["traps_n"] not in ("", "0"):
            assert "trap" not in row["primary_reason"], row["strategy_id"]
        if row["cohort"] in ("excluded", "exclusion_unconfirmed", "pending",
                             "not_tested_in_current_runtime",
                             "not_a_strategy", "too_few_trades"):
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
        # A look-ahead finding disqualifies a row whatever its warm-up does.
        # Convergence is about recursion and answers a different question.
        for gate in ("lookahead", "recursive"):
            if row[gate] == "FOUND":
                assert row["cohort"] not in ("convergence_candidate",
                                             "E0_strict67", "E1_expanded"), \
                    (row["strategy_id"], gate, row["cohort"])
        # A recursion finding the ladder confirmed - it ran every rung and the
        # drift stayed - is a closed case, never an open question.
        if row["recursive_evidence"] == "convergence:not_settled":
            assert row["cohort"] in ("excluded", "exclusion_unconfirmed"), \
                (row["strategy_id"], row["cohort"])
        # A strategy that did not pass the trial run is open, never excluded:
        # nothing has been judged about it.
        if row["exclusion_basis"] == "blocked":
            assert row["cohort"] == "pending", \
                (row["strategy_id"], row["cohort"])
            assert row["repair_verdict"], row["strategy_id"]
        # A candidate must have cleared both gates, not merely failed neither.
        if row["cohort"] == "convergence_candidate":
            # The same standard admission uses: a PASS borrowed from the
            # original sweep is an absence claim from an environment that could
            # not measure, and cannot carry a row towards admission.
            assert row["lookahead"] == "PASS" \
                and row["lookahead_evidence"] in NATIVE_LOOKAHEAD_EVIDENCE, \
                (row["strategy_id"], row["lookahead"], row["lookahead_evidence"])
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
        # A repaired row must be runnable again by somebody reading this table
        # alone: either the calls were recorded, or the settings that
        # reproduce them are stated. A repair nobody can repeat is a claim,
        # not a result.
        if row["repair_verdict"] == "repaired":
            assert row["repair_settings"] or \
                row["cmd_backtest"].startswith("[recorded]"), row["strategy_id"]
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
            assert not row["open_work"], \
                "an excluded strategy must not remain in the work queue: %s" % \
                row["strategy_id"]
        if row["cohort"] == "exclusion_unconfirmed" \
                and row["exclusion_basis"] != "own_measurement":
            assert row["open_work"], \
                "%s: unconfirmed exclusion on %s with no work queued" % (
                    row["strategy_id"], row["exclusion_basis"])
        # A recovered timestamp always names where it came from.
        assert bool(row["last_tested_at"]) == bool(row["last_tested_source"]), \
            row["strategy_id"]

    # Every native re-measurement must be visible in the table. A verdict that
    # exists in a store this generator does not read is worse than no verdict:
    # the table looks current and is not. A row with a current (sha-matched)
    # entry in evidence/LOOKAHEAD_INDICATOR_REVIEW.json is the one deliberate
    # exception: its FOUND was reviewed and demoted to PASS by hand, so its
    # table verdict is expected to differ from the raw store.
    fresh_store = {}
    fresh_store_sha = {}
    for store in LOOKAHEAD_STORES:
        for name, record in _json(store).items():
            gate = record.get("lookahead") or {}
            if gate.get("status") in ("PASS", "FOUND"):
                fresh_store[name] = gate["status"]
                fresh_store_sha[name] = record.get("canonical_sha256")
    by_id = {r["strategy_id"]: r for r in data}
    lookahead_review = _json(LOOKAHEAD_INDICATOR_REVIEW, key="reviewed")
    reviewed_seen = set()
    for name, status in fresh_store.items():
        review = lookahead_review.get(name)
        reviewed = (status == "FOUND" and review
                    and review.get("canonical_sha256") == fresh_store_sha.get(name))
        if reviewed:
            reviewed_seen.add(name)
            assert by_id[name]["lookahead"] == "PASS", (name, status)
            assert by_id[name]["lookahead_evidence"] == "reviewed_indicator_only", name
        else:
            assert by_id[name]["lookahead"] == status, (name, status)
            assert by_id[name]["lookahead_evidence"] == "native", name

    # The check above only walks LOOKAHEAD_STORES; evidence/PROFILE_BIAS.json (the
    # original corpus-wide sweep) is the other source `rows()` reads via
    # `diagnostics`, at lower precedence. Re-check every reviewed row against
    # whichever of the two actually produced its FOUND, so a review whose sha
    # no longer matches anything currently FOUND - stale, or never matched -
    # is caught instead of silently, permanently trusted.
    combined_sha = dict(fresh_store_sha)
    combined_status = dict(fresh_store)
    for name, record in _json(BIAS).items():
        gate = record.get("lookahead") or {}
        if gate.get("status") in ("PASS", "FOUND") and name not in combined_status:
            combined_status[name] = gate["status"]
            combined_sha[name] = record.get("canonical_sha256")
    for name, review in lookahead_review.items():
        assert combined_status.get(name) == "FOUND" \
            and combined_sha.get(name) == review.get("canonical_sha256"), name
        assert by_id[name]["lookahead"] == "PASS", name
        assert by_id[name]["lookahead_evidence"] == "reviewed_indicator_only", name

    # The old ledger is reference material, not evidence. It records what the
    # original author's sweep did in an environment that did not establish this
    # audit's preconditions, so a row appearing there proves nothing about
    # whether it works under the current runtime. It is read only to attach a
    # historical hint, never to decide a cohort or to clear a row.
    assert len({r["strategy"] for r in _csv(LEDGER)}) == 895
    assert all(r["strategy_type"] for r in data), \
        "strategy_type must be explicit: family, unclassified, or not_applicable"
    print("strategy_status selftest: PASS (%d rows, %d ex-E0, %d E1, %d unmeasured, "
          "%d timestamped)"
          % (len(data), len(noted), len(admitted),
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
    rendered = {OUTPUT: _csv_bytes(data), REPORT: _report(data),
               RUNTIME_OUT: _runtime_environments_report(data)}
    if args.check:
        # The report embeds its generation time, so it is stale by definition
        # a second after it is written. Only the row data is compared.
        current = io.open(OUTPUT, "rb").read() if os.path.exists(OUTPUT) else b""
        if current != rendered[OUTPUT]:
            print("stale: %s" % os.path.relpath(OUTPUT, ROOT))
            return 1
        from evidence import exclusion_criteria
        for path, build in ((exclusion_criteria.CRITERIA_OUT,
                             exclusion_criteria.criteria_report),
                            (exclusion_criteria.REPAIRS_OUT,
                             exclusion_criteria.repair_report)):
            before = (io.open(path, "rb").read()
                      if os.path.exists(path) else b"")
            build(data, path)
            after = io.open(path, "rb").read()
            if before != after:
                print("stale: %s" % os.path.relpath(path, ROOT))
                return 1
        exclusion_criteria.selftest()
        print("strategy status: current")
        return 0
    for path, content in rendered.items():
        _write(path, content)
    counts = collections.Counter(row["cohort"] for row in data)
    for cohort, count in counts.most_common():
        print("%s: %d" % (cohort, count))
    # The exclusion criteria and the repair routes describe these same rows,
    # and a reference that lags the table it describes is worse than none:
    # it reads as current. So they are written here rather than by a separate
    # command somebody has to remember. exclusion_criteria.selftest is what
    # refuses a row excluded for a reason nobody has written down, and a
    # repair route taken and not recorded.
    from evidence import exclusion_criteria
    exclusion_criteria.criteria_report(data, exclusion_criteria.CRITERIA_OUT)
    exclusion_criteria.repair_report(data, exclusion_criteria.REPAIRS_OUT)
    exclusion_criteria.selftest()
    return 0


if __name__ == "__main__":
    sys.exit(main())
