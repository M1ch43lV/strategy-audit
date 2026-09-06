"""Entry-only regime gating installed around Freqtrade's strategy interface."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd


STATE_SET = {"BULL", "BEAR", "SIDEWAYS", "TRANSITION"}


def _states(config: dict, side: str, scope: str) -> set[str]:
    key = f"{side}_{scope}_states"
    if key not in config:
        raise ValueError(f"missing explicit regime gate setting: {key}")
    values = config[key]
    if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
        raise ValueError(f"{key} must be a list of regime-state strings")
    if len(values) != len(set(values)):
        raise ValueError(f"{key} contains duplicate states")
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
        self.btc_daily = None
        self.coin_daily = None
        self.allowed = {}
        if self.mode != "ungated":
            path = Path(config["daily_path"])
            daily = pd.read_csv(path, usecols=["date", "pair", "btc_regime", "coin_regime"])
            daily["date"] = pd.to_datetime(daily["date"], utc=True).dt.normalize()
            if daily.duplicated(["pair", "date"]).any():
                raise ValueError("regime daily data contains duplicate pair/date keys")
            inconsistent = daily.groupby("date")["btc_regime"].nunique(dropna=False).gt(1)
            if inconsistent.any():
                raise ValueError("regime daily data contains inconsistent BTC states for one date")
            # BTC is a global state.  It must remain available even when the
            # traded coin has no local row (for example XMR after delisting).
            # Model 2 separately looks up the pair-local state and therefore
            # still fails closed when that local evidence is absent.
            self.btc_daily = (daily.drop_duplicates("date").set_index("date")["btc_regime"]
                              .sort_index())
            self.coin_daily = daily.set_index(["pair", "date"])["coin_regime"].sort_index()
            for side in ("long", "short"):
                self.allowed[(side, "btc")] = _states(config, side, "btc")
                if self.mode == "btc_coin":
                    self.allowed[(side, "coin")] = _states(config, side, "coin")

    def mask(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        if self.mode == "ungated":
            return dataframe
        pair = metadata["pair"].split(":", 1)[0]
        dates = pd.to_datetime(dataframe["date"], utc=True).dt.normalize()
        btc_states = self.btc_daily.reindex(dates).reset_index(drop=True)
        key = pd.MultiIndex.from_arrays([[pair] * len(dates), dates], names=["pair", "date"])
        coin_states = self.coin_daily.reindex(key).reset_index(drop=True)
        result = dataframe.copy()
        for side, column in (("long", "enter_long"), ("short", "enter_short")):
            if column not in result.columns:
                continue
            allowed = btc_states.isin(self.allowed[(side, "btc")])
            if self.mode == "btc_coin":
                allowed &= coin_states.isin(self.allowed[(side, "coin")])
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

        # BTC-only gating is global and survives a missing pair-local row;
        # BTC+coin gating has no local evidence and therefore fails closed.
        missing_pair = source.iloc[:1].copy()
        btc_gate = RegimeGate({"mode": "btc", "daily_path": str(path),
                               "long_btc_states": ["BULL"],
                               "short_btc_states": []})
        assert btc_gate.mask(missing_pair, {"pair": "XMR/USDT"})["enter_long"].tolist() == [1]
        local_gate = RegimeGate({"mode": "btc_coin", "daily_path": str(path),
                                 "long_btc_states": ["BULL"],
                                 "short_btc_states": [],
                                 "long_coin_states": ["BULL"],
                                 "short_coin_states": []})
        assert local_gate.mask(missing_pair, {"pair": "XMR/USDT"})["enter_long"].tolist() == [0]
        try:
            RegimeGate({"mode": "btc", "daily_path": str(path),
                        "long_btc_states": ["BULL"]})
        except ValueError as exc:
            assert "short_btc_states" in str(exc)
        else:
            raise AssertionError("gated configs must never default an omitted side to all states")
    print("regime gate selftest: PASS")


if __name__ == "__main__":
    selftest()
