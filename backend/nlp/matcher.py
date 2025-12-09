# backend/nlp/matcher.py
from __future__ import annotations
from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 輕量通用模型（第一次會自動下載）
_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def _ensure_text(s: str | None) -> str:
    return (s or "").strip()


def match_resume_to_jobs(
    resume_text: str,
    jobs: List[Dict[str, Any]],
    top_k: int = 20,
) -> List[Dict[str, Any]]:
    """
    根據履歷文字與職缺描述計算語意相似度，將分數貼回每個職缺並排序後回傳。
    參數 jobs 需含：
      - job_title: str
      - description: str
      - job_url: str (可選，但前端好用)
      - company / location / salary / update_date (可選)
    回傳：原 job 欄位 + score (float)
    """
    ## 準備文本資料
    texts = []
    valid_idx = []
    for i, j in enumerate(jobs):
        desc = _ensure_text(j.get("description"))
        if not desc:
            desc = " ".join(
                filter(
                    None,
                    [
                        _ensure_text(j.get("job_title")),
                        _ensure_text(j.get("company")),
                        _ensure_text(j.get("location")),
                    ],
                )
            )
        texts.append(desc if desc else "N/A")
        valid_idx.append(i)

    ## 向量化
    resume_vec = _model.encode([resume_text], convert_to_numpy=True, normalize_embeddings=True)
    job_vecs = _model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    ## 語意相似度 (semantic_score)
    sims = cosine_similarity(resume_vec, job_vecs)[0]

    ## 關鍵詞相似度 (keyword_score)
    for idx, j in enumerate(jobs):
        job_text = (j.get("description") or "") + " " + (j.get("job_title") or "")
        # 計算關鍵詞交集比例
        resume_words = set(resume_text.lower().split())
        job_words = set(job_text.lower().split())
        overlap = len(resume_words & job_words)
        keyword_score = overlap / (len(resume_words) + 1e-6)  # 避免除 0

        #加權平均結合兩種分數
        semantic_score = float(sims[idx])
        final_score = 0.7 * semantic_score + 0.3 * keyword_score

        j["score"] = round(final_score, 4)

    ranked = sorted(jobs, key=lambda x: x.get("score", 0.0), reverse=True)


    #######################
    top_jobs = ranked[: top_k]

    # ✅ 只印第一名
    if top_jobs:
        print("TOP 1 JOB:", top_jobs[0])

    #######################
    return ranked[: top_k]

