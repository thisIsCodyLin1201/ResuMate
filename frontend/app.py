# frontend/app.py
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="ResuMate", page_icon="💼", layout="wide")

# ---------- CSS (保留你原本的，略) ----------
st.markdown("""
<style>
    .main {
        background-color: white !important;
    }
    .main .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        max-height: 100vh;
        overflow: hidden;
        padding-left: 0rem;
        padding-right: 0rem;
    }
    .stFileUploader > label {
        display: none !important;
    }
    .header-section {
        background-color: transparent;   /* 或直接刪掉這行 */
        padding: 20px 30px 10px 30px;   /* 看你要不要留一點內距 */
        border-radius: 0;               /* 不要圓角 */
        color: #333;                    /* 文字顏色改回深色 */
    }
    .content-section {
        padding: 10px 30px 30px 30px;
    }
    .title-text {
        font-size: 48px;
        font-weight: bold;
    }
    [data-testid="column"] {
        height: 65vh;
        padding: 20px;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        background-color: #f9f9f9;
    }
    [data-testid="column"]:first-child {
        overflow-y: hidden;
        display: flex;
        flex-direction: column;
    }
    [data-testid="column"]:last-child {
        overflow-y: auto;
        max-height: 65vh;
    }
    .stButton > button[kind="primary"] {
        height: 60px !important;
        font-size: 32px !important;
        font-weight: bold !important;
    }
    [data-testid="stFileUploader"] {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 20px;
        background-color: white;
        min-height: 150px;
        flex-grow: 1;
    }
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
        font-size: 18px !important;
        margin: 4px 0 !important;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# ---------- 標題區（橘色 header） ----------
st.markdown('<div class="header-section">', unsafe_allow_html=True)
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown('<div class="title-text">💼 ResuMate</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 24px; margin: 0;">上傳你的履歷，我們會幫你找到適合的職缺！</p>', unsafe_allow_html=True)

with header_col2:
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    # with btn_col1:
    #     st.button("Historical View", key="btn1", help="歷史記錄")
    # with btn_col2:
    #     st.button("👤", key="btn2", help="使用者")
    # with btn_col3:
    #     st.button("⚙️", key="btn3", help="設定")
st.markdown('</div>', unsafe_allow_html=True)

# ---------- 從後端抓 filter 選項 ----------
@st.cache_data
def load_filters():
    try:
        r = requests.get(f"{API_URL}/filters", timeout=10)
        if r.ok:
            data = r.json()
            return data.get("areas", {}), data.get("industries", {})
    except Exception:
        pass
    return {}, {}

areas_map, industries_map = load_filters()

# human friendly label（現在先直接用 key，之後你可以換成中文）
area_options = ["不限地區"] + list(areas_map.keys())
industry_options = ["不限產業"] + list(industries_map.keys())

st.markdown('<div class="content-section">', unsafe_allow_html=True)

# ---------- 上方 filter 列（對應右邊 wireframe 的欄位） ----------
st.markdown("### 🔍 篩選條件")
fcol1, fcol2, fcol3 = st.columns([2, 1, 1])

with fcol1:
    keyword = st.text_input("關鍵字", value="資料分析")
with fcol2:
    area_choice = st.selectbox("地區", area_options)
    area_key = None if area_choice == "不限地區" else area_choice
with fcol3:
    industry_choice = st.selectbox("產業", industry_options)
    industry_key = None if industry_choice == "不限產業" else industry_choice

# ---------- 左右主內容 ----------
left_col, right_col = st.columns([1, 1])

# 左：上傳履歷 + 按鈕
with left_col:
    uploaded_file = st.file_uploader("上傳履歷檔案", type=["pdf", "docx", "txt"], label_visibility="collapsed")

    if st.button("開始配對", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.warning("⚠️ 請先上傳履歷檔案")
        else:
            with st.spinner("正在分析您的履歷並搜尋職缺..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                params = {
                    "keyword": keyword,
                    "area_key": area_key,
                    "industry_key": industry_key,
                    "pages": 2,           # 想抓幾頁結果可以調整
                    "fetch_detail": False,
                    "top_k": 20,
                }

                # 只有在使用者真的有輸入時，才把 keyword 丟給後端
                if keyword.strip():
                     params["keyword"] = keyword.strip()
                try:
                    res = requests.post(f"{API_URL}/match", files=files, params=params, timeout=180)
                except Exception as e:
                    st.error(f"❌ 無法連線到後端：{e}")
                else:
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state["results"] = data.get("recommendations", [])
                        st.success(f"✅ 找到 {len(st.session_state['results'])} 個推薦職缺！")
                    else:
                        try:
                            detail = res.json().get("detail")
                        except Exception:
                            detail = res.text
                        st.error(f"❌ 後端錯誤 {res.status_code}: {detail}")

# 右：顯示職缺卡片
with right_col:
    results = st.session_state.get("results", [])
    if not results:
        st.info("👈 請先上傳履歷並點擊「開始配對」")
    else:
        st.markdown("### 📝 推薦職缺")
        for i, r in enumerate(results, 1):
            title = r.get("job_title", "未命名職缺")
            company = r.get("company", "未提供公司名稱")
            location = r.get("location", "")
            salary = r.get("salary", "")
            score = r.get("score", 0.0)
            url = r.get("job_url", "#")
            update_date = r.get("update_date", "")

            st.markdown(f"""
            <div class="job-card">
                <h4>{i}. <a href="{url}" target="_blank">{title}</a></h4>
                <p>🏢 公司：{company}</p>
                <p>📍 地點：{location}</p>
                <p>💰 薪資：{salary}</p>
                <p>🕒 更新日期：{update_date}</p>
                <p>⭐ 匹配度：{score:.4f}</p>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
