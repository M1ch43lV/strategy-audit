# -*- coding: utf-8 -*-
"""strategy_ideas - what each strategy does, in one sentence, from its own code.

WHY A SEPARATE STEP FROM THE TAXONOMY. `cluster/` labels a strategy on five
mechanical axes (direction, trading logic, speed, complexity, regime hypothesis)
and `evidence/strategy_classification.py` reads a signal family off the class
block. Both are derived, both say *what kind* of thing a strategy is, and
neither says what its idea is: the sentence a reader needs before deciding
whether to spend a benchmark on it. That sentence cannot be produced by a rule
table - it has to be read out of the code and interpreted - so this tool splits
the job in two and keeps the halves apart:

1. `--bundle` extracts the facts an interpretation has to rest on - the
   indicators, the entry and exit conditions, the settings, the author's own
   docstring - from the canonical file of each strategy, and writes
   `evidence/STRATEGY_IDEAS_INPUT.json`. It also carries what the existing
   stores already know (classification, cluster labels) instead of re-deriving
   it.
2. An LLM - an agent session, not this program - reads that bundle and writes
   `evidence/STRATEGY_IDEAS.json`: one entry per family, each idea bound to the
   one revision it was read from (`read_from`, with that revision's
   `source_sha256`) and to the facts it rests on. The family's *other* rows are
   derived from the corpus by stem instead of being listed, because a family
   with 39 revisions would otherwise need 39 hand-written hash entries that
   repeat what the corpus already records. This program never writes that
   store; `--render` only lays it out, and `--check` fails when the corpus has
   moved on from the revision an idea describes. A description that silently
   outlives its source is the failure mode this artifact would otherwise have.

WHY THE HASH IS THE WHOLE POINT. A strategy file in this corpus is identified by
its bytes, and the corpus changes underneath it: the wave of 2026-09-23 moved 45
rows to a different revision of the same name. Prose cannot be re-measured, so
it must at least be *tied*: every idea names the file and hash it was written
from, the page shows both, and `--check` reports an idea whose source no longer
matches. Interpreting the new revision is then a deliberate act rather than a
quiet drift.

WHAT IT IS NOT. Not a measurement, not evidence, not an admission argument -
`PIPELINE.md`'s stages decide those, and this file changes no stage. The page
exists so a reader can see what the corpus contains before opening any code.
"""
from __future__ import annotations

import argparse
import ast
import html
import io
import json
import os
import re
import sys
import time
import warnings

_ROOT = (os.environ.get("AUDIT_ROOT") or
         os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROFILES = os.path.join(_ROOT, "evidence", "EXECUTION_PROFILES.csv")
CLUSTERS = os.path.join(_ROOT, "cluster", "clusters.json")
CLASSIFICATION = os.path.join(_ROOT, "evidence", "STRATEGY_CLASSIFICATION.json")
BUNDLE = os.path.join(_ROOT, "evidence", "STRATEGY_IDEAS_INPUT.json")
IDEAS = os.path.join(_ROOT, "evidence", "STRATEGY_IDEAS.json")
PAGE = os.path.join(_ROOT, "strategy_ideas.html")

# Caps keep the bundle readable for a model instead of dumping a 200 KB file:
# what matters is which indicators are used, how entry and exit are decided, and
# what the author wrote down. Nothing here is a claim about behaviour.
MAX_ITEMS = 40
MAX_EXPR = 240
MAX_DOC = 700

INTERESTING_SETTINGS = (
    "timeframe", "ticker_interval", "stoploss", "minimal_roi", "trailing_stop",
    "trailing_stop_positive", "trailing_stop_positive_offset", "can_short",
    "startup_candle_count", "use_custom_stoploss", "use_sell_signal",
    "position_adjustment_enable", "max_open_trades", "leverage",
    "process_only_new_candles", "ignore_buying_expired_candle_after",
)
TARGET_FUNCS = ("populate_indicators", "populate_entry_trend",
                "populate_exit_trend", "populate_buy_trend",
                "populate_sell_trend", "custom_stoploss", "confirm_trade_entry",
                "adjust_trade_position", "informative_pairs")


def _read(path):
    return io.open(path, encoding="utf-8", errors="replace").read()


def _parse(source):
    with warnings.catch_warnings():
        # Third-party corpus source; invalid escape sequences are expected and
        # the source hash is the identity, so it is never repaired.
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(source)


def _expr(node):
    try:
        text = ast.unparse(node)
    except Exception:
        return "<unparseable>"
    text = " ".join(text.split())
    return text[:MAX_EXPR] + (" ..." if len(text) > MAX_EXPR else "")


def _call_name(node):
    """`qtpylib.bollinger_bands` and `ta.RSI` as written, else ''."""
    func = node.func
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        return "%s.%s" % (func.value.id, func.attr)
    if isinstance(func, ast.Name):
        return func.id
    return ""


def indicators_in(trees) -> list[str]:
    """Every indicator call in the file, deduplicated, calls kept with arguments.

    Kept as written (`ta.RSI(dataframe, timeperiod=14)`) because the parameters
    are part of the idea in this corpus - `RSI(7)` against `RSI(14)` is a
    different claim about the market, not a detail.
    """
    seen, out = set(), []
    for tree in trees:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = _call_name(node)
            if not name or name.split(".")[0] in ("super", "self"):
                continue
            if name.split(".")[0] not in ("ta", "qtpylib", "np", "pd", "talib",
                                          "numpy", "pandas"):
                continue
            text = _expr(node)
            if text not in seen:
                seen.add(text)
                out.append(text)
    return out[:MAX_ITEMS]


def _column_name(node):
    """`'enter_long'` as `enter_long`, anything else as written."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return _expr(node)


def signals_in(tree, names) -> dict:
    """The assignment of `enter_long`/`exit_long` and friends, as written.

    Both styles exist in the corpus: the modern
    `dataframe.loc[(cond), 'enter_long'] = 1` and the older
    `dataframe.loc[cond, 'buy'] = 1` inside `populate_buy_trend`. The condition
    is the strategy's claim and the `= 1` is bookkeeping, so the output is
    `enter_long = (cond)` - column first, condition second.
    """
    found = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in names:
            continue
        conditions = []
        for sub in ast.walk(node):
            if isinstance(sub, ast.If):
                conditions.append("if %s:" % _expr(sub.test))
                continue
            if not (isinstance(sub, ast.Assign) and len(sub.targets) == 1
                    and isinstance(sub.value, ast.Constant)
                    and sub.value.value in (0, 1)):
                continue
            target = sub.targets[0]
            if not isinstance(target, ast.Subscript):
                continue
            slice_ = target.slice
            column = condition = ""
            if isinstance(slice_, ast.Tuple) and slice_.elts:
                condition = _expr(slice_.elts[0])
                column = _column_name(slice_.elts[-1])
            else:
                column = _column_name(slice_)
            if not any(word in column for word in ("enter", "exit", "buy", "sell",
                                                   "long", "short")):
                continue
            conditions.append("%s = %s" % (column, condition or sub.value.value))
        found[node.name] = conditions[:MAX_ITEMS]
    return found


def settings_of(tree) -> dict:
    out = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        for statement in node.body:
            target = None
            value = None
            if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                target, value = statement.targets[0], statement.value
            elif isinstance(statement, ast.AnnAssign) and statement.value is not None:
                target, value = statement.target, statement.value
            if isinstance(target, ast.Name) and target.id in INTERESTING_SETTINGS:
                out.setdefault(target.id, _expr(value))
    return out


def docstring_of(tree) -> str:
    text = ast.get_docstring(tree) or ""
    if not text:
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                text = ast.get_docstring(node) or ""
                if text:
                    break
    return " ".join(text.split())[:MAX_DOC]


def functions_of(tree) -> list[str]:
    """The methods the class defines, with their size in lines.

    A reader's first question after "what does it buy on" is "what does it do
    that the framework would not" - a DCA hook, a custom stop, a confirmation
    gate - and that question is answered by which hooks exist. Sizes are line
    spans of the definition, a fact about the file.
    """
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.append("%s (%d lines)" % (
                        item.name,
                        (item.end_lineno or item.lineno) - item.lineno + 1))
    return out


_VERSION = re.compile(r"(?i)(?:v|ver|version)(\d+(?:[._]\d+)*)$")
_DATE = re.compile(r"(20\d{2})[-_]?(0[1-9]|1[0-2])[-_]?(0[1-9]|[12]\d|3[01])")
_EPOCH = re.compile(r"(?:^|[^0-9])(1[0-9]{9})(?:[^0-9]|$)")


def version_key(strategy_id) -> str:
    """The version the *name* claims, as written - `V31`, `v12_4`, `2023-09-15`.

    A fact about the id, not a decision about order, and deliberately not a sort
    key. The marker has to sit at the end of the name, which is why `E0V1E`
    reports none although `V1` appears in the middle of it, and why the marker
    is returned verbatim instead of being reformatted - `V7_2021` is what the
    author wrote and this function does not get to decide whether the `2021` is
    a minor version or a year. GeneTrader's generator writes a Unix timestamp
    into the class name, so that counts as a marker too. A family without
    markers is a family whose order the name cannot tell; the interpretation has
    to say what it used instead.
    """
    dates = _DATE.findall(strategy_id)
    if dates:
        year, month, day = dates[-1]
        return "%s-%s-%s" % (year, month, day)
    epoch = _EPOCH.search(strategy_id)
    if epoch:
        return time.strftime("%Y-%m-%d", time.gmtime(int(epoch.group(1))))
    marker = _VERSION.search(strategy_id)
    return marker.group(0) if marker else ""


def family_stem(strategy_id) -> str:
    """The name without its version marker - the mechanical family guess.

    It is a guess on purpose: `ZaratustraV10` and `ZaratustraDCA2_06` share a
    stem, `SlopeV8` and `SlopeIsDope` do not, and only the interpretation may
    decide whether that matters. The ideas store may name a different family;
    this function only has to be deterministic and visible.
    """
    stem = re.sub(r"[_\-]?(?i:v|ver|version)?\d+(?:[._]\d+)*$", "", strategy_id)
    stem = re.sub(r"[_\-]?(?i:dca)\d*(?:[._]\d+)*$", "", stem)
    return stem or strategy_id


def bundle_rows(strategy_ids, profiles, clusters, classification) -> list[dict]:
    rows = []
    for strategy_id in strategy_ids:
        profile = profiles.get(strategy_id)
        if not profile:
            rows.append({"strategy_id": strategy_id, "error": "not in the corpus"})
            continue
        path = os.path.join(_ROOT, profile["canonical_file"].replace("/", os.sep))
        try:
            source = _read(path)
            tree = _parse(source)
        except (OSError, SyntaxError) as exc:
            rows.append({"strategy_id": strategy_id, "error": "unreadable: %s" % exc})
            continue
        import hashlib
        row = {
            "strategy_id": strategy_id,
            "family_stem": family_stem(strategy_id),
            "version_key": version_key(strategy_id),
            "canonical_file": profile["canonical_file"],
            "source_sha256": "sha256_" + hashlib.sha256(
                io.open(path, "rb").read()).hexdigest(),
            "class": profile.get("strategy") or strategy_id,
            "timeframe": profile.get("execution_timeframe") or "",
            "canonical_measured": profile.get("canonical_measured") or "",
            "classification": (classification.get(strategy_id) or {}).get("signal_family")
                              or (classification.get("strategies", {}).get(strategy_id) or {}).get("signal_family") or "",
            "cluster": {key: (clusters.get(strategy_id) or {}).get(key) for key in
                        ("direction", "logic", "speed", "complexity", "exit_style", "dca",
                         "informative", "regime_hypothesis")},
            "cluster_why": str((clusters.get(strategy_id) or {}).get("why") or "")[:MAX_DOC],
            "docstring": docstring_of(tree),
            "settings": settings_of(tree),
            "indicators": indicators_in([tree]),
            "signals": signals_in(tree, TARGET_FUNCS),
            "functions": functions_of(tree),
        }
        rows.append(row)
    return rows


def load_profiles():
    import csv
    with io.open(PROFILES, encoding="utf-8-sig", newline="") as handle:
        return {row["strategy_id"]: row for row in csv.DictReader(handle)}


def load_clusters():
    """`cluster/clusters.json` keyed by strategy class name.

    The store is a list of per-implementation rows (`strategy`, `marker`...)
    with the five taxonomy axes the `cluster/` module derives, plus `why` - the
    reason for its own label. That reason is carried into the bundle because a
    description that disagrees with it should say so rather than quietly differ.
    """
    if not os.path.exists(CLUSTERS):
        return {}
    data = json.load(io.open(CLUSTERS, encoding="utf-8"))
    if isinstance(data, list):
        return {row.get("strategy"): row for row in data if isinstance(row, dict)}
    return data.get("strategies") or data


def load_classification():
    if not os.path.exists(CLASSIFICATION):
        return {}
    return json.load(io.open(CLASSIFICATION, encoding="utf-8"))


def write_bundle(rows, out=BUNDLE):
    payload = {
        "schema_version": 1,
        "what_this_is": ("Facts extracted from each strategy's canonical file so an LLM can "
                         "state its idea. Read `docstring`, `settings`, `indicators` and "
                         "`signals`; do not infer beyond them."),
        "how_to_answer": ("Write evidence/STRATEGY_IDEAS.json: one entry per family with "
                          "`family`, `stem` (the mechanical family the rows are grouped by), "
                          "`read_from` ({strategy_id, source_sha256} - the one revision the "
                          "sentences were read from), `idea` (2-3 sentences: what it trades, "
                          "on which signal, how it exits), `versions` (a short note per era of "
                          "the family: what changed from one revision to the next, from the "
                          "`settings`, `indicators`, `signals` and `functions` below), "
                          "`evidence` (the code facts the sentence rests on) and `exclude` "
                          "for any row of the stem the family does not cover, with a reason."),
        "strategies": rows,
    }
    with io.open(out, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=False)
        handle.write("\n")
    print("wrote %s (%d strategies)" % (os.path.relpath(out, _ROOT), len(rows)))
    return out


def family_members(family, profiles) -> list[str]:
    """The corpus rows the family covers: by stem, minus what the store excludes.

    Derived, not listed, because a family with 39 revisions would otherwise need
    39 hand-written hash entries that say nothing the corpus does not already
    say. What *is* hand-written is the revision the sentence was read from, and
    that one carries its hash.
    """
    listed = family.get("members")
    if listed:
        return [m.get("strategy_id") if isinstance(m, dict) else m for m in listed]
    stem = family.get("stem") or family.get("family")
    excluded = {e.get("strategy_id") if isinstance(e, dict) else e
                for e in family.get("exclude") or []}
    return [sid for sid in sorted(profiles)
            if family_stem(sid) == stem and sid not in excluded]


def render_html(profiles, ideas, stream):
    """One section per family: the idea, what changed between revisions, its rows."""
    families = ideas.get("families") or []
    parts = [
        "<!doctype html>", '<html lang="en"><head><meta charset="utf-8">',
        "<title>Strategy ideas</title>",
        "<style>",
        "body{font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;margin:2rem auto;"
        "max-width:1100px;padding:0 1rem;color:#1b1f23}",
        "h1{font-size:1.6rem;margin-bottom:.2rem}h2{font-size:1.15rem;margin-top:2rem}",
        "table{border-collapse:collapse;width:100%;margin:.6rem 0 1.2rem}",
        "th,td{border:1px solid #d8dee4;padding:.45rem .6rem;text-align:left;vertical-align:top}",
        "th{background:#f6f8fa;font-weight:600}",
        "code{background:#f6f8fa;padding:.05rem .25rem;border-radius:3px;font-size:.86em}",
        ".idea{font-size:1.02rem}",
        "details{margin:.4rem 0 0}summary{cursor:pointer;color:#444}",
        ".stale{color:#b3261e;font-weight:600}",
        ".meta{color:#57606a;font-size:.9rem}",
        "</style></head><body>",
        "<h1>Strategy ideas</h1>",
        "<p class=\"meta\">One family per block: what the code does, read from the code, "
        "and what changed between revisions. Written by an LLM session, each sentence tied to "
        "the one revision it was read from - a family whose file has changed since is marked "
        "<span class=\"stale\">stale</span>. This is a description, not a measurement, and it "
        "decides nothing.</p>",
    ]
    if not families:
        parts.append("<p>No interpretations yet: run <code>python -m tools.strategy_ideas "
                     "--bundle</code>, then write <code>evidence/STRATEGY_IDEAS.json</code>."
                     "</p>")
    for family in families:
        members = family_members(family, profiles)
        parts.append("<h2>%s <span class=\"meta\">- %d row(s) in the corpus</span>"
                     % (html.escape(str(family.get("family", "?"))), len(members)))
        parts.append('<p class="idea">%s</p>' % html.escape(str(family.get("idea", ""))))
        if family.get("caveat"):
            # Where the code says something the published table does not, the
            # difference belongs on the page: a reader who knows the table would
            # otherwise read the silence as agreement.
            parts.append('<p class="meta"><strong>Caveat:</strong> %s</p>'
                         % html.escape(str(family["caveat"])))
        versions = family.get("versions") or []
        if versions:
            # What changed between revisions is the part a name cannot carry:
            # `V8` says nothing about which indicator it added, and the corpus
            # keeps several revisions per name, so the eras are listed.
            parts.append("<table><tr><th>Versions</th><th>What changed</th></tr>")
            for version in versions:
                parts.append("<tr><td><code>%s</code></td><td>%s</td></tr>"
                             % (html.escape(str(version.get("label", ""))),
                                html.escape(str(version.get("note", "")))))
            parts.append("</table>")
        read_from = family.get("read_from") or {}
        strategy_id = read_from.get("strategy_id")
        row = profiles.get(strategy_id) or {}
        current = row.get("source_sha256")
        if not current:
            state = ('<span class="stale">no longer in the corpus</span>')
        elif current != read_from.get("source_sha256"):
            state = ('<span class="stale">stale - the corpus holds a different '
                     'revision under this name</span>')
        else:
            state = "the corpus still holds it"
        parts.append('<p class="meta">Read from <code>%s</code> <code>%s</code>: %s</p>'
                     % (html.escape(str(strategy_id)),
                        html.escape(str(read_from.get("source_sha256", ""))[:22] + "..."),
                        state))
        parts.append("<table><tr><th>Row in the corpus</th><th>Timeframe</th>"
                     "<th>Class</th><th>File</th></tr>")
        for member in members:
            member_row = profiles.get(member) or {}
            marker = " *" if member == strategy_id else ""
            parts.append("<tr><td><code>%s</code>%s</td><td>%s</td><td>%s</td><td>%s</td>"
                         "</tr>" % (
                             html.escape(str(member)), marker,
                             html.escape(str(member_row.get("execution_timeframe") or "-")),
                             html.escape(str(member_row.get("strategy") or "-")),
                             html.escape(str(member_row.get("canonical_file") or "-"))))
        parts.append("</table>")
        evidence = family.get("evidence") or []
        if evidence:
            parts.append("<details><summary>what this reading rests on</summary><ul>")
            for item in evidence:
                parts.append("<li>%s</li>" % html.escape(str(item)))
            parts.append("</ul></details>")
    parts.append("</body></html>")
    stream.write("\n".join(parts) + "\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bundle, render and check strategy ideas.")
    parser.add_argument("--bundle", action="store_true",
                        help="write evidence/STRATEGY_IDEAS_INPUT.json for the given strategies")
    parser.add_argument("--render", action="store_true",
                        help="write strategy_ideas.html from the ideas store")
    parser.add_argument("--check", action="store_true",
                        help="fail if an idea describes a revision the corpus no longer holds")
    parser.add_argument("--strategies", default="",
                        help="comma-separated strategy_ids (with --bundle)")
    parser.add_argument("--families", default="",
                        help="comma-separated family stems; their newest member is bundled")
    parser.add_argument("--limit", type=int, default=0,
                        help="with --families: how many members per family (default 1, newest)")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()

    profiles = load_profiles()
    if args.bundle:
        ids = [s.strip() for s in args.strategies.split(",") if s.strip()]
        if args.families:
            wanted = [s.strip().lower() for s in args.families.split(",") if s.strip()]
            for stem in wanted:
                members = [sid for sid in profiles if family_stem(sid).lower() == stem]
                ids.extend(sorted(members)[-max(args.limit, 1):])
        if not ids:
            parser.error("--bundle needs --strategies and/or --families")
        rows = bundle_rows(ids, profiles, load_clusters(), load_classification())
        write_bundle(rows)
        for row in rows:
            print("  %-46s %s" % (row["strategy_id"], row.get("error") or row["canonical_file"]))
        return 0

    if args.render:
        ideas = json.load(io.open(IDEAS, encoding="utf-8")) if os.path.exists(IDEAS) else {}
        with io.open(PAGE, "w", encoding="utf-8", newline="\n") as handle:
            render_html(profiles, ideas, handle)
        print("wrote %s (%d families)"
              % (os.path.relpath(PAGE, _ROOT), len(ideas.get("families") or [])))
        return 0

    if args.check:
        if not os.path.exists(IDEAS):
            print("no ideas store yet: %s" % os.path.relpath(IDEAS, _ROOT))
            return 1
        ideas = json.load(io.open(IDEAS, encoding="utf-8"))
        stale = []
        for family in ideas.get("families") or []:
            read_from = family.get("read_from") or {}
            strategy_id = read_from.get("strategy_id")
            current = (profiles.get(strategy_id) or {}).get("source_sha256")
            if not current:
                stale.append("%s (read from %s, which the corpus no longer holds)"
                             % (family.get("family"), strategy_id))
            elif current != read_from.get("source_sha256"):
                stale.append("%s (read from %s, now a different revision)"
                             % (family.get("family"), strategy_id))
            for member in family.get("members") or []:
                # The older shape listed every member with its own hash; keep
                # checking it rather than letting such an entry rot silently.
                member_id = member.get("strategy_id") if isinstance(member, dict) else member
                recorded = member.get("source_sha256") if isinstance(member, dict) else None
                current = (profiles.get(member_id) or {}).get("source_sha256")
                if recorded and current != recorded:
                    stale.append("%s (listed member %s is now a different revision)"
                                 % (family.get("family"), member_id))
        page_current = (os.path.exists(PAGE)
                        and os.path.getmtime(PAGE) >= os.path.getmtime(IDEAS))
        print("strategy ideas: %d families, %d stale, page %s"
              % (len(ideas.get("families") or []), len(stale),
                 "current" if page_current else "NOT current"))
        for entry in stale:
            print("  stale: %s" % entry)
        return 1 if (stale or not page_current) else 0

    parser.print_help()
    return 0


def selftest():
    cases = 0
    assert family_stem("ZaratustraV31") == "Zaratustra"
    assert family_stem("el_extrema_rolling_2") == "el_extrema_rolling"
    assert family_stem("PlusMinusV1") == "PlusMinus"
    assert family_stem("BollingerMACD_V3") == "BollingerMACD"
    cases += 4
    tree = _parse(
        "import talib.abstract as ta\n"
        "class S:\n"
        "    timeframe = '5m'\n"
        "    stoploss = -0.1\n"
        "    def populate_indicators(self, dataframe, metadata):\n"
        "        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=7)\n"
        "        return dataframe\n"
        "    def populate_entry_trend(self, dataframe, metadata):\n"
        "        dataframe.loc[(dataframe['rsi'] < 30), 'enter_long'] = 1\n"
        "        return dataframe\n")
    assert indicators_in([tree]) == ["ta.RSI(dataframe, timeperiod=7)"], indicators_in([tree])
    settings = settings_of(tree)
    assert settings["timeframe"] == "'5m'" and settings["stoploss"] == "-0.1", settings
    signals = signals_in(tree, TARGET_FUNCS)
    assert signals["populate_entry_trend"] == \
        ["enter_long = dataframe['rsi'] < 30"], signals
    assert functions_of(tree) == ["populate_indicators (3 lines)",
                                  "populate_entry_trend (3 lines)"], functions_of(tree)
    cases += 4
    # The version key is read off the name and must not invent one: a family
    # whose ids carry no marker has no marker, and the order is the reader's
    # problem to state, not the tool's to guess.
    assert version_key("ZaratustraV31") == "V31"
    assert version_key("Ichimoku_v12_4") == "v12_4"
    assert version_key("E0V1E_20230915") == "2023-09-15"
    assert version_key("E0V1E_13") == ""
    assert version_key("BinHV45") == "V45"
    assert version_key("GeneTrader_gen9_1735161895_5455") == "2024-12-25"
    cases += 6
    # An idea whose file moved must be reported, not silently re-used.
    profiles = {"X": {"source_sha256": "sha256_new", "execution_timeframe": "5m",
                       "strategy": "X", "canonical_file": "repos/a/X.py"}}
    ideas = {"families": [{"family": "X", "stem": "X",
                            "read_from": {"strategy_id": "X", "source_sha256": "sha256_old"}}]}
    out = io.StringIO()
    render_html(profiles, ideas, out)
    assert "stale" in out.getvalue(), out.getvalue()
    # The members of a family are derived from the corpus, not listed by hand:
    # a 39-revision family would otherwise need 39 hand-written hash entries
    # that repeat what the corpus already knows.
    profiles = {name: {"source_sha256": "s", "execution_timeframe": "5m",
                       "strategy": name, "canonical_file": "repos/a/%s.py" % name}
                for name in ("F", "F2", "F3", "Other")}
    assert family_members({"stem": "F"}, profiles) == ["F", "F2", "F3"]
    assert family_members({"stem": "F", "exclude": ["F2"]}, profiles) == ["F", "F3"]
    cases += 3
    print("strategy_ideas selftest: PASS (%d cases)" % cases)
    return 0


if __name__ == "__main__":
    sys.exit(main())
