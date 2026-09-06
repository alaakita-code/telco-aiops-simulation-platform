"""趨勢預測模組：預設使用輕量線性趨勢，避免部署環境依賴 Prophet/Stan。"""
import pandas as pd
from loguru import logger
from sklearn.linear_model import LinearRegression


class TrendPredictor:
    """趨勢預測器"""

    def __init__(self):
        logger.info("趨勢預測器初始化：使用 LinearRegression")

    def forecast_speedtest(self, df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
        """
        預測未來網路速度趨勢

        Args:
            df: 包含 timestamp, download_mbps 的 DataFrame
            periods: 預測天數

        Returns:
            預測結果 DataFrame
        """
        if df.empty:
            return pd.DataFrame()

        required_columns = {"timestamp", "download_mbps"}
        if not required_columns.issubset(df.columns):
            logger.warning(f"缺少趨勢預測欄位：{sorted(required_columns - set(df.columns))}")
            return pd.DataFrame()

        # 準備數據
        data = df[["timestamp", "download_mbps"]].copy()
        data.columns = ["ds", "y"]
        data["ds"] = pd.to_datetime(data["ds"], errors="coerce")
        data["y"] = pd.to_numeric(data["y"], errors="coerce")
        data = data.dropna()
        data = data.sort_values("ds")

        if len(data) < 30:
            logger.warning("數據不足，需要至少 30 筆")
            return pd.DataFrame()

        return self._forecast_with_linear_model(data, periods)

    def _forecast_with_linear_model(self, data: pd.DataFrame, periods: int) -> pd.DataFrame:
        """使用 scikit-learn 線性回歸建立輕量趨勢預測。"""
        model_data = data.copy()
        model_data["x"] = (model_data["ds"] - model_data["ds"].min()).dt.total_seconds() / 86400

        model = LinearRegression()
        model.fit(model_data[["x"]], model_data["y"])

        last_date = model_data["ds"].max()
        future_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1),
            periods=periods,
            freq="D"
        )
        history_forecast = model_data[["ds", "x"]].copy()
        future_forecast = pd.DataFrame({
            "ds": future_dates,
            "x": (future_dates - model_data["ds"].min()).total_seconds() / 86400,
        })

        forecast = pd.concat([history_forecast, future_forecast], ignore_index=True)
        forecast["yhat"] = model.predict(forecast[["x"]])
        forecast["yhat"] = forecast["yhat"].clip(lower=0)
        forecast["model"] = "LinearRegression"
        logger.info(f"線性趨勢預測完成：{periods} 天")
        return forecast[["ds", "yhat", "model"]]

    def get_trend_direction(self, forecast: pd.DataFrame) -> str:
        """
        判斷趨勢方向

        Args:
            forecast: 預測結果

        Returns:
            趨勢方向字串
        """
        if forecast.empty:
            return "無數據"
        if "yhat" not in forecast.columns:
            return "無預測欄位"

        # 比較首尾預測值
        first = forecast["yhat"].iloc[0]
        last = forecast["yhat"].iloc[-1]

        if first == 0:
            return "無法判斷趨勢"

        change = (last - first) / first * 100

        if change > 5:
            return f"上升趨勢 (+{change:.1f}%)"
        elif change < -5:
            return f"下降趨勢 ({change:.1f}%)"
        else:
            return f"持平趨勢 ({change:+.1f}%)"
