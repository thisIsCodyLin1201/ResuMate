# 先用假資料，之後你再改成真實爬 104

def get_jobs_data(keyword="資料分析", pages=1):
    jobs = [
        {
            "job_name": "資料分析師",
            "company": "遠見科技股份有限公司",
            "description": "負責資料清理、統計分析、儀表板設計，協助業務單位制定決策。"
        },
        {
            "job_name": "數據工程師",
            "company": "智鏈數據有限公司",
            "description": "建立 ETL 管線、資料倉儲架構與雲端資料流處理流程。"
        },
        {
            "job_name": "商業智能分析師",
            "company": "耀光電商股份有限公司",
            "description": "利用 Power BI / Tableau 製作銷售與顧客行為分析報表。"
        },
        {
            "job_name": "機器學習工程師",
            "company": "鼎盛科技股份有限公司",
            "description": "負責模型訓練、特徵工程與模型部署，優化推薦系統。"
        },
        {
            "job_name": "行銷數據分析專員",
            "company": "聯信整合行銷顧問公司",
            "description": "分析廣告投放與轉換成效，設計 A/B 測試並優化行銷策略。"
        },
        {
            "job_name": "AI 研究員",
            "company": "未來智研中心",
            "description": "參與 AI 模型研究與開發，探索生成式 AI 在企業場景的應用。"
        },
        {
            "job_name": "風險管理分析師",
            "company": "華泰金融控股公司",
            "description": "建立信用風險模型，監控金融產品風險與客戶行為模式。"
        },
        {
            "job_name": "資料科學家",
            "company": "群策智能股份有限公司",
            "description": "整合多來源資料，利用機器學習演算法發掘商業洞察。"
        },
        {
            "job_name": "產品數據分析師",
            "company": "優品生活科技有限公司",
            "description": "分析使用者行為與產品轉換率，提出產品優化建議。"
        },
        {
            "job_name": "財務資料分析師",
            "company": "宏信資產管理公司",
            "description": "負責財務報表分析、預測模型建構與財務儀表板維護。"
        },
        {
            "job_name": "資料工程實習生",
            "company": "星聯雲端科技",
            "description": "協助團隊撰寫資料處理腳本與自動化 ETL 流程。"
        },
        {
            "job_name": "顧客洞察分析師",
            "company": "幸福購物網股份有限公司",
            "description": "進行顧客分群與流失分析，提出行銷留存策略。"
        },
        {
            "job_name": "商業分析顧問",
            "company": "銳智顧問有限公司",
            "description": "協助企業導入數據分析流程與報表自動化專案。"
        },
        {
            "job_name": "演算法工程師",
            "company": "研智科技股份有限公司",
            "description": "設計與實作推薦系統演算法，提升用戶點擊率。"
        },
        {
            "job_name": "資料視覺化工程師",
            "company": "虹映互動媒體",
            "description": "開發互動式資料可視化平台，支援決策儀表板建構。"
        },
        {
            "job_name": "行銷資料策略專員",
            "company": "信達廣告行銷公司",
            "description": "結合數據洞察規劃品牌策略與跨平台廣告投放。"
        },
        {
            "job_name": "資料品質管理師",
            "company": "頂誠資訊服務股份有限公司",
            "description": "負責資料清理、驗證與一致性檢查，確保資料正確性。"
        },
        {
            "job_name": "AI 應用開發工程師",
            "company": "創科智能科技",
            "description": "開發 NLP 與 CV 模型應用，協助業務流程自動化。"
        },
        {
            "job_name": "電商數據分析師",
            "company": "快購電商股份有限公司",
            "description": "分析訂單、客戶與商品資料，提供營收成長建議。"
        },
        {
            "job_name": "數據策略規劃師",
            "company": "創策數位顧問公司",
            "description": "設計企業數據策略藍圖，建立指標追蹤機制與分析模型。"
        },
    ]
    return jobs
