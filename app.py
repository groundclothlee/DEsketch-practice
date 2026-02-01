#coding = UTF-8
#202602 DE  Gemini AI小光寫的 streamlit速寫小工具 上傳圖片計時
import streamlit as st
import time
from PIL import Image

# 設定網頁標題與寬度組態
st.set_page_config(page_title="速寫練習工具", layout="wide")


# --- CSS 魔法區 ---
st.markdown("""
<style>
    div[data-testid="stImage"] img {
        height: auto;
        max-height: 80vh; 
        width: auto;
        max-width: 100%;
        object-fit: contain; 
        margin: 0 auto; 
        display: block;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px;
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
    if 'session_start_time' not in st.session_state:
        st.session_state.session_start_time = None
    if 'time_records' not in st.session_state:
        st.session_state.time_records = {}
    if 'is_running' not in st.session_state:
        st.session_state.is_running = True
    if 'uploader_key' not in st.session_state:
        st.session_state.uploader_key = 0

    # --- 側邊欄：設定區 ---
    with st.sidebar:
        st.header("⚙️ 設定與操作")

        # 1. 先畫出開關 (但還不要處理邏輯)
        # 這裡單純取得使用者目前的開關狀態
        new_timer_mode = st.toggle("開啟計時模式", value=True)

        st.divider()


        uploaded_files = st.file_uploader(
            "上傳圖片 (支援多選)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )
        if st.button("❌ 清除所有已上傳檔案", type="secondary"):
            st.session_state.uploader_key += 1
            st.session_state.current_index = 0
            st.session_state.start_time = None
            st.session_state.session_start_time = None
            st.session_state.time_records = {}
            st.rerun()


        # 這樣就能確保 uploaded_files 已經存在，可以安全存檔
        if new_timer_mode != st.session_state.is_running:
            # 如果正在計時且有檔案，切換前先存檔
            if st.session_state.start_time and uploaded_files:
                # 防呆：確保 index 沒有超出範圍
                if st.session_state.current_index < len(uploaded_files):
                    current_file_name = uploaded_files[st.session_state.current_index].name
                    save_current_duration(current_file_name)

            # 更新狀態
            st.session_state.is_running = new_timer_mode
            st.session_state.start_time = None  # 重設單張計時
            # 這裡移除了 st.rerun()，讓程式繼續往下跑，UI 自然會更新

        st.divider()


        st.header("📊 練習統計")

        if st.session_state.session_start_time:
            total_elapsed = int(time.time() - st.session_state.session_start_time)
            tm, ts = divmod(total_elapsed, 60)
            th, tm = divmod(tm, 60)
            st.caption(f"本次總時長: {th:02}:{tm:02}:{ts:02}")

        if st.session_state.time_records:
            st.write("各張圖片累計：")
            for filename, seconds in st.session_state.time_records.items():
                mins, secs = divmod(seconds, 60)
                st.text(f"{filename[:10]}... : {mins:02}:{secs:02}")
        else:
            st.write("尚無紀錄")


        if st.button("🗑️ 清除計時紀錄", type="primary"):
            st.session_state.start_time = None
            st.session_state.session_start_time = None
            st.session_state.time_records = {}
            st.rerun()

    # --- 主畫面邏輯 ---
    if uploaded_files:
        if st.session_state.current_index >= len(uploaded_files):
            st.session_state.current_index = 0

        current_file = uploaded_files[st.session_state.current_index]
        current_filename = current_file.name

        if st.session_state.is_running:
            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()
            if st.session_state.session_start_time is None:
                st.session_state.session_start_time = time.time()

        col_prev, col_next, col_blank = st.columns([1, 1, 3])

        with col_prev:
            if st.button("⬅️ 上一張", disabled=(st.session_state.current_index == 0), use_container_width=True):
                if st.session_state.is_running:
                    save_current_duration(current_filename)
                st.session_state.current_index -= 1
                st.session_state.start_time = None
                st.rerun()

        with col_next:
            if st.button("下一張 ➡️", disabled=(st.session_state.current_index == len(uploaded_files) - 1),
                         use_container_width=True):
                if st.session_state.is_running:
                    save_current_duration(current_filename)
                st.session_state.current_index += 1
                st.session_state.start_time = None
                st.rerun()

        show_realtime_timer(current_filename)

        st.caption(f"進度：{st.session_state.current_index + 1} / {len(uploaded_files)} | {current_filename}")

        image = Image.open(current_file)
        st.image(image)

    else:
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


@st.fragment(run_every=1)
def show_realtime_timer(current_filename):
    display_current = "⏸️ 暫停"
    display_total = "00:00"

    if st.session_state.is_running:
        now = time.time()

        if st.session_state.start_time:
            session_elapsed = int(now - st.session_state.start_time)
            past_total = st.session_state.time_records.get(current_filename, 0)
            total_seconds = past_total + session_elapsed
            m, s = divmod(total_seconds, 60)
            display_current = f"{m:02}:{s:02}"

        if st.session_state.session_start_time:
            total_elapsed = int(now - st.session_state.session_start_time)
            tm, ts = divmod(total_elapsed, 60)
            th, tm = divmod(tm, 60)
            if th > 0:
                display_total = f"{th}:{tm:02}:{ts:02}"
            else:
                display_total = f"{tm:02}:{ts:02}"
    else:
        past_total = st.session_state.time_records.get(current_filename, 0)
        m, s = divmod(past_total, 60)
        display_current = f"🛑 {m:02}:{s:02}"

        if st.session_state.session_start_time:
            total_elapsed = int(time.time() - st.session_state.session_start_time)
            tm, ts = divmod(total_elapsed, 60)
            display_total = f"{tm:02}:{ts:02}"

    t1, t2, t3 = st.columns([1, 1, 3])
    with t1:
        st.metric(label="⏱️ 本張耗時", value=display_current)
    with t2:
        st.metric(label="⏳ 總練習時間", value=display_total)


if __name__ == "__main__":
    main()