# ui_desktop/layout.py
# Titan V100.0 - Desktop UI Layout & Router
# 狀態: 桌面版主框架

import streamlit as st
import pandas as pd
from . import tab1_macro, tab2_radar, tab3_sniper, tab4_decision, tab5_wiki, tab6_metatrend
from data_engine import DataMacroRiskEngine, TitanIntelAgency
from core_logic import TitanKnowledgeBase, TitanStrategyEngine

@st.cache_resource
def load_desktop_engines():
    """Load all necessary engines for the desktop UI."""
    kb = TitanKnowledgeBase()
    strategy_engine = TitanStrategyEngine()
    strategy_engine.kb = kb
    macro_engine = DataMacroRiskEngine()
    intel_engine = TitanIntelAgency()
    return kb, strategy_engine, macro_engine, intel_engine

def render():
    """Renders the entire desktop UI including sidebar and tabs."""
    st.markdown('<h1 style="text-align: center;">🏛️ Titan SOP 桌面戰情室</h1>', unsafe_allow_html=True)
    
    kb, strategy_engine, macro_engine, intel_engine = load_desktop_engines()

    # --- Sidebar Logic (migrated from app.py) ---
    with st.sidebar:
        st.header("⚙️ 系統設定")
        if st.button("🔄 清除快取並刷新"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()

        st.divider()
        st.header("📂 CB 資料上傳")
        f_cb_list = st.file_uploader("1. 上傳 CB 清單 (Excel/CSV)", type=['csv','xlsx'])
        if f_cb_list:
            try:
                df = pd.read_excel(f_cb_list) if f_cb_list.name.endswith('.xlsx') else pd.read_csv(f_cb_list)
                # Simplified data cleaning for brevity
                st.session_state['df'] = df
                st.success(f"✅ 載入 {len(df)} 筆 CB")
            except Exception as e:
                st.error(f"檔案讀取失敗: {e}")

        st.divider()
        st.header("🧠 情報獵殺")
        api_key = st.text_input("輸入你的 Gemini API Key (選填)", type="password")
        if api_key:
            st.session_state['api_key'] = api_key
        uploaded_intel_files = st.file_uploader("2. 拖曳情報文件 (PDF, TXT)", type=['pdf', 'txt'], accept_multiple_files=True)
        st.session_state['intel_files'] = uploaded_intel_files

    # --- Main Content Tabs ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🛡️ 宏觀大盤", "🏹 獵殺雷達", "🎯 單兵狙擊", 
        "🚀 全球決策", "📚 戰略百科", "🧠 元趨勢戰法"
    ])

    df = st.session_state.get('df', pd.DataFrame())

    with tab1:
        tab1_macro.render(df, macro_engine, strategy_engine, kb)
    with tab2:
        tab2_radar.render(df, strategy_engine, kb)
    with tab3:
        tab3_sniper.render() # Sniper is self-contained
    with tab4:
        tab4_decision.render()
    with tab5:
        tab5_wiki.render(df, intel_engine, kb)
    with tab6:
        tab6_metatrend.render()