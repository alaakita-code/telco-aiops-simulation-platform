"""Generate simulated telco demo datasets."""

from datetime import datetime, timedelta
from typing import Literal

import numpy as np
import pandas as pd


Scenario = Literal["normal", "peak_congestion", "regional_issue", "device_degradation"]


REGION_CENTERS = {
    "台北": (25.0330, 121.5654),
    "新北": (25.0169, 121.4628),
    "台中": (24.1477, 120.6736),
    "高雄": (22.6273, 120.3014),
    "全台": (23.6978, 120.9605),
}


def _rng(seed: int | None = 42) -> np.random.Generator:
    return np.random.default_rng(seed)


def generate_speedtest(
    rows: int = 120,
    region: str = "台北",
    scenario: Scenario = "normal",
    seed: int | None = 42,
) -> pd.DataFrame:
    """Create simulated speedtest records for demo and portfolio use."""
    generator = _rng(seed)
    base_time = datetime.now() - timedelta(hours=rows)
    center_lat, center_lon = REGION_CENTERS.get(region, REGION_CENTERS["台北"])

    timestamps = [base_time + timedelta(hours=i) for i in range(rows)]
    hours = np.array([timestamp.hour for timestamp in timestamps])

    download = generator.normal(145, 18, rows)
    upload = generator.normal(38, 7, rows)
    ping = generator.normal(16, 4, rows)

    if scenario == "peak_congestion":
        peak_mask = (hours >= 19) & (hours <= 23)
        download[peak_mask] *= 0.58
        upload[peak_mask] *= 0.72
        ping[peak_mask] += 18
    elif scenario == "regional_issue":
        issue_start = max(0, rows // 2 - rows // 10)
        issue_end = min(rows, issue_start + max(6, rows // 8))
        download[issue_start:issue_end] *= 0.45
        upload[issue_start:issue_end] *= 0.65
        ping[issue_start:issue_end] += 28
    elif scenario == "device_degradation":
        trend = np.linspace(1.0, 0.62, rows)
        download *= trend
        upload *= np.linspace(1.0, 0.78, rows)
        ping += np.linspace(0, 22, rows)

    df = pd.DataFrame({
        "timestamp": timestamps,
        "region": region,
        "scenario": scenario,
        "download_mbps": np.clip(download, 5, None).round(2),
        "upload_mbps": np.clip(upload, 1, None).round(2),
        "ping_ms": np.clip(ping, 1, None).round(2),
        "lat": (center_lat + generator.normal(0, 0.025, rows)).round(6),
        "lon": (center_lon + generator.normal(0, 0.025, rows)).round(6),
    })
    return df


def generate_cell_towers(
    rows: int = 80,
    region: str = "台北",
    seed: int | None = 42,
) -> pd.DataFrame:
    """Create simulated cell tower records with anonymized operators."""
    generator = _rng(seed)
    center_lat, center_lon = REGION_CENTERS.get(region, REGION_CENTERS["台北"])
    operators = np.array(["模擬業者 A", "模擬業者 B", "模擬業者 C"])

    df = pd.DataFrame({
        "cellId": np.arange(100000, 100000 + rows),
        "MCC": 466,
        "MNC": generator.choice([92, 99, 1], size=rows),
        "operator": generator.choice(operators, size=rows, p=[0.45, 0.30, 0.25]),
        "lat": (center_lat + generator.normal(0, 0.035, rows)).round(6),
        "lon": (center_lon + generator.normal(0, 0.035, rows)).round(6),
        "avgRange": generator.integers(250, 1800, size=rows),
        "radio": generator.choice(["LTE", "NR", "LTE+NR"], size=rows, p=[0.45, 0.35, 0.20]),
    })
    return df
