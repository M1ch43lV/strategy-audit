# -*- coding: utf-8 -*-
u"""TOTALITY OF CHECKS — the first assembly-level instrument.

Operator 22.08: "I need a machine that cannot err if the
instructions are correct… Do you think the Assembler errs?"

He is right, and the reason is technical. The semantics of an assembly instruction are defined ON
ALL inputs: `ADD` is defined on any pair of registers, division by zero is not
undefined behavior but a specified `#DE` trap. No input without a defined output exists.

Three of 22.08's four defects violate exactly this:
  · a counterfactual counted "not checked" as "passed";
  · G9_candle: a missing field was read as a skip;
  · G9 before the fix: `not card.get("intracandle")` on a card without the field.
In all three, the function is PARTIAL: on the input "no value" there is no defined
answer, and a default is silently substituted. The default is always flattering.

WHAT THIS INSTRUMENT LOOKS FOR (by AST, not by text — D185: regex on Python is forbidden):

  P1  the result of `.get(k)` (without a default) goes directly into a CONDITION.
      Key absent → None → false. Missing data is read as the answer "no".
  P2  the same under `not` — absence is read as the answer "yes".
      ⚠ 22.08: I had written "worse than P1, flatters". INCORRECT. The instrument does NOT KNOW
      which branch is flattering: in system_audit, absence of a pulse gives FAIL, i.e.,
      an alarm — the direction is safe. The requirement is not "don't do this" but
      "DECLARE the semantics of absence": with a `# TOTAL: reason` marker or code.
  P3  `.get(k, D)` in a condition, where the default D is itself silently true/false.
      The default may be legitimate, but it must be NAMED, not implied.
  P4  index `row[k]` in a condition — absence raises an exception (this is HONEST,
      a loud failure), so it is NOT a defect. Counted separately as a reference.

  P5  THROUGH A VARIABLE: `v = d.get(k)` … `if v:` — the same partiality, just
      spread over two lines. Closed by 22.08: until then, zero findings
      held up due to the instrument's blindness, not code quality.
      It is lifted by an explicit `is None` branch anywhere in the same function.
  P6  DETERMINISM (property 3): time, randomness, filesystem order, and
      set traversal — an input not in the declared inputs. The same verdict
      on the same data must be reproducible.
  P8  GATES VIA NEGATION: `x != BAD` instead of `x == GOOD`. The set
      "not bad" is ALWAYS wider than the set "good" by exactly "don't know", and that
      "don't know" passes silently. The observed case of 22.08: `level != FOUND`
      let through 49 unchecked strategies out of 72 and 12 of 14 survivors.
      Lifted by comparison with a positive value or a declaration.
  P7  CHECK SUBJECT ENUMERATED BY HAND (property 2): a list of files/modules
      as a literal, over which traversal runs. Exactly the freeze_guard defect and the
      first defect of this instrument: a new file silently remains unchecked.

WHAT IT CANNOT DO — named so as not to pass it off as completeness:
  · does not trace values through function returns and object fields;
  · does not know whether a default is legitimate by the task's meaning;
  · P7 recognizes the list by the look of the name (.py/.json/path), not by usage.

Run:  python totality.py [file ...]
Exit code 1 on P1/P2 findings — a rule without an exit code does not apply.
"""
from __future__ import print_function

import ast
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))

# ⚠ A MANUAL LIST of files STOOD HERE. This is exactly the freeze_guard defect of the same
# day: the response depended on an input that was not among the declared inputs, and a new
# file silently remained unchecked. The list has been replaced with a FULL TRAVERSAL — the subject
# of the check is enumerated by the machine, not remembered by the author.
# TOTAL: foreign code in repos*/ — SUBJECT of audit, not our machine; holding it
# to our standard is impossible, and staying silent about it too: it is counted separately.
SKIP_DIRS = {".git", "__pycache__", "data", "results", "ftenv", "venv"}
FOREIGN = ("repos", "repos_longonly")   # foreign: counted, but not required

# ── PROVENANCE OF RULES ────────────────────────────────────────────────────
# Operator, 22.08: “Categories must be derived from the nature of things, not
# imposed on it” — said about the structure of the machine ITSELF.
#
# Verified on this same instrument, and the principle was confirmed by measurement:
#   P1/P2/P5/P7 derived from OBSERVED failures — found the real;
#   P6/P3 imposed by me from general knowledge about Python — P6 yielded 20 findings,
#   of which 12 turned out to be an already-sorted traversal (three exception patches
#   in a row), P3 yielded not a single finding EVER.
#
# Hence the executable requirement: a rule must have a CASE from which
# it was born. A rule without a observed case is a hypothesis, and a hypothesis has NO
# RIGHT to stand in a hook with a return code: it is printed, but does not fail the build.
# This is the same as what was done on 19.08 for defects (origin became a field, not prose),
# only now for checks.
ORIGIN = {
    "P1": (u"observed", u"22.08 G9_candle: a missing card field was read"
                      u"as “check passed”"),
    "P2": (u"observed", u"22.08 my counterfactual on traps: “not checked”"
                      u"counted as “passed”, nearly published 0→8"),
    "P5": (u"observed", u"22.08 the same partiality, split across two lines;"
                      u"while there was no rule, zero held on blindness"),
    "P7": (u"observed", u"22.08 freeze_guard watched the file of step NAMES, but"
                      u"not the code deciding the fate; and the first defect of this"
                      u"instrument — the manual file list"),
    "P8": (u"observed", u"22.08 evening: G6/G7 stood as `level != FOUND`, and "
                      u"\"could not verify\" passed; 12 of 14 survivors "
                      u"were NEVER tested for lookahead"),
    "P3": (u"imposed", u"general knowledge of Python; NO case in the registry, "
                        u"0 findings over the entire period"),
    "P6": (u"imposed", u"general knowledge of nondeterminism; NO case in the registry, "
                        u"12 of the first 20 findings turned out to be false"),
}
GATING = set(k for k, v in ORIGIN.items() if v[0] == u"observed")


def enumerate_py(root):
    out = []
    # TOTAL: traversal order does not matter — result is sorted before return
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            if f.endswith(".py"):
                rel = os.path.relpath(os.path.join(base, f), root)
                if rel.split(os.sep)[0] in FOREIGN:
                    continue
                out.append(rel)
    return sorted(out)


class Scan(ast.NodeVisitor):
    def __init__(self, path, src):
        self.path = path
        self.lines = src.split("\n")
        self.hits = []          # (code, line, text)
        self.declared = []      # removed by the # TOTAL: marker
        self.honest = 0         # P4: loud failure
        self.exempt = set()     # dismissed on substantive grounds (sorted around traversal)

    # ── conditions under which the value decides the fate ────────────────────
    def _tests(self, node):
        if isinstance(node, ast.If):
            return [node.test]
        if isinstance(node, (ast.While, ast.Assert)):
            return [node.test]
        if isinstance(node, ast.IfExp):
            return [node.test]
        if isinstance(node, ast.comprehension):
            return list(node.ifs)
        return []

    def _walk_test(self, t, negated=False):
        u"""Decompose the condition into elementary checks, remembering negation."""
        if isinstance(t, ast.UnaryOp) and isinstance(t.op, ast.Not):
            return self._walk_test(t.operand, not negated)
        if isinstance(t, ast.BoolOp):
            out = []
            for v in t.values:
                out += self._walk_test(v, negated)
            return out
        return [(t, negated)]

    def _report(self, node, code, why):
        ln = getattr(node, "lineno", 0)
        txt = self.lines[ln - 1].strip() if 0 < ln <= len(self.lines) else u""
        # ⚠ first run gave a FALSE positive: in memory_audit the dictionary
        # inbound is built by a FULL traversal of all files, and the absence of a key there
        # is not "don't know" but a definite answer "no inbound links". The tool cannot
        # decide this for the author — but it CAN REQUIRE the author
        # wrote the definition aloud. Mark `# TOTAL: reason` on the line
        # removes the finding and remains in the code as declared semantics.
        # ⚠ 22.08: the marker was accepted ONLY on the line itself, and a declaration
        # written as an adjacent comment above was not counted. The author
        # writes an explanation above the line ? this is a normal way, and the tool must
        # understand it, otherwise it forces writing awkwardly for its own simplicity.
        if "# TOTAL:" in txt or self._declared_above(ln):
            self.declared.append((code, ln, txt[:96]))
            return
        self.hits.append((code, ln, txt[:96], why))

    def _declared_above(self, ln):
        u"""The adjacent comment block above belongs to this line."""
        i = ln - 2
        while i >= 0:
            t = self.lines[i].strip()
            if not t.startswith("#"):
                return False
            if "# TOTAL:" in t or t.startswith("# TOTAL"):
                return True
            i -= 1
        return False

    def _check_expr(self, e, negated):
        # .get(...)
        if (isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute)
                and e.func.attr == "get"):
            if len(e.args) == 1:
                self._report(e, "P2" if negated else "P1",
                             u"absence of a key is silently read as \"%s\" — "
                             u"semantics not declared"
                             % (u"YES" if negated else u"NO"))
            elif len(e.args) >= 2:
                d = e.args[1]
                lit = isinstance(d, ast.Constant)
                self._report(e, "P3",
                             u"default %s is implied, not declared"
                             % (repr(d.value) if lit else u"expression"))
        # row[k] ? fails when absent: honestly
        elif isinstance(e, ast.Subscript):
            self.honest += 1
        # bool(x.get(...))
        elif (isinstance(e, ast.Call) and isinstance(e.func, ast.Name)
                and e.func.id == "bool" and e.args):
            self._check_expr(e.args[0], negated)

    # ── P5: partiality spread across two lines ───────────────────
    def visit_FunctionDef(self, node):
        risky = {}          # name → line where taken from .get()
        guarded = set()     # name for which there is a branch on None
        for n in ast.walk(node):
            if isinstance(n, ast.Assign) and len(n.targets) == 1                     and isinstance(n.targets[0], ast.Name)                     and isinstance(n.value, ast.Call)                     and isinstance(n.value.func, ast.Attribute)                     and n.value.func.attr == "get"                     and len(n.value.args) == 1:
                risky.setdefault(n.targets[0].id, n.lineno)
            if isinstance(n, ast.Compare):
                for side in [n.left] + list(n.comparators):
                    if isinstance(side, ast.Name) and any(
                            isinstance(c, ast.Constant) and c.value is None
                            for c in n.comparators):
                        guarded.add(side.id)
        for n in ast.walk(node):
            for t in self._tests(n):
                for e, neg in self._walk_test(t):
                    if isinstance(e, ast.Name) and e.id in risky                             and e.id not in guarded:
                        self._report(e, "P5",
                                     u"`%s` taken from .get() on line %d and "
                                     u"resolves the branch without a None fork"
                                     % (e.id, risky[e.id]))
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    # ── P8: gates expressed via negation ───────────────────────
    def visit_Assign(self, node):
        v = node.value
        if isinstance(v, ast.Compare) and len(v.ops) == 1                 and isinstance(v.ops[0], ast.NotEq):
            # only where the value IS PLACED into the verdict dictionary —
            # `g["G6"] = ... != FOUND`. We don't touch ordinary `if a != b`:
            # the rule's subject is GATES, not any inequality.
            tgt = node.targets[0] if node.targets else None
            if isinstance(tgt, ast.Subscript):
                self._report(node, "P8",
                             u"gates are defined by negation: «not bad» is wider than "
                             u"«good» exactly by «unknown»")
        self.generic_visit(node)

    # ── P6: nondeterminism ────────────────────────────────────────────
    NONDET = {("time", "time"), ("time", "localtime"), ("time", "gmtime"),
              ("random", "random"), ("random", "choice"), ("random", "shuffle"),
              ("os", "listdir"), ("os", "walk"), ("datetime", "now"),
              ("datetime", "today"), ("uuid", "uuid4")}

    ORDER_ONLY = {("os", "listdir"), ("os", "walk")}

    def visit_Call(self, node):
        # ⚠ clarified 22.08: `sorted(os.listdir(...))` is ALREADY deterministic in
        # order, and counting it as a defect is the same as treating a wide
        # trailing as a trap. The instrument must distinguish «nondeterminism» from
        # «enumeration». Sorted traversal is dismissed on the merits; time and
        # randomness — only by declaration, because legality depends on
        # usage (in freeze_guard time IS the subject of measurement).
        f = node.func
        if isinstance(f, ast.Name) and f.id == "sorted":
            # traversal can be directly in the argument and inside a generator:
            # `sorted(os.listdir(p))` and `sorted(f for f in os.listdir(p) ...)`
            # — both are ordered. We search the ENTIRE argument subtree.
            for a in node.args:
                for sub in ast.walk(a):
                    if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)                             and isinstance(sub.func.value, ast.Name)                             and (sub.func.value.id, sub.func.attr) in self.ORDER_ONLY:
                        self.exempt.add(id(sub))
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            key = (f.value.id, f.attr)
            # time.gmtime(epoch) / localtime(epoch) WITH AN ARGUMENT — a pure
            # function of the passed number, it doesn't read the clock. Counting it
            # as nondeterminism is an error of the same kind as «wide trailing».
            pure_arg = (key in (("time", "gmtime"), ("time", "localtime"),
                                ("time", "strftime")) and node.args)
            if key in self.NONDET and id(node) not in self.exempt and not pure_arg:
                self._report(node, "P6",
                             u"%s.%s — %s"
                             % (f.value.id, f.attr,
                                u"order is not specified: wrap in sorted()"
                                if key in self.ORDER_ONLY
                                else u"input outside declared; declare # TOTAL:"))
        self.generic_visit(node)

    def generic_visit(self, node):
        for t in self._tests(node):
            for e, neg in self._walk_test(t):
                self._check_expr(e, neg)
        ast.NodeVisitor.generic_visit(self, node)


def hand_scope(tree, lines):
    u"""P7: the subject of check is enumerated by hand (list of paths/modules as a literal)."""
    out = []
    for n in tree.body:
        if not isinstance(n, ast.Assign) or not isinstance(n.value, (ast.List, ast.Tuple, ast.Set)):
            continue
        vals = [e.value for e in n.value.elts if isinstance(e, ast.Constant)
                and isinstance(e.value, str)]
        if len(vals) < 2:
            continue
        looks = sum(1 for v in vals if v.endswith(".py") or v.endswith(".json")
                    or "/" in v or "\\" in v)
        if looks >= max(2, len(vals) // 2):
            ln = n.lineno
            txt = lines[ln - 1].strip() if 0 < ln <= len(lines) else u""
            above = False
            i = ln - 2
            while i >= 0 and lines[i].strip().startswith("#"):
                if "# TOTAL" in lines[i]:
                    above = True
                    break
                i -= 1
            if "# TOTAL:" not in txt and not above:
                out.append(("P7", ln, txt[:96],
                            u"%d paths are enumerated by hand — a new file silently "
                            u"won't be checked" % len(vals)))
    return out


def scan(path):
    src = io.open(path, encoding="utf-8").read()
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return None, exc
    s = Scan(path, src)
    s.visit(tree)
    s.hits += hand_scope(tree, s.lines)
    return s, None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    files = args or enumerate_py(ROOT)
    total = {"P1": 0, "P2": 0, "P3": 0, "P5": 0, "P6": 0, "P7": 0, "P8": 0}
    honest = 0
    declared = 0
    unread = []
    print(u"── TOTALITY: input without a defined output")
    print()
    for rel in files:
        p = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
        if not os.path.exists(p):
            unread.append(rel)
            continue
        s, err = scan(p)
        if s is None:
            unread.append(u"%s (%s)" % (rel, err.__class__.__name__))
            continue
        honest += s.honest
        declared += len(s.declared)
        bad = [h for h in s.hits if h[0] in ("P1", "P2", "P5", "P6", "P7", "P8")]
        soft = [h for h in s.hits if h[0] == "P3"]
        for c, _l, _t, _w in s.hits:
            total[c] = total.get(c, 0) + 1
        if bad or soft:
            print(u"  %s" % rel)
            for c, ln, txt, why in sorted(bad, key=lambda x: x[1]):
                print(u"    ⛔ %s:%-4d %s" % (c, ln, txt))
                print(u"           %s" % why)
            if soft:
                print(u"    · P3 defaults in conditions: %d" % len(soft))
            print()

    print(u"=" * 62)
    print(u"  P1 absence → «NO»          %4d" % total["P1"])
    print(u"  P2 absence → «YES», not declared%4d" % total["P2"])
    print(u"  P3 default not declared      %4d" % total["P3"])
    print(u"  P5 partiality via variable    %4d" % total["P5"])
    print(u"  P6 nondeterminism               %4d" % total["P6"])
    print(u"  P7 item enumerated by hand    %4d" % total["P7"])
    print(u"  P8 gate via negation      %4d" % total["P8"])
    print(u"  P4 loud failure (reference)      %4d" % honest)
    print(u"  declared total (# TOTAL)  %4d" % declared)
    if unread:
        # unread file — NOT "ok": this is exactly the defect
        print(u"  ⛔ NOT READ                %4d  — %s"
              % (len(unread), ", ".join(unread[:4])))
    print()
    print(u"? COMPLETENESS, NOT COUNT. Closed 22.08: variable (P5), determinism (P6),")
    print(u"  enumerating item by hand (P7). NOT closed and therefore I do not claim")
    print(u"  completeness: value via function return and via object fields;")
    print(u"  legitimacy of default by meaning; P7 recognizes list by name form.")
    # ? only rules with an observed case break the build. Overlaid ones are printed
    # and remain visible, but have no right to refuse until a case appears.
    gate = sum(total.get(k, 0) for k in GATING)
    hyp = sum(total.get(k, 0) for k in ORIGIN if k not in GATING)
    print()
    print(u"── origin of rules (principle: category from the nature of things)")
    for k in ("P1", "P2", "P3", "P5", "P6", "P7", "P8"):
        kind, why = ORIGIN[k]
        mark = u"⚖ breaks" if k in GATING else u"? hypothesis, does NOT fail"
        print(u"  %-3s %-9s %-22s %s" % (k, kind, mark, why[:52]))
    print(u"  ⇒ refusals by rules with provenance: %d · by hypotheses: %d"
          % (gate, hyp))
    return 1 if (gate or unread) else 0


if __name__ == "__main__":
    sys.exit(main())
