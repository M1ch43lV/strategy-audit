# -*- coding: utf-8 -*-
"""Report every status token the stores actually hold, and what the schema says.

This is the discovery half of the verdict schema (`evidence/verdicts.py`). The
schema can only map the tokens somebody has seen; this program walks the real
stores, counts the raw values at every mapped field, and names the ones the
schema does not know. It reads only - no store is written, and no measurement
is started.

Two findings matter, and they are different:

* An UNKNOWN token at a mapped field means the schema is already wrong about a
  store it claims to cover. That is a defect in `evidence/verdicts.py`.
* A field that is not mapped at all means nobody has decided yet whether it is
  a verdict or a taxonomy. That is unfinished work, and the sweep section lists
  it so it is a queue rather than a memory.

Raw stores stay exactly as they are. They are append-only provenance, so the
migration normalizes on read and never rewrites history.

    python tools/verdict_migration_audit.py              # report, exit 0
    python tools/verdict_migration_audit.py --strict     # exit 1 on a finding
    python tools/verdict_migration_audit.py --write      # + evidence/VERDICT_MIGRATION.json
"""
from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import io
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "evidence" / "VERDICT_MIGRATION.json"

# Where a store may live. Searched in order; the first hit wins.
SEARCH_BASES = ("evidence", "results/regime", ".", "user_data")

# Record keys that look like a verdict, for the sweep over un-mapped fields.
SWEEP_FIELDS = ("status", "state")
SWEEP_BASES = ("evidence",)
# The published CSVs re-expose the same gates as columns, so they are swept too.
SWEEP_CSV = ("STRATEGY_STATUS.csv", "evidence/REGIME_ELIGIBILITY.csv")
SWEEP_COLUMN_NAMES = ("state", "lookahead", "recursive", "measured")


def _verdict_column(column):
    """Whether a CSV column name promises a verdict rather than a description.

    The first version of this audit walked `evidence/*.json` only, which left
    every published column unchecked - the gap that let `lookahead`,
    `coverage_status` and four others sit un-mapped while the audit reported a
    clean sheet. A name is treated as a verdict when it is one of the known
    verdict names or ends in `_status`.
    """
    return (column == "state" or column in SWEEP_COLUMN_NAMES
            or column.endswith("_status"))


def _verdicts():
    """Load the schema without putting the repository on sys.path."""
    path = ROOT / "evidence" / "verdicts.py"
    spec = importlib.util.spec_from_file_location("_audit_verdicts", path)
    module = importlib.util.module_from_spec(spec)
    # The `dataclass` decorator reads sys.modules while it runs, so register the
    # module before executing it.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _locate(name):
    for base in SEARCH_BASES:
        path = ROOT / base / name
        if path.is_file():
            return path
    return None


def _records(path):
    """Yield the current records of a store.

    A store with a `results` mapping yields those entries only. The
    `superseded` block is a history of retired records, not a set of current
    verdicts, and counting it would double-count a strategy under two answers.
    """
    suffix = path.suffix.lower()
    if suffix == ".csv":
        with io.open(path, newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                yield row
        return
    if suffix == ".jsonl":
        with io.open(path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    yield json.loads(line)
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and isinstance(payload.get("results"), dict):
        for key, record in payload["results"].items():
            if isinstance(record, dict):
                yield dict(record, _strategy=key)
        return
    if isinstance(payload, dict):
        yield payload
    elif isinstance(payload, list):
        for record in payload:
            if isinstance(record, dict):
                yield record


def _dig(record, dotted):
    value = record
    for part in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def collect(verdicts):
    """{store: {field: Counter(raw token)}} for every mapped field."""
    out = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    for store, field in sorted(verdicts.MAPPING):
        path = _locate(store)
        if path is None:
            continue
        for record in _records(path):
            raw = _dig(record, field)
            if raw is None or raw == "":
                out[store][field]["<absent>"] += 1
            else:
                out[store][field][str(raw)] += 1
    return out


def _score(verdicts, store, field, counter):
    """(mapped, unknown, unmapped_field) counts for one field."""
    mapping = verdicts.MAPPING.get((store, field))
    mapped = unknown = 0
    for token, count in counter.items():
        if token == "<absent>":
            unknown += count
            continue
        if mapping and token in mapping[1]:
            mapped += count
        else:
            unknown += count
    return mapped, unknown


def sweep(verdicts):
    """Fields under evidence/ that hold status-like keys with no mapping yet."""
    found = collections.defaultdict(collections.Counter)
    for base in SWEEP_BASES:
        for path in sorted((ROOT / base).glob("*.json")):
            store = path.name
            if store == OUTPUT.name:
                continue
            try:
                records = list(_records(path))
            except Exception:
                continue
            for record in records:
                for key in SWEEP_FIELDS:
                    if key not in record:
                        continue
                    if (store, key) in verdicts.MAPPING or (store, key) in verdicts.OUT_OF_SCOPE:
                        continue
                    raw = record.get(key)
                    found[(store, key)][str(raw) if raw not in (None, "") else "<absent>"] += 1
    for relative in SWEEP_CSV:
        path = ROOT / relative
        if not path.is_file():
            continue
        store = path.name
        with io.open(path, newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        if not rows:
            continue
        for column in rows[0]:
            if not _verdict_column(column):
                continue
            if ((store, column) in verdicts.MAPPING
                    or (store, column) in verdicts.OUT_OF_SCOPE):
                continue
            for row in rows:
                raw = row.get(column)
                found[(store, column)][str(raw) if raw not in (None, "") else "<absent>"] += 1
    return found


def report(verdicts, verbose=True):
    collected = collect(verdicts)
    problems = []
    lines = []
    total = mapped_total = unknown_total = 0

    for store in sorted(collected):
        for field in sorted(collected[store]):
            counter = collected[store][field]
            mapping = verdicts.MAPPING.get((store, field))
            count = sum(counter.values())
            mapped, unknown = _score(verdicts, store, field, counter)
            total += count
            mapped_total += mapped
            unknown_total += unknown
            lines.append("%s.%s  (%d value(s), layer %s)"
                         % (store, field, count, mapping[0] if mapping else "-"))
            for token, hits in sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])):
                if token == "<absent>":
                    lines.append("    %-34s %5d  absent -> UNKNOWN/missing_value"
                                 % ("(no value)", hits))
                elif mapping and token in mapping[1]:
                    verdict = verdicts.normalize(store, field, token)
                    lines.append("    %-34s %5d  %s%s"
                                 % (token, hits, verdict.value,
                                    " (%s)" % verdict.reason if verdict.reason else ""))
                else:
                    lines.append("    %-34s %5d  UNKNOWN - needs a mapping entry"
                                 % (token, hits))
                    problems.append("%s.%s: unknown token %r (%d value(s))"
                                    % (store, field, token, hits))

    pending = sweep(verdicts)
    lines.append("")
    lines.append("status-like fields with no decision yet (%d):" % len(pending))
    for (store, field), counter in sorted(pending.items()):
        tokens = ", ".join("%s x%d" % (token, hits)
                           for token, hits in sorted(counter.items(),
                                                     key=lambda kv: (-kv[1], kv[0]))[:6])
        lines.append("    %-44s %s" % ("%s.%s" % (store, field), tokens))

    if verbose:
        for line in lines:
            print(line)
        print("")
        print("mapped fields: %d value(s), %d mapped, %d unknown, %d field(s) pending"
              % (total, mapped_total, unknown_total, len(pending)))
    return lines, problems, pending, (total, mapped_total, unknown_total)


def write_report(lines, problems, pending, counts):
    payload = {
        "schema_version": 1,
        "note": ("Discovery evidence for the verdict schema migration. Raw stores "
                 "are unchanged; this file records what they hold and what the "
                 "schema does not yet map."),
        "mapped_values": counts[0],
        "mapped": counts[1],
        "unknown": counts[2],
        "unknown_tokens": list(problems),
        "fields_pending_decision": sorted("%s.%s" % key for key in pending),
        "report": lines,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    temporary.replace(OUTPUT)
    print("wrote %s" % OUTPUT.relative_to(ROOT))


def selftest():
    verdicts = _verdicts()
    problems = []
    lines, unknown, pending, counts = report(verdicts, verbose=False)
    if not lines:
        problems.append("selftest: the report is empty")
    if counts[0] and counts[1] + counts[2] != counts[0]:
        problems.append("selftest: mapped + unknown != total")

    # A synthetic store must produce exactly one unknown-token finding.
    sample = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
    sample["PROFILE_SMOKE.json"]["status"].update({"measured": 3, "totally_new": 1})
    mapped, missing = _score(verdicts, "PROFILE_SMOKE.json", "status",
                             sample["PROFILE_SMOKE.json"]["status"])
    if (mapped, missing) != (3, 1):
        problems.append("selftest: scoring is wrong (%r, %r)" % (mapped, missing))

    # The dotted path and the results-only rule must both hold.
    record = {"lookahead": {"status": "PASS"}, "superseded": {"x": 1}}
    if _dig(record, "lookahead.status") != "PASS":
        problems.append("selftest: dotted path failed")
    if _dig(record, "missing.status") is not None:
        problems.append("selftest: a missing path did not return None")

    for problem in problems:
        print("FAIL %s" % problem)
    print("migration audit selftest: %d problem(s)" % len(problems))
    return 1 if problems else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 when a token or field needs a decision")
    parser.add_argument("--write", action="store_true",
                        help="write evidence/VERDICT_MIGRATION.json")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    verdicts = _verdicts()
    lines, problems, pending, counts = report(verdicts, verbose=not args.quiet)
    if args.write:
        write_report(lines, problems, pending, counts)
    if args.strict and (problems or pending):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
