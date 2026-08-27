# -*- coding: utf-8 -*-
"""
regime_harness.py - Führt die regime-differenzierte Evaluierung und das Benchmarking
aller 569 lauffähigen Freqtrade-Strategien über die identifizierten HMM-Marktphasen durch.
"""
import io
import json
import os
import sys
import numpy as np
import pandas as pd
from tabulate import tabulate

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
MAP_FILE = os.path.join(ROOT, "data", "STRATEGY_REGIME_MAP.json")
REGIMES_FILE = os.path.join(ROOT, "data", "btc_regimes_master.csv")
OUTPUT_CSV = os.path.join(ROOT, "data", "REGIME_BENCHMARK_RESULTS.csv")


def evaluate_regime_performance(strats, category):
    """
    Evaluiert die Leistung der Strategien unter Berücksichtigung ihrer jeweiligen Ziel-Marktphase.
    """
    results = []
    
    for s in strats:
        strat_name = s["strategy"]
        repo = s["repo"]
        sub_type = s["sub_type"]
        
        is_trades = float(s["is_trades"]) if s["is_trades"] is not None else 0
        is_exp = float(s["is_exp"]) if s["is_exp"] is not None else 0.0
        is_p = float(s["is_p"]) if s["is_p"] is not None else 1.0
        
        os_trades = float(s["os_trades"]) if s["os_trades"] is not None else 0
        os_exp = float(s["os_exp"]) if s["os_exp"] is not None else 0.0
        os_p = float(s["os_p"]) if s["os_p"] is not None else 1.0
        os_avg_pct = float(s["os_avg_pct"]) if s["os_avg_pct"] is not None else 0.0
        
        lookahead = s.get("lookahead", "clean")
        recursive = s.get("recursive", "clean")
        traps = s.get("traps", "")
        
        # Qualitäts-Gates
        is_lookahead_clean = (lookahead == "clean" or lookahead == "ПРОШЛА" or pd.isna(lookahead))
        is_recursive_clean = (recursive == "clean" or recursive == "ПРОШЛА" or pd.isna(recursive))
        is_traps_clean = (traps == "" or traps == "0" or pd.isna(traps))
        
        # 2x Cost Survival (Bleibt der Ertrag nach Verdopplung von Gebühren/Slippage > 0?)
        # 0.1% pro Seite = 0.2% roundtrip; 2x cost = 0.4% roundtrip
        cost_2x_profit = os_avg_pct - 0.20
        survives_2x_cost = (cost_2x_profit > 0 and os_trades >= 30)
        
        is_significant = (os_p < 0.05 and os_trades >= 30)
        
        # Regime-Spezifische Bewertung (einheitliche harte Kriterien)
        passed_hard_criteria = survives_2x_cost and is_significant and is_lookahead_clean and is_recursive_clean
        
        if category == "long_trend":
            target_regime = "🐂 BULL (Uptrend)"
            # Benchmark im Bullenmarkt: Out-of-Sample Buy & Hold (+346%)
            # Im Bullenmarkt zählt positiver Ertrag pro Trade und Signifikanz
            regime_score = os_avg_pct * np.log10(max(os_trades, 1)) if os_avg_pct > 0 else os_avg_pct
            verdict = "PASSED BULL AUDIT" if passed_hard_criteria else "FAILED"
        elif category == "short_futures":
            target_regime = "🐻 BEAR (Downtrend / Futures)"
            # Im Bärenmarkt zählt Kapitalschutz / Short-Gewinn
            regime_score = (os_exp if os_exp > 0 else 0.0) + (1.0 if s.get("is_short_futures_recovered") else 0.0)
            verdict = "FUTURES READY" if passed_hard_criteria else "FAILED"
        else: # mean_reversion
            target_regime = "🦀 SIDE (Chop / Range)"
            # In Seitwärtsmärkten zählt konstante Win-Rate und positiver Ertrag bei geringem Drawdown
            regime_score = os_avg_pct if os_avg_pct > 0 else os_avg_pct
            verdict = "PASSED SIDE AUDIT" if passed_hard_criteria else "FAILED"
            
        results.append({
            "strategy": strat_name,
            "category": category,
            "sub_type": sub_type,
            "target_regime": target_regime,
            "repo": repo,
            "os_trades": int(os_trades),
            "os_avg_pct": os_avg_pct,
            "cost_2x_profit_pct": cost_2x_profit,
            "os_p_value": os_p,
            "is_significant": is_significant,
            "lookahead_clean": is_lookahead_clean,
            "recursive_clean": is_recursive_clean,
            "traps_clean": is_traps_clean,
            "survives_2x_cost": survives_2x_cost,
            "regime_score": regime_score,
            "verdict": verdict
        })
        
    return results


def main():
    if not os.path.exists(MAP_FILE):
        print(f"Fehler: {MAP_FILE} existiert nicht.")
        sys.exit(1)
        
    with open(MAP_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    cats = data["categories"]
    
    print(f"Starte Multi-Regime Benchmark für {data['summary']['working_strategies_count']} Strategien...", flush=True)
    
    all_results = []
    
    # 1. Long Trend
    long_res = evaluate_regime_performance(cats["long_trend"], "long_trend")
    all_results.extend(long_res)
    
    # 2. Short Futures
    short_res = evaluate_regime_performance(cats["short_futures"], "short_futures")
    all_results.extend(short_res)
    
    # 3. Mean Reversion
    range_res = evaluate_regime_performance(cats["mean_reversion"], "mean_reversion")
    all_results.extend(range_res)
    
    df_res = pd.DataFrame(all_results)
    df_res.to_csv(OUTPUT_CSV, index=False)
    print(f"\n[OK] Gesamtergebnis gespeichert in: {OUTPUT_CSV}")
    
    # Top Überlebende nach Kategorie
    print("\n" + "="*85)
    print("TOP ÜBERLEBENDE STRATEGIEN NACH REGIME-KATEGORIE")
    print("="*85)
    
    # Top 5 Long Trend
    print("\n🐂 TOP 5 LONG-TREND STRATEGIEN (BULL REGIME):")
    long_top = df_res[df_res["category"] == "long_trend"].sort_values("os_avg_pct", ascending=False).head(5)
    long_table = [[r["strategy"], r["repo"], f"{r['os_trades']} Trades", f"{r['os_avg_pct']:+.2f} %", f"{r['cost_2x_profit_pct']:+.2f} %", f"p={r['os_p_value']:.4f}", r["verdict"]] for _, r in long_top.iterrows()]
    print(tabulate(long_table, headers=["Strategie", "Repository", "Trades", "Ø Trade %", "2x Cost %", "p-Value", "Status"], tablefmt="grid"))

    # Top 5 Mean Reversion
    print("\n🦀 TOP 5 MEAN-REVERSION & RANGE STRATEGIEN (SIDE/CHOP REGIME):")
    side_top = df_res[df_res["category"] == "mean_reversion"].sort_values("os_avg_pct", ascending=False).head(5)
    side_table = [[r["strategy"], r["repo"], f"{r['os_trades']} Trades", f"{r['os_avg_pct']:+.2f} %", f"{r['cost_2x_profit_pct']:+.2f} %", f"p={r['os_p_value']:.4f}", r["verdict"]] for _, r in side_top.iterrows()]
    print(tabulate(side_table, headers=["Strategie", "Repository", "Trades", "Ø Trade %", "2x Cost %", "p-Value", "Status"], tablefmt="grid"))

    # Top Short / Futures
    print("\n🐻 TOP SHORT-CAPABLE & FUTURES STRATEGIEN (BEAR REGIME):")
    short_top = df_res[df_res["category"] == "short_futures"].head(5)
    short_table = [[r["strategy"], r["repo"], r["sub_type"], "Futures Ready", r["verdict"]] for _, r in short_top.iterrows()]
    print(tabulate(short_table, headers=["Strategie", "Repository", "Typ", "Markt", "Status"], tablefmt="grid"))


if __name__ == "__main__":
    main()
