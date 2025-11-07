from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# 載入輕量模型（第一次會自動下載）
model = SentenceTransformer('all-MiniLM-L6-v2')

def match_resume_to_jobs(resume_text, jobs):
    job_texts = [job["description"] for job in jobs]

    # 向量化
    resume_vec = model.encode([resume_text])
    job_vecs = model.encode(job_texts)

    # 計算 cosine similarity
    sims = cosine_similarity(resume_vec, job_vecs)[0]

    ranked = sorted(
        zip(jobs, sims),
        key=lambda x: x[1],
        reverse=True
    )

    results = []
    for job, score in ranked:
        results.append({
            "job": job["job_name"],
            "company": job["company"],
            "score": round(float(score), 3)
        })
    return results
