# -*- coding: utf-8 -*-
"""Create narrowly proven Class 2 overlays for execution-profile failures.

Original repository files are never edited.  Generated overlays live under
``user_data/profile_repairs`` and the reproducible manifest is published as
``evidence/PROFILE_REPAIRS.json``.
"""
from __future__ import print_function

import ast
import csv
import hashlib
import io
import json
import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "evidence/EXECUTION_PROFILES.csv")
SMOKE = os.path.join(ROOT, "evidence/PROFILE_SMOKE.json")
OUTPUT = os.path.join(ROOT, "evidence/PROFILE_REPAIRS.json")
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


def patch_single_empty_exit(source):
    """Initialize Solipsis_v4's deliberately empty exit signal numerically."""
    old = "dataframe.loc[(), ['exit_long', 'exit_tag']] = (0, 'long_out')"
    new = "dataframe.loc[:, 'exit_long'] = 0"
    if source.count(old) != 1 or "class Solipsis_v4(IStrategy):" not in source:
        return source, 0
    return source.replace(old, new), 1


def patch_quickbuy_timeframe_literal(source):
    """Normalize the author's unambiguous legacy one-hour spelling."""
    old = "timeframe = '1hr'"
    new = "timeframe = '1h'"
    if source.count(old) != 1 or "class QuickBuyStrategy(IStrategy):" not in source:
        return source, 0
    return source.replace(old, new), 1


def patch_missing_dataframe_import(source):
    """Supply the standard pandas annotation symbol referenced by BlueEyes."""
    anchor = "from freqtrade.strategy.interface import IStrategy\n"
    if (source.count(anchor) != 1 or "class BlueEyes_MPP_v1(IStrategy):" not in source
            or "DataFrame" not in source or "from pandas import DataFrame" in source):
        return source, 0
    return source.replace(anchor, anchor + "from pandas import DataFrame\n"), 1


def patch_missing_sibling_pivots_import(source):
    """Import BlueEyes' referenced helper from the sibling file that defines it."""
    anchor = "from pandas import DataFrame\n"
    plain = "from Miku_PP_v3 import pivots_points\n"
    loader = ("import os\nimport sys\n"
              "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "
              "'..', '..', 'repos', 'PeetCrypto_freqtrade-stuff')))\n"
              + plain)
    if ("class BlueEyes_MPP_v1(IStrategy):" not in source
            or "pivots_points(dataframe1d)" not in source):
        return source, 0
    if plain in source and "sys.path.insert(0" not in source:
        return source.replace(plain, loader), 1
    if source.count(anchor) != 1 or plain in source:
        return source, 0
    return source.replace(anchor, anchor + loader), 1


def patch_all_na_idxmax(source):
    """Restore pre-pandas-3 all-NA idxmax behavior without affecting valid rows."""
    old = "momentum_df.idxmax(axis=1).reindex(dataframe.index)"
    new = ("momentum_df.apply(lambda row: row.idxmax() if row.notna().any() "
           "else None, axis=1).reindex(dataframe.index)")
    if source.count(old) != 1 or "class BestSingleAssetPortfolio(IStrategy):" not in source:
        return source, 0
    return source.replace(old, new), 1


def patch_min_roi_call_signature(source):
    """Pass arguments added to Freqtrade's ROI-table helper."""
    old = "self.min_roi_reached_entry(trade_dur)"
    new = "self.min_roi_reached_entry(trade, trade_dur, current_time)"
    count = source.count(old)
    if count != 2 or "class Solipsis_v4(IStrategy):" not in source:
        return source, 0
    return source.replace(old, new), count


def patch_import_time_root_logging(source):
    """Remove Ichi's process-wide import-time logging reconfiguration.

    The strategy deletes every root handler and redirects all Freqtrade output
    to a dated file while the module is imported.  Removing only that setup is
    output-equivalent for indicators and signals and keeps analyzer evidence on
    the invoking process' configured streams.
    """
    if "class Ichi(IStrategy):" not in source:
        return source, 0
    old = '''LOG_FILENAME = datetime.now().strftime('logfile_%d_%m_%Y.log')
os.system("rm " + LOG_FILENAME)

# This will have an impact on all the logging from FreqTrade, when using other strategies than this one !!!
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s :: %(message)s')

logging.info("test")
'''
    old = old.replace("strategies than this one !!!\n",
                      "strategies than this one !!! \n")
    if source.count(old) != 1:
        return source, 0
    return source.replace(old, ""), 1


def patch_fott_quadratic_recurrence(source):
    """Linearize two unused-variable fixpoint loops in FOttStrategy.ott().

    Each original outer iteration advances a shift-based recurrence by one
    row. Repeating it ``len(df)`` times reaches exactly the same fixed point as
    a single left-to-right recurrence, but with quadratic instead of linear
    cost. The exact source anchors keep this rule file-specific.
    """
    if "class FOttStrategy(IStrategy):" not in source:
        return source, 0
    old_var = '''        df["Var"] = 0.0
        for i in range(pds, len(df)):
            df["Var"].iat[i] = (alpha * df["CMO"].iat[i] * df["close"].iat[i]) + (
                1 - alpha * df["CMO"].iat[i]
            ) * df["Var"].iat[i - 1]
'''
    new_var = '''        var = np.zeros(len(df), dtype=float)
        for i in range(pds, len(df)):
            var[i] = (alpha * df["CMO"].iat[i] * df["close"].iat[i]) + (
                1 - alpha * df["CMO"].iat[i]
            ) * var[i - 1]
        df["Var"] = var
'''
    if source.count(old_var) != 1:
        return source, 0
    source = source.replace(old_var, new_var)
    start = source.find('        df["longstop"] = 0.0\n')
    end = source.find('        # get xover\n', start)
    if start < 0 or end < 0 or '        for i in df["UD"]:\n' not in source[start:end]:
        return source, 0
    stops = '''        longstop = np.empty(len(df), dtype=float)
        shortstop = np.empty(len(df), dtype=float)
        if len(df):
            longstop[0] = df["newlongstop"].iat[0]
            shortstop[0] = df["newshortstop"].iat[0]
        for i in range(1, len(df)):
            previous_long = longstop[i - 1]
            previous_short = shortstop[i - 1]
            new_long = df["newlongstop"].iat[i]
            new_short = df["newshortstop"].iat[i]
            longstop[i] = (max(new_long, previous_long)
                           if df["Var"].iat[i] > previous_long else new_long)
            shortstop[i] = (min(new_short, previous_short)
                            if df["Var"].iat[i] < previous_short else new_short)
        df["longstop"] = longstop
        df["shortstop"] = shortstop

'''
    changed = source[:start] + stops + source[end:]
    start = changed.find('        df["trend"] = 0\n')
    end = changed.find('        # get OTT\n', start)
    if start < 0 or end < 0 or '        for i in df["UD"]:\n' not in changed[start:end]:
        return source, 0
    trend = '''        trend = np.empty(len(df), dtype=float)
        direction = np.empty(len(df), dtype=float)
        if len(df):
            trend[0] = np.nan
            direction[0] = 1
        for i in range(1, len(df)):
            trend[i] = (1 if df["xshortstop"].iat[i] == 1 else
                        -1 if df["xlongstop"].iat[i] == 1 else trend[i - 1])
            direction[i] = (1 if df["xshortstop"].iat[i] == 1 else
                            -1 if df["xlongstop"].iat[i] == 1 else direction[i - 1])
        df["trend"] = trend
        df["dir"] = direction

'''
    return changed[:start] + trend + changed[end:], 3


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
            if not count:
                changed, count = patch_single_empty_exit(changed)
            if count:
                rules.append("empty_loc_signal_initialization")
                equivalence = "output_equivalent"
        if "invalid literal for int() with base 10: '1h'" in result.get("why", ""):
            changed, count = patch_quickbuy_timeframe_literal(changed)
            if count:
                rules.append("legacy_one_hour_timeframe_spelling")
        if "unsupported callable" in result.get("why", ""):
            changed, count = patch_missing_dataframe_import(changed)
            if count:
                rules.append("missing_dataframe_annotation_import")
        if ("name 'pivots_points' is not defined" in result.get("why", "")
                or (strategy == "BlueEyes_MPP_v1"
                    and "Impossible to load Strategy" in result.get("why", ""))):
            changed, count = patch_missing_sibling_pivots_import(changed)
            if count:
                rules.append("restore_sibling_pivots_helper")
        if "Encountered all NA values" in result.get("why", ""):
            changed, count = patch_all_na_idxmax(changed)
            if count:
                rules.append("pandas_all_na_idxmax_compatibility")
                equivalence = "output_equivalent"
        if "min_roi_reached_entry() missing 2 required positional arguments" in result.get("why", ""):
            changed, count = patch_min_roi_call_signature(changed)
            if count:
                rules.append("current_min_roi_helper_signature")

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
    # FOttStrategy loads and trades in the short smoke, so it is not part of
    # the failure-driven loop above. Its quadratic recurrence only becomes an
    # execution blocker on the frozen full window and is handled explicitly.
    strategy = "FOttStrategy"
    if strategy in rows:
        row = rows[strategy]
        base_file = row.get("original_file") or row["canonical_file"]
        original = _read(os.path.join(ROOT, base_file.replace("/", os.sep)))
        changed, count = patch_fott_quadratic_recurrence(original)
        if count:
            os.makedirs(OVERLAYS, exist_ok=True)
            destination = os.path.join(OVERLAYS, strategy + ".py")
            io.open(destination, "w", encoding="utf-8", newline="").write(changed)
            repairs_by_strategy[strategy] = {
                "strategy": strategy, "population": "repaired",
                "repair_class": "class2",
                "repair_rules": ["linearize_quadratic_fixpoint_recurrence"],
                "equivalence_status": "strict_equivalent",
                "base_file": base_file,
                "overlay_file": os.path.relpath(destination, ROOT).replace(os.sep, "/"),
                "input_sha256": _sha(original), "output_sha256": _sha(changed),
                "source_tree": "profile-class2-overlay",
            }
    # Ichi's import-time root logger reset hides the recursive analyzer's
    # startup-candle refusal and result table.  This is independent of smoke
    # success, so publish a narrow source overlay explicitly.
    strategy = "Ichi"
    if strategy in rows:
        row = rows[strategy]
        base_file = row.get("original_file") or row["canonical_file"]
        original = _read(os.path.join(ROOT, base_file.replace("/", os.sep)))
        changed, count = patch_import_time_root_logging(original)
        if count:
            os.makedirs(OVERLAYS, exist_ok=True)
            destination = os.path.join(OVERLAYS, strategy + ".py")
            io.open(destination, "w", encoding="utf-8", newline="").write(changed)
            repairs_by_strategy[strategy] = {
                "strategy": strategy, "population": "repaired",
                "repair_class": "class2",
                "repair_rules": ["remove_import_time_root_logging_reset"],
                "equivalence_status": "output_equivalent",
                "base_file": base_file,
                "overlay_file": os.path.relpath(destination, ROOT).replace(os.sep, "/"),
                "input_sha256": _sha(original), "output_sha256": _sha(changed),
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
    solipsis = ("class Solipsis_v4(IStrategy):\n"
                "dataframe.loc[(), ['exit_long', 'exit_tag']] = (0, 'long_out')\n")
    assert patch_single_empty_exit(solipsis)[1] == 1
    quickbuy = "class QuickBuyStrategy(IStrategy):\n    timeframe = '1hr'\n"
    assert patch_quickbuy_timeframe_literal(quickbuy)[1] == 1
    blue = ("from freqtrade.strategy.interface import IStrategy\n"
            "class BlueEyes_MPP_v1(IStrategy):\n    def f(self, x: DataFrame): pass\n")
    assert patch_missing_dataframe_import(blue)[1] == 1
    portfolio = ("class BestSingleAssetPortfolio(IStrategy):\n"
                 "x = momentum_df.idxmax(axis=1).reindex(dataframe.index)\n")
    assert "notna" in patch_all_na_idxmax(portfolio)[0]
    roi = ("class Solipsis_v4(IStrategy):\n"
           "a = self.min_roi_reached_entry(trade_dur)\n"
           "b = self.min_roi_reached_entry(trade_dur)\n")
    assert patch_min_roi_call_signature(roi)[1] == 2
    ichi = ("import logging\nimport os\nclass Ichi(IStrategy):\n    pass\n")
    assert patch_import_time_root_logging(ichi) == (ichi, 0)
    ichi = ("import logging\nimport os\n\n"
            "LOG_FILENAME = datetime.now().strftime('logfile_%d_%m_%Y.log')\n"
            "os.system(\"rm \" + LOG_FILENAME)\n\n"
            "# This will have an impact on all the logging from FreqTrade, when using other strategies than this one !!!" + " \n"
            "for handler in logging.root.handlers[:]:\n"
            "    logging.root.removeHandler(handler)\n"
            "logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format='%(asctime)s :: %(message)s')\n\n"
            "logging.info(\"test\")\n\n\nclass Ichi(IStrategy):\n    pass\n")
    assert patch_import_time_root_logging(ichi)[1] == 1
    fott = ('class FOttStrategy(IStrategy):\n'
            '        df["longstop"] = 0.0\n        for i in df["UD"]:\n'
            '            pass\n        # get xover\n'
            '        df["trend"] = 0\n        for i in df["UD"]:\n'
            '            pass\n        # get OTT\n')
    fott = fott.replace('class FOttStrategy(IStrategy):\n',
        'class FOttStrategy(IStrategy):\n        df["Var"] = 0.0\n'
        '        for i in range(pds, len(df)):\n'
        '            df["Var"].iat[i] = (alpha * df["CMO"].iat[i] * df["close"].iat[i]) + (\n'
        '                1 - alpha * df["CMO"].iat[i]\n'
        '            ) * df["Var"].iat[i - 1]\n')
    assert patch_fott_quadratic_recurrence(fott)[1] == 3
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
