"""
OpenCellID API 客戶端
取得全球基地台開放數據
"""
import requests
import streamlit as st
import pandas as pd
import os
from typing import List, Dict, Optional, Tuple
from loguru import logger


class OpenCellIDClient:
    """OpenCellID API 客戶端"""

    BASE_URL = "https://opencellid.org/cell"

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OPENCELLID_API_KEY 不可為空")

        self.api_key = api_key
        self.session = requests.Session()
        self.session.params = {"key": api_key}
        logger.info("OpenCellID 客戶端初始化完成")

    def get_cells_in_bbox(self, bbox: Tuple[float, float, float, float]) -> pd.DataFrame:
        """
        取得指定區域內的基地台

        Args:
            bbox: (min_lon, min_lat, max_lon, max_lat)

        Returns:
            DataFrame 包含基地台數據
        """
        min_lon, min_lat, max_lon, max_lat = bbox
        url = f"{self.BASE_URL}/getInArea"
        params = {
            "BBOX": f"{min_lon},{min_lat},{max_lon},{max_lat}",
            "format": "json"
        }

        try:
            logger.debug(f"查詢區域：{bbox}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "cells" not in data or not data["cells"]:
                logger.warning("無基地台數據")
                return pd.DataFrame()

            df = pd.DataFrame(data["cells"])
            logger.info(f"取得 {len(df)} 筆基地台數據")
            return df

        except Exception as e:
            logger.error(f"API 請求失敗：{e}")
            return pd.DataFrame()

    def get_cells_by_operator(self, mcc: int = 466, mnc: int = 92) -> pd.DataFrame:
        """
        取得特定電信業者的基地台

        Args:
            mcc: Mobile Country Code (台灣: 466)
            mnc: Mobile Network Code
                - 中華電信：92, 93, 97
                - 台灣大哥大：97, 99
                - 遠傳電信：1, 2, 5, 11, 12

        Returns:
            DataFrame 包含基地台數據
        """
        url = f"{self.BASE_URL}/getInArea"
        params = {
            "MCC": mcc,
            "MNC": mnc,
            "format": "json"
        }

        try:
            logger.info(f"查詢電信業者：MCC={mcc}, MNC={mnc}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "cells" not in data or not data["cells"]:
                logger.warning(f"無基地台數據 (MCC={mcc}, MNC={mnc})")
                return pd.DataFrame()

            df = pd.DataFrame(data["cells"])
            logger.info(f"取得 {len(df)} 筆基地台數據")
            return df

        except Exception as e:
            logger.error(f"API 請求失敗：{e}")
            return pd.DataFrame()

    def search_cell(self, cell_id: int) -> Optional[Dict]:
        """
        根據 Cell ID 查詢詳細資訊

        Args:
            cell_id: 基地台 ID

        Returns:
            基地台詳細資訊
        """
        url = f"{self.BASE_URL}/get"
        params = {"cellId": cell_id, "format": "json"}

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("cell")
        except Exception as e:
            logger.error(f"查詢失敗：{e}")
            return None


@st.cache_resource
def get_opencellid_client() -> Optional[OpenCellIDClient]:
    """從 secrets 取得 API Key 並建立客戶端"""
    try:
        api_key = st.secrets.get("OPENCELLID_API_KEY") or os.getenv("OPENCELLID_API_KEY")
        if not api_key:
            st.warning("尚未設定 OPENCELLID_API_KEY，將略過 OpenCellID API。")
            return None
        return OpenCellIDClient(api_key)
    except Exception as e:
        st.error(f"OpenCellID 客戶端初始化失敗：{e}")
        return None
