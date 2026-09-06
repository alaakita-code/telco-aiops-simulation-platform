# Telco AIOps Simulation Platform

電信網路模擬數據分析與 AIOps 展示平台。這是一個可放上 GitHub、可部署到 Streamlit Community Cloud，也適合作為作品集展示的互動式專案 Demo。

本專案不使用真實電信商營運資料。所有業者欄位都會轉成「模擬業者 A/B/C」，用於展示資料工程、GIS、網路品質分析、異常偵測、趨勢預測與報告匯出流程。

## Demo 功能

- 營運總覽 Dashboard
- 模擬資料產生器
- 基地台 GIS 熱力圖
- Speedtest 網路品質分析
- AIOps 異常中心
- 趨勢預測
- 資料品質檢查
- ETL 資料管理
- 自動產出 CSV / Markdown / HTML / PDF / ZIP 報表包
- 作品集專案說明頁

## 技術亮點

- Streamlit 多頁式資料產品
- pandas ETL 清洗、匿名化與欄位辨識
- SQLite 本機資料庫
- Folium / Plotly 互動式圖表與地圖
- Isolation Forest 異常偵測
- scikit-learn 線性趨勢預測
- GitHub + Streamlit Community Cloud 免費部署

## 專案結構

```text
telco_aiops_simulation_platform/
├─ app.py
├─ requirements.txt
├─ data/
│  ├─ raw/
│  ├─ processed/
│  ├─ sample/
│  └─ exports/
├─ docs/
├─ src/
│  ├─ aiops/
│  ├─ api/
│  ├─ etl/
│  ├─ ml/
│  ├─ quality/
│  ├─ simulation/
│  └─ visualization/
└─ .streamlit/
```

## 本機執行

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
streamlit run app.py
```

## 趨勢預測模型

為了讓本機與 Streamlit Cloud 更穩定，「趨勢預測」頁預設使用 scikit-learn 的 LinearRegression。這個 Demo 不需要安裝 Prophet，也不會依賴 Stan 後端。

## Streamlit Cloud 部署

完整步驟可看 `DEPLOYMENT.md`。摘要流程如下：

1. 到 GitHub 建立空的 repository，名稱可用 `telco-aiops-simulation-platform`。
2. 本機進入專案資料夾：

```powershell
cd Desktop\telco_aiops_simulation_platform
```

3. 初始化 Git、提交並推送：

```powershell
git init
git add .
git commit -m "Initial telco aiops simulation platform"
git branch -M main
git remote add origin https://github.com/<your-account>/telco-aiops-simulation-platform.git
git push -u origin main
```

4. 到 Streamlit Community Cloud 建立 `New app`。
5. Repository 選此專案。
6. Branch 選 `main`。
7. Main file path 填 `app.py`。
8. 按 `Deploy`。

如果之後有更新程式或文件：

```powershell
git add .
git commit -m "Update Streamlit demo"
git push
```

## 專案展示說明

這個專案用模擬資料展示一個電信網路數據平台如何運作。使用者可以先透過「模擬資料產生器」建立 Speedtest 與基地台資料，也可以從「ETL 資料管理」上傳自己的 CSV。系統會自動辨識資料類型，將資料進行匿名化、欄位清洗與格式轉換，再同步寫入 raw CSV 與 SQLite。

作為作品集專案時，它的重點不是呈現真實營運資料，而是完整展示一個資料產品如何從資料來源、處理流程、分析邏輯到互動式視覺化逐步完成。

資料建立後，平台會提供多種分析與視覺化方式：

- 「營運總覽」用 KPI 卡片呈現目前資料量、平均下載速度、平均 Ping 與異常筆數。
- 「基地台 GIS 熱力圖」用地圖方式呈現模擬基地台分布與熱點。
- 「Speedtest 網路品質」呈現下載、上傳、Ping、時間序列與每小時變化。
- 「AIOps 異常中心」會根據測速資料偵測異常，並產生營運建議。
- 「趨勢預測」會在資料量足夠時預估未來網路速度變化。
- 「資料品質檢查」會檢查必要欄位、重複資料、數值範圍與座標有效性。
- 「ETL 資料管理」提供 CSV 匯入、資料表寫入、CSV 匯出與一鍵報表包產出。

整體流程重點是把原始資料轉成可觀察、可分析、可追蹤的網路品質資訊，讓使用者能清楚看到資料從產生、清洗、儲存、分析到決策建議的完整路徑。

## 自動化報表輸出

在「ETL 資料管理」頁按下「一鍵產出完整報表包」後，系統會在 `data/exports/` 建立一份報表資料夾，並打包成 ZIP。頁面也會直接顯示 PDF 預覽與 PDF 下載按鈕。報表包包含：

- `summary.csv`：核心 KPI 與 AIOps 摘要。
- `telco_aiops_report.md`：適合放入 GitHub 或文件庫的 Markdown 報告。
- `telco_aiops_report.html`：可直接用瀏覽器開啟的視覺化報告。
- `telco_aiops_report.pdf`：可預覽與下載的 PDF 報告。
- `speedtest_export.csv`：Speedtest 匯出資料。
- `cell_towers_export.csv`：基地台匯出資料。
