"""
數據轉換器
清洗、轉換、特徵工程
"""
import pandas as pd
import numpy as np
from typing import Optional
from loguru import logger


class DataTransformer:
    """數據轉換器"""

    def __init__(self):
        logger.info("數據轉換器初始化")

    def clean_cell_tower_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗基地台數據

        Args:
            df: 原始數據

        Returns:
            清洗後數據
        """
        if df.empty:
            return df

        logger.info(f"清洗基地台數據：{len(df)} 筆")

        # 移除重複
        if "cellId" in df.columns:
            df = df.drop_duplicates(subset=["cellId"])
        else:
            df = df.drop_duplicates()

        # 移除缺失座標
        df = df.dropna(subset=["lat", "lon"])

        # 轉換數據類型
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
        df = df.dropna(subset=["lat", "lon"])

        for column in ("cellId", "MCC", "MNC"):
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

        # 加入模擬業者名稱，避免展示資料誤認為真實電信商營運資料。
        mnc_mapping = {
            92: "模擬業者 A",
            93: "模擬業者 A",
            97: "模擬業者 A",
            99: "模擬業者 B",
            1: "模擬業者 C",
            2: "模擬業者 C",
            5: "模擬業者 C",
            11: "模擬業者 C",
            12: "模擬業者 C",
        }
        if "MNC" in df.columns:
            df["operator"] = df["MNC"].map(mnc_mapping).fillna("模擬業者其他")
        elif "operator" in df.columns:
            labels = ["模擬業者 A", "模擬業者 B", "模擬業者 C"]
            raw_operators = df["operator"].fillna("未標示").astype(str)
            unique_operators = [
                value for value in raw_operators.drop_duplicates().tolist()
                if value and value != "未標示"
            ]
            anonymized_mapping = {
                value: labels[index] if index < len(labels) else "模擬業者其他"
                for index, value in enumerate(unique_operators)
            }
            df["operator"] = raw_operators.map(anonymized_mapping).fillna("未標示")
        elif "operator" not in df.columns:
            df["operator"] = "未標示"

        logger.info(f"清洗完成：{len(df)} 筆")
        return df

    def clean_speedtest_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清洗 Speedtest 數據

        Args:
            df: 原始數據

        Returns:
            清洗後數據
        """
        if df.empty:
            return df

        logger.info(f"清洗 Speedtest 數據：{len(df)} 筆")

        # 轉換時間戳
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        # 移除異常值
        df["download_mbps"] = pd.to_numeric(df["download_mbps"], errors="coerce")
        df["upload_mbps"] = pd.to_numeric(df["upload_mbps"], errors="coerce")
        if "ping_ms" in df.columns:
            df["ping_ms"] = pd.to_numeric(df["ping_ms"], errors="coerce")

        df = df.dropna(subset=["timestamp", "download_mbps", "upload_mbps"])
        df = df[df["download_mbps"] > 0]
        df = df[df["upload_mbps"] > 0]

        # 加入時間特徵
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.day_name()
        df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"])

        logger.info(f"清洗完成：{len(df)} 筆")
        return df

    def add_geohash(self, df: pd.DataFrame, precision: int = 6) -> pd.DataFrame:
        """
        加入 GeoHash 欄位（用於空間聚合）

        Args:
            df: 包含 lat, lon 的 DataFrame
            precision: GeoHash 精度

        Returns:
            加入 geohash 欄位的 DataFrame
        """
        try:
            import pygeohash as gh
            df["geohash"] = df.apply(
                lambda row: gh.encode(row["lat"], row["lon"], precision),
                axis=1
            )
        except ImportError:
            logger.warning("pygeohash 未安裝，跳過 GeoHash 計算")
            df["geohash"] = None

        return df
