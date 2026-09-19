"""Make conservative, reproducible repair decisions for known blocked rows.

This is deliberately narrower than a generic ``fix errors`` tool.  It records
either a source-bound refusal (where running the row would require inventing
code, data, a live service, or an unavailable platform) or an explicit owner
scope decision. The latter is intentionally *not* a claim that a strategy is
intrinsically unrepairable. A first timeout is never an exclusion. A repeated,
identical timeout may be excluded only after the documented repair route was
actually applied and exhausted.

The output is consumed by ``evidence.strategy_status``.  Each decision carries
the canonical file digest, so a later harvest or source correction makes it
inapplicable rather than carrying an old judgement forward.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRIAGE = ROOT / "evidence" / "BLOCKED_TRIAGE.json"
PROFILES = ROOT / "evidence" / "EXECUTION_PROFILES.csv"
OUTPUT = ROOT / "evidence" / "REPAIR_ADJUDICATION.json"
TIMEFRAME_REPAIR = ROOT / "evidence" / "ELIGIBILITY_TIMEFRAME_REPAIR.json"


def _ids(*names: str) -> frozenset[str]:
    return frozenset(names)


# These source-bound observations retain the result of triage. The 13
# Solipsis rows deliberately do not appear: the author's repository does ship
# custom_indicators.py, so they retain a Class 1 local-module route.
HARD_LIMITS = (
    ("missing_author_dependency", _ids(
        "LitmusBBStrategy", "LitmusBBTrendStrategy", "LitmusClucStrategy",
        "LitmusSARStrategy", "LitmusScalpStrategy", "LitmusTrendScalpStrategy",
        "LitmusVulcanStrategy"),
     "Imports the unshipped cointanalysis runtime. Its model/data contract is not present in the captured repository, so installing or recreating it would not reproduce the author environment."),
    ("platform_unsupported", _ids("TS_Coeff", "TS_Gain", "TS_Wavelet"),
     "Depends on Apple MLX, which is unavailable in the canonical Linux/Windows audit runtime. Porting its tensor implementation changes the execution platform and is not a compatibility shim."),
    ("external_live_data_not_canonical", _ids("CombinedBinHAndClucV4WS", "OBOnlyWSv2bband"),
     "Depends on the BinanceStream websocket/order-book base class. A historical candle backtest cannot reproduce the required live stream without author-supplied recorded data."),
    ("not_backtest_compatible", _ids("TrailingBuySellStrat"),
     "The author explicitly states that this trailing-buy wrapper is not compatible with backtest or hyperopt; a canonical historical measurement would not measure its declared operating mode."),
    ("author_logic_incomplete", _ids("SuperBuy", "zorkv7_0_0"),
     "The recorded failure is inside author trading/model logic. Replacing it would alter signals rather than restore an API name."),
    ("not_a_strategy_fixture", _ids("_Strat"),
     "The harvested file is Framework/test_base_strategy.py, a test fixture rather than a runnable published strategy."),
)


# Explicit owner scope decision, 2026-09-17: retain only the repair routes
# that are actionable without expanding methodology. This is separate from
# HARD_LIMITS so a later owner can reopen a row without rewriting its triage.
KEEP_OPEN = _ids(
    "Solipsis_BTC", "Solipsis_ETH", "Solipsis3_BTC", "Solipsis3_ETH",
    "Solipsis4_BTC", "Solipsis4_ETH", "Solipsis5_BTC", "Solipsis5_ETH",
    "Solipsis6_BTC", "Solipsis6_ETH", "SolipsisCon_BTC", "SolipsisMM_BTC",
    "SolipsisMM_ETH", "MASlopeStrategy", "MAStopLossStrategy",
    "MATrailingStopLossStrategy", "StopLossStrategy",
    "TPActivatingTSLwithInitialTSLStrategy", "TPActivatingTSLwithSLStrategy",
    "TrailingStopLossStrategy", "ViNBuyVws",
)

POLICY_EXCLUSIONS = _ids(
    "ARIMA_5", "BBBHold", "BB_RPB_TSL_Trailing", "BaseNNStrategy",
    "ClucHAnix_BB_RPB_MOD_CTT_DTB", "CombinedBinHAndClucV4WS",
    "LitmusBBStrategy", "LitmusBBTrendStrategy", "LitmusClucStrategy",
    "LitmusSARStrategy", "LitmusScalpStrategy", "LitmusTrendScalpStrategy",
    "LitmusVulcanStrategy", "MoniGoManiHyperStrategy", "NNPredict",
    "NNPredict_LSTM", "NNPredict_LSTM0", "NNPredict_Transformer",
    "NNPredict_kTFT", "NNTC_adx_LSTM", "NNTC_bbw_Transformer",
    "NNTC_fbb_Transformer", "NNTC_jump_Transformer", "NNTC_macd_TCN",
    "NNTC_macd_Transformer", "NNTC_nseq_Transformer", "NNTC_profit_Multihead",
    "NNTC_profit_TCN", "NNTC_profit_Transformer", "NNTC_profit_Wavenet2",
    "NNTC_profit_Wavenet3", "NNTC_pv_Multihead", "OBOnlyWSv2bband",
    "SuperBuy", "TS_Coeff", "TS_Gain", "TS_Wavelet", "TrailingBuySellStrat",
    "TrailingBuyStrat", "TrailingBuyStrat2a", "_Strat", "zorkv7_0_0",
)


def _triage_context(strategy: str) -> str:
    for family, names, reason in HARD_LIMITS:
        if strategy in names:
            return "%s: %s" % (family, reason)
    return "Unselected repair branch after triage; no repair action is scheduled under the current owner scope."


def _digest(relative: str) -> str:
    path = ROOT / relative.replace("/", "\\")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _repeated_timeout_decisions(records: dict, profiles: dict[str, dict]) -> dict:
    """Derive exclusions only for identical retries after an applied repair."""
    decisions = {}
    for strategy, record in records.items():
        prior = record.get("prior_attempts") or []
        why = record.get("why")
        identical_prior = [attempt for attempt in prior
                           if attempt.get("status") == "timeout"
                           and attempt.get("why") == why
                           and attempt.get("runtime_id") == record.get("runtime_id")]
        route_applied = ("-override-" in record.get("invocation", "")
                         and bool(record.get("timeframe"))
                         and bool(record.get("timeframe_evidence")))
        # A lone timeout, an altered timeout, or a route that did not actually
        # apply an author-evidenced override remains eligible for repair.
        if record.get("status") != "timeout" or not why \
                or not identical_prior or not route_applied:
            continue
        source_file = profiles.get(strategy, {}).get("canonical_file", "")
        if not source_file:
            continue
        try:
            digest = _digest(source_file)
        except OSError:
            continue
        decisions[strategy] = {
            "strategy_id": strategy,
            "decision": "exclude_after_repeated_timeout",
            "family": "repeated_timeout_after_exhausted_repair",
            "reason": ("The author-evidenced timeframe override was applied and the same "
                       "native timeout recurred on retry; the repair route is exhausted."),
            "source_file": source_file,
            "source_sha256": digest,
            "evidence": "ELIGIBILITY_TIMEFRAME_REPAIR.json",
            "repair_route": "timeframe_recovered_from_author_declaration",
            "timeframe": record["timeframe"],
            "timerange": record.get("timerange", ""),
            "runtime_id": record.get("runtime_id", ""),
            "timeout_reason": why,
            "identical_prior_timeouts": len(identical_prior),
        }
    return decisions


def derive(triage: dict, timeframe_repair: dict | None = None) -> dict:
    """Build hash-bound owner-scope decisions without writing evidence."""
    records = triage.get("results", {})
    with io.open(PROFILES, newline="", encoding="utf-8-sig") as handle:
        profiles = {row["strategy_id"]: row for row in csv.DictReader(handle)}
    decisions: dict[str, dict] = {}
    for strategy in POLICY_EXCLUSIONS:
        # The profile is the durable source identity. A changed source digest
        # invalidates this scope decision rather than applying it to a later
        # harvested implementation with the same name.
        record = records.get(strategy) or profiles.get(strategy)
        if not record:
            continue
        source_file = record.get("source_file") or record.get("canonical_file", "")
        if not source_file:
            continue
        try:
            digest = _digest(source_file)
        except OSError:
            continue
        decisions[strategy] = {
            "strategy_id": strategy,
            "decision": "exclude_by_user_policy",
            "family": "user_policy_excluded_after_triage",
            "reason": ("Explicit owner scope decision: exclude from the repair queue after triage; "
                       "this is not a claim that the strategy is intrinsically unrepairable."),
            "triage_context": _triage_context(strategy),
            "source_file": source_file,
            "source_sha256": digest,
            "evidence": "repair.adjudicate hash-bound owner scope decision",
        }
    timeout_records = (timeframe_repair or {}).get("results", {})
    timeout_decisions = _repeated_timeout_decisions(timeout_records, profiles)
    decisions.update(timeout_decisions)
    return {"schema_version": 3, "decisions": decisions, "candidates": {},
            "keep_open": sorted(KEEP_OPEN - set(timeout_decisions)),
            "repeated_timeout_exclusions": sorted(timeout_decisions)}


def _load_triage() -> dict:
    with io.open(TRIAGE, encoding="utf-8") as handle:
        return json.load(handle)


def _load_timeframe_repair() -> dict:
    with io.open(TIMEFRAME_REPAIR, encoding="utf-8") as handle:
        return json.load(handle)


def write(data: dict) -> None:
    temporary = OUTPUT.with_suffix(".json.tmp")
    with io.open(temporary, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    temporary.replace(OUTPUT)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write the source-bound decision store")
    parser.add_argument("--selftest", action="store_true", help="validate policy shape without writing")
    args = parser.parse_args(argv)
    data = derive(_load_triage(), _load_timeframe_repair())
    assert POLICY_EXCLUSIONS <= set(data["decisions"])
    assert not (set(POLICY_EXCLUSIONS) & KEEP_OPEN)
    assert all(record["decision"] == "exclude_by_user_policy"
               for strategy, record in data["decisions"].items()
               if strategy in POLICY_EXCLUSIONS)
    timeout_ids = set(data["repeated_timeout_exclusions"])
    assert not (timeout_ids & set(data["keep_open"]))
    assert all(data["decisions"][strategy]["decision"] ==
               "exclude_after_repeated_timeout" for strategy in timeout_ids)
    assert all(len(record["source_sha256"]) == 64 for record in data["decisions"].values())
    if args.selftest:
        print("repair adjudication selftest: PASS (%d owner-scope exclusions, %d repeated-timeout exclusions, %d retained repair routes)" % (len(POLICY_EXCLUSIONS), len(timeout_ids), len(data["keep_open"])))
        return 0
    print("Repair adjudication plan: %d owner-scope exclusions; %d repeated-timeout exclusions; %d retained repair routes." % (len(POLICY_EXCLUSIONS), len(timeout_ids), len(data["keep_open"])))
    if args.apply:
        write(data)
        print("wrote %s" % OUTPUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
