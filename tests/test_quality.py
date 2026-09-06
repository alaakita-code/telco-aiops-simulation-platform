import pandas as pd

from src.quality.data_quality import DataQualityChecker


def test_speedtest_quality_passes_valid_data():
    df = pd.DataFrame(
        {
            "timestamp": ["2026-09-01 09:00:00", "2026-09-01 10:00:00"],
            "download_mbps": [120.5, 98.2],
            "upload_mbps": [35.0, 28.7],
            "ping_ms": [18.0, 22.5],
        }
    )

    rules = DataQualityChecker().check_speedtest(df)

    assert rules[0].status == "通過"
    assert all(rule.status == "通過" for rule in rules)


def test_cell_tower_quality_reports_missing_required_column():
    df = pd.DataFrame({"lat": [25.03], "operator": ["模擬業者 A"]})

    rules = DataQualityChecker().check_cell_towers(df)

    assert rules[0].status == "需修正"
    assert "lon" in rules[0].detail
