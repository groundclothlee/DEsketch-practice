#coding = UTF-8
#202602 DE  Gemini AI小光寫的 streamlit速寫小工具 上傳圖片計時
import streamlit as st
import time
from PIL import Image

# 設定網頁標題與寬度組態
st.set_page_config(page_title="速寫練習工具", layout="wide")

# --- CSS 魔法區：強制圖片不超出視窗高度 ---
# 這段 CSS 會限制圖片最大高度為視窗的 70% (70vh)，預留空間給按鈕，確保不用捲動
st.markdown("""
<style>
    div[data-testid="stImage"] img {
        height: auto;
        max-height: 70vh; /* 限制最大高度為視窗的 70% */
        width: auto;
        max-width: 100%;
        object-fit: contain; /* 保持比例完整顯示 */
        margin: 0 auto; /* 置中 */
        display: block;
    }
</style>
""", unsafe_allow_html=True)


def main():
    st.title("🎨 速寫練習工具")

    # --- 初始化 Session State ---
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'time_records' not in st.session_state:
        st.session_state.time_records = {}
    if 'is_running' not in st.session_state:
        st.session_state.is_running = True
    # 新增：上傳元件的 Key，改變這個 Key 就可以強制重設上傳框
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    # --- 側邊欄：設定區 ---
    with st.sidebar:
        st.header("⚙️ 設定與操作")

        # 計時模式開關
        timer_mode = st.toggle("開啟計時模式", value=True)
        if timer_mode != st.session_state.is_running:
            # 切換前若正在計時，先存檔
            if st.session_state.start_time and 'uploaded_files' in locals() and uploaded_files:
                current_file_name = uploaded_files[st.session_state.current_index].name
                save_current_duration(current_file_name)
            st.session_state.is_running = timer_mode
            st.session_state.start_time = None
            st.rerun()

        st.divider()

        # 需求 1: 清除所有檔案按鈕
        # 邏輯：點擊後，讓 uploader_key +1，上傳框就會被視為一個新的元件而重設
        if st.button("❌ 清除所有已上傳檔案", type="secondary"):
            st.session_state.uploader_key += 1
            # 重設其他相關狀態
            st.session_state.current_index = 0
            st.session_state.start_time = None
            st.rerun()

        # 上傳區 (使用動態 Key)
        uploaded_files = st.file_uploader(
            "上傳圖片 (支援多選)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )

        st.divider()

        # 清除紀錄按鈕
        if st.button("🗑️ 清除計時紀錄 (保留檔案)", type="primary"):
            st.session_state.start_time = None
            st.session_state.time_records = {}
            st.rerun()

        st.header("📊 練習統計")
        if st.session_state.time_records:
            st.write("各張圖片累計時間：")
            for filename, seconds in st.session_state.time_records.items():
                mins, secs = divmod(seconds, 60)
                st.text(f"{filename[:10]}... : {mins:02}:{secs:02}")
        else:
            st.write("尚無紀錄")

    # --- 主畫面邏輯 ---
    if uploaded_files:
        # 防呆
        if st.session_state.current_index >= len(uploaded_files):
            st.session_state.current_index = 0

        current_file = uploaded_files[st.session_state.current_index]
        current_filename = current_file.name

        # --- 計時顯示 ---
        display_time = "⏸️ 暫停中"

        if st.session_state.is_running:
            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()

            session_elapsed = int(time.time() - st.session_state.start_time)
            past_total = st.session_state.time_records.get(current_filename, 0)
            total_seconds = past_total + session_elapsed

            mins, secs = divmod(total_seconds, 60)
            display_time = f"⏱️ {mins:02}:{secs:02}"
        else:
            past_total = st.session_state.time_records.get(current_filename, 0)
            mins, secs = divmod(past_total, 60)
            display_time = f"🛑 已累計: {mins:02}:{secs:02}"

        # --- 控制按鈕區 ---
        # 調整比例，讓按鈕集中一點
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

        with col1:
            if st.button("⬅️ 上一張", disabled=(st.session_state.current_index == 0), use_container_width=True):
                if st.session_state.is_running:
                    save_current_duration(current_filename)
                st.session_state.current_index -= 1
                st.session_state.start_time = None
                st.rerun()

        with col2:
            if st.button("下一張 ➡️", disabled=(st.session_state.current_index == len(uploaded_files) - 1),
                         use_container_width=True):
                if st.session_state.is_running:
                    save_current_duration(current_filename)
                st.session_state.current_index += 1
                st.session_state.start_time = None
                st.rerun()

        with col3:
            st.markdown(f"### {display_time}")

        with col4:
            st.caption(f"進度：{st.session_state.current_index + 1} / {len(uploaded_files)} | {current_filename}")

        # --- 圖片顯示區 ---
        image = Image.open(current_file)
        # 這裡不需要 use_container_width=True 了，因為我們已經用上方的 CSS 強制接管了圖片大小
        st.image(image)

    else:
        # 歡迎畫面
        st.info("👈 請從左側選單上傳圖片！")
        st.write("💡 小提示：可以一次選取整個資料夾的所有圖片喔。")


def save_current_duration(filename):
    """累加時間到紀錄中"""
    if st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
        if filename in st.session_state.time_records:
            st.session_state.time_records[filename] += elapsed
        else:
            st.session_state.time_records[filename] = elapsed


if __name__ == "__main__":
    main()