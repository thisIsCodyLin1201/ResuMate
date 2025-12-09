from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent  # 這個資料夾的絕對路徑

# 定義三個資料庫的完整路徑
RESUME_DB_PATH = BASE_DIR / "resume.db"
JOB_DB_PATH    = BASE_DIR / "job.db"
MATCH_DB_PATH  = BASE_DIR / "match.db"


def get_resume_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(RESUME_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_job_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(JOB_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_match_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(MATCH_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_resume_db() -> None:
    conn = get_resume_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS resumes(
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            filename     TEXT,
            uploaded_at  TEXT, 
            content      TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def init_job_db() -> None:
    conn = get_job_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs(
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            job_no         TEXT UNIQUE,   -- 104 的 job ID
            job_title      TEXT,
            company        TEXT,
            location       TEXT,
            salary         TEXT,
            update_date    TEXT,
            job_url        TEXT,
            keyword        TEXT,
            area           TEXT,
            industry       TEXT,
            condition_json TEXT,          -- 之後要存條件 JSON
            crawled_at     TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def init_match_db() -> None:
    conn = get_match_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS matches(
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id  INTEGER,   -- 對應 resumes.id
            job_no     TEXT,      -- 對應 jobs.job_no
            job_title  TEXT,      -- 對應 jobs.job_title
            company    TEXT,      -- 對應 jobs.company
            score      REAL,
            rank       INTEGER,
            matched_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def init_all_dbs() -> None:
    init_resume_db()
    init_job_db()
    init_match_db()


# 把解析後的履歷文字存進 resume.db
def save_parsed_resume(filename: str, resume_text: str) -> int:
    conn = get_resume_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO resumes (filename, uploaded_at, content)
        VALUES (?, ?, ?)
        """,
        (
            filename,
            datetime.utcnow().isoformat(),
            resume_text,
        ),
    )
    conn.commit()
    resume_id = cur.lastrowid
    conn.close()
    return resume_id


def save_jobs(
    jobs: List[Dict[str, Any]],
    *,
    keyword: str,
    area: Optional[str],
    industry: Optional[str],
) -> int:
    conn = get_job_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    inserted = 0

    for j in jobs:
        job_url = j.get("job_url") or ""
        job_no = job_url.split("/")[-1] if job_url else None

        condition = j.get("condition") or {}
        condition_json = json.dumps(condition, ensure_ascii=False) if condition else None

        try:
            cur.execute(
                """
                INSERT OR IGNORE INTO jobs(
                    job_no, job_title, company, location, salary,
                    update_date, job_url, keyword, area, industry,
                    condition_json, crawled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_no,
                    j.get("job_title"),
                    j.get("company"),
                    j.get("location"),
                    j.get("salary"),
                    j.get("update_date"),
                    job_url,
                    keyword,
                    area,
                    industry,
                    condition_json,
                    now,
                ),
            )
            if cur.rowcount > 0:
                inserted += 1
        except Exception as e:
            print("[job.db insert error]", e)
            continue

    conn.commit()
    conn.close()
    return inserted


def save_match_results(
    resume_id: int,
    ranked_jobs: List[Dict[str, Any]],
) -> int:
    conn = get_match_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    inserted = 0

    for rank, job in enumerate(ranked_jobs, start=1):
        job_url = job.get("job_url") or ""
        job_no = job_url.split("/")[-1] if job_url else None
        score = float(job.get("score") or 0.0)

        cur.execute(
            """
            INSERT INTO matches (resume_id, job_no, job_title, company, score, rank, matched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                resume_id,
                job_no,
                job.get("job_title"),
                job.get("company"),
                score,
                rank,
                now,
            ),
        )
        inserted += 1

    conn.commit()
    conn.close()
    return inserted


