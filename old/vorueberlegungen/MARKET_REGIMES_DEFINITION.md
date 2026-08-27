# Definition von Krypto-Marktphasen (Market Regimes)

> **Status: historische methodische Vorüberlegung.** Dieses Dokument ist nicht
> preregistriert und nicht normativ. Der aktuelle Versuchsplan steht in
> `../../REGIME_AUDIT_PLAN.md`; insbesondere ist dort DMI/ADX primär und HMM
> für Version 1 zurückgestellt.

Dieses Dokument definiert **quantitative, reaktionsschnelle und krypto-native Methoden** zur Bestimmung der verschiedenen Marktphasen (Bullenmarkt, Bärenmarkt, Seitwärtsmarkt) für Bitcoin (BTC) und den breiteren Kryptomarkt. 

---

## 1. Problemstellung: Warum klassische TradFi-Metriken (SMA 200) versagen

In der traditionellen Finanzwelt (TradFi) gilt der **200-Tage-SMA** als Standard für Makro-Trends. Im 24/7-gehandelten Kryptomarkt mit extremer Volatilität und 4-Jahres-Zyklen weist der SMA 200 jedoch gravierende Schwächen auf:
* **Hohe Trägheit (Lag):** Der SMA 200 reagiert oft erst Wochen nach Beginn einer Trendwende. Ein Großteil der Aufwärts- oder Abwärtsbewegung ist dann bereits vorbei.
* **Verzerrung durch Krypto-Korrekturen:** Schnelle Zwischenkorrekturen im Bullenmarkt von −20 % bis −30 % führen zu Fehlsignalen oder verzögertem Wiedereinstieg.

Für ein präzises Regime-Benchmarking von Trading-Strategien sind daher **krypto-spezifische On-Chain-, Derivate- und adaptive Volatilitätsmodelle** erforderlich.

---

## 2. Framework 1: Das On-Chain-Kostenbasis-Modell (Glassnode Standard)

Der Goldstandard institutioneller Krypto-Analysten basiert auf der **Kostenbasis der kurzfristigen Halter (Short-Term Holders / STH)**, definiert als Coins, die in den letzten 155 Tagen bewegt wurden.

```
                            ┌──────────────────────────────────────┐
                            │    Marktpreis vs. STH Realized Price │
                            └──────────────────┬───────────────────┘
                                               │
             ┌─────────────────────────────────┼─────────────────────────────────┐
             ▼                                 ▼                                 ▼
   Preis > STH Realized Price        Preis pendelt um STH-Preis        Preis < STH Realized Price
      (STH-MVRV > 1.0)                    (STH-MVRV ≈ 1.0)                  (STH-MVRV < 1.0)
   ────────────────────────          ────────────────────────          ────────────────────────
   🐂 BULLEN-REGIME                  🦀 SEITWÄRTS / TRANSITION         🐻 BÄREN- / STRESS-REGIME
   Neukäufer sind im Profit.         Unentschlossenheit.               Neukäufer sind "underwater".
   Rücksetzer zur Kostenbasis        Kostenbasis wird mehrfach         Rallies zur Kostenbasis werden
   werden als Support gekauft.       getestet.                         als Notausstieg abverkauft.
```

### Quantitative Kriterien:
1. 🐂 **Bullenmarkt (Markup / Risk-On):**
   * **Bedingung:** `Spot-Preis > STH Realized Price` (äquivalent zu `STH-MVRV > 1.0`).
   * **Dynamik:** Die jüngsten Käufer sitzen auf Gewinnen. Dips in Richtung der STH-Kostenbasis fungieren als starker Support.
2. 🐻 **Bärenmarkt (Markdown / Risk-Off):**
   * **Bedingung:** `Spot-Preis < STH Realized Price` (äquivalent zu `STH-MVRV < 1.0`).
   * **Dynamik:** Neukäufer erleiden Buchverluste. Erholungen (Bounces) zur STH-Kostenbasis werden als Exit-Liquidität abverkauft (Widerstand).
3. 💀 **Makro-Kapitulation (Deep Bear Bottom):**
   * **Bedingung:** `Spot-Preis < Realized Price (Gesamtnetzwerk)` bzw. `Spot-Preis < LTH Realized Price`.
4. 🦀 **Seitwärtsmarkt (Akkumulation / Distribution):**
   * **Bedingung:** `STH-MVRV` oszilliert eng um `1.0` ($\pm 5\,\%$) bei abnehmender Netto-Realisierter-Gewinn/Verlust-Volatilität.

---

## 3. Framework 2: Krypto-Native Preis- & Volatilitätsmodelle (OHLCV)

Wenn keine On-Chain-Datenbank angebunden ist, bieten rein chartbasierte, adaptive Indikatoren eine deutlich agilere Klassifikation als der SMA 200.

### A. Bull Market Support Band (20-Wochen-SMA + 21-Wochen-EMA)
Das von Benjamin Cowen etablierte Modell kombiniert Glättung mit Reaktionsschnelligkeit:
* **20-Week SMA:** Glättet die Makro-Preishistorie über ca. 4–5 Monate.
* **21-Week EMA:** Reagiert dynamisch auf neuere Kursimpulse.

| Marktphase | Kriterium | Strategie-Fokus |
|---|---|---|
| 🐂 **Bullenmarkt** | Wöchentlicher Schlusskurs **oberhalb beider Bänder**. Band dient als dynamischer Support bei Pullbacks. | Long-Only Momentum & Trendfolge |
| 🐻 **Bärenmarkt** | Wöchentlicher Schlusskurs **unterhalb beider Bänder**. Band fungiert als starker dynamischer Widerstand. | Short-Only Futures / Cash-Absicherung |
| 🦀 **Seitwärts / Chop** | Kurs schließt **innerhalb des Bandes** (Zone der Richtungsentscheidung). | Range-Trading / Neutral |

---

### B. Supertrend & Adaptive Volatilitätsfilter (Daily / 4H)
Verwendet die **Average True Range (ATR)** anstelle fixer Zeitperioden.
* **Supertrend (ATR 10, Multiplier 3 auf 1D BTC):**
  * `Supertrend == Grün` $\rightarrow$ **Bullen-Regime**
  * `Supertrend == Rot` $\rightarrow$ **Bären-Regime**
* **Ergänzung für Seitwärtsmärkte:**
  * `ADX(14) < 20` + `Bollinger Band Width (BBW) im unteren 25%-Perzentil`: Identifiziert trendlose Kompressionsphasen (Chop).

---

### C. Kaufman Adaptive Moving Average (KAMA)
* Passt seine Glättung automatisch an die Markteffizienz an ($ER = \text{Efficiency Ratio}$):
  * **Im starken Trend:** KAMA wird extrem schnell (vergleichbar mit einem 9-EMA).
  * **Im Seitwärtsmarkt:** KAMA flacht komplett ab und filtert Rauschen heraus.

---

## 4. Framework 3: Derivate- & Liquiditäts-Regimes (Perpetual Futures)

Krypto-Spotmärkte werden maßgeblich von den Terminmärkten (Binance, Bybit USDT-Perpetuals) getrieben:

```
                               ┌─────────────────────────────┐
                               │   8h Perpetual Funding Rate │
                               └──────────────┬──────────────┘
                                              │
              ┌───────────────────────────────┼───────────────────────────────┐
              ▼                               ▼                               ▼
    Funding > +0.015 % pro 8h           Funding ≈ 0.000 %            Funding < 0.000 %
       + Steigendes Open Interest        + Sinkendes/Flaches OI          + Hohes/Steigendes Short-OI
    ─────────────────────────         ───────────────────────        ───────────────────────────
    🐂 BULLEN-MOMENTUM                🦀 SEITWÄRTS / RESET           🐻 BÄREN-DRUCK
    Longs zahlen Shorts;              Hebelbereinigung;              Shorts zahlen Longs;
    Aggressiver Kaufdruck.            Markt konsolidiert.            Dominanter Verkaufsdruck.
```

---

## 5. Framework 4: Statistische Regime-Erkennung (Hidden Markov Models / HMM)

Im quantitativen Fonds-Management werden **Hidden Markov Models (HMM)** oder **GMM (Gaussian Mixture Models)** trainiert, die den Markt anhand von Rendite- und Volatilitätsverteilungen unsupervised klassifizieren:

* **State 0 (Bull Regime):** $\mu > 0$ (positive Rendite), $\sigma$ moderat.
* **State 1 (Bear Regime):** $\mu < 0$ (negative Rendite), $\sigma$ hoch (panikgetrieben).
* **State 2 (Chop / Sideways Regime):** $\mu \approx 0$ (neutrale Rendite), $\sigma$ komprimiert/niedrig.

---

## 6. Zusammenfassende Entscheidungsmatrix für Freqtrade-Audits

| Regime | Primäre Kriterien (BTC/USDT) | Sekundäre Bestätigung | Zulässiger Strategietyp |
|---|---|---|---|
| 🐂 **BULL** | 1. Kurs > 21-Wochen-EMA (oder Supertrend 1D Grün)<br>2. STH-MVRV > 1.0 | 1. ADX(14) $\ge 25$ mit $+DI > -DI$<br>2. Funding Rate $> +0.01\,\%$ | **Long-Only** (Momentum, Breakout, Trendfolge) |
| 🐻 **BEAR** | 1. Kurs < 21-Wochen-EMA (oder Supertrend 1D Rot)<br>2. STH-MVRV < 1.0 | 1. ADX(14) $\ge 25$ mit $-DI > +DI$<br>2. Funding Rate $< 0.00\,\%$ | **Short-Only** (Futures Short, Hedging, Rebound-Sells) |
| 🦀 **SIDE** | 1. ADX(14) $< 20$<br>2. Kurs innerhalb des Bull Market Support Bands | 1. Bollinger Band Width komprimiert<br>2. Funding Rate neutral ($\approx 0.00\,\%$) | **Mean-Reversion** (RSI/BB-Oszillatoren, Grid) |

---

## 7. Quellenverzeichnis & Weiterführende Referenzen

1. **Glassnode Insights & Academy:**
   * *A Primer on On-Chain Market Regimes and Short-Term Holder Cost Basis:* [Glassnode Academy](https://academy.glassnode.com/)
   * *Short-Term Holder MVRV as a Market Indicator:* [Glassnode Insights](https://insights.glassnode.com/)
2. **Benjamin Cowen (Into The Cryptoverse):**
   * *The Bitcoin Bull Market Support Band (20-Week SMA & 21-Week EMA Methodology):* [Bull Market Support Band Reference](https://bullmarketsupportband.com/)
3. **Wyckoff Analytics:**
   * *The Wyckoff Method of Market Analysis (Accumulation, Markup, Distribution, Markdown):* [Wyckoff Analytics Educational Resources](https://www.wyckoffanalytics.com/)
4. **Quantitative Finance & Machine Learning:**
   * *Hamilton, J. D. (1989): "A New Approach to the Economic Analysis of Nonstationary Time Series and the Business Cycle" (Grundlagenwerk zu Markov-Regime-Switching).*
   * *Quantifying Cryptocurrency Regimes using Hidden Markov Models (Applied Quant Research).*
5. **Freqtrade Framework & Community:**
   * *Brook Miles: Backtesting Traps in Crypto Trading Bots:* [Brook Miles Freqtrade Stuff](https://brookmiles.github.io/freqtrade-stuff/2021/04/12/backtesting-traps/)
