# -*- coding: utf-8 -*-
"""patch_class2 - mechanical, behaviour-preserving patches to strategy files.

This is the only part of the pipeline that edits overlay copies of strategy
code. Its results belong to the repaired population, with the source-edit class
and behavior-equivalence status recorded explicitly. Everything else repairs
the environment and leaves the published code alone.

THE STANDARD EVERY RULE MUST MEET. A patch is allowed only when it can be
*proven* not to change trading behaviour - a dead assignment nothing reads, a
parameter space the file itself already states, an identical operation under a
new name. Each rule therefore carries a `precondition` that is evaluated against
the specific file and must return True before anything is written. A rule whose
precondition cannot be established SKIPS the file and says why. Guessing what
the author meant is not repair; it is authorship, and it does not belong in an
audit.

WHAT IS WRITTEN WHERE. Originals in `repos/` are never touched. Patched copies
go to `repair/patched/<same relative path>` and a unified diff per file goes to
`repair/patched/diffs/`. The measurement then points `--strategy-path` at the
overlay. Original and repaired implementations remain physically separate for
paired sensitivity; the canonical corpus selects at most one per strategy and
run profile. Class 1/Class 2 remain provenance fields.

    python repair/patch_class2.py --dry-run    report what would be patched
    python repair/patch_class2.py              write overlay and diffs
"""
import argparse
import ast
import csv
import difflib
import io
import json
import os
import re
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUD = ROOT
OVERLAY = os.path.join(ROOT, "repair", "patched")
DIFFS = os.path.join(OVERLAY, "diffs")

AUTO_SPACES = ("buy", "sell", "enter", "exit", "protection")


# ───────────────────────── rule 1: dead np.where with mixed dtypes ──────────

RX_PMX = re.compile(
    r"(np\.where\(\s*\(pm_arr\s*>\s*0\.00\)\s*,\s*"
    r"np\.where\(\s*\(mavalue\s*<\s*pm_arr\)\s*,\s*'down'\s*,\s*'up'\s*\)\s*,\s*)"
    r"np\.NaN(\s*\))"
)


def pre_pmx(src, path):
    """Provable only if the column the expression feeds is never read.

    numpy 1 silently merged the string branches and the float NaN into a string
    array; numpy 2 refuses. The faithful replacement is the string 'nan', which
    is exactly what numpy 1 produced. That fidelity argument is secondary here:
    the precondition below establishes that nothing reads the value at all, so
    the patch cannot affect any trading decision.
    """
    if not RX_PMX.search(src):
        return False, "expression not present"
    # Decided on the AST, not by counting text. The first version of this check
    # used a regex plus an `if not m or A and B` whose precedence made it far
    # laxer than intended - it could have passed a file where the column IS
    # read. Store/Load contexts answer the question exactly.
    try:
        with warnings.catch_warnings():
            # Corpus escapes are often invalid; the source hash is the identity.
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(src)
    except SyntaxError as e:
        return False, "cannot parse file: %s" % str(e)[:60]
    stores, loads = 0, 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        if not (isinstance(node.value, ast.Name) and node.value.id == "dataframe"):
            continue
        key = node.slice
        if not (isinstance(key, ast.Constant) and key.value == "pmx"):
            continue
        if isinstance(node.ctx, ast.Store):
            stores += 1
        else:
            loads += 1
    if stores == 0:
        return False, "dataframe['pmx'] never assigned - unexpected shape, skipping"
    if loads > 0:
        return False, ("dataframe['pmx'] is READ %d time(s) - value is used, "
                       "patch not provably neutral" % loads)
    return True, ("dataframe['pmx'] has %d store(s) and 0 loads - write-only, "
                  "so the value cannot affect any trading decision" % stores)


def apply_pmx(src):
    return RX_PMX.sub(r"\1'nan'\2", src)


# ───────────────────── rule 2: hyperopt parameter without a space ───────────

RX_PARAM = re.compile(
    r"^(?P<indent>\s*)(?P<name>\w+)\s*=\s*"
    r"(?P<cls>Decimal|Integer|Int|Real|Categorical|Boolean)Parameter\s*\((?P<args>[^\n]*)\)\s*$",
    re.M)


def _params_dict(src, which):
    """Keys of the strategy's buy_params / sell_params literal, or None."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(src)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == which and isinstance(node.value, ast.Dict):
                    return {k.value for k in node.value.keys
                            if isinstance(k, ast.Constant) and isinstance(k.value, str)}
    return None


def pre_space(src, path):
    """freqtrade infers a parameter's space from a `buy_`/`sell_` name prefix or
    an explicit `space=`. Older versions were lenient; 2026.7 raises
    "Cannot determine parameter space for X".

    The patch is only provable when the file itself states the answer: the
    parameter's stored value sits in `buy_params` or `sell_params`, and in
    exactly one of them. Renaming the attribute to carry a prefix would be the
    obvious alternative and is WRONG - the params-dict key would no longer
    match, the tuned value would be silently dropped, and `default=` would take
    over. That is a behaviour change wearing the mask of a rename.
    """
    buy = _params_dict(src, "buy_params") or set()
    sell = _params_dict(src, "sell_params") or set()
    targets = []
    for m in RX_PARAM.finditer(src):
        name, args = m.group("name"), m.group("args")
        if "space" in args:
            continue
        if any(name.startswith(s + "_") for s in AUTO_SPACES):
            continue
        in_buy, in_sell = name in buy, name in sell
        if in_buy and in_sell:
            continue                      # ambiguous - the file does not decide
        if not in_buy and not in_sell:
            continue                      # nothing states the space
        targets.append((name, "buy" if in_buy else "sell"))
    if not targets:
        return False, "no parameter both lacking a space and named in a params dict"
    return True, "space stated by the file itself: " + ", ".join(
        "%s -> %s_params" % (n, s) for n, s in targets)


def apply_space(src):
    buy = _params_dict(src, "buy_params") or set()
    sell = _params_dict(src, "sell_params") or set()

    def repl(m):
        name, args = m.group("name"), m.group("args")
        if "space" in args or any(name.startswith(s + "_") for s in AUTO_SPACES):
            return m.group(0)
        in_buy, in_sell = name in buy, name in sell
        if in_buy == in_sell:
            return m.group(0)
        space = "buy" if in_buy else "sell"
        return "%s%s = %sParameter(%s, space='%s')" % (
            m.group("indent"), name, m.group("cls"), args.rstrip().rstrip(","), space)

    return RX_PARAM.sub(repl, src)


# ─────────────── rule 3: Rolling.any - DETECT ONLY, never patched ───────────

RX_ROLLING_ANY = re.compile(r"\.rolling\([^)]*\)\s*\.any\(\)")


def pre_rolling_any(src, path):
    """pandas removed `Rolling.any`. `.rolling(n).sum() > 0` is equivalent for
    boolean data - but only away from the first n-1 rows, where the old method
    and the replacement disagree about incomplete windows, and where the calling
    code often applies `~`.

    That difference lands exactly on the warm-up region, which is where entry
    signals are most fragile. Equivalence is therefore NOT proven, so this rule
    reports and never writes. Listed here so the case is visible rather than
    quietly absent.
    """
    if RX_ROLLING_ANY.search(src):
        return False, ("Rolling.any present - NOT patched: behaviour at incomplete "
                       "windows is not provably identical; needs case-by-case review")
    return False, "not present"


# ───────── rule 4: Rolling.any where the disagreement is provably masked ────

RX_A9AV_ANY = re.compile(
    r"\(~dataframe\[(?P<q>['\"])(?P<col>buy_signal|sell_signal)(?P=q)\]"
    r"\.rolling\(window=self\.opposing_signal_filter\.value\)\.any\(\)\)")
RX_MASK_TERM = re.compile(r"dataframe\[['\"]volume['\"]\]\s*>\s*dataframe\[['\"]SMA_9['\"]\]")
RX_INTPARAM = re.compile(
    r"^\s*(?P<name>\w+)\s*=\s*IntParameter\(\s*(?P<lo>\d+)\s*,\s*(?P<hi>\d+)", re.M)


def pre_rolling_any_masked(src, path):
    """Patch `.rolling(n).any()` ONLY where the rows the replacements disagree
    about cannot reach the result.

    The generic rule below refuses this substitution, and rightly: candidate
    replacements disagree in the first n-1 rows, and which of them matched the
    removed `Rolling.any` can no longer be observed. Here the disagreement is
    provably masked, and the precondition checks each step rather than trusting
    the argument:

      1. the term is ANDed with `volume > SMA_9`, where SMA_9 is
         `rolling(length).mean()` - NaN for its first length-1 rows, and
         `NaN > x` is False, so those rows cannot produce a signal at all;
      2. the disputed rows are 0 .. n-2 with n = opposing_signal_filter;
      3. from the declared parameter ranges, max(n) <= min(length), so
         n-2 < length-1 across the WHOLE declared space, not merely at the
         defaults.

    Anything that fails to establish (1)-(3) is skipped. The proof is specific
    to this file's shape; it is checked here rather than assumed, and the
    generic rule stays refuse-only because it cannot check it.
    """
    if not RX_A9AV_ANY.search(src):
        return False, "guarded rolling().any() shape not present"
    if not RX_MASK_TERM.search(src):
        return False, "masking term `volume > SMA_9` not found - not provably masked"
    params = {m.group("name"): (int(m.group("lo")), int(m.group("hi")))
              for m in RX_INTPARAM.finditer(src)}
    if "length" not in params or "opposing_signal_filter" not in params:
        return False, "cannot read the declared ranges of length / opposing_signal_filter"
    n_hi = params["opposing_signal_filter"][1]
    len_lo = params["length"][0]
    if n_hi > len_lo:
        return False, ("max(opposing_signal_filter)=%d exceeds min(length)=%d - "
                       "disputed rows can escape the mask" % (n_hi, len_lo))
    return True, ("disputed rows 0..n-2 (n<=%d) always fall inside the %d+ rows "
                  "where SMA_9 is NaN and the ANDed term is False" % (n_hi, len_lo - 1))


def apply_rolling_any_masked(src):
    def repl(m):
        col = m.group("col")
        return ("(~(dataframe['%s'].rolling(window=self.opposing_signal_filter.value)"
                ".max() > 0))" % col)
    return RX_A9AV_ANY.sub(repl, src)


# ───── rule 5: explicit rolling Spearman correlation for ViNBuyVws ─────────

# pandas never accepted ``method=`` on Rolling.corr.  The author did state the
# intended statistic, however, and Series.corr has supported that spelling.
# This remains an intent-preserving *unverified* Class 2 overlay: no historical
# run of the invalid call exists to prove output equivalence.
RX_VIN_SPEARMAN = re.compile(
    r"(?P<left>ef\['index'\])\.rolling\(window=(?P<window>[^,]+),\s*"
    r"min_periods=(?P<minimum>[^)]+)\)\.corr\("
    r"(?P<right>ef\['(?:hlc3_adj|close)'\]),\s*method=['\"]spearman['\"]\)"
)
VIN_SPEARMAN_HELPER = '''\
def rolling_spearman_corr(left, right, *, window, min_periods):
    """Rolling Spearman correlation using pandas' supported Series API."""
    return left.rolling(window=window, min_periods=min_periods).apply(
        lambda sample: sample.corr(right.reindex(sample.index), method="spearman"),
        raw=False)
'''


def pre_vin_spearman(src, path):
    if "class ViNBuyVws" not in src:
        return False, "ViNBuyVws class not present"
    matches = list(RX_VIN_SPEARMAN.finditer(src))
    if len(matches) != 3:
        return False, "expected exactly three explicit ViN rolling Spearman calls, found %d" % len(matches)
    if "def rolling_spearman_corr(" in src:
        return False, "explicit rolling Spearman helper already present"
    return True, ("three invalid Rolling.corr(method='spearman') calls name the "
                  "intended statistic; rewrite through supported Series.corr")


def apply_vin_spearman(src):
    def replace(match):
        return ("rolling_spearman_corr(%s, %s, window=%s, min_periods=%s)" %
                (match.group("left"), match.group("right"),
                 match.group("window"), match.group("minimum")))
    out = RX_VIN_SPEARMAN.sub(replace, src)
    marker = "\nclass ViNBuyVws(ViN):"
    if marker not in out:
        return src
    return out.replace(marker, "\n\n" + VIN_SPEARMAN_HELPER + marker, 1)


# ───────── rule 5: fillna(method=...) and sum(level=...) - pandas renames ───

FILL_MAP = {"ffill": "ffill", "pad": "ffill", "bfill": "bfill", "backfill": "bfill"}
RX_FILLNA = re.compile(r"\.fillna\(\s*(?P<args>[^()]*)\)")
RX_METHOD_ARG = re.compile(r"""method\s*=\s*['"](?P<m>ffill|pad|bfill|backfill)['"]""")
RX_SUM_LEVEL = re.compile(r"\.(?P<fn>sum|mean|min|max|std|var|count)\(\s*level\s*=\s*(?P<lv>\d+)\s*\)")
RX_CHAINED_FILL_INPLACE = re.compile(
    r"^(?P<i>[ \t]*)(?P<t>dataframe\[[^\n]+\])\.fillna\(\s*"
    r"method\s*=\s*['\"](?P<m>ffill|pad|bfill|backfill)['\"]\s*,\s*"
    r"inplace\s*=\s*True\s*\)[ \t]*$", re.M)


def _split_args(s):
    """Split a comma-separated argument list at top level only."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [a.strip() for a in out if a.strip()]


def pre_pandas_renames(src, path):
    """`fillna(method=...)` and `sum(level=...)` were removed from pandas, and
    pandas' own deprecation notes name the exact replacements: `ffill()`/`bfill()`
    and `groupby(level=n).sum()`. These are renames of the same operation, not
    reconstructions of it, which is what makes them provable.

    Refused deliberately: `replace(to_replace=0, method='ffill')`. There is no
    renamed equivalent - reproducing it needs `mask(...).ffill()`, which is a
    reconstruction of intent rather than a rename, and reconstructions are
    where a patch stops being neutral.
    """
    hits = []
    for m in RX_FILLNA.finditer(src):
        args = _split_args(m.group("args"))
        meth = [a for a in args if RX_METHOD_ARG.search(a)]
        if not meth:
            continue
        if any(a.startswith("value") for a in args) or (
                args and "=" not in args[0] and not RX_METHOD_ARG.search(args[0])):
            continue          # a fill value is also given - not a plain rename
        hits.append("fillna(method=)")
    if RX_SUM_LEVEL.search(src):
        hits.append("agg(level=)")
    if RX_CHAINED_FILL_INPLACE.search(src):
        hits.append("chained fillna(method=, inplace=True)")
    if not hits:
        return False, "no removed-pandas-keyword call present"
    return True, "pandas documents exact replacements for: " + ", ".join(sorted(set(hits)))


def apply_pandas_renames(src):
    def chained_repl(m):
        method = FILL_MAP[m.group("m")]
        return "%s%s = %s.%s()" % (
            m.group("i"), m.group("t"), m.group("t"), method)

    src = RX_CHAINED_FILL_INPLACE.sub(chained_repl, src)

    def fill_repl(m):
        args = _split_args(m.group("args"))
        meth, rest = None, []
        for a in args:
            mm = RX_METHOD_ARG.search(a)
            if mm and meth is None:
                meth = FILL_MAP[mm.group("m")]
            else:
                rest.append(a)
        if meth is None:
            return m.group(0)
        if any(a.startswith("value") for a in rest):
            return m.group(0)
        return ".%s(%s)" % (meth, ", ".join(rest))

    out = RX_FILLNA.sub(fill_repl, src)
    out = RX_SUM_LEVEL.sub(
        lambda m: ".groupby(level=%s).%s()" % (m.group("lv"), m.group("fn")), out)
    return out


# ── rule 6: re-enable a commented-out feature source its consumers still read ─

# `[ \t]*` rather than `\s*`: the latter matches across newlines, so it ate the
# blank lines around the block and the replacement came out with stray gaps
# inside the for-body. Valid Python, but generated code that looks careless
# invites doubt about whether it was checked.
RX_COMMENTED_MML = re.compile(
    r"^(?P<i>[ \t]*)#[ \t]*(?P<a>murrey_math_levels[ \t]*=[ \t]*calculate_murrey_math_levels\(dataframe\))[ \t]*\n"
    r"[ \t]*#[ \t]*(?P<b>for level, value in murrey_math_levels\.items\(\):)[ \t]*\n"
    r"(?P<j>[ \t]*)#(?P<k>[ \t]*)(?P<c>dataframe\[level\] = value)[ \t]*$",
    re.M)
RX_MML_CONSUMER = re.compile(r"dataframe\[\"(\[[-+]?\d/8\]P)\"\]")
RX_MML_KEY = re.compile(r'"(\[[-+]?\d/8\]P)"\s*:')


def pre_restore_feature_source(src, path):
    """Re-enable a computation the author commented out while leaving every line
    that reads its result.

    THIS RULE IS STRONGER THAN THE OTHERS AND MUST BE READ AS SUCH. The rest of
    Phase 3 renames APIs and touches values nothing reads. This one restores a
    computation, so the strategy afterwards produces feature columns it did not
    produce before. It is only in the pipeline because the operator asked for it
    explicitly, to establish whether the strategy works at all; results from it
    are not comparable with the rest and must be reported apart.

    What can still be checked, and is:

      1. the commented block has the exact shape "compute, then assign each
         returned level into the dataframe" - not some other disabled code;
      2. the function it calls is defined in the same file;
      3. EVERY column the surviving consumers read is a key that function
         returns. A partial restoration would leave a different KeyError one
         line further down, and that is the failure mode worth excluding.
    """
    m = RX_COMMENTED_MML.search(src)
    if not m:
        return False, "no commented-out murrey-math feature source in the expected shape"
    if "def calculate_murrey_math_levels" not in src:
        return False, "the function the block calls is not defined in this file"
    consumed = set(RX_MML_CONSUMER.findall(src))
    produced = set(RX_MML_KEY.findall(src))
    if not consumed:
        return False, "nothing reads those columns - restoring would change behaviour for no reason"
    missing = consumed - produced
    if missing:
        return False, ("restoration would be incomplete: %d consumed column(s) the "
                       "function never returns, e.g. %s"
                       % (len(missing), sorted(missing)[:3]))
    return True, ("re-enables the source of %d columns that %d consumer lines read; "
                  "every consumed key is produced by the function"
                  % (len(produced & consumed), len(consumed)))


def apply_restore_feature_source(src):
    def repl(m):
        i = m.group("i")
        body = m.group("k") or "    "     # keep the author's own body indent
        return "%s%s\n%s%s\n%s%s%s" % (i, m.group("a"), i, m.group("b"),
                                       i, body, m.group("c"))
    return RX_COMMENTED_MML.sub(repl, src)


# ── rule 6b: honor the author's own "disable for backtest" comment ──────────

RX_ALEX_DYN_OPT = re.compile(
    r"^(?P<indent>[ \t]*)self\.enable_dynamic_optimization[ \t]*=[ \t]*True"
    r"[ \t]*(?P<comment>#.*deaktivieren.*Backtest.*)$", re.M)

# The flag's own name and its own log line ("Dynamic optimization:
# {'ENABLED' if self.enable_dynamic_optimization else 'DISABLED'}") declare it
# a single master switch for the whole feature, not just the first read of it.
# Two of the feature's own entry points never check it at all:
#   - maybe_optimize_coin(): reached, unguarded, from a "retrain every 20
#     trades" trigger and a 24h periodic trigger - both real during a backtest;
#   - daily_optimization_check(): called from populate_indicators() the very
#     first time it runs for a pair, because `self.last_daily_check` starts at
#     0, so `time.time() - 0 > 86400` is true immediately.
# Silencing the startup call alone leaves the same Optuna search reachable
# through either path, which is why the file still would not finish under the
# flag's own stated meaning. Gating these exact, unique def lines completes
# the single switch the author already named, rather than adding a new one.
RX_ALEX_MAYBE_OPT_DEF = re.compile(
    r"^(?P<indent>[ \t]*)def maybe_optimize_coin\(self, pair: str, "
    r"force_startup: bool = False\):[ \t]*\n", re.M)
RX_ALEX_DAILY_CHECK_DEF = re.compile(
    r"^(?P<indent>[ \t]*)def daily_optimization_check\(self\):[ \t]*\n", re.M)


def pre_alex_dynamic_opt(src, path):
    """A strategy flag the author's own inline comment says to flip for
    backtesting, but which is hardcoded True regardless of run mode, and
    which two of the feature's own entry points never check at all.

    This is not a reconstruction: the file itself states the intended
    behaviour ("deaktivieren fuer Backtest" - disable for backtest) right next
    to the line that fails to do it, and states the feature is a single
    on/off concept via its own "ENABLED"/"DISABLED" log line. The patch
    restores exactly that stated intent and changes nothing else. It is
    scoped to fire only where all of the following hold, so it cannot
    silently apply to a differently-shaped file:

      1. the exact assignment, with the author's own qualifying comment,
         is present and unique;
      2. `super().__init__(config)` already ran earlier in the same method,
         so `self.config` exists at the point of the assignment;
      3. the flag is read at least once elsewhere in the file, so gating it
         has an observable effect confined to what the author already named;
      4. `maybe_optimize_coin` and `daily_optimization_check` are each
         defined exactly once, with this exact signature, so the guard can
         only land in the one function body it was verified against.
    """
    matches = list(RX_ALEX_DYN_OPT.finditer(src))
    if not matches:
        return False, "no 'enable_dynamic_optimization = True' with the author's own backtest-disable comment"
    if len(matches) > 1:
        return False, "more than one matching assignment - not unambiguous"
    init_idx = src.find("super().__init__(config)")
    if init_idx == -1 or init_idx > matches[0].start():
        return False, "super().__init__(config) does not precede the assignment - self.config not proven available"
    reads = len(re.findall(r"self\.enable_dynamic_optimization\b(?!\s*=[^=])", src))
    if reads <= 1:  # the assignment itself is one occurrence
        return False, "flag is never read elsewhere - gating it would have no effect"
    maybe_defs = list(RX_ALEX_MAYBE_OPT_DEF.finditer(src))
    daily_defs = list(RX_ALEX_DAILY_CHECK_DEF.finditer(src))
    if len(maybe_defs) != 1:
        return False, "maybe_optimize_coin not defined exactly once with the expected signature"
    if len(daily_defs) != 1:
        return False, "daily_optimization_check not defined exactly once with the expected signature"
    return True, ("author's own comment and log line state the intended "
                  "behaviour (a single switch, off during backtest); gates "
                  "the hardcoded True and the two entry points that bypass "
                  "the flag entirely, instead of inventing new logic")


def apply_alex_dynamic_opt(src):
    def repl_assign(m):
        return ("%sself.enable_dynamic_optimization = ("
                "getattr(self.config.get('runmode'), 'value', '') "
                "not in ('backtest', 'hyperopt'))  %s"
                % (m.group("indent"), m.group("comment").lstrip("#").strip()
                   and "# " + m.group("comment").lstrip("#").strip()))
    out = RX_ALEX_DYN_OPT.sub(repl_assign, src)

    def repl_guard(m):
        body_indent = m.group("indent") + "    "
        return (m.group(0) + body_indent + "if not self.enable_dynamic_optimization:\n"
                + body_indent + "    return\n")
    out = RX_ALEX_MAYBE_OPT_DEF.sub(repl_guard, out)
    out = RX_ALEX_DAILY_CHECK_DEF.sub(repl_guard, out)
    return out


# ── rule 6c: startup_candle_count too low for the file's own 1h guard ───────

RX_ALEX_STARTUP = re.compile(
    r"^(?P<indent>[ \t]*)startup_candle_count[ \t]*:[ \t]*int[ \t]*=[ \t]*10[ \t]*$",
    re.M)
RX_ALEX_1H_GUARD = re.compile(
    r"len\(informative_1h\)[ \t]*>[ \t]*50")

# 220 fifteen-minute candles is the smallest round number that clears the
# file's own "len(informative_1h) > 50" guard with a margin: freqtrade loads
# informative-timeframe history to cover the same wall-clock span as
# startup_candle_count on the base (15m) timeframe, so 1h coverage scales by
# the timeframe ratio (60/15 = 4). 220/4 = 55 1h candles, five clear of the
# guard's own ">50" - enough that a partial trailing 1h candle at the window
# edge cannot drop it back to 50 or below. The previous value of 10 cleared
# neither this guard nor the ema200_1h computed two lines below it once the
# guard passes.
ALEX_STARTUP_VALUE = 220


def pre_alex_startup_candles(src, path):
    """`startup_candle_count = 10` is inconsistent with the file's own 1h
    merge guard (`len(informative_1h) > 50`, populate_indicators) and the
    ema200_1h it computes once that guard passes - both need far more
    warm-up than 10 candles can supply. In a short analysis window (the
    lookahead-analysis "cut" slice near a candidate trade, or the start of
    any backtest) the guard fails silently, merge_informative_pair is never
    called, and the six merged 1h/OHLCV columns are present in a longer run
    but absent in a shorter one - the exact column-set mismatch that crashes
    freqtrade's own lookahead-analysis
    ("Can only compare identically-labeled ... DataFrame objects"), and
    silently changes the strategy's own decision inputs near the start of
    any run. This does not invent new behaviour: it makes the declared
    warm-up honor a threshold and a computation the author's own file
    already require, restoring what len(informative_1h) > 50 assumed was
    guaranteed. It cannot be called strictly equivalent (any run's leading
    candles that used to fall short of the guard were seeing dummy 1h
    columns and now see merged real ones), so it is applied only on the
    repair owner's explicit direction, not inferred silently like a pure
    bugfix would be.

    Scoped to fire only where all of the following hold:
      1. the exact declaration is present and unique;
      2. the file's own `len(informative_1h) > 50` guard is present, so the
         fix is proven to target the guard it was diagnosed against, not a
         differently-shaped file that happens to share the same default.
    """
    matches = list(RX_ALEX_STARTUP.finditer(src))
    if not matches:
        return False, "no 'startup_candle_count: int = 10' declaration"
    if len(matches) > 1:
        return False, "more than one matching declaration - not unambiguous"
    if not RX_ALEX_1H_GUARD.search(src):
        return False, "file's own 'len(informative_1h) > 50' guard not found - not the diagnosed shape"
    return True, ("startup_candle_count raised to %d so the file's own "
                  "len(informative_1h) > 50 guard and ema200_1h computation "
                  "have the warm-up they require in every analysis window, "
                  "not just long ones" % ALEX_STARTUP_VALUE)


def apply_alex_startup_candles(src):
    def repl(m):
        return "%sstartup_candle_count: int = %d" % (m.group("indent"), ALEX_STARTUP_VALUE)
    return RX_ALEX_STARTUP.sub(repl, src)


# ── rule 7: legacy int literal into a now bool-typed column ─────────────────

# freqtrade guarantees these five are declared bool without needing textual
# proof from the file itself - the standard pre-2021 idiom
# `dataframe.loc[conditions, 'buy'] = 1` is safe on the framework's own word.
SIGNAL_COLUMNS = {"buy", "sell", "enter_long", "exit_long",
                  "enter_short", "exit_short"}


def _column_name(target):
    """The column a `Subscript` assignment target names, or None.

    Handles both `df['col'] = ...` and the `.loc[cond, 'col'] = ...` shape,
    where the slice is a tuple and the column is its last element. A
    list/tuple of several columns on one side (`.loc[cond, ['a', 'b']] =
    (1, 2)`) returns None - not this shape, deliberately left alone rather
    than guessed at positionally.
    """
    if not isinstance(target, ast.Subscript):
        return None
    key = target.slice
    if isinstance(key, ast.Tuple) and key.elts:
        key = key.elts[-1]
    if isinstance(key, ast.Constant) and isinstance(key.value, str):
        return key.value
    return None


def _bool_typed_columns(tree):
    """Column names the file itself assigns a bare `True`/`False` literal to
    at least once - the author's own declaration that the column is a flag,
    not merely a name that looks like one. Established once per file, not
    per assignment, so a column set to `False` for initialisation and later
    to `1` for a specific candle is still recognised as the same column.
    """
    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not (isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, bool)):
            continue
        for target in node.targets:
            name = _column_name(target)
            if name:
                found.add(name)
    return found


def _is_int01(node):
    return (isinstance(node, ast.Constant)
            and isinstance(node.value, int)
            and not isinstance(node.value, bool)
            and node.value in (0, 1))


def _int_literal_assignments(tree, bool_columns):
    """Every literal-0/1 AST node that a column in `bool_columns` receives -
    either a freqtrade signal column (always eligible) or one this same file
    proved bool-typed itself via `_bool_typed_columns`. Two assignment
    shapes, both common in this corpus's pre-2021 strategies:

    * single column: `df['col'] = 1`, `df.loc[cond, 'col'] = 1` - the
      literal is the whole right-hand side.
    * several columns at once: `df.loc[cond, ['col', 'tag']] = (1, 'text')` -
      only the position paired with a bool-proven column name is a hit;
      the row's other elements (an entry tag, say) are untouched, and a
      length mismatch between the column list and the value tuple is
      skipped rather than guessed at.
    """
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Subscript):
                continue
            key = target.slice
            if isinstance(key, ast.Tuple) and key.elts:
                key = key.elts[-1]
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                if key.value in bool_columns and _is_int01(node.value):
                    hits.append(node.value)
            elif (isinstance(key, (ast.List, ast.Tuple))
                  and isinstance(node.value, (ast.List, ast.Tuple))
                  and len(key.elts) == len(node.value.elts)):
                for col, val in zip(key.elts, node.value.elts):
                    if (isinstance(col, ast.Constant)
                            and isinstance(col.value, str)
                            and col.value in bool_columns
                            and _is_int01(val)):
                        hits.append(val)
    return hits


def pre_signal_int_literal(src, path):
    """A strategy written before pandas enforced a column's declared dtype
    assigns the literal 1/0 it always meant as a flag - into freqtrade's own
    signal columns, or into a column the file's own code elsewhere assigns
    `True`/`False` to, which is the author stating the same thing about
    their own column. `True`/`False` are the exact same value as `1`/`0`
    under Python's own `bool <: int` (`1 == True` unconditionally), so which
    literal spells "flagged" cannot change which candles freqtrade decides
    to enter or exit on, or what a custom flag column reads as downstream.
    Scoped to columns proven bool one way or the other, by the AST, not by
    file: an integer written anywhere else, in a column with no bool
    declaration on record, is left untouched.
    """
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            tree = ast.parse(src)
    except SyntaxError as e:
        return False, "cannot parse file: %s" % str(e)[:60]
    bool_columns = SIGNAL_COLUMNS | _bool_typed_columns(tree)
    hits = _int_literal_assignments(tree, bool_columns)
    if not hits:
        return False, "no bare 0/1 literal assigned to a column proven bool-typed"
    return True, ("%d assignment(s) of a literal 0/1 into a column this file "
                  "itself declares bool (signal column, or assigned True/"
                  "False elsewhere in the same file) - the same value under "
                  "a different spelling" % len(hits))


def apply_signal_int_literal(src):
    with warnings.catch_warnings():
        # Corpus escapes are often invalid; the source hash is the identity.
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(src)
    bool_columns = SIGNAL_COLUMNS | _bool_typed_columns(tree)
    hits = _int_literal_assignments(tree, bool_columns)
    lines = src.splitlines(keepends=True)
    # Highest position first so an earlier replacement cannot shift the
    # recorded line/column of a node still to be applied.
    for node in sorted(hits, key=lambda n: (n.lineno, n.col_offset),
                       reverse=True):
        replacement = "True" if node.value == 1 else "False"
        line = lines[node.lineno - 1]
        lines[node.lineno - 1] = (
            line[:node.col_offset] + replacement + line[node.end_col_offset:])
    return "".join(lines)


RULES = [
    ("restore_commented_feature_source", pre_restore_feature_source,
     apply_restore_feature_source),
    ("pandas_removed_keywords", pre_pandas_renames, apply_pandas_renames),
    ("dead_np_where_dtype", pre_pmx, apply_pmx),
    ("param_missing_space", pre_space, apply_space),
    ("rolling_any_masked", pre_rolling_any_masked, apply_rolling_any_masked),
    ("rolling_any_detect_only", pre_rolling_any, None),
    ("vin_explicit_rolling_spearman", pre_vin_spearman, apply_vin_spearman),
    ("alex_dynamic_optimization_gate", pre_alex_dynamic_opt, apply_alex_dynamic_opt),
    ("alex_startup_candle_count", pre_alex_startup_candles, apply_alex_startup_candles),
    ("legacy_signal_int_literal", pre_signal_int_literal,
     apply_signal_int_literal),
]


def equivalence_status(rule_names):
    """Return the strongest behavior classification among applied rules."""
    if "restore_commented_feature_source" in rule_names:
        return "behavior_changed"
    if "alex_dynamic_optimization_gate" in rule_names:
        return "behavior_changed"
    if "alex_startup_candle_count" in rule_names:
        return "behavior_changed"
    if "rolling_any_masked" in rule_names:
        return "output_equivalent"
    if "vin_explicit_rolling_spearman" in rule_names:
        return "intent_preserving_unverified"
    return "strict_equivalent"


# ───────────────────────────────── driver ──────────────────────────────────

def targets_from_ledger(ledger):
    rows = list(csv.DictReader(io.open(ledger, encoding="utf-8")))
    return [(r["strategy"], r["repo"], r["file"]) for r in rows]


def targets_from_profiles(names):
    """Resolve explicit overlay targets without a temporary ledger file.

    Reads `original_file`, not `canonical_file`. Once a strategy already has
    an overlay selected as canonical, `canonical_file` points back INTO
    `repair/patched/` - patching from there would read the previous rule's
    own output as source, so a rule whose precondition matches the untouched
    original (e.g. a literal the overlay already rewrote) silently stops
    firing on a second run. `original_file` is always the untouched repos/
    source, which is what every rule's precondition is proven against.
    """
    profiles = os.path.join(ROOT, "evidence", "EXECUTION_PROFILES.csv")
    rows = {row["strategy_id"]: row
            for row in csv.DictReader(io.open(profiles, encoding="utf-8-sig"))}
    out = []
    for name in names:
        row = rows.get(name)
        if not row:
            raise ValueError("strategy not present in EXECUTION_PROFILES.csv: %s" % name)
        out.append((name, row["repo"], row["original_file"]))
    return out


def selftest():
    """Validate the narrow matcher and Spearman result without writing files."""
    vin = os.path.join(ROOT, "repos", "PeetCrypto_freqtrade-stuff", "vin.py")
    source = io.open(vin, encoding="utf-8").read()
    ok, _why = pre_vin_spearman(source, vin)
    assert ok
    patched = apply_vin_spearman(source)
    assert patched.count("rolling_spearman_corr(") == 4  # helper plus 3 calls
    namespace = {}
    exec(VIN_SPEARMAN_HELPER, namespace)
    import pandas as pd
    left = pd.Series([1.0, 2.0, 3.0, 4.0])
    right = pd.Series([4.0, 3.0, 2.0, 1.0])
    result = namespace["rolling_spearman_corr"](left, right, window=3, min_periods=3)
    assert result.iloc[-1] == -1.0
    print("patch_class2 selftest: PASS (ViN explicit rolling Spearman overlay)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger", nargs="?", default=os.path.join(
        AUD, "old", "predecessor_audit", "LEDGER.csv"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--strategy", action="append", dest="strategies",
                    help="explicit strategy from EXECUTION_PROFILES.csv; repeatable")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return

    # The report is read by evidence/execution_profiles.py to decide which
    # strategies get their patched overlay selected as canonical, and this
    # driver has always been run against whatever ledger the moment called
    # for - the default, or a one-off custom one for a single family like
    # dtype_drift. A plain overwrite here means the SECOND kind erases every
    # strategy the FIRST kind ever patched: a dtype_drift-only ledger run on
    # 2026-09-09 silently dropped 58 already-patched strategies (`BBRSIS`
    # among them) from this file, and evidence/execution_profiles.py just as
    # silently stopped selecting their overlays - the files stayed on disk
    # under repair/patched/, only the record of them existed nowhere this
    # driver, or anything downstream of it, still read. Carrying forward
    # every strategy this run does not itself touch is what makes a custom
    # ledger additive instead of destructive.
    report_path = os.path.join(ROOT, "repair", "patch_class2_report.json")
    previous_by_strategy = {}
    if os.path.exists(report_path):
        for entry in json.loads(io.open(report_path, encoding="utf-8").read()):
            previous_by_strategy.setdefault(entry["strategy"], []).append(entry)

    report, patched = [], 0
    seen_this_run = set()
    targets = (targets_from_profiles(args.strategies) if args.strategies
               else targets_from_ledger(args.ledger))
    for name, repo, rel in targets:
        seen_this_run.add(name)
        path = os.path.join(AUD, rel)
        if not os.path.exists(path):
            continue
        try:
            src = io.open(path, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        out, applied = src, []
        for rule, precond, apply_fn in RULES:
            ok, why = precond(out, path)
            if not ok:
                if "NOT patched" in why:
                    report.append({"strategy": name, "rule": rule,
                                   "action": "refused", "reason": why})
                continue
            if apply_fn is None:
                continue
            new = apply_fn(out)
            if new == out:
                report.append({"strategy": name, "rule": rule,
                               "action": "no-op", "reason": "precondition held but nothing changed"})
                continue
            out, _ = new, applied.append({"rule": rule, "reason": why})
        if not applied:
            continue
        patched += 1
        rule_names = [a["rule"] for a in applied]
        report.append({"strategy": name, "rule": rule_names,
                       "repair_rules": rule_names,
                       "action": "patched", "reason": [a["reason"] for a in applied],
                       "file": rel, "population": "repaired",
                       "repair_class": "class2", "source_tree": "class2-overlay",
                       "equivalence_status": equivalence_status(rule_names)})
        if args.dry_run:
            continue
        dst = os.path.join(OVERLAY, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        io.open(dst, "w", encoding="utf-8", newline="").write(out)
        os.makedirs(DIFFS, exist_ok=True)
        diff = difflib.unified_diff(src.splitlines(True), out.splitlines(True),
                                    fromfile="original/" + rel, tofile="patched/" + rel)
        io.open(os.path.join(DIFFS, name.replace("/", "_") + ".diff"),
                "w", encoding="utf-8").write("".join(diff))

    carried = 0
    for strategy, entries in previous_by_strategy.items():
        if strategy in seen_this_run:
            continue
        report.extend(entries)
        carried += 1

    if not args.dry_run:
        io.open(report_path, "w", encoding="utf-8").write(
            json.dumps(report, ensure_ascii=False, indent=1))
    acted = [r for r in report if r["action"] == "patched"]
    refused = [r for r in report if r["action"] == "refused"]
    print("patched %d strategies | refused %d | %d carried forward from "
          "earlier ledgers | %s"
          % (len(acted), len(refused), carried,
             "DRY RUN" if args.dry_run else "written to " + OVERLAY))
    for r in acted[:15]:
        print("  + %-34s %s" % (r["strategy"][:34], ",".join(r["rule"])))
    if refused:
        print("  refused (reported, not patched):")
        for r in refused[:8]:
            print("  - %-34s %s" % (r["strategy"][:34], r["reason"][:70]))


if __name__ == "__main__":
    main()
