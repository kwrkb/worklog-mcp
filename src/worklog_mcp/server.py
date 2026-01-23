"""Simple Markdown-based MCP Server for worklog-mcp."""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

# MCPサーバー初期化
mcp = FastMCP("worklog-mcp")


# Google Drive検出（OS別）
def _detect_macos_google_drive() -> Path | None:
    """MacでGoogle Driveを検出"""
    cloud_storage = Path.home() / "Library" / "CloudStorage"
    if not cloud_storage.exists():
        return None

    # GoogleDrive-*（アカウント名付き）を検索
    for item in cloud_storage.iterdir():
        if item.is_dir() and item.name.startswith("GoogleDrive-"):
            # 英語: "My Drive", 日本語: "マイドライブ"
            for drive_name in ["My Drive", "マイドライブ"]:
                my_drive = item / drive_name
                if my_drive.exists():
                    return my_drive
    return None


def _detect_windows_google_drive() -> Path | None:
    """WindowsでGoogle Driveを検出"""
    # 1. ホームディレクトリ配下を最優先
    home_gdrive = Path.home() / "Google Drive"
    if home_gdrive.exists():
        return home_gdrive

    # 2. 全ドライブレター（D:〜Z:）をスキャン
    # 英語: "My Drive", 日本語: "マイドライブ"
    drive_names = ["My Drive", "マイドライブ"]
    for letter in "DEFGHIJKLMNOPQRSTUVWXYZ":
        for drive_name in drive_names:
            path = Path(f"{letter}:/{drive_name}")
            if path.exists():
                return path

    return None


def _detect_linux_google_drive() -> Path | None:
    """Linux/WSLでGoogle Driveを検出"""
    # WSL: /mnt/c/Users/<user>/Google Drive
    # 英語: "Google Drive", 日本語: "Google ドライブ"
    gdrive_names = ["Google Drive", "Google ドライブ"]

    mnt_c = Path("/mnt/c/Users")
    if mnt_c.exists():
        for user_dir in mnt_c.iterdir():
            if user_dir.is_dir():
                for gdrive_name in gdrive_names:
                    gdrive = user_dir / gdrive_name
                    if gdrive.exists():
                        return gdrive
    return None


def detect_google_drive_path() -> Path | None:
    """OS別にGoogle Driveを自動検出"""
    import sys

    if sys.platform == "darwin":
        return _detect_macos_google_drive()
    elif sys.platform == "win32":
        return _detect_windows_google_drive()
    else:  # linux, WSL
        return _detect_linux_google_drive()

# ログディレクトリの取得（環境変数またはデフォルト）
def get_worklog_dir() -> Path:
    """ログディレクトリを取得

    優先順位:
    1. WORKLOG_DIR 環境変数（直接パス指定）
    2. WORKLOG_STORAGE 環境変数に基づく選択
       - "local": ~/.worklogs/
       - "googledrive": Google Drive/worklogs/（見つからなければローカル）
       - "auto"（デフォルト）: Google Drive検出、なければローカル
    """
    # 1. WORKLOG_DIR が設定されていれば最優先
    custom_dir = os.environ.get("WORKLOG_DIR")
    if custom_dir:
        return Path(custom_dir).expanduser()

    # 2. WORKLOG_STORAGE に基づく選択
    storage = os.environ.get("WORKLOG_STORAGE", "auto").lower()

    if storage == "local":
        return Path.home() / ".worklogs"

    # googledrive または auto: Google Driveを検出
    gdrive = detect_google_drive_path()

    if storage == "googledrive":
        if gdrive:
            return gdrive / "worklogs"
        # Google Drive未インストール時はローカルにフォールバック
        return Path.home() / ".worklogs"

    # auto: Google Driveがあればそちら、なければローカル
    if gdrive:
        return gdrive / "worklogs"
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
