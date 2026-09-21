"""Append and validate reproducible model-routing run metadata.

This file records operational provenance only. It does not execute a gate or
change the benchmark's evidence stores.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import uuid


STATUSES = {"PASS", "FAIL", "ESCALATE", "ERROR"}
GATES = {"classification", "smoke", "lookahead", "warmup_recursive", "full_backtest",
         "execution_robustness", "resource_diagnostic", "regime_evaluation"}
MODELS = {"gpt-5.6-luna", "gpt-5.6-terra", "gpt-5.6-sol"}
REASONING = {"low", "medium", "high"}
FIELDS = (
    "run_id", "timestamp", "gate", "model", "reasoning", "status",
    "strategy_ref", "task", "command", "evidence", "tool_versions",
    "escalation_reason", "previous_run_id",
)


def _json_value(value: str):
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def validate(record: dict) -> dict:
    missing = [field for field in FIELDS if field not in record]
    if missing:
        raise ValueError("missing metadata fields: " + ", ".join(missing))
    if record["gate"] not in GATES:
        raise ValueError("invalid gate: %s" % record["gate"])
    if record["model"] not in MODELS:
        raise ValueError("invalid model: %s" % record["model"])
    if record["reasoning"] not in REASONING:
        raise ValueError("invalid reasoning: %s" % record["reasoning"])
    if record["status"] not in STATUSES:
        raise ValueError("invalid status: %s" % record["status"])
    if record["status"] == "ESCALATE" and not record["escalation_reason"]:
        raise ValueError("ESCALATE requires escalation_reason")
    return record


def append_record(path: pathlib.Path, record: dict) -> None:
    validate(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="evidence/RUN_METADATA.jsonl")
    parser.add_argument("--gate", choices=sorted(GATES), required=True)
    parser.add_argument("--model", choices=sorted(MODELS), required=True)
    parser.add_argument("--reasoning", choices=sorted(REASONING), required=True)
    parser.add_argument("--status", choices=sorted(STATUSES), required=True)
    parser.add_argument("--strategy-ref", default="")
    parser.add_argument("--task", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--evidence", default="[]", help="JSON list or reference")
    parser.add_argument("--tool-versions", default="{}", help="JSON object")
    parser.add_argument("--escalation-reason", default="")
    parser.add_argument("--previous-run-id", default="")
    parser.add_argument("--run-id", default=str(uuid.uuid4()))
    parser.add_argument("--timestamp", default=dt.datetime.now(dt.timezone.utc).isoformat())
    args = parser.parse_args(argv)
    record = {field: getattr(args, field.replace("-", "_")) for field in FIELDS}
    record["evidence"] = _json_value(record["evidence"])
    record["tool_versions"] = _json_value(record["tool_versions"])
    append_record(pathlib.Path(args.output), record)
    print(json.dumps(record, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
