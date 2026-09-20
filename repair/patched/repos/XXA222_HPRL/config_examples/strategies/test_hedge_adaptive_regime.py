"""Reproducible no-data contract test for HedgeAdaptiveRegimeStrategy.

Run from the audit root with:
    .\\ftenv\\Scripts\\python.exe repair\\patched\\repos\\XXA222_HPRL\\config_examples\\strategies\\test_hedge_adaptive_regime.py

This is not a backtest and writes no audit result artifact.  It only checks
that the isolated import path and deterministic indicator/entry/exit contract
can execute in the pinned environment.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


sys.path.insert(0, str(Path(__file__).resolve().parent))
from HedgeAdaptiveRegimeStrategy import HedgeAdaptiveRegimeStrategy


def main() -> None:
    strategy = HedgeAdaptiveRegimeStrategy({})
    close = np.r_[
        100 * np.exp(np.linspace(0, 0.35, 350)),
        142 * np.exp(np.linspace(0, -0.35, 350)),
    ]
    frame = pd.DataFrame(
        {
            "close": close,
            "open": close,
            "high": close * 1.001,
            "low": close * 0.999,
            "volume": 1.0,
        }
    )
    frame = strategy.populate_indicators(frame, {})
    frame = strategy.populate_entry_trend(frame, {})
    frame = strategy.populate_exit_trend(frame, {})
    type(strategy).validate_hedge_dataframe(frame)

    required = {
        "hedge_long_score",
        "hedge_short_score",
        "hedge_target_net_ratio",
        "hedge_confidence",
        "hedge_risk_scale",
        "hedge_allow_new_risk",
        "hedge_regime",
        "enter_long",
        "enter_short",
        "exit_long",
        "exit_short",
    }
    assert required <= set(frame), sorted(required - set(frame))
    assert frame.hedge_long_score.between(0, 1).all()
    assert frame.hedge_short_score.between(0, 1).all()
    assert frame.hedge_target_net_ratio.between(-0.35, 0.35).all()
    assert frame.enter_long.fillna(0).sum() > 0
    assert frame.enter_short.fillna(0).sum() > 0
    print(
        "HedgeAdaptiveRegimeStrategy contract: PASS "
        f"long_entries={int(frame.enter_long.fillna(0).sum())} "
        f"short_entries={int(frame.enter_short.fillna(0).sum())}"
    )


if __name__ == "__main__":
    main()
