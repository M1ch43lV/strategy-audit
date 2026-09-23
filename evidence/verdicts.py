# -*- coding: utf-8 -*-
"""One closed status vocabulary for every strategy-audit evidence store.

WHY THIS EXISTS. The audit answers the same kind of question in six different
token sets today. `evidence/profile_bias.py` says `PASS`/`FOUND`/`NA`; the
smoke store says `measured`/`timeout`/`failed`; the warm-up ladder says
`converged`/`inconclusive`; `evidence/regime_coverage.py` says
`PASS`/`PENDING`/`FAIL`; `evidence/regime_eligibility.py` says
`eligible`/`ineligible`; `tools/run_metadata.py` says
`PASS`/`FAIL`/`ESCALATE`/`ERROR`. The words overlap, the questions do not, and
a reader cannot tell from a bare `NA` whether a check ran and found nothing or
never ran at all.

WHAT A VERDICT IS. A verdict is one statement about one strategy, gate or run,
on exactly one LAYER: what a check found, how a run ended, whether a ladder
settled, what the pipeline decided about a row, or how an agent run ended. The
layer is not decoration - it is what makes `PASS` in a coverage check
distinguishable from `PASS` in an agent run.

THE FOUR RULES
--------------
1. `reason` is required unless the value is the satisfying value of its layer
   (`PASS`, `MEASURED`, `CONVERGED`, `ELIGIBLE`, `PASS`). A `FOUND` without a
   reason is not publishable.
2. Fail closed. An unknown token never becomes a pass: it becomes `UNKNOWN`,
   which is deliberately *not* part of any layer's vocabulary, and `satisfied()`
   is false for it. `--check` and `tools/verdict_migration_audit.py` report it.
   NOTE, and this is a deliberate deviation from the first draft of this
   schema: a single `UNKNOWN` sentinel is used for every layer instead of
   mapping to `NA`, because the `execution` and `state` layers have no `NA`
   member and inventing one would weaken the vocabulary to fit a corner case.
3. Absent is not clean. A missing value is `UNKNOWN` with reason
   `missing_value`; it is never silently dropped.
4. Normalization is field-bound, never global. `measured` means "the run
   completed" in the smoke store and "this row is an accepted measurement" in
   the full-backtest manifest. A global token table would quietly redefine one
   of them, so MAPPING is keyed by (store, field).

THIS MODULE IS A READ-SIDE LAYER. It changes how a result is *described*, never
which inputs were measured. It must therefore stay out of every identity hash:
`tools/identity_freeze.py` fails the build if a verdict token appears inside an
identity function. See `README.md` in this directory, "Verdict schema".
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field as dataclass_field


SCHEMA_VERSION = 1

LAYER_ORDER = ("check", "execution", "state", "disposition", "run")

# The closed vocabulary of each layer. Adding a member is a schema change and
# belongs in the decision record of ../PIPELINE.md.
LAYERS = {
    "check": ("PASS", "FOUND", "NA", "SKIP"),
    "execution": ("MEASURED", "TIMEOUT", "FAILED", "RESOURCE_INCONCLUSIVE",
                  "INCOMPLETE"),
    "state": ("CONVERGED", "NOT_CONVERGED", "INCONCLUSIVE"),
    "disposition": ("ELIGIBLE", "EXCLUDED", "PENDING"),
    "run": ("PASS", "FAIL", "ESCALATE", "ERROR"),
}

# The one value per layer that means "this question was answered without a
# finding". Everything else carries a reason.
SATISFIED = {
    "check": "PASS",
    "execution": "MEASURED",
    "state": "CONVERGED",
    "disposition": "ELIGIBLE",
    "run": "PASS",
}

# Deliberately outside every layer vocabulary so that it can never be mistaken
# for a member, and so that `satisfied()` is false for it by construction.
UNKNOWN = "UNKNOWN"

# Rule 1 holds even when a store carries nothing but a token. The specific
# detail stays in the store's own `why`/`evidence` field; this names the class of
# the finding. `_check()` requires an entry for every non-satisfying value in
# every layer, so adding a vocabulary member cannot leave a silent gap.
DEFAULT_REASONS = {
    ("check", "FOUND"): "finding_recorded",
    ("check", "NA"): "not_available",
    ("check", "SKIP"): "not_run",
    ("execution", "TIMEOUT"): "timeout",
    ("execution", "FAILED"): "failed",
    ("execution", "RESOURCE_INCONCLUSIVE"): "resource_inconclusive",
    ("execution", "INCOMPLETE"): "incomplete_measurement",
    ("state", "NOT_CONVERGED"): "drift_above_tolerance",
    ("state", "INCONCLUSIVE"): "inconclusive",
    ("disposition", "EXCLUDED"): "excluded",
    ("disposition", "PENDING"): "pending",
    ("run", "FAIL"): "failed",
    ("run", "ESCALATE"): "escalated",
    ("run", "ERROR"): "error",
}

# Token sets that recur across stores. Sharing the *tokens* is safe; sharing the
# meaning is not, which is why they are still bound per (store, field) below.
_EXECUTION_OUTCOMES = {
    "measured": "MEASURED",
    "timeout": "TIMEOUT",
    "failed": "FAILED",
    "resource_inconclusive": "RESOURCE_INCONCLUSIVE",
}

# A mapped token is either a plain value, or (value, reason) when the token
# itself states why it is not the satisfying value.
MAPPING = {
    # Stage 1 - how the smoke run ended.
    ("PROFILE_SMOKE.json", "status"): ("execution", dict(_EXECUTION_OUTCOMES)),
    # Stage 8 - how the canonical pooled full backtest ended. The three
    # `*_confirmed` tokens are the retired statuses of regime/full_backtest.py:
    # oom and performance are fixed-budget walls (memory, wall clock), while
    # stake overflow is a deterministic numeric failure, not a budget.
    ("full_backtest_manifest.json", "status"): ("execution", {
        "measured": "MEASURED",
        "timeout": "TIMEOUT",
        "failed": "FAILED",
        "resource_inconclusive": "RESOURCE_INCONCLUSIVE",
        "oom_confirmed": ("RESOURCE_INCONCLUSIVE", "oom_confirmed"),
        "performance_limited": ("RESOURCE_INCONCLUSIVE", "performance_limited"),
        "stake_overflow_confirmed": ("FAILED", "stake_overflow_confirmed"),
    }),
    ("PROFILE_FULL_WINDOW.json", "status"): ("execution", {
        **_EXECUTION_OUTCOMES,
        "incomplete": "INCOMPLETE",
    }),
    # Stages 2 and 4 - the two native bias gates. `FOUND` here keeps its
    # original meaning - "a bias was found" - and the reason names WHICH bias.
    ("PROFILE_BIAS.json", "lookahead.status"): ("check", {
        "PASS": "PASS",
        "FOUND": ("FOUND", "lookahead_bias_found"),
        "NA": "NA",
    }),
    ("PROFILE_BIAS.json", "recursive.status"): ("check", {
        "PASS": "PASS",
        "FOUND": ("FOUND", "recursion_bias_found"),
        "NA": "NA",
        "WARMUP_NEEDED": ("SKIP", "warmup_not_settled"),
    }),
    # Stage 3 - the warm-up convergence ladder.
    ("WARMUP_CONVERGENCE.json", "state"): ("state", {
        "converged": "CONVERGED",
        "not_converged_within_ladder": "NOT_CONVERGED",
        "inconclusive": "INCONCLUSIVE",
        "no_usable_ladder": ("INCONCLUSIVE", "no_usable_ladder"),
        "crashes_even_at_longest_rungs": ("INCONCLUSIVE", "crashes_even_at_longest_rungs"),
    }),
    # Stage 8b - the detail classifier. `ERROR` means the classifier ran but
    # had no usable comparison run; it is not a finding about the strategy.
    ("EXECUTION_ROBUSTNESS.json", "status"): ("check", {
        "PASS": "PASS",
        "SENSITIVE": ("FOUND", "sensitive_to_detail_granularity"),
        "PENDING": ("SKIP", "robustness_not_yet_measured"),
        "NA": "NA",
        "ERROR": ("NA", "detail_classification_error"),
    }),
    # Stage 8b - the cost screen: does the net profit survive reference slippage?
    ("COST_SCREEN.json", "status"): ("check", {
        "PASS": "PASS",
        "SENSITIVE": ("FOUND", "sensitive_to_cost"),
        "NA": "NA",
    }),
    # Stage 5 - data coverage.
    ("REGIME_COVERAGE.csv", "coverage_status"): ("check", {
        "PASS": "PASS",
        "PENDING": ("SKIP", "coverage_problems_present"),
        "FAIL": ("FOUND", "coverage_problems_present"),
    }),
    # The published admission decision.
    ("REGIME_ELIGIBILITY.csv", "eligibility_status"): ("disposition", {
        "eligible": "ELIGIBLE",
        "pending_diagnostics": "PENDING",
        "ineligible": ("EXCLUDED", "ineligible"),
    }),
    # The published flat view. `PASS_1PCT` is the narrower recursion band: it is
    # a pass whose tolerance is worth naming, not a separate verdict.
    ("STRATEGY_STATUS.csv", "recursive"): ("check", {
        "PASS": "PASS",
        "PASS_1PCT": ("PASS", "recursive_drift_below_1pct"),
        "FOUND": ("FOUND", "recursion_bias_found"),
        "NA": "NA",
        "WARMUP_NEEDED": ("SKIP", "warmup_not_settled"),
    }),
    # The rest of STRATEGY_STATUS.csv's verdict columns. This file is the
    # published read model, so a consumer that needs one strategy's verdict
    # reads these rather than re-deriving precedence from the raw stores.
    ("STRATEGY_STATUS.csv", "lookahead"): ("check", {
        "PASS": "PASS",
        "FOUND": ("FOUND", "lookahead_bias_found"),
        "NA": "NA",
    }),
    ("STRATEGY_STATUS.csv", "coverage_status"): ("check", {
        "PASS": "PASS",
        "PENDING": ("SKIP", "coverage_problems_present"),
        "FAIL": ("FOUND", "coverage_problems_present"),
    }),
    ("STRATEGY_STATUS.csv", "full_backtest_status"): ("execution", {
        "measured": "MEASURED",
        "timeout": "TIMEOUT",
        "failed": "FAILED",
        "resource_inconclusive": "RESOURCE_INCONCLUSIVE",
        "oom_confirmed": ("RESOURCE_INCONCLUSIVE", "oom_confirmed"),
        "performance_limited": ("RESOURCE_INCONCLUSIVE", "performance_limited"),
        "stake_overflow_confirmed": ("FAILED", "stake_overflow_confirmed"),
    }),
    ("STRATEGY_STATUS.csv", "execution_robustness_status"): ("check", {
        "PASS": "PASS",
        "SENSITIVE": ("FOUND", "sensitive_to_detail_granularity"),
        "PENDING": ("SKIP", "robustness_not_yet_measured"),
        "NA": "NA",
        "ERROR": ("NA", "detail_classification_error"),
    }),
    ("STRATEGY_STATUS.csv", "cost_screen_status"): ("check", {
        "PASS": "PASS",
        "SENSITIVE": ("FOUND", "sensitive_to_cost"),
        "PENDING": ("SKIP", "cost_not_yet_screened"),
        "NA": "NA",
    }),
    ("STRATEGY_STATUS.csv", "baseline_status"): ("disposition", {
        "eligible": "ELIGIBLE",
        "pending_diagnostics": "PENDING",
        "ineligible": ("EXCLUDED", "ineligible"),
    }),
    # The frozen eligibility snapshot carries the same bias and coverage
    # columns; its own `eligibility_status` is mapped further up.
    ("REGIME_ELIGIBILITY.csv", "lookahead"): ("check", {
        "PASS": "PASS",
        "FOUND": ("FOUND", "lookahead_bias_found"),
        "NA": "NA",
    }),
    ("REGIME_ELIGIBILITY.csv", "recursive"): ("check", {
        "PASS": "PASS",
        "FOUND": ("FOUND", "recursion_bias_found"),
        "NA": "NA",
    }),
    ("REGIME_ELIGIBILITY.csv", "coverage_status"): ("check", {
        "PASS": "PASS",
        "PENDING": ("SKIP", "coverage_problems_present"),
        "FAIL": ("FOUND", "coverage_problems_present"),
    }),
    # The overlay equivalence class of a repaired source: does the patched copy
    # behave like the author's original? `output_equivalent` is the weaker of
    # the two passing kinds and says so in its reason, because the difference
    # between a strict and an output equivalence is provenance, not trust.
    ("REGIME_ELIGIBILITY.csv", "equivalence_status"): ("check", {
        "strict_equivalent": ("PASS", "strict_equivalent"),
        "output_equivalent": ("PASS", "output_equivalent"),
        "behavior_changed": ("FOUND", "behavior_changed"),
        "not_applicable": "NA",
    }),
    # Operational provenance of an agent run - a different axis from a gate.
    ("RUN_METADATA.jsonl", "status"): ("run", {
        "PASS": "PASS",
        "FAIL": "FAIL",
        "ESCALATE": "ESCALATE",
        "ERROR": "ERROR",
    }),
    # Repair routes: their run results reuse the smoke-run outcomes verbatim
    # (every writer below calls profile_smoke.run_one), so the layer is
    # execution and the tokens are the same four.
    ("ELIGIBILITY_TIMEFRAME_EVIDENCE.json", "status"): ("execution", dict(_EXECUTION_OUTCOMES)),
    ("ELIGIBILITY_TIMEFRAME_REPAIR.json", "status"): ("execution", dict(_EXECUTION_OUTCOMES)),
    ("ELIGIBILITY_MODULE_REPAIR.json", "status"): ("execution", dict(_EXECUTION_OUTCOMES)),
    ("ELIGIBILITY_SIGNATURE_REPAIR.json", "status"): ("execution", dict(_EXECUTION_OUTCOMES)),
    ("ELIGIBILITY_RL_IMAGE.json", "status"): ("execution", dict(_EXECUTION_OUTCOMES)),
    ("ELIGIBILITY_FREQAI_REPAIR.json", "status"): ("execution", dict(_EXECUTION_OUTCOMES)),
    ("ELIGIBILITY_FREQAI_WTAI.json", "status"): ("execution", dict(_EXECUTION_OUTCOMES)),
    # The 5m recovery route: where the recovery landed. `promoted_E1` is an
    # admission; the blocked states and an unmeasured full backtest are still
    # pending. This is a disposition, not an execution outcome.
    ("TIMEFRAME_5M_RECOVERY.json", "status"): ("disposition", {
        "promoted_E1": ("ELIGIBLE", "promoted_e1"),
        "measured_5m_pending_owner_promotion": ("PENDING", "measured_5m_pending_owner_promotion"),
        "recovery_blocked_warmup": ("PENDING", "recovery_blocked_warmup"),
        "recovery_blocked_smoke": ("PENDING", "recovery_blocked_smoke"),
        "recovery_blocked_lookahead": ("PENDING", "recovery_blocked_lookahead"),
        "recovery_blocked_recursive": ("PENDING", "recovery_blocked_recursive"),
        "recovery_full_backtest_not_measured": ("PENDING", "recovery_full_backtest_not_measured"),
    }),
}

# Columns that are taxonomies, not verdicts. They are named here so that an
# audit can report "deliberately not a verdict" instead of "unmapped", which
# would hide a real gap among false ones. Three further kinds live here:
# repair provenance (resolved/unresolved), discovery indexes, and the
# per-pair shard inputs that merge into the canonical full-window store.
OUT_OF_SCOPE = frozenset((
    ("STRATEGY_STATUS.csv", "cohort"),
    ("STRATEGY_STATUS.csv", "artifact_role"),
    ("STRATEGY_STATUS.csv", "expansion_wave"),
    ("STRATEGY_STATUS.csv", "repair_family"),
    ("STRATEGY_STATUS.csv", "repair_verdict"),
    ("STRATEGY_STATUS.csv", "execution_robustness_basis"),
    ("EXECUTION_PROFILES.csv", "repair_class"),
    ("EXECUTION_PROFILES.csv", "environment_repair_status"),
    # Boolean summaries of a verdict, not verdicts: they answer "is there a
    # measurement / a complete chain", which the layer already answers.
    ("STRATEGY_STATUS.csv", "measured"),
    ("STRATEGY_STATUS.csv", "technical_chain_complete"),
    ("REGIME_ELIGIBILITY.csv", "canonical_measured"),
    ("REGIME_ELIGIBILITY.csv", "regime_eligible"),
    ("REPAIR_LOCAL_MODULES.json", "status"),
    ("NEW_REPO_CANDIDATES.json", "status"),
    ("ELIGIBILITY_EXPANSION_MANIFEST.json", "status"),
    ("PROFILE_FULL_WINDOW_shardA.json", "status"),
    ("PROFILE_FULL_WINDOW_shardB.json", "status"),
    ("PROFILE_FULL_WINDOW_shardTF.json", "status"),
    ("PROFILE_FULL_WINDOW_shardZeroConfirm.json", "status"),
))


@dataclass(frozen=True)
class Verdict:
    """One statement about one strategy, gate or run on exactly one layer."""

    store: str
    field: str
    raw: object
    layer: str = ""
    value: str = UNKNOWN
    reason: str = ""
    evidence: str = ""
    mapped: bool = False
    extra: tuple = dataclass_field(default_factory=tuple)

    @property
    def satisfied(self) -> bool:
        """True only for the satisfying value of this verdict's own layer."""
        return bool(self.layer) and self.value == SATISFIED.get(self.layer)

    def line(self) -> str:
        """One readable line, for a report or an error message."""
        where = "%s.%s" % (self.store, self.field)
        why = " (%s)" % self.reason if self.reason else ""
        return "%s = %s%s [raw %r]" % (where, self.value, why, self.raw)


def _resolve(entry, token):
    """Return (value, reason) for one mapped token, or None when unmapped."""
    if token not in entry:
        return None
    mapped = entry[token]
    if isinstance(mapped, tuple):
        return mapped[0], mapped[1]
    return mapped, ""


def normalize(store, field, raw, reason="", evidence=""):
    """Turn one raw store value into a Verdict without ever inventing a pass.

    `raw` is what the store actually holds today; `reason` may carry a reason
    the caller already knows (for example `TIMEOUT` recorded beside an `NA`).
    """
    key = (store, field)
    mapping = MAPPING.get(key)
    if mapping is None:
        scope = "out_of_scope" if key in OUT_OF_SCOPE else "unmapped_field"
        return Verdict(store=store, field=field, raw=raw, reason=scope,
                       evidence=evidence, mapped=False)
    layer, entry = mapping
    if raw is None or raw == "":
        return Verdict(store=store, field=field, raw=raw, layer=layer,
                       value=UNKNOWN, reason="missing_value",
                       evidence=evidence, mapped=True)
    token = str(raw)
    hit = _resolve(entry, token)
    if hit is None:
        return Verdict(store=store, field=field, raw=raw, layer=layer,
                       value=UNKNOWN, reason="unknown_token:%s" % token,
                       evidence=evidence, mapped=True)
    value, token_reason = hit
    if value not in LAYERS[layer]:
        # A mapping table error must be loud, not silently accepted.
        return Verdict(store=store, field=field, raw=raw, layer=layer,
                       value=UNKNOWN, reason="invalid_mapping:%s" % value,
                       evidence=evidence, mapped=True)
    if not token_reason and value != SATISFIED[layer]:
        token_reason = (reason or DEFAULT_REASONS.get((layer, value))
                        or "not_satisfied")
    return Verdict(store=store, field=field, raw=raw, layer=layer, value=value,
                   reason=token_reason or reason, evidence=evidence, mapped=True)


def value(store, field, raw, reason=""):
    """The normalized value of a raw token - what a comparison should use.

    `raw in ("PASS", "FOUND")` and `value(...) in ("PASS", "FOUND")` agree for
    every token the store can write today; they differ for a token nobody has
    mapped, which this returns as `UNKNOWN` instead of passing it through. Use
    this only where the comparison means "which verdict class". A comparison
    that deliberately distinguishes two raw states on the same class (the
    warm-up ladder's `crashes_even_at_longest_rungs` beside `inconclusive`)
    must keep reading the raw value, or it would silently broaden.
    """
    return normalize(store, field, raw, reason=reason).value


def tokens():
    """Every token the schema knows, for the identity guard in tools/."""
    out = {UNKNOWN}
    for vocabulary in LAYERS.values():
        out.update(vocabulary)
    for _layer, entry in MAPPING.values():
        out.update(entry)
        for mapped in entry.values():
            out.add(mapped[0] if isinstance(mapped, tuple) else mapped)
    return frozenset(out)


def acceptance(*items, identity_ok=True):
    """The bounded acceptance gate: (accepted, blockers).

    An item is a Verdict or a (label, Verdict) pair. A missing, unknown or
    unsatisfied verdict blocks acceptance, and so does an identity mismatch -
    the schema may never accept a result it cannot bind to the inputs that
    produced it.
    """
    blockers = []
    if not identity_ok:
        blockers.append("identity_mismatch")
    if not items:
        blockers.append("no_verdicts_supplied")
    for item in items:
        label, verdict = item if isinstance(item, tuple) else ("", item)
        if not verdict.mapped:
            blockers.append("%s:unmapped_field" % (label or verdict.field))
        elif not verdict.satisfied:
            blockers.append("%s:%s" % (label or verdict.field,
                                       verdict.reason or verdict.value))
    return (not blockers), tuple(blockers)


# The gates the canonical read model publishes, each bound to the store and
# field its raw token comes from. Binding them here means the published block
# names only a gate, and `decode` can restore a full verdict from it - so no
# consumer has to reimplement the vocabulary to read its own read model.
GATES = {
    "measurement": ("PROFILE_SMOKE.json", "status"),
    "lookahead": ("STRATEGY_STATUS.csv", "lookahead"),
    "recursive": ("STRATEGY_STATUS.csv", "recursive"),
    "full_backtest": ("STRATEGY_STATUS.csv", "full_backtest_status"),
    "execution_robustness": ("STRATEGY_STATUS.csv", "execution_robustness_status"),
    "cost_screen": ("STRATEGY_STATUS.csv", "cost_screen_status"),
}


def block(values):
    """Encode one verdict per gate, compactly, as the read model publishes it.

    The form is the bare value when the verdict carries no reason, and
    {"value": ..., "reason": ...} when it does. `layer` and `satisfied` are
    deliberately absent: both follow from the gate name and the value through
    this module, and carrying them cost two thirds of the block. A verdict that
    keeps a reason - a PASS whose tolerance is worth naming, an absence, a
    deferral - stays an object, so the reason is never lost.

    `values` maps a gate name in GATES to the raw store token, or to a
    (raw, reason) pair when the caller knows a reason the store does not.
    """
    out = {}
    for gate, supplied in values.items():
        if gate not in GATES:
            raise KeyError("unknown gate %r" % (gate,))
        store, field_name = GATES[gate]
        raw, reason = supplied if isinstance(supplied, tuple) else (supplied, "")
        verdict = normalize(store, field_name, raw, reason=reason)
        out[gate] = ({"value": verdict.value, "reason": verdict.reason}
                     if verdict.reason else verdict.value)
    return out


def decode(gate, encoded):
    """Restore a Verdict from one entry of a published block.

    The entry already holds a *normalized* value, so this must not re-normalize
    it: `FOUND` and `SKIP` are values of the schema and not raw tokens of the
    store they came from, and a round trip through `normalize` would reject
    them. A value outside its layer's vocabulary degrades to UNKNOWN rather
    than being accepted.
    """
    store, field_name = GATES[gate]
    layer = MAPPING[(store, field_name)][0]
    if isinstance(encoded, dict):
        value = encoded.get("value")
        reason = encoded.get("reason", "")
    else:
        value, reason = encoded, ""
    if value not in LAYERS[layer]:
        return Verdict(store=store, field=field_name, raw=encoded, layer=layer,
                       value=UNKNOWN, reason=reason or "unknown_value:%s" % value,
                       mapped=True)
    return Verdict(store=store, field=field_name, raw=encoded, layer=layer,
                   value=value, reason=reason, mapped=True)


def decode_block(payload):
    """{gate: Verdict} from a published block."""
    return {gate: decode(gate, encoded) for gate, encoded in payload.items()
            if gate in GATES}


def _check():
    """Internal consistency. Deliberate, documented duplication as a
    change-detector: extending a vocabulary means editing here too."""
    problems = []
    expected_order = ("check", "execution", "state", "disposition", "run")
    if LAYER_ORDER != expected_order:
        problems.append("LAYER_ORDER changed: %r" % (LAYER_ORDER,))
    for layer in LAYER_ORDER:
        vocabulary = LAYERS.get(layer)
        if not vocabulary:
            problems.append("%s: empty or missing vocabulary" % layer)
            continue
        if len(set(vocabulary)) != len(vocabulary):
            problems.append("%s: duplicate token" % layer)
        if any(token != token.upper() for token in vocabulary):
            problems.append("%s: token is not uppercase" % layer)
        if UNKNOWN in vocabulary:
            problems.append("%s: UNKNOWN must not be a member" % layer)
        if SATISFIED.get(layer) not in vocabulary:
            problems.append("%s: SATISFIED is not a member" % layer)
        for token in vocabulary:
            if token != SATISFIED.get(layer) and (layer, token) not in DEFAULT_REASONS:
                problems.append("%s: no default reason for %s" % (layer, token))
    for key, (layer, entry) in MAPPING.items():
        if layer not in LAYERS:
            problems.append("%s: unknown layer %s" % (key, layer))
            continue
        if key in OUT_OF_SCOPE:
            problems.append("%s: mapped and out of scope" % (key,))
        for token, mapped in entry.items():
            value = mapped[0] if isinstance(mapped, tuple) else mapped
            if value not in LAYERS[layer]:
                problems.append("%s: %s -> %s is not in %s"
                                % (key, token, value, layer))
    for key in OUT_OF_SCOPE:
        if key in MAPPING:
            problems.append("%s: out of scope and mapped" % (key,))
    if SCHEMA_VERSION != 1:
        problems.append("SCHEMA_VERSION is %r, expected 1" % SCHEMA_VERSION)
    return problems


def selftest():
    """Every rule the module claims, exercised on the rule itself."""
    problems = _check()

    def check(condition, message):
        if not condition:
            problems.append(message)

    # 2. Fail closed: an unknown token is never a pass and never a member.
    odd = normalize("EXECUTION_ROBUSTNESS.json", "status", "TOTALLY_NEW")
    check(odd.value == UNKNOWN, "unknown token became %r" % odd.value)
    check(not odd.satisfied, "unknown token counted as satisfied")
    check(odd.reason == "unknown_token:TOTALLY_NEW", "wrong reason %r" % odd.reason)

    # 3. Absent is not clean.
    for absent in (None, ""):
        missing = normalize("PROFILE_SMOKE.json", "status", absent)
        check(missing.value == UNKNOWN, "absent value became %r" % missing.value)
        check(missing.reason == "missing_value", "absent reason %r" % missing.reason)

    # 4. Field-bound: the same token means a different layer in another field.
    smoke = normalize("PROFILE_SMOKE.json", "status", "measured")
    check(smoke.layer == "execution" and smoke.satisfied,
          "smoke 'measured' is not an execution MEASURED")
    manifest = normalize("full_backtest_manifest.json", "status", "measured")
    check(manifest.layer == "execution", "manifest 'measured' lost its layer")

    # 1. A reason is required for everything that is not satisfying. The two
    # bias gates name WHICH bias was found, so FOUND never reads as "something
    # generic was found".
    found = normalize("PROFILE_BIAS.json", "lookahead.status", "FOUND")
    check(found.value == "FOUND" and found.reason == "lookahead_bias_found",
          "lookahead FOUND lost its meaning (%r)" % found.reason)
    check(not found.satisfied, "FOUND counted as satisfied")
    recursion_found = normalize("PROFILE_BIAS.json", "recursive.status", "FOUND")
    check(recursion_found.reason == "recursion_bias_found",
          "recursive FOUND lost its meaning (%r)" % recursion_found.reason)
    check(found.reason != recursion_found.reason,
          "lookahead and recursion FOUND must not collapse into one reason")
    na = normalize("PROFILE_BIAS.json", "lookahead.status", "NA")
    check(na.value == "NA" and not na.satisfied, "NA counted as satisfied")
    check(na.reason == "not_available", "NA did not get a default reason")

    # A narrower pass keeps its tolerance visible in the reason.
    narrow = normalize("STRATEGY_STATUS.csv", "recursive", "PASS_1PCT")
    check(narrow.satisfied and narrow.reason == "recursive_drift_below_1pct",
          "PASS_1PCT lost its tolerance reason")

    # Caller-supplied reasons survive, and a token reason wins over them.
    timed_out = normalize("PROFILE_BIAS.json", "lookahead.status", "NA",
                          reason="TIMEOUT")
    check(timed_out.reason == "TIMEOUT", "caller reason was dropped")
    sensitive = normalize("EXECUTION_ROBUSTNESS.json", "status", "SENSITIVE",
                          reason="TIMEOUT")
    check(sensitive.reason == "sensitive_to_detail_granularity",
          "token reason did not win")

    # The migration-audit findings, each pinned to its decided layer and value.
    warmup = normalize("PROFILE_BIAS.json", "recursive.status", "WARMUP_NEEDED")
    check(warmup.value == "SKIP" and warmup.reason == "warmup_not_settled",
          "WARMUP_NEEDED is not a SKIP: %r" % warmup.line())
    error = normalize("EXECUTION_ROBUSTNESS.json", "status", "ERROR")
    check(error.value == "NA" and error.reason == "detail_classification_error",
          "robustness ERROR is not an NA: %r" % error.line())
    incomplete = normalize("PROFILE_FULL_WINDOW.json", "status", "incomplete")
    check(incomplete.value == "INCOMPLETE" and not incomplete.satisfied,
          "full-window incomplete lost its value: %r" % incomplete.line())
    oom = normalize("full_backtest_manifest.json", "status", "oom_confirmed")
    check(oom.value == "RESOURCE_INCONCLUSIVE" and oom.reason == "oom_confirmed",
          "oom_confirmed lost its value: %r" % oom.line())
    overflow = normalize("full_backtest_manifest.json", "status",
                         "stake_overflow_confirmed")
    check(overflow.value == "FAILED" and overflow.reason == "stake_overflow_confirmed",
          "stake_overflow_confirmed lost its value: %r" % overflow.line())

    # The remaining 15 fields, each pinned to its decided layer or scope.
    promoted = normalize("TIMEFRAME_5M_RECOVERY.json", "status", "promoted_E1")
    check(promoted.value == "ELIGIBLE" and promoted.satisfied,
          "promoted_E1 is not an ELIGIBLE disposition: %r" % promoted.line())
    blocked = normalize("TIMEFRAME_5M_RECOVERY.json", "status",
                        "recovery_blocked_warmup")
    check(blocked.value == "PENDING" and not blocked.satisfied,
          "recovery_blocked_warmup is not PENDING: %r" % blocked.line())
    tf_repair = normalize("ELIGIBILITY_TIMEFRAME_REPAIR.json", "status", "measured")
    check(tf_repair.layer == "execution" and tf_repair.satisfied,
          "a repair run is not an execution MEASURED")
    modules = normalize("REPAIR_LOCAL_MODULES.json", "status", "resolved")
    check(not modules.mapped and modules.reason == "out_of_scope",
          "repair provenance was not marked out of scope: %r" % modules.line())
    shard = normalize("PROFILE_FULL_WINDOW_shardA.json", "status", "measured")
    check(not shard.mapped and shard.reason == "out_of_scope",
          "a shard input was not marked out of scope: %r" % shard.line())

    # The published verdict columns of both CSVs.
    check(normalize("STRATEGY_STATUS.csv", "full_backtest_status", "oom_confirmed").value
          == "RESOURCE_INCONCLUSIVE",
          "the published full-backtest column is unmapped")
    check(normalize("STRATEGY_STATUS.csv", "lookahead", "FOUND").reason
          == "lookahead_bias_found",
          "the published lookahead column lost its meaning")
    check(normalize("REGIME_ELIGIBILITY.csv", "recursive", "FOUND").reason
          == "recursion_bias_found",
          "the eligibility recursive column lost its meaning")
    check(normalize("STRATEGY_STATUS.csv", "measured", "true").reason
          == "out_of_scope",
          "a boolean summary was treated as a verdict")
    check(normalize("REGIME_ELIGIBILITY.csv", "equivalence_status",
                    "behavior_changed").value == "FOUND",
          "a changed repair overlay is not a finding")
    check(normalize("REGIME_ELIGIBILITY.csv", "equivalence_status",
                    "output_equivalent").satisfied,
          "an output-equivalent overlay is not a pass")

    # The read-model block: bare value when there is no reason, an object when
    # there is, and a decode that loses nothing.
    published = block({
        "lookahead": "FOUND",
        "recursive": "WARMUP_NEEDED",
        "cost_screen": None,
        "execution_robustness": "PASS",
        "measurement": "measured",
    })
    check(set(published) == {"lookahead", "recursive", "cost_screen",
                            "execution_robustness", "measurement"},
          "the verdict block lost a gate")
    check(published["lookahead"] == {"value": "FOUND",
                                     "reason": "lookahead_bias_found"},
          "the block lost the lookahead meaning: %r" % (published["lookahead"],))
    check(published["recursive"] == {"value": "SKIP",
                                     "reason": "warmup_not_settled"},
          "the block lost WARMUP_NEEDED: %r" % (published["recursive"],))
    check(published["cost_screen"] == {"value": UNKNOWN,
                                       "reason": "missing_value"},
          "an absent gate was not reported as missing")
    check(published["execution_robustness"] == "PASS",
          "a reasonless pass was not compacted: %r"
          % (published["execution_robustness"],))
    check(published["measurement"] == "MEASURED",
          "a reasonless execution value was not compacted")
    check(json.loads(json.dumps(published)) == published,
          "the verdict block is not JSON-safe")

    # A pass that keeps a reason must stay an object, or the tolerance it names
    # is lost - the one case where the compact form could quietly drop meaning.
    narrow_block = block({"recursive": "PASS_1PCT"})
    check(narrow_block["recursive"] == {"value": "PASS",
                                        "reason": "recursive_drift_below_1pct"},
          "the compact form dropped the narrower pass's reason")

    # decode restores the layer and the satisfied flag from the gate name alone.
    decoded = decode("lookahead", published["lookahead"])
    check(decoded.layer == "check" and decoded.value == "FOUND"
          and not decoded.satisfied,
          "decode lost a finding: %r" % decoded.line())
    check(decode("measurement", "MEASURED").satisfied,
          "decode lost the satisfied flag on a compact value")
    check(decode("lookahead", "NOT_A_VALUE").value == UNKNOWN,
          "decode accepted a value outside the layer vocabulary")
    check(decode_block(published)["cost_screen"].reason == "missing_value",
          "decode_block lost a reason")

    # `value()` answers with the class, and an unmapped token is UNKNOWN rather
    # than a raw string that happens not to match.
    check(value("PROFILE_BIAS.json", "lookahead.status", "FOUND") == "FOUND",
          "value() lost a mapped token")
    check(value("PROFILE_BIAS.json", "lookahead.status", None) == UNKNOWN,
          "value() did not fail closed on an absent token")
    check(value("PROFILE_BIAS.json", "lookahead.status", "NEW_TOKEN") == UNKNOWN,
          "value() passed an unmapped token through")

    # Unmapped and out-of-scope fields are reported, not guessed.
    unmapped = normalize("SOMETHING_NEW.json", "status", "PASS")
    check(not unmapped.mapped and unmapped.reason == "unmapped_field",
          "an unmapped field was accepted")
    scope = normalize("STRATEGY_STATUS.csv", "cohort", "excluded")
    check(not scope.mapped and scope.reason == "out_of_scope",
          "an out-of-scope column was treated as a verdict")

    # The acceptance gate refuses an unmapped, an unknown and a mismatch.
    accepted, blockers = acceptance(("lookahead", found))
    check(not accepted and blockers == ("lookahead:lookahead_bias_found",),
          "acceptance accepted a FOUND: %r" % (blockers,))
    accepted, blockers = acceptance(("lookahead", normalize(
        "PROFILE_BIAS.json", "lookahead.status", "PASS")))
    check(accepted and not blockers, "acceptance refused a PASS")
    accepted, blockers = acceptance(("x", odd), identity_ok=False)
    check(blockers == ("identity_mismatch", "x:unknown_token:TOTALLY_NEW"),
          "acceptance blockers are wrong: %r" % (blockers,))
    accepted, blockers = acceptance()
    check(blockers == ("no_verdicts_supplied",),
          "an empty gate accepted: %r" % (blockers,))

    for problem in problems:
        print("FAIL %s" % problem)
    print("verdicts selftest: %d problem(s)" % len(problems))
    return 1 if problems else 0


def _list():
    print("verdict schema v%d" % SCHEMA_VERSION)
    for layer in LAYER_ORDER:
        print("  %-12s satisfied=%-11s %s"
              % (layer, SATISFIED[layer], " ".join(LAYERS[layer])))
    print("\nmapped stores and fields:")
    for (store, field_name), (layer, entry) in sorted(MAPPING.items()):
        print("  %-28s %-18s %s" % (store, field_name, layer))
        for token, mapped in sorted(entry.items()):
            if isinstance(mapped, tuple):
                print("      %-30s -> %s (%s)" % (token, mapped[0], mapped[1]))
            else:
                print("      %-30s -> %s" % (token, mapped))
    print("\nnot verdicts (taxonomies): %d named"
          % len(OUT_OF_SCOPE))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true",
                        help="print the layers, vocabs and the mapping table")
    parser.add_argument("--check", action="store_true",
                        help="fail on any internal inconsistency")
    parser.add_argument("--selftest", action="store_true",
                        help="exercise every rule of the schema")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.list:
        return _list()
    if args.check:
        problems = _check()
        for problem in problems:
            print("FAIL %s" % problem)
        print("verdict schema check: %d problem(s)" % len(problems))
        return 1 if problems else 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
