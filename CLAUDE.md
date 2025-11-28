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

- `add_log(content, category, tags, file_path, line_start, line_end, git_branch, git_commit, project_path)` - Add work record with optional file context
- `search_logs(keyword, start_date, end_date, file_path, project_path, git_branch, limit)` - Search logs with file and project filters
- `get_recent_logs(limit)` - Get recent entries
- `get_logs_by_category(category, limit)` - Filter by category
- `update_log(log_id, content, category, tags, file_path, line_start, line_end, git_branch, git_commit, project_path)` - Update existing log
- `delete_log(log_id)` - Delete a log entry

### MCP Resources

- `logs://today` - Today's logs in Markdown format
- `logs://{date}` - Specific date logs (YYYY-MM-DD)

### MCP Prompts

- `daily-report` - Generate daily report from today's logs
- `weekly-report` - Generate weekly report from this week's logs
- `monthly-report` - Generate monthly report from this month's logs

## IDE Integration Features

worklog-mcp supports automatic file context collection for IDE integration:

### File Context Parameters

When logging work from an IDE, you can include:
- `file_path` - Path to the file you're working on
- `line_start`, `line_end` - Range of lines being modified
- `git_branch` - Current Git branch
- `git_commit` - Current Git commit hash
- `project_path` - Project root directory

### Usage Example

```python
# Log with file context
add_log(
    content="Fixed authentication bug in login handler",
    category="開発",
    tags=["bugfix", "auth"],
    file_path="/project/src/auth/login.py",
    line_start=45,
    line_end=52,
    git_branch="fix/auth-bug",
    git_commit="abc123",
    project_path="/project"
)
```

### Search by File Context

```python
# Find all logs related to a specific file
search_logs(file_path="auth/login.py")

# Find logs from a specific project
search_logs(project_path="/project")

# Find logs from a specific branch
search_logs(git_branch="main")
```
