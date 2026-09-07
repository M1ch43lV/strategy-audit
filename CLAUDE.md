## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `python graphify_scope_sync.py` and then `graphify update graphify-scope` to keep the graph current (AST-only, no API cost). Not `graphify update .` - the graph is built from `graphify-scope/`, a curated copy that excludes `repos/`, `ftenv/`, `old/`, `corpus/`, `user_data/` and `repair/patched/`. Scanning `.` would pull in several hundred thousand files, and skipping the sync step rebuilds the graph from a stale copy.
