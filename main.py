# main.py
# Titan SOP V100.0 - Main Entry Point
# 修正：解決 Mobile -> Desktop 的 NoneType 崩潰，並預設展開側邊欄

import streamlit as st
import pandas as pd # 補上 pandas
from streamlit_lottie import st_lottie
import time

# 導入工具函數
try:
    from utils_ui import load_lottie_url, inject_css, get_lottie_animation
except ImportError:
    st.error("❌ 無法導入 utils_ui 模組。請確保 utils_ui.py 在同一目錄下，且包含必要函數。")
    st.stop()

# 導入 UI 模組
def import_ui_modules():
    try:
        from ui_desktop import layout as desktop_layout
        from ui_mobile import layout as mobile_layout
        return desktop_layout, mobile_layout
    except ImportError:
        return None, None

# ==========================================
# [1] 頁面配置 (修正：預設展開側邊欄)
# ==========================================

st.set_page_config(
    page_title="Titan SOP V100.0 - Ray of Hope",
    layout="wide",
    page_icon="🌅",
    initial_sidebar_state="expanded"  # <--- 改為 expanded，確保看得到上傳區
)

# ==========================================
# [2] Session State 初始化 & 消毒
# ==========================================

if 'animation_shown' not in st.session_state:
    st.session_state.animation_shown = False

if 'device_mode' not in st.session_state:
    st.session_state.device_mode = None

# --- 關鍵修正：數據狀態防護罩 ---
# 確保 df 永遠是 DataFrame，防止 Desktop 讀到 Mobile 的 None 而崩潰
if 'df' not in st.session_state or st.session_state.df is None:
    st.session_state.df = pd.DataFrame()

# ==========================================
# [3] CSS 樣式
# ==========================================

MAIN_CSS = """
<style>
    /* 全局背景：深邃宇宙 + 極光流動 */
    .stApp {
        background: radial-gradient(circle at 50% 10%, #1a1a2e 0%, #000000 100%);
        color: #FFFFFF;
    }
    
    /* 隱藏原生元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 呼吸燈標題特效 */
    @keyframes glow {
        0% { text-shadow: 0 0 10px #FFD700, 0 0 20px #FFD700; }
        50% { text-shadow: 0 0 20px #FFA500, 0 0 40px #FF4500; }
        100% { text-shadow: 0 0 10px #FFD700, 0 0 20px #FFD700; }
    }
    
    h1 {
        animation: glow 3s infinite alternate;
        font-family: 'Helvetica Neue', sans-serif;
        letter-spacing: 2px;
    }
    
    /* 選擇卡片：玻璃擬態 (Glassmorphism) */
    .choice-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .choice-card:hover {
        transform: translateY(-10px) scale(1.02);
        border-color: #FFD700;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
        background: rgba(255, 255, 255, 0.1);
    }
    
    .choice-icon {
        font-size: 80px;
        margin-bottom: 20px;
        filter: drop-shadow(0 0 10px rgba(255, 255, 255, 0.5));
    }
    
    .choice-title {
        font-size: 28px;
        font-weight: 700;
        background: -webkit-linear-gradient(#FFD700, #FFA500);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    /* 按鈕美化 */
    div.stButton > button {
        background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
        border: none;
        color: black;
        font-weight: bold;
        transition: all 0.3s;
    }
    div.stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.6);
    }
</style>
"""

# ==========================================
# [4] 日出動畫
# ==========================================

def render_sunrise_animation():
    lottie_url = get_lottie_animation("sunrise")
    lottie_sunrise = load_lottie_url(lottie_url)
    
    st.markdown('<div class="sunrise-container">', unsafe_allow_html=True)
    if lottie_sunrise:
        try:
            st_lottie(lottie_sunrise, speed=1.0, height=300, key="sunrise")
        except:
            st.warning("🌅 [動畫載入中...]") 
    else:
        st.title("🌅 Titan V100.0")
        
    st.markdown("""
        <h1 style='text-align: center; color: #FFD700;'>Titan SOP V100.0</h1>
        <p style='text-align: center; font-size: 1.5rem;'>在混亂的股海中，這是你的希望之光。</p>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 確認進入戰情室", use_container_width=True):
        st.session_state.animation_shown = True
        st.rerun()

# ==========================================
# [5] 設備選擇
# ==========================================

def render_device_selection():
    st.markdown("<h1 style='text-align: center;'>Choose Your Battle Station</h1>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="choice-card">
            <div class="choice-icon">🖥️</div>
            <div class="choice-title">Desktop War Room</div>
            <p>Bloomberg 風格 | 深度分析</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("進入桌面版", key="btn_desktop", use_container_width=True):
            st.session_state.device_mode = "desktop"
            st.session_state.choice_confirmed = True
            st.rerun()
            
    with col2:
        st.markdown("""
        <div class="choice-card">
            <div class="choice-icon">📱</div>
            <div class="choice-title">Mobile Command Post</div>
            <p>Tinder 風格 | 快速獵殺</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("進入手機版", key="btn_mobile", use_container_width=True):
            st.session_state.device_mode = "mobile"
            st.session_state.choice_confirmed = True
            st.rerun()

# ==========================================
# [6] 主路由器
# ==========================================

def render_ui():
    desktop_layout, mobile_layout = import_ui_modules()
    
    # 再次消毒，確保 df 不是 None
    if 'df' not in st.session_state or st.session_state.df is None:
        st.session_state.df = pd.DataFrame()

    if desktop_layout is None or mobile_layout is None:
        st.warning("🚧 系統建構中 (UI Modules Missing)")
        if st.button("🔄 重試"): st.rerun()
        return

    if st.session_state.device_mode == "desktop":
        try:
            inject_css("desktop")
            desktop_layout.render()
        except Exception as e:
            st.error(f"❌ 桌面版崩潰: {e}")
            if st.button("🔄 重啟系統"):
                st.session_state.clear()
                st.rerun()
            
    elif st.session_state.device_mode == "mobile":
        try:
            inject_css("mobile")
            mobile_layout.render()
        except Exception as e:
            st.error(f"❌ 手機版崩潰: {e}")

# ==========================================
# [7] 主程式
# ==========================================

def main():
    if not st.session_state.animation_shown:
        render_sunrise_animation()
        return
    
    if st.session_state.device_mode is None or not st.session_state.choice_confirmed:
        render_device_selection()
        return
    
    render_ui()

if __name__ == "__main__":
    main()