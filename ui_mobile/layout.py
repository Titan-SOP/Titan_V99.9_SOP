# ui_mobile/layout.py
# Titan V100.0 - Mobile UI Layout & Router
# 狀態: 手機版主框架

import streamlit as st
from streamlit_option_menu import option_menu
from utils_ui import MOBILE_CSS
from . import tab1_home, tab2_swipe, tab3_hud, tab4_chat, tab5_tiktok, tab6_compass

def render():
    """Renders the entire mobile UI including bottom navigation."""
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)

    # Bottom Navigation Bar
    selected = option_menu(
        menu_title=None,
        options=["首頁", "獵殺", "狙擊", "AI參謀", "學習", "羅盤"],
        icons=['house-fill', 'search', 'bullseye', 'chat-dots-fill', 'book-half', 'compass-fill'],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#1C1C1E"},
            "icon": {"color": "white", "font-size": "20px"},
            "nav-link": {"font-size": "14px", "text-align": "center", "margin": "0px", "--hover-color": "#3A3A3C"},
            "nav-link-selected": {"background-color": "#007AFF"},
        }
    )

    # Routing to the selected tab's content
    if selected == "首頁":
        tab1_home.render()
    elif selected == "獵殺":
        tab2_swipe.render()
    elif selected == "狙擊":
        tab3_hud.render()
    elif selected == "AI參謀":
        tab4_chat.render()
    elif selected == "學習":
        tab5_tiktok.render()
    elif selected == "羅盤":
        tab6_compass.render()