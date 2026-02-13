# ui_desktop/layout.py
# Titan SOP V100.0 - Desktop UI Layout
# Bloomberg Terminal Style Interface

import streamlit as st
import pandas as pd
from utils_ui import inject_css, create_glowing_title
from data_engine import load_cb_data_from_upload

# 導入各個 Tab
from ui_desktop import tab1_macro, tab2_radar, tab3_sniper, tab4_decision, tab5_wiki, tab6_metatrend


def render():
    """
    渲染桌面版 UI
    
    功能：
    - 側邊欄：CB 清單上傳、API Key、返回按鈕
    - 主區域：6 個 Tab
    """
    # 注入桌面版 CSS
    inject_css("desktop")
    
    # 初始化 Session State
    if 'df' not in st.session_state:
        st.session_state.df = pd.DataFrame()
    
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ''
    
    if 'selected_ticker' not in st.session_state:
        st.session_state.selected_ticker = None
    
    # ==========================================
    # 側邊欄設定
    # ==========================================
    
    with st.sidebar:
        st.markdown(create_glowing_title("⚙️ 系統設定"), unsafe_allow_html=True)
        
        # 返回模式選擇按鈕
        if st.button("🔄 切換模式", use_container_width=True):
            st.session_state.device_mode = None
            st.session_state.choice_confirmed = False
            st.rerun()
        
        st.divider()
        
        # ========== CB 清單上傳 ==========
        st.header("📂 CB 資料上傳")
        
        uploaded_file = st.file_uploader(
            "上傳 CB 清單 (Excel/CSV)",
            type=['csv', 'xlsx'],
            help="需包含：代號、名稱、標的股票代號、可轉債市價"
        )
        
        if uploaded_file:
            with st.spinner("正在載入數據..."):
                df = load_cb_data_from_upload(uploaded_file)
                
                if df is not None and not df.empty:
                    st.session_state.df = df
                    st.success(f"✅ 載入 {len(df)} 筆 CB")
                    
                    # 顯示基本統計
                    st.metric("總數量", len(df))
                    if 'close' in df.columns:
                        avg_price = df['close'].mean()
                        st.metric("平均市價", f"{avg_price:.2f}")
        
        st.divider()
        
        # ========== API Key 設定 ==========
        st.header("🔑 AI 功能")
        
        api_key = st.text_input(
            "Gemini API Key (選填)",
            type="password",
            value=st.session_state.api_key,
            help="啟用 AI 辯論功能需要 API Key"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key 已設定")
        
        st.divider()
        
        # ========== 快速清除 ==========
        st.header("🧹 快速操作")
        
        if st.button("清除快取", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ 快取已清除")
            st.rerun()
        
        if st.button("重置數據", use_container_width=True):
            st.session_state.df = pd.DataFrame()
            st.session_state.selected_ticker = None
            st.success("✅ 數據已重置")
            st.rerun()
    
    # ==========================================
    # 主標題
    # ==========================================
    
    st.markdown(
        create_glowing_title("🏛️ Titan SOP V100.0 - Desktop War Room"),
        unsafe_allow_html=True
    )
    
    st.caption("Bloomberg Terminal Style | 專業級可轉債獵殺系統")
    st.markdown("---")
    
    # ==========================================
    # 檢查數據是否已載入
    # ==========================================
    
    if st.session_state.df.empty:
        st.info("👆 請先在側邊欄上傳 CB 清單以開始使用")
        
        # 顯示功能預覽
        st.subheader("📋 功能預覽")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🛡️ 宏觀風控**
            - VIX 恐慌指數
            - 市場信號燈
            - 產業熱圖
            """)
        
        with col2:
            st.markdown("""
            **🏹 獵殺雷達**
            - CB 全景掃描
            - 智慧篩選
            - 即時排序
            """)
        
        with col3:
            st.markdown("""
            **🎯 單兵狙擊**
            - K 線圖表
            - 技術指標
            - 回測引擎
            """)
        
        st.divider()
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            st.markdown("""
            **🚀 全球決策**
            - AI 參謀本部
            - 五大角鬥士
            - 操作指令
            """)
        
        with col5:
            st.markdown("""
            **📚 戰略百科**
            - SOP 知識庫
            - 第一性原則
            - 時間套利
            """)
        
        with col6:
            st.markdown("""
            **🧠 元趨勢戰法**
            - 7D 幾何引擎
            - 22 階信評
            - 獵殺清單
            """)
        
        return
    
    # ==========================================
    # 6 個 Tab
    # ==========================================
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🛡️ 宏觀風控",
        "🏹 獵殺雷達",
        "🎯 單兵狙擊",
        "🚀 全球決策",
        "📚 戰略百科",
        "🧠 元趨勢戰法"
    ])
    
    with tab1:
        tab1_macro.render()
    
    with tab2:
        tab2_radar.render()
    
    with tab3:
        tab3_sniper.render()
    
    with tab4:
        tab4_decision.render()
    
    with tab5:
        render_tab5_placeholder()
    
    with tab6:
        tab6_metatrend.render()


def render_tab5_placeholder():
    """Tab 5 暫時佔位符"""
    st.subheader("📚 戰略百科 (開發中)")
    
    st.info("""
    ### 🚧 功能規劃
    
    **知識庫內容**:
    - SOP 核心策略
    - 20 條第一性原則
    - 時間套利事件
    - 發債故事關鍵字
    
    **未來功能**:
    - 知識庫搜索
    - 策略案例庫
    - 歷史回測資料庫
    """)
