"""Machine learning helpers."""

from .anomaly_detection import AnomalyDetector


def __getattr__(name):
    if name == "TrendPredictor":
        from .trend_prediction import TrendPredictor

        return TrendPredictor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
