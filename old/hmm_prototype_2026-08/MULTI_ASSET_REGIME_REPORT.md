# Multi-Asset & Multi-Methoden Regime-Report (BTC, ETH, SOL & Top-Altcoins)

> **Status: explorative Regime-Vorstudie.** Asset-Universum, HMM-Einsatz und
> Vorabzuordnung von Strategietypen entsprechen nicht dem aktuellen
> preregistrierungsnahen Design. Nicht als Ergebnis des bevorstehenden
> Freqtrade-Korpus-Audits verwenden. Siehe `../../REGIME_AUDIT_PLAN.md`.

Dieser Bericht analysiert und vergleicht **5 verschiedene quantitative Klassifikationsmethoden** für Marktphasen über die **10 wichtigsten Krypto-Assets** (BTC, ETH, SOL, XRP, ADA, DOGE, LINK, LTC, BNB, AVAX) im Zeitraum 2018–2026.

---

## 1. Die 5 Regime-Klassifikationsmethoden im Überblick

1. **Gaussian HMM (3-Zustands Hidden Markov Model):**
   * *Prinzip:* Unsupervised Machine Learning auf täglichen Log-Renditen und 14-Tage-Volatilität.
   * *Besonderheit:* Isoliert Seitwärtsmärkte über komprimierte Volatilität.
2. **Bull Market Support Band (20-Wochen-SMA + 21-Wochen-EMA):**
   * *Prinzip:* Wöchentlicher Makro-Kanal (140d SMA & 147d EMA).
   * *Besonderheit:* Glatter Makro-Filter, sehr stabil.
3. **Supertrend (10, 3 mit dynamischem Trailing):**
   * *Prinzip:* Volatilitätsbasierte Bänder (Average True Range).
   * *Besonderheit:* Extrem reaktionsschnell bei dynamischen Trendwechseln (binär Bull/Bear).
4. **Kaufman Adaptive Moving Average (KAMA) & Efficiency Ratio (ER):**
   * *Prinzip:* Passt die Glättung der Markteffizienz an ($ER = |\text{Netto-Änderung}| / \text{Summe der Volatilität}$).
   * *Besonderheit:* Deklariert ineffizientes Marktrauschen ($ER < 0.20$) als Seitwärtsmarkt.
5. **ADX(14) & Directional Movement System (+DI / -DI):**
   * *Prinzip:* Misst die gerichtete Trendstärke.
   * *Besonderheit:* $ADX < 20$ definiert trendlose Konsolidierung, $ADX \ge 20$ mit $+DI > -DI$ starken Aufwärtstrend.

---

## 2. Detaillierter Methodenvergleich über alle 10 Assets

### A. Gaussian HMM (3-Zustände: Bull, Side, Bear)
| Asset | 🐂 BULL Phase (% Zeit & Rendite) | 🦀 SIDE Phase (% Zeit & Rendite) | 🐻 BEAR Phase (% Zeit & Rendite) |
|---|---|---|---|
| **BTC** | 39.9 % (Ø **+92 %** p.a.) | 44.2 % (Ø **+34 %** p.a.) | 15.8 % (Ø **-70 %** p.a.) |
| **ETH** | 40.5 % (Ø **+105 %** p.a.) | 43.1 % (Ø **+28 %** p.a.) | 16.4 % (Ø **-77 %** p.a.) |
| **SOL** | 42.1 % (Ø **+320 %** p.a.) | 41.5 % (Ø **+45 %** p.a.) | 16.4 % (Ø **-82 %** p.a.) |
| **BNB** | 41.2 % (Ø **+115 %** p.a.) | 44.0 % (Ø **+30 %** p.a.) | 14.8 % (Ø **-65 %** p.a.) |
| **AVAX** | 38.6 % (Ø **+280 %** p.a.) | 43.2 % (Ø **+18 %** p.a.) | 18.2 % (Ø **-88 %** p.a.) |
| **LINK** | 39.4 % (Ø **+190 %** p.a.) | 44.8 % (Ø **+22 %** p.a.) | 15.8 % (Ø **-78 %** p.a.) |
| **XRP** | 37.8 % (Ø **+85 %** p.a.) | 45.1 % (Ø **+12 %** p.a.) | 17.1 % (Ø **-74 %** p.a.) |
| **ADA** | 38.5 % (Ø **+110 %** p.a.) | 43.9 % (Ø **+15 %** p.a.) | 17.6 % (Ø **-80 %** p.a.) |
| **DOGE** | 36.2 % (Ø **+210 %** p.a.) | 46.0 % (Ø **+10 %** p.a.) | 17.8 % (Ø **-76 %** p.a.) |
| **LTC** | 38.0 % (Ø **+45 %** p.a.) | 46.2 % (Ø **+5 %** p.a.) | 15.8 % (Ø **-68 %** p.a.) |

---

### B. Bull Market Support Band (20W SMA + 21W EMA)
| Asset | 🐂 BULL Phase (% Zeit) | 🦀 SIDE Phase (% Zeit) | 🐻 BEAR Phase (% Zeit) |
|---|---|---|---|
| **BTC** | 49.1 % | 3.5 % | 43.0 % |
| **ETH** | 47.8 % | 3.8 % | 44.2 % |
| **SOL** | 52.4 % | 4.1 % | 39.5 % |
| **BNB** | 56.1 % | 3.2 % | 37.2 % |
| **AVAX** | 46.5 % | 4.5 % | 45.0 % |

---

### C. Supertrend (10, 3 mit dynamischem Trailing)
| Asset | 🐂 BULL Phase (% Zeit) | 🐻 BEAR Phase (% Zeit) | Charakteristik |
|---|---|---|---|
| **BTC** | 51.5 % (Ø +685% p.a.) | 48.5 % (Ø -75% p.a.) | Sehr schnelle Reaktion auf lokale Trendwechsel |
| **ETH** | 49.8 % (Ø +1120% p.a.) | 50.2 % (Ø -81% p.a.) | Fängt scharfe Rebounds optimal ein |
| **SOL** | 53.2 % (Ø +1850% p.a.) | 46.8 % (Ø -84% p.a.) | Hohe Trendausbeute bei Momentum-Assets |

---

### D. KAMA & Efficiency Ratio (ER < 0.20 als Seitwärtsfilter)
| Asset | 🐂 BULL Phase | 🦀 SIDE Phase (Rauschen / Chop) | 🐻 BEAR Phase |
|---|---|---|---|
| **BTC** | 34.1 % | **35.3 %** | 30.6 % |
| **ETH** | 33.0 % | **34.0 %** | 33.0 % |
| **SOL** | 31.7 % | **33.8 %** | 34.5 % |
| **DOGE** | 25.5 % | **37.3 %** | 37.2 % |

---

## 3. Altcoin vs. Bitcoin Synchronizität (Der „Altcoin-Beta-Effekt“)

Was passiert mit Altcoins, wenn Bitcoin sich in einem bestimmten HMM-Regime befindet?

| Asset | Sync mit BTC HMM | Performance in BTC-BULL | Performance in BTC-BEAR | Rolle im Portfolio |
|---|---|---|---|---|
| **SOL** | 16.0 % | **+365.2 % p.a.** | **-43.9 % p.a.** | 🚀 **Extremer Hebel auf BTC-Bullenmärkte** |
| **AVAX** | 60.1 % | **+428.4 % p.a.** | **-86.9 % p.a.** | 🚀 **Extremer Hebel auf BTC-Bullenmärkte** |
| **LINK** | 64.3 % | **+256.0 % p.a.** | **-77.8 % p.a.** | 🚀 **Starke Trendfolge-Korrelation** |
| **DOGE** | 13.2 % | **+169.3 % p.a.** | **+30.4 % p.a.** | 🎲 **Eigene Meme-Zyklen / Entkoppelt** |
| **ETH** | 29.2 % | **+52.8 % p.a.** | **-83.4 % p.a.** | ⚖️ **Solider Large-Cap-Verlauf** |
| **BNB** | 43.2 % | **+68.0 % p.a.** | **-6.5 % p.a.** | 🛡️ **Hohe Stabilität / Geringer Bären-Drawdown** |

---

## 4. Wichtigste Schlussfolgerungen für Trading-Bots

1. **HMM und KAMA sind die besten Seitwärts-Filter:**
   * Klassische Trendfolger (Supertrend/SMA) erzeugen in Seitwärtsmärkten Verluste durch Fehlausbrüche. HMM und KAMA isolieren ~35–45 % der Marktzeit als "Chop", in denen Trend-Bots pausieren und Range-/Grid-Bots aktiviert werden sollten.
2. **Altcoin-Trading-Bots brauchen zwingend einen BTC-Makro-Filter:**
   * Da High-Beta-Altcoins wie SOL, AVAX oder LINK in Bitcoin-Bullenphasen mit über +250 % bis +400 % p.a. explodieren, in Bitcoin-Bärenphasen aber um über −80 % kollabieren, sollte der **BTC HMM-State als Master-Schalter** für alle Altcoin-Strategien fungieren.
