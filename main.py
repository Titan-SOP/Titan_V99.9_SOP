# main.py
# Titan V100.0 - The Soul (Entry Point & Router)
# 狀態: 系統入口

import streamlit as st
import time
from streamlit_lottie import st_lottie
from utils_ui import load_lottie_url, LOTTIE_ANIMATIONS, DESKTOP_CSS
from ui_desktop.layout import render as render_desktop
from ui_mobile.layout import render as render_mobile

# --- Page Configuration (must be the first Streamlit command) ---
st.set_page_config(
    page_title="Titan V100.0",
    layout="wide",
    initial_sidebar_state="auto",
    page_icon="🏛️"
)

def show_intro_animation():
    """Displays the initial animation and manifesto."""
    st.markdown(DESKTOP_CSS, unsafe_allow_html=True) # Use desktop for intro
    
    # The "Ray of Hope" Animation
    lottie_sunrise = load_lottie_url(LOTTIE_ANIMATIONS["sunrise"])
    if lottie_sunrise:
        st_lottie(lottie_sunrise, height=400, key="sunrise_intro")

    # The Manifesto
    st.markdown(
        "<h2 style='text-align: center;'>In the chaotic sea of the stock market, this is your ray of hope.</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h3 style='text-align: center;'>Free for all souls seeking salvation.</h3>",
        unsafe_allow_html=True
    )
    
    time.sleep(3) # Hold for 3 seconds as requested
    
    if st.button("確認 (Confirm)", use_container_width=True):
        st.session_state['intro_complete'] = True
        st.rerun()

def show_mode_selection():
    """Displays the Desktop vs. Mobile mode selection cards."""
    st.markdown(DESKTOP_CSS, unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center;'>選擇您的操作介面</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        if st.button("🖥️ 桌面戰情室\n(Desktop War Room)"):
            st.session_state['device_mode'] = 'desktop'
            st.rerun()
    with col2:
        if st.button("📱 行動指揮所\n(Mobile Command Post)"):
            st.session_state['device_mode'] = 'mobile'
            st.rerun()

def main():
    """Main application router."""
    if 'intro_complete' not in st.session_state:
        show_intro_animation()
    elif 'device_mode' not in st.session_state:
        show_mode_selection()
    else:
        # Route to the selected UI layout
        if st.session_state['device_mode'] == 'desktop':
            render_desktop()
        elif st.session_state['device_mode'] == 'mobile':
            render_mobile()
        else:
            # Fallback to mode selection if state is invalid
            show_mode_selection()

if __name__ == "__main__":
    main()