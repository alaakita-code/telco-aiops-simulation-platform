"""
異常偵測模組
偵測網路速度異常、基地台異常
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from loguru import logger


class AnomalyDetector:
    """異常偵測器"""

    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        logger.info(f"異常偵測器初始化 (contamination={contamination})")

    def detect_speedtest_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        偵測 Speedtest 異常

        Args:
            df: 包含 download_mbps, upload_mbps 的 DataFrame

        Returns:
            加入 is_anomaly 欄位的 DataFrame
        """
        if df.empty:
            return df

        features = ["download_mbps", "upload_mbps"]
        missing = [feature for feature in features if feature not in df.columns]
        if missing:
            logger.warning(f"缺少異常偵測欄位：{missing}")
            df["is_anomaly"] = 0
            df["anomaly_score"] = 0.0
            return df

        df = df.copy()
        for feature in features:
            df[feature] = pd.to_numeric(df[feature], errors="coerce")

        valid_df = df.dropna(subset=features)
        if len(valid_df) < 2:
            logger.warning("數據不足，跳過 Speedtest 異常偵測")
            df["is_anomaly"] = 0
            df["anomaly_score"] = 0.0
            return df

        contamination = min(self.contamination, max(1 / len(valid_df), 0.001))
        model = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        X = valid_df[features].values

        # 訓練模型
        model.fit(X)

        # 預測異常
        predictions = model.predict(X)

        # -1 表示異常，1 表示正常
        df["is_anomaly"] = 0
        df["anomaly_score"] = 0.0
        df.loc[valid_df.index, "is_anomaly"] = (predictions == -1).astype(int)
        df.loc[valid_df.index, "anomaly_score"] = -model.score_samples(X)

        anomaly_count = df["is_anomaly"].sum()
        logger.info(f"偵測到 {anomaly_count} 筆異常 ({anomaly_count/len(df)*100:.1f}%)")

        return df

    def detect_network_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        偵測網路掃描異常

        Args:
            df: 包含 ping_ms 的 DataFrame

        Returns:
            加入 is_anomaly 欄位的 DataFrame
        """
        if df.empty or "ping_ms" not in df.columns:
            return df

        df_clean = df.dropna(subset=["ping_ms"])

        if len(df_clean) < 10:
            logger.warning("數據不足，跳過異常偵測")
            df["is_anomaly"] = 0
            return df

        df = df.copy()
        df_clean = df_clean.copy()
        df_clean["ping_ms"] = pd.to_numeric(df_clean["ping_ms"], errors="coerce")
        df_clean = df_clean.dropna(subset=["ping_ms"])

        X = df_clean[["ping_ms"]].values

        contamination = min(self.contamination, max(1 / len(df_clean), 0.001))
        model = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        model.fit(X)
        predictions = model.predict(X)

        df.loc[df_clean.index, "is_anomaly"] = (predictions == -1).astype(int)
        df["is_anomaly"] = df["is_anomaly"].fillna(0).astype(int)

        return df

    def get_anomaly_summary(self, df: pd.DataFrame) -> dict:
        """
        取得異常統計摘要

        Returns:
            異常統計字典
        """
        if "is_anomaly" not in df.columns:
            return {"error": "無 is_anomaly 欄位"}

        total = len(df)
        anomalies = df["is_anomaly"].sum()

        return {
            "total_records": total,
            "anomalies": int(anomalies),
            "anomaly_rate": float(anomalies / total * 100) if total > 0 else 0,
            "normal_records": int(total - anomalies)
        }
