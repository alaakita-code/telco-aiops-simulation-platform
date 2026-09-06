"""
數據提取器
從多個來源提取電信/網路數據
"""
import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from loguru import logger


class DataExtractor:
    """數據提取器"""

    def __init__(self, db_path: str = "data/processed/telco_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"數據提取器初始化：{self.db_path}")

    def extract_from_csv(self, file_path: str) -> pd.DataFrame:
        """從 CSV 提取數據"""
        logger.info(f"從 CSV 提取：{file_path}")
        return pd.read_csv(file_path)

    def extract_from_sqlite(self, table_name: str) -> pd.DataFrame:
        """從 SQLite 提取數據"""
        if not self.db_path.exists():
            logger.warning(f"SQLite 資料庫不存在：{self.db_path}")
            return pd.DataFrame()

        with sqlite3.connect(str(self.db_path)) as conn:
            table_exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            ).fetchone()

            if not table_exists:
                logger.warning(f"SQLite 資料表不存在：{table_name}")
                return pd.DataFrame()

            df = pd.read_sql_query(f'SELECT * FROM "{table_name}"', conn)

        logger.info(f"從 SQLite 提取 {len(df)} 筆數據：{table_name}")
        return df

    def extract_speedtest_history(self) -> pd.DataFrame:
        """提取 Speedtest 歷史記錄"""
        df = self.extract_from_sqlite("speedtest_results")

        if df.empty:
            logger.warning("Speedtest 歷史數據不存在")
            return df

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        return df

    def extract_all(self) -> dict:
        """提取所有可用數據"""
        data = {}

        # 提取 Speedtest 歷史
        data["speedtest"] = self.extract_speedtest_history()

        # 提取基地台數據（若有）
        try:
            data["cell_towers"] = self.extract_from_sqlite("cell_towers")
        except:
            data["cell_towers"] = pd.DataFrame()

        logger.info(f"數據提取完成：{list(data.keys())}")
        return data
