"""Import-only stand-in for `tvDatafeed`, for strategies that fetch from
TradingView in live mode but read the author's own shipped CSV in a backtest.

`tvDatafeed` is not on PyPI (it installs from a GitHub URL) and it works by
querying TradingView at runtime, so it is not a dependency this audit can
supply and then honestly call the author's own. Two strategies here do not
need it at all in the mode we run them in:

- `CME` guards its download with `if self.dp.runmode.value in ('live',
  'dry_run')` and otherwise reads `cme_data/BTC1_weekly_data.csv`.
- `QuatreMousquetaires` does the same with its four TradingView series.

Both fail before that choice is ever made, on an unconditional top-level
`from tvDatafeed import TvDatafeed, Interval`. This module satisfies exactly
that import and nothing else.

It deliberately does NOT fetch, cache or fabricate market data. `Interval`
carries the two members these strategies name, as plain strings, because
they are only passed back into `get_hist()`. `TvDatafeed` constructs (some
strategies instantiate it at module scope, before any mode is known) but
every data call raises, so a strategy that really does need the feed during
a backtest - `kac_index_v1`/`kac_index_v2` call `get_hist()` from their
indicator path regardless of mode - fails loudly here instead of silently
measuring against data this stub invented. That failure is the correct
outcome for them, and it is what makes this stub falsifiable rather than a
substitute for the real package.
"""


class Interval(object):
    in_daily = "in_daily"
    in_weekly = "in_weekly"


class TvDatafeed(object):
    def __init__(self, *args, **kwargs):
        pass

    def get_hist(self, *args, **kwargs):
        raise RuntimeError(
            "tvDatafeed is stubbed for this audit: it fetches from TradingView "
            "at runtime and is not installable as a declared dependency. A "
            "strategy reaching this call needs live feed data that neither its "
            "author shipped nor this runtime can supply - see "
            "repair/compat_helpers/tvdatafeed_stub/tvDatafeed/__init__.py")

    def search_symbol(self, *args, **kwargs):
        raise RuntimeError("tvDatafeed is stubbed for this audit; see get_hist")
