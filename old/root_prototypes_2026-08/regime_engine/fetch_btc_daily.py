# -*- coding: utf-8 -*-
"""
fetch_btc_daily.py - Lädt tägliche BTC/USDT Klines von 2018 bis 2026 blitzschnell via Binance REST API.
"""
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_all_daily_candles(symbol="BTCUSDT"):
    print(f"Lade tägliche {symbol} Klines via Binance REST API (2018 bis heute)...", flush=True)
    start_time = int(pd.Timestamp("2018-01-01", tz="UTC").timestamp() * 1000)
    end_time = int(time.time() * 1000)
    
    all_candles = []
    current_start = start_time
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    while current_start < end_time:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1d&startTime={current_start}&limit=1000"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
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
                # Setze nächsten Start auf den Timestamp der letzten Kerze + 1 Tag (86400000 ms)
                last_ts = int(data[-1][0])
                if last_ts <= current_start:
                    break
                current_start = last_ts + 86400000
                print(f"  -> {len(all_candles)} Kerzen geladen (bis {pd.to_datetime(last_ts, unit='ms', utc=True).strftime('%Y-%m-%d')})...", flush=True)
                time.sleep(0.1)
        except Exception as e:
            print(f"Fehler beim Abruf: {e}", flush=True)
            # Versuche Binance Vision Mirror wenn api.binance.com blockiert ist
            url_mirror = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=1d&startTime={current_start}&limit=1000"
            try:
                req = urllib.request.Request(url_mirror, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as resp:
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
                    current_start = last_ts + 86400000
            except Exception as e2:
                print(f"Mirror Fehler: {e2}", flush=True)
                break

    df = pd.DataFrame(all_candles)
    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.strftime("%Y-%m-%d")
    
    out_file = os.path.join(DATA_DIR, "btc_daily_2018_2026.csv")
    df.to_csv(out_file, index=False)
    print(f"\n[OK] Fertig! {len(df)} Tageskerzen von {df['date'].iloc[0]} bis {df['date'].iloc[-1]} in {out_file} gespeichert.", flush=True)
    return out_file

if __name__ == "__main__":
    fetch_all_daily_candles()
