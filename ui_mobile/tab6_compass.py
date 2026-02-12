# ui_mobile/tab6_compass.py
# Titan V100.0 - Mobile UI: Treasure Hunt
# 狀態: 手機版羅盤尋寶

import streamlit as st
import time
from utils_ui import load_lottie_url, LOTTIE_ANIMATIONS

def render():
    st.header("🧭 羅盤尋寶")
    
    if st.button("開始尋寶 (Scan for >80° Angle)", use_container_width=True):
        with st.spinner("掃描中..."):
            lottie_radar = load_lottie_url(LOTTIE_ANIMATIONS["radar"])
            radar_container = st.empty()
            if lottie_radar:
                with radar_container:
                    st_lottie(lottie_radar, height=300, key="radar_scan")
            
            time.sleep(3) # Simulate scanning
            
            # Found a treasure
            radar_container.empty()
            st.success("發現寶藏！")
            
            lottie_treasure = load_lottie_url(LOTTIE_ANIMATIONS["treasure"])
            if lottie_treasure:
                st_lottie(lottie_treasure, height=300, key="treasure_found")
            
            st.metric("發現標的", "SMCI", delta="85.1° Angle")
            st.balloons()