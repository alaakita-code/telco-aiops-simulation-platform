"""Rule-based AIOps advisor for simulated telco data."""

import pandas as pd


class IncidentAdvisor:
    """Convert analysis signals into operation-friendly recommendations."""

    def summarize_speedtest(self, df: pd.DataFrame) -> list[dict]:
        if df.empty:
            return [{
                "severity": "低",
                "signal": "無測速資料",
                "impact": "暫無法判斷網路品質",
                "recommendation": "先產生或匯入模擬 Speedtest 資料",
            }]

        download_avg = pd.to_numeric(df.get("download_mbps"), errors="coerce").mean()
        upload_avg = pd.to_numeric(df.get("upload_mbps"), errors="coerce").mean()
        ping_avg = pd.to_numeric(df.get("ping_ms"), errors="coerce").mean()
        anomaly_rate = float(df.get("is_anomaly", pd.Series([0] * len(df))).mean() * 100)

        incidents = []
        if download_avg < 60:
            incidents.append(self._item("高", "平均下載速度偏低", "使用者下載體驗可能下降", "比對尖峰時段與區域分布，優先檢查容量壓力"))
        if upload_avg < 15:
            incidents.append(self._item("中", "平均上傳速度偏低", "視訊會議與上傳作業可能受影響", "檢查上行干擾、設備負載與測試位置"))
        if ping_avg > 60:
            incidents.append(self._item("中", "平均延遲偏高", "互動式服務體驗可能變差", "檢查路由、回程鏈路與尖峰流量"))
        if anomaly_rate >= 10:
            incidents.append(self._item("高", "異常比例偏高", "品質波動可能已影響多筆測試", "針對異常點做時間與區域交叉分析"))

        if not incidents:
            incidents.append(self._item("低", "整體品質穩定", "目前模擬資料未顯示明顯風險", "持續累積資料並觀察趨勢變化"))

        return incidents

    @staticmethod
    def _item(severity: str, signal: str, impact: str, recommendation: str) -> dict:
        return {
            "severity": severity,
            "signal": signal,
            "impact": impact,
            "recommendation": recommendation,
        }
