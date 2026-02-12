# ui_mobile/tab1_home.py
# Titan V100.0 - Mobile UI: Home Screen
# 狀態: 手機版首頁

import streamlit as st
from utils_ui import load_lottie_url, LOTTIE_ANIMATIONS
from data_engine import DataMacroRiskEngine
from core_logic import compute_7d_geometry
from data_engine import download_full_history

@st.cache_resource
def get_macro_weather():
    engine = DataMacroRiskEngine()
    vix_df = engine.get_single_stock_data("^VIX", period="5d")
    if not vix_df.empty:
        return vix_df['Close'].iloc[-1]
    return 20 # Default

def render():
    st.title("Titan 指揮所")

    # Spotlight Search
    st.text_input("🔍 搜尋全球標的...", placeholder="例如: NVDA, 2330, BTC-USD", key="mobile_search")

    # Macro Weather
    vix = get_macro_weather()
    st.markdown("---")
    st.subheader("今日市場氣象")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        if vix < 20:
            st_lottie(load_lottie_url(LOTTIE_ANIMATIONS["sun"]), height=100, key="sun")
        else:
            st_lottie(load_lottie_url(LOTTIE_ANIMATIONS["storm"]), height=100, key="storm")
    with col2:
        status = "風平浪靜" if vix < 20 else "市場風暴"
        st.metric(label="VIX 恐慌指數", value=f"{vix:.2f}", delta=status)

    # Opportunity Carousel (Dummy data for demonstration)
    st.markdown("---")
    st.subheader("🔥 今日機會")
    
    # In a real app, this would come from the core_logic scan results
    top_picks = ["NVDA", "TSM", "2330.TW"]
    
    cols = st.columns(len(top_picks))
    for i, ticker in enumerate(top_picks):
        with cols[i]:
            with st.container(border=True):
                 st.markdown(f"**{ticker}**")
                 # Simulate fetching geometry
                 st.markdown(f"<h3 style='color: #00FF00;'>75°</h3>", unsafe_allow_html=True)
                 if st.button("分析", key=f"analyze_{ticker}"):
                     st.toast(f"正在分析 {ticker}...")