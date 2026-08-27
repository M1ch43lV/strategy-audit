# -*- coding: utf-8 -*-
"""
classify_strategies.py - Parst alle 895 Strategien aus LEDGER.csv und corpus/*.md,
erkennt funktionierende Strategien (inklusive der 37 Short/Futures-Strategien, die im Spot-Audit blockiert wurden)
und teilt alle lauffähigen Strategien in die 3 Marktregime-Kategorien ein:
1. 🐂 long_trend (Long Trendfolge / Momentum / Breakout)
2. 🐻 short_futures (Short-fähige / Futures Strategien)
3. 🦀 mean_reversion (Oszillatoren / Range / Mean-Reversion / Dips)
"""
import glob
import io
import json
import os
import re
import sys
import pandas as pd
from tabulate import tabulate

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.abspath(__file__))
AUDIT_DIR = os.path.join(ROOT, "strategy-audit")
CORPUS_DIR = os.path.join(AUDIT_DIR, "corpus")
LEDGER_CSV = os.path.join(AUDIT_DIR, "LEDGER.csv")
OUTPUT_JSON = os.path.join(ROOT, "data", "STRATEGY_REGIME_MAP.json")

SHORT_PATTERNS = ["short", "futures", "bear", "f_"]
MEAN_REV_PATTERNS = [
    "rsi", "bb", "bollinger", "cluc", "binh", "stoch", "cci", "mfi",
    "reversion", "oscillator", "squeeze", "range", "madv", "band", "bbrsi",
    "dip", "bounce", "scalp"
]
TREND_PATTERNS = [
    "ema", "sma", "dema", "tema", "macd", "supertrend", "adx", "trend",
    "momentum", "cross", "ichimoku", "breakout", "sar", "tank", "reinforced",
    "actionzone", "alex", "combo", "multi", "pure", "wave"
]


def get_short_spot_blocked_strategies():
    """
    Findet alle Strategien, die nur deshalb bei G0 fehlschlugen, weil Freqtrade im Spot-Modus lief
    ('Short strategies cannot run in spot markets').
    """
    blocked_shorts = set()
    cards = glob.glob(os.path.join(CORPUS_DIR, "*.md"))
    for c in cards:
        if os.path.basename(c) == "INDEX.md":
            continue
        try:
            txt = io.open(c, encoding="utf-8", errors="replace").read()
            if "Short strategies cannot run in spot markets" in txt:
                name = os.path.basename(c).replace(".md", "")
                blocked_shorts.add(name)
        except Exception:
            pass
    return blocked_shorts


def classify_strategy(strat_name, repo, file_path, is_short_blocked):
    name_low = strat_name.lower()
    file_low = str(file_path).lower()
    
    # 1. Short / Futures
    if is_short_blocked or any(p in name_low or p in file_low for p in SHORT_PATTERNS):
        return "short_futures", "Short / Futures"
        
    # 2. Mean Reversion vs Trend
    mean_score = sum(1 for p in MEAN_REV_PATTERNS if p in name_low or p in file_low)
    trend_score = sum(1 for p in TREND_PATTERNS if p in name_low or p in file_low)
    
    if mean_score > trend_score:
        return "mean_reversion", "Mean-Reversion / Range / Dip-Buyer"
    elif trend_score > 0:
        return "long_trend", "Long Trendfolge / Momentum"
    else:
        if any(w in name_low for w in ["cluc", "hanix", "bin", "quickie", "buy", "sell"]):
            return "mean_reversion", "Mean-Reversion / Range / Dip-Buyer"
        return "unknown", "Unklassifiziert"


def main():
    if not os.path.exists(LEDGER_CSV):
        print(f"Fehler: {LEDGER_CSV} nicht gefunden!")
        sys.exit(1)
        
    df = pd.read_csv(LEDGER_CSV)
    print(f"Lese LEDGER.csv ({len(df)} Strategien)...", flush=True)
    
    short_blocked_set = get_short_spot_blocked_strategies()
    print(f"Identifizierte Futures-/Short-Strategien (durch Spot-Modus blockiert): {len(short_blocked_set)}")
    
    working = []
    broken = []
    
    categories = {
        "long_trend": [],
        "short_futures": [],
        "mean_reversion": [],
        "unknown": []
    }
    
    for _, row in df.iterrows():
        strat = str(row["strategy"])
        repo = str(row["repo"])
        file_p = str(row["file"])
        dropped_at = str(row["dropped_at"])
        
        is_trades = row["is_trades"]
        os_trades = row["os_trades"]
        has_trades = (pd.notna(is_trades) and str(is_trades) != "" and str(is_trades) != "0") or \
                     (pd.notna(os_trades) and str(os_trades) != "" and str(os_trades) != "0")
                     
        is_short_blocked = strat in short_blocked_set
        
        # Wirklich defekt sind nur jene, die keine Trades hatten UND nicht als Short blockiert wurden
        if dropped_at == "G0_measured" and not has_trades and not is_short_blocked:
            broken.append({
                "strategy": strat,
                "repo": repo,
                "file": file_p,
                "dropped_at": dropped_at,
                "reason": "Syntaxfehler, fehlende Imports oder Absturz (echter G0-Defekt)"
            })
            continue
            
        cat, sub = classify_strategy(strat, repo, file_p, is_short_blocked)
        
        strat_entry = {
            "strategy": strat,
            "repo": repo,
            "file": file_p,
            "regime_category": cat,
            "sub_type": sub,
            "is_short_futures_recovered": is_short_blocked,
            "is_trades": row["is_trades"] if pd.notna(row["is_trades"]) else None,
            "is_exp": row["is_exp"] if pd.notna(row["is_exp"]) else None,
            "is_p": row["is_p"] if pd.notna(row["is_p"]) else None,
            "os_trades": row["os_trades"] if pd.notna(row["os_trades"]) else None,
            "os_exp": row["os_exp"] if pd.notna(row["os_exp"]) else None,
            "os_p": row["os_p"] if pd.notna(row["os_p"]) else None,
            "os_avg_pct": row["os_avg_pct"] if pd.notna(row["os_avg_pct"]) else None,
            "lookahead": row["lookahead"],
            "recursive": row["recursive"],
            "traps": row["traps"],
            "dropped_at": row["dropped_at"],
            "survives_through": row["survives_through"]
        }
        
        categories[cat].append(strat_entry)
        working.append(strat_entry)
        
    print("\n" + "="*80)
    print("STRATEGIE-KLASSIFIKATION & REGIME-ZUORDNUNG (INKL. FUTURES RECOVERY)")
    print("="*80)
    
    n_tot = len(df)
    n_work = len(working)
    n_brok = len(broken)
    n_long = len(categories["long_trend"])
    n_short = len(categories["short_futures"])
    n_range = len(categories["mean_reversion"])
    n_unk = len(categories["unknown"])
    
    table = [
        ["🐂 Long-Trend & Momentum", f"{n_long} Strategien", f"{n_long/n_work*100:.1f} %", "Bullenmarkt / Uptrend (HMM Bull)"],
        ["🐻 Short-Capable & Futures", f"{n_short} Strategien", f"{n_short/n_work*100:.1f} %", "Bärenmarkt / Downtrend (HMM Bear)"],
        ["🦀 Mean-Reversion & Range", f"{n_range} Strategien", f"{n_range/n_work*100:.1f} %", "Seitwärts- / Chop-Markt (HMM Side)"],
        ["❓ Unklassifiziert", f"{n_unk} Strategien", f"{n_unk/n_work*100:.1f} %", "Wird im Benchmark ignoriert"],
        ["❌ Echter Defekt / Syntaxfehler", f"{n_brok} Strategien", f"{n_brok/n_tot*100:.1f} %", "Vom Benchmark ausgeschlossen"],
        ["TOTAL LAUFFÄHIG", f"{n_work} Strategien", "100.0 %", "Für Regime-Benchmark bereit"]
    ]
    print(tabulate(table, headers=["Kategorie", "Anzahl", "Anteil der Lauffähigen", "Ziel-Marktphase"], tablefmt="grid"))
    
    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_in_ledger": n_tot,
                "working_strategies_count": n_work,
                "broken_strategies_count": n_brok,
                "long_trend_count": n_long,
                "short_futures_count": n_short,
                "mean_reversion_count": n_range,
                "unknown_count": n_unk
            },
            "categories": categories,
            "broken": broken
        }, f, indent=2)
        
    print(f"\n[OK] Vollständige Klassifikations-Matrix gespeichert: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
