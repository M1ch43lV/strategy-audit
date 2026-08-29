"""Deterministic daily features used by the preregistered regime models."""
from __future__ import annotations

import numpy as np
import pandas as pd
import talib


def wilder_dmi(frame: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Return the audit runtime's pinned TA-Lib Wilder +DI, -DI and ADX."""
    high = frame["high"].astype(float)
    low = frame["low"].astype(float)
    close = frame["close"].astype(float)
    plus_di = pd.Series(talib.PLUS_DI(high, low, close, timeperiod=period), index=frame.index)
    minus_di = pd.Series(talib.MINUS_DI(high, low, close, timeperiod=period), index=frame.index)
    adx = pd.Series(talib.ADX(high, low, close, timeperiod=period), index=frame.index)
    return pd.DataFrame({"plus_di": plus_di, "minus_di": minus_di, "adx": adx})


def signed_efficiency_ratio(close: pd.Series, period: int = 30) -> pd.Series:
    movement = close.astype(float).diff(period)
    path = close.astype(float).diff().abs().rolling(period, min_periods=period).sum()
    return movement / path.replace(0.0, np.nan)


def classify_dmi(plus_di: pd.Series, minus_di: pd.Series, adx: pd.Series) -> pd.Series:
    values = np.select(
        [adx.ge(25.0) & plus_di.gt(minus_di),
         adx.ge(25.0) & minus_di.gt(plus_di),
         adx.lt(20.0),
         adx.ge(20.0) & adx.lt(25.0)],
        ["BULL", "BEAR", "SIDEWAYS", "TRANSITION"],
        default="WARMUP",
    )
    return pd.Series(values, index=adx.index, dtype="object")


def asset_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Calculate close-of-day features, then lag them one full UTC day."""
    ordered = frame.sort_values("date").reset_index(drop=True).copy()
    dmi = wilder_dmi(ordered)
    close = ordered["close"].astype(float)
    daily_log = np.log(close / close.shift())
    raw = pd.DataFrame({
        "plus_di": dmi["plus_di"],
        "minus_di": dmi["minus_di"],
        "adx": dmi["adx"],
        "di_spread": dmi["plus_di"] - dmi["minus_di"],
        "di_spread_normalized": ((dmi["plus_di"] - dmi["minus_di"]) /
                                 (dmi["plus_di"] + dmi["minus_di"]).replace(0.0, np.nan)),
        "ser_30": signed_efficiency_ratio(close, 30),
        "return_30d": close.pct_change(30, fill_method=None),
        "return_90d": close.pct_change(90, fill_method=None),
        "realized_vol_30d": daily_log.rolling(30, min_periods=30).std(ddof=1) * np.sqrt(365.0),
    })
    raw["regime"] = classify_dmi(raw["plus_di"], raw["minus_di"], raw["adx"])
    # A row dated D is the candle opening at D and completing at D+1.  Shifting
    # once means the state attached to date D uses only the candle completed at D.
    lagged = raw.shift(1)
    lagged["regime"] = lagged["regime"].fillna("WARMUP")
    return pd.concat([ordered[["date", "close"]], lagged], axis=1)
