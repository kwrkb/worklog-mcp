"""Simple Markdown-based MCP Server for worklog-mcp."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# MCPサーバー初期化
mcp = FastMCP("worklog-mcp")


def get_worklog_dir() -> Path:
    """ログディレクトリを取得

    WORKLOG_DIR環境変数が設定されていればそれを使用、
    なければ ~/.worklogs/ を使用。
    """
    custom_dir = os.environ.get("WORKLOG_DIR")
    if custom_dir:
        return Path(custom_dir).expanduser()
    return Path.home() / ".worklogs"


def ensure_worklog_dir() -> Path:
    """ログディレクトリを確保（存在しない場合は作成）"""
    worklog_dir = get_worklog_dir()
    worklog_dir.mkdir(parents=True, exist_ok=True)
    return worklog_dir


@mcp.tool()
def save_worklog(
    content: str,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """
    作業ログ、思考の断片、エラー解決策を保存します。

    データは月単位のMarkdownファイル（~/.worklogs/YYYY-MM.md）に追記されます。

    Args:
        content: ログの内容。作業メモ、解決策、思考の断片など。
        tags: 関連タグのリスト（任意）。検索時に役立ちます。

    Returns:
        保存成功メッセージとファイルパスを含む辞書
    """
    # 現在の日時を取得
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # 月単位のファイル名（YYYY-MM.md）
    worklog_dir = ensure_worklog_dir()
    filename = now.strftime("%Y-%m.md")
    filepath = worklog_dir / filename

    # エントリの作成
    entry_lines = [f"### {timestamp}"]

    # タグがあれば追加
    if tags:
        tags_str = " ".join(f"#{tag}" for tag in tags)
        entry_lines.append(f"Tags: {tags_str}")

    entry_lines.append("")
    entry_lines.append(content)
    entry_lines.append("")  # 空行で区切り

    entry = "\n".join(entry_lines)

    # ファイルに追記
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

    return {
        "message": "ログを保存しました。",
        "filepath": str(filepath),
        "timestamp": timestamp,
    }


@mcp.tool()
def search_worklogs(query: str) -> dict[str, Any]:
    """
    過去のMarkdownログファイルを全走査し、キーワードに関連するエントリを抽出します。

    シンプルなテキストマッチング（grep的な挙動）で該当箇所と、
    その周辺行（コンテキスト）を抽出して返します。

    Args:
        query: 検索キーワード（正規表現ではなく、プレーンテキスト）

    Returns:
        検索結果を含む辞書（マッチしたエントリのリスト）
    """
    worklog_dir = get_worklog_dir()

    if not worklog_dir.exists():
        return {
            "message": "ログディレクトリが見つかりません。",
            "matches": [],
        }

    # .mdファイルを全て取得（新しい順）
    md_files = sorted(worklog_dir.glob("*.md"), reverse=True)

    if not md_files:
        return {
            "message": "ログファイルが見つかりません。",
            "matches": [],
        }

    matches = []
    query_lower = query.lower()

    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()

        # エントリごとに分割（### で始まる行で区切る）
        entries = re.split(r'\n(?=### \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', content)

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            # 大文字小文字を無視して検索
            if query_lower in entry.lower():
                # タイムスタンプを抽出
                timestamp_match = re.match(r'### (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', entry)
                timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"

                matches.append({
                    "file": md_file.name,
                    "timestamp": timestamp,
                    "content": entry,
                })

    return {
        "message": f"{len(matches)}件のマッチが見つかりました。",
        "matches": matches,
    }


def main():
    """MCPサーバーを起動"""
    mcp.run()


if __name__ == "__main__":
    main()
