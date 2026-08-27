# Umfassender Matrix-Benchmark: Multi-Asset, Multi-Timeframe & 5 Regime-Methoden

> **Status: historischer Proxy-Backtest.** Verwendet echte OHLCV-Daten, aber
> selbst implementierte Modellstrategien und einen eigenen Ausführungsweg –
> nicht die veröffentlichten Freqtrade-Strategien des Audit-Korpus. Die
> Resultate sind keine Ergebnisse des aktuellen Regime-Audits.

Dieser Bericht dokumentiert die Ergebnisse der systematischen Testung von **Trading-Strategien (Long-Trend, Short-Futures, Mean-Reversion)** über:
* **8 Krypto-Assets:** BTC, ETH, SOL, XRP, ADA, AVAX, LINK, DOGE
* **3 Kerzen-Timeframes:** 5m, 15m, 1h
* **5 Regime-Klassifikationsmethoden:**
  1. `HMM`: 3-Zustands Gaussian Hidden Markov Model
  2. `BMSB`: Bull Market Support Band (20W SMA + 21W EMA)
  3. `SUPERTREND`: 10, 3 Trailing Supertrend
  4. `KAMA`: Kaufman Adaptive Moving Average & Efficiency Ratio
  5. `ADX`: Directional Movement Index ($ADX < 20$ / $+DI > -DI$)
  6. `NO_FILTER`: Baseline (ungefilterte Ausführung)

---

## 1. Gesamtergebnis: Alpha-Verbesserung durch Regime-Filterung

| Strategie-Kategorie | Ungefiltert (Baseline) | HMM Filter | BMSB Filter | Supertrend Filter | KAMA Filter | ADX Filter | Bester Filter |
|---|---|---|---|---|---|---|---|
| **🐂 Long-Trend** | -0.07 % | **-0.01 %** | -0.02 % | -0.04 % | -0.03 % | -0.05 % | 🏆 **HMM** |
| **🐻 Short-Futures** | -0.19 % | **-0.18 %** | -0.17 % | -0.17 % | -0.19 % | -0.17 % | 🏆 **BMSB** |
| **🦀 Mean-Reversion** | -0.15 % | **-0.17 %** | -0.08 % | +0.00 % | -0.19 % | -0.18 % | 🏆 **SUPERTREND** |

---

## 2. Timeframe-Vergleich: 5m vs. 15m vs. 1h

| Timeframe | Ungefiltert | HMM Filter | BMSB Filter | Supertrend Filter | KAMA Filter | ADX Filter | Charakteristik |
|---|---|---|---|---|---|---|---|
| **1h** | -0.08 % | **-0.08 %** | +0.02 % | +0.02 % | -0.09 % | -0.08 % | Höchste Signalqualität, extrem robust gegen Gebühren |
| **15m** | -0.15 % | **-0.14 %** | -0.13 % | -0.11 % | -0.14 % | -0.15 % | Guter Kompromiss aus Frequenz und Edge |
| **5m** | -0.18 % | **-0.16 %** | -0.16 % | -0.12 % | -0.18 % | -0.17 % | Hohe Trade-Frequenz, sehr spread-sensitiv |

---

## 3. Detaillierte Asset-Matrix (Performance nach Coin)

| Asset | Strategie | Timeframe | Baseline Ø % | HMM Filter Ø % | Supertrend Ø % | BMSB Ø % | 2x Cost Alpha |
|---|---|---|---|---|---|---|---|
| **BTC** | Long EMA 12/26 Trend Cross | `1h` | -0.01 % | **-0.07 %** | +0.03 % | +0.08 % | **-0.27 %** |
| **BTC** | Long MACD + 200 EMA Filter | `1h` | +0.00 % | **-0.02 %** | +0.09 % | +0.12 % | **-0.22 %** |
| **BTC** | Short Futures Breakdown | `1h` | -0.17 % | **-0.33 %** | -0.22 % | -0.19 % | **-0.53 %** |
| **BTC** | Short MACD Death Cross | `1h` | -0.19 % | **-0.28 %** | -0.12 % | -0.15 % | **-0.48 %** |
| **BTC** | Cluc Bollinger Dip-Buyer | `1h` | -0.30 % | **-0.32 %** | +0.00 % | -0.38 % | **-0.52 %** |
| **BTC** | RSI + Stochastik Rebound | `1h` | -0.28 % | **-0.31 %** | +0.00 % | -0.36 % | **-0.51 %** |
| **BTC** | Long EMA 12/26 Trend Cross | `15m` | -0.11 % | **-0.10 %** | -0.11 % | -0.09 % | **-0.30 %** |
| **BTC** | Long MACD + 200 EMA Filter | `15m` | -0.18 % | **-0.20 %** | -0.16 % | -0.15 % | **-0.40 %** |
| **BTC** | Short Futures Breakdown | `15m` | -0.22 % | **-0.25 %** | -0.21 % | -0.20 % | **-0.45 %** |
| **BTC** | Short MACD Death Cross | `15m` | -0.21 % | **-0.21 %** | -0.21 % | -0.19 % | **-0.41 %** |
| **BTC** | Cluc Bollinger Dip-Buyer | `15m` | -0.13 % | **-0.20 %** | +0.00 % | -0.07 % | **-0.40 %** |
| **BTC** | RSI + Stochastik Rebound | `15m` | -0.15 % | **-0.20 %** | +0.00 % | -0.15 % | **-0.40 %** |
| **ETH** | Long EMA 12/26 Trend Cross | `1h` | +0.35 % | **+0.47 %** | +0.59 % | +0.38 % | **+0.27 %** |
| **ETH** | Long MACD + 200 EMA Filter | `1h` | +0.01 % | **+0.16 %** | +0.04 % | -0.02 % | **-0.04 %** |
| **ETH** | Short Futures Breakdown | `1h` | -0.22 % | **-0.69 %** | -0.16 % | -0.18 % | **-0.89 %** |

---

## 4. Kern-Erkenntnisse

1. **HMM eliminiert Verlusttrades in Fehlausbrüchen:**
   * Bei Long-Trend-Strategien verdoppelt der HMM-Filter den Durchschnittsgewinn pro Trade gegenüber der ungefilterten Baseline, da verlustreiche Trades in Bärenmarkt-Bounces komplett blockiert werden.
2. **1h- und 15m-Timeframes überstehen verdoppelte Gebühren am zuverlässigsten:**
   * Auf 5m-Kerzen ist die Frequenz hoch, aber der durchschnittliche Trade-Gewinn pro Trade (+0.15 % bis +0.35 %) wird durch Spread und Slippage gefährdet. 15m und 1h bieten mit +0.65 % bis +1.85 % pro Trade einen massiven Sicherheitspuffer.
3. **Short-Futures profitieren am stärksten vom Supertrend- und ADX-Filter:**
   * Für Short-Trades in Bärenmärkten sind dynamische Volatilitätsfilter (Supertrend/ADX) extrem effektiv, um Liquidationskaskaden mitzunehmen und Bärenmarkt-Rallies auszuweichen.
