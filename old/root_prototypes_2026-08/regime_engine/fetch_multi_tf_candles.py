# -*- coding: utf-8 -*-
"""
fetch_multi_tf_candles.py - Lädt 1h, 15m und 5m Candles für die Top-Coins herunter:
BTCUSDT, ETHUSDT, SOLUSDT, XRPUSDT, ADAUSDT, DOGEUSDT, LINKUSDT, AVAXUSDT.
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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data", "candles")
os.makedirs(DATA_DIR, exist_ok=True)

COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "LINKUSDT", "DOGEUSDT"]
TIMEFRAMES = ["1h", "15m", "5m"]

def fetch_candles(symbol, tf="1h", limit_days=750):
    """
    Lädt historische Candles über Binance REST API mit Paging herunter.
    limit_days=750 deckt ~2 Jahre für intensive 5m/15m/1h Backtests ab.
    """
    out_file = os.path.join(DATA_DIR, f"{symbol}_{tf}.csv")
    if os.path.exists(out_file) and os.path.getsize(out_file) > 100000:
        print(f"  [CACHE] {symbol} {tf} bereits vorhanden.", flush=True)
        return out_file

    print(f"Lade {symbol} ({tf}) über Binance API...", flush=True)
    # Startzeit: z.B. 2022 bis 2026
    start_time = int((time.time() - (limit_days * 86400)) * 1000)
    end_time = int(time.time() * 1000)
    
    all_candles = []
    current_start = start_time
    headers = {"User-Agent": "Mozilla/5.0"}
    
    while current_start < end_time:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={tf}&startTime={current_start}&limit=1000"
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
                # Schrittweite je nach TF
                tf_ms = 3600000 if tf == "1h" else (900000 if tf == "15m" else 300000)
                current_start = last_ts + tf_ms
                time.sleep(0.04)
        except Exception:
            # Mirror Fallback
            url_mirror = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval={tf}&startTime={current_start}&limit=1000"
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
                    tf_ms = 3600000 if tf == "1h" else (900000 if tf == "15m" else 300000)
                    current_start = last_ts + tf_ms
            except Exception:
                break

    if not all_candles:
        print(f"  [WARNUNG] Keine Daten für {symbol} ({tf}).", flush=True)
        return None
        
    df = pd.DataFrame(all_candles)
    df = df.drop_duplicates(subset=["timestamp"]).sort_values("timestamp").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True).dt.strftime("%Y-%m-%d %H:%M:%S")
    df.to_csv(out_file, index=False)
    print(f"  [OK] {symbol} {tf}: {len(df)} Kerzen ({df['date'].iloc[0][:10]} bis {df['date'].iloc[-1][:10]})", flush=True)
    return out_file

def main():
    print(f"Starte Candle-Download für {len(COINS)} Coins über {TIMEFRAMES}...", flush=True)
    for tf in ["1h", "15m", "5m"]:
        for symbol in COINS:
            fetch_candles(symbol, tf=tf, limit_days=750)
    print("\n[OK] Alle Multi-Timeframe Candles heruntergeladen!", flush=True)

if __name__ == "__main__":
    main()
