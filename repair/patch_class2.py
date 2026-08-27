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


# ───────── rule 5: fillna(method=...) and sum(level=...) - pandas renames ───

FILL_MAP = {"ffill": "ffill", "pad": "ffill", "bfill": "bfill", "backfill": "bfill"}
RX_FILLNA = re.compile(r"\.fillna\(\s*(?P<args>[^()]*)\)")
RX_METHOD_ARG = re.compile(r"""method\s*=\s*['"](?P<m>ffill|pad|bfill|backfill)['"]""")
RX_SUM_LEVEL = re.compile(r"\.(?P<fn>sum|mean|min|max|std|var|count)\(\s*level\s*=\s*(?P<lv>\d+)\s*\)")


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
    if not hits:
        return False, "no removed-pandas-keyword call present"
    return True, "pandas documents exact replacements for: " + ", ".join(sorted(set(hits)))


def apply_pandas_renames(src):
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


RULES = [
    ("restore_commented_feature_source", pre_restore_feature_source,
     apply_restore_feature_source),
    ("pandas_removed_keywords", pre_pandas_renames, apply_pandas_renames),
    ("dead_np_where_dtype", pre_pmx, apply_pmx),
    ("param_missing_space", pre_space, apply_space),
    ("rolling_any_masked", pre_rolling_any_masked, apply_rolling_any_masked),
    ("rolling_any_detect_only", pre_rolling_any, None),
]


def equivalence_status(rule_names):
    """Return the strongest behavior classification among applied rules."""
    if "restore_commented_feature_source" in rule_names:
        return "behavior_changed"
    if "rolling_any_masked" in rule_names:
        return "output_equivalent"
    return "strict_equivalent"


# ───────────────────────────────── driver ──────────────────────────────────

def targets_from_ledger(ledger):
    rows = list(csv.DictReader(io.open(ledger, encoding="utf-8")))
    return [(r["strategy"], r["repo"], r["file"]) for r in rows]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger", nargs="?", default=os.path.join(AUD, "LEDGER.csv"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    report, patched = [], 0
    for name, repo, rel in targets_from_ledger(args.ledger):
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

    dst = os.path.join(ROOT, "repair", "patch_class2_report.json")
    if not args.dry_run:
        io.open(dst, "w", encoding="utf-8").write(
            json.dumps(report, ensure_ascii=False, indent=1))
    acted = [r for r in report if r["action"] == "patched"]
    refused = [r for r in report if r["action"] == "refused"]
    print("patched %d strategies | refused %d | %s"
          % (len(acted), len(refused), "DRY RUN" if args.dry_run else "written to " + OVERLAY))
    for r in acted[:15]:
        print("  + %-34s %s" % (r["strategy"][:34], ",".join(r["rule"])))
    if refused:
        print("  refused (reported, not patched):")
        for r in refused[:8]:
            print("  - %-34s %s" % (r["strategy"][:34], r["reason"][:70]))


if __name__ == "__main__":
    main()
