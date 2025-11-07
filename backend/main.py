from fastapi import FastAPI, UploadFile, File
from backend.nlp.matcher import match_resume_to_jobs
from backend.utils.parser import extract_text_from_resume
from backend.crawler.crawler_104 import get_jobs_data

app = FastAPI(title="ResuMate API", version="0.1")

# 模擬職缺資料
jobs_data = get_jobs_data(keyword="資料分析", pages=1)

@app.get("/")
def root():
    return {"message": "ResuMate API is running."}

@app.post("/match/")
async def match_resume(file: UploadFile = File(...)):
    resume_text = extract_text_from_resume(file)
    results = match_resume_to_jobs(resume_text, jobs_data)
    return {"recommendations": results[:5]}
