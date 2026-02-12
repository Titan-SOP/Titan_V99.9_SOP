# ui_desktop/tab6_metatrend.py
# Titan V100.0 - Desktop UI: Meta-Trend
# 狀態: 桌面版元趨勢戰法

import streamlit as st
from data_engine import download_full_history
from core_logic import compute_7d_geometry, titan_rating_system, TitanAgentCouncil

def render():
    """Renders the Meta-Trend tab."""
    st.header("🧠 元趨勢戰法 (Meta-Trend)")
    ticker = st.text_input("🎯 輸入分析標的", value="TSLA", key="desktop_meta_ticker")

    if st.button("啟動掃描", key="desktop_meta_scan"):
        _, df_monthly = download_full_history(ticker)
        geo = compute_7d_geometry(df_monthly)
        rating = titan_rating_system(geo)
        st.session_state['desktop_geo'] = geo
        st.session_state['desktop_rating'] = rating

    if 'desktop_geo' in st.session_state:
        geo = st.session_state['desktop_geo']
        rating = st.session_state['desktop_rating']
        
        st.metric(f"信評: {rating[0]} - {rating[1]}", f"{geo['3M']['angle']}°", delta=f"{geo['acceleration']}° G力")
        
        with st.expander("戰略工廠"):
            api_key = st.session_state.get('api_key')
            if not api_key:
                st.warning("請在側邊欄輸入 Gemini API Key 以啟用 AI 參謀。")
            else:
                council = TitanAgentCouncil(api_key)
                if st.button("召喚 AI 參謀團"):
                    with st.spinner("AI 辯論中..."):
                        # Dummy data for demonstration
                        response = council.run_debate(ticker, 180.0, geo, rating)
                        st.markdown(response)