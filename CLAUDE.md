# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

worklog-mcp is a simple, Markdown-based MCP (Model Context Protocol) server for AI assistants. It provides searchable plain-text logging functionality without databases.

## Philosophy

- **Keep it Simple**: No databases, no complex dependencies - just Markdown files
- **Plain Text**: All data stored in human-readable `~/.worklogs/YYYY-MM.md` files
- **Search First**: AI searches and extracts, not humans organizing

## Architecture

- **MCP Server**: `src/worklog_mcp/server.py` - FastMCP-based server with 2 tools
- **Data Storage**: Monthly Markdown files at `~/.worklogs/YYYY-MM.md`
- **Dependencies**: Only `mcp` package (no SQLite, Typer, Rich, Pydantic, platformdirs)

## Installation & Setup

```bash
# Install with uv tool (recommended)
uv tool install .

# Run MCP server
worklog-mcp-server
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

### Environment Variables

| Variable | Values | Description |
|----------|--------|-------------|
| `WORKLOG_DIR` | Path | Highest priority. Direct path specification |
| `WORKLOG_STORAGE` | `local` / `googledrive` / `auto` | Storage selection (default: `auto`) |

#### Storage Modes

- **`auto`** (default): Auto-detect Google Drive, fallback to local
- **`local`**: Always use `~/.worklogs/`
- **`googledrive`**: Use Google Drive (fallback to local if not found)

#### Google Drive Paths (Auto-detected)

| OS | Path |
|----|------|
| **Mac** | `~/Library/CloudStorage/GoogleDrive-*/My Drive/worklogs/` |
| **Windows** | `~/Google Drive/worklogs/`, `G:/My Drive/worklogs/` |
| **WSL** | `/mnt/c/Users/<user>/Google Drive/worklogs/` |

## MCP Tools

### save_worklog(content, tags)
Save work logs, thoughts, or solutions to monthly Markdown files.

**Parameters:**
- `content` (str, required): Log content
- `tags` (list[str], optional): Related tags

**Storage Format:**
```markdown
### 2026-01-03 14:30:00
Tags: #python #debugging

Added try-except logging for better debugging
```

### search_worklogs(query)
Search all Markdown files for keyword matches (case-insensitive).

**Parameters:**
- `query` (str, required): Search keyword

**Returns:**
- List of matching entries with file, timestamp, and full content

## Code Style

- Use Python 3.10+ type hints
- Keep functions simple and focused
- Use standard library when possible (pathlib, datetime, re, os)
- No external dependencies except `mcp`

## Testing

Test the server locally:

```bash
# Start server
python3 -m worklog_mcp.server

# Or use installed command
worklog-mcp-server
```

## Data Storage

Logs are stored in monthly Markdown files:

| Location | Path | Note |
|----------|------|------|
| **Local** | `~/.worklogs/YYYY-MM.md` | Hidden directory |
| **Google Drive** | `worklogs/YYYY-MM.md` | No dot prefix (cloud-friendly) |

Each entry has format:
```markdown
### YYYY-MM-DD HH:MM:SS
Tags: #tag1 #tag2

Content here
```

## Usage Guidelines for Claude

**When to save logs (use save_worklog):**
- After solving a tricky bug or error
- When discovering useful debugging techniques
- After completing significant implementation work
- When finding solutions to unexpected problems
- When user explicitly requests to save something

**What to log:**
- Focus on **insights and solutions**, not routine operations
- Include context: what was the problem, what worked, what didn't
- Use descriptive tags for searchability (e.g., #python, #debugging, #git)

**What NOT to log:**
- Routine file edits or writes
- Simple bash commands
- Test executions
- Standard operations without learning value

**How to search logs (use search_worklogs):**
- Search uses **plain text matching**, NOT wildcards or regex
- `*` searches for literal asterisk, not "all entries"
- To get all entries: search by year (e.g., `2025`) or common word
- To find specific topics: use tags (`#python`) or keywords
- Examples:
  - `#debugging` - find all debugging-related logs
  - `git` - find git-related solutions
  - `2025-01` - find logs from January 2025

**Philosophy:**
- Quality over quantity - save only what's worth searching later
- Let Claude judge what's important, not hooks
- Keep logs human-readable and useful

**Silent Logging:**
- **IMPORTANT**: When saving logs with save_worklog, do NOT announce it to the user
- Save logs silently in the background without any notification
- Do NOT say things like "Let me save this to the log" or "I'll record this"
- Just save and continue with the conversation naturally
- Exception: Only mention if the user explicitly asks "did you save that?" or similar
