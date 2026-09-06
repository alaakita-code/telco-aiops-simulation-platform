"""
地圖可視化
Folium, Plotly 地圖
"""
import folium
from folium.plugins import HeatMap, MarkerCluster
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from typing import Tuple, Optional
from loguru import logger


class MapCharts:
    """地圖可視化"""

    @staticmethod
    def create_folium_map(center: Tuple[float, float], zoom: int = 12) -> folium.Map:
        """建立 Folium 基礎地圖"""
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles="OpenStreetMap",
            prefer_canvas=True
        )
        return m

    @staticmethod
    def add_heatmap(m: folium.Map, df: pd.DataFrame, radius: int = 15, blur: int = 10) -> folium.Map:
        """
        加入熱力圖

        Args:
            m: Folium 地圖
            df: 包含 lat, lon 的 DataFrame
            radius: 熱力圖半徑
            blur: 模糊度
        """
        if df.empty:
            return m
        if not {"lat", "lon"}.issubset(df.columns):
            logger.warning("缺少熱力圖必要欄位：lat/lon")
            return m

        df = df.copy()
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
        df = df.dropna(subset=["lat", "lon"])
        df = df[df["lat"].between(-90, 90) & df["lon"].between(-180, 180)]
        if df.empty:
            return m

        heat_data = df[["lat", "lon"]].values.tolist()

        HeatMap(
            heat_data,
            radius=radius,
            blur=blur,
            gradient={0.3: "green", 0.5: "yellow", 0.7: "orange", 1.0: "red"},
            min_opacity=0.4
        ).add_to(m)

        logger.info(f"加入熱力圖：{len(df)} 個點")
        return m

    @staticmethod
    def create_plotly_map(df: pd.DataFrame, color_col: Optional[str] = None) -> go.Figure:
        """
        建立 Plotly 互動地圖

        Args:
            df: 包含 lat, lon 的 DataFrame
            color_col: 用於著色的欄位

        Returns:
            Plotly Figure
        """
        if df.empty:
            return go.Figure()
        if not {"lat", "lon"}.issubset(df.columns):
            logger.warning("缺少地圖必要欄位：lat/lon")
            return go.Figure()

        df = df.copy()
        df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
        df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
        df = df.dropna(subset=["lat", "lon"])
        df = df[df["lat"].between(-90, 90) & df["lon"].between(-180, 180)]
        if df.empty:
            return go.Figure()

        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            color=color_col if color_col in df.columns else None,
            zoom=10,
            center={"lat": df["lat"].mean(), "lon": df["lon"].mean()},
            mapbox_style="open-street-map",
            hover_data=list(df.columns)
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            height=600
        )

        return fig

    @staticmethod
    def create_operator_distribution(df: pd.DataFrame) -> go.Figure:
        """
        建立模擬業者分布圖

        Args:
            df: 包含 operator 欄位的 DataFrame

        Returns:
            Plotly Figure
        """
        if df.empty or "operator" not in df.columns:
            return go.Figure()

        operator_counts = df["operator"].value_counts().reset_index()
        operator_counts.columns = ["operator", "count"]

        fig = px.bar(
            operator_counts,
            x="operator",
            y="count",
            title="模擬業者基地台數量分布",
            labels={"operator": "模擬業者", "count": "基地台數量"}
        )

        fig.update_layout(height=400)
        return fig
