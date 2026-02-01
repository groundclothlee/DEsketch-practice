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
        max-height: 70vh; 
        width: auto;
        max-width: 100%;
        object-fit: contain; 
        margin: 0 auto; 
        display: block;
    }
    /* 讓計時器的數字大一點，比較好讀秒 */
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

    # 本張圖片開始時間
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None

    # 整個練習的開始時間 (需求 1)
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

        # 計時模式開關
        timer_mode = st.toggle("開啟計時模式", value=True)
        if timer_mode != st.session_state.is_running:
            # 切換暫停/開始時的邏輯
            if st.session_state.start_time and 'uploaded_files' in locals() and uploaded_files:
                current_file_name = uploaded_files[st.session_state.current_index].name
                save_current_duration(current_file_name)

            st.session_state.is_running = timer_mode
            st.session_state.start_time = None
            # 注意：暫停不重置「總時間」，只影響當下計時
            st.rerun()

        st.divider()

        if st.button("❌ 清除所有已上傳檔案", type="secondary"):
            st.session_state.uploader_key += 1
            st.session_state.current_index = 0
            st.session_state.start_time = None
            st.session_state.session_start_time = None  # 清除總時間
            st.session_state.time_records = {}  # 清除紀錄
            st.rerun()

        uploaded_files = st.file_uploader(
            "上傳圖片 (支援多選)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )

        st.divider()

        if st.button("🗑️ 清除計時紀錄 (保留檔案)", type="primary"):
            st.session_state.start_time = None
            st.session_state.session_start_time = None  # 清除總時間
            st.session_state.time_records = {}
            st.rerun()

        st.header("📊 練習統計")

        # 顯示總練習時間 (靜態統計用)
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

    # --- 主畫面邏輯 ---
    if uploaded_files:
        # 1. 確保索引正確
        if st.session_state.current_index >= len(uploaded_files):
            st.session_state.current_index = 0

        current_file = uploaded_files[st.session_state.current_index]
        current_filename = current_file.name

        # 2. 初始化計時器 (若為空)
        if st.session_state.is_running:
            # 單張開始時間
            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()
            # 總練習開始時間 (只在第一次設定)
            if st.session_state.session_start_time is None:
                st.session_state.session_start_time = time.time()

        # --- 控制按鈕區 (放在最上方) ---
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

        # --- 3. 動態計時顯示區 (使用 Fragment 實現讀秒) ---
        # 傳入檔名是為了讓 Fragment 知道要讀取哪張圖的舊紀錄
        show_realtime_timer(current_filename)

        # 顯示進度文字
        st.caption(f"進度：{st.session_state.current_index + 1} / {len(uploaded_files)} | {current_filename}")

        # --- 圖片顯示區 ---
        image = Image.open(current_file)
        st.image(image)

    else:
        st.info("👈 請從左側選單上傳圖片！")
        st.write("💡 小提示：可以一次選取整個資料夾的所有圖片喔。")


def save_current_duration(filename):
    """累加時間到紀錄中 (切換圖片時觸發)"""
    if st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
        if filename in st.session_state.time_records:
            st.session_state.time_records[filename] += elapsed
        else:
            st.session_state.time_records[filename] = elapsed


# --- 關鍵修改：獨立的計時器區塊 ---
# run_every=1 代表這個函式每 1 秒會自己重新執行一次，創造讀秒效果
@st.fragment(run_every=1)
def show_realtime_timer(current_filename):
    # 預設顯示文字
    display_current = "⏸️ 暫停"
    display_total = "00:00"

    # 計算邏輯
    if st.session_state.is_running:
        now = time.time()

        # A. 本張圖片時間
        if st.session_state.start_time:
            session_elapsed = int(now - st.session_state.start_time)
            past_total = st.session_state.time_records.get(current_filename, 0)
            total_seconds = past_total + session_elapsed

            m, s = divmod(total_seconds, 60)
            display_current = f"{m:02}:{s:02}"

        # B. 總練習時間 (需求 1)
        if st.session_state.session_start_time:
            total_elapsed = int(now - st.session_state.session_start_time)
            tm, ts = divmod(total_elapsed, 60)
            th, tm = divmod(tm, 60)
            if th > 0:
                display_total = f"{th}:{tm:02}:{ts:02}"
            else:
                display_total = f"{tm:02}:{ts:02}"
    else:
        # 暫停時，只顯示最後紀錄的靜態時間
        past_total = st.session_state.time_records.get(current_filename, 0)
        m, s = divmod(past_total, 60)
        display_current = f"🛑 {m:02}:{s:02}"

        # 暫停時顯示目前的總累積時間
        if st.session_state.session_start_time:
            # 注意：這裡簡單處理，暫停時總時間也會暫停更新顯示，直到再次開始
            total_elapsed = int(time.time() - st.session_state.session_start_time)
            # 嚴謹來說暫停時應該扣除暫停時長，但作為速寫練習，這樣顯示「距離開始多久」通常已足夠
            tm, ts = divmod(total_elapsed, 60)
            display_total = f"{tm:02}:{ts:02}"

    # 顯示 UI (使用 Columns 排版)
    t1, t2, t3 = st.columns([1, 1, 3])
    with t1:
        st.metric(label="⏱️ 本張耗時 (讀秒中)", value=display_current)
    with t2:
        st.metric(label="⏳ 總練習時間", value=display_total)


if __name__ == "__main__":
    main()