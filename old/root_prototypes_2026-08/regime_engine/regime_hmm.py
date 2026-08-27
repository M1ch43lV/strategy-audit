# -*- coding: utf-8 -*-
"""
regime_hmm.py - 3-Zustands Gaussian Hidden Markov Model (HMM) zur quantitativen
Erkennung von Krypto-Marktphasen (Bull, Side, Bear) auf täglichen Bitcoin-Daten.
"""
import os
import sys
import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from tabulate import tabulate

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
INPUT_FILE = os.path.join(DATA_DIR, "btc_daily_2018_2026.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "btc_regimes_master.csv")


def calculate_technical_indicators(df):
    """
    Berechnet die wichtigsten krypto-spezifischen Indikatoren:
    1. Bull Market Support Band (20W SMA & 21W EMA auf Tagesbasis: 140d & 147d)
    2. Supertrend (10, 3)
    3. ADX(14)
    """
    c = df["close"]
    h = df["high"]
    l = df["low"]
    
    # 1. Bull Market Support Band
    df["sma_20w"] = c.rolling(140).mean()
    df["ema_21w"] = c.ewm(span=147, adjust=False).mean()
    
    reg_bmsb = []
    for close_val, sma_val, ema_val in zip(c, df["sma_20w"], df["ema_21w"]):
        if pd.isna(sma_val) or pd.isna(ema_val):
            reg_bmsb.append("UNKNOWN")
        elif close_val > sma_val and close_val > ema_val:
            reg_bmsb.append("BULL")
        elif close_val < sma_val and close_val < ema_val:
            reg_bmsb.append("BEAR")
        else:
            reg_bmsb.append("SIDE")
    df["regime_bmsb"] = reg_bmsb

    # 2. ATR & Supertrend (10, 3)
    prev_close = c.shift(1).fillna(c)
    tr = pd.concat([h - l, (h - prev_close).abs(), (l - prev_close).abs()], axis=1).max(axis=1)
    atr = tr.rolling(10).mean().bfill()
    df["atr_10"] = atr
    
    hl2 = (h + l) / 2.0
    upper_band = hl2 + (3.0 * atr)
    lower_band = hl2 - (3.0 * atr)
    
    st = [True] * len(df)
    for i in range(1, len(df)):
        if st[i-1]:
            st[i] = False if c.iloc[i] < lower_band.iloc[i] else True
        else:
            st[i] = True if c.iloc[i] > upper_band.iloc[i] else False
    df["regime_supertrend"] = ["BULL" if x else "BEAR" for x in st]

    # 3. ADX (14)
    up = h - h.shift(1)
    down = l.shift(1) - l
    pdm = pd.Series(np.where((up > down) & (up > 0), up, 0.0))
    mdm = pd.Series(np.where((down > up) & (down > 0), down, 0.0))
    
    tr14 = tr.rolling(14).mean().replace(0, 1e-9).bfill()
    pdi = 100.0 * (pdm.rolling(14).mean().bfill() / tr14)
    mdi = 100.0 * (mdm.rolling(14).mean().bfill() / tr14)
    dx = 100.0 * ((pdi - mdi).abs() / (pdi + mdi).replace(0, 1e-9))
    df["adx_14"] = dx.rolling(14).mean().bfill()

    return df


def train_hmm_model(df):
    """
    Trainiert ein 3-Zustands Gaussian HMM auf täglichen Log-Renditen und rollierender Volatilität.
    (Geändert auf Walk-Forward zur Vermeidung von Lookahead-Bias)
    """
    df["log_ret"] = np.log(df["close"] / df["close"].shift(1))
    df["vol_14d"] = df["log_ret"].rolling(14).std()
    
    valid_idx = df["vol_14d"].dropna().index
    df_clean = df.loc[valid_idx].copy().reset_index(drop=True)
    
    X = df_clean[["log_ret", "vol_14d"]].values
    
    n_samples = len(X)
    window_size = 365
    min_history = 365
    n_states = 3
    
    states_labels = ["UNKNOWN"] * n_samples
    prob_bull = np.zeros(n_samples)
    prob_side = np.zeros(n_samples)
    prob_bear = np.zeros(n_samples)
    
    print("Trainiere rollierendes Walk-Forward HMM (Fenster: 365 Tage)...", flush=True)
    
    for T in range(min_history, n_samples - 1):
        train_start = max(0, T - window_size)
        train_end = T + 1
        train_data = X[train_start:train_end]
        
        model = GaussianHMM(
            n_components=n_states,
            covariance_type="full",
            n_iter=100,
            random_state=42
        )
        try:
            model.fit(train_data)
            hidden_states_train = model.predict(train_data)
            
            stats = []
            for s in range(n_states):
                idx = (hidden_states_train == s)
                if idx.sum() == 0:
                    mean_ret = 0
                else:
                    mean_ret = train_data[idx, 0].mean()
                stats.append({"raw_id": s, "mean_ret": mean_ret})
                
            stats_sorted = sorted(stats, key=lambda x: x["mean_ret"], reverse=True)
            label_map = {
                stats_sorted[0]["raw_id"]: "BULL",
                stats_sorted[1]["raw_id"]: "SIDE",
                stats_sorted[2]["raw_id"]: "BEAR"
            }
            
            last_state = hidden_states_train[-1]
            state_probs_next = model.transmat_[last_state, :]
            next_state = np.argmax(state_probs_next)
            
            states_labels[T + 1] = label_map[next_state]
            
            for s in range(n_states):
                lbl = label_map[s]
                if lbl == "BULL": prob_bull[T + 1] += state_probs_next[s]
                elif lbl == "SIDE": prob_side[T + 1] += state_probs_next[s]
                elif lbl == "BEAR": prob_bear[T + 1] += state_probs_next[s]
        except Exception as e:
            # Wenn das Modell nicht konvergiert oder transmat_ kaputt ist,
            # behalte UNKNOWN (Default) oder übernehme den vorherigen Wert.
            if T > 0 and states_labels[T] != "UNKNOWN":
                states_labels[T + 1] = states_labels[T]
                prob_bull[T + 1] = prob_bull[T]
                prob_side[T + 1] = prob_side[T]
                prob_bear[T + 1] = prob_bear[T]
            continue

    df_clean["regime_hmm"] = states_labels
    df_clean["prob_bull"] = prob_bull
    df_clean["prob_side"] = prob_side
    df_clean["prob_bear"] = prob_bear
    
    # Merge zurück
    df_merged = pd.merge(df, df_clean[["date", "regime_hmm", "prob_bull", "prob_side", "prob_bear"]], on="date", how="left")
    df_merged["regime_hmm"] = df_merged["regime_hmm"].fillna("UNKNOWN")
    return df_merged, None, None


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Fehler: {INPUT_FILE} existiert nicht.")
        sys.exit(1)
        
    df = pd.read_csv(INPUT_FILE)
    print(f"Lese {len(df)} Tageskerzen von {df['date'].iloc[0]} bis {df['date'].iloc[-1]}...", flush=True)
    
    df = calculate_technical_indicators(df)
    df_out, model, state_map = train_hmm_model(df)
    
    df_out.to_csv(OUTPUT_FILE, index=False)
    print(f"\n[OK] Ergebnis-Datensatz gespeichert: {OUTPUT_FILE}", flush=True)
    
    # Jahresweise Aufschlüsselung
    df_out["year"] = pd.to_datetime(df_out["date"]).dt.year
    year_summary = []
    for y, g in df_out.groupby("year"):
        counts = g["regime_hmm"].value_counts().to_dict()
        n_bull = counts.get("BULL", 0)
        n_side = counts.get("SIDE", 0)
        n_bear = counts.get("BEAR", 0)
        tot = len(g)
        mkt_ret = ((g["close"].iloc[-1] / g["close"].iloc[0]) - 1) * 100.0
        year_summary.append([
            y,
            f"{mkt_ret:+.1f} %",
            f"{n_bull} ({n_bull/tot*100:.0f}%)",
            f"{n_side} ({n_side/tot*100:.0f}%)",
            f"{n_bear} ({n_bear/tot*100:.0f}%)",
        ])
    print("\n" + "="*75, flush=True)
    print("JAHRESWEISE REGIME-AUFTEILUNG NACH HMM (2018 - 2026)", flush=True)
    print("="*75, flush=True)
    print(tabulate(year_summary, headers=["Jahr", "BTC Rendite", "Bull Tage", "Side Tage", "Bear Tage"], tablefmt="grid"), flush=True)


if __name__ == "__main__":
    main()
