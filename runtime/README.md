# Runtime and container entry points

This directory keeps the execution environment as one family:

- `Dockerfile.audit*`: pinned default, TensorFlow, package, and RL images;
- `requirements*.txt`: dependency sets copied by those Dockerfiles;
- `profile_*_config.json`: baseline spot and futures Freqtrade configs;
- `*_docker.ps1`: host wrappers that build an image when needed, mount the
  repository at `/audit`, and invoke the corresponding package module;
- `runlock.py` / `runlog.py`: shared single-writer locking and complete command
  provenance used across evidence and benchmark runners.

Run wrappers from any working directory, for example:

```powershell
.\runtime\profile_smoke_docker.ps1 --strategy A9AV
.\runtime\regime_full_backtest_docker.ps1 --workers 1
```

Each wrapper resolves the repository root from its own parent directory. Docker
build context remains the repository root; Dockerfiles therefore copy dependency
files using their `runtime/` paths.
