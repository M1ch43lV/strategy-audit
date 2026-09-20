"""Narrow compatibility surface for XXA222's Hedge strategy example.

The upstream strategy imports ``freqtrade.strategy.hedge.HedgeStrategyMixin``.
That module belongs to XXA222's fork and is absent from the pinned audit
runtime. The upstream mixin only validates its optional Hedge signal-column
contract; it does not calculate indicators, entries, exits, sizing, or orders.

This module lives beside this one patched strategy, is loaded only through its
``--strategy-path``, and does not patch the installed ``freqtrade`` package.
"""
from __future__ import annotations


HEDGE_SIGNAL_COLUMNS = (
    "hedge_long_score",
    "hedge_short_score",
    "hedge_target_net",
    "hedge_target_net_ratio",
    "hedge_confidence",
    "hedge_risk_scale",
    "hedge_long_exposure_scale",
    "hedge_short_exposure_scale",
    "hedge_allow_new_risk",
    "hedge_regime",
    "hedge_reason",
    "hedge_model_version",
)


class HedgeStrategyMixin:
    """Upstream-compatible validator for the passive Hedge signal contract."""

    hedge_allowed_columns = frozenset(HEDGE_SIGNAL_COLUMNS)

    @classmethod
    def validate_hedge_dataframe(cls, dataframe: object) -> None:
        columns = set(getattr(dataframe, "columns", ()))
        unknown = {
            str(name)
            for name in columns
            if str(name).startswith("hedge_") and name not in cls.hedge_allowed_columns
        }
        if unknown:
            raise ValueError("unknown Hedge signal column(s): " + ", ".join(sorted(unknown)))
        if not ({"hedge_long_score", "hedge_short_score"} & columns):
            raise ValueError("strategy must emit Hedge scores or legacy enter_long/enter_short")

    @classmethod
    def hedge_contract_columns(cls) -> tuple[str, ...]:
        return HEDGE_SIGNAL_COLUMNS
