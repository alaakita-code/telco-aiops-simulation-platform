"""
數據載入器
將處理後的數據載入資料庫
"""
import pandas as pd
import sqlite3
from pathlib import Path
from loguru import logger


class DataLoader:
    """數據載入器"""

    def __init__(self, db_path: str = "data/processed/telco_data.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"數據載入器初始化：{self.db_path}")

    def load_to_sqlite(self, df: pd.DataFrame, table_name: str, if_exists: str = "replace"):
        """
        載入數據到 SQLite

        Args:
            df: DataFrame
            table_name: 資料表名稱
            if_exists: 'fail', 'replace', 'append'
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(str(self.db_path)) as conn:
            df.to_sql(table_name, conn, if_exists=if_exists, index=False)

        logger.info(f"載入 {len(df)} 筆數據到 {table_name}")

    def load_cell_towers(self, df: pd.DataFrame):
        """載入基地台數據"""
        self.load_to_sqlite(df, "cell_towers", if_exists="replace")

    def load_speedtest_results(self, df: pd.DataFrame, if_exists: str = "replace"):
        """載入 Speedtest 結果"""
        self.load_to_sqlite(df, "speedtest_results", if_exists=if_exists)
