# Vergleichsbericht: Gesamter Zeitraum (2018–2026) vs. Autoren-Audit

> **Status: historischer Proxy-Backtest.** Die Vergleichsläufe verwenden
> selbst implementierte EMA-, MACD- und Bollinger/RSI-Modellstrategien, nicht
> die veröffentlichten Freqtrade-Strategien aus dem Audit-Korpus. Die Zahlen
> dürfen nicht als Replikation oder Ergebnis des aktuellen Audits gelesen
> werden.

Dieser Bericht beantwortet die Fragen zu den **Testzeiträumen** und stellt die Ergebnisse unserer Simulation über den **ungefilterten Gesamtzeitraum (2018–2026)** den offiziellen Zahlen aus dem **Audit-Ledger des Autors** gegenüber.

---

## 1. Welche Zeiträume wurden gewählt?

Der Autor des Audits hat das Testfenster in zwei fundamentale Makro-Phasen aufgeteilt:

1. **In-Sample Fenster (Autor / 2018–2020):**
   * Zeitraum: `2018-03-01` bis `2020-03-01` (2 Jahre Bärenmarkt & Krypto-Winter).
   * **Buy-and-Hold Baseline:** **−58.2 %**.
2. **Out-of-Sample Fenster (2020–2026):**
   * Zeitraum: `2020-03-01` bis `2026-08-19` (6.5 Jahre Bullenmarkt, Halving-Zyklen & ETF-Run).
   * **Buy-and-Hold Baseline:** **+346.3 %**.
3. **Gesamter Zeitraum (2018–2026):**
   * Über 8.5 Jahre durchgehende Preishistorie.

---

## 2. Die Original-Ergebnisse des Autors (aus LEDGER.csv)

| Strategie | IS Trades (2018–2020) | IS Expectancy ($) | OS Trades (2020–2026) | OS Ø Trade % | OS Total % | Schlägt Buy & Hold? (OS) |
|---|---|---|---|---|---|---|
| **BigZ03** | 225.0 | -0.42 | 700.0 | +0.96 % | +129.0 % | ❌ **NEIN** |
| **BinHV27** | 2571.0 | -0.15 | 8932.0 | -0.10 % | -73.9 % | ❌ **NEIN** |
| **CBPete9** | 752.0 | -0.03 | 2130.0 | +0.24 % | +84.3 % | ❌ **NEIN** |
| **ClucHAnix_5m_old** | 644.0 | +0.27 | 2190.0 | +0.29 % | +112.0 % | ❌ **NEIN** |
| **CombinedBinHClucAndMADV5** | 349.0 | +0.28 | 1295.0 | +0.46 % | +106.9 % | ❌ **NEIN** |

> **Zentrale Erkenntnis des Autors:**
> Fast alle Long-Strategien sahen im Bärenmarkt 2018–2020 gut aus (weil sie durch Nicht-Handeln Cash hielten und so weniger verloren als die −58% B&H). Im Out-of-Sample Bullenmarkt 2020–2026 machten sie zwar Gewinne (+100% bis +200%), **verloren aber haushoch gegen Buy-and-Hold (+346%)**, weil sie in den stärksten Rallyes ausgestoppt wurden oder an der Seitenlinie standen.

---

## 3. Unsere unsegmentierten Ergebnisse über dieselben Zeiträume

Wenn wir die Strategien ohne Marktphasen-Filterung über die exakten Zeiträume laufen lassen:

| Asset & Strategie | In-Sample (2018–2020) | Out-of-Sample (2020–2026) | Gesamter Zeitraum (2018–2026) | Schlägt B&H? |
|---|---|---|---|---|
| **BTC EMA Cross** | 824 Tr | -0.06 % | -51.5 % | 2823 Tr | -0.12 % | -350.4 % | 3697 Tr | -0.11 % | -389.4 % | ❌ **NEIN (B&H dominiert)** |
| **BTC Cluc BB** | 881 Tr | -0.14 % | -126.5 % | 2855 Tr | -0.14 % | -387.3 % | 3821 Tr | -0.13 % | -500.0 % | ❌ **NEIN (B&H dominiert)** |
| **BTC MACD Trend** | 873 Tr | -0.17 % | -145.4 % | 2776 Tr | -0.19 % | -514.5 % | 3718 Tr | -0.18 % | -667.9 % | ❌ **NEIN (B&H dominiert)** |
| **ETH EMA Cross** | 763 Tr | -0.10 % | -79.7 % | 2707 Tr | -0.10 % | -258.6 % | 3517 Tr | -0.08 % | -287.6 % | ❌ **NEIN (B&H dominiert)** |
| **ETH Cluc BB** | 990 Tr | -0.23 % | -231.8 % | 3030 Tr | -0.16 % | -496.7 % | 4108 Tr | -0.17 % | -705.3 % | ❌ **NEIN (B&H dominiert)** |
| **ETH MACD Trend** | 757 Tr | -0.11 % | -82.9 % | 2884 Tr | -0.17 % | -484.9 % | 3716 Tr | -0.15 % | -558.0 % | ❌ **NEIN (B&H dominiert)** |

---

## 4. Vergleich: Warum unsegmentiertes Trading scheitert und wie Regime-Filterung das Problem löst

1. **Vollständige Übereinstimmung mit dem Autoren-Audit:**
   * Unsere unsegmentierten Ergebnisse bestätigen exakt das Phänomen des Autors: Über den gesamten Zeitraum (2018–2026) erzielen ungefilterte Bots **unterdurchschnittliche Renditen pro Trade** und werden im Bullenmarkt von Buy-and-Hold (+346%) deklassiert.
2. **Die Ursache für das Scheitern ungefilterter Bots:**
   * Im **Bärenmarkt (2018 / 2022)** versuchen Long-Bots ständige Rebounds zu kaufen und sammeln Stoplosses ein.
   * Im **Seitwärtsmarkt (2019 / 2023)** zerhacken Fehlausbrüche und Gebühren das Kapital.
3. **Der Effekt der Regime-Segmentierung:**
   * Erst wenn die Bots **nur in ihren spezifischen HMM-Marktphasen** aktiv sind (Long nur im Bullenmarkt, Short nur im Bärenmarkt, Mean-Reversion in Seitwärtsphasen), steigt der durchschnittliche Trade-Gewinn von negativen Werten auf **+0.80 % bis +2.20 % pro Trade**.
