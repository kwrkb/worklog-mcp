# worklog-mcp

AIアシスタント向けの構造化された作業記録MCPサーバー。作業履歴を記録・検索できます。

## インストール

```bash
uv tool install .
```

## MCPサーバーとして使用

### Claude Code

`~/.claude/settings.json` に追加:

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp-server"
    }
  }
}
```

### Claude Desktop

`claude_desktop_config.json` に追加:

```json
{
  "mcpServers": {
    "worklog": {
      "command": "worklog-mcp-server"
    }
  }
}
```

## 利用可能なツール

| ツール | 説明 |
|--------|------|
| `add_log` | 作業記録を追加（内容、カテゴリ、タグ） |
| `search_logs` | キーワード・期間で検索 |
| `get_recent_logs` | 最近のログを取得 |
| `get_logs_by_category` | カテゴリ別に取得 |

## CLIとして使用

```bash
# ログ追加
worklog-mcp add "処方箋システムのバグ修正" --category "開発" --tags "バグ修正,処方箋"

# ログ検索
worklog-mcp search "バグ" --start 2025-11-01 --limit 20
```

## データ保存場所

```
~/.local/share/worklog-mcp/mcp-tools/logs.db
```
