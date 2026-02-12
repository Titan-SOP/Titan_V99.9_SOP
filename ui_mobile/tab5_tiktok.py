# ui_mobile/tab5_tiktok.py
# Titan V100.0 - Mobile UI: Short-form Learning
# 狀態: 手機版短影片學習

import streamlit as st

def render():
    st.header("📚 戰術百科")
    
    concepts = [
        {'title': '87MA 生命線', 'icon': '❤️', 'text': '代表一季的平均成本，股價站上代表趨勢轉多，跌破則轉空。是波段操作的核心指標。'},
        {'title': '284MA 帝王線', 'icon': '👑', 'text': '代表一年的平均成本，是判斷長期牛熊市的分水嶺。87MA 向上穿越 284MA 稱為「黃金交叉」。'},
        {'title': '7D 幾何戰法', 'icon': '📐', 'text': '透過分析不同時間週期的月K線對數斜率，判斷趨勢的強度與加速度，捕捉轉折點。'}
    ]
    
    for concept in concepts:
        with st.container(border=True):
            st.markdown(f"## {concept['icon']} {concept['title']}")
            st.write(concept['text'])