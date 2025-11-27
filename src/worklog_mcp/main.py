import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from pydantic import BaseModel, Field

from .config import get_config, APP_NAME

# --- 設定 ---
console = Console()
app = typer.Typer()

# データベースパスは設定から取得
def get_db_path() -> Path:
    """設定ファイルからDBパスを取得"""
    return get_config().get_db_path()

DB_PATH = get_db_path()


# ディレクトリとデータベースの初期化
def init_db():
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT
            )
        """)
        conn.commit()


def get_db_connection():
    init_db()
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


# --- AIが利用するデータ構造定義 ---

class LogEntry(BaseModel):
    id: int = Field(..., description="一意のログID")
    timestamp: str = Field(..., description="ISO形式のタイムスタンプ (例: 2025-11-25T23:30:00)")
    category: str = Field(..., description="ログの分類 (例: 開発, 調査, ミーティング)")
    content: str = Field(..., description="作業内容の詳細")
    tags: List[str] = Field(..., description="関連するタグのリスト")


class AddLogResult(BaseModel):
    message: str = Field(..., description="ログが正常に追加されたことを示すメッセージ")
    log_id: int = Field(..., description="新しく作成されたログの一意のID")


class LogsSearchResult(BaseModel):
    message: str = Field(..., description="検索結果の概要メッセージ")
    logs: List[LogEntry] = Field(..., description="条件に一致したログエントリのリスト")


class LogSearchInput(BaseModel):
    keyword: Optional[str] = Field(None, description="ログの内容、カテゴリ、タグを検索するためのキーワード。")
    start_date: Optional[str] = Field(None, description="検索期間の開始日 (YYYY-MM-DD形式)。")
    end_date: Optional[str] = Field(None, description="検索期間の終了日 (YYYY-MM-DD形式)。")
    limit: int = Field(10, description="取得するログの最大数。")


# --- AIが呼び出す関数（ツール） ---

def add_log(
    content: str,
    category: str = "General",
    tags: Optional[List[str]] = None,
) -> AddLogResult:
    """
    ユーザーの作業記録を構造化された形式でデータベースに追加します。

    Args:
        content: 記録する作業内容の詳細。
        category: 作業の分類。例: '開発', '調査', 'ミーティング'。
        tags: 作業に関連するタグのリスト。
    """
    timestamp = datetime.now().isoformat(timespec='seconds')
    tags_str = ",".join(tags) if tags else ""

    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO logs (timestamp, category, content, tags) VALUES (?, ?, ?, ?)",
            (timestamp, category, content, tags_str)
        )
        conn.commit()
        last_id = cursor.lastrowid
        return AddLogResult(
            message="作業記録を正常に追加しました。",
            log_id=last_id
        )


def search_logs(
    input: LogSearchInput
) -> LogsSearchResult:
    """
    キーワード、期間、またはその両方を使用して過去の作業記録を検索し、関連するログを返します。
    """
    params: List = []
    where_clauses: List[str] = []

    if input.keyword:
        where_clauses.append("(content LIKE ? OR category LIKE ? OR tags LIKE ?)")
        params.extend([f"%{input.keyword}%"] * 3)

    if input.start_date:
        where_clauses.append("timestamp >= ?")
        params.append(f"{input.start_date}T00:00:00")
    if input.end_date:
        where_clauses.append("timestamp <= ?")
        params.append(f"{input.end_date}T23:59:59")

    where_sql = " AND ".join(where_clauses)
    query = f"SELECT * FROM logs {'WHERE ' + where_sql if where_sql else ''} ORDER BY timestamp DESC LIMIT ?"
    params.append(input.limit)

    with get_db_connection() as conn:
        rows = conn.execute(query, params).fetchall()

        logs = []
        for row in rows:
            logs.append(LogEntry(
                id=row['id'],
                timestamp=row['timestamp'],
                category=row['category'],
                content=row['content'],
                tags=row['tags'].split(',') if row['tags'] else [],
            ))

        message = f"検索条件に一致する{len(logs)}件のログが見つかりました。"
        return LogsSearchResult(message=message, logs=logs)


# --- CLIコマンド（手動実行用） ---

@app.command(name="search")
def cli_search_logs(
    keyword: Optional[str] = typer.Argument(None, help="検索キーワード (Search keyword). ログの内容、カテゴリ、タグから検索します。"),
    start: Optional[str] = typer.Option(None, "--start", "-s", help="検索開始日 (Start Date). YYYY-MM-DD形式 (例: 2025-11-01)。"),
    end: Optional[str] = typer.Option(None, "--end", "-e", help="検索終了日 (End Date). YYYY-MM-DD形式 (例: 2025-11-30)。"),
    limit: int = typer.Option(10, "--limit", "-l", help="表示件数 (Limit). デフォルトは10件です。"),
):
    """
    作業ログを検索し、テーブル表示します (Search work logs).
    
    キーワード、期間、またはその両方を使用して過去の作業記録を検索します。
    """
    search_input = LogSearchInput(keyword=keyword, start_date=start, end_date=end, limit=limit)
    result = search_logs(search_input)

    console.print(f"[bold blue]Search Result:[/bold blue] {result.message}")
    if not result.logs:
        return

    table = Table(title="Work Log Entries", style="dim", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", width=5)
    table.add_column("Timestamp", style="dim")
    table.add_column("Category", style="green")
    table.add_column("Content", style="white")
    table.add_column("Tags", style="yellow")

    for log in result.logs:
        table.add_row(
            str(log.id),
            log.timestamp.split('T')[0] + " " + log.timestamp.split('T')[1],
            log.category,
            log.content[:60] + "..." if len(log.content) > 60 else log.content,
            ", ".join(log.tags)
        )
    console.print(table)


@app.command(name="add")
def cli_add_log(
    content: str = typer.Argument(..., help="作業内容 (Content). 記録する作業の詳細。"),
    category: str = typer.Option("General", "--category", "-c", help="カテゴリ (Category). 作業の分類 (例: 開発, 調査)。"),
    tags: Optional[str] = typer.Option(None, "--tags", "-t", help="タグ (Tags). カンマ区切りのタグ (例: バグ修正,認証)。"),
):
    """
    作業ログを追加します (Add a work log).
    
    作業内容、カテゴリ、タグを指定してログを記録します。
    """
    tags_list = [t.strip() for t in tags.split(",")] if tags else None
    result = add_log(content=content, category=category, tags=tags_list)
    console.print(f"[bold green]{result.message}[/bold green] (ID: {result.log_id})")


@app.command(name="schema")
def print_schema():
    """
    MCPサーバー用のJSONスキーマを出力します (Print MCP JSON Schema).

    AIエージェント設定用のツール定義を出力します。
    """
    # add_log用のスキーマを手動で定義
    add_log_params_schema = {
        "type": "object",
        "properties": {
            "content": {
                "type": "string",
                "description": "記録する作業内容の詳細。"
            },
            "category": {
                "type": "string",
                "description": "作業の分類。例: '開発', '調査', 'ミーティング'。",
                "default": "General"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "作業に関連するタグのリスト。"
            }
        },
        "required": ["content"]
    }

    schema_output = {
        "name": APP_NAME,
        "description": "作業履歴を正確に記録・検索するためのツールです。日報作成や過去の解決策の検索に役立ちます。",
        "functions": [
            {
                "name": "add_log",
                "description": "ユーザーの作業記録や調べた内容を、カテゴリとタグ付きでデータベースに記録します。AIはこれを呼び出すことで、ユーザーの作業の記録を永続化し、日報作成の土台を作ります。",
                "parameters": add_log_params_schema,
                "returns": AddLogResult.model_json_schema(),
            },
            {
                "name": "search_logs",
                "description": "キーワード、期間、またはその両方を使用して過去の作業記録を検索し、関連するログを取得します。AIが過去の文脈を思い出す際に使用します。",
                "parameters": LogSearchInput.model_json_schema(),
                "returns": LogsSearchResult.model_json_schema(),
            },
        ]
    }
    console.print_json(json.dumps(schema_output, indent=2, ensure_ascii=False))


# --- Config コマンド ---

config_app = typer.Typer(help="設定管理コマンド (Configuration commands)")
app.add_typer(config_app, name="config")


@config_app.command(name="show")
def config_show():
    """
    現在の設定を表示します (Show current configuration).

    データベースパスや設定ファイルの場所を確認できます。
    """
    config = get_config()
    settings = config.get_all()

    console.print("\n[bold cyan]worklog-mcp Configuration[/bold cyan]\n")
    console.print(f"[yellow]Config File:[/yellow]     {settings['config_file']}")
    console.print(f"[yellow]DB Path (current):[/yellow] {settings['db_path']}")

    if settings['db_path_custom']:
        console.print(f"[green]  └─ Custom path set[/green]")
    else:
        console.print(f"[dim]  └─ Using default path[/dim]")

    console.print(f"\n[dim]Default DB Path: {settings['db_path_default']}[/dim]\n")


@config_app.command(name="set-db-path")
def config_set_db_path(
    path: str = typer.Argument(..., help="データベースファイルのパス (Database file path)"),
):
    """
    データベースの保存先を変更します (Set custom database path).

    WSLとWindows間でデータベースを共有する場合などに使用します。
    例: worklog-mcp config set-db-path /mnt/c/Users/username/worklog.db
    """
    try:
        config = get_config()
        config.set_db_path(path)
        abs_path = Path(path).expanduser().resolve()
        console.print(f"[bold green]✓[/bold green] データベースパスを設定しました: {abs_path}")

        # データベースの親ディレクトリを作成
        abs_path.parent.mkdir(parents=True, exist_ok=True)

        # データベースを初期化（既存のファイルがある場合はスキップ）
        if not abs_path.exists():
            console.print(f"[dim]  └─ 新しいデータベースを作成します...[/dim]")
        else:
            console.print(f"[dim]  └─ 既存のデータベースを使用します[/dim]")

    except Exception as e:
        console.print(f"[bold red]✗[/bold red] エラー: {e}")
        raise typer.Exit(1)


@config_app.command(name="reset")
def config_reset():
    """
    データベースパスをデフォルトに戻します (Reset to default database path).

    カスタム設定を削除し、OS標準の保存場所を使用します。
    """
    config = get_config()
    config.reset_db_path()
    default_path = config.get_db_path()
    console.print(f"[bold green]✓[/bold green] データベースパスをデフォルトに戻しました: {default_path}")


if __name__ == "__main__":
    app()
