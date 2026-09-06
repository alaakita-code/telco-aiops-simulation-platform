"""
Speedtest 網路速度測試客戶端
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False
    logger.warning("speedtest-cli 未安裝")


class SpeedtestClient:
    """Speedtest 客戶端"""

    def __init__(self):
        if not SPEEDTEST_AVAILABLE:
            logger.error("speedtest-cli 未安裝")
            self.st = None
        else:
            try:
                self.st = speedtest.Speedtest()
                logger.info("Speedtest 客戶端初始化完成")
            except Exception as e:
                logger.error(f"Speedtest 初始化失敗：{e}")
                self.st = None

    def is_available(self) -> bool:
        """檢查 Speedtest 是否可用"""
        return self.st is not None

    def get_best_server(self) -> Optional[Dict]:
        """取得最佳測試伺服器"""
        if not self.st:
            return None
        try:
            self.st.get_best_server()
            return self.st.best
        except Exception as e:
            logger.error(f"取得伺服器失敗：{e}")
            return None

    def run_test(self) -> Dict:
        """執行完整速度測試"""
        if not self.st:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": "Speedtest 不可用",
                "download_mbps": 0,
                "upload_mbps": 0,
                "ping_ms": 0
            }

        try:
            logger.info("開始速度測試...")

            # 下載測試
            download = self.st.download()
            logger.info(f"下載速度：{download / 1_000_000:.2f} Mbps")

            # 上傳測試
            upload = self.st.upload()
            logger.info(f"上傳速度：{upload / 1_000_000:.2f} Mbps")

            # Ping 測試
            ping = self.st.results.ping

            results = {
                "timestamp": datetime.now().isoformat(),
                "download_mbps": download / 1_000_000,
                "upload_mbps": upload / 1_000_000,
                "ping_ms": ping,
                "server_name": self.st.best.get("name", "Unknown"),
                "server_country": self.st.best.get("country", "Unknown"),
            }

            logger.info(f"測試完成：{results}")
            return results

        except Exception as e:
            logger.error(f"速度測試失敗：{e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "download_mbps": 0,
                "upload_mbps": 0,
                "ping_ms": 0
            }

    def save_results(self, results: Dict, db_path: str = "data/processed/telco_data.db"):
        """儲存測試結果到資料庫"""
        import sqlite3

        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame([results])

        with sqlite3.connect(str(db_path)) as conn:
            df.to_sql("speedtest_results", conn, if_exists="append", index=False)

        logger.info(f"結果已儲存至 {db_path}")


@st.cache_resource
def get_speedtest_client() -> SpeedtestClient:
    """建立並快取 Speedtest 客戶端"""
    return SpeedtestClient()
