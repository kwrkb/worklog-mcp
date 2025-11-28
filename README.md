# worklog-mcp

**[English](#english) | [日本語](#japanese)**

<a name="japanese"></a>

AIアシスタント向けの構造化された作業記録MCPサーバー。作業履歴を記録・検索できます。

## 機能

- **作業記録の追加**: カテゴリやタグ付きで作業内容を記録
- **ファイルコンテキスト**: 編集ファイル、行番号、Gitブランチなどを自動記録
- **ログ検索**: キーワード、期間、カテゴリ、ファイルパスで柔軟に検索
- **SQLite保存**: ローカルにデータを永続化

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

# または開発モードでインストール
uv pip install -e .
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

### add_log - 作業記録を追加

```
「APIエンドポイントの実装を完了した」と作業記録に追加して
→ add_log(content="APIエンドポイントの実装を完了した", category="開発", tags="API,実装")

今日やったバグ修正を記録して
→ add_log(content="ログイン画面のバリデーションエラーを修正", category="開発", tags="バグ修正,認証")
```

**パラメータ:**
- `content` (必須): 作業内容
- `category` (任意): カテゴリ名（例: 開発、レビュー、会議）
- `tags` (任意): カンマ区切りのタグ
- `file_path` (任意): 作業中のファイルパス
- `line_start`, `line_end` (任意): 作業した行範囲
- `git_branch` (任意): 現在のGitブランチ
- `git_commit` (任意): 現在のGitコミットハッシュ
- `project_path` (任意): プロジェクトのルートパス

### search_logs - ログを検索

```
「API」に関するログを検索して
→ search_logs(keyword="API")

先週のバグ修正履歴を見せて
→ search_logs(keyword="バグ", start_date="2025-11-18", end_date="2025-11-25")
```

**パラメータ:**
- `keyword` (任意): 検索キーワード
- `start_date` (任意): 開始日（YYYY-MM-DD形式）
- `end_date` (任意): 終了日（YYYY-MM-DD形式）
- `file_path` (任意): ファイルパスで絞り込み（部分一致）
- `project_path` (任意): プロジェクトパスで絞り込み（部分一致）
- `git_branch` (任意): Gitブランチで絞り込み（完全一致）
- `limit` (任意): 取得件数（デフォルト: 50）

### get_recent_logs - 最近のログを取得

```
最近の作業履歴を見せて
→ get_recent_logs(limit=10)
```

**パラメータ:**
- `limit` (任意): 取得件数（デフォルト: 10）

### get_logs_by_category - カテゴリ別に取得

```
開発カテゴリのログを見せて
→ get_logs_by_category(category="開発", limit=20)
```

**パラメータ:**
- `category` (必須): カテゴリ名
- `limit` (任意): 取得件数（デフォルト: 50）

## MCPリソース - ログをファイルのように参照

MCPのリソース機能により、ログデータをファイルのように参照できます。

### logs://today - 今日のログ

```
logs://today のリソースを開いて
→ 今日の作業ログがMarkdown形式で表示されます
```

### logs://{date} - 特定日のログ

```
logs://2025-11-25 のリソースを開いて
→ 指定日のログがMarkdown形式で表示されます
```

## MCPプロンプト - 日報作成テンプレート

Claude のプロンプトメニューから `daily-report` を選択すると、今日のログを元に業務日報を自動生成できます。

**プロンプト内容:**
- 本日のハイライト
- 業務詳細（カテゴリ別）
- 課題と解決
- 明日の予定

## 自動ログ機能（Claude Code Hooks）

Claude Code の Hooks 機能を使うと、作業完了時に自動でログを記録できます。

### 設定方法

`~/.claude/settings.json` に以下を追加：

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "会話で行った作業を worklog MCP の add_log ツールで記録してください。カテゴリは作業内容に応じて「開発」「調査」「レビュー」「設定」などを選択し、関連するタグも付けてください。"
          }
        ]
      }
    ]
  }
}
```

### 動作

1. Claude Code での作業が完了すると、Stop フックがトリガー
2. Claude が自動的に `add_log` ツールを呼び出し、作業内容を記録
3. カテゴリとタグが自動で付与される

### カスタマイズ例

#### 特定ツール使用後にログ

Edit/Write ツール使用後に自動記録する場合：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "ファイルを編集しました。この変更内容を worklog MCP の add_log で記録してください。"
          }
        ]
      }
    ]
  }
}
```

#### コミット後にログ

Git コミット後に自動記録する場合：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "git commit を実行した場合は、コミット内容を worklog MCP の add_log で記録してください。git commit でなければ何もしないでください。"
          }
        ]
      }
    ]
  }
}
```

### 注意事項

- Hooks は Claude Code v1.0.17 以降で利用可能
- `type: "prompt"` を使うと、Claude に追加の指示を与えられます
- `type: "command"` を使うと、シェルコマンドを直接実行できます

## CLIとして使用

MCPサーバー経由ではなく、コマンドラインから直接操作することもできます。

### ログを追加

```bash
# 基本的な追加
worklog-mcp add "認証システムのバグ修正"

# カテゴリとタグを指定
worklog-mcp add "認証システムのバグ修正" --category "開発" --tags "バグ修正,認証"

# 短縮オプション
worklog-mcp add "会議メモ" -c "会議" -t "定例,チーム"
```

### ログを検索

```bash
# キーワード検索
worklog-mcp search "バグ"

# 期間を指定
worklog-mcp search "バグ" --start 2025-11-01 --end 2025-11-30

# 件数を制限
worklog-mcp search "バグ" --limit 20

# 全てのオプションを組み合わせ
worklog-mcp search "API" --start 2025-11-01 --end 2025-11-30 --limit 10
```

### スキーマを確認

```bash
worklog-mcp schema
```

## データ保存場所

ログデータはSQLiteデータベースに保存されます：

```
~/.local/share/worklog-mcp/logs.db
```

### データベース保存先の設定

WSLとWindows間でデータベースを共有したい場合など、保存先をカスタマイズできます。

#### 現在の設定を確認

```bash
worklog-mcp config show
```

出力例：
```
worklog-mcp Configuration

Config File:     /home/user/.config/worklog-mcp/config.json
DB Path (current): /home/user/.local/share/worklog-mcp/logs.db
  └─ Using default path

Default DB Path: /home/user/.local/share/worklog-mcp/logs.db
```

#### データベースパスを変更

```bash
# WSLからWindowsのデータベースを使用する場合
worklog-mcp config set-db-path /mnt/c/Users/username/worklog.db

# Windowsから別の場所を指定する場合
worklog-mcp config set-db-path C:\Users\username\Documents\worklog.db
```

#### デフォルトに戻す

```bash
worklog-mcp config reset
```

**注意事項:**
- 設定ファイルはユーザーのホームディレクトリに保存されます（`~/.config/worklog-mcp/config.json`）
- `uvx` で実行する場合でも設定は永続化されます
- パスは絶対パスで指定してください
- 既存のデータベースを指定すると、そのデータを使用します

### データベーススキーマ

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    file_path TEXT,
    line_start INTEGER,
    line_end INTEGER,
    git_branch TEXT,
    git_commit TEXT,
    project_path TEXT
);
```

## トラブルシューティング

### MCPサーバーが認識されない

1. `worklog-mcp-server` コマンドがPATHに通っているか確認：
   ```bash
   which worklog-mcp-server
   ```

2. Claude Code/Desktopを再起動

3. 設定ファイルのJSON構文を確認

### uvでインストールしたコマンドが見つからない

uvツールのパスを確認し、必要に応じてPATHに追加：

```bash
# パスを確認
uv tool dir

# .bashrc や .zshrc に追加
export PATH="$HOME/.local/bin:$PATH"
```

## アンインストールとクリーンアップ

### アンインストール

```bash
# uv tool でインストールした場合
uv tool uninstall worklog-mcp

# pip でインストールした場合
pip uninstall worklog-mcp
```

### データと設定のクリーンアップ

アンインストール後、以下のファイルが残ります。必要に応じて削除してください。

#### データベースファイル

```bash
# Linux/macOS
rm -rf ~/.local/share/worklog-mcp/

# Windows
rmdir /s "%LOCALAPPDATA%\mcp-tools\worklog-mcp"
```

#### 設定ファイル

```bash
# Linux/macOS
rm -rf ~/.config/worklog-mcp/

# Windows
rmdir /s "%LOCALAPPDATA%\worklog-mcp"
```

#### MCP設定から削除

Claude Code や Claude Desktop、Gemini CLI の設定ファイルから `worklog` サーバーの設定を削除してください。

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

A structured work log MCP server for AI assistants. Record and search your work history.

## Features

- **Add Work Logs**: Record work details with categories and tags.
- **File Context**: Automatically record edited files, line numbers, Git branches, and more.
- **Search Logs**: Flexible search by keyword, date range, category, and file paths.
- **SQLite Storage**: Persist data locally.

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

# Or install in editable mode
uv pip install -e .
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

### add_log - Add a work log

```
Add "Completed API endpoint implementation" to work log
→ add_log(content="Completed API endpoint implementation", category="Development", tags="API,Implementation")

Record the bug fix I did today
→ add_log(content="Fixed validation error on login screen", category="Development", tags="Bugfix,Auth")
```

**Parameters:**
- `content` (Required): Details of the work.
- `category` (Optional): Category name (e.g., Development, Review, Meeting).
- `tags` (Optional): Comma-separated tags.
- `file_path` (Optional): Path to the file you're working on.
- `line_start`, `line_end` (Optional): Range of lines being modified.
- `git_branch` (Optional): Current Git branch.
- `git_commit` (Optional): Current Git commit hash.
- `project_path` (Optional): Project root directory.

### search_logs - Search logs

```
Search logs for "API"
→ search_logs(keyword="API")

Show me bug fix history from last week
→ search_logs(keyword="Bug", start_date="2025-11-18", end_date="2025-11-25")
```

**Parameters:**
- `keyword` (Optional): Search keyword.
- `start_date` (Optional): Start date (YYYY-MM-DD format).
- `end_date` (Optional): End date (YYYY-MM-DD format).
- `file_path` (Optional): Filter by file path (partial match).
- `project_path` (Optional): Filter by project path (partial match).
- `git_branch` (Optional): Filter by Git branch (exact match).
- `limit` (Optional): Number of results (default: 50).

### get_recent_logs - Get recent logs

```
Show me recent work history
→ get_recent_logs(limit=10)
```

**Parameters:**
- `limit` (Optional): Number of results (default: 10).

### get_logs_by_category - Get logs by category

```
Show me logs in Development category
→ get_logs_by_category(category="Development", limit=20)
```

**Parameters:**
- `category` (Required): Category name.
- `limit` (Optional): Number of results (default: 50).

## MCP Resources - Reference logs like files

MCP Resources allow you to reference log data as if they were files.

### logs://today - Today's logs

```
Open resource logs://today
→ Displays today's work logs in Markdown format
```

### logs://{date} - Logs for a specific date

```
Open resource logs://2025-11-25
→ Displays logs for the specified date in Markdown format
```

## MCP Prompts - Daily Report Template

Select `daily-report` from Claude's prompt menu to automatically generate a daily business report based on today's logs.

**Prompt Content:**
- Highlights of the day
- Details by category
- Issues and solutions
- Plan for tomorrow

## Automatic Logging (Claude Code Hooks)

Using Claude Code's Hooks feature, you can automatically record logs when work is completed.

### Configuration

Add the following to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Please record the work done in this conversation using the worklog MCP add_log tool. Select a category such as 'Development', 'Research', 'Review', 'Config' based on the work content, and add relevant tags."
          }
        ]
      }
    ]
  }
}
```

### Behavior

1. When work in Claude Code is completed, the Stop hook is triggered.
2. Claude automatically calls the `add_log` tool to record the work content.
3. Category and tags are automatically assigned.

### Customization Examples

#### Log after using specific tools

To automatically record after using Edit/Write tools:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "I edited a file. Please record this change using worklog MCP add_log."
          }
        ]
      }
    ]
  }
}
```

#### Log after commit

To automatically record after a Git commit:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "If git commit was executed, record the commit message using worklog MCP add_log. If not git commit, do nothing."
          }
        ]
      }
    ]
  }
}
```

### Notes

- Hooks are available in Claude Code v1.0.17 or later.
- Use `type: "prompt"` to give additional instructions to Claude.
- Use `type: "command"` to execute shell commands directly.

## Usage as CLI

You can also operate directly from the command line without using the MCP server.

### Add a log

```bash
# Basic add
worklog-mcp add "Fixed bug in auth system"

# Specify category and tags
worklog-mcp add "Fixed bug in auth system" --category "Development" --tags "Bugfix,Auth"

# Short options
worklog-mcp add "Meeting notes" -c "Meeting" -t "Weekly,Team"
```

### Search logs

```bash
# Keyword search
worklog-mcp search "bug"

# Specify date range
worklog-mcp search "bug" --start 2025-11-01 --end 2025-11-30

# Limit results
worklog-mcp search "bug" --limit 20

# Combine all options
worklog-mcp search "API" --start 2025-11-01 --end 2025-11-30 --limit 10
```

### Check Schema

```bash
worklog-mcp schema
```

## Data Storage Location

Log data is stored in a SQLite database:

```
~/.local/share/worklog-mcp/logs.db
```

### Configure Database Location

You can customize the database location, for example, to share the database between WSL and Windows.

#### Check current configuration

```bash
worklog-mcp config show
```

Example output:
```
worklog-mcp Configuration

Config File:     /home/user/.config/worklog-mcp/config.json
DB Path (current): /home/user/.local/share/worklog-mcp/logs.db
  └─ Using default path

Default DB Path: /home/user/.local/share/worklog-mcp/logs.db
```

#### Change database path

```bash
# To use Windows database from WSL
worklog-mcp config set-db-path /mnt/c/Users/username/worklog.db

# To specify a different location on Windows
worklog-mcp config set-db-path C:\Users\username\Documents\worklog.db
```

#### Reset to default

```bash
worklog-mcp config reset
```

**Notes:**
- Configuration file is saved in the user's home directory (`~/.config/worklog-mcp/config.json`)
- Settings persist even when running with `uvx`
- Specify absolute paths
- If you specify an existing database, it will use that data

### Database Schema

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    category TEXT NOT NULL,
    content TEXT NOT NULL,
    tags TEXT,
    file_path TEXT,
    line_start INTEGER,
    line_end INTEGER,
    git_branch TEXT,
    git_commit TEXT,
    project_path TEXT
);
```

## Troubleshooting

### MCP Server not recognized

1. Check if `worklog-mcp-server` command is in your PATH:
   ```bash
   which worklog-mcp-server
   ```

2. Restart Claude Code/Desktop.

3. Check JSON syntax in settings file.

### Commands installed by uv not found

Check uv tool path and add to PATH if necessary:

```bash
# Check path
uv tool dir

# Add to .bashrc or .zshrc
export PATH="$HOME/.local/bin:$PATH"
```

## Uninstall and Cleanup

### Uninstall

```bash
# If installed with uv tool
uv tool uninstall worklog-mcp

# If installed with pip
pip uninstall worklog-mcp
```

### Data and Configuration Cleanup

After uninstalling, the following files will remain. Delete them if needed.

#### Database Files

```bash
# Linux/macOS
rm -rf ~/.local/share/worklog-mcp/

# Windows
rmdir /s "%LOCALAPPDATA%\mcp-tools\worklog-mcp"
```

#### Configuration Files

```bash
# Linux/macOS
rm -rf ~/.config/worklog-mcp/

# Windows
rmdir /s "%LOCALAPPDATA%\worklog-mcp"
```

#### Remove from MCP Configuration

Remove the `worklog` server configuration from Claude Code, Claude Desktop, or Gemini CLI settings.

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
