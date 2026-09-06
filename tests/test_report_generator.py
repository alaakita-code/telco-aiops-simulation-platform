from pathlib import Path
from zipfile import ZipFile

from src.reports.report_generator import ReportGenerator
from src.simulation.data_generator import generate_cell_towers, generate_speedtest


def test_report_package_exports_markdown_html_pdf_and_zip(tmp_path: Path):
    data = {
        "speedtest": generate_speedtest(rows=40, seed=5),
        "cell_towers": generate_cell_towers(rows=10, seed=5),
    }

    files = ReportGenerator(output_dir=str(tmp_path)).generate_report_package(data)

    assert files["markdown_report"].exists()
    assert files["html_report"].exists()
    assert files["pdf_report"].exists()
    assert files["zip"].exists()
    assert files["markdown_report"].read_text(encoding="utf-8").startswith("# 電信網路模擬數據分析報告")
    assert "<html" in files["html_report"].read_text(encoding="utf-8").lower()
    assert files["pdf_report"].stat().st_size > 0

    with ZipFile(files["zip"]) as zip_file:
        names = set(zip_file.namelist())

    assert {
        "summary.csv",
        "telco_aiops_report.md",
        "telco_aiops_report.html",
        "telco_aiops_report.pdf",
        "speedtest_export.csv",
        "cell_towers_export.csv",
    }.issubset(names)
