# -*- coding: utf-8 -*-
"""Why each blocked row does not start, and whether that is ours to fix.

152 rows never ran, so nothing about them has been judged. "Excluded" is the
wrong word for them and "unfixable" is an assumption nobody checked. This
sorts them by what actually stops them and, for each, whether a repair would
be legitimate - which is a separate question from whether it is possible.

THE LINE THIS DRAWS. A repair may restore what the author wrote; it may never
supply what they did not. Renaming `ticker_interval` to `timeframe` carries the
author's own literal across a framework rename. Inventing a stoploss for a
strategy that declares none does not restore anything - it makes up the risk
management and then measures our invention. The first is a repair, the second
is a different strategy wearing the same name.

WHAT FREQTRADE HIDES. Forty-eight rows report only

    Impossible to load Strategy 'X'. This class does not exist or contains
    Python code errors.

which conflates a missing class with a syntax error with a missing import, and
names none of them. So the file is imported here directly and the real
exception recorded. Until that is done, every one of those rows is filed under
a message that cannot be acted on.
"""
from __future__ import annotations

import argparse
import collections
import csv
import importlib.util
import io
import json
import os
import re
import sys
import traceback


ROOT = os.path.dirname(os.path.abspath(__file__))
STATUS = os.path.join(ROOT, "STRATEGY_STATUS.csv")
OUTPUT = os.path.join(ROOT, "BLOCKED_TRIAGE.json")

LOAD_FAILURE = re.compile(r"Impossible to load (?:Strategy|FreqaiModel) '([^']+)'")

# How each family is judged. `verdict` is about legitimacy first and effort
# second: a repair that would invent behaviour is refused however easy it is.
FAMILIES = (
    ("timeframe_missing", "Timeframe needs to be set", "to_be_fixed",
     "37 of these declare the value as ticker_interval, freqtrade's own name "
     "for the field before 2021.4. eligibility_timeframe_repair carries it "
     "across; the rest are refused there with a reason."),
    ("freqai_not_enabled", "freqAI is not enabled", "to_be_fixed",
     "A runtime matter, not a strategy defect: the image needs torch and the "
     "config needs a freqai block. Already queued as the FreqAI arm."),
    ("freqai_model_missing", "Impossible to load FreqaiModel", "to_be_fixed",
     "Same arm: the model class ships with the FreqAI extras."),
    ("old_hook_signature", "min_roi_reached_entry() missing", "to_be_fixed",
     "The strategy overrides a freqtrade hook whose signature gained two "
     "parameters. Accepting them and ignoring them restores the author's "
     "logic unchanged - but it is a source edit, so it owes a paired "
     "equivalence run before the result counts."),
    ("no_stoploss", "'stoploss' is a required property", "refuse_repair",
     "The strategy declares no stoploss. Supplying one does not restore "
     "anything the author wrote; it invents the risk management and then "
     "measures the invention."),
    ("no_exit_logic", "must be implemented", "refuse_repair",
     "No exit logic at all. Whatever we wrote would be ours, not theirs."),
    ("dtype_drift", "dtype", "needs_a_look",
     "The strategy's own code trips a pandas or numpy type rule that has "
     "tightened since it was written. Sometimes a one-line cast the author "
     "would recognise, sometimes a real bug. Not one family, despite the "
     "shared message."),
)


def _csv(path):
    with io.open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def _write(data):
    tmp = OUTPUT + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, OUTPUT)


def blocked_rows():
    return [row for row in _csv(STATUS) if row["exclusion_basis"] == "blocked"]


def probe_import(source_file, class_name):
    """Import the file and report what actually goes wrong.

    Returns `(kind, detail)`. The import is done in this process because that
    is the point: the same interpreter, the same installed packages, the same
    answer freqtrade would get. Anything raised is caught, including
    SystemExit, which a few corpus files call at import time.
    """
    path = source_file if os.path.isabs(source_file) \
        else os.path.join(ROOT, source_file)
    if not os.path.isfile(path):
        return "file_missing", path
    name = "triage_%s" % re.sub(r"\W+", "_", class_name)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return "not_importable", "no loader for %s" % path
    module = importlib.util.module_from_spec(spec)
    previous = sys.modules.get(name)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException as exc:            # noqa: BLE001 - that is the point
        frames = traceback.extract_tb(sys.exc_info()[2])
        where = ""
        for frame in reversed(frames):
            if frame.filename == path:
                where = "%s:%d" % (os.path.basename(path), frame.lineno)
                break
        return "import_raises", "%s: %s%s" % (
            type(exc).__name__, str(exc)[:160], " at " + where if where else "")
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
    if not hasattr(module, class_name):
        defined = [key for key, value in vars(module).items()
                   if isinstance(value, type)
                   and getattr(value, "__module__", "") == name]
        return "class_absent", ("file imports cleanly; classes defined here: %s"
                                % (", ".join(sorted(defined)) or "none"))
    return "imports_fine", "class %s is present" % class_name


MISSING_MODULE = re.compile(r"No module named '([^']+)'")


_INDEX = None
_LIBRARY = ("freqtrade", "numpy", "pandas", "technical", "scipy", "sklearn")


def _corpus_index():
    """Every importable name under `repos/`, mapped to where it is.

    Built once. Walking the corpus per lookup took longer than the freqtrade
    runs it was meant to explain - 900 repositories is a lot of directory to
    cross thirty-eight times.
    """
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    _INDEX = {}
    repos = os.path.join(ROOT, "repos")
    for base, dirs, files in os.walk(repos):
        for name in files:
            if name.endswith(".py"):
                _INDEX.setdefault(name[:-3], os.path.join(base, name))
        for name in dirs:
            if os.path.exists(os.path.join(base, name, "__init__.py")):
                _INDEX.setdefault(name, os.path.join(base, name))
    return _INDEX


def locate_module(dotted, source_file):
    """Where in the corpus the author's own module lives, or "".

    Preference goes to a copy inside the strategy's own repository, because
    that is the one the author imported. A module that exists in the corpus at
    all is on the author's side of the line: the import fails because our path
    does not reach it, which is ours to fix.
    """
    top = dotted.split(".")[0]
    if top in _LIBRARY:
        return ""              # a library internal, not an author module
    index = _corpus_index()
    if top not in index:
        return ""
    parts = (source_file or "").replace(os.sep, "/").split("/")
    if len(parts) > 2:
        own = os.path.join(ROOT, parts[0], parts[1])
        for base, dirs, files in os.walk(own):
            if top + ".py" in files:
                return os.path.relpath(os.path.join(base, top + ".py"),
                                       ROOT).replace(os.sep, "/")
            if top in dirs and os.path.exists(
                    os.path.join(base, top, "__init__.py")):
                return os.path.relpath(os.path.join(base, top),
                                       ROOT).replace(os.sep, "/")
    return os.path.relpath(index[top], ROOT).replace(os.sep, "/")


def family(message):
    for key, marker, verdict, note in FAMILIES:
        if marker in message:
            return key, verdict, note
    return "", "", ""


def triage(probe):
    """One record per blocked row: what stops it, and what may be done."""
    out = {}
    for row in blocked_rows():
        message = row["runtime_failure"] or ""
        record = {"strategy_id": row["strategy_id"],
                  "source_file": row["source_file"],
                  "runtime_failure": message}
        load = LOAD_FAILURE.search(message)
        key, verdict, note = family(message)
        if key:
            # A named family wins over the load probe. "Impossible to load
            # FreqaiModel 'CatboostClassifier'" is not a broken strategy file:
            # it is the FreqAI extras missing from the image, and probing the
            # strategy for a class that was never supposed to be in it reports
            # a fault that does not exist.
            record["family"] = key
            record["verdict"] = verdict
            record["note"] = note
        elif load:
            record["family"] = "class_not_loaded"
            if probe:
                kind, detail = probe_import(row["source_file"], load.group(1))
                record["probe"] = kind
                record["probe_detail"] = detail
                record["verdict"], record["note"] = PROBE_VERDICT[kind]
                missing = MISSING_MODULE.search(detail or "")
                if missing:
                    where = locate_module(missing.group(1), row["source_file"])
                    record["missing_module"] = missing.group(1)
                    record["module_found_at"] = where
                    if where:
                        record["family"] = "local_module_off_path"
                        record["verdict"] = "to_be_fixed"
                        record["note"] = (
                            "The module the author imports is in the corpus at "
                            "%s. Nothing is wrong with the strategy; our import "
                            "path does not include it." % where)
                    else:
                        record["family"] = "third_party_package"
                        record["verdict"] = "needs_a_look"
                        record["note"] = (
                            "Imports %s, which is not in the corpus and not in "
                            "the image. Installing an author's declared "
                            "dependency is legitimate, but it rebuilds the "
                            "pinned runtime, so it is one decision for all of "
                            "them rather than a per-row repair."
                            % missing.group(1))
            else:
                record["verdict"] = "needs_a_look"
                record["note"] = ("freqtrade's message conflates several "
                                  "causes; run with --probe to name this one")
        else:
            record["family"] = "individual"
            record["verdict"] = "needs_a_look"
            record["note"] = "one of a kind; read the message"
        out[row["strategy_id"]] = record
    return out


PROBE_VERDICT = {
    "imports_fine": ("to_be_fixed",
                     "The file imports and the class is there, so the failure "
                     "is in how we resolve or invoke it, not in the strategy."),
    "class_absent": ("to_be_fixed",
                     "The file imports cleanly but does not define the class "
                     "we ask for: our canonical-file mapping points at the "
                     "wrong file, which is ours to fix."),
    "import_raises": ("needs_a_look",
                      "The file raises on import. Whether that is a missing "
                      "dependency we can install or code that no longer runs "
                      "depends on the exception."),
    "not_importable": ("needs_a_look", "No loader for the path."),
    "file_missing": ("to_be_fixed",
                     "The canonical file is not on disk; the mapping is ours."),
}


def selftest():
    rows = blocked_rows()
    assert rows, "no blocked rows - has the basis label changed?"
    for key, marker, verdict, note in FAMILIES:
        assert verdict in ("to_be_fixed", "refuse_repair", "needs_a_look"), key
        assert len(note) > 40, key
    records = triage(probe=False)
    assert len(records) == len(rows)
    for record in records.values():
        assert record["verdict"], record["strategy_id"]
        assert record["note"], record["strategy_id"]
    for kind, (verdict, note) in PROBE_VERDICT.items():
        assert verdict in ("to_be_fixed", "refuse_repair", "needs_a_look"), kind
        assert note, kind
    print("blocked_triage selftest: PASS (%d blocked rows, %d families)"
          % (len(rows), len(FAMILIES)))


REPAIR_LIST = os.path.join(ROOT, "REPAIR_LIST.md")

ORDER = ("to_be_fixed", "needs_a_look", "refuse_repair")
VERDICT_TEXT = {
    "to_be_fixed": ("What stops the row is ours, or is the author's own words "
                    "under a name the framework has since changed. Repairing "
                    "it restores what they wrote."),
    "needs_a_look": ("Repairable in principle, but not by a rule that can be "
                     "written now - the decision differs row by row, or costs "
                     "something outside this row."),
    "refuse_repair": ("The strategy does not declare what freqtrade requires. "
                      "Supplying it would measure our invention under the "
                      "author's name."),
}


def write_list():
    """The repair list, grouped by what would be done and why."""
    records = json.load(io.open(OUTPUT, encoding="utf-8"))["results"]
    by_verdict = collections.defaultdict(lambda: collections.defaultdict(list))
    for record in records.values():
        by_verdict[record["verdict"]][record["family"]].append(record)
    lines = [
        "# Repair list - the %d rows that never ran" % len(records), "",
        "**Generated by `blocked_triage.py --probe --list`.** Regenerate it "
        "rather than editing it.", "",
        "None of these rows has been judged: freqtrade would not start them, "
        "so no gate ever saw them. That makes the question here different from "
        "everywhere else in this audit. It is not *is this strategy sound* but "
        "*would repairing it restore what the author wrote, or supply what "
        "they did not*.", "",
        "Freqtrade reports most load failures as `Impossible to load Strategy "
        "'X'. This class does not exist or contains Python code errors`, which "
        "names none of the three things it could be. Each file was therefore "
        "imported directly in the pinned runtime and the real exception "
        "recorded; that is what the families below are built from.", "",
    ]
    for verdict in ORDER:
        families = by_verdict.get(verdict)
        if not families:
            continue
        total = sum(len(rows) for rows in families.values())
        lines += ["## `%s` - %d strategies" % (verdict, total), "",
                  VERDICT_TEXT[verdict], ""]
        for family_name, rows in sorted(families.items(),
                                        key=lambda kv: -len(kv[1])):
            lines += ["### `%s` - %d" % (family_name, len(rows)), "",
                      rows[0]["note"], "", "| Strategy | Detail |", "|---|---|"]
            for record in sorted(rows, key=lambda r: r["strategy_id"]):
                detail = (record.get("module_found_at")
                          or record.get("probe_detail")
                          or record["runtime_failure"])
                lines.append("| `%s` | %s |" % (record["strategy_id"],
                                                detail[:140].replace("|", "/")))
            lines.append("")
    with io.open(REPAIR_LIST, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(chr(10).join(lines) + chr(10))
    return REPAIR_LIST


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true",
                        help="import each unloadable file and record why")
    parser.add_argument("--list", action="store_true",
                        dest="write_list", help="write REPAIR_LIST.md")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.write_list and not args.probe:
        print(write_list())
        return 0
    if args.selftest:
        selftest()
        return 0
    records = triage(args.probe)
    _write({"schema_version": 1, "probed": bool(args.probe),
            "results": records})
    verdicts = collections.Counter(r["verdict"] for r in records.values())
    families = collections.Counter(r["family"] for r in records.values())
    print("%d blocked rows" % len(records))
    for key, count in families.most_common():
        print("   %-24s %d" % (key, count))
    print()
    for key, count in verdicts.most_common():
        print("   %-16s %d" % (key, count))
    if args.probe:
        probes = collections.Counter(r.get("probe", "") for r in records.values()
                                     if r.get("probe"))
        print()
        for key, count in probes.most_common():
            print("   probe %-16s %d" % (key, count))
    if args.write_list:
        print(write_list())
    return 0


if __name__ == "__main__":
    sys.exit(main())
