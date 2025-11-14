# backend/utils/parser.py
from __future__ import annotations
from fastapi import UploadFile
import io, os, tempfile

# txt/docx
try:
    import docx2txt
except Exception:
    docx2txt = None

# pdf 第一優先：pdfminer
try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
except Exception:
    pdfminer_extract_text = None

# pdf 備援：PyPDF2
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None


def _ext(name: str) -> str:
    return os.path.splitext(name or "")[1].lower()


def _pdf_text_pdfminer(raw: bytes) -> str:
    if not pdfminer_extract_text:
        return ""
    # 直接給 bytes
    with io.BytesIO(raw) as bio:
        try:
            txt = pdfminer_extract_text(bio) or ""
            return txt.strip()
        except Exception:
            return ""


def _pdf_text_pypdf2(raw: bytes) -> str:
    if not PdfReader:
        return ""
    try:
        reader = PdfReader(io.BytesIO(raw))
        parts = []
        for p in reader.pages:
            try:
                parts.append(p.extract_text() or "")
            except Exception:
                continue
        return "\n".join(parts).strip()
    except Exception:
        return ""


def extract_text_from_resume(file: UploadFile) -> str:
    """
    支援 txt / docx / pdf（pdf 先用 pdfminer，再退回 PyPDF2）。
    任一流程失敗都回空字串（不拋例外）。
    """
    try:
        file.file.seek(0)
        raw = file.file.read()
        ext = _ext(file.filename or "")

        # txt
        if ext == ".txt":
            try:
                return raw.decode("utf-8")
            except Exception:
                return raw.decode("utf-8", errors="ignore")

        # docx
        if ext == ".docx" and docx2txt:
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=True) as tmp:
                tmp.write(raw); tmp.flush()
                return docx2txt.process(tmp.name) or ""

        # pdf（先 pdfminer，再 PyPDF2）
        if ext == ".pdf":
            txt = _pdf_text_pdfminer(raw)
            if not txt:
                txt = _pdf_text_pypdf2(raw)
            return txt or ""

        # 其他副檔名：當作純文字
        try:
            return raw.decode("utf-8")
        except Exception:
            return raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""



