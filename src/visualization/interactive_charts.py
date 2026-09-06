"""
互動式圖表
Plotly, Altair 圖表
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from loguru import logger


class InteractiveCharts:
    """互動式圖表"""

    @staticmethod
    def create_speedtest_timeline(df: pd.DataFrame) -> go.Figure:
        """
        建立 Speedtest 時間序列圖

        Args:
            df: 包含 timestamp, download_mbps, upload_mbps 的 DataFrame

        Returns:
            Plotly Figure
        """
        if df.empty:
            return go.Figure()
        if not {"timestamp", "download_mbps", "upload_mbps"}.issubset(df.columns):
            logger.warning("缺少 Speedtest 時間序列圖必要欄位")
            return go.Figure()

        df = df.copy()
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["download_mbps"] = pd.to_numeric(df["download_mbps"], errors="coerce")
        df["upload_mbps"] = pd.to_numeric(df["upload_mbps"], errors="coerce")
        df = df.dropna(subset=["timestamp", "download_mbps", "upload_mbps"])
        if df.empty:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["download_mbps"],
            mode="lines+markers",
            name="下載速度",
            line=dict(color="blue", width=2)
        ))

        fig.add_trace(go.Scatter(
            x=df["timestamp"],
            y=df["upload_mbps"],
            mode="lines+markers",
            name="上傳速度",
            line=dict(color="green", width=2)
        ))

        fig.update_layout(
            title="網路速度趨勢",
            xaxis_title="時間",
            yaxis_title="速度 (Mbps)",
            hovermode="x unified",
            height=500
        )

        return fig

    @staticmethod
    def create_speedtest_distribution(df: pd.DataFrame) -> go.Figure:
        """
        建立速度分布盒狀圖

        Args:
            df: 包含 download_mbps, upload_mbps 的 DataFrame

        Returns:
            Plotly Figure
        """
        if df.empty:
            return go.Figure()
        if not {"download_mbps", "upload_mbps"}.issubset(df.columns):
            logger.warning("缺少 Speedtest 分布圖必要欄位")
            return go.Figure()

        df = df.copy()
        df["download_mbps"] = pd.to_numeric(df["download_mbps"], errors="coerce")
        df["upload_mbps"] = pd.to_numeric(df["upload_mbps"], errors="coerce")
        df = df.dropna(subset=["download_mbps", "upload_mbps"])
        if df.empty:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Box(
            y=df["download_mbps"],
            name="下載速度",
            boxpoints="all",
            jitter=0.3,
            pointpos=-1.8
        ))

        fig.add_trace(go.Box(
            y=df["upload_mbps"],
            name="上傳速度",
            boxpoints="all",
            jitter=0.3,
            pointpos=-1.8
        ))

        fig.update_layout(
            title="速度分布盒狀圖",
            yaxis_title="速度 (Mbps)",
            height=500
        )

        return fig

    @staticmethod
    def create_ping_histogram(df: pd.DataFrame) -> go.Figure:
        """
        建立 Ping 值直方圖

        Args:
            df: 包含 ping_ms 的 DataFrame

        Returns:
            Plotly Figure
        """
        if df.empty or "ping_ms" not in df.columns:
            return go.Figure()
        df = df.copy()
        df["ping_ms"] = pd.to_numeric(df["ping_ms"], errors="coerce")
        df = df.dropna(subset=["ping_ms"])
        if df.empty:
            return go.Figure()

        fig = px.histogram(
            df,
            x="ping_ms",
            nbins=30,
            title="Ping 值分布",
            labels={"ping_ms": "Ping (ms)"}
        )

        fig.update_layout(height=400)
        return fig

    @staticmethod
    def create_hourly_pattern(df: pd.DataFrame) -> go.Figure:
        """
        建立每小時網路使用模式

        Args:
            df: 包含 hour, download_mbps 的 DataFrame

        Returns:
            Plotly Figure
        """
        if df.empty or "hour" not in df.columns:
            return go.Figure()
        if "download_mbps" not in df.columns:
            logger.warning("缺少每小時模式圖必要欄位：download_mbps")
            return go.Figure()

        df = df.copy()
        df["hour"] = pd.to_numeric(df["hour"], errors="coerce")
        df["download_mbps"] = pd.to_numeric(df["download_mbps"], errors="coerce")
        df = df.dropna(subset=["hour", "download_mbps"])
        if df.empty:
            return go.Figure()

        hourly_avg = df.groupby("hour")["download_mbps"].mean().reset_index()

        fig = px.line(
            hourly_avg,
            x="hour",
            y="download_mbps",
            title="每小時平均下載速度",
            labels={"hour": "小時", "download_mbps": "平均速度 (Mbps)"}
        )

        fig.update_layout(height=400)
        return fig
