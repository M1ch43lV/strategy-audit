# -*- coding: utf-8 -*-
"""modpath - locate helper modules that ARE in the corpus but cannot be found.

The audit harness invokes freqtrade with `--strategy-path <dirname(file)>` so
that repositories do not bleed into each other. Helper modules such as
`custom_indicators` often live in a sibling or parent directory and are
therefore invisible to the import machinery. That is a path problem, not a
defect in the strategy - which is why fixing it here touches no strategy file.

Lookup is restricted to the repository the strategy came from. Pulling a module
out of a foreign repository would be exactly the cross-contamination that
`--strategy-path` exists to prevent, and it would silently change which code is
under test.

Known limitation: only top-level module names are checked. An import such as
`freqtrade.litmus` resolves its top level (`freqtrade`) successfully and is
never flagged, even though the submodule is missing.
"""
import ast
import io
import os


def imported_toplevel(path):
    """Return the set of top-level module names the file imports."""
    try:
        tree = ast.parse(io.open(path, encoding="utf-8", errors="replace").read())
    except Exception:
        return set()
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.level == 0 and n.module:
            out.add(n.module.split(".")[0])
    return {m for m in out if m}


def repo_root(strategy_file, repos_dir):
    """Return the `repos/<owner>_<name>` directory above the strategy file."""
    p = os.path.abspath(strategy_file)
    repos_dir = os.path.abspath(repos_dir)
    while True:
        parent = os.path.dirname(p)
        if parent == p:
            return None
        if os.path.abspath(parent) == repos_dir:
            return p
        p = parent


def find_module_dirs(root, modules):
    """Map each wanted module to directories holding `<mod>.py` or `<mod>/__init__.py`."""
    want = set(modules)
    found = {m: [] for m in want}
    for dirpath, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", "venv", ".venv")]
        for m in want:
            if m + ".py" in names:
                found[m].append(dirpath)
            elif m in dirs and os.path.exists(os.path.join(dirpath, m, "__init__.py")):
                found[m].append(dirpath)
    return {m: v for m, v in found.items() if v}


def _distance(strategy_dir, candidate):
    """Proximity key: deepest shared prefix first, then shortest remainder."""
    a = os.path.abspath(strategy_dir).split(os.sep)
    b = os.path.abspath(candidate).split(os.sep)
    common = 0
    for x, y in zip(a, b):
        if x != y:
            break
        common += 1
    return (-common, len(b) - common)


def extra_syspath(strategy_file, repos_dir, missing):
    """Directories to add to sys.path so that `missing` resolves.

    Returns (dirs, unresolved). When a module exists in several places inside
    the repository, the copy nearest to the strategy wins - a strategy is far
    more likely to mean the helper next to it than one several levels away.
    """
    root = repo_root(strategy_file, repos_dir)
    if root is None:
        return [], sorted(missing)
    found = find_module_dirs(root, missing)
    sdir = os.path.dirname(strategy_file)
    dirs, unresolved = [], []
    for m in sorted(missing):
        cands = found.get(m)
        if not cands:
            unresolved.append(m)
            continue
        best = sorted(cands, key=lambda c: _distance(sdir, c))[0]
        if best not in dirs:
            dirs.append(best)
    return dirs, unresolved
