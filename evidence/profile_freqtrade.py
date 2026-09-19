#!/usr/bin/env python
"""Launch Freqtrade with explicitly registered author-package extensions."""
from __future__ import annotations

import os
import sys

import freqtrade

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def main() -> int:
    import_paths = os.environ.get("PROFILE_STRATEGY_IMPORT_PATH", "")
    for path in import_paths.split(os.pathsep):
        if path and path not in sys.path:
            # Append so installed packages retain precedence over corpus files
            # named like real packages (for example technical.py).
            sys.path.append(path)
    extensions = os.environ.get("PROFILE_FREQTRADE_PATH", "")
    for path in extensions.split(os.pathsep):
        package = os.path.join(path, "freqtrade")
        if path and os.path.isdir(package) and package not in freqtrade.__path__:
            freqtrade.__path__.append(package)

    # Optional audit adapter: wraps entry signals only. With no environment
    # variable this launcher is byte-for-byte equivalent to the old path.
    from regime.gate_adapter import install_from_environment
    install_from_environment()

    # Signature adapters for framework renames. Named by the runner, never
    # applied by default: with no environment variable this launcher is
    # byte-for-byte equivalent to the old path.
    from repair.compat_signature import install_from_environment as install_compat
    install_compat()

    # Opt-in diagnostic for successful recursive-analysis runs that produce no
    # report table.  It does not alter comparisons or verdicts; it only emits
    # the analyzer's per-rung comparison dimensions after the normal method.
    if os.environ.get("PROFILE_RECURSIVE_TRACE") == "1":
        from freqtrade.optimize.analysis.recursive import RecursiveAnalysis

        original_analyze = RecursiveAnalysis.analyze_indicators

        def analyze_with_trace(self):
            result = original_analyze(self)
            pair = self.pair_to_used
            base = self.full_varHolder.indicators[pair].iloc[-1]
            for part in self.partial_varHolder_array:
                compared = base.compare(part.indicators[pair].iloc[-1])
                print("PROFILE_RECURSIVE_TRACE startup=%s shape=%sx%s columns=%s"
                      % (part.startup_candle, compared.shape[0], compared.shape[1],
                         ",".join(map(str, compared.columns))), flush=True)
            print("PROFILE_RECURSIVE_TRACE result_indicators=%s"
                  % len(self.dict_recursive), flush=True)
            return result

        RecursiveAnalysis.analyze_indicators = analyze_with_trace

    from freqtrade.main import main as freqtrade_main

    return int(freqtrade_main() or 0)


if __name__ == "__main__":
    sys.exit(main())
