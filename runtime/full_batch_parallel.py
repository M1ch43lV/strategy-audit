# -*- coding: utf-8 -*-
"""Run canonical pooled full backtests several containers at a time, then repeat the failures alone.

    ./ftenv/Scripts/python.exe runtime/full_batch_parallel.py --strategy A --strategy B ...

Owner's rule (2026-09-21): four containers side by side, each one strategy under a 3.5 GB memory limit; a strategy that
dies of memory or hits the time ceiling under that limit is repeated at the end, one at a time, in a single container
with 15.5 GB (`docker info` reports about 15.6 GiB for the 16 GB WSL machine). The ceiling of 3600 s per run is not
raised.

Why containers and not `--workers N` inside one: the limit is per container, and a SIGKILL inside a shared pool cannot
be pinned on one strategy (`regime/full_backtest.py` accepts an OOM as confirmed only under `--workers 1`).

Every worker writes its own store, `results/regime/full_backtest_manifest_w<N>_docker.json`, because two containers must
not write the canonical manifest. When the parallel pass is over the measured results are imported into the canonical
manifest (`regime.full_backtest --import-manifest ... --import-only`). Everything else, whether failed, timed out or
killed, is repeated alone against the canonical manifest with `--force`, so the canonical record of such a strategy is
always the solo result. The sibling `runtime/detail_batch_parallel.py` does the same for the 5m detail runs.
"""
from __future__ import annotations

import argparse
import datetime
import glob
import io
import json
import os
import queue
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from runtime.detail_batch_parallel import Peaks  # noqa: E402

WRAPPER = os.path.join(ROOT, "runtime", "regime_full_backtest_docker.ps1")
REGIME = os.path.join(ROOT, "results", "regime")
WORKER_STORES = os.path.join(REGIME, "full_backtest_manifest_w*_docker.json")
PARALLEL_MEMORY = "3500m"
SOLO_MEMORY = "15500m"
SOLO_CPUS = "4"


def worker_store(number):
    return os.path.join(REGIME, "full_backtest_manifest_w%d_docker.json" % number)


def read_record(path, strategy):
    try:
        with io.open(path, encoding="utf-8") as handle:
            return (json.load(handle).get("results") or {}).get(strategy)
    except (OSError, ValueError):
        return None


def import_stores(paths):
    """Import the measured results of worker stores into the canonical manifest."""
    if not paths:
        return 0
    command = [sys.executable, "-m", "regime.full_backtest", "--import-only"]
    for path in paths:
        command += ["--import-manifest", path]
    return subprocess.run(command, cwd=ROOT).returncode


def run_pass(names, workers, memory, cpus, timeout, prefix, solo):
    """One pass over ``names``. Returns {strategy: (status, elapsed_s, peak_mib)}."""
    work = queue.Queue()
    for name in names:
        work.put(name)
    results, lock = {}, threading.Lock()
    peaks = Peaks(prefix)
    peaks.start()
    log = io.open(os.path.join(REGIME, "full_backtest_batch_memory.csv"), "a", encoding="utf-8")
    if log.tell() == 0:
        log.write("strategy,worker,status,elapsed_s,peak_mib,memory_limit\n")

    def worker(number):
        container = "%s%d" % (prefix, number)
        output = worker_store(number)
        while True:
            try:
                strategy = work.get_nowait()
            except queue.Empty:
                return
            peaks.take(container)
            started = time.time()
            command = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", WRAPPER,
                       "-ContainerName", container, "-MemoryLimit", memory, "-Cpus", cpus,
                       "--strategy", strategy, "--workers", "1", "--timeout", str(timeout), "--force"]
            if not solo:
                command += ["--output", os.path.relpath(output, ROOT).replace(os.sep, "/")]
            with io.open(os.path.join(REGIME, "full_backtest_batch.log"), "a", encoding="utf-8") as sink:
                sink.write("=== %s %s %s\n" % (datetime.datetime.now().isoformat(timespec="seconds"),
                                               "solo" if solo else "w%d" % number, strategy))
                sink.flush()
                subprocess.run(command, cwd=ROOT, stdout=sink, stderr=subprocess.STDOUT)
            canonical = os.path.join(REGIME, "full_backtest_manifest.json")
            record = read_record(canonical if solo else output, strategy) or {}
            fresh = (record.get("attempted_at") or "") >= datetime.datetime.fromtimestamp(
                started, datetime.timezone.utc).isoformat(timespec="seconds")
            status = record.get("status") if fresh else "no_record"
            elapsed = time.time() - started
            peak = peaks.take(container)
            with lock:
                results[strategy] = (status, elapsed, peak)
                log.write("%s,%s,%s,%.0f,%.0f,%s\n" % (strategy, "solo" if solo else number, status, elapsed, peak, memory))
                log.flush()
                print("%s  %s  %-40s %-22s %6.0fs  peak %5.0f MiB" % (
                    datetime.datetime.now().strftime("%H:%M:%S"), "solo" if solo else "w%d" % number, strategy,
                    status, elapsed, peak), flush=True)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(1, workers + 1)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    peaks.stop.set()
    log.close()
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strategy", action="append", default=[], help="strategy id to run; repeat for several")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--memory", default=PARALLEL_MEMORY, help="per-container memory and swap limit of the parallel pass")
    parser.add_argument("--solo-memory", default=SOLO_MEMORY, help="memory limit of the repeat, one strategy at a time")
    parser.add_argument("--timeout", type=int, default=3600)
    args = parser.parse_args(argv)
    if not args.strategy:
        raise SystemExit("no strategy given")
    # A worker store left by an interrupted batch is imported first, then removed: a fresh batch starts empty.
    leftovers = sorted(glob.glob(WORKER_STORES))
    if leftovers:
        import_stores(leftovers)
        for path in leftovers:
            os.replace(path, path + ".imported")
    names = sorted(set(args.strategy))
    print("%d strategies; %d containers x %s, then the failures alone with %s" % (
        len(names), args.workers, args.memory, args.solo_memory), flush=True)
    parallel = run_pass(names, min(args.workers, len(names)), args.memory, "1", args.timeout, "fullbatch-w", False)
    stores = sorted(glob.glob(WORKER_STORES))
    if import_stores(stores):
        print("import of the worker stores failed", file=sys.stderr)
        return 1
    for path in stores:
        os.replace(path, path + ".imported")
    retry = sorted(s for s, (status, _, _) in parallel.items() if status != "measured")
    print("parallel pass: %d measured, %d to repeat alone: %s" % (len(names) - len(retry), len(retry), ", ".join(retry) or "-"), flush=True)
    if retry:
        run_pass(retry, 1, args.solo_memory, SOLO_CPUS, args.timeout, "fullbatch-solo", True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
