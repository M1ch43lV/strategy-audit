"""Identity-bound, resumable Model 1, Model 2, and Model 3 pooled backtests.

The runner executes only an explicit candidate specification.  It never
chooses profitable states, a discovery/validation split, or a replacement for
a failed candidate.  Those are preregistration decisions outside this module.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import json
import os
import re
import shlex
import sys
import threading
from pathlib import Path

import profile_smoke
from regime.gate_adapter import STATE_SET


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "STRATEGY_STATUS.csv"
DAILY = ROOT / "results" / "regime" / "regime_daily.csv"
CONFIG_DIR = ROOT / "user_data" / "regime_gate_configs"
LOCK = threading.Lock()
MODELS = {
    "model1": {
        "gate_mode": "btc",
        "scope": "btc_entry_gated_pooled_native_pair_universe",
        "output": ROOT / "results" / "regime" / "model1_backtest_manifest.json",
    },
    "model2": {
        "gate_mode": "coin",
        "scope": "coin_entry_gated_pooled_native_pair_universe",
        "output": ROOT / "results" / "regime" / "model2_backtest_manifest.json",
    },
    "model3": {
        "gate_mode": "btc_coin",
        "scope": "btc_coin_entry_gated_pooled_native_pair_universe",
        "output": ROOT / "results" / "regime" / "model3_backtest_manifest.json",
    },
}
ANALYSIS_ROLES = {
    "PILOT", "DISCOVERY", "VALIDATION", "ROBUSTNESS", "SENSITIVITY", "EXPLORATORY",
}
TIMERANGE_RE = re.compile(r"^[0-9]{8}-[0-9]{8}$")


def _file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return "sha256_" + digest.hexdigest()


def _json_sha(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256_" + hashlib.sha256(encoded).hexdigest()


def _state_list(candidate: dict, key: str) -> list[str]:
    if key not in candidate:
        raise ValueError(f"candidate {candidate.get('candidate_id', '<unknown>')} misses {key}")
    values = candidate[key]
    if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
        raise ValueError(f"{key} must be a list of state strings")
    if len(values) != len(set(values)):
        raise ValueError(f"{key} contains duplicate states")
    unknown = set(values) - STATE_SET
    if unknown:
        raise ValueError(f"{key} contains unknown states: {sorted(unknown)}")
    return sorted(values)


def load_candidate_spec(path: Path, model: str) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    if raw.get("schema_version") != 1:
        raise ValueError("candidate spec schema_version must be 1")
    candidate_set_id = raw.get("candidate_set_id")
    if not isinstance(candidate_set_id, str) or not candidate_set_id.strip():
        raise ValueError("candidate_set_id must be a non-empty string")
    role = raw.get("analysis_role")
    if role not in ANALYSIS_ROLES:
        raise ValueError(f"analysis_role must be one of {sorted(ANALYSIS_ROLES)}")
    timeranges = raw.get("timerange")
    if not isinstance(timeranges, dict) or set(timeranges) != {"spot", "futures"}:
        raise ValueError("timerange must contain exactly spot and futures")
    for mode, value in timeranges.items():
        if not isinstance(value, str) or not TIMERANGE_RE.fullmatch(value):
            raise ValueError(f"invalid {mode} timerange: {value!r}")
        start, end = value.split("-", 1)
        if start >= end:
            raise ValueError(f"{mode} timerange must have start before end")
    candidates = raw.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("candidates must be a non-empty list")
    normalized = []
    seen = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("every candidate must be an object")
        candidate_id = candidate.get("candidate_id")
        strategy_id = candidate.get("strategy_id")
        if not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError("every candidate needs a non-empty candidate_id")
        if candidate_id in seen:
            raise ValueError(f"duplicate candidate_id: {candidate_id}")
        seen.add(candidate_id)
        if not isinstance(strategy_id, str) or not strategy_id.strip():
            raise ValueError(f"candidate {candidate_id} needs a non-empty strategy_id")
        item = {
            "candidate_id": candidate_id,
            "strategy_id": strategy_id,
        }
        if model in {"model1", "model3"}:
            item["long_btc_states"] = _state_list(candidate, "long_btc_states")
            item["short_btc_states"] = _state_list(candidate, "short_btc_states")
        if model in {"model2", "model3"}:
            item["long_coin_states"] = _state_list(candidate, "long_coin_states")
            item["short_coin_states"] = _state_list(candidate, "short_coin_states")
        normalized.append(item)
    return {
        "schema_version": 1,
        "candidate_set_id": candidate_set_id,
        "analysis_role": role,
        "timerange": timeranges,
        "candidates": normalized,
    }


def _eligible_profiles() -> tuple[dict[str, dict], dict[str, dict]]:
    with STATUS.open(newline="", encoding="utf-8-sig") as handle:
        status = {row["strategy_id"]: row for row in csv.DictReader(handle)}
    eligible = {strategy for strategy, row in status.items()
                if row.get("cohort") == "E1_expanded"}
    profiles = {row["strategy_id"]: row
                for row in profile_smoke.read_manifest(profile_smoke.MANIFEST)
                if row["strategy_id"] in eligible}
    return profiles, status


def _gate_config(candidate: dict, model: str, daily_path: Path) -> dict:
    try:
        relative_daily = daily_path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        relative_daily = str(daily_path.resolve())
    config = {
        "schema_version": 1,
        "mode": MODELS[model]["gate_mode"],
        "daily_path": relative_daily,
    }
    if model in {"model1", "model3"}:
        config.update({
            "long_btc_states": candidate["long_btc_states"],
            "short_btc_states": candidate["short_btc_states"],
        })
    if model in {"model2", "model3"}:
        config.update({
            "long_coin_states": candidate["long_coin_states"],
            "short_coin_states": candidate["short_coin_states"],
        })
    return config


def _write_gate_config(candidate: dict, model: str, daily_path: Path) -> tuple[Path, dict, str]:
    config = _gate_config(candidate, model, daily_path)
    digest = _json_sha(config)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{profile_smoke._safe(candidate['candidate_id'])}-{model}-{digest[7:19]}.json"
    path = CONFIG_DIR / filename
    payload = json.dumps(config, indent=2, sort_keys=True) + "\n"
    temporary = path.with_name(path.name + f".{os.getpid()}.{threading.get_ident()}.tmp")
    temporary.write_text(payload, encoding="utf-8")
    os.replace(temporary, path)
    return path, config, digest


def _write(data: dict, path: Path) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _runner_invocation(args, output: Path) -> str:
    command = ["python", "-m", "regime.gated_backtest", "--model", args.model,
               "--candidate-spec", str(args.candidate_spec), "--daily", str(args.daily),
               "--output", str(output), "--timeout", str(args.timeout),
               "--workers", str(args.workers)]
    for candidate in args.candidate:
        command.extend(["--candidate", candidate])
    if args.limit:
        command.extend(["--limit", str(args.limit)])
    if args.force:
        command.append("--force")
    return " ".join(shlex.quote(part) for part in command)


def _claim(path: Path) -> Path:
    claim = Path(str(path) + ".running")
    try:
        claim.mkdir()
    except FileExistsError as exc:
        raise SystemExit(
            f"another runner may own {path.name}: {claim.name} exists; inspect it before retrying"
        ) from exc
    return claim


def _release_claim(claim: Path) -> None:
    try:
        claim.rmdir()
    except FileNotFoundError:
        pass


def _validate_existing(data: dict, expected: dict, output: Path) -> None:
    for key, value in expected.items():
        if data.get(key) != value:
            raise SystemExit(
                f"{output} belongs to a different {key}; use a new output path instead of mixing runs"
            )
    unexpected = set(data.get("results", {})) - set(expected["candidate_ids"])
    if unexpected:
        raise SystemExit(f"{output} contains candidates outside this spec: {sorted(unexpected)}")


def selftest() -> None:
    import tempfile
    global CONFIG_DIR, _eligible_profiles
    with tempfile.TemporaryDirectory() as directory:
        directory_path = Path(directory)
        path = directory_path / "candidates.json"
        base = {
            "schema_version": 1,
            "candidate_set_id": "pilot-v1",
            "analysis_role": "PILOT",
            "timerange": {"spot": "20200401-20200501", "futures": "20200301-20200401"},
            "candidates": [{
                "candidate_id": "Example-bull",
                "strategy_id": "Example",
                "long_btc_states": ["BULL"],
                "short_btc_states": [],
            }],
        }
        path.write_text(json.dumps(base), encoding="utf-8")
        model1 = load_candidate_spec(path, "model1")
        assert model1["candidates"][0]["long_btc_states"] == ["BULL"]
        try:
            load_candidate_spec(path, "model2")
        except ValueError as exc:
            assert "long_coin_states" in str(exc)
        else:
            raise AssertionError("Model 2 must require explicit coin states")
        base["candidates"][0].update({"long_coin_states": ["SIDEWAYS"],
                                      "short_coin_states": []})
        path.write_text(json.dumps(base), encoding="utf-8")
        model3 = load_candidate_spec(path, "model3")
        combined = _gate_config(model3["candidates"][0], "model3", DAILY)
        assert combined["mode"] == "btc_coin"
        assert combined["long_btc_states"] == ["BULL"]
        assert combined["long_coin_states"] == ["SIDEWAYS"]
        coin_only = json.loads(json.dumps(base))
        del coin_only["candidates"][0]["long_btc_states"]
        del coin_only["candidates"][0]["short_btc_states"]
        path.write_text(json.dumps(coin_only), encoding="utf-8")
        model2 = load_candidate_spec(path, "model2")
        config = _gate_config(model2["candidates"][0], "model2", DAILY)
        assert config["mode"] == "coin"
        assert config["long_coin_states"] == ["SIDEWAYS"]
        assert "long_btc_states" not in model2["candidates"][0]
        assert "long_btc_states" not in config
        expected = {"model": "model2", "candidate_ids": ["Example-bull"]}
        _validate_existing(dict(expected, results={}), expected, path)
        try:
            _validate_existing(dict(expected, results={"other": {}}), expected, path)
        except SystemExit:
            pass
        else:
            raise AssertionError("a manifest must not mix candidate specifications")

        # Exercise the complete resumable runner without invoking Freqtrade.
        # The second call must use the identity-bound cached measurement.
        daily = directory_path / "daily.csv"
        daily.write_text("date,pair,btc_regime,coin_regime\n", encoding="utf-8")
        output = directory_path / "model2.json"
        fake_profile = {"strategy_id": "Example", "run_profile": "spot_long"}
        calls = []
        saved = (CONFIG_DIR, _eligible_profiles, profile_smoke._identity,
                 profile_smoke.run_one, profile_smoke._read_jsonc)
        CONFIG_DIR = directory_path / "configs"
        _eligible_profiles = lambda: (
            {"Example": fake_profile},
            {"Example": {"cohort": "E1_expanded", "last_tested_at": "now"}},
        )
        profile_smoke._identity = lambda row: {
            "canonical_sha256": "sha256_source",
            "runtime_config_sha256": "sha256_config",
        }
        profile_smoke.run_one = lambda row, timerange, timeout, **kwargs: (
            calls.append(kwargs) or {
                "status": "measured", "trades": 3, "runtime_id": "selftest",
                "archive": "fake.zip", "archive_sha256": "sha256_archive",
            }
        )
        profile_smoke._read_jsonc = lambda _path: {
            "exchange": {"pair_whitelist": ["BTC/USDT"]}
        }
        try:
            arguments = ["--model", "model2", "--candidate-spec", str(path),
                         "--daily", str(daily), "--output", str(output)]
            assert main(arguments) == 0
            assert main(arguments) == 0
            stored = json.loads(output.read_text(encoding="utf-8"))
            result = stored["results"]["Example-bull"]
            assert len(calls) == 1
            assert result["gate_config"]["mode"] == "coin"
            assert "long_btc_states" not in result["gate_config"]
            assert result["artifact_key"] == "model2-Example-bull"
            assert calls[0]["run_context"]["candidate_id"] == "Example-bull"
        finally:
            (CONFIG_DIR, _eligible_profiles, profile_smoke._identity,
             profile_smoke.run_one, profile_smoke._read_jsonc) = saved
    print("gated backtest selftest: PASS")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=sorted(MODELS))
    parser.add_argument("--candidate-spec", type=Path)
    parser.add_argument("--daily", type=Path, default=DAILY)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        selftest()
        return 0
    if not args.model or not args.candidate_spec:
        parser.error("--model and --candidate-spec are required")
    if not args.daily.is_file():
        parser.error(f"regime daily file not found: {args.daily}")
    output = args.output or MODELS[args.model]["output"]
    spec = load_candidate_spec(args.candidate_spec, args.model)
    all_candidates = spec["candidates"]
    candidates = all_candidates
    if args.candidate:
        selected = set(args.candidate)
        candidates = [row for row in candidates if row["candidate_id"] in selected]
        missing = selected - {row["candidate_id"] for row in candidates}
        if missing:
            parser.error("candidate not in spec: " + ", ".join(sorted(missing)))
    if args.limit:
        candidates = candidates[:args.limit]
    if not candidates:
        parser.error("selection contains no candidates")

    profiles, status = _eligible_profiles()
    missing = sorted({row["strategy_id"] for row in all_candidates} - set(profiles))
    if missing:
        raise SystemExit("candidate strategies are not currently E1_expanded: " + ", ".join(missing))
    eligibility_projection = [{
        "strategy_id": strategy,
        "cohort": status[strategy].get("cohort"),
        "last_tested_at": status[strategy].get("last_tested_at"),
        **profile_smoke._identity(profiles[strategy]),
    } for strategy in sorted({row["strategy_id"] for row in all_candidates})]
    expected = {
        "schema_version": 1,
        "model": args.model,
        "measurement_scope": MODELS[args.model]["scope"],
        "analysis_role": spec["analysis_role"],
        "candidate_set_id": spec["candidate_set_id"],
        "candidate_spec_sha256": _file_sha(args.candidate_spec),
        "candidate_ids": [row["candidate_id"] for row in all_candidates],
        "candidates": all_candidates,
        "timerange": spec["timerange"],
        "regime_daily_sha256": _file_sha(args.daily),
        "eligibility_snapshot_sha256": _json_sha(eligibility_projection),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    claim = _claim(output)
    try:
        if output.exists():
            data = json.loads(output.read_text(encoding="utf-8"))
            _validate_existing(data, expected, output)
        else:
            data = dict(expected, results={})
        data["runner_invocation"] = _runner_invocation(args, output)

        def refresh_runtime_ids() -> None:
            data["runtime_ids"] = sorted({
                row.get("runtime_id", "native_unversioned")
                for row in data["results"].values() if row.get("status") == "measured"
            })

        def run(candidate: dict):
            candidate_id = candidate["candidate_id"]
            row = profiles[candidate["strategy_id"]]
            identity = profile_smoke._identity(row)
            mode = "futures" if row["run_profile"].startswith("futures_") else "spot"
            selected_timerange = spec["timerange"][mode]
            gate_path, gate_config, gate_sha = _write_gate_config(
                candidate, args.model, args.daily)
            bindings = {
                "candidate_id": candidate_id,
                "strategy_id": candidate["strategy_id"],
                "model": args.model,
                "measurement_scope": MODELS[args.model]["scope"],
                "analysis_role": spec["analysis_role"],
                "timerange": selected_timerange,
                "gate_rule_sha256": gate_sha,
                "regime_daily_sha256": expected["regime_daily_sha256"],
                **identity,
            }
            previous = data["results"].get(candidate_id) or {}
            if (not args.force and previous.get("status") == "measured" and
                    all(previous.get(key) == value for key, value in bindings.items())):
                return candidate_id, previous, True
            result = profile_smoke.run_one(
                row, selected_timerange, args.timeout,
                extra_env={"REGIME_GATE_CONFIG": str(gate_path.resolve())},
                artifact_key=f"{args.model}-{candidate_id}",
                run_context={"model": args.model, "candidate_id": candidate_id,
                             "analysis_role": spec["analysis_role"]},
            )
            config = (profile_smoke.FUTURES_CONFIG if mode == "futures"
                      else profile_smoke.SPOT_CONFIG)
            result.update(bindings)
            result["artifact_key"] = f"{args.model}-{candidate_id}"
            result["pairs"] = profile_smoke._read_jsonc(config)["exchange"]["pair_whitelist"]
            result["gate_config"] = gate_config
            try:
                result["regime_gate_config"] = gate_path.relative_to(ROOT).as_posix()
            except ValueError:
                result["regime_gate_config"] = str(gate_path.resolve())
            return candidate_id, result, False

        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = [pool.submit(run, candidate) for candidate in candidates]
            for future in concurrent.futures.as_completed(futures):
                candidate_id, result, cached = future.result()
                with LOCK:
                    data["results"][candidate_id] = result
                    refresh_runtime_ids()
                    _write(data, output)
                print(f"{candidate_id}: {'cached' if cached else result['status']} "
                      f"trades={result.get('trades', '')}", flush=True)
        measured = sum(data["results"].get(row["candidate_id"], {}).get("status") == "measured"
                       for row in candidates)
        print(f"{args.model} pooled gated backtests measured: {measured}/{len(candidates)}")
        return 0
    finally:
        _release_claim(claim)


if __name__ == "__main__":
    raise SystemExit(main())
