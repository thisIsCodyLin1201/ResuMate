import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("💼 ResuMate - 履歷職缺配對系統")
st.write("上傳你的履歷，我們會幫你找到適合的職缺！")

uploaded_file = st.file_uploader("上傳履歷（PDF / DOCX / TXT）", type=["pdf", "docx", "txt"])

if st.button("開始配對", type="primary") and uploaded_file is not None:
    with st.spinner("分析中，請稍候..."):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        res = requests.post(f"{API_URL}/match/", files=files)

        if res.status_code == 200:
            data = res.json()
            results = data.get("recommendations", [])
            st.success("為你找到以下推薦職缺：")
            for r in results:
                st.write(f"🔹 **{r['job']}** - {r['company']}（相似度：{r['score']}）")
        else:
            st.error(f"後端發生錯誤：{res.status_code}")
elif uploaded_file is None:
    st.info("請先上傳履歷檔案。")