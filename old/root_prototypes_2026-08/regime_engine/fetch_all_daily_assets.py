# -*- coding: utf-8 -*-
"""
fetch_all_daily_assets.py - Lädt tägliche Candles für das gesamte Krypto-Universum herunter:
BTC, ETH, SOL, XRP, ADA, DOGE, LINK, LTC, BNB, AVAX.
"""
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data", "daily_assets")
os.makedirs(DATA_DIR, exist_ok=True)

ASSETS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", 
    "ADAUSDT", "DOGEUSDT", "LINKUSDT", "LTCUSDT", 
    "BNBUSDT", "AVAXUSDT"
]

def fetch_asset_daily(symbol):
    print(f"Lade tägliche Klines für {symbol}...", flush=True)
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
                last_ts = int(data[-1][0])
                if last_ts <= current_start:
                    break
                current_start = last_ts + 86400000
                time.sleep(0.05)
        except Exception as e:
            # Fallback Binance Vision Mirror
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
            except Exception:
                break

    if not all_candles:
        print(f"  [WARNUNG] Keine Daten für {symbol} erhalten.", flush=True)
        return None

    df = pd.DataFrame(all_candles)
    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.strftime("%Y-%m-%d")
    
    out_file = os.path.join(DATA_DIR, f"{symbol}_daily.csv")
    df.to_csv(out_file, index=False)
    print(f"  [OK] {symbol}: {len(df)} Kerzen von {df['date'].iloc[0]} bis {df['date'].iloc[-1]}", flush=True)
    return out_file

def main():
    print(f"Starte Download für {len(ASSETS)} Top-Krypto-Assets...", flush=True)
    for asset in ASSETS:
        fetch_asset_daily(asset)
    print("\n[OK] Alle Asset-Candles erfolgreich geladen!", flush=True)

if __name__ == "__main__":
    main()
