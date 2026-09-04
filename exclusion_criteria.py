# -*- coding: utf-8 -*-
"""The criteria that put a strategy out, and the ones that only look like it.

Written because the distinction kept getting lost. Over the course of this
audit five different things have at one time or another moved a strategy into
`excluded`, and only three of them were findings. The other two were a
source-code heuristic and a verdict inherited from an environment whose
preconditions we never established. Both were withdrawn once looked at, and
both had by then taken 53 strategies out of the work.

So this file is not a description of what the table happens to contain. It is
the standard the table is held to, and `selftest` checks the table against it:
every excluded row must satisfy one of the criteria here, and every criterion
must still match rows. A criterion nothing matches any more is either finished
or wrong, and either way that should be said out loud rather than left
standing.

The list is meant to be used forwards as well. A strategy sitting under `open`
or `exclusion unconfirmed` can be checked against these conditions directly: if
one holds on evidence of ours, the strategy is excluded and the question is
closed. If none holds, the strategy is not excluded - it is unfinished, and
what is missing is named in `open_work`.

Both documents this writes are generated. Editing them by hand loses the edit
on the next run; change the criteria here instead.
"""
from __future__ import print_function

import argparse
import collections
import csv
import io
import json
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
TRIAGE = os.path.join(ROOT, "BLOCKED_TRIAGE.json")
CLASS1 = os.path.join(ROOT, "PROFILE_CLASS1.json")
CRITERIA_OUT = os.path.join(ROOT, "exclusion_criteria_list.md")
REPAIRS_OUT = os.path.join(ROOT, "repair_measures_list.md")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _json(path):
    if not os.path.exists(path):
        return {}
    return json.load(io.open(path, encoding="utf-8"))


# ---------------------------------------------------------------- criteria

def _lookahead_found(row):
    return (row["lookahead"] == "FOUND"
            and row["lookahead_evidence"] == "native")


def _recursion_found(row):
    return row["recursive_evidence"] == "convergence:not_settled"


def _never_trades(row):
    return (row["primary_reason"] == "no_trades_in_full_measurement"
            and row["trade_evidence"] == "full_window")


def _no_repair_possible(row):
    return row["primary_reason"] == "repair_refused_would_invent_strategy"


def _local_module_exhausted(row):
    return row["primary_reason"] == "local_module_repair_exhausted"


def _freqai_arm_only(row):
    return row["primary_reason"] == "measured_only_in_freqai_arm"


def _third_party_package_declined(row):
    return row["primary_reason"] == "third_party_package_declined"


def _shared_runtime_change_declined(row):
    return row["primary_reason"] == "shared_runtime_change_declined"


CRITERIA = [
    {
        "id": "C1",
        "name": "Look-ahead bias found",
        "test": _lookahead_found,
        "columns": 'lookahead == "FOUND" and lookahead_evidence == "native"',
        "what": "freqtrade's `lookahead-analysis` compared the strategy's "
                "signals against a run allowed to see the whole window, and "
                "the signals moved. The strategy is reading data it could not "
                "have had at the time.",
        "why_final": "This is the one defect no repair can undo without "
                     "rewriting what the author wrote. A strategy that reads "
                     "future candles has no measurable performance: every "
                     "number it produces is a number about the future.",
        "evidence": "The record names how many entries and exits of how many "
                    "signals moved, and which indicators carry it. A verdict "
                    "reached on fewer than ten signals does not count - the "
                    "analyzer widens its window rather than ruling on too "
                    "little.",
        "watch": "`lookahead_evidence` must read `native`. A FOUND carried "
                 "over from the original sweep is not this criterion but an "
                 "inherited claim, and the check has to be run here.",
    },
    {
        "id": "C2",
        "name": "Recursion bias found by our own ladder",
        "test": _recursion_found,
        "columns": 'recursive_evidence == "convergence:not_settled"',
        "what": "The warm-up ladder climbed every rung the data allows - 1, "
                "2, 7, 14, 30, 90 and 365 days, converted to the strategy's "
                "own timeframe - and at each of them at least one indicator "
                "still moved by 1.0 % or more against the full-history run. "
                "The indicator never settles, so its value depends on where "
                "the backtest happens to start.",
        "why_final": "Nothing downstream can be trusted: the same strategy on "
                     "the same data gives different signals for a different "
                     "start date.\n\n"
                     "**How high the ladder actually got, stated plainly.** "
                     "Not one of these rows was offered a full year. The bias "
                     "window leaves 97222 candles of prefix history, and a "
                     "365-day warm-up at five minutes needs 105120, so the "
                     "top rung is unreachable by data rather than by choice. "
                     "Forty-five of the 59 reached 90 days; fourteen reached "
                     "14, their timeframe being too coarse for more history "
                     "to exist. Until 2026-09-03 the ceiling was lower still "
                     "- freqtrade's OHLCV call budget capped every warm-up at "
                     "4999 candles, fourteen days at five minutes - and "
                     "lifting it (`startup_candles_not_limited_by_call_"
                     "budget`) settled two rows outright and more than halved "
                     "the residual drift on 24 others. Testing a full year "
                     "would need a later bias window, which is frozen.",
        "evidence": "The record keeps the whole drift table - one column per "
                    "rung, one row per indicator - so the finding can be read "
                    "rather than taken on faith, along with the rungs the "
                    "ladder was able to offer. A record made under a ceiling "
                    "that has since been lifted is kept under `superseded` "
                    "rather than deleted; 131 strategies carry such a "
                    "history.",
        "watch": "`recursive_evidence` must start with `convergence:`. A "
                 "FOUND from the baseline, or from a Wave B run under the "
                 "parser that read the wrong column, is not this criterion. "
                 "Two further things that are not findings: the analyzer "
                 "printing no table while reporting no variance on any "
                 "indicator, which is the strongest possible pass, and an "
                 "indicator printed as `nan%` at every rung, which is a "
                 "column the analyzer cannot express as a percentage at all.",
    },
    {
        "id": "C3",
        "name": "Ran the whole window and never traded",
        "test": _never_trades,
        "columns": 'primary_reason == "no_trades_in_full_measurement" '
                   'and trade_evidence == "full_window"',
        "what": "The strategy started, ran `20200301-20260821` across all "
                "eight pairs, and opened no position at all.",
        "why_final": "There is nothing to classify. Market-phase efficiency "
                     "is a statement about trades, and this strategy makes "
                     "none in six and a half years. Several are deliberate: a "
                     "template, a demonstration of stop-loss handling, a "
                     "strategy whose entry column is set to False in the "
                     "source.",
        "evidence": "Eight per-pair runs over the full window, each with its "
                    "own archive and hash.",
        "watch": "`trade_evidence` must read `full_window`. Zero trades in "
                 "the one-month trial run means nothing - the window is too "
                 "short to expect any. And a strategy that trades nothing "
                 "because it was given the wrong profile - a futures strategy "
                 "run on spot, a short-only strategy with `can_short` unset - "
                 "is a setup fault of ours, not this criterion.",
    },
    {
        "id": "C4",
        "name": "No repair exists that would not invent the strategy",
        "test": _no_repair_possible,
        "columns": 'primary_reason == "repair_refused_would_invent_strategy"',
        "what": "The strategy declares no timeframe anywhere, no stoploss "
                "or an explicit stoploss of 0, no exit logic, no "
                "`populate_indicators` at all, names a prediction model "
                "that no longer exists and that this repository holds no "
                "copy of, opens a data file (a pre-trained model, a lookup "
                "table) the author's own repository never included, or "
                "declares two config values in a combination freqtrade "
                "refuses (`trailing_stop_positive_offset` below "
                "`trailing_stop_positive`). A repair route read the file "
                "looking for the author's own value and found none to "
                "restore, or found two declared values that cannot both be "
                "honoured without guessing which one the author meant.",
        "why_final": "This is the same ground as C1 and C2, one step "
                     "earlier: those found that the measurement cannot be "
                     "trusted, this finds that no measurement can be taken "
                     "at all without writing the missing part ourselves. "
                     "Supplying a timeframe, a stoploss, an exit signal or a "
                     "model the author never named would not repair the "
                     "strategy - it would measure a strategy of our own "
                     "invention wearing the author's name.",
        "evidence": "`repair_family` names which requirement is missing "
                    "(`timeframe_not_recoverable`, `no_stoploss`, "
                    "`no_exit_logic`, `freqai_model`) and `repair_settings` "
                    "or the row's note in `repair_measures_list.md` records "
                    "what was searched and where.",
        "watch": "`freqai_arm` and `freqai_config_built` are also recorded "
                 "as `refuse_repair` but are not this criterion: both are "
                 "measured in the separate FreqAI arm, under the author's "
                 "own configuration, and refused only for this audit's "
                 "ordinary cohort - a different question from whether any "
                 "measurement is possible.",
    },
    {
        "id": "C5",
        "name": "Local module repair exhausted every candidate",
        "test": _local_module_exhausted,
        "columns": 'primary_reason == "local_module_repair_exhausted"',
        "what": "The strategy imports a helper the author shipped beside it "
                "in their own repository, and the corpus copy has nowhere to "
                "resolve from on its own. `repair_local_modules.py` searched "
                "the whole corpus for another copy that satisfies the import.",
        "why_final": "Three shapes, the search exhausted either way. No "
                     "candidate imports at all - `BaseStrategy`, "
                     "`BinanceStream` and four others, each candidate's own "
                     "failure recorded. The one candidate that does import "
                     "would shadow an installed package (`freqtrade` itself, "
                     "for `DualModelPolymarketPortfolio` and three peers) and "
                     "was applied, found to break other rows, and withdrawn. "
                     "Or a candidate was applied and the row moved past the "
                     "import to a second failure the import test cannot see - "
                     "`Solipsis6` and `SolipsisMM` reach werkkrew's "
                     "`custom_indicators` module and then call a function it "
                     "does not define; `DWT` reaches a read-only numpy "
                     "buffer past its own module fix. Restoring a module we "
                     "cannot verify against the author's own copy would be "
                     "writing code under their name.",
        "evidence": "`REPAIR_LOCAL_MODULES.json` keeps every candidate tried "
                    "and why each failed, or the shadowing that forced a "
                    "withdrawal recorded in `PROFILE_CLASS1.json` with "
                    "`status: withdrawn` rather than deleted.",
        "watch": "A row with NO entry in `REPAIR_LOCAL_MODULES.json` at all "
                 "has not been searched, not searched-and-refused - that is "
                 "`needs_a_look`, not this criterion, and three rows moved "
                 "from there to a working repair the same day this criterion "
                 "was written (`Solipsis3`, `SolipsisCon`, `Solipsis4`, "
                 "`Dyna_opti`), which is the reason `repair_attempted` is "
                 "trusted here only once `repair_local_modules.py` has "
                 "actually run against the row.",
    },
    {
        "id": "C6",
        "name": "Measured only in the separate FreqAI arm",
        "test": _freqai_arm_only,
        "columns": 'primary_reason == "measured_only_in_freqai_arm"',
        "what": "The strategy is only half a strategy without its FreqAI "
                "configuration - the feature set, the model, the training "
                "window live in a config file, not the source - and it was "
                "measured with the author's own config, in the FreqAI arm's "
                "own runtime.",
        "why_final": "Not a gap, a different measurement. The FreqAI arm "
                     "answers a different question, under a different "
                     "runtime, with the author's own settings rather than "
                     "this audit's frozen basket and windows. Its result is "
                     "real and is kept - `WTAI` and `WTRSIAI` both start and "
                     "trade under the config `repair/freqai_config_wtai.py` "
                     "rebuilt from the author's own commented block - it is "
                     "just not comparable with the ordinary cohort, so it "
                     "cannot admit a row here either.",
        "evidence": "The arm's own result card - trades, verdict, the config "
                    "used - travels with the row in `repair_settings` and "
                    "`repair/results_freqai`.",
        "watch": "This is the one criterion that is not a finding against "
                 "the strategy. A row here may run perfectly well; it is "
                 "excluded from THIS cohort because this audit's own "
                 "preconditions - the eight-pair basket, the frozen windows, "
                 "the shared runtime - were never applied to it.",
    },
    {
        "id": "C7",
        "name": "A missing package with no safe way found to supply it",
        "test": _third_party_package_declined,
        "columns": 'primary_reason == "third_party_package_declined"',
        "what": "The strategy imports a package this runtime does not "
                "install - sometimes declared by the author, sometimes not, "
                "sometimes no longer installable at all.",
        "why_final": "Superseded 2026-09-04 from a blanket refusal to a "
                     "row-by-row search. The original call - installing a "
                     "package changes what every one of the ~900 corpus "
                     "strategies imports into - is still true of the shared "
                     "runtime, but it stops applying the moment the package "
                     "is installed into an ISOLATED companion image instead: "
                     "`strategy-audit-packages-runtime` (matplotlib, "
                     "catboost, tslearn, pykalman - each checked beforehand "
                     "with `pip install --dry-run`, no core-stack version "
                     "bump) and the existing `strategy-audit-tensorflow-"
                     "runtime` (matplotlib added there too, for "
                     "`CryptoPredictionTraining`'s second import). Four rows "
                     "moved off this criterion that way (`MKR`, `Persia` "
                     "moved under C-none entirely once measured; "
                     "`TwoCandleTheory`; `BBRSI`, which also needed its "
                     "timeframe recovered once loading got that far) and "
                     "three more turned out to need nothing installable at "
                     "all once the real blocker was reached - "
                     "`TrainCatBoostStrategy` and `CryptoPredictionTraining` "
                     "moved to C4 (no stoploss declared), `Prediction_"
                     "Strategy` to a missing pre-trained model file no "
                     "corpus copy holds, neither a packaging question. "
                     "Thirteen remain, individually investigated rather "
                     "than assumed: five want `zigzag`, whose published "
                     "sdist has a malformed `pyproject.toml` build "
                     "requirement (`Cython>=^0.29`, invalid PEP 508 syntax) "
                     "that this pip refuses to build; `LitmusSimpleStrategy` "
                     "wants `cointanalysis`, which is not on PyPI under any "
                     "name tried; four `Litmus*` rows and that same one want "
                     "`freqtrade.litmus`, which lives inside "
                     "`markdregan_FreqAI-Marcos-Lopez-De-Prado`'s own "
                     "vendored `freqtrade/` tree - putting that repository "
                     "on the path risks the real freqtrade package "
                     "resolving to its fork instead; `KMM` wants `openai` to "
                     "call a live model during indicator computation, which "
                     "installing would not make a deterministic backtest; "
                     "`Enchilada` wants `technical.tradingview`, a whole "
                     "class (`SummaryConsensus`) the `technical` package "
                     "dropped, which would need vendoring real algorithm "
                     "code rather than restoring one textbook function; "
                     "`GymStrategy` wants `stable-baselines3`, whose own "
                     "resolution pulls the full CUDA/PyTorch chain - "
                     "installable, held rather than built for one row.",
        "evidence": "`BLOCKED_TRIAGE.json` names the exact missing module "
                    "for each row, found by importing the file directly in "
                    "the pinned runtime rather than trusting freqtrade's "
                    "generic \"does not exist\" message. `Dockerfile.audit-"
                    "packages` records what was checked and installed for "
                    "the four rows it resolved.",
        "watch": "Not a finding that the strategy is broken - several of "
                 "these thirteen would very likely run if their package "
                 "existed and could be isolated the same way. The row is "
                 "closed by the search having been made and having found "
                 "nothing safe, not by a standing policy against looking.",
    },
    {
        "id": "C8",
        "name": "The fix would touch every strategy's column writes",
        "test": _shared_runtime_change_declined,
        "columns": 'primary_reason == "shared_runtime_change_declined"',
        "what": "Eighteen rows, two mechanisms, not eighteen bugs. Fourteen "
                "assign a Python `bool` or `int` into a column pandas 3.0.5 "
                "no longer coerces silently - `Invalid value '1' for dtype "
                "'bool'` and its mirror images (`'True'` into `float64`, a "
                "float into `int64`, an int into `str`). Seven build a "
                "direction column with `np.where(cond, np.where(..., "
                "'down', 'up'), np.NaN)` - a Supertrend snippet credited to "
                "`freqtrade/freqtrade-strategies#30`, copied near-verbatim "
                "into five unrelated repositories - mixing a string branch "
                "with a float NaN in one array, which numpy 2.5.2 refuses "
                "to promote to a common dtype where older numpy coerced it.",
        "why_final": "Owner's call, 2026-09-04: both mechanisms are "
                     "understood and both have a fix in principle - relax "
                     "pandas' item-assignment dtype check, or numpy's "
                     "promotion rule - and both fixes would run under every "
                     "column write in the corpus, not only these eighteen "
                     "rows'. That is the large intervention a narrow shim "
                     "exists to avoid, so none was written.",
        "evidence": "`BLOCKED_TRIAGE.json` and `runtime_failure` carry the "
                    "exact pandas/numpy exception per row; the shared "
                    "`np.where(...,'down','up'), np.NaN` line was confirmed "
                    "byte-identical across five of the seven repositories "
                    "before this criterion was written.",
        "watch": "A row here is not judged unfixable in principle, only "
                 "not worth fixing at the cost this fix would impose on "
                 "the other roughly 880 strategies that never trip it. A "
                 "future decision to relax the pandas or numpy rule "
                 "corpus-wide would reopen every row this criterion "
                 "closed, together.",
    },
]


# What has at some point moved a row into `excluded` and must not again. Each
# entry says what it is, why it was withdrawn, and what happens instead.
NOT_CRITERIA = [
    {
        "name": "A trap found by reading the source",
        "what": "`traps.py` scans the source for the patterns the freqtrade "
                "community's Backtesting Traps article names: a trailing stop "
                "tighter than a realistic spread, a minimal ROI too tight for "
                "the timeframe, a declared stop of -0.99.",
        "why_not": "It is a heuristic over source text, not a measurement. "
                   "And what it describes is a fill-realism problem - the "
                   "backtest assumes an order of events inside a candle that "
                   "would not fill that way in the market - which inflates "
                   "how much a strategy appears to earn. It says nothing "
                   "about whether the strategy read the future.",
        "cost": "40 strategies that run and trade were excluded on it, 35 of "
                "them without a look-ahead run of ours ever having happened.",
        "instead": "The flag stays visible in `traps_n`, the strategy goes "
                   "through both bias checks like everything else, and the "
                   "realism problem is met where it lives - in the run, with "
                   "`--timeframe-detail 1m`, which resolves the order of "
                   "events inside a candle from real one-minute data instead "
                   "of assuming it.",
    },
    {
        "name": "A finding inherited from the original sweep",
        "what": "The frozen baseline carries look-ahead and recursion "
                "verdicts from a sweep that ran in an environment whose "
                "preconditions this audit never established.",
        "why_not": "It is somebody else's measurement of a different setup. "
                   "This audit does not issue a verdict on one.",
        "cost": "15 rows sat under `own_measurement` on an inherited "
                "recursion FOUND, and not one of them had a ladder run of "
                "ours.",
        "instead": "`exclusion_basis` reads `inherited`, the cohort reads "
                   "`exclusion unconfirmed`, and the row carries the work "
                   "that would settle it.",
    },
    {
        "name": "A check that returned no verdict (NA)",
        "what": "The check ran and produced nothing to judge - too few "
                "trades, a crash, an output the reader could not parse.",
        "why_not": "The absence of a result is not a result. Reading NA as a "
                   "failure convicts a strategy of what was never measured.",
        "cost": "",
        "instead": "`no_verdict_on_...` as the reason, and the check is "
                   "queued again.",
    },
    {
        "name": "The analyzer refusing for want of a declared warm-up",
        "what": "`recursive-analysis` will not start on a strategy whose "
                "`startup_candle_count` is zero, and says so.",
        "why_not": "Nothing was compared. The refusal is about the "
                   "invocation, not about the strategy.",
        "cost": "76 records read as FOUND until this was separated out.",
        "instead": "`WARMUP_NEEDED`, and the ladder supplies a warm-up and "
                   "runs it.",
    },
    {
        "name": "A failed trial run",
        "what": "The strategy will not start, or crashes before it trades.",
        "why_not": "No check has seen it, so nothing about it has been "
                   "judged. Whether the obstacle can be removed is a "
                   "different question from whether the strategy is out.",
        "cost": "99 rows sat in `excluded` on this.",
        "instead": "Status `open`, labelled `to be fixed`, with the obstacle "
                   "named in `repair_family` and `runtime_failure`. The "
                   "repair list records what has been recovered this way and "
                   "what has not.",
    },
]


# Before any criterion is read, one question is asked that no measurement can
# answer: is this a strategy at all. Fourteen files in the corpus are not.
PREFILTER = {
    "cohort": "not_a_strategy",
    "test": 'artifact_role != "strategy"',
    "what": "Eleven fixtures that freqtrade and NostalgiaForInfinity ship to "
            "test their own code, under `tests/strategy/strats/`, and three "
            "templates with no strategy filled in.",
    "why_first": "No measurement can change what a file is. `StrategyTestV2` "
                 "clears look-ahead and recursion cleanly, with coverage "
                 "`PASS`, no trap and 26,070 trades behind it, and is still a "
                 "fixture from freqtrade's own test suite. Deciding this "
                 "after the measurements is how it sat for a day as a "
                 "`convergence candidate` - a label that means on its way to "
                 "admission, which for a fixture is untrue and always will "
                 "be.",
    "not_excluded": "These files are not excluded, and saying so would be "
                    "wrong: `excluded` is a verdict about a strategy, and no "
                    "verdict about a strategy was reached. They carry their "
                    "own cohort, and they ask for no work, because no work "
                    "would change the answer. What happened when each ran is "
                    "kept in its reason - a fixture that also would not start "
                    "says both things.",
}


# Decided by measurement, unlike the prefilter, but it is not an exclusion
# either: nothing was found against these strategies. Owner's decision,
# 2026-09-03.
TOO_FEW = {
    "cohort": "too_few_trades",
    "test": 'lookahead NA reporting "too few trades" over the widest window',
    "floor": 10,
    "what": "The strategy trades fewer than ten times over "
            "`20200301-20260820` across all eight pairs. "
            "`lookahead-analysis` needs ten trades before it will judge "
            "anything, so it turned the row away rather than ruling on too "
            "little.",
    "why_not_excluded": "Nothing was found against these strategies. Calling "
                        "them excluded would claim a verdict nobody reached, "
                        "which is the same error the trap heuristic made.",
    "why_not_usable": "And they cannot be ranked either. Market-phase "
                      "efficiency is a statement about how a strategy behaves "
                      "in each phase, and three trades in six and a half "
                      "years distribute across nothing.",
    "threshold": "Ten is not our number. It is what freqtrade itself "
                 "requires before `lookahead-analysis` reaches a verdict, "
                 "which makes it the one threshold here that is not a choice "
                 "of ours. Whether a market-phase ranking needs more than "
                 "ten - per phase rather than in total - belongs to the "
                 "benchmark's preregistration and is still open.",
    "excluded_from_it": "A row that trades rarely because OUR setup stopped "
                        "it does not belong here. `BasketStrategy` reports "
                        "zero because a portfolio basket was measured one "
                        "pair at a time; it is `open`, and "
                        "`ZERO_TRADE_TRIAGE.json` says why.",
}


def too_few(row):
    """True when the row is in the too-few-trades cohort."""
    return row.get("cohort") == TOO_FEW["cohort"]


def prefiltered(row):
    """True when the row is not a strategy, whatever its measurements say."""
    return bool(row.get("artifact_role")) and row["artifact_role"] != "strategy"


def classify(row):
    """Which criteria a row satisfies. Empty means it is not excluded."""
    return [c["id"] for c in CRITERIA if c["test"](row)]


# ----------------------------------------------------------------- criteria

def criteria_report(rows, path):
    excluded = [r for r in rows if r["cohort"] == "excluded"]
    matched = collections.Counter()
    for row in excluded:
        for cid in classify(row):
            matched[cid] += 1
    open_rows = [r for r in rows
                 if r["cohort"] in ("pending", "exclusion_unconfirmed")]
    would = [r for r in open_rows if classify(r)]

    lines = []
    add = lines.append
    add("# Exclusion criteria")
    add("")
    add("Generated by `exclusion_criteria.py`. Do not edit by hand.")
    add("")
    add("A strategy is **excluded** when one of the criteria below holds on "
        "evidence this audit produced itself. Nothing else excludes a "
        "strategy. One that satisfies none of them is not excluded - it is "
        "unfinished, and `open_work` says what is missing.")
    add("")
    add("Currently %d of %d strategies are excluded. The criteria are not "
        "exclusive - %d strategies satisfy more than one, and the counts "
        "below therefore add up to more than the total."
        % (len(excluded), len(rows),
           sum(1 for r in excluded if len(classify(r)) > 1)))
    add("")
    add("| | Criterion | Strategies |")
    add("|---|---|---:|")
    for c in CRITERIA:
        add("| %s | %s | %d |" % (c["id"], c["name"], matched[c["id"]]))
    add("")

    add("## The criteria in full")
    add("")
    for c in CRITERIA:
        add("### %s &middot; %s" % (c["id"], c["name"]))
        add("")
        add("**Machine test.** `%s`, together with `exclusion_basis == "
            '"own_measurement"`.' % c["columns"])
        add("")
        add("**What it means.** %s" % c["what"])
        add("")
        add("**Why it is final.** %s" % c["why_final"])
        add("")
        add("**What stands behind it.** %s" % c["evidence"])
        add("")
        add("**What this is not.** %s" % c["watch"])
        add("")
        sample = sorted(r["strategy_id"] for r in excluded
                        if c["id"] in classify(r))
        add("%d strategies, among them %s."
            % (len(sample), ", ".join("`%s`" % s for s in sample[:6])))
        add("")

    fixtures = [r for r in rows if prefiltered(r)]
    add("## Before the criteria: is it a strategy at all")
    add("")
    add("**Machine test.** `%s`. Cohort `%s`, decided before any measurement "
        "is consulted." % (PREFILTER["test"], PREFILTER["cohort"]))
    add("")
    add("**What these are.** %s Currently %d of them."
        % (PREFILTER["what"], len(fixtures)))
    add("")
    add("**Why it is asked first.** %s" % PREFILTER["why_first"])
    add("")
    add("**They are not excluded.** %s" % PREFILTER["not_excluded"])
    add("")
    if fixtures:
        add("| Strategy | What it is |")
        add("|---|---|")
        for row in sorted(fixtures, key=lambda r: r["strategy_id"]):
            add("| `%s` | %s |" % (row["strategy_id"],
                                   row["primary_reason"] or "-"))
        add("")

    rare = [r for r in rows if too_few(r)]
    add("## Neither excluded nor usable: too few trades to measure")
    add("")
    add("**Machine test.** %s. Cohort `%s`, floor %d trades."
        % (TOO_FEW["test"], TOO_FEW["cohort"], TOO_FEW["floor"]))
    add("")
    add("**What it means.** %s Currently %d strategies."
        % (TOO_FEW["what"], len(rare)))
    add("")
    add("**Why they are not excluded.** %s" % TOO_FEW["why_not_excluded"])
    add("")
    add("**Why they are not usable.** %s" % TOO_FEW["why_not_usable"])
    add("")
    add("**Where the number comes from.** %s" % TOO_FEW["threshold"])
    add("")
    add("**What does not belong here.** %s" % TOO_FEW["excluded_from_it"])
    add("")
    if rare:
        add("| Strategy | Trades | Measured over |")
        add("|---|---:|---|")
        for row in sorted(rare, key=lambda r: r["strategy_id"]):
            add("| `%s` | %s | %s |" % (row["strategy_id"],
                                        row["observed_trades"] or "0",
                                        row["trade_evidence"] or "-"))
        add("")

    add("## What does not exclude a strategy")
    add("")
    add("Each of these has at some point moved strategies into `excluded` and "
        "has been withdrawn. They are listed so the mistake is not repeated.")
    add("")
    for n in NOT_CRITERIA:
        add("### %s" % n["name"])
        add("")
        add("**What it is.** %s" % n["what"])
        add("")
        add("**Why it does not exclude.** %s" % n["why_not"])
        add("")
        if n["cost"]:
            add("**What it cost.** %s" % n["cost"])
            add("")
        add("**What happens instead.** %s" % n["instead"])
        add("")

    add("## Using this list on an unfinished strategy")
    add("")
    add("For a strategy under `open` or `exclusion unconfirmed`, read the "
        "three criteria in order and stop at the first that holds.")
    add("")
    add("0. Is `artifact_role` anything but `strategy`? Then it is a fixture "
        "or a template, it belongs in `not a strategy`, and none of the rest "
        "applies. It is not excluded either.")
    add("1. Does `lookahead` read `FOUND` **and** `lookahead_evidence` read "
        "`native`? Then C1, and it is excluded.")
    add("2. Does `recursive_evidence` read `convergence:not_settled`? Then "
        "C2, and it is excluded.")
    add("3. Did the full window run and produce no trades, with "
        "`trade_evidence` reading `full_window`? Then C3, and it is "
        "excluded.")
    add("4. Did the look-ahead check turn it away for want of ten trades "
        "over the widest window? Then it is `too few trades` - not excluded, "
        "and not usable either.")
    add("5. Otherwise it is not excluded. `open_work` names what is missing, "
        "and the checks run in the order the status page sets out: trial "
        "run, recursion, look-ahead, backtest.")
    add("")
    add("Of the %d unfinished strategies, %d currently satisfy a criterion."
        % (len(open_rows), len(would)))
    if would:
        add("")
        for row in sorted(would, key=lambda r: r["strategy_id"])[:25]:
            add("- `%s` &mdash; %s" % (row["strategy_id"],
                                       ", ".join(classify(row))))
    add("")

    text = "\n".join(lines) + "\n"
    tmp = path + ".tmp"
    io.open(tmp, "w", encoding="utf-8", newline="\n").write(text)
    os.replace(tmp, path)
    return len(excluded), matched


# ------------------------------------------------------------------ repairs

# One entry per repair route actually taken. `error` is the message freqtrade
# produced before the repair, verbatim from BLOCKED_TRIAGE.json where one was
# recorded. `family` ties the entry to the rows in the status table, so the
# counts below are read from the table rather than typed in.
REPAIRS = [
    {
        "family": "timeframe_missing",
        "name": "Timeframe recovered from the author's own field",
        "error": "Timeframe needs to be set in either configuration or as "
                 "cli argument `--timeframe 5m`",
        "cause": "Freqtrade renamed `ticker_interval` to `timeframe` in "
                 "2021.4 and stopped reading the old name. A strategy written "
                 "before that declares its timeframe in a field current "
                 "freqtrade ignores, so it refuses to start - even though the "
                 "author did state it.",
        "fix": "`eligibility_timeframe_repair.py` reads `ticker_interval` "
               "from the source and passes the value as `--timeframe`. The "
               "source is not touched, and `repair_settings` records the "
               "recovered value and where it came from "
               "(`author_ticker_interval`).",
        "limit": "Only where the author wrote the value down. Where no field "
                 "exists, choosing a timeframe would be inventing the "
                 "strategy rather than restoring it, and those rows are "
                 "refused as `timeframe_not_recoverable`.",
        "tool": "eligibility_timeframe_repair.py",
    },
    {
        "family": "framework_compat_shim",
        "name": "Seven compatibility shims for freqtrade's own behaviour",
        "error": "IStrategy.min_roi_reached_entry() missing 2 required "
                 "positional arguments: 'trade_dur' and 'current_time'  /  "
                 "<Name>.min_roi_reached_entry() takes 2 positional arguments "
                 "but 4 were given  /  Impossible to load Strategy '<Name>'. "
                 "This class does not exist or contains Python code errors.  "
                 "/  ValueError: cannot reindex on an axis with duplicate "
                 "labels  /  KeyError: 'rmi-up-trend'  /  This strategy "
                 "requires <N> candles to start, which is more than 5x the "
                 "amount of candles Binance provides  /  ImportError: cannot "
                 "import name 'accumulation_distribution' from "
                 "'technical.indicators'",
        "cause": "Seven unrelated things inside freqtrade or a package it "
                 "depends on, none of them a defect in a strategy.\n\n"
                 "1. The ROI hook gained two parameters, so a strategy "
                 "calling the old one-argument form crashes.\n\n"
                 "2. `IResolver._search_object` decides whether to import a "
                 "file by scanning its text for the literal `class <Name>(`. "
                 "A single space before the bracket makes freqtrade skip the "
                 "file entirely and report it as though the class were "
                 "absent.\n\n"
                 "3. `advise_entry` initialises `enter_tag` to \"\" - its own "
                 "workaround for a pandas bug - and then renames a legacy "
                 "`buy_tag` onto that same name. Renaming relabels rather "
                 "than merges, so the frame comes back with TWO `enter_tag` "
                 "columns. An ordinary backtest calls the hook once and never "
                 "notices; `lookahead-analysis` calls it twice on the same "
                 "frame, and the second pass cannot align against a duplicate "
                 "label.\n\n"
                 "4. `start_lookahead_analysis` builds its config with "
                 "`RunMode.UTIL_NO_EXCHANGE`, so a strategy that caches "
                 "per-candle series under `if self.dp.runmode.value in "
                 "('backtest', 'hyperopt')` caches nothing and raises when it "
                 "reads them back - even though the analyzer does build a "
                 "Backtesting object and run `backtest()` over real candles."
                 "\n\n"
                 "5. `Exchange.validate_required_startup_candles` refuses a "
                 "warm-up needing more than five OHLCV calls per pair - a "
                 "live-bot API courtesy that a backtest reading local feather "
                 "files never spends.\n\n"
                 "6. The reverse of 1: four strategies DEFINE their own "
                 "`min_roi_reached_entry(self, trade_dur)` in the pre-2022 "
                 "shape, and freqtrade calls it with three arguments. "
                 "Patching the base class does nothing here - the subclass's "
                 "own method is what Python resolves.\n\n"
                 "7. `IchimokuStrategy` and `Ichimoku_SenkouSpanCross` import "
                 "`technical.indicators.accumulation_distribution`, which "
                 "the installed `technical` 1.6.0 no longer ships, and never "
                 "call it - dead code from an earlier revision of the file.",
        "fix": "`repair/compat_signature.py` installs the shims into "
               "freqtrade inside the runner process, named per strategy by "
               "`PROFILE_COMPAT_SIGNATURES`.\n\n"
               "`legacy_min_roi_reached_entry_signature` accepts the "
               "one-argument call, and raises if the strategy sets "
               "`use_custom_roi` - the only case where the extra arguments "
               "change the answer.\n\n"
               "`whitespace_tolerant_class_scan` replaces the literal text "
               "scan with a regular expression that tolerates the space.\n\n"
               "`idempotent_entry_tag_initialisation` collapses the duplicate "
               "onto the last occurrence, which is the strategy's own tags "
               "rather than the empty placeholder, and returns a frame with "
               "one `enter_tag` untouched.\n\n"
               "`lookahead_runmode_reports_backtest` rewrites "
               "`UTIL_NO_EXCHANGE` to `BACKTEST` on `DataProvider.runmode` "
               "alone, leaving `self.config['runmode']` and every other "
               "runmode as they are.\n\n"
               "`startup_candles_not_limited_by_call_budget` catches only the "
               "\"more than 5x\" refusal and recomputes the same call count "
               "the original function would have returned; any other "
               "refusal - in particular an exchange with no history at all - "
               "still stands.\n\n"
               "`legacy_min_roi_reached_entry_override` wraps "
               "`StrategyResolver.load_strategy`: once the real loader "
               "returns, if the resolved class's own `min_roi_reached_entry` "
               "binds a one-argument call and rejects the three-argument "
               "one, the INSTANCE gets its own attribute that translates a "
               "three-argument call down to the author's form and passes "
               "any other call through unchanged - which matters for "
               "`Schism-v2`, whose own `min_roi_reached` calls its "
               "`min_roi_reached_entry` internally with two arguments in its "
               "own convention, not freqtrade's three.\n\n"
               "`restore_accumulation_distribution` puts the function back "
               "on `technical.indicators` before the strategy's import runs, "
               "computed as the standard Money-Flow-Volume running total - "
               "the same Money Flow Multiplier `technical`'s own "
               "`chaikin_money_flow` still computes, summed rather than "
               "averaged over a window.",
        "limit": "Each is scoped as narrowly as the defect it answers. The "
                 "scan shim only widens which files freqtrade agrees to look "
                 "at - a class that then fails to import for a real reason "
                 "still fails. The runmode shim touches one property and "
                 "cannot tell a live or dry run it is a backtest; the "
                 "selftest checks every other runmode passes through. The "
                 "startup-budget shim leaves the ceiling `available_prefix_"
                 "candles` computes untouched - it removes a courtesy limit, "
                 "not the limit of what history exists.\n\n"
                 "Neutrality of the `enter_tag` shim was measured rather than "
                 "assumed. On `NotAnotherSMAOffsetStrategy`, `Apollo11`, "
                 "`Saturn5`, `INSIDEUP`, `Dracula` and `tbtest` the entry "
                 "signals and their tags are identical with and without it, "
                 "on runs carrying 138, 147 and 1956 entries. "
                 "`BinHV27_werkkrew`, which writes `buy` but no `buy_tag`, "
                 "holds one `enter_tag` column and passes twice unshimmed - "
                 "the control that identifies the rename as the cause.\n\n"
                 "The accumulation/distribution shim restores a genuinely "
                 "standard, unambiguous formula rather than inventing one - "
                 "and both strategies it applies to never call the function "
                 "at all, so its exact values are untested by either.",
        "tool": "repair/compat_signature.py",
    },
    {
        "family": "local_module_off_path",
        "name": "The author's own module put back on the path",
        "error": "Impossible to load Strategy '<Name>'. This class does not "
                 "exist or contains Python code errors.",
        "cause": "The strategy imports a helper the author shipped beside it "
                 "in their repository. Collected on its own, the import has "
                 "nowhere to resolve from.",
        "fix": "`repair_local_modules.py` finds copies of the missing module "
               "in the corpus and decides between them by testing the import, "
               "not by name. `shadows_a_package()` rejects any directory "
               "containing `freqtrade/`, `numpy/` and the like.",
        "limit": "That guard exists because four repairs made things worse: "
                 "adding `repos/mlsys-io_PortfolioBench` to the path shadowed "
                 "freqtrade itself. They are recorded as `repair_withdrawn`, "
                 "and the withdrawn entries stay in `PROFILE_CLASS1.json` "
                 "with `status: withdrawn` - deleting them had deleted the "
                 "finding.",
        "tool": "repair_local_modules.py",
    },
    {
        "family": "freqai_arm",
        "name": "FreqAI strategies given the author's own configuration",
        "error": "freqAI is not enabled. Please enable it in your config to "
                 "use this strategy.  /  Impossible to load FreqaiModel "
                 "'<Name>'.",
        "cause": "A FreqAI strategy is only half a strategy: the feature set, "
                 "the model and the training window live in the config, not "
                 "the source. Without the author's config there is nothing to "
                 "run.",
        "fix": "Where the author shipped a config it is restored "
               "(`restore_author_config`), with their model path. For WTAI "
               "and WTRSIAI, whose author left the freqai block commented out "
               "in `config_blank.json`, `repair/freqai_config_wtai.py` builds "
               "the config from that block.",
        "limit": "These runs use a different runtime, the authors' own "
                 "configs and a different question, so they are kept as a "
                 "separate arm and never merged into a cohort. Freqtrade "
                 "2026.7 no longer ships `CatboostClassifier` at all, so "
                 "strategies naming it cannot be run as written.",
        "tool": "repair/freqai_config_wtai.py, eligibility_freqai_repair.py",
    },
    {
        "family": "freqai_model",
        "name": "FreqAI: the author's model class is gone",
        "error": "Impossible to load FreqaiModel 'CatboostClassifier'  /  "
                 "'LitmusMultiTargetClassifier'  /  'ReforceXY'.",
        "cause": "The strategy names a prediction model that this freqtrade "
                 "no longer ships, or that the author kept in their own "
                 "repository.",
        "fix": "Where the author's model directory is in the corpus it is "
               "restored with `--freqaimodel-path` "
               "(`restore_author_package_extension`). Where the class was "
               "removed from freqtrade itself - `CatboostClassifier` in "
               "2026.7 - there is nothing to restore.",
        "limit": "Substituting a different model would measure a different "
                 "strategy, so those are `refuse_repair`.",
        "tool": "eligibility_freqai_repair.py",
    },
    {
        "family": "freqai_config_built",
        "name": "FreqAI: the config rebuilt from the author's own block",
        "error": "freqAI is not enabled. Please enable it in your config to "
                 "use this strategy.",
        "cause": "`WTAI` and `WTRSIAI` ship no freqai config. Their author "
                 "left the whole block commented out in `config_blank.json`, "
                 "which is a statement of intent but not a file freqtrade "
                 "will read.",
        "fix": "`repair/freqai_config_wtai.py` builds the config from that "
               "commented block, starting `include_timeframes` at the "
               "strategy's own timeframe and setting `test_size` to 0.33.",
        "limit": "Uncommenting is still a reconstruction: the author never "
                 "ran this exact file. Both rows are recorded as "
                 "`refuse_repair` for the audit proper and kept in the FreqAI "
                 "arm, which is reported separately and never merged into a "
                 "cohort.",
        "tool": "repair/freqai_config_wtai.py",
    },
    {
        "family": "wrong_profile",
        "name": "Run under a profile its entry logic cannot satisfy",
        "error": "(no error - the run succeeds and opens nothing)",
        "cause": "The strategy starts, runs the full window and never enters, "
                 "because the profile withholds something its entry needs. "
                 "`FundingCarry` builds `funding_z` from funding rates, which "
                 "exist only in futures mode, and was run under `spot_long`. "
                 "`Insomnia_short` sets `enter_long = 0` and raises only "
                 "`enter_short`, with `can_short` unset, so freqtrade "
                 "discards every signal it produces.",
        "fix": "Re-run under the profile the strategy was written for. "
               "Nothing about the strategy is changed; what changes is what "
               "we asked it to run in.",
        "limit": "This is the one shape of zero trades that is our fault "
                 "rather than the strategy's, which is why criterion C3 "
                 "requires it to be ruled out first. Recorded in "
                 "`ZERO_TRADE_TRIAGE.json` with the reason, so the row reads "
                 "`open` and `to be fixed` rather than `excluded`.",
        "tool": "probe_zero.py, ZERO_TRADE_TRIAGE.json",
    },
    {
        "family": "measured_outside_its_design",
        "name": "Measured one pair at a time when it needs the whole basket",
        "error": "(no error - the run succeeds and opens nothing)",
        "cause": "`BasketStrategy` marks an entry on 8831 of 18570 candles, "
                 "so it is not idle. It is a portfolio basket: "
                 "`custom_stake_amount` sizes each entry as a target weight "
                 "of the whole portfolio and returns 0.0 when that falls "
                 "below the exchange minimum. The full-window measurement "
                 "runs one pair at a time, so there is no portfolio to take "
                 "a weight of and every entry is sized to nothing.",
        "fix": "Measure it across all eight pairs in a single run, the way "
               "its author intended.",
        "limit": "Worth watching for beyond this one row: any strategy whose "
                 "position sizing reads the portfolio rather than the pair "
                 "will do the same thing, and it looks exactly like a "
                 "strategy that never trades.",
        "tool": "probe_zero.py, ZERO_TRADE_TRIAGE.json",
    },
    {
        "family": "no_stoploss",
        "name": "Refused: no stoploss declared",
        "error": "Configuration error: 'stoploss' is a required property",
        "cause": "The author declared no stoploss. Freqtrade requires one.",
        "fix": "None. Supplying a stoploss does not restore anything the "
               "author wrote - it invents the risk management and then "
               "measures the invention.",
        "limit": "Recorded as `refuse_repair`, which is a decision rather "
                 "than a failure to try.",
        "tool": "blocked_triage.py",
    },
    {
        "family": "no_exit_logic",
        "name": "Refused: no exit logic",
        "error": "`populate_exit_trend` or `populate_sell_trend` must be "
                 "implemented.",
        "cause": "The file has no exit hook at all.",
        "fix": "None, for the same reason: writing the exit would be writing "
               "the strategy.",
        "limit": "`refuse_repair`.",
        "tool": "blocked_triage.py",
    },
    {
        "family": "no_populate_indicators",
        "name": "Refused: no populate_indicators at all",
        "error": "Can't instantiate abstract class <Name> without an "
                 "implementation for abstract method 'populate_indicators'.",
        "cause": "Not a missing helper - the one method every strategy is "
                 "built around was never written.",
        "fix": "None. Writing it would be writing the strategy from "
               "nothing, not restoring anything the author left out by "
               "accident.",
        "limit": "`refuse_repair`.",
        "tool": "blocked_triage.py",
    },
    {
        "family": "missing_author_data_file",
        "name": "Refused: a file the author never shipped",
        "error": "[Errno 2] No such file or directory: '<path>' / Could not "
                 "find pair source at '<path>'.",
        "cause": "The strategy opens a specific file at runtime - a "
                 "pre-trained model, a lookup table - that never existed in "
                 "the author's own repository.",
        "fix": "None; no corpus copy exists to restore. Distinct from "
               "`AutoArimaTripleV1`'s unrelated missing LOG directory, "
               "which this audit's own environment supplies as a write "
               "target rather than something the author would have shipped "
               "- see repair/compat_signature.py's `install_dataframe_"
               "append` docstring for that row.",
        "limit": "`refuse_repair`.",
        "tool": "blocked_triage.py",
    },
    {
        "family": "invalid_declared_config",
        "name": "Refused: two declared values that cannot both be honoured",
        "error": "Configuration error: The config trailing_stop_positive_"
                 "offset needs to be greater than trailing_stop_positive.",
        "cause": "The author's own `trailing_stop_positive_offset` is "
                 "smaller than their own `trailing_stop_positive`, a "
                 "combination freqtrade's lookahead-analysis refuses to "
                 "start on even though the strategy backtests and trades "
                 "normally otherwise.",
        "fix": "None. Both values are the author's; adjusting either one "
               "would be guessing which of the two they actually meant.",
        "limit": "`refuse_repair`. Found by the lookahead gate rather than "
                 "a trial-run failure - `TGMA` measures and trades "
                 "normally - so the family is set directly in strategy_"
                 "status.py's own cohort logic rather than read out of "
                 "`BLOCKED_TRIAGE.json` the way the others here are.",
        "tool": "strategy_status.py (invalid_gate_config)",
    },
    {
        "family": "timeframe_not_recoverable",
        "name": "Refused: timeframe nowhere stated",
        "error": "Timeframe needs to be set in either configuration or as "
                 "cli argument `--timeframe 5m`",
        "cause": "The same message as the recovered ones, a different "
                 "situation: the author names no timeframe anywhere.",
        "fix": "None. Every timeframe would produce a different strategy.",
        "limit": "`refuse_repair`.",
        "tool": "eligibility_timeframe_repair.py",
    },
    {
        "family": "dtype_drift",
        "name": "Open: pandas and numpy have moved under the strategy",
        "error": "The DType <class 'numpy.dtypes.StrDType'> could not be "
                 "promoted by <class 'numpy.dtypes._PyFloatDType'>  /  "
                 "Invalid value 'False' for dtype 'float64'",
        "cause": "Assignments pandas used to coerce silently now raise: a "
                 "string written into a float column, a bool into a float, "
                 "`fillna(method=...)` removed.",
        "fix": "Not yet attempted beyond three cases "
               "(`datetime_safe_rmi_fillna`). Each needs reading before it "
               "can be judged, because the repair touches the strategy's own "
               "dataframe rather than its environment.",
        "limit": "`needs_a_look`.",
        "tool": "blocked_triage.py",
    },
    {
        "family": "third_party_package",
        "name": "Open: a package the author depended on",
        "error": "Impossible to load Strategy '<Name>'. This class does not "
                 "exist or contains Python code errors.",
        "cause": "An import of a package that is not installed - sometimes "
                 "declared by the author, sometimes not, sometimes no longer "
                 "installable at all.",
        "fix": "One case done (`restore_declared_pypi_dependency`: pyrenko "
               "installed with `--no-deps`, because its numpy 1.18.5 pin is "
               "obsolete). The rest are unexamined.",
        "limit": "`needs_a_look`. Installing an arbitrary package into the "
                 "runtime changes the runtime for every other strategy, so "
                 "each one needs a decision rather than a reflex.",
        "tool": "blocked_triage.py",
    },
    {
        "family": "class_not_loaded",
        "name": "Open: the class will not import",
        "error": "Impossible to load Strategy '<Name>'. This class does not "
                 "exist or contains Python code errors.",
        "cause": "Whatever is left once the whitespace scan and the missing "
                 "module have been ruled out.",
        "fix": "`blocked_triage.py` imports the file in the pinned runtime to "
               "get the real exception rather than freqtrade's summary. Seven "
               "rows still need reading.",
        "limit": "`needs_a_look`, two `to_be_fixed`.",
        "tool": "blocked_triage.py",
    },
    {
        "family": "individual",
        "name": "Open: one of a kind",
        "error": "cannot import name '__version__' from 'freqtrade'  /  You "
                 "are using the `populate_any_indicators()` function which "
                 "was deprecated  /  Remora API key missing. Set "
                 "REMORA_API_KEY env var.",
        "cause": "No shared shape. Some read a freqtrade attribute that no "
                 "longer exists, some use a hook removed years ago, one wants "
                 "a paid API key.",
        "fix": "Nothing general. Each needs its own decision.",
        "limit": "`needs_a_look`.",
        "tool": "blocked_triage.py",
    },
]


# Corrections to our own reading rather than to a strategy. Each of these had
# already put strategies in the wrong place by the time it was found, and the
# count is what it cost. They are here because the question "what did you
# repair" has two answers, and this is the one that is easy to leave out.
READER_FIXES = [
    {
        "what": "The drift table was read at a fixed column",
        "symptom": "Recursion verdicts that did not match their own logs.",
        "cause": "The parser took the drift at 199 candles instead of at the "
                 "strategy's declared warm-up. The analyzer prints one column "
                 "per startup value and labels the strategy's own; the "
                 "position moves with the value.",
        "fix": "Locate the column by its label. `warmup_reparse.py --store "
               "bias` re-reads the logs already on disk.",
        "cost": "47 of 302 logs flipped, every one from excluded to clean. "
                "55 of 124 bias records disagreed with their own logs.",
    },
    {
        "what": "No variance was read as no measurement",
        "symptom": "17 ladder runs recorded as inconclusive.",
        "cause": "`analyze_indicators` walks the rungs upward and stops at "
                 "the first that matches the full-history run exactly, "
                 "reporting no variance and printing no table. An empty table "
                 "was read as nothing having been compared.",
        "fix": "That sentence is the verdict: a pass at the smallest rung. "
               "`profile_bias._recursive` returns PASS on an empty table when "
               "the sentence is present, and the logs were re-read.",
        "cost": "17 records, three of them sitting in `excluded`.",
    },
    {
        "what": "A refusal was read as a finding",
        "symptom": "76 recursion records reading FOUND.",
        "cause": "`recursive-analysis` refuses to start on a strategy whose "
                 "`startup_candle_count` is zero. The refusal was parsed as a "
                 "verdict.",
        "fix": "`WARMUP_NEEDED`, which is not a finding, and the ladder "
               "supplies a warm-up and runs the check properly.",
        "cost": "76 records, 47 rows relabelled.",
    },
    {
        "what": "An unreadable column was read as a failure to settle",
        "symptom": "Two strategies recorded as recursion findings while every "
                   "readable indicator sat at 0.00 % from 2016 candles on.",
        "cause": "The analyzer printed `nan%` for one volume-derived column "
                 "at every rung - a percentage it cannot express, not a "
                 "shortage of history. The settling rule requires a number at "
                 "every rung, so no rung could ever qualify.",
        "fix": "A column undefined at every rung is set aside from the "
               "decision and named in `undefined_throughout`. One undefined "
               "at only some rungs keeps its old handling: that really is too "
               "little history.",
        "cost": "`MultiMA_TSL3_Mod` and `NotAnotherSMAOffSetStrategy_V2`.",
    },
    {
        "what": "A refusal killed the whole ladder run",
        "symptom": "31 ladder runs producing nothing at all.",
        "cause": "Asking for a rung above the exchange's candle limit makes "
                 "freqtrade refuse the entire invocation, not just that rung. "
                 "A bottom rung too small to compute did the same.",
        "fix": "Trim the ladder to the limit freqtrade states, drop an "
               "uncomputable bottom rung, and retry.",
        "cost": "21 plus 10 runs.",
    },
    {
        "what": "The trap heuristic decided the status",
        "symptom": "40 strategies that run and trade sitting in `excluded`.",
        "cause": "`traps.py` reads the source for the patterns the freqtrade "
                 "community's Backtesting Traps article names. Useful, but a "
                 "heuristic over text, and about fill realism rather than "
                 "bias.",
        "fix": "Withdrawn as a failure reason on 2026-09-02 by the owner's "
               "decision. The flag stays in `traps_n`; the realism problem is "
               "met in the run with `--timeframe-detail 1m`.",
        "cost": "40 strategies, 35 of them never look-ahead checked at all.",
    },
    {
        "what": "An inherited finding was labelled as ours",
        "symptom": "15 rows reading `own_measurement` with no ladder run "
                   "behind them.",
        "cause": "`technical_trap_found` forced the basis to "
                 "`own_measurement`, which then covered the inherited "
                 "recursion FOUND sitting on the same row.",
        "fix": "`recursive_bias_found` reads `own_measurement` only when "
               "`recursive_evidence` starts with `convergence:`.",
        "cost": "15 rows.",
    },
    {
        "what": "The selftest covered one row",
        "symptom": "A test reporting PASS while checking almost nothing.",
        "cause": "A bad patch split the per-row loop, so four invariants ran "
                 "against a single leftover row out of 900.",
        "fix": "One loop, with a comment saying why it must stay one.",
        "cost": "Unknown, and that is the point.",
    },
    {
        "what": "Two runners on one store",
        "symptom": "Three measurements lost.",
        "cause": "A rule of this audit is one writer per store. I broke it: "
                 "two runs shared `ELIGIBILITY_SIGNATURE_REPAIR.json`.",
        "fix": "A store claim - a `<store>.running` directory held for the "
               "life of the run, with a two-hour takeover for a claim left "
               "behind by `docker stop`. `runlog.py` builds the whole entry "
               "before writing it under a claim.",
        "cost": "Three measurements, re-run.",
    },
]


def repair_report(rows, path):
    families = collections.defaultdict(collections.Counter)
    members = collections.defaultdict(list)
    for row in rows:
        if row["repair_family"]:
            families[row["repair_family"]][row["repair_verdict"] or "-"] += 1
            members[row["repair_family"]].append(row["strategy_id"])
    class1 = (_json(CLASS1) or {}).get("strategies", {})
    rules = collections.Counter(rule for entry in class1.values()
                                for rule in (entry.get("rules") or []))

    order = {"repaired": 0, "repair_attempted": 1, "to_be_fixed": 2,
             "needs_a_look": 3, "repair_withdrawn": 4, "refuse_repair": 5}
    meaning = {
        "repaired": "runs now, and the run is recorded",
        "repair_attempted": "a route was applied and did not finish the job",
        "to_be_fixed": "the route is known, the run has not happened yet",
        "needs_a_look": "no route yet; the obstacle has been identified",
        "repair_withdrawn": "the repair made things worse and was undone",
        "refuse_repair": "repairing it would mean inventing the strategy",
    }

    lines = []
    add = lines.append
    add("# Repair measures")
    add("")
    add("Generated by `exclusion_criteria.py`. Do not edit by hand.")
    add("")
    add("Every route taken to get a strategy running again, with the message "
        "freqtrade gave before it. Two rules hold throughout: no strategy "
        "source is edited, and a repair that would require deciding something "
        "the author did not decide is refused rather than guessed.")
    add("")
    add("Each repaired strategy carries its route in the status table, in "
        "`repair_family`, `repair_verdict` and `repair_settings`, so a row "
        "always says what it was run with.")
    add("")

    total = collections.Counter()
    for counts in families.values():
        total.update(counts)
    add("| Verdict | Strategies | Meaning |")
    add("|---|---:|---|")
    for verdict in sorted(total, key=lambda v: order.get(v, 9)):
        add("| `%s` | %d | %s |"
            % (verdict, total[verdict], meaning.get(verdict, "")))
    add("")

    add("## Routes taken")
    add("")
    for entry in REPAIRS:
        counts = families.get(entry["family"], collections.Counter())
        add("### %s" % entry["name"])
        add("")
        add("`repair_family: %s` &mdash; %d strategies (%s)"
            % (entry["family"], sum(counts.values()),
               ", ".join("%s %d" % (v, n) for v, n
                         in sorted(counts.items(),
                                   key=lambda kv: order.get(kv[0], 9)))
               or "none"))
        add("")
        add("**The message.**")
        add("")
        add("```")
        for part in entry["error"].split("  /  "):
            add(part)
        add("```")
        add("")
        add("**What it actually was.** %s" % entry["cause"])
        add("")
        add("**The repair.** %s" % entry["fix"])
        add("")
        add("**Where it stops.** %s" % entry["limit"])
        add("")
        add("Tool: `%s`." % entry["tool"])
        add("")
        sample = sorted(members.get(entry["family"], []))[:6]
        if sample:
            add("For example: %s." % ", ".join("`%s`" % s for s in sample))
            add("")

    add("## Rules recorded per strategy")
    add("")
    add("`PROFILE_CLASS1.json` is the registry of environment and "
        "configuration restorations. No strategy source is modified by any "
        "of them.")
    add("")
    add("| Rule | Strategies |")
    add("|---|---:|")
    for rule, count in rules.most_common():
        add("| `%s` | %d |" % (rule, count))
    add("")

    add("## Corrections to our own reading")
    add("")
    add("The other half of the answer. Each of these had already put "
        "strategies in the wrong place by the time it was found, and none of "
        "them was a fault of the strategies.")
    add("")
    for fix in READER_FIXES:
        add("### %s" % fix["what"])
        add("")
        add("**How it showed.** %s" % fix["symptom"])
        add("")
        add("**What it was.** %s" % fix["cause"])
        add("")
        add("**The correction.** %s" % fix["fix"])
        add("")
        add("**What it had cost.** %s" % fix["cost"])
        add("")

    text = "\n".join(lines) + "\n"
    tmp = path + ".tmp"
    io.open(tmp, "w", encoding="utf-8", newline="\n").write(text)
    os.replace(tmp, path)
    return total


def selftest():
    rows = _csv(STATUS)
    excluded = [r for r in rows if r["cohort"] == "excluded"]
    # The whole point of the list: nothing is excluded for a reason that is
    # not on it, and every criterion still describes real rows.
    for row in excluded:
        assert classify(row), (
            "%s is excluded for `%s`, which is not one of the criteria in "
            "this file. Either it belongs under an existing criterion and the "
            "table is wrong, or a new ground has been established and belongs "
            "in CRITERIA - with its machine test, what stands behind it, and "
            "what it is not. Nothing is excluded for a reason that is not "
            "written down here."
            % (row["strategy_id"], row["primary_reason"]))
        assert row["exclusion_basis"] == "own_measurement", row["strategy_id"]
    # The prefilter and the criteria may never disagree, in either
    # direction: a file that is not a strategy is never excluded, and a row
    # in the not_a_strategy cohort is never a strategy.
    for row in rows:
        if prefiltered(row):
            assert row["cohort"] == "not_a_strategy", (
                "%s is not a strategy (artifact_role %s) but sits in %s. "
                "The prefilter runs before the criteria and no measurement "
                "overrides it."
                % (row["strategy_id"], row["artifact_role"], row["cohort"]))
            assert not row["open_work"], (
                "%s is not a strategy and is asking for work no measurement "
                "could use." % row["strategy_id"])
        if row["cohort"] == "not_a_strategy":
            assert prefiltered(row), row["strategy_id"]
    # Too rare to measure is never a verdict against a strategy, so no such
    # row may be excluded, and none may be admitted either.
    for row in rows:
        if too_few(row):
            assert row["lookahead"] == "NA", row["strategy_id"]
            assert not classify(row), (
                "%s is in the too-few-trades cohort and also satisfies %s"
                % (row["strategy_id"], ", ".join(classify(row))))
        if row["cohort"] in ("E0_strict67", "E1_expanded"):
            assert not too_few(row), row["strategy_id"]
    for criterion in CRITERIA:
        matched = [r for r in excluded if criterion["test"](r)]
        assert matched, "criterion %s matches nothing" % criterion["id"]
    # And the withdrawn ones stay withdrawn. A trap may sit on any row and
    # decide none of them.
    for row in rows:
        if row["traps_n"] not in ("", "0"):
            assert "trap" not in row["primary_reason"], row["strategy_id"]
        if row["cohort"] == "excluded":
            assert row["lookahead_evidence"] != "historical_spot" \
                or row["lookahead"] != "FOUND", row["strategy_id"]
    # Every repair family named here exists in the table, and every family in
    # the table is named here. A route taken and not written down is the
    # failure mode this file exists to prevent.
    named = {entry["family"] for entry in REPAIRS}
    present = {r["repair_family"] for r in rows if r["repair_family"]}
    assert not (present - named), (
        "these repair families are in the status table and not in this file: "
        "%s. Add an entry to REPAIRS for each - the original message, what it "
        "actually was, the repair, and where the repair stops - then re-run "
        "`python exclusion_criteria.py`."
        % ", ".join(sorted(present - named)))
    assert not (named - present), (
        "these repair families are described here and match no row any more: "
        "%s. Either the route was withdrawn, in which case say so, or the "
        "family was renamed and the entry should follow it."
        % ", ".join(sorted(named - present)))
    print("exclusion_criteria selftest: PASS (%d excluded, %d criteria, "
          "%d repair families)" % (len(excluded), len(CRITERIA), len(named)))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", default=STATUS)
    parser.add_argument("--criteria-out", default=CRITERIA_OUT)
    parser.add_argument("--repairs-out", default=REPAIRS_OUT)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    rows = _csv(args.status)
    count, matched = criteria_report(rows, args.criteria_out)
    print("%s: %d excluded, %s"
          % (os.path.basename(args.criteria_out), count,
             ", ".join("%s=%d" % kv for kv in sorted(matched.items()))))
    total = repair_report(rows, args.repairs_out)
    print("%s: %s"
          % (os.path.basename(args.repairs_out),
             ", ".join("%s=%d" % kv for kv in sorted(total.items()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
