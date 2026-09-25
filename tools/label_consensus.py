# -*- coding: utf-8 -*-
"""label_consensus - the rule for when a second model must confirm a logic label.

Haiku 4.5 labels every strategy (`tools.strategy_labels`). Measured against a blind second
opinion (DeepSeek, `tools.label_check`), its trend_following, momentum, breakout, volatility and
grid labels were the unreliable ones: a dip-buy read as momentum or breakout, a delegating or
empty class read as grid. So a strategy whose Haiku answer carries one of those labels
(as primary, or at high/medium confidence) must also be labelled by the second model.

* `needs_second_opinion(item)` - the rule.
* `status(item)` - `single` (rule does not apply), `pending` (applies, no second answer yet),
  `confirmed` (same primary label), `contested` (different primary label).
* `confirmed_labels(item)` - the labels a report may rely on: high/medium labels; a label under
  the rule counts only when the second model also gave it at high/medium confidence.

No imports on purpose: `evidence/strategy_status.py` and the intake step both use it.
"""
SECOND_OPINION_LABELS = frozenset({"trend_following", "momentum", "breakout", "volatility", "grid"})
TRUSTED = ("high", "medium")


def _kept(labels):
    return {l["label"] for l in labels if l.get("confidence") in TRUSTED}


def needs_second_opinion(item: dict) -> bool:
    return bool(item.get("primary") in SECOND_OPINION_LABELS
                or _kept(item.get("labels", [])) & SECOND_OPINION_LABELS)


def status(item: dict) -> str:
    if not item or not needs_second_opinion(item):
        return "single"
    second = item.get("second_opinion")
    if not second:
        return "pending"
    return "confirmed" if second.get("primary") == item.get("primary") else "contested"


def confirmed_labels(item: dict) -> list:
    mine = _kept((item or {}).get("labels", []))
    if not needs_second_opinion(item or {}):
        return sorted(mine)
    second = _kept(((item or {}).get("second_opinion") or {}).get("labels", []))
    return sorted(l for l in mine if l not in SECOND_OPINION_LABELS or l in second)
