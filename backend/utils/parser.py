import docx2txt
from pdfminer.high_level import extract_text

def extract_text_from_resume(file):
    filename = file.filename.lower()

    # 先把檔案內容讀出來存成 bytes
    file_bytes = file.file.read()

    if filename.endswith(".pdf"):
        # pdfminer 需要 file-like object
        from io import BytesIO
        text = extract_text(BytesIO(file_bytes))
    elif filename.endswith(".docx"):
        from io import BytesIO
        text = docx2txt.process(BytesIO(file_bytes))
    else:
        # 純文字檔
        text = file_bytes.decode("utf-8", errors="ignore")

    # 避免太長，先截斷
    return text[:8000]
