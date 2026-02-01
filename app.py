#coding = UTF-8
#202602 DE AI寫的 streamlit速寫小工具 上傳圖片計時
import streamlit as st
import time
from PIL import Image

# 設定網頁標題與寬度組態
st.set_page_config(page_title="速寫練習工具", layout="wide")


def main():
    st.title("🎨 速寫練習工具")

    # --- 初始化 Session State ---
    # current_index: 目前看到第幾張
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    # start_time: 開始看這張圖的時間點
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    # time_records: 使用字典來儲存每張圖的「累計」時間 {檔名: 秒數}
    if 'time_records' not in st.session_state:
        st.session_state.time_records = {}
    # is_running: 計時器是否正在跑 (對應暫停需求)
    if 'is_running' not in st.session_state:
        st.session_state.is_running = True

    # --- 側邊欄：設定區 ---
    with st.sidebar:
        st.header("⚙️ 設定與上傳")

        # 需求 4: 全部停止計時 (開關)
        timer_mode = st.toggle("開啟計時模式", value=True)
        # 如果切換開關，更新狀態
        if timer_mode != st.session_state.is_running:
            # 切換瞬間若正在計時，先結算當前時間以免遺失
            if st.session_state.start_time and uploaded_files:
                current_file_name = uploaded_files[st.session_state.current_index].name
                save_current_duration(current_file_name)
            st.session_state.is_running = timer_mode
            st.session_state.start_time = None  # 重設開始點
            st.rerun()

        st.divider()

        uploaded_files = st.file_uploader(
            "1. 上傳圖片 (支援多選)",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True
        )

        st.divider()

        # 需求 3: 全部清除按鈕
        if st.button("🗑️ 清除所有紀錄與重設", type="primary"):
            st.session_state.current_index = 0
            st.session_state.start_time = None
            st.session_state.time_records = {}
            st.rerun()

        st.header("📊 練習統計")
        if st.session_state.time_records:
            st.write("各張圖片累計時間：")
            for filename, seconds in st.session_state.time_records.items():
                mins, secs = divmod(seconds, 60)
                st.text(f"{filename[:15]}... : {mins:02}:{secs:02}")
        else:
            st.write("尚無紀錄")

    # --- 主畫面邏輯 ---
    if uploaded_files:
        # 防呆：確保索引不超出範圍
        if st.session_state.current_index >= len(uploaded_files):
            st.session_state.current_index = 0

        current_file = uploaded_files[st.session_state.current_index]
        current_filename = current_file.name

        # --- 計時邏輯 ---
        display_time = "⏸️ 暫停中"

        if st.session_state.is_running:
            # 如果還沒開始計時，現在開始
            if st.session_state.start_time is None:
                st.session_state.start_time = time.time()

            # 計算「這一輪」經過的時間
            session_elapsed = int(time.time() - st.session_state.start_time)

            # 加上「過去累計」的時間 (需求 2)
            past_total = st.session_state.time_records.get(current_filename, 0)
            total_seconds = past_total + session_elapsed

            mins, secs = divmod(total_seconds, 60)
            display_time = f"⏱️ {mins:02}:{secs:02}"
        else:
            # 停止計時模式，只顯示過去紀錄
            past_total = st.session_state.time_records.get(current_filename, 0)
            mins, secs = divmod(past_total, 60)
            display_time = f"🛑 已累計: {mins:02}:{secs:02}"

        # --- 控制按鈕區 (放在圖片上方，符合需求 1 的操作便利性) ---
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

        with col1:
            # 上一張按鈕
            if st.button("⬅️ 上一張", disabled=(st.session_state.current_index == 0), use_container_width=True):
                if st.session_state.is_running:
                    save_current_duration(current_filename)
                st.session_state.current_index -= 1
                st.session_state.start_time = None  # 重設這一輪計時
                st.rerun()

        with col2:
            # 下一張按鈕
            if st.button("下一張 ➡️", disabled=(st.session_state.current_index == len(uploaded_files) - 1),
                         use_container_width=True):
                if st.session_state.is_running:
                    save_current_duration(current_filename)
                st.session_state.current_index += 1
                st.session_state.start_time = None
                st.rerun()

        with col3:
            # 顯示時間
            st.markdown(f"### {display_time}")

        with col4:
            st.caption(
                f"目前進度：{st.session_state.current_index + 1} / {len(uploaded_files)} | 檔名: {current_filename}")

        # --- 圖片顯示區 ---
        image = Image.open(current_file)
        # 需求 1: use_container_width=True 會讓圖片寬度填滿欄位，高度自動依比例縮放
        st.image(image, use_container_width=True)

    else:
        st.info("👈 請從左側選單上傳圖片開始練習！")


def save_current_duration(filename):
    """將當前這一次的練習時間累加到總紀錄中"""
    if st.session_state.start_time:
        elapsed = int(time.time() - st.session_state.start_time)
        if filename in st.session_state.time_records:
            st.session_state.time_records[filename] += elapsed
        else:
            st.session_state.time_records[filename] = elapsed


if __name__ == "__main__":
    main()