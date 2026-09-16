"""
AdaptiveRegimeLong - AdaptiveRegime with the short side switched off.

Reason for existing: on the full backtest the parent's arms split like this --

    trend_long    56 trades   +43.2%
    trend_short   64 trades   -41.5%

The long arm carried a real profit and the short arm gave back almost exactly
the same amount. That asymmetry is not a quirk of one window; it is what you
would expect from an asset class with strong positive drift, where shorting
means standing in front of that drift and paying funding for the privilege.

This variant tests whether dropping the short side keeps the profit. If it does
NOT, the short arm was providing a hedge that mattered and should stay.
"""
from pandas import DataFrame

from AdaptiveRegime import AdaptiveRegime


class AdaptiveRegimeLong(AdaptiveRegime):
    can_short = False

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = super().populate_entry_trend(dataframe, metadata)
        # Strip every short signal the parent produced.
        if "enter_short" in dataframe.columns:
            dataframe["enter_short"] = 0
        return dataframe
