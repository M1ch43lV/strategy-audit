# -*- coding: utf-8 -*-
"""Activate the versioned Class 1 compatibility shim in every Python process."""
try:
    import compat_shim
    compat_shim.install()
except Exception:
    # The shim must never prevent Python itself from starting. Individual
    # strategy checks will retain a readable error if a required alias remains.
    pass
