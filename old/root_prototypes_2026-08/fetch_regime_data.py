# -*- coding: utf-8 -*-
"""
fetch_regime_data.py - Lädt Spot- und USDT-M Futures-Candles für die Benchmark-Coins von Binance Vision herunter.
Unterstützt: BTC, ETH, SOL, XRP, ADA, DOGE, LINK, LTC (5m, 15m, 1h).
"""
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import zipfile
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "user_data", "data", "binance")
os.makedirs(DATA_DIR, exist_ok=True)

COINS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "LINKUSDT", "LTCUSDT"]
TIMEFRAMES = ["1h", "5m", "15m"]

BASE_SPOT = "https://data.binance.vision/data/spot/monthly/klines/%s/%s/%s-%s-%d-%02d.zip"
BASE_FUTURES = "https://data.binance.vision/data/futures/um/monthly/klines/%s/%s/%s-%s-%d-%02d.zip"


def download_pair_tf(symbol, tf="1h", market_type="spot", start_year=2020, end_year=2026):
    """
    Lädt monatliche Archive für ein Handelspaar herunter und speichert sie als Feather-Datei für Freqtrade.
    """
    print(f"\nLade {market_type.upper()} {symbol} ({tf}) von {start_year} bis {end_year}...", flush=True)
    all_candles = []
    
    base_template = BASE_SPOT if market_type == "spot" else BASE_FUTURES
    
    for y in range(start_year, end_year + 1):
        for m in range(1, 13):
            if y == 2020 and m < 3 and market_type == "futures":
                continue # Futures start 2020-03
            if y == 2026 and m > 8:
                continue
                
            url = base_template % (symbol, tf, symbol, tf, y, m)
            for attempt in range(2):
                try:
                    req = urllib.request.urlopen(url, timeout=20)
                    z = zipfile.ZipFile(io.BytesIO(req.read()))
                    csv_name = z.namelist()[0]
                    with z.open(csv_name) as f:
                        df_m = pd.read_csv(f, header=None)
                        for _, row in df_m.iterrows():
                            if str(row[0]).startswith("open_time") or not str(row[0]).isdigit():
                                continue
                            all_candles.append({
                                "date": int(row[0]),
                                "open": float(row[1]),
                                "high": float(row[2]),
                                "low": float(row[3]),
                                "close": float(row[4]),
                                "volume": float(row[5])
                            })
                    break
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        break
                    time.sleep(0.5)
                except Exception:
                    time.sleep(0.5)

    if not all_candles:
        print(f"  [WARNUNG] Keine Daten für {symbol} ({market_type}) gefunden.", flush=True)
        return None
        
    df = pd.DataFrame(all_candles)
    df = df.drop_duplicates(subset=["date"]).sort_values("date").reset_index(drop=True)
    df["date"] = pd.to_datetime(df["date"], unit="ms", utc=True)
    
    # Freqtrade format: BTC_USDT-1h.feather oder BTC_USDT_USDT-1h.feather für Futures
    ft_pair_name = symbol.replace("USDT", "_USDT")
    if market_type == "futures":
        ft_pair_name = symbol.replace("USDT", "_USDT:USDT")
        
    safe_name = ft_pair_name.replace(":", "_")
    out_file = os.path.join(DATA_DIR, f"{safe_name}-{tf}.feather")
    df.to_feather(out_file)
    print(f"  [OK] Gespeichert: {os.path.basename(out_file)} ({len(df)} Kerzen von {str(df['date'].iloc[0])[:10]} bis {str(df['date'].iloc[-1])[:10]})", flush=True)
    return out_file


def main():
    tf = sys.argv[1] if len(sys.argv) > 1 else "1h"
    print(f"Starte Daten-Download für {len(COINS)} Coins auf Timeframe {tf}...", flush=True)
    
    # 1. Spot
    for c in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        download_pair_tf(c, tf=tf, market_type="spot", start_year=2020, end_year=2026)
        
    # 2. Futures
    for c in ["BTCUSDT", "ETHUSDT", "SOLUSDT"]:
        download_pair_tf(c, tf=tf, market_type="futures", start_year=2020, end_year=2026)


if __name__ == "__main__":
    main()
