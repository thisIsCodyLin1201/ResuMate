from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.utils.parser import extract_text_from_resume
from backend.crawler.crawler_104 import get_jobs_data
from backend.nlp.matcher import match_resume_to_jobs
from backend.db import save_parsed_resume, save_jobs, save_match_results

router = APIRouter()

@router.post("/match")
async def match_resume(
    file: UploadFile = File(...),
    keyword: str = Query("資料分析"),
    area_key: Optional[str] = Query(None),
    industry_key: Optional[str] = Query(None),
    pages: int = Query(1, ge=1, le=3),
    #fetch_detail: bool = Query(True), 
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
    
    # ⭐ 1-1) 把解析後的履歷文字存進 resume.db，拿到 resume_id
    resume_id = save_parsed_resume(
        filename=file.filename or "uploaded_resume",
        resume_text=resume_text,
        user_id=None,   # 之後如果有登入系統，可以放使用者 ID
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
    

    # ⭐ 2-1) 把這次爬回來的職缺存進 job.db
    try:
        inserted = save_jobs(jobs, keyword=keyword, area=area, industry=ind)
        print(f"[job.db] inserted {inserted} jobs")
    except Exception as e:
        print("[/match] save_jobs error:", e)



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

    # ⭐ 3-1) 把這次媒合結果存進 match.db
    try:
        count = save_match_results(resume_id, ranked)
        print(f"[match.db] inserted {count} match rows for resume {resume_id}")
    except Exception as e:
        print("[/match] save_match_results error:", e)
    
    
    return {"recommendations": ranked}


