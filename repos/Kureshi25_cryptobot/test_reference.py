"""
Backtest every strategy in the official Freqtrade reference repo.

Freqtrade's own docs warn that "most public strategies are not good performers".
This measures exactly how true that is, on one consistent dataset, rather than
trusting any repo's README.
"""
import re, subprocess, sys, pathlib, json, concurrent.futures as cf
sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(r"C:\Users\hassa\cryptobot")
FT = ROOT / ".venv" / "Scripts" / "freqtrade.exe"
CFG = ROOT / "user_data" / "config.json"
SRC = ROOT / "reference_strategies" / "user_data" / "strategies"
HAVE = {"5m", "1h", "4h", "1d"}
TIMERANGE = "20250901-"          # inside the 5m data window
PER_STRAT_TIMEOUT = 240

def timeframe_of(path):
    src = path.read_text(encoding="utf-8", errors="ignore")
    if "IStrategy" not in src:
        return None
    m = re.search(r"^\s*timeframe\s*=\s*['\"]([^'\"]+)['\"]", src, re.M)
    return m.group(1) if m else "5m"

NUM = r"(-?\d+\.?\d*)"
def run_one(path):
    name = path.stem
    tf = timeframe_of(path)
    if tf is None:
        return None
    if tf not in HAVE:
        return {"name": name, "tf": tf, "status": f"no {tf} data"}
    try:
        r = subprocess.run(
            [str(FT), "backtesting", "--config", str(CFG), "--strategy", name,
             "--strategy-path", str(path.parent), "--timeframe", tf,
             "--timerange", TIMERANGE],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=ROOT, timeout=PER_STRAT_TIMEOUT)
        out = r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return {"name": name, "tf": tf, "status": "timeout"}
    except Exception as e:
        return {"name": name, "tf": tf, "status": type(e).__name__}

    def grab(label):
        m = re.search(rf"\|\s*{label}\s*\|\s*{NUM}", out)
        return float(m.group(1)) if m else None

    prof = grab(r"Total profit %")
    if prof is None:
        err = "error"
        if "OperationalException" in out: err = "incompatible"
        elif "ImportError" in out or "ModuleNotFound" in out: err = "missing dep"
        elif "No trades" in out or "found no trades" in out.lower(): err = "no trades"
        return {"name": name, "tf": tf, "status": err}
    return {"name": name, "tf": tf, "status": "ok", "profit": prof,
            "market": grab(r"Market change"), "pf": grab(r"Profit factor"),
            "dd": grab(r"Max % of account underwater"),
            "trades": grab(r"Total/Daily Avg Trades"),
            "sharpe": grab(r"Sharpe \(daily wallet balance\)")}

files = sorted(SRC.rglob("*.py"))
print(f"Testing {len(files)} files from the official reference repo", file=sys.stderr)
print(f"Timerange {TIMERANGE} | $1000 wallet | real fees\n", file=sys.stderr)

results = []
with cf.ThreadPoolExecutor(max_workers=4) as pool:
    for i, res in enumerate(pool.map(run_one, files), 1):
        if res:
            results.append(res)
            tag = res["status"] if res["status"] != "ok" else f"{res.get('profit'):+.1f}%"
            print(f"  [{i:2d}/{len(files)}] {res['name'][:34]:34s} {res['tf']:4s} {tag}", file=sys.stderr)

ok = [r for r in results if r["status"] == "ok"]
bad = [r for r in results if r["status"] != "ok"]
ok.sort(key=lambda r: r["profit"], reverse=True)

print("\n" + "=" * 88)
print("OFFICIAL FREQTRADE REFERENCE STRATEGIES - MEASURED, NOT ADVERTISED")
print("=" * 88)
hdr = f"{'STRATEGY':34s}{'TF':>5s}{'PROFIT':>9s}{'MARKET':>9s}{'vs MKT':>9s}{'PF':>6s}{'MAXDD':>8s}{'TRADES':>8s}"
print(hdr); print("-" * len(hdr))
for r in ok:
    vs = r["profit"] - r["market"] if r["market"] is not None else None
    print(f"{r['name'][:34]:34s}{r['tf']:>5s}{r['profit']:>8.1f}%"
          f"{(r['market'] or 0):>8.1f}%{(vs if vs is not None else 0):>8.1f}p"
          f"{(r['pf'] or 0):>6.2f}{(r['dd'] or 0):>7.1f}%{int(r['trades'] or 0):>8d}")
print("-" * len(hdr))

if ok:
    prof = [r["profit"] for r in ok]
    winners = [r for r in ok if r["profit"] > 0]
    beat = [r for r in ok if r["market"] is not None and r["profit"] > r["market"]]
    print(f"\nRan successfully : {len(ok)} of {len(results)}")
    print(f"Profitable       : {len(winners)}/{len(ok)}  ({100*len(winners)/len(ok):.0f}%)")
    print(f"Beat buy-and-hold: {len(beat)}/{len(ok)}  ({100*len(beat)/len(ok):.0f}%)")
    print(f"Median return    : {sorted(prof)[len(prof)//2]:+.1f}%")
    print(f"Mean return      : {sum(prof)/len(prof):+.1f}%")
    print(f"Market over same : {(ok[0]['market'] or 0):+.1f}%")

if bad:
    import collections
    print(f"\nDid not produce a result ({len(bad)}):")
    for status, n in collections.Counter(r["status"] for r in bad).most_common():
        print(f"  {status:16s} {n}")

json.dump(results, open("reference_results.json", "w"), indent=1)
print("\nsaved -> reference_results.json")
