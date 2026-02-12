# ui_mobile/tab2_swipe.py
# Titan V100.0 - Mobile UI: Swipe Hunter
# 狀態: 手機版滑動獵殺

import streamlit as st

def render():
    st.header("🏹 滑動獵殺")
    
    # Initialize session state for swiping
    if 'swipe_index' not in st.session_state:
        st.session_state.swipe_index = 0
    if 'locked_targets' not in st.session_state:
        st.session_state.locked_targets = []
    
    # Dummy data, would come from a scan
    scan_results = [
        {'ticker': 'NVDA', 'angle': 78.5, 'reason': 'AI 晶片龍頭'},
        {'ticker': 'TSLA', 'angle': -15.2, 'reason': '電動車競爭加劇'},
        {'ticker': 'SMCI', 'angle': 85.1, 'reason': 'AI 伺服器噴射機'}
    ]
    
    # Check if we've run out of stocks
    if st.session_state.swipe_index >= len(scan_results):
        st.success("已完成今日所有標的檢視！")
        st.write("已鎖定目標:", ", ".join(st.session_state.locked_targets))
        return

    current_stock = scan_results[st.session_state.swipe_index]

    with st.container(border=True, height=300):
        st.subheader(current_stock['ticker'])
        st.metric("3個月動能角度", f"{current_stock['angle']}°")
        st.write(current_stock['reason'])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("PASS", use_container_width=True):
            st.session_state.swipe_index += 1
            st.rerun()
    with col2:
        if st.button("LOCK", type="primary", use_container_width=True):
            st.session_state.locked_targets.append(current_stock['ticker'])
            st.session_state.swipe_index += 1
            st.toast(f"已鎖定 {current_stock['ticker']}!", icon="🎯")
            st.rerun()