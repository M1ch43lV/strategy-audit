# -*- coding: utf-8 -*-
"""Create narrowly proven Class 2 overlays for execution-profile failures.

Original repository files are never edited.  Generated overlays live under
``user_data/profile_repairs`` and the reproducible manifest is published as
``PROFILE_REPAIRS.json``.
"""
from __future__ import print_function

import ast
import csv
import hashlib
import io
import json
import os
import sys


ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "EXECUTION_PROFILES.csv")
SMOKE = os.path.join(ROOT, "PROFILE_SMOKE.json")
OUTPUT = os.path.join(ROOT, "PROFILE_REPAIRS.json")
OVERLAYS = os.path.join(ROOT, "user_data", "profile_repairs")


def _read(path):
    return io.open(path, encoding="utf-8", errors="strict").read()


def _sha(data):
    # The label distinguishes an integrity digest from an unlabelled 64-hex
    # exchange secret while retaining the complete digest.
    return "sha256_" + hashlib.sha256(data.encode("utf-8")).hexdigest()


def _offsets(source):
    starts = [0]
    for index, char in enumerate(source):
        if char == "\n":
            starts.append(index + 1)
    return starts


def _span(node, starts):
    return (starts[node.lineno - 1] + node.col_offset,
            starts[node.end_lineno - 1] + node.end_col_offset)


def _np_where(call):
    return (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "np" and call.func.attr == "where")


def patch_string_nan(source):
    """Restore NumPy 1's exact string coercion for nested string np.where."""
    tree = ast.parse(source)
    starts = _offsets(source)
    replacements = []
    for node in ast.walk(tree):
        if not _np_where(node) or len(node.args) < 3:
            continue
        inner, missing = node.args[1], node.args[2]
        if not (_np_where(inner) and len(inner.args) >= 3):
            continue
        if not all(isinstance(value, ast.Constant) and isinstance(value.value, str)
                   for value in inner.args[1:3]):
            continue
        if not (isinstance(missing, ast.Attribute)
                and isinstance(missing.value, ast.Name)
                and missing.value.id == "np" and missing.attr in ("NaN", "NAN")):
            continue
        replacements.append((*_span(missing, starts), "'nan'"))
    if not replacements:
        return source, 0
    for start, end, replacement in sorted(replacements, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source, len(replacements)


def patch_parameter_spaces(source):
    """Assign a neutral backtest space to otherwise unresolvable parameters.

    Preconditions: a class-level IntParameter call has no space, and its name
    occurs in neither a buy_params nor sell_params dictionary.  The space label
    changes hyperopt organization, not the default/range used by backtesting.
    """
    tree = ast.parse(source)
    starts = _offsets(source)
    param_dict_keys = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id in ("buy_params", "sell_params")
            for t in node.targets
        ) and isinstance(node.value, ast.Dict):
            param_dict_keys.update(
                key.value for key in node.value.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            )
    insertions = []
    for cls in (node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)):
        for statement in cls.body:
            if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
                continue
            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
            if len(targets) != 1 or not isinstance(targets[0], ast.Name):
                continue
            name = targets[0].id
            call = statement.value
            if not (isinstance(call, ast.Call) and getattr(call.func, "id", "") == "IntParameter"):
                continue
            if any(keyword.arg == "space" for keyword in call.keywords) or name in param_dict_keys:
                continue
            start, end = _span(call, starts)
            if source[end - 1] != ")":
                raise ValueError("cannot locate IntParameter closing parenthesis")
            insertions.append((end - 1, ', space="buy"'))
    for position, text in sorted(insertions, reverse=True):
        source = source[:position] + text + source[position:]
    return source, len(insertions)


def patch_pandas_object_marker(source):
    old = "dataframe['pattern_marker'] = np.nan"
    new = "dataframe['pattern_marker'] = pd.Series(np.nan, index=dataframe.index, dtype='object')"
    count = source.count(old)
    if count != 1 or "dataframe.loc[idx, 'pattern_marker'] = label" not in source:
        return source, 0
    return source.replace(old, new), 1


def patch_dormant_signal_dtype(source):
    pairs = [
        ('df.loc[:, "enter_long"] = ""', 'df.loc[:, "enter_long"] = False'),
        ('df.loc[:, "enter_short"] = ""', 'df.loc[:, "enter_short"] = False'),
    ]
    if any(source.count(old) != 1 for old, _new in pairs):
        return source, 0
    if not all(('df.loc[:, "%s"] = item_%s_entry' % (column, side)) in source
               for column, side in (("enter_long", "long"), ("enter_short", "short"))):
        return source, 0
    for old, new in pairs:
        source = source.replace(old, new)
    return source, 2


def patch_pywavelets_writable_buffer(source):
    """Copy a read-only pandas rolling window before passing it to PyWavelets."""
    old = "pywt.wavedec(data, wavelet, mode=wmode)"
    new = "pywt.wavedec(np.array(data, copy=True), wavelet, mode=wmode)"
    count = source.count(old)
    if count != 1 or "import numpy as np" not in source:
        return source, 0
    return source.replace(old, new), 1


def patch_pandas_writable_numpy(source):
    """Request the writable ndarray that legacy pandas returned implicitly."""
    old = 'df["gain"].shift(-self.lookahead).to_numpy()'
    new = 'df["gain"].shift(-self.lookahead).to_numpy(copy=True)'
    count = source.count(old)
    if count != 1 or "future_gain[-self.lookahead :] = 0.0" not in source:
        return source, 0
    return source.replace(old, new), 1


def patch_futures_informative_pair(source):
    """Use Freqtrade's current settled-pair spelling for the same BTC perpetual."""
    old = "@informative('1d', 'BTC/USDT')"
    new = "@informative('1d', 'BTC/USDT:USDT')"
    count = source.count(old)
    if count != 1 or "can_short = True" not in source:
        return source, 0
    return source.replace(old, new), 1


def patch_empty_loc_signals(source):
    """Replace obsolete empty-index signal creation with explicit numeric columns."""
    replacements = [
        ("dataframe.loc[(), ['enter_long', 'enter_tag']] = (0, 'long_in')",
         "dataframe.loc[:, 'enter_long'] = 0"),
        ("dataframe.loc[(), ['exit_short', 'exit_tag']] = (0, 'short_out')",
         "dataframe.loc[:, 'exit_short'] = 0"),
        ("dataframe.loc[(), ['exit_long', 'exit_tag']] = (0, 'long_out')",
         "dataframe.loc[:, 'exit_long'] = 0"),
    ]
    if any(source.count(old) != 1 for old, _new in replacements):
        return source, 0
    for old, new in replacements:
        source = source.replace(old, new)
    return source, len(replacements)


def _load():
    with io.open(MANIFEST, newline="", encoding="utf-8-sig") as handle:
        rows = {row["strategy_id"]: row for row in csv.DictReader(handle)}
    smoke = json.load(io.open(SMOKE, encoding="utf-8")).get("results") or {}
    return rows, smoke


def _write_json(data, path):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(tmp, path)


def build():
    rows, smoke = _load()
    repairs_by_strategy = {}
    if os.path.exists(OUTPUT):
        previous = json.load(io.open(OUTPUT, encoding="utf-8"))
        for repair in previous.get("repairs", []):
            for field in ("input_sha256", "output_sha256"):
                if repair.get(field) and not repair[field].startswith("sha256_"):
                    repair[field] = "sha256_" + repair[field]
            overlay = os.path.join(ROOT, repair["overlay_file"].replace("/", os.sep))
            if os.path.exists(overlay):
                repairs_by_strategy[repair["strategy"]] = repair
    for strategy, result in sorted(smoke.items()):
        if result.get("status") != "failed" or strategy not in rows:
            continue
        row = rows[strategy]
        prior = repairs_by_strategy.get(strategy)
        selected_file = prior["overlay_file"] if prior else row["canonical_file"]
        path = os.path.abspath(os.path.join(ROOT, selected_file.replace("/", os.sep)))
        if not os.path.exists(path):
            continue
        original = _read(path)
        changed = original
        rules = []
        equivalence = "strict_equivalent"

        if "DType <class 'numpy.dtypes.StrDType'>" in result.get("why", ""):
            changed, count = patch_string_nan(changed)
            if count:
                rules.append("numpy1_string_nan_coercion")
        if "Cannot determine parameter space" in result.get("why", ""):
            changed, count = patch_parameter_spaces(changed)
            if count:
                rules.append("parameter_space_default_only")
        if "Invalid value 'A' for dtype 'float64'" in result.get("why", ""):
            changed, count = patch_pandas_object_marker(changed)
            if count:
                rules.append("pandas_object_upcast")
                equivalence = "output_equivalent"
        if "Invalid value '[False False False" in result.get("why", ""):
            changed, count = patch_dormant_signal_dtype(changed)
            if count:
                rules.append("freqtrade_signal_dtype")
                equivalence = "output_equivalent"
        if "buffer source array is read-only" in result.get("why", ""):
            changed, count = patch_pywavelets_writable_buffer(changed)
            if count:
                rules.append("pywavelets_writable_buffer")
        if "assignment destination is read-only" in result.get("why", ""):
            changed, count = patch_pandas_writable_numpy(changed)
            if count:
                rules.append("pandas_writable_numpy")
        if "Informative dataframe for (BTC/USDT, 1d, futures) is empty" in result.get("why", ""):
            changed, count = patch_futures_informative_pair(changed)
            if count:
                rules.append("futures_settlement_pair_syntax")
        if "Something has gone wrong, please report a bug" in result.get("why", ""):
            changed, count = patch_empty_loc_signals(changed)
            if count:
                rules.append("empty_loc_signal_initialization")
                equivalence = "output_equivalent"

        if not rules or changed == original:
            continue
        os.makedirs(OVERLAYS, exist_ok=True)
        destination = os.path.join(OVERLAYS, "%s.py" % strategy)
        tmp = destination + ".tmp"
        io.open(tmp, "w", encoding="utf-8", newline="").write(changed)
        os.replace(tmp, destination)
        all_rules = list(prior.get("repair_rules", [])) if prior else []
        all_rules.extend(rule for rule in rules if rule not in all_rules)
        if prior and prior.get("equivalence_status") == "output_equivalent":
            equivalence = "output_equivalent"
        repairs_by_strategy[strategy] = {
            "strategy": strategy,
            "population": "repaired",
            "repair_class": "class2",
            "repair_rules": all_rules,
            "equivalence_status": equivalence,
            "base_file": prior["base_file"] if prior else row["canonical_file"],
            "overlay_file": os.path.relpath(destination, ROOT).replace(os.sep, "/"),
            "input_sha256": prior["input_sha256"] if prior else _sha(original),
            "output_sha256": _sha(changed),
            "source_tree": "profile-class2-overlay",
        }
    repairs = [repairs_by_strategy[name] for name in sorted(repairs_by_strategy)]
    return {"schema_version": 1, "repairs": repairs}


def selftest():
    source = "x = np.where(ok, np.where(up, 'down', 'up'), np.NaN)\n"
    patched, count = patch_string_nan(source)
    assert count == 1 and patched.endswith("'nan')\n")
    numeric = "x = np.where(ok, np.where(up, 1.0, 2.0), np.NaN)\n"
    assert patch_string_nan(numeric) == (numeric, 0)
    wavelet = "import numpy as np\nx = pywt.wavedec(data, wavelet, mode=wmode)\n"
    assert patch_pywavelets_writable_buffer(wavelet)[1] == 1
    writable = ('future_gain = df["gain"].shift(-self.lookahead).to_numpy()\n'
                'future_gain[-self.lookahead :] = 0.0\n')
    assert "copy=True" in patch_pandas_writable_numpy(writable)[0]
    futures = "can_short = True\n@informative('1d', 'BTC/USDT')\n"
    assert "BTC/USDT:USDT" in patch_futures_informative_pair(futures)[0]
    empty = ("dataframe.loc[(), ['enter_long', 'enter_tag']] = (0, 'long_in')\n"
             "dataframe.loc[(), ['exit_short', 'exit_tag']] = (0, 'short_out')\n"
             "dataframe.loc[(), ['exit_long', 'exit_tag']] = (0, 'long_out')\n")
    assert patch_empty_loc_signals(empty)[1] == 3
    print("profile_repairs selftest: PASS")


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if "--selftest" in argv:
        selftest()
        return 0
    data = build()
    _write_json(data, OUTPUT)
    print("profile Class 2 overlays: %d" % len(data["repairs"]))
    for row in data["repairs"]:
        print("  %-38s %s (%s)" % (
            row["strategy"], ",".join(row["repair_rules"]), row["equivalence_status"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
