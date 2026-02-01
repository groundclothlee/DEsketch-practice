#coding = UTF-8
#202602 DE streamlit速寫小工具 上傳圖片計時

import streamlit as st
import time
from PIL import Image

# 設定網頁標題與寬度組態
st.set_page_config(page_title="速寫練習工具", layout="wide")


def main():
    st.title("線上速寫練習工具")
    st.write("上傳你的圖片資料夾，開始速寫練習！(.jpg, .png)")

    # --- 側邊欄：設定與上傳 ---
    with st.sidebar:
        st.header("1. 上傳圖片")
        uploaded_files = st.file_uploader(
            "請選擇多張圖片",
            type=['jpg', 'jpeg', 'png'],
            accept_multiple_files=True
        )

        st.header("2. 計時")
        if 'log' in st.session_state and st.session_state.log:
            st.write("已完成的練習：")
            for record in st.session_state.log:
                st.text(record)
        else:
            st.write("尚未開始記錄")

    # --- 初始化 Session State (紀錄狀態用) ---
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'log' not in st.session_state:
        st.session_state.log = []

    # --- 主邏輯 ---
    if uploaded_files:
        # 確保索引不超出範圍 (防止刪減圖片後報錯)
        if st.session_state.current_index >= len(uploaded_files):
            st.session_state.current_index = 0

        # 1. 取得當前圖片
        current_file = uploaded_files[st.session_state.current_index]
        image = Image.open(current_file)

        # 2. 開始計時 (如果是剛切換到這張圖)
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()

        # 3. 計算目前經過時間
        elapsed_time = int(time.time() - st.session_state.start_time)
        mins, secs = divmod(elapsed_time, 60)

        # 4. 顯示資訊列 (上方)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.subheader(f"目前進度：{st.session_state.current_index + 1} / {len(uploaded_files)}")
        with col2:
            # 這裡顯示的是「你打開這張圖後經過的時間」
            st.metric(label="⏱️ 本張耗時", value=f"{mins:02}:{secs:02}")
        with col3:
            # 下一張按鈕
            if st.button("下一張 ➡️", use_container_width=True):
                next_image(current_file.name, elapsed_time)

        # 5. 展示圖片
        st.image(image, caption=current_file.name, use_container_width=True)

    else:
        # 如果還沒上傳圖片，顯示引導畫面
        st.info("👈 請先從左側側邊欄上傳圖片以開始練習！")


def next_image(filename, duration):
    """切換到下一張並記錄時間"""
    # 記錄時間
    mins, secs = divmod(duration, 60)
    record = f"{filename}: {mins:02}:{secs:02}"
    st.session_state.log.append(record)

    # 索引 +1
    st.session_state.current_index += 1

    # 重設開始時間，讓下一張圖重新計時
    st.session_state.start_time = None

    # 強制重新執行頁面以更新畫面
    st.rerun()


if __name__ == "__main__":
    main()