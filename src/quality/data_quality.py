"""Data quality checks for simulated telco datasets."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class QualityRule:
    name: str
    status: str
    detail: str


class DataQualityChecker:
    """Small, explainable data quality checker for Streamlit display."""

    def check_speedtest(self, df: pd.DataFrame) -> list[QualityRule]:
        required = ["timestamp", "download_mbps", "upload_mbps", "ping_ms"]
        rules = self._check_required(df, required)
        if df.empty:
            return rules

        rules.append(self._check_duplicates(df))
        rules.append(self._check_numeric_range(df, "download_mbps", 0, 2000))
        rules.append(self._check_numeric_range(df, "upload_mbps", 0, 1000))
        rules.append(self._check_numeric_range(df, "ping_ms", 0, 1000))
        return rules

    def check_cell_towers(self, df: pd.DataFrame) -> list[QualityRule]:
        required = ["lat", "lon", "operator"]
        rules = self._check_required(df, required)
        if df.empty:
            return rules

        rules.append(self._check_duplicates(df))
        rules.append(self._check_numeric_range(df, "lat", -90, 90))
        rules.append(self._check_numeric_range(df, "lon", -180, 180))
        return rules

    def to_dataframe(self, rules: list[QualityRule]) -> pd.DataFrame:
        return pd.DataFrame([rule.__dict__ for rule in rules])

    def _check_required(self, df: pd.DataFrame, required: list[str]) -> list[QualityRule]:
        missing = [column for column in required if column not in df.columns]
        status = "通過" if not missing else "需修正"
        detail = "必要欄位完整" if not missing else f"缺少欄位：{', '.join(missing)}"
        return [QualityRule("必要欄位", status, detail)]

    def _check_duplicates(self, df: pd.DataFrame) -> QualityRule:
        count = int(df.duplicated().sum())
        status = "通過" if count == 0 else "需檢查"
        detail = "無重複資料" if count == 0 else f"發現 {count} 筆重複資料"
        return QualityRule("重複資料", status, detail)

    def _check_numeric_range(self, df: pd.DataFrame, column: str, min_value: float, max_value: float) -> QualityRule:
        if column not in df.columns:
            return QualityRule(column, "略過", "欄位不存在")

        values = pd.to_numeric(df[column], errors="coerce")
        invalid = values.isna() | ~values.between(min_value, max_value)
        count = int(invalid.sum())
        status = "通過" if count == 0 else "需修正"
        detail = f"{column} 數值範圍正常" if count == 0 else f"{column} 有 {count} 筆無效值"
        return QualityRule(column, status, detail)
