# -*- coding: utf-8 -*-
"""
regime_report.py - Analysiert die HMM- und technischen Regime-Ergebnisse aus btc_regimes_master.csv,
erstellt konkrete zusammenhängende Zeitblöcke für das Backtesting und generiert den historischen
HMM-Prototypbericht unter old/hmm_prototype_2026-08/.
"""
import io
import json
import os
import sys
import pandas as pd
from tabulate import tabulate

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT, "data", "btc_regimes_master.csv")
REPORT_MD = os.path.join(
    ROOT, "old", "hmm_prototype_2026-08", "REGIME_ANALYSIS_SUMMARY.md"
)


def extract_contiguous_blocks(df, col="regime_hmm", min_days=7):
    """
    Findet zusammenhängende Regime-Blöcke (z. B. mindestens 7 aufeinanderfolgende Tage im selben Regime).
    """
    blocks = []
    curr_regime = None
    start_date = None
    start_price = None
    count = 0
    
    for i, row in df.iterrows():
        r = row[col]
        d = row["date"]
        p = row["close"]
        
        if r != curr_regime:
            if curr_regime is not None and count >= min_days:
                end_date = df.iloc[i-1]["date"]
                end_price = df.iloc[i-1]["close"]
                ret = ((end_price / start_price) - 1.0) * 100.0
                blocks.append({
                    "regime": curr_regime,
                    "start_date": start_date,
                    "end_date": end_date,
                    "days": count,
                    "start_price": start_price,
                    "end_price": end_price,
                    "btc_return_pct": ret
                })
            curr_regime = r
            start_date = d
            start_price = p
            count = 1
        else:
            count += 1
            
    # Letzter Block
    if curr_regime is not None and count >= min_days:
        end_date = df.iloc[-1]["date"]
        end_price = df.iloc[-1]["close"]
        ret = ((end_price / start_price) - 1.0) * 100.0
        blocks.append({
            "regime": curr_regime,
            "start_date": start_date,
            "end_date": end_date,
            "days": count,
            "start_price": start_price,
            "end_price": end_price,
            "btc_return_pct": ret
        })
        
    return blocks


def main():
    os.makedirs(os.path.dirname(REPORT_MD), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        print(f"Fehler: {DATA_FILE} existiert nicht.")
        sys.exit(1)
        
    df = pd.read_csv(DATA_FILE)
    print(f"Lese {len(df)} Zeilen aus btc_regimes_master.csv...")
    
    # 1. Kontigente HMM Blöcke
    blocks = extract_contiguous_blocks(df, col="regime_hmm", min_days=14)
    df_blocks = pd.DataFrame(blocks)
    
    # Sortiere nach Dauer / Relevanz
    bull_blocks = [b for b in blocks if b["regime"] == "BULL"]
    bear_blocks = [b for b in blocks if b["regime"] == "BEAR"]
    side_blocks = [b for b in blocks if b["regime"] == "SIDE"]
    
    print("\n" + "="*85)
    print("HAUPT-MARKTREGIMES NACH 3-ZUSTANDS HMM (MIN. 14 TAGE DAUER)")
    print("="*85)
    
    table_rows = []
    for b in sorted(blocks, key=lambda x: x["start_date"]):
        reg_emoji = "🐂 BULL" if b["regime"] == "BULL" else ("🐻 BEAR" if b["regime"] == "BEAR" else "🦀 SIDE")
        table_rows.append([
            reg_emoji,
            b["start_date"],
            b["end_date"],
            f"{b['days']} Tage",
            f"${b['start_price']:,.0f}",
            f"${b['end_price']:,.0f}",
            f"{b['btc_return_pct']:+.1f} %"
        ])
    print(tabulate(table_rows, headers=["Regime", "Start", "Ende", "Dauer", "Startpreis", "Endpreis", "BTC Ertrag"], tablefmt="grid"))
    
    # 2. Vergleich HMM vs BMSB vs Supertrend
    comp_data = []
    for reg in ["BULL", "SIDE", "BEAR"]:
        hmm_count = (df["regime_hmm"] == reg).sum()
        bmsb_count = (df["regime_bmsb"] == reg).sum()
        st_count = (df["regime_supertrend"] == reg).sum()
        comp_data.append([
            reg,
            f"{hmm_count} Tage ({hmm_count/len(df)*100:.1f}%)",
            f"{bmsb_count} Tage ({bmsb_count/len(df)*100:.1f}%)",
            f"{st_count} Tage ({st_count/len(df)*100:.1f}%)" if reg != "SIDE" else "N/A (Binär)"
        ])
    print("\n" + "="*85)
    print("METHODEN-VERGLEICH DER REGIME-VERTEILUNG (2018 - 2026)")
    print("="*85)
    print(tabulate(comp_data, headers=["Regime", "Gaussian HMM", "Bull Market Support Band", "Supertrend (10,3)"], tablefmt="grid"))

    # Markdown Report schreiben
    md_content = f"""# Analysebericht: Krypto-Marktphasen & HMM-Modellierung (2018–2026)

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
"""
    for b in sorted(blocks, key=lambda x: x["start_date"]):
        em = "🐂 BULL" if b["regime"] == "BULL" else ("🐻 BEAR" if b["regime"] == "BEAR" else "🦀 SIDE")
        md_content += f"| {em} | {b['start_date']} | {b['end_date']} | {b['days']} Tage | ${b['start_price']:,.0f} | ${b['end_price']:,.0f} | **{b['btc_return_pct']:+.1f} %** |\n"

    md_content += """
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
"""

    with open(REPORT_MD, "w", encoding="utf-8") as f:
        f.write(md_content)
        
    print(f"\n[OK] Analysebericht erfolgreich erstellt: {REPORT_MD}")


if __name__ == "__main__":
    main()
