# -*- coding: utf-8 -*-
"""
fetch_multi_tf_candles_fast.py - Paralleler Multi-Thread Downloader für 1h, 15m und 5m Candles.
Lädt über mehrere Threads die Kerzen für BTC, ETH, SOL, XRP, ADA, AVAX, LINK, DOGE herunter.
"""
import concurrent.futures
import io
import json
import os
import sys
import time
import urllib.request
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "candles")
os.makedirs(DATA_DIR, exist_ok=True)

COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "DOGEUSDT"]
TIMEFRAMES = ["1h", "15m", "5m"]


def fetch_symbol_tf(symbol, tf="1h"):
    limit_days = 3150 # approx 8.6 years
    out_file = os.path.join(DATA_DIR, f"{symbol}_{tf}.csv")
    if os.path.exists(out_file):
        try:
            df_old = pd.read_csv(out_file, nrows=1)
            first_year = int(str(df_old["date"].iloc[0])[:4])
            if first_year <= 2020:
                return f"{symbol} {tf}: [CACHE VORHANDEN (komplett)]"
        except:
            pass

    start_time = int((time.time() - (limit_days * 86400)) * 1000)
    end_time = int(time.time() * 1000)
    
    all_candles = []
    current_start = start_time
    headers = {"User-Agent": "Mozilla/5.0"}
    
    tf_ms = 3600000 if tf == "1h" else (900000 if tf == "15m" else 300000)
    
    while current_start < end_time:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&startTime={current_start}&limit=1000"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                if not data:
                    break
                for row in data:
                    all_candles.append({
                        "timestamp": int(row[0]),
                        "open": float(row[1]),
                        "high": float(row[2]),
                        "low": float(row[3]),
                        "close": float(row[4]),
                        "volume": float(row[5])
                    })
                last_ts = int(data[-1][0])
                if last_ts <= current_start:
                    break
                current_start = last_ts + tf_ms
        except Exception:
            break

    if not all_candles:
        return f"{symbol} {tf}: [KEINE DATEN]"
        
    df = pd.DataFrame(all_candles)
    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(out_file, index=False)
    return f"{symbol} {tf}: [OK] {len(df)} Kerzen ({df['date'].iloc[0][:10]} bis {df['date'].iloc[-1][:10]})"


def main():
    print(f"Starte parallelen Download für {len(COINS)} Coins über {TIMEFRAMES}...", flush=True)
    tasks = []
    for tf in TIMEFRAMES:
        for symbol in COINS:
            tasks.append((symbol, tf))
            
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_symbol_tf, sym, tf): (sym, tf) for sym, tf in tasks}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            print(f"  {res}", flush=True)
            
    print("\n[OK] Paralleler Multi-Timeframe Download abgeschlossen!", flush=True)


if __name__ == "__main__":
    main()
