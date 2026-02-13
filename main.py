# main.py
# Titan SOP V100.0 - Main Entry Point (PHASE 1 OVERHAUL)
# CRITICAL FIX: State Initialization + Sidebar Expanded

import streamlit as st
import pandas as pd  # [PHASE 1 FIX] Import pandas
from streamlit_lottie import st_lottie
import time

# [PHASE 1 CRITICAL FIX] Initialize state BEFORE anything else
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# 導入工具函數
try:
    from utils_ui import load_lottie_url, inject_css, get_lottie_animation
except ImportError:
    st.error("❌ 無法導入 utils_ui 模組。請確保 utils_ui.py 在同一目錄下。")
    st.stop()

def import_ui_modules():
    """延遲導入 UI 模組"""
    try:
        from ui_desktop import layout as desktop_layout
        from ui_mobile import layout as mobile_layout
        return desktop_layout, mobile_layout
    except ImportError as e:
        st.warning(f"⚠️ UI 模組尚未完成: {e}")
        return None, None

# ==========================================
# [1] 頁面配置
# ==========================================

st.set_page_config(
    page_title="Titan SOP V100.0 - Ray of Hope",
    layout="wide",
    page_icon="🌅",
    initial_sidebar_state="expanded"  # [PHASE 1 FIX] Changed to expanded
)

# ==========================================
# [2] Session State 初始化
# ==========================================

if 'animation_shown' not in st.session_state:
    st.session_state.animation_shown = False

if 'device_mode' not in st.session_state:
    st.session_state.device_mode = None

if 'choice_confirmed' not in st.session_state:
    st.session_state.choice_confirmed = False

if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

if 'selected_ticker' not in st.session_state:
    st.session_state.selected_ticker = None

# [其餘代碼與上傳的 main.py 相同...]