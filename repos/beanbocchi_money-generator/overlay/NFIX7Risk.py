"""
NFIX7Risk -- thin risk-overlay subclass of NostalgiaForInfinityX7.

Why this file exists
--------------------
Two risk changes needed to live somewhere that `git pull` from upstream
(iterativv/NostalgiaForInfinity) will never clobber:

  1. leverage 3.0 -> 2.0        -> done via "nfi_parameters" in user_data/config.json,
                                   because NFI whitelists those keys in NFI_SAFE_PARAMETERS.
  2. a per-pair cooldown        -> HAS to be a strategy attribute. This freqtrade version
                                   hard-rejects "protections" in the config file
                                   ("DEPRECATED: Setting 'protections' in the configuration
                                   is deprecated"), and NostalgiaForInfinityX7 does not
                                   define a `protections` property of its own.

Editing NostalgiaForInfinityX7.py directly would work but upstream touches that file in
almost every commit, so every future pull would conflict. Subclassing keeps the upstream
file pristine and byte-identical to origin/main.

Everything else -- every entry/exit signal, grinding, derisk, the doom stops -- is
inherited unchanged from NostalgiaForInfinityX7.
"""

import os
import sys

# The freqtrade resolver already inserts the strategy directory into sys.path while it
# imports this module, but make the parent import independent of that implementation
# detail.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from NostalgiaForInfinityX7 import NostalgiaForInfinityX7


class NFIX7Risk(NostalgiaForInfinityX7):
    @property
    def protections(self):
        """
        Per-pair cooldown once a pair has recently hurt the account.

        Fixes the single largest loss pattern in this bot's live history: re-entering
        the same collapsing pair within hours.
            ZEC   2026-06-04/05: #126 -7.28 USDT, then #131 -7.30 USDT
                                 (the pair alone erased 4.5 months of net profit)
            SIREN 2026-06-13:    #163 -3.93 USDT, then #165 -3.65 USDT, 89 min apart

        LowProfitPairs is used rather than StoplossGuard deliberately. StoplossGuard
        requires exit_reason to be one of freqtrade's native stops
        (stop_loss / trailing_stop_loss / stoploss_on_exchange / liquidation) AND
        close_profit < required_profit. NFI exits its doom stops through custom_exit,
        e.g. "exit_long_tc_stoploss_doom_m ( 143 )", so StoplossGuard would have caught
        only the 2 real liquidations out of the 12 disasters and missed all 10 doom
        stops. LowProfitPairs ignores exit_reason entirely and just sums close_profit
        per pair, so it sees them.

        trade_limit=2 (not 1) is deliberate. Replayed against the SIREN sequence:
            trade_limit=1 -> blocks the +0.37 winner AND the -3.65 doom   (+3.28 USDT)
            trade_limit=2 -> blocks only the -3.65 doom                   (+3.65 USDT)
        Requiring two closed trades whose summed profit is negative lets one unlucky
        small loss through but still catches the repeated-damage pattern.

        Replayed over the 208 closed trades in the live DB:
            post-blacklist universe (what the upstream update yields): +6.83 USDT
                -> blocks ZEC #131 (-7.30), sacrifices ZEC #130 (+0.46)
            full history: +9.30 USDT, catching both the ZEC and the SIREN second doom
        Caveat: that counterfactual cannot model the capital freed by a blocked trade,
        and it rests on n=2 doom events, so treat the parameters as reasonable rather
        than optimal.

        LowProfitPairs.global_stop() returns None, so this can only ever lock the
        offending pair -- it can never halt the whole bot.
        """
        return [
            {
                "method": "LowProfitPairs",
                "lookback_period": 2880,  # 48h window of closed trades for the pair
                "trade_limit": 2,  # need >= 2 closed trades in that window
                "stop_duration": 720,  # lock the pair for 12h
                "required_profit": 0.0,  # trigger when their summed profit is negative
            }
        ]
