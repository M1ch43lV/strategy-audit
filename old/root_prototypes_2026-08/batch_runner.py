import os
import re
import sys
import glob
import json
import shutil
import zipfile
import subprocess
import pandas as pd
from pathlib import Path

# Config
REPO_DIR = Path("strategy-audit/repos/MelvynClark_Freqtrade-Strategy")
CONFIG_FILE = "config_futures.json"
TIMERANGE = "20200101-20260823"
ADX_REGIMES_FILE = "data/multi_asset_results/BTCUSDT_regimes.csv"
OUTPUT_FILE = "batch_results.csv"

# Regex for parsing
class_regex = re.compile(r"class\s+([A-Za-z0-9_]+)\s*\(\s*IStrategy\s*\)\s*:")
timeframe_regex = re.compile(r"timeframe\s*=\s*['\"]([^'\"]+)['\"]")

def parse_strategy_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    match_class = class_regex.search(content)
    match_tf = timeframe_regex.search(content)
    
    if match_class:
        class_name = match_class.group(1)
        timeframe = match_tf.group(1) if match_tf else "1h" # Default to 1h if not found
        return class_name, timeframe
    return None, None

def run_backtest(strategy_path, strategy_class, timeframe):
    print(f"Running backtest for {strategy_class} with timeframe {timeframe}...")
    
    # We must ensure the directory is the strategy path.
    # In Freqtrade, --strategy-path should point to the directory containing the file.
    strat_dir = strategy_path.parent
    
    cmd = [
        ".\\.venv\\Scripts\\python.exe", "-m", "freqtrade", "backtesting",
        "--config", CONFIG_FILE,
        "--strategy-path", str(strat_dir),
        "--strategy", strategy_class,
        "--timerange", TIMERANGE,
        "--timeframe", timeframe,
        "--export", "trades",
        "--fee", "0.0004",
        "--max-open-trades", "1"
    ]
    
    log_file = f"unzipped/{strategy_class}_log.txt"
    Path("unzipped").mkdir(exist_ok=True)
    with open(log_file, "w", encoding="utf-8") as f:
        try:
            subprocess.run(cmd, check=True, stdout=f, stderr=subprocess.STDOUT, timeout=180)
            return True
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT: {strategy_class} took longer than 3 minutes to backtest. Skipping.")
            return False
        except subprocess.CalledProcessError as e:
            print(f"Error running backtest for {strategy_class}. Check {log_file}")
            return False

def extract_and_evaluate(strategy_class):
    last_result_path = Path("user_data/backtest_results/.last_result.json")
    if not last_result_path.exists():
        print(f"No last_result.json found for {strategy_class}")
        return None
        
    with open(last_result_path, "r") as f:
        meta = json.load(f)
    
    zip_name = meta.get("latest_backtest")
    if not zip_name:
        return None
        
    zip_path = Path("user_data/backtest_results") / zip_name
    unzip_dir = Path("user_data/backtest_results/unzipped")
    
    if unzip_dir.exists():
        shutil.rmtree(unzip_dir)
    unzip_dir.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(unzip_dir)
    
    # Find the extracted json file
    json_files = list(unzip_dir.glob("*.json"))
    trades_json = None
    for jf in json_files:
        if jf.name == zip_name.replace(".zip", ".json"):
            trades_json = jf
            break
            
    if not trades_json:
        print(f"Trades JSON not found in zip for {strategy_class}")
        return None
        
    # Run evaluation script
    eval_cmd = [
        ".\\.venv\\Scripts\\python.exe", "evaluate_adx_trades.py",
        str(trades_json), ADX_REGIMES_FILE
    ]
    
    try:
        result = subprocess.run(eval_cmd, check=True, capture_output=True, text=True)
        # Parse the output
        output = result.stdout
        
        metrics = {"Strategy": strategy_class, "BULL_Return_%": 0, "BEAR_Return_%": 0, "SIDE_Return_%": 0}
        for line in output.split("\n"):
            if "Regime BULL" in line:
                m = re.search(r"Gesamt:\s*([\-\+\d\.]+)", line)
                if m: metrics["BULL_Return_%"] = float(m.group(1))
            elif "Regime BEAR" in line:
                m = re.search(r"Gesamt:\s*([\-\+\d\.]+)", line)
                if m: metrics["BEAR_Return_%"] = float(m.group(1))
            elif "Regime SIDE" in line:
                m = re.search(r"Gesamt:\s*([\-\+\d\.]+)", line)
                if m: metrics["SIDE_Return_%"] = float(m.group(1))
                
        return metrics
    except subprocess.CalledProcessError as e:
        print(f"Error evaluating {strategy_class}: {e.stderr}")
        return None

def main():
    if not REPO_DIR.exists():
        print(f"Repository directory {REPO_DIR} does not exist.")
        return
        
    results = []
    py_files = list(REPO_DIR.rglob("*.py"))
    print(f"Found {len(py_files)} Python files.")
    
    for pf in py_files:
        # Skip internal or test files if necessary
        class_name, timeframe = parse_strategy_file(pf)
        if not class_name:
            continue
            
        print(f"Processing Strategy: {class_name} (TF: {timeframe})")
        
        success = run_backtest(pf, class_name, timeframe)
        if success:
            metrics = extract_and_evaluate(class_name)
            if metrics:
                results.append(metrics)
                print(f"Success! BULL: {metrics['BULL_Return_%']}%, BEAR: {metrics['BEAR_Return_%']}%, SIDE: {metrics['SIDE_Return_%']}%")
        print("-" * 40)
            
    if results:
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Results saved to {OUTPUT_FILE}")
        
if __name__ == "__main__":
    main()
