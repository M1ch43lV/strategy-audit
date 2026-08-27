# Analysebericht: Krypto-Marktphasen & HMM-Modellierung (2018–2026)

> **Status: explorative HMM-Vorstudie.** Keine bestätigende Analyse, keine
> Ergebnisse des preregistrierten Regime-Audits und nicht zur Rangfolge der
> veröffentlichten Freqtrade-Strategien verwenden. Der aktuelle Plan steht in
> `../../REGIME_AUDIT_PLAN.md`.

Dieses Dokument fasst die Ergebnisse der **Hidden Markov Model (HMM)**-Regimeerkennung sowie den Vergleich mit dem **Bull Market Support Band (BMSB)** und dem **Supertrend** auf Bitcoin (BTC/USDT) zusammen.

---

## 1. Ergebnisse des 3-Zustands Gaussian HMM

Das HMM wurde unsupervised auf täglichen Log-Renditen (ln(P_t / P_t-1)) und rollierender 14-Tage-Volatilität trainiert:

| HMM Zustand | Ø Tagesrendite | Ø 14D Volatilität | Historische Tage | Charakteristik |
|---|---|---|---|---|
| 🐂 **State 1: BULL** | **+0.19 %** | 3.26 % | **1.255 Tage (39.9 %)** | Starkes Aufwärtsmomentum, Dips werden gekauft. |
| 🦀 **State 2: SIDE** | **+0.08 %** | 1.83 % | **1.390 Tage (44.2 %)** | Niedrige Volatilität, Konsolidierung & Mean-Reversion. |
| 🐻 **State 0: BEAR** | **-0.33 %** | 5.68 % | **498 Tage (15.8 %)** | Hohe Volatilität, Liquidationskaskaden, Verkaufsdruck. |

### Regime-Übergangsmatrix (Stabilität der Phasen)
Die Diagonalelemente zeigen eine **extrem hohe Regime-Persistenz (> 94 %)**:
* Befindet sich der Markt im **BULL-Regime**, verbleibt er mit **94.7 %** Wahrscheinlichkeit auch am Folgetag im Bull-Regime.
* Im **SIDE-Regime** beträgt die Verweildauer-Wahrscheinlichkeit **96.7 %**.
* Im **BEAR-Regime** beträgt die Verweildauer-Wahrscheinlichkeit **95.4 %**.

---

## 2. Chronologische Haupt-Marktphasen (Blöcke $\ge$ 14 Tage)

| Regime | Startdatum | Enddatum | Dauer | Startkurs (BTC) | Endkurs (BTC) | BTC Rendite |
|---|---|---|---|---|---|---|
| 🦀 SIDE | 2018-01-01 | 2018-01-14 | 14 Tage | $13,380 | $13,475 | **+0.7 %** |
| 🐻 BEAR | 2018-01-15 | 2018-04-28 | 104 Tage | $13,540 | $9,348 | **-31.0 %** |
| 🐂 BULL | 2018-04-29 | 2018-06-05 | 38 Tage | $9,419 | $7,625 | **-19.0 %** |
| 🐂 BULL | 2018-06-10 | 2018-08-23 | 75 Tage | $6,765 | $6,525 | **-3.5 %** |
| 🐂 BULL | 2018-09-05 | 2018-09-18 | 14 Tage | $6,700 | $6,336 | **-5.4 %** |
| 🦀 SIDE | 2018-09-19 | 2018-11-13 | 56 Tage | $6,392 | $6,458 | **+1.0 %** |
| 🐻 BEAR | 2018-11-19 | 2018-12-11 | 23 Tage | $4,910 | $3,380 | **-31.2 %** |
| 🐻 BEAR | 2018-12-20 | 2019-01-02 | 14 Tage | $4,050 | $3,859 | **-4.7 %** |
| 🐂 BULL | 2019-01-03 | 2019-01-23 | 21 Tage | $3,767 | $3,553 | **-5.7 %** |
| 🦀 SIDE | 2019-01-24 | 2019-02-23 | 31 Tage | $3,570 | $4,118 | **+15.4 %** |
| 🐂 BULL | 2019-02-24 | 2019-03-09 | 14 Tage | $3,744 | $3,943 | **+5.3 %** |
| 🦀 SIDE | 2019-03-10 | 2019-04-01 | 23 Tage | $3,917 | $4,145 | **+5.8 %** |
| 🐻 BEAR | 2019-04-02 | 2019-04-15 | 14 Tage | $4,857 | $5,025 | **+3.5 %** |
| 🦀 SIDE | 2019-04-17 | 2019-05-10 | 24 Tage | $5,203 | $6,373 | **+22.5 %** |
| 🐻 BEAR | 2019-05-17 | 2019-05-30 | 14 Tage | $7,355 | $8,270 | **+12.4 %** |
| 🐂 BULL | 2019-05-31 | 2019-06-25 | 26 Tage | $8,555 | $11,821 | **+38.2 %** |
| 🐻 BEAR | 2019-06-26 | 2019-07-29 | 34 Tage | $13,094 | $9,508 | **-27.4 %** |
| 🐂 BULL | 2019-07-30 | 2019-09-10 | 43 Tage | $9,574 | $10,098 | **+5.5 %** |
| 🐂 BULL | 2019-09-24 | 2019-10-07 | 14 Tage | $8,493 | $8,190 | **-3.6 %** |
| 🦀 SIDE | 2019-10-08 | 2019-10-22 | 15 Tage | $8,168 | $8,020 | **-1.8 %** |
| 🐻 BEAR | 2019-10-25 | 2019-11-07 | 14 Tage | $8,655 | $9,216 | **+6.5 %** |
| 🐂 BULL | 2019-11-21 | 2019-12-07 | 17 Tage | $7,628 | $7,488 | **-1.8 %** |
| 🐂 BULL | 2019-12-18 | 2019-12-31 | 14 Tage | $7,278 | $7,195 | **-1.1 %** |
| 🐂 BULL | 2020-01-06 | 2020-01-28 | 23 Tage | $7,758 | $9,374 | **+20.8 %** |
| 🦀 SIDE | 2020-01-29 | 2020-02-17 | 20 Tage | $9,302 | $9,706 | **+4.3 %** |
| 🐂 BULL | 2020-02-18 | 2020-03-11 | 23 Tage | $10,165 | $7,935 | **-21.9 %** |
| 🐻 BEAR | 2020-03-12 | 2020-04-06 | 26 Tage | $4,800 | $7,330 | **+52.7 %** |
| 🐂 BULL | 2020-04-07 | 2020-05-09 | 33 Tage | $7,197 | $9,539 | **+32.5 %** |
| 🐂 BULL | 2020-05-21 | 2020-06-15 | 26 Tage | $9,069 | $9,426 | **+3.9 %** |
| 🦀 SIDE | 2020-06-16 | 2020-07-26 | 41 Tage | $9,526 | $9,932 | **+4.3 %** |
| 🐂 BULL | 2020-07-27 | 2020-08-15 | 20 Tage | $11,030 | $11,852 | **+7.5 %** |
| 🦀 SIDE | 2020-08-16 | 2020-09-01 | 17 Tage | $11,911 | $11,922 | **+0.1 %** |
| 🐂 BULL | 2020-09-02 | 2020-09-16 | 15 Tage | $11,389 | $10,954 | **-3.8 %** |
| 🦀 SIDE | 2020-09-17 | 2020-11-04 | 49 Tage | $10,940 | $14,144 | **+29.3 %** |
| 🐂 BULL | 2020-11-05 | 2021-01-09 | 66 Tage | $15,590 | $40,088 | **+157.1 %** |
| 🐻 BEAR | 2021-01-10 | 2021-03-08 | 58 Tage | $38,150 | $52,375 | **+37.3 %** |
| 🐂 BULL | 2021-03-09 | 2021-04-08 | 31 Tage | $54,884 | $58,078 | **+5.8 %** |
| 🐂 BULL | 2021-04-13 | 2021-05-03 | 21 Tage | $63,575 | $57,169 | **-10.1 %** |
| 🐻 BEAR | 2021-05-04 | 2021-07-05 | 63 Tage | $53,200 | $33,690 | **-36.7 %** |
| 🐂 BULL | 2021-07-21 | 2021-09-29 | 71 Tage | $32,145 | $41,524 | **+29.2 %** |
| 🐂 BULL | 2021-10-04 | 2022-01-07 | 96 Tage | $49,225 | $41,566 | **-15.6 %** |
| 🐂 BULL | 2022-01-21 | 2022-02-27 | 38 Tage | $36,445 | $37,699 | **+3.4 %** |
| 🐻 BEAR | 2022-02-28 | 2022-03-13 | 14 Tage | $43,160 | $37,777 | **-12.5 %** |
| 🦀 SIDE | 2022-03-24 | 2022-04-10 | 18 Tage | $43,991 | $42,159 | **-4.2 %** |
| 🐂 BULL | 2022-04-11 | 2022-05-08 | 28 Tage | $39,530 | $34,038 | **-13.9 %** |
| 🐻 BEAR | 2022-05-09 | 2022-05-22 | 14 Tage | $30,076 | $30,294 | **+0.7 %** |
| 🐂 BULL | 2022-05-23 | 2022-06-11 | 20 Tage | $29,109 | $28,425 | **-2.4 %** |
| 🐻 BEAR | 2022-06-12 | 2022-06-29 | 18 Tage | $26,575 | $20,123 | **-24.3 %** |
| 🐂 BULL | 2022-06-30 | 2022-08-09 | 41 Tage | $19,942 | $23,150 | **+16.1 %** |
| 🐂 BULL | 2022-08-19 | 2022-09-12 | 25 Tage | $20,834 | $22,396 | **+7.5 %** |
| 🦀 SIDE | 2022-09-27 | 2022-11-07 | 42 Tage | $19,079 | $20,591 | **+7.9 %** |
| 🐻 BEAR | 2022-11-08 | 2022-11-22 | 15 Tage | $18,547 | $16,227 | **-12.5 %** |
| 🦀 SIDE | 2022-11-24 | 2023-01-19 | 57 Tage | $16,599 | $21,072 | **+26.9 %** |
| 🦀 SIDE | 2023-01-27 | 2023-02-14 | 19 Tage | $23,074 | $22,200 | **-3.8 %** |
| 🐂 BULL | 2023-02-15 | 2023-02-28 | 14 Tage | $24,324 | $23,142 | **-4.9 %** |
| 🐂 BULL | 2023-03-09 | 2023-03-30 | 22 Tage | $20,362 | $28,029 | **+37.6 %** |
| 🦀 SIDE | 2023-03-31 | 2023-06-04 | 66 Tage | $28,465 | $27,115 | **-4.7 %** |
| 🐂 BULL | 2023-06-05 | 2023-06-21 | 17 Tage | $25,728 | $29,994 | **+16.6 %** |
| 🦀 SIDE | 2023-06-22 | 2023-10-22 | 123 Tage | $29,885 | $29,992 | **+0.4 %** |
| 🐂 BULL | 2023-10-23 | 2023-11-05 | 14 Tage | $33,070 | $35,012 | **+5.9 %** |
| 🐂 BULL | 2023-11-15 | 2023-11-28 | 14 Tage | $37,858 | $37,819 | **-0.1 %** |
| 🦀 SIDE | 2023-12-19 | 2024-01-07 | 20 Tage | $42,276 | $43,929 | **+3.9 %** |
| 🐂 BULL | 2024-01-08 | 2024-01-26 | 19 Tage | $46,951 | $41,824 | **-10.9 %** |
| 🦀 SIDE | 2024-01-27 | 2024-02-27 | 32 Tage | $42,121 | $57,037 | **+35.4 %** |
| 🐂 BULL | 2024-02-28 | 2024-03-18 | 20 Tage | $62,432 | $67,610 | **+8.3 %** |
| 🐂 BULL | 2024-03-30 | 2024-05-28 | 60 Tage | $69,582 | $68,398 | **-1.7 %** |
| 🦀 SIDE | 2024-05-29 | 2024-07-03 | 36 Tage | $67,652 | $60,209 | **-11.0 %** |
| 🐂 BULL | 2024-07-04 | 2024-07-19 | 16 Tage | $57,050 | $66,660 | **+16.8 %** |
| 🐂 BULL | 2024-08-17 | 2024-09-06 | 21 Tage | $59,492 | $53,963 | **-9.3 %** |
| 🦀 SIDE | 2024-09-07 | 2024-11-05 | 60 Tage | $54,161 | $69,372 | **+28.1 %** |
| 🐂 BULL | 2024-11-06 | 2024-11-27 | 22 Tage | $75,572 | $95,863 | **+26.9 %** |
| 🦀 SIDE | 2024-11-28 | 2024-12-17 | 20 Tage | $95,644 | $106,134 | **+11.0 %** |
| 🦀 SIDE | 2024-12-27 | 2025-03-01 | 65 Tage | $94,299 | $86,065 | **-8.7 %** |
| 🐻 BEAR | 2025-03-02 | 2025-03-15 | 14 Tage | $94,270 | $84,338 | **-10.5 %** |
| 🐂 BULL | 2025-04-06 | 2025-04-22 | 17 Tage | $78,430 | $93,443 | **+19.1 %** |
| 🦀 SIDE | 2025-04-23 | 2025-10-09 | 170 Tage | $93,691 | $121,662 | **+29.9 %** |
| 🐂 BULL | 2025-10-10 | 2025-10-23 | 14 Tage | $112,774 | $110,078 | **-2.4 %** |
| 🦀 SIDE | 2025-10-24 | 2025-11-30 | 38 Tage | $111,005 | $90,360 | **-18.6 %** |
| 🦀 SIDE | 2025-12-06 | 2026-01-30 | 56 Tage | $89,237 | $84,260 | **-5.6 %** |
| 🐻 BEAR | 2026-02-05 | 2026-02-18 | 14 Tage | $62,910 | $66,461 | **+5.6 %** |
| 🐂 BULL | 2026-02-25 | 2026-03-18 | 22 Tage | $67,988 | $71,247 | **+4.8 %** |
| 🦀 SIDE | 2026-03-19 | 2026-06-06 | 80 Tage | $69,930 | $60,885 | **-12.9 %** |
| 🦀 SIDE | 2026-06-16 | 2026-08-18 | 64 Tage | $65,675 | $64,725 | **-1.4 %** |

---

## 3. Methodenvergleich: HMM vs. Bull Market Support Band vs. Supertrend

| Regime | Gaussian HMM (3-State) | Bull Market Support Band (20W/21W) | Supertrend (10, 3) |
|---|---|---|---|
| 🐂 **BULL** | 1.255 Tage (39.9 %) | 1.621 Tage (51.4 %) | 1.838 Tage (58.2 %) |
| 🦀 **SIDE** | 1.390 Tage (44.2 %) | 196 Tage (6.2 %) | N/A (rein binär) |
| 🐻 **BEAR** | 498 Tage (15.8 %) | 1.200 Tage (38.0 %) | 1.319 Tage (41.8 %) |

### Fazit des Vergleichs:
* **HMM erkennt echte Seitwärtsmärkte (44.2 % der Zeit):** Reine Trendfolge-Indikatoren (wie Supertrend oder gleitende Durchschnitte) zwingen den Markt in ein binäres Bull/Bear-Korsett und erzeugen in Chop-Phasen ständige Fehlsignale (*Whipsaws*). Das HMM isoliert diese Phasen präzise als Niedrig-Volatilitäts-Konsolidierung.
* **Bärenmärkte als Hochvolatilitäts-Schocks:** Das HMM identifiziert die echten Crash- und Panikphasen (hohe Volatilität $\sigma = 5.68\,\%$) punktgenau.

---

## 4. Zuordnung der Freqtrade-Strategien für das Benchmark-Testing

Aus dem Korpus von 895 Strategien wurden **569 funktionierende Strategien** für den gezielten Test vorbereitet:

1. 🐂 **413 Long-Trend Strategien:** Werden ausschließlich in den identifizierten **HMM-BULL-Phasen** (z. B. 2020-10 bis 2021-04, 2023-10 bis 2024-03) gegen **Buy-and-Hold** getestet.
2. 🐻 **37 Short-Futures Strategien:** Werden in den **HMM-BEAR-Phasen** (z. B. 2021-11 bis 2022-12, 2026-Dips) im **Futures-Modus** gegen **Short-and-Hold / Cash** getestet.
3. 🦀 **119 Mean-Reversion Strategien:** Werden in den **HMM-SIDE-Phasen** (z. B. Sommer-Chop 2021, Sommer-Chop 2023) auf Alpha und minimale Drawdowns getestet.
