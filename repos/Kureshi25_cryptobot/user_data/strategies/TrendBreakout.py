"""
TrendBreakout - a deliberately plain Donchian-channel trend follower.

Design rule: as few knobs as possible. Every extra parameter is another way to
fool yourself in a backtest. The mechanism (breakout + regime filter + channel
exit) is the classic turtle setup and is documented to have worked across
decades and asset classes, which is a much better prior than anything tuned to
fit the last four years of crypto.

Deliberate anti-lookahead choice: both Donchian channels are .shift(1), so the
breakout is measured against a channel that EXCLUDES the current candle.
Without that shift, "close >= rolling max including today" is near-tautological
at new highs and the backtest prints beautiful, fictional returns.
"""
from datetime import datetime
import numpy as np
import talib.abstract as ta
from pandas import DataFrame
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter


class TrendBreakout(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = "1d"
    can_short = False

    # Exits are driven by the channel, not by a profit target.
    # Letting winners run is the entire source of edge in trend following.
    minimal_roi = {"0": 100}

    # Hard disaster stop only. The real exit is the Donchian low.
    stoploss = -0.35
    trailing_stop = False
    use_custom_stoploss = True

    process_only_new_candles = True
    startup_candle_count = 220

    order_types = {
        "entry": "limit", "exit": "limit",
        "stoploss": "market", "stoploss_on_exchange": False,
    }

    # --- the only tunable knobs, kept few on purpose ---
    entry_lookback = IntParameter(15, 60, default=20, space="buy", optimize=True)
    exit_lookback = IntParameter(5, 30, default=10, space="sell", optimize=True)
    atr_stop_mult = DecimalParameter(1.5, 10.0, default=3.0, decimals=1,
                                     space="sell", optimize=True)

    # ------------------------------------------------------------------
    # Risk protections. These are circuit breakers, not profit tuning:
    # they halt trading when the bot is clearly in trouble, which matters
    # far more on a small account than any entry rule does.
    # On the 1d timeframe, one "candle" is one day.
    # ------------------------------------------------------------------
    @property
    def protections(self):
        return [
            # Do not re-enter the same pair the moment it closes.
            {"method": "CooldownPeriod", "stop_duration_candles": 2},
            # Account-level brake: 20% drawdown halts everything for 10 days.
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 60,
                "trade_limit": 8,
                "stop_duration_candles": 10,
                "max_allowed_drawdown": 0.20,
            },
            # Three stoplosses inside 30 days means conditions changed. Stand down.
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 30,
                "trade_limit": 3,
                "stop_duration_candles": 10,
                "only_per_pair": False,
            },
            # Retire pairs that keep bleeding rather than trading them forever.
            {
                "method": "LowProfitPairs",
                "lookback_period_candles": 90,
                "trade_limit": 4,
                "stop_duration_candles": 20,
                "required_profit": -0.05,
            },
        ]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Donchian channels, shifted so the current bar cannot see itself.
        for v in self.entry_lookback.range:
            dataframe[f"dc_high_{v}"] = dataframe["high"].rolling(v).max().shift(1)
        for v in self.exit_lookback.range:
            dataframe[f"dc_low_{v}"] = dataframe["low"].rolling(v).min().shift(1)

        # Regime filter: only take longs while the slow trend is up.
        dataframe["ema200"] = ta.EMA(dataframe, timeperiod=200)

        # ATR drives the trailing stop distance (volatility-adaptive).
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dc_high = dataframe[f"dc_high_{self.entry_lookback.value}"]
        dataframe.loc[
            (dataframe["close"] > dc_high)          # breakout above prior channel
            & (dataframe["close"] > dataframe["ema200"])   # ...in an uptrend only
            & (dataframe["volume"] > 0),
            ["enter_long", "enter_tag"],
        ] = (1, "donchian_break")
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dc_low = dataframe[f"dc_low_{self.exit_lookback.value}"]
        dataframe.loc[
            (dataframe["close"] < dc_low) & (dataframe["volume"] > 0),
            ["exit_long", "exit_tag"],
        ] = (1, "channel_exit")
        return dataframe

    def custom_stoploss(self, pair: str, trade, current_time: datetime,
                        current_rate: float, current_profit: float,
                        after_fill: bool, **kwargs) -> float:
        """ATR trailing stop: ratchets up with price, never loosens."""
        df, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df is None or len(df) == 0:
            return self.stoploss
        atr = df["atr"].iat[-1]
        if not np.isfinite(atr) or current_rate <= 0:
            return self.stoploss
        # Distance below current price, as a negative ratio.
        dist = (atr * float(self.atr_stop_mult.value)) / current_rate
        return max(-abs(dist), self.stoploss)
