"""
Catalogue the strategy patterns used across the official Freqtrade reference repo.

The point is not to admire the list -- it is to find which *families* of idea
keep recurring, so we test the family rather than 64 near-duplicates of it.
"""
import re, sys, pathlib, collections
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path("reference_strategies/user_data/strategies")

# indicator -> which family of market behaviour it bets on
FAMILY = {
    "momentum/trend": ["EMA", "SMA", "TEMA", "MACD", "ADX", "PLUS_DI", "MINUS_DI",
                       "SAR", "ichimoku", "supertrend", "ott", "AROON", "TRIX", "DEMA"],
    "mean reversion": ["RSI", "BBANDS", "bollinger", "STOCH", "CCI", "WILLR", "MFI",
                       "fisher", "TSF", "CORREL"],
    "volatility":     ["ATR", "NATR", "TRANGE", "bbwidth"],
    "volume":         ["OBV", "AD", "ADOSC", "volume_mean", "MFI"],
    "candle/pattern": ["CDL", "heikin", "ha_", "TD_", "sequential"],
}
LOOKUP = {ind.lower(): fam for fam, inds in FAMILY.items() for ind in inds}

ind_counts = collections.Counter()
fam_counts = collections.Counter()
strat_fams = {}
tfs = collections.Counter()
files = sorted(ROOT.rglob("*.py"))

for f in files:
    try:
        src = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if "class " not in src or "IStrategy" not in src:
        continue
    found = set()
    for ind, fam in LOOKUP.items():
        if re.search(re.escape(ind), src, re.IGNORECASE):
            ind_counts[ind.upper()] += 1
            found.add(fam)
    for fam in found:
        fam_counts[fam] += 1
    strat_fams[f.stem] = found
    m = re.search(r"timeframe\s*=\s*['\"]([^'\"]+)['\"]", src)
    if m:
        tfs[m.group(1)] += 1

print(f"Scanned {len(strat_fams)} strategy classes in the official reference repo\n")

print("PATTERN FAMILIES -- how many strategies bet on each")
print("-" * 56)
for fam, n in fam_counts.most_common():
    pct = 100 * n / len(strat_fams)
    bar = "#" * int(pct / 2.5)
    print(f"  {fam:16s} {n:3d}  {pct:5.1f}%  {bar}")

print("\nMOST-USED INDICATORS")
print("-" * 56)
for ind, n in ind_counts.most_common(16):
    print(f"  {ind:14s} {n:3d} strategies   ({LOOKUP[ind.lower()]})")

print("\nTIMEFRAMES CHOSEN")
print("-" * 56)
for tf, n in tfs.most_common():
    print(f"  {tf:6s} {n:3d}")

print("\nHOW MANY FAMILIES EACH STRATEGY COMBINES")
print("-" * 56)
combo = collections.Counter(len(v) for v in strat_fams.values())
for k in sorted(combo):
    print(f"  {k} famil{'y' if k==1 else 'ies'}: {combo[k]:3d} strategies")

pure_mr = [s for s, v in strat_fams.items() if v == {"mean reversion"}]
pure_tr = [s for s, v in strat_fams.items() if v == {"momentum/trend"}]
print(f"\n  pure mean-reversion only: {len(pure_mr)}   pure trend only: {len(pure_tr)}")
