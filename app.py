"""Telco AIOps Simulation Platform."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.aiops import IncidentAdvisor
from src.etl import DataExtractor, DataLoader, DataTransformer
from src.ml import AnomalyDetector
from src.quality import DataQualityChecker
from src.reports import ReportGenerator
from src.simulation import generate_cell_towers, generate_speedtest
from src.visualization import InteractiveCharts, MapCharts


APP_TITLE = "電信網路模擬數據分析與 AIOps 展示平台"


def ensure_data_directories() -> None:
    for path in ("data/raw", "data/processed", "data/sample", "data/exports"):
        Path(path).mkdir(parents=True, exist_ok=True)


def detect_uploaded_data_type(df: pd.DataFrame) -> str:
    columns = {str(col).strip().lower() for col in df.columns}
    if {"timestamp", "download_mbps", "upload_mbps", "ping_ms"}.issubset(columns):
        return "speedtest"
    if {"lat", "lon"}.issubset(columns):
        return "cell_towers"
    return "uploaded_data"


def save_uploaded_data(df: pd.DataFrame) -> tuple[str, Path, str]:
    loader = DataLoader()
    data_type = detect_uploaded_data_type(df)

    if data_type == "speedtest":
        df = DataTransformer().clean_speedtest_data(df)
        raw_path = Path("data/raw/manual_speedtest.csv")
        df.to_csv(raw_path, index=False, encoding="utf-8-sig")
        loader.load_speedtest_results(df)
        return "Speedtest 測速資料", raw_path, "speedtest_results"

    if data_type == "cell_towers":
        df = DataTransformer().clean_cell_tower_data(df)
        raw_path = Path("data/raw/manual_cell_towers.csv")
        df.to_csv(raw_path, index=False, encoding="utf-8-sig")
        loader.load_cell_towers(df)
        return "基地台模擬資料", raw_path, "cell_towers"

    raw_path = Path("data/raw/uploaded_data.csv")
    df.to_csv(raw_path, index=False, encoding="utf-8-sig")
    loader.load_to_sqlite(df, "uploaded_data")
    return "一般上傳資料", raw_path, "uploaded_data"


def load_speedtest() -> pd.DataFrame:
    df = DataExtractor().extract_speedtest_history()
    if not df.empty:
        return DataTransformer().clean_speedtest_data(df)

    raw_path = Path("data/raw/manual_speedtest.csv")
    if raw_path.exists():
        return DataTransformer().clean_speedtest_data(pd.read_csv(raw_path))
    return pd.DataFrame()


def load_cell_towers() -> pd.DataFrame:
    df = DataExtractor().extract_from_sqlite("cell_towers")
    if not df.empty:
        return DataTransformer().clean_cell_tower_data(df)

    raw_path = Path("data/raw/manual_cell_towers.csv")
    if raw_path.exists():
        return DataTransformer().clean_cell_tower_data(pd.read_csv(raw_path))
    return pd.DataFrame()


def seed_demo_data(rows: int = 120, region: str = "台北", scenario: str = "peak_congestion") -> None:
    speedtest_df = generate_speedtest(rows=rows, region=region, scenario=scenario)
    tower_df = generate_cell_towers(rows=max(40, rows // 2), region=region)

    speedtest_df.to_csv("data/raw/manual_speedtest.csv", index=False, encoding="utf-8-sig")
    tower_df.to_csv("data/raw/manual_cell_towers.csv", index=False, encoding="utf-8-sig")

    loader = DataLoader()
    loader.load_speedtest_results(speedtest_df)
    loader.load_cell_towers(tower_df)


def inject_design() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1240px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #eff6ff 0%, #f6f0ff 100%);
            border-right: 1px solid #dbe5f5;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        section[data-testid="stSidebar"] label {
            color: #24324b;
        }
        h1, h2, h3 {
            color: #122033;
            letter-spacing: 0;
        }
        h1 {
            font-size: 2.1rem;
            margin-bottom: .4rem;
        }
        h2 {
            font-size: 1.45rem;
            margin-top: 1.4rem;
        }
        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #dbe5f5;
            border-radius: 8px;
            padding: 1rem 1rem .85rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, .06);
        }
        div[data-testid="stMetric"] label {
            color: #64748b;
            font-size: .88rem;
        }
        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #0f172a;
            font-size: 1.5rem;
        }
        .hero {
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, #0f766e 0%, #2563eb 52%, #7c3aed 100%);
            color: white;
            border-radius: 8px;
            padding: 1.45rem 1.65rem;
            margin-bottom: 1rem;
            box-shadow: 0 16px 36px rgba(37, 99, 235, .18);
        }
        .hero:after {
            content: "";
            position: absolute;
            right: -80px;
            top: -90px;
            width: 260px;
            height: 260px;
            border-radius: 999px;
            background: rgba(255, 255, 255, .13);
        }
        .hero h1 {
            color: white;
            margin: 0 0 .45rem;
            font-size: 1.9rem;
        }
        .hero p {
            margin: 0;
            max-width: 820px;
            color: #e0f2fe;
            line-height: 1.7;
        }
        .pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: .55rem;
            margin-top: 1rem;
        }
        .pill {
            background: rgba(255, 255, 255, .16);
            border: 1px solid rgba(255, 255, 255, .22);
            border-radius: 999px;
            color: #f8fafc;
            padding: .36rem .72rem;
            font-size: .86rem;
        }
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: .8rem;
            margin-bottom: 1.1rem;
        }
        .mini-metric {
            background: #ffffff;
            border: 1px solid #dbe5f5;
            border-radius: 8px;
            padding: .95rem;
            box-shadow: 0 8px 22px rgba(15, 23, 42, .05);
        }
        .mini-metric .icon {
            width: 34px;
            height: 34px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: #eef6ff;
            margin-bottom: .65rem;
            font-size: 1.15rem;
        }
        .mini-metric .label {
            color: #64748b;
            font-size: .85rem;
            margin-bottom: .25rem;
        }
        .mini-metric .value {
            color: #0f172a;
            font-size: 1.35rem;
            font-weight: 750;
        }
        .section-title {
            color: #0f172a;
            font-size: 1.2rem;
            font-weight: 700;
            margin: 1.2rem 0 .7rem;
        }
        .card-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: .85rem;
            margin-bottom: 1rem;
        }
        .info-card {
            background: #ffffff;
            border: 1px solid #dbe5f5;
            border-radius: 8px;
            padding: 1rem 1rem 1.1rem;
            min-height: 130px;
            box-shadow: 0 8px 22px rgba(15, 23, 42, .05);
        }
        .card-icon {
            width: 38px;
            height: 38px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: linear-gradient(135deg, #e0f2fe, #ede9fe);
            margin-bottom: .65rem;
            font-size: 1.25rem;
        }
        .info-card .kicker {
            color: #2563eb;
            font-size: .8rem;
            font-weight: 700;
            margin-bottom: .35rem;
        }
        .info-card h3 {
            font-size: 1rem;
            margin: 0 0 .45rem;
        }
        .info-card p {
            color: #475569;
            font-size: .9rem;
            line-height: 1.55;
            margin: 0;
        }
        .flow {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: .65rem;
        }
        .flow-step {
            background: #ffffff;
            border: 1px solid #dbe5f5;
            border-radius: 8px;
            padding: .9rem;
            box-shadow: 0 6px 16px rgba(15, 23, 42, .04);
        }
        .flow-step b {
            display: block;
            color: #0f172a;
            margin-bottom: .25rem;
        }
        .flow-step span {
            color: #64748b;
            font-size: .86rem;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: .65rem;
            margin-bottom: 1rem;
        }
        .status-chip {
            background: #ffffff;
            border: 1px solid #dbe5f5;
            border-radius: 8px;
            padding: .8rem;
        }
        .status-chip .stage {
            color: #475569;
            font-size: .82rem;
            margin-bottom: .35rem;
        }
        .status-chip .state {
            color: #047857;
            font-weight: 750;
            font-size: .95rem;
        }
        .page-head {
            display: grid;
            grid-template-columns: 58px 1fr;
            gap: 1rem;
            align-items: start;
            background: #ffffff;
            border: 1px solid #dbe5f5;
            border-radius: 8px;
            padding: 1.15rem 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 10px 26px rgba(15, 23, 42, .06);
        }
        .page-icon {
            width: 48px;
            height: 48px;
            display: grid;
            place-items: center;
            border-radius: 8px;
            background: linear-gradient(135deg, #dcfce7, #dbeafe 55%, #ede9fe);
            font-size: 1.55rem;
        }
        .page-head h1 {
            margin: 0 0 .25rem;
            font-size: 1.65rem;
        }
        .page-head p {
            margin: 0;
            color: #475569;
            line-height: 1.65;
        }
        .chip-row {
            display: flex;
            flex-wrap: wrap;
            gap: .45rem;
            margin-top: .7rem;
        }
        .soft-chip {
            background: #f1f5f9;
            border: 1px solid #dbe5f5;
            border-radius: 999px;
            color: #334155;
            padding: .28rem .62rem;
            font-size: .8rem;
        }
        .small-card-grid {
            display: grid;
            grid-template-columns: repeat(var(--card-cols, 4), minmax(0, 1fr));
            gap: .75rem;
            margin: .85rem 0 1.1rem;
            align-items: stretch;
        }
        .small-card {
            background: #ffffff;
            border: 1px solid #dbe5f5;
            border-radius: 8px;
            padding: .95rem;
            min-height: 104px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, .045);
        }
        .small-card .icon {
            font-size: 1.3rem;
            margin-bottom: .35rem;
        }
        .small-card b {
            display: block;
            color: #0f172a;
            margin-bottom: .25rem;
            overflow-wrap: anywhere;
        }
        .small-card span {
            color: #64748b;
            font-size: .88rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
            word-break: normal;
        }
        .quality-pass {
            border-left: 5px solid #10b981;
        }
        .quality-warn {
            border-left: 5px solid #f59e0b;
        }
        .incident-low {
            border-left: 5px solid #38bdf8;
        }
        .incident-mid {
            border-left: 5px solid #f59e0b;
        }
        .incident-high {
            border-left: 5px solid #ef4444;
        }
        .note-panel {
            background: #ecfeff;
            border: 1px solid #bae6fd;
            border-radius: 8px;
            padding: .95rem 1rem;
            color: #164e63;
            margin: .75rem 0 1rem;
        }
        @media (max-width: 900px) {
            .card-grid,
            .flow,
            .metric-grid,
            .status-grid {
                grid-template-columns: 1fr;
            }
            .small-card-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            }
            .hero {
                padding: 1.2rem;
            }
            .hero h1 {
                font-size: 1.55rem;
            }
        }
        @media (max-width: 480px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .page-head {
                grid-template-columns: 44px 1fr;
                gap: .8rem;
                padding: 1rem;
            }
            .page-icon {
                width: 42px;
                height: 42px;
                font-size: 1.35rem;
            }
            .page-head h1 {
                font-size: 1.5rem;
                line-height: 1.25;
            }
            .page-head p {
                font-size: .98rem;
                line-height: 1.55;
            }
            .small-card-grid {
                grid-template-columns: 1fr !important;
                gap: .65rem;
            }
            .small-card {
                display: grid;
                grid-template-columns: 36px 1fr;
                column-gap: .75rem;
                align-items: start;
                min-height: 0;
                padding: .85rem;
            }
            .small-card .icon {
                margin-bottom: 0;
                line-height: 1.2;
            }
            .small-card b {
                font-size: 1rem;
                line-height: 1.35;
            }
            .small-card span {
                grid-column: 2;
                font-size: .86rem;
                line-height: 1.55;
            }
            div[data-testid="stDataFrame"],
            div[data-testid="stTable"] {
                overflow-x: auto;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(icon: str, title: str, subtitle: str, chips: list[str] | None = None) -> None:
    chip_html = "".join(f'<span class="soft-chip">{chip}</span>' for chip in (chips or []))
    st.markdown(
        f'<div class="page-head"><div class="page-icon">{icon}</div><div><h1>{title}</h1><p>{subtitle}</p><div class="chip-row">{chip_html}</div></div></div>',
        unsafe_allow_html=True,
    )


def icon_cards(cards: list[tuple[str, str, str]], columns: int = 4) -> None:
    html = "".join(
        f'<div class="small-card"><div class="icon">{icon}</div><b>{title}</b><span>{body}</span></div>'
        for icon, title, body in cards
    )
    st.markdown(f'<div class="small-card-grid" style="--card-cols: {columns};">{html}</div>', unsafe_allow_html=True)


def quality_cards(title: str, rules: pd.DataFrame) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    cards = []
    for _, row in rules.iterrows():
        css = "quality-pass" if row.get("status") == "通過" else "quality-warn"
        icon = "✅" if row.get("status") == "通過" else "⚠️"
        cards.append(
            f'<div class="small-card {css}"><div class="icon">{icon}</div><b>{row.get("name", "檢查項目")}</b><span>{row.get("status", "")}｜{row.get("detail", "")}</span></div>'
        )
    st.markdown(f'<div class="small-card-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def compact_plotly(fig: go.Figure, height: int = 420) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=56, b=38),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    ensure_data_directories()
    inject_design()

    with st.sidebar:
        st.header("導覽")
        page = st.radio(
            "選擇頁面",
            [
                "🏠 營運總覽",
                "🧪 模擬資料產生器",
                "🗺️ 基地台 GIS 熱力圖",
                "📶 Speedtest 網路品質",
                "🤖 AIOps 異常中心",
                "📈 趨勢預測",
                "🧹 資料品質檢查",
                "🗄️ ETL 資料管理",
                "📘 作品集專案說明",
            ],
        )
        st.markdown("---")
        st.info("資料皆為模擬或使用者匯入後匿名化結果，不代表任何真實電信商營運資料。")

    pages = {
        "🏠 營運總覽": show_overview,
        "🧪 模擬資料產生器": show_simulator,
        "🗺️ 基地台 GIS 熱力圖": show_cell_tower_map,
        "📶 Speedtest 網路品質": show_speedtest_analysis,
        "🤖 AIOps 異常中心": show_aiops_center,
        "📈 趨勢預測": show_trend_prediction,
        "🧹 資料品質檢查": show_data_quality,
        "🗄️ ETL 資料管理": show_data_management,
        "📘 作品集專案說明": show_portfolio,
    }
    pages[page]()


def show_overview() -> None:
    speedtest_df = load_speedtest()
    tower_df = load_cell_towers()

    st.markdown(
        """
        <div class="hero">
            <h1>電信網路模擬數據分析平台</h1>
            <p>以安全的模擬資料展示從資料產生、ETL 清洗、SQLite 儲存、GIS 視覺化、異常偵測到營運建議的完整 AIOps Demo 流程。</p>
            <div class="pill-row">
                <span class="pill">Streamlit Demo</span>
                <span class="pill">ETL Pipeline</span>
                <span class="pill">GIS Heatmap</span>
                <span class="pill">AIOps Advisor</span>
                <span class="pill">GitHub Portfolio</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if speedtest_df.empty and tower_df.empty:
        st.warning("目前尚未建立 demo 資料，請先到「模擬資料產生器」一鍵產生。")

    anomaly_df = pd.DataFrame()
    if not speedtest_df.empty:
        anomaly_df = AnomalyDetector().detect_speedtest_anomalies(speedtest_df)

    anomaly_count = int(anomaly_df.get("is_anomaly", pd.Series(dtype=int)).sum()) if not anomaly_df.empty else 0
    st.markdown('<div class="section-title">Demo 即時摘要</div>', unsafe_allow_html=True)
    metric_cols = st.columns(5)
    metric_cols[0].metric("📶 測速筆數", len(speedtest_df))
    metric_cols[1].metric("🗼 基地台筆數", len(tower_df))
    metric_cols[2].metric("⚡ 平均下載", _metric_mean(speedtest_df, "download_mbps", "Mbps"))
    metric_cols[3].metric("⏱️ 平均 Ping", _metric_mean(speedtest_df, "ping_ms", "ms"))
    metric_cols[4].metric("🔎 異常筆數", anomaly_count)

    statuses = [
        ("資料產生 / 匯入", "完成" if not speedtest_df.empty or not tower_df.empty else "待建立", "🧪"),
        ("匿名化與清洗", "完成" if not tower_df.empty or not speedtest_df.empty else "待處理", "🧼"),
        ("SQLite 儲存", "完成" if Path("data/processed/telco_data.db").exists() else "待建立", "🗄️"),
        ("GIS / 圖表", "可展示" if not tower_df.empty or not speedtest_df.empty else "待資料", "🗺️"),
        ("AIOps 分析", "可展示" if not speedtest_df.empty else "待資料", "🤖"),
    ]
    status_html = "".join(
        f'<div class="status-chip"><div class="stage">{icon} {stage}</div><div class="state">{state}</div></div>'
        for stage, state, icon in statuses
    )
    st.markdown('<div class="section-title">資料流程狀態</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="status-grid">{status_html}</div>', unsafe_allow_html=True)

    st.markdown("#### 🧭 Demo 流程地圖")

    st.markdown(
        """
        <div class="section-title">核心能力展示</div>
        <div class="card-grid">
            <div class="info-card">
                <div class="card-icon">🧩</div>
                <div class="kicker">DATA ENGINEERING</div>
                <h3>資料產生、匯入與清洗</h3>
                <p>支援模擬資料與 CSV 匯入，自動辨識 Speedtest / 基地台資料，完成匿名化、型別轉換與 SQLite 寫入。</p>
            </div>
            <div class="info-card">
                <div class="card-icon">🗺️</div>
                <div class="kicker">GIS VISUALIZATION</div>
                <h3>基地台熱力圖與分布</h3>
                <p>使用 Folium 與 Plotly 呈現模擬基地台分布、業者比例與地理熱點，適合展示電信場景理解。</p>
            </div>
            <div class="info-card">
                <div class="card-icon">🧠</div>
                <div class="kicker">AIOPS</div>
                <h3>異常偵測與營運建議</h3>
                <p>以 Isolation Forest 偵測速度異常，再轉換為營運可讀的影響描述與處置建議。</p>
            </div>
        </div>
        <div class="flow">
            <div class="flow-step"><b>1. 產生資料</b><span>模擬區域與壅塞情境</span></div>
            <div class="flow-step"><b>2. ETL 清洗</b><span>欄位辨識、匿名化、轉型</span></div>
            <div class="flow-step"><b>3. 儲存</b><span>SQLite 與 raw CSV 同步</span></div>
            <div class="flow-step"><b>4. 分析</b><span>圖表、地圖、品質檢查</span></div>
            <div class="flow-step"><b>5. AIOps</b><span>異常中心與決策建議</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not speedtest_df.empty:
        st.markdown('<div class="section-title">速度趨勢快照</div>', unsafe_allow_html=True)
        st.plotly_chart(compact_plotly(InteractiveCharts.create_speedtest_timeline(speedtest_df), 390), width="stretch")


def show_simulator() -> None:
    page_header(
        "🧪",
        "模擬資料產生器",
        "建立可公開展示的 Speedtest 與基地台資料，資料會使用模擬業者名稱，不帶入任何真實營運資料。",
        ["安全 Demo", "CSV", "SQLite"],
    )
    icon_cards(
        [
            ("📶", "測速紀錄", "產生下載、上傳、Ping 與時間序列欄位。"),
            ("🗼", "基地台資料", "產生經緯度、模擬業者、訊號範圍與制式。"),
            ("🧼", "匿名化情境", "只保留流程展示需要的欄位與模擬名稱。"),
            ("🗄️", "一鍵寫入", "同步寫入 raw CSV 與 SQLite 資料庫。"),
        ]
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        rows = st.selectbox("Speedtest 筆數", [30, 60, 120, 300, 500], index=2)
    with col2:
        region = st.selectbox("模擬區域", ["台北", "新北", "台中", "高雄", "全台"], index=0)
    with col3:
        scenario = st.selectbox(
            "模擬情境",
            ["normal", "peak_congestion", "regional_issue", "device_degradation"],
            index=1,
        )

    if st.button("一鍵產生並寫入 Demo 資料", type="primary"):
        seed_demo_data(rows=rows, region=region, scenario=scenario)
        st.success("Demo 資料已建立，已同步寫入 CSV 與 SQLite。")

    st.markdown('<div class="section-title">資料預覽</div>', unsafe_allow_html=True)
    with st.expander("📶 Speedtest 預覽", expanded=True):
        st.dataframe(generate_speedtest(rows=min(rows, 20), region=region, scenario=scenario), width="stretch", hide_index=True, height=300)
    with st.expander("🗼 基地台預覽", expanded=False):
        st.dataframe(generate_cell_towers(rows=20, region=region), width="stretch", hide_index=True, height=300)


def show_cell_tower_map() -> None:
    page_header(
        "🗺️",
        "基地台 GIS 熱力圖",
        "用互動地圖看模擬基地台分布、訊號熱區與模擬業者配置，適合展示地理資料分析流程。",
        ["Folium", "Heatmap", "Operator Mix"],
    )
    df = load_cell_towers()
    if df.empty:
        st.warning("尚無基地台資料，請先產生 demo 資料或匯入 CSV。")
        return

    operators = ["全部"] + sorted(df["operator"].dropna().unique().tolist())
    selected = st.selectbox("模擬業者", operators)
    if selected != "全部":
        df = df[df["operator"] == selected]

    cols = st.columns(3)
    cols[0].metric("🗼 基地台數量", len(df))
    cols[1].metric("🏷️ 模擬業者數", df["operator"].nunique())
    cols[2].metric("📡 平均訊號範圍", _metric_mean(df, "avgRange", "m"))

    from streamlit_folium import st_folium

    center = (float(df["lat"].mean()), float(df["lon"].mean()))
    folium_map = MapCharts.create_folium_map(center=center, zoom=12)
    st_folium(MapCharts.add_heatmap(folium_map, df), height=470, use_container_width=True, returned_objects=[])

    st.markdown('<div class="section-title">模擬業者基地台數量分布</div>', unsafe_allow_html=True)
    st.plotly_chart(compact_plotly(MapCharts.create_operator_distribution(df), 360), width="stretch")
    with st.expander("查看基地台資料"):
        st.dataframe(df, width="stretch", hide_index=True, height=320)


def show_speedtest_analysis() -> None:
    page_header(
        "📶",
        "Speedtest 網路品質",
        "觀察模擬測速資料的下載、上傳、Ping 與尖峰變化，把單筆測試轉成可解讀的品質趨勢。",
        ["Timeline", "Distribution", "Hourly Pattern"],
    )
    df = load_speedtest()
    if df.empty:
        st.warning("尚無 Speedtest 資料，請先產生 demo 資料或匯入 CSV。")
        return

    cols = st.columns(4)
    cols[0].metric("⚡ 平均下載", _metric_mean(df, "download_mbps", "Mbps"))
    cols[1].metric("⬆️ 平均上傳", _metric_mean(df, "upload_mbps", "Mbps"))
    cols[2].metric("⏱️ 平均 Ping", _metric_mean(df, "ping_ms", "ms"))
    cols[3].metric("🧾 測試次數", len(df))

    st.markdown('<div class="section-title">網路速度趨勢</div>', unsafe_allow_html=True)
    st.plotly_chart(compact_plotly(InteractiveCharts.create_speedtest_timeline(df), 410), width="stretch")
    st.markdown('<div class="section-title">速度分布與時段型態</div>', unsafe_allow_html=True)
    st.plotly_chart(compact_plotly(InteractiveCharts.create_speedtest_distribution(df), 380), width="stretch")
    st.plotly_chart(compact_plotly(InteractiveCharts.create_hourly_pattern(df), 380), width="stretch")


def show_aiops_center() -> None:
    page_header(
        "🤖",
        "AIOps 異常中心",
        "把異常偵測結果轉成營運可讀的事件摘要，協助判斷影響、嚴重度與後續處置建議。",
        ["Isolation Forest", "Incident Advisor", "Ops Summary"],
    )
    df = load_speedtest()
    if df.empty:
        st.warning("尚無 Speedtest 資料，請先產生 demo 資料或匯入 CSV。")
        return

    detected = AnomalyDetector(contamination=0.1).detect_speedtest_anomalies(df)
    incidents = IncidentAdvisor().summarize_speedtest(detected)

    st.markdown('<div class="section-title">營運建議</div>', unsafe_allow_html=True)
    incident_html = []
    for item in incidents:
        severity = item.get("severity", "低")
        css = {"高": "incident-high", "中": "incident-mid"}.get(severity, "incident-low")
        icon = {"高": "🚨", "中": "🟠"}.get(severity, "🔵")
        incident_html.append(
            f'<div class="small-card {css}"><div class="icon">{icon}</div><b>{item.get("signal", "營運訊號")}</b><span>嚴重度：{severity}<br>{item.get("impact", "")}<br>建議：{item.get("recommendation", "")}</span></div>'
        )
    incident_cols = min(max(len(incident_html), 1), 3)
    st.markdown(
        f'<div class="small-card-grid" style="grid-template-columns: repeat({incident_cols}, minmax(0, 1fr));">{"".join(incident_html)}</div>',
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-title">異常點</div>', unsafe_allow_html=True)
    anomalies = detected[detected["is_anomaly"] == 1]
    if anomalies.empty:
        st.success("目前未偵測到明顯異常。")
    else:
        with st.expander(f"🔎 查看 {len(anomalies)} 筆異常資料", expanded=True):
            st.dataframe(anomalies, width="stretch", hide_index=True, height=180)

    fig = px.scatter(
        detected,
        x="timestamp",
        y="download_mbps",
        color="is_anomaly",
        size="anomaly_score",
        title="AIOps 異常偵測結果",
    )
    st.plotly_chart(compact_plotly(fig, 430), width="stretch")


def show_trend_prediction() -> None:
    page_header(
        "📈",
        "趨勢預測",
        "用歷史測速序列預估未來下載速度走向，資料不足時會清楚提示需要補足的筆數。",
        ["Forecast", "Fallback Model", "7 Days"],
    )
    df = load_speedtest()
    if df.empty:
        st.warning("尚無 Speedtest 資料，請先產生 demo 資料或匯入 CSV。")
        return

    if len(df) < 30:
        st.warning(f"目前只有 {len(df)} 筆，建議至少 30 筆。可到「模擬資料產生器」建立 120 筆展示資料。")
        return

    from src.ml.trend_prediction import TrendPredictor

    predictor = TrendPredictor()
    forecast = predictor.forecast_speedtest(df, periods=7)
    if forecast.empty:
        st.warning("預測尚未產生，請確認資料至少 30 筆且包含 timestamp、download_mbps。")
        return

    model_name = forecast["model"].iloc[-1] if "model" in forecast.columns else "Trend Model"
    trend_text = predictor.get_trend_direction(forecast)
    icon_cards(
        [
            ("📊", "預測趨勢", trend_text),
            ("🧠", "使用模型", str(model_name)),
            ("🧾", "歷史筆數", f"{len(df)} 筆測速資料"),
            ("🗓️", "預測區間", "未來 7 天下載速度"),
        ]
    )
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["download_mbps"], mode="lines", name="實際值"))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], mode="lines", name="預測值"))
    fig.update_layout(title="未來 7 天下載速度預測", xaxis_title="時間", yaxis_title="Mbps")
    st.plotly_chart(compact_plotly(fig, 430), width="stretch")


def show_data_quality() -> None:
    page_header(
        "🧹",
        "資料品質檢查",
        "檢查必要欄位、重複資料與數值範圍，先確認資料可靠，再進入圖表與 AIOps 分析。",
        ["Schema Check", "Duplicates", "Range Rules"],
    )
    checker = DataQualityChecker()

    speed_rules = checker.to_dataframe(checker.check_speedtest(load_speedtest()))
    tower_rules = checker.to_dataframe(checker.check_cell_towers(load_cell_towers()))
    quality_cards("📶 Speedtest 品質", speed_rules)
    with st.expander("查看 Speedtest 品質明細"):
        st.dataframe(speed_rules, width="stretch", hide_index=True, height=220)

    quality_cards("🗼 基地台品質", tower_rules)
    with st.expander("查看基地台品質明細"):
        st.dataframe(tower_rules, width="stretch", hide_index=True, height=220)


def show_data_management() -> None:
    page_header(
        "🗄️",
        "ETL 資料管理",
        "上傳 CSV 後自動辨識資料類型，清洗後寫入 SQLite，也能匯出目前 Demo 資料。",
        ["Upload", "Clean", "Export"],
    )
    icon_cards(
        [
            ("📤", "上傳", "拖曳 Speedtest 或基地台 CSV。"),
            ("🔍", "辨識", "依欄位判斷資料類型。"),
            ("🧼", "清洗", "套用型別轉換與匿名化。"),
            ("📦", "報表", "自動產出 CSV、HTML、Markdown、PDF 與 ZIP。"),
        ]
    )
    uploaded_file = st.file_uploader("上傳 CSV 檔案", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success(f"已讀取 {len(df)} 筆資料，辨識為：{detect_uploaded_data_type(df)}")
        with st.expander("📄 查看上傳資料前 30 筆", expanded=True):
            st.dataframe(df.head(30), width="stretch", hide_index=True, height=340)

        if st.button("清洗並寫入資料庫", type="primary"):
            data_label, raw_path, table_name = save_uploaded_data(df)
            st.success(f"已儲存為 {data_label}")
            st.caption(f"CSV：`{raw_path}`｜SQLite：`{table_name}`")

    st.markdown('<div class="section-title">可匯出資料</div>', unsafe_allow_html=True)
    data = DataExtractor().extract_all()

    if st.button("📦 一鍵產出完整報表包", type="primary"):
        files = ReportGenerator().generate_report_package(data)
        zip_path = files["zip"]
        pdf_path = files["pdf_report"]
        html_path = files["html_report"]
        markdown_path = files["markdown_report"]
        st.success(f"已產出報表包：{zip_path.name}")
        st.markdown('<div class="section-title">HTML 報表預覽</div>', unsafe_allow_html=True)
        st.components.v1.html(html_path.read_text(encoding="utf-8"), height=620, scrolling=True)
        with st.expander("📝 Markdown 報告預覽", expanded=False):
            st.markdown(markdown_path.read_text(encoding="utf-8"))
        st.info("PDF 在部分雲端瀏覽器會被內嵌預覽封鎖，請使用下方按鈕下載 PDF 檢視。")
        st.download_button(
            "下載 PDF 報表",
            data=pdf_path.read_bytes(),
            file_name=pdf_path.name,
            mime="application/pdf",
        )
        st.download_button(
            "下載 HTML 報表",
            data=html_path.read_bytes(),
            file_name=html_path.name,
            mime="text/html",
        )
        st.download_button(
            "下載 Markdown 報告",
            data=markdown_path.read_bytes(),
            file_name=markdown_path.name,
            mime="text/markdown",
        )
        st.download_button(
            "下載完整報表包 ZIP",
            data=zip_path.read_bytes(),
            file_name=zip_path.name,
            mime="application/zip",
        )

    for name, df in data.items():
        if df.empty:
            continue
        st.markdown(f'<div class="note-panel">📦 <b>{name}</b>：目前可匯出 {len(df)} 筆資料</div>', unsafe_allow_html=True)
        st.download_button(
            f"下載 {name}.csv",
            data=df.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"{name}.csv",
            mime="text/csv",
        )


def show_portfolio() -> None:
    page_header(
        "📘",
        "作品集專案說明",
        "這個專案說明一個電信資料產品 Demo 如何從模擬資料、ETL、資料庫、視覺化到 AIOps 建議完整運作。",
        ["Portfolio", "Data Product", "Deployable Demo"],
    )
    st.markdown(
        """
        <div class="card-grid">
            <div class="info-card">
                <div class="card-icon">🧭</div>
                <div class="kicker">PROJECT</div>
                <h3>這個專案在做什麼</h3>
                <p>用模擬電信資料建立可公開展示的資料平台，涵蓋資料產生、匯入、清洗、儲存、分析與營運建議。</p>
            </div>
            <div class="info-card">
                <div class="card-icon">🧩</div>
                <div class="kicker">MODULES</div>
                <h3>多頁式資料產品</h3>
                <p>包含總覽、模擬資料、GIS 熱力圖、Speedtest 品質、AIOps 異常、趨勢預測、資料品質與 ETL 管理。</p>
            </div>
            <div class="info-card">
                <div class="card-icon">🚀</div>
                <div class="kicker">DEPLOYMENT</div>
                <h3>GitHub 與 Streamlit Demo</h3>
                <p>專案可推送到 GitHub，並部署到 Streamlit Community Cloud，讓瀏覽器直接開啟互動 Demo。</p>
            </div>
        </div>
        <div class="flow">
            <div class="flow-step"><b>1. 模擬 / 匯入</b><span>產生安全展示資料</span></div>
            <div class="flow-step"><b>2. 欄位辨識</b><span>判斷資料類型</span></div>
            <div class="flow-step"><b>3. 清洗入庫</b><span>pandas + SQLite</span></div>
            <div class="flow-step"><b>4. 視覺分析</b><span>Plotly + Folium</span></div>
            <div class="flow-step"><b>5. AIOps 建議</b><span>異常偵測與說明</span></div>
        </div>
        """
        ,
        unsafe_allow_html=True,
    )


def _metric_mean(df: pd.DataFrame, column: str, unit: str) -> str:
    if df.empty or column not in df.columns:
        return "N/A"
    value = pd.to_numeric(df[column], errors="coerce").mean()
    if pd.isna(value):
        return "N/A"
    return f"{value:.1f} {unit}"


if __name__ == "__main__":
    main()
