# Configuration Guide

## MCP Client Configuration

freqtrade-mcp uses **stdio transport** — it runs as a local subprocess managed by your MCP client.

### Claude Desktop (macOS / Windows only)

> **Note:** Claude Desktop is not available on Linux. Linux users should use [Claude Code (CLI)](#claude-code) instead.

Add the following to your `claude_desktop_config.json`:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "freqtrade": {
      "command": "freqtrade-mcp",
      "args": [],
      "env": {
        "FREQTRADE_MCP_LOG_LEVEL": "INFO",
        "FREQTRADE_DOCS_PATH": "/path/to/freqtrade/docs"
      }
    }
  }
}
```

If `freqtrade-mcp` is installed in a virtual environment, use the full path:

```json
{
  "mcpServers": {
    "freqtrade": {
      "command": "/path/to/venv/bin/freqtrade-mcp",
      "args": [],
      "env": {
        "FREQTRADE_MCP_LOG_LEVEL": "INFO",
        "FREQTRADE_DOCS_PATH": "/path/to/freqtrade/docs"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add freqtrade-mcp \
  -e FREQTRADE_DOCS_PATH=/path/to/freqtrade/docs \
  -- "$(command -v freqtrade-mcp)"
```

Or with a virtual environment:

```bash
claude mcp add freqtrade-mcp \
  -e FREQTRADE_DOCS_PATH=/path/to/freqtrade/docs \
  -- /path/to/venv/bin/freqtrade-mcp
```

> **Integrations note:** Claude Code (CLI) configuration has been tested and verified. Claude Desktop configuration is based on official documentation but has **not been tested** by the author.

### Generic stdio

Run directly:

```bash
FREQTRADE_DOCS_PATH=/path/to/freqtrade/docs freqtrade-mcp
```

The server communicates over stdin/stdout using the MCP JSON-RPC protocol.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FREQTRADE_DOCS_PATH` | *(not set)* | Path to the freqtrade `docs/` directory. Enables documentation tools. |
| `FREQTRADE_MCP_LOG_LEVEL` | `WARNING` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |

## Documentation Setup

The documentation tools (`freqtrade_list_docs`, `freqtrade_search_docs`, `freqtrade_get_doc`) require a local copy of the freqtrade documentation. Point `FREQTRADE_DOCS_PATH` to the `docs/` directory of a cloned freqtrade repository:

```bash
git clone https://github.com/freqtrade/freqtrade.git /opt/freqtrade
export FREQTRADE_DOCS_PATH=/opt/freqtrade/docs
```

**Behavior when not configured:**
- The server starts normally without errors
- Documentation tools return a guidance message explaining how to enable them
- All other introspection tools work as expected

**Cache behavior:**
- Documentation files are cached with a 1-hour TTL
- Changes to the docs directory are picked up automatically after the cache expires
- Restarting the server clears the cache immediately

## Prerequisites

freqtrade must be installed and importable in the same Python environment as freqtrade-mcp. The server validates the freqtrade version at startup and will refuse to start if:

- freqtrade is not installed
- freqtrade version is below the minimum supported version (2026.2)

## Troubleshooting

### "freqtrade is not installed"

Ensure freqtrade is installed in the same Python environment:

```bash
pip install freqtrade
```

### "freqtrade version too old"

Upgrade freqtrade:

```bash
pip install --upgrade freqtrade
```

### Server not responding

Check stderr output for error messages:

```bash
FREQTRADE_MCP_LOG_LEVEL=DEBUG freqtrade-mcp 2>debug.log
```

### Documentation tools return "not available"

1. Ensure `FREQTRADE_DOCS_PATH` is set and points to a directory containing `.md` files
2. Verify the path: `ls $FREQTRADE_DOCS_PATH/*.md`
3. Check the server logs: `FREQTRADE_MCP_LOG_LEVEL=DEBUG freqtrade-mcp 2>debug.log`

### Tools not appearing in Claude

1. Verify the server starts without errors: `freqtrade-mcp`
2. Check your MCP client configuration path is correct
3. Restart the MCP client after configuration changes
