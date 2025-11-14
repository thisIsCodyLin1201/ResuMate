from __future__ import annotations
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.parser import extract_text_from_resume
from backend.crawler.crawler_104 import get_jobs_data
from backend.nlp.matcher import match_resume_to_jobs

app = FastAPI(title="ResuMate API", version="0.2")

# 若前端非同源，開 CORS（依你的前端來源調整）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "*",  # 開發階段先放寬；上線請改白名單
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 簡易對照表（可日後抽到 config）
AREA_MAP = {
    # 北部
    "台北市": "6001001000",
    "新北市": "6001002000",
    "基隆市": "6001003000",
    "桃園市": "6001004000",
    "新竹市": "6001005000",
    "新竹縣": "6001006000",
    "宜蘭縣": "6001007000",

    # 中部
    "台中市": "6001008000",
    "苗栗縣": "6001009000",
    "彰化縣": "6001010000",
    "南投縣": "6001011000",
    "雲林縣": "6001012000",

    # 南部
    "嘉義市": "6001013000",
    "嘉義縣": "6001014000",
    "台南市": "6001015000",
    "高雄市": "6001016000",
    "屏東縣": "6001018000",

    # 東部 & 離島
    "花蓮縣": "6001019000",
    "台東縣": "6001020000",
    "澎湖縣": "6001021000",
    "金門縣": "6001022000",
    "連江縣": "6001023000",
}
INDUSTRY_MAP = {
    "批發／零售／傳直銷業": "1003000000",
    "文教相關業": "1005000000",
    "大眾傳播相關業": "1006000000",
    "旅遊／休閒／運動業": "1007000000",
    "一般服務業": "1009000000",
    "電子資訊／軟體／半導體相關業": "1001000000",
    "一般製造業": "1002000000",
    "農林漁牧水電資源業": "1014000000", 
    "運輸物流及倉儲": "1010000000",
    "政治宗教及社福相關業": "1013000000",
    "金融投顧及保險業": "1004000000",
    "法律／會計／顧問／研發／設計業": "1008000000",
    "建築工程、空間設計與不動產業": "1011000000",
    "醫療保健及環境衛生業": "1012000000",
    "礦業及土石採取業": "1015000000",
    "住宿／餐飲服務業": "1016000000",



    # "經營/人資類": "2001000000",
    # "行政/總務/法務類": "2002000000",
    # "財會/金融類": "2003000000",
    # "行銷／企劃／專案管理類": "2004000000",
    # "客服／門市／業務／貿易類": "2005000000",
    # "餐飲／旅遊 ／美容美髮類": "2006000000",
    # "資訊軟體系統類": "2007000000",
    # "研發相關類": "2008000000",
    # "生產製造／品管／環衛類": "2009000000",
    # "操作／技術／維修類": "2010000000",
    # "資材／物流／運輸類": "2011000000",
    # "營建／製圖類": "2012000000",
    # "傳播藝術／設計類": "2013000000",
    # "文字／傳媒工作類": "2014000000",
    # "醫療／保健服務類": "2015000000",
    # "學術／教育／輔導類": "2016000000",
    # "軍警消／保全類": "2017000000",
    # "其他職類": "2018000000",
}

@app.get("/")
def root():
    return {"message": "ResuMate API is running."}

@app.get("/filters")
def filters():
    """提供前端下拉選單的地區/產業對照（key -> 104 代碼）。"""
    return {"areas": AREA_MAP, "industries": INDUSTRY_MAP}

@app.post("/match")
async def match_resume(
    file: UploadFile = File(...),
    keyword: str = Query("資料分析"),
    area_key: Optional[str] = Query(None),
    industry_key: Optional[str] = Query(None),
    pages: int = Query(1, ge=1, le=3),
    fetch_detail: bool = Query(False),   # 先用 False 比較穩
    top_k: int = Query(20, ge=1, le=50),
):
    """
    上傳履歷 → 抓取符合 filter 的職缺 → 計算匹配分數。
    回傳每筆包含：
      job_title / job_url / description / company / location / salary / update_date / score
    """
    # 1) 解析履歷
    file.file.seek(0)
    resume_text = extract_text_from_resume(file)
    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail="讀不到履歷文字：請改傳 .txt / .docx，或是可擷取文字的 PDF（非掃描影像）。"
        )

    # 2) 依過濾抓職缺
    area = AREA_MAP.get(area_key) if area_key else None
    ind  = INDUSTRY_MAP.get(industry_key) if industry_key else None

    try:
        jobs = get_jobs_data(
            keyword=keyword,
            pages=pages,
            area=area,
            industry=ind,
            fetch_detail=fetch_detail,
        )
    except Exception as e:
        print("[/match] get_jobs_data error:", e)
        jobs = []

    if not jobs:
        return {"recommendations": []}

    # 3) 匹配排序
    try:
        ranked = match_resume_to_jobs(resume_text, jobs, top_k=top_k)
    except Exception as e:
        print("[/match] matcher error:", e)
        raise HTTPException(status_code=500, detail="匹配計算失敗，請稍後再試。")
    finally:
        try:
            file.file.close()
        except Exception:
            pass

    return {"recommendations": ranked}


