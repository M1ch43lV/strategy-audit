import json
import os
import sys
import pandas as pd
from datetime import datetime

def evaluate_trades_by_regime(trades_file, regimes_file):
    if not os.path.exists(trades_file):
        print(f"Error: {trades_file} not found.")
        return
    if not os.path.exists(regimes_file):
        print(f"Error: {regimes_file} not found. Run multi_asset_regimes.py first.")
        return

    print(f"Lade Trades aus {trades_file}...")
    with open(trades_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Freqtrade backtest export structure varies slightly, usually data['strategy_name']['trades']
    strategy_name = list(data['strategy'].keys())[0]
    trades = data['strategy'][strategy_name]['trades']
    
    print(f"Lade ADX-Regimes aus {regimes_file}...")
    regimes_df = pd.read_csv(regimes_file)
    regimes_df['date'] = pd.to_datetime(regimes_df['date']).dt.date
    regime_map = dict(zip(regimes_df['date'], regimes_df['regime_adx']))

    results = {
        "BULL": {"count": 0, "profit_pct": 0.0},
        "BEAR": {"count": 0, "profit_pct": 0.0},
        "SIDE": {"count": 0, "profit_pct": 0.0},
        "UNKNOWN": {"count": 0, "profit_pct": 0.0}
    }

    print(f"\nAnalysiere {len(trades)} Trades für Strategie: {strategy_name}...")
    
    for t in trades:
        # Freqtrade open_date format: "2024-01-01 10:00:00+00:00" or similar
        open_time = pd.to_datetime(t['open_date'])
        trade_date = open_time.date()
        
        regime = regime_map.get(trade_date, "UNKNOWN")
        profit_pct = t.get('profit_ratio', 0.0) * 100.0  # Convert to percent
        
        results[regime]["count"] += 1
        results[regime]["profit_pct"] += profit_pct

    # Summary
    print("\n" + "="*50)
    print(f"ADX REGIME PERFORMANCE: {strategy_name}")
    print("="*50)
    
    for regime in ["BULL", "BEAR", "SIDE"]:
        count = results[regime]["count"]
        total_profit = results[regime]["profit_pct"]
        avg_profit = total_profit / count if count > 0 else 0.0
        
        print(f"Regime {regime.ljust(5)} | Trades: {str(count).rjust(4)} | Ø Rendite: {avg_profit:+.2f}% | Gesamt: {total_profit:+.2f}%")
        
    print("="*50)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python evaluate_adx_trades.py <backtest-result.json> <BTCUSDT_regimes.csv>")
        sys.exit(1)
        
    evaluate_trades_by_regime(sys.argv[1], sys.argv[2])
