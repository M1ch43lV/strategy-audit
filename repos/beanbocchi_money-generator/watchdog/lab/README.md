# Replay lab

Runs the bot's real history through the alert rules to answer a question unit tests cannot:
**would the watchdog actually have helped, and how often would it have cried wolf?**

```bash
cd watchdog && .venv/bin/python -m lab.replay \
  --logs ../../NostalgiaForInfinity/user_data/logs \
  --db   ../../NostalgiaForInfinity/user_data/khoakomlem_binance_futures-tradesv3.sqlite
```

Only log- and DB-derived rules are replayable (`ExchangeAuthError`, `ExitFailed`,
`NoActivity`, `DrawdownBreach`). The five liveness rules need historical API responses that
were never recorded; those were proven live instead — see §Live evidence.

## Results (2026-07-30, 76 days of history)

| Criterion | Target | Measured | |
|---|---|---|---|
| `ExchangeAuthError` detection latency | < 1h | **0:00:00** | met |
| `ExitFailed` fires in the 2026-07-27 window | yes | 20:01, 21:01 | met |
| `NoActivity` silent on legitimate 3.4–4.0 day gaps | yes | fires only in the two real outage clusters | met |
| Alert rate | < ~1/day | 13.01/day | **not met — see below** |

**50 of 77 calendar days produced zero alerts.** That is the honest false-positive number.
Alerts concentrate in two contiguous runs — 2026-07-05..07-15 (463) and 2026-07-17..07-29
(523) — which are the real outage windows, plus three isolated single-alert days.

Three distinct auth-error episodes were found: 2026-05-14, 2026-07-05, 2026-07-17. Only the
last was known before this exercise.

## Why the alert-rate criterion failed, and what was changed

The volume was not false positives. It was a **flat 60-minute cooldown re-reporting a
condition that lasted 13 days** — correct behaviour, and completely unusable: the channel
gets muted, which is the exact blind spot this service exists to remove.

Fixed by making the cooldown double while a condition persists (1h, 2h, 4h, 8h, 16h, capped
at 24h) and reset once the condition clears. Measured on the real 13-day outage:
**312 messages → 17.** The rules and their thresholds were left alone.

## A measurement error worth recording

The first run of this lab computed drawdown as a fraction of **peak profit** and concluded
that `DrawdownBreach`'s 0.15 threshold was breached on 55 of 76 days, so the threshold was
raised to 0.50. That was wrong.

`rule_drawdown_breach` reads `/api/v1/profit.current_drawdown`, which freqtrade computes
**relative to capital**. Verified against the live API: `current_drawdown_abs` 11.33 with
`current_drawdown` 0.0443 implies a base of ~256 (capital), not the 25.81 peak of closed
profit. The two differ by ~10x (0.4391 vs 0.0443).

The bot's worst drawdown in its entire history is **0.0775**, so 0.15 has never been
breached and is a sensible warning level; 0.50 would have made the rule nearly unfireable,
since a 50% capital drawdown means the account is already destroyed. Threshold restored to
0.15 and the lab's formula corrected — it now reproduces freqtrade's own reported
`max_drawdown` of 0.0775 from the same trade data, which is the check that it is right.

Caveat: the lab assumes a constant `STARTING_CAPITAL = 230.23`. Capital was smaller earlier
in the history, so early drawdown ratios are slightly understated.

## Live evidence for the rules the replay cannot cover

- `BotUnreachable` — a throwaway watchdog pointed at a dead port delivered a real Telegram
  message: `nfi_alert_fired_total{rule="BotUnreachable"} 1.0`, zero delivery failures.
- `NoActivity` and `Stalled` — both fired and delivered on the live deployment.
- `Stalled` also produced a real **false positive** there, on the first poll after a deploy:
  `/health` returns the previous run's `last_process` until the new run finishes its
  ~3-minute startup. Fixed with an uptime guard. No test would have caught this.
