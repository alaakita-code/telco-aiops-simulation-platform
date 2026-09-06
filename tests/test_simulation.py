import pandas as pd

from src.simulation.data_generator import generate_cell_towers, generate_speedtest


def test_generate_speedtest_has_expected_columns_and_rows():
    df = generate_speedtest(rows=24, region="台北", scenario="peak_congestion", seed=7)

    assert len(df) == 24
    assert {
        "timestamp",
        "region",
        "scenario",
        "download_mbps",
        "upload_mbps",
        "ping_ms",
        "lat",
        "lon",
    }.issubset(df.columns)
    assert (df["download_mbps"] > 0).all()
    assert (df["upload_mbps"] > 0).all()
    assert (df["ping_ms"] > 0).all()
    assert pd.api.types.is_datetime64_any_dtype(df["timestamp"])


def test_generate_cell_towers_has_expected_columns_and_anonymized_operators():
    df = generate_cell_towers(rows=12, region="台北", seed=7)

    assert len(df) == 12
    assert {"cellId", "MCC", "MNC", "operator", "lat", "lon", "avgRange", "radio"}.issubset(df.columns)
    assert set(df["operator"]).issubset({"模擬業者 A", "模擬業者 B", "模擬業者 C"})
    assert df["lat"].between(-90, 90).all()
    assert df["lon"].between(-180, 180).all()
