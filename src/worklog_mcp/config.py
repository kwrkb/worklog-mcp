"""設定ファイル管理モジュール"""

import json
from pathlib import Path
from typing import Optional

from platformdirs import user_config_dir, user_data_dir

APP_NAME = "worklog-mcp"

# デフォルトの設定ディレクトリとファイルパス
CONFIG_DIR = Path(user_config_dir(APP_NAME, "mcp-tools"))
CONFIG_FILE = CONFIG_DIR / "config.json"

# デフォルトのデータベースパス
DEFAULT_DB_DIR = Path(user_data_dir(APP_NAME, "mcp-tools"))
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "logs.db"


class Config:
    """設定管理クラス"""

    def __init__(self):
        self.config_data = self._load_config()

    def _load_config(self) -> dict:
        """設定ファイルを読み込む"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # 設定ファイルが壊れている場合はデフォルト設定を返す
                return {}
        return {}

    def _save_config(self):
        """設定ファイルに保存"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config_data, f, indent=2, ensure_ascii=False)

    def get_db_path(self) -> Path:
        """データベースパスを取得"""
        custom_path = self.config_data.get('db_path')
        if custom_path:
            return Path(custom_path)
        return DEFAULT_DB_PATH

    def set_db_path(self, path: str):
        """データベースパスを設定"""
        # パスを絶対パスに変換
        abs_path = Path(path).expanduser().resolve()
        self.config_data['db_path'] = str(abs_path)
        self._save_config()

    def reset_db_path(self):
        """データベースパスをデフォルトに戻す"""
        if 'db_path' in self.config_data:
            del self.config_data['db_path']
            self._save_config()

    def get_all(self) -> dict:
        """全設定を取得"""
        return {
            'config_file': str(CONFIG_FILE),
            'db_path': str(self.get_db_path()),
            'db_path_custom': self.config_data.get('db_path'),
            'db_path_default': str(DEFAULT_DB_PATH),
        }


def get_config() -> Config:
    """設定インスタンスを取得"""
    return Config()
