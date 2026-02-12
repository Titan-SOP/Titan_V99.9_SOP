# ui_mobile/tab3_hud.py
# Titan V100.0 - Mobile UI: Sniper HUD
# 狀態: 手機版狙擊抬頭顯示器

import streamlit as st

def render():
    st.header("🎯 狙擊鏡")
    
    # Get ticker from home search or locked targets
    ticker = st.session_state.get('mobile_search', 'NVDA').upper()
    
    st.subheader(f"目標: {ticker}")
    
    # Dummy data, would be fetched from data_engine
    price = 924.79
    angle = 78.5
    g_force = 35.2
    
    st.markdown(f"<div class='hud-metric'>{price:.2f}</div>", unsafe_allow_html=True)
    st.markdown("<div class='hud-label'>Current Price (USD)</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"<div class='hud-metric'>{angle}°</div>", unsafe_allow_html=True)
        st.markdown("<div class='hud-label'>3M Angle</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='hud-metric'>{g_force:+.1f}</div>", unsafe_allow_html=True)
        st.markdown("<div class='hud-label'>G-Force</div>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("LOCK ON", type="primary", use_container_width=True):
        st.balloons()
        st.toast(f"{ticker} 已鎖定，移至 AI 參謀部分析！", icon="🚀")