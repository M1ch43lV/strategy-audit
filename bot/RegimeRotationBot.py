# -*- coding: utf-8 -*-
"""Regime rotation bot: one strategy per ADX market phase, Buy-and-Hold in the BTC uptrend.

Built from the phase portfolio of the "Regime-Spezialisten" page. The phase of a pair on a day is
decided from the daily Wilder DMI/ADX(14), the same rule and thresholds as `regime/features.py`
(ADX >= 25 and +DI > -DI is BULL, ADX >= 25 and -DI > +DI is BEAR, ADX < 20 is SIDEWAYS, 20 <= ADX
< 25 is TRANSITION), and the state of day D comes from the candle that closed on day D-1.

    BTC regime BULL                 Buy-and-Hold on every pair (1x leverage, `hold_leverage` for a test)
    BTC regime BEAR                 EI3v2_tag_cofi_green            (or a 1x short hold, `bear_mode`)
    otherwise, coin regime SIDEWAYS Ichimoku_v31 (Heikin-Ashi Ichimoku on 4h)
    otherwise, coin regime TRANSITION BuyOrDie (HMA20 cross)
    otherwise                       flat (no new trade)

A trade keeps the exit logic of the component that opened it (`enter_tag`). The one exception is
the priority of the BTC phases: when BTC turns BULL or BEAR, positions that belong to another
component are closed and the phase's own component takes the pair over (`phase_takeover`).
Hold positions end when BTC leaves BULL.

Variants (`RegimeRotationBotV2N1`, `RegimeRotationBotV2`, and the older test subclasses at the end of the file) change the option
per phase (`bear_mode`, `side_mode`, `trans_mode`) and the days a new state must hold (`phase_confirm_days`). The rule and the
result of each is `PIPELINE_EXTENSIONS.md`, Part 4.

Every component is a port of the strategy in `repos/`, checked against the original's own
`populate_*` output by `bot/check_ports.py`. Known deviations from the originals: the protections of
EI3v2 are not carried over (they are global and would also lock the hold; a backtest ignores protections
unless it is started with --enable-protections, so no backtest of the original had them either), the 1h/4h informative
signals are available at 5m granularity instead of 1h, and the component exits run through
`custom_exit`/`custom_stoploss` at the 5m candle.

Backtest: base timeframe 5m, `--timeframe-detail 1m`, futures, isolated, fee 0.1 % per side.
"""
from __future__ import annotations

import logging
from datetime import datetime

import numpy as np
import pandas as pd
import talib
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
import technical.indicators as ftt
from pandas import DataFrame
from technical.indicators import ichimoku

from freqtrade.enums import CandleType
from freqtrade.persistence import Trade
from freqtrade.strategy import (IStrategy, merge_informative_pair, stoploss_from_absolute,
                                stoploss_from_open)

logger = logging.getLogger(__name__)

ADX_TREND = 25.0
ADX_SIDEWAYS = 20.0
BASE_MINUTES = 5


def daily_regime(daily: DataFrame) -> DataFrame:
    """Phase per day, as regime/features.asset_features: classify on the closed candle, lag one day."""
    high, low, close = (daily[c].astype(float) for c in ("high", "low", "close"))
    plus_di = pd.Series(talib.PLUS_DI(high, low, close, timeperiod=14), index=daily.index)
    minus_di = pd.Series(talib.MINUS_DI(high, low, close, timeperiod=14), index=daily.index)
    adx = pd.Series(talib.ADX(high, low, close, timeperiod=14), index=daily.index)
    state = np.select(
        [adx.ge(ADX_TREND) & plus_di.gt(minus_di), adx.ge(ADX_TREND) & minus_di.gt(plus_di),
         adx.lt(ADX_SIDEWAYS), adx.ge(ADX_SIDEWAYS) & adx.lt(ADX_TREND)],
        ["BULL", "BEAR", "SIDEWAYS", "TRANSITION"], default="WARMUP")
    out = DataFrame({"date": daily["date"], "regime": pd.Series(state, index=daily.index).shift(1)})
    out["regime"] = out["regime"].fillna("WARMUP")
    return out


def confirm_regime(states: pd.Series, days: int) -> pd.Series:
    """A change of state is accepted only after the new raw state has held for `days` consecutive days.

    Bot logic on top of the frozen labels; the labels themselves are not touched. `days` = 1 returns the input."""
    if days <= 1:
        return states
    raw = states.to_numpy(dtype=object)
    out = raw.copy()
    current = raw[0]
    for i in range(len(raw)):
        if i >= days - 1 and all(raw[i - k] == raw[i] for k in range(days)):
            current = raw[i]
        out[i] = current
    return pd.Series(out, index=states.index)


def ewo(dataframe: DataFrame, ema_length: int = 5, ema2_length: int = 3):
    ema1 = ta.EMA(dataframe, timeperiod=ema_length)
    ema2 = ta.EMA(dataframe, timeperiod=ema2_length)
    return (ema1 - ema2) / dataframe["close"] * 100


class RegimeRotationBot(IStrategy):
    INTERFACE_VERSION = 3
    can_short = True
    timeframe = "5m"
    # Base candles. Freqtrade refuses more than 5x the exchange's per-call limit (2494 here). What needs more
    # history than that, the daily ADX and the 4h Ichimoku, reads informative frames, which the data provider
    # returns in full (bot/check_ports.py and the backtest log show where they start).
    startup_candle_count = 2400
    process_only_new_candles = True

    minimal_roi = {"0": 100}
    stoploss = -0.99
    use_custom_stoploss = True
    trailing_stop = False
    # Freqtrade only asks custom_exit while this is True; exit_long/exit_short stay zero, the exits are custom.
    use_exit_signal = True
    ignore_roi_if_entry_signal = True

    # test switches, overridden in the subclasses below
    hold_leverage = 1.0
    bear_mode = "ei3v2"          # "ei3v2", "short_hold" or "cash" (cash: everything is closed when BTC turns BEAR)
    bear_regime = "btc"          # which regime decides the downtrend phase: "btc" or "coin"
    side_mode = "ichimoku"       # coin SIDEWAYS: "ichimoku" or "cash"
    trans_mode = "buyordie"      # coin TRANSITION: "buyordie" or "cash"
    phase_confirm_days = 1       # days a new raw state must hold before the bot follows it (1 = no confirmation)

    # EI3v2_tag_cofi_green, the values its `buy_params`/`sell_params` load
    ei = {"ma_buy": 12, "ma_sell": 22, "rsi_buy": 58, "ewo_high": 3.001, "ewo_low": -10.289,
          "low_offset": 0.987, "high_offset": 1.014, "high_offset_2": 1.01,
          "lambo_ema_factor": 0.981, "lambo_rsi_4": 44, "lambo_rsi_14": 39,
          "cofi_ema": 0.98, "cofi_fastk": 22, "cofi_fastd": 20, "cofi_adx": 20, "cofi_ewo_high": 4.179,
          "profit_offset": 0.01, "trail_offset": 0.012, "trail_positive": 0.001,
          "unclog_loss": -0.04, "unclog_days": 4}

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._cache: dict = {}

    # ------------------------------------------------------------------ data
    def _btc(self) -> str:
        return "BTC/USDT:USDT" if self.config.get("trading_mode") == "futures" else "BTC/USDT"

    @staticmethod
    def _spot(pair: str) -> str:
        return pair.split(":")[0]

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        wanted = [(p, "4h") for p in pairs]
        # The regime reads the coin's own SPOT daily candles, as the frozen engine does
        # (regime/regime_engine.py); the futures candles differ enough to move about 6 % of the days.
        wanted += [(self._spot(p), "1d", CandleType.SPOT) for p in pairs]
        btc = self._btc()
        return wanted + [(self._spot(btc), "1d", CandleType.SPOT), (btc, "1h")]

    # ------------------------------------------------------------------ indicators
    def _merge_regime(self, dataframe: DataFrame, prefix: str, source: str) -> DataFrame:
        """Attach the day's phase to every 5m candle of that day. The daily state already uses the
        candle that closed the day before, so no further shift is applied."""
        raw = self.dp.get_pair_dataframe(pair=self._spot(source), timeframe="1d", candle_type="spot")
        logger.info("regime source %s starts %s, %d daily candles", self._spot(source), raw["date"].iloc[0], len(raw))
        daily = daily_regime(raw)
        daily["regime"] = confirm_regime(daily["regime"], self.phase_confirm_days)
        daily = daily.rename(columns={"regime": prefix + "_regime"})
        left = dataframe[["date"]].copy()
        unit = left["date"].dtype
        daily["date"] = daily["date"].astype(unit)
        # A day without its own daily candle has no state: XMR's spot candles end with the delisting on
        # 2024-02-20, and the last state must not be carried on for the years after.
        merged = pd.merge_asof(left, daily, on="date", direction="backward",
                               tolerance=pd.Timedelta(hours=23, minutes=59))
        dataframe[prefix + "_regime"] = merged[prefix + "_regime"].fillna("WARMUP").to_numpy()
        return dataframe

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata["pair"]
        dataframe = self._merge_regime(dataframe, "btc", self._btc())
        dataframe = self._merge_regime(dataframe, "coin", pair)
        btc, coin = dataframe["btc_regime"], dataframe["coin_regime"]
        # The uptrend is always the BTC regime's. The downtrend follows `bear_regime`: either the BTC regime
        # (it takes priority over the coin's own states), or the coin's own downtrend.
        bear = btc.eq("BEAR") if self.bear_regime == "btc" else coin.eq("BEAR")
        dataframe["phase"] = np.select(
            [btc.eq("BULL"), bear, coin.eq("SIDEWAYS"), coin.eq("TRANSITION")],
            ["hold", "bear", "side", "trans"], default="flat")

        dataframe = self._ei3v2_indicators(dataframe)
        dataframe = self._ichimoku_indicators(dataframe, pair)
        dataframe = self._buyordie_indicators(dataframe)

        dates = dataframe["date"].tolist()
        self._cache[pair] = dict(zip(dates, zip(dataframe["phase"], dataframe["ei_sell"], dataframe["ich_sell"])))
        return dataframe

    # -- EI3v2_tag_cofi_green
    def _ei3v2_indicators(self, dataframe: DataFrame) -> DataFrame:
        p = self.ei
        btc_1h = self.dp.get_pair_dataframe(self._btc(), "1h")
        btc_1h["rsi_8"] = ta.RSI(btc_1h, timeperiod=8)
        btc_1h = btc_1h.rename(columns={c: "btc_" + c for c in btc_1h.columns
                                        if c not in ("date", "open", "high", "low", "close", "volume")})
        dataframe = merge_informative_pair(dataframe, btc_1h, self.timeframe, "1h", ffill=True)
        dataframe = dataframe.drop(columns=dataframe.columns.intersection(
            [f"{c}_1h" for c in ("date", "open", "high", "low", "close", "volume")]))

        dataframe["ma_buy"] = ta.EMA(dataframe, timeperiod=p["ma_buy"])
        dataframe["ma_sell"] = ta.EMA(dataframe, timeperiod=p["ma_sell"])
        dataframe["hma_50"] = qtpylib.hull_moving_average(dataframe["close"], window=50)
        dataframe["EWO"] = ewo(dataframe, 50, 200)
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        dataframe["rsi_fast"] = ta.RSI(dataframe, timeperiod=4)
        dataframe["rsi_slow"] = ta.RSI(dataframe, timeperiod=20)
        dataframe["ema_14"] = ta.EMA(dataframe, timeperiod=14)
        dataframe["rsi_4"] = ta.RSI(dataframe, timeperiod=4)
        dataframe["rsi_14"] = ta.RSI(dataframe, timeperiod=14)
        stoch = ta.STOCHF(dataframe, 5, 3, 0, 3, 0)
        dataframe["fastd"], dataframe["fastk"] = stoch["fastd"], stoch["fastk"]
        dataframe["adx"] = ta.ADX(dataframe)
        dataframe["ema_8"] = ta.EMA(dataframe, timeperiod=8)
        # pump and dump protection, 5m specific as in the original
        df36h, df24h = dataframe.copy().shift(432), dataframe.copy().shift(288)
        dataframe["volume_mean_short"] = dataframe["volume"].rolling(4).mean()
        dataframe["volume_mean_long"] = df24h["volume"].rolling(48).mean()
        pnd = dataframe["volume_mean_short"] / dataframe["volume_mean_long"] > 5.0

        lambo2 = ((dataframe["close"] < dataframe["ema_14"] * p["lambo_ema_factor"])
                  & (dataframe["rsi_4"] < p["lambo_rsi_4"]) & (dataframe["rsi_14"] < p["lambo_rsi_14"]))
        below_offsets = ((dataframe["close"] < dataframe["ma_buy"] * p["low_offset"])
                         & (dataframe["volume"] > 0)
                         & (dataframe["close"] < dataframe["ma_sell"] * p["high_offset"]))
        buy1 = (dataframe["rsi_fast"] < 35) & below_offsets & (dataframe["EWO"] > p["ewo_high"]) & (dataframe["rsi"] < p["rsi_buy"])
        buy2 = (dataframe["rsi_fast"] < 35) & below_offsets & (dataframe["EWO"] < p["ewo_low"])
        cofi = ((dataframe["open"] < dataframe["ema_8"] * p["cofi_ema"])
                & qtpylib.crossed_above(dataframe["fastk"], dataframe["fastd"])
                & (dataframe["fastk"] < p["cofi_fastk"]) & (dataframe["fastd"] < p["cofi_fastd"])
                & (dataframe["adx"] > p["cofi_adx"]) & (dataframe["EWO"] > p["cofi_ewo_high"]))
        raw = lambo2 | buy1 | buy2 | cofi
        dataframe["ei_buy"] = (raw & ~pnd & ~(dataframe["btc_rsi_8_1h"] < 35.0)).astype(int)

        sell_a = ((dataframe["close"] > dataframe["hma_50"])
                  & (dataframe["close"] > dataframe["ma_sell"] * p["high_offset_2"])
                  & (dataframe["rsi"] > 50) & (dataframe["volume"] > 0)
                  & (dataframe["rsi_fast"] > dataframe["rsi_slow"]))
        sell_b = ((dataframe["close"] < dataframe["hma_50"])
                  & (dataframe["close"] > dataframe["ma_sell"] * p["high_offset"])
                  & (dataframe["volume"] > 0) & (dataframe["rsi_fast"] > dataframe["rsi_slow"]))
        dataframe["ei_sell"] = (sell_a | sell_b).astype(int)
        return dataframe

    # -- Ichimoku_v31 (Heikin-Ashi Ichimoku on 4h)
    def _ichimoku_indicators(self, dataframe: DataFrame, pair: str) -> DataFrame:
        inf = self.dp.get_pair_dataframe(pair=pair, timeframe="4h")
        heikin = qtpylib.heikinashi(inf)
        inf["ha_close"] = heikin["close"]
        cloud = ichimoku(heikin, conversion_line_period=20, base_line_periods=60, laggin_span=120, displacement=30)
        inf["senkou_a"], inf["senkou_b"] = cloud["senkou_span_a"], cloud["senkou_span_b"]
        inf["cloud_green"], inf["cloud_red"] = cloud["cloud_green"], cloud["cloud_red"]
        # the crossing is an event of the 4h series; it becomes visible when the 4h candle has closed
        cross_a = qtpylib.crossed_above(inf["ha_close"], inf["senkou_a"]) & (inf["ha_close"].shift() < inf["senkou_a"]) & (inf["cloud_green"] == True)  # noqa: E712
        cross_b = qtpylib.crossed_above(inf["ha_close"], inf["senkou_b"]) & (inf["ha_close"].shift() < inf["senkou_b"]) & (inf["cloud_red"] == True)  # noqa: E712
        inf["ich_buy"] = (cross_a | cross_b).astype(int)
        inf["ich_sell"] = ((inf["ha_close"] < inf["senkou_a"]) | (inf["ha_close"] < inf["senkou_b"])).astype(int)
        events = inf[["date", "ich_buy"]]
        state = inf[["date", "ich_sell"]]
        dataframe = merge_informative_pair(dataframe, events, self.timeframe, "4h", ffill=False)
        dataframe = merge_informative_pair(dataframe, state, self.timeframe, "4h", ffill=True)
        dataframe["ich_buy"] = dataframe["ich_buy_4h"].fillna(0).astype(int)
        dataframe["ich_sell"] = dataframe["ich_sell_4h"].fillna(0).astype(int)
        return dataframe.drop(columns=["ich_buy_4h", "ich_sell_4h"])

    # -- BuyOrDie (HMA20 cross)
    def _buyordie_indicators(self, dataframe: DataFrame) -> DataFrame:
        hma = qtpylib.hull_moving_average(dataframe["close"], window=20)
        close_prev, hma_prev = dataframe["close"].shift(2), hma.shift(2)
        close_curr, hma_curr = dataframe["close"].shift(1), hma.shift(1)
        dataframe["bod_buy"] = ((close_curr > hma_curr) & (close_prev < hma_prev)).astype(int)
        return dataframe

    # ------------------------------------------------------------------ entries
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        phase = dataframe["phase"]
        dataframe["enter_long"] = 0
        dataframe["enter_short"] = 0
        dataframe["enter_tag"] = ""

        def enter(mask, side, tag):
            dataframe.loc[mask, side] = 1
            dataframe.loc[mask, "enter_tag"] = tag

        enter(phase.eq("hold"), "enter_long", "hold")
        if self.bear_mode == "short_hold":
            enter(phase.eq("bear"), "enter_short", "hold_short")
        else:
            if self.bear_mode == "ei3v2":
                enter(phase.eq("bear") & dataframe["ei_buy"].eq(1), "enter_long", "ei3v2")
        if self.side_mode == "ichimoku":
            enter(phase.eq("side") & dataframe["ich_buy"].eq(1), "enter_long", "ichimoku")
        if self.trans_mode == "buyordie":
            enter(phase.eq("trans") & dataframe["bod_buy"].eq(1), "enter_long", "buyordie")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["exit_long"] = 0
        dataframe["exit_short"] = 0
        return dataframe

    def leverage(self, pair: str, current_time: datetime, current_rate: float, proposed_leverage: float,
                 max_leverage: float, entry_tag: str | None, side: str, **kwargs) -> float:
        wanted = self.hold_leverage if entry_tag == "hold" else 1.0
        return float(min(wanted, max_leverage))

    # ------------------------------------------------------------------ exits
    def _signals(self, pair: str, current_time: datetime):
        """(phase, ei_sell, ich_sell) of the last closed 5m candle before `current_time`."""
        if self.dp.runmode.value in ("backtest", "hyperopt"):
            key = pd.Timestamp(current_time).floor("%dmin" % BASE_MINUTES) - pd.Timedelta(minutes=BASE_MINUTES)
            return self._cache.get(pair, {}).get(key)
        frame, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if frame.empty:
            return None
        row = frame.iloc[-1]
        return row["phase"], row["ei_sell"], row["ich_sell"]

    def _owner(self, phase: str) -> str | None:
        if phase == "hold":
            return "hold"
        if phase == "bear":
            return {"short_hold": "hold_short", "cash": "cash"}.get(self.bear_mode, "ei3v2")
        return None

    def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                    current_profit: float, **kwargs):
        signals = self._signals(pair, current_time)
        if signals is None:
            return None
        phase, ei_sell, ich_sell = signals
        tag = trade.enter_tag
        if tag == "hold":
            return "phase_end" if phase != "hold" else None
        if tag == "hold_short":
            return "phase_end" if phase != "bear" else None
        owner = self._owner(phase)
        if owner is not None and tag != owner:
            return "phase_takeover"
        if tag == "ei3v2":
            p = self.ei
            if ei_sell and current_profit > p["profit_offset"]:
                return "ei_sell"
            if current_profit < p["unclog_loss"] and (current_time - trade.open_date_utc).days >= p["unclog_days"]:
                return "unclog"
        elif tag == "ichimoku" and ich_sell:
            return "ich_cloud"
        return None

    def custom_stoploss(self, pair: str, trade: Trade, current_time: datetime, current_rate: float,
                        current_profit: float, after_fill: bool, **kwargs) -> float | None:
        tag = trade.enter_tag
        if tag == "buyordie":
            # stoploss -2 % from the open rate; the trailing (+36.4 % offset, 33.2 % distance) is kept
            if trade.calc_profit_ratio(trade.max_rate) >= 0.364:
                return stoploss_from_absolute(trade.max_rate * (1 - 0.332), current_rate, False, trade.leverage)
            return stoploss_from_open(-0.02, current_profit, False, trade.leverage)
        if tag == "ei3v2":
            p = self.ei
            if trade.calc_profit_ratio(trade.max_rate) >= p["trail_offset"]:
                return stoploss_from_absolute(trade.max_rate * (1 - p["trail_positive"]), current_rate, False, trade.leverage)
        return None


class RegimeRotationBot2x(RegimeRotationBot):
    """Test: the uptrend hold with 2x leverage."""
    hold_leverage = 2.0


class RegimeRotationBotCoinBear(RegimeRotationBot):
    """Test: the downtrend phase (EI3v2) follows the coin's own regime instead of BTC's."""
    bear_regime = "coin"


class RegimeRotationBotShort(RegimeRotationBot):
    """Test: a 1x short hold in the BTC downtrend instead of EI3v2."""
    bear_mode = "short_hold"


class RegimeRotationBotV2N1(RegimeRotationBot):
    """V2 without the phase confirmation (decomposition only, `PIPELINE_EXTENSIONS.md` Part 4.2 point 3).

    The component choice is the result of `bot/phase_choice.py` on the discovery window (`results/regime/rotation_bot/
    phase_choice.json`): BTC bear and coin TRANSITION go to cash, coin SIDEWAYS keeps Ichimoku."""
    bear_mode = "cash"
    trans_mode = "cash"
    side_mode = "ichimoku"
    phase_confirm_days = 1


class RegimeRotationBotV2(RegimeRotationBotV2N1):
    """V2: the component choice above, and a change of phase is followed after 2 consecutive days."""
    phase_confirm_days = 2
