"""產出 Demo 資料報表與匯出檔。"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd

logger = logging.getLogger(__name__)


class ReportGenerator:
    """將目前資料輸出成 CSV、Markdown、HTML、PDF 與 ZIP 報表包。"""

    def __init__(self, output_dir: str = "data/exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report_package(self, data: dict[str, pd.DataFrame]) -> dict[str, Path]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_dir = self.output_dir / f"telco_aiops_report_{timestamp}"
        package_dir.mkdir(parents=True, exist_ok=True)

        speedtest_df = data.get("speedtest", pd.DataFrame())
        tower_df = data.get("cell_towers", pd.DataFrame())
        summary = self._build_summary(speedtest_df, tower_df)

        files: dict[str, Path] = {}
        files["summary_csv"] = self._write_summary_csv(summary, package_dir)
        files["markdown_report"] = self._write_markdown_report(summary, speedtest_df, tower_df, package_dir)
        files["html_report"] = self._write_html_report(summary, speedtest_df, tower_df, package_dir)
        files["pdf_report"] = self._write_pdf_report(summary, speedtest_df, tower_df, package_dir)

        if not speedtest_df.empty:
            speedtest_path = package_dir / "speedtest_export.csv"
            speedtest_df.to_csv(speedtest_path, index=False, encoding="utf-8-sig")
            files["speedtest_csv"] = speedtest_path

        if not tower_df.empty:
            tower_path = package_dir / "cell_towers_export.csv"
            tower_df.to_csv(tower_path, index=False, encoding="utf-8-sig")
            files["cell_towers_csv"] = tower_path

        zip_path = self.output_dir / f"{package_dir.name}.zip"
        with ZipFile(zip_path, "w", ZIP_DEFLATED) as zip_file:
            for path in files.values():
                zip_file.write(path, arcname=path.name)

        files["zip"] = zip_path
        logger.info(f"報表包產出完成：{zip_path}")
        return files

    def _build_summary(self, speedtest_df: pd.DataFrame, tower_df: pd.DataFrame) -> dict[str, str]:
        anomaly_count = 0
        incident_signal = "尚無測速資料"
        incident_recommendation = "請先產生或匯入 Demo 資料"

        if not speedtest_df.empty:
            try:
                from src.aiops import IncidentAdvisor
                from src.ml import AnomalyDetector

                detected = AnomalyDetector(contamination=0.1).detect_speedtest_anomalies(speedtest_df)
                anomaly_count = int(detected.get("is_anomaly", pd.Series(dtype=int)).sum())
                incidents = IncidentAdvisor().summarize_speedtest(detected)
                if incidents:
                    incident_signal = incidents[0].get("signal", "整體品質穩定")
                    incident_recommendation = incidents[0].get("recommendation", "持續觀察趨勢變化")
            except Exception as exc:
                logger.warning("AIOps 摘要產生失敗，改用基礎摘要：%s", exc)
                incident_signal = "已產生基礎資料摘要"
                incident_recommendation = "可於 Streamlit AIOps 頁查看完整異常分析"

        return {
            "產出時間": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Speedtest 筆數": str(len(speedtest_df)),
            "基地台筆數": str(len(tower_df)),
            "平均下載 Mbps": self._mean(speedtest_df, "download_mbps"),
            "平均上傳 Mbps": self._mean(speedtest_df, "upload_mbps"),
            "平均 Ping ms": self._mean(speedtest_df, "ping_ms"),
            "異常筆數": str(anomaly_count),
            "模擬業者數": str(tower_df["operator"].nunique()) if "operator" in tower_df.columns and not tower_df.empty else "0",
            "營運訊號": incident_signal,
            "建議處置": incident_recommendation,
        }

    def _write_summary_csv(self, summary: dict[str, str], package_dir: Path) -> Path:
        path = package_dir / "summary.csv"
        pd.DataFrame(summary.items(), columns=["指標", "數值"]).to_csv(path, index=False, encoding="utf-8-sig")
        return path

    def _write_markdown_report(
        self,
        summary: dict[str, str],
        speedtest_df: pd.DataFrame,
        tower_df: pd.DataFrame,
        package_dir: Path,
    ) -> Path:
        path = package_dir / "telco_aiops_report.md"
        quality = self._quality_sections(speedtest_df, tower_df)
        lines = [
            "# 電信網路模擬數據分析報告",
            "",
            "本報告由 Streamlit Demo 自動產生，資料來源為模擬資料或使用者匯入後的匿名化資料。",
            "",
            "## 摘要指標",
            "",
        ]
        lines += [f"- **{key}**：{value}" for key, value in summary.items()]
        lines += ["", "## 資料品質", "", quality, "", "## 匯出內容", "", "- summary.csv", "- telco_aiops_report.md", "- telco_aiops_report.html", "- speedtest_export.csv（若有資料）", "- cell_towers_export.csv（若有資料）"]
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _write_html_report(
        self,
        summary: dict[str, str],
        speedtest_df: pd.DataFrame,
        tower_df: pd.DataFrame,
        package_dir: Path,
    ) -> Path:
        path = package_dir / "telco_aiops_report.html"
        metric_cards = "".join(f"<div class='card'><span>{key}</span><b>{value}</b></div>" for key, value in summary.items())
        speed_preview = speedtest_df.head(12).to_html(index=False, border=0) if not speedtest_df.empty else "<p>尚無 Speedtest 資料。</p>"
        tower_preview = tower_df.head(12).to_html(index=False, border=0) if not tower_df.empty else "<p>尚無基地台資料。</p>"
        html = f"""<!doctype html>
<html lang="zh-Hant-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>電信網路模擬數據分析報告</title>
<style>
body{{font-family:"Microsoft JhengHei","Noto Sans CJK TC",Arial,sans-serif;background:#f4f7fb;color:#102033;margin:0;padding:32px}}
.wrap{{max-width:1100px;margin:auto}}
.hero{{background:linear-gradient(135deg,#0f766e,#2563eb,#7c3aed);color:white;border-radius:8px;padding:24px;margin-bottom:20px}}
.hero h1{{margin:0 0 12px;font-size:32px;line-height:1.25}}
.hero p{{margin:0;font-size:16px;line-height:1.6}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}}
.card{{background:white;border:1px solid #dbe5f5;border-radius:8px;padding:16px}}
.card span{{display:block;color:#64748b;font-size:13px;margin-bottom:6px}}
.card b{{font-size:20px}}
section{{background:white;border:1px solid #dbe5f5;border-radius:8px;padding:18px;margin-top:16px;overflow:auto}}
table{{width:100%;border-collapse:collapse;font-size:13px}}
th,td{{border-bottom:1px solid #e2e8f0;padding:8px;text-align:left;white-space:nowrap}}
@media (max-width: 640px){{
body{{padding:16px}}
.hero{{padding:20px}}
.hero h1{{font-size:28px}}
.grid{{grid-template-columns:1fr}}
.card{{padding:18px}}
.card b{{font-size:22px}}
section{{padding:16px}}
table{{font-size:12px;min-width:720px}}
}}
</style>
</head>
<body>
<main class="wrap">
<div class="hero"><h1>電信網路模擬數據分析報告</h1><p>自動彙整 Demo 資料、品質摘要、AIOps 訊號與匯出檔案。</p></div>
<div class="grid">{metric_cards}</div>
<section><h2>Speedtest 預覽</h2>{speed_preview}</section>
<section><h2>基地台資料預覽</h2>{tower_preview}</section>
</main>
</body>
</html>"""
        path.write_text(html, encoding="utf-8")
        return path

    def _write_pdf_report(
        self,
        summary: dict[str, str],
        speedtest_df: pd.DataFrame,
        tower_df: pd.DataFrame,
        package_dir: Path,
    ) -> Path:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        path = package_dir / "telco_aiops_report.pdf"
        font_name = self._register_pdf_font()
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ChineseTitle",
            parent=styles["Title"],
            fontName=font_name,
            fontSize=20,
            leading=26,
            textColor=colors.HexColor("#102033"),
        )
        body_style = ParagraphStyle(
            "ChineseBody",
            parent=styles["BodyText"],
            fontName=font_name,
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#334155"),
        )
        heading_style = ParagraphStyle(
            "ChineseHeading",
            parent=styles["Heading2"],
            fontName=font_name,
            fontSize=14,
            leading=20,
            textColor=colors.HexColor("#0f766e"),
        )

        doc = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            rightMargin=16 * mm,
            leftMargin=16 * mm,
            topMargin=16 * mm,
            bottomMargin=16 * mm,
        )
        story = [
            Paragraph("電信網路模擬數據分析報告", title_style),
            Paragraph("本報告由 Streamlit Demo 自動產生，資料來源為模擬資料或使用者匯入後的匿名化資料。", body_style),
            Spacer(1, 8),
            Paragraph("摘要指標", heading_style),
            self._pdf_table([["指標", "數值"], *summary.items()], font_name),
            Spacer(1, 10),
            Paragraph("Speedtest 預覽", heading_style),
            self._pdf_dataframe(speedtest_df, font_name, ["timestamp", "region", "download_mbps", "upload_mbps", "ping_ms"], 8),
            Spacer(1, 10),
            Paragraph("基地台資料預覽", heading_style),
            self._pdf_dataframe(tower_df, font_name, ["cellId", "operator", "lat", "lon", "avgRange", "radio"], 8),
        ]
        doc.build(story)
        return path

    def _quality_sections(self, speedtest_df: pd.DataFrame, tower_df: pd.DataFrame) -> str:
        try:
            from src.quality import DataQualityChecker

            checker = DataQualityChecker()
            speed_rules = checker.to_dataframe(checker.check_speedtest(speedtest_df))
            tower_rules = checker.to_dataframe(checker.check_cell_towers(tower_df))
            speed_lines = [f"- Speedtest / {row['name']}：{row['status']}，{row['detail']}" for _, row in speed_rules.iterrows()]
            tower_lines = [f"- 基地台 / {row['name']}：{row['status']}，{row['detail']}" for _, row in tower_rules.iterrows()]
            return "\n".join(speed_lines + tower_lines)
        except Exception as exc:
            logger.warning("資料品質摘要產生失敗，改用基礎摘要：%s", exc)
            return "- 已產生資料筆數與核心 KPI 摘要。"

    def _mean(self, df: pd.DataFrame, column: str) -> str:
        if df.empty or column not in df.columns:
            return "N/A"
        value = pd.to_numeric(df[column], errors="coerce").mean()
        return "N/A" if pd.isna(value) else f"{value:.1f}"

    def _register_pdf_font(self) -> str:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfbase.ttfonts import TTFont

        font_candidates = [
            "C:/Windows/Fonts/msjh.ttc",
            "C:/Windows/Fonts/mingliu.ttc",
            "/System/Library/Fonts/PingFang.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]
        for font_path in font_candidates:
            if Path(font_path).exists():
                try:
                    pdfmetrics.registerFont(TTFont("ReportChinese", font_path))
                    return "ReportChinese"
                except Exception as exc:
                    logger.warning("PDF 字型註冊失敗，嘗試下一個字型：%s (%s)", font_path, exc)

        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        return "STSong-Light"

    def _pdf_table(self, rows: list, font_name: str) -> "Table":
        from reportlab.lib import colors
        from reportlab.platypus import Table, TableStyle

        table = Table(rows, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), font_name),
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbeafe")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbd5e1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        return table

    def _pdf_dataframe(self, df: pd.DataFrame, font_name: str, columns: list[str], rows: int) -> "Table":
        if df.empty:
            return self._pdf_table([["狀態"], ["尚無資料"]], font_name)

        available_columns = [column for column in columns if column in df.columns]
        preview = df[available_columns].head(rows).copy()
        preview = preview.astype(str)
        return self._pdf_table([available_columns, *preview.values.tolist()], font_name)
