#!/usr/bin/env python
"""Launch Freqtrade with explicitly registered author-package extensions."""
from __future__ import annotations

import os
import sys

import freqtrade


def main() -> int:
    extensions = os.environ.get("PROFILE_FREQTRADE_PATH", "")
    for path in extensions.split(os.pathsep):
        package = os.path.join(path, "freqtrade")
        if path and os.path.isdir(package) and package not in freqtrade.__path__:
            freqtrade.__path__.append(package)

    # Optional audit adapter: wraps entry signals only. With no environment
    # variable this launcher is byte-for-byte equivalent to the old path.
    from regime.gate_adapter import install_from_environment
    install_from_environment()

    from freqtrade.main import main as freqtrade_main

    return int(freqtrade_main() or 0)


if __name__ == "__main__":
    sys.exit(main())
