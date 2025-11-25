# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

worklog-mcp is a structured work log MCP (Model Context Protocol) tool for AI assistants. It provides SQLite-backed logging functionality for recording and searching work activities, designed for pharmacist duties and development tasks.

## Build & Install Commands

```bash
# Install with uv tool (recommended)
uv tool install .

# Or install in development mode
uv pip install -e .

# Run CLI commands
worklog-mcp search [keyword] --start YYYY-MM-DD --end YYYY-MM-DD --limit N
worklog-mcp add "content" --category "Category" --tags "tag1,tag2"
worklog-mcp schema  # Output JSON schema for AI registration
```

## Architecture

- **Entry point**: `src/worklog_mcp/main.py` - Contains all logic (Typer CLI, Pydantic models, SQLite operations)
- **Data storage**: SQLite database at `~/.local/share/worklog-mcp/mcp-tools/logs.db` (via platformdirs)
- **CLI framework**: Typer with Rich for table output

### Core Functions

- `add_log(content, category, tags)` - Insert work record
- `search_logs(LogSearchInput)` - Query logs by keyword/date range
- `init_db()` / `get_db_connection()` - Database lifecycle

### Data Models (Pydantic)

- `LogEntry` - Single log record
- `LogSearchInput` - Search parameters
- `AddLogResult` / `LogsSearchResult` - Operation results
