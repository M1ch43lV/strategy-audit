"""Serialize evidence-store publication after a completed check run."""
from __future__ import annotations

import contextlib
import io
import os


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK_PATH = os.path.join(ROOT, "user_data", ".evidence_finalize.lock")


@contextlib.contextmanager
def publication_lock():
    """Hold one cross-process publication lock for merge plus regeneration."""
    if not os.path.isdir(os.path.dirname(LOCK_PATH)):
        os.makedirs(os.path.dirname(LOCK_PATH))
    handle = io.open(LOCK_PATH, "a+b")
    handle.seek(0, os.SEEK_END)
    if handle.tell() == 0:
        handle.write(b"0")
        handle.flush()
    handle.seek(0)
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
    else:
        import fcntl
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    try:
        yield
    finally:
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        handle.close()


def refresh_published_state():
    """Regenerate every public status view from the canonical evidence stores."""
    from evidence import strategy_status
    from tools import strategy_status_page

    if strategy_status.main([]) != 0:
        raise RuntimeError("strategy status refresh failed")
    if strategy_status_page.main([]) != 0:
        raise RuntimeError("strategy status page refresh failed")
    if strategy_status.main(["--check"]) != 0:
        raise RuntimeError("published pipeline state is stale after refresh")
    print("canonical pipeline state refreshed")
