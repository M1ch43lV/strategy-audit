## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost). What the scan covers is stated in `.graphifyignore`, which mirrors DOCUMENT_MAP.md's "Do not read" section - change them together.
- Do not add semantic (LLM) extraction to that update. Measured 2026-09-07: all documents together contribute 70 of 1394 nodes, 40 of them strategy names out of the generated `STRATEGY_STATUS.md`, while the code side is deterministic and free. The document pass also exceeds the Gemini free-tier rate limit and truncates on `STRATEGY_STATUS.md` (527 KB).
- If AST extraction reports `process pool terminated abruptly`, re-run it serially (`extract(..., parallel=False)`). The 8-worker default died against this tree while the backtest container held the machine, and it fails silently - 130 files produced zero nodes and the build still exited 0.

## Canonical pipeline state

- Read `HANDOFF.md` before continuing an existing audit task.
- Use `evidence/PIPELINE_STATE.json` or `python -m evidence.pipeline_state --summary` for counts across the complete technical check chain and canonical pooled Full-Backtest. Never derive a pipeline-wide count from an individual runner store such as `PROFILE_SMOKE.json` or `PROFILE_BIAS.json`.
- In Python, use `evidence.pipeline_state.EvidenceStore` instead of reimplementing evidence precedence. The raw JSON stores remain separate, writer-owned provenance.
- Do not start a measurement until the process checks in `HANDOFF.md` confirm that no equivalent runner is active.

## Codex delegation

- The project MCP server `codex` exposes the local Codex CLI for bounded delegated tasks. Give it explicit scope, expected outputs, validation requirements, and files it may modify.
- The current `codex mcp-server` bridge is deprecated upstream. If it stops connecting after a Codex CLI upgrade, inspect the current CLI help and update `.mcp.json` rather than silently proceeding without the delegated review.
