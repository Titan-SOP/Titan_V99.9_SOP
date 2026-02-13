# ui_mobile/layout.py
# Titan SOP V100.0 - Mobile UI Layout
# Netflix/Robinhood Style Interface

import streamlit as st
from utils_ui import inject_css, create_mobile_nav_bar

# 導入各個 Tab
from ui_mobile import tab1_home, tab2_analysis, tab3_ai


def render():
    """
    渲染移動版 UI
    
    功能：
    - 隱藏側邊欄
    - 底部導航欄
    - 4 個主要部分
    """
    # 注入移動版 CSS
    inject_css("mobile")
    
    # 隱藏側邊欄
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="stHeader"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # 初始化 Session State
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0
    
    if 'mobile_tab' not in st.session_state:
        st.session_state.mobile_tab = "home"
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    # ==========================================
    # 頂部標題
    # ==========================================
    
    st.markdown(
        """
        <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, #1a1a2e 0%, #000000 100%);">
            <h1 style="color: #FFD700; font-size: 36px; margin: 0; text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);">
                ⚔️ Titan SOP
            </h1>
            <p style="color: #AAAAAA; font-size: 14px; margin: 5px 0 0 0;">
                Mobile Command Post
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ==========================================
    # 底部導航欄（簡化版）
    # ==========================================
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # 使用按鈕模擬導航欄
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 首頁", use_container_width=True, 
                    type="primary" if st.session_state.mobile_tab == "home" else "secondary"):
            st.session_state.mobile_tab = "home"
            st.rerun()
    
    with col2:
        if st.button("📊 雷達", use_container_width=True,
                    type="primary" if st.session_state.mobile_tab == "radar" else "secondary"):
            st.session_state.mobile_tab = "radar"
            st.rerun()
    
    with col3:
        if st.button("🤖 AI", use_container_width=True,
                    type="primary" if st.session_state.mobile_tab == "ai" else "secondary"):
            st.session_state.mobile_tab = "ai"
            st.rerun()
    
    with col4:
        if st.button("⚙️ 設定", use_container_width=True,
                    type="primary" if st.session_state.mobile_tab == "settings" else "secondary"):
            st.session_state.mobile_tab = "settings"
            st.rerun()
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # ==========================================
    # 路由到對應的 Tab
    # ==========================================
    
    current_tab = st.session_state.mobile_tab
    
    if current_tab == "home":
        tab1_home.render()
    
    elif current_tab == "radar":
        tab2_analysis.render()
    
    elif current_tab == "ai":
        tab3_ai.render()
    
    elif current_tab == "settings":
        render_settings()
    
    # ==========================================
    # 底部留白（避免被導航欄遮擋）
    # ==========================================
    
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)


def render_settings():
    """
    設定頁面
    """
    st.markdown("### ⚙️ 設定")
    
    # 模式切換
    st.markdown("#### 📱 模式切換")
    
    if st.button("🖥️ 切換到桌面版", use_container_width=True, type="primary"):
        st.session_state.device_mode = None
        st.session_state.choice_confirmed = False
        st.success("✅ 即將切換到桌面版...")
        st.rerun()
    
    st.divider()
    
    # API Key 設定
    st.markdown("#### 🔑 AI 功能")
    
    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=st.session_state.api_key,
        placeholder="輸入 API Key 啟用 AI 功能"
    )
    
    if api_key:
        st.session_state.api_key = api_key
        st.success("✅ API Key 已設定")
    else:
        st.info("💡 提示：輸入 API Key 以啟用 AI 聊天功能")
    
    st.divider()
    
    # 數據管理
    st.markdown("#### 📊 數據管理")
    
    if st.session_state.df is not None:
        st.success(f"✅ 已載入 {len(st.session_state.df)} 筆數據")
    else:
        st.warning("⚠️ 尚未載入數據")
    
    st.info("""
    **💡 如何上傳數據？**
    
    移動版不支援直接上傳。請：
    1. 切換到桌面版
    2. 在側邊欄上傳 CB 清單
    3. 切換回移動版使用
    """)
    
    if st.button("🗑️ 清除所有數據", use_container_width=True):
        st.session_state.df = None
        st.session_state.watchlist = []
        st.session_state.current_index = 0
        st.success("✅ 數據已清除")
        st.rerun()
    
    st.divider()
    
    # 關於
    st.markdown("#### ℹ️ 關於")
    
    st.info("""
    **Titan SOP V100.0**
    
    移動指揮所版本
    
    特色：
    - 🏠 Tinder 滑動介面
    - 📊 簡潔雷達掃描
    - 🤖 AI 聊天助手
    - ⚡ 極速操作體驗
    
    版本：V100.0
    """)
