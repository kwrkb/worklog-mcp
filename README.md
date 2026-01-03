# worklog-mcp

**[English](#english) | [日本語](#japanese)**

<a name="japanese"></a>

シンプルで検索可能なMarkdownベースの作業ログMCPサーバー。

## 設計思想

> 「ログを取るのは億劫だが、過去の解決策は検索したい」

**Keep it Simple**
- データベース不要、すべて平文のMarkdownファイル
- 複雑な設定や外部依存を排除
- 可搬性と可読性を最優先

**Search First**
- 人間が整理するのではなく、AIが検索して情報を引き出す
- シンプルなテキストマッチングで過去の知見を発掘

## 機能

worklog-mcpは2つのMCPツールのみを提供します：

### 1. `save_worklog` - ログを保存
作業ログ、思考の断片、エラー解決策を月単位のMarkdownファイル（`~/.worklogs/YYYY-MM.md`）に保存します。

**パラメータ:**
- `content` (必須): ログの内容
- `tags` (任意): 関連タグのリスト

**保存形式:**
```markdown
### 2026-01-03 14:30:00
Tags: #python #mcp #refactoring

worklog-mcpをMarkdownベースに完全リファクタリング。
SQLiteを削除し、平文管理に変更。
```

### 2. `search_worklogs` - ログを検索
過去のMarkdownファイルを全走査し、キーワードに関連するエントリを抽出します。

**パラメータ:**
- `query` (必須): 検索キーワード（大文字小文字を無視）

**検索ロジック:**
- ディレクトリ内の`.md`ファイルを新しい順に走査
- シンプルなテキストマッチング（grep的な挙動）
- マッチしたエントリ全体を返す

## インストール

### GitHubから直接インストール（推奨）

```bash
# uvがない場合は先にインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# GitHubから直接インストール
uv tool install git+https://github.com/kwrkb/worklog-mcp
```

### ローカルからインストール

```bash
# リポジトリをクローンしてインストール
git clone https://github.com/kwrkb/worklog-mcp.git
cd worklog-mcp
uv tool install .
```

### pipを使用

```bash
pip install git+https://github.com/kwrkb/worklog-mcp
```

## MCPサーバーとして使用

### Claude Code（claude mcp addコマンド）

最も簡単な方法は `claude mcp add` コマンドを使用することです。

#### uvxを使用（インストール不要）

```bash
# グローバルに追加（すべてのプロジェクトで使用可能）
claude mcp add worklog -s user -- uvx --from git+https://github.com/kwrkb/worklog-mcp worklog-mcp-server

# プロジェクト固有で追加（現在のプロジェクトのみ）
claude mcp add worklog -- uvx --from git+https://github.com/kwrkb/worklog-mcp worklog-mcp-server
```

#### インストール済みの場合

```bash
# グローバルに追加
claude mcp add worklog -s user -- worklog-mcp-server

# プロジェクト固有で追加
claude mcp add worklog -- worklog-mcp-server
```

追加後、`claude mcp list` で確認できます：

```bash
claude mcp list
```

### Claude Code（手動設定）

`~/.claude/settings.json` に追加:

```json
{
  "mcpServers": {
    "worklog": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/kwrkb/worklog-mcp", "worklog-mcp-server"]
    }
  }
}
```

### Claude Desktop

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "worklog": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/kwrkb/worklog-mcp", "worklog-mcp-server"]
    }
  }
}
```

### VS Code (Roo Code / Cline)

VS Code で MCP を使用するには、Roo Code や Cline などの拡張機能を使用します。
拡張機能の設定画面（MCP Servers）で以下のように設定してください。

```json
{
  "mcpServers": {
    "worklog": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/kwrkb/worklog-mcp",
        "worklog-mcp-server"
      ]
    }
  }
}
```

### Gemini CLI

Gemini CLI は `gemini mcp add` コマンドまたは設定ファイルの編集でMCPサーバーを追加できます。

#### コマンドで追加

```bash
# グローバルに追加（すべてのプロジェクトで使用可能）
gemini mcp add -s user worklog uvx --from git+https://github.com/kwrkb/worklog-mcp worklog-mcp-server

# プロジェクト固有で追加
gemini mcp add worklog uvx --from git+https://github.com/kwrkb/worklog-mcp worklog-mcp-server
```

**Windows の場合:**

```powershell
gemini mcp add -s user worklog uvx "--from" "git+https://github.com/kwrkb/worklog-mcp" "worklog-mcp-server"
```

#### 手動設定

`~/.gemini/settings.json`（グローバル）または `.gemini/settings.json`（プロジェクト）に追加:

```json
{
  "mcpServers": {
    "worklog": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/kwrkb/worklog-mcp", "worklog-mcp-server"]
    }
  }
}
```

## MCPツールの使用例

MCPサーバーを設定後、Claude Code、Claude Desktop、Gemini CLI から以下のツールが利用できます。

### save_worklog - ログを保存

```
「Pythonのエラーハンドリングの解決策をメモ」
→ save_worklog(content="try-except でログ出力を追加することでデバッグしやすくなった", tags=["python", "debugging"])

「今日やったリファクタリングを記録」
→ save_worklog(content="server.pyをMarkdownベースに書き換え。SQLite削除でコードが150行に削減", tags=["refactoring", "mcp"])
```

### search_worklogs - ログを検索

```
「Pythonに関する過去のメモを探して」
→ search_worklogs(query="python")

「エラーハンドリングの解決策を検索」
→ search_worklogs(query="try-except")
```

## データ保存場所

ログデータはMarkdownファイルとして保存されます：

```
~/.worklogs/2026-01.md
~/.worklogs/2025-12.md
~/.worklogs/2025-11.md
...
```

### カスタム保存先の設定

環境変数 `WORKLOG_DIR` で保存先をカスタマイズできます：

```bash
# カスタムディレクトリを指定
export WORKLOG_DIR=~/Documents/worklogs

# WSLからWindowsのディレクトリを使用
export WORKLOG_DIR=/mnt/c/Users/username/worklogs
```

**永続化するには `.bashrc` や `.zshrc` に追加してください。**

## アンインストールとクリーンアップ

### アンインストール

```bash
# uv tool でインストールした場合
uv tool uninstall worklog-mcp

# pip でインストールした場合
pip uninstall worklog-mcp
```

### データのクリーンアップ

```bash
# デフォルト保存先の削除
rm -rf ~/.worklogs/

# カスタム保存先を使用している場合
rm -rf $WORKLOG_DIR
```

### MCP設定から削除

**Claude Code:**
```bash
# グローバル設定から削除
claude mcp remove worklog -s user

# プロジェクト設定から削除
claude mcp remove worklog
```

**Gemini CLI:**
```bash
# グローバル設定から削除
gemini mcp remove worklog -s user

# プロジェクト設定から削除
gemini mcp remove worklog
```

**手動削除の場合:**
- Claude Code: `~/.claude/settings.json`
- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) または `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
- Gemini CLI: `~/.gemini/settings.json` または `.gemini/settings.json`

---

<a name="english"></a>

# worklog-mcp (English)

Simple, searchable Markdown-based worklog MCP server.

## Philosophy

> "Recording logs is tedious, but searching past solutions is valuable"

**Keep it Simple**
- No database, everything is plain Markdown files
- No complex configuration or external dependencies
- Portability and readability first

**Search First**
- Let AI search and extract information, not humans organizing
- Simple text matching to discover past insights

## Features

worklog-mcp provides only 2 MCP tools:

### 1. `save_worklog` - Save logs
Save work logs, thought fragments, and error solutions to monthly Markdown files (`~/.worklogs/YYYY-MM.md`).

**Parameters:**
- `content` (Required): Log content
- `tags` (Optional): List of related tags

**Storage format:**
```markdown
### 2026-01-03 14:30:00
Tags: #python #mcp #refactoring

Completely refactored worklog-mcp to Markdown-based.
Removed SQLite and switched to plain text management.
```

### 2. `search_worklogs` - Search logs
Scan all past Markdown files and extract entries related to keywords.

**Parameters:**
- `query` (Required): Search keyword (case-insensitive)

**Search logic:**
- Scan `.md` files in directory (newest first)
- Simple text matching (grep-like behavior)
- Return entire matching entries

## Installation

### Install directly from GitHub (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install directly from GitHub
uv tool install git+https://github.com/kwrkb/worklog-mcp
```

### Install locally

```bash
# Clone the repository and install
git clone https://github.com/kwrkb/worklog-mcp.git
cd worklog-mcp
uv tool install .
```

### Using pip

```bash
pip install git+https://github.com/kwrkb/worklog-mcp
```

## Usage as an MCP Server

### Claude Code (claude mcp add command)

The easiest way is to use the `claude mcp add` command.

#### Using uvx (No installation required)

```bash
# Add globally (available in all projects)
claude mcp add worklog -s user -- uvx --from git+https://github.com/kwrkb/worklog-mcp worklog-mcp-server

# Add per project (current project only)
claude mcp add worklog -- uvx --from git+https://github.com/kwrkb/worklog-mcp worklog-mcp-server
```

#### If already installed

```bash
# Add globally
claude mcp add worklog -s user -- worklog-mcp-server

# Add per project
claude mcp add worklog -- worklog-mcp-server
```

After adding, you can verify with `claude mcp list`:

```bash
claude mcp list
```

### Claude Code (Manual Configuration)

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "worklog": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/kwrkb/worklog-mcp", "worklog-mcp-server"]
    }
  }
}
```

### Claude Desktop

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "worklog": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/kwrkb/worklog-mcp", "worklog-mcp-server"]
    }
  }
}
```

### VS Code (Roo Code / Cline)

To use MCP in VS Code, use extensions like Roo Code or Cline.
Configure the extension settings (MCP Servers) as follows:

```json
{
  "mcpServers": {
    "worklog": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/kwrkb/worklog-mcp",
        "worklog-mcp-server"
      ]
    }
  }
}
```

### Gemini CLI

Gemini CLI supports adding MCP servers via the `gemini mcp add` command or by editing the settings file.

#### Using commands

```bash
# Add globally (available in all projects)
gemini mcp add -s user worklog uvx --from git+https://github.com/kwrkb/worklog-mcp worklog-mcp-server

# Add per project
gemini mcp add worklog uvx --from git+https://github.com/kwrkb/worklog-mcp worklog-mcp-server
```

**On Windows:**

```powershell
gemini mcp add -s user worklog uvx "--from" "git+https://github.com/kwrkb/worklog-mcp" "worklog-mcp-server"
```

#### Manual configuration

Add to `~/.gemini/settings.json` (global) or `.gemini/settings.json` (project):

```json
{
  "mcpServers": {
    "worklog": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/kwrkb/worklog-mcp", "worklog-mcp-server"]
    }
  }
}
```

## MCP Tool Usage Examples

After configuring the MCP server, the following tools are available from Claude Code, Claude Desktop, or Gemini CLI.

### save_worklog - Save logs

```
"Note Python error handling solution"
→ save_worklog(content="Adding log output in try-except made debugging easier", tags=["python", "debugging"])

"Record today's refactoring"
→ save_worklog(content="Rewrote server.py to Markdown-based. Removed SQLite, code reduced to 150 lines", tags=["refactoring", "mcp"])
```

### search_worklogs - Search logs

```
"Find past notes about Python"
→ search_worklogs(query="python")

"Search for error handling solutions"
→ search_worklogs(query="try-except")
```

## Data Storage Location

Log data is stored as Markdown files:

```
~/.worklogs/2026-01.md
~/.worklogs/2025-12.md
~/.worklogs/2025-11.md
...
```

### Configure Custom Storage Location

You can customize the storage location using the `WORKLOG_DIR` environment variable:

```bash
# Specify custom directory
export WORKLOG_DIR=~/Documents/worklogs

# Use Windows directory from WSL
export WORKLOG_DIR=/mnt/c/Users/username/worklogs
```

**To persist, add to `.bashrc` or `.zshrc`.**

## Uninstall and Cleanup

### Uninstall

```bash
# If installed with uv tool
uv tool uninstall worklog-mcp

# If installed with pip
pip uninstall worklog-mcp
```

### Data Cleanup

```bash
# Remove default storage location
rm -rf ~/.worklogs/

# If using custom storage location
rm -rf $WORKLOG_DIR
```

### Remove from MCP Configuration

**Claude Code:**
```bash
# Remove from global settings
claude mcp remove worklog -s user

# Remove from project settings
claude mcp remove worklog
```

**Gemini CLI:**
```bash
# Remove from global settings
gemini mcp remove worklog -s user

# Remove from project settings
gemini mcp remove worklog
```

**Manual removal:**
- Claude Code: `~/.claude/settings.json`
- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
- Gemini CLI: `~/.gemini/settings.json` or `.gemini/settings.json`

## License

MIT License
