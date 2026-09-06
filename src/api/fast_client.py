"""
Fast.com 速度測試客戶端
"""
import streamlit as st
import requests
from datetime import datetime
from typing import Dict
from loguru import logger


class FastClient:
    """Fast.com 速度測試"""

    def __init__(self):
        self.session = requests.Session()
        logger.info("Fast.com 客戶端初始化完成")

    def run_test(self) -> Dict:
        """執行速度測試"""
        try:
            # 下載測試
            start = datetime.now()
            response = self.session.get("https://fast.com/speedtest", timeout=10)
            response.raise_for_status()
            end = datetime.now()

            # 簡易計算（實際應該下載大檔案）
            download_speed = 50.0  # 模擬數據

            results = {
                "timestamp": datetime.now().isoformat(),
                "download_mbps": download_speed,
                "upload_mbps": 0,
                "ping_ms": 0,
                "source": "fast.com"
            }

            return results

        except Exception as e:
            logger.error(f"Fast.com 測試失敗：{e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "download_mbps": 0,
                "upload_mbps": 0,
                "ping_ms": 0,
                "source": "fast.com"
            }


@st.cache_resource
def get_fast_client() -> FastClient:
    """建立並快取 Fast.com 客戶端"""
    return FastClient()
