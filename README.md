# worklog-mcp

AIアシスタント向けの構造化された作業記録MCPサーバー。作業履歴を記録・検索できます。

## 機能

- **作業記録の追加**: カテゴリやタグ付きで作業内容を記録
- **ログ検索**: キーワード、期間、カテゴリで柔軟に検索
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

## MCPツールの使用例

MCPサーバーを設定後、Claude Code や Claude Desktop から以下のツールが利用できます。

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
~/.local/share/worklog-mcp/mcp-tools/logs.db
```

### データベーススキーマ

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    category TEXT,
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

## ライセンス

MIT License
