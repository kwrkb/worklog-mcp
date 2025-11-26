"""MCP Server for worklog-mcp."""

import sqlite3
from datetime import datetime, timedelta
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
        category: カテゴリ名（例: '開発', '調査', 'ミーティング'）
        limit: 取得するログの最大数
    """
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM logs WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
            (category, limit)
        ).fetchall()

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
            "message": f"カテゴリ「{category}」の{len(logs)}件のログが見つかりました。",
            "logs": logs,
        }


@mcp.tool()
def update_log(
    log_id: int,
    content: str | None = None,
    category: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    既存の作業記録を更新します。

    Args:
        log_id: 更新するログのID
        content: 新しい作業内容（省略時は変更なし）
        category: 新しいカテゴリ（省略時は変更なし）
        tags: 新しいタグのリスト（省略時は変更なし）
    """
    with get_db_connection() as conn:
        # 既存のログを取得
        row = conn.execute("SELECT * FROM logs WHERE id = ?", (log_id,)).fetchone()
        if not row:
            return {"message": f"ID {log_id} のログが見つかりませんでした。", "success": False}

        # 更新前の内容を記録
        old_content = row["content"]
        old_category = row["category"]
        old_tags = row["tags"]

        # 更新するフィールドを決定
        new_content = content if content is not None else old_content
        new_category = category if category is not None else old_category
        new_tags = ",".join(tags) if tags is not None else old_tags

        conn.execute(
            "UPDATE logs SET content = ?, category = ?, tags = ? WHERE id = ?",
            (new_content, new_category, new_tags, log_id)
        )

        # 編集履歴をログとして追加
        timestamp = datetime.now().isoformat(timespec='seconds')
        history_content = f"[編集履歴] ID {log_id} を更新\n変更前: {old_content[:50]}{'...' if len(old_content) > 50 else ''}\n変更後: {new_content[:50]}{'...' if len(new_content) > 50 else ''}"
        conn.execute(
            "INSERT INTO logs (timestamp, category, content, tags) VALUES (?, ?, ?, ?)",
            (timestamp, "システム", history_content, "編集履歴,auto")
        )

        conn.commit()

        return {
            "message": f"ID {log_id} のログを更新しました。",
            "success": True,
            "log_id": log_id,
        }


@mcp.tool()
def delete_log(log_id: int) -> dict[str, Any]:
    """
    作業記録を削除します。

    Args:
        log_id: 削除するログのID
    """
    with get_db_connection() as conn:
        # 存在確認と内容取得
        row = conn.execute("SELECT * FROM logs WHERE id = ?", (log_id,)).fetchone()
        if not row:
            return {"message": f"ID {log_id} のログが見つかりませんでした。", "success": False}

        # 削除前の内容を記録
        old_content = row["content"]
        old_category = row["category"]

        conn.execute("DELETE FROM logs WHERE id = ?", (log_id,))

        # 削除履歴をログとして追加
        timestamp = datetime.now().isoformat(timespec='seconds')
        history_content = f"[削除履歴] ID {log_id} を削除\nカテゴリ: {old_category}\n内容: {old_content[:100]}{'...' if len(old_content) > 100 else ''}"
        conn.execute(
            "INSERT INTO logs (timestamp, category, content, tags) VALUES (?, ?, ?, ?)",
            (timestamp, "システム", history_content, "削除履歴,auto")
        )

        conn.commit()

        return {
            "message": f"ID {log_id} のログを削除しました。",
            "success": True,
            "log_id": log_id,
        }


def get_logs_for_date(date_str: str) -> str:
    """指定日付のログをテキスト形式で取得（内部ヘルパー関数）"""
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM logs WHERE date(timestamp) = ? ORDER BY timestamp",
            (date_str,)
        ).fetchall()

        if not rows:
            return f"# {date_str} のログ\n\nログが見つかりませんでした。"

        lines = [f"# {date_str} のログ\n"]
        for row in rows:
            time = row["timestamp"].split("T")[1] if "T" in row["timestamp"] else ""
            tags_text = f" [{row['tags']}]" if row["tags"] else ""
            lines.append(f"## [{row['category']}] {time}{tags_text}")
            lines.append(f"{row['content']}\n")

        return "\n".join(lines)


def get_logs_for_period(start_date: str, end_date: str) -> str:
    """指定期間のログをテキスト形式で取得（内部ヘルパー関数）"""
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM logs WHERE date(timestamp) >= ? AND date(timestamp) <= ? ORDER BY timestamp",
            (start_date, end_date)
        ).fetchall()

        if not rows:
            return f"# {start_date} 〜 {end_date} のログ\n\nログが見つかりませんでした。"

        lines = [f"# {start_date} 〜 {end_date} のログ\n"]
        current_date = None
        for row in rows:
            log_date = row["timestamp"].split("T")[0]
            if log_date != current_date:
                current_date = log_date
                lines.append(f"\n## {current_date}\n")
            time = row["timestamp"].split("T")[1] if "T" in row["timestamp"] else ""
            tags_text = f" [{row['tags']}]" if row["tags"] else ""
            lines.append(f"### [{row['category']}] {time}{tags_text}")
            lines.append(f"{row['content']}\n")

        return "\n".join(lines)


@mcp.resource("logs://today")
def logs_today() -> str:
    """今日のログを取得"""
    today = datetime.now().date().isoformat()
    return get_logs_for_date(today)


@mcp.resource("logs://{date}")
def logs_by_date(date: str) -> str:
    """指定日付のログを取得（YYYY-MM-DD形式）"""
    return get_logs_for_date(date)


@mcp.prompt()
def daily_report() -> list[dict[str, str]]:
    """今日の作業ログから日報を作成するためのプロンプト"""
    today = datetime.now().date().isoformat()

    return [
        {
            "role": "user",
            "content": f"""logs://today のリソースを参照して、以下の構成で業務日報を作成してください。

【本日のハイライト】
今日の最も重要な成果や進捗を2-3点で簡潔にまとめる

【業務詳細】
カテゴリごとに作業内容を整理：
- 開発: ...
- 調査: ...
- ミーティング: ...
（該当するカテゴリのみ記載）

【課題と解決】
発生した問題とその対応について

【明日の予定】
次に取り組むべきタスク

日付: {today}"""
        }
    ]


@mcp.prompt()
def weekly_report() -> list[dict[str, str]]:
    """今週の作業ログから週報を作成するためのプロンプト"""
    today = datetime.now().date()
    # 今週の月曜日を計算
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    logs_text = get_logs_for_period(start_of_week.isoformat(), end_of_week.isoformat())

    return [
        {
            "role": "user",
            "content": f"""以下の今週のログを参照して、週報を作成してください。

{logs_text}

【週報の構成】

## 今週のハイライト
最も重要な成果や進捗を3-5点で簡潔にまとめる

## カテゴリ別サマリー
各カテゴリの作業をまとめる（該当するもののみ）：
- 開発: ...
- 調査: ...
- レビュー: ...
- ミーティング: ...

## 課題と対応
今週発生した課題とその対応状況

## 来週の予定
来週取り組む予定のタスク

期間: {start_of_week.isoformat()} 〜 {end_of_week.isoformat()}"""
        }
    ]


@mcp.prompt()
def monthly_report() -> list[dict[str, str]]:
    """今月の作業ログから月報を作成するためのプロンプト"""
    today = datetime.now().date()
    # 今月の初日
    start_of_month = today.replace(day=1)
    # 来月の初日を計算して1日引く
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    logs_text = get_logs_for_period(start_of_month.isoformat(), end_of_month.isoformat())

    return [
        {
            "role": "user",
            "content": f"""以下の今月のログを参照して、月報を作成してください。

{logs_text}

【月報の構成】

## 今月のハイライト
最も重要な成果や進捗を5-7点で簡潔にまとめる

## プロジェクト・機能別サマリー
主要なプロジェクトや機能ごとに進捗をまとめる

## カテゴリ別統計
各カテゴリの作業量や傾向を分析

## 課題と学び
今月発生した課題、その対応、得られた学び

## 来月の目標
来月取り組む予定の主要タスクや目標

期間: {start_of_month.isoformat()} 〜 {end_of_month.isoformat()}"""
        }
    ]


def main():
    """MCPサーバーを起動"""
    mcp.run()


if __name__ == "__main__":
    main()
