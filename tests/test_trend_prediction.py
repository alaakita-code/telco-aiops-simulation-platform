import pandas as pd

from src.ml.trend_prediction import TrendPredictor


def test_forecast_speedtest_returns_history_and_future_rows():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-09-01", periods=36, freq="h"),
            "download_mbps": [100 + index for index in range(36)],
        }
    )

    forecast = TrendPredictor().forecast_speedtest(df, periods=7)

    assert len(forecast) == 43
    assert {"ds", "yhat", "model"}.issubset(forecast.columns)
    assert forecast["model"].eq("LinearRegression").all()
    assert (forecast["yhat"] >= 0).all()


def test_forecast_speedtest_returns_empty_when_data_is_insufficient():
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-09-01", periods=8, freq="h"),
            "download_mbps": [100] * 8,
        }
    )

    forecast = TrendPredictor().forecast_speedtest(df, periods=7)

    assert forecast.empty
