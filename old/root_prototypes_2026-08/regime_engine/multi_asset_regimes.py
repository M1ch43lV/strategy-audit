# -*- coding: utf-8 -*-
"""
multi_asset_regimes.py - Vergleicht 5 verschiedene Regime-Klassifikationsmethoden
über 10 Krypto-Assets (BTC, ETH, SOL, XRP, ADA, DOGE, LINK, LTC, BNB, AVAX):
1. 3-Zustands Gaussian HMM
2. Bull Market Support Band (20W SMA + 21W EMA)
3. Supertrend (10, 3)
4. Kaufman Adaptive Moving Average (KAMA) & Efficiency Ratio
5. ADX(14) & +DI/-DI Trend-System
"""
import glob
import io
import json
import os
import sys
import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from tabulate import tabulate

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "regime_engine", "data", "daily_assets")
OUTPUT_DIR = os.path.join(ROOT, "data", "multi_asset_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

ASSETS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LINKUSDT", "LTCUSDT", "BNBUSDT", "AVAXUSDT"]


def calculate_kama(close, n=10, pow_fast=2, pow_slow=30):
    """
    Kaufman Adaptive Moving Average (KAMA).
    """
    change = (close - close.shift(n)).abs()
    volatility = (close - close.shift(1)).abs().rolling(n).sum()
    er = np.where(volatility == 0, 0.0, change / volatility) # Efficiency Ratio
    
    sc_fast = 2.0 / (pow_fast + 1)
    sc_slow = 2.0 / (pow_slow + 1)
    sc = (er * (sc_fast - sc_slow) + sc_slow) ** 2 # Smoothing Constant
    
    kama = np.zeros(len(close))
    kama[0] = close.iloc[0]
    for i in range(1, len(close)):
        kama[i] = kama[i-1] + sc[i] * (close.iloc[i] - kama[i-1]) if not np.isnan(sc[i]) else close.iloc[i]
        
    return pd.Series(kama, index=close.index), pd.Series(er, index=close.index)


def process_asset(symbol):
    file_path = os.path.join(DATA_DIR, f"{symbol}_daily.csv")
    if not os.path.exists(file_path):
        return None
        
    df = pd.read_csv(file_path)
    c = df["close"]
    h = df["high"]
    l = df["low"]
    n = len(df)
    
    # 1. HMM (3-Zustände)
    df["log_ret"] = np.log(c / c.shift(1))
    df["vol_14d"] = df["log_ret"].rolling(14).std()
    
    valid_idx = df["vol_14d"].dropna().index
    df_valid = df.loc[valid_idx].copy().reset_index(drop=True)
    X = df_valid[["log_ret", "vol_14d"]].values
    
    hmm = GaussianHMM(n_components=3, covariance_type="full", n_iter=200, random_state=42)
    hmm.fit(X)
    hidden_states = hmm.predict(X)
    
    # Sortiere HMM nach Rendite
    stats = []
    for s in range(3):
        idx = (hidden_states == s)
        mean_r = df_valid.loc[idx, "log_ret"].mean()
        stats.append((s, mean_r))
    stats_sorted = sorted(stats, key=lambda x: x[1], reverse=True)
    
    label_map = {
        stats_sorted[0][0]: "BULL",
        stats_sorted[1][0]: "SIDE",
        stats_sorted[2][0]: "BEAR"
    }
    df_valid["regime_hmm"] = [label_map[s] for s in hidden_states]
    
    # 2. Bull Market Support Band (20W SMA = 140d, 21W EMA = 147d)
    sma_20w = c.rolling(140).mean()
    ema_21w = c.ewm(span=147, adjust=False).mean()
    
    reg_bmsb = []
    for close_val, sma_val, ema_val in zip(c, sma_20w, ema_21w):
        if pd.isna(sma_val) or pd.isna(ema_val):
            reg_bmsb.append("UNKNOWN")
        elif close_val > sma_val and close_val > ema_val:
            reg_bmsb.append("BULL")
        elif close_val < sma_val and close_val < ema_val:
            reg_bmsb.append("BEAR")
        else:
            reg_bmsb.append("SIDE")
    df["regime_bmsb"] = reg_bmsb

    # 3. Supertrend (10, 3) mit dynamischem Trailing-Band
    prev_close = c.shift(1).fillna(c)
    tr = pd.concat([h - l, (h - prev_close).abs(), (l - prev_close).abs()], axis=1).max(axis=1)
    atr = tr.rolling(10).mean().bfill()
    
    hl2 = (h + l) / 2.0
    basic_upper = (hl2 + (3.0 * atr)).values
    basic_lower = (hl2 - (3.0 * atr)).values
    final_upper = np.copy(basic_upper)
    final_lower = np.copy(basic_lower)
    
    close_vals = c.values
    st = np.ones(n, dtype=bool)
    
    for i in range(1, n):
        # Trailing Lower Band
        if basic_lower[i] > final_lower[i-1] or close_vals[i-1] < final_lower[i-1]:
            final_lower[i] = basic_lower[i]
        else:
            final_lower[i] = final_lower[i-1]
            
        # Trailing Upper Band
        if basic_upper[i] < final_upper[i-1] or close_vals[i-1] > final_upper[i-1]:
            final_upper[i] = basic_upper[i]
        else:
            final_upper[i] = final_upper[i-1]
            
        # Supertrend Signal
        if st[i-1]:
            st[i] = False if close_vals[i] < final_lower[i] else True
        else:
            st[i] = True if close_vals[i] > final_upper[i] else False
            
    df["regime_supertrend"] = ["BULL" if x else "BEAR" for x in st]

    # 4. KAMA & Efficiency Ratio
    kama, er = calculate_kama(c)
    df["kama"] = kama
    df["er"] = er
    
    reg_kama = []
    for close_val, kama_val, er_val in zip(c, kama, er):
        if pd.isna(er_val) or er_val < 0.20:
            reg_kama.append("SIDE") # Geringe Markteffizienz = Seitwärts / Rauschen
        elif close_val > kama_val:
            reg_kama.append("BULL")
        else:
            reg_kama.append("BEAR")
    df["regime_kama"] = reg_kama

    # 5. ADX(14) & +DI/-DI
    up = h - h.shift(1)
    down = l.shift(1) - l
    pdm = pd.Series(np.where((up > down) & (up > 0), up, 0.0))
    mdm = pd.Series(np.where((down > up) & (down > 0), down, 0.0))
    
    tr14 = tr.rolling(14).mean().replace(0, 1e-9).bfill()
    pdi = 100.0 * (pdm.rolling(14).mean().bfill() / tr14)
    mdi = 100.0 * (mdm.rolling(14).mean().bfill() / tr14)
    dx = 100.0 * ((pdi - mdi).abs() / (pdi + mdi).replace(0, 1e-9))
    adx14 = dx.rolling(14).mean().bfill()
    
    reg_adx = []
    for adx_v, pdi_v, mdi_v in zip(adx14, pdi, mdi):
        if pd.isna(adx_v) or adx_v < 20:
            reg_adx.append("SIDE") # Kein Trend
        elif pdi_v > mdi_v:
            reg_adx.append("BULL")
        else:
            reg_adx.append("BEAR")
    df["regime_adx"] = reg_adx

    # Merge HMM
    df = pd.merge(df, df_valid[["date", "regime_hmm"]], on="date", how="left")
    df["regime_hmm"] = df["regime_hmm"].fillna("UNKNOWN")
    
    # Speichern
    out_csv = os.path.join(OUTPUT_DIR, f"{symbol}_regimes.csv")
    df.to_csv(out_csv, index=False)
    
    # Metriken je Methode berechnen
    methods = ["regime_hmm", "regime_bmsb", "regime_supertrend", "regime_kama", "regime_adx"]
    method_names = {
        "regime_hmm": "Gaussian HMM (3-State)",
        "regime_bmsb": "Bull Market Support Band",
        "regime_supertrend": "Supertrend (10, 3)",
        "regime_kama": "KAMA (Adaptive Efficiency)",
        "regime_adx": "ADX(14) Trend Strength"
    }
    
    summary = {}
    for m in methods:
        counts = df[m].value_counts().to_dict()
        tot = len(df[df[m] != "UNKNOWN"])
        bull_pct = counts.get("BULL", 0) / tot * 100 if tot > 0 else 0
        side_pct = counts.get("SIDE", 0) / tot * 100 if tot > 0 else 0
        bear_pct = counts.get("BEAR", 0) / tot * 100 if tot > 0 else 0
        
        # Rendite im jeweiligen Regime
        bull_idx = (df[m] == "BULL")
        bear_idx = (df[m] == "BEAR")
        side_idx = (df[m] == "SIDE")
        
        bull_ret_ann = (np.exp(df.loc[bull_idx, "log_ret"].mean() * 365.0) - 1.0) * 100 if bull_idx.sum() > 0 else 0
        bear_ret_ann = (np.exp(df.loc[bear_idx, "log_ret"].mean() * 365.0) - 1.0) * 100 if bear_idx.sum() > 0 else 0
        side_ret_ann = (np.exp(df.loc[side_idx, "log_ret"].mean() * 365.0) - 1.0) * 100 if side_idx.sum() > 0 else 0
        
        summary[method_names[m]] = {
            "bull_pct": bull_pct,
            "side_pct": side_pct,
            "bear_pct": bear_pct,
            "bull_ann_return": bull_ret_ann,
            "bear_ann_return": bear_ret_ann,
            "side_ann_return": side_ret_ann
        }
        
    return {
        "symbol": symbol,
        "candles": n,
        "first_date": df["date"].iloc[0],
        "last_date": df["date"].iloc[-1],
        "total_asset_return": ((c.iloc[-1] / c.iloc[0]) - 1.0) * 100.0,
        "methods_summary": summary,
        "df": df
    }


def main():
    print(f"Starte Multi-Methoden-Analyse für alle {len(ASSETS)} Assets...", flush=True)
    all_summaries = {}
    asset_dfs = {}
    
    for asset in ASSETS:
        res = process_asset(asset)
        if res:
            all_summaries[asset] = res["methods_summary"]
            asset_dfs[asset] = res["df"]
            print(f"  [OK] {asset} verarbeitet ({res['candles']} Kerzen, Gesamtrendite: {res['total_asset_return']:+.1f} %)", flush=True)
            
    # 1. Großer Vergleich: HMM vs BMSB vs Supertrend vs KAMA vs ADX über die Top-Assets
    print("\n" + "="*95)
    print("METHODEN-VERGLEICH ÜBER BTC, ETH, SOL & TOP-ALTCOINS (% ZEIT IN JEDEM REGIME)")
    print("="*95)
    
    for method_name in ["Gaussian HMM (3-State)", "Bull Market Support Band", "Supertrend (10, 3)", "KAMA (Adaptive Efficiency)", "ADX(14) Trend Strength"]:
        print(f"\n▶ Methode: {method_name}")
        t_rows = []
        for asset in ASSETS:
            if asset in all_summaries and method_name in all_summaries[asset]:
                s = all_summaries[asset][method_name]
                t_rows.append([
                    asset.replace("USDT", ""),
                    f"{s['bull_pct']:.1f} % (Ø {s['bull_ann_return']:+.0f}% p.a.)",
                    f"{s['side_pct']:.1f} % (Ø {s['side_ann_return']:+.0f}% p.a.)",
                    f"{s['bear_pct']:.1f} % (Ø {s['bear_ann_return']:+.0f}% p.a.)"
                ])
        print(tabulate(t_rows, headers=["Asset", "🐂 BULL Phase", "🦀 SIDE Phase", "🐻 BEAR Phase"], tablefmt="grid"))
        
    # 2. Altcoin vs BTC Regime-Synchronizität (Korrelation mit BTC HMM)
    print("\n" + "="*95)
    print("ALTCOIN vs. BTC REGIME-SYNCHRONIZITÄT (WIE SEHR FOLGEN ALTCOINS BITCOIN?)")
    print("="*95)
    
    btc_df = asset_dfs["BTCUSDT"].set_index("date")
    sync_rows = []
    
    for asset in ASSETS:
        if asset == "BTCUSDT":
            continue
        cur_df = asset_dfs[asset].set_index("date")
        merged = pd.merge(btc_df[["regime_hmm", "log_ret"]], cur_df[["regime_hmm", "log_ret"]], left_index=True, right_index=True, suffixes=("_btc", f"_{asset}"))
        
        # Übereinstimmungsquote
        same_regime_pct = (merged["regime_hmm_btc"] == merged[f"regime_hmm_{asset}"]).mean() * 100.0
        
        # Rendite des Altcoins, wenn BTC im Bullenmarkt ist
        btc_bull = (merged["regime_hmm_btc"] == "BULL")
        alt_ret_in_btc_bull = (np.exp(merged.loc[btc_bull, f"log_ret_{asset}"].mean() * 365.0) - 1.0) * 100.0
        
        # Rendite des Altcoins, wenn BTC im Bärenmarkt ist
        btc_bear = (merged["regime_hmm_btc"] == "BEAR")
        alt_ret_in_btc_bear = (np.exp(merged.loc[btc_bear, f"log_ret_{asset}"].mean() * 365.0) - 1.0) * 100.0
        
        sync_rows.append([
            asset.replace("USDT", ""),
            f"{same_regime_pct:.1f} %",
            f"{alt_ret_in_btc_bull:+.1f} % p.a.",
            f"{alt_ret_in_btc_bear:+.1f} % p.a.",
            "Extremer Hebel auf BTC-Bull" if alt_ret_in_btc_bull > 150 else "Moderat"
        ])
        
    print(tabulate(sync_rows, headers=["Altcoin", "HMM Regime Sync mit BTC", "Altcoin Ertrag in BTC-BULL", "Altcoin Ertrag in BTC-BEAR", "Charakteristik"], tablefmt="grid"))
    
    # Speichern der Zusammenfassung
    with open(os.path.join(OUTPUT_DIR, "multi_asset_regimes_summary.json"), "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2)


if __name__ == "__main__":
    main()
