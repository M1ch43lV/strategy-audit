# -*- coding: utf-8 -*-
"""Run the Stage 8b detail reruns several containers at a time.

The serial batch takes one strategy after the other. This one keeps N Docker
containers busy, each running exactly one strategy at a time under its own memory
limit, so a strategy that outgrows the limit dies alone and is attributable. Those
strategies, and timeouts under parallel load, are then repeated one at a time with
one at a time with 15.5 GB (`--solo`).

Why containers and not `--workers N` inside one: the memory limit is per container,
and a SIGKILL inside a shared pool cannot be pinned on one strategy - the reason
`regime/full_backtest.py` only accepts an OOM as confirmed under `--workers 1`.

Every worker writes its own store, `execution_robustness_detail_<tf>_w<N>_docker.json`,
because two containers must not write one file. `evidence/execution_robustness.py`
already reads every `execution_robustness_detail_*.json` and keeps the best record per
strategy (a measured one beats a failed one), so a solo repeat replaces a killed
parallel attempt without any further step.

    ./ftenv/Scripts/python.exe runtime/detail_batch_parallel.py            # 4 x 3.5 GB, then solo
    ./ftenv/Scripts/python.exe runtime/detail_batch_parallel.py --limit 4  # a short trial
    ./ftenv/Scripts/python.exe runtime/detail_batch_parallel.py --solo     # only the repeat
"""
from __future__ import annotations

import argparse
import datetime
import io
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from evidence import execution_robustness as er  # noqa: E402
from regime import full_backtest  # noqa: E402

WRAPPER = os.path.join(ROOT, "runtime", "regime_full_backtest_docker.ps1")
REGIME = os.path.join(ROOT, "results", "regime")
RETRY_STATUSES = ("resource_inconclusive", "timeout")
UNITS = {"b": 1.0, "kb": 1e3, "kib": 1024.0, "mb": 1e6, "mib": 1024.0 ** 2,
         "gb": 1e9, "gib": 1024.0 ** 3}


def stem(tf, tag):
    return os.path.join(REGIME, "execution_robustness_detail_%s_%s" % (tf, tag))


def store(tf, tag):
    return stem(tf, tag) + "_docker.json"


def read_record(path, strategy):
    try:
        with io.open(path, encoding="utf-8") as handle:
            return (json.load(handle).get("results") or {}).get(strategy)
    except (OSError, ValueError):
        return None


def mib(text):
    """'1.293GiB / 3.418GiB' -> 1324.0 (the used part, in MiB)."""
    match = re.match(r"\s*([0-9.]+)\s*([A-Za-z]+)", text or "")
    if not match or match.group(2).lower() not in UNITS:
        return 0.0
    return float(match.group(1)) * UNITS[match.group(2).lower()] / 1024.0 ** 2


class Peaks(object):
    """Polls `docker stats` and keeps the highest memory each container reached."""

    def __init__(self, prefix):
        self.prefix = prefix
        self.peak = {}
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        self.thread.start()

    def _loop(self):
        while not self.stop.is_set():
            try:
                out = subprocess.run(
                    ["docker", "stats", "--no-stream", "--format", "{{.Name}}\t{{.MemUsage}}"],
                    capture_output=True, text=True, timeout=60).stdout
            except (OSError, subprocess.SubprocessError):
                out = ""
            for line in out.splitlines():
                name, _, usage = line.partition("\t")
                if name.startswith(self.prefix):
                    self.peak[name] = max(self.peak.get(name, 0.0), mib(usage))
            self.stop.wait(10)

    def take(self, name):
        return self.peak.pop(name, 0.0)


def run_pass(tf, names, workers, memory, tag, timeout, prefix, cpus="1"):
    """One pass over ``names``. Returns {strategy: (status, elapsed_s, peak_mib)}."""
    work = queue.Queue()
    for name in names:
        work.put(name)
    results, lock = {}, threading.Lock()
    peaks = Peaks(prefix)
    peaks.start()
    log = io.open(stem(tf, tag) + "_memory.csv", "a", encoding="utf-8")
    if log.tell() == 0:
        log.write("strategy,worker,status,elapsed_s,peak_mib,memory_limit\n")

    def worker(number):
        container = "%s%d" % (prefix, number)
        output = store(tf, "%s%d" % (tag, number) if workers > 1 else tag)
        while True:
            try:
                strategy = work.get_nowait()
            except queue.Empty:
                return
            peaks.take(container)
            started = time.time()
            command = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", WRAPPER,
                       "-ContainerName", container]
            if memory:
                command += ["-MemoryLimit", memory, "-Cpus", cpus]
            command += ["--timeframe-detail", tf, "--output", os.path.relpath(output, ROOT).replace(os.sep, "/"),
                        "--workers", "1", "--timeout", str(timeout), "--strategy", strategy, "--force"]   # --force: a record over the old window is in the store
            with io.open(output[:-len("_docker.json")] + ".log", "a", encoding="utf-8") as sink:
                sink.write("=== %s %s\n" % (datetime.datetime.now().isoformat(timespec="seconds"), strategy))
                sink.flush()
                subprocess.run(command, cwd=ROOT, stdout=sink, stderr=subprocess.STDOUT)
            record = read_record(output, strategy) or {}
            # A record older than this attempt means the container died before writing.
            fresh = (record.get("attempted_at") or "") >= datetime.datetime.fromtimestamp(
                started, datetime.timezone.utc).isoformat(timespec="seconds")
            status = record.get("status") if fresh else "no_record"
            elapsed = time.time() - started
            peak = peaks.take(container)
            with lock:
                results[strategy] = (status, elapsed, peak)
                log.write("%s,%d,%s,%.0f,%.0f,%s\n" % (strategy, number, status, elapsed, peak,
                                                       memory or "none"))
                log.flush()
                print("%s  w%d  %-40s %-22s %6.0fs  peak %5.0f MiB" % (
                    datetime.datetime.now().strftime("%H:%M:%S"), number, strategy, status,
                    elapsed, peak), flush=True)

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(1, workers + 1)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    peaks.stop.set()
    log.close()
    return results


def solo_candidates(tf):
    """Strategies whose best record is a killed or timed-out attempt from a parallel worker."""
    best = er.choose_detail_records()
    return sorted(s for s, r in best.items()
                  if r.get("timeframe_detail") == tf and r.get("status") in RETRY_STATUSES
                  and re.search(r"_w\d+_docker\.json$", r.get("store", "")))


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--detail", default="5m")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--memory", default="3500m",
                        help="per-container memory and swap limit; 4 x 3.5 GB leaves the 16 GB VM some room")
    parser.add_argument("--solo-memory", default="15500m",
                        help="memory limit of the repeat, one strategy at a time (owner, 2026-09-21: 15.5 GB)")
    parser.add_argument("--strategy", action="append", default=[],
                        help="run exactly these strategies instead of the ones still owed (a detail run over an old window)")
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--solo", action="store_true",
                        help="only repeat the killed or timed-out parallel attempts, one at a time, with --solo-memory")
    parser.add_argument("--no-solo", action="store_true", help="skip the repeat after the parallel pass")
    args = parser.parse_args(argv)

    if not args.solo:
        # A serial attempt that already failed on its own, or hit the 3600 s ceiling
        # alone, is final: repeating it in parallel would only reproduce it.
        final = {s for s, r in er.choose_detail_records().items()
                 if r.get("status") in ("failed", "timeout")}
        # The runner refuses a strategy it no longer lists as eligible ("not currently
        # eligible") - a baseline can outlive that - so those cannot be rerun at all.
        eligible = {row["strategy_id"] for row in full_backtest.eligible()}
        owed = list(args.strategy) or [s for s in er.targets(args.detail) if s not in final]
        names = [s for s in owed if s in eligible]
        if len(names) != len(owed):
            print("not currently eligible, skipped: %s" % ", ".join(sorted(set(owed) - eligible)),
                  flush=True)
        if args.limit:
            names = names[:args.limit]
        print("%d strategies owed a %s detail run; %d containers x %s" % (
            len(names), args.detail, args.workers, args.memory), flush=True)
        results = run_pass(args.detail, names, args.workers, args.memory, "w", args.timeout, "detail5m-w")
        by_status = {}
        for status, _, _ in results.values():
            by_status[status] = by_status.get(status, 0) + 1
        print("parallel pass:", by_status, flush=True)
        if args.no_solo:
            return 0
    retry = solo_candidates(args.detail)
    # A container that died before writing anything leaves no record at all.
    if not args.solo:
        retry = sorted(set(retry) | {s for s, (status, _, _) in results.items() if status == "no_record"})
    print("%d strategies to repeat one at a time: %s" % (len(retry), ", ".join(retry) or "-"), flush=True)
    if retry:
        run_pass(args.detail, retry, 1, args.solo_memory, "solo", args.timeout, "detail5m-solo", cpus="4")
    return 0


if __name__ == "__main__":
    sys.exit(main())
