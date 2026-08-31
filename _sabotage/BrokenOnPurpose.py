from freqtrade.strategy import IStrategy
import this_module_does_not_exist_xyz
class BrokenOnPurpose(IStrategy):
    timeframe = '1h'
    stoploss = -0.10
    def populate_indicators(self, d, m): return d
    def populate_entry_trend(self, d, m): return d
    def populate_exit_trend(self, d, m): return d
