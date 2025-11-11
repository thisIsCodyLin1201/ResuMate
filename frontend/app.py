import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ResuMate", page_icon="💼", layout="wide")

#layout相關
st.markdown("""
<style>
    /* 主背景顏色 - 白色 */
    .main {
        background-color: white !important;
    }
    
    /* 禁止整個頁面滾動 */
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-height: 100vh;
        overflow: hidden;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    
    /* 隱藏上傳區塊的標籤 */
    .stFileUploader > label {
        display: none !important;
    }
    
    /* 標題區域樣式 */
    .title-section {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        margin-bottom: 20px;
    }
            
    .title-text {
        font-size: 48px;
        font-weight: bold;
    }
    
    .header-buttons {
        display: flex;
        gap: 10px;
    }

    /* 讓左右欄位高度一致且固定 */
    [data-testid="column"] {
        height: 75vh;
        padding: 20px;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    
    /* 左側不滾動 */
    [data-testid="column"]:first-child {
        overflow-y: hidden;
        display: flex;
        flex-direction: column;
    }
    
    /* 右側可滾動 */
    [data-testid="column"]:last-child {
        overflow-y: auto;
        max-height: 75vh;
    }
    
    /* 主要按鈕（開始配對）大小 */
    .stButton > button[kind="primary"] {
        height: 60px !important;
        font-size: 32px !important;
        font-weight: bold !important;
    }
    
    /* 上傳區域樣式 */
    [data-testid="stFileUploader"] {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 20px;
        background-color: white;
        min-height: 150px;
        flex-grow: 1;
    }
    
    /* 職缺卡片樣式 - 統一字體大小 */
    .job-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .job-card h4 {
        font-size: 24px !important;
        margin: 0 0 8px 0 !important;
        color: #333;
    }
    
    .job-card p {
        font-size: 24px !important;
        margin: 4px 0 !important;
        color: #666;
    }
    
    /* 隱藏 Streamlit 的分隔線 */
    hr {
        display: none;
    }
            
    /* 說明文字加大 */
    .s0Markdo8n p {
        font-size: 24px !important;
    }
    
    /* 警告、成功、錯誤訊息字體加大 */
    .stAlert {
        font-size: 20px !important;
    }
    
    .stAlert p {
        font-size: 20px !important;
    }
    
    /* Info 訊息字體加大 */
    .stInfo {
        font-size: 20px !important;
    }
            
    /* 頂部按鈕樣式 */
    button[kind="secondary"] {
        min-width: 140px !important;
        width: 140px !important;
        height: 45px !important;
        font-size: 16px !important;
        padding: 8px 12px !important;
        white-space: nowrap !important;
    }
</style>
""", unsafe_allow_html=True)

# 標題區域 (橘色背景)
st.markdown('<div class="header-section">', unsafe_allow_html=True)

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown('<div class="title-text">💼 ResuMate</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 24px; margin: 0;">上傳你的履歷，我們會幫你找到適合的職缺！</p>', unsafe_allow_html=True)

with header_col2:
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("Historical View", key="btn1", help="歷史記錄"):
            st.info("Historical View 被點擊")
    with btn_col2:
        if st.button("👤", key="btn2", help="使用者"):
            st.info("👤 被點擊")
    with btn_col3:
        if st.button("⚙️", key="btn3", help="設定"):
            st.info("⚙️ 被點擊")

st.markdown('</div>', unsafe_allow_html=True)

# 內容區域 (白色背景)
st.markdown('<div class="content-section">', unsafe_allow_html=True)

left_col, right_col = st.columns([1, 1])

# left：upload area
with left_col:
    #st.subheader("📤 上傳履歷")
    uploaded_file = st.file_uploader("上傳履歷檔案", type=["pdf", "docx", "txt"],label_visibility="collapsed")
    
    if st.button("開始配對", type="primary", use_container_width=True):
        if uploaded_file is not None:
            with st.spinner("正在分析您的履歷..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                res = requests.post(f"{API_URL}/match/", files=files)

                if res.status_code == 200:
                    data = res.json()
                    results = data.get("recommendations", [])
                    st.session_state['results'] = results
                    st.success(f"✅ 找到 {len(results)} 個推薦職缺！")
                else:
                    st.error(f"❌ 後端發生錯誤：{res.status_code}")
        else:
            st.warning("⚠️ 請先上傳履歷檔案")

# right：results display
with right_col:
    if 'results' in st.session_state and st.session_state['results']:
        results = st.session_state['results']
        
        for i, r in enumerate(results, 1):
            st.markdown(f"""
            <div class="job-card">
                <h4>💼 {i}. {r['job']}</h4>
                <p>🏢 公司：{r['company']}</p>
                <p>⭐ 相似度：{r['score']}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("👈 請先上傳履歷並點擊「開始配對」")

st.markdown('</div>', unsafe_allow_html=True)