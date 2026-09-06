# 部署說明

## GitHub

以下步驟適合第一次把本機專案推到 GitHub。

### 1. 確認專案位置

在 PowerShell 先進入解壓縮後的上一層資料夾，再進入專案資料夾：

```powershell
cd telco_aiops_simulation_platform
```

確認目前資料夾內有這些重要檔案：

```powershell
dir
```

至少應該看到：

- `app.py`
- `requirements.txt`
- `README.md`
- `DEPLOYMENT.md`
- `src`
- `data`
- `.streamlit`

### 2. 確認不要上傳的檔案

專案已包含 `.gitignore`，用來避免把本機環境與暫存資料推上 GitHub。推送前建議確認以下內容不要進 GitHub：

- `.venv`
- `__pycache__`
- `*.pyc`
- `.env`
- `data/processed/*.db`
- `data/exports/telco_aiops_report_*`

如果曾經不小心把 `.venv` 加進 Git 追蹤，先執行：

```powershell
git rm -r --cached .venv
```

### 3. 在 GitHub 建立 Repository

1. 開啟 GitHub。
2. 右上角按 `+`。
3. 選擇 `New repository`。
4. Repository name 建議填：

```text
telco-aiops-simulation-platform
```

5. Public / Private 依需求選擇。
6. 不要勾選 `Add a README file`。
7. 不要勾選 `Add .gitignore`。
8. 不要勾選 `Choose a license`。
9. 按 `Create repository`。

> 因為本機專案已經有 `README.md` 與 `.gitignore`，GitHub 端先保持空白會比較單純。

### 4. 第一次提交並推送

在專案根目錄執行：

```powershell
git init
git status
git add .
git commit -m "Initial telco aiops simulation platform"
git branch -M main
git remote add origin https://github.com/<your-account>/telco-aiops-simulation-platform.git
git push -u origin main
```

請把 `<your-account>` 換成自己的 GitHub 帳號。例如：

```powershell
git remote add origin https://github.com/wingsfree/telco-aiops-simulation-platform.git
```

### 5. 推送後確認

回到 GitHub Repository 頁面，重新整理後應該看到：

- `app.py`
- `requirements.txt`
- `README.md`
- `DEPLOYMENT.md`
- `.github/workflows/ci.yml`
- `.streamlit/config.toml`
- `src/`
- `tests/`
- `data/sample/`

GitHub 頁面不應該看到：

- `.venv/`
- `data/processed/telco_data.db`
- `data/exports/telco_aiops_report_*.zip`

### 6. 確認 GitHub Actions 測試

推送完成後，GitHub 會自動執行 `.github/workflows/ci.yml`。

確認方式：

1. 進入 GitHub Repository。
2. 點上方 `Actions`。
3. 選擇最新一筆 `Python CI`。
4. 確認流程顯示綠色勾勾。

GitHub Actions 會執行：

- 安裝 `requirements.txt`
- 編譯核心 Python 檔案
- 執行 `pytest -q`

若 Actions 失敗，先點進失敗步驟查看錯誤訊息。常見原因通常是套件版本、Python 版本或缺少必要檔案。

### 7. 後續更新專案

之後每次修改完程式或文件，可以照這個流程更新 GitHub：

```powershell
git status
git add .
git commit -m "Update Streamlit demo"
git push
```

如果只是修改部署說明，也可以用較明確的 commit message：

```powershell
git commit -m "Add deployment instructions"
```

### 8. 常見 GitHub 推送問題

#### `fatal: remote origin already exists`

代表這個專案已經設定過 GitHub 遠端位置。可以先查看：

```powershell
git remote -v
```

如果網址不對，改成正確的 repository：

```powershell
git remote set-url origin https://github.com/<your-account>/telco-aiops-simulation-platform.git
```

再推送：

```powershell
git push -u origin main
```

#### `src refspec main does not match any`

通常是還沒有 commit。先執行：

```powershell
git add .
git commit -m "Initial telco aiops simulation platform"
git branch -M main
git push -u origin main
```

#### GitHub 要求登入或 Token

如果 PowerShell 推送時要求登入，依畫面提示用瀏覽器登入 GitHub。若要求 Personal Access Token，請到 GitHub 建立 token，權限至少需要能推送 repository，然後把 token 當成密碼貼上。

#### 不小心把大型檔案加入 Git

先確認 `.gitignore` 是否已包含該檔案類型，再取消追蹤：

```powershell
git rm --cached <file-path>
git add .gitignore
git commit -m "Remove generated files from git tracking"
git push
```

## Streamlit Community Cloud

專案推到 GitHub 後，就可以部署到 Streamlit Community Cloud。

### 1. 建立 Streamlit App

```text
New app
Repository: <your-account>/telco-aiops-simulation-platform
Branch: main
Main file path: app.py
```

### 2. 部署設定

建議設定如下：

| 欄位 | 設定 |
| --- | --- |
| Repository | `<your-account>/telco-aiops-simulation-platform` |
| Branch | `main` |
| Main file path | `app.py` |
| Python version | 依 `runtime.txt` 或 `.python-version` |

設定完成後按 `Deploy`。

### 3. 更新後重新部署

之後只要把新版本推到 GitHub：

```powershell
git add .
git commit -m "Update demo"
git push
```

Streamlit Community Cloud 通常會自動重新部署。若畫面沒有更新，可以到 App 管理頁按 `Reboot` 或 `Rerun`。

### 4. Streamlit Cloud 常見問題

#### 找不到 `app.py`

確認部署設定的 `Main file path` 是：

```text
app.py
```

如果 repository 不是直接以專案根目錄上傳，而是多包了一層資料夾，就要改成：

```text
telco_aiops_simulation_platform/app.py
```

#### 套件安裝失敗

確認 GitHub 上有 `requirements.txt`，並且 Streamlit Cloud 使用的是 repository 最新版本。

#### 地圖或資料一開始是空的

先到「模擬資料產生器」建立資料，或到「ETL 資料管理」上傳 CSV。SQLite 會在執行時自動建立，不需要先手動上傳 `.db` 檔。

## 注意事項

- Demo 預設使用模擬資料，不需要 API Key。
- OpenCellID API Key 是選用功能，可在 Streamlit Secrets 設定 `OPENCELLID_API_KEY`。
- 網路掃描功能在雲端環境通常無法掃描使用者本機區網，較適合本機展示。
- SQLite 檔案會在執行時自動建立於 `data/processed/telco_data.db`。
