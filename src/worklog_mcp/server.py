"""MCP Server for worklog-mcp."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from platformdirs import user_data_dir

# --- 設定 ---
APP_NAME = "worklog-mcp"
DB_DIR = Path(user_data_dir(APP_NAME, "mcp-tools"))
DB_PATH = DB_DIR / "logs.db"

# MCPサーバー初期化
mcp = FastMCP("worklog-mcp")


def init_db():
    """データベースとテーブルを初期化"""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
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
    """DB接続を取得（必要に応じて初期化）"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def add_log(
    content: str,
    category: str = "General",
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    作業記録をデータベースに追加します。

    Args:
        content: 記録する作業内容の詳細
        category: 作業の分類（例: '開発', '調査', 'ミーティング'）
        tags: 作業に関連するタグのリスト
    """
    timestamp = datetime.now().isoformat(timespec='seconds')
    tags_str = ",".join(tags) if tags else ""

    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO logs (timestamp, category, content, tags) VALUES (?, ?, ?, ?)",
            (timestamp, category, content, tags_str)
        )
        conn.commit()
        return {
            "message": "作業記録を正常に追加しました。",
            "log_id": cursor.lastrowid,
            "timestamp": timestamp,
        }


@mcp.tool()
def search_logs(
    keyword: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    過去の作業記録を検索します。

    Args:
        keyword: 検索キーワード（内容、カテゴリ、タグを検索）
        start_date: 検索開始日（YYYY-MM-DD形式）
        end_date: 検索終了日（YYYY-MM-DD形式）
        limit: 取得するログの最大数
    """
    params: list = []
    where_clauses: list[str] = []

    if keyword:
        where_clauses.append("(content LIKE ? OR category LIKE ? OR tags LIKE ?)")
        params.extend([f"%{keyword}%"] * 3)

    if start_date:
        where_clauses.append("timestamp >= ?")
        params.append(f"{start_date}T00:00:00")
    if end_date:
        where_clauses.append("timestamp <= ?")
        params.append(f"{end_date}T23:59:59")

    where_sql = " AND ".join(where_clauses)
    query = f"SELECT * FROM logs {'WHERE ' + where_sql if where_sql else ''} ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    with get_db_connection() as conn:
        rows = conn.execute(query, params).fetchall()

        logs = []
        for row in rows:
            logs.append({
                "id": row["id"],
                "timestamp": row["timestamp"],
                "category": row["category"],
                "content": row["content"],
                "tags": row["tags"].split(",") if row["tags"] else [],
            })

        return {
            "message": f"検索条件に一致する{len(logs)}件のログが見つかりました。",
            "logs": logs,
        }


@mcp.tool()
def get_recent_logs(limit: int = 5) -> dict[str, Any]:
    """
    最近の作業記録を取得します。

    Args:
        limit: 取得するログの数
    """
    return search_logs(limit=limit)


@mcp.tool()
def get_logs_by_category(category: str, limit: int = 10) -> dict[str, Any]:
    """
    特定カテゴリの作業記録を取得します。

    Args:
        category: カテゴリ名（例: '開発', '調査', '薬局業務'）
        limit: 取得するログの最大数
    """
    return search_logs(keyword=category, limit=limit)


def main():
    """MCPサーバーを起動"""
    mcp.run()


if __name__ == "__main__":
    main()
