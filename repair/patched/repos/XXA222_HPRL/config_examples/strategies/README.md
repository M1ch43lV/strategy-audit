# HedgeAdaptiveRegimeStrategy audit overlay

The upstream source is recorded unchanged at
`repos/XXA222_HPRL/config_examples/strategies/HedgeAdaptiveRegimeStrategy.py`.
This executable overlay changes precisely one import because
`freqtrade.strategy.hedge.HedgeStrategyMixin` exists only in XXA222's private
Freqtrade fork.

`xxa222_hedge_audit_shim.py` implements only that mixin's passive Hedge
signal-column validation contract. It has no indicator, signal, entry, exit,
stake, leverage, order, exchange, HPRL, or live-execution functionality. It is
on this strategy's path, rather than installed into `freqtrade`, so it cannot
affect another audit strategy.

This measures deterministic strategy signals in the audit's ordinary futures
runtime. It does not claim to reproduce XXA222's bespoke live Hedge execution
engine.

Run the no-data contract test before an intentional benchmark:

```powershell
.\ftenv\Scripts\python.exe `
  repair\patched\repos\XXA222_HPRL\config_examples\strategies\test_hedge_adaptive_regime.py
```

```powershell
.\ftenv\Scripts\freqtrade.exe list-strategies `
  --config runtime\profile_futures_config.json `
  --strategy-path repair\patched\repos\XXA222_HPRL\config_examples\strategies
```
