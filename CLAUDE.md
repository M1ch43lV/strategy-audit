## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost). What the scan covers is stated in `.graphifyignore`, which mirrors DOCUMENT_MAP.md's "Do not read" section - change them together.
- Do not add semantic (LLM) extraction to that update. Measured 2026-09-07: all documents together contribute 70 of 1394 nodes, 40 of them strategy names out of the generated `STRATEGY_STATUS.md`, while the code side is deterministic and free. The document pass also exceeds the Gemini free-tier rate limit and truncates on `STRATEGY_STATUS.md` (527 KB).
- If AST extraction reports `process pool terminated abruptly`, re-run it serially (`extract(..., parallel=False)`). The 8-worker default died against this tree while the backtest container held the machine, and it fails silently - 130 files produced zero nodes and the build still exited 0.
