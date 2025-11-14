# backend/nlp/matcher.py
from __future__ import annotations
from typing import List, Dict, Any

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 輕量通用模型（第一次會自動下載）
_model = SentenceTransformer("all-MiniLM-L6-v2")


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
    # 準備描述文本；若描述缺失，用 job_title/company 當備援，避免空字串導致全 0
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

    # 向量化
    resume_vec = _model.encode([resume_text], convert_to_numpy=True, normalize_embeddings=True)
    job_vecs = _model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    # 相似度（cosine）
    sims = cosine_similarity(resume_vec, job_vecs)[0]  # shape: (n_jobs,)

    # 把分數貼回原物件
    for idx, score in zip(valid_idx, sims):
        jobs[idx]["score"] = float(round(float(score), 4))

    # 依分數排序並截取 top_k
    ranked = sorted(jobs, key=lambda x: x.get("score", 0.0), reverse=True)
    return ranked[: top_k]

