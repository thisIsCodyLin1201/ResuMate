# backend/crawler/crawler_104.py
# -*- coding: utf-8 -*-
"""
104 職缺爬取（使用其公開 JSON 介面）

主要方法
--------
get_jobs_data(keyword="資料分析", pages=1, area=None, industry=None, fetch_detail=True)

參數
----
keyword : str
    搜尋關鍵字（例如 "資料分析", "產品經理"）
pages : int
    要抓的頁數（安全上限 10 頁）
area : Optional[str]
    地區代碼（例如：台北市 "6001001000"；可由後端 map 或前端直接傳代碼）
industry : Optional[str]
    產業代碼（例如：軟體/網路相關 "1002000000"）
fetch_detail : bool
    是否補抓內頁 Ajax 以取得完整職缺描述（較慢，但資訊完整）

回傳
----
List[Dict]，每筆至少包含：
{
  "job_title": str,
  "description": str,
  "job_url": str,
  "company": str,
  "location": str,
  "salary": str,
  "update_date": str
}

注意
----
- 請尊重網站使用條款，控制請求頻率。
- 若遇到 429/5xx 會自動重試；仍失敗則略過該筆。
"""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter, Retry

# 104 搜尋清單與內頁 Ajax 端點
SEARCH_API = "https://www.104.com.tw/jobs/search/list"
DETAIL_API = "https://www.104.com.tw/job/ajax/content/{jobNo}"

__all__ = ["get_jobs_data"]


# ---------------------------
# Session / HTTP utilities
# ---------------------------
def _build_session() -> requests.Session:
    s = requests.Session()
    retries = Retry(
        total=3, backoff_factor=0.6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset({"GET"}),
    )
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.mount("http://", HTTPAdapter(max_retries=retries))
    s.headers.update({
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/118.0.0.0 Safari/537.36"),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "Origin": "https://www.104.com.tw",
        "Referer": "https://www.104.com.tw/jobs/search/",
    })
    return s


def _search_page(session, keyword, page, area=None, industry=None):
    params = {
        "ro": "0", "kwop": "7", "keyword": keyword,
        "order": "11", "asc": "0", "page": str(page),
        "mode": "s", "jobsource": "2018indexpoc",
    }
    if area:     params["area"] = area
    if industry: params["indcat"] = industry
    print(f"[104] using indcat = {industry}")

    r = session.get(SEARCH_API, params=params, timeout=12)
    if not r.ok:
        print(f"[104] search non-200: {r.status_code}")
        return {"data": {"list": []}}

    ctype = r.headers.get("content-type", "")
    if "application/json" not in ctype:
        print("[104] unexpected content-type:", ctype)
        print("[104] first 200 chars:", r.text[:200])
        return {"data": {"list": []}}

    try:
        return r.json()
    except Exception as e:
        print("[104] json decode error:", e)
        print("[104] first 200 chars:", r.text[:200])
        return {"data": {"list": []}}



def _fetch_description(session, job_no):
    try:
        r = session.get(
            DETAIL_API.format(jobNo=job_no),
            headers={"Referer": f"https://www.104.com.tw/job/{job_no}"},
            timeout=12,
        )
        if not r.ok:
            print("[104] detail non-200:", r.status_code)
            return ""
        if "application/json" not in r.headers.get("content-type", ""):
            print("[104] detail unexpected content-type:", r.headers.get("content-type"))
            return ""
        data = r.json().get("data", {}) or {}
        detail = data.get("jobDetail", {}) or data
        return detail.get("jobDescription") or ""
    except Exception as e:
        print("[104] detail fetch error:", e)
        return ""



# ---------------------------
# Public API
# ---------------------------

def get_jobs_data(
    keyword: str = "資料分析",
    pages: int = 1,
    *,
    area: Optional[str] = None,
    industry: Optional[str] = None,
    fetch_detail: bool = True,
    per_item_delay: float = 0.4,
    per_page_delay: float = 0.6,
) -> List[Dict[str, Any]]:
    """
    以關鍵字（可含地區/產業過濾）抓取 104 職缺清單，並可選擇補抓內頁描述。

    回傳每筆至少包含：
    {
      "job_title": str,
      "description": str,
      "job_url": str | None,
      "company": str | None,
      "location": str | None,
      "salary": str | None,
      "update_date": str | None,
    }
    """
    session = _build_session()
    results: List[Dict[str, Any]] = []

    # 安全上限，避免打太多
    pages = max(1, min(int(pages or 1), 10))

    for p in range(1, pages + 1):
        try:
            payload = _search_page(session, keyword, p, area=area, industry=industry)
        except Exception as e:
            print(f"[104] search page {p} error: {e}")
            continue

        data = (payload or {}).get("data", {}) or {}
        items = data.get("list", []) or []

        for it in items:
            try:
                # ---- 1) 解析 job_no & 正確 job_url ----
                link_info = it.get("link") or {}
                job_path = link_info.get("job", "") or ""

                job_no: Optional[str] = None

                # 優先從 link.job 拿真正網址用的那段（例如 /job/7y92b?jobsource=xxx）
                if job_path:
                    # 去掉 query string，只留 /job/7y92b
                    job_path_no_q = job_path.split("?", 1)[0]
                    # 取最後一段當 job_no：7y92b
                    job_no = job_path_no_q.rstrip("/").split("/")[-1]

                # 如果 link.job 抓不到，再退回用 jobNo（通常是數字 ID）
                if not job_no:
                    raw_no = it.get("jobNo")
                    if raw_no is not None:
                        job_no = str(raw_no).strip() or None

                job_url = f"https://www.104.com.tw/job/{job_no}" if job_no else None

                # ---- 2) 先嘗試抓完整描述；失敗則用清單摘要備援 ----
                description = ""
                if fetch_detail and job_no:
                    description = _fetch_description(session, job_no) or ""
                if not description:
                    description = (
                        it.get("description")
                        or it.get("jobDescription")
                        or ""
                    )

                # ---- 3) 組裝結果 ----
                results.append(
                    {
                        "job_title": it.get("jobName"),
                        "description": description or "",
                        "job_url": job_url,
                        "company": it.get("custName"),
                        "location": it.get("jobAddrNoDesc"),
                        "salary": it.get("salaryDesc"),
                        "update_date": it.get("appearDate"),
                    }
                )

                # 禮貌性節流（每筆）
                time.sleep(per_item_delay + random.random() * 0.4)

            except Exception as e:
                print(f"[104] parse item error: {e}")
                continue

        # 換頁再等一下
        time.sleep(per_page_delay + random.random() * 0.5)

    return results






