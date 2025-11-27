# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

worklog-mcp is a structured work log MCP (Model Context Protocol) server for AI assistants. It provides SQLite-backed logging functionality for recording and searching work activities.

## Build & Install Commands

```bash
# Install with uv tool (recommended)
uv tool install .

# Or install in development mode
uv pip install -e .

# Run MCP server (for Claude Code / Claude Desktop)
worklog-mcp-server

# Run CLI commands (for manual use)
worklog-mcp search [keyword] --start YYYY-MM-DD --end YYYY-MM-DD --limit N
worklog-mcp add "content" --category "Category" --tags "tag1,tag2"
worklog-mcp schema

# Configure database location
worklog-mcp config show                    # Show current config
worklog-mcp config set-db-path <path>      # Set custom DB path
worklog-mcp config reset                   # Reset to default
```

## MCP Server Setup

### Claude Code (~/.claude/settings.json)

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp-server"
    }
  }
}
```

### Claude Desktop (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp-server"
    }
  }
}
```

## Architecture

- **MCP Server**: `src/worklog_mcp/server.py` - FastMCP-based server with tools
- **CLI**: `src/worklog_mcp/main.py` - Typer CLI for manual operations
- **Data storage**: SQLite at `~/.local/share/worklog-mcp/logs.db`

### MCP Tools

- `add_log(content, category, tags)` - Add work record
- `search_logs(keyword, start_date, end_date, limit)` - Search logs
- `get_recent_logs(limit)` - Get recent entries
- `get_logs_by_category(category, limit)` - Filter by category

### MCP Resources

- `logs://today` - Today's logs in Markdown format
- `logs://{date}` - Specific date logs (YYYY-MM-DD)

### MCP Prompts

- `daily-report` - Generate daily report from today's logs
