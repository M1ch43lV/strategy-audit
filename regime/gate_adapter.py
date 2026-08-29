"""Entry-only regime gating installed around Freqtrade's strategy interface."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd


STATE_SET = {"BULL", "BEAR", "SIDEWAYS", "TRANSITION"}


def _states(config: dict, side: str, scope: str) -> set[str]:
    values = config.get(f"{side}_{scope}_states", sorted(STATE_SET))
    result = set(values)
    if not result.issubset(STATE_SET):
        raise ValueError(f"unknown {side} {scope} state: {sorted(result - STATE_SET)}")
    return result


class RegimeGate:
    def __init__(self, config: dict):
        self.config = config
        self.mode = config.get("mode", "ungated")
        if self.mode not in {"ungated", "btc", "btc_coin"}:
            raise ValueError(f"unknown regime gate mode: {self.mode}")
        self.daily = None
        if self.mode != "ungated":
            path = Path(config["daily_path"])
            daily = pd.read_csv(path, usecols=["date", "pair", "btc_regime", "coin_regime"])
            daily["date"] = pd.to_datetime(daily["date"], utc=True).dt.normalize()
            self.daily = daily.set_index(["pair", "date"]).sort_index()

    def mask(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        if self.mode == "ungated":
            return dataframe
        pair = metadata["pair"].split(":", 1)[0]
        dates = pd.to_datetime(dataframe["date"], utc=True).dt.normalize()
        key = pd.MultiIndex.from_arrays([[pair] * len(dates), dates], names=["pair", "date"])
        states = self.daily.reindex(key).reset_index(drop=True)
        result = dataframe.copy()
        for side, column in (("long", "enter_long"), ("short", "enter_short")):
            if column not in result.columns:
                continue
            allowed = states["btc_regime"].isin(_states(self.config, side, "btc"))
            if self.mode == "btc_coin":
                allowed &= states["coin_regime"].isin(_states(self.config, side, "coin"))
            result.loc[~allowed.to_numpy(), column] = 0
        return result


def install_from_environment() -> bool:
    """Wrap ``advise_entry`` once when REGIME_GATE_CONFIG names a JSON file."""
    config_path = os.environ.get("REGIME_GATE_CONFIG")
    if not config_path:
        return False
    config = json.loads(Path(config_path).read_text(encoding="utf-8-sig"))
    gate = RegimeGate(config)
    from freqtrade.strategy.interface import IStrategy
    if getattr(IStrategy.advise_entry, "_regime_gate_installed", False):
        return True
    original = IStrategy.advise_entry

    def advise_entry(self, dataframe, metadata):
        return gate.mask(original(self, dataframe, metadata), metadata)

    advise_entry._regime_gate_installed = True
    advise_entry._regime_gate_original = original
    IStrategy.advise_entry = advise_entry
    return True


def selftest() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "daily.csv"
        pd.DataFrame({
            "date": ["2024-01-01T00:00:00Z", "2024-01-02T00:00:00Z"],
            "pair": ["BTC/USDT", "BTC/USDT"],
            "btc_regime": ["BULL", "BEAR"],
            "coin_regime": ["BULL", "SIDEWAYS"],
        }).to_csv(path, index=False)
        source = pd.DataFrame({
            "date": ["2024-01-01T01:00:00Z", "2024-01-02T23:00:00Z"],
            "enter_long": [1, 1], "enter_short": [1, 1], "exit_long": [1, 1],
        })
        ungated = RegimeGate({"mode": "ungated"}).mask(source, {"pair": "BTC/USDT:USDT"})
        pd.testing.assert_frame_equal(source, ungated)
        gate = RegimeGate({"mode": "btc_coin", "daily_path": str(path),
                           "long_btc_states": ["BULL"], "long_coin_states": ["BULL"],
                           "short_btc_states": ["BEAR"],
                           "short_coin_states": ["SIDEWAYS"]})
        result = gate.mask(source, {"pair": "BTC/USDT:USDT"})
        assert result["enter_long"].tolist() == [1, 0]
        assert result["enter_short"].tolist() == [0, 1]
        assert result["exit_long"].tolist() == [1, 1]
    print("regime gate selftest: PASS")


if __name__ == "__main__":
    selftest()
